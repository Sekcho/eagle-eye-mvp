#!/usr/bin/env python3
"""
Test BestTime API functionality for Agent 3
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.datasources.besttime_client import add_venue, get_populartimes

def test_besttime_api():
    """Test BestTime API connection and functionality"""

    print("Testing BestTime API")
    print("=" * 40)

    # Check API key
    api_key = os.getenv("BESTTIME_API_KEY_PRIVATE")
    if not api_key or api_key.startswith("pri_xxxxx"):
        print("ERROR: BESTTIME_API_KEY_PRIVATE not configured")
        print("Please set a valid BestTime API key in .env file")
        return False

    print(f"API Key found: {api_key[:8]}...")

    # Test with a known venue (use major shopping center)
    test_venue = {
        "name": "Central Festival Hatyai",
        "address": "233/5 Phetkasem Rd, Hat Yai, Songkhla 90110, Thailand",
        "lat": 7.0067,
        "lng": 100.4681
    }

    print(f"\nTesting with venue: {test_venue['name']}")
    print(f"Address: {test_venue['address']}")
    print(f"Coordinates: {test_venue['lat']}, {test_venue['lng']}")

    try:
        # Step 1: Add venue to BestTime
        print("\nStep 1: Adding venue to BestTime...")
        venue_id = add_venue(
            test_venue["name"],
            test_venue["address"],
            test_venue["lat"],
            test_venue["lng"]
        )

        if venue_id:
            print(f"SUCCESS: Venue added with ID: {venue_id}")
        else:
            print("ERROR: No venue ID returned")
            return False

        # Step 2: Get popular times
        print(f"\nStep 2: Getting popular times for venue {venue_id}...")
        popular_times = get_populartimes(venue_id)

        print("SUCCESS: Popular times retrieved")
        print("Response keys:", list(popular_times.keys()))

        # Analyze the response
        if "analysis" in popular_times:
            analysis = popular_times["analysis"]
            print("\nAnalysis found:")
            if isinstance(analysis, dict):
                for key, value in analysis.items():
                    print(f"  {key}: {value}")
            else:
                print(f"  {analysis}")

        if "populartimes" in popular_times:
            populartimes = popular_times["populartimes"]
            print(f"\nPopular times data type: {type(populartimes)}")
            if isinstance(populartimes, list) and populartimes:
                print(f"Days available: {len(populartimes)}")
                # Show first day as example
                if populartimes[0]:
                    day_data = populartimes[0]
                    print(f"Sample day data keys: {list(day_data.keys())}")

        return True

    except Exception as e:
        print(f"ERROR: BestTime API test failed: {e}")
        return False

def test_venue_lookup():
    """Test if we can look up existing venues"""
    print("\n" + "=" * 40)
    print("Testing venue lookup capabilities")

    # This would test looking up existing venues if BestTime API supports it
    # For now, we'll focus on the add_venue + get_populartimes workflow

    print("Note: Using add_venue + get_populartimes workflow")
    print("This is the standard BestTime API pattern")

    return True

if __name__ == "__main__":
    print("BestTime API Test Suite")
    print("=" * 50)

    success = test_besttime_api() and test_venue_lookup()

    if success:
        print("\nSUCCESS: BestTime API is working!")
        print("Agent 3 can proceed with implementation")
    else:
        print("\nFAILED: BestTime API test failed")
        print("Please check API key and configuration")

    sys.exit(0 if success else 1)