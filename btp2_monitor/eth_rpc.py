#!/usr/bin/env python3

from typing import Tuple

from web3 import Web3

from . import eth_abi, types
from .types import LinkStatus


class BMCWithEthereumRPC(types.BMC):
    def __init__(self, config: dict) -> None:
        bmc = config['bmc']
        url = config['endpoint']
        w3 = Web3(Web3.HTTPProvider(url))
        self.__periphery = w3.eth.contract(address=bmc, abi=eth_abi.BMCPeriphery)
        if 'bmcm' in config:
            self.__management = w3.eth.contract(address=config['bmcm'], abi=eth_abi.BMCManagement)
        else:
            self.__management = self.__periphery
        self.__address = f'btp://{config["network"]}/{bmc}'

    @property
    def address(self) -> str:
        return self.__address

    def get_status(self, _link: str) -> LinkStatus:
        return LinkStatus(self.__periphery.functions.getStatus(_link=_link).call())

    def get_links(self) -> Tuple[str]:
        return tuple(self.__management.functions.getLinks().call())

    def get_routes(self) -> dict[str,str]:
        return dict(self.__management.functions.getRoutes().call())

    def get_fee(self, dst: str, rollback: bool) -> int:
        return self.__periphery.functions.getFee(dst, rollback).call()