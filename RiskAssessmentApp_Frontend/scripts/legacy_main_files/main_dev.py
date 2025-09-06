import flet as ft
import os
from views.login import LoginView
from views.dashboard import DashboardView
from views.assessment.list import AssessmentListView
from views.user_management import UserManagementView
from views.departments_view import DepartmentsView
from views.projects_view import ProjectsView
from config import get_db_connection

# Import utility modules
from utils.pdf_generator import PDFGenerator
from utils.excel_exporter import ExcelExporter


def main(page: ft.Page):
    """Main function for hot reload compatibility"""
    app = RiskAssessmentApp()
    app.main(page)


class RiskAssessmentApp:
    def __init__(self):
        self.auth_controller = None  # Simplified for testing
        self.current_user = None

    def main(self, page: ft.Page):
        # Set up the page
        page.title = "Risk Assessment Application"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.window_width = 1200
        page.window_height = 800
        page.padding = 0
        print("Page configured")  # Debug print

        page.APP_INSTANCE = self

        # Initialize navigation state
        self.page = page
        self.views = {}
        self.current_view = None
        self.current_nav_index = 0

        # Create navigation handling function
        def nav_change(index):
            print(f"Navigation change to index: {index}")  # Debug print
            try:
                if index == 0:
                    self.show_view("dashboard")
                elif index == 1:
                    self.show_view("assessments")
                elif index == 2:
                    self.show_view("departments")
                elif index == 3:
                    self.show_view("projects")
                elif index == 4:
                    self.show_view("users")
                elif index == 5:
                    self.show_view("settings")
            except Exception as e:
                print(f"Navigation error: {e}")
                # Show error in UI
                self.content_area.content = ft.Text(f"Navigation error: {str(e)}")
                self.page.update()

        # Define menu items with proper handling
        menu_items = [
            {"text": "Dashboard", "index": 0},
            {"text": "Assessments", "index": 1},
            {"text": "Departments", "index": 2},
            {"text": "Projects", "index": 3},
            {"text": "Users", "index": 4},
            {"text": "Settings", "index": 5},
        ]

        # Create menu item containers with correct event handling
        menu_containers = []
        for item in menu_items:
            index = item["index"]
            menu_containers.append(
                ft.TextButton(
                    content=self.create_menu_item(item["text"], index == 0, index),
                    style=ft.ButtonStyle(
                        padding=0,
                        shape=ft.RoundedRectangleBorder(radius=0),
                    ),
                    on_click=lambda e, idx=index: nav_change(idx),
                    data=index,  # Store the index as data for reference
                    width=220,
                )
            )

        # User profile section for the sidebar
        user_profile = ft.Container(
            padding=20,
            content=ft.Container(
                padding=10,
                bgcolor="#34495e",
                border_radius=10,
                content=ft.Row([
                    ft.Container(
                        width=40,
                        height=40,
                        bgcolor="#3498db",
                        border_radius=20,
                        alignment=ft.alignment.center,
                        content=ft.Text("A", color="white", size=16, weight=ft.FontWeight.BOLD)
                    ),
                    ft.Column([
                        ft.Text("Auditor User", color="white", size=14, weight=ft.FontWeight.BOLD),
                        ft.Text("Risk Assessor", color="#95a5a6", size=12)
                    ])
                ])
            )
        )

        # Build the sidebar with all elements
        sidebar_content = [
            ft.Container(
                padding=10,
                content=ft.Text("Risk Assessment App", color="white", size=18, weight=ft.FontWeight.BOLD)
            )
        ]
        sidebar_content.extend(menu_containers)
        sidebar_content.append(ft.Container(expand=True))  # Spacer
        sidebar_content.append(user_profile)

        # Create the sidebar container
        self.sidebar = ft.Container(
            width=220,
            height=page.height,
            bgcolor="#2c3e50",
            content=ft.Column(sidebar_content)
        )

        # Store menu containers for later reference when updating selection
        self.menu_containers = menu_containers

        # Content area will hold the active view
        self.content_area = ft.Container(
            expand=True,
            alignment=ft.alignment.top_left,
            bgcolor="#f5f5f5"  # Light background for content area
        )

        # Layout
        self.layout = ft.Row(
            [
                self.sidebar,
                self.content_area
            ],
            spacing=0,
            expand=True
        )

        # Start with login
        self.show_login()
        print("Initial view setup complete")  # Debug print

        # Update page
        page.update()

    def update_sidebar_selection(self):
        """Update the sidebar to reflect the current selection"""
        try:
            for button in self.menu_containers:
                index = button.data
                # Only update the appearance, not the entire button
                button.content = self.create_menu_item(
                    self.get_menu_text(index),
                    index == self.current_nav_index,
                    index
                )
            self.page.update()
        except Exception as e:
            print(f"Error updating sidebar: {e}")

    def get_menu_text(self, index):
        """Get the menu text for a given index"""
        menu_texts = {
            0: "Dashboard",
            1: "Assessments",
            2: "Departments",
            3: "Projects",
            4: "Users",
            5: "Settings",
        }
        return menu_texts.get(index, "Unknown")

    def create_menu_item(self, text, selected=False, index=0):
        # Dictionary of icon colors for menu items
        icon_colors = {
            0: "#ffffff",  # Dashboard
            1: "#3498db",  # Assessments
            2: "#f39c12",  # Departments
            3: "#2ecc71",  # Projects
            4: "#e74c3c",  # Users
            5: "#95a5a6",  # Settings
        }

        return ft.Container(
            height=50,
            bgcolor="#34495e" if selected else "#2c3e50",
            content=ft.Row([
                ft.Container(
                    margin=ft.margin.only(left=20, right=10),
                    content=ft.Container(
                        width=20,
                        height=20,
                        border_radius=10,
                        bgcolor=icon_colors.get(index, "#ffffff")
                    )
                ),
                ft.Text(text, color="white", size=14)
            ]),
            # Add explicit hover effect for better UX
            ink=True,
            tooltip=text,
        )

    def show_login(self):
        """Show the login screen"""
        print("Showing login view")  # Debug print
        try:
            # For testing, we'll use a simplified login without icons
            self.login_view = ft.Container(
                content=ft.Column([
                    ft.Text("Risk Assessment Login", size=28, weight=ft.FontWeight.BOLD, color="#2c3e50"),
                    ft.Container(height=20),
                    ft.TextField(
                        label="Username",
                        border_radius=5,
                        value="admin"
                    ),
                    ft.TextField(
                        label="Password",
                        border_radius=5,
                        password=True,
                        value="password"
                    ),
                    ft.Container(height=20),
                    ft.ElevatedButton(
                        "Login",
                        on_click=self.test_login,
                        bgcolor="#3498db",
                        color="white",
                        width=200
                    )
                ], width=300, alignment=ft.MainAxisAlignment.CENTER),
                alignment=ft.alignment.center,
                expand=True,
                bgcolor="#f5f5f5"
            )
            self.page.controls = [self.login_view]
            self.page.update()
        except Exception as e:
            print(f"Error showing login: {e}")
            self.page.controls = [ft.Text(f"Error loading login view: {str(e)}")]
            self.page.update()

    def test_login(self, e):
        """Test login function without actual authentication"""
        self.current_user = {"username": "admin", "role": "administrator"}
        self.on_login(self.current_user)

    def on_login(self, user):
        """Handle successful login"""
        print(f"Login successful for user: {user}")  # Debug print
        try:
            self.current_user = user

            # Initialize views that need user information
            print("Initializing views")

            # Dashboard view with export button (no icon) and scrolling enabled
            dashboard_header = ft.Row([
                ft.Text("Dashboard", size=24, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),
                ft.ElevatedButton(
                    "Export Reports",
                    bgcolor="#3498db",
                    color="white",
                    on_click=self.show_export_options
                )
            ])

            self.views["dashboard"] = ft.Container(
                padding=20,
                content=ft.Column([
                    dashboard_header,
                    ft.Text("Welcome to your Risk Assessment Dashboard", size=16),
                    ft.Container(height=20),
                    ft.Row([
                        ft.Card(
                            content=ft.Container(
                                padding=20,
                                content=ft.Column([
                                    ft.Text("15", size=36, weight=ft.FontWeight.BOLD, color="#3498db"),
                                    ft.Text("Active Assessments", size=14, color="#666666")
                                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                            ),
                            width=200,
                            height=150
                        ),
                        ft.Container(width=20),
                        ft.Card(
                            content=ft.Container(
                                padding=20,
                                content=ft.Column([
                                    ft.Text("5", size=36, weight=ft.FontWeight.BOLD, color="#e74c3c"),
                                    ft.Text("High Risk Areas", size=14, color="#666666")
                                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                            ),
                            width=200,
                            height=150
                        ),
                        ft.Container(width=20),
                        ft.Card(
                            content=ft.Container(
                                padding=20,
                                content=ft.Column([
                                    ft.Text("8", size=36, weight=ft.FontWeight.BOLD, color="#2ecc71"),
                                    ft.Text("Completed This Month", size=14, color="#666666")
                                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                            ),
                            width=200,
                            height=150
                        ),
                    ]),

                    # Updated Risk Distribution by Department section
                    ft.Container(
                        height=300,
                        margin=ft.margin.only(top=20, bottom=30),
                        content=ft.Column([
                            ft.Text("Risk Distribution by Department", size=18, weight=ft.FontWeight.BOLD),
                            ft.Container(height=20),
                            ft.Row([
                                # IT Department
                                ft.Container(
                                    expand=1,
                                    padding=10,
                                    margin=ft.margin.all(5),
                                    border_radius=10,
                                    bgcolor="white",
                                    content=ft.Column([
                                        ft.Text("IT", size=16, weight=ft.FontWeight.BOLD, color="#2c3e50"),
                                        ft.Container(height=15),
                                        ft.Container(
                                            height=60,
                                            bgcolor="#e74c3c",  # High risk
                                            border_radius=5,
                                            alignment=ft.alignment.center,
                                            content=ft.Text("35%", color="white", weight=ft.FontWeight.BOLD)
                                        ),
                                        ft.Container(height=8),
                                        ft.Container(
                                            height=40,
                                            bgcolor="#f39c12",  # Medium risk
                                            border_radius=5,
                                            alignment=ft.alignment.center,
                                            content=ft.Text("25%", color="white", weight=ft.FontWeight.BOLD)
                                        ),
                                        ft.Container(height=8),
                                        ft.Container(
                                            height=25,
                                            bgcolor="#2ecc71",  # Low risk
                                            border_radius=5,
                                            alignment=ft.alignment.center,
                                            content=ft.Text("15%", color="white", weight=ft.FontWeight.BOLD)
                                        ),
                                        ft.Container(height=15),
                                        ft.Row([
                                            ft.Container(
                                                width=12,
                                                height=12,
                                                bgcolor="#e74c3c",
                                                border_radius=6,
                                            ),
                                            ft.Text(" High", size=12, color="#666666"),
                                            ft.Container(width=8),
                                            ft.Container(
                                                width=12,
                                                height=12,
                                                bgcolor="#f39c12",
                                                border_radius=6,
                                            ),
                                            ft.Text(" Med", size=12, color="#666666"),
                                            ft.Container(width=8),
                                            ft.Container(
                                                width=12,
                                                height=12,
                                                bgcolor="#2ecc71",
                                                border_radius=6,
                                            ),
                                            ft.Text(" Low", size=12, color="#666666"),
                                        ], alignment=ft.MainAxisAlignment.CENTER)
                                    ])
                                ),
                                # Finance Department
                                ft.Container(
                                    expand=1,
                                    padding=10,
                                    margin=ft.margin.all(5),
                                    border_radius=10,
                                    bgcolor="white",
                                    content=ft.Column([
                                        ft.Text("Finance", size=16, weight=ft.FontWeight.BOLD, color="#2c3e50"),
                                        ft.Container(height=15),
                                        ft.Container(
                                            height=35,
                                            bgcolor="#e74c3c",  # High risk
                                            border_radius=5,
                                            alignment=ft.alignment.center,
                                            content=ft.Text("20%", color="white", weight=ft.FontWeight.BOLD)
                                        ),
                                        ft.Container(height=8),
                                        ft.Container(
                                            height=50,
                                            bgcolor="#f39c12",  # Medium risk
                                            border_radius=5,
                                            alignment=ft.alignment.center,
                                            content=ft.Text("30%", color="white", weight=ft.FontWeight.BOLD)
                                        ),
                                        ft.Container(height=8),
                                        ft.Container(
                                            height=40,
                                            bgcolor="#2ecc71",  # Low risk
                                            border_radius=5,
                                            alignment=ft.alignment.center,
                                            content=ft.Text("25%", color="white", weight=ft.FontWeight.BOLD)
                                        ),
                                        ft.Container(height=15),
                                        ft.Row([
                                            ft.Container(
                                                width=12,
                                                height=12,
                                                bgcolor="#e74c3c",
                                                border_radius=6,
                                            ),
                                            ft.Text(" High", size=12, color="#666666"),
                                            ft.Container(width=8),
                                            ft.Container(
                                                width=12,
                                                height=12,
                                                bgcolor="#f39c12",
                                                border_radius=6,
                                            ),
                                            ft.Text(" Med", size=12, color="#666666"),
                                            ft.Container(width=8),
                                            ft.Container(
                                                width=12,
                                                height=12,
                                                bgcolor="#2ecc71",
                                                border_radius=6,
                                            ),
                                            ft.Text(" Low", size=12, color="#666666"),
                                        ], alignment=ft.MainAxisAlignment.CENTER)
                                    ])
                                ),
                                # Operations Department
                                ft.Container(
                                    expand=1,
                                    padding=10,
                                    margin=ft.margin.all(5),
                                    border_radius=10,
                                    bgcolor="white",
                                    content=ft.Column([
                                        ft.Text("Operations", size=16, weight=ft.FontWeight.BOLD, color="#2c3e50"),
                                        ft.Container(height=15),
                                        ft.Container(
                                            height=25,
                                            bgcolor="#e74c3c",  # High risk
                                            border_radius=5,
                                            alignment=ft.alignment.center,
                                            content=ft.Text("15%", color="white", weight=ft.FontWeight.BOLD)
                                        ),
                                        ft.Container(height=8),
                                        ft.Container(
                                            height=25,
                                            bgcolor="#f39c12",  # Medium risk
                                            border_radius=5,
                                            alignment=ft.alignment.center,
                                            content=ft.Text("15%", color="white", weight=ft.FontWeight.BOLD)
                                        ),
                                        ft.Container(height=8),
                                        ft.Container(
                                            height=65,
                                            bgcolor="#2ecc71",  # Low risk
                                            border_radius=5,
                                            alignment=ft.alignment.center,
                                            content=ft.Text("40%", color="white", weight=ft.FontWeight.BOLD)
                                        ),
                                        ft.Container(height=15),
                                        ft.Row([
                                            ft.Container(
                                                width=12,
                                                height=12,
                                                bgcolor="#e74c3c",
                                                border_radius=6,
                                            ),
                                            ft.Text(" High", size=12, color="#666666"),
                                            ft.Container(width=8),
                                            ft.Container(
                                                width=12,
                                                height=12,
                                                bgcolor="#f39c12",
                                                border_radius=6,
                                            ),
                                            ft.Text(" Med", size=12, color="#666666"),
                                            ft.Container(width=8),
                                            ft.Container(
                                                width=12,
                                                height=12,
                                                bgcolor="#2ecc71",
                                                border_radius=6,
                                            ),
                                            ft.Text(" Low", size=12, color="#666666"),
                                        ], alignment=ft.MainAxisAlignment.CENTER)
                                    ])
                                ),
                                # Marketing Department
                                ft.Container(
                                    expand=1,
                                    padding=10,
                                    margin=ft.margin.all(5),
                                    border_radius=10,
                                    bgcolor="white",
                                    content=ft.Column([
                                        ft.Text("Marketing", size=16, weight=ft.FontWeight.BOLD, color="#2c3e50"),
                                        ft.Container(height=15),
                                        ft.Container(
                                            height=20,
                                            bgcolor="#e74c3c",  # High risk
                                            border_radius=5,
                                            alignment=ft.alignment.center,
                                            content=ft.Text("10%", color="white", weight=ft.FontWeight.BOLD)
                                        ),
                                        ft.Container(height=8),
                                        ft.Container(
                                            height=40,
                                            bgcolor="#f39c12",  # Medium risk
                                            border_radius=5,
                                            alignment=ft.alignment.center,
                                            content=ft.Text("25%", color="white", weight=ft.FontWeight.BOLD)
                                        ),
                                        ft.Container(height=8),
                                        ft.Container(
                                            height=60,
                                            bgcolor="#2ecc71",  # Low risk
                                            border_radius=5,
                                            alignment=ft.alignment.center,
                                            content=ft.Text("35%", color="white", weight=ft.FontWeight.BOLD)
                                        ),
                                        ft.Container(height=15),
                                        ft.Row([
                                            ft.Container(
                                                width=12,
                                                height=12,
                                                bgcolor="#e74c3c",
                                                border_radius=6,
                                            ),
                                            ft.Text(" High", size=12, color="#666666"),
                                            ft.Container(width=8),
                                            ft.Container(
                                                width=12,
                                                height=12,
                                                bgcolor="#f39c12",
                                                border_radius=6,
                                            ),
                                            ft.Text(" Med", size=12, color="#666666"),
                                            ft.Container(width=8),
                                            ft.Container(
                                                width=12,
                                                height=12,
                                                bgcolor="#2ecc71",
                                                border_radius=6,
                                            ),
                                            ft.Text(" Low", size=12, color="#666666"),
                                        ], alignment=ft.MainAxisAlignment.CENTER)
                                    ])
                                ),
                            ])
                        ])
                    ),

                    ft.Container(height=30),
                    ft.Text("Recent Assessments", size=18, weight=ft.FontWeight.BOLD),
                    ft.DataTable(
                        columns=[
                            ft.DataColumn(ft.Text("ID")),
                            ft.DataColumn(ft.Text("Title")),
                            ft.DataColumn(ft.Text("Department")),
                            ft.DataColumn(ft.Text("Risk Level")),
                            ft.DataColumn(ft.Text("Date")),
                        ],
                        rows=[
                            ft.DataRow(
                                cells=[
                                    ft.DataCell(ft.Text("A-001")),
                                    ft.DataCell(ft.Text("Annual IT Security Review")),
                                    ft.DataCell(ft.Text("IT")),
                                    ft.DataCell(ft.Container(
                                        padding=5,
                                        border_radius=5,
                                        bgcolor="#e74c3c",
                                        content=ft.Text("High", color="white")
                                    )),
                                    ft.DataCell(ft.Text("2025-03-15")),
                                ],
                            ),
                            ft.DataRow(
                                cells=[
                                    ft.DataCell(ft.Text("A-002")),
                                    ft.DataCell(ft.Text("Financial Controls Audit")),
                                    ft.DataCell(ft.Text("Finance")),
                                    ft.DataCell(ft.Container(
                                        padding=5,
                                        border_radius=5,
                                        bgcolor="#f39c12",
                                        content=ft.Text("Medium", color="white")
                                    )),
                                    ft.DataCell(ft.Text("2025-03-10")),
                                ],
                            ),
                            ft.DataRow(
                                cells=[
                                    ft.DataCell(ft.Text("A-003")),
                                    ft.DataCell(ft.Text("Operational Process Review")),
                                    ft.DataCell(ft.Text("Operations")),
                                    ft.DataCell(ft.Container(
                                        padding=5,
                                        border_radius=5,
                                        bgcolor="#2ecc71",
                                        content=ft.Text("Low", color="white")
                                    )),
                                    ft.DataCell(ft.Text("2025-03-05")),
                                ],
                            ),
                        ],
                    ),
                ], scroll=ft.ScrollMode.AUTO),  # Enable scrolling for dashboard
                bgcolor="#f5f5f5",
                expand=True
            )

            # Initialize Departments view
            self.views["departments"] = DepartmentsView(self.page)

            # Initialize Projects view
            self.views["projects"] = ProjectsView(self.page)

            # Show main application
            self.page.controls = [self.layout]
            self.show_view("dashboard")
            self.page.update()
        except Exception as e:
            print(f"Error in on_login: {e}")
            self.page.controls = [ft.Text(f"Error after login: {str(e)}")]
            self.page.update()

    def show_view(self, view_name):
        """Switch to a specific view"""
        print(f"Showing view: {view_name}")  # Debug print

        try:
            # Lazy initialization of views
            if view_name not in self.views:
                if view_name == "departments":
                    # Initialize department view
                    self.views[view_name] = DepartmentsView(self.page)
                elif view_name == "projects":
                    # Initialize projects view
                    self.views[view_name] = ProjectsView(self.page)
                elif view_name == "assessments":
                    try:
                        # Store current controls to restore them if needed
                        original_controls = self.page.controls.copy() if hasattr(self.page, 'controls') else []
                        # Initialize assessments view with proper user information
                        from views.assessment.list import AssessmentListView
                        assessment_view = AssessmentListView(self.page, self.current_user)

                        # Set the view
                        self.views[view_name] = assessment_view
                        self.content_area.content = assessment_view
                        self.current_view = view_name

                        # Important: Update page
                        self.page.update()

                    except Exception as e:
                        print(f"Error showing assessment view: {str(e)}")
                        # Try to restore original controls if needed
                        if original_controls and hasattr(self.page, 'controls'):
                            self.page.controls = original_controls
                            self.page.update()

                        # Show error in UI
                        self.content_area.content = ft.Column([
                            ft.Text("Error loading assessments view:", color="#e74c3c", size=18,
                                    weight=ft.FontWeight.BOLD),
                            ft.Container(height=10),
                            ft.Text(str(e)),
                            ft.Container(height=20),
                            ft.ElevatedButton(
                                text="Back to Dashboard",
                                on_click=lambda _: self.show_view("dashboard")
                            )
                        ], alignment=ft.MainAxisAlignment.CENTER)
                        self.page.update()

                elif view_name == "users":
                    # Initialize user management view
                    self.views[view_name] = UserManagementView(self.page, self.current_user)
                elif view_name == "settings":
                    # Initialize settings view

                    light_button = ft.ElevatedButton(
                        "Light Mode",
                        on_click=lambda e: self.change_theme(e, ft.ThemeMode.LIGHT, light_button, dark_button),
                        disabled=True
                    )

                    dark_button = ft.ElevatedButton(
                        "Dark Mode",
                        on_click=lambda e: self.change_theme(e, ft.ThemeMode.DARK, light_button, dark_button)
                    )

                    self.views[view_name] = ft.Container(
                        padding=20,
                        content=ft.Column([
                            ft.Text("Settings", size=24, weight=ft.FontWeight.BOLD),
                            ft.Text("Customize your application settings", size=16),
                            ft.Container(height=20),
                            ft.Text("Theme", size=18, weight=ft.FontWeight.BOLD),
                            ft.Row([light_button, dark_button]),
                            ft.Container(height=20),
                            ft.Text("Profile Settings", size=18, weight=ft.FontWeight.BOLD),
                            ft.TextField(
                                label="Name",
                                value=f"{self.current_user['username']}",
                                disabled=True
                            ),
                            ft.TextField(
                                label="Role",
                                value=f"{self.current_user['role']}",
                                disabled=True
                            ),
                            ft.Container(height=10),
                            ft.ElevatedButton(
                                "Edit Profile",
                                disabled=True
                            )
                        ]),
                        bgcolor="#f5f5f5",
                        expand=True
                    )

            # If the view exists, display it
            if view_name in self.views:
                print(f"Setting content area to {view_name} view")  # Debug print
                self.content_area.content = self.views[view_name]
                self.current_view = view_name

                # Update current nav index based on view name
                view_indices = {
                    "dashboard": 0,
                    "assessments": 1,
                    "departments": 2,
                    "projects": 3,
                    "users": 4,
                    "settings": 5
                }
                self.current_nav_index = view_indices.get(view_name, 0)

                # Update sidebar to reflect current selection
                self.update_sidebar_selection()
                self.page.update()
            else:
                print(f"View not found: {view_name}")  # Debug print
                self.content_area.content = ft.Text(f"View '{view_name}' not found")
                self.page.update()
        except Exception as e:
            print(f"Error showing view {view_name}: {e}")
            self.content_area.content = ft.Text(f"Error loading {view_name} view: {str(e)}")
            self.page.update()

    def change_theme(self, e, theme_mode, light_button, dark_button):
        """Change the theme of the application"""
        self.page.theme_mode = theme_mode
        if theme_mode == ft.ThemeMode.LIGHT:
            light_button.disabled = True
            dark_button.disabled = False
        else:
            light_button.disabled = False
            dark_button.disabled = True
        self.page.update()

    def show_export_options(self, e):
        """Show export options dialog"""
        dialog = ft.AlertDialog(
            title=ft.Text("Export Options"),
            content=ft.Column([
                ft.ListTile(
                    title=ft.Text("Export All Assessments (Excel)"),
                    on_click=lambda _: self.handle_export_option("excel_all")
                ),
                ft.ListTile(
                    title=ft.Text("Export Summary Report (PDF)"),
                    on_click=lambda _: self.handle_export_option("pdf_summary")
                ),
                ft.ListTile(
                    title=ft.Text("Export Assessment Report (PDF)"),
                    on_click=lambda _: self.handle_export_option("pdf_assessment")
                ),
            ], width=400)
        )

        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def handle_export_option(self, option):
        """Handle selected export option"""
        self.page.dialog.open = False
        self.page.update()

        # Create export directories if they don't exist
        reports_dir = "reports"
        exports_dir = "exports"
        if not os.path.exists(reports_dir):
            os.makedirs(reports_dir)
        if not os.path.exists(exports_dir):
            os.makedirs(exports_dir)

        # Get assessments from the current view
        assessments = []
        if "assessments" in self.views:
            assessment_view = self.views["assessments"]
            if hasattr(assessment_view, "assessments"):
                assessments = assessment_view.assessments

        # If no assessments yet, use sample data
        if not assessments:
            from datetime import datetime
            from models.assessment import Assessment

            # Create sample assessments for demo
            assessments = [
                Assessment(
                    id="A-001",
                    title="Annual IT Security Review",
                    department_id=1,
                    department="IT",
                    project_id=None,
                    project=None,
                    auditor_id=1,
                    auditor="Admin User",
                    assessment_date=datetime.now().date(),
                    risk_score=3.8,
                    risk_level="High",
                    scope="Assessment of IT security controls and procedures",
                    findings="Multiple security vulnerabilities found in legacy systems",
                    recommendations="Upgrade legacy systems and implement security training",
                    risk_factors=[
                        {"name": "Security Controls", "value": 4.0},
                        {"name": "Staff Training", "value": 3.5},
                        {"name": "System Vulnerabilities", "value": 4.0}
                    ],
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                ),
            ]

        # Handle different export options
        if option == "excel_all":
            try:
                exporter = ExcelExporter()
                exported_file = exporter.export_assessments(assessments)
                self.show_snackbar(f"Exported to {exported_file}")
            except Exception as e:
                self.show_snackbar(f"Export failed: {str(e)}")

        elif option == "pdf_summary":
            try:
                pdf_gen = PDFGenerator()
                pdf_file = pdf_gen.generate_summary_report(assessments)
                self.show_snackbar(f"Report generated: {pdf_file}")
            except Exception as e:
                self.show_snackbar(f"Report generation failed: {str(e)}")

    def show_snackbar(self, message):
        """Show a snackbar message"""
        self.page.snack_bar = ft.SnackBar(content=ft.Text(message))
        self.page.snack_bar.open = True
        self.page.update()


if __name__ == "__main__":
    # Development mode with hot reload
    ports_to_try = [9090, 9091, 9092, 9093, 9094]
    
    for port in ports_to_try:
        try:
            print(f"🚀 Starting Risk Assessment App (DEV MODE) on http://localhost:{port}")
            print("📁 Files will auto-reload when changed!")
            ft.app(
                target=main,  # Use the standalone main function for better hot reload
                port=port, 
                view=ft.AppView.WEB_BROWSER,
                host="127.0.0.1",
                web_renderer=ft.WebRenderer.HTML,
                # Enable hot reload in development
                # assets_dir="assets" if os.path.exists("assets") else None
            )
            break
        except Exception as e:
            print(f"Port {port} failed: {e}")
            continue
    else:
        print("❌ Could not start on any port!") 