# 🦅 Eagle Eye Sales Intelligence

Advanced door-to-door sales optimization system with real-time foot traffic analysis.

## 🚀 Quick Start

### For New Computer Setup
1. **Read the complete setup guide**: [`SETUP.md`](SETUP.md)
2. **Follow all VSCode configuration steps**
3. **Run the application**

### If Already Setup
```bash
cd D:\eagle-eye-mvp
eagle-env\Scripts\activate
streamlit run app.py
```

Open browser: **http://localhost:8501**

## 📁 Key Files

- **`SETUP.md`** - Complete step-by-step setup guide for new computers
- **`CLAUDE.md`** - Technical documentation and development notes
- **`app.py`** - Main Streamlit application
- **`requirements.txt`** - Python dependencies
- **`.env`** - API keys and configuration

## 🔧 Features

✅ **Location-Based POI Search** - Real venue discovery via Google Places API
✅ **BestTime Integration** - Live foot traffic timing data
✅ **Smart Coordinate System** - Handles 20K+ locations with deduplication
✅ **Hierarchical Filtering** - Province → District → Subdistrict → Village
✅ **Excel Export** - Comprehensive reports with OVERVIEW/DETAIL structure

## 📊 System Stats

- **20,915 Happy Blocks** across 14 provinces
- **1M+ L2 infrastructure records**
- **Real-time POI discovery** within 2km radius
- **Location-specific timing generation**

## 🆘 Quick Troubleshooting

### App Won't Start
```bash
# Clear cache and restart
rm -rf .streamlit __pycache__
python -m streamlit run app.py
```

### Missing Dependencies
```bash
eagle-env\Scripts\activate
pip install -r requirements.txt
```

### VSCode Issues
- Select Python interpreter: `Ctrl+Shift+P` → "Python: Select Interpreter"
- Choose: `.\eagle-env\Scripts\python.exe`

---

**For complete setup instructions**: See [`SETUP.md`](SETUP.md)
**For technical details**: See [`CLAUDE.md`](CLAUDE.md)

**System Status**: ✅ Fully Operational
**Last Updated**: 2025-09-21
# eagle-eye-mvp
