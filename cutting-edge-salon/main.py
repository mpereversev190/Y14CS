## main entry point for the application
## run this to start: python3 main.py

import subprocess
import sys
import os
from dotenv import load_dotenv

# load environment variables
load_dotenv()

def main():
    """Start the application"""
    try:
        # start with welcome window
        subprocess.Popen(["python3", "welcome_window.py"])
    except Exception as e:
        print(f"Error starting application: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()