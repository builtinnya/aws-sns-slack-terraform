#####
# IAM roles
#

resource "aws_iam_role" "lambda_sns_to_slack" {
  name = "lambda-sns-to-slack"
  assume_role_policy = "${file("${path.module}/policies/lambda-assume-role.json")}"
}
