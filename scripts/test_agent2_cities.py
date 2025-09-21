#!/usr/bin/env python3
"""
Test Agent 2 with major cities coordinates to validate improvements
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.datasources.gmaps_client import find_nearest_convenience_store, get_poi_for_village

def test_major_cities():
    """Test Agent 2 with coordinates from major cities"""

    test_locations = [
        {
            "name": "Bangkok Central (Siam)",
            "lat": 13.7455,
            "lng": 100.5387,
            "expected": "Should find many stores"
        },
        {
            "name": "Hat Yai Center",
            "lat": 7.0067,
            "lng": 100.4681,
            "expected": "Should find 7-Eleven"
        },
        {
            "name": "Chiang Mai Old Town",
            "lat": 18.7869,
            "lng": 98.9933,
            "expected": "Should find convenience stores"
        },
        {
            "name": "Phuket Patong",
            "lat": 7.8907,
            "lng": 98.2965,
            "expected": "Tourist area - many stores"
        },
        {
            "name": "Songkhla City Center",
            "lat": 7.1756,
            "lng": 100.6014,
            "expected": "Provincial capital"
        }
    ]

    print("Testing Agent 2 Improvements with Major Cities")
    print("=" * 60)
    print(f"Search radius: 3000m")
    print(f"Keywords: 7-Eleven, เซเว่น, CP Freshmart, Lotus Go Fresh")
    print()

    results = []

    for i, location in enumerate(test_locations, 1):
        print(f"[{i}/{len(test_locations)}] Testing: {location['name']}")
        print(f"  Coordinates: {location['lat']:.4f}, {location['lng']:.4f}")
        print(f"  Expected: {location['expected']}")

        try:
            # Test the improved multi-keyword search
            result = find_nearest_convenience_store(location['lat'], location['lng'])

            if result:
                print(f"  SUCCESS: Found {result['name']}")
                print(f"    Distance: {result.get('distance_km', 'N/A')}km")
                print(f"    Address: {result['address']}")
                print(f"    Search keyword: {result.get('search_keyword', 'N/A')}")

                results.append({
                    'location': location['name'],
                    'success': True,
                    'store': result['name'],
                    'distance': result.get('distance_km', 0),
                    'keyword': result.get('search_keyword', 'N/A')
                })
            else:
                print(f"  NO RESULT: No convenience store found within 3km")
                results.append({
                    'location': location['name'],
                    'success': False,
                    'store': None,
                    'distance': None,
                    'keyword': None
                })

        except Exception as e:
            print(f"  ERROR: {e}")
            results.append({
                'location': location['name'],
                'success': False,
                'store': f"ERROR: {e}",
                'distance': None,
                'keyword': None
            })

        print()

    # Summary
    print("=" * 60)
    print("SUMMARY OF RESULTS")
    print("=" * 60)

    successful = [r for r in results if r['success']]

    print(f"Success rate: {len(successful)}/{len(results)} ({len(successful)/len(results)*100:.1f}%)")
    print()

    if successful:
        print("Successful locations:")
        for result in successful:
            print(f"  {result['location']}: {result['store']} ({result['distance']:.2f}km) [{result['keyword']}]")

    failed = [r for r in results if not r['success']]
    if failed:
        print(f"\nFailed locations ({len(failed)}):")
        for result in failed:
            print(f"  {result['location']}: {result['store'] or 'No store found'}")

    # Test full get_poi_for_village function with one successful location
    if successful:
        print(f"\n{'='*60}")
        print("TESTING get_poi_for_village FUNCTION")
        print("=" * 60)

        test_case = successful[0]
        test_location = test_locations[0]  # Use first location

        poi_result = get_poi_for_village(
            test_case['location'],
            test_location['lat'],
            test_location['lng']
        )

        print("Full Agent 2 result:")
        for key, value in poi_result.items():
            print(f"  {key}: {value}")

    return len(successful) > 0

if __name__ == "__main__":
    success = test_major_cities()

    if success:
        print("\nAGENT 2 IMPROVEMENTS WORKING!")
        print("Ready for large-scale processing")
    else:
        print("\nNEED TO CHECK CONFIGURATION")

    sys.exit(0 if success else 1)