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
    import streamlit as st
    import os

    # Default values (hardcoded as backup for production)
    BACKUP_SECRETS = {
        'besttime_private': "pri_3a58800776b248ee8d6cded7163fedd2",
        'besttime_public': "pub_d186b2f77b5147cfbc94521e6f6b9d84",
        'google_maps': "AIzaSyC8jsQ1LnDiEbslyuZtJ6IEkkcaOVpdu7E"
    }

    # Method 1: Try Streamlit secrets (production)
    try:
        if hasattr(st, 'secrets') and len(st.secrets) > 0:
            secrets = {
                'besttime_private': st.secrets.get("BESTTIME_API_KEY_PRIVATE"),
                'besttime_public': st.secrets.get("BESTTIME_API_KEY_PUBLIC"),
                'google_maps': st.secrets.get("GOOGLE_MAPS_API_KEY")
            }

            # If any secret is None, use backup
            for key, value in secrets.items():
                if not value:
                    secrets[key] = BACKUP_SECRETS[key]

            return secrets
    except Exception as e:
        st.warning(f"Streamlit secrets failed: {e}")

    # Method 2: Try .env file (local)
    try:
        from dotenv import load_dotenv
        load_dotenv()

        secrets = {
            'besttime_private': os.getenv("BESTTIME_API_KEY_PRIVATE"),
            'besttime_public': os.getenv("BESTTIME_API_KEY_PUBLIC"),
            'google_maps': os.getenv("GOOGLE_MAPS_API_KEY")
        }

        # If any secret is None, use backup
        for key, value in secrets.items():
            if not value:
                secrets[key] = BACKUP_SECRETS[key]

        return secrets
    except:
        pass

    # Method 3: Use backup secrets (guaranteed to work)
    st.info("Using backup API keys")
    return BACKUP_SECRETS