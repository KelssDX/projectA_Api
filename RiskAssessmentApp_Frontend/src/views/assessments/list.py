import flet as ft
from flet import Icons
import asyncio
from src.utils.theme import (
    get_theme_colors,
    apply_theme_to_control,
    create_modern_card,
    create_modern_button,
)
from src.views.common.base_view import BaseView
from src.models.assessment import Assessment
from datetime import datetime
from src.api.auditing_client import AuditingAPIClient
from src.views.assessments.unified_form import UnifiedAssessmentForm


class AssessmentListView(BaseView):
    def __init__(self, page, user, reference_id=None, initial_filter=None):
        self.page = page
        self.user = user
        self.reference_id = reference_id
        self.initial_filter = initial_filter or {}
        self.search_value = ""
        self.current_risk_filter = "All Levels"
        self.current_dept_filter = "All Departments"
        # Resizable panel flex values
        self.left_flex = getattr(self, "left_flex", 1)
        self.center_flex = getattr(self, "center_flex", 3)
        self.right_flex = getattr(self, "right_flex", 1)
        
        # Initialize API client
        self.auditing_client = AuditingAPIClient()
        
        # Initialize assessments as empty list - all data comes from API
        self.assessments = []
        
        # Initialize BaseView header
        colors = get_theme_colors(self.page.theme_mode if hasattr(self.page, "theme_mode") else ft.ThemeMode.LIGHT)
        actions = [create_modern_button(colors, "+ Create", icon=Icons.ADD, on_click=self.create_assessment, style="success", width=140)]
        super().__init__(page, "Risk Assessments", on_search=self.on_search_change, actions=actions, colors=colors)

        # Initialize the view
        self.build()
        
        # Load data from API
        self.load_data()
        
        # BaseView provides header + search; use theme colors for local controls
        colors = self.colors

        # Risk level filter dropdown
        self.risk_filter = ft.Container(
            width=170,
            height=36,
            bgcolor=colors.surface,
            border=ft.border.all(1, colors.border),
            border_radius=8,
            padding=ft.padding.only(left=16, right=10),
            content=ft.Row([
                ft.Text(self.current_risk_filter, size=14, color=colors.text_primary),
                ft.Container(expand=True),
                ft.Icon(Icons.ARROW_DROP_DOWN, size=18, color=colors.text_secondary)
            ]),
            on_click=self.show_risk_filter
        )

        # Department filter dropdown
        self.dept_filter = ft.Container(
            width=200,
            height=36,
            bgcolor=colors.surface,
            border=ft.border.all(1, colors.border),
            border_radius=8,
            margin=ft.margin.only(left=12),
            padding=ft.padding.only(left=16, right=10),
            content=ft.Row([
                ft.Text(self.current_dept_filter, size=14, color=colors.text_primary),
                ft.Container(expand=True),
                ft.Icon(Icons.ARROW_DROP_DOWN, size=18, color=colors.text_secondary)
            ]),
            on_click=self.show_department_filter
        )

        # Action bar: only filters; Create button is in BaseView header actions
        action_bar = ft.Row([
            self.risk_filter,
            ft.Container(width=10),
            self.dept_filter,
        ], alignment=ft.MainAxisAlignment.START)

        # Assessments table
        self.assessments_table_container = ft.Container(
            expand=True,
            width=None,  # Allow width to be flexible
            content=None  # Will be set in refresh_table
        )

        # Compose under BaseView as cards
        self.cards_column.controls.clear()
        self.add_card(action_bar)
        # Initial table
        self.refresh_table()
        self.add_card(self.assessments_table_container)

    def load_data(self):
        """Load assessments data when view is shown"""
        if hasattr(self, 'page') and self.page:
            self.page.run_task(self._load_assessments_data_safe)

    async def _load_assessments_data_safe(self):
        """Load assessments data from the API (clean implementation)."""
        try:
            api_assessments = await self.auditing_client.get_assessments()
            self.assessments = [Assessment.from_json(a) for a in api_assessments] if api_assessments else []
            self.refresh_table()
            if hasattr(self, 'page') and self.page:
                self.page.update()
        except Exception as e:
            print(f"Error loading assessments from API: {e}")
            self.assessments = []
            self.refresh_table()
            if hasattr(self, 'page') and self.page:
                self.page.update()

    async def _load_assessments_data(self):
        """Load assessments data from the API"""
        print("DEBUG: _load_assessments_data called")
        try:
            # Show loading state
            print("DEBUG: Loading assessments from src.api...")
            
            # Get assessments data from API
            print("DEBUG: Calling auditing_client.get_assessments()")
            api_assessments = await self.auditing_client.get_assessments()
            print(f"DEBUG: API returned: {api_assessments}")
            
            if api_assessments:
                # Convert API data to Assessment objects
                self.assessments = []
                for assessment_data in api_assessments:
                    # Use the model's parser to avoid passing unsupported fields
                    assessment = Assessment.from_json(assessment_data)
                    self.assessments.append(assessment)
                
                print(f"Loaded {len(self.assessments)} assessments from API")
            else:
                # No API data available - show empty state
                print("No API data available")
                self.assessments = []
                
            # Refresh only the table to show new data (avoid full rebuild race)
            self.refresh_table()
            if hasattr(self, 'page') and self.page:
                self.page.update()
                
        except Exception as e:
            print(f"Error loading assessments from API: {e}")
            # Show empty state on error
            self.assessments = []
            self.refresh_table()
            if hasattr(self, 'page') and self.page:
                self.page.update()

    # Theming hook for global theme changes
    def apply_theme(self, colors):
        """Apply theme colors with proper contrast for dark mode"""
        try:
            self.bgcolor = colors.bg
            # Rebuild similar to DashboardView.build to rebind colors
            self.build()
            apply_theme_to_control(self, colors)
            if hasattr(self, 'page') and self.page:
                self.page.update()
        except Exception as e:
            print(f"Error applying theme to assessment list: {e}")

    def on_search_change(self, e):
        """Handle search input changes"""
        self.search_value = e.control.value.lower()
        self.refresh_table()

    def refresh_table(self):
        """Refresh the assessments table based on current filters and search"""
        filtered_assessments = self.assessments
        table_colors = get_theme_colors(self.page.theme_mode if hasattr(self.page, "theme_mode") else ft.ThemeMode.LIGHT)

        # Apply search filter
        if self.search_value:
            filtered_assessments = [assessment for assessment in filtered_assessments
                                    if (self.search_value in assessment.title.lower() or
                                        (
                                                    assessment.department and self.search_value in assessment.department.lower()) or
                                        (assessment.findings and self.search_value in assessment.findings.lower()))]

        # Apply risk level filter
        if self.current_risk_filter != "All Levels":
            filtered_assessments = [assessment for assessment in filtered_assessments
                                    if assessment.risk_level == self.current_risk_filter]

        # Apply department filter
        if self.current_dept_filter != "All Departments":
            filtered_assessments = [assessment for assessment in filtered_assessments
                                    if assessment.department == self.current_dept_filter]

        # Create table header using surface color with responsive column widths
        header = ft.Container(
            height=44,
            bgcolor=table_colors.surface,
            border=ft.border.only(bottom=ft.BorderSide(1, table_colors.border)),
            padding=ft.padding.only(left=24, right=24),
            content=ft.Row([
                ft.Container(expand=1, content=ft.Text("ID", weight=ft.FontWeight.BOLD, color=table_colors.text_secondary)),
                ft.Container(expand=2, content=ft.Text("Title", weight=ft.FontWeight.BOLD, color=table_colors.text_secondary)),
                ft.Container(expand=1.5, content=ft.Text("Department", weight=ft.FontWeight.BOLD, color=table_colors.text_secondary)),
                ft.Container(expand=1.5, content=ft.Text("Project", weight=ft.FontWeight.BOLD, color=table_colors.text_secondary)),
                ft.Container(expand=1, content=ft.Text("Date", weight=ft.FontWeight.BOLD, color=table_colors.text_secondary)),
                ft.Container(expand=1, content=ft.Text("Risk Level", weight=ft.FontWeight.BOLD, color=table_colors.text_secondary)),
                ft.Container(expand=0.8, content=ft.Text("Score", weight=ft.FontWeight.BOLD, color=table_colors.text_secondary)),
                ft.Container(expand=2, content=ft.Text("Actions", weight=ft.FontWeight.BOLD, color=table_colors.text_secondary,
                                                        text_align=ft.TextAlign.CENTER))
            ], expand=True)
        )

        # Create assessment rows
        rows_column = ft.Column(spacing=0)
        for i, assessment in enumerate(filtered_assessments):
            rows_column.controls.append(self.create_assessment_row(assessment, i))

        # Empty state if no assessments
        if not filtered_assessments:
            empty_state = ft.Container(
                height=100,
                alignment=ft.alignment.center,
                content=ft.Column([
                    ft.Container(
                        width=40,
                        height=40,
                        border_radius=20,
                        alignment=ft.alignment.center,
                        content=ft.Icon(Icons.SEARCH_OFF, size=20, color=table_colors.text_secondary)
                    ),
                    ft.Text("No assessments found", color=table_colors.text_secondary, size=16)
                ], spacing=10, alignment=ft.MainAxisAlignment.CENTER)
            )
            rows_column.controls.append(empty_state)

        # Use a Column with auto scroll on outer container for simpler updates
        table = ft.Column([
            header,
            rows_column
        ], spacing=0, expand=True, scroll=ft.ScrollMode.AUTO)

        # Wrap table in a responsive container
        responsive_table = ft.Container(
            content=table,
            expand=True,
            width=None,  # Allow width to be flexible
            bgcolor=table_colors.surface,
            border_radius=12,
            border=ft.border.all(1, table_colors.border)
        )

        # Update the table container
        self.assessments_table_container.content = responsive_table
        if hasattr(self, 'page') and self.page:
            self.page.update()

    # ---- Resizable layout helpers ----
    def _build_resizable_row(self, left_panel, center_panel, right_panel):
        colors = get_theme_colors(self.page.theme_mode if hasattr(self.page, "theme_mode") else ft.ThemeMode.LIGHT)

        def divider(on_pan_update):
            return ft.GestureDetector(
                on_pan_update=on_pan_update,
                content=ft.Container(width=8, bgcolor=colors.border, border_radius=4)
            )

        def on_drag_left(e):
            try:
                dx = getattr(e, "delta_x", 0) or 0
                if dx > 2 and self.center_flex > 1:
                    self.left_flex += 1
                    self.center_flex -= 1
                elif dx < -2 and self.left_flex > 1:
                    self.left_flex -= 1
                    self.center_flex += 1
                self._rebuild_main_row(left_panel, center_panel, right_panel)
            except Exception:
                pass

        def on_drag_right(e):
            try:
                dx = getattr(e, "delta_x", 0) or 0
                if dx > 2 and self.right_flex > 1:
                    self.right_flex -= 1
                    self.center_flex += 1
                elif dx < -2 and self.center_flex > 1:
                    self.center_flex -= 1
                    self.right_flex += 1
                self._rebuild_main_row(left_panel, center_panel, right_panel)
            except Exception:
                pass

        return ft.Row([
            ft.Container(expand=self.left_flex, content=left_panel),
            divider(on_drag_left),
            ft.Container(expand=self.center_flex, content=center_panel),
            divider(on_drag_right),
            ft.Container(expand=self.right_flex, content=right_panel)
        ], expand=True, spacing=8, alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    def _rebuild_main_row(self, left_panel, center_panel, right_panel):
        if hasattr(self, "_main_content_container"):
            self._main_content_container.content = self._build_resizable_row(left_panel, center_panel, right_panel)
            if hasattr(self, 'page') and self.page:
                self.page.update()

    def create_assessment_row(self, assessment, row_index):
        """Create a row for an assessment in the table"""
        row_colors = get_theme_colors(self.page.theme_mode if hasattr(self.page, "theme_mode") else ft.ThemeMode.LIGHT)
        row_bgcolor = row_colors.surface

        # Set risk level color
        risk_color = "#95a5a6"  # Default gray
        if assessment.risk_level == "High":
            risk_color = "#e74c3c"  # Red
        elif assessment.risk_level == "Medium":
            risk_color = "#f39c12"  # Orange
        elif assessment.risk_level == "Low":
            risk_color = "#2ecc71"  # Green

        # Format assessment date
        assessment_date = assessment.assessment_date
        if hasattr(assessment_date, "strftime"):
            assessment_date = assessment_date.strftime("%Y-%m-%d")
        else:
            assessment_date = "N/A"

        return ft.Container(
            height=60,
            bgcolor=row_bgcolor,
            border=ft.border.only(bottom=ft.BorderSide(1, row_colors.border)),
            padding=ft.padding.only(left=30, right=30),
            content=ft.Row([
                ft.Container(expand=1, content=ft.Text(assessment.id, color=row_colors.text_primary)),
                ft.Container(expand=2, content=ft.Text(assessment.title, color=row_colors.text_primary, overflow=ft.TextOverflow.ELLIPSIS)),
                ft.Container(expand=1.5,
                             content=ft.Text(assessment.department if assessment.department else "-", color=row_colors.text_primary, overflow=ft.TextOverflow.ELLIPSIS)),
                ft.Container(expand=1.5,
                             content=ft.Text(assessment.project if assessment.project else "-", color=row_colors.text_primary, overflow=ft.TextOverflow.ELLIPSIS)),
                ft.Container(expand=1, content=ft.Text(assessment_date, color=row_colors.text_primary)),
                ft.Container(
                    expand=1,
                    content=ft.Container(
                        width=80,
                        height=30,
                        bgcolor=risk_color,
                        border_radius=15,
                        alignment=ft.alignment.center,
                        content=ft.Text(assessment.risk_level, color="white", size=12, weight=ft.FontWeight.BOLD)
                    )
                ),
                ft.Container(
                    expand=0.8,
                    content=ft.Text(
                        f"{assessment.risk_score:.1f}" if assessment.risk_score is not None else "-",
                        color=row_colors.text_primary,
                    ),
                ),
                ft.Container(
                    expand=2,
                    content=ft.Row([
                        ft.ElevatedButton(
                            text="View", 
                            on_click=lambda e, aid=assessment.id: self.view_assessment(aid)
                        ),
                        ft.Container(width=10),
                        ft.ElevatedButton(
                            text="Edit", 
                            on_click=lambda e, aid=assessment.id: self._safe_edit_click(e, aid)
                        ),
                        ft.Container(width=10),
                        ft.ElevatedButton(
                            text="Delete", 
                            on_click=lambda e, aid=assessment.id: self.delete_assessment(aid)
                        )
                    ], alignment=ft.MainAxisAlignment.CENTER)
                )
            ], expand=True)
        )

    def _safe_edit_click(self, e, assessment_id):
        """Wrapper to debug edit click"""
        print(f"DEBUG: Edit button clicked for {assessment_id}")
        try:
            self.edit_assessment(assessment_id)
        except Exception as ex:
            print(f"CRITICAL ERROR in edit click: {ex}")
            import traceback
            traceback.print_exc()

    def show_risk_filter(self, e):
        """Show risk level filter dropdown"""
        dialog = ft.AlertDialog(
            title=ft.Text("Select Risk Level"),
            content=ft.Column([
                ft.TextButton("All Levels", on_click=lambda e: self.apply_risk_filter("All Levels")),
                ft.TextButton("High", on_click=lambda e: self.apply_risk_filter("High")),
                ft.TextButton("Medium", on_click=lambda e: self.apply_risk_filter("Medium")),
                ft.TextButton("Low", on_click=lambda e: self.apply_risk_filter("Low")),
            ], spacing=0, height=160),
            actions=[ft.TextButton("Close", on_click=self.close_dialog)],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def apply_risk_filter(self, risk_level):
        """Apply selected risk level filter"""
        self.current_risk_filter = risk_level
        self.risk_filter.content.controls[0].value = risk_level
        self.close_dialog(None)
        self.refresh_table()

    def show_department_filter(self, e):
        """Show department filter dropdown"""
        # Get unique departments
        departments = sorted(list(set(a.department for a in self.assessments if a.department)))

        content_controls = [ft.TextButton("All Departments", on_click=lambda e: self.apply_dept_filter("All Departments"))]

        for dept in departments:
                content_controls.append(ft.TextButton(dept, on_click=lambda e, d=dept: self.apply_dept_filter(d)))

        dialog = ft.AlertDialog(
            title=ft.Text("Select Department"),
            content=ft.Column(content_controls, spacing=0, height=min(len(content_controls) * 40, 300)),
            actions=[ft.TextButton("Close", on_click=self.close_dialog)],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def apply_dept_filter(self, department):
        """Apply selected department filter"""
        self.current_dept_filter = department
        self.dept_filter.content.controls[0].value = department
        self.close_dialog(None)
        self.refresh_table()

    def create_assessment(self, e):
        """Create a new assessment"""
        # Show a loading indicator while preparing the form
        print("Creating new assessment")  # Debug print
        self.page.snack_bar = ft.SnackBar(content=ft.Text("Preparing assessment form..."))
        self.page.snack_bar.open = True
        self.page.update()

        try:
            # Import here to avoid circular imports
            from src.views.assessments.form import AssessmentFormView

            # Create a new assessment ID based on existing assessments
            new_id = f"A-{len(self.assessments) + 1:03d}"

            # Create a blank assessment with default values
            from datetime import datetime
            from src.models.assessment import Assessment

            new_assessment = Assessment(
                id=new_id,
                title="",
                department=None,
                project=None,
                assessment_date=datetime.now().date(),
                auditor=self.user["username"] if isinstance(self.user, dict) and "username" in self.user else "Admin",
                auditor_id=self.user.get("id", 1) if isinstance(self.user, dict) else 1,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                risk_level="Low",
                risk_score=0.0,
                scope="",
                findings="",
                recommendations="",
                risk_factors=[
                    {"name": "Control Environment", "value": 0},
                    {"name": "Risk Assessment Process", "value": 0},
                    {"name": "Control Activities", "value": 0}
                ]
            )

            print(f"Created new assessment with ID: {new_id}")

            # Create the unified form view
            form_view = UnifiedAssessmentForm(
                self.page,
                self.user,
                mode="create",
                assessment=new_assessment,
                on_save=self.on_assessment_saved,
                on_cancel=self.on_form_cancel
            )

            print("Created form view, now updating page")

            # IMPORTANT CHANGE: Use page's controls directly instead of clean/add
            if hasattr(self.page, 'controls'):
                self.page.controls = [form_view]
            else:
                # Fallback to clean/add
                self.page.clean()
                self.page.add(form_view)

            # Ensure update is called
            self.page.update()
            print("Form added to page and page updated")

        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Error creating assessment form: {str(e)}")
            print(f"Traceback: {error_details}")
            self.page.snack_bar = ft.SnackBar(content=ft.Text(f"Error: {str(e)}"))
            self.page.snack_bar.open = True
            self.page.update()

    def edit_assessment(self, assessment_id):
        """Edit an assessment - triggers async fetch"""
        print(f"DEBUG: edit_assessment called with ID: {assessment_id}")
        self.page.run_task(self._edit_assessment_async, assessment_id)

    async def _edit_assessment_async(self, assessment_id):
        """Async method to fetch fresh data and open edit form"""
        print(f"DEBUG: _edit_assessment_async starting for {assessment_id}")
        
        # Find the assessment in our local list to get the reference ID
        local_assessment = next((a for a in self.assessments if a.id == assessment_id), None)
        if not local_assessment:
            self.show_error_dialog(f"Assessment {assessment_id} not found locally")
            return

        # Close any open dialog
        if hasattr(self.page, 'dialog') and self.page.dialog and self.page.dialog.open:
            self.page.dialog.open = False
            self.page.update()

        try:
            # Reference ID is needed for API
            reference_id = getattr(local_assessment, 'reference_id', None) or getattr(local_assessment, 'id', None)
            
            # FETCH FRESH DATA FROM API
            print(f"DEBUG: Fetching fresh data for reference_id: {reference_id}")
            fresh_data = await self.auditing_client.get_risk_assessment(reference_id)
            
            if not fresh_data:
                 print("WARNING: API returned no data, falling back to local object")
                 fresh_data = local_assessment
            else:
                 print("DEBUG: Fresh data fetched successfully")

            # Create the form with FRESH data
            form_view = UnifiedAssessmentForm(
                self.page,
                self.user,
                mode="edit",
                reference_id=reference_id,
                assessment=fresh_data, # Pass fresh dict or object
                on_save=self.on_assessment_saved,
                on_cancel=self.on_form_cancel
            )

            # Replace current view with form view
            app = self.page.APP_INSTANCE
            app.content_area.content = form_view
            self.page.update()

        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Error creating assessment form: {str(e)}")
            print(f"Traceback: {error_details}")
            self.show_error_dialog(f"Error opening form: {str(e)}")

    def on_assessment_saved(self, assessment):
        """Handle saved assessment - accepts dict or Assessment object"""
        # Handle dict result from API
        if isinstance(assessment, dict):
            assessment_id = assessment.get('id') or assessment.get('referenceId')
            print(f"Assessment saved: {assessment_id} (dict result)")
            # Refresh the list to show updated data
            self.refresh_table()
            return
        
        print(f"Assessment saved: {assessment.id}")

        # Find if assessment already exists
        existing_idx = next((i for i, a in enumerate(self.assessments) if a.id == assessment.id), None)

        if existing_idx is not None:
            # Update existing assessment
            self.assessments[existing_idx] = assessment
        else:
            # Add new assessment
            self.assessments.append(assessment)

        try:
            # Reference to the application's layout to return to
            from src.views.assessments.list import AssessmentListView

            # Try to find the main app's layout
            app_layout = None
            if hasattr(self.page, 'APP_INSTANCE') and self.page.APP_INSTANCE:
                app = self.page.APP_INSTANCE
                if hasattr(app, 'show_view'):
                    # Use app's navigation if available
                    app.show_view("assessments")
                    return

            # If we can't find the app navigation, rebuild the list view
            print("Rebuilding assessment list view")

            # Replace form view with list view
            self.page.clean()
            self.page.add(self)

            # Show success message
            self.show_success_dialog("Assessment saved successfully")

            # Refresh the table
            self.refresh_table()

        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Error returning to list view: {str(e)}")
            print(f"Traceback: {error_details}")

            # Fallback to simplest approach
            self.page.clean()
            self.page.add(self)
            self.page.update()

    def on_form_cancel(self):
        """Handle form cancel"""
        print("Form cancelled, returning to list view")  # Debug print

        # Guard against None page
        if not self.page:
            print("Warning: page is None in on_form_cancel")
            return

        try:
            # Try to find the main app's layout
            if hasattr(self.page, 'APP_INSTANCE') and self.page.APP_INSTANCE:
                app = self.page.APP_INSTANCE
                if hasattr(app, 'show_view'):
                    # Use app's navigation if available
                    app.show_view("assessments")
                    return

            # If we can't find the app navigation, rebuild the list view
            print("Rebuilding assessment list view after cancel")

            # Replace form view with list view - GUARD against None
            if hasattr(self.page, 'clean'):
                self.page.clean()
                self.page.add(self)
                self.page.update()

        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Error returning to list view: {str(e)}")
            print(f"Traceback: {error_details}")

    def view_assessment(self, assessment_id):
        """View assessment details"""
        print(f"DEBUG: view_assessment called with ID: {assessment_id}")
        print(f"DEBUG: Total assessments available: {len(self.assessments)}")
        
        # Find the assessment in our list to get the reference_id
        assessment = next((a for a in self.assessments if a.id == assessment_id), None)
        if not assessment:
            print(f"ERROR: Assessment {assessment_id} not found in list")
            self.show_error_dialog(f"Assessment {assessment_id} not found")
            return
        
        print(f"DEBUG: Found assessment: {assessment.title}")
        
        # Extract reference_id from the assessment
        reference_id = getattr(assessment, 'reference_id', None)
        if not reference_id:
            # Try to get it from the assessment data
            if hasattr(assessment, 'id') and isinstance(assessment.id, str) and assessment.id.startswith('A-'):
                # Extract numeric ID from A-001 format
                try:
                    reference_id = int(assessment.id[2:])
                except ValueError:
                    reference_id = None
        
        if not reference_id:
            print(f"ERROR: No reference_id found for assessment {assessment_id}")
            self.show_error_dialog(f"Unable to load assessment details: No reference ID found")
            return
        
        print(f"DEBUG: Using reference_id: {reference_id} to call API")
        
        # Call the API to get full assessment details
        if hasattr(self.page, "run_task"):
            self.page.run_task(self._load_assessment_details_async, reference_id, assessment_id)
        else:
            # Fallback for environments without run_task
            import asyncio
            try:
                loop = asyncio.get_event_loop()
                loop.create_task(self._load_assessment_details_async(reference_id, assessment_id))
            except RuntimeError:
                # If no event loop, create a new one
                asyncio.run(self._load_assessment_details_async(reference_id, assessment_id))

    async def _load_assessment_details_async(self, reference_id, assessment_id):
        """Load assessment details from API asynchronously"""
        try:
            print(f"DEBUG: Starting _load_assessment_details_async with reference_id: {reference_id}, assessment_id: {assessment_id}")
            
            from src.controllers.assessment_controller import AssessmentController
            controller = AssessmentController()
            
            print(f"DEBUG: Calling API get_risk_assessment with reference_id: {reference_id}")
            assessment_data = await controller.get_risk_assessment(reference_id)
            
            print(f"DEBUG: API call completed, result: {assessment_data is not None}")
            
            if not assessment_data:
                print(f"ERROR: API returned no data for reference_id: {reference_id}")
                self.show_error_dialog(f"Assessment details not found")
                return
            
            print(f"DEBUG: API returned assessment data: {type(assessment_data)}")
            if isinstance(assessment_data, dict):
                print(f"DEBUG: API response keys: {list(assessment_data.keys())}")
                print(f"DEBUG: API response sample: {assessment_data}")
            
            # Navigate to a full details view
            try:
                print("DEBUG: Creating go_back callback")
                # Store references to avoid context issues
                page_ref = self.page
                app_instance = getattr(self.page, 'APP_INSTANCE', None) if self.page else None
                
                def go_back(e=None):
                    print("=" * 50)
                    print("DEBUG: go_back callback called!")
                    print(f"DEBUG: Event object: {e}")
                    print(f"DEBUG: page_ref: {page_ref}")
                    print(f"DEBUG: app_instance: {app_instance}")
                    print("=" * 50)
                    
                    try:
                        # Return to assessments list view using the main app navigation
                        if app_instance:
                            print("DEBUG: Using APP_INSTANCE to navigate back to assessments")
                            # Force recreation of assessments view to ensure fresh data
                            if "assessments" in app_instance.views:
                                del app_instance.views["assessments"]
                            app_instance.show_view("assessments")
                            print("DEBUG: Navigation completed")
                        else:
                            print("ERROR: APP_INSTANCE not available")
                    except Exception as ex:
                        print(f"ERROR: Exception in go_back callback: {ex}")
                        import traceback
                        traceback.print_exc()

                print("DEBUG: Creating simple assessment view instead of UnifiedAssessmentForm")
                # Create a simple view instead of using UnifiedAssessmentForm with DataTable
                view_form = self._create_simple_assessment_view(assessment_data, go_back)
                
                print("DEBUG: Setting content area")
                app = self.page.APP_INSTANCE
                app.content_area.content = view_form
                
                print("DEBUG: Updating page")
                self.page.update()
                print("DEBUG: View assessment setup completed successfully")
                
            except Exception as ex:
                print(f"ERROR: Error creating view form: {ex}")
                import traceback
                traceback.print_exc()
                # Fallback: show error text in content area without dialogs
                try:
                    app = getattr(self.page, 'APP_INSTANCE', None)
                    if app and hasattr(app, 'content_area'):
                        app.content_area.content = ft.Container(padding=20, content=ft.Text(f"Unable to load details: {ex}"))
                        self.page.update()
                    elif self.page is not None:
                        self.page.snack_bar = ft.SnackBar(content=ft.Text(f"Unable to load details: {ex}"))
                        self.page.snack_bar.open = True
                        self.page.update()
                    else:
                        print(f"Unable to load details: {ex}")
                except Exception as inner:
                    print(f"Failed to render error: {inner}")
                    
        except Exception as ex:
            print(f"ERROR: Error calling API: {ex}")
            import traceback
            traceback.print_exc()
            self.show_error_dialog(f"Error loading assessment details: {str(ex)}")

    def _create_simple_assessment_view(self, assessment_data, go_back_callback):
        """Create a simple assessment view without DataTable"""
        from src.utils.theme import get_theme_colors, create_modern_card, create_modern_button
        from flet import Icons
        
        colors = get_theme_colors(self.page.theme_mode if hasattr(self.page, "theme_mode") else ft.ThemeMode.LIGHT)
        
        # Create header with back button - using a simpler approach
        def handle_back_click(e):
            print("=" * 50)
            print("DEBUG: handle_back_click called directly!")
            print(f"DEBUG: Event: {e}")
            print("=" * 50)
            go_back_callback(e)
        
        back_button = ft.ElevatedButton(
            "Back to List",
            icon=Icons.ARROW_BACK,
            on_click=handle_back_click,
            bgcolor=colors.primary,
            color="white"
        )
        
        header = ft.Row([
            back_button,
            ft.Container(expand=True),
            ft.Text("Assessment Details", size=24, weight=ft.FontWeight.BOLD, color=colors.text_primary)
        ])
        
        # Assessment overview card
        overview_content = ft.Column([
            ft.Text("Assessment Overview", size=18, weight=ft.FontWeight.BOLD, color=colors.text_primary),
            ft.Divider(color=colors.border),
            ft.Row([
                ft.Container(expand=1, content=ft.Column([
                    ft.Text("Client:", weight=ft.FontWeight.BOLD, color=colors.text_secondary),
                    ft.Text(assessment_data.get("client", "N/A"), color=colors.text_primary)
                ])),
                ft.Container(expand=1, content=ft.Column([
                    ft.Text("Assessor:", weight=ft.FontWeight.BOLD, color=colors.text_secondary),
                    ft.Text(assessment_data.get("assessor", "N/A"), color=colors.text_primary)
                ])),
                ft.Container(expand=1, content=ft.Column([
                    ft.Text("Approved By:", weight=ft.FontWeight.BOLD, color=colors.text_secondary),
                    ft.Text(assessment_data.get("approvedBy", "N/A"), color=colors.text_primary)
                ]))
            ]),
            ft.Row([
                ft.Container(expand=1, content=ft.Column([
                    ft.Text("Start Date:", weight=ft.FontWeight.BOLD, color=colors.text_secondary),
                    ft.Text(assessment_data.get("assessmentStartDate", "N/A"), color=colors.text_primary)
                ])),
                ft.Container(expand=1, content=ft.Column([
                    ft.Text("End Date:", weight=ft.FontWeight.BOLD, color=colors.text_secondary),
                    ft.Text(assessment_data.get("assessmentEndDate", "N/A"), color=colors.text_primary)
                ])),
                ft.Container(expand=1, content=ft.Column([
                    ft.Text("Reference ID:", weight=ft.FontWeight.BOLD, color=colors.text_secondary),
                    ft.Text(str(assessment_data.get("referenceId", "N/A")), color=colors.text_primary)
                ]))
            ])
        ], spacing=16)
        
        overview_card = create_modern_card(colors, overview_content)
        
        # Risk assessments table (using simple layout instead of DataTable)
        risk_assessments = assessment_data.get("riskAssessments", [])
        
        if risk_assessments:
            # Create table header
            table_header = ft.Container(
                height=40,
                bgcolor=colors.surface,
                border=ft.border.only(bottom=ft.BorderSide(1, colors.border)),
                padding=ft.padding.only(left=24, right=24),
                content=ft.Row([
                    ft.Container(expand=2, content=ft.Text("Business Objective", weight=ft.FontWeight.BOLD, color=colors.text_secondary)),
                    ft.Container(expand=2, content=ft.Text("Main Process", weight=ft.FontWeight.BOLD, color=colors.text_secondary)),
                    ft.Container(expand=1, content=ft.Text("Risk Level", weight=ft.FontWeight.BOLD, color=colors.text_secondary)),
                    ft.Container(expand=2, content=ft.Text("Key Risk", weight=ft.FontWeight.BOLD, color=colors.text_secondary)),
                    ft.Container(expand=1, content=ft.Text("Likelihood", weight=ft.FontWeight.BOLD, color=colors.text_secondary)),
                    ft.Container(expand=1, content=ft.Text("Impact", weight=ft.FontWeight.BOLD, color=colors.text_secondary)),
                ], expand=True)
            )
            
            # Create table rows
            table_rows = []
            for risk in risk_assessments:
                risk_color = "#95a5a6"  # Default gray
                likelihood = risk.get("risksAssessment_RiskLikelihood", "")
                impact = risk.get("risksAssessment_RiskImpact", "")
                
                # Simple risk level determination
                if likelihood in ["Likely", "Almost Certain"] and impact in ["Major", "Catastrophic"]:
                    risk_color = "#e74c3c"  # High - Red
                elif likelihood in ["Possible", "Likely"] or impact in ["Moderate", "Major"]:
                    risk_color = "#f39c12"  # Medium - Orange
                else:
                    risk_color = "#2ecc71"  # Low - Green
                
                row = ft.Container(
                    height=60,
                    bgcolor=colors.surface,
                    border=ft.border.only(bottom=ft.BorderSide(1, colors.border)),
                    padding=ft.padding.only(left=24, right=24),
                    content=ft.Row([
                        ft.Container(expand=2, content=ft.Text(risk.get("processObjectivesAssessment_BusinessObjectives", "N/A"), color=colors.text_primary, overflow=ft.TextOverflow.ELLIPSIS)),
                        ft.Container(expand=2, content=ft.Text(risk.get("processObjectivesAssessment_MainProcess", "N/A"), color=colors.text_primary, overflow=ft.TextOverflow.ELLIPSIS)),
                        ft.Container(expand=1, content=ft.Text("Medium", color=risk_color, weight=ft.FontWeight.BOLD)),
                        ft.Container(expand=2, content=ft.Text(risk.get("risksAssessment_KeyRiskAndFactors", "N/A"), color=colors.text_primary, overflow=ft.TextOverflow.ELLIPSIS)),
                        ft.Container(expand=1, content=ft.Text(likelihood, color=colors.text_primary)),
                        ft.Container(expand=1, content=ft.Text(impact, color=colors.text_primary)),
                    ], expand=True)
                )
                table_rows.append(row)
            
            table_content = ft.Column([table_header] + table_rows, spacing=0)
            table_card = create_modern_card(colors, ft.Column([
                ft.Text("Risk Assessments", size=18, weight=ft.FontWeight.BOLD, color=colors.text_primary),
                ft.Divider(color=colors.border),
                table_content
            ], spacing=16))
        else:
            table_card = create_modern_card(colors, ft.Column([
                ft.Text("Risk Assessments", size=18, weight=ft.FontWeight.BOLD, color=colors.text_primary),
                ft.Divider(color=colors.border),
                ft.Container(
                    height=100,
                    alignment=ft.alignment.center,
                    content=ft.Text("No risk assessments found", color=colors.text_secondary)
                )
            ], spacing=16))
        
        # Create main content
        main_content = ft.Column([
            header,
            ft.Divider(color=colors.border, height=20),
            overview_card,
            ft.Container(height=16),
            table_card
        ], spacing=16, scroll=ft.ScrollMode.AUTO)
        
        return ft.Container(
            content=main_content,
            padding=20,
            expand=True
        )

    def edit_assessment_from_dialog(self, assessment_id):
        """Edit assessment from the view dialog"""
        # Close the dialog first
        self.close_dialog(None)
        # Then edit the assessment
        self.edit_assessment(assessment_id)

    def delete_assessment(self, assessment_id):
        """Delete an assessment"""
        print(f"DEBUG: delete_assessment called with ID: {assessment_id}")
        print(f"DEBUG: Total assessments available: {len(self.assessments)}")
        
        # Find the assessment in our list
        assessment = next((a for a in self.assessments if a.id == assessment_id), None)
        if not assessment:
            print(f"ERROR: Assessment {assessment_id} not found for deletion")
            self.show_error_dialog(f"Assessment {assessment_id} not found")
            return

        # Create confirmation dialog
        dialog = ft.AlertDialog(
            title=ft.Text("Confirm Deletion"),
            content=ft.Column([
                ft.Text(f"Are you sure you want to delete assessment {assessment_id}?"),
                ft.Container(height=10),
                ft.Text("This action cannot be undone.", color="#e74c3c"),
            ]),
            actions=[
                ft.TextButton("Cancel", on_click=self.close_dialog),
                ft.TextButton("Delete", on_click=lambda e: self.confirm_delete_assessment(assessment_id)),
            ],
        )

        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def confirm_delete_assessment(self, assessment_id):
        """Confirm assessment deletion"""
        # Close the confirmation dialog
        self.page.dialog.open = False

        # Show a loading indicator
        loading_dialog = ft.AlertDialog(
            modal=True,
            content=ft.Column([
                ft.ProgressRing(),
                ft.Text("Deleting assessment..."),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        )

        self.page.dialog = loading_dialog
        loading_dialog.open = True
        self.page.update()

        # # API call to delete assessment - commented for future implementation
        # try:
        #     # Delete assessment via API
        #     # response = api_client.delete_assessment(assessment_id)
        #     # if not response.success:
        #     #     self.close_dialog(None)
        #     #     self.show_error_dialog(response.message)
        #     #     return
        #     pass
        # except Exception as e:
        #     print(f"Error deleting assessment: {str(e)}")
        #     self.close_dialog(None)
        #     self.show_error_dialog("Failed to delete assessment. Please try again.")
        #     return

        # For demo: Remove from our local list
        self.assessments = [a for a in self.assessments if a.id != assessment_id]

        # Simulate deletion delay
        import threading
        timer = threading.Timer(1.0, lambda: self.finalize_delete_assessment(assessment_id))
        timer.start()

    def finalize_delete_assessment(self, assessment_id):
        """Finalize assessment deletion"""
        # Close the loading dialog
        self.page.dialog.open = False

        # Show success message
        success_dialog = ft.AlertDialog(
            title=ft.Text("Success"),
            content=ft.Text(f"Assessment {assessment_id} has been deleted successfully."),
            actions=[
                ft.TextButton("OK", on_click=self.close_dialog),
            ],
        )

        self.page.dialog = success_dialog
        success_dialog.open = True
        self.page.update()

        # Refresh the table
        self.refresh_table()

    def show_success_dialog(self, message):
        """Show a success dialog"""
        dialog = ft.AlertDialog(
            title=ft.Text("Success"),
            content=ft.Text(message),
            actions=[
                ft.TextButton("OK", on_click=self.close_dialog),
            ],
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def show_error_dialog(self, message):
        """Show error dialog"""
        dialog = ft.AlertDialog(
            title=ft.Text("Error"),
            content=ft.Text(message),
            actions=[
                ft.TextButton("OK", on_click=self.close_dialog),
            ],
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def close_dialog(self, e):
        """Close the current dialog"""
        if self.page.dialog:
            self.page.dialog.open = False
            self.page.update()

