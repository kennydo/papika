import asyncio
import click

import papika.config
from papika.bridges.from_slack import BridgeFromSlack
from papika.bridges.to_slack import BridgeToSlack


@click.command()
def from_slack():
    config = papika.config.load_from_env_var_path()

    bridge = BridgeFromSlack(config)
    bridge.run()


@click.command()
def to_slack():
    config = papika.config.load_from_env_var_path()

    bridge = BridgeToSlack(config)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(bridge.run())
