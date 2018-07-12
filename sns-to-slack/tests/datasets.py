import json

CLOUDWATCH_EVENTS = json.loads(r"""
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

DATADOG_EVENTS = json.loads(r"""
{
"Records": [
{
  "Sns": {
    "SignatureVersion": "1",
    "SigningCertURL": "EXAMPLE",
    "MessageId": "1e675b29-113a-5eb5-9a67-08b184f8e515",
    "Timestamp": "2018-06-11T15:21:38.646Z",
    "Message": "@sns-system-health edited\n\ndocker.cpu.usage over docker_image:nginx,host:host.example.com,environment:production was > 0.1 on average during the last 1m.\n\nMetric value: 0.21\n\nMonitor Status: https:\/\/app.datadoghq.com\/monitors#5203057?group=docker_image%3Anginx \u00b7 Edit Monitor: https:\/\/app.datadoghq.com\/monitors#5203057\/edit \u00b7 Event URL: https:\/\/app.datadoghq.com\/event\/event?id=4437030580617369909 \u00b7 Related Logs: https:\/\/app.datadoghq.com\/logs?query=",
    "Signature": "EXAMPLE",
    "Type": "Notification",
    "TopicArn": "arn:aws:sns:eu-west-1:123456789012:system-health-notices",
    "Subject": "[Triggered] CPU Load"
  }
},
{
  "Sns": {
    "SignatureVersion": "1",
    "SigningCertURL": "EXAMPLE",
    "MessageId": "1e675b29-113a-5eb5-9a67-08b184f8e515",
    "Timestamp": "2018-06-11T15:21:38.646Z",
    "Message": "@sns-system-health edited\n\ndocker.cpu.usage over docker_image:nginx,host:host.example.com,environment:production was > 0.1 on average during the last 1m.\n\nMetric value: 0.21\n\nMonitor Status: https:\/\/app.datadoghq.com\/monitors#5203057?group=docker_image%3Anginx \u00b7 Edit Monitor: https:\/\/app.datadoghq.com\/monitors#5203057\/edit \u00b7 Event URL: https:\/\/app.datadoghq.com\/event\/event?id=4437030580617369909 \u00b7 Related Logs: https:\/\/app.datadoghq.com\/logs?query=",
    "Signature": "EXAMPLE",
    "Type": "Notification",
    "TopicArn": "arn:aws:sns:eu-west-1:123456789012:system-health-notices",
    "Subject": "[Warn] CPU Load"
  }
},
{
  "Sns": {
    "SignatureVersion": "1",
    "SigningCertURL": "EXAMPLE",
    "MessageId": "1e675b29-113a-5eb5-9a67-08b184f8e515",
    "Timestamp": "2018-06-11T15:21:38.646Z",
    "Message": "@sns-system-health edited\n\ndocker.cpu.usage over docker_image:nginx,host:host.example.com,environment:production was > 0.1 on average during the last 1m.\n\nMetric value: 0.21\n\nMonitor Status: https:\/\/app.datadoghq.com\/monitors#5203057?group=docker_image%3Anginx \u00b7 Edit Monitor: https:\/\/app.datadoghq.com\/monitors#5203057\/edit \u00b7 Event URL: https:\/\/app.datadoghq.com\/event\/event?id=4437030580617369909 \u00b7 Related Logs: https:\/\/app.datadoghq.com\/logs?query=",
    "Signature": "EXAMPLE",
    "Type": "Notification",
    "TopicArn": "arn:aws:sns:eu-west-1:123456789012:system-health-notices",
    "Subject": "[Recovered] CPU Load"
  }
}
]
}""")

SSL_CHECK_EVENTS = json.loads(r"""
{
"Records": [
{
  "Sns": {
    "MessageId": "1e675b29-113a-5eb5-9a67-08b184f8e515",
    "Timestamp": "2018-06-11T15:21:38.646Z",
    "Message": "{\"hostname\":null, \"message\":\"All certificates are valid.\", \"priority\":\"Low\"}",
    "Type": "Notification",
    "TopicArn": "arn:aws:sns:eu-west-1:123456789012:system-health-notices",
    "Subject": "SSL Expiration Check"
  }
},
{
  "Sns": {
    "MessageId": "1e675b29-113a-5eb5-9a67-08b184f8e515",
    "Timestamp": "2018-06-11T15:21:38.646Z",
    "Message": "{\"hostname\":\"fake.hostname.dummy\", \"message\":\"28 days left\", \"priority\":\"High\"}",
    "Type": "Notification",
    "TopicArn": "arn:aws:sns:eu-west-1:123456789012:system-health-notices",
    "Subject": "SSL Expiration Check"
  }
},
{
  "Sns": {
    "MessageId": "1e675b29-113a-5eb5-9a67-08b184f8e515",
    "Timestamp": "2018-06-11T15:21:38.646Z",
    "Message": "{\"hostname\":\"fake.hostname.dummy\", \"message\":\"Broken pipe\", \"priority\":\"Critical\"}",
    "Type": "Notification",
    "TopicArn": "arn:aws:sns:eu-west-1:123456789012:system-health-notices",
    "Subject": "SSL Expiration Check"
  }
}
]
}""")


BACKUP_CHECKER_EVENTS = json.loads(r"""
{
"Records": [
{
  "Sns": {
    "MessageId": "1e675b29-113a-5eb5-9a67-08b184f8e515",
    "Timestamp": "2018-06-11T15:21:38.646Z",
    "Message": "{\"hostname\":\"fake.hostname.dummy\", \"message\":\"Backups ran smoothly\", \"priority\":\"Low\"}",
    "Type": "Notification",
    "TopicArn": "arn:aws:sns:eu-west-1:123456789012:system-health-notices",
    "Subject": "Backup checker"
  }
},
{
  "Sns": {
    "MessageId": "1e675b29-113a-5eb5-9a67-08b184f8e515",
    "Timestamp": "2018-06-11T15:21:38.646Z",
    "Message": "{\"hostname\":\"fake.hostname.dummy\", \"message\":\"Backup not performed for mongo\", \"priority\":\"Critical\"}",
    "Type": "Notification",
    "TopicArn": "arn:aws:sns:eu-west-1:123456789012:system-health-notices",
    "Subject": "Backup checker"
  }
}
]
}""")

def get_events(event_type):
    if event_type == 'cloudwatch':
        return CLOUDWATCH_EVENTS
    elif event_type == 'datadog':
        return DATADOG_EVENTS
    elif event_type == 'ssl_check':
        return SSL_CHECK_EVENTS
    elif event_type == 'backup_check':
        return BACKUP_CHECKER_EVENTS
