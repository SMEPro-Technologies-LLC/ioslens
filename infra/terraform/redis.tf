resource "google_redis_instance" "cache" {
  name           = "ioslens-redis-${var.environment}"
  tier           = var.redis_tier
  memory_size_gb = var.redis_memory_gb
  region         = var.region

  authorized_network = google_compute_network.vpc.id
  connect_mode       = "PRIVATE_SERVICE_ACCESS"

  redis_version     = "REDIS_7_0"
  display_name      = "iOSLENS Token Replay Store (${var.environment})"
  reserved_ip_range = "10.40.0.0/29"

  redis_configs = {
    maxmemory-policy = "allkeys-lru"
  }

  depends_on = [
    google_project_service.apis["redis.googleapis.com"],
    google_service_networking_connection.private_vpc_connection,
  ]
}
