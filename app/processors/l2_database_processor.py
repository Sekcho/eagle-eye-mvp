"""
Enhanced L2 Database Processor for Eagle Eye MVP
Processes L2 port utilization data with priority scoring and Happy Block aggregation
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple
import os


class L2DatabaseProcessor:
    """Process L2 database and create enhanced village/timing analysis"""

    def __init__(self, csv_path: str):
        self.csv_path = csv_path
        self.df = None
        self.happy_blocks_df = None

        # Priority scoring weights (40% ports, 60% aging urgency)
        self.PORT_WEIGHT = 0.4
        self.AGING_WEIGHT = 0.6

        # Installation status thresholds (days)
        self.NEW_THRESHOLD = 180      # <= 6 months
        self.MEDIUM_THRESHOLD = 365   # <= 12 months

        # Priority score ranges
        self.PRIORITY_RANGES = {
            'VERY_HIGH': (80, 100),
            'HIGH': (60, 80),
            'MEDIUM': (40, 60),
            'LOW': (20, 40),
            'VERY_LOW': (0, 20)
        }

    def load_data(self, sample_size: int = None) -> pd.DataFrame:
        """Load L2 database with optional sampling for faster processing"""
        print(f"Loading L2 database: {self.csv_path}")

        if not os.path.exists(self.csv_path):
            raise FileNotFoundError(f"L2 database not found: {self.csv_path}")

        # Load with sampling if specified
        if sample_size:
            print(f"Loading sample of {sample_size:,} rows for faster processing...")
            self.df = pd.read_csv(self.csv_path, low_memory=False, nrows=sample_size)
        else:
            self.df = pd.read_csv(self.csv_path, low_memory=False)

        print(f"Loaded {len(self.df):,} L2 records")

        # Clean and validate data
        self.df = self.df[
            (self.df['lat_happy_block'].notna()) &
            (self.df['long_happy_block'].notna()) &
            (self.df['Rollout Location name'].notna()) &
            (self.df['sum_tol_avail'].notna()) &
            (self.df['inservice_aging'].notna())
        ]

        print(f"After cleaning: {len(self.df):,} valid L2 records")
        return self.df

    def calculate_priority_score(self, row) -> float:
        """
        Calculate L2 priority score
        Formula: (Available_Ports * 0.4) + (Aging_Urgency * 0.6)
        """
        try:
            # Available Ports Score (40%)
            if row['sum_tol_port'] > 0:
                available_score = (row['sum_tol_avail'] / row['sum_tol_port']) * 40
            else:
                available_score = 0

            # Aging Urgency Score (60%)
            aging_days = row['inservice_aging']
            if pd.isna(aging_days):
                aging_score = 20 * 0.6  # Default to LOW
            elif aging_days <= 180:      # ≤6 months HIGH
                aging_score = 100 * 0.6
            elif aging_days <= 365:      # 6-12 months MEDIUM
                aging_score = 60 * 0.6
            else:                        # >12 months LOW
                aging_score = 20 * 0.6

            return round(available_score + aging_score, 1)

        except Exception as e:
            print(f"Error calculating priority for L2 {row.get('splt_l2', 'Unknown')}: {e}")
            return 0.0

    def calculate_priority_scores(self) -> pd.DataFrame:
        """Calculate priority scores for each L2"""
        print("Calculating priority scores...")

        # Apply new priority calculation
        self.df['priority_score'] = self.df.apply(self.calculate_priority_score, axis=1)

        # Add priority labels
        self.df['priority_label'] = self.df['priority_score'].apply(self._get_priority_label)

        # Add installation status
        self.df['installation_status'] = self.df['inservice_aging'].apply(self._get_installation_status)

        print(f"Priority scores calculated. Range: {self.df['priority_score'].min():.1f} - {self.df['priority_score'].max():.1f}")
        return self.df

    def aggregate_happy_blocks(self) -> pd.DataFrame:
        """Aggregate L2 data by Happy Block with Sales Zone support"""
        print("Aggregating data by Happy Block with Sales Zone approach...")

        # Group by Happy Block only (not by village to avoid splitting multi-village blocks)
        grouped = self.df.groupby(['happy_block']).agg({
            'splt_l2': 'count',                    # L2 count
            'sum_tol_avail': 'sum',               # Total ports available
            'tol_avail_by_hhb': 'first',          # Happy block total ports
            'priority_score': 'mean',             # Average priority score
            'inservice_aging': 'mean',            # Average aging
            'lat_happy_block': 'first',           # Happy block coordinates
            'long_happy_block': 'first',
            'Rollout Location name': 'first',    # Primary village name
            'Province': 'first',
            'District': 'first',
            'Subdistrict': 'first',
            'Location Type': 'first',
            'installation_status': lambda x: self._get_dominant_status(x),  # Dominant status
            'priority_label': lambda x: self._get_dominant_priority(x)       # Dominant priority
        }).round(1)

        # Rename columns
        grouped.columns = [
            'L2_Count', 'Total_Ports_Available', 'HHB_Ports_Available',
            'Priority_Score', 'Avg_Aging_Days', 'Latitude', 'Longitude',
            'Village_Name', 'Province', 'District', 'Subdistrict', 'Location_Type',
            'Installation_Status', 'Priority_Label'
        ]

        # Reset index to get happy_block as column
        grouped = grouped.reset_index()
        grouped = grouped[['happy_block', 'Village_Name', 'L2_Count', 'Total_Ports_Available',
                          'HHB_Ports_Available', 'Priority_Score', 'Avg_Aging_Days',
                          'Latitude', 'Longitude', 'Province', 'District', 'Subdistrict',
                          'Location_Type', 'Installation_Status', 'Priority_Label']]
        grouped.columns = ['Happy_Block'] + list(grouped.columns[1:])

        self.happy_blocks_df = grouped
        print(f"Created {len(grouped):,} Happy Block aggregations")
        return grouped

    def create_sales_zones(self) -> pd.DataFrame:
        """Create Sales Zones for multi-block villages"""
        print("Creating Sales Zones for multi-block villages...")

        if self.happy_blocks_df is None:
            raise ValueError("Must run aggregate_happy_blocks() first")

        # Identify multi-block villages (villages spanning multiple Happy Blocks)
        village_block_counts = self.happy_blocks_df.groupby('Village_Name')['Happy_Block'].count()
        multi_block_villages = village_block_counts[village_block_counts > 1].index.tolist()

        print(f"Found {len(multi_block_villages)} multi-block villages")

        # Create Sales Zone aggregation
        sales_zones = []

        for village in multi_block_villages:
            village_blocks = self.happy_blocks_df[self.happy_blocks_df['Village_Name'] == village]

            # Create Sales Zone ID (village name + block count)
            sales_zone_id = f"{village}_ZONE_{len(village_blocks)}BLOCKS"

            # Aggregate metrics across all Happy Blocks in this village
            total_l2_count = village_blocks['L2_Count'].sum()
            total_ports = village_blocks['Total_Ports_Available'].sum()
            total_hhb_ports = village_blocks['HHB_Ports_Available'].sum()
            avg_priority = village_blocks['Priority_Score'].mean()
            avg_aging = village_blocks['Avg_Aging_Days'].mean()

            # Get central coordinates (mean of all blocks)
            central_lat = village_blocks['Latitude'].mean()
            central_lng = village_blocks['Longitude'].mean()

            # Get location info from first block
            first_block = village_blocks.iloc[0]

            # Determine dominant status and priority
            dominant_status = self._get_dominant_status(village_blocks['Installation_Status'])
            dominant_priority = self._get_dominant_priority(village_blocks['Priority_Label'])

            sales_zone = {
                'Sales_Zone_ID': sales_zone_id,
                'Village_Name': village,
                'Happy_Block_Count': len(village_blocks),
                'Happy_Blocks': ', '.join(village_blocks['Happy_Block'].tolist()),
                'L2_Count': total_l2_count,
                'Total_Ports_Available': total_ports,
                'HHB_Ports_Available': total_hhb_ports,
                'Priority_Score': round(avg_priority, 1),
                'Priority_Label': dominant_priority,
                'Avg_Aging_Days': round(avg_aging, 1),
                'Installation_Status': dominant_status,
                'Central_Latitude': round(central_lat, 6),
                'Central_Longitude': round(central_lng, 6),
                'Province': first_block['Province'],
                'District': first_block['District'],
                'Subdistrict': first_block['Subdistrict'],
                'Location_Type': first_block['Location_Type']
            }
            sales_zones.append(sales_zone)

        sales_zones_df = pd.DataFrame(sales_zones)

        # Add single-block villages as individual sales zones
        single_block_villages = self.happy_blocks_df[
            ~self.happy_blocks_df['Village_Name'].isin(multi_block_villages)
        ].copy()

        if len(single_block_villages) > 0:
            single_block_villages['Sales_Zone_ID'] = single_block_villages['Village_Name'] + '_ZONE_1BLOCK'
            single_block_villages['Happy_Block_Count'] = 1
            single_block_villages['Happy_Blocks'] = single_block_villages['Happy_Block']
            single_block_villages['Central_Latitude'] = single_block_villages['Latitude']
            single_block_villages['Central_Longitude'] = single_block_villages['Longitude']

            # Reorder columns to match sales_zones_df
            single_zone_cols = [
                'Sales_Zone_ID', 'Village_Name', 'Happy_Block_Count', 'Happy_Blocks',
                'L2_Count', 'Total_Ports_Available', 'HHB_Ports_Available',
                'Priority_Score', 'Priority_Label', 'Avg_Aging_Days', 'Installation_Status',
                'Central_Latitude', 'Central_Longitude', 'Province', 'District',
                'Subdistrict', 'Location_Type'
            ]
            single_block_zones = single_block_villages[single_zone_cols]

            # Combine multi-block and single-block zones
            all_sales_zones = pd.concat([sales_zones_df, single_block_zones], ignore_index=True)
        else:
            all_sales_zones = sales_zones_df

        print(f"Created {len(all_sales_zones)} Sales Zones ({len(sales_zones_df)} multi-block, {len(single_block_villages)} single-block)")

        self.sales_zones_df = all_sales_zones
        return all_sales_zones

    def get_prioritized_sales_zones(self, top_n: int = None) -> pd.DataFrame:
        """Get Sales Zones sorted by priority score"""
        if not hasattr(self, 'sales_zones_df') or self.sales_zones_df is None:
            raise ValueError("Must run create_sales_zones() first")

        # Sort by priority score (descending)
        prioritized = self.sales_zones_df.sort_values('Priority_Score', ascending=False)

        if top_n:
            prioritized = prioritized.head(top_n)

        print(f"Returning {len(prioritized)} prioritized Sales Zones")
        return prioritized

    def get_prioritized_villages(self, top_n: int = None) -> pd.DataFrame:
        """Get villages sorted by priority score"""
        if self.happy_blocks_df is None:
            raise ValueError("Must run aggregate_happy_blocks() first")

        # Sort by priority score (descending)
        prioritized = self.happy_blocks_df.sort_values('Priority_Score', ascending=False)

        if top_n:
            prioritized = prioritized.head(top_n)

        print(f"Returning {len(prioritized)} prioritized villages")
        return prioritized

    def get_l2_details_for_village(self, village_name: str, happy_block: str = None) -> pd.DataFrame:
        """Get L2-level details for a specific village and happy block"""
        if happy_block:
            # Filter by both village and happy block
            village_l2s = self.df[
                (self.df['Rollout Location name'] == village_name) &
                (self.df['happy_block'] == happy_block)
            ].copy()
        else:
            # Legacy: filter by village only
            village_l2s = self.df[self.df['Rollout Location name'] == village_name].copy()

        if len(village_l2s) == 0:
            return pd.DataFrame()

        # Select relevant columns for L2 details
        l2_details = village_l2s[[
            'splt_l2', 'sum_tol_avail', 'sum_tol_port', 'sum_tol_act',
            'percent_utilization', 'inservice_aging', 'priority_score',
            'priority_label', 'installation_status', 'latitude', 'longitude'
        ]].copy()

        l2_details.columns = [
            'L2_Name', 'Ports_Available', 'Total_Ports', 'Ports_Used',
            'Utilization_Percent', 'Aging_Days', 'Priority_Score',
            'Priority_Label', 'Installation_Status', 'L2_Latitude', 'L2_Longitude'
        ]

        # Sort by priority score
        l2_details = l2_details.sort_values('Priority_Score', ascending=False)

        return l2_details

    def export_enhanced_database(self, output_path: str):
        """Export processed data for Eagle Eye MVP"""
        if self.happy_blocks_df is None:
            raise ValueError("Must process data first")

        print(f"Exporting enhanced database to: {output_path}")

        # Add timestamp
        self.happy_blocks_df['Last_Updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Export main Happy Block data
        self.happy_blocks_df.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"Exported {len(self.happy_blocks_df)} Happy Blocks")

        # Export detailed L2 data
        l2_output_path = output_path.replace('.csv', '_l2_details.csv')
        l2_export = self.df[[
            'happy_block', 'Rollout Location name', 'splt_l2', 'sum_tol_avail',
            'priority_score', 'priority_label', 'installation_status',
            'latitude', 'longitude', 'inservice_aging'
        ]].copy()

        l2_export.to_csv(l2_output_path, index=False, encoding='utf-8-sig')
        print(f"Exported {len(l2_export)} L2 details")

    def _get_priority_label(self, score: float) -> str:
        """Convert priority score to label"""
        for label, (min_score, max_score) in self.PRIORITY_RANGES.items():
            if min_score <= score < max_score:
                return label
        return 'VERY_LOW'

    def _get_installation_status(self, aging_days: float) -> str:
        """Convert aging days to installation status"""
        if aging_days <= self.NEW_THRESHOLD:
            return 'New'
        elif aging_days <= self.MEDIUM_THRESHOLD:
            return 'Medium'
        else:
            return 'Old'

    def _get_dominant_status(self, status_series) -> str:
        """Get dominant installation status from a series"""
        return status_series.mode().iloc[0] if len(status_series) > 0 else 'Old'

    def _get_dominant_priority(self, priority_series) -> str:
        """Get dominant priority label from a series"""
        return priority_series.mode().iloc[0] if len(priority_series) > 0 else 'LOW'

    def get_summary_stats(self) -> Dict:
        """Get summary statistics"""
        if self.df is None or self.happy_blocks_df is None:
            return {}

        return {
            'total_l2_records': len(self.df),
            'total_happy_blocks': len(self.happy_blocks_df),
            'total_villages': self.df['Rollout Location name'].nunique(),
            'avg_l2_per_village': (len(self.df) / self.df['Rollout Location name'].nunique()),
            'priority_distribution': self.happy_blocks_df['Priority_Label'].value_counts().to_dict(),
            'installation_distribution': self.happy_blocks_df['Installation_Status'].value_counts().to_dict(),
            'avg_ports_per_village': self.happy_blocks_df['HHB_Ports_Available'].mean(),
            'total_available_ports': self.happy_blocks_df['HHB_Ports_Available'].sum()
        }


def main():
    """Test the L2 Database Processor"""
    processor = L2DatabaseProcessor("data/South L2 Ports Utilization on W25036_20250905.csv")

    # Load and process data
    processor.load_data()
    processor.calculate_priority_scores()
    processor.aggregate_happy_blocks()

    # Get top priority villages
    top_villages = processor.get_prioritized_villages(top_n=10)
    print("\nTop 10 Priority Villages:")
    for _, village in top_villages.iterrows():
        print(f"  {village['Village_Name']}: Score {village['Priority_Score']:.1f} "
              f"({village['Priority_Label']}, {village['L2_Count']} L2s, "
              f"{village['HHB_Ports_Available']:.0f} ports)")

    # Export enhanced database
    processor.export_enhanced_database("data/enhanced_village_database.csv")

    # Print summary
    stats = processor.get_summary_stats()
    print(f"\nSummary Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()