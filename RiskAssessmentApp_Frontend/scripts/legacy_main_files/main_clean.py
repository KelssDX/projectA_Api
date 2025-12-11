import flet as ft
from flet import Icons
import os
import asyncio
from views.login import LoginView
from views.dashboard import DashboardView
from views.assessment.list import AssessmentListView
from views.user_management import UserManagementView
from views.departments_view import DepartmentsView
from views.projects_view import ProjectsView
from config import get_db_connection
from controllers.auth_controller import AuthController
from controllers.assessment_controller import AssessmentController
from models.assessment import Assessment

# Import utility modules
from utils.pdf_generator import PDFGenerator
from utils.excel_exporter import ExcelExporter


class RiskAssessmentApp:
    def __init__(self):
        self.auth_controller = AuthController()
        self.current_user = None
        self.assessment_controller = AssessmentController()
        self.current_reference_id = None
        self.pending_assessment_filter = None

    async def main(self, page: ft.Page):
        # Set up the page
        page.title = "Risk Assessment Application"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.window_width = 1200
        page.window_height = 800
        page.padding = 0
        print("Page configured")

        page.APP_INSTANCE = self

        # Initialize navigation state
        self.page = page
        self.views = {}
        self.current_view = None
        self.current_nav_index = 0

        # Prepare theme colors for building UI
        from utils.theme import get_theme_colors, create_modern_button
        colors = get_theme_colors(page.theme_mode)
        self.sidebar_collapsed = False
        self.sidebar_collapsed_width = 70
        self.sidebar_expanded_width = 240

        # Create navigation handling function
        def nav_change(index):
            print(f"Navigation change to index: {index}")
            try:
                self.current_nav_index = index
                view_map = {
                    0: "dashboard",
                    1: "assessments",
                    2: "departments",
                    3: "projects",
                    4: "users",
                    5: "settings"
                }
                view_name = view_map.get(index, "dashboard")
                self.show_view(view_name)
                self.update_sidebar_selection()
            except Exception as e:
                print(f"Error in nav_change: {e}")

        def on_navigate(view_name, subview=None, params=None):
            """Handle navigation requests from views"""
            try:
                if params:
                    if view_name == "assessments" and "reference_id" in params:
                        self.current_reference_id = params["reference_id"]
                    if "filter" in params:
                        self.pending_assessment_filter = params
                
                if subview == "form":
                    # Handle form navigation
                    self.show_view(f"{view_name}_form")
                elif subview == "details":
                    # Handle details navigation
                    self.show_view(f"{view_name}_details")
                else:
                    # Regular view navigation
                    self.show_view(view_name)
            except Exception as e:
                print(f"Error in on_navigate: {e}")

        self.on_navigate = on_navigate

        # Menu items with proper structure
        menu_items = [
            {"text": "Dashboard", "index": 0},
            {"text": "Assessments", "index": 1},
            {"text": "Departments", "index": 2},
            {"text": "Projects", "index": 3},
            {"text": "Users", "index": 4},
            {"text": "Settings", "index": 5},
        ]

        # Create modern menu item containers
        menu_containers = []
        menu_icons = [Icons.DASHBOARD, Icons.ASSESSMENT, Icons.APARTMENT, Icons.WORK, Icons.PEOPLE, Icons.SETTINGS]
        
        for i, item in enumerate(menu_items):
            index = item["index"]
            is_active = index == 0
            
            menu_item = ft.Container(
                content=ft.Row([
                    ft.Container(
                        content=ft.Icon(menu_icons[i], color=colors.primary if is_active else colors.sidebar_text, size=20),
                        width=40,
                        alignment=ft.alignment.center
                    ),
                    ft.Text(
                        item["text"], 
                        color=colors.primary if is_active else colors.sidebar_text,
                        weight=ft.FontWeight.BOLD if is_active else ft.FontWeight.NORMAL,
                        size=14
                    )
                ], spacing=12),
                padding=ft.padding.symmetric(horizontal=16, vertical=12),
                bgcolor=colors.sidebar_item_active if is_active else None,
                border_radius=12,
                margin=ft.margin.symmetric(horizontal=8, vertical=2),
                on_click=lambda e, idx=index: nav_change(idx),
                data=index,
                animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
                ink=True
            )
            menu_containers.append(menu_item)

        # Modern user profile section
        user_profile = ft.Container(
            padding=ft.padding.all(16),
            content=ft.Container(
                padding=ft.padding.all(12),
                bgcolor=colors.glass_bg,
                border_radius=16,
                border=ft.border.all(1, colors.border),
                content=ft.Row([
                    ft.Container(
                        width=40,
                        height=40,
                        bgcolor=colors.primary,
                        border_radius=20,
                        alignment=ft.alignment.center,
                        content=ft.Text("A", color="white", size=16, weight=ft.FontWeight.BOLD),
                        shadow=ft.BoxShadow(
                            spread_radius=0,
                            blur_radius=8,
                            color=colors.shadow,
                            offset=ft.Offset(0, 2)
                        )
                    ),
                    ft.Column([
                        ft.Text("Auditor User", size=14, weight=ft.FontWeight.BOLD, color=colors.sidebar_text),
                        ft.Text("Risk Assessor", size=12, color=colors.text_secondary)
                    ], spacing=2)
                ], spacing=12)
            )
        )

        # Modern toggle sidebar function
        def toggle_sidebar(_=None):
            self.sidebar_collapsed = not self.sidebar_collapsed
            new_width = self.sidebar_collapsed_width if self.sidebar_collapsed else self.sidebar_expanded_width
            self.sidebar.width = new_width
            
            # Update menu items for collapsed/expanded state
            for i, menu_item in enumerate(menu_containers):
                is_active = menu_item.data == self.current_nav_index
                if self.sidebar_collapsed:
                    # Show only icon when collapsed
                    menu_item.content = ft.Container(
                        content=ft.Icon(menu_icons[i], color=colors.primary if is_active else colors.sidebar_text, size=20),
                        alignment=ft.alignment.center,
                        tooltip=menu_items[i]["text"]
                    )
                    menu_item.margin = ft.margin.symmetric(horizontal=4, vertical=2)
                else:
                    # Show icon and text when expanded
                    menu_item.content = ft.Row([
                        ft.Container(
                            content=ft.Icon(menu_icons[i], color=colors.primary if is_active else colors.sidebar_text, size=20),
                            width=40,
                            alignment=ft.alignment.center
                        ),
                        ft.Text(
                            menu_items[i]["text"], 
                            color=colors.primary if is_active else colors.sidebar_text,
                            weight=ft.FontWeight.BOLD if is_active else ft.FontWeight.NORMAL,
                            size=14
                        )
                    ], spacing=12)
                    menu_item.margin = ft.margin.symmetric(horizontal=8, vertical=2)
            
            # Hide/show elements based on collapsed state
            user_profile.visible = not self.sidebar_collapsed
            header_title.visible = not self.sidebar_collapsed
            
            self.sidebar.update()

        # Modern sidebar header
        header_title = ft.Text("Risk Core77", size=20, weight=ft.FontWeight.BOLD, color=colors.sidebar_text)
        sidebar_header = ft.Container(
            padding=ft.padding.all(16),
            content=ft.Row([
                header_title,
                ft.Container(expand=True),
                ft.Container(
                    content=ft.IconButton(
                        icon=Icons.MENU, 
                        icon_color=colors.sidebar_text,
                        tooltip="Toggle sidebar", 
                        on_click=toggle_sidebar,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=8)
                        )
                    ),
                    bgcolor=colors.sidebar_item,
                    border_radius=8,
                    animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT)
                )
            ])
        )

        sidebar_content = [sidebar_header]
        sidebar_content.extend(menu_containers)
        sidebar_content.append(ft.Container(expand=True))  # Spacer
        sidebar_content.append(user_profile)

        # Create modern sidebar with glass effect and shadows
        self.sidebar = ft.Container(
            width=self.sidebar_expanded_width,
            bgcolor=colors.sidebar_bg,
            content=ft.Column(sidebar_content, expand=True),
            animate=ft.Animation(300, ft.AnimationCurve.EASE_IN_OUT),
            border=ft.border.only(right=ft.BorderSide(1, colors.border)),
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=20,
                color=colors.shadow,
                offset=ft.Offset(2, 0)
            )
        )

        # Store menu containers for later reference when updating selection
        self.menu_containers = menu_containers

        # Content area will hold the active view (themed)
        self.content_area = ft.Container(
            expand=True,
            alignment=ft.alignment.top_left,
            bgcolor=colors.bg
        )

        # Layout with fixed sidebar width and flexible content
        self.layout = ft.Row(
            [
                self.sidebar,
                ft.Container(expand=True, content=self.content_area)
            ],
            spacing=0,
            expand=True
        )

        # Start with login
        self.show_login()
        print("Initial view setup complete")

        # Update page
        page.update()

    def show_login(self):
        """Show the login view with modern styling"""
        try:
            from utils.theme import get_theme_colors
            colors = get_theme_colors(self.page.theme_mode)
            
            # Create login form with proper fields
            self.email_field = ft.TextField(
                label="Email",
                border_radius=5,
                prefix_icon=Icons.EMAIL,
                value=""
            )
            
            self.password_field = ft.TextField(
                label="Password",
                border_radius=5,
                prefix_icon=Icons.LOCK,
                password=True,
                value=""
            )
            
            self.login_view = ft.Container(
                content=ft.Column([
                    ft.Text("Risk Assessment Login", size=28, weight=ft.FontWeight.BOLD),
                    ft.Container(height=20),
                    self.email_field,
                    self.password_field,
                    ft.Container(height=20),
                    ft.ElevatedButton(
                        "Login",
                        on_click=lambda _: self.page.run_task(self.handle_login()),
                        bgcolor=None,
                        width=200
                    )
                ], width=300, alignment=ft.MainAxisAlignment.CENTER),
                alignment=ft.alignment.center,
                expand=True,
                bgcolor=colors.bg
            )
            self.page.controls = [self.login_view]
            self.page.update()
        except Exception as e:
            print(f"Error showing login: {e}")
            self.page.controls = [ft.Text(f"Error loading login view: {str(e)}")]
            self.page.update()

    async def handle_login(self, e=None):
        """Handle login with real API authentication"""
        email = self.email_field.value
        password = self.password_field.value
        
        if not email or not password:
            # Show inline helper text and snackbar for visibility
            if not email:
                self.email_field.error_text = "Email is required"
            else:
                self.email_field.error_text = None
            if not password:
                self.password_field.error_text = "Password is required"
            else:
                self.password_field.error_text = None
            self.page.update()
            self.show_snackbar("Please enter both email and password")
            return
        
        try:
            print(f"Attempting to login with email: {email}")
            # Authenticate with the API
            user = await self.auth_controller.login(email, password)
            if user:
                print(f"Login successful for user: {user.email}")
                # Convert User object to dict for compatibility with existing code
                user_dict = {
                    'id': user.id,
                    'username': user.username,
                    'name': user.name,
                    'email': user.email,
                    'role': user.role,
                    'department': user.department
                }
                print(f"Login successful for user: {user_dict}")
                self.current_user = user_dict
                await self.on_login()
            else:
                self.show_snackbar("Invalid credentials", ft.colors.RED)
        except Exception as e:
            print(f"Login error: {e}")
            self.show_snackbar(f"Login failed: {str(e)}", ft.colors.RED)

    def show_snackbar(self, message, color=ft.colors.BLUE):
        """Show a snackbar message"""
        snackbar = ft.SnackBar(content=ft.Text(message), bgcolor=color)
        self.page.snack_bar = snackbar
        snackbar.open = True
        self.page.update()

    async def on_login(self):
        """Handle successful login"""
        try:
            print("Initializing views")
            
            # Initialize views
            from api.auditing_client import AuditingAPIClient
            auditing_client = AuditingAPIClient()
            
            # Create modern dashboard view
            dashboard_view = DashboardView(
                self.page,
                auditing_client,
                self.on_navigate,
                self.current_user
            )
            dashboard_view.build()
            self.views["dashboard"] = dashboard_view

            # Initialize other views
            self.views["departments"] = DepartmentsView(self.page)
            self.views["projects"] = ProjectsView(self.page)
            self.views["users"] = UserManagementView(self.page, self.current_user)

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
        print(f"Showing view: {view_name}")

        try:
            # Lazy initialization of views
            if view_name not in self.views:
                if view_name == "departments":
                    self.views[view_name] = DepartmentsView(self.page)
                elif view_name == "projects":
                    self.views[view_name] = ProjectsView(self.page)
                elif view_name == "users":
                    self.views[view_name] = UserManagementView(self.page, self.current_user)
                elif view_name == "assessments":
                    try:
                        assessment_view = AssessmentListView(
                            self.page,
                            self.current_user,
                            reference_id=self.current_reference_id,
                            initial_filter=self.pending_assessment_filter or {}
                        )
                        self.pending_assessment_filter = None
                        self.views[view_name] = assessment_view
                    except Exception as e:
                        print(f"Error creating assessment view: {e}")
                        self.views[view_name] = ft.Container(
                            content=ft.Text(f"Error loading assessments view: {str(e)}", color=ft.colors.RED),
                            padding=20,
                            expand=True
                        )
                elif view_name == "settings":
                    self.views[view_name] = self.create_settings_view()

            # Set the content area to the selected view
            if view_name in self.views:
                print(f"Setting content area to {view_name} view")
                self.content_area.content = self.views[view_name]
                self.page.update()
            else:
                print(f"View {view_name} not found")
                
        except Exception as e:
            print(f"Error showing view {view_name}: {e}")
            self.content_area.content = ft.Text(f"Error loading {view_name} view: {str(e)}")
            self.page.update()

    def create_settings_view(self):
        """Create the settings view with theme toggle"""
        from utils.theme import get_theme_colors
        colors = get_theme_colors(self.page.theme_mode)
        
        # Theme toggle buttons
        light_button = ft.ElevatedButton(
            "Light Mode",
            disabled=self.page.theme_mode == ft.ThemeMode.LIGHT,
            on_click=lambda e: self.change_theme(e, ft.ThemeMode.LIGHT, light_button, dark_button)
        )
        
        dark_button = ft.ElevatedButton(
            "Dark Mode", 
            disabled=self.page.theme_mode == ft.ThemeMode.DARK,
            on_click=lambda e: self.change_theme(e, ft.ThemeMode.DARK, light_button, dark_button)
        )

        return ft.Container(
            content=ft.Column([
                ft.Text("Settings", size=24, weight=ft.FontWeight.BOLD, color=colors.text_primary),
                ft.Container(height=20),
                ft.Text("Theme", size=18, weight=ft.FontWeight.BOLD, color=colors.text_primary),
                ft.Container(height=10),
                ft.Row([light_button, dark_button], spacing=10),
            ], spacing=10),
            padding=20,
            bgcolor=colors.bg,
            expand=True
        )

    def change_theme(self, e, theme_mode, light_button, dark_button):
        """Change the theme of the application across all views with modern 2025 styling"""
        from utils.theme import get_theme_colors

        self.page.theme_mode = theme_mode
        self.page.theme = ft.Theme(color_scheme_seed="#3B82F6")

        colors = get_theme_colors(theme_mode)

        # Update sidebar with modern styling
        if hasattr(self, "sidebar") and self.sidebar:
            self.sidebar.bgcolor = colors.sidebar_bg
            self.sidebar.border = ft.border.only(right=ft.BorderSide(1, colors.border))
            self.sidebar.shadow = ft.BoxShadow(
                spread_radius=0,
                blur_radius=20,
                color=colors.shadow,
                offset=ft.Offset(2, 0)
            )

        # Update content area
        if hasattr(self, "content_area") and self.content_area:
            self.content_area.bgcolor = colors.bg

        # Update all menu items with modern styling
        if hasattr(self, "menu_containers"):
            menu_icons = [Icons.DASHBOARD, Icons.ASSESSMENT, Icons.APARTMENT, Icons.WORK, Icons.PEOPLE, Icons.SETTINGS]
            menu_items = [
                {"text": "Dashboard", "index": 0},
                {"text": "Assessments", "index": 1},
                {"text": "Departments", "index": 2},
                {"text": "Projects", "index": 3},
                {"text": "Users", "index": 4},
                {"text": "Settings", "index": 5},
            ]
            
            for i, menu_item in enumerate(self.menu_containers):
                is_active = menu_item.data == self.current_nav_index
                if not self.sidebar_collapsed:
                    menu_item.content = ft.Row([
                        ft.Container(
                            content=ft.Icon(menu_icons[i], color=colors.primary if is_active else colors.sidebar_text, size=20),
                            width=40,
                            alignment=ft.alignment.center
                        ),
                        ft.Text(
                            menu_items[i]["text"], 
                            color=colors.primary if is_active else colors.sidebar_text,
                            weight=ft.FontWeight.BOLD if is_active else ft.FontWeight.NORMAL,
                            size=14
                        )
                    ], spacing=12)
                menu_item.bgcolor = colors.sidebar_item_active if is_active else None

        # Update all instantiated views with modern theme
        for view_instance in self.views.values():
            if hasattr(view_instance, "apply_theme"):
                try:
                    view_instance.apply_theme(colors)
                except Exception as ex:
                    print(f"Error applying theme to view {type(view_instance).__name__}: {ex}")

        # Update theme toggle buttons with modern styling
        if theme_mode == ft.ThemeMode.LIGHT:
            light_button.disabled = True
            light_button.bgcolor = colors.primary
            light_button.color = colors.button_text
            dark_button.disabled = False
            dark_button.bgcolor = colors.button_secondary
            dark_button.color = colors.text_primary
        else:
            light_button.disabled = False
            light_button.bgcolor = colors.button_secondary
            light_button.color = colors.text_primary
            dark_button.disabled = True
            dark_button.bgcolor = colors.primary
            dark_button.color = colors.button_text
        
        self.page.update()

    def update_sidebar_selection(self):
        """Update the sidebar to reflect the current selection"""
        try:
            from utils.theme import get_theme_colors
            colors = get_theme_colors(self.page.theme_mode)
            
            for menu_item in self.menu_containers:
                is_active = menu_item.data == self.current_nav_index
                menu_item.bgcolor = colors.sidebar_item_active if is_active else None
                
                # Update icon and text colors
                if hasattr(menu_item.content, 'controls'):
                    for control in menu_item.content.controls:
                        if isinstance(control, ft.Container) and hasattr(control.content, 'name'):  # Icon
                            control.content.color = colors.primary if is_active else colors.sidebar_text
                        elif isinstance(control, ft.Text):  # Text
                            control.color = colors.primary if is_active else colors.sidebar_text
                            control.weight = ft.FontWeight.BOLD if is_active else ft.FontWeight.NORMAL
            
            self.page.update()
        except Exception as e:
            print(f"Error updating sidebar: {e}")


async def main(page: ft.Page):
    app = RiskAssessmentApp()
    await app.main(page)


if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.FLET_APP)
