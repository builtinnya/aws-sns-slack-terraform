#!/usr/bin/env python
#
# Copyright (c) 2017 Naoto Yokoyama
#
# Modifications applied to the original work.
#
#
# Original copyright notice:
#
# Copyright 2015 Robb Wagoner
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
'''
Parse an SNS event message and send to a Slack Channel
'''
import os
import logging
import json
import base64
import requests

from notification import parse_notifications

logging.basicConfig()
logger = logging.getLogger('sns-to-slack')
try:
    logger.setLevel(os.environ.get('LOG_LEVEL', 'INFO').upper())
except AttributeError:
    logger.setLevel('INFO')

def lambda_handler(event, context):
    '''The Lambda function handler
    '''
    logger.debug("Event received: %s", event)
    config = {
        'webhook_url': os.environ['WEBHOOK_URL'],
        'channel_map': json.loads(base64.b64decode(os.environ['CHANNEL_MAP']))
    }

    notifications = parse_notifications(event)
    logger.debug("%s notification(s) parsed from event", len(notifications))
    webhook_url = "https://" + config['webhook_url']
    channel_map = config['channel_map']

    status_codes = []
    for notification in notifications:
        payload = {
            'text': notification.message,
            'channel': channel_map.get(notification.topic_name, notification.DEFAULT_CHANNEL),
            'username': notification.USERNAME if notification.USERNAME else notification.DEFAULT_USERNAME,
            'as_user': False,
            'icon_emoji': notification.get_emoji()
        }
        if notification.slack_attachments:
            payload['attachments'] = notification.slack_attachments
        req = requests.post(webhook_url, json=payload)
        status_codes += [req.status_code]
        if req.status_code == 200:
            logger.info("Message processed %s", notification.message_id)
    return status_codes

# Test locally
if __name__ == '__main__':
    from argparse import ArgumentParser
    from tests import datasets

    parser = ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--cloudwatch', action='store_true', help='Launch the test script with a CloudWatch event')
    group.add_argument('--datadog', action='store_true', help='Launch the test script with a Datadog event')
    group.add_argument('--ssl-check', action='store_true', help='Launch the test script with SSL check event')
    group.add_argument('--backup-check', action='store_true', help= 'Launch the test script with backup check event')
    args = parser.parse_args()

    if args.cloudwatch:
        sns_template = datasets.CLOUDWATCH_EVENTS
    elif args.datadog:
        sns_template = datasets.DATADOG_EVENTS
    elif args.ssl_check:
        sns_template = datasets.SSL_CHECK_EVENTS
    elif args.backup_check:
        sns_template = datasets.BACKUP_CHECKER_EVENTS
    else:
        parser.error('One event type must be provided [--cloudwatch | --datadog | --ssl-check | --backup-check]')

    logger.info('running locally')
    logger.info(lambda_handler(sns_template, None))
