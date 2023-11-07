# TODO: Add prefix to name!
# TODO: Make keys secure using KMS
resource "aws_ssm_parameter" "mongo_uri" {
  type  = "String"
  name  = "MONGODB_URI"
  value = mongodbatlas_cluster.main.mongo_uri_with_options
}
resource "aws_ssm_parameter" "mongo_user" {
  type  = "String"
  name  = "MONGODB_USERNAME"
  value = local.dot_env["MONGODB_USERNAME"]
}
resource "aws_ssm_parameter" "mongo_pw" {
  type  = "String"
  name  = "MONGODB_PASSWORD"
  value = local.dot_env["MONGODB_PASSWORD"]
}
