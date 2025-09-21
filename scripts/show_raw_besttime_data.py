"""
Show RAW BestTime API data - detailed analysis breakdown
"""

import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

def show_raw_besttime_data():
    """Show detailed raw data from BestTime API"""

    private_key = os.getenv("BESTTIME_API_KEY_PRIVATE")

    # The venues we found that work
    venues = [
        {"name": "Burger King", "address": "Hat Yai, Songkhla, Thailand"},
        {"name": "Tesco Lotus", "address": "Hat Yai, Songkhla, Thailand"}
    ]

    print("RAW BESTTIME API DATA ANALYSIS")
    print("=" * 60)

    for venue in venues:
        print(f"\n{'='*60}")
        print(f"VENUE: {venue['name']}")
        print(f"ADDRESS: {venue['address']}")
        print(f"{'='*60}")

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

            if response.status_code == 200:
                data = response.json()

                # Show venue info
                venue_info = data.get('venue_info', {})
                print(f"\nVENUE INFO:")
                print(f"  Venue ID: {venue_info.get('venue_id', 'Unknown')}")
                print(f"  Venue Name: {venue_info.get('venue_name', 'Unknown')}")
                print(f"  Address: {venue_info.get('venue_address', 'Unknown')}")

                # Show analysis structure
                analysis = data.get('analysis', [])
                print(f"\nANALYSIS STRUCTURE:")
                print(f"  Total days: {len(analysis)}")

                if analysis:
                    # Show each day
                    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

                    for day_index, day_data in enumerate(analysis):
                        if day_index < len(days):
                            day_name = days[day_index]
                            print(f"\n  {day_name.upper()} (Day {day_index}):")
                            print(f"    Day info: {day_data.get('day_info', {})}")

                            # Show hour by hour data
                            hour_analysis = day_data.get('hour_analysis', [])
                            print(f"    Hour analysis ({len(hour_analysis)} hours):")

                            for hour_data in hour_analysis:
                                hour = hour_data.get('hour', 0)
                                intensity = hour_data.get('intensity_nr', 0)
                                intensity_txt = hour_data.get('intensity_txt', 'Unknown')

                                # Show hours with meaningful activity
                                if intensity > 0:
                                    print(f"      {hour:02d}:00 - Intensity: {intensity} ({intensity_txt})")

                    # Show my analysis logic
                    print(f"\n  MY ANALYSIS LOGIC:")
                    print(f"    Looking for hours with intensity >= 40")

                    # Analyze Monday (weekday)
                    if len(analysis) > 0:
                        monday_data = analysis[0]
                        monday_peaks = []
                        if 'hour_analysis' in monday_data:
                            for hour in monday_data['hour_analysis']:
                                intensity = hour.get('intensity_nr', 0)
                                if intensity >= 40:
                                    monday_peaks.append(f"{hour.get('hour', 0):02d}:00 (intensity: {intensity})")

                        print(f"    Monday peaks (>=40): {monday_peaks}")

                    # Analyze Saturday (weekend)
                    if len(analysis) > 5:
                        saturday_data = analysis[5]
                        saturday_peaks = []
                        if 'hour_analysis' in saturday_data:
                            for hour in saturday_data['hour_analysis']:
                                intensity = hour.get('intensity_nr', 0)
                                if intensity >= 40:
                                    saturday_peaks.append(f"{hour.get('hour', 0):02d}:00 (intensity: {intensity})")

                        print(f"    Saturday peaks (>=40): {saturday_peaks}")

                # Show raw JSON structure (truncated)
                print(f"\nRAW JSON STRUCTURE (first 500 chars):")
                json_str = json.dumps(data, indent=2)
                print(json_str[:500] + "..." if len(json_str) > 500 else json_str)

            else:
                print(f"ERROR: Status {response.status_code}")
                print(f"Response: {response.text}")

        except Exception as e:
            print(f"Error: {e}")

    print(f"\n" + "=" * 60)
    print("RAW DATA ANALYSIS COMPLETE")

if __name__ == "__main__":
    show_raw_besttime_data()