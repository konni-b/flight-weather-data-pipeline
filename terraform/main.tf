terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = "flight-weather-pipeline-2026"
  region  = "europe-west3"
}

# The Data Lake (Bucket)
resource "google_storage_bucket" "data-lake" {
  name     = "pippin-flights-data-lake-2026"
  location = "EU"

  storage_class               = "STANDARD"
  uniform_bucket_level_access = true

  public_access_prevention = "enforced"

  versioning {
    enabled = true
  }

  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      age = 90 // days
    }
  }

  force_destroy = true
}

# The Warehouse (BigQuery Dataset)
resource "google_bigquery_dataset" "flights_dataset" {
  dataset_id = "flights_data_all"
  location   = "EU"
}