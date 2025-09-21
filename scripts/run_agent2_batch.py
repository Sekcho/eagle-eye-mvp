#!/usr/bin/env python3
"""
Batch processor for Agent 2 - Process all villages in Google Sheets
"""

import os
import sys
import time
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.datasources.gmaps_client import get_poi_for_village
from app.io.gsheets import GoogleSheetsClient

def process_villages_batch():
    """Process all villages that need POI data"""

    print("Starting Agent 2 Batch Processing...")
    print("=" * 50)

    # Initialize Google Sheets client
    try:
        gsheets = GoogleSheetsClient()
        print("OK: Google Sheets client initialized")
    except Exception as e:
        print(f"ERROR: Cannot initialize Google Sheets client: {e}")
        return False

    # Read master village data
    sheet_id = os.getenv("GSHEET_MASTER_ID")
    sheet_tab = os.getenv("GSHEET_MASTER_TAB", "master_village_data_clean")

    try:
        df = gsheets.read_sheet(sheet_id, sheet_tab)
        print(f"OK: Read {len(df)} villages from Google Sheets")
    except Exception as e:
        print(f"ERROR: Cannot read Google Sheets: {e}")
        return False

    # Filter villages that need POI processing
    # Has Latitude/Longitude but no Indicator_POI
    needs_poi = df[
        (df['Latitude'].notna()) &
        (df['Longitude'].notna()) &
        (df['Latitude'] != '') &
        (df['Longitude'] != '') &
        ((df['Indicator_POI'].isna()) | (df['Indicator_POI'] == ''))
    ].copy()

    print(f"Found {len(needs_poi)} villages that need POI processing")

    if len(needs_poi) == 0:
        print("All villages already have POI data!")
        return True

    # Process each village
    processed_count = 0
    updated_rows = []

    for index, row in needs_poi.iterrows():
        village_id = row.get('Village_ID', f"row_{index}")
        village_name = row.get('Village_Name', 'Unknown Village')
        lat = float(row['Latitude'])
        lng = float(row['Longitude'])

        print(f"\nProcessing {processed_count + 1}/{len(needs_poi)}: {village_name}")
        print(f"  Coordinates: {lat}, {lng}")

        try:
            # Run Agent 2 for this village
            poi_result = get_poi_for_village(village_name, lat, lng)

            if poi_result['Indicator_POI']:
                # Update the dataframe
                df.loc[index, 'Indicator_POI'] = poi_result['Indicator_POI']
                df.loc[index, 'Indicator_Place_ID'] = poi_result['Indicator_Place_ID']
                df.loc[index, 'Indicator_Address'] = poi_result['Indicator_Address']
                df.loc[index, 'Last_Updated'] = poi_result['Last_Updated']

                updated_rows.append({
                    'Village_ID': village_id,
                    'Village_Name': village_name,
                    'POI': poi_result['Indicator_POI'],
                    'Distance': poi_result.get('distance_km', 'N/A')
                })

                processed_count += 1
                print(f"  SUCCESS: Found {poi_result['Indicator_POI']}")
            else:
                print(f"  WARNING: No POI found for {village_name}")

            # Rate limiting - be nice to Google API
            time.sleep(1)

        except Exception as e:
            print(f"  ERROR: Failed to process {village_name}: {e}")
            continue

    # Update Google Sheets with results
    if updated_rows:
        try:
            gsheets.update_sheet(sheet_id, sheet_tab, df)
            print(f"\nSUCCESS: Updated {len(updated_rows)} villages in Google Sheets")

            print("\nUpdated villages:")
            for row in updated_rows:
                print(f"  - {row['Village_Name']}: {row['POI']}")

        except Exception as e:
            print(f"ERROR: Failed to update Google Sheets: {e}")
            return False

    print(f"\nBatch processing completed!")
    print(f"Total processed: {processed_count}/{len(needs_poi)}")
    return True

if __name__ == "__main__":
    success = process_villages_batch()
    sys.exit(0 if success else 1)