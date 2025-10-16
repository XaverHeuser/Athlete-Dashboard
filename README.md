# Athlete-Dashboard

## Project Goal & Motivation

This project aims to create a personal, extensible, and self-hosted dashboard for athletic activities. By pulling data from APIs like Strava and Garmin, it provides full ownership of your training history and enables custom data analysis and visualizations that go beyond the capabilities of the original platforms.
It also serves as a practical learning project for building a modern ELT data pipeline using Google Cloud Platform (GCP) and Python — taking advantage of BigQuery for scalable transformations and analytics

## Project Status

Status: 🚧 In Development 🚧

This project is currently in the architectural and initial development phase.
The core workflow has been designed, but implementation of several components is still ongoing.

## Key Features (Planned)

- Automated Data Sync: Automatically fetches new activities from the Strava API on a given schedule.
- Historical Archive: Securely stores your entire activity history in a personal BigQuery data warehouse.
- Interactive Dashboard: A web-based frontend built with Streamlit to visualize trends, summaries, and individual activities.
- Custom Analytics: Calculates and tracks custom metrics like Training Stress Score (TSS), weekly/monthly totals, and personal records.
- Multi-Source Ready: Designed to be easily extended to support other data sources like Garmin Connect in the future.

## Technology Stack

| Component            | Technology                     | Description                                     |
|----------------------|--------------------------------|-------------------------------------------------|
| Data Source          | Strava API                     | Source of raw activity data                     |
| Cloud Provider       | Google Cloud Platform          | End-to-end hosting environment                  |
| Data Storage         | BigQuery                       | Central data warehouse (Bronze → Silver → Gold) |
| ELT & Wrangling      | Python 3.9+ on Cloud Run       | Extraction and loading                          |
| Transformation Layer | BigQuery SQL + dbt / Dataform  | Transformations executed directly in BigQuery   |
| Scheduling           | Google Cloud Scheduler         | Triggers Cloud Run jobs                         |
| Frontend             | Streamlit                      | Visualizes data via interactive dashboards      |


## Roadmap

- [ ] Phase 1: Core ELT Pipeline
    - [ ] Implement Strava API authentication and data fetching.
    - [ ] Set up BigQuery datasets: raw, silver, and gold
    - [ ] Implement transformation logic in dbt/Dataform
    - [ ] Deploy extraction and load to Cloud Run; schedule via Cloud Scheduler.

- [ ] Phase 2: Dashboard V1
    - [ ] Develop a basic Streamlit dashboard to show key stats (mileage, time).
    - [ ] Add filters for date ranges and activity types.

- [ ] Phase 3: Enhancements
    - [ ] Add support for Garmin API.
    - [ ] Implement more advanced metrics (TSS, Fitness/Fatigue).
    - [ ] Experiment with PostgreSQL as an alternative data store.
    - [ ] Experiment with other Transformation tools.

## Getting Started

TBD

## Project Structure

TBD

## Workflow

This project follows a modern ELT (Extract → Load → Transform) architecture instead of the traditional ETL pattern.

- Extract: A scheduled Cloud Run job pulls activity data from the Strava API.
- Load: The raw JSON data is loaded directly into BigQuery (raw.strava_activities).
- Transform: All cleaning, enrichment, and aggregation are done inside BigQuery using SQL-based transformations orchestrated by dbt, Dataform, or BigQuery Scheduled Queries.

This approach leverages BigQuery’s native scalability, eliminates the need for external ETL servers, and keeps the raw data available for future reprocessing.
For a detailed breakdown of the services, triggers, and data flow, please see the [Architecture Document](docs/architecture/architecture.md).

## License

This project is licensed under the MIT License. See the LICENSE file for details.
