#####
# IAM roles
#

resource "aws_iam_role" "lambda_sns_to_slack" {
  name = "lambda-sns-to-slack"
  assume_role_policy = "${file("${path.module}/policies/lambda-assume-role.json")}"
}

#####
# IAM policies
#

resource "aws_iam_role_policy" "lambda_sns_to_slack" {
  name = "lambda-sns-to-slack-policy"
  role = "${aws_iam_role.lambda_sns_to_slack.id}"
  policy = "${file("${path.module}/policies/lambda-role-policy.json")}"
}
