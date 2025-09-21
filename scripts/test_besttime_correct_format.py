"""
Test BestTime API with correct format from documentation
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_besttime_correct_format():
    """Test BestTime API with exact format from documentation"""

    private_key = os.getenv("BESTTIME_API_KEY_PRIVATE")
    print(f"Testing with API key: {private_key}")

    # Exact format from BestTime documentation
    url = "https://besttime.app/api/v1/forecasts"
    params = {
        'api_key_private': private_key,
        'venue_name': 'McDonalds',
        'venue_address': 'Ocean Ave, San Francisco'
    }

    print(f"Request URL: {url}")
    print(f"Request params: {params}")

    try:
        print("Sending POST request with params...")
        response = requests.post(url, params=params, timeout=30)

        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")

        if response.status_code == 200:
            result = response.json()
            print("SUCCESS! BestTime API working!")
            print(f"Response keys: {list(result.keys())}")

            if 'venue_info' in result:
                venue_info = result['venue_info']
                print(f"Venue ID: {venue_info.get('venue_id')}")
                print(f"Venue Name: {venue_info.get('venue_name')}")

            if 'analysis' in result:
                print("Timing analysis data available!")

        else:
            try:
                error_data = response.json()
                print(f"API Error: {error_data}")
            except:
                print(f"Raw error response: {response.text}")

    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_besttime_correct_format()