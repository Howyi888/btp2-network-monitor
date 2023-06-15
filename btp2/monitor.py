#!/usr/bin/env python3

from datetime import datetime
import sys
from typing import Any, Dict, List, Tuple, TypeVar
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

    def __init__(self, src: str, dst: str, time_limit: int) -> None:
        self.src = src
        self.dst = dst
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
    def pending_duration(self) -> int:
        ts = datetime.now()
        if len(self.tx_history) > 0:
            first = self.tx_history[0]
            return (ts - first[1]).total_seconds()
        else:
            return 0

    def __str__(self) -> str:
        return f'Link(src={self.src},dst={self.dst},tx={self.tx_seq},rx={self.rx_seq},state={self.state})'
    
    def update(self, tx: int, rx: int) -> bool:
        ts = datetime.now()
        if self.tx_seq is None or self.tx_seq < tx:
            self.tx_seq = tx
            self.tx_ts = ts
            self.tx_history.append((tx, ts))

        if self.rx_seq is None or self.rx_seq < rx:
            self.rx_seq = rx
            self.rx_ts = ts
            # Remove transmitted history
            while len(self.tx_history) > 0 and self.tx_history[0][0] <= rx:
                self.tx_history.pop(0)
        
        if len(self.tx_history) > 0:
            first = self.tx_history[0]
            time_diff = (ts - first[1]).total_seconds()
        else:
            time_diff = 0

        if time_diff > self.time_limit:
            state = Link.BAD
        else:
            state = Link.GOOD
        if self.state != state:
            self.state = state
            return True
        else:
            return False


class Links:
    def __init__(self, networks: List[dict]):
        self.__bmcs = build_proxies(networks)
        self.__links = {}
        time_limits = {}
        names = {}
        for net in networks:
            network = net['network']
            if 'time_limit' in net:
                time_limits[network] = net['time_limit']
            if 'name' in net:
                names[network] = net['name']
        self.__time_limits = time_limits
        self.__names = names

    def get_link(self, src: str, dst: str) -> Link:
        key = (src, dst)
        if key not in self.__links:
            self.__links[key] = Link(src, dst, self.__time_limits.get(src, 60))
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

    def apply_status(self, btp_status: Dict[Tuple[str,str],LinkStatus]) -> Tuple[bool, List[Link]]:
        changed = False
        changed_links = []
        for conn, status in btp_status.items():
            source, target = conn
            tx_seq = status.tx_seq
            rx_seq = btp_status[(target,source)].rx_seq
            src_net = urlparse(source).netloc
            dst_net = urlparse(target).netloc
            link = self.get_link(src_net, dst_net)
            if link.update(tx_seq, rx_seq):
                changed = True
                changed_links.append(link)

        return changed, changed_links

    def update(self) -> Tuple[bool, List[Link]]:
        try :
            status = self.query_status()
            return self.apply_status(status)
        except BaseException as exc:
            print(f'FAIL to update status err={exc}', file=sys.stderr)
            return False, []

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

