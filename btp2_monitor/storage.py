#!/usr/bin/env python3

from datetime import datetime
import json
import sqlite3
from threading import Timer
from typing import Iterable, List, Optional, TypedDict


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
    def __init__(self, url: str = ":memory:"):
        conn = sqlite3.connect(url, check_same_thread=False)
        c = conn.cursor()
        c.execute(self.CREATE_LOGS_TABLE)
        conn.commit()
        c.close()
        self.__conn = conn

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
        c = self.__conn.cursor()
        c.execute('INSERT INTO logs (ts, src, dst, event, extra) values ( ?, ?, ?, ?, ? )', (ts.timestamp(), src, dst, event, json.dumps(msg)))
        self.__conn.commit()
        row_id = c.lastrowid
        c.close()
        return row_id

    def get_logs(self, src: Optional[str] = None, dst: Optional[str] = None, event: Optional[str] = None, limit: Optional[int] = None, start: Optional[int] = None, end: Optional[int] = None) -> List[Log]:
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
        if start is not None:
            order = 'ASC'
            conditions.append('sn >= ?')
            params.append(start)
        if end is not None:
            conditions.append('sn < ?')
            params.append(end)

        if limit is None or limit > 100:
            limit = 100

        where_clause = (' WHERE ' + " AND ".join(conditions)) if len(conditions) > 0 else ''
        c = self.__conn.cursor()
        sql = f'SELECT sn, ts, src, dst, event, extra FROM logs {where_clause} ORDER BY sn {order} LIMIT ?'
        c.execute(sql, params+[limit])
        items = c.fetchall()
        c.close()
        return list(map(log_from_list, items))

    def term(self):
        self.__conn.close()
        if self.__timer is not None:
            self.__timer.cancel()
            self.__timer = None