# Environment Configuration
import os

def get_config():
    """Get configuration based on environment"""

    # Environment detection: production only if explicitly set
    is_production = os.getenv("STREAMLIT_SHARING_MODE") == "1"

    if is_production:
        # Production settings (Streamlit Cloud)
        return {
            'csv_path': 'data/South L2 Ports Utilization on W25036_20250905.csv',
            'sample_size': 80000,  # Increased for geographic completeness
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
            'sample_size': None,  # Use full dataset locally
            'cache_ttl': 14 * 24 * 3600,  # 14 days cache
            'debug_mode': True,
            'max_happy_blocks': 50,
            'poi_radius': 2000,
            'api_timeout': 30
        }

def get_secrets():
    """Get API keys from appropriate source"""
    import streamlit as st
    import os

    # Backup API keys for production reliability
    BACKUP_KEYS = {
        'besttime_private': "pri_3a58800776b248ee8d6cded7163fedd2",
        'besttime_public': "pub_d186b2f77b5147cfbc94521e6f6b9d84",
        'google_maps': "AIzaSyC8jsQ1LnDiEbslyuZtJ6IEkkcaOVpdu7E"
    }

    # Try Streamlit secrets first (production)
    try:
        if hasattr(st, 'secrets') and len(st.secrets) > 0:
            return {
                'besttime_private': st.secrets.get("BESTTIME_API_KEY_PRIVATE") or BACKUP_KEYS['besttime_private'],
                'besttime_public': st.secrets.get("BESTTIME_API_KEY_PUBLIC") or BACKUP_KEYS['besttime_public'],
                'google_maps': st.secrets.get("GOOGLE_MAPS_API_KEY") or BACKUP_KEYS['google_maps']
            }
    except:
        pass

    # Try .env file (local development)
    try:
        from dotenv import load_dotenv
        load_dotenv()

        return {
            'besttime_private': os.getenv("BESTTIME_API_KEY_PRIVATE") or BACKUP_KEYS['besttime_private'],
            'besttime_public': os.getenv("BESTTIME_API_KEY_PUBLIC") or BACKUP_KEYS['besttime_public'],
            'google_maps': os.getenv("GOOGLE_MAPS_API_KEY") or BACKUP_KEYS['google_maps']
        }
    except:
        pass

    # Fallback to backup keys
    return BACKUP_KEYS