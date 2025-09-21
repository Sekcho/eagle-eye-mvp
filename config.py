# Environment Configuration
import os
import streamlit as st

def get_config():
    """Get configuration based on environment"""

    # Check if running on Streamlit Cloud
    is_production = os.getenv("STREAMLIT_SHARING_MODE") == "1" or \
                   hasattr(st, 'secrets') and len(st.secrets) > 0

    if is_production:
        # Production settings (Streamlit Cloud)
        return {
            'csv_path': 'data/South L2 Ports Utilization on W25036_20250905.csv',
            'sample_size': 20000,  # Reduced for cloud memory limits
            'cache_ttl': 3600,     # 1 hour cache
            'debug_mode': False,
            'max_happy_blocks': 25, # Limit report size
            'poi_radius': 2000,
            'api_timeout': 15
        }
    else:
        # Local development settings
        return {
            'csv_path': 'data/South L2 Ports Utilization on W25036_20250905.csv',
            'sample_size': 50000,  # Full performance locally
            'cache_ttl': 14 * 24 * 3600,  # 14 days cache
            'debug_mode': True,
            'max_happy_blocks': 50,
            'poi_radius': 2000,
            'api_timeout': 30
        }

def get_secrets():
    """Get API keys from appropriate source"""
    try:
        # Try Streamlit secrets first (production)
        if hasattr(st, 'secrets'):
            return {
                'besttime_private': st.secrets["BESTTIME_API_KEY_PRIVATE"],
                'besttime_public': st.secrets["BESTTIME_API_KEY_PUBLIC"],
                'google_maps': st.secrets["GOOGLE_MAPS_API_KEY"]
            }
    except:
        pass

    # Fallback to .env file (local)
    from dotenv import load_dotenv
    load_dotenv()

    return {
        'besttime_private': os.getenv("BESTTIME_API_KEY_PRIVATE"),
        'besttime_public': os.getenv("BESTTIME_API_KEY_PUBLIC"),
        'google_maps': os.getenv("GOOGLE_MAPS_API_KEY")
    }