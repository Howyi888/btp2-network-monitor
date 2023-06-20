#!/usr/bin/env python3

from datetime import datetime, timedelta
import sys
from typing import Any, Dict, List, Optional, Tuple, TypeVar, Union
from urllib.parse import urlparse

from .eth_rpc import BMCWithEthereumRPC
from .icon_rpc import BMCWithICONRPC
from .types import BMC, LinkStatus

BMC_FACTORY = {
    'icon': BMCWithICONRPC,
    'eth': BMCWithEthereumRPC,
}

def build_proxies(networks) -> Dict[str,BMC]:
    bmcs: Dict[str,BMC] = {}
    for net in networks:
        factory = BMC_FACTORY.get(net['type'], None)
        if factory is None:
            raise Exception(f'unknown network type={net["type"]}')
        bmc: BMC = factory(net)
        network = net['network']
        bmc_address = net['bmc']
        self = f'btp://{network}/{bmc_address}'
        bmcs[self] = bmc
    return bmcs

class Link:
    UNKNOWN = 'unknown'
    BAD = 'bad'
    GOOD = 'good'

    def __init__(self, src: str, dst: str, time_limit: int, src_name: str, dst_name: str) -> None:
        self.src = src
        self.dst = dst
        self.src_name = src_name
        self.dst_name = dst_name
        self.tx_history: List[Tuple[int,datetime]] = []
        self.tx_seq = None
        self.tx_ts = None
        self.rx_seq = None
        self.rx_ts = None
        self.time_limit = time_limit
        self.state = Link.UNKNOWN

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
            return ts - first[1]
        else:
            return timedelta(0)

    def __str__(self) -> str:
        return f'Link(src={self.src},dst={self.dst},tx={self.tx_seq},rx={self.rx_seq},state={self.state})'
    
    def update(self, tx: int, rx: int, now: Optional[datetime] = None) -> Tuple[bool, List['LinkEvent']]:
        if now is None:
            now = datetime.now()
        events = []
        if self.tx_seq is None or self.tx_seq < tx:
            tx_count = (tx-self.tx_seq) if self.tx_seq is not None else 0
            self.tx_seq = tx
            self.tx_ts = now
            self.tx_history.append((tx, now))
            events.append(LinkEvent.TXEvent(self, tx_count, now))

        if self.rx_seq is None or self.rx_seq < rx:
            while len(self.tx_history) > 0 and self.tx_history[0][0] <= rx:
                seq, ts = self.tx_history.pop(0)
                rx_count = (seq - self.rx_seq) if self.rx_seq is not None else 0
                self.rx_seq = seq
                events.append(LinkEvent.RXEvent(self, rx_count, now-ts))

            if rx > self.rx_seq and len(self.tx_history) > 0:
                _, ts = self.tx_history[0]
                rx_count = (rx - self.rx_seq) if self.rx_seq is not None else 0
                self.rx_seq = rx
                events.append(LinkEvent.RXEvent(self, rx_count, now-ts))
            self.rx_ts = now
        
        if len(self.tx_history) > 0:
            first = self.tx_history[0]
            time_diff = now - first[1]
        else:
            time_diff = timedelta(0)

        if time_diff.total_seconds() > self.time_limit:
            state = Link.BAD
        else:
            state = Link.GOOD
        if self.state != state:
            events.append(LinkEvent.StateEvent(self, self.state, state))
            self.state = state
            return True, events
        else:
            return False, events

class LinkEvent(tuple):
    TX = 'tx'
    RX = 'rx'
    STATE = 'state'

    @staticmethod
    def TXEvent(link: 'Link', count: int, ts: datetime) -> 'LinkEvent':
        return LinkEvent((LinkEvent.TX, link, count, ts))
    
    @staticmethod
    def RXEvent(link: 'Link', count: int, delta: timedelta) -> 'LinkEvent':
        return LinkEvent((LinkEvent.RX, link, count, delta))

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
    def count(self) -> int:
        return self[2]

    @property
    def delta(self) -> timedelta:
        return self[3]

    @property
    def ts(self) -> datetime:
        return self[3]

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


class Links:
    def __init__(self, networks: List[dict]):
        self.__bmcs = build_proxies(networks)
        self.__links = {}
        tx_limits = {}
        rx_limits = {}
        names = {}
        for net in networks:
            network = net['network']
            tx_limits[network] = net.get('tx_limit', 30)
            rx_limits[network] = net.get('rx_limit', 30)
            names[network] = net.get('name', network)
        self.__tx_limits = tx_limits
        self.__rx_limits = rx_limits
        self.__names = names

    def get_link(self, src: str, dst: str) -> Link:
        key = (src, dst)
        if key not in self.__links:
            time_limit = self.__rx_limits[src]+self.__tx_limits[dst]
            src_name = self.name_of(src)
            dst_name = self.name_of(dst)
            self.__links[key] = Link(src, dst, time_limit, src_name=src_name, dst_name=dst_name)
        return self.__links[key]

    def name_of(self, net: str) -> str:
        return self.__names.get(net, net)

    def keys(self):
        return self.__links.keys()

    def items(self):
        return self.__links.items()

    def values(self):
        return self.__links.values()

    def query_status(self) -> Dict[Tuple[str,str],LinkStatus]:
        btp_status: Dict[Tuple[str,str],LinkStatus] = {}
        for addr, bmc in self.__bmcs.items():
            links = bmc.getLinks()
            for link in links:
                status = bmc.getStatus(link)
                btp_status[(addr,link)] = status
        return btp_status

    def apply_status(self, btp_status: Dict[Tuple[str,str],LinkStatus], now: Optional[datetime] = None) -> Tuple[bool, List[LinkEvent]]:
        status_change = False
        link_events: List[LinkEvent] = []
        if now is None:
            now = datetime.now()
        for conn, status in btp_status.items():
            source, target = conn
            tx_seq = status.tx_seq
            rx_seq = btp_status[(target,source)].rx_seq
            src_net = urlparse(source).netloc
            dst_net = urlparse(target).netloc
            link = self.get_link(src_net, dst_net)
            change, events = link.update(tx_seq, rx_seq, now)
            if change:
                status_change = True
            link_events += events

        return status_change, link_events

    def update(self) -> Tuple[bool, List[LinkEvent]]:
        status = self.query_status()
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

