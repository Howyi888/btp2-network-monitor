#!/usr/bin/env python3


import json
from abc import ABCMeta, abstractmethod
from collections.abc import Iterable
from typing import Tuple


class VerifierStatus(tuple):
    def __new__(cls, __iterable: Iterable = ...) -> 'VerifierStatus':
        return super().__new__(cls, __iterable)

    def from_dict(value: dict) -> 'VerifierStatus':
        return VerifierStatus((
            int(value['height'], 0),
            bytes.fromhex(value['extra'][2:]) if value['extra'] is not None else None,
        ))

    @property
    def height(self) -> int:
        return self[0]

    @property
    def extra(self) -> bytes:
        return self[1]

    def __str__(self) -> str:
        return f'VerifierStatus(height={self.height},extra={self.extra.hex()})'


class LinkStatus(tuple):
    def __new__(cls, __iterable: Iterable = ...) -> 'LinkStatus':
        return super().__new__(cls, __iterable)

    @staticmethod
    def from_dict(value: dict) -> 'LinkStatus':
        try:
            return LinkStatus((
                int(value['rx_seq'], 0),
                int(value['tx_seq'], 0),
                VerifierStatus.from_dict(value['verifier']),
                int(value['cur_height'], 0),
            ))
        except:
            raise Exception(f'Invalid LinkStatus({json.dumps(value)})')

    @property
    def rx_seq(self) -> int:
        return self[0]

    @property
    def tx_seq(self) -> int:
        return self[1]

    @property
    def verifier(self) -> VerifierStatus:
        return VerifierStatus(self[2])

    @property
    def current_height(self) -> int:
        return self[3]

    def __str__(self) -> str:
        return f'LinkStatus(rx_seq={self.rx_seq},tx_seq={self.tx_seq},verifier={self.verifier},current_height={self.current_height})'


class BMC(metaclass=ABCMeta):
    @property
    @abstractmethod
    def address(self) -> str:
        pass

    @abstractmethod
    def get_status(self, _link: str) -> LinkStatus:
        pass

    @abstractmethod
    def get_links(self) -> Tuple[str]:
        pass