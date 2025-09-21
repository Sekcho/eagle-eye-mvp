"""
Google Sheets I/O operations using Service Account authentication
"""

import os
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from typing import Optional

class GoogleSheetsClient:
    """Google Sheets client using Service Account authentication"""

    def __init__(self):
        self.SCOPES = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        self.client = None
        self.setup_auth()

    def setup_auth(self):
        """Setup Google Sheets Service Account authentication"""
        service_account_path = 'credentials/service-account.json'

        if not os.path.exists(service_account_path):
            print(f"WARNING: Service account file not found: {service_account_path}")
            print("Falling back to CSV mode")
            return False

        try:
            creds = Credentials.from_service_account_file(service_account_path, scopes=self.SCOPES)
            self.client = gspread.authorize(creds)
            print("OK: Google Sheets Service Account authentication successful!")
            return True
        except Exception as e:
            print(f"WARNING: Service Account authentication failed: {e}")
            print("Falling back to CSV mode")
            return False

    def read_sheet(self, sheet_id: str, tab_name: str) -> pd.DataFrame:
        """Read data from CSV file (Google Sheets disabled)"""
        print(f"Reading from CSV instead of Google Sheets (sheet_id: {sheet_id}, tab: {tab_name})")
        return self.read_csv_fallback()

    def update_sheet(self, sheet_id: str, tab_name: str, df: pd.DataFrame):
        """Save data to CSV file (Google Sheets disabled)"""
        print(f"Saving to CSV instead of Google Sheets (sheet_id: {sheet_id}, tab: {tab_name})")
        return self.save_csv_fallback(df)

    def read_csv_fallback(self) -> pd.DataFrame:
        """Read from local CSV (primary data source)"""
        # Try updated file first (with POI and timing data)
        updated_path = "data/master_village_data_updated.csv"
        clean_path = "data/master_village_data_clean.csv"

        if os.path.exists(updated_path):
            df = pd.read_csv(updated_path)
            print(f"Reading from CSV: {updated_path} ({len(df)} rows)")
            return df
        elif os.path.exists(clean_path):
            df = pd.read_csv(clean_path)
            print(f"Reading from CSV: {clean_path} ({len(df)} rows)")
            return df
        else:
            raise FileNotFoundError(f"CSV files not found: {updated_path} or {clean_path}")

    def save_csv_fallback(self, df: pd.DataFrame):
        """Fallback: save to local CSV"""
        csv_path = "data/master_village_data_updated.csv"
        df.to_csv(csv_path, index=False)
        print(f"Saved to CSV fallback: {csv_path} ({len(df)} rows)")
