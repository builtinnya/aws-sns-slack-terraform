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
  # Or use the following source if your Terraform version >= 0.12
  # source = "github.com/builtinnya/aws-sns-slack-terraform/module-v0.12"

  slack_webhook_url = "hooks.slack.com/services/XXXXXXXXX/XXXXXXXXX/XXXXXXXXXXXXXXXXXXXXXXXX"
  slack_channel_map = {
    "topic-name" = "#slack-channel"
  }

  # The following variables are optional.
  lambda_function_name = "sns-to-slack"
  default_username = "AWS Lambda"
  default_channel = "#webhook-tests"
  default_emoji = ":information_source:"
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

## Configurable variables

### Inputs

| Name | Description | Type | Default | Required |
|------|-------------|:----:|:-----:|:-----:|
| default\_channel | Default channel used if no matching channel found | string | `#webhook-tests` | no |
| default\_emoji | Default emoji used if no matching emoji found | string | `:information_source:` | no |
| default\_username | Default username for notifications used if no matching one found | string | `AWS Lambda` | no |
| lambda\_function\_name | AWS Lambda function name for the Slack notifier | string | `sns-to-slack` | no |
| lambda\_iam\_policy\_name | IAM policy name for lambda functions | string | `lambda-sns-to-slack-policy` | no |
| lambda\_iam\_role\_name | IAM role name for lambda functions | string | `lambda-sns-to-slack` | no |
| slack\_channel\_map | Topic-to-channel mapping | map | - | yes |
| slack\_webhook\_url | Slack incoming webhook URL without protocol name | string | - | yes |
| username\_prefix | if sepecified the usernames that are looked up will be prefixed by this. Useful in situations where multiple accounts report to a single slack channel. | string | `` | no |

### Outputs

| Name | Description |
|------|-------------|
| lambda\_function\_arn | AWS Lambda notifier function ARN |



## Examples

### minimal

The minimal example is located at [examples/minimal](/examples/minimal).
It builds no extra AWS resources except a CloudWatch alarm for AWS Lambda's duration metric.

>NOTE: for terraform >= 0.12, see [examples/minimal-v0.12](/examples/minimal-v0.12) instead.

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
To prepare development, you need to use [Pipenv](https://docs.pipenv.org/) for this project and install required dependencies as following.

```bash
$ cd sns-to-slack
$ pipenv install
```

You need to create [module/lambda/sns-to-slack.zip](/module/lambda/sns-to-slack.zip) to update the code as following.

```bash
$ ./build-function.sh
```

### Testing

To test the function locally, just run [lambda_function.py](/sns-to-slack/lambda_function.py) with some environment variables.

```bash
$ WEBHOOK_URL="hooks.slack.com/services/XXXXXXXXX/XXXXXXXXX/XXXXXXXXXXXXXXXXXXXXXXXX" \
  CHANNEL_MAP=`echo '{ "production-notices": "#webhook-tests" }' | base64` \
  python sns-to-slack/lambda_function.py
```

## Contributors

See [CONTRIBUTORS.md](./CONTRIBUTORS.md).

## License

Copyright © 2017-present Naoto Yokoyama

Distributed under the Apache license version 2.0. See the [LICENSE](./LICENSE) file for full details.
