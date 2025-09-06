import flet as ft
from flet import Icons
from src.utils.theme import (
    get_theme_colors,
    apply_theme_to_control,
    create_modern_card,
    create_modern_button,
)
from src.models.assessment import Assessment
from datetime import datetime
from src.api.auditing_client import AuditingAPIClient


class AssessmentListView(ft.Container):
    def __init__(self, page, user, reference_id=None, initial_filter=None):
        super().__init__()
        self.page = page
        self.user = user
        self.reference_id = reference_id
        self.initial_filter = initial_filter or {}
        self.expand = True
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
        
        # Initialize the view
        self.build()
        
        # Load data from API
        self.load_data()
        
        # Theme and search field styled like user_management.py
        colors = get_theme_colors(self.page.theme_mode if hasattr(self.page, "theme_mode") else ft.ThemeMode.LIGHT)
        self._search_input = ft.TextField(
            border=ft.InputBorder.NONE,
            color="#2c3e50",
            hint_text="Search assessments",
            hint_style=ft.TextStyle(color="#95a5a6", size=14),
            expand=True,
            height=30,
            content_padding=5,
            on_change=self.on_search_change,
        )
        self.search_field = ft.Container(
            width=240,
            height=30,
            bgcolor="#f5f7fa",
            border=ft.border.all(1, "#e6e9ed"),
            border_radius=15,
            padding=ft.padding.only(left=10, right=10),
            content=ft.Row([
                ft.Icon(Icons.SEARCH, color="#95a5a6", size=18),
                self._search_input,
            ])
        )

        # Header
        header = ft.Container(
            content=ft.Row([
                ft.Column([
                    ft.Text("Risk Assessments", size=22, weight=ft.FontWeight.BOLD, color=colors.text_primary),
                    ft.Text("Browse and manage assessments", size=12, color=colors.text_secondary),
                ], alignment=ft.CrossAxisAlignment.START),
                ft.Container(expand=True),
                self.search_field,
                # Only one Create button in the filters bar below
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        )

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

        # Action bar: filters + create (match user_management layout)
        action_bar = create_modern_card(
            colors,
            ft.Row([
                self.risk_filter,
                ft.Container(width=10),
                self.dept_filter,
                ft.Container(expand=True),
                create_modern_button(colors, "+ Create", icon=Icons.ADD, on_click=self.create_assessment, style="success", width=140)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        )

        # Assessments table
        self.assessments_table_container = ft.Container(
            expand=True,
            content=None  # Will be set in refresh_table
        )

        # Refresh the table with initial data
        self.refresh_table()

        # No footer/status bar per spec

        # Main content: header already set; now action bar and table card, then status bar
        dash_colors = colors
        table_card = create_modern_card(dash_colors, self.assessments_table_container)
        self._main_content_container = ft.Container(
            expand=True,
            bgcolor=dash_colors.bg,
            content=ft.Column([
                action_bar,
                ft.Container(height=16),
                table_card,
            ], spacing=0, expand=True),
        )

        # Assemble the view
        # Make the whole view scrollable for better UX on smaller screens
        self.content = ft.Column([
            header,
            self._main_content_container,
        ], spacing=0, expand=True, scroll=ft.ScrollMode.AUTO)

        # Normalize colors to theme immediately
        try:
            colors = get_theme_colors(self.page.theme_mode if hasattr(self.page, "theme_mode") else ft.ThemeMode.LIGHT)
            apply_theme_to_control(self, colors)
        except Exception:
            pass

    def load_data(self):
        """Load assessments data when view is shown"""
        if hasattr(self, 'page') and self.page:
            self.page.run_task(self._load_assessments_data)

    async def _load_assessments_data(self):
        """Load assessments data from the API"""
        print("🔧 DEBUG: _load_assessments_data called")
        try:
            # Show loading state
            print("🔧 DEBUG: Loading assessments from src.api...")
            
            # Get assessments data from API
            print("🔧 DEBUG: Calling auditing_client.get_assessments()")
            api_assessments = await self.auditing_client.get_assessments()
            print(f"🔧 DEBUG: API returned: {api_assessments}")
            
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

        # Create table header using surface color
        header = ft.Container(
            height=44,
            bgcolor=table_colors.surface,
            border=ft.border.only(bottom=ft.BorderSide(1, table_colors.border)),
            padding=ft.padding.only(left=24, right=24),
            content=ft.Row([
                ft.Container(width=120, content=ft.Text("ID", weight=ft.FontWeight.BOLD, color=table_colors.text_secondary)),
                ft.Container(expand=True, content=ft.Text("Title", weight=ft.FontWeight.BOLD, color=table_colors.text_secondary)),
                ft.Container(width=180, content=ft.Text("Department", weight=ft.FontWeight.BOLD, color=table_colors.text_secondary)),
                ft.Container(width=140, content=ft.Text("Project", weight=ft.FontWeight.BOLD, color=table_colors.text_secondary)),
                ft.Container(width=120, content=ft.Text("Date", weight=ft.FontWeight.BOLD, color=table_colors.text_secondary)),
                ft.Container(width=120, content=ft.Text("Risk Level", weight=ft.FontWeight.BOLD, color=table_colors.text_secondary)),
                ft.Container(width=100, content=ft.Text("Score", weight=ft.FontWeight.BOLD, color=table_colors.text_secondary)),
                ft.Container(width=200, content=ft.Text("Actions", weight=ft.FontWeight.BOLD, color=table_colors.text_secondary,
                                                        text_align=ft.TextAlign.CENTER))
            ])
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

        # Update the table container
        self.assessments_table_container.content = table
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
                ft.Container(width=120, content=ft.Text(assessment.id, color=row_colors.text_primary)),
                ft.Container(width=250, content=ft.Text(assessment.title, color=row_colors.text_primary)),
                ft.Container(width=150,
                             content=ft.Text(assessment.department if assessment.department else "-", color=row_colors.text_primary)),
                ft.Container(width=140,
                             content=ft.Text(assessment.project if assessment.project else "-", color=row_colors.text_primary)),
                ft.Container(width=120, content=ft.Text(assessment_date, color=row_colors.text_primary)),
                ft.Container(
                    width=120,
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
                    width=100,
                    content=ft.Text(
                        f"{assessment.risk_score:.1f}" if assessment.risk_score is not None else "-",
                        color=row_colors.text_primary,
                    ),
                ),
                ft.Container(
                    width=200,
                    content=ft.Row([
                        ft.ElevatedButton(text="View", on_click=lambda e, id=assessment.id: self.view_assessment(id)),
                        ft.Container(width=10),
                        ft.ElevatedButton(text="Edit", on_click=lambda e, id=assessment.id: self.edit_assessment(id)),
                        ft.Container(width=10),
                        ft.ElevatedButton(text="Delete", on_click=lambda e, id=assessment.id: self.delete_assessment(id)),
                    ], alignment=ft.MainAxisAlignment.CENTER)
                )
            ])
        )

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
            from src.views.assessments.unified_form import UnifiedAssessmentForm
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
        """Edit an assessment"""
        print(f"🔧 DEBUG: edit_assessment called with ID: {assessment_id}")
        print(f"🔧 DEBUG: Total assessments available: {len(self.assessments)}")

        # Find the assessment in our list
        assessment = next((a for a in self.assessments if a.id == assessment_id), None)
        if not assessment:
            self.show_error_dialog(f"Assessment {assessment_id} not found")
            return

        # Close any open dialog
        if hasattr(self.page, 'dialog') and self.page.dialog and self.page.dialog.open:  # Safe check
            self.page.dialog.open = False
            self.page.update()

        try:
            # Import here to avoid circular imports
            from src.views.assessments.form import AssessmentFormView

            # Display a snackbar to indicate loading
            self.page.snack_bar = ft.SnackBar(content=ft.Text("Loading assessment form..."))
            self.page.snack_bar.open = True
            self.page.update()

            # Reference to the application's layout to return to later
            app_layout = None
            if hasattr(self.page, "_controls") and self.page._controls:
                app_layout = self.page._controls[0]

            # Create the form with proper callbacks
            from src.views.assessments.unified_form import UnifiedAssessmentForm
            form_view = UnifiedAssessmentForm(
                self.page,
                self.user,
                mode="edit",
                assessment=assessment,
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
            self.page.snack_bar = ft.SnackBar(content=ft.Text(f"Error: {str(e)}"))
            self.page.snack_bar.open = True
            self.page.update()

    def on_assessment_saved(self, assessment):
        """Handle saved assessment"""
        print(f"Assessment saved: {assessment.id}")  # Debug print

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
            from src.views.assessment.list import AssessmentListView

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
        print(f"🔧 DEBUG: view_assessment called with ID: {assessment_id}")
        print(f"🔧 DEBUG: Total assessments available: {len(self.assessments)}")
        
        # Find the assessment in our list
        assessment = next((a for a in self.assessments if a.id == assessment_id), None)
        if not assessment:
            print(f"❌ DEBUG: Assessment {assessment_id} not found in list")
            self.show_error_dialog(f"Assessment {assessment_id} not found")
            return
        
        print(f"✅ DEBUG: Found assessment: {assessment.title}")

        # Format assessment date
        assessment_date = assessment.assessment_date
        if hasattr(assessment_date, "strftime"):
            assessment_date = assessment_date.strftime("%Y-%m-%d")
        else:
            assessment_date = "N/A"

        # Set risk level color
        risk_color = "#95a5a6"  # Default gray
        if assessment.risk_level == "High":
            risk_color = "#e74c3c"  # Red
        elif assessment.risk_level == "Medium":
            risk_color = "#f39c12"  # Orange
        elif assessment.risk_level == "Low":
            risk_color = "#2ecc71"  # Green

        # Create risk factors display
        risk_factors_column = ft.Column(spacing=10)
        for factor in assessment.risk_factors:
            if isinstance(factor, dict) and "name" in factor and "value" in factor:
                risk_factors_column.controls.append(
                    ft.Row([
                        ft.Text(factor["name"], weight=ft.FontWeight.BOLD),
                        ft.Container(expand=True),
                        ft.Text(
                            f"{factor['value']:.1f}" if isinstance(factor["value"], (int, float)) else factor["value"])
                    ])
                )

        # Navigate to a full details view instead of a simple dialog
        try:
            from src.views.assessments.details import AssessmentDetailsView
            def go_back():
                # Return to list view
                if hasattr(self.page, 'APP_INSTANCE') and self.page.APP_INSTANCE:
                    self.page.APP_INSTANCE.show_view("assessments")
                else:
                    self.page.clean()
                    self.page.add(self)
                    self.page.update()

            # Use unified form in view (read-only) mode
            from src.views.assessments.unified_form import UnifiedAssessmentForm
            view_form = UnifiedAssessmentForm(self.page, self.user, mode="view", assessment=assessment, on_cancel=go_back)
            app = self.page.APP_INSTANCE
            app.content_area.content = view_form
            self.page.update()
        except Exception as ex:
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

    def edit_assessment_from_dialog(self, assessment_id):
        """Edit assessment from the view dialog"""
        # Close the dialog first
        self.close_dialog(None)
        # Then edit the assessment
        self.edit_assessment(assessment_id)

    def delete_assessment(self, assessment_id):
        """Delete an assessment"""
        print(f"🔧 DEBUG: delete_assessment called with ID: {assessment_id}")
        print(f"🔧 DEBUG: Total assessments available: {len(self.assessments)}")
        
        # Find the assessment in our list
        assessment = next((a for a in self.assessments if a.id == assessment_id), None)
        if not assessment:
            print(f"❌ DEBUG: Assessment {assessment_id} not found for deletion")
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

