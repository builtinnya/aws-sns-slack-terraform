variable "slack_webhook_url" {
  type = "string"
}

variable "slack_channel_map" {
  type = "map"
}

variable "lambda_function_name" {
  type    = "string"
  default = "sns-to-slack"
}

variable "default_username" {
  type    = "string"
  default = "AWS Lambda"
}

variable "default_channel" {
  type    = "string"
  default = "#webhook-tests"
}

variable "default_emoji" {
  type    = "string"
  default = ":information_source:"
}

variable "lambda_iam_role_name" {
  type    = "string"
  default = "lambda-sns-to-slack"
}

variable "lambda_iam_policy_name" {
  type    = "string"
  default = "lambda-sns-to-slack-policy"
}

variable "log_level" {
  type    = "string"
  default = "INFO"
}
