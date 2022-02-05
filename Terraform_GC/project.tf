data "google_billing_account" "acct" {
  display_name = "My Account"
  open         = true
}

resource "random_id" "id" {
  byte_length = 4
}

resource "google_project" "bigquery_project" {
  name       = "TestProject"
  project_id = "test-project-${random_id.id.hex}"
  billing_account = data.google_billing_account.acct.id
}

resource "google_project_service" "service" {
  for_each = toset([
    "iam.googleapis.com", 
    "cloudresourcemanager.googleapis.com",
    "compute.googleapis.com",
    "bigquery.googleapis.com",
    "storage.googleapis.com"
  ])

  service = each.key
  project = google_project.bigquery_project.project_id
  disable_on_destroy = false
}