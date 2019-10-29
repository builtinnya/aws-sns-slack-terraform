#####
# Lambda functions
#

resource "aws_lambda_function" "sns_to_slack" {
  filename         = "${path.module}/lambda/sns-to-slack.zip"
  function_name    = var.lambda_function_name
  role             = aws_iam_role.lambda_sns_to_slack.arn
  handler          = "lambda_function.lambda_handler"
  source_code_hash = filebase64sha256("${path.module}/lambda/sns-to-slack.zip")
  runtime          = "python2.7"

  environment {
    variables = {
      WEBHOOK_URL      = var.slack_webhook_url
      CHANNEL_MAP      = base64encode(jsonencode(var.slack_channel_map))
      DEFAULT_USERNAME = var.default_username
      DEFAULT_CHANNEL  = var.default_channel
      DEFAULT_EMOJI    = var.default_emoji
      USERNAME_PREFIX  = var.username_prefix
    }
  }
}

