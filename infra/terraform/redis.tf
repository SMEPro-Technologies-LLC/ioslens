# iOSLENS — Redis (Memorystore) for token replay store and rate limiting

resource "google_redis_instance" "ioslens" {
  name           = "ioslens-redis-${var.environment}"
  memory_size_gb = var.redis_memory_gb
  region         = var.region
  project        = var.project_id

  redis_version     = "REDIS_7_0"
  authorized_network = google_compute_network.ioslens.id

  tier = var.environment == "production" ? "STANDARD_HA" : "BASIC"

  redis_configs = {
    maxmemory-policy = "allkeys-lru"
  }

  labels = {
    environment = var.environment
    app         = "ioslens"
  }

  depends_on = [google_project_service.required_apis]
}

output "redis_host" {
  value     = google_redis_instance.ioslens.host
  sensitive = false
}

output "redis_port" {
  value = google_redis_instance.ioslens.port
}
