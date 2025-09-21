# Eagle Eye Setup Guide - VSCode

## 🚀 Complete Setup Guide for New Computer/VSCode

### Step 1: Prerequisites Installation

#### 1.1 Install Python 3.8+
```bash
# Download from: https://www.python.org/downloads/
# During installation, check "Add Python to PATH"

# Verify installation
python --version
pip --version
```

#### 1.2 Install VSCode
```bash
# Download from: https://code.visualstudio.com/
# Install recommended extensions:
# - Python (Microsoft)
# - Python Debugger (Microsoft)
# - Pylance (Microsoft)
```

#### 1.3 Install Git (if not already installed)
```bash
# Download from: https://git-scm.com/downloads
git --version
```

### Step 2: Project Setup

#### 2.1 Open Project in VSCode
```bash
# Method 1: Command Line
cd D:\eagle-eye-mvp
code .

# Method 2: VSCode File Menu
# File → Open Folder → Select D:\eagle-eye-mvp
```

#### 2.2 Create Python Virtual Environment
```bash
# In VSCode Terminal (Ctrl + `)
cd D:\eagle-eye-mvp

# Create virtual environment
python -m venv eagle-env

# Activate virtual environment
# Windows:
eagle-env\Scripts\activate

# You should see (eagle-env) in terminal prompt
```

#### 2.3 Install Dependencies
```bash
# With virtual environment activated
pip install streamlit pandas plotly folium streamlit-folium
pip install googlemaps requests python-dotenv openpyxl

# Alternative: if requirements.txt exists
pip install -r requirements.txt
```

### Step 3: VSCode Configuration

#### 3.1 Select Python Interpreter
```bash
# In VSCode:
# 1. Press Ctrl+Shift+P
# 2. Type "Python: Select Interpreter"
# 3. Choose: .\eagle-env\Scripts\python.exe
```

#### 3.2 Create VSCode Workspace Settings
Create `.vscode/settings.json`:
```json
{
    "python.defaultInterpreterPath": "./eagle-env/Scripts/python.exe",
    "python.terminal.activateEnvironment": true,
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": false,
    "python.linting.flake8Enabled": true,
    "files.associations": {
        "*.md": "markdown"
    }
}
```

#### 3.3 Create VSCode Launch Configuration
Create `.vscode/launch.json`:
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Run Eagle Eye Streamlit",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/eagle-env/Scripts/streamlit",
            "args": ["run", "app.py"],
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}",
            "env": {
                "PYTHONPATH": "${workspaceFolder}"
            }
        }
    ]
}
```

### Step 4: Environment Configuration

#### 4.1 Verify .env File
Ensure `.env` file exists with correct API keys:
```env
BESTTIME_API_KEY_PRIVATE=pri_3a58800776b248ee8d6cded7163fedd2
BESTTIME_API_KEY_PUBLIC=pub_d186b2f77b5147cfbc94521e6f6b9d84
GOOGLE_MAPS_API_KEY=AIzaSyC8jsQ1LnDiEbslyuZtJ6IEkkcaOVpdu7E

# CSV-based system
USE_CSV_ONLY=true
CSV_MASTER_PATH=data/South L2 Ports Utilization on W25036_20250905.csv

# Default settings
REGION_DEFAULT=Songkhla
CACHE_TTL_DAYS=14
```

#### 4.2 Verify Data Files
Check that required files exist:
```bash
# Main data file
ls "data/South L2 Ports Utilization on W25036_20250905.csv"

# Should show file size ~100MB+
```

### Step 5: Running the Application

#### 5.1 Method 1: VSCode Terminal
```bash
# Ensure virtual environment is activated
cd D:\eagle-eye-mvp
eagle-env\Scripts\activate

# Run Streamlit
python -m streamlit run app.py

# Or direct streamlit command
streamlit run app.py
```

#### 5.2 Method 2: VSCode Debugger
```bash
# 1. Press F5 or go to Run → Start Debugging
# 2. Select "Run Eagle Eye Streamlit" configuration
# 3. Application will start in debug mode
```

#### 5.3 Method 3: VSCode Tasks
Create `.vscode/tasks.json`:
```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Run Eagle Eye",
            "type": "shell",
            "command": "python",
            "args": ["-m", "streamlit", "run", "app.py"],
            "group": "build",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "new"
            },
            "options": {
                "cwd": "${workspaceFolder}"
            }
        }
    ]
}
```

Then run: `Ctrl+Shift+P` → `Tasks: Run Task` → `Run Eagle Eye`

### Step 6: Accessing the Application

#### 6.1 Open Browser
```bash
# Application will be available at:
http://localhost:8501

# If port 8501 is busy, Streamlit will auto-assign another port
# Check terminal output for the correct URL
```

#### 6.2 Expected Startup Messages
```bash
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501

  For better performance, install the following packages:
  ...
```

### Step 7: Verification & Testing

#### 7.1 Test Basic Functionality
1. **Homepage Loading**: Should see Eagle Eye header and stats
2. **Area Selection**: Try changing Province/District filters
3. **Report Generation**: Click "Generate Eagle Eye Report"
4. **POI Search**: Should see messages about finding POIs

#### 7.2 Expected Debug Output
```bash
🔍 Searching for POIs near 7.0000, 100.5000
✅ Found 18 POIs: ['7-Eleven', '7-Eleven', '7-eleven']
✅ Found location-specific POI data for X areas
✅ Report generated! Found XX results
```

### Step 8: Common Issues & Solutions

#### 8.1 Python/Pip Not Found
```bash
# Add Python to PATH manually
# Windows: System Properties → Environment Variables
# Add: C:\Users\[Username]\AppData\Local\Programs\Python\Python3x\
# Add: C:\Users\[Username]\AppData\Local\Programs\Python\Python3x\Scripts\
```

#### 8.2 Virtual Environment Issues
```bash
# If activation fails, try:
python -m venv --clear eagle-env
eagle-env\Scripts\activate
pip install --upgrade pip
```

#### 8.3 Import Errors
```bash
# If modules not found:
pip install --upgrade -r requirements.txt

# Check Python interpreter in VSCode
# Ctrl+Shift+P → "Python: Select Interpreter"
```

#### 8.4 Port Already in Use
```bash
# Run on different port:
streamlit run app.py --server.port 8502

# Or kill existing process:
taskkill /f /im streamlit.exe
```

#### 8.5 API Key Issues
```bash
# Check .env file is in project root
# Verify API keys are valid
# No quotes around values in .env
```

### Step 9: Development Workflow

#### 9.1 Recommended VSCode Extensions
```bash
# Essential extensions:
- Python (Microsoft)
- Python Debugger (Microsoft)
- Pylance (Microsoft)
- GitLens (GitKraken)
- Markdown All in One
- Excel Viewer (for .csv files)
```

#### 9.2 Code Editing Tips
```bash
# Auto-formatting
pip install black
# Settings → Format On Save → Enable

# Linting
pip install flake8
# Will show code issues in Problems panel
```

#### 9.3 Git Integration
```bash
# Initialize if needed
git init
git add .
git commit -m "Initial setup"

# VSCode Git panel: Ctrl+Shift+G
```

### Step 10: Performance Optimization

#### 10.1 Clear Cache When Needed
```bash
# In terminal:
rm -rf .streamlit __pycache__
find . -name "*.pyc" -delete

# Or use PowerShell:
Remove-Item -Recurse -Force .streamlit, __pycache__
Get-ChildItem -Recurse -Name "*.pyc" | Remove-Item
```

#### 10.2 Monitor Performance
```bash
# Task Manager → Performance
# Watch RAM usage (should be < 2GB)
# Watch CPU usage during report generation
```

---

## 📋 Quick Reference Commands

### Daily Startup
```bash
cd D:\eagle-eye-mvp
eagle-env\Scripts\activate
streamlit run app.py
```

### Troubleshooting
```bash
# Clear cache
rm -rf .streamlit __pycache__

# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Check system
python --version
pip list
```

### VSCode Shortcuts
- **Open Terminal**: `Ctrl + ` `
- **Command Palette**: `Ctrl + Shift + P`
- **Run Debugger**: `F5`
- **Select Interpreter**: `Ctrl + Shift + P` → "Python: Select Interpreter"

---

**Setup Complete!** 🎉

Your Eagle Eye Sales Intelligence system should now be running at `http://localhost:8501`

For technical details and development notes, see: `CLAUDE.md`