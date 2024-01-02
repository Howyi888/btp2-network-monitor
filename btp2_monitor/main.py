
import json
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse

import click
import requests

from .cui import MonitorApp
from .monitor import Link, LinkEvent, Links, strfdelta
from .storage import Storage

KEY_LINKS = 'links'

@click.group()
@click.option('--networks', metavar='<networks.json>', type=str, envvar="NETWORKS_JSON")
@click.option('--storage_url', type=str, envvar="STORAGE_URL")
@click.pass_context
def main(ctx: click.Context, networks: str, storage_url: Optional[str] = None):
    with open(networks, 'rb') as fd:
        network_json = json.load(fd)

    storage = storage_url and Storage(storage_url)
    links = Links(network_json, storage)

    ctx.ensure_object(dict)
    ctx.obj[KEY_LINKS] = links

def build_slack_message(events:list[LinkEvent]) -> str:
    items = []
    for event in events:
        link_str = f'{event.link.src_name} -> {event.link.dst_name}'
        if event.after == Link.GOOD:
            items.append(f'{link_str} : :large_green_circle: *GOOD*')
        else:
            items.append(f'{link_str} : :red_circle: *{event.after.upper()}*')
    return "\n".join(items)

@main.command('monitor')
@click.pass_obj
@click.option('--interval', type=click.INT, default=30.0, envvar="REFRESH_INTERVAL")
@click.option('--slack_hook', type=str, envvar='SLACK_HOOK')
@click.option('--slack_channel', type=str, envvar='SLACK_CHANNEL')
@click.option('--log_file', type=str, envvar="LOG_FILE")
def monitor_status(obj: dict, interval: int = 30, slack_hook: str = None, slack_channel: str = None, log_file: str = None):
    links: Links = obj[KEY_LINKS]
    links.update(True)

    def on_update(changes: List[LinkEvent]):
        if slack_hook is not None and slack_channel is not None:
            msg = {
                'channel': slack_channel,
                'username': 'BTP Monitor',
                'text': build_slack_message(changes)
            }
            requests.post(slack_hook, json=msg)

    app = MonitorApp(links, interval, on_update)
    if log_file is not None:
        with open(log_file, "+at") as fd:
            def on_log(log):
                print(log, file=fd, flush=True)
            app.on_log = on_log
            app.run()
    else:
        app.run()


@main.command('status')
@click.pass_obj
def show_status(obj: dict):
    links: Links = obj[KEY_LINKS]
    btp_status = links.query_status(True)
    known_links = btp_status.get_known_links()

    connected: list[tuple[str,str]] = []
    for link in known_links:
        rlink = (link[1], link[0])
        if rlink in known_links and rlink not in connected:
            connected.append(link)

    click.secho(f'| {"Network":^44s} | {"FW Pending":^10s} | {"BW Pending":^10s} |',reverse=True)
    for conn in connected:
        fw = btp_status.get_link_update(conn[0], conn[1])
        bw = btp_status.get_link_update(conn[1], conn[0])
        fw_pending = fw.tx_seq - fw.rx_seq
        bw_pending = bw.tx_seq - bw.rx_seq
        src_name = links.name_of(conn[0])
        dst_name = links.name_of(conn[1])
        click.echo(f'| {src_name:>20s} -> {dst_name:<20s} | {fw_pending:10d} | {bw_pending:10d} |')

@main.command('web')
@click.pass_obj
def web_server(obj: dict):
    links: Links = obj[KEY_LINKS]

if __name__ == '__main__':
    main()