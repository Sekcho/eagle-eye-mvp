"""
Enhanced L2 Sales Report Generator with Dual-Level Structure
Generates OVERVIEW + DETAIL reports for sales team with Happy Block precision
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
import datasources.besttime_client as besttime_client

class EnhancedL2SalesReportGenerator:
    """Generate enhanced sales reports with L2 infrastructure and timing data"""

    def __init__(self, l2_csv_path: str):
        """Initialize enhanced report generator"""
        self.l2_csv_path = l2_csv_path
        self.l2_processor = L2DatabaseProcessor(l2_csv_path)
        self.poi_agent = EnhancedPOIAgent()
        self.besttime_client = besttime_client

        self.happy_blocks_data = {}
        self.timing_data = {}

    def load_and_process_l2_data(self) -> bool:
        """Load and process L2 database"""
        print("=" * 70)
        print("ENHANCED L2 SALES REPORT GENERATOR")
        print("=" * 70)

        try:
            # Load L2 data
            self.l2_processor.load_data()
            self.l2_processor.calculate_priority_scores()
            happy_blocks_df = self.l2_processor.aggregate_happy_blocks()

            # Get processed Happy Blocks and convert to dictionary format
            self.happy_blocks_data = self._convert_df_to_happy_blocks_dict(happy_blocks_df)

            print(f"Processed {len(self.happy_blocks_data):,} Happy Blocks")
            return True

        except Exception as e:
            print(f"Error processing L2 data: {e}")
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

    def process_poi_and_timing_analysis(self, limit: int = None) -> Dict:
        """Process POI discovery and timing analysis for Happy Blocks"""
        print(f"\nProcessing POI and Timing Analysis...")

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

                # Step 2: Timing Analysis (if POI found)
                timing_info = self._get_timing_analysis(poi_result)

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

    def _get_timing_analysis(self, poi_block_data: Dict) -> Dict:
        """Get timing analysis for POI"""
        default_timing = {
            'timing_weekday': '16:00, 17:00, 18:00',
            'timing_weekend': '17:00, 18:00, 19:00',
            'best_day': 'Wednesday',
            'activity_level': 'Medium',
            'timing_status': 'default'
        }

        poi_name = poi_block_data.get('poi_name', '')
        poi_address = poi_block_data.get('poi_address', '')

        if not poi_name:
            return {
                **default_timing,
                'timing_status': 'no_poi'
            }

        try:
            # Use BestTime client for timing analysis with real API
            print(f"    Querying BestTime for: {poi_name}")
            timing_result = self.besttime_client.query_venue_week(poi_name, poi_address, 0, 0)

            if timing_result and 'analysis' in timing_result:
                analysis = timing_result['analysis']

                # Extract peak hours from BestTime response
                weekday_peaks = self._extract_peak_hours(analysis, 'weekday')
                weekend_peaks = self._extract_peak_hours(analysis, 'weekend')

                # Determine best day and activity level
                best_day = self._get_best_day(analysis)
                activity_level = self._get_activity_level(analysis)

                return {
                    'timing_weekday': ', '.join([f"{h:02d}:00" for h in weekday_peaks]),
                    'timing_weekend': ', '.join([f"{h:02d}:00" for h in weekend_peaks]),
                    'best_day': best_day,
                    'activity_level': activity_level,
                    'timing_status': 'besttime_success'
                }
            else:
                print(f"    BestTime API returned no analysis data")
                return {
                    **default_timing,
                    'timing_status': 'besttime_no_data'
                }

        except Exception as e:
            print(f"    Timing analysis error: {e}")
            return {
                **default_timing,
                'timing_status': 'timing_error'
            }

    def _extract_peak_hours(self, analysis: Dict, day_type: str) -> List[int]:
        """Extract peak hours from BestTime analysis"""
        try:
            if day_type == 'weekday':
                # Average Monday-Friday data
                days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
            else:
                # Weekend data
                days = ['Saturday', 'Sunday']

            all_hours = {}
            for day in days:
                if day in analysis:
                    day_data = analysis[day]
                    for hour_str, busy_percent in day_data.items():
                        try:
                            hour = int(hour_str)
                            if 6 <= hour <= 22:  # Business hours only
                                all_hours[hour] = all_hours.get(hour, 0) + busy_percent
                        except (ValueError, TypeError):
                            continue

            if not all_hours:
                # Fallback to default
                return [16, 17, 18] if day_type == 'weekday' else [17, 18, 19]

            # Average and get top 3 hours
            avg_hours = {h: pct/len(days) for h, pct in all_hours.items()}
            sorted_hours = sorted(avg_hours.items(), key=lambda x: x[1], reverse=True)

            # Return top 3 peak hours
            peak_hours = [hour for hour, _ in sorted_hours[:3]]
            return sorted(peak_hours)

        except Exception as e:
            print(f"    Error extracting peak hours: {e}")
            return [16, 17, 18] if day_type == 'weekday' else [17, 18, 19]

    def _get_best_day(self, analysis: Dict) -> str:
        """Determine best day from BestTime analysis"""
        try:
            day_scores = {}

            for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
                if day in analysis:
                    day_data = analysis[day]
                    # Calculate average busyness during business hours (16-20)
                    business_hours = [16, 17, 18, 19, 20]
                    total_busy = 0
                    count = 0

                    for hour in business_hours:
                        if str(hour) in day_data:
                            total_busy += day_data[str(hour)]
                            count += 1

                    if count > 0:
                        day_scores[day] = total_busy / count

            if day_scores:
                best_day = max(day_scores, key=day_scores.get)
                return best_day
            else:
                return 'Wednesday'  # Default

        except Exception as e:
            print(f"    Error determining best day: {e}")
            return 'Wednesday'

    def _get_activity_level(self, analysis: Dict) -> str:
        """Determine activity level from BestTime analysis"""
        try:
            total_busyness = 0
            total_hours = 0

            for day in analysis.values():
                if isinstance(day, dict):
                    for hour_str, busy_percent in day.items():
                        try:
                            hour = int(hour_str)
                            if 6 <= hour <= 22:  # Business hours
                                total_busyness += busy_percent
                                total_hours += 1
                        except (ValueError, TypeError):
                            continue

            if total_hours == 0:
                return 'Medium'

            avg_busyness = total_busyness / total_hours

            if avg_busyness >= 75:
                return 'Very High'
            elif avg_busyness >= 60:
                return 'High'
            elif avg_busyness >= 40:
                return 'Medium'
            else:
                return 'Low'

        except Exception as e:
            print(f"    Error determining activity level: {e}")
            return 'Medium'

    def generate_dual_level_report(self, enhanced_blocks: List[Dict], output_path: str):
        """Generate dual-level CSV report (OVERVIEW + DETAIL)"""
        print(f"\nGenerating Dual-Level Sales Report...")

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
                    'Recommendations': self._generate_overview_recommendation(block)
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
                        'Recommendations': self._generate_l2_recommendation(l2)
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

        print(f"Generated dual-level report: {output_path}")
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

        if priority == 'HIGH':
            return f"High priority area - {priority} priority, {status} installation"
        elif l2_count > 3:
            return f"Multi-L2 coverage area - {l2_count} L2s, {ports} total ports"
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

    parser = argparse.ArgumentParser(description='Generate Enhanced L2 Sales Report')
    parser.add_argument('--limit', type=int, default=20, help='Number of Happy Blocks to process')
    parser.add_argument('--output', type=str, help='Output CSV path')

    args = parser.parse_args()

    # Set default output path
    if not args.output:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        args.output = f"enhanced_l2_sales_report_{timestamp}.csv"

    # Initialize generator
    l2_csv_path = "data/South L2 Ports Utilization on W25036_20250905.csv"
    generator = EnhancedL2SalesReportGenerator(l2_csv_path)

    # Process data
    if not generator.load_and_process_l2_data():
        print("Failed to load L2 data")
        return

    # Process POI and timing
    enhanced_blocks = generator.process_poi_and_timing_analysis(limit=args.limit)

    # Generate report
    output_path = generator.generate_dual_level_report(enhanced_blocks, args.output)

    print(f"\nSALES REPORT READY!")
    print(f"File: {output_path}")
    print(f"Happy Blocks processed: {len(enhanced_blocks)}")
    print(f"Ready for sales team!")

if __name__ == "__main__":
    main()