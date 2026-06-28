# iOSLENS — Terraform Outputs

output "postgres_connection_name" {
  description = "Cloud SQL connection name for Cloud SQL Proxy"
  value       = google_sql_database_instance.ioslens.connection_name
}

output "postgres_private_ip" {
  description = "Cloud SQL private IP address"
  value       = google_sql_database_instance.ioslens.private_ip_address
  sensitive   = true
}

output "redis_url" {
  description = "Redis connection URL"
  value       = "redis://${google_redis_instance.ioslens.host}:${google_redis_instance.ioslens.port}/0"
  sensitive   = false
}

output "vpc_name" {
  description = "VPC network name"
  value       = google_compute_network.ioslens.name
}

output "cluster_name" {
  description = "GKE cluster name"
  value       = google_container_cluster.ioslens.name
}

output "postgres_secret_id" {
  description = "Secret Manager secret ID for Postgres password"
  value       = google_secret_manager_secret.postgres_password.secret_id
}
