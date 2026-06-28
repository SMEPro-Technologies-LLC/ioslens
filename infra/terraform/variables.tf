variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "us-central1"
}

variable "zone" {
  description = "GCP zone"
  type        = string
  default     = "us-central1-a"
}

variable "environment" {
  description = "Deployment environment (staging | production)"
  type        = string
  default     = "staging"
  validation {
    condition     = contains(["staging", "production"], var.environment)
    error_message = "environment must be staging or production"
  }
}

variable "cluster_name" {
  description = "GKE cluster name"
  type        = string
  default     = "ioslens-cluster"
}

variable "node_count" {
  description = "Number of GKE nodes per zone"
  type        = number
  default     = 2
}

variable "node_machine_type" {
  description = "GCE machine type for GKE nodes"
  type        = string
  default     = "e2-standard-4"
}

variable "postgres_tier" {
  description = "Cloud SQL machine tier"
  type        = string
  default     = "db-g1-small"
}

variable "postgres_db_name" {
  description = "PostgreSQL database name"
  type        = string
  default     = "ioslens"
}

variable "redis_tier" {
  description = "Redis memory tier (BASIC | STANDARD_HA)"
  type        = string
  default     = "STANDARD_HA"
}

variable "redis_memory_gb" {
  description = "Redis memory size in GB"
  type        = number
  default     = 2
}
