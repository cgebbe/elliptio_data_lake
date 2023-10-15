# required variables

variable "aws_region" {} # eu-central-1
variable "aws_secret_access_key" {}
variable "aws_access_key_id" {}

variable "mongodbatlas_public_key" {}
variable "mongodbatlas_private_key" {}
variable "mongodbatlas_org_id" {}

variable "my_ip_address" {
  description = "required to access mongodb access for testing purposes"
}

# optional variables

variable "mongodbatlas_db_instance_size" {
  description = "M0 is free tier and comes with 512 MB"
  default     = "M0"
}

variable "app_name" {
  default = null
}

# locals

locals {
  app_name = var.app_name == null ? "elliptio" : var.app_name
}

data "aws_caller_identity" "current" {}

locals {
  aws_account_id = data.aws_caller_identity.current.account_id
}
