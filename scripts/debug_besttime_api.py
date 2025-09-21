"""
Debug BestTime API calls
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

def debug_besttime_api():
    """Debug BestTime API calls with detailed response"""

    private_key = os.getenv("BESTTIME_API_KEY_PRIVATE")
    public_key = os.getenv("BESTTIME_API_KEY_PUBLIC")

    print("Debug BestTime API")
    print("=" * 40)
    print(f"Private key: {private_key}")
    print(f"Public key: {public_key}")

    base_url = "https://besttime.app/api/v1"

    # Test 1: Simple venue query
    test_payload = {
        "api_key_private": private_key,
        "venue_name": "7-Eleven",
        "venue_address": "Hat Yai, Thailand"
    }

    print(f"\nTesting payload: {test_payload}")

    try:
        # Test forecasts endpoint
        print("\n1. Testing /forecasts endpoint (POST JSON)...")
        response = requests.post(f"{base_url}/forecasts", json=test_payload, timeout=30)
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")

        try:
            result = response.json()
            print(f"Response: {result}")
        except:
            print(f"Raw response: {response.text}")

    except Exception as e:
        print(f"Error: {e}")

    try:
        # Test forecasts endpoint with params
        print("\n2. Testing /forecasts endpoint (POST params)...")
        response = requests.post(f"{base_url}/forecasts", data=test_payload, timeout=30)
        print(f"Status: {response.status_code}")

        try:
            result = response.json()
            print(f"Response: {result}")
        except:
            print(f"Raw response: {response.text}")

    except Exception as e:
        print(f"Error: {e}")

    try:
        # Test with minimal payload
        minimal_payload = {
            "api_key_private": private_key,
            "venue_name": "McDonald's"
        }

        print("\n3. Testing minimal payload...")
        print(f"Payload: {minimal_payload}")
        response = requests.post(f"{base_url}/forecasts", json=minimal_payload, timeout=30)
        print(f"Status: {response.status_code}")

        try:
            result = response.json()
            print(f"Response: {result}")
        except:
            print(f"Raw response: {response.text}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_besttime_api()