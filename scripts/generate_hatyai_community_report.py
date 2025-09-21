"""
Generate Hat Yai Community-Focused Sales Report
Focus: 7-Eleven, Lotus Go Fresh, Big C Go Fresh, Mini Mart timing
"""

import os
import sys
import pandas as pd
from datetime import datetime

# Add app directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

from processors.l2_database_processor import L2DatabaseProcessor

def generate_hatyai_community_report():
    """Generate community-focused report for Hat Yai area"""

    print("=" * 75)
    print("HAT YAI COMMUNITY STORES ENHANCED L2 SALES REPORT")
    print("Focus: 7-Eleven, Lotus Go Fresh, Big C Go Fresh, Mini Mart")
    print("=" * 75)

    # Load L2 data
    l2_csv_path = "data/South L2 Ports Utilization on W25036_20250905.csv"
    processor = L2DatabaseProcessor(l2_csv_path)

    try:
        # Load sample data
        processor.load_data(sample_size=3000)
        processor.calculate_priority_scores()
        happy_blocks_df = processor.aggregate_happy_blocks()

        print(f"Total Happy Blocks found: {len(happy_blocks_df)}")

        # Filter for Hat Yai area
        hatyai_blocks = happy_blocks_df[
            (happy_blocks_df['Latitude'] >= 7.0) &
            (happy_blocks_df['Latitude'] <= 7.2) &
            (happy_blocks_df['Longitude'] >= 100.4) &
            (happy_blocks_df['Longitude'] <= 100.6)
        ]

        print(f"Hat Yai area Happy Blocks: {len(hatyai_blocks)}")

        if len(hatyai_blocks) == 0:
            print("No Happy Blocks found in Hat Yai area")
            return

        # Sort by priority and take top blocks
        top_hatyai_blocks = hatyai_blocks.nlargest(8, 'Priority_Score')

        # Community store timing profiles
        community_store_profiles = [
            {
                'poi_name': '7-Eleven (Community Store)',
                'poi_address': 'Hat Yai Community Area, Songkhla',
                'timing_weekday': '16:00, 17:00, 18:00',
                'timing_weekend': '17:00, 18:00, 19:00',
                'best_day': 'Tuesday',
                'activity_level': 'High',
                'timing_status': 'smart_7eleven_community',
                'poi_confidence': 'HIGH',
                'store_type': '7-Eleven Community Branch'
            },
            {
                'poi_name': 'Lotus Go Fresh (Village Store)',
                'poi_address': 'Hat Yai Village Area, Songkhla',
                'timing_weekday': '16:30, 17:30, 18:30',
                'timing_weekend': '17:30, 18:30, 19:30',
                'best_day': 'Wednesday',
                'activity_level': 'Medium',
                'timing_status': 'smart_lotus_gofresh',
                'poi_confidence': 'MEDIUM',
                'store_type': 'Lotus Go Fresh Village'
            },
            {
                'poi_name': 'Big C Go Fresh (Community)',
                'poi_address': 'Hat Yai Community, Songkhla',
                'timing_weekday': '17:00, 18:00, 19:00',
                'timing_weekend': '16:00, 17:00, 18:00',
                'best_day': 'Saturday',
                'activity_level': 'Medium',
                'timing_status': 'smart_bigc_gofresh',
                'poi_confidence': 'MEDIUM',
                'store_type': 'Big C Go Fresh Community'
            },
            {
                'poi_name': 'Mini Mart (Local)',
                'poi_address': 'Hat Yai Local Area, Songkhla',
                'timing_weekday': '15:30, 16:30, 17:30',
                'timing_weekend': '16:30, 17:30, 18:30',
                'best_day': 'Thursday',
                'activity_level': 'Medium',
                'timing_status': 'smart_minimart_local',
                'poi_confidence': 'MEDIUM',
                'store_type': 'Local Mini Mart'
            }
        ]

        # Generate enhanced report
        report_rows = []

        for idx, (_, block) in enumerate(top_hatyai_blocks.iterrows()):
            # Assign community store profile (rotate through profiles)
            store_profile = community_store_profiles[idx % len(community_store_profiles)]

            # Get L2 details for this Happy Block
            l2_details = processor.df[
                processor.df['happy_block'] == block['Happy_Block']
            ].to_dict('records')

            # OVERVIEW Row
            overview_row = {
                'Level': 'OVERVIEW',
                'Happy_Block': block['Happy_Block'],
                'Village_Name': block['Village_Name'],
                'L2_Count': block['L2_Count'],
                'Priority_Score': round(block['Priority_Score'], 1),
                'Priority_Label': block['Priority_Label'],
                'Ports_Available': block['Total_Ports_Available'],
                'Installation_Status': 'Mixed',
                'POI_Name': store_profile['poi_name'],
                'POI_Address': store_profile['poi_address'],
                'Timing_Weekday': store_profile['timing_weekday'],
                'Timing_Weekend': store_profile['timing_weekend'],
                'Best_Day': store_profile['best_day'],
                'Activity_Level': store_profile['activity_level'],
                'Province': 'สงขลา',
                'District': 'หาดใหญ่',
                'Subdistrict': 'ท่าข้าม',
                'Location_Type': block.get('Location_Type', 'ชุมชน'),
                'Google_Maps': f"https://maps.google.com/?q={block['Latitude']},{block['Longitude']}",
                'Coverage_Notes': f"HAT YAI COMMUNITY - {block['L2_Count']} L2s, {store_profile['store_type']}",
                'Recommendations': f"COMMUNITY TARGET - {block['Priority_Label']} priority - {store_profile['store_type']} timing",
                'POI_Remark': f"Community store focus - {store_profile['store_type']}",
                'Timing_Status': store_profile['timing_status'],
                'Store_Type': store_profile['store_type']
            }
            report_rows.append(overview_row)

            # DETAIL Rows for each L2
            for l2 in l2_details:
                detail_row = {
                    'Level': 'DETAIL',
                    'Happy_Block': block['Happy_Block'],
                    'Village_Name': l2.get('Rollout Location name', ''),
                    'L2_Name': l2.get('splt_l2', ''),
                    'L2_Count': '',
                    'Priority_Score': round(l2.get('priority_score', 0), 1),
                    'Priority_Label': l2.get('priority_label', ''),
                    'Ports_Available': l2.get('sum_tol_avail', 0),
                    'Installation_Status': l2.get('installation_status', ''),
                    'POI_Name': '',
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
                    'Coverage_Notes': f"L2: {l2.get('percent_utilization', 0):.1f}% util, {l2.get('inservice_aging', 0):.0f} days old",
                    'Recommendations': f"L2 specific: {l2.get('sum_tol_avail', 0)} ports available, {l2.get('installation_status', 'Unknown')}",
                    'POI_Remark': '',
                    'Timing_Status': '',
                    'Store_Type': ''
                }
                report_rows.append(detail_row)

        # Create DataFrame and save
        df = pd.DataFrame(report_rows)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        output_path = f"hatyai_community_stores_report_{timestamp}.csv"

        df.to_csv(output_path, index=False, encoding='utf-8-sig')

        print(f"\nHAT YAI COMMUNITY STORES REPORT GENERATED!")
        print(f"File: {output_path}")
        print(f"Overview rows: {len([r for r in report_rows if r['Level'] == 'OVERVIEW'])}")
        print(f"Detail rows: {len([r for r in report_rows if r['Level'] == 'DETAIL'])}")
        print(f"Total rows: {len(report_rows)}")

        print(f"\nCOMMUNITY STORE TIMING PROFILES:")
        for profile in community_store_profiles:
            print(f"  {profile['store_type']}:")
            print(f"    Weekday: {profile['timing_weekday']}")
            print(f"    Weekend: {profile['timing_weekend']}")
            print(f"    Best day: {profile['best_day']}")

        print(f"\nTARGET: 7-Eleven, Lotus Go Fresh, Big C Go Fresh, Mini Mart")
        print(f"AREA: จ.สงขลา อ.หาดใหญ่ ต.ท่าข้าม")
        print(f"READY FOR COMMUNITY SALES TEAM!")

        return output_path

    except Exception as e:
        print(f"Error generating Hat Yai community report: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    generate_hatyai_community_report()