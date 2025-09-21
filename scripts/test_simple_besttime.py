"""
Simple BestTime API test
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_simple_besttime():
    """Test BestTime API with simple example"""

    private_key = os.getenv("BESTTIME_API_KEY_PRIVATE")
    print(f"Using API key: {private_key}")

    # Simple test with exact format from documentation
    payload = {
        'api_key_private': private_key,
        'venue_name': 'McDonalds',
        'venue_address': 'Ocean Ave, San Francisco'
    }

    try:
        print("Sending request to BestTime API...")
        response = requests.post('https://besttime.app/api/v1/forecasts', json=payload, timeout=30)

        print(f"Response status: {response.status_code}")
        print(f"Response headers: {response.headers.get('content-type', 'unknown')}")

        if response.status_code == 200:
            result = response.json()
            print("SUCCESS! Response received:")
            print(f"Keys in response: {list(result.keys())}")

            if 'venue_info' in result:
                venue_info = result['venue_info']
                print(f"Venue ID: {venue_info.get('venue_id', 'Not found')}")
                print(f"Venue Name: {venue_info.get('venue_name', 'Not found')}")

            if 'analysis' in result:
                print("Analysis data available!")
                analysis = result['analysis']
                print(f"Analysis has {len(analysis)} days of data")
            else:
                print("No analysis data (might need to wait for processing)")

        else:
            print(f"ERROR Response:")
            try:
                error_info = response.json()
                print(f"Error: {error_info}")
            except:
                print(f"Raw response: {response.text}")

            # Check if it's an authentication issue
            if response.status_code == 401:
                print("Authentication failed - check API key")
            elif response.status_code == 403:
                print("Forbidden - check API permissions or quota")
            elif response.status_code == 429:
                print("Rate limited - too many requests")

    except requests.exceptions.Timeout:
        print("Request timed out")
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    test_simple_besttime()