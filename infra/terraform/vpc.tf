resource "google_compute_network" "vpc" {
  name                    = "ioslens-vpc-${var.environment}"
  auto_create_subnetworks = false
  depends_on              = [google_project_service.apis["compute.googleapis.com"]]
}

resource "google_compute_subnetwork" "private" {
  name          = "ioslens-private-${var.environment}"
  ip_cidr_range = "10.10.0.0/20"
  region        = var.region
  network       = google_compute_network.vpc.id

  secondary_ip_range {
    range_name    = "gke-pods"
    ip_cidr_range = "10.20.0.0/16"
  }

  secondary_ip_range {
    range_name    = "gke-services"
    ip_cidr_range = "10.30.0.0/20"
  }

  private_ip_google_access = true
}

resource "google_compute_global_address" "private_services" {
  name          = "ioslens-private-services-${var.environment}"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16
  network       = google_compute_network.vpc.id
}

resource "google_service_networking_connection" "private_vpc_connection" {
  network                 = google_compute_network.vpc.id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.private_services.name]
  depends_on              = [google_project_service.apis["servicenetworking.googleapis.com"]]
}

resource "google_compute_router" "router" {
  name    = "ioslens-router-${var.environment}"
  region  = var.region
  network = google_compute_network.vpc.id
}

resource "google_compute_router_nat" "nat" {
  name                               = "ioslens-nat-${var.environment}"
  router                             = google_compute_router.router.name
  region                             = var.region
  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"
}
