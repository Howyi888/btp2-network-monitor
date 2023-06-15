#!/usr/bin/env python3

from typing import Tuple

from web3 import Web3

from . import eth_abi, types
from .types import LinkStatus


class BMCWithEthereumRPC(types.BMC):
    def __init__(self, config: dict) -> None:
        bmc = config['bmc']
        bmcm = config['bmcm']
        url = config['endpoint']
        w3 = Web3(Web3.HTTPProvider(url))
        self.__periphery = w3.eth.contract(address=bmc, abi=eth_abi.BMCPeriphery)
        self.__management = w3.eth.contract(address=bmcm, abi=eth_abi.BMCManagement)

    def getStatus(self, _link: str) -> LinkStatus:
        return LinkStatus(self.__periphery.functions.getStatus(_link=_link).call())

    def getLinks(self) -> Tuple[str]:
        return tuple(self.__management.functions.getLinks().call())
