# Create an Email Notification Channel
resource "google_monitoring_notification_channel" "email_admin" {
  display_name = "Platform Engineering Admin Email"
  type         = "email"
  labels = {
    email_address = "xaver.heuser@gmail.com" # Swap with your target alert email
  }
}

# Alert Policy: Triggered if ANY Cloud Run Job terminates with a Failure code
resource "google_monitoring_alert_policy" "cloud_run_job_failures" {
  display_name = "Alert: Cloud Run Job Failed Execution"
  combiner     = "OR"

  notification_channels = [google_monitoring_notification_channel.email_admin.name]

  conditions {
    display_name = "Cloud Run Job Failure Condition"

    condition_threshold {
      # Filter explicitly tracks execution outcomes across both EL and dbt jobs
      filter          = "resource.type = \"cloud_run_job\" AND metric.type = \"run.googleapis.com/job/completed_execution_count\" AND metric.labels.result = \"failed\""
      duration        = "0s" # Fire immediately upon job exit failure
      comparison      = "COMPARISON_GT"
      threshold_value = 0

      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_COUNT"
      }
    }
  }

  documentation {
    content   = "One of the pipeline Cloud Run jobs ('extract-load-job' or 'dbt-transform-job') has failed. Check Cloud Logging logs for error traceback stacks."
    mime_type = "text/markdown"
  }
}

resource "google_monitoring_alert_policy" "python_pipeline_exceptions" {
  display_name = "Alert: Application Ingestion Exception Messages"
  combiner     = "OR"

  notification_channels = [google_monitoring_notification_channel.email_admin.name]

  conditions {
    display_name = "Log Exception Match Condition"

    condition_matched_log {
      # Scrapes container logs for explicit application panic output
      filter = "resource.type=\"cloud_run_job\" AND textPayload=~\"Load failed|Failed to trigger dbt-job\""
    }
  }
  alert_strategy {
    notification_rate_limit {
      # Period between notifications. Must be at least 300s (5 minutes) for log-based alerts
      period = "300s"
    }
  }

  documentation {
    content   = "The ingestion application explicitly trapped an exception and bypassed downstream dbt processing. Investigate Cloud Run job run records immediately."
    mime_type = "text/markdown"
  }
}