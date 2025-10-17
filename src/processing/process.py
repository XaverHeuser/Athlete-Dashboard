"""Processing Function."""


from elt.extractors.strava import StravaExtractor, get_fresh_access_token


def extract_and_load_data() -> None:
    """Test function."""
    
    CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN = load_strava_auth('local')
    
    access_token = get_fresh_access_token(CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN)

    extractor = StravaExtractor(access_token)
    all_activities = extractor.fetch_all_activities()


    
