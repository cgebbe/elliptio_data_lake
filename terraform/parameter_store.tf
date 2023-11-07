resource "aws_ssm_parameter" "main" {
  type  = "String"
  name  = "MONGODB_URI"
  value = local.dot_env["MONGODB_URI"]
}
