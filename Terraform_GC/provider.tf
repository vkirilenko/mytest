terraform {
  required_version = ">=1.0.9"
  required_providers {
    google = "4.4.0"
  }
}

provider "google" {
  region  = "europe-west3"
}