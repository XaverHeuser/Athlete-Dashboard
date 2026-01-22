"""UI Constants for the Dashboard"""

# COLORS
SPORT_COLORS: dict[str, str] = {
    'Run': '#DA5234',
    'Ride': '#A75ABA',
    'Swim': '#D6837A',
    'InlineSkate': '#1967D2',
    'WeightTraining': '#7C7C7C',
}
DEFAULT_COLOR: str = '#bdbdbd'

MAIN_SPORT_COLORS: dict[str, str] = {
    'Run': '#DA5234',
    'Ride': '#A75ABA',
    'Swim': '#D6837A',
    'Strength': '#7C7C7C',
}

GOOGLE_COLOR_ID_BY_SPORT: dict[str, str] = {
    'Run': '11',  # red
    'Ride': '3',  # purple
    'Swim': '4',  # pink
    'Strength': '8',  # gray
}
HEX_BY_GOOGLE_COLOR_ID: dict[str, str] = {
    '11': '#DA5234',  # Run
    '3': '#A75ABA',  # Ride
    '4': '#D6837A',  # Swim
    '8': '#7C7C7C',  # Strength
}


# List of main sports to highlight in visualizations
MAIN_DISCIPLINES: list[str] = ['Swim', 'Ride', 'Run', 'Strength']

# Order for gear types
GEAR_TYPE_ORDER: list[str] = ['Shoes', 'Bike', 'Other']

# Icons for KPIs
KPI_ICONS: dict[str, str] = {
    'distance': '📏',
    'speed': '⚡',
    'heartrate': '❤️',
    'time': '⏱️',
    'elevation_gain': '⛰️',
}

# Pagination for activities list
PAGE_SIZE: int = 10
