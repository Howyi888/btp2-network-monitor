
import json
from typing import Dict, List, Tuple
from urllib.parse import urlparse

import click
import requests

from .cui import MonitorApp
from .monitor import Link, LinkEvent, Links, merge_status, strfdelta

KEY_LINKS = 'links'

@click.group()
@click.option('--networks', metavar='<networks.json>')
@click.pass_context
def main(ctx: click.Context, networks: str):
    with open(networks, 'rb') as fd:
        network_json = json.load(fd)
    links = Links(network_json)

    ctx.ensure_object(dict)
    ctx.obj[KEY_LINKS] = links

def build_blocks_for_slack(links: Links, link_status: Dict[Tuple[str,str],List[Link]]) -> List[any]:
    blocks = []
    blocks.append({
        'type': 'section',
        'fields': [
            {'type': 'mrkdwn', 'text': '*Source*\n*Destination*' },
            {'type': 'mrkdwn', 'text': '*Forward Status*\n*Backward Status*' },
        ],
    })

    def state_to_mrkdwn(link: Link)->str:
        if link.state == Link.GOOD:
            return ':large_green_circle: OK'
        else:
            return f':red_circle: BAD (cnt={link.pending_count},dur={strfdelta(link.pending_duration)})'

    for conn, status in link_status.items():
        src_name = links.name_of(conn[0])
        dst_name = links.name_of(conn[1])
        fw_status = state_to_mrkdwn(status[0])
        bw_status = state_to_mrkdwn(status[1])
        blocks.append({
            'type': 'section',
            'fields': [
                {'type': 'plain_text', 'text': f'{src_name}\n{dst_name}'},
                {'type': 'plain_text', 'text': f'{fw_status}\n{bw_status}' },
            ],
        })
    return blocks


@main.command('monitor')
@click.pass_obj
@click.option('--interval', type=click.INT, default=30)
@click.option('--slack_hook', type=str, envvar='SLACK_HOOK')
@click.option('--slack_channel', type=str, envvar='SLACK_CHANNEL')
@click.option('--log_file', type=str, envvar="LOG_FILE")
def monitor_status(obj: dict, interval: int = 30, slack_hook: str = None, slack_channel: str = None, log_file: str = None):
    links: Links = obj[KEY_LINKS]
    links.update()

    def on_update(changes: List[LinkEvent]):
        if slack_hook is not None and slack_channel is not None:
            items = []
            for c in changes:
                link_str = f'{c.link.src_name} -> {c.link.dst_name}'
                if c.after == Link.GOOD:
                    items.append(f'{link_str} : :large_green_circle: *GOOD*')
                else:
                    items.append(f'{link_str} : :red_circle: *BAD*')
            change_text = "\n".join(items)
            link_status = merge_status(links)
            blocks = build_blocks_for_slack(links, link_status)
            msg = {
                'channel': slack_channel,
                'username': 'BTP Monitor',
                'text': change_text,
                'blocks': blocks,
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
    btp_status = links.query_status()
    link_status = merge_status(btp_status)
    click.secho(f'| {"Network":^44s} | {"FW Pending":^10s} | {"BW Pending":^10s} |',reverse=True)
    for conn, sl in link_status.items():
        fw_pending = sl[0].tx_seq - sl[1].rx_seq
        bw_pending = sl[1].tx_seq - sl[0].rx_seq
        src_name = links.name_of(urlparse(conn[0]).netloc)
        dst_name = links.name_of(urlparse(conn[1]).netloc)
        click.echo(f'| {src_name:>20s} -> {dst_name:<20s} | {fw_pending:10d} | {bw_pending:10d} |')

@main.command('web')
@click.pass_obj
def web_server(obj: dict):
    links: Links = obj[KEY_LINKS]

if __name__ == '__main__':
    main()