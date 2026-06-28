# iOSLENS — Cloud SQL PostgreSQL

resource "google_sql_database_instance" "ioslens" {
  name             = "ioslens-postgres-${var.environment}"
  database_version = "POSTGRES_16"
  region           = var.region
  project          = var.project_id

  settings {
    tier              = var.postgres_tier
    availability_type = var.environment == "production" ? "REGIONAL" : "ZONAL"
    disk_autoresize   = true
    disk_size         = var.postgres_disk_gb

    backup_configuration {
      enabled                        = true
      start_time                     = "03:00"
      point_in_time_recovery_enabled = true
      transaction_log_retention_days = 7
      backup_retention_settings {
        retained_backups = 30
      }
    }

    ip_configuration {
      ipv4_enabled    = false
      private_network = google_compute_network.ioslens.id
    }

    database_flags {
      name  = "cloudsql.enable_pgaudit"
      value = "on"
    }

    insights_config {
      query_insights_enabled  = true
      query_string_length     = 4096
      record_application_tags = true
      record_client_address   = false
    }
  }

  deletion_protection = var.environment == "production"

  depends_on = [google_project_service.required_apis]
}

resource "google_sql_database" "ioslens" {
  name     = "ioslens"
  instance = google_sql_database_instance.ioslens.name
  project  = var.project_id
}

resource "random_password" "postgres" {
  length  = 32
  special = false
}

resource "google_sql_user" "ioslens_app" {
  name     = "ioslens"
  instance = google_sql_database_instance.ioslens.name
  password = random_password.postgres.result
  project  = var.project_id
}

resource "google_secret_manager_secret" "postgres_password" {
  secret_id = "ioslens-postgres-password-${var.environment}"
  project   = var.project_id

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "postgres_password" {
  secret      = google_secret_manager_secret.postgres_password.id
  secret_data = random_password.postgres.result
}
