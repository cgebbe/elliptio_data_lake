resource "mongodbatlas_project" "main" {
  org_id = var.mongodbatlas_org_id
  name   = local.app_name

  lifecycle {
    prevent_destroy = true
  }
}


resource "mongodbatlas_project_ip_access_list" "example" {
  project_id = mongodbatlas_project.main.id
  ip_address = var.my_ip_address
  comment    = "My current IP address"
}



resource "mongodbatlas_database_user" "main" {
  project_id         = mongodbatlas_project.main.id
  username           = "dbuser"
  password           = "dbpassword"
  auth_database_name = "admin"

  roles {
    role_name     = "readWriteAnyDatabase"
    database_name = "admin"
  }
}

locals {
  # transform `eu-central-1` to `EU_CENTRAL_1`
  uppercase_aws_region = upper(replace(var.aws_region, "-", "_"))
}

resource "mongodbatlas_cluster" "main" {
  project_id = mongodbatlas_project.main.id
  name       = "main"

  provider_name               = "TENANT"
  backing_provider_name       = "AWS"
  provider_region_name        = local.uppercase_aws_region
  provider_instance_size_name = var.mongodbatlas_db_instance_size
  cluster_type                = "REPLICASET"

  lifecycle {
    prevent_destroy = true
  }
}
