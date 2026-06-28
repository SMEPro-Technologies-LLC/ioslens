# iOSLENS — VPC Networking

resource "google_compute_network" "ioslens" {
  name                    = "ioslens-${var.environment}"
  auto_create_subnetworks = false
  project                 = var.project_id
}

resource "google_compute_subnetwork" "ioslens_primary" {
  name          = "ioslens-primary-${var.environment}"
  ip_cidr_range = var.subnet_cidr
  region        = var.region
  network       = google_compute_network.ioslens.id

  secondary_ip_range {
    range_name    = "pods"
    ip_cidr_range = var.pods_cidr
  }

  secondary_ip_range {
    range_name    = "services"
    ip_cidr_range = var.services_cidr
  }

  private_ip_google_access = true
}

resource "google_compute_router" "ioslens" {
  name    = "ioslens-router-${var.environment}"
  region  = var.region
  network = google_compute_network.ioslens.id
}

resource "google_compute_router_nat" "ioslens" {
  name                               = "ioslens-nat-${var.environment}"
  router                             = google_compute_router.ioslens.name
  region                             = var.region
  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"
}

# Firewall rules
resource "google_compute_firewall" "allow_internal" {
  name    = "ioslens-allow-internal-${var.environment}"
  network = google_compute_network.ioslens.name

  allow {
    protocol = "tcp"
  }
  allow {
    protocol = "udp"
  }
  allow {
    protocol = "icmp"
  }

  source_ranges = [var.subnet_cidr, var.pods_cidr, var.services_cidr]
}
