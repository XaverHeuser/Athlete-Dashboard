import os

from google.cloud import bigquery
import streamlit as st
from utilities.auth import logout_button, require_login
import vertexai
from vertexai.generative_models import (
    FunctionDeclaration,
    GenerationResponse,
    GenerativeModel,
    Part,
    Tool,
)


# --------------
# Config
# --------------
_GCP_PROJECT_ID = os.getenv('GCP_PROJECT_ID')
_BQ_DATASET_MARTS = os.getenv('BIGQUERY_DATASET_MARTS')
LOCATION = 'us-central1'
TABLE_ID = 'fct_activities'

vertexai.init(project=_GCP_PROJECT_ID, location=LOCATION)
bq_client = bigquery.Client(project=_GCP_PROJECT_ID)
job_config = bigquery.QueryJobConfig(
    maximum_bytes_billed=10**9
)  # Limit to 1GB for safety


# -------------------
# Helper Functions
# -------------------
def get_clean_text(res: GenerationResponse) -> str:
    try:
        if not res.candidates:
            return ''
        # Wir sammeln nur Parts ein, die wirklich Text enthalten
        parts = res.candidates[0].content.parts
        text_parts = [p.text for p in parts if hasattr(p, 'text') and p.text]
        return ' '.join(text_parts).strip()
    except Exception:
        return ''


# ------------------------------
# Safety Check for SQL Queries
# ------------------------------
def is_safe_sql(sql_query: str) -> bool:
    # List of forbidden SQL commands that could modify data or access sensitive information
    forbidden_words = [
        'DROP',
        'DELETE',
        'TRUNCATE',
        'ALTER',
        'UPDATE',
        'INSERT',
        'GRANT',
    ]

    upper_query = sql_query.upper()
    for word in forbidden_words:
        if word in upper_query:
            return False
    return True


# -------------------
# Define the Tool
# -------------------
# Tell Gemini how to use BigQuery
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


# ------------------------------
# Model Initialization
# ------------------------------
generation_config = {
    'temperature': 0.3,  # Less creative, more focused on accurate analysis
    'max_output_tokens': 4000,  # Protects your budget from overly long responses
    'top_p': 0.8,  # Diversity of word choice
    'top_k': 40,  # Limits the number of tokens considered at each step, improving focus
}

# Running tool wraps the function declaration and allows Gemini to call it during the conversation when needed
running_tool = Tool(function_declarations=[sql_declaration])

# Define your schema as a string to keep the code clean
SCHEMA_DESCRIPTION = f"""
The table `{_GCP_PROJECT_ID}.{_BQ_DATASET_MARTS}.{TABLE_ID}` contains triathlon and fitness activity data with the following columns:

- activity_id (INTEGER): Unique identifier for the activity.
- activity_name (STRING): Title given to the workout.
- discipline (STRING): The type of sport (e.g., Run, Bike, Swim, WeightTraining).
- start_date_local (TIMESTAMP): Full start time in local timezone.
- activity_date_local (DATE): The date of the activity (Use this for daily/monthly grouping).
- activity_year/activity_month/activity_weekday/activity_hour_local (INTEGER): Time components for easier filtering.
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
    'gemini-2.5-flash',
    tools=[running_tool],
    generation_config=generation_config,
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

# Initialize the chat session in Streamlit's state if it doesn't exist
if 'chat' not in st.session_state:
    # Disable response_validation to handle reasoning/thought parts or safety blocks gracefully
    st.session_state.chat = model.start_chat(response_validation=False)

# Render the chat input widget
prompt = st.chat_input('Ask about your activities...')

if prompt:
    # Display the user's question in the chat UI
    st.chat_message('user').markdown(prompt)

    # Send the initial user prompt to the Gemini model
    response = st.session_state.chat.send_message(prompt)

    # Limit the loop to 5 steps to prevent infinite recursion/API costs
    max_iterations = 5
    iterations = 0

    while iterations < max_iterations:
        iterations += 1

        # Extract only the actual prose text from the model's response parts, ignoring any function call metadata or reasoning steps
        clean_text = get_clean_text(response)
        if clean_text:
            with st.chat_message('assistant'):
                st.markdown(clean_text)

        # HANDLE SQL GENERATION & EXECUTION
        function_responses = []

        # Check if the model wants to call a function (i.e., generate SQL)
        if response.candidates and response.candidates[0].content.parts:
            # Open an assistant message container for the technical steps
            with st.chat_message('assistant'):
                for part in response.candidates[0].content.parts:
                    if part.function_call:
                        func_name = part.function_call.name
                        sql = part.function_call.args['query']

                        # Use Streamlit's status widget to show progress for data analysis
                        with st.status(
                            f'Analysis Step {iterations}...', expanded=True
                        ) as status:
                            st.markdown('**Executing SQL:**')
                            st.code(sql, language='sql')

                            # Verify the SQL query against the blacklist (DROP, DELETE, etc.)
                            if is_safe_sql(sql):
                                try:
                                    # Execute the query in BigQuery and convert to a Pandas DataFrame
                                    data = bq_client.query(
                                        sql, job_config=job_config
                                    ).to_dataframe()

                                    st.write('Result Dataframe:')
                                    st.dataframe(data)

                                    # Convert data to string for the AI to read; handle empty results
                                    content = (
                                        data.to_string()
                                        if not data.empty
                                        else 'No data found.'
                                    )
                                    status.update(
                                        label='Query successful', state='complete'
                                    )
                                except Exception as e:
                                    st.error(f'Error: {e}')
                                    content = f'Error: {e}'
                                    status.update(
                                        label='Query failed', state='error'
                                    )
                            else:
                                st.error('Blocked for safety.')
                                content = 'Error: SQL blocked.'

                        # Collect the data to send back to the AI in the next turn
                        function_responses.append(
                            Part.from_function_response(
                                name=func_name, response={'content': content}
                            )
                        )

        # If Gemini generated function calls, send the data back to let it interpret the results
        if function_responses:
            # Overwrite the 'response' variable to enter the next loop iteration
            response = st.session_state.chat.send_message(function_responses)
        else:
            # If no function calls were found, the AI is done
            break
