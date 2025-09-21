"""
Test different BestTime API request formats
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_api_formats():
    """Test different request formats for BestTime API"""

    private_key = os.getenv("BESTTIME_API_KEY_PRIVATE")
    base_url = "https://besttime.app/api/v1/forecasts"

    test_data = {
        'api_key_private': private_key,
        'venue_name': 'McDonalds'
    }

    print("Testing different BestTime API formats")
    print("=" * 50)

    # Test 1: POST with form data
    print("\n1. Testing POST with form data...")
    try:
        response = requests.post(base_url, data=test_data, timeout=30)
        print(f"Status: {response.status_code}")
        if response.status_code != 200:
            print(f"Error: {response.text}")
        else:
            print("Success!")
    except Exception as e:
        print(f"Error: {e}")

    # Test 2: POST with JSON
    print("\n2. Testing POST with JSON...")
    try:
        response = requests.post(base_url, json=test_data, timeout=30)
        print(f"Status: {response.status_code}")
        if response.status_code != 200:
            print(f"Error: {response.text}")
        else:
            print("Success!")
    except Exception as e:
        print(f"Error: {e}")

    # Test 3: GET with query params
    print("\n3. Testing GET with query params...")
    try:
        response = requests.get(base_url, params=test_data, timeout=30)
        print(f"Status: {response.status_code}")
        if response.status_code != 200:
            print(f"Error: {response.text}")
        else:
            print("Success!")
    except Exception as e:
        print(f"Error: {e}")

    # Test 4: Check API key validity by testing a simpler endpoint
    print("\n4. Testing API key validity...")
    simple_url = "https://besttime.app/api/v1/keys/info"
    try:
        response = requests.get(simple_url, params={'api_key_private': private_key}, timeout=30)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

    # Test 5: Try with venue search endpoint
    print("\n5. Testing venue search...")
    search_url = "https://besttime.app/api/v1/venues/search"
    search_data = {
        'api_key_private': private_key,
        'q': 'McDonald',
        'location': 'San Francisco'
    }
    try:
        response = requests.post(search_url, json=search_data, timeout=30)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Search results: {len(result.get('venues', []))} venues found")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_api_formats()