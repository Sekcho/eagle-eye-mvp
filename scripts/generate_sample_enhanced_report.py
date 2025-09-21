"""
Generate Sample Enhanced L2 Sales Report
Creates a demo report to show the dual-level structure
"""

import pandas as pd
from datetime import datetime

def generate_sample_enhanced_report():
    """Generate sample enhanced report with dual-level structure"""

    print("Generating Sample Enhanced L2 Sales Report...")

    # Sample data based on real L2 structure
    sample_data = [
        # OVERVIEW Rows (Happy Block summaries)
        {
            'Level': 'OVERVIEW',
            'Happy_Block': '09320-099700',
            'Village_Name': 'ชลคราม, บ้านดอนสัก',
            'L2_Count': 3,
            'Priority_Score': 85.2,
            'Priority_Label': 'VERY_HIGH',
            'Ports_Available': 15,
            'Installation_Status': 'New',
            'POI_Name': '7-Eleven สาขา ดอนสัก (17957)',
            'POI_Address': '8M7V+J5M, Don Sak, Don Sak District',
            'Timing_Weekday': '16:00, 17:00, 18:00',
            'Timing_Weekend': '17:00, 18:00, 19:00',
            'Best_Day': 'Wednesday',
            'Activity_Level': 'High',
            'Province': 'สุราษฎร์ธานี',
            'District': 'ดอนสัก',
            'Subdistrict': 'ดอนสัก',
            'Location_Type': 'ชุมชน',
            'Google_Maps': 'https://maps.google.com/?q=9.3175,99.7025',
            'Coverage_Notes': '3 L2 coverage points',
            'Recommendations': 'High priority area - VERY_HIGH priority, New installation'
        },

        # DETAIL Rows (Individual L2s in the Happy Block)
        {
            'Level': 'DETAIL',
            'Happy_Block': '09320-099700',
            'Village_Name': 'ชลคราม',
            'L2_Name': 'SRT03X30B0E',
            'L2_Count': '',
            'Priority_Score': 100.0,
            'Priority_Label': 'VERY_HIGH',
            'Ports_Available': 8,
            'Installation_Status': 'New',
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
            'Google_Maps': 'https://maps.google.com/?q=9.315526,99.7006599',
            'Coverage_Notes': 'L2 utilization: 37.5%, 120 days old',
            'Recommendations': 'L2-specific: 8 ports available, New installation - URGENT'
        },

        {
            'Level': 'DETAIL',
            'Happy_Block': '09320-099700',
            'Village_Name': 'ชลคราม',
            'L2_Name': 'SRT03X30B0D',
            'L2_Count': '',
            'Priority_Score': 75.4,
            'Priority_Label': 'HIGH',
            'Ports_Available': 5,
            'Installation_Status': 'New',
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
            'Google_Maps': 'https://maps.google.com/?q=9.31376399,99.7067199',
            'Coverage_Notes': 'L2 utilization: 75.0%, 120 days old',
            'Recommendations': 'L2-specific: 5 ports available, New installation'
        },

        {
            'Level': 'DETAIL',
            'Happy_Block': '09320-099700',
            'Village_Name': 'บ้านดอนสัก',
            'L2_Name': 'SRT03X30B0C',
            'L2_Count': '',
            'Priority_Score': 82.1,
            'Priority_Label': 'VERY_HIGH',
            'Ports_Available': 2,
            'Installation_Status': 'New',
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
            'Google_Maps': 'https://maps.google.com/?q=9.314521,99.7045123',
            'Coverage_Notes': 'L2 utilization: 88.9%, 120 days old',
            'Recommendations': 'L2-specific: 2 ports available, New installation'
        },

        # Second Happy Block
        {
            'Level': 'OVERVIEW',
            'Happy_Block': '09315-099705',
            'Village_Name': 'ชลคราม, บ้านบางน้ำจืด',
            'L2_Count': 2,
            'Priority_Score': 72.8,
            'Priority_Label': 'HIGH',
            'Ports_Available': 12,
            'Installation_Status': 'Medium',
            'POI_Name': 'Big C สาขา ดอนสัก',
            'POI_Address': 'No POI (nearby happyblock: 09315-099700, distance: 0.5km)',
            'Timing_Weekday': '15:00, 16:00, 18:00',
            'Timing_Weekend': '16:00, 17:00, 19:00',
            'Best_Day': 'Thursday',
            'Activity_Level': 'Medium',
            'Province': 'สุราษฎร์ธานี',
            'District': 'ดอนสัก',
            'Subdistrict': 'ดอนสัก',
            'Location_Type': 'ชุมชน',
            'Google_Maps': 'https://maps.google.com/?q=9.3125,99.7075',
            'Coverage_Notes': '2 L2 coverage points',
            'Recommendations': 'Multi-L2 coverage area - 2 L2s, Medium installation'
        },

        {
            'Level': 'DETAIL',
            'Happy_Block': '09315-099705',
            'Village_Name': 'ชลคราม',
            'L2_Name': 'SRT03X30B0F',
            'L2_Count': '',
            'Priority_Score': 68.5,
            'Priority_Label': 'HIGH',
            'Ports_Available': 7,
            'Installation_Status': 'Medium',
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
            'Google_Maps': 'https://maps.google.com/?q=9.3135796,99.688613',
            'Coverage_Notes': 'L2 utilization: 62.5%, 280 days old',
            'Recommendations': 'L2-specific: 7 ports available, Medium installation'
        },

        {
            'Level': 'DETAIL',
            'Happy_Block': '09315-099705',
            'Village_Name': 'บ้านบางน้ำจืด',
            'L2_Name': 'SRT03X36NDB',
            'L2_Count': '',
            'Priority_Score': 77.1,
            'Priority_Label': 'HIGH',
            'Ports_Available': 5,
            'Installation_Status': 'Medium',
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
            'Google_Maps': 'https://maps.google.com/?q=9.313988,99.7110399',
            'Coverage_Notes': 'L2 utilization: 58.3%, 245 days old',
            'Recommendations': 'L2-specific: 5 ports available, Medium installation'
        }
    ]

    # Create DataFrame
    df = pd.DataFrame(sample_data)

    # Generate timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    output_path = f"sample_enhanced_l2_report_{timestamp}.csv"

    # Export to CSV
    df.to_csv(output_path, index=False, encoding='utf-8-sig')

    print(f"Generated sample report: {output_path}")
    print(f"Overview rows: {len(df[df['Level'] == 'OVERVIEW'])}")
    print(f"Detail rows: {len(df[df['Level'] == 'DETAIL'])}")
    print(f"Total rows: {len(df)}")

    # Display sample data
    print(f"\nSample OVERVIEW data:")
    overview_sample = df[df['Level'] == 'OVERVIEW'].iloc[0]
    print(f"Happy Block: {overview_sample['Happy_Block']}")
    print(f"Village: {overview_sample['Village_Name']}")
    print(f"Priority: {overview_sample['Priority_Score']} ({overview_sample['Priority_Label']})")
    print(f"Ports Available: {overview_sample['Ports_Available']}")
    print(f"POI: {overview_sample['POI_Name']}")
    print(f"Best Times: {overview_sample['Timing_Weekday']}")

    print(f"\nSample DETAIL data:")
    detail_sample = df[df['Level'] == 'DETAIL'].iloc[0]
    print(f"L2 Name: {detail_sample['L2_Name']}")
    print(f"Priority: {detail_sample['Priority_Score']} ({detail_sample['Priority_Label']})")
    print(f"Ports: {detail_sample['Ports_Available']}")
    print(f"Status: {detail_sample['Installation_Status']}")
    print(f"Recommendation: {detail_sample['Recommendations']}")

    return output_path

if __name__ == "__main__":
    output_file = generate_sample_enhanced_report()
    print(f"\nSample Enhanced L2 Sales Report ready!")
    print(f"File: {output_file}")
    print(f"This demonstrates the dual-level structure for sales teams.")