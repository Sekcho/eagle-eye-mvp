#!/usr/bin/env python3
"""
Simple test script for Agent 2 - Google Places POI Finder
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.datasources.gmaps_client import GoogleMapsClient, find_nearest_7eleven, find_nearest_convenience_store, get_poi_for_village

def test_google_maps_client():
    """Test basic Google Maps client functionality"""
    print("Testing Google Maps Client...")

    try:
        client = GoogleMapsClient()
        print("OK: Client initialized successfully")
    except Exception as e:
        print(f"ERROR: Client initialization failed: {e}")
        return False

    # Test coordinates (Hat Yai, Songkhla)
    test_lat = 7.0067
    test_lng = 100.4681
    test_village = "Test Village Hat Yai"

    print(f"\nTesting with coordinates: {test_lat}, {test_lng}")

    # Test find nearby places with improved radius
    print("\nTesting find_nearby_places with 3km radius...")
    try:
        places = client.find_nearby_places(test_lat, test_lng, keyword="7-Eleven", radius=3000)
        print(f"OK: Found {len(places)} places within 3km")

        if places:
            nearest = places[0]
            print(f"   Nearest: {nearest['name']} - {nearest.get('distance_km', 'N/A')}km")
            print(f"   Address: {nearest['address']}")
            print(f"   Place ID: {nearest['place_id']}")

    except Exception as e:
        print(f"ERROR: find_nearby_places failed: {e}")
        return False

    # Test improved multi-keyword search
    print("\nTesting find_nearest_convenience_store (multi-keyword)...")
    try:
        nearest_store = find_nearest_convenience_store(test_lat, test_lng)
        if nearest_store:
            print(f"OK: Found convenience store: {nearest_store['name']} - {nearest_store.get('distance_km', 'N/A')}km")
            print(f"   Search keyword: {nearest_store.get('search_keyword', 'N/A')}")
            print(f"   Address: {nearest_store['address']}")
        else:
            print("WARNING: No convenience store found within 3km radius")

    except Exception as e:
        print(f"ERROR: find_nearest_convenience_store failed: {e}")
        return False

    # Test legacy find_nearest_7eleven function
    print("\nTesting find_nearest_7eleven (legacy)...")
    try:
        nearest_7e = find_nearest_7eleven(test_lat, test_lng)
        if nearest_7e:
            print(f"OK: Found store: {nearest_7e['name']} - {nearest_7e.get('distance_km', 'N/A')}km")
        else:
            print("WARNING: No store found within 3km radius")

    except Exception as e:
        print(f"ERROR: find_nearest_7eleven failed: {e}")
        return False

    # Test get_poi_for_village (main Agent 2 function)
    print("\nTesting get_poi_for_village (Agent 2 main function)...")
    try:
        poi_result = get_poi_for_village(test_village, test_lat, test_lng)
        print("OK: Agent 2 function completed")
        print("   Result:")
        for key, value in poi_result.items():
            print(f"     {key}: {value}")

    except Exception as e:
        print(f"ERROR: get_poi_for_village failed: {e}")
        return False

    return True

def main():
    """Run all tests"""
    print("Starting Agent 2 Tests")
    print("=" * 50)

    # Check environment variables
    required_env_vars = ["GOOGLE_MAPS_API_KEY"]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]

    if missing_vars:
        print(f"ERROR: Missing required environment variables: {', '.join(missing_vars)}")
        print("   Please set them in your .env file")
        return False

    print("OK: Environment variables found")

    # Run test
    print(f"\n{'='*20} Google Maps Client {'='*20}")
    try:
        if test_google_maps_client():
            print("PASSED: Google Maps Client test")
            passed_tests = 1
        else:
            print("FAILED: Google Maps Client test")
            passed_tests = 0
    except Exception as e:
        print(f"CRASHED: Google Maps Client test: {e}")
        passed_tests = 0

    print(f"\n{'='*50}")
    print(f"Tests completed: {passed_tests}/1 passed")

    if passed_tests == 1:
        print("SUCCESS: All tests passed! Agent 2 is ready to use.")
        return True
    else:
        print("WARNING: Some tests failed. Please check the configuration.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)