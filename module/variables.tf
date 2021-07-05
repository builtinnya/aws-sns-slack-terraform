variable "slack_webhook_url" {
  type        = "string"
  description = "Slack incoming webhook URL (with or without protocol name)"
}

variable "slack_channel_map" {
  type        = "map"
  description = "Topic-to-channel mapping"
}

variable "lambda_function_name" {
  type        = "string"
  default     = "sns-to-slack"
  description = "AWS Lambda function name for the Slack notifier"
}

variable "default_username" {
  type        = "string"
  default     = "AWS Lambda"
  description = "Default username for notifications used if no matching one found"
}

variable "username_prefix" {
  type        = "string"
  default     = ""
  description = "if sepecified the usernames that are looked up will be prefixed by this. Useful in situations where multiple accounts report to a single slack channel."
}

variable "default_channel" {
  type        = "string"
  default     = "#webhook-tests"
  description = "Default channel used if no matching channel found"
}

variable "default_emoji" {
  type        = "string"
  default     = ":information_source:"
  description = "Default emoji used if no matching emoji found"
}

variable "lambda_iam_role_name" {
  type        = "string"
  default     = "lambda-sns-to-slack"
  description = "IAM role name for lambda functions"
}

variable "lambda_iam_policy_name" {
  type        = "string"
  default     = "lambda-sns-to-slack-policy"
  description = "IAM policy name for lambda functions"
}
