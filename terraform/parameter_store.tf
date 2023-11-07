resource "aws_ssm_parameter" "main" {
  type  = "String"
  name  = "MONGODB_URI"
  value = mongodbatlas_cluster.main.mongo_uri_with_options
}
