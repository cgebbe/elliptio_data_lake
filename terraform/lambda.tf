data "archive_file" "main" {
  type        = "zip"
  source_file = "lambda_func.py"
  output_path = "lambda_func.zip"
}


resource "aws_iam_role" "iam_for_lambda" {
  name = "iam_for_lambda"

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


resource "aws_lambda_function" "main" {
  filename      = data.archive_file.main.output_path
  function_name = "etl-s3-metadata-to-mongodb"
  role          = aws_iam_role.iam_for_lambda.arn
  handler       = "lambda_func.lambda_handler"
  runtime       = "python3.9"
}

resource "aws_lambda_permission" "main" {
  statement_id  = "AllowExecutionFromS3Bucket"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.main.arn
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.main.arn
}

resource "aws_s3_bucket_notification" "main" {
  bucket = aws_s3_bucket.main.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.main.arn
    events              = ["s3:ObjectCreated:*"]
    filter_suffix       = "metadata.yaml"
  }

  depends_on = [aws_lambda_permission.main]

}
