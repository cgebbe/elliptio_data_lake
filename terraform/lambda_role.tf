resource "aws_iam_role" "lambda" {
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow"
    }
  ]
}
EOF
}

# Attach an inline policy to the IAM role to allow access to SSM Parameter Store
resource "aws_iam_policy" "ssm_policy" {
  name        = "SSMParameterAccessPolicy"
  description = "Policy to allow access to SSM Parameter Store"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ssm:GetParameters",
        "ssm:GetParameter",
        "ssm:GetParametersByPath"
      ],
      "Resource": "*"
    }
  ]
}
EOF
}

# Attach an inline policy to the IAM role to allow access to AWS MongoDB Atlas
resource "aws_iam_policy" "mongodb_policy" {
  name        = "MongoDBAtlasAccessPolicy"
  description = "Policy to allow access to AWS MongoDB Atlas"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "mongodb:DescribeDBClusters",
        "mongodb:DescribeDBInstances",
        "mongodb:Connect"
      ],
      "Resource": "*"
    }
  ]
}
EOF
}

# Attach an inline policy to the IAM role to allow writing to CloudWatch Logs
resource "aws_iam_policy" "cloudwatch_logs_policy" {
  name        = "CloudWatchLogsWritePolicy"
  description = "Policy to allow writing logs to CloudWatch Logs"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "*"
    }
  ]
}
EOF
}



# Create an IAM policy that grants S3 access (replace with your policy content)
resource "aws_iam_policy" "s3_access_policy" {
  name        = "S3AccessPolicy"
  description = "Policy to allow access to S3 bucket"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": "*"
    }
  ]
}
EOF
}

# Attach the IAM policy to the IAM role
resource "aws_iam_role_policy_attachment" "s3_access_attachment" {
  policy_arn = aws_iam_policy.s3_access_policy.arn
  role       = aws_iam_role.lambda.name
}

resource "aws_iam_role_policy_attachment" "ssm_attachment" {
  policy_arn = aws_iam_policy.ssm_policy.arn
  role       = aws_iam_role.lambda.name
}
resource "aws_iam_role_policy_attachment" "mongodb_attachment" {
  policy_arn = aws_iam_policy.mongodb_policy.arn
  role       = aws_iam_role.lambda.name
}
resource "aws_iam_role_policy_attachment" "cloudwatch_logs_attachment" {
  policy_arn = aws_iam_policy.cloudwatch_logs_policy.arn
  role       = aws_iam_role.lambda.name
}
