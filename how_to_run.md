 การใช้งานใน VSCode ใหม่:

  Method 1: Terminal

  cd D:\eagle-eye-mvp
  eagle-env\Scripts\activate
  streamlit run app.py

  Method 2: VSCode Debugger


  - กด F5 หรือ Run → Start Debugging
  - เลือก "Run Eagle Eye Streamlit"

  Method 3: VSCode Tasks

  - Ctrl+Shift+P → "Tasks: Run Task" → "Run Eagle Eye"

  🔧 Quick Commands เมื่อ restart:

  # Setup environment
  python -m venv eagle-env
  eagle-env\Scripts\activate
  pip install -r requirements.txt

  # Run application
  streamlit run app.py