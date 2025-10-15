# Athlete-Dashboard

## Project Goal & Motivation

This project aims to create a personal, extensible, and self-hosted dashboard for athletic activities. By pulling data from APIs like Strava and Garmin, it provides full ownership of training history and enables custom data analysis and visualizations that go beyond the capabilities of the original platforms. It also serves as a practical learning project for building a modern ETL data pipeline using Google Cloud Platform services and Python.

## Project Status

Status: 🚧 In Development 🚧

This project is currently in the architectural and initial development phase. The core workflow has been designed, but the components listed below are not yet implemented.

## Key Features (Planned)

- Automated Data Sync: Automatically fetches new activities from the Strava API on a daily schedule.
- Historical Archive: Securely stores your entire activity history in a personal BigQuery data warehouse.
- Interactive Dashboard: A web-based front-end built with Streamlit to visualize trends, summaries, and individual activities.
- Custom Analytics: Calculates and tracks custom metrics like Training Stress Score (TSS), weekly/monthly totals, and personal records.
- Multi-Source Ready: Designed to be easily extended to support other data sources like Garmin Connect in the future.

## Technology Stack

- Data Source: Strava API
- Cloud Provider: Google Cloud Platform (GCP)
- Data Storage: BigQuery
- ETL & Wrangling: Python 3.9+ running on Google Cloud Run
- Scheduling: Google Cloud Scheduler
- Frontend/Visualization: Streamlit

## Roadmap

[ ] Phase 1: Core ETL Pipeline
    [ ] Implement Strava API authentication and data fetching.
    [ ] Set up BigQuery tables for raw and processed data.
    [ ] Create basic data transformation script.
    [ ] Deploy ingestion and transformation as a scheduled Cloud Run job.

[ ] Phase 2: Dashboard V1
    [ ] Develop a basic Streamlit dashboard to show key stats (mileage, time).
    [ ] Add filters for date ranges and activity types.

[ ] Phase 3: Enhancements
    [ ] Add support for Garmin API.
    [ ] Implement more advanced metrics (TSS, Fitness/Fatigue).
    [ ] Experiment with PostgreSQL as an alternative data store.

## Getting Started

tbd.

## Project Structure

tbd.

## Workflow

The application operates on an automated ETL (Extract, Transform, Load) pipeline:

- Extract: A scheduled Google Cloud Run job fetches new activities from the Strava API and lands the raw JSON data in a BigQuery table.
- Transform: The raw data is then cleaned, enriched with custom metrics (like TSS), and aggregated into analysis-ready "mart" tables.
- Load: The Streamlit dashboard queries only these pre-processed tables, allowing it to load charts and visualizations almost instantly for a smooth user experience.

For a detailed breakdown of the services, triggers, and data flow, please see the Architecture Document.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
