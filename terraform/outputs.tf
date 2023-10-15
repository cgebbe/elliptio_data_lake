output "s3_bucket_name" {
  value = aws_s3_bucket.main.id
}

output "mongodb_uri" {
  value = mongodbatlas_cluster.main.mongo_uri_with_options
}
