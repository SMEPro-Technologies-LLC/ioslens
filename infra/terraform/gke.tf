# iOSLENS — GKE Cluster

resource "google_container_cluster" "ioslens" {
  provider = google-beta
  name     = "ioslens-${var.environment}"
  location = var.region
  project  = var.project_id

  # Remove the default node pool after creation
  remove_default_node_pool = true
  initial_node_count       = 1

  network    = google_compute_network.ioslens.name
  subnetwork = google_compute_subnetwork.ioslens_primary.name

  ip_allocation_policy {
    cluster_secondary_range_name  = "pods"
    services_secondary_range_name = "services"
  }

  private_cluster_config {
    enable_private_nodes    = true
    enable_private_endpoint = false
    master_ipv4_cidr_block  = "172.16.0.0/28"
  }

  workload_identity_config {
    workload_pool = "${var.project_id}.svc.id.goog"
  }

  release_channel {
    channel = "STABLE"
  }

  addons_config {
    http_load_balancing {
      disabled = false
    }
    horizontal_pod_autoscaling {
      disabled = false
    }
  }

  depends_on = [google_project_service.required_apis]
}

resource "google_container_node_pool" "ioslens_nodes" {
  name       = "ioslens-nodes-${var.environment}"
  location   = var.region
  cluster    = google_container_cluster.ioslens.name
  node_count = var.min_node_count

  autoscaling {
    min_node_count = var.min_node_count
    max_node_count = var.max_node_count
  }

  node_config {
    preemptible  = var.environment != "production"
    machine_type = var.node_machine_type

    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform",
    ]

    workload_metadata_config {
      mode = "GKE_METADATA"
    }

    labels = {
      environment = var.environment
      app         = "ioslens"
    }
  }

  management {
    auto_repair  = true
    auto_upgrade = true
  }
}

output "gke_endpoint" {
  value     = google_container_cluster.ioslens.endpoint
  sensitive = true
}

output "gke_ca_certificate" {
  value     = google_container_cluster.ioslens.master_auth[0].cluster_ca_certificate
  sensitive = true
}
