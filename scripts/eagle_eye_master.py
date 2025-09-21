"""
Eagle Eye Master - One Command with Flexible Area Selection
"""

import os
import sys
import pandas as pd
import argparse
from datetime import datetime

# Add app directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

from processors.l2_database_processor import L2DatabaseProcessor
from processors.enhanced_poi_agent import EnhancedPOIAgent

class EagleEyeMaster:
    """Master orchestrator for Eagle Eye reports with flexible area selection"""

    def __init__(self):
        self.l2_csv_path = "data/South L2 Ports Utilization on W25036_20250905.csv"
        self.processor = None
        self.poi_agent = None

    def initialize_agents(self):
        """Initialize processing agents"""
        print("Initializing Eagle Eye agents...")
        self.processor = L2DatabaseProcessor(self.l2_csv_path)
        # Skip POI agent for basic functionality
        self.poi_agent = None

    def get_available_areas(self, sample_size=5000):
        """Get available areas from L2 data"""
        print("Scanning available areas...")

        # Initialize processor if not already done
        if self.processor is None:
            self.processor = L2DatabaseProcessor(self.l2_csv_path)

        # Load sample to get area options
        self.processor.load_data(sample_size=sample_size)
        self.processor.calculate_priority_scores()
        happy_blocks_df = self.processor.aggregate_happy_blocks()

        areas = {
            'provinces': sorted(happy_blocks_df['Province'].dropna().unique().tolist()),
            'districts': sorted(happy_blocks_df['District'].dropna().unique().tolist()),
            'subdistricts': sorted(happy_blocks_df['Subdistrict'].dropna().unique().tolist()),
            'villages': sorted(happy_blocks_df['Village_Name'].dropna().unique().tolist()),
            'happy_blocks': sorted(happy_blocks_df['Happy_Block'].dropna().unique().tolist())
        }

        return areas

    def filter_by_area(self, happy_blocks_df, **filters):
        """Filter Happy Blocks by various criteria"""

        filtered_df = happy_blocks_df.copy()

        # Filter by Province
        if filters.get('province'):
            provinces = [p.strip() for p in filters['province'].split(',')]
            filtered_df = filtered_df[filtered_df['Province'].isin(provinces)]

        # Filter by District
        if filters.get('district'):
            districts = [d.strip() for d in filters['district'].split(',')]
            filtered_df = filtered_df[filtered_df['District'].isin(districts)]

        # Filter by Subdistrict
        if filters.get('subdistrict'):
            subdistricts = [s.strip() for s in filters['subdistrict'].split(',')]
            filtered_df = filtered_df[filtered_df['Subdistrict'].isin(subdistricts)]

        # Filter by Village Name
        if filters.get('village'):
            villages = [v.strip() for v in filters['village'].split(',')]
            filtered_df = filtered_df[filtered_df['Village_Name'].isin(villages)]

        # Filter by Happy Block IDs
        if filters.get('happyblock'):
            happy_blocks = [h.strip() for h in filters['happyblock'].split(',')]
            filtered_df = filtered_df[filtered_df['Happy_Block'].isin(happy_blocks)]

        # Filter by Bounding Box (lat1,lng1,lat2,lng2)
        if filters.get('bbox'):
            try:
                lat1, lng1, lat2, lng2 = map(float, filters['bbox'].split(','))
                filtered_df = filtered_df[
                    (filtered_df['Latitude'] >= min(lat1, lat2)) &
                    (filtered_df['Latitude'] <= max(lat1, lat2)) &
                    (filtered_df['Longitude'] >= min(lng1, lng2)) &
                    (filtered_df['Longitude'] <= max(lng1, lng2))
                ]
            except ValueError:
                print("Invalid bbox format. Use: lat1,lng1,lat2,lng2")

        # Filter by Location Type
        if filters.get('location_type'):
            location_types = [l.strip() for l in filters['location_type'].split(',')]
            filtered_df = filtered_df[filtered_df['Location_Type'].isin(location_types)]

        return filtered_df

    def interactive_area_selection(self):
        """Interactive area selection mode"""
        print("\n" + "="*60)
        print("INTERACTIVE AREA SELECTION")
        print("="*60)

        # Get available areas
        areas = self.get_available_areas()

        # Show provinces
        print(f"\nAvailable Provinces ({len(areas['provinces'])}):")
        for i, province in enumerate(areas['provinces'][:10], 1):
            print(f"  {i}. {province}")
        if len(areas['provinces']) > 10:
            print(f"  ... and {len(areas['provinces'])-10} more")

        province = input("\nEnter Province name (or press Enter for all): ").strip()

        # Show districts for selected province
        if province:
            sample_df = pd.read_csv(self.l2_csv_path, nrows=5000)
            districts = sorted(sample_df[sample_df['Province'] == province]['District'].unique())

            print(f"\nDistricts in {province}:")
            for i, district in enumerate(districts, 1):
                print(f"  {i}. {district}")

            district = input("\nEnter District name (or press Enter for all): ").strip()
        else:
            district = ""

        # Ask for other filters
        limit = input("\nNumber of Happy Blocks to process (default: 10): ").strip()
        limit = int(limit) if limit.isdigit() else 10

        return {
            'province': province if province else None,
            'district': district if district else None,
            'limit': limit
        }

    def generate_report(self, **kwargs):
        """Generate report with flexible area selection"""

        print("="*80)
        print("EAGLE EYE MASTER - FLEXIBLE AREA TARGETING")
        print("="*80)

        # Initialize agents
        self.initialize_agents()

        # Load and process L2 data
        sample_size = kwargs.get('sample', 3000)
        self.processor.load_data(sample_size=sample_size)
        self.processor.calculate_priority_scores()
        happy_blocks_df = self.processor.aggregate_happy_blocks()

        print(f"Total Happy Blocks loaded: {len(happy_blocks_df):,}")

        # Apply area filters
        area_filters = {k: v for k, v in kwargs.items()
                       if k in ['province', 'district', 'subdistrict', 'village', 'happyblock', 'bbox', 'location_type'] and v}

        if area_filters:
            print(f"Applying filters: {area_filters}")
            filtered_blocks = self.filter_by_area(happy_blocks_df, **area_filters)
        else:
            # Default to Hat Yai if no filters
            print("No area filters specified, using Hat Yai default...")
            filtered_blocks = happy_blocks_df[
                (happy_blocks_df['District'] == 'หาดใหญ่')
            ]

        print(f"Filtered Happy Blocks: {len(filtered_blocks):,}")

        if len(filtered_blocks) == 0:
            print("No Happy Blocks found with specified criteria!")
            return None

        # Sort by priority and limit
        limit = kwargs.get('limit', 10)
        top_blocks = filtered_blocks.nlargest(limit, 'Priority_Score')

        print(f"Processing top {len(top_blocks)} Happy Blocks...")

        # Generate report rows
        report_rows = []
        for idx, (_, block) in enumerate(top_blocks.iterrows()):

            # Get L2 details
            l2_details = self.processor.df[
                self.processor.df['happy_block'] == block['Happy_Block']
            ].to_dict('records')

            # Create overview row
            overview_row = {
                'Level': 'OVERVIEW',
                'Happy_Block': block['Happy_Block'],
                'Village_Name': block['Village_Name'],
                'L2_Count': block['L2_Count'],
                'Priority_Score': round(block['Priority_Score'], 1),
                'Priority_Label': block['Priority_Label'],
                'Ports_Available': block['Total_Ports_Available'],
                'Province': block['Province'],
                'District': block['District'],
                'Subdistrict': block['Subdistrict'],
                'Location_Type': block.get('Location_Type', 'Unknown'),
                'Google_Maps': f"https://maps.google.com/?q={block['Latitude']},{block['Longitude']}",
                'Recommendations': f"{block['Priority_Label']} priority - {block['L2_Count']} L2s available",
                'Timing_Weekday': '17:00, 18:00, 19:00',  # Default timing
                'Timing_Weekend': '12:00, 17:00, 18:00',
                'Best_Day': 'Saturday'
            }
            report_rows.append(overview_row)

            # Add detail rows
            for l2 in l2_details:
                detail_row = {
                    'Level': 'DETAIL',
                    'Happy_Block': block['Happy_Block'],
                    'Village_Name': l2.get('Rollout Location name', ''),
                    'L2_Name': l2.get('splt_l2', ''),
                    'Priority_Score': round(l2.get('priority_score', 0), 1),
                    'Ports_Available': l2.get('sum_tol_avail', 0),
                    'Installation_Status': l2.get('installation_status', ''),
                    'Google_Maps': f"https://maps.google.com/?q={l2.get('latitude', 0)},{l2.get('longitude', 0)}",
                    'Coverage_Notes': f"L2: {l2.get('percent_utilization', 0):.1f}% util, {l2.get('inservice_aging', 0):.0f} days old"
                }
                report_rows.append(detail_row)

        # Create output
        df = pd.DataFrame(report_rows)

        # Generate filename based on filters
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        area_name = ""
        if kwargs.get('district'):
            area_name = f"_{kwargs['district'].replace(' ', '_')}"
        elif kwargs.get('province'):
            area_name = f"_{kwargs['province'].replace(' ', '_')}"
        elif kwargs.get('happyblock'):
            area_name = f"_happyblock_{kwargs['happyblock'][:8]}"

        output_path = f"eagle_eye_report{area_name}_{timestamp}.csv"

        # Save report
        df.to_csv(output_path, index=False, encoding='utf-8-sig')

        # Convert to Excel if requested
        if kwargs.get('format', 'csv').lower() == 'excel':
            excel_path = output_path.replace('.csv', '.xlsx')
            df.to_excel(excel_path, index=False, engine='openpyxl')
            output_path = excel_path

        # Summary
        print(f"\nEAGLE EYE REPORT GENERATED!")
        print(f"File: {output_path}")
        print(f"Overview rows: {len([r for r in report_rows if r.get('Level') == 'OVERVIEW'])}")
        print(f"Detail rows: {len([r for r in report_rows if r.get('Level') == 'DETAIL'])}")
        print(f"Area: {', '.join([f'{k}={v}' for k, v in area_filters.items()])}")
        print(f"Ready for sales team!")

        return output_path

def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(
        description='Eagle Eye Master - Flexible Area Selection for Door-to-Door Sales',
        epilog='''
Examples:
  %(prog)s --list-areas                              # List all available areas
  %(prog)s --province="สงขลา" --limit=10              # Select by province
  %(prog)s --district="หาดใหญ่" --limit=5             # Select by district
  %(prog)s --village="หมู่บ้านออกซิเจน วีฟวา"          # Select by village
  %(prog)s --happyblock="07110-100570" --format=excel  # Select by Happy Block ID
  %(prog)s --bbox="7.0,100.5,7.2,100.6" --limit=3     # Select by geographic area
  %(prog)s --interactive                             # Interactive mode
        ''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # Area selection options
    parser.add_argument('--province', help='Province name (comma-separated)')
    parser.add_argument('--district', help='District name (comma-separated)')
    parser.add_argument('--subdistrict', help='Subdistrict name (comma-separated)')
    parser.add_argument('--village', help='Village name (comma-separated)')
    parser.add_argument('--happyblock', help='Happy Block IDs (comma-separated)')
    parser.add_argument('--bbox', help='Bounding box: lat1,lng1,lat2,lng2')
    parser.add_argument('--location-type', help='Location type filter')

    # Processing options
    parser.add_argument('--limit', type=int, default=10, help='Number of Happy Blocks to process')
    parser.add_argument('--sample', type=int, default=3000, help='Sample size for faster processing')
    parser.add_argument('--format', choices=['csv', 'excel'], default='csv', help='Output format')

    # Modes
    parser.add_argument('--interactive', action='store_true', help='Interactive area selection')
    parser.add_argument('--list-areas', action='store_true', help='List available areas')

    args = parser.parse_args()

    # Initialize Eagle Eye Master
    eagle_eye = EagleEyeMaster()

    # List areas mode
    if args.list_areas:
        areas = eagle_eye.get_available_areas()
        print(f"\nAvailable Areas:")
        print(f"Provinces: {areas['provinces'][:5]}... ({len(areas['provinces'])} total)")
        print(f"Districts: {areas['districts'][:5]}... ({len(areas['districts'])} total)")
        print(f"Subdistricts: {areas['subdistricts'][:5]}... ({len(areas['subdistricts'])} total)")
        print(f"Villages: {areas['villages'][:5]}... ({len(areas['villages'])} total)")
        print(f"Happy Blocks: {len(areas['happy_blocks'])} total")
        return

    # Interactive mode
    if args.interactive:
        selections = eagle_eye.interactive_area_selection()
        args.province = selections.get('province')
        args.district = selections.get('district')
        args.limit = selections.get('limit', 10)

    # Generate report
    kwargs = {
        'province': args.province,
        'district': args.district,
        'subdistrict': args.subdistrict,
        'village': args.village,
        'happyblock': args.happyblock,
        'bbox': args.bbox,
        'location_type': args.location_type,
        'limit': args.limit,
        'sample': args.sample,
        'format': args.format
    }

    eagle_eye.generate_report(**kwargs)

if __name__ == "__main__":
    main()