terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.16"
    }

    mongodbatlas = {
      source  = "mongodb/mongodbatlas"
      version = "~> 1.9"
    }
  }

  required_version = ">= 1.2.0"
}

provider "aws" {
  region     = local.dot_env["AWS_REGION"]
  access_key = local.dot_env["AWS_ACCESS_KEY_ID"]
  secret_key = local.dot_env["AWS_SECRET_ACCESS_KEY"]
}


provider "mongodbatlas" {
  public_key  = local.dot_env["MONGODBATLAS_PUBLIC_KEY"]
  private_key = local.dot_env["MONGODBATLAS_PRIVATE_KEY"]
}
