#!/usr/bin/env python3
"""
Test script for Agent 2 - Google Places POI Finder

This script tests the Google Maps client functionality
independently of the n8n workflow.
"""

import os
import sys

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.datasources.gmaps_client import GoogleMapsClient, find_nearest_7eleven, get_poi_for_village

def test_google_maps_client():
    """Test basic Google Maps client functionality"""
    print("🧪 Testing Google Maps Client...")

    try:
        client = GoogleMapsClient()
        print("✅ Client initialized successfully")
    except Exception as e:
        print(f"❌ Client initialization failed: {e}")
        return False

    # Test coordinates (somewhere in Hat Yai, Songkhla)
    test_lat = 7.0067
    test_lng = 100.4681
    test_village = "หมู่บ้านทดสอบ หาดใหญ่"

    print(f"\n📍 Testing with coordinates: {test_lat}, {test_lng}")

    # Test find nearby places
    print("\n🔍 Testing find_nearby_places...")
    try:
        places = client.find_nearby_places(test_lat, test_lng, keyword="7-Eleven", radius=2000)
        print(f"✅ Found {len(places)} places")

        if places:
            nearest = places[0]
            print(f"   Nearest: {nearest['name']} - {nearest.get('distance_km', 'N/A')}km")
            print(f"   Address: {nearest['address']}")
            print(f"   Place ID: {nearest['place_id']}")

    except Exception as e:
        print(f"❌ find_nearby_places failed: {e}")
        return False

    # Test find_nearest_7eleven convenience function
    print("\n🏪 Testing find_nearest_7eleven...")
    try:
        nearest_7e = find_nearest_7eleven(test_lat, test_lng)
        if nearest_7e:
            print(f"✅ Found 7-Eleven: {nearest_7e['name']} - {nearest_7e.get('distance_km', 'N/A')}km")
        else:
            print("⚠️  No 7-Eleven found within 2km radius")

    except Exception as e:
        print(f"❌ find_nearest_7eleven failed: {e}")
        return False

    # Test get_poi_for_village (main Agent 2 function)
    print("\n🎯 Testing get_poi_for_village (Agent 2 main function)...")
    try:
        poi_result = get_poi_for_village(test_village, test_lat, test_lng)
        print("✅ Agent 2 function completed")
        print("   Result:")
        for key, value in poi_result.items():
            print(f"     {key}: {value}")

    except Exception as e:
        print(f"❌ get_poi_for_village failed: {e}")
        return False

    return True

def test_geocoding():
    """Test geocoding functionality"""
    print("\n🌍 Testing Geocoding...")

    try:
        client = GoogleMapsClient()

        # Test addresses in Songkhla/Hat Yai area
        test_addresses = [
            "หาดใหญ่ สงขลา",
            "มหาวิทยาลัยสงขลานครินทร์ หาดใหญ่",
            "เทสโก้โลตัส หาดใหญ่"
        ]

        for address in test_addresses:
            print(f"\n📍 Geocoding: {address}")
            try:
                coords = client.geocode(address)
                if coords:
                    lat, lng = coords
                    print(f"✅ Found: {lat}, {lng}")
                else:
                    print("⚠️  No coordinates found")
            except Exception as e:
                print(f"❌ Error: {e}")

    except Exception as e:
        print(f"❌ Geocoding test failed: {e}")
        return False

    return True

def main():
    """Run all tests"""
    print("🚀 Starting Agent 2 Tests")
    print("=" * 50)

    # Check environment variables
    required_env_vars = ["GOOGLE_MAPS_API_KEY"]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]

    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("   Please set them in your .env file")
        return False

    print("✅ Environment variables found")

    # Run tests
    tests = [
        ("Google Maps Client", test_google_maps_client),
        ("Geocoding", test_geocoding)
    ]

    passed_tests = 0
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                print(f"✅ {test_name} PASSED")
                passed_tests += 1
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} CRASHED: {e}")

    print(f"\n{'='*50}")
    print(f"🏁 Tests completed: {passed_tests}/{len(tests)} passed")

    if passed_tests == len(tests):
        print("🎉 All tests passed! Agent 2 is ready to use.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the configuration.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)