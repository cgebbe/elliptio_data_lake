data "aws_iam_policy_document" "assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "iam_for_lambda" {
  name               = "iam_for_lambda"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json
}


resource "aws_lambda_function" "main" {
  function_name = "etl-s3-metadata-to-mongodb"
  filename      = "lambda_func.py"
  handler       = "lambda_func.lambda_handler"
  runtime       = "python3.11"
  role          = aws_iam_role.iam_for_lambda.arn
}



resource "aws_lambda_permission" "main" {
  statement_id  = "AllowS3Invocation"
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
    # filter_prefix       = "input/"  # Optional: Filter S3 objects by prefix
  }

  filter {
    prefix = ""
    suffix = "metadata.yaml"
  }
}
