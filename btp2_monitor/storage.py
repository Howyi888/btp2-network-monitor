#!/usr/bin/env python3

from datetime import datetime
import json
import sqlite3
from threading import Timer, RLock
from typing import Callable, Concatenate, Iterable, List, Optional, ParamSpec, TypedDict, TypeVar

P = ParamSpec('P')
R = TypeVar('R')

class Log(TypedDict):
    sn: int
    ts: float
    src: str
    dst: str
    event: str
    extra: str

def log_from_list(item: Iterable) -> Log:
    return {
        'sn': item[0],
        'ts': item[1],
        'src': item[2],
        'dst': item[3],
        'event': item[4],
        'extra': item[5],
    }

class ConnectionState(TypedDict):
    id: Optional[int]
    state: Optional[str]
    tx_state: Optional[str]
    tx_seq: Optional[int]
    tx_ts: Optional[float]
    tx_height: Optional[int]
    rx_state: Optional[str]
    rx_seq: Optional[int]
    rx_ts: Optional[float]
    rx_height: Optional[int]

ConnectionStateFields = (
    'state',
    'tx_state', 'tx_seq', 'tx_ts', 'tx_height',
    'rx_state', 'rx_seq', 'rx_ts', 'rx_height',
)

def new_connection_state() -> ConnectionState:
    return {
        'id': None,
        'state': None,
        'tx_state': None,
        'tx_seq': None,
        'tx_height': None,
        'tx_ts': None,
        'rx_state': None,
        'rx_seq': None,
        'rx_height': None,
        'rx_ts': None,
    }

def connection_state_from(item: Iterable) -> ConnectionState:
    cs = {}
    cs['id'] = item[0]
    for i in range(len(ConnectionStateFields)):
        cs[ConnectionStateFields[i]] = item[i+1]
    return cs

class TXRecord(tuple):
    @property
    def sn(self) -> int:
        return self[0]

    @property
    def tx_seq(self) -> int:
        return self[1]

    @property
    def tx_ts(self) -> datetime:
        return datetime.fromtimestamp(self[2])

class Storage:
    CREATE_LOGS_TABLE = """
CREATE TABLE IF NOT EXISTS logs (
        sn INTEGER PRIMARY KEY AUTOINCREMENT,
        ts DOUBLE,
        src TEXT,
        dst TEXT,
        event TEXT,
        extra TEXT
)
    """
    CREATE_CONNECTIONS_TABLE = '''
CREATE TABLE IF NOT EXISTS connections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    src TEXT NOT NULL,
    dst TEXT NOT NULL,
    state TEXT,
    tx_state TEXT,
    tx_seq INTEGER,
    tx_ts DOUBLE,
    tx_height INTEGER,
    rx_state TEXT,
    rx_seq INTEGER,
    rx_ts DOUBLE,
    rx_height INTEGER,
    UNIQUE(src, dst)
)
    '''
    CREATE_TXHISTORY_TABLE= '''
CREATE TABLE IF NOT EXISTS txhistory (
    sn INTEGER PRIMARY KEY AUTOINCREMENT,
    conn_id INTEGER NOT NULL,
    tx_seq INTEGER NOT NULL,
    tx_ts DOUBLE NOT NULL
)
    '''
    CREATE_TABLES = [
        CREATE_LOGS_TABLE,
        CREATE_CONNECTIONS_TABLE,
        CREATE_TXHISTORY_TABLE,
    ]
    def __init__(self, url: str = ":memory:"):
        conn = sqlite3.connect(url, check_same_thread=False)
        for sql in self.CREATE_TABLES:
            conn.execute(sql)
        self.__conn = conn
        self.__cursor = None
        self.__lock = RLock()

        self.__timer = None
        # self.generate_log()

    def generate_log(self):
        self.__timer = None
        now = datetime.now()
        self.write_log(now, "0x7.icon", "0xaa36a7.eth2", "tx", { 'count': 3 })
        self.write_log(now, "0x7.icon", "0xaa36a7.eth2", "rx", { 'count': 3, 'delta': 30.3 })
        self.write_log(now, "0x7.icon", "0xaa36a7.eth2", "state", { 'before': 'good', 'after': 'bad' })
        self.write_log(now, "", "", "log", "yahoo")
        self.__timer = Timer(5.0, self.generate_log)
        self.__timer.start()

    def write_log(self, ts: datetime, src: str, dst: str, event: str, msg: any) -> int:
        def write_log(c: sqlite3.Cursor) -> int:
            c.execute('INSERT INTO logs (ts, src, dst, event, extra) values ( ?, ?, ?, ?, ? )', (ts.timestamp(), src, dst, event, json.dumps(msg)))
            return c.lastrowid
        return self.do_write(write_log)

    def get_logs(self, src: Optional[str] = None, dst: Optional[str] = None, event: Optional[str] = None, limit: Optional[int] = None, after: Optional[int] = None, before: Optional[int] = None) -> List[Log]:
        conditions = []
        params = []
        order = 'DESC'
        if src is not None:
            conditions.append('src = ?')
            params.append(src)
        if dst is not None:
            conditions.append('dst = ?')
            params.append(dst)
        if event is not None:
            conditions.append('event = ?')
            params.append(event)
        if after is not None:
            order = 'ASC'
            conditions.append('sn > ?')
            params.append(after)
        if before is not None:
            conditions.append('sn < ?')
            params.append(before)

        if limit is None or limit > 100:
            limit = 100

        where_clause = (' WHERE ' + " AND ".join(conditions)) if len(conditions) > 0 else ''
        c = self.__conn.cursor()
        sql = f'SELECT sn, ts, src, dst, event, extra FROM logs {where_clause} ORDER BY sn {order} LIMIT ?'
        c.execute(sql, params+[limit])
        items = c.fetchall()
        c.close()
        return list(map(log_from_list, items))

    def get_connection_state(self, src: str, dst: str) -> ConnectionState:
        c = self.__conn.cursor()
        sql = f'SELECT id, {",".join(ConnectionStateFields)} FROM connections WHERE src = ? AND dst = ?'
        c.execute(sql, [src, dst])
        result = c.fetchone()
        c.close()
        if result is None:
            return None
        return connection_state_from(result)
    
    def do_batch(self, call: Callable[P, R], *args, **kwargs) -> R:
        self.__lock.acquire()
        try :
            cursor = self.__conn.execute('BEGIN DEFERRED')
            self.__cursor = cursor
            try:
                ret: R = call(*args, **kwargs)
                cursor.execute('COMMIT')
                return ret
            except:
                cursor.execute('ROLLBACK')
                raise
            finally:
                self.__cursor = None
                cursor.close()
        finally:
            self.__lock.release()

    def do_write(self,  call: Callable[Concatenate[sqlite3.Cursor,P],R], *args, **kwargs) -> R:
        self.__lock.acquire()
        try :
            if self.__cursor is None:
                cursor = self.__conn.execute('BEGIN DEFERRED')
                try:
                    ret: R = call(cursor, *args, **kwargs)
                    cursor.execute('COMMIT')
                except:
                    cursor.execute('ROLLBACK')
                    raise
                finally:
                    cursor.close()
            else:
                cursor = self.__conn.cursor()
                try :
                    ret: R = call(cursor, *args, **kwargs)
                finally:
                    cursor.close()
            return ret
        finally:
            self.__lock.release()
        
    def set_connection_state(self, src: str, dst: str, state: ConnectionState, update_id: Optional[bool] = True):
        def do_set(cursor: sqlite3.Cursor) -> int:
            sql = f'INSERT INTO connections (src,dst,{",".join(ConnectionStateFields)}) VALUES (?,?,{",".join("?" * len(ConnectionStateFields))})'
            sql += f' ON CONFLICT(src,dst) DO UPDATE SET {" , ".join(map(lambda x: f"{x} = excluded.{x}",ConnectionStateFields))}'
            params = [src, dst]
            params += list(map(lambda x:state[x],ConnectionStateFields))
            cursor.execute(sql, params)
            id = cursor.lastrowid
            if update_id:
                state['id'] = id
            return id
        return self.do_write(do_set)

    def add_tx_record(self, conn_id: int, tx_seq: int, tx_ts: datetime,) -> TXRecord:
        def do_write(cursor: sqlite3.Cursor) -> TXRecord:
            sql = f'INSERT INTO txhistory ( conn_id, tx_seq, tx_ts ) VALUES ( ?, ?, ? )'
            params = [conn_id, tx_seq, tx_ts.timestamp()]
            cursor.execute(sql, params)
            sn = cursor.lastrowid
            return TXRecord((sn, tx_seq, tx_ts.timestamp()))
        return self.do_write(do_write)
    
    def get_tx_records(self, conn_id: int) -> Iterable[TXRecord]:
        cursor = self.__conn.cursor()
        sql = f'SELECT sn, tx_seq, tx_ts FROM txhistory WHERE conn_id = ? ORDER BY sn'
        params = [ conn_id ]
        cursor.execute(sql, params)
        while True:
            entry = cursor.fetchone()
            if entry is None:
                break
            yield TXRecord(entry)
        cursor.close()
        return
    
    def delete_tx_record(self, sn: int, **kwargs):
        def do_write(cursor: sqlite3.Cursor):
            cursor.execute('DELETE FROM txhistory WHERE sn = ?', [sn])
        return self.do_write(do_write, **kwargs)

    def term(self):
        self.__conn.close()
        if self.__timer is not None:
            self.__timer.cancel()
            self.__timer = None