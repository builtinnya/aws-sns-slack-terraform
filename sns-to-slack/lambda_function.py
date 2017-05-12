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
from __future__ import print_function

import os
import json
import base64
import re
import requests

from base64 import b64decode

__author__ = "Robb Wagoner (@robbwagoner)"
__copyright__ = "Copyright 2015 Robb Wagoner"
__credits__ = ["Robb Wagoner"]
__license__ = "Apache License, 2.0"
__version__ = "0.1.2"
__maintainer__ = "Robb Wagoner"
__email__ = "robb@pandastrike.com"
__status__ = "Production"

DEFAULT_USERNAME = os.environ.get('DEFAULT_USERNAME', 'AWS Lambda')
DEFAULT_CHANNEL = os.environ.get('DEFAULT_CHANNEL', '#webhook-tests')


def get_slack_emoji(event_src, topic_name, event_cond='default'):
    '''Map an event source, severity, and condition to an emoji
    '''
    emoji_map = {
        'autoscaling': {
            'notices': {'default': ':scales:'}},
        'cloudwatch': {
            'notices': {
                'ok': ':ok:',
                'alarm': ':fire:',
                'insuffcient_data': ':question:'},
            'alerts': {
                'ok': ':ok:',
                'alarm': ':fire:',
                'insuffcient_data': ':question:'}},
        'elasticache': {
            'notices': {'default': ':stopwatch:'}},
        'rds': {
            'notices': {'default': ':registered:'}}}

    try:
        return emoji_map[event_src][topic_name][event_cond]
    except KeyError:
        if topic_name == 'alerts':
            return ':fire:'
        else:
            return ':information_source:'


def get_slack_username(event_src):
    '''Map event source to the Slack username
    '''
    username_map = {
        'cloudwatch': 'AWS CloudWatch',
        'autoscaling': 'AWS AutoScaling',
        'elasticache': 'AWS ElastiCache',
        'rds': 'AWS RDS'}

    try:
        return username_map[event_src]
    except KeyError:
        return DEFAULT_USERNAME


def get_slack_channel(region, event_src, topic_name, channel_map):
    '''Map region and event type to Slack channel name
    '''
    try:
        return channel_map[topic_name]
    except KeyError:
        return DEFAULT_CHANNEL


def autoscaling_capacity_change(cause):
    '''
    '''
    s = re.search(r'capacity from (\w+ to \w+)', cause)
    if s:
        return s.group(0)


def lambda_handler(event, context):
    '''The Lambda function handler
    '''
    config = {
      'webhook_url': os.environ['WEBHOOK_URL'],
      'channel_map': json.loads(base64.b64decode(os.environ['CHANNEL_MAP']))
    }

    event_cond = 'default'
    sns = event['Records'][0]['Sns']
    print('DEBUG:', sns['Message'])
    json_msg = json.loads(sns['Message'])

    if sns['Subject']:
        message = sns['Subject']
    else:
        message = sns['Message']

    # https://api.slack.com/docs/attachments
    attachments = []
    if json_msg.get('AlarmName'):
        event_src = 'cloudwatch'
        event_cond = json_msg['NewStateValue']
        color_map = {
            'OK': 'good',
            'INSUFFICIENT_DATA': 'warning',
            'ALARM': 'danger'
        }
        attachments = [{
            'fallback': json_msg,
            'message': json_msg,
            'color': color_map[event_cond],
            "fields": [{
                "title": "Alarm",
                "value": json_msg['AlarmName'],
                "short": True
            }, {
                "title": "Status",
                "value": json_msg['NewStateValue'],
                "short": True
            }, {
                "title": "Reason",
                "value": json_msg['NewStateReason'],
                "short": False
            }]
        }]
    elif json_msg.get('Cause'):
        event_src = 'autoscaling'
        attachments = [{
            "text": "Details",
            "fallback": message,
            "color": "good",
            "fields": [{
                "title": "Capacity Change",
                "value": autoscaling_capacity_change(json_msg['Cause']),
                "short": True
            }, {
                "title": "Event",
                "value": json_msg['Event'],
                "short": False
            }, {
                "title": "Cause",
                "value": json_msg['Cause'],
                "short": False
            }]
        }]
    elif json_msg.get('ElastiCache:SnapshotComplete'):
        event_src = 'elasticache'
        attachments = [{
            "text": "Details",
            "fallback": message,
            "color": "good",
            "fields": [{
                "title": "Event",
                "value": "ElastiCache Snapshot"
            }, {
                "title": "Message",
                "value": "Snapshot Complete"
            }]
        }]
    elif re.match("RDS", sns.get('Subject') or ''):
        event_src = 'rds'
        attachments = [{
            "fields": [{
                "title": "Source",
                "value": json_msg['Event Source']
                },{
                "title": "Message",
                "value": json_msg['Event Message']
                }]}]
        if json_msg.get('Identifier Link'):
            attachments.append({
                "text": "Details",
                "title": json_msg['Identifier Link'].split('\n')[1],
                "title_link": json_msg['Identifier Link'].split('\n')[0]})
    else:
        event_src = 'other'

    # SNS Topic ARN: arn:aws:sns:<REGION>:<AWS_ACCOUNT_ID>:<TOPIC_NAME>
    #
    # SNS Topic Names => Slack Channels
    #  <env>-alerts => alerts-<region>
    #  <env>-notices => events-<region>
    #
    region = sns['TopicArn'].split(':')[3]
    topic_name = sns['TopicArn'].split(':')[-1]
    # event_env = topic_name.split('-')[0]
    # event_sev = topic_name.split('-')[1]

    # print('DEBUG:', topic_name, region, event_env, event_sev, event_src)

    WEBHOOK_URL = "https://" + config['webhook_url']

    channel_map = config['channel_map']

    payload = {
        'text': message,
        'channel': get_slack_channel(region, event_src, topic_name, channel_map),
        'username': get_slack_username(event_src),
        'icon_emoji': get_slack_emoji(event_src, topic_name, event_cond.lower())}
    if attachments:
        payload['attachments'] = attachments
    print('DEBUG:', payload)
    r = requests.post(WEBHOOK_URL, json=payload)
    return r.status_code

# Test locally
if __name__ == '__main__':
    sns_event_template = json.loads(r"""
{
  "Records": [
    {
      "EventVersion": "1.0",
      "EventSubscriptionArn": "arn:aws:sns:EXAMPLE",
      "EventSource": "aws:sns",
      "Sns": {
        "SignatureVersion": "1",
        "Timestamp": "1970-01-01T00:00:00.000Z",
        "Signature": "EXAMPLE",
        "SigningCertUrl": "EXAMPLE",
        "MessageId": "95df01b4-ee98-5cb9-9903-4c221d41eb5e",
        "Message": "{\"AlarmName\":\"sns-slack-test-from-cloudwatch-total-cpu\",\"AlarmDescription\":null,\"AWSAccountId\":\"123456789012\",\"NewStateValue\":\"OK\",\"NewStateReason\":\"Threshold Crossed: 1 datapoint (7.9053535353535365) was not greater than or equal to the threshold (8.0).\",\"StateChangeTime\":\"2015-11-09T21:19:43.454+0000\",\"Region\":\"US - N. Virginia\",\"OldStateValue\":\"ALARM\",\"Trigger\":{\"MetricName\":\"CPUUtilization\",\"Namespace\":\"AWS/EC2\",\"Statistic\":\"AVERAGE\",\"Unit\":null,\"Dimensions\":[],\"Period\":300,\"EvaluationPeriods\":1,\"ComparisonOperator\":\"GreaterThanOrEqualToThreshold\",\"Threshold\":8.0}}",
        "MessageAttributes": {
          "Test": {
            "Type": "String",
            "Value": "TestString"
          },
          "TestBinary": {
            "Type": "Binary",
            "Value": "TestBinary"
          }
        },
        "Type": "Notification",
        "UnsubscribeUrl": "EXAMPLE",
        "TopicArn": "arn:aws:sns:us-east-1:123456789012:production-notices",
        "Subject": "OK: sns-slack-test-from-cloudwatch-total-cpu"
      }
    }
  ]
}""")
    print('running locally')
    print(lambda_handler(sns_event_template, None))
