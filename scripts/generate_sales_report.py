#!/usr/bin/env python3
"""
Sales Report Generator - Create actionable timing reports for sales teams
"""

import os
import sys
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.io.gsheets import GoogleSheetsClient

def generate_sales_report():
    """Generate a sales-friendly report with timing recommendations"""

    load_dotenv()

    # Read data from CSV files (Google Sheets disabled)
    try:
        client = GoogleSheetsClient()
        data = client.read_sheet("CSV_BASED_SYSTEM", "master_village_data")
        print(f"OK: อ่านข้อมูลจาก CSV: {len(data)} หมู่บ้าน")
    except Exception as e:
        print(f"ERROR: ไม่สามารถอ่าน CSV: {e}")
        raise

    # Filter villages with POI data (must have actual POI name, not empty/NaN)
    villages_with_real_poi = data[
        (data['Indicator_POI'].notna()) &
        (data['Indicator_POI'].str.strip() != '') &
        (data['Indicator_POI'] != 'No POI found')
    ]

    # Filter for villages that also have timing data (not default values)
    if 'Residential_Peak_Weekday' in villages_with_real_poi.columns:
        villages_with_timing = villages_with_real_poi[
            (villages_with_real_poi['Residential_Peak_Weekday'].notna()) &
            (villages_with_real_poi['Residential_Peak_Weekday'] != '16:00, 17:00, 18:00')
        ]
    else:
        villages_with_timing = pd.DataFrame()  # Empty if no timing column

    print(f"\nสรุปข้อมูล:")
    print(f"   หมู่บ้านทั้งหมด: {len(data):,}")
    print(f"   หมู่บ้านที่มี POI จริง: {len(villages_with_real_poi):,}")
    print(f"   หมู่บ้านที่มีข้อมูล timing จริง: {len(villages_with_timing):,}")
    print(f"   Coverage: {len(villages_with_real_poi)/len(data)*100:.1f}%")

    if len(villages_with_real_poi) == 0:
        print("\nWARNING: ยังไม่มีข้อมูล POI สำหรับหมู่บ้านใดๆ")
        print("   กรุณารัน Agent 2 เพื่อหาข้อมูล POI ก่อน")
        return

    # Use villages with real POI data for the report
    villages_with_poi = villages_with_real_poi

    # Generate sales report
    report_data = []

    # Import Google Maps client to get POI coordinates
    from app.datasources.gmaps_client import GoogleMapsClient

    for _, village in villages_with_poi.iterrows():
        # Get timing data (if available) or use default recommendations
        weekday_times = village.get('Residential_Peak_Weekday', '16:00, 17:00, 18:00')
        weekend_times = village.get('Residential_Peak_Weekend', '17:00, 16:00, 18:00')
        best_day = village.get('Best_Sales_Day', 'Wednesday')
        activity_level = village.get('Residential_Activity', 'Medium')

        # Use village coordinates for door-to-door sales (not store coordinates)
        village_lat = village.get('Latitude', '')
        village_lng = village.get('Longitude', '')

        report_row = {
            'หมู่บ้าน': village.get('Village_Name', ''),
            'ตำบล': village.get('Sub_District', ''),
            'อำเภอ': village.get('District', ''),
            'จังหวัด': village.get('Province', ''),
            'พิกัด_Lat': village_lat,
            'พิกัด_Lng': village_lng,
            'ร้านอ้างอิง': village.get('Indicator_POI', ''),
            'ระยะห่างร้าน_km': 'ใกล้หมู่บ้าน',  # จาก Agent 2 analysis
            'เวลาดี_วันธรรมดา': weekday_times,
            'เวลาดี_วันหยุด': weekend_times,
            'วันที่แนะนำ': best_day,
            'ระดับกิจกรรม': activity_level,
            'Google_Maps': f"https://maps.google.com/?q={village_lat},{village_lng}",
            'คำแนะนำ': 'ใช้พิกัดนี้เพื่อไปยังจุดกลางหมู่บ้าน แล้วเดินขายไปทีละบ้าน'
        }
        report_data.append(report_row)

    # Create DataFrame
    report_df = pd.DataFrame(report_data)

    # Save to CSV
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    filename = f"sales_timing_report_{timestamp}.csv"
    report_df.to_csv(filename, index=False, encoding='utf-8-sig')

    print(f"\nOK: สร้างรายงานเสร็จแล้ว: {filename}")
    print(f"   จำนวนหมู่บ้าน: {len(report_df)}")

    # Show sample data
    print(f"\nตัวอย่างรายงาน (5 หมู่บ้านแรก):")
    print("=" * 100)

    for i, (_, row) in enumerate(report_df.head(5).iterrows(), 1):
        print(f"{i:2d}. หมู่บ้าน: {row['หมู่บ้าน']}")
        print(f"    ที่ตั้ง: {row['ตำบล']}, {row['อำเภอ']}, {row['จังหวัด']}")
        print(f"    ร้านอ้างอิง: {row['ร้านอ้างอิง']} ({row['ระยะห่างร้าน_km']})")
        print(f"    เวลาดี (จ-ศ): {row['เวลาดี_วันธรรมดา']}")
        print(f"    เวลาดี (ส-อา): {row['เวลาดี_วันหยุด']}")
        print(f"    วันที่แนะนำ: {row['วันที่แนะนำ']}")
        print(f"    ระดับกิจกรรม: {row['ระดับกิจกรรม']}")
        print(f"    พิกัดหมู่บ้าน: {row['พิกัด_Lat']}, {row['พิกัด_Lng']}")
        print(f"    Google Maps: {row['Google_Maps']}")
        print(f"    หมายเหตุ: {row['คำแนะนำ']}")
        print()

    print(f"ไฟล์รายงาน: {filename}")
    print("สามารถเปิดด้วย Excel หรือ Google Sheets")

    return filename

if __name__ == "__main__":
    generate_sales_report()