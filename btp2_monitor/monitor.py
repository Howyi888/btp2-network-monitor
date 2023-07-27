#!/usr/bin/env python3

from datetime import datetime, timedelta
from typing import Any, Dict, Iterable, List, Optional, Tuple, TypeVar
from urllib.parse import urlparse

from .storage import ConnectionState, Storage, TXRecord, new_connection_state

from .eth_rpc import BMCWithEthereumRPC
from .icon_rpc import BMCWithICONRPC
from .types import BMC, LinkStatus, FeeTable

BMC_FACTORY = {
    'icon': BMCWithICONRPC,
    'eth': BMCWithEthereumRPC,
}

COIN_BY_TYPE = {
    'icon': 'ICX',
    'eth': 'ETH',
}

def build_proxy(net: dict) -> BMC:
    factory = BMC_FACTORY.get(net['type'], None)
    if factory is None:
        raise Exception(f'unknown network type={net["type"]}')
    return factory(net)

def bmc_changed(net: dict, bmc: str) -> dict:
    n2 = net.copy()
    for k in ['bmc', 'bmcm', 'bmcs']:
        if k in n2:
            del n2[k]
    n2['bmc'] = bmc
    n2['name'] = n2.get('name', net['network'])+f'({str(bmc)[:6]})'
    return n2

class EdgeState(tuple[str,Optional[int],Optional[int]]):
    ACTIVE = 'active'
    INACTIVE = 'inactive'

    @property
    def state(self) -> str:
        return self[0]
    
    @property
    def seq(self) -> Optional[int]:
        return self[1]

    @property
    def height(self) -> Optional[int]:
        return self[2]

class LinkUpdate(tuple[Optional[EdgeState],Optional[EdgeState]]):
    @property
    def tx(self) -> Optional[EdgeState]:
        return self[0]
    
    @property
    def tx_state(self) -> Optional[str]:
        tx = self[0]
        return tx.state if tx is not None else None

    @property
    def tx_seq(self) -> Optional[int]:
        tx = self[0]
        return tx.seq if tx is not None else None

    @property
    def tx_height(self) -> Optional[int]:
        tx = self[0]
        return tx.height if tx is not None else None

    @property
    def rx(self) -> Optional[EdgeState]:
        return self[1]

    @property
    def rx_state(self) -> Optional[str]:
        rx = self[1]
        return rx.state if rx is not None else None

    @property
    def rx_seq(self) -> Optional[int]:
        rx = self[1]
        return rx.seq if rx is not None else None

    @property
    def rx_height(self) -> Optional[int]:
        rx = self[1]
        return rx.height if rx is not None else None

class LinkEvent(tuple):
    TX = 'tx'
    RX = 'rx'
    STATE = 'state'

    @staticmethod
    def TXEvent(link: 'Link', seq: int, count: int) -> 'LinkEvent':
        return LinkEvent((LinkEvent.TX, link, seq, count))
    
    @staticmethod
    def RXEvent(link: 'Link', seq: int, count: int, delta: timedelta) -> 'LinkEvent':
        return LinkEvent((LinkEvent.RX, link, seq, count, delta))

    @staticmethod
    def StateEvent(link: 'Link', before: str, after: str) -> 'LinkEvent':
        return LinkEvent((LinkEvent.STATE, link, before, after))

    @property
    def name(self) -> str:
        return self[0]

    @property
    def link(self) -> 'Link':
        return self[1]

    @property
    def seq(self) -> int:
        return self[2]

    @property
    def count(self) -> int:
        return self[3]

    @property
    def delta(self) -> timedelta:
        return self[4]

    @property
    def before(self) -> str:
        return self[2]

    @property
    def after(self) -> str:
        return self[3]

    def __str__(self) -> str:
        name = self.name
        link_str = f'{self.link.src_name} -> {self.link.dst_name}'
        if name == self.TX:
            return f'{link_str} : TX count={self.count}'
        elif name == self.RX:
            return f'{link_str} : RX count={self.count} delay={strfdelta(self.delta)}'
        elif name == self.STATE:
            return f'{link_str} : {self.after.upper()} delay={strfdelta(self.link.pending_duration)}'
        else:
            super().__str__()

class Link:
    UNKNOWN = 'unknown'
    BROKEN = 'broken'
    BAD = 'bad'
    GOOD = 'good'

    def __init__(self, storage: Storage, src: str, dst: str, time_limit: int, src_name: str, dst_name: str) -> None:
        self.__storage = storage
        self.__conn_id = None
        self.__conn_dirty = True
        self.__conn_state = new_connection_state()
        self.src = src
        self.dst = dst
        self.src_name = src_name
        self.dst_name = dst_name
        self.tx_history: List[TXRecord] = []
        self.__tx_state = None
        self.__rx_state = None
        self.time_limit = time_limit
        self.state = Link.UNKNOWN
        self.__tx_ts = None
        self.__rx_ts = None

        cstate = storage.get_connection_state(src, dst)
        if cstate is None:
            cstate = new_connection_state()
            self.__storage.set_connection_state(self.src, self.dst, cstate)
        self.__conn_state = cstate
        self.__conn_id = self.__conn_state['id']
        if cstate['tx_state'] is not None:
            self.__tx_state = EdgeState((cstate['tx_state'], cstate['tx_seq'], cstate['tx_height']))
        if cstate['rx_state'] is not None:
            self.__rx_state = EdgeState((cstate['rx_state'], cstate['rx_seq'], cstate['rx_height']))
        self.tx_history = list(storage.get_tx_records(self.__conn_id))
        self.__tx_ts = datetime.fromtimestamp(cstate['tx_ts']) if cstate['tx_ts'] is not None else None
        self.__rx_ts = datetime.fromtimestamp(cstate['rx_ts']) if cstate['rx_ts'] is not None else None
        self.handle_update(LinkUpdate((None,None)), datetime.now())

    @property
    def state(self) -> str:
        state = self.__conn_state['state']
        return self.UNKNOWN if state is None else state

    @state.setter
    def state(self, state: str):
        self.__conn_state['state'] = state
        self.__conn_dirty = True
    
    @property
    def tx_state(self) -> Optional[EdgeState]:
        return self.__tx_state

    @tx_state.setter
    def tx_state(self, state: Optional[EdgeState]):
        if self.__tx_state != state:
            self.__tx_state = state
            self.__conn_dirty = True
            self.__conn_state['tx_state'] = None if state is None else state.state

    @property
    def tx_seq(self) -> Optional[int]:
        return self.__conn_state['tx_seq']
    
    @tx_seq.setter
    def tx_seq(self, seq: Optional[int]):
        self.__conn_dirty = True
        self.__conn_state['tx_seq'] = seq

    @property
    def tx_height(self) -> Optional[int]:
        return self.__conn_state['tx_height']
    
    @tx_height.setter
    def tx_height(self, height: Optional[int]):
        self.__conn_dirty = True
        self.__conn_state['tx_height'] = height

    @property
    def tx_ts(self) -> Optional[datetime]:
        return self.__tx_ts
    
    @tx_ts.setter
    def tx_ts(self, ts: Optional[datetime]):
        self.__tx_ts = ts
        ts_value = None if ts is None else ts.timestamp()
        self.__conn_dirty = True
        self.__conn_state['tx_ts'] = ts_value

    @property
    def rx_state(self) -> Optional[EdgeState]:
        return self.__rx_state

    @rx_state.setter
    def rx_state(self, state: Optional[EdgeState]):
        if self.__rx_state != state:
            self.__rx_state = state
            self.__conn_dirty = True
            self.__conn_state['rx_state'] = None if state is None else state.state

    @property
    def rx_seq(self) -> Optional[int]:
        return self.__conn_state['rx_seq']
    
    @rx_seq.setter
    def rx_seq(self, seq: Optional[int]):
        self.__conn_dirty = True
        self.__conn_state['rx_seq'] = seq

    @property
    def rx_height(self) -> Optional[int]:
        return self.__conn_state['rx_height']
    
    @rx_height.setter
    def rx_height(self, height: Optional[int]):
        self.__conn_dirty = True
        self.__conn_state['rx_height'] = height

    @property
    def rx_ts(self) -> Optional[datetime]:
        return self.__rx_ts
    
    @rx_ts.setter
    def rx_ts(self, ts: Optional[datetime]):
        self.__rx_ts = ts
        ts_value = None if ts is None else ts.timestamp()
        self.__conn_dirty = True
        self.__conn_state['rx_ts'] = ts_value
    
    def flush(self):
        if self.__conn_dirty:
            self.__storage.set_connection_state(self.src, self.dst, self.__conn_state, False)
            self.__conn_dirty = False

    @property
    def pending_count(self) -> int:
        if self.tx_seq is not None and self.rx_seq is not None:
            return self.tx_seq - self.rx_seq
        else:
            return 0
    
    @property
    def pending_duration(self) -> timedelta:
        ts = datetime.now()
        if len(self.tx_history) > 0:
            first = self.tx_history[0]
            return ts - first.tx_ts
        else:
            return timedelta(0)

    def __str__(self) -> str:
        return f'Link(src={self.src},dst={self.dst},tx={self.tx_seq},rx={self.rx_seq},state={self.state})'
    
    def add_tx_record(self, seq: int, ts: datetime):
        record = self.__storage.add_tx_record(self.__conn_id, seq, ts)
        self.tx_history.append(record)

    def pop_tx_record(self) -> TXRecord:
        record = self.tx_history.pop(0)
        self.__storage.delete_tx_record(record.sn)
        return record

    def handle_tx(self, tx_state: EdgeState, now: datetime) -> Iterable['LinkEvent']:
        if tx_state.state == EdgeState.ACTIVE:
            if self.tx_seq is None:
                self.tx_seq = tx_state.seq
                self.tx_ts = now
            elif self.tx_seq < tx_state.seq:
                tx_seq = self.tx_seq
                count = tx_state.seq - tx_seq
                self.tx_seq = tx_state.seq
                self.tx_ts = now
                self.add_tx_record(tx_state.seq, now)
                yield LinkEvent.TXEvent(self, tx_seq, count)

            if self.tx_height is None or tx_state.height > self.tx_height:
                self.tx_height = tx_state.height

        elif self.tx_seq is not None:
            self.tx_seq = None
            self.tx_ts = now
            self.tx_height = None

    def handle_rx(self, rx_state: EdgeState, now: datetime) -> Iterable['LinkEvent']:
        if rx_state.state == EdgeState.ACTIVE:
            if self.rx_seq is None:
                self.rx_seq = rx_state.seq
                self.rx_ts = now
            elif self.rx_seq < rx_state.seq:
                while len(self.tx_history) > 0 and self.rx_seq < rx_state.seq:
                    tx_record = self.tx_history[0]
                    if tx_record.tx_seq <= rx_state.seq:
                        self.pop_tx_record()
                        rx_seq = self.rx_seq
                        count = tx_record.tx_seq - self.rx_seq
                        self.rx_seq = tx_record.tx_seq
                    else:
                        rx_seq = self.rx_seq
                        count = rx_state.seq - self.rx_seq
                        self.rx_seq = rx_state.seq
                    delay = now - tx_record.tx_ts
                    yield LinkEvent.RXEvent(self, rx_seq, count, delay)

            if self.rx_height is None or rx_state.height > self.rx_height:
                self.rx_height = rx_state.height

        elif self.rx_seq is not None:
            self.rx_seq = None
            self.rx_height = None
            self.rx_ts = now
    
    def handle_update(self, update: LinkUpdate, now: datetime) -> tuple[bool,list['LinkEvent']]:
        changed = False
        events: list[LinkEvent] = []

        tx_state = update.tx or self.tx_state
        rx_state = update.rx or self.rx_state

        if tx_state is None or rx_state is None:
            state = Link.UNKNOWN
        else:
            events.extend(self.handle_tx(tx_state, now))
            events.extend(self.handle_rx(rx_state, now))

            if tx_state.state == EdgeState.INACTIVE or rx_state.state == EdgeState.INACTIVE:
                state = Link.BROKEN
            else:
                if len(self.tx_history) > 0:
                    delay = now - self.tx_history[0].tx_ts
                    if delay.total_seconds() > self.time_limit:
                        state = Link.BAD
                    else:
                        state = Link.GOOD
                else:
                    state = Link.GOOD

        if self.state != state:
            changed = True
            events.append(LinkEvent.StateEvent(self, self.state, state))
            self.state = state

        self.tx_state = tx_state
        self.rx_state = rx_state
        self.flush()
        return changed, events

class NetworkStatus(dict[str,dict[str,LinkStatus]]):
    def __new__(cls, *args: Any, **kwargs: Any) -> 'NetworkStatus':
        return super().__new__(cls, *args, **kwargs)

    def set_link_statuses(self, src: str, links: list[tuple[str,LinkStatus]]):
        self[src] = dict(links)

    def get_known_links(self) -> list[tuple[str,str]]:
        knowns: list[tuple[str,str]] = list()
        for src, link in self.items():
            for dst in link.keys():
                knowns.append((src, dst))
        return knowns

    def get_tx_update(self, src: str, dst: str) -> Optional[EdgeState]:
        if src not in self:
            return None
        link_map = self[src]
        if dst not in link_map:
            return EdgeState((EdgeState.INACTIVE, None, None))
        link_status = link_map[dst]
        return EdgeState((EdgeState.ACTIVE, link_status.tx_seq, link_status.current_height))
    
    def get_rx_update(self, src: str, dst: str) -> Optional[EdgeState]:
        if dst not in self:
            return None
        link_map = self[dst]
        if src not in link_map:
            return EdgeState((EdgeState.INACTIVE, None, None))
        link_status = link_map[src]
        return EdgeState((EdgeState.ACTIVE, link_status.rx_seq, link_status.verifier.height))

    def get_link_update(self, src: str, dst: str) -> LinkUpdate:
        return LinkUpdate((self.get_tx_update(src, dst), self.get_rx_update(src, dst)))


class Links:
    def __init__(self, networks: List[dict], storage: Optional[Storage] = None):
        if storage is None:
            storage = Storage()
        self.__storage = storage
        self.__bmcs = {}
        self.__links = {}
        self.__networks = {}
        self.__configs = {}
        for net in networks:
            network = net['network']
            if network in self.__configs:
                raise Exception(f'duplicate network id={network}')
            bmc = build_proxy(net)
            self.__configs[network] = net
            self.__bmcs[bmc.address] = bmc
            self.__networks[bmc.address] = net

    def get_rx_limit(self, id: str) -> int:
        return self.__networks[id].get('rx_limit', 30)

    def get_tx_limit(self, id: str) -> int:
        return self.__networks[id].get('tx_limit', 30)

    def name_of(self, id: str) -> str:
        return self.__networks.get(id, {}).get('name', id)

    def get_network(self, id: str) -> any:
        return self.__networks.get(id, None)

    def get_link(self, src: str, dst: str) -> Link:
        key = (src, dst)
        if key not in self.__links:
            time_limit = self.get_tx_limit(src)+self.get_rx_limit(dst)
            src_name = self.name_of(src)
            dst_name = self.name_of(dst)
            self.__links[key] = Link(self.__storage, src, dst, time_limit, src_name=src_name, dst_name=dst_name)
        return self.__links[key]

    def get_connected_links(self):
        return map(
            lambda x: (x.src, x.dst),
            filter(
                lambda x: x.state != Link.BROKEN,
                 self.__links.values()
            )
        )

    def add_proxy(self, addr: str) -> bool:
        btp_addr = urlparse(addr)
        if btp_addr.netloc not in self.__configs:
            return False
        net = bmc_changed(self.__configs[btp_addr.netloc], btp_addr.path[1:])
        bmc = build_proxy(net)
        self.__bmcs[addr] = bmc
        self.__networks[addr] = net
        return True

    def query_status(self, all: bool = False) -> NetworkStatus:
        btp_status = NetworkStatus()
        bmc_addrs = list(self.__bmcs.keys())
        while len(bmc_addrs):
            addr = bmc_addrs.pop(0)
            bmc = self.__bmcs[addr]
            try :
                links = bmc.get_links()

                link_statuses = []
                for link in links:
                    status: LinkStatus = bmc.get_status(link)
                    link_statuses.append((link, status))
                    if link not in self.__bmcs:
                        if self.add_proxy(link):
                            bmc_addrs.append(link)
                # print('STATUS:', addr, link_statuses)
                btp_status.set_link_statuses(addr, link_statuses)
            except BaseException as exc:
                if all:
                    raise exc
                continue
        return btp_status
    
    def get_relay_fee_table(self, id: str) -> FeeTable:
        if id not in self.__bmcs :
            raise Exception(f'Unknown Network id={id}')
        proxy: BMC = self.__bmcs[id]
        network: dict = self.__networks[id]
        links = proxy.get_links()
        routes = proxy.get_routes()
        networks = set(routes.keys())
        networks = networks.union(set(map(lambda x: urlparse(x).netloc, links)))
        fee_table = []
        for net in networks:
            config = self.__configs[net]
            fee1: int = proxy.get_fee(net, False)
            fee2: int = proxy.get_fee(net, True)
            fee_table.append({
                'id': net,
                'name': config['name'],
                'fees': [fee1, fee2],
            })
        decimal = network.get('decimal', 18)
        symbol = network.get('symbol') or COIN_BY_TYPE.get(network['type'], 'UNK')
        return {
            'decimal': decimal,
            'symbol': symbol,
            'table': fee_table,
        }

    def apply_status(self, btp_status: NetworkStatus, now: Optional[datetime] = None) -> Tuple[bool, List[LinkEvent]]:
        if now is None:
            now = datetime.now()

        links = list(self.__links.keys())
        for link in btp_status.get_known_links():
            if link not in links:
                links.append(link)
        link_objs = map(lambda x: self.get_link(x[0], x[1]), links)

        def do_update() -> tuple[bool, list[LinkEvent]]:
            status_change = False
            link_events: List[LinkEvent] = []
            for link in link_objs:
                update = btp_status.get_link_update(link.src, link.dst)
                change, events = link.handle_update(update, now)
                if change:
                    status_change = True
                link_events += events
            return status_change, link_events
        return self.__storage.do_batch(do_update)

    def update(self, all: bool = False) -> Tuple[bool, List[LinkEvent]]:
        status = self.query_status(all)
        return self.apply_status(status)

T = TypeVar('T')
def merge_status(status: Dict[Tuple[str,str],T]) -> Dict[Tuple[str,str],List[T]]:
    new_status: Dict[Tuple[str,str],List[T]] = {}
    for conn, value in status.items():
        reverse = conn[0] > conn[1]
        key = conn if not reverse else (conn[1], conn[0])
        if key not in new_status:
            new_status[key] = [ None, None ]
        sl = new_status[key]
        sl[reverse] = value
    return new_status

TIME_MODULERS = [
    ('s', 60),
    ('m', 60),
    ('h', 24),
    ('d', 0),
]
def strfdelta(d: timedelta) -> str:
    remainder = d.total_seconds()
    if remainder<0:
        return '-'+strfdelta(-d)
    elif remainder<1:
        return f'{remainder}s'
    remainder = int(remainder)
    items = []
    for s, mod in TIME_MODULERS:
        if mod != 0:
            remainder, v = divmod(remainder, mod)
        else:
            v = remainder
        if v>0:
            items.insert(0, f'{v}{s}')
        if not remainder:
            break
    return "".join(items)

