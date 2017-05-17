# aws-sns-slack-terraform

![Minimal CloudWatch Screenshot](screenshots/minimal-cloudwatch-screenshot.png)

This is a [Terraform](https://www.terraform.io/) module which maps an AWS SNS topic name to a Slack channel.
The AWS Lambda function code it uses is derived from [robbwagoner/aws-lambda-sns-to-slack](https://github.com/robbwagoner/aws-lambda-sns-to-slack).

The supported features are:

- Posting AWS SNS notifications to Slack channels
- Building necessary AWS resources by Terraform automatically
- Customizable topic-to-channel map

## Usage

aws-sns-slack-terraform is a [Terraform module](https://www.terraform.io/docs/modules/index.html).
You just need to include the module in one of your Terraform scripts and set up SNS topics and permissions.
See [examples/](/examples) for concrete examples.

```hcl
module "sns_to_slack" {
  source = "github.com/builtinnya/aws-sns-slack-terraform/module"

  slack_webhook_url = "hooks.slack.com/services/XXXXXXXXX/XXXXXXXXX/XXXXXXXXXXXXXXXXXXXXXXXX"
  slack_channel_map = "{ \"topic-name\": \"#slack-channel\" }"

  # The following variables are optional.
  lambda_function_name = "sns-to-slack"
  default_username = "AWS Lambda"
  default_channel = "#webhook-tests"
}

resource "aws_sns_topic" "test_topic" {
  name = "topic-name"
}

resource "aws_lambda_permission" "allow_lambda_sns_to_slack" {
  statement_id = "AllowSNSToSlackExecutionFromSNS"
  action = "lambda:invokeFunction"
  function_name = "${module.sns_to_slack.lambda_function_arn}"
  principal = "sns.amazonaws.com"
  source_arn = "${aws_sns_topic.test_topic.arn}"
}

resource "aws_sns_topic_subscription" "lambda_sns_to_slack" {
  topic_arn = "${aws_sns_topic.test_topic.arn}"
  protocol = "lambda"
  endpoint = "${module.sns_to_slack.lambda_function_arn}"
}
```

### Configurable variables

|       **Variable**       |                          **Description**                          | **Required** | **Default**      |
|:------------------------:|:-----------------------------------------------------------------:|--------------|------------------|
| **slack_webhook_url**    | Slack incoming webhook URL without protocol name.                 | yes          |                  |
| **slack_channel_map**    | Topic-to-channel mapping string in JSON.                          | yes          |                  |
| **lambda_function_name** | AWS Lambda function name for the Slack notifier                   | no           | `"sns-to-slack"` |
| **default_username**     | Default username for notifications used if no matching one found. | no           |  `"AWS Lambda"`  |
| **default_channel**      | Default channel used if no matching channel found.                | no           | `#webhook-tests` |

### Output variables

| **Variable**            | **Description**                   |
|-------------------------|-----------------------------------|
| **lambda_function_arn** | AWS Lambda notifier function ARN. |

## Examples

### minimal

The minimal example is located at [examples/minimal](/examples/minimal).
It builds no extra AWS resources except a CloudWatch alarm for AWS Lambda's duration metric.

#### Building steps

1. Move to the [examples/minimal](/examples/minimal) directory.

    ```bash
    $ cd examples/minimal
    ```

2. Copy `secrets.tfvars.example` to `secrets.tfvars` and fill in the values.

    ```bash
    $ cp secrets.tfvars.example secrets.tfvars
    $ # Edit secrets.tfvars using your favorite editor.
    ```

    ```hcl
    access_key = "<your AWS Access Key>"
    secret_key = "<your AWS Secret Key>"
    region = "<region>"
    slack_webhook_url="hooks.slack.com/services/XXXXXXXXX/XXXXXXXXX/XXXXXXXXXXXXXXXXXXXXXXXX"
    ```

3. Execute the following commands to build resources using Terraform.

    ```bash
    $ terraform init
    $ terraform plan -var-file=terraform.tfvars -var-file=secrets.tfvars
    $ terraform apply -var-file=terraform.tfvars -var-file=secrets.tfvars
    ```

#### Destroying resources

To destory AWS resources created by the above steps, execute the following command in `examples/minimal` directory.

```bash
$ terraform destroy -var-file=terraform.tfvars -var-file=secrets.tfvars
```

#### Testing

To test notification, use [`awscli cloudwatch set-alarm-state`](http://docs.aws.amazon.com/cli/latest/reference/cloudwatch/set-alarm-state.html) as following.

```bash
$ AWS_ACCESS_KEY_ID=<ACCESS_KEY> \
  AWS_SECRET_ACCESS_KEY=<SECRET> \
  AWS_DEFAULT_REGION=<REGION> \
    aws cloudwatch set-alarm-state \
      --alarm-name lambda-duration \
      --state-value ALARM \
      --state-reason xyzzy
```

## Development

The main AWS Lambda function code is located in [sns-to-slack/](/sns-to-slack) directory.
To prepare development, you need to create [virtualenv](https://virtualenv.pypa.io/en/stable/) for this project and install required pip packages as following.

```bash
$ virtualenv sns-to-slack/virtualenv
$ source sns-to-slack/virtualenv/bin/activate
$ pip install -r sns-to-slack/requirements.txt
```

You need to create [module/lambda/sns-to-slack.zip](/module/lambda/sns-to-slack.zip) to update the code as following.

```bash
$ source sns-to-slack/virtualenv/bin/activate # if you haven't yet
$ ./build-function.sh
```

### Testing

To test the function locally, just run [lambda_function.py](/sns-to-slack/lambda_function.py) with some environment variables.

```bash
$ WEBHOOK_URL="hooks.slack.com/services/XXXXXXXXX/XXXXXXXXX/XXXXXXXXXXXXXXXXXXXXXXXX" \
  CHANNEL_MAP=`echo '{ "production-notices": "#webhook-tests" }' | base64` \
  python sns-to-slack/lambda_function.py
```

## License

Copyright © 2017 Naoto Yokoyama

Distributed under the Apache license version 2.0. See the [LICENSE](./LICENSE) file for full details.
