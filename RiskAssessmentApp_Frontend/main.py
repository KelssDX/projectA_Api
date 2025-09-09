import flet as ft
from flet import Icons
import os
import asyncio
import traceback

from src.views.dashboard.dashboard import DashboardView
from src.views.assessments.list import AssessmentListView
from src.views.users.user_management import UserManagementView
from src.views.departments.departments_view import DepartmentsView
from src.views.projects.projects_view import ProjectsView
from src.core.config import get_db_connection
from src.controllers.auth_controller import AuthController
from src.controllers.assessment_controller import AssessmentController
from src.models.assessment import Assessment

# Import utility modules
from src.utils.pdf_generator import PDFGenerator
from src.utils.excel_exporter import ExcelExporter


class RiskAssessmentApp:
    def __init__(self):
        self.auth_controller = AuthController()
        self.current_user = None
        self.assessment_controller = AssessmentController()
        self.current_reference_id = None
        self.pending_assessment_filter = None
        self.auditing_client = None

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
        from src.utils.theme import get_theme_colors, create_modern_button
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
                    2: "heatmap",
                    3: "departments",
                    4: "projects",
                    5: "users",
                    6: "settings"
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
                    # Handle details navigation explicitly
                    try:
                        from src.views.assessments.details import AssessmentDetailsView
                        assessment_id = None
                        if isinstance(params, dict):
                            assessment_id = params.get("id") or params.get("assessment_id")

                        def go_back():
                            # Return to list view
                            self.show_view("assessments")

                        details_view = AssessmentDetailsView(
                            self.page,
                            self.current_user,
                            assessment_id=assessment_id,
                            on_back=go_back,
                        )
                        # Swap page content to details
                        if hasattr(self.page, 'controls'):
                            self.page.controls = [self.layout]
                            # Place details in content area next to sidebar
                            self.content_area.content = details_view
                        else:
                            self.content_area.content = details_view
                        self.page.update()
                        return
                    except Exception as _:
                        # Fallback to default view switcher
                        self.show_view(view_name)
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
            {"text": "Risk Heatmap", "index": 2},
            {"text": "Departments", "index": 3},
            {"text": "Projects", "index": 4},
            {"text": "Users", "index": 5},
            {"text": "Settings", "index": 6},
        ]

        # Create modern menu item containers with professional auditing icons
        menu_containers = []
        menu_icons = [
            Icons.DASHBOARD_OUTLINED,     # Dashboard - Clean dashboard outline
            Icons.FACT_CHECK,             # Assessments - Professional fact check/audit icon
            Icons.GRID_ON,                # Risk Heatmap - Clean grid for matrix view
            Icons.DOMAIN,                 # Departments - Corporate building/domain
            Icons.WORK_OUTLINE,           # Projects - Professional work briefcase outline
            Icons.ADMIN_PANEL_SETTINGS,   # Users - Admin panel for user management
            Icons.SETTINGS_OUTLINED       # Settings - Clean settings outline
        ]
        
        for i, item in enumerate(menu_items):
            index = item["index"]
            is_active = (index == self.current_nav_index)
            
            active_label_color = colors.button_text if is_active else colors.sidebar_text
            active_icon_color = colors.button_text if is_active else colors.sidebar_text
            menu_item = ft.Container(
                content=ft.Row([
                    ft.Container(
                        content=ft.Icon(menu_icons[i], color=active_icon_color, size=20),
                        width=40,
                        alignment=ft.alignment.center
                    ),
                    ft.Text(
                        item["text"], 
                        color=active_label_color,
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

        # Modern user profile section - derive real initials, name and role; remove yellow
        initials = "A"
        full_name = "User"
        role_text = ""
        if isinstance(self.current_user, dict):
            full_name = self.current_user.get("name") or self.current_user.get("username") or "User"
            initials = (self.current_user.get("username") or full_name or "A")[:1].upper()
            role_text = (self.current_user.get("role") or "").title()
        else:
            full_name = getattr(self.current_user, "name", None) or getattr(self.current_user, "username", "User")
            initials = (getattr(self.current_user, "username", None) or full_name or "A")[:1].upper()
            role_text = (getattr(self.current_user, "role", "") or "").title()

        # elements reused for runtime updates
        self.user_initials_text = ft.Text(initials, color=colors.button_text, size=16, weight=ft.FontWeight.BOLD)
        self.user_name_text = ft.Text(
            full_name,
            size=14,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.WHITE,
            max_lines=1,
            overflow=ft.TextOverflow.ELLIPSIS,
            tooltip=full_name
        )
        self.user_role_text = ft.Text(
            role_text or "",
            size=12,
            color=ft.Colors.WHITE70,
            max_lines=1,
            overflow=ft.TextOverflow.ELLIPSIS,
            tooltip=role_text or ""
        )

        user_profile = ft.Container(
            padding=ft.padding.all(16),
            content=ft.Container(
                padding=ft.padding.all(12),
                # Apple-like darker purple gradient background for the badge
                gradient=ft.LinearGradient(
                    begin=ft.alignment.top_left,
                    end=ft.alignment.bottom_right,
                    colors=["#2E1065", "#4C1D95", "#6D28D9"]
                ),
                border_radius=16,
                border=ft.border.all(1, ft.Colors.with_opacity(0.3, ft.Colors.WHITE)),
                content=ft.Row([
                    ft.Container(
                        width=40,
                        height=40,
                        # Avatar circle uses the same (darker) gradient as panel for coherence
                        gradient=ft.LinearGradient(
                            begin=ft.alignment.top_left,
                            end=ft.alignment.bottom_right,
                            colors=["#2E1065", "#4C1D95", "#6D28D9"]
                        ),
                        border_radius=20,
                        alignment=ft.alignment.center,
                        content=self.user_initials_text,
                        border=ft.border.all(1, ft.Colors.with_opacity(0.35, ft.Colors.WHITE)),
                        shadow=ft.BoxShadow(
                            spread_radius=0,
                            blur_radius=8,
                            color=colors.shadow,
                            offset=ft.Offset(0, 2)
                        )
                    ),
                    ft.Column([
                        self.user_name_text,
                        self.user_role_text
                    ], spacing=2, expand=True)
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
                    label_color = colors.button_text if is_active else colors.sidebar_text
                    icon_color = colors.button_text if is_active else colors.sidebar_text
                    menu_item.content = ft.Row([
            ft.Container(
                            content=ft.Icon(menu_icons[i], color=icon_color, size=20),
                            width=40,
                            alignment=ft.alignment.center
                        ),
                        ft.Text(
                            menu_items[i]["text"], 
                            color=label_color,
                            weight=ft.FontWeight.BOLD if is_active else ft.FontWeight.NORMAL,
                            size=14
                        )
                    ], spacing=12)
                    # Apply gradient to active item
                    try:
                        from src.utils.theme import build_gradient
                        if is_active:
                            menu_item.gradient = build_gradient(colors.sidebar_item_active)
                            menu_item.bgcolor = None
                        else:
                            menu_item.gradient = None
                            menu_item.bgcolor = None
                    except Exception:
                        pass
                    menu_item.margin = ft.margin.symmetric(horizontal=8, vertical=2)
            
            # Always keep icons + labels visible on selection
            for i, menu_item in enumerate(menu_containers):
                is_active = menu_item.data == self.current_nav_index
                if hasattr(menu_item, 'content') and isinstance(menu_item.content, ft.Row) and len(menu_item.content.controls) >= 2:
                    # Icon
                    if hasattr(menu_item.content.controls[0], 'content') and isinstance(menu_item.content.controls[0].content, ft.Icon):
                        menu_item.content.controls[0].content.color = colors.button_text if is_active else colors.sidebar_text
                    # Label
                    if isinstance(menu_item.content.controls[1], ft.Text):
                        menu_item.content.controls[1].color = colors.button_text if is_active else colors.sidebar_text

            # Hide/show elements based on collapsed state
            user_profile.visible = not self.sidebar_collapsed
            header_title.visible = not self.sidebar_collapsed
            
            self.sidebar.update()

        # Modern sidebar header
        header_title = ft.Text("Risk Core", size=20, weight=ft.FontWeight.BOLD, color=colors.sidebar_text)
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
        from src.utils.theme import build_gradient, darken_color
        base_shade = colors.sidebar_bg
        self.sidebar = ft.Container(
            width=self.sidebar_expanded_width,
            gradient=build_gradient(base_shade if self.page.theme_mode == ft.ThemeMode.LIGHT else darken_color(base_shade, 0.35)),
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
            from src.utils.theme import get_theme_colors
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
                        on_click=self.handle_login_click,
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

    def handle_login_click(self, e):
        """Handle login button click and run async login"""
        self.page.run_task(self.handle_login)

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
                self.show_snackbar("Invalid credentials", ft.Colors.RED)
        except Exception as e:
            print(f"Login error: {e}")
            self.show_snackbar(f"Login failed: {str(e)}", ft.Colors.RED)

    def show_snackbar(self, message, color=ft.Colors.BLUE):
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
            from src.api.auditing_client import AuditingAPIClient
            self.auditing_client = AuditingAPIClient()
            
            # Create modern dashboard view
            self.views["dashboard"] = DashboardView(
                self.page,
                self.auditing_client,
                self.on_navigate,
                self.current_user
            )
            # Load dashboard stats and recent assessments
            try:
                if hasattr(self.views["dashboard"], "load_dashboard_data"):
                    self.page.run_task(self.views["dashboard"].load_dashboard_data)
            except Exception:
                pass

            # Initialize other views
            self.views["departments"] = DepartmentsView(self.page)
            self.views["projects"] = ProjectsView(self.page)
            self.views["users"] = UserManagementView(self.page, self.current_user)

            # Show main application
            self.page.controls = [self.layout]
            self.show_view("dashboard")
            # Update user badge with real values post-login
            try:
                if hasattr(self, 'user_name_text') and isinstance(self.user_name_text, ft.Text):
                    self.user_name_text.value = self.current_user.get('name') or self.current_user.get('username') or 'User'
                if hasattr(self, 'user_initials_text') and isinstance(self.user_initials_text, ft.Text):
                    self.user_initials_text.value = (self.current_user.get('username') or self.current_user.get('name') or 'U')[:1].upper()
                if hasattr(self, 'user_role_text') and isinstance(self.user_role_text, ft.Text):
                    self.user_role_text.value = (self.current_user.get('role') or '').title()
            except Exception:
                pass
            self.page.update()
        except Exception as e:
            print(f"Error in on_login: {e}")
            try:
                print(traceback.format_exc())
            except Exception:
                pass
            self.page.controls = [ft.Text(f"Error after login: {str(e)}")]
            self.page.update()

    def show_view(self, view_name):
        """Switch to a specific view"""
        print(f"Showing view: {view_name}")

        try:
            # Lazy initialization of views
            if view_name not in self.views:
                if view_name == "dashboard":
                    # Safely (re)create the dashboard if needed
                    try:
                        from src.api.auditing_client import AuditingAPIClient
                        if self.auditing_client is None:
                            self.auditing_client = AuditingAPIClient()
                        self.views[view_name] = DashboardView(
                            self.page, self.auditing_client, self.on_navigate, self.current_user
                        )
                    except Exception as e:
                        print(f"Error creating dashboard view: {e}")
                        self.views[view_name] = ft.Container(
                            content=ft.Text(f"Error loading dashboard: {str(e)}", color=ft.Colors.RED),
                            padding=20,
                            expand=True
                        )
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
                            content=ft.Text(f"Error loading assessments view: {str(e)}", color=ft.Colors.RED),
                            padding=20,
                            expand=True
                        )
                elif view_name == "heatmap":
                    from src.views.dashboard.heatmap import HeatmapView
                    heatmap_view = HeatmapView(
                        self.page, 
                        self.current_user,
                        on_navigate=self.on_navigate
                    )
                    self.views[view_name] = heatmap_view
                    # Load data when view is created
                    if hasattr(heatmap_view, 'load_data'):
                        heatmap_view.load_data()
                elif view_name == "settings":
                    self.views[view_name] = self.create_settings_view()

            # Set the content area to the selected view (always rebuild lazily for dashboard)
            if view_name in self.views:
                print(f"Setting content area to {view_name} view")
                # For dashboard specifically, ensure an instance exists and is up to date
                if view_name == "dashboard" and not isinstance(self.views[view_name], DashboardView):
                    try:
                        self.views[view_name] = DashboardView(self.page, self.auditing_client, self.on_navigate, self.current_user)
                    except Exception:
                        pass
                self.content_area.content = self.views[view_name]
                # Normalize colors for the inserted view based on current theme
                try:
                    from src.utils.theme import get_theme_colors, apply_theme_to_control
                    colors = get_theme_colors(self.page.theme_mode)
                    apply_theme_to_control(self.content_area.content, colors)
                except Exception:
                    pass
                # If dashboard selected, refresh its data
                if view_name == "dashboard":
                    try:
                        if hasattr(self.views[view_name], "load_dashboard_data"):
                            self.page.run_task(self.views[view_name].load_dashboard_data)
                    except Exception:
                        pass
                # Keep sidebar selection in sync when navigating programmatically
                try:
                    index_map = {
                        "dashboard": 0,
                        "assessments": 1,
                        "heatmap": 2,
                        "departments": 3,
                        "projects": 4,
                        "users": 5,
                        "settings": 6,
                    }
                    new_index = index_map.get(view_name, self.current_nav_index)
                    self.current_nav_index = new_index
                    self.update_sidebar_selection()
                except Exception:
                    pass
                self.page.update()
            else:
                print(f"View {view_name} not found")

        except Exception as e:
            print(f"Error showing view {view_name}: {e}")
            self.content_area.content = ft.Text(f"Error loading {view_name} view: {str(e)}")
            self.page.update()

    def create_settings_view(self):
        """Create the settings view with dashboard-style layout and theme toggle"""
        from src.utils.theme import (
            get_theme_colors,
            build_gradient,
            darken_color,
            apply_theme_to_control,
            create_modern_card,
        )
        colors = get_theme_colors(self.page.theme_mode)

        # Header (Dashboard-style)
        header = ft.Container(
            content=ft.Row([
                ft.Column([
                    ft.Text("Settings", size=24, weight=ft.FontWeight.BOLD, color=colors.text_primary),
                    ft.Text("Customize your Risk Core experience", size=14, color=colors.text_secondary),
                ], alignment=ft.CrossAxisAlignment.START),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        )

        # Theme toggle buttons (keep ElevatedButton to integrate with change_theme state)
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

        theme_card = create_modern_card(
            colors,
            ft.Column([
                ft.Text("Theme", size=18, weight=ft.FontWeight.BOLD, color=colors.text_primary),
                ft.Container(height=10),
                ft.Row([light_button, dark_button], spacing=10),
                ft.Container(height=8),
                ft.Text("Switch between light and dark modes. Changes apply instantly across all views.", size=12, color=colors.text_secondary)
            ], spacing=8)
        )

        # Appearance / Info card (optional, keeps layout consistent)
        info_card = create_modern_card(
            colors,
            ft.Column([
                ft.Text("Appearance", size=18, weight=ft.FontWeight.BOLD, color=colors.text_primary),
                ft.Container(height=8),
                ft.Text("The interface uses modern 2025 styling with gradient sidebar and glass cards.", size=12, color=colors.text_secondary)
            ], spacing=8)
        )

        content_column = ft.Column([
            header,
            ft.Container(height=16),
            theme_card,
            ft.Container(height=12),
            info_card,
        ], spacing=0)

        settings_view = ft.Container(
            content=content_column,
            padding=ft.padding.all(24),
            bgcolor=colors.bg,
            expand=True
        )

        # In dark mode keep page surface darker than panel surfaces
        try:
            from src.utils.theme import apply_theme_to_control
            apply_theme_to_control(settings_view, colors)
        except Exception:
            pass

        return settings_view

    def change_theme(self, e, theme_mode, light_button, dark_button):
        """Change the theme of the application across all views with modern 2025 styling"""
        from src.utils.theme import get_theme_colors

        self.page.theme_mode = theme_mode
        self.page.theme = ft.Theme(color_scheme_seed="#3B82F6")

        colors = get_theme_colors(theme_mode)

        # Update sidebar with modern styling (theme-aware gradient)
        if hasattr(self, "sidebar") and self.sidebar:
            try:
                base = colors.sidebar_bg
                shade = base if theme_mode == ft.ThemeMode.LIGHT else darken_color(base, 0.35)
                self.sidebar.gradient = build_gradient(shade)
                self.sidebar.bgcolor = None
            except Exception:
                self.sidebar.gradient = None
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
            # Normalize colors within current view content
            try:
                if hasattr(self.content_area, "content") and self.content_area.content:
                    apply_theme_to_control(self.content_area.content, colors)
            except Exception as _:
                pass

        # Update all menu items with modern styling
        if hasattr(self, "menu_containers"):
            menu_icons = [
                Icons.DASHBOARD_OUTLINED,     # Dashboard - Clean dashboard outline
                Icons.FACT_CHECK,             # Assessments - Professional fact check/audit icon
                Icons.GRID_ON,                # Risk Heatmap - Clean grid for matrix view
                Icons.DOMAIN,                 # Departments - Corporate building/domain
                Icons.WORK_OUTLINE,           # Projects - Professional work briefcase outline
                Icons.ADMIN_PANEL_SETTINGS,   # Users - Admin panel for user management
                Icons.SETTINGS_OUTLINED       # Settings - Clean settings outline
            ]
            menu_items = [
                {"text": "Dashboard", "index": 0},
                {"text": "Assessments", "index": 1},
                {"text": "Risk Heatmap", "index": 2},
                {"text": "Departments", "index": 3},
                {"text": "Projects", "index": 4},
                {"text": "Users", "index": 5},
                {"text": "Settings", "index": 6},
            ]
            
            for i, menu_item in enumerate(self.menu_containers):
                is_active = menu_item.data == self.current_nav_index
                if not self.sidebar_collapsed:
                    # In both themes, active item text/icon should be white (button_text)
                    active_color = colors.button_text if is_active else colors.sidebar_text
                    menu_item.content = ft.Row([
                        ft.Container(
                            content=ft.Icon(menu_icons[i], color=active_color, size=20),
                            width=40,
                            alignment=ft.alignment.center
                        ),
                        ft.Text(
                            menu_items[i]["text"], 
                            color=active_color,
                            weight=ft.FontWeight.BOLD if is_active else ft.FontWeight.NORMAL,
                            size=14
                        )
                    ], spacing=12)
                # Apply gradient to active item
                try:
                    if is_active:
                        menu_item.gradient = build_gradient(colors.sidebar_item_active)
                        menu_item.bgcolor = None
                    else:
                        menu_item.gradient = None
                        menu_item.bgcolor = None
                except Exception:
                    menu_item.bgcolor = colors.sidebar_item_active if is_active else None

        # Update/rebuild settings view explicitly (it's a simple container)
        try:
            if "settings" in self.views:
                self.views["settings"] = self.create_settings_view()
                # If currently on settings, swap content immediately
                if getattr(self, "current_nav_index", None) == 6 and hasattr(self, "content_area"):
                    self.content_area.content = self.views["settings"]
        except Exception:
            pass

        # Update all instantiated views with modern theme
        for view_instance in self.views.values():
            try:
                if hasattr(view_instance, "apply_theme"):
                    view_instance.apply_theme(colors)
                else:
                    apply_theme_to_control(view_instance, colors)
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

        # Force current view to rebuild from blueprint so changes are visible immediately
        try:
            view_map = {
                0: "dashboard",
                1: "assessments",
                2: "heatmap",
                3: "departments",
                4: "projects",
                5: "users",
                6: "settings",
            }
            current = view_map.get(self.current_nav_index, "dashboard")
            self.views = {}
            self.show_view(current)
        except Exception as _:
            pass

    def update_sidebar_selection(self):
        """Update the sidebar to reflect the current selection"""
        try:
            from src.utils.theme import get_theme_colors, build_gradient
            colors = get_theme_colors(self.page.theme_mode)

            for menu_item in self.menu_containers:
                is_active = menu_item.data == self.current_nav_index

                # Apply gradient highlight only to the active item
                if is_active:
                    try:
                        menu_item.gradient = build_gradient(colors.sidebar_item_active)
                        menu_item.bgcolor = None
                    except Exception:
                        menu_item.gradient = None
                        menu_item.bgcolor = colors.sidebar_item_active
                else:
                    menu_item.gradient = None
                    menu_item.bgcolor = None

                # Update icon and text colors
                if hasattr(menu_item.content, 'controls') and len(menu_item.content.controls) >= 2:
                    icon_holder = menu_item.content.controls[0]
                    label = menu_item.content.controls[1]
                    if isinstance(icon_holder, ft.Container) and hasattr(icon_holder, 'content') and isinstance(icon_holder.content, ft.Icon):
                        icon_holder.content.color = colors.button_text if is_active else colors.sidebar_text
                    if isinstance(label, ft.Text):
                        label.color = colors.button_text if is_active else colors.sidebar_text
                        label.weight = ft.FontWeight.BOLD if is_active else ft.FontWeight.NORMAL

            self.page.update()
        except Exception as e:
            print(f"Error updating sidebar: {e}")


async def main(page: ft.Page):
    app = RiskAssessmentApp()
    await app.main(page)


if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.FLET_APP)
