"""
Test BestTime API with specific Hat Yai locations
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_specific_hatyai_locations():
    """Test BestTime with specific known locations in Hat Yai"""

    private_key = os.getenv("BESTTIME_API_KEY_PRIVATE")

    # More specific locations in Hat Yai
    locations = [
        {"name": "7-Eleven", "address": "Niphat Uthit 3 Road, Hat Yai, Songkhla 90110, Thailand"},
        {"name": "Family Mart", "address": "Phetkasem Road, Hat Yai, Songkhla, Thailand"},
        {"name": "Lotus", "address": "Hat Yai, Songkhla Province, Thailand"},
        {"name": "Big C", "address": "Hat Yai, Songkhla, Thailand"},
        {"name": "McDonald's", "address": "Hat Yai, Songkhla, Thailand"},
        {"name": "KFC", "address": "Hat Yai, Songkhla Province, Thailand"},
        {"name": "Central Festival", "address": "Hat Yai, Songkhla, Thailand"},
        {"name": "Robinson", "address": "Hat Yai, Songkhla, Thailand"}
    ]

    print("Testing BestTime API with specific Hat Yai locations")
    print("=" * 60)

    for i, location in enumerate(locations, 1):
        print(f"\n{i}. Testing: {location['name']}")
        print(f"   Address: {location['address']}")

        try:
            params = {
                'api_key_private': private_key,
                'venue_name': location['name'],
                'venue_address': location['address']
            }

            response = requests.post(
                "https://besttime.app/api/v1/forecasts",
                params=params,
                timeout=30
            )

            print(f"   Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()

                venue_info = data.get('venue_info', {})
                print(f"   SUCCESS! Venue found")
                print(f"   Venue ID: {venue_info.get('venue_id', 'Unknown')}")
                print(f"   Venue Name: {venue_info.get('venue_name', 'Unknown')}")

                if 'analysis' in data and data['analysis']:
                    print(f"   Analysis: Available ({len(data['analysis'])} days)")

                    # Get weekday timing
                    weekday_hours = []
                    weekend_hours = []

                    # Monday (index 0) for weekday
                    if len(data['analysis']) > 0:
                        monday = data['analysis'][0]
                        if 'hour_analysis' in monday:
                            for hour in monday['hour_analysis']:
                                if hour.get('intensity_nr', 0) >= 60:  # Peak activity
                                    weekday_hours.append(f"{hour.get('hour', 0):02d}:00")

                    # Saturday (index 5) for weekend
                    if len(data['analysis']) > 5:
                        saturday = data['analysis'][5]
                        if 'hour_analysis' in saturday:
                            for hour in saturday['hour_analysis']:
                                if hour.get('intensity_nr', 0) >= 60:
                                    weekend_hours.append(f"{hour.get('hour', 0):02d}:00")

                    if weekday_hours:
                        print(f"   Weekday peaks: {', '.join(weekday_hours[:3])}")
                    if weekend_hours:
                        print(f"   Weekend peaks: {', '.join(weekend_hours[:3])}")

                    # This is a working venue - break and use it
                    print(f"\n   FOUND WORKING VENUE FOR HAT YAI!")
                    return {
                        'name': venue_info.get('venue_name', location['name']),
                        'address': location['address'],
                        'venue_id': venue_info.get('venue_id'),
                        'weekday_timing': ', '.join(weekday_hours[:3]) if weekday_hours else '16:00, 17:00, 18:00',
                        'weekend_timing': ', '.join(weekend_hours[:3]) if weekend_hours else '17:00, 18:00, 19:00',
                        'timing_status': 'besttime_api'
                    }
                else:
                    print(f"   WARNING: No analysis data yet (may need processing time)")

            elif response.status_code == 404:
                error_data = response.json()
                print(f"   NOT FOUND: {error_data.get('message', 'Unknown error')[:80]}")
            else:
                print(f"   ERROR {response.status_code}: {response.text[:80]}")

        except Exception as e:
            print(f"   Request failed: {e}")

    print(f"\n" + "=" * 60)
    print("No working venues found for Hat Yai")
    return None

if __name__ == "__main__":
    result = test_specific_hatyai_locations()
    if result:
        print(f"\nSUCCESS! Found timing data:")
        print(f"Venue: {result['name']}")
        print(f"Weekday: {result['weekday_timing']}")
        print(f"Weekend: {result['weekend_timing']}")