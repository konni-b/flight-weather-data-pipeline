terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

variable "project_id" {
  description = "GCP project ID"
  type        = string
  default     = "flight-weather-pipeline-2026"
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "europe-west3"
}

variable "bucket_name" {
  description = "GCS data lake bucket name"
  type        = string
  default     = "pippin-flights-data-lake-2026"
}

# ---------------------------------------------------------------------------
# Data Lake (GCS)
# ---------------------------------------------------------------------------
resource "google_storage_bucket" "data_lake" {
  name     = var.bucket_name
  location = "EU"

  storage_class               = "STANDARD"
  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"
  force_destroy               = true

  versioning {
    enabled = true
  }

  # Keep raw files for a full year — enough to demo the project to anyone
  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      age = 365
    }
  }

  labels = {
    project = "flight-weather-pipeline"
    env     = "dev"
  }
}

# ---------------------------------------------------------------------------
# Data Warehouse (BigQuery) — three datasets matching the ELT layers
# ---------------------------------------------------------------------------

# Raw: unmodified data loaded straight from GCS
resource "google_bigquery_dataset" "raw" {
  dataset_id            = "raw"
  friendly_name         = "Raw"
  description           = "Unmodified source data — flights (BTS) and weather (Meteostat)"
  location              = "EU"
  delete_contents_on_destroy = true

  labels = {
    project = "flight-weather-pipeline"
    layer   = "raw"
  }
}

# Staging: dbt staging models (renamed columns, casts, basic cleaning)
resource "google_bigquery_dataset" "staging" {
  dataset_id            = "staging"
  friendly_name         = "Staging"
  description           = "dbt staging models — typed, renamed, no business logic"
  location              = "EU"
  delete_contents_on_destroy = true

  labels = {
    project = "flight-weather-pipeline"
    layer   = "staging"
  }
}

# Marts: dbt mart models — the analytical layer exposed to dashboards / notebooks
resource "google_bigquery_dataset" "marts" {
  dataset_id            = "marts"
  friendly_name         = "Marts"
  description           = "dbt mart models — facts, dimensions, and analytical aggregates"
  location              = "EU"
  delete_contents_on_destroy = true

  labels = {
    project = "flight-weather-pipeline"
    layer   = "marts"
  }
}
