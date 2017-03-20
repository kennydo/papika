import logging

from websocket import create_connection

from slackclient._client import SlackClient
from slackclient._server import (
    Server,
    SlackConnectionError,
)


log = logging.getLogger(__name__)


class BlockingServer(Server):
    def connect_slack_websocket(self, ws_url):
        # Override the vanilla Server method to make the websocket socket blocking
        try:
            self.websocket = create_connection(ws_url)
            self.websocket.sock.setblocking(1)
        except:
            raise SlackConnectionError


class BlockingSlackClient(SlackClient):
    def __init__(self, token):
        log.info("Creating a blocking Slack client")
        self.token = token
        self.server = BlockingServer(self.token, False)
