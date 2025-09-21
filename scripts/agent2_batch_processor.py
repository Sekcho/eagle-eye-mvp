#!/usr/bin/env python3
"""
Agent 2 Batch Processor - Google Places POI Finder

This script processes all villages in Google Sheets and finds the nearest 7-Eleven
using Google Places API, then updates the sheet with POI information.
"""

import os
import sys
import time
import pandas as pd
from dotenv import load_dotenv
from typing import Dict, List

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.datasources.gmaps_client import get_poi_for_village
from app.io.gsheets import GoogleSheetsClient

class Agent2BatchProcessor:
    """Agent 2 Batch Processor for finding POIs for all villages"""

    def __init__(self):
        self.gsheets = GoogleSheetsClient()
        # CSV-based system (Google Sheets variables kept for compatibility)
        self.sheet_id = "CSV_BASED_SYSTEM"
        self.sheet_tab = "master_village_data"

        # Processing options
        self.batch_size = 10  # Process N villages at a time
        self.delay_between_requests = 1.5  # Seconds (to respect API rate limits)
        self.used_place_ids = set()  # Track used POIs to prevent duplicates

    def load_villages(self) -> pd.DataFrame:
        """Load village data from CSV files"""
        print("Loading village data from CSV files...")

        try:
            df = self.gsheets.read_sheet(self.sheet_id, self.sheet_tab)
            print(f"Loaded {len(df)} villages from CSV")
            return df
        except Exception as e:
            print(f"ERROR: Failed to load village data: {e}")
            raise

    def filter_villages_needing_poi(self, df: pd.DataFrame) -> pd.DataFrame:
        """Filter villages that need POI processing"""
        print("Filtering villages that need POI processing...")

        # Clean up data types
        df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
        df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')

        # Filter criteria:
        # 1. Has valid Latitude and Longitude
        # 2. Indicator_POI is empty or null
        needs_poi = df[
            (df['Latitude'].notna()) &
            (df['Longitude'].notna()) &
            (df['Latitude'] != 0) &
            (df['Longitude'] != 0) &
            ((df['Indicator_POI'].isna()) | (df['Indicator_POI'] == '') | (df['Indicator_POI'] == 'nan'))
        ].copy()

        print(f"Found {len(needs_poi)} villages needing POI processing")
        print(f"Total villages with coordinates: {len(df[(df['Latitude'].notna()) & (df['Longitude'].notna())])}")

        if len(needs_poi) == 0:
            print("All villages already have POI data!")

        return needs_poi

    def process_village_batch(self, villages: pd.DataFrame, start_idx: int = 0) -> List[Dict]:
        """Process a batch of villages"""
        batch_end = min(start_idx + self.batch_size, len(villages))
        batch_villages = villages.iloc[start_idx:batch_end]

        print(f"\nProcessing batch {start_idx+1}-{batch_end} of {len(villages)} villages")
        print("=" * 60)

        results = []

        for idx, (_, row) in enumerate(batch_villages.iterrows(), start_idx + 1):
            village_id = row.get('Village_ID', f"row_{idx}")
            village_name = row.get('Village_Name', 'Unknown Village')
            lat = float(row['Latitude'])
            lng = float(row['Longitude'])

            print(f"\n[{idx}/{len(villages)}] Processing: {village_name}")
            print(f"  Coordinates: {lat:.4f}, {lng:.4f}")

            try:
                # Run Agent 2 for this village (excluding already used POIs)
                poi_result = get_poi_for_village(village_name, lat, lng, self.used_place_ids)

                if poi_result['Indicator_POI']:
                    # Add this Place ID to the exclusion set
                    place_id = poi_result['Indicator_Place_ID']
                    if place_id:
                        self.used_place_ids.add(place_id)

                    results.append({
                        'row_index': row.name,  # pandas index for updating
                        'Village_ID': village_id,
                        'Village_Name': village_name,
                        'Indicator_POI': poi_result['Indicator_POI'],
                        'Indicator_Place_ID': poi_result['Indicator_Place_ID'],
                        'Indicator_Address': poi_result['Indicator_Address'],
                        'Last_Updated': poi_result['Last_Updated']
                    })
                    print(f"  SUCCESS: Found {poi_result['Indicator_POI']} (Place ID: {place_id})")
                else:
                    print(f"  NO POI: No convenience store found within 3km")

                # Rate limiting - be nice to Google API
                if idx < len(villages):  # Don't delay after last request
                    time.sleep(self.delay_between_requests)

            except Exception as e:
                print(f"  ERROR: Failed to process {village_name}: {e}")
                continue

        return results

    def update_dataframe(self, df: pd.DataFrame, results: List[Dict]) -> pd.DataFrame:
        """Update the dataframe with POI results"""
        print(f"\nUpdating dataframe with {len(results)} results...")

        for result in results:
            row_idx = result['row_index']
            df.loc[row_idx, 'Indicator_POI'] = result['Indicator_POI']
            df.loc[row_idx, 'Indicator_Place_ID'] = result['Indicator_Place_ID']
            df.loc[row_idx, 'Indicator_Address'] = result['Indicator_Address']
            df.loc[row_idx, 'Last_Updated'] = result['Last_Updated']

        return df

    def save_results(self, df: pd.DataFrame, results: List[Dict]):
        """Save results to CSV files"""
        if not results:
            print("No results to save")
            return

        print(f"Saving {len(results)} updates to CSV...")

        try:
            self.gsheets.update_sheet(self.sheet_id, self.sheet_tab, df)
            print("SUCCESS: Results saved to CSV!")

            # Summary
            print("\nProcessing Summary:")
            print("-" * 40)
            for result in results[:10]:  # Show first 10
                print(f"  {result['Village_Name']}: {result['Indicator_POI']}")

            if len(results) > 10:
                print(f"  ... and {len(results) - 10} more villages")

        except Exception as e:
            print(f"ERROR: Failed to save to Google Sheets: {e}")

            # Fallback: save to CSV
            backup_path = f"data/agent2_results_backup_{int(time.time())}.csv"
            df.to_csv(backup_path, index=False)
            print(f"BACKUP: Results saved to {backup_path}")

    def run_batch_processing(self, max_villages: int = None, start_from: int = 0):
        """Run the complete batch processing"""
        print("Starting Agent 2 Batch Processing")
        print("=" * 50)
        print(f"Target: Find POI for villages in Google Sheets")
        print(f"Batch size: {self.batch_size} villages")
        print(f"API delay: {self.delay_between_requests} seconds")
        if max_villages:
            print(f"Max villages to process: {max_villages}")
        if start_from > 0:
            print(f"Starting from village #{start_from + 1}")
        print()

        # Load data
        df = self.load_villages()
        needs_poi = self.filter_villages_needing_poi(df)

        if len(needs_poi) == 0:
            print("All villages already have POI data. Nothing to process!")
            return True

        # Apply limits
        if start_from > 0:
            needs_poi = needs_poi.iloc[start_from:]
            print(f"Starting from village #{start_from + 1}, remaining: {len(needs_poi)}")

        if max_villages:
            needs_poi = needs_poi.head(max_villages)
            print(f"Limited to {max_villages} villages")

        print(f"Will process {len(needs_poi)} villages")

        # Confirm before starting (skip confirmation for batch processing)
        if len(needs_poi) > 50:
            print(f"About to process {len(needs_poi)} villages. This may take {len(needs_poi) * self.delay_between_requests / 60:.1f} minutes.")
            print("Starting processing automatically...")

        # Process in batches
        all_results = []
        processed_count = 0

        for batch_start in range(0, len(needs_poi), self.batch_size):
            batch_results = self.process_village_batch(needs_poi, batch_start)
            all_results.extend(batch_results)
            processed_count += min(self.batch_size, len(needs_poi) - batch_start)

            # Save progress after each batch
            if batch_results:
                updated_df = self.update_dataframe(df.copy(), all_results)
                self.save_results(updated_df, all_results)

            print(f"\nBatch complete. Progress: {processed_count}/{len(needs_poi)} villages")

            # Give user a chance to stop
            if batch_start + self.batch_size < len(needs_poi):
                print("Press Ctrl+C to stop, or wait 3 seconds to continue...")
                try:
                    time.sleep(3)
                except KeyboardInterrupt:
                    print("\nProcessing stopped by user")
                    break

        # Final summary
        print(f"\nAgent 2 Batch Processing Complete!")
        print(f"Processed: {processed_count} villages")
        print(f"Found POI: {len(all_results)} villages")
        print(f"Success rate: {len(all_results)/processed_count*100:.1f}%")

        return True

def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description='Agent 2 Batch Processor - Find POI for villages')
    parser.add_argument('--max', type=int, help='Maximum number of villages to process')
    parser.add_argument('--start', type=int, default=0, help='Start from village number (0-based)')
    parser.add_argument('--test', action='store_true', help='Test mode - process only 5 villages')

    args = parser.parse_args()

    if args.test:
        args.max = 5
        print("TEST MODE: Processing only 5 villages")

    processor = Agent2BatchProcessor()
    success = processor.run_batch_processing(
        max_villages=args.max,
        start_from=args.start
    )

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()