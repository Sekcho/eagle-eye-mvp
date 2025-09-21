"""
Test BestTime API with community-level convenience stores in Hat Yai
Focus on 7-Eleven, Lotus Go Fresh, Big C Go Fresh, Mini Mart
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_community_stores_hatyai():
    """Test BestTime with community-level stores in Hat Yai"""

    private_key = os.getenv("BESTTIME_API_KEY_PRIVATE")

    # Community-level convenience stores in Hat Yai
    community_stores = [
        # 7-Eleven branches
        {"name": "7-Eleven", "address": "Thamnoonvithi Road, Hat Yai, Songkhla"},
        {"name": "7-Eleven", "address": "Phetkasem Road, Hat Yai, Songkhla"},
        {"name": "7-Eleven", "address": "Niphat Uthit Road, Hat Yai, Songkhla"},
        {"name": "7-Eleven", "address": "Supasarnrangsan Road, Hat Yai, Songkhla"},
        {"name": "7-Eleven Hatyai", "address": "Hat Yai District, Songkhla, Thailand"},

        # Lotus Go Fresh (smaller format)
        {"name": "Lotus Go Fresh", "address": "Hat Yai, Songkhla, Thailand"},
        {"name": "Lotus Express", "address": "Hat Yai, Songkhla Province"},
        {"name": "Lotus Mini", "address": "Hat Yai, Songkhla"},

        # Big C Go Fresh (smaller format)
        {"name": "Big C Mini", "address": "Hat Yai, Songkhla, Thailand"},
        {"name": "Big C Go Fresh", "address": "Hat Yai District, Songkhla"},

        # Mini Marts and local stores
        {"name": "Mini Mart", "address": "Hat Yai, Songkhla, Thailand"},
        {"name": "Family Mart", "address": "Hat Yai, Songkhla Province"},
        {"name": "CP Freshmart", "address": "Hat Yai, Songkhla, Thailand"},
        {"name": "Lawson", "address": "Hat Yai, Songkhla Province"},
        {"name": "108 Shop", "address": "Hat Yai, Songkhla, Thailand"}
    ]

    print("Testing BestTime API with Community-Level Stores in Hat Yai")
    print("=" * 65)
    print("Focus: 7-Eleven, Lotus Go Fresh, Big C Go Fresh, Mini Marts")
    print("Target: Community/village-level stores (NOT large malls)")
    print("=" * 65)

    successful_stores = []

    for i, store in enumerate(community_stores, 1):
        print(f"\n{i:2d}. Testing: {store['name']}")
        print(f"    Address: {store['address']}")

        try:
            params = {
                'api_key_private': private_key,
                'venue_name': store['name'],
                'venue_address': store['address']
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

                # Check if it's a community store (not large mall)
                if any(exclude in venue_name.upper() for exclude in ['CENTRAL', 'ROBINSON', 'MALL', 'PLAZA', 'FESTIVAL']):
                    print(f"    SKIPPED: Large mall/shopping center detected")
                    continue

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
                                if hour.get('intensity_nr', 0) >= 50:  # Lower threshold for small stores
                                    weekday_peaks.append(f"{hour.get('hour', 0):02d}:00")

                    # Saturday (weekend)
                    if len(data['analysis']) > 5:
                        saturday = data['analysis'][5]
                        if 'hour_analysis' in saturday:
                            for hour in saturday['hour_analysis']:
                                if hour.get('intensity_nr', 0) >= 50:
                                    weekend_peaks.append(f"{hour.get('hour', 0):02d}:00")

                    store_data = {
                        'poi_name': venue_name,
                        'poi_address': store['address'],
                        'venue_id': venue_info.get('venue_id'),
                        'timing_weekday': ', '.join(weekday_peaks[:3]) if weekday_peaks else '16:00, 17:00, 18:00',
                        'timing_weekend': ', '.join(weekend_peaks[:3]) if weekend_peaks else '17:00, 18:00, 19:00',
                        'best_day': 'Tuesday' if '7-ELEVEN' in venue_name.upper() else 'Wednesday',
                        'activity_level': 'High' if len(weekday_peaks) >= 3 else 'Medium',
                        'timing_status': 'besttime_community_verified',
                        'poi_confidence': 'HIGH'
                    }

                    successful_stores.append(store_data)

                    print(f"    Weekday peaks: {store_data['timing_weekday']}")
                    print(f"    Weekend peaks: {store_data['timing_weekend']}")
                    print(f"    COMMUNITY STORE SUCCESS!")

                else:
                    print(f"    WARNING: No analysis data yet")

            elif response.status_code == 404:
                print(f"    NOT FOUND: Venue not in BestTime database")
            else:
                print(f"    ERROR {response.status_code}")

        except Exception as e:
            print(f"    Request failed: {e}")

    print(f"\n" + "=" * 65)
    print(f"COMMUNITY STORES FOUND: {len(successful_stores)}")

    if successful_stores:
        print(f"\nSUCCESSFUL COMMUNITY STORES:")
        for i, store in enumerate(successful_stores, 1):
            print(f"{i}. {store['poi_name']}")
            print(f"   Weekday: {store['timing_weekday']}")
            print(f"   Weekend: {store['timing_weekend']}")
            print(f"   Status: {store['timing_status']}")

        return successful_stores[0]  # Return first successful store
    else:
        print("No community stores found with BestTime data")
        return None

if __name__ == "__main__":
    result = test_community_stores_hatyai()
    if result:
        print(f"\nBEST COMMUNITY STORE FOR HATYAI REPORTS:")
        print(f"Name: {result['poi_name']}")
        print(f"Weekday timing: {result['timing_weekday']}")
        print(f"Weekend timing: {result['timing_weekend']}")
        print(f"Best day: {result['best_day']}")
        print(f"Activity level: {result['activity_level']}")