#!/usr/bin/env python3
"""
Simple script to run the Risk Assessment App
"""
import subprocess
import sys
import os

def main():
    print("Starting Risk Assessment Application...")
    print("Press Ctrl+C to stop")
    
    try:
        # Run the main application
        subprocess.run([sys.executable, "main.py"])
    except KeyboardInterrupt:
        print("\nApplication stopped by user")
    except Exception as e:
        print(f"Error running application: {e}")

if __name__ == "__main__":
    main()
