
resource "random_id" "storage" {
  byte_length = 4
  prefix      = "datatables_"
}

resource "google_storage_bucket" "datatables_bucket" {
    project = google_project.bigquery_project.project_id
    name          = random_id.storage.hex
    location      = "EU"
    force_destroy = true

    lifecycle_rule {
        condition {
            age = 2
        }
        action {
            type = "Delete"
        }
    }
}

resource "google_storage_bucket_object" "datatables_original_csv" {
  name   = "original/my_table.csv"
  source = "./Data/original/my_table.csv"
  bucket = random_id.storage.hex
  depends_on = [
    google_storage_bucket.datatables_bucket,
  ]
}

resource "google_storage_bucket_object" "datatables_new_csv" {
  name   = "newversion/my_table.csv"
  source = "./Data/newversion/my_table.csv"
  bucket = random_id.storage.hex
  depends_on = [
    google_storage_bucket.datatables_bucket,
  ]
}

resource "google_bigquery_dataset" "default" {
    project = google_project.bigquery_project.project_id
    dataset_id                  = "test"
    friendly_name               = "test"
    description                 = "Testing table"
    location                    = "EU"
    default_table_expiration_ms = 10800000 // 3 hr

    depends_on = [
    google_storage_bucket_object.datatables_original_csv,
    google_storage_bucket_object.datatables_new_csv,
  ]
}

resource "google_bigquery_table" "original_my_table" {
    project = google_project.bigquery_project.project_id
    dataset_id = google_bigquery_dataset.default.dataset_id
    table_id   = "original_my_table"
    deletion_protection = false

    schema = file("./Data/original/my_table_metadata.json")

    external_data_configuration {
        autodetect    = true
        source_format = "CSV"

        csv_options {
            quote = "\""
            skip_leading_rows = 1
        }

        source_uris = [
            "${google_storage_bucket.datatables_bucket.url}/original/my_table.csv",
        ]
    }

    depends_on = [
        google_bigquery_dataset.default,
    ]
}

resource "google_bigquery_table" "newversion_my_table" {
    project = google_project.bigquery_project.project_id
    dataset_id = google_bigquery_dataset.default.dataset_id
    table_id   = "newversion_my_table"
    deletion_protection = false

    schema = file("./Data/newversion/my_table_metadata.json")

    external_data_configuration {
        autodetect    = true
        source_format = "CSV"

        csv_options {
            quote = "\""
            skip_leading_rows = 1
        }

        source_uris = [
            "${google_storage_bucket.datatables_bucket.url}/newversion/my_table.csv",
        ]
    }

    depends_on = [
        google_bigquery_dataset.default,
    ]
}