from contextlib import asynccontextmanager
from datetime import datetime
import json
import os
from threading import Timer
import traceback
from typing import List, Optional, TypedDict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .types import NetworkID
from .monitor import LinkEvent, Links
from .storage import Log, Storage

NETWORKS_JSON = os.environ.get('NETWORKS_JSON', 'networks.json')
DOCUMENT_ROOT = os.environ.get('DOCUMENT_ROOT', "web/build/")
STORAGE_URL = os.environ.get('STORAGE_URL', ':memory:')
REFRESH_INTERVAL = float(os.environ.get('REFRESH_INTERVAL', '30.0'))
INITIAL_INTERVAL = 1.0

class LinkID(TypedDict):
    src: NetworkID
    dst: NetworkID

class LinkInfo(TypedDict):
    src: NetworkID
    dst: NetworkID
    src_name: str
    dst_name: str
    state: str
    tx_seq: Optional[int]
    rx_seq: Optional[int]
    tx_height: Optional[int]
    rx_height: Optional[int]
    pending_count: Optional[int]
    pending_delay: Optional[float]

class NetworkInfo(TypedDict):
    network: str
    bmc: str
    endpoint: str

class MonitorBackend:
    def __init__(self):
        with open(NETWORKS_JSON, 'rb') as fd:
            network_json = json.load(fd)
        self.__storage = Storage(STORAGE_URL)
        self.__links = Links(network_json, self.__storage)
        self.__initialized = False
        self.__stopped = False
        self.try_update()

    @property
    def storage(self) -> Storage:
        return self.__storage

    def write_log(self, ts: datetime, src: str, dst: str, event: str, extra: any) -> Log:
        row_id = self.__storage.write_log(ts, src, dst, event, extra)
        log: Log = {
            'sn': row_id,
            'ts': ts,
            'src': src,
            'dst': dst,
            'event': event,
            'extra': extra,
        }
        # TODO notify log
        return log

    def try_update(self):
        if self.__stopped:
            return
        self.__timer = None

        try :
            now = datetime.now()
            updated, changes = self.__links.update()
        except BaseException as exc:
            traceback.print_exc()
            self.write_log(now, "", "", "log", f'Exception:{str(exc)}')
            self.__timer = Timer(REFRESH_INTERVAL, self.try_update)
            self.__timer.start()
            return

        if not self.__initialized:
            self.__initialized = True
            self.write_log(now, '', '', 'log', 'START')
        else:
            events = []
            for c in changes:
                extra = None
                if c.name == LinkEvent.TX:
                    extra = {'count': c.count}
                elif c.name == LinkEvent.RX:
                    extra = {'count': c.count, 'delta': c.delta.total_seconds()}
                elif c.name == LinkEvent.STATE:
                    extra = {'after': c.after, 'before': c.before}
                event = self.write_log(now, c.link.src, c.link.dst, c.name, extra)
                events.append(event)

            if updated:
                # notify changes to slack
                pass

        self.__timer = Timer(REFRESH_INTERVAL, self.try_update)
        self.__timer.start()

    def get_links(self) -> List[LinkID]:
        links = []
        if not self.__initialized:
            return links
        for key in self.__links.get_connected_links():
            if key in links or (key[1], key[0]) in links:
                continue
            links.append(key)
        return list(map(lambda key: {
             'src': NetworkID.from_address(key[0]),
             'dst': NetworkID.from_address(key[1]),
        }, links))

    def get_network(self, id: NetworkID) -> dict:
        return self.__links.get_network(id.address)

    def get_link(self, src: NetworkID, dst: NetworkID) -> LinkInfo:
        if not self.__initialized:
            raise Exception('Unknown')

        link = self.__links.get_link(src.address, dst.address)
        return {
            'src': NetworkID.from_address(link.src),
            'dst': NetworkID.from_address(link.dst),
            'src_name': link.src_name,
            'dst_name': link.dst_name,
            'state': link.state,
            'tx_seq': link.tx_seq,
            'rx_seq': link.rx_seq,
            'tx_height': link.tx_height,
            'rx_height': link.rx_height,
            'pending_count': link.pending_count,
            'pending_delay': link.pending_duration.total_seconds(),
        }

    def get_logs(self, **kwargs) -> List[Log]:
        logs = self.__storage.get_logs(**kwargs)
        for log in logs:
            if 'src' in log:
                log['src_name'] = be.__links.name_of(log['src'])
                log['src'] = NetworkID.from_address(log['src'])
            if 'dst' in log:
                log['dst_name'] = be.__links.name_of(log['dst'])
                log['dst'] = NetworkID.from_address(log['dst'])
        return logs

    def term(self):
        if self.__stopped:
            return
        self.__stopped = True
        if self.__timer is not None:
            self.__timer.cancel()
            self.__timer = None
        self.write_log(datetime.now(), '', '', 'log', 'SHUTDOWN')
        self.__storage.term()


be = MonitorBackend()

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    be.term()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"]
)

@app.get("/links/{src}/{dst}")
async def getLinkInfo(src: str, dst: str) -> LinkInfo:
    return be.get_link(NetworkID(src), NetworkID(dst))

@app.get('/network/{id}')
async def getNetworkInfo(id: str) -> dict:
    return be.get_network(NetworkID(id))

@app.get("/links")
async def getLinks() -> List[LinkID]:
    return be.get_links()

@app.get("/events")
async def getLogs(limit: Optional[int] = None, after: Optional[int] = None, before: Optional[int] = None) -> List[dict]:
    return be.get_logs(after=after, limit=limit, before=before)

app.mount("/", StaticFiles(directory=DOCUMENT_ROOT, html=True), name="static")
