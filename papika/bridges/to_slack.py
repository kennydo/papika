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
    is_valid = True

    if 'channel' not in message:
        log.error("Required argument 'channel' was missing in message: {0}".format(message))
        is_valid = False

    if 'text' not in message and 'attachments' not in message:
        log.error("One of either 'text' or 'attachments' must be supplied in message: {0}".format(message))
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
                parse=message.get('parse', 'none'),
                link_names=message.get('link_names', '1'),
                attachments=message.get('attachments'),
                unfurl_links=message.get('unfurl_links', 'false'),
                unfurl_media=message.get('unfurl_media', 'true'),
                username=message.get('username', ''),
                as_user=message.get('as_user', 'true'),
                icon_url=message.get('icon_url'),
                icon_emoji=message.get('icon_emoji'),
            )

            if 'text' in message:
                message_as_kwargs['text'] = message['text']

            log.info("Sending message: {0}".format(message_as_kwargs))

            try:
                self.slack_client.api_call(
                    'chat.postMessage',
                    **message_as_kwargs,
                )
            except:
                log.exception("Unable to send message: %s", message)
