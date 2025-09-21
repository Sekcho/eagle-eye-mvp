#!/usr/bin/env python3
"""
Test Google Sheets access with Service Account
"""

import os
import sys
from dotenv import load_dotenv
import gspread
from google.oauth2.service_account import Credentials

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_service_account_access():
    """Test Google Sheets access using Service Account"""

    print("Testing Google Sheets Service Account Access")
    print("=" * 50)

    # Path to service account credentials
    service_account_path = "credentials/service-account.json"

    if not os.path.exists(service_account_path):
        print(f"ERROR: Service account file not found: {service_account_path}")
        return False

    try:
        # Setup credentials and authorize
        scope = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]

        creds = Credentials.from_service_account_file(service_account_path, scopes=scope)
        client = gspread.authorize(creds)

        print("OK: Service Account authentication successful!")

        # Test access to your Google Sheet
        sheet_id = os.getenv("GSHEET_MASTER_ID", "1aRuiVS8b-Kmnn48MHg5Nm-lr13a997AVEzIMjt5IN1c")

        print(f"Accessing sheet ID: {sheet_id}")
        sheet = client.open_by_key(sheet_id)

        print(f"OK: Successfully opened sheet: {sheet.title}")
        print(f"Available worksheets: {[ws.title for ws in sheet.worksheets()]}")

        # Test reading data from first worksheet
        worksheet = sheet.worksheets()[0]
        data = worksheet.get_all_records()

        print(f"OK: Successfully read {len(data)} rows")

        if data:
            print("Sample columns:", list(data[0].keys())[:8])

            # Count rows with coordinates but no POI
            needs_poi = 0
            for row in data:
                if (row.get('Latitude') and row.get('Longitude') and
                    not row.get('Indicator_POI')):
                    needs_poi += 1

            print(f"Villages needing POI processing: {needs_poi}")

        return True

    except Exception as e:
        print(f"ERROR: Service Account test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_service_account_access()

    if success:
        print("\nSUCCESS: Google Sheets Service Account is ready!")
        print("You can now run Agent 2 with Google Sheets integration")
    else:
        print("\nFAILED: Please check:")
        print("1. Service account file exists")
        print("2. Google Sheets is shared with service account email")
        print("3. Google Sheets API is enabled")

    sys.exit(0 if success else 1)