"""
Simple script to run the frontend application on an available port
"""
import flet as ft
from main import RiskAssessmentApp

def main():
    app = RiskAssessmentApp()
    
    # Try different ports
    ports_to_try = [8081, 8082, 8083, 8084, 8085]
    
    for port in ports_to_try:
        try:
            print(f"Trying to start frontend on port {port}...")
            ft.app(
                target=app.main, 
                port=port, 
                view=ft.AppView.WEB_BROWSER, 
                host="127.0.0.1"  # Use localhost instead of 0.0.0.0
            )
            break
        except Exception as e:
            print(f"Port {port} failed: {e}")
            continue
    else:
        print("Could not start on any port!")

if __name__ == "__main__":
    main() 