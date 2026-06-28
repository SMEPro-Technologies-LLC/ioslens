resource "random_password" "postgres" {
  length  = 32
  special = false
}

resource "google_sql_database_instance" "postgres" {
  name             = "ioslens-postgres-${var.environment}"
  database_version = "POSTGRES_15"
  region           = var.region

  settings {
    tier = var.postgres_tier

    ip_configuration {
      ipv4_enabled    = false
      private_network = google_compute_network.vpc.id
    }

    backup_configuration {
      enabled                        = true
      point_in_time_recovery_enabled = true
      start_time                     = "03:00"
      backup_retention_settings {
        retained_backups = 7
      }
    }

    database_flags {
      name  = "max_connections"
      value = "200"
    }

    database_flags {
      name  = "log_statement"
      value = "ddl"
    }

    database_flags {
      name  = "log_min_duration_statement"
      value = "1000"
    }

    insights_config {
      query_insights_enabled  = true
      query_string_length     = 1024
      record_application_tags = true
    }
  }

  deletion_protection = var.environment == "production"

  depends_on = [
    google_project_service.apis["sqladmin.googleapis.com"],
    google_service_networking_connection.private_vpc_connection,
  ]
}

resource "google_sql_database" "ioslens" {
  name     = var.postgres_db_name
  instance = google_sql_database_instance.postgres.name
}

resource "google_sql_user" "app_user" {
  name     = "ioslens_app"
  instance = google_sql_database_instance.postgres.name
  password = random_password.postgres.result
}

resource "google_secret_manager_secret" "postgres_password" {
  secret_id = "ioslens-postgres-password-${var.environment}"
  replication {
    auto {}
  }
  depends_on = [google_project_service.apis["secretmanager.googleapis.com"]]
}

resource "google_secret_manager_secret_version" "postgres_password" {
  secret      = google_secret_manager_secret.postgres_password.id
  secret_data = random_password.postgres.result
}
