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

    # Check if running on Streamlit Cloud
    if hasattr(st, 'secrets') and len(st.secrets) > 0:
        try:
            secrets = {
                'besttime_private': st.secrets.get("BESTTIME_API_KEY_PRIVATE"),
                'besttime_public': st.secrets.get("BESTTIME_API_KEY_PUBLIC"),
                'google_maps': st.secrets.get("GOOGLE_MAPS_API_KEY")
            }

            # Debug info for production
            if get_config()['debug_mode'] or True:  # Always show in production for now
                st.info(f"🔑 Loaded secrets: BestTime={'✓' if secrets['besttime_private'] else '✗'}, Google Maps={'✓' if secrets['google_maps'] else '✗'}")
                if secrets['google_maps']:
                    st.success(f"✅ Google Maps API Key: {secrets['google_maps'][:20]}...")
                else:
                    st.error("❌ Google Maps API Key not found in secrets")

            return secrets
        except Exception as e:
            st.error(f"Error loading secrets: {e}")

    # Fallback to .env file (local)
    from dotenv import load_dotenv
    load_dotenv()

    secrets = {
        'besttime_private': os.getenv("BESTTIME_API_KEY_PRIVATE"),
        'besttime_public': os.getenv("BESTTIME_API_KEY_PUBLIC"),
        'google_maps': os.getenv("GOOGLE_MAPS_API_KEY")
    }

    return secrets