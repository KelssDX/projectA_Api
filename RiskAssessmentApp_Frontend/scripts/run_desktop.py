"""
Run the frontend application in desktop mode (no web server needed)
"""
import flet as ft
from main import RiskAssessmentApp

def main():
    print("Starting Risk Assessment Application in Desktop Mode...")
    
    app = RiskAssessmentApp()
    
    # Run in desktop mode - no web server needed
    ft.app(
        target=app.main,
        view=ft.AppView.FLET_APP  # Desktop application mode
    )

if __name__ == "__main__":
    main() 