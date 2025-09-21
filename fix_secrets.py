# Auto-fix for Streamlit Cloud Secrets
# This creates a simple secrets.toml that works with st.secrets

import os

# Create .streamlit directory if not exists
os.makedirs('.streamlit', exist_ok=True)

# Create secrets.toml with proper format
secrets_content = '''# Streamlit Cloud Secrets
BESTTIME_API_KEY_PRIVATE = "pri_3a58800776b248ee8d6cded7163fedd2"
BESTTIME_API_KEY_PUBLIC = "pub_d186b2f77b5147cfbc94521e6f6b9d84"
GOOGLE_MAPS_API_KEY = "AIzaSyC8jsQ1LnDiEbslyuZtJ6IEkkcaOVpdu7E"
STREAMLIT_SHARING_MODE = "1"
'''

with open('.streamlit/secrets.toml', 'w') as f:
    f.write(secrets_content)

print("✅ Created .streamlit/secrets.toml")
print("✅ Secrets format should work with Streamlit Cloud")

# Test secrets loading
try:
    import streamlit as st
    if hasattr(st, 'secrets'):
        print("✅ Streamlit secrets available")
        for key in ['BESTTIME_API_KEY_PRIVATE', 'BESTTIME_API_KEY_PUBLIC', 'GOOGLE_MAPS_API_KEY']:
            try:
                value = st.secrets[key]
                print(f"✅ {key}: {value[:20]}...")
            except:
                print(f"❌ {key}: Not found")
    else:
        print("ℹ️ Not running in Streamlit context")
except:
    print("ℹ️ Streamlit not available (normal for script execution)")