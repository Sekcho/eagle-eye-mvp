"""
Test POI and BestTime API specifically for Hat Yai, Tha Kham area
"""

import os
import sys
import requests
from dotenv import load_dotenv

# Add app directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

load_dotenv()

def test_hatyai_poi_besttime():
    """Test POI search and BestTime API for Hat Yai area"""

    # Hat Yai Tha Kham coordinates
    lat = 7.0167
    lng = 100.4667

    print("Testing POI and BestTime for Hat Yai, Tha Kham")
    print("=" * 50)
    print(f"Location: {lat}, {lng}")

    # Test 1: Google Places API search for convenience stores
    try:
        from datasources.gmaps_client import GoogleMapsClient
        gmaps = GoogleMapsClient()

        print("\n1. Testing Google Places API...")

        # Search for convenience stores
        places = gmaps.search_places_nearby(
            lat=lat,
            lng=lng,
            radius=2000,
            place_type='convenience_store'
        )

        if places:
            print(f"Found {len(places)} convenience stores:")
            for i, place in enumerate(places[:3]):
                print(f"  {i+1}. {place.get('name', 'Unknown')}")
                print(f"     Address: {place.get('vicinity', 'No address')}")
                print(f"     Place ID: {place.get('place_id', 'No ID')}")
        else:
            print("No convenience stores found")

        # Try broader search
        print("\n   Trying broader search...")
        places = gmaps.search_places_nearby(
            lat=lat,
            lng=lng,
            radius=5000,
            place_type='store'
        )

        if places:
            print(f"Found {len(places)} stores in 5km radius:")
            for i, place in enumerate(places[:5]):
                print(f"  {i+1}. {place.get('name', 'Unknown')}")

    except Exception as e:
        print(f"Google Places API error: {e}")

    # Test 2: BestTime API with Hat Yai locations
    print("\n2. Testing BestTime API...")

    test_venues = [
        {"name": "7-Eleven", "address": "Hat Yai, Songkhla, Thailand"},
        {"name": "Family Mart", "address": "Tha Kham, Hat Yai, Songkhla"},
        {"name": "Lotus Express", "address": "Hat Yai District, Songkhla"},
        {"name": "CP Freshmart", "address": "Hat Yai, Thailand"}
    ]

    private_key = os.getenv("BESTTIME_API_KEY_PRIVATE")

    for venue in test_venues:
        try:
            print(f"\n   Testing: {venue['name']} at {venue['address']}")

            params = {
                'api_key_private': private_key,
                'venue_name': venue['name'],
                'venue_address': venue['address']
            }

            response = requests.post(
                "https://besttime.app/api/v1/forecasts",
                params=params,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()

                if 'analysis' in data and data['analysis']:
                    print(f"   SUCCESS! Found timing data")

                    # Extract peak hours
                    analysis = data['analysis']
                    if analysis:
                        # Get Monday data (index 0)
                        monday_data = analysis[0] if len(analysis) > 0 else None
                        if monday_data and 'hour_analysis' in monday_data:
                            hours = monday_data['hour_analysis']
                            peak_hours = []

                            for hour_data in hours:
                                if hour_data.get('intensity_nr', 0) >= 70:  # High activity
                                    peak_hours.append(f"{hour_data.get('hour', 0):02d}:00")

                            if peak_hours:
                                print(f"   Peak hours: {', '.join(peak_hours[:3])}")
                            else:
                                print(f"   Default timing: 16:00, 17:00, 18:00")

                        venue_info = data.get('venue_info', {})
                        print(f"   Venue ID: {venue_info.get('venue_id', 'Unknown')}")
                        break  # Found working venue
                else:
                    print(f"   WARNING: No analysis data available yet")

            else:
                print(f"   ERROR {response.status_code}: {response.text[:100]}")

        except Exception as e:
            print(f"   Request failed: {e}")

    print("\n" + "=" * 50)
    print("Hat Yai POI and BestTime test completed")

if __name__ == "__main__":
    test_hatyai_poi_besttime()