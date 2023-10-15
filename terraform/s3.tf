resource "aws_s3_bucket" "main" {
  bucket = "${local.app_name}-${local.aws_account_id}"

  object_lock_enabled = true

  # logging {
  #     target_bucket = aws_s3_bucket.log_bucket_cloudtrail[count.index].id
  #     target_prefix = "log/"
  # }

  lifecycle {
    prevent_destroy = true
  }

}