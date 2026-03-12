import os

from google.cloud import bigquery
import streamlit as st
from utilities.auth import logout_button, require_login
import vertexai
from vertexai.generative_models import FunctionDeclaration, GenerativeModel, Tool


# --------------
# Config
# --------------
_GCP_PROJECT_ID = os.getenv('GCP_PROJECT_ID')
_BQ_DATASET_MARTS = os.getenv('BIGQUERY_DATASET_MARTS')
LOCATION = 'us-central1'
TABLE_ID = 'fct_activities'

vertexai.init(project=_GCP_PROJECT_ID, location=LOCATION)
bq_client = bigquery.Client(project=_GCP_PROJECT_ID)

# -------------------
# Define the Tool
# -------------------
# We tell Gemini how to use our BigQuery
sql_declaration = FunctionDeclaration(
    name='list_activitiy_data',
    description='Get all activity data from BigQuery for performance analysis.',
    parameters={
        'type': 'object',
        'properties': {
            'query': {
                'type': 'string',
                'description': f'The SQL query to run. The table is `{_GCP_PROJECT_ID}.{_BQ_DATASET_MARTS}.{TABLE_ID}`',
            }
        },
        'required': ['query'],
    },
)

running_tool = Tool(function_declarations=[sql_declaration])

# ----------------------------------
# System Instruction for Gemini
# ----------------------------------
# Define your schema as a string to keep the code clean
SCHEMA_DESCRIPTION = f"""
The table `{_GCP_PROJECT_ID}.{_BQ_DATASET_MARTS}.{TABLE_ID}` contains triathlon and fitness activity data with the following columns:

- activity_id (INTEGER): Unique identifier for the activity.
- activity_name (STRING): Title given to the workout.
- discipline (STRING): The type of sport (e.g., Running, Cycling, Swimming).
- start_date_local (TIMESTAMP): Full start time in local timezone.
- activity_date_local (DATE): The date of the activity (Use this for daily/monthly grouping).
- activity_year/month/weekday/hour_local (INTEGER): Time components for easier filtering.
- distance_m (FLOAT): Distance in meters.
- distance_km (FLOAT): Distance in kilometers.
- moving_time_s (INTEGER): Active duration in seconds.
- elapsed_time_s (INTEGER): Total duration in seconds including stops.
- avg_pace_min_per_km (FLOAT): Running pace (lower is faster).
- avg_speed_kph (FLOAT): Average speed in km/h.
- elevation_gain_m (FLOAT): Total climbing in meters.
- avg_heartrate / max_heartrate (FLOAT): Heart rate metrics.
- avg_cadence (FLOAT): Steps per minute (Running) or RPM (Cycling).
- avg_watts / max_watts / weighted_watts (FLOAT): Power metrics for Cycling.
- is_commute / is_trainer (BOOLEAN): Flags for indoor or transport activities.
- has_heartrate (BOOLEAN): Whether HR data is available.
"""

# Gemini System Instruction: We give it the schema and rules for analysis and SQL generation
model = GenerativeModel(
    'gemini-2.0-flash',
    tools=[running_tool],
    system_instruction=[
        'You are an expert triathlon coach and data analyst.',
        f'DATASET CONTEXT:\n{SCHEMA_DESCRIPTION}',
        'CRITICAL ANALYSIS RULES:',
        "1. SEGMENTATION: Never average KPIs (pace, speed, heart rate, watts) across different disciplines. Always use 'GROUP BY discipline' in your SQL.",
        "2. PERFORMANCE LOGIC: Remember that 'Running' performance is measured by 'avg_pace_min_per_km' (lower is better), while 'Cycling' is measured by 'avg_speed_kph' or 'weighted_watts' (higher is better). Swimming time should be printed as minutes per 100m (lower is better).",
        '3. COMPARISON: When comparing weeks, compare like-for-like (e.g., Running vs. Running). If a discipline exists in Week A but not Week B, explicitly mention the lack of data.',
        'SQL GENERATION RULES:',
        "1. BIGQUERY DIALECT: Use Standard SQL. Use 'EXTRACT(DAYOFWEEK FROM ...)' or the provided 'activity_weekday' column.",
        "2. FILTERING: Use 'activity_date_local' for date ranges.",
        'OUTPUT FORMATTING:',
        "1. HUMAN-READABLE TIME: Convert 'moving_time_s' into 'HH:MM:SS' or 'Xh Ym Zs'. Never show raw seconds to the user.",
        '2. HUMAN-READABLE DATE: When naming explicit days, use a format like DD.MM.YYYY (e.g., 01.03.2026).',
        "3. CLARITY: Clearly label the discipline for every metric shown (e.g., 'Running Avg Pace', 'Cycling Total Distance').",
        "4. TONE: Provide actionable coaching advice (e.g., 'Your running intensity was higher this week, but your cycling volume dropped').",
    ],
)

# ------------------
# Streamlit UI
# ------------------
st.set_page_config(page_title='AI Coach', page_icon='🤖', layout='wide')
require_login()
logout_button('sidebar')
st.title('My AI Sports Coach')

# Initialize chat state
if 'chat' not in st.session_state:
    st.session_state.chat = model.start_chat()

# User input
prompt = st.chat_input('Ask about your activities...')

if prompt:
    st.chat_message('user').markdown(prompt)

    # Get response from Gemini
    response = st.session_state.chat.send_message(prompt)

    # Only show the text part of the response if it exists, otherwise skip to function handling
    first_part = response.candidates[0].content.parts[0]
    text_content = getattr(first_part, 'text', None)

    if text_content:
        with st.chat_message('assistant'):
            st.markdown(text_content)

    # Run SQL queries if Gemini has returned any function calls, and show results
    for part in response.candidates[0].content.parts:
        if part.function_call:
            sql = part.function_call.args['query']

            with st.status('Analysing Data...', expanded=True):
                # Show the SQL query being run for transparency
                st.markdown('**Generated SQL Query:**')
                st.code(sql, language='sql')
                try:
                    # Run the query and show results in a dataframe
                    data = bq_client.query(sql).to_dataframe()
                    st.dataframe(data)

                    # Result is sent back to Gemini for interpretation. We expect Gemini to return a text summary based on the data.
                    response = st.session_state.chat.send_message(
                        f'Data result for this query: {data.to_string()}'
                    )
                except Exception as e:
                    st.error(f'SQL Error: {e}')
                    response = st.session_state.chat.send_message(
                        f'The query failed: {e}. Explain the problem.'
                    )

    # Show the final interpretation from Gemini after it has processed the data.
    if response.text:
        with st.chat_message('assistant'):
            final_text_parts = []
            for part in response.candidates[0].content.parts:
                if getattr(part, 'text', None):
                    final_text_parts.append(part.text)

            if final_text_parts:
                st.markdown(' '.join(final_text_parts))
            else:
                # If Gemini only returned a function without any text, show a default message to the user
                st.info('Analysis complete, but no summary text was generated.')
