data "archive_file" "main" {
  type        = "zip"
  source_file = "lambda_func.py"
  output_path = "lambda_func.zip"
}

resource "aws_lambda_function" "main" {
  filename      = data.archive_file.main.output_path
  source_code_hash = data.archive_file.main.output_base64sha256
  function_name = "etl-s3-metadata-to-mongodb"
  handler       = "lambda_func.lambda_handler"
  runtime       = "python3.9"
  role          = aws_iam_role.lambda.arn
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
