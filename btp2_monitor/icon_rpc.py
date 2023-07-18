#!/usr/bin/env python3

from typing import List

from iconsdk.builder.call_builder import CallBuilder
from iconsdk.icon_service import IconService
from iconsdk.providers.http_provider import HTTPProvider

from . import types


class BMCWithICONRPC(types.BMC):
    def __init__(self, config: dict) -> None:
        bmc = config['bmc']
        url = config['endpoint']
        self.__service = IconService(HTTPProvider(url))
        self.__bmc = bmc
        self.__address = f'btp://{config["network"]}/{bmc}'

    @property
    def address(self) -> str:
        return self.__address

    def get_status(self, link: str) -> types.LinkStatus:
        status = self.__service.call(CallBuilder()
                .to(self.__bmc)
                .method('getStatus')
                .params({'_link': link})
                .build())
        return types.LinkStatus.from_dict(status)

    def get_links(self) -> List[str]:
        return self.__service.call(CallBuilder()
                .to(self.__bmc)
                .method('getLinks')
                .build())

    def get_routes(self) -> dict[str,str]:
        return self.__service.call(CallBuilder()
                .to(self.__bmc)
                .method('getRoutes')
                .build())

    def get_fee(self, _to: str,  _response: bool) -> int:
        return int(self.__service.call(CallBuilder()
                .to(self.__bmc)
                .method('getFee')
                .params({ '_to':_to, '_response': _response})
                .build()), 0)