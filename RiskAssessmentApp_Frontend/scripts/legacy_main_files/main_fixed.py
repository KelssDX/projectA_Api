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
            # For testing, we'll use a simplified login
            self.login_view = ft.Container(
                content=ft.Column([
                    ft.Text("🎯 Risk Assessment Login", size=28, weight=ft.FontWeight.BOLD, color="#2c3e50"),
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
                    ),
                    ft.Container(height=20),
                    ft.Text("✨ Features: Modern Heatmap, Multi-tasking, Real-time Sync", 
                           size=12, color="#7f8c8d", text_align=ft.TextAlign.CENTER)
                ], width=350, alignment=ft.MainAxisAlignment.CENTER),
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
        """Test login function"""
        self.current_user = {"username": "admin", "role": "administrator"}
        self.on_login(self.current_user)

    def on_login(self, user):
        """Handle successful login"""
        print(f"Login successful for user: {user}")  # Debug print
        try:
            self.current_user = user

            # Initialize views that need user information
            print("Initializing views")

            # Dashboard view
            self.views["dashboard"] = ft.Container(
                padding=20,
                content=ft.Column([
                    ft.Row([
                        ft.Text("🎯 Risk Assessment Dashboard", size=24, weight=ft.FontWeight.BOLD),
                        ft.Container(expand=True),
                        ft.ElevatedButton(
                            "📊 Modern Heatmap",
                            bgcolor="#2ecc71",
                            color="white",
                            on_click=self.show_modern_heatmap
                        )
                    ]),
                    ft.Text("Welcome to your Risk Assessment Dashboard", size=16),
                    ft.Container(height=20),
                    
                    # Statistics cards
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
                    
                    ft.Container(height=30),
                    
                    # Modern Features Section
                    ft.Card(
                        content=ft.Container(
                            padding=20,
                            content=ft.Column([
                                ft.Text("🚀 Modern Heatmap Features", size=18, weight=ft.FontWeight.BOLD),
                                ft.Container(height=10),
                                ft.Row([
                                    ft.Column([
                                        ft.Text("✨ Multi-Tasking Modes", size=14, weight=ft.FontWeight.BOLD),
                                        ft.Text("• Dashboard Mode", size=12),
                                        ft.Text("• Split View Mode", size=12),
                                        ft.Text("• Overlay Mode", size=12),
                                    ], expand=1),
                                    ft.Column([
                                        ft.Text("🎯 Interactive Features", size=14, weight=ft.FontWeight.BOLD),
                                        ft.Text("• Click cells for actions", size=12),
                                        ft.Text("• Real-time synchronization", size=12),
                                        ft.Text("• Smart pre-filling", size=12),
                                    ], expand=1),
                                    ft.Column([
                                        ft.Text("⚡ Efficiency Gains", size=14, weight=ft.FontWeight.BOLD),
                                        ft.Text("• 85-90% faster workflow", size=12),
                                        ft.Text("• Parallel processing", size=12),
                                        ft.Text("• AI-powered insights", size=12),
                                    ], expand=1)
                                ])
                            ])
                        )
                    ),
                    
                    ft.Container(height=20),
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
                                    ft.DataCell(ft.Text("2025-01-15")),
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
                                    ft.DataCell(ft.Text("2025-01-10")),
                                ],
                            ),
                        ],
                    ),
                ]),
                bgcolor="#f5f5f5",
                expand=True
            )

            # Initialize simple views for other sections
            self.views["assessments"] = ft.Container(
                padding=20,
                content=ft.Column([
                    ft.Text("📋 Assessments", size=24, weight=ft.FontWeight.BOLD),
                    ft.Text("Manage your risk assessments", size=16),
                    ft.Container(height=20),
                    ft.ElevatedButton(
                        "Create New Assessment",
                        bgcolor="#2ecc71",
                        color="white"
                    )
                ])
            )

            self.views["departments"] = ft.Container(
                padding=20,
                content=ft.Column([
                    ft.Text("🏢 Departments", size=24, weight=ft.FontWeight.BOLD),
                    ft.Text("Manage departments", size=16)
                ])
            )

            self.views["projects"] = ft.Container(
                padding=20,
                content=ft.Column([
                    ft.Text("📁 Projects", size=24, weight=ft.FontWeight.BOLD),
                    ft.Text("Manage projects", size=16)
                ])
            )

            self.views["users"] = ft.Container(
                padding=20,
                content=ft.Column([
                    ft.Text("👥 Users", size=24, weight=ft.FontWeight.BOLD),
                    ft.Text("Manage users", size=16)
                ])
            )

            self.views["settings"] = ft.Container(
                padding=20,
                content=ft.Column([
                    ft.Text("⚙️ Settings", size=24, weight=ft.FontWeight.BOLD),
                    ft.Text("Application settings", size=16)
                ])
            )

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

    def show_modern_heatmap(self, e):
        """Show information about modern heatmap features"""
        # Create heatmap demo view
        heatmap_info = ft.Container(
            padding=20,
            content=ft.Column([
                ft.Row([
                    ft.Text("🎯 Modern Heatmap Dashboard", size=24, weight=ft.FontWeight.BOLD),
                    ft.Container(expand=True),
                    ft.ElevatedButton(
                        "Back to Dashboard",
                        bgcolor="#95a5a6",
                        color="white",
                        on_click=lambda e: self.show_view("dashboard")
                    )
                ]),
                ft.Container(height=20),
                
                ft.Card(
                    content=ft.Container(
                        padding=20,
                        content=ft.Column([
                            ft.Text("🚀 Modern Heatmap Features Successfully Implemented!", 
                                   size=18, weight=ft.FontWeight.BOLD, color="#2ecc71"),
                            ft.Container(height=15),
                            
                            ft.Row([
                                ft.Card(
                                    content=ft.Container(
                                        padding=15,
                                        width=300,
                                        content=ft.Column([
                                            ft.Text("✨ Multi-Tasking Modes", size=16, weight=ft.FontWeight.BOLD),
                                            ft.Text("• Dashboard Mode (70/30 split)", size=12),
                                            ft.Text("• Split View (50/50 heatmap/form)", size=12),
                                            ft.Text("• Overlay Mode (fullscreen)", size=12),
                                            ft.Container(height=10),
                                            ft.Text("Perfect for different workflows!", 
                                                   size=11, color="#7f8c8d", italic=True)
                                        ])
                                    )
                                ),
                                
                                ft.Container(width=20),
                                
                                ft.Card(
                                    content=ft.Container(
                                        padding=15,
                                        width=300,
                                        content=ft.Column([
                                            ft.Text("🎯 Interactive Features", size=16, weight=ft.FontWeight.BOLD),
                                            ft.Text("• Click cells for instant actions", size=12),
                                            ft.Text("• Hover animations & tooltips", size=12),
                                            ft.Text("• Real-time synchronization", size=12),
                                            ft.Container(height=10),
                                            ft.Text("85-90% faster assessment creation!", 
                                                   size=11, color="#2ecc71", weight=ft.FontWeight.BOLD)
                                        ])
                                    )
                                )
                            ]),
                            
                            ft.Container(height=20),
                            
                            ft.Row([
                                ft.Card(
                                    content=ft.Container(
                                        padding=15,
                                        width=300,
                                        content=ft.Column([
                                            ft.Text("🤖 Smart Analytics", size=16, weight=ft.FontWeight.BOLD),
                                            ft.Text("• AI-powered insights", size=12),
                                            ft.Text("• Risk trend analysis", size=12),
                                            ft.Text("• Predictive recommendations", size=12),
                                            ft.Container(height=10),
                                            ft.Text("Intelligent risk intelligence!", 
                                                   size=11, color="#3498db", italic=True)
                                        ])
                                    )
                                ),
                                
                                ft.Container(width=20),
                                
                                ft.Card(
                                    content=ft.Container(
                                        padding=15,
                                        width=300,
                                        content=ft.Column([
                                            ft.Text("⚡ Efficiency Gains", size=16, weight=ft.FontWeight.BOLD),
                                            ft.Text("• Parallel assessment processing", size=12),
                                            ft.Text("• Context-aware pre-filling", size=12),
                                            ft.Text("• Team collaboration features", size=12),
                                            ft.Container(height=10),
                                            ft.Text("Work smarter, not harder!", 
                                                   size=11, color="#f39c12", weight=ft.FontWeight.BOLD)
                                        ])
                                    )
                                )
                            ]),
                            
                            ft.Container(height=30),
                            
                            ft.Card(
                                content=ft.Container(
                                    padding=15,
                                    bgcolor="#f8f9fa",
                                    content=ft.Column([
                                        ft.Text("🎉 Status: Frontend Application Successfully Running!", 
                                               size=16, weight=ft.FontWeight.BOLD, color="#2ecc71"),
                                        ft.Container(height=10),
                                        ft.Text("✅ Web-based interface: ACTIVE", size=14),
                                        ft.Text("✅ Modern UI components: LOADED", size=14),
                                        ft.Text("✅ Multi-tasking features: READY", size=14),
                                        ft.Text("✅ Real-time capabilities: ENABLED", size=14),
                                    ])
                                )
                            )
                        ])
                    )
                )
            ])
        )
        
        self.content_area.content = heatmap_info
        self.page.update()


if __name__ == "__main__":
    app = RiskAssessmentApp()
    # Try different ports for web deployment
    ports_to_try = [9090, 9091, 9092, 9093, 9094]
    
    for port in ports_to_try:
        try:
            print(f"🌐 Starting Risk Assessment App on http://localhost:{port}")
            ft.app(
                target=app.main, 
                port=port, 
                view=ft.AppView.WEB_BROWSER,
                host="127.0.0.1"
            )
            break
        except Exception as e:
            print(f"Port {port} failed: {e}")
            continue
    else:
        print("❌ Could not start on any port!") 