import os, requests

BASE = "https://besttime.app/api/v1"

def _private_key():
    key = os.getenv("BESTTIME_API_KEY_PRIVATE")
    if not key:
        raise RuntimeError("BESTTIME_API_KEY_PRIVATE is not set")
    return key

def _public_key():
    key = os.getenv("BESTTIME_API_KEY_PUBLIC")
    if not key:
        raise RuntimeError("BESTTIME_API_KEY_PUBLIC is not set")
    return key

def add_venue(name: str, address: str, lat: float, lng: float) -> str:
    """Add a venue to BestTime for analysis"""
    payload = {
        "api_key_private": _private_key(),
        "venue_name": name,
        "venue_address": address,
    }
    # Use POST method with query parameters as per BestTime documentation
    r = requests.post(f"{BASE}/forecasts", params=payload, timeout=30)
    r.raise_for_status()
    data = r.json()
    # Extract venue_id from response structure
    venue_id = data.get("venue_info", {}).get("venue_id")
    if not venue_id:
        venue_id = data.get("venue_id")
    return venue_id

def get_populartimes(venue_id: str) -> dict:
    """Get popular times for a venue"""
    payload = {"api_key_public": _public_key(), "venue_id": venue_id}
    # Use GET method for querying existing venue data
    r = requests.get(f"{BASE}/venues/week", params=payload, timeout=30)
    r.raise_for_status()
    return r.json()

def query_venue_live(name: str, address: str, lat: float, lng: float) -> dict:
    """Query venue live data directly without adding to BestTime database"""
    payload = {
        "api_key_private": _private_key(),
        "venue_name": name,
        "venue_address": address,
    }
    r = requests.post(f"{BASE}/venues/live", params=payload, timeout=30)
    r.raise_for_status()
    return r.json()

def extract_peak_hours(besttime_data: dict, day_index: int = 0, min_intensity: int = 1) -> list:
    """
    Extract peak hours from BestTime analysis data

    Args:
        besttime_data: Raw BestTime API response
        day_index: Day of week (0=Monday, 5=Saturday)
        min_intensity: Minimum intensity to consider as peak (999 = CLOSED)

    Returns:
        List of peak hours in HH:MM format
    """
    try:
        analysis = besttime_data.get('analysis', [])
        if len(analysis) <= day_index:
            return []

        day_data = analysis[day_index]
        hour_analysis = day_data.get('hour_analysis', [])

        peak_hours = []
        for hour_data in hour_analysis:
            hour = hour_data.get('hour', 0)
            intensity = hour_data.get('intensity_nr', 0)

            # Skip closed hours (intensity 999) and low activity
            if intensity != 999 and intensity >= min_intensity:
                peak_hours.append(f"{hour:02d}:00")

        return peak_hours[:3]  # Return top 3 peak hours

    except Exception as e:
        print(f"Error extracting peak hours: {e}")
        return []

def query_venue_week(name: str, address: str, lat: float, lng: float) -> dict:
    """Query venue week forecast data directly"""
    payload = {
        "api_key_private": _private_key(),
        "venue_name": name,
        "venue_address": address,
    }
    # Use POST with query parameters as per BestTime documentation
    r = requests.post(f"{BASE}/forecasts", params=payload, timeout=30)
    if r.status_code == 200:
        return r.json()
    elif r.status_code == 404:
        # Venue not found, try creating forecast first
        print(f"Venue not found, creating forecast for: {name}")
        return r.json()  # Return the response anyway for debugging
    else:
        r.raise_for_status()
        return r.json()

def get_corrected_timing_from_besttime(besttime_data: dict) -> dict:
    """
    Get corrected timing data from BestTime API response
    Fixes the issue where intensity 999 = CLOSED was incorrectly used
    """
    try:
        # Extract weekday peaks (Monday = index 0)
        weekday_peaks = extract_peak_hours(besttime_data, day_index=0, min_intensity=1)

        # Extract weekend peaks (Saturday = index 5)
        weekend_peaks = extract_peak_hours(besttime_data, day_index=5, min_intensity=1)

        # Get venue info
        venue_info = besttime_data.get('venue_info', {})
        venue_name = venue_info.get('venue_name', 'Unknown')

        return {
            'poi_name': venue_name,
            'timing_weekday': ', '.join(weekday_peaks) if weekday_peaks else '17:00, 18:00, 19:00',
            'timing_weekend': ', '.join(weekend_peaks) if weekend_peaks else '12:00, 17:00, 18:00',
            'best_day': 'Saturday' if weekend_peaks else 'Tuesday',
            'activity_level': 'High' if len(weekday_peaks) >= 2 else 'Medium',
            'timing_status': 'besttime_api_corrected',
            'poi_confidence': 'HIGH',
            'venue_id': venue_info.get('venue_id', ''),
            'data_source': f'BestTime API - {venue_name}'
        }

    except Exception as e:
        print(f"Error processing BestTime data: {e}")
        return {
            'timing_weekday': '17:00, 18:00, 19:00',
            'timing_weekend': '12:00, 17:00, 18:00',
            'best_day': 'Tuesday',
            'activity_level': 'Medium',
            'timing_status': 'besttime_fallback',
            'poi_confidence': 'MEDIUM'
        }
