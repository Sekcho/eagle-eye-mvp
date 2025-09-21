"""
Find venues that actually exist in BestTime database for Hat Yai area
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

def find_real_besttime_venues():
    """Find actual venues with BestTime data in Hat Yai area"""

    private_key = os.getenv("BESTTIME_API_KEY_PRIVATE")

    # Try different venue types that might be in BestTime database
    test_venues = [
        # Restaurants (more likely to be in BestTime)
        {"name": "McDonald's", "address": "Hat Yai, Songkhla, Thailand"},
        {"name": "KFC", "address": "Hat Yai, Songkhla, Thailand"},
        {"name": "Pizza Hut", "address": "Hat Yai, Songkhla, Thailand"},
        {"name": "Starbucks", "address": "Hat Yai, Songkhla, Thailand"},
        {"name": "Burger King", "address": "Hat Yai, Songkhla, Thailand"},

        # Banks
        {"name": "Kasikorn Bank", "address": "Hat Yai, Songkhla, Thailand"},
        {"name": "Bangkok Bank", "address": "Hat Yai, Songkhla, Thailand"},
        {"name": "SCB", "address": "Hat Yai, Songkhla, Thailand"},

        # Gas stations
        {"name": "PTT", "address": "Hat Yai, Songkhla, Thailand"},
        {"name": "Shell", "address": "Hat Yai, Songkhla, Thailand"},
        {"name": "Esso", "address": "Hat Yai, Songkhla, Thailand"},

        # Common locations
        {"name": "7-Eleven", "address": "Hat Yai, Songkhla, Thailand"},
        {"name": "Tesco Lotus", "address": "Hat Yai, Songkhla, Thailand"},
        {"name": "Big C", "address": "Hat Yai, Songkhla, Thailand"},

        # Try with more specific addresses
        {"name": "McDonald's", "address": "Niphat Uthit Road, Hat Yai, Songkhla"},
        {"name": "KFC", "address": "Phetkasem Road, Hat Yai, Songkhla"},
        {"name": "7-Eleven", "address": "Thamnoonvithi Road, Hat Yai, Songkhla"},

        # Try major landmarks
        {"name": "Hat Yai Railway Station", "address": "Hat Yai, Songkhla, Thailand"},
        {"name": "Prince of Songkla University", "address": "Hat Yai, Songkhla, Thailand"},
        {"name": "Hat Yai Hospital", "address": "Hat Yai, Songkhla, Thailand"},
    ]

    print("Searching for REAL venues with BestTime data in Hat Yai")
    print("=" * 60)

    successful_venues = []

    for i, venue in enumerate(test_venues, 1):
        print(f"\n{i:2d}. Testing: {venue['name']}")
        print(f"    Address: {venue['address']}")

        try:
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

            print(f"    Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                venue_info = data.get('venue_info', {})
                venue_name = venue_info.get('venue_name', 'Unknown')

                print(f"    SUCCESS! Found: {venue_name}")
                print(f"    Venue ID: {venue_info.get('venue_id', 'Unknown')}")

                if 'analysis' in data and data['analysis']:
                    print(f"    Analysis: Available ({len(data['analysis'])} days)")

                    # Extract timing data
                    weekday_peaks = []
                    weekend_peaks = []

                    # Monday (weekday)
                    if len(data['analysis']) > 0:
                        monday = data['analysis'][0]
                        if 'hour_analysis' in monday:
                            for hour in monday['hour_analysis']:
                                if hour.get('intensity_nr', 0) >= 40:  # Lower threshold
                                    weekday_peaks.append(f"{hour.get('hour', 0):02d}:00")

                    # Saturday (weekend)
                    if len(data['analysis']) > 5:
                        saturday = data['analysis'][5]
                        if 'hour_analysis' in saturday:
                            for hour in saturday['hour_analysis']:
                                if hour.get('intensity_nr', 0) >= 40:
                                    weekend_peaks.append(f"{hour.get('hour', 0):02d}:00")

                    venue_data = {
                        'poi_name': venue_name,
                        'poi_address': venue['address'],
                        'venue_id': venue_info.get('venue_id'),
                        'timing_weekday': ', '.join(weekday_peaks[:3]) if weekday_peaks else 'No peak data',
                        'timing_weekend': ', '.join(weekend_peaks[:3]) if weekend_peaks else 'No peak data',
                        'timing_status': 'besttime_api_real',
                        'poi_confidence': 'HIGH'
                    }

                    successful_venues.append(venue_data)

                    print(f"    REAL BESTTIME DATA FOUND!")
                    print(f"    Weekday peaks: {venue_data['timing_weekday']}")
                    print(f"    Weekend peaks: {venue_data['timing_weekend']}")

                else:
                    print(f"    Found venue but no analysis data yet")

            elif response.status_code == 404:
                print(f"    NOT FOUND in BestTime database")
            else:
                print(f"    ERROR {response.status_code}")

        except Exception as e:
            print(f"    Request failed: {e}")

    print(f"\n" + "=" * 60)
    print(f"REAL BESTTIME VENUES FOUND: {len(successful_venues)}")

    if successful_venues:
        print(f"\nVENUES WITH REAL BESTTIME DATA:")
        for i, venue in enumerate(successful_venues, 1):
            print(f"{i}. {venue['poi_name']}")
            print(f"   Weekday: {venue['timing_weekday']}")
            print(f"   Weekend: {venue['timing_weekend']}")
            print(f"   Status: REAL BestTime API data")
            print()

        return successful_venues
    else:
        print("No venues found with BestTime data in Hat Yai")
        return None

if __name__ == "__main__":
    venues = find_real_besttime_venues()
    if venues:
        print(f"READY TO USE REAL BESTTIME DATA FOR HAT YAI REPORTS!")
    else:
        print("Need to find alternative approach for BestTime data")