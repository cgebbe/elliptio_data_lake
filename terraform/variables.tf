# # required variables

# variable "aws_region" {} # eu-central-1
# variable "aws_secret_access_key" {}
# variable "aws_access_key_id" {}

# variable "mongodbatlas_public_key" {}
# variable "mongodbatlas_private_key" {}
# variable "mongodbatlas_org_id" {}

# see https://stackoverflow.com/a/68833352/2135504
data "http" "ifconfig_ip" {
  url = "https://ifconfig.me/ip"
}
locals {
  my_ipv6 = data.http.ifconfig_ip.response_body
}

data "http" "icanhazip" {
  url = "https://ipv4.icanhazip.com"
}
locals {
  my_ipv4 = chomp(data.http.icanhazip.response_body)
}

data "aws_caller_identity" "current" {}
locals {
  aws_account_id = data.aws_caller_identity.current.account_id
}

# optional variables
variable "mongodbatlas_db_instance_size" {
  description = "M0 is free tier and comes with 512 MB"
  default     = "M0"
}

variable "app_name" {
  default = null
}
locals {
  app_name = var.app_name == null ? "elliptio" : var.app_name
}

# from dotenv file
# see https://stackoverflow.com/a/76194380/2135504
variable "dot_env_file_path" {
  default = "../.env"
}
locals {
  dot_env_regex = "(?m:^\\s*([^#\\s]\\S*)\\s*=\\s*[\"']?(.*[^\"'\\s])[\"']?\\s*$)"
  dot_env       = { for tuple in regexall(local.dot_env_regex, file(var.dot_env_file_path)) : tuple[0] => sensitive(tuple[1]) }
}
