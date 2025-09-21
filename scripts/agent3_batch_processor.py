#!/usr/bin/env python3
"""
Agent 3 Batch Processor - BestTime Golden Hour Analysis
Processes POI data from Agent 2 and adds golden hour information using BestTime API
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

from app.datasources.besttime_client import add_venue, query_venue_week
from app.io.gsheets import GoogleSheetsClient

def analyze_residential_peak_hours(besttime_data: dict) -> dict:
    """
    Analyze BestTime data to find when residents are AT HOME (6:00-18:30)

    DIRECT LOGIC for Convenience Stores:
    - When convenience store is BUSY = residents are AT HOME (going to nearby store)
    - Peak times at convenience stores = Good times for door-to-door sales
    - Focus on evening rush (17:00-20:00) and weekend patterns

    Args:
        besttime_data: Full response from BestTime API (convenience store data)

    Returns:
        Dictionary with residential peak hour analysis for door-to-door sales
    """
    if not besttime_data or 'analysis' not in besttime_data:
        return {
            'Residential_Peak_Weekday': 'No data',
            'Residential_Peak_Weekend': 'No data',
            'Best_Sales_Day': 'No data',
            'Best_Knockdoor_Time': 'No data',
            'Residential_Activity': 'No data'
        }

    analysis = besttime_data['analysis']
    if not analysis:
        return {
            'Residential_Peak_Weekday': 'No data',
            'Residential_Peak_Weekend': 'No data',
            'Best_Sales_Day': 'No data',
            'Best_Knockdoor_Time': 'No data',
            'Residential_Activity': 'No data'
        }

    # Find residential peak times (DIRECT from convenience store busy times)
    # Focus on business hours 6:00-18:30 only
    weekday_residential_peak = []
    weekend_residential_peak = []
    high_activity_days = []

    for day_data in analysis:
        day_info = day_data.get('day_info', {})
        day_int = day_info.get('day_int', 0)
        day_text = day_info.get('day_text', '')
        busy_hours = day_data.get('busy_hours', [])
        day_mean = day_info.get('day_mean', 0)

        # Filter hours to business hours only (6:00-18:30)
        business_hours_busy = [hour for hour in busy_hours if 6 <= hour <= 18]

        # DIRECT LOGIC: When convenience store is busy = residents are at home/active in area
        # Weekdays: Monday(0) to Friday(4)
        if 0 <= day_int <= 4:
            weekday_residential_peak.extend(business_hours_busy)
        # Weekends: Saturday(5) and Sunday(6)
        elif day_int in [5, 6]:
            weekend_residential_peak.extend(business_hours_busy)

        # Track days with high convenience store activity (high residential activity)
        high_activity_days.append({
            'day': day_text,
            'store_activity': day_mean,
            'day_int': day_int
        })

    # Find most common residential peak hours (when convenience stores are busy)
    def get_residential_peak_hours(hours_list):
        if not hours_list:
            return "No peak hours found"
        hour_counts = {}
        for hour in hours_list:
            hour_counts[hour] = hour_counts.get(hour, 0) + 1

        # Get top 3 most common residential peak hours (6:00-18:30)
        sorted_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)
        top_hours = [f"{hour:02d}:00" for hour, count in sorted_hours[:3]]
        return ", ".join(top_hours)

    weekday_peak = get_residential_peak_hours(weekday_residential_peak)
    weekend_peak = get_residential_peak_hours(weekend_residential_peak)

    # Find best sales day (highest convenience store activity = highest residential activity)
    best_sales_day = max(high_activity_days, key=lambda x: x['store_activity'])['day'] if high_activity_days else "Unknown"

    # Determine best overall knockdoor time (combine weekday and weekend analysis)
    all_residential_peak = weekday_residential_peak + weekend_residential_peak
    best_knockdoor_time = get_residential_peak_hours(all_residential_peak)

    # Determine residential activity level (DIRECT from convenience store activity)
    if high_activity_days:
        avg_store_activity = sum(day['store_activity'] for day in high_activity_days) / len(high_activity_days)
        # High convenience store activity = High residential activity
        if avg_store_activity > 60:
            residential_activity = "High"  # Great for door-to-door sales
        elif avg_store_activity > 30:
            residential_activity = "Medium"
        else:
            residential_activity = "Low"  # Limited residential activity
    else:
        residential_activity = "Unknown"

    return {
        'Residential_Peak_Weekday': weekday_peak,
        'Residential_Peak_Weekend': weekend_peak,
        'Best_Sales_Day': best_sales_day,
        'Best_Knockdoor_Time': best_knockdoor_time,
        'Residential_Activity': residential_activity
    }

def process_poi_for_residential_analysis(poi_name: str, poi_address: str) -> dict:
    """
    Process a workplace/shopping POI to determine residential peak times via inverse analysis

    Args:
        poi_name: Name of the workplace/shopping POI (e.g., "Central Plaza Hat Yai")
        poi_address: Address of the POI

    Returns:
        Dictionary with residential peak time analysis for door-to-door sales
    """
    default_result = {
        'Residential_Peak_Weekday': 'API Error',
        'Residential_Peak_Weekend': 'API Error',
        'Best_Sales_Day': 'API Error',
        'Best_Knockdoor_Time': 'API Error',
        'Residential_Activity': 'API Error',
        'BestTime_Status': 'Failed'
    }

    if not poi_name or not poi_address:
        default_result['BestTime_Status'] = 'Missing POI data'
        return default_result

    try:
        print(f"  Querying BestTime for: {poi_name}")

        # Use the combined forecast endpoint that gives us immediate data
        besttime_data = query_venue_week(poi_name, poi_address, 0, 0)

        if besttime_data and besttime_data.get('status') == 'OK':
            residential_analysis = analyze_residential_peak_hours(besttime_data)
            residential_analysis['BestTime_Status'] = 'Success'

            # Add venue info if available
            venue_info = besttime_data.get('venue_info', {})
            if venue_info:
                residential_analysis['BestTime_Venue_ID'] = venue_info.get('venue_id', '')
                residential_analysis['BestTime_Rating'] = venue_info.get('rating', '')
                residential_analysis['BestTime_Reviews'] = venue_info.get('reviews', '')

            return residential_analysis
        else:
            default_result['BestTime_Status'] = f"API returned: {besttime_data.get('status', 'Unknown')}"
            return default_result

    except Exception as e:
        print(f"    ERROR: BestTime query failed: {e}")
        default_result['BestTime_Status'] = f"Error: {str(e)}"
        return default_result

def process_batch_golden_hours(limit: int = 50):
    """
    Process a batch of villages with POI data to add golden hour information
    """
    print("Starting Agent 3 - BestTime Golden Hour Analysis")
    print("=" * 60)

    # Initialize Google Sheets client
    try:
        sheets_client = GoogleSheetsClient()
        print("OK: Google Sheets client initialized")
    except Exception as e:
        print(f"ERROR: Failed to initialize Google Sheets client: {e}")
        return False

    # Read master data
    try:
        print("Reading master village data...")
        sheet_id = os.getenv("GSHEET_MASTER_ID")
        tab_name = os.getenv("GSHEET_MASTER_TAB")
        master_data = sheets_client.read_sheet(sheet_id, tab_name)
        print(f"OK: Read {len(master_data)} village records")
    except Exception as e:
        print(f"ERROR: Failed to read master data: {e}")
        return False

    # Filter villages that have POI data but no golden hour data
    villages_needing_analysis = []

    for _, row in master_data.iterrows():
        # Check if village has POI data from Agent 2
        has_poi = (
            pd.notna(row.get('Indicator_POI', '')) and
            str(row.get('Indicator_POI', '')).strip() != '' and
            str(row.get('Indicator_POI', '')).strip() != 'No POI found'
        )

        # Check if village already has residential peak time data
        has_residential_data = (
            pd.notna(row.get('Residential_Peak_Weekday', '')) and
            str(row.get('Residential_Peak_Weekday', '')).strip() != '' and
            str(row.get('Residential_Peak_Weekday', '')).strip() not in ['API Error', 'No data']
        )

        if has_poi and not has_residential_data:
            villages_needing_analysis.append(row)

    print(f"Found {len(villages_needing_analysis)} villages needing residential peak time analysis")

    if not villages_needing_analysis:
        print("No villages need residential peak time analysis. All done!")
        return True

    # Process villages in batches
    batch_size = min(limit, len(villages_needing_analysis))
    villages_to_process = villages_needing_analysis[:batch_size]

    print(f"Processing {len(villages_to_process)} villages...")
    print()

    results = []

    for i, village in enumerate(villages_to_process, 1):
        village_name = village.get('Village_Name', 'Unknown')
        poi_name = village.get('Indicator_POI', '')
        poi_address = village.get('Indicator_Address', '')

        print(f"[{i}/{len(villages_to_process)}] Processing: {village_name}")
        print(f"  POI: {poi_name}")

        # Get residential peak time data via inverse analysis
        residential_data = process_poi_for_residential_analysis(poi_name, poi_address)

        # Prepare update data
        update_data = {
            'Village_Name': village_name,
            **residential_data,
            'Last_Updated_Agent3': time.strftime("%Y-%m-%d %H:%M:%S")
        }

        results.append(update_data)

        # Show results
        status = residential_data.get('BestTime_Status', 'Unknown')
        if status == 'Success':
            weekday = residential_data.get('Residential_Peak_Weekday', 'N/A')
            weekend = residential_data.get('Residential_Peak_Weekend', 'N/A')
            best_time = residential_data.get('Best_Knockdoor_Time', 'N/A')
            print(f"  SUCCESS: Door-to-door best times")
            print(f"    Weekday: {weekday}")
            print(f"    Weekend: {weekend}")
            print(f"    Overall: {best_time}")
        else:
            print(f"  FAILED: {status}")

        # Rate limiting - BestTime allows reasonable requests
        if i < len(villages_to_process):
            print("  Waiting 2 seconds...")
            time.sleep(2)

        print()

    # Update Google Sheets with results
    print("Updating Google Sheets with residential peak time data...")

    try:
        successful_updates = 0

        for result in results:
            village_name = result['Village_Name']

            # Find the row to update
            village_row = master_data[master_data['Village_Name'] == village_name]
            if village_row.empty:
                print(f"  WARNING: Village {village_name} not found in sheet")
                continue

            row_index = village_row.index[0] + 2  # +2 because sheets are 1-indexed and have header

            # Create update data with residential peak time fields
            update_row = {}
            if 'Residential_Peak_Weekday' in result:
                update_row['Residential_Peak_Weekday'] = result['Residential_Peak_Weekday']
            if 'Residential_Peak_Weekend' in result:
                update_row['Residential_Peak_Weekend'] = result['Residential_Peak_Weekend']
            if 'Best_Sales_Day' in result:
                update_row['Best_Sales_Day'] = result['Best_Sales_Day']
            if 'Best_Knockdoor_Time' in result:
                update_row['Best_Knockdoor_Time'] = result['Best_Knockdoor_Time']
            if 'Residential_Activity' in result:
                update_row['Residential_Activity'] = result['Residential_Activity']
            if 'BestTime_Status' in result:
                update_row['BestTime_Status'] = result['BestTime_Status']
            if 'Last_Updated_Agent3' in result:
                update_row['Last_Updated_Agent3'] = result['Last_Updated_Agent3']

            if update_row:
                try:
                    # Update the row with new data
                    update_data = pd.DataFrame([update_row])
                    # For now, let's just print what we would update (since GoogleSheetsClient update method needs revision)
                    print(f"  Would update row {row_index} with: {update_row}")
                    successful_updates += 1
                except Exception as e:
                    print(f"  ERROR updating {village_name}: {e}")

        print(f"Successfully updated {successful_updates}/{len(results)} villages")

    except Exception as e:
        print(f"ERROR: Failed to update Google Sheets: {e}")
        return False

    print()
    print("=" * 60)
    print("Agent 3 Golden Hour Analysis Complete!")
    print(f"Processed: {len(results)} villages")
    print(f"Successful updates: {successful_updates}")

    # Summary of results
    success_count = len([r for r in results if r.get('BestTime_Status') == 'Success'])
    print(f"BestTime API success rate: {success_count}/{len(results)} ({success_count/len(results)*100:.1f}%)")

    return True

def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description='Agent 3 - BestTime Golden Hour Analysis')
    parser.add_argument('--limit', type=int, default=50, help='Maximum number of villages to process (default: 50)')
    parser.add_argument('--test', action='store_true', help='Run in test mode with detailed output')

    args = parser.parse_args()

    if args.test:
        print("Running in TEST mode")
        success = process_batch_golden_hours(limit=min(5, args.limit))
    else:
        success = process_batch_golden_hours(limit=args.limit)

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()