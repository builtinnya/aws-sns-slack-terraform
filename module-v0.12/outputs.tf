output "lambda_function_arn" {
  value       = aws_lambda_function.sns_to_slack.arn
  description = "AWS Lambda notifier function ARN"
}

