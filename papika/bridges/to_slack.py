import json
import logging
from typing import (
    Any,
    Dict,
)

import kafka
import slackclient

from papika.bridges import Bridge


log = logging.getLogger(__name__)


def is_valid_message(message: Dict[str, Any]) -> bool:
    required_arguments = [
        'channel',
        'text',
    ]
    is_valid = True

    for arg in required_arguments:
        if arg not in message:
            log.error("Required argument {0} was missing in message: {1}".format(arg, message))
            is_valid = False

    return is_valid


class BridgeToSlack(Bridge):
    def __init__(self, config: Dict[str, Any]) -> None:
        token = config['slack']['api_token']

        self.slack_client = slackclient.SlackClient(token)

        self.kafka_consumer = kafka.KafkaConsumer(
            config['kafka']['to_slack']['topic'],
            bootstrap_servers=config['kafka']['bootstrap_servers'],
            group_id=config['kafka']['to_slack']['group_id'],
        )

    def run(self) -> None:
        auth_test = self.slack_client.api_call('auth.test')
        if auth_test['ok']:
            log.info("Successfully authenticated with Slack: {0}".format(auth_test))
        else:
            log.error("Could not authenticate to Slack: {0}".format(auth_test))
            raise ValueError("Invalid Slack token")

        for event in self.kafka_consumer:
            try:
                raw_message = event.value.decode('utf-8')
            except UnicodeDecodeError:
                log.exception("Could not decode: {0}".format(event.value))
                continue

            try:
                message = json.loads(raw_message)
            except json.JSONDecodeError:
                log.exception("Could not parse as JSON: {0}".format(raw_message))
                continue

            if not is_valid_message(message):
                log.error("Received invalid message, skipping: {0}".format(message))
                continue

            message_as_kwargs = dict(
                channel=message['channel'],
                text=message['text'],
                parse=message.get('parse', 'none'),
                link_names=message.get('link_names', '1'),
                unfurl_links=message.get('unfurl_links', 'false'),
                unfurl_media=message.get('unfurl_media', 'true'),
                username=message.get('username', ''),
                as_user=message.get('as_user', 'true'),
                icon_url=message.get('icon_url'),
                icon_emoji=message.get('icon_emoji'),
            )
            log.info("Sending message: {0}".format(message_as_kwargs))

            self.slack_client.api_call(
                'chat.postMessage',
                **message_as_kwargs,
            )
