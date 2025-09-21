#!/usr/bin/env python3
"""
Simple Google Sheets authentication setup
"""

import os
import gspread
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def setup_google_sheets_auth():
    """Setup Google Sheets authentication using simple method"""

    print("Setting up Google Sheets Authentication")
    print("=" * 50)

    # Method 1: Try gspread.oauth() (simplest)
    print("Method 1: Using gspread.oauth() (recommended)")
    print("This will open a browser window for authorization")

    try:
        gc = gspread.oauth()
        print("OK: Authentication successful!")

        # Test access to your sheet
        sheet_id = os.getenv("GSHEET_MASTER_ID", "1aRuiVS8b-Kmnn48MHg5Nm-lr13a997AVEzIMjt5IN1c")
        sheet = gc.open_by_key(sheet_id)

        print(f"OK: Successfully accessed sheet: {sheet.title}")
        print(f"Available worksheets: {[ws.title for ws in sheet.worksheets()]}")

        return True

    except Exception as e:
        print(f"ERROR: Method 1 failed: {e}")
        print("\n" + "="*50)
        print("Alternative setup required:")
        print("1. Go to: https://console.cloud.google.com/")
        print("2. Create a new project or select existing")
        print("3. Enable Google Sheets API")
        print("4. Create OAuth2 credentials:")
        print("   - Credentials → Create Credentials → OAuth client ID")
        print("   - Application type: Desktop application")
        print("   - Download JSON file")
        print("5. Rename to 'credentials.json' and put in credentials/ folder")
        print("6. Run this script again")
        return False

def test_sheet_access():
    """Test if we can access the Google Sheet"""
    try:
        gc = gspread.oauth()
        sheet_id = os.getenv("GSHEET_MASTER_ID", "1aRuiVS8b-Kmnn48MHg5Nm-lr13a997AVEzIMjt5IN1c")
        sheet = gc.open_by_key(sheet_id)
        worksheet = sheet.worksheets()[0]  # First worksheet

        # Get a sample of data
        data = worksheet.get_all_records()

        print(f"OK: Sheet access test successful!")
        print(f"   Sheet title: {sheet.title}")
        print(f"   First worksheet: {worksheet.title}")
        print(f"   Total rows: {len(data)}")

        if data:
            print(f"   Sample columns: {list(data[0].keys())[:5]}...")

        return True

    except Exception as e:
        print(f"ERROR: Sheet access test failed: {e}")
        return False

if __name__ == "__main__":
    print("Google Sheets Authentication Setup")
    print("This will help you connect to your Google Sheets")
    print()

    success = setup_google_sheets_auth()

    if success:
        print("\nSetup complete! Testing sheet access...")
        test_sheet_access()
        print("\nGoogle Sheets is ready for Agent 2!")
    else:
        print("\nManual setup required. Follow the instructions above.")