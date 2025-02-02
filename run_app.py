import subprocess
import sys
from pathlib import Path

if __name__ == "__main__":
    app_path = Path("src/pages/login.py")
    try:
        subprocess.run(["streamlit", "run", str(app_path)], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running Streamlit app: {e}")
        sys.exit(1) 