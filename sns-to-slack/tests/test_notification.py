import json
import unittest

from datasets import get_events, DATADOG_EVENTS
from notification import (
    AbstractNotification, CloudWatchNotification, DatadogNotification,
    parse_notifications
)

class TestAbstractNotification(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._events = get_events('cloudwatch')
        cls.notif = parse_notifications(cls._events)[0]

    def test_notification_base_attributes(self):
        assert self.notif.region == 'us-east-1'
        assert self.notif.topic_name == 'production-notices'
        assert self.notif.subject == 'OK: sns-slack-test-from-cloudwatch-total-cpu'

class TestCloudWatchNotification(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._events = get_events('cloudwatch')
        cls.notif = parse_notifications(cls._events)[0]

    def test_parse_notification(self):
        assert isinstance(self.notif, CloudWatchNotification)

    def test_notification_attributes(self):
        assert self.notif.subject == 'OK: sns-slack-test-from-cloudwatch-total-cpu'
        assert self.notif.alarm == 'sns-slack-test-from-cloudwatch-total-cpu'
        assert self.notif.status == 'OK'
        assert self.notif.description is None
        assert self.notif.reason == 'Threshold Crossed: 1 datapoint (7.9053535353535365) was not greater than or equal to the threshold (8.0).'

    def test_slack_attachments(self):
        attachments = self.notif.slack_attachments
        assert len(attachments) == 1
        assert attachments[0]['color'] == 'good'
        assert attachments[0]['fields'][0]['title'] == 'Alarm'
        assert attachments[0]['fields'][0]['value'] == 'sns-slack-test-from-cloudwatch-total-cpu'
        assert attachments[0]['fields'][1]['title'] == 'Status'
        assert attachments[0]['fields'][1]['value'] == 'OK'
        assert attachments[0]['fields'][2]['title'] == 'Description'
        assert attachments[0]['fields'][2]['value'] is None
        assert attachments[0]['fields'][3]['title'] == 'Reason'
        assert attachments[0]['fields'][3]['value'] == 'Threshold Crossed: 1 datapoint (7.9053535353535365) was not greater than or equal to the threshold (8.0).'

class TestDatadogNotification(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._events = get_events('datadog')
        cls.notif = parse_notifications(cls._events)[0]

    def test_parse_notification(self):
        assert isinstance(self.notif, DatadogNotification)

    def test_notification_attributes(self):
        assert self.notif.host == 'host.example.com'
        assert self.notif.status == 'Triggered'

    def test_slack_attachments(self):
        attachments = self.notif.slack_attachments
        assert len(attachments) == 1
        assert attachments[0]['color'] == '#FF0000'
        assert attachments[0]['title'] == 'host.example.com'
