"""
Test BestTime API Integration
Tests real BestTime API calls with actual API keys
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add app directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

import datasources.besttime_client as besttime_client

def test_besttime_api():
    """Test BestTime API with real POI data"""

    print("Testing BestTime API Integration")
    print("=" * 50)

    # Check API keys
    private_key = os.getenv("BESTTIME_API_KEY_PRIVATE")
    public_key = os.getenv("BESTTIME_API_KEY_PUBLIC")

    if not private_key or not public_key:
        print("BestTime API keys not found in environment")
        return False

    print(f"Private key: {private_key[:20]}...")
    print(f"Public key: {public_key[:20]}...")

    # Test venues
    test_venues = [
        {
            "name": "7-Eleven",
            "address": "Hat Yai, Songkhla, Thailand"
        },
        {
            "name": "7-Eleven สาขา ดอนสัก",
            "address": "Don Sak, Surat Thani, Thailand"
        },
        {
            "name": "FamilyMart",
            "address": "Surat Thani, Thailand"
        }
    ]

    for i, venue in enumerate(test_venues, 1):
        print(f"\nTest {i}: {venue['name']}")
        print(f"   Address: {venue['address']}")

        try:
            # Test query_venue_week function
            print("   Querying BestTime API...")
            result = besttime_client.query_venue_week(
                venue["name"],
                venue["address"],
                0, 0  # lat, lng not required for this function
            )

            if result:
                print("   BestTime API response received")

                # Check response structure
                if 'analysis' in result:
                    analysis = result['analysis']
                    print(f"   Analysis data available for {len(analysis)} days")

                    # Show sample data for one day
                    if 'Monday' in analysis:
                        monday_data = analysis['Monday']
                        print(f"   Monday sample: {len(monday_data)} hours of data")

                        # Show peak hours
                        if monday_data:
                            sorted_hours = sorted(monday_data.items(),
                                                key=lambda x: x[1], reverse=True)[:3]
                            peak_hours = [hour for hour, pct in sorted_hours]
                            peak_percentages = [pct for hour, pct in sorted_hours]

                            print(f"   Top 3 busy hours: {peak_hours}")
                            print(f"   Busy percentages: {peak_percentages}")

                    # Extract overall statistics
                    total_data_points = 0
                    total_busyness = 0

                    for day_data in analysis.values():
                        if isinstance(day_data, dict):
                            for hour, pct in day_data.items():
                                try:
                                    total_busyness += pct
                                    total_data_points += 1
                                except:
                                    continue

                    if total_data_points > 0:
                        avg_busyness = total_busyness / total_data_points
                        print(f"   Average busyness: {avg_busyness:.1f}%")

                        if avg_busyness >= 60:
                            activity_level = "High"
                        elif avg_busyness >= 40:
                            activity_level = "Medium"
                        else:
                            activity_level = "Low"

                        print(f"   Activity level: {activity_level}")

                else:
                    print("   No 'analysis' data in response")
                    print(f"   Response keys: {list(result.keys())}")

            else:
                print("   Empty response from BestTime API")

        except Exception as e:
            print(f"   Error: {e}")
            continue

    print(f"\nBestTime API Test Complete")
    return True

if __name__ == "__main__":
    test_besttime_api()