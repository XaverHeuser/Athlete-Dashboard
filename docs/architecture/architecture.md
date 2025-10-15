# Workflow (DRAFT!)

This workflow is designed as an ETL (Extract, Transform, Load) pipeline. It automates the process of fetching data from a source, processing it into a useful format, storing it efficiently, and finally presenting it in an interactive dashboard.

### 1. Data Ingestion (Scheduled Extraction) (Not Implemented yet)

This is the automated "Extract" phase, which runs on a schedule without any user interaction.

- Trigger: A scheduler service like Google Cloud Scheduler triggers your Python script at a set interval (e.g., every hour or once daily).
- Execution: The trigger invokes a Google Cloud Run job.
- Action:
    - The Python script authenticates with the Strava API using OAuth2 tokens.
    - It requests all new activities that have occurred since the last successful run. This is crucial to avoid re-downloading your entire history every time.
    - The script pulls the raw activity data (e.g., GPS coordinates, heart rate, power, time, distance) and saves it directly into a "raw data" table in BigQuery.

*Why this is smart: This process is completely automated and runs in the background. It ensures your data is consistently kept up-to-date in your database.*

### 2. Data Transformation (Wrangling & Enrichment) (Not Implemented yet)

This is the "Transform" phase, where raw data is turned into valuable information. This can be part of the same Cloud Run job or a subsequent one.

- Trigger: Can be triggered immediately after the ingestion step completes.
- Execution: A Python script runs in Cloud Run.
- Action:
    - The script queries the "raw data" table in BigQuery.
    - It performs all the heavy lifting and calculations:
    - Cleaning: Handles missing data points (e.g., no heart rate data for a run).
    - Enrichment: Calculates new metrics like Training Stress Score (TSS), power zones, heart rate zones, or year-over-year progress.
    - Aggregation: Creates summary tables, for example, weekly/monthly mileage, total elevation gain, or personal bests for different distances (e.g., fastest 5k, 10k).
    - This newly processed, cleaned, and aggregated data is then loaded into new, analysis-ready "mart" tables in BigQuery.

*Why this is smart: Your dashboard won't have to do these calculations on the fly. It will query simple, pre-computed tables, making it incredibly fast.*

### 3. Data Presentation (The Dashboard) (Not Implemented yet)

This is the "Load" (from the user's perspective) and visualization phase, where the user interacts with the application.

- Trigger: A user navigates to your Streamlit dashboard's URL.
- Execution: The Streamlit application, hosted on a service like Streamlit Community Cloud or your own server, starts up.
- Action:
    - When the user loads the page or applies a filter (e.g., "Show me all my runs from last year"), Streamlit executes a query.
    - This query is sent to BigQuery, targeting the clean, pre-processed "mart" tables.
    - BigQuery runs the simple query (e.g., SELECT * FROM monthly_summary WHERE year = 2024) and returns the results in milliseconds.
    - Streamlit uses this data to instantly render interactive charts, maps, and tables for the user.
    
*Why this is smart: The user experiences a fast, snappy dashboard because all the slow, heavy data processing has already been done behind the scenes. The application is only performing quick lookups on analysis-ready data.*
