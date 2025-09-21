"""
Production Enhanced L2 Sales Report Generator
Uses smart default timing with POI-based adjustments instead of BestTime API
"""

import os
import sys
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from typing import Dict, List

# Load environment variables
load_dotenv()

# Add app directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

from processors.l2_database_processor import L2DatabaseProcessor
from processors.enhanced_poi_agent import EnhancedPOIAgent

class ProductionEnhancedReportGenerator:
    """Production-ready enhanced sales report generator with smart timing"""

    def __init__(self, l2_csv_path: str):
        """Initialize production report generator"""
        self.l2_csv_path = l2_csv_path
        self.l2_processor = L2DatabaseProcessor(l2_csv_path)
        self.poi_agent = EnhancedPOIAgent()

        self.happy_blocks_data = {}

    def load_and_process_l2_data(self, sample_size: int = None) -> bool:
        """Load and process L2 database with optional sampling for faster testing"""
        print("=" * 70)
        print("PRODUCTION ENHANCED L2 SALES REPORT GENERATOR")
        print("=" * 70)

        try:
            # Load L2 data with optional sampling
            print("Loading L2 data...")
            self.l2_processor.load_data(sample_size=sample_size)
            print("Calculating priority scores...")
            self.l2_processor.calculate_priority_scores()
            print("Aggregating Happy Blocks...")
            happy_blocks_df = self.l2_processor.aggregate_happy_blocks()

            # Get processed Happy Blocks and convert to dictionary format
            print("Converting to dictionary format...")
            self.happy_blocks_data = self._convert_df_to_happy_blocks_dict(happy_blocks_df)

            print(f"Processed {len(self.happy_blocks_data):,} Happy Blocks")
            return True

        except Exception as e:
            print(f"Error processing L2 data: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _convert_df_to_happy_blocks_dict(self, happy_blocks_df: pd.DataFrame) -> Dict:
        """Convert Happy Blocks DataFrame to dictionary format for processing"""
        happy_blocks = {}

        # Group by Happy_Block to handle multiple villages per block
        grouped = happy_blocks_df.groupby('Happy_Block')

        for hb_id, group in grouped:
            # Aggregate data for this Happy Block
            total_l2s = group['L2_Count'].sum()
            total_ports = group['Total_Ports_Available'].sum()
            avg_priority = group['Priority_Score'].mean()

            # Get unique villages
            villages = group['Village_Name'].unique()
            village_names = ', '.join([str(v) for v in villages if str(v) != 'nan'])

            # Use first row for coordinates and location info
            first_row = group.iloc[0]

            # Get L2 details for this Happy Block
            l2_details = self.l2_processor.df[
                self.l2_processor.df['happy_block'] == hb_id
            ].to_dict('records')

            happy_blocks[hb_id] = {
                'happy_block': hb_id,
                'village_names': village_names,
                'lat_hb': first_row['Latitude'],
                'long_hb': first_row['Longitude'],
                'l2_count': total_l2s,
                'total_available_ports': total_ports,
                'top_priority_score': avg_priority,
                'overall_priority': first_row['Priority_Label'],
                'province': first_row['Province'],
                'district': first_row['District'],
                'subdistrict': first_row['Subdistrict'],
                'location_type': first_row['Location_Type'],
                'l2_details': l2_details
            }

        return happy_blocks

    def process_poi_and_timing_analysis(self, limit: int = None) -> List[Dict]:
        """Process POI discovery and smart timing analysis for Happy Blocks"""
        print(f"\nProcessing POI and Smart Timing Analysis...")

        # Get top priority Happy Blocks
        sorted_blocks = sorted(
            self.happy_blocks_data.values(),
            key=lambda x: x['top_priority_score'],
            reverse=True
        )
        top_blocks = sorted_blocks[:limit or 50]
        processed_count = 0
        success_count = 0

        enhanced_blocks = []

        for block_data in top_blocks:
            try:
                processed_count += 1
                happy_block_id = block_data['happy_block']

                print(f"  Processing {processed_count}/{len(top_blocks)}: {happy_block_id}")

                # Step 1: POI Analysis
                poi_result = self.poi_agent.process_happy_block_poi_analysis(block_data)

                # Step 2: Smart Timing Analysis (POI-aware defaults)
                timing_info = self._get_smart_timing_analysis(poi_result)

                # Combine all data
                enhanced_block = {
                    **poi_result,
                    **timing_info,
                    'processing_status': 'success'
                }

                enhanced_blocks.append(enhanced_block)
                success_count += 1

            except Exception as e:
                print(f"    Error processing {happy_block_id}: {e}")
                # Add error record
                error_block = {
                    **block_data,
                    'poi_name': '',
                    'poi_remark': f'Processing error: {str(e)[:50]}',
                    'timing_weekday': '',
                    'timing_weekend': '',
                    'processing_status': 'error'
                }
                enhanced_blocks.append(error_block)
                continue

        print(f"Processed {processed_count} Happy Blocks")
        print(f"   Success: {success_count}, Errors: {processed_count - success_count}")

        return enhanced_blocks

    def _get_smart_timing_analysis(self, poi_block_data: Dict) -> Dict:
        """Get smart timing analysis based on POI type and confidence"""

        poi_name = poi_block_data.get('poi_name', '')
        poi_confidence = poi_block_data.get('poi_confidence', 'NONE')

        # Smart timing based on POI type and confidence
        if not poi_name:
            # No POI found - use conservative default
            return {
                'timing_weekday': '16:00, 17:00, 18:00',
                'timing_weekend': '17:00, 18:00, 19:00',
                'best_day': 'Wednesday',
                'activity_level': 'Medium',
                'timing_status': 'default_no_poi'
            }

        # Analyze POI type for timing patterns (focus on community stores)
        poi_upper = poi_name.upper()

        # Community convenience stores timing
        if any(brand in poi_upper for brand in ['7-ELEVEN', 'เซเว่น', 'SEVEN', 'SEVEN-ELEVEN']):
            # 7-Eleven: Peak after work hours
            timing_data = {
                'timing_weekday': '16:00, 17:00, 18:00',
                'timing_weekend': '17:00, 18:00, 19:00',
                'best_day': 'Tuesday',
                'activity_level': 'High' if poi_confidence == 'HIGH' else 'Medium',
                'timing_status': 'smart_7eleven'
            }
        elif any(brand in poi_upper for brand in ['FAMILY', 'LOTUS GO', 'LOTUS EXPRESS', 'LOTUS MINI', 'CP', 'FRESHMART']):
            # Other convenience stores: Similar but slightly later
            timing_data = {
                'timing_weekday': '16:30, 17:30, 18:30',
                'timing_weekend': '17:30, 18:30, 19:30',
                'best_day': 'Wednesday',
                'activity_level': 'High' if poi_confidence == 'HIGH' else 'Medium',
                'timing_status': 'smart_convenience'
            }
        elif any(brand in poi_upper for brand in ['BIG C GO', 'BIG C MINI', 'MINI MART', 'MINIMART', '108']):
            # Supermarkets: Weekend peak, different weekday pattern
            timing_data = {
                'timing_weekday': '17:00, 18:00, 19:00',
                'timing_weekend': '16:00, 17:00, 18:00',
                'best_day': 'Saturday',
                'activity_level': 'Medium',
                'timing_status': 'smart_community_store'
            }
        else:
            # Unknown POI type: Conservative default
            timing_data = {
                'timing_weekday': '16:00, 17:00, 18:00',
                'timing_weekend': '17:00, 18:00, 19:00',
                'best_day': 'Wednesday',
                'activity_level': 'Medium',
                'timing_status': 'smart_unknown'
            }

        # Adjust for confidence level
        if poi_confidence == 'LOW':
            timing_data['activity_level'] = 'Medium'
        elif poi_confidence == 'HIGH':
            timing_data['activity_level'] = 'High'

        return timing_data

    def generate_dual_level_report(self, enhanced_blocks: List[Dict], output_path: str):
        """Generate dual-level CSV report (OVERVIEW + DETAIL)"""
        print(f"\nGenerating Production Sales Report...")

        overview_rows = []
        detail_rows = []

        for block in enhanced_blocks:
            try:
                # OVERVIEW Row: Happy Block summary
                overview_row = {
                    'Level': 'OVERVIEW',
                    'Happy_Block': block['happy_block'],
                    'Village_Name': block['village_names'],
                    'L2_Count': block['l2_count'],
                    'Priority_Score': block['top_priority_score'],
                    'Priority_Label': block['overall_priority'],
                    'Ports_Available': block['total_available_ports'],
                    'Installation_Status': self._get_dominant_installation_status(block),
                    'POI_Name': block.get('poi_name', 'No POI found'),
                    'POI_Address': block.get('poi_address', ''),
                    'Timing_Weekday': block.get('timing_weekday', ''),
                    'Timing_Weekend': block.get('timing_weekend', ''),
                    'Best_Day': block.get('best_day', ''),
                    'Activity_Level': block.get('activity_level', ''),
                    'Province': block.get('province', ''),
                    'District': block.get('district', ''),
                    'Subdistrict': block.get('subdistrict', ''),
                    'Location_Type': block.get('location_type', ''),
                    'Google_Maps': f"https://maps.google.com/?q={block['lat_hb']},{block['long_hb']}",
                    'Coverage_Notes': f"{block['l2_count']} L2 coverage points",
                    'Recommendations': self._generate_overview_recommendation(block),
                    'POI_Remark': block.get('poi_remark', ''),
                    'Timing_Status': block.get('timing_status', '')
                }
                overview_rows.append(overview_row)

                # DETAIL Rows: Each L2 in the Happy Block
                l2_details = block.get('l2_details', [])
                for l2 in l2_details:
                    detail_row = {
                        'Level': 'DETAIL',
                        'Happy_Block': block['happy_block'],
                        'Village_Name': l2.get('Rollout Location name', ''),
                        'L2_Name': l2.get('splt_l2', ''),
                        'L2_Count': '',  # Not applicable for detail
                        'Priority_Score': l2.get('priority_score', 0),
                        'Priority_Label': l2.get('priority_label', ''),
                        'Ports_Available': l2.get('sum_tol_avail', 0),
                        'Installation_Status': l2.get('installation_status', ''),
                        'POI_Name': '',  # Populated in overview only
                        'POI_Address': '',
                        'Timing_Weekday': '',
                        'Timing_Weekend': '',
                        'Best_Day': '',
                        'Activity_Level': '',
                        'Province': '',
                        'District': '',
                        'Subdistrict': '',
                        'Location_Type': '',
                        'Google_Maps': f"https://maps.google.com/?q={l2.get('latitude', 0)},{l2.get('longitude', 0)}",
                        'Coverage_Notes': f"L2 utilization: {l2.get('percent_utilization', 0):.1f}%, {l2.get('inservice_aging', 0):.0f} days old",
                        'Recommendations': self._generate_l2_recommendation(l2),
                        'POI_Remark': '',
                        'Timing_Status': ''
                    }
                    detail_rows.append(detail_row)

            except Exception as e:
                print(f"    Error generating report for {block.get('happy_block', 'Unknown')}: {e}")
                continue

        # Combine and sort all rows
        all_rows = overview_rows + detail_rows

        # Create DataFrame and export
        df = pd.DataFrame(all_rows)
        df.to_csv(output_path, index=False, encoding='utf-8-sig')

        print(f"Generated production report: {output_path}")
        print(f"   Overview rows: {len(overview_rows):,}")
        print(f"   Detail rows: {len(detail_rows):,}")
        print(f"   Total rows: {len(all_rows):,}")

        return output_path

    def _get_dominant_installation_status(self, block: Dict) -> str:
        """Get dominant installation status for Happy Block"""
        l2_details = block.get('l2_details', [])
        if not l2_details:
            return 'Unknown'

        # Count status occurrences
        status_counts = {}
        for l2 in l2_details:
            status = l2.get('installation_status', 'Unknown')
            status_counts[status] = status_counts.get(status, 0) + 1

        # Return most common status
        return max(status_counts, key=status_counts.get)

    def _generate_overview_recommendation(self, block: Dict) -> str:
        """Generate recommendation for Happy Block overview"""
        priority = block.get('overall_priority', 'LOW')
        l2_count = block.get('l2_count', 0)
        ports = block.get('total_available_ports', 0)
        status = self._get_dominant_installation_status(block)

        if priority == 'VERY_HIGH':
            return f"URGENT - {priority} priority, {status} installation"
        elif priority == 'HIGH':
            return f"High priority area - {l2_count} L2s, {ports} ports available"
        elif l2_count > 3:
            return f"Multi-L2 coverage area - {l2_count} L2s, {status} installation"
        else:
            return f"Standard coverage - {l2_count} L2s, {status} installation"

    def _generate_l2_recommendation(self, l2: Dict) -> str:
        """Generate recommendation for specific L2"""
        ports = l2.get('sum_tol_avail', 0)
        total_ports = l2.get('sum_tol_port', 1)
        status = l2.get('installation_status', 'Unknown')
        aging = l2.get('inservice_aging', 0)

        if aging <= 180:  # New installation
            return f"L2-specific: {ports} ports available, {status} installation - URGENT"
        elif ports >= 5:
            return f"L2-specific: {ports} ports available, high capacity"
        else:
            return f"L2-specific: {ports}/{total_ports} ports available, {status} installation"

def main():
    """Main execution function"""
    import argparse

    parser = argparse.ArgumentParser(description='Generate Production Enhanced L2 Sales Report')
    parser.add_argument('--limit', type=int, default=20, help='Number of Happy Blocks to process')
    parser.add_argument('--sample', type=int, help='Sample size of L2 records to load (for faster testing)')
    parser.add_argument('--output', type=str, help='Output CSV path')

    args = parser.parse_args()

    # Set default output path
    if not args.output:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        args.output = f"production_enhanced_l2_report_{timestamp}.csv"

    # Initialize generator
    l2_csv_path = "data/South L2 Ports Utilization on W25036_20250905.csv"
    generator = ProductionEnhancedReportGenerator(l2_csv_path)

    # Process data
    if not generator.load_and_process_l2_data(sample_size=args.sample):
        print("Failed to load L2 data")
        return

    # Process POI and timing
    enhanced_blocks = generator.process_poi_and_timing_analysis(limit=args.limit)

    # Generate report
    output_path = generator.generate_dual_level_report(enhanced_blocks, args.output)

    print(f"\nPRODUCTION SALES REPORT READY!")
    print(f"File: {output_path}")
    print(f"Happy Blocks processed: {len(enhanced_blocks)}")
    print(f"Ready for sales team!")

if __name__ == "__main__":
    main()