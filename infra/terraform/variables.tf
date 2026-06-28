# iOSLENS — Terraform Input Variables

variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region for all resources"
  type        = string
  default     = "us-central1"
}

variable "environment" {
  description = "Deployment environment: development, staging, or production"
  type        = string
  validation {
    condition     = contains(["development", "staging", "production"], var.environment)
    error_message = "Environment must be development, staging, or production."
  }
}

variable "subnet_cidr" {
  description = "Primary subnet CIDR"
  type        = string
  default     = "10.0.0.0/24"
}

variable "pods_cidr" {
  description = "GKE pods secondary CIDR"
  type        = string
  default     = "10.1.0.0/16"
}

variable "services_cidr" {
  description = "GKE services secondary CIDR"
  type        = string
  default     = "10.2.0.0/20"
}

variable "min_node_count" {
  description = "Minimum GKE node count"
  type        = number
  default     = 1
}

variable "max_node_count" {
  description = "Maximum GKE node count"
  type        = number
  default     = 5
}

variable "node_machine_type" {
  description = "GKE node machine type"
  type        = string
  default     = "e2-standard-4"
}

variable "postgres_tier" {
  description = "Cloud SQL tier"
  type        = string
  default     = "db-g1-small"
}

variable "postgres_disk_gb" {
  description = "Cloud SQL initial disk size in GB"
  type        = number
  default     = 20
}

variable "redis_memory_gb" {
  description = "Redis Memorystore memory in GB"
  type        = number
  default     = 1
}
