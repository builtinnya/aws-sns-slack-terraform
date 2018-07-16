#####
# Lambda functions
#

data "null_data_source" "lambda_archive" {
  inputs {
    filename = "${substr("${path.module}/lambda/sns-to-slack.zip", length(path.cwd) + 1, -1)}"
  }
}

resource "aws_lambda_function" "sns_to_slack" {
  filename         = "${data.null_data_source.lambda_archive.outputs.filename}"
  function_name    = "${var.lambda_function_name}"
  description      = "Sends SNS events to Slack"
  role             = "${aws_iam_role.lambda_sns_to_slack.arn}"
  handler          = "lambda_function.lambda_handler"
  source_code_hash = "${base64sha256(file("${path.module}/lambda/sns-to-slack.zip"))}"
  runtime          = "python2.7"

  environment {
    variables = {
      WEBHOOK_URL      = "${var.slack_webhook_url}"
      CHANNEL_MAP      = "${base64encode(jsonencode(var.slack_channel_map))}"
      DEFAULT_USERNAME = "${var.default_username}"
      DEFAULT_CHANNEL  = "${var.default_channel}"
      DEFAULT_EMOJI    = "${var.default_emoji}"
      LOG_LEVEL        = "${var.log_level}"
    }
  }
}
