import unittest

from datasets import get_events
from notification import (
    CloudWatchNotification, DatadogNotification, SSLExpirationNotification,
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
        assert self.notif.message_id == '95df01b4-ee98-5cb9-9903-4c221d41eb5e'

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

    def test_get_emoji(self):
        assert self.notif.get_emoji() == ':ok:'

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

    def test_get_emoji(self):
        assert self.notif.get_emoji() == ':datadog:'

    def test_message_contains_link_to_event(self):
        assert 'https://app.datadoghq.com/event/event?id=443703058061736990' in self.notif.message

class TestSSLExpirationNotification(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._events = get_events('ssl_check')
        cls.notifs = parse_notifications(cls._events)
        cls.nominal = cls.notifs[0]
        cls.warn = cls.notifs[1]
        cls.critical = cls.notifs[2]

    def test_parse_notification(self):
        assert isinstance(self.nominal, SSLExpirationNotification)

    def test_notification_attributes(self):
        assert self.nominal.priority == 'Low'
        assert self.nominal.display_message == 'All certificates are valid.'
        assert self.nominal.hostname is None

        assert self.warn.priority == 'High'
        assert self.warn.display_message == '28 days left'
        assert self.warn.hostname == 'fake.hostname.dummy'

        assert self.critical.priority == 'Critical'
        assert self.critical.display_message == 'Broken pipe'
        assert self.critical.hostname == 'fake.hostname.dummy'

    def test_slack_attachments(self):
        assert self.nominal.slack_attachments[0]['title'] == ':white_check_mark: :scroll:'
        assert self.nominal.slack_attachments[0]['title_link'] is None
        assert self.nominal.slack_attachments[0]['pretext'] is None
        assert self.nominal.slack_attachments[0]['color'] == '#008000'
        assert self.nominal.slack_attachments[0]['fields'][0]['value'] == 'Low'

        assert self.warn.slack_attachments[0]['title'] == 'fake.hostname.dummy'
        assert self.warn.slack_attachments[0]['title_link'] == 'https://fake.hostname.dummy'
        assert self.warn.slack_attachments[0]['pretext'] == ':warning: Certificate will expire soon. Have a look at it! :warning:'
        assert self.warn.slack_attachments[0]['color'] == '#FF8C00'
        assert self.warn.slack_attachments[0]['fields'][0]['value'] == 'High'
        assert self.warn.slack_attachments[0]['fields'][1]['value'] == '28 days left'

        assert self.critical.slack_attachments[0]['title'] == 'fake.hostname.dummy'
        assert self.critical.slack_attachments[0]['title_link'] =='https://fake.hostname.dummy'
        assert self.critical.slack_attachments[0]['pretext'] == ':rotating_light: Error while validating certificate. :rotating_light:'
        assert self.critical.slack_attachments[0]['color'] == '#FF0000'
        assert self.critical.slack_attachments[0]['fields'][0]['value'] == 'Critical'
        assert self.critical.slack_attachments[0]['fields'][1]['value'] == 'Broken pipe'

    def test_get_emoji(self):
        assert self.nominal.get_emoji() == ':supersurycat:'
