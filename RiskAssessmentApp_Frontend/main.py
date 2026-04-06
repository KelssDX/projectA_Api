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
from src.views.dashboard.modern_heatmap_dashboard import ModernHeatmapDashboard
from src.views.analytics.analytical_dashboard import AnalyticalDashboard
from src.views.audit_universe.audit_universe_view import AuditUniverseView
from src.views.notifications.notifications_center_view import NotificationsCenterView
from src.views.reviews.review_signoff_view import ReviewSignoffView
from src.views.workflows.workflow_inbox_view import WorkflowInboxView
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
        self.assessment_controller = AssessmentController(self.current_user)
        self.current_reference_id = None
        self.pending_assessment_filter = None
        self.auditing_client = None
        self.platform_config = {}
        self.feature_flags = {}
        # Initialize UI components state
        self.sidebar = None
        self.layout = None
        self.content_area = None

    async def main(self, page: ft.Page):
        # Set up the page
        page.title = "Audit Management Application"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.window_width = 1200
        page.window_height = 800
        page.padding = 0
        
        # Clear Flet's internal session to prevent state conflicts
        try:
            page.session.clear()
        except:
            pass
        
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
                # DEBUG: Check sidebar state BEFORE navigation
                if hasattr(self, 'sidebar') and hasattr(self.sidebar, 'content'):
                    print(f"DEBUG [BEFORE NAV]: Sidebar.content has {len(self.sidebar.content.controls)} controls")
                
                self.current_nav_index = index
                view_name = self._view_name_for_index(index)
                self.show_view(view_name)
                self.update_sidebar_selection()
                
                # DEBUG: Check sidebar state AFTER navigation
                if hasattr(self, 'sidebar') and hasattr(self.sidebar, 'content'):
                    print(f"DEBUG [AFTER NAV]: Sidebar.content has {len(self.sidebar.content.controls)} controls")
            except Exception as e:
                print(f"Error in nav_change: {e}")

        def on_navigate(view_name, subview=None, params=None):
            """Handle navigation requests from views"""
            try:
                if isinstance(params, dict):
                    if view_name == "assessments":
                        ref_id = params.get("reference_id") or params.get("referenceId")
                        if ref_id is not None:
                            self.current_reference_id = ref_id
                        if subview != "details":
                            # Store list-level filters only; details navigation manages its own state.
                            self.pending_assessment_filter = params
                
                if subview == "form":
                    # Handle form navigation
                    self.show_view(f"{view_name}_form")
                elif subview == "details":
                    assessment_id = None
                    reference_id = None
                    initial_tab = 0
                    if isinstance(params, dict):
                        assessment_id = params.get("id") or params.get("assessment_id")
                        reference_id = params.get("reference_id") or params.get("referenceId") or assessment_id
                        initial_tab = params.get("initial_tab", 0)

                    self._open_assessment_details(
                        assessment_id=assessment_id,
                        reference_id=reference_id,
                        initial_tab=initial_tab,
                    )
                else:
                    # Regular view navigation
                    self.show_view(view_name)
            except Exception as e:
                print(f"Error in on_navigate: {e}")

        self.on_navigate = on_navigate

        # Don't create sidebar yet - will be created in on_login()
        self.sidebar = None
        self.menu_containers = []
        self.layout = None
        
        # Content area will hold the active view (themed)
        self.content_area = ft.Container(
            expand=True,
            alignment=ft.alignment.top_left,
            bgcolor=colors.bg
        )

        # Check for stored session and auto-login if exists
        stored_user = await self.check_stored_session()
        if stored_user:
            print(f"Restored session for user: {stored_user.get('email')}")
            self.current_user = stored_user
            await self.on_login()
        else:
            self.show_login()
        print("Initial view setup complete")

        # Update page
        page.update()

    async def check_stored_session(self):
        """Check if there's a stored user session in client storage"""
        try:
            import json
            print("DEBUG: Checking for stored session...")
            stored_data = await self.page.client_storage.get_async("user_session")
            print(f"DEBUG: Stored data retrieved: {stored_data is not None}")
            if stored_data:
                user_dict = json.loads(stored_data)
                if user_dict and user_dict.get('email'):
                    print(f"DEBUG: Found stored session for: {user_dict.get('email')}")
                    return user_dict
            print("DEBUG: No valid stored session found")
        except Exception as e:
            print(f"Error checking stored session: {e}")
            import traceback
            traceback.print_exc()
        return None

    async def save_session(self, user_dict):
        """Save user session to client storage for persistence"""
        try:
            import json
            await self.page.client_storage.set_async("user_session", json.dumps(user_dict))
            print(f"Session saved for user: {user_dict.get('email')}")
        except Exception as e:
            print(f"Error saving session: {e}")

    async def clear_session(self):
        """Clear stored session on logout"""
        try:
            await self.page.client_storage.remove_async("user_session")
            print("Session cleared")
        except Exception as e:
            print(f"Error clearing session: {e}")

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
                    ft.Text("Audit Platform Login", size=28, weight=ft.FontWeight.BOLD),
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
            
            # Clear page and show login (no sidebar)
            self.page.controls.clear()
            self.page.controls.append(self.login_view)
            self.page.update()
            
            print("DEBUG: Login screen shown (no sidebar)")
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
                # Save session for persistence across page refreshes
                await self.save_session(user_dict)
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

    def _format_assessment_id(self, assessment_id=None, reference_id=None):
        if isinstance(assessment_id, str) and assessment_id.strip():
            return assessment_id
        if isinstance(assessment_id, int):
            return f"A-{assessment_id:03d}"
        if isinstance(reference_id, int):
            return f"A-{reference_id:03d}"
        if isinstance(reference_id, str):
            raw = reference_id.strip()
            if raw.startswith("A-"):
                return raw
            try:
                return f"A-{int(raw):03d}"
            except ValueError:
                return raw or None
        return None

    def _return_to_assessments(self):
        self.current_reference_id = None
        self.pending_assessment_filter = None
        self.views.pop("assessments", None)
        self.show_view("assessments")

    def _show_assessments_shell_state(self):
        self.current_nav_index = self._view_index_for_name("assessments")
        self.update_sidebar_selection()

    def _open_assessment_edit_form(self, reference_id, on_cancel=None):
        try:
            from src.views.assessments.unified_form import UnifiedAssessmentForm
        except Exception as ex:
            print(f"Error importing edit form: {ex}")
            self.show_snackbar("Unable to open edit form.", ft.Colors.RED)
            return

        async def load_and_edit():
            try:
                controller = AssessmentController(self.current_user)
                assessment_data = await controller.get_risk_assessment(reference_id)
                if not assessment_data:
                    self.show_snackbar("Audit file details could not be loaded for editing.", ft.Colors.RED)
                    return

                edit_form = UnifiedAssessmentForm(
                    self.page,
                    self.current_user,
                    mode="edit",
                    reference_id=reference_id,
                    assessment=assessment_data,
                    on_cancel=on_cancel or self._return_to_assessments,
                )
                self._show_assessments_shell_state()
                self.content_area.content = edit_form
                self.page.update()
            except Exception as ex:
                print(f"Error loading edit form: {ex}")
                try:
                    print(traceback.format_exc())
                except Exception:
                    pass
                self.show_snackbar("Unable to open the edit view for this audit file.", ft.Colors.RED)

        self.page.run_task(load_and_edit)

    def _open_assessment_details(self, assessment_id=None, reference_id=None, initial_tab=0):
        resolved_reference_id = reference_id or assessment_id
        resolved_assessment_id = self._format_assessment_id(assessment_id=assessment_id, reference_id=resolved_reference_id)
        self.current_reference_id = resolved_reference_id
        self.pending_assessment_filter = None

        def go_back():
            self._return_to_assessments()

        def edit_assessment(ref_id):
            self._open_assessment_edit_form(ref_id, on_cancel=go_back)

        try:
            from src.views.assessments.modern_details import ModernAssessmentDetails

            details_view = ModernAssessmentDetails(
                self.page,
                self.current_user,
                assessment_id=resolved_assessment_id,
                reference_id=resolved_reference_id,
                on_back=go_back,
                on_edit=edit_assessment,
                initial_tab=initial_tab,
            )
            self._show_assessments_shell_state()
            self.content_area.content = details_view
            self.page.update()
            return
        except Exception as ex:
            print(f"Error loading modern details view: {ex}")
            try:
                print(traceback.format_exc())
            except Exception:
                pass

        try:
            from src.views.assessments.details import AssessmentDetailsView

            fallback_view = AssessmentDetailsView(
                self.page,
                self.current_user,
                assessment_id=resolved_assessment_id,
                on_back=go_back,
            )
            self._show_assessments_shell_state()
            self.content_area.content = fallback_view
            self.page.update()
            self.show_snackbar("Opened audit file in the fallback details view.", ft.Colors.ORANGE)
        except Exception as ex:
            print(f"Error loading fallback details view: {ex}")
            try:
                print(traceback.format_exc())
            except Exception:
                pass
            self.show_snackbar("Unable to open this audit file right now.", ft.Colors.RED)
            self._return_to_assessments()

    async def on_login(self):
        """Handle successful login"""
        try:
            print("Initializing views")
            self.assessment_controller = AssessmentController(self.current_user)
            
            # Initialize views
            from src.api.auditing_client import AuditingAPIClient
            self.auditing_client = AuditingAPIClient()
            self.auditing_client.set_current_user(self.current_user)
            await self._load_platform_configuration()
            
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

            # Clear any stale nav state
            try:
                await self.page.client_storage.remove_async("last_nav_index")
            except:
                pass

            # Initialize sidebar only if not already created
            if not self.sidebar:
                from src.components.sidebar import Sidebar
                
                def nav_change_handler(index):
                    print(f"Navigation change to index: {index}")
                    try:
                        # DEBUG: Check sidebar state BEFORE navigation
                        if hasattr(self, 'sidebar') and self.sidebar:
                            print(f"DEBUG [BEFORE NAV]: Sidebar exists")
                        
                        self.current_nav_index = index
                        view_name = self._view_name_for_index(index)
                        self.show_view(view_name)
                        if hasattr(self.sidebar, 'update_selection'):
                            self.sidebar.update_selection(index)
                            self.page.update()
                        
                        # DEBUG: Check sidebar state AFTER navigation  
                        if hasattr(self, 'sidebar') and self.sidebar:
                            print(f"DEBUG [AFTER NAV]: Sidebar still exists")
                    except Exception as e:
                        print(f"Error in nav_change: {e}")
                        import traceback
                        traceback.print_exc()
                
                # Create the sidebar as a self-contained component
                self.sidebar = Sidebar(
                    page=self.page,
                    current_user=self.current_user,
                    nav_change_callback=nav_change_handler,
                    current_nav_index=self.current_nav_index,
                    feature_flags=self.feature_flags
                )
                print(f"DEBUG: Created NEW Sidebar component")
            else:
                # Update existing sidebar with current user and callback if needed
                self.sidebar.current_user = self.current_user
                self.sidebar.feature_flags = self.feature_flags
                # Re-bind callback to ensure it uses current context
                # (Optional depending on if context changed, but safe to do)
                print(f"DEBUG: Reusing EXISTING Sidebar component")

            # Initialize layout only if not already created
            if not self.layout:
                self.layout = ft.Row(
                    [self.sidebar, ft.Container(expand=True, content=self.content_area)],
                    spacing=0,
                    expand=True
                )
                print("DEBUG: Created NEW layout with Sidebar component")
            else:
                print("DEBUG: Reusing EXISTING layout")
            
            # Ensure layout is the only control on the page
            self.page.controls.clear()
            self.page.controls.append(self.layout)
            self.page.update()
            
            print("DEBUG: Page updated with Sidebar component")
            
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
            
            # Force full page update
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
        view_name = self._normalize_shell_view_name(view_name)
        print(f"Showing view: {view_name}")
        if not self._is_view_enabled(view_name):
            self.show_snackbar(f"{view_name.replace('_', ' ').title()} is disabled in this environment.", ft.Colors.ORANGE)
            return

        if view_name == "assessments" and not self.pending_assessment_filter:
            self.current_reference_id = None
        
        # DEBUG: Check sidebar state at start of show_view
        if hasattr(self, 'sidebar') and hasattr(self.sidebar, 'content'):
            print(f"DEBUG [show_view START]: Sidebar has {len(self.sidebar.content.controls)} controls")
            print(f"DEBUG [show_view START]: Sidebar object id: {id(self.sidebar)}")
            print(f"DEBUG [show_view START]: Sidebar.content object id: {id(self.sidebar.content)}")

        try:
            # Lazy initialization of views
            if view_name not in self.views:
                if view_name == "dashboard":
                    # Safely (re)create the dashboard if needed
                    try:
                        from src.api.auditing_client import AuditingAPIClient
                        if self.auditing_client is None:
                            self.auditing_client = AuditingAPIClient()
                        self.auditing_client.set_current_user(self.current_user)
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
                    try:
                        heatmap_view = ModernHeatmapDashboard(
                            self.page, 
                            self.current_user
                        )
                        self.views[view_name] = heatmap_view
                    except Exception as e:
                        print(f"Error creating heatmap view: {e}")
                        self.views[view_name] = ft.Container(
                            content=ft.Text(f"Error loading heatmap view: {str(e)}", color=ft.Colors.RED),
                            padding=20,
                            expand=True
                        )
                elif view_name == "analytics":
                    try:
                        analytics_view = AnalyticalDashboard(
                            self.page,
                            self.current_user,
                            on_navigate=self.on_navigate,
                            platform_config=self.platform_config
                        )
                        self.views[view_name] = analytics_view
                    except Exception as e:
                        print(f"Error creating analytics view: {e}")
                        self.views[view_name] = ft.Container(
                            content=ft.Text(f"Error loading analytics view: {str(e)}", color=ft.Colors.RED),
                            padding=20,
                            expand=True
                        )
                elif view_name == "audit_universe":
                    try:
                        audit_universe_view = AuditUniverseView(self.page)
                        self.views[view_name] = audit_universe_view
                    except Exception as e:
                        print(f"Error creating audit universe view: {e}")
                        self.views[view_name] = ft.Container(
                            content=ft.Text(f"Error loading audit universe view: {str(e)}", color=ft.Colors.RED),
                            padding=20,
                            expand=True
                        )
                elif view_name == "workflows":
                    try:
                        workflow_view = WorkflowInboxView(
                            self.page,
                            self.current_user,
                            on_navigate=self.on_navigate
                        )
                        self.views[view_name] = workflow_view
                    except Exception as e:
                        print(f"Error creating workflow inbox view: {e}")
                        self.views[view_name] = ft.Container(
                            content=ft.Text(f"Error loading workflow inbox: {str(e)}", color=ft.Colors.RED),
                            padding=20,
                            expand=True
                        )
                elif view_name == "notifications":
                    try:
                        notifications_view = NotificationsCenterView(
                            self.page,
                            self.current_user,
                            on_navigate=self.on_navigate
                        )
                        self.views[view_name] = notifications_view
                    except Exception as e:
                        print(f"Error creating notifications center: {e}")
                        self.views[view_name] = ft.Container(
                            content=ft.Text(f"Error loading notifications center: {str(e)}", color=ft.Colors.RED),
                            padding=20,
                            expand=True
                        )
                elif view_name == "reviews":
                    try:
                        review_view = ReviewSignoffView(
                            self.page,
                            self.current_user,
                            on_navigate=self.on_navigate
                        )
                        self.views[view_name] = review_view
                    except Exception as e:
                        print(f"Error creating review and sign-off view: {e}")
                        self.views[view_name] = ft.Container(
                            content=ft.Text(f"Error loading review and sign-off view: {str(e)}", color=ft.Colors.RED),
                            padding=20,
                            expand=True
                        )
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
                # If heatmap selected, load its data
                elif view_name == "heatmap":
                    try:
                        if hasattr(self.views[view_name], "load_data"):
                            self.views[view_name].load_data()
                    except Exception:
                        pass
                # If analytics selected, load its data
                elif view_name == "analytics":
                    try:
                        if hasattr(self.views[view_name], "load_data"):
                            self.views[view_name].load_data()
                    except Exception:
                        pass
                elif view_name in {"workflows", "notifications", "reviews"}:
                    try:
                        if hasattr(self.views[view_name], "load_data"):
                            self.page.run_task(self.views[view_name].load_data)
                    except Exception:
                        pass
                # Keep sidebar selection in sync when navigating programmatically
                try:
                    new_index = self._view_index_for_name(view_name)
                    self.current_nav_index = new_index
                    self.update_sidebar_selection()
                except Exception:
                    pass
                
                # DEBUG: Check sidebar state before page.update()
                if hasattr(self, 'sidebar') and hasattr(self.sidebar, 'content'):
                    print(f"DEBUG [show_view BEFORE update]: Sidebar has {len(self.sidebar.content.controls)} controls")
                
                self.page.update()
                self.page.run_task(self._record_module_open_usage, view_name)
                
                # DEBUG: Check sidebar state after page.update()
                if hasattr(self, 'sidebar') and hasattr(self.sidebar, 'content'):
                    print(f"DEBUG [show_view AFTER update]: Sidebar has {len(self.sidebar.content.controls)} controls")
            else:
                print(f"View {view_name} not found")

        except Exception as e:
            print(f"Error showing view {view_name}: {e}")
            self.content_area.content = ft.Text(f"Error loading {view_name} view: {str(e)}")
            self.page.update()

    async def _load_platform_configuration(self):
        if self.auditing_client is None:
            return
        try:
            config = await self.auditing_client.get_platform_configuration()
            self.platform_config = config or {}
            self.feature_flags = self._normalize_feature_flags(self.platform_config.get("featureFlags"))
        except Exception as ex:
            print(f"Failed to load platform configuration: {ex}")
            self.platform_config = {}
            self.feature_flags = {}

    @staticmethod
    def _normalize_feature_flags(flags):
        if not isinstance(flags, dict):
            return {}
        normalized = {}
        for key, value in flags.items():
            normalized_key = "".join(ch if ch.isalnum() else "_" for ch in str(key)).strip("_").lower()
            normalized[normalized_key] = bool(value)
        return normalized

    def _feature_enabled(self, flag_name, default=True):
        return self.feature_flags.get(flag_name, default)

    def _normalize_shell_view_name(self, view_name):
        if view_name == "heatmap":
            return "analytics"
        if view_name == "departments":
            return "audit_universe"
        return view_name

    def _is_view_enabled(self, view_name):
        mapping = {
            "dashboard": "dashboard",
            "assessments": "assessments",
            "heatmap": "heatmap",
            "analytics": "analytics",
            "audit_universe": "audit_universe",
            "departments": "departments",
            "projects": "projects",
            "users": "users_admin",
            "workflows": "workflow_inbox",
            "notifications": "notifications_center",
            "reviews": "review_signoff",
            "settings": None,
        }
        flag_name = mapping.get(view_name)
        return True if flag_name is None else self._feature_enabled(flag_name, True)

    @staticmethod
    def _nav_view_map():
        return {
            0: "dashboard",
            1: "assessments",
            2: "heatmap",
            3: "analytics",
            4: "audit_universe",
            5: "departments",
            6: "projects",
            7: "users",
            8: "workflows",
            9: "notifications",
            10: "reviews",
            11: "settings",
        }

    def _view_name_for_index(self, index):
        return self._nav_view_map().get(index, "dashboard")

    def _view_index_for_name(self, view_name):
        for index, mapped_name in self._nav_view_map().items():
            if mapped_name == view_name:
                return index
        return self.current_nav_index

    async def _record_module_open_usage(self, view_name):
        if self.auditing_client is None:
            return
        try:
            await self.auditing_client.record_usage_event({
                "moduleName": "navigation",
                "featureName": view_name,
                "eventName": "open_view",
                "referenceId": self.current_reference_id,
                "source": "frontend-shell"
            })
        except Exception as ex:
            print(f"Failed to record usage event for {view_name}: {ex}")

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
                    ft.Text("Customize your audit workspace", size=14, color=colors.text_secondary),
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
        from src.utils.theme import get_theme_colors, build_gradient, darken_color, apply_theme_to_control

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

        # Rebuild the sidebar so grouped navigation and labels follow the new theme.
        if hasattr(self, "sidebar") and self.sidebar:
            try:
                self.sidebar._build_sidebar_content(colors)
            except Exception:
                pass

        # Update/rebuild settings view explicitly (it's a simple container)
        try:
            if "settings" in self.views:
                self.views["settings"] = self.create_settings_view()
                # If currently on settings, swap content immediately
                if getattr(self, "current_nav_index", None) == 9 and hasattr(self, "content_area"):
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
            current = self._view_name_for_index(self.current_nav_index)
            self.views = {}
            self.show_view(current)
        except Exception as _:
            pass

    def update_sidebar_selection(self):
        """Update the sidebar to reflect the current selection"""
        try:
            if hasattr(self, 'sidebar') and self.sidebar and hasattr(self.sidebar, 'update_selection'):
                self.sidebar.update_selection(self.current_nav_index)
                self.page.update()
        except Exception as e:
            print(f"Error updating sidebar: {e}")


async def main(page: ft.Page):
    app = RiskAssessmentApp()
    await app.main(page)


if __name__ == "__main__":
    import argparse
    import sys
    
    # Check if running through flet CLI - if so, don't call ft.app()
    # flet CLI handles the app lifecycle itself
    is_flet_cli = 'flet' in sys.modules or any('flet' in str(arg).lower() for arg in sys.argv)
    
    parser = argparse.ArgumentParser(description="Audit Management Application")
    parser.add_argument(
        "--mode", 
        choices=["app", "web"], 
        default="web",
        help="Run mode: 'app' for desktop application, 'web' for web browser (default)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8550,
        help="Port number for web mode (default: 8550)"
    )
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host address for web mode (default: 127.0.0.1, use 0.0.0.0 for external access)"
    )
    
    args, _ = parser.parse_known_args()
    
    assets_dir = "assets" if os.path.exists("assets") else None
    
    print(f"Starting Audit Management App in {'WEB' if args.mode == 'web' else 'DESKTOP'} mode")
    print(f"Access at: http://{args.host}:{args.port}")
    
    if args.mode == "web":
        ft.app(
            target=main,
            view=ft.AppView.WEB_BROWSER,
            assets_dir=assets_dir,
            port=args.port,
            host=args.host
        )
    else:
        ft.app(
            target=main,
            view=ft.AppView.FLET_APP,
            assets_dir=assets_dir,
            port=0,
            host="127.0.0.1"
        )
