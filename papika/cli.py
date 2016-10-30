import click

import papika.config
from papika.bridges.to_slack import BridgeToSlack


@click.command()
def to_slack():
    config = papika.config.load_from_env_var_path()

    bridge = BridgeToSlack(config)
    bridge.run()
