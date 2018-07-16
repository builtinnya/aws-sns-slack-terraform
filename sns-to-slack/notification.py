from abc import ABCMeta, abstractmethod
import json
import re
import os

def parse_notifications(events):
    notifications = []
    for record in events.get('Records', []):
        event = record['Sns']
        if event.get('Type') == 'Notification':
            try:
                message = json.loads(event['Message'])
                if message.get('AlarmName'):
                    notifications += [CloudWatchNotification(event)]
                elif message.get('Cause'):
                    notifications += [AutoScalingNotification(event)]
                elif message.get('ElastiCache:SnapshotComplete'):
                    notifications += [ElastiCacheNotification(event)]
                elif message.get('source') == 'aws.codepipeline':
                    notifications += [CodePipelineNotification(event)]
                elif 'RDS' in event.get('Subject', ''):
                    notifications += [RDSNotification(event)]
                elif 'SSL Expiration Check' in event.get('Subject', ''):
                    notifications += [SSLExpirationNotification(event)]
                elif 'Backup checker':
                    notifications += [BackupCheckerNotification(event)]
            except ValueError:
                if 'app.datadoghq.com' in event.get('Message'):
                    notifications += [DatadogNotification(event)]
    return notifications

class AbstractNotification:
    __metaclass__ = ABCMeta

    DEFAULT_USERNAME = os.environ.get('DEFAULT_USERNAME', 'AWS Lambda')
    DEFAULT_CHANNEL = os.environ.get('DEFAULT_CHANNEL', '#webhook-tests')
    DEFAULT_EMOJI = os.environ.get('DEFAULT_EMOJI', ':information_source:')
    DEFAULT_EVENT_COND = 'default'

    USERNAME = None
    EMOJI_MAP = {}

    def __init__(self, event):
        self._event = event
        self._message_id = event['MessageId']
        self._event_cond = self.DEFAULT_EVENT_COND
        try:
            self._message = json.loads(event['Message'])
        except ValueError:
            self._message = event['Message']
        self._subject = event.get('Subject', self._message)
        self._topic_arn = event.get('TopicArn')

    @property
    @abstractmethod
    def slack_attachments(self):
        pass

    @abstractmethod
    def _get_color(self):
        pass

    def get_emoji(self):
        try:
            return self.EMOJI_MAP[self.topic_type][self._event_cond]
        except KeyError:
            if 'alerts' in self.topic_name:
                return ':fire:'
            return self.DEFAULT_EMOJI

    @property
    def region(self):
        return self._topic_arn.split(':')[3]

    @property
    def topic_name(self):
        return self._topic_arn.split(':')[-1]

    @property
    def topic_type(self):
        matches = re.search(r'(notices|alerts)', self.topic_name)
        if matches:
            return matches.groups()[0]
        return 'default'

    @property
    def subject(self):
        return self._subject

    @property
    def message(self):
        return self._message

    @property
    def message_id(self):
        return self._message_id

class AutoScalingNotification(AbstractNotification):

    USERNAME = 'AWS AutoScaling'
    EMOJI_MAP = {
        'notices': {'default': ':scales:'}
    }

    def __init__(self, event):
        super(AutoScalingNotification, self).__init__(event)
        self._event = self._message['Event']
        self._cause = self._message['Cause']

    def _get_color(self):
        return 'good'

    @property
    def slack_attachments(self):
        return [
            {
                "text": "Details",
                "fallback": self._message,
                "color": self._get_color(),
                "fields": [
                    {
                        "title": "Capacity Change",
                        "value": self.capacity_change,
                        "short": True
                    }, {
                        "title": "Event",
                        "value": self._event,
                        "short": False
                    }, {
                        "title": "Cause",
                        "value": self._cause,
                        "short": False
                    }
                ]
            }
        ]

    @property
    def capacity_change(self):
        matches = re.search(r'capacity from (\w+ to \w+)', self._cause)
        if matches:
            return matches.group(0)

class CloudWatchNotification(AbstractNotification):

    USERNAME = 'AWS CloudWatch'
    EMOJI_MAP = {
        'notices': {
            'ok': ':ok:',
            'alarm': ':fire:',
            'insuffcient_data': ':question:'
        },
        'alerts': {
            'ok': ':ok:',
            'alarm': ':fire:',
            'insuffcient_data': ':question:'
        }
    }

    def __init__(self, event):
        super(CloudWatchNotification, self).__init__(event)
        self._event_cond = self._message['NewStateValue'].lower()
        self._alarm = self._message['AlarmName']
        self._status = self._message['NewStateValue']
        self._description = self._message['AlarmDescription']
        self._reason = self._message['NewStateReason']

    def _get_color(self):
        color_map = {
            'ok': 'good',
            'insuffcient_data': 'warning',
            'alarm': 'danger'
        }
        return color_map[self._event_cond]

    @property
    def slack_attachments(self):
        return [
            {
                'fallback': self._message,
                'message': self._message,
                'color': self._get_color(),
                "fields": [
                    {
                        "title": "Alarm",
                        "value": self._alarm,
                        "short": True
                    },
                    {
                        "title": "Status",
                        "value": self._status,
                        "short": True
                    },
                    {
                        "title": "Description",
                        "value": self._description,
                        "short": False
                    },
                    {
                        "title": "Reason",
                        "value": self._reason,
                        "short": False
                    }
                ]
            }
        ]

    @property
    def alarm(self):
        return self._alarm

    @property
    def status(self):
        return self._status

    @property
    def description(self):
        return self._description

    @property
    def reason(self):
        return self._reason

class ElastiCacheNotification(AbstractNotification):

    USERNAME = 'AWS ElastiCache'
    EMOJI_MAP = {
        'notices': {'default': ':stopwatch:'}
    }

    def __init__(self, event):
        super(ElastiCacheNotification, self).__init__(self)
        self._event = 'ElastiCache Snapshot'
        self._display_message = 'Snapshot Complete'

    def _get_color(self):
        return 'good'

    @property
    def slack_attachments(self):
        return [
            {
                "text": "Details",
                "fallback": self._message,
                "color": self._get_color(),
                "fields": [{
                    "title": "Event",
                    "value": "ElastiCache Snapshot"
                }, {
                    "title": "Message",
                    "value": "Snapshot Complete"
                }]
            }
        ]

class RDSNotification(AbstractNotification):

    USERNAME = 'AWS RDS'
    EMOJI_MAP = {
        'notices': {'default': ':registered:'}
    }

    def __init__(self, event):
        super(RDSNotification, self).__init__(event)
        self._event_source = self._message['Event Source']
        self._event_message = self._message['Event Message']
        self._source_id = self._message['Source ID']
        self._identifier_link = self._message.get('Identifier Link')

    def _get_color(self):
        pass

    @property
    def slack_attachments(self):
        attachments = [
            {
                "fields": [
                    {
                        "title": "Source",
                        "value": "{0} '{1}'".format(self._event_source, self._source_id)
                    }, {
                        "title": "Message",
                        "value": self._event_message
                    }
                ]
            }
        ]
        if self._identifier_link:
            title_arr = self._identifier_link.split('\n')
            if len(title_arr) >= 2:
                title_str = title_arr[1]
                title_lnk_str = title_arr[0]
            else:
                title_str = title_lnk_str = title_arr[0]
            attachments[0]['fields'].append({
                "title": "Details",
                "value": "<{0}|{1}>".format(title_str, title_lnk_str)
            })
        return attachments

class CodePipelineNotification(AbstractNotification):

    USERNAME = 'AWS CodePipeline'
    EMOJI_MAP = {
        'notices': {
            'default': ':datadog:'
        }
    }

    def __init__(self, event):
        super(CodePipelineNotification, self).__init__(event)
        self._event_cond = self._message['detail']['state']
        self._pipeline = self._message['detail']['pipeline']
        self._state = self._message['detail']['state']
        self._display_message = self._message['detail-type']

    def _get_color(self):
        return {
            'STARTED': 'good',
            'SUCCEEDED': 'good',
            'FAILED': 'danger'
        }[self._event_cond]

    @property
    def slack_attachments(self):
        return [
            {
                'fallback': self._display_message,
                'color': self._get_color(),
                'fields': [
                    {
                        'title': 'Pipeline',
                        'value': self._pipeline
                    }, {
                        'title': 'State',
                        'value': self._state
                    }
                ]
            }
        ]

class DatadogNotification(AbstractNotification):

    USERNAME = 'Datadog'
    EMOJI_MAP = {
        'notices' : {
            'default': ':datadog:'
        }
    }

    def __init__(self, event):
        super(DatadogNotification, self).__init__(event)
        matches = re.search(r'Event URL: (\S*)', self._message)
        self._event_url = matches.groups()[0] if matches else None
        self._message = '<{}|{}>\n\n'.format(self._event_url, self._subject) + re.sub(r'\sMonitor Status.*', r'', self._message)

    def _get_color(self):
        return {
            'Recovered': '#008000',
            'Warn': '#FF8C00',
            'Triggered': '#FF0000'
        }[self.status]

    @property
    def slack_attachments(self):
        attachments = [
            {
                'fallback': self._message,
                'color': self._get_color(),
                'title': self.host,
                'fields': [
                    {
                        'title': 'Alarm',
                        'value': 'Datadog'
                    }, {
                        'title': 'Status',
                        'value': self.status
                    }, {
                        'title': 'Host',
                        'value': self.host
                    }
                ]
            }
        ]
        return attachments

    @property
    def status(self):
        matches = re.search(r'\[(\w+)\]', self._subject)
        if matches:
            return matches.groups()[0]

    @property
    def host(self):
        matches = re.search(r'host:([A-Za-z0-9\.-]*)', self._message)
        if matches:
            return matches.groups()[0]

class SSLExpirationNotification(AbstractNotification):

    USERNAME = 'SSL Production Expiry Checker'
    EMOJI_MAP = {
        'notices' : {
            'default': ':supersurycat:'
        }
    }

    def __init__(self, event):
        super(SSLExpirationNotification, self).__init__(event)
        self._hostname = self._message['hostname']
        self._display_message = self._message['message']
        self._priority = self._message['priority']

    def _get_color(self):
        return {
            'Critical': '#FF0000',
            'High': '#FF8C00',
            'Low': '#008000'
        }[self._priority]

    def _get_marker_emoji(self):
        return {
            'Critical': ':rotating_light:',
            'High': ':warning:',
            'Low': ''
        }[self._priority]

    @property
    def slack_attachments(self):
        if self._priority in ('Critical', 'High'):
            title = self._hostname
            title_link = 'https://' + title
            fallback = self._display_message
            marker_emoji = self._get_marker_emoji()
            pretext = 'Certificate will expire soon. Have a look at it!' if self._priority == 'High' else 'Error while validating certificate.'
            pretext = "{0} {1} {2}".format(marker_emoji, pretext, marker_emoji)
            fields = [
                {
                    "title": "Priority",
                    "value": self._priority,
                    "short": False
                },
                {
                    "title": "Reason",
                    "value": self._display_message,
                    "short": False
                }
            ]
        elif self._priority == 'Low':
            title = ':white_check_mark: :scroll:'
            title_link = None
            fallback = self._display_message
            pretext = None
            fields = [
                {
                    "title": "Priority",
                    "value": self._priority,
                    "short": False
                }
            ]
        return [{
            "fallback": fallback,
            "color": self._get_color(),
            "pretext": pretext,
            "title": title,
            "title_link": title_link,
            "fields": fields
        }]

    @property
    def priority(self):
        return self._priority

    @property
    def display_message(self):
        return self._display_message

    @property
    def hostname(self):
        return self._hostname

    @property
    def message(self):
        return self._display_message

class BackupCheckerNotification(AbstractNotification):

    USERNAME = 'Backup checker'
    EMOJI_MAP = {
        'notices' : {
            'default': ':open_file_folder:'
        }
    }

    def __init__(self, event):
        super(BackupCheckerNotification, self).__init__(event)
        self._hostname = self._message['hostname']
        self._display_message = self._message['message']
        self._priority = self._message['priority']

    def _get_color(self):
        return {
            'Critical': '#FF0000',
            'Low': '#008000'
        }[self._priority]

    @property
    def slack_attachments(self):
        base = {
            "title": self._hostname,
            "title_link": "https://" + self._hostname,
            "fallback": self._display_message,
            "color": self._get_color(),
            "fields": [{
                "title": "Priority",
                "value": self._priority,
                "short": False
            }, {
                "title": "Reason",
                "value": self._display_message,
                "short": False
            }]
        }
        return [base]

    @property
    def priority(self):
        return self._priority

    @property
    def display_message(self):
        return self._display_message

    @property
    def hostname(self):
        return self._hostname

    @property
    def message(self):
        return self._display_message
