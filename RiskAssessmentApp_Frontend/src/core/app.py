"""
Risk Assessment Application - Main Application Entry Point
"""

import flet as ft
import sys
import os
from pathlib import Path

# Add the src directory to the Python path for imports
src_path = Path(__file__).parent.parent
sys.path.insert(0, str(src_path))

from src.views.auth.login import LoginView
from src.views.dashboard.dashboard import DashboardView
from src.views.dashboard.heatmap import HeatmapView
from src.views.assessments.list import AssessmentListView
from src.views.departments.departments_view import DepartmentsView
from src.views.projects.projects_view import ProjectsView
from src.views.settings.settings_view import SettingsView
from src.views.users.user_management import UserManagementView
from src.views.support import SupportView
from src.utils.theme import get_theme_colors, apply_theme_to_control
from core.config import API_CONFIG
from src.api.auditing_client import AuditingAPIClient


class RiskAssessmentApp:
    """Main Risk Assessment Application Class"""
    
    def __init__(self):
        self.page = None
        self.current_user = None
        self.current_view = None
        self.theme_mode = ft.ThemeMode.DARK
        
        # View instances
        self.views = {}
        self.auditing_client = None
        
    def main(self, page: ft.Page):
        """Main application entry point"""
        self.page = page
        self.page.title = "Risk Core - Assessment Platform"
        self.page.theme_mode = self.theme_mode
        self.page.window_width = 1200
        self.page.window_height = 800
        self.page.window_min_width = 800
        self.page.window_min_height = 600
        
        # Set page reference for navigation
        self.page.APP_INSTANCE = self
        
        print("Page configured")
        
        # Show login initially
        self.show_login()
        
    def show_login(self):
        """Show the login screen"""
        login_view = LoginView(
            self.page,
            on_login_success=self.on_login_success
        )
        self.page.clean()
        self.page.add(login_view)
        self.page.update()
        
    def on_login_success(self, user_data):
        """Handle successful login"""
        self.current_user = user_data
        print(f"Login successful for user: {user_data}")
        
        # Initialize main application views
        self.initialize_views()
        
        # Show dashboard by default
        self.show_view("dashboard")
        
    def initialize_views(self):
        """Initialize all application views"""
        print("Initializing views")
        
        # Lazy init API clients
        if self.auditing_client is None:
            try:
                self.auditing_client = AuditingAPIClient()
            except Exception:
                self.auditing_client = None
        
        self.views = {
            "dashboard": DashboardView(self.page, self.auditing_client, self.on_navigate, self.current_user),
            "assessments": AssessmentListView(self.page, self.current_user),
            "departments": DepartmentsView(self.page),
            "projects": ProjectsView(self.page, self.current_user),
            "users": UserManagementView(self.page, self.current_user),
            "support": SupportView(self.page, self.current_user),
            "settings": SettingsView(self.page, self.current_user),
            "heatmap": HeatmapView(self.page, self.current_user, on_navigate=self.on_navigate),
        }
        
    def show_view(self, view_name):
        """Show a specific view"""
        print(f"Showing view: {view_name}")
        
        if view_name not in self.views:
            print(f"View {view_name} not found")
            return
            
        view = self.views[view_name]
        
        # Create main layout with navigation
        self.create_main_layout(view)

    def on_navigate(self, dest, sub=None, params=None):
        """Handle in-app navigation requests from views/cards."""
        try:
            target = (dest or "").lower()
            if target in self.views:
                # Optionally pass simple filters to target views
                if target == "assessments" and isinstance(params, dict):
                    view = self.views.get("assessments")
                    # Map common params
                    status = params.get("status")
                    if status:
                        try:
                            view.current_risk_filter = "All Levels"
                            view.current_dept_filter = "All Departments"
                            view.search_value = status.lower()
                            view.refresh_table()
                        except Exception:
                            pass
                self.current_view = target
                self.show_view(target)
            elif target == "dashboard":
                self.current_view = "dashboard"
                self.show_view("dashboard")
        except Exception as e:
            print(f"Navigation error: {e}")
        
    def create_main_layout(self, content_view):
        """Create the main application layout with navigation"""
        # Navigation rail
        nav_rail = ft.NavigationRail(
            selected_index=self.get_nav_index(),
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=100,
            min_extended_width=200,
            group_alignment=-0.9,
            destinations=[
                ft.NavigationRailDestination(
                    icon=ft.icons.DASHBOARD,
                    selected_icon=ft.icons.DASHBOARD,
                    label="Dashboard"
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.ASSESSMENT,
                    selected_icon=ft.icons.ASSESSMENT,
                    label="Assessments"
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.BUSINESS,
                    selected_icon=ft.icons.BUSINESS,
                    label="Departments"
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.FOLDER_SPECIAL,
                    selected_icon=ft.icons.FOLDER_SPECIAL,
                    label="Projects"
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.PEOPLE,
                    selected_icon=ft.icons.PEOPLE,
                    label="Users"
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.HELP,
                    selected_icon=ft.icons.HELP,
                    label="Support"
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.SETTINGS,
                    selected_icon=ft.icons.SETTINGS,
                    label="Settings"
                ),
            ],
            on_change=self.on_nav_change,
        )
        
        # Header
        header = ft.Container(
            content=ft.Row([
                ft.Text(
                    "Risk Core",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color="#ffffff"
                ),
                ft.Container(expand=True),
                ft.Text(
                    f"Welcome, {self.current_user.get('name', 'User') if self.current_user else 'User'}",
                    color="#ffffff"
                ),
                ft.IconButton(
                    icon=ft.icons.LOGOUT,
                    tooltip="Logout",
                    on_click=self.logout,
                    icon_color="#ffffff"
                )
            ]),
            bgcolor="#1e293b",
            padding=ft.padding.symmetric(horizontal=20, vertical=10),
        )
        
        # Main content area
        content_area = ft.Container(
            content=content_view,
            expand=True,
            padding=10,
        )
        
        print("Setting content area to dashboard view")
        
        # Main layout
        main_layout = ft.Column([
            header,
            ft.Row([
                nav_rail,
                ft.VerticalDivider(width=1),
                content_area,
            ], expand=True)
        ], expand=True, spacing=0)
        
        self.page.clean()
        self.page.add(main_layout)
        self.page.update()
        
    def get_nav_index(self):
        """Get the current navigation index based on current view"""
        view_mapping = {
            "dashboard": 0,
            "assessments": 1,
            "departments": 2,
            "projects": 3,
            "users": 4,
            "support": 5,
            "settings": 6,
        }
        return view_mapping.get(self.current_view, 0)
        
    def on_nav_change(self, e):
        """Handle navigation changes"""
        index_mapping = {
            0: "dashboard",
            1: "assessments", 
            2: "departments",
            3: "projects",
            4: "users",
            5: "support",
            6: "settings",
        }
        
        selected_view = index_mapping.get(e.control.selected_index)
        if selected_view:
            print(f"Navigation change to index: {e.control.selected_index}")
            self.current_view = selected_view
            self.show_view(selected_view)
            
    def logout(self, e):
        """Handle user logout"""
        self.current_user = None
        self.current_view = None
        self.views.clear()
        self.show_login()


def create_app():
    """Create and return the main application instance"""
    app = RiskAssessmentApp()
    return app.main


if __name__ == "__main__":
    # Run the application
    app = RiskAssessmentApp()
    ft.app(target=app.main)
