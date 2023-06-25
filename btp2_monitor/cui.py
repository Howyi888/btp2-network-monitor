#!/usr/bin/env python3

from datetime import datetime
from typing import Dict, Optional, Tuple
from textual.app import App, ComposeResult
from textual.widgets import Header, Static, TextLog, ProgressBar
from textual.containers import Container, Horizontal

from .monitor import Link, LinkEvent, Links, strfdelta

class StatusEntry(Static):
    def __init__(self, links: Links, conn: Tuple[str,str]):
        super().__init__()
        self.__links = links
        self.__conn = conn

    def compose(self) -> ComposeResult:
        src_name = self.__links.name_of(self.__conn[0])
        dst_name = self.__links.name_of(self.__conn[1])
        self.border_title = f'{src_name} <-> {dst_name}'
        self.__forward = Static('', id='forward')
        self.__forward.border_title = 'Forward'
        yield self.__forward
        self.__backward = Static('', id='backward')
        self.__backward.border_title = 'Backward'
        yield self.__backward

    def on_mount(self) -> None:
        self.update_self()

    @staticmethod
    def state_from_link(link: Link):
        return f'[b]{link.state.upper()}[/b]\ntx_seq={link.tx_seq}, rx_seq={link.rx_seq}\npending={link.pending_count}, delay={strfdelta(link.pending_duration)}'

    def update_status(self, w: Static, link: Link):
        if link.state == Link.GOOD:
            if link.pending_count > 0:
                w.set_classes('pending')
            else:
                w.set_classes('good')
        else:
            w.set_classes('bad')
        w.update(self.state_from_link(link))

    def update_self(self):
        fw_link = self.__links.get_link(self.__conn[0], self.__conn[1])
        bw_link = self.__links.get_link(self.__conn[1], self.__conn[0])
        self.update_status(self.__forward, fw_link)
        self.update_status(self.__backward, bw_link)

class MonitorApp(App):
    CSS_PATH = 'cui.css'
    TITLE = 'BTP2 Network Monitor'

    def __init__(self, links: Links, interval: int = 60, on_update: callable = None):
        super().__init__()
        self.__links = links
        self.__interval = interval
        self.__on_update = on_update
        self.__on_log = None
        self.__last_update: Optional[datetime] = None

    @property
    def on_log(self) -> Optional[callable]:
        return self.__on_log

    @on_log.setter
    def on_log(self, on_log: callable):
        self.__on_log = on_log

    def compose(self) -> ComposeResult:
        yield Header(name='BTP2 Network Monitor')
        entries: Dict[Tuple[str,str], StatusEntry] = {}
        for conn in self.__links.keys():
            if conn in entries or (conn[1], conn[0]) in entries:
                continue
            entries[conn] = StatusEntry(self.__links, conn)
        self.__entries = entries
        yield Container(*entries.values(), id="monitors")
        self.__log = TextLog(id="log")
        self.__log.border_title = 'Log'
        yield self.__log
        self.__progress = ProgressBar(total=self.__interval, show_percentage=False, show_eta=False)
        self.__bottom = Static()
        yield Horizontal(self.__progress, self.__bottom, id="bottom")

    def update_progress(self):
        if self.__last_update is not None:
            now = datetime.now()
            delta = now - self.__last_update
            passed = delta.total_seconds()
            self.__progress.progress = min(passed, self.__interval)

    def on_mount(self) -> None:
        self.write_log(f'{str(datetime.now())}: START')
        self.update_self()
        self.set_interval(self.__interval, self.update_status)
        self.set_interval(1.0, self.update_progress)

    def write_log(self, msg: any):
        if self.__on_log is not None:
            self.__on_log(msg)
        self.__log.write(msg)

    def update_status(self) -> None:
        now = datetime.now()
        try:
            changed, updated = self.__links.update()
        except BaseException as exc:
            self.__last_update = now
            self.write_log(f'{str(now)}: FAIL to update err={exc}')
            return
        self.update_self(now=now)
        if changed:
            self.__on_update(list(filter(lambda x: x.name == LinkEvent.STATE, updated)))
        if len(updated)>0:
            self.write_log(f'{str(now)}: UPDATED')
            for event in updated:
                self.write_log(f'* {str(event)}')

    def update_self(self, now: Optional[datetime] = None):
        if now is None:
            now = datetime.now()
        self.__last_update = now
        self.__bottom.update("[b]Last Update:[/b] "+str(now))
        for entry in self.__entries.values():
            entry.update_self()
