import json
import logging
import time
from typing import (
    Any,
    Dict,
    Iterable,
)

import kafka
import slackclient

from papika.bridges import Bridge


log = logging.getLogger(__name__)


#: We don't care about forwarding these Slack events into Kafka
SLACK_EVENT_TYPE_BLACKLIST = set([
    'goodbye',
    'hello',
    'reconnect_url',
])


def yield_events_from_slack_client(sc: slackclient.SlackClient) -> Iterable[Dict[str, Any]]:
    while True:
        events = sc.rtm_read()
        for event in events:
            if event.get('type') not in SLACK_EVENT_TYPE_BLACKLIST:
                yield event

        time.sleep(1)


class BridgeFromSlack(Bridge):
    def __init__(self, config: Dict[str, Any]) -> None:
        token = config['slack']['api_token']
        self.slack_client = slackclient.SlackClient(token)

        self.destination_kafka_topic = config['kafka']['from_slack']['topic']
        self.kafka_producer = kafka.KafkaProducer(
            bootstrap_servers=config['kafka']['bootstrap_servers'],
        )

    def run(self) -> None:
        if self.slack_client.rtm_connect():
            log.info("Successfully authenticated with Slack")
        else:
            log.error("Could not authenticate to Slack")
            raise ValueError("Invalid Slack token")

        for event in yield_events_from_slack_client(self.slack_client):
            log.debug("Received Slack event: {0}".format(event))

            value = {
                'timestamp': time.time(),
                'event': event,
            }

            value = json.dumps(value).encode('utf-8')

            log.info("Sending to Kafka: {0}".format(value))

            self.kafka_producer.send(
                self.destination_kafka_topic,
                value=value,
            )
