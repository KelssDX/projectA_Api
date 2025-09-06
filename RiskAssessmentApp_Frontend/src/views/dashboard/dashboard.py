import flet as ft
from flet import Icons
import asyncio
from src.utils.theme import get_theme_colors, create_stat_card, create_modern_button, create_modern_card, create_glass_card


class DashboardView(ft.Container):
    def __init__(self, page, auditing_client, on_navigate, current_user=None):
        super().__init__()
        self.page = page
        self.auditing_client = auditing_client
        self.on_navigate = on_navigate
        self.current_user = current_user
        self.assessments_data = []
        self.stats = {
            'active_assessments': 0,
            'high_risk_areas': 0,
            'completed_this_month': 0,
            'pending_reviews': 0
        }
        
        # Build the dashboard immediately
        self.build()

    def build(self):
        import flet as ft
        
        # Ensure page exists and has theme_mode
        if not hasattr(self, 'page') or not self.page or not hasattr(self.page, 'theme_mode'):
            # Fallback to light mode if page is not available
            theme_mode = ft.ThemeMode.LIGHT
        else:
            theme_mode = self.page.theme_mode
            
        colors = get_theme_colors(theme_mode)
        
        # Set container properties
        self.expand = True
        self.bgcolor = colors.bg

        # Header with welcome message and actions
        header = ft.Container(
            content=ft.Row([
                ft.Column([
                    ft.Text(
                        "Risk Assessment Dashboard",
                        size=32,
                        weight=ft.FontWeight.BOLD,
                        color=colors.text_primary
                    ),
                    ft.Text(
                        f"Welcome back, {self.current_user.get('name', 'Auditor') if self.current_user else 'Auditor'}",
                        size=16,
                        color=colors.text_secondary
                    )
                ], alignment=ft.CrossAxisAlignment.START),
                ft.Row([
                    create_modern_button(
                        colors, 
                        "Export Data", 
                        icon=Icons.DOWNLOAD,
                        on_click=self.export_assessments,
                        style="primary"
                    ),
                    create_modern_button(
                        colors, 
                        "New Assessment", 
                        icon=Icons.ADD,
                        on_click=self.handle_new_assessment,
                        style="success"
                    )
                ], spacing=12)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        )

        # Stats cards with modern design
        stats_row = ft.Row([
                ft.Container(
                content=create_stat_card(
                    colors,
                    "Active Assessments",
                    str(self.stats['active_assessments']),
                    Icons.ASSIGNMENT_OUTLINED,
                    colors.primary,
                    on_click=lambda _: self.on_navigate("assessments", "list", {"status": "active"})
                ),
                expand=True
            ),
            ft.Container(
                content=create_stat_card(
                    colors,
                    "High Risk Areas",
                    str(self.stats['high_risk_areas']),
                    Icons.ERROR_OUTLINE,
                    colors.danger,
                    on_click=lambda _: self.on_navigate("heatmap", None, {"filter": "high_risk"})
                ),
                expand=True
            ),
            ft.Container(
                content=create_stat_card(
                    colors,
                    "Completed This Month",
                    str(self.stats['completed_this_month']),
                    Icons.CHECK_CIRCLE_OUTLINE,
                    colors.success,
                    on_click=lambda _: self.on_navigate("assessments", "list", {"status": "completed"})
                ),
                expand=True
            ),
                ft.Container(
                content=create_stat_card(
                    colors,
                    "Pending Reviews",
                    str(self.stats['pending_reviews']),
                    Icons.SCHEDULE,
                    colors.warning,
                    on_click=lambda _: self.on_navigate("assessments", "list", {"status": "pending"})
                ),
                expand=True
            )
        ], spacing=16)

        # Risk Distribution Chart (Modern Glass Card)
        risk_distribution = create_modern_card(
            colors,
            ft.Column([
                ft.Row([
                    ft.Text(
                        "Risk Distribution by Department",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color=colors.text_primary
                    ),
                    create_modern_button(
                        colors,
                        "View Heatmap",
                        icon=Icons.GRID_VIEW,
                        on_click=lambda _: self.on_navigate("heatmap"),
                        style="secondary",
                        width=140
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(color=colors.border, height=20),
                self.create_risk_distribution_chart(colors)
            ], spacing=16)
        )

        # Recent Assessments Table (Modern Card)
        recent_assessments = create_modern_card(
            colors,
            ft.Column([
                ft.Row([
                    ft.Text(
                        "Recent Assessments",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color=colors.text_primary
                    ),
                    create_modern_button(
                        colors,
                        "View All",
                        icon=Icons.LIST_ALT,
                        on_click=lambda _: self.on_navigate("assessments", "list"),
                        style="secondary",
                        width=100
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(color=colors.border, height=20),
                 self.create_recent_assessments_table(colors)
            ], spacing=16)
        )

        # Main content with animations
        main_content = ft.Container(
            content=ft.Column([
                header,
                ft.Container(height=24),  # Spacing
                stats_row,
                ft.Container(height=24),  # Spacing
                risk_distribution,
                ft.Container(height=24),  # Spacing
                recent_assessments
            ], scroll=ft.ScrollMode.AUTO, spacing=0),
            padding=ft.padding.all(24),
            bgcolor=colors.bg,
            expand=True,
            animate=ft.Animation(300, ft.AnimationCurve.EASE_OUT)
        )

        # Set the content of this container
        self.content = main_content
        return self

    def create_risk_distribution_chart(self, colors):
        """Create modern risk distribution visualization"""
        departments = ["IT", "Finance", "Operations", "Marketing"]
        risk_data = [
            {"dept": "IT", "high": 35, "medium": 25, "low": 15},
            {"dept": "Finance", "high": 20, "medium": 30, "low": 25},
            {"dept": "Operations", "high": 15, "medium": 15, "low": 40},
            {"dept": "Marketing", "high": 10, "medium": 25, "low": 35}
        ]
        
        chart_rows = []
        for data in risk_data:
            dept_row = ft.Row([
                ft.Container(
                    content=ft.Text(data["dept"], color=colors.text_primary, weight=ft.FontWeight.W_500),
                    width=100
                ),
                ft.Container(
                    content=ft.Row([
                        # High risk bar
                        ft.Container(
                            content=ft.Text(f"{data['high']}%", color="white", size=12, weight=ft.FontWeight.BOLD),
                            bgcolor=colors.danger,
                            border_radius=8,
                            padding=ft.padding.symmetric(horizontal=8, vertical=4),
                            width=data["high"] * 3,  # Scale for visualization
                            alignment=ft.alignment.center,
                            animate=ft.Animation(500, ft.AnimationCurve.EASE_OUT)
                        ),
                        # Medium risk bar
                        ft.Container(
                            content=ft.Text(f"{data['medium']}%", color="white", size=12, weight=ft.FontWeight.BOLD),
                            bgcolor=colors.warning,
                            border_radius=8,
                            padding=ft.padding.symmetric(horizontal=8, vertical=4),
                            width=data["medium"] * 3,
                            alignment=ft.alignment.center,
                            animate=ft.Animation(600, ft.AnimationCurve.EASE_OUT)
                        ),
                        # Low risk bar
                        ft.Container(
                            content=ft.Text(f"{data['low']}%", color="white", size=12, weight=ft.FontWeight.BOLD),
                            bgcolor=colors.success,
                            border_radius=8,
                            padding=ft.padding.symmetric(horizontal=8, vertical=4),
                            width=data["low"] * 3,
                            alignment=ft.alignment.center,
                            animate=ft.Animation(700, ft.AnimationCurve.EASE_OUT)
                        )
                    ], spacing=4),
                    expand=True
                )
            ], alignment=ft.MainAxisAlignment.START)
            chart_rows.append(dept_row)
        
        # Legend
        legend = ft.Row([
            ft.Row([
                ft.Container(width=12, height=12, bgcolor=colors.danger, border_radius=2),
                ft.Text("High", color=colors.text_secondary, size=12)
            ], spacing=4),
            ft.Row([
                ft.Container(width=12, height=12, bgcolor=colors.warning, border_radius=2),
                ft.Text("Medium", color=colors.text_secondary, size=12)
            ], spacing=4),
            ft.Row([
                ft.Container(width=12, height=12, bgcolor=colors.success, border_radius=2),
                ft.Text("Low", color=colors.text_secondary, size=12)
            ], spacing=4)
        ], spacing=16, alignment=ft.MainAxisAlignment.END)
        
        return ft.Column([
            *chart_rows,
            ft.Container(height=12),
            legend
        ], spacing=12)

    def create_recent_assessments_table(self, colors):
        """Create modern assessments table"""
        if not self.assessments_data:
            # No data available - show empty state
            self.assessments_data = []
        
        # Table header
        header_row = ft.Row([
            ft.Container(
                content=ft.Text("ID", color=colors.text_secondary, weight=ft.FontWeight.BOLD, size=12),
                width=80
            ),
            ft.Container(
                content=ft.Text("Title", color=colors.text_secondary, weight=ft.FontWeight.BOLD, size=12),
                expand=True
            ),
            ft.Container(
                content=ft.Text("Department", color=colors.text_secondary, weight=ft.FontWeight.BOLD, size=12),
                width=120
            ),
            ft.Container(
                content=ft.Text("Risk Level", color=colors.text_secondary, weight=ft.FontWeight.BOLD, size=12),
                width=100
            ),
            ft.Container(
                content=ft.Text("Date", color=colors.text_secondary, weight=ft.FontWeight.BOLD, size=12),
                width=100
            )
        ])
        
        # Table rows
        table_rows = []
        def _format_date(a):
            d = a.get("assessment_date") or a.get("created_at") or a.get("date")
            if isinstance(d, str):
                # Trim ISO timestamp to date if needed
                return d.split("T")[0]
            try:
                # datetime/date object
                return d.strftime("%Y-%m-%d")
            except Exception:
                return "N/A"

        for assessment in self.assessments_data[:5]:  # Show only first 5
            risk_color = colors.danger if assessment["risk_level"] == "High" else colors.warning if assessment["risk_level"] == "Medium" else colors.success
            
            row = ft.Container(
                content=ft.Row([
                    ft.Container(
                        content=ft.Text(assessment["id"], color=colors.text_primary, size=12),
                        width=80
                    ),
                    ft.Container(
                        content=ft.Text(assessment["title"], color=colors.text_primary, size=12),
                        expand=True
                    ),
                    ft.Container(
                        content=ft.Text(assessment["department"], color=colors.text_secondary, size=12),
                        width=120
                    ),
                    ft.Container(
                        content=ft.Container(
                            content=ft.Text(assessment["risk_level"], color="white", size=10, weight=ft.FontWeight.BOLD),
                            bgcolor=risk_color,
                            border_radius=12,
                            padding=ft.padding.symmetric(horizontal=8, vertical=4),
                            alignment=ft.alignment.center
                        ),
                        width=100
                    ),
                    ft.Container(
                        content=ft.Text(_format_date(assessment), color=colors.text_secondary, size=12),
                        width=100
                    )
                ]),
                padding=ft.padding.symmetric(vertical=8, horizontal=4),
                border_radius=8,
                on_click=lambda _, aid=assessment["id"]: self.on_navigate("assessments", "details", {"id": aid}),
                animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
                ink=True
            )
            table_rows.append(row)
        
        return ft.Column([
            header_row,
            ft.Divider(color=colors.border, height=1),
            *table_rows
        ], spacing=4)

    async def export_assessments(self, e):
        """Export assessments functionality"""
        print("🔧 DEBUG: export_assessments called")
        try:
            print("🔧 DEBUG: Importing ExcelExporter")
            from utils.excel_exporter import ExcelExporter
            print("✅ DEBUG: ExcelExporter imported successfully")
            
            # Show loading state
            print("🔧 DEBUG: Showing loading snackbar")
            self.show_snackbar("Preparing export...")
            
            # Get assessments data from API
            print("🔧 DEBUG: Attempting to get assessments from API")
            try:
                assessments = await self.auditing_client.get_assessments()
                print(f"✅ DEBUG: Got {len(assessments) if assessments else 0} assessments from API")
            except Exception as api_error:
                print(f"❌ DEBUG: API error: {api_error}")
                self.show_snackbar("API connection failed. Creating empty export template.", ft.Colors.AMBER)
                assessments = []
            
            # Export to Excel (even if empty)
            print("🔧 DEBUG: Creating ExcelExporter instance")
            exporter = ExcelExporter()
            print("🔧 DEBUG: Calling export_assessments")
            filename = exporter.export_assessments(assessments or [])
            print(f"✅ DEBUG: Export completed, filename: {filename}")
            
            if assessments:
                self.show_snackbar(f"Assessments exported successfully to {filename}", ft.Colors.GREEN)
            else:
                self.show_snackbar(f"Empty template exported to {filename}", ft.Colors.AMBER)
            
        except Exception as ex:
            print(f"❌ DEBUG: Export error: {ex}")
            import traceback
            traceback.print_exc()
            self.show_snackbar(f"Export failed: {str(ex)}", ft.Colors.RED)

    def show_snackbar(self, message, color=None):
        """Show snackbar message"""
        colors = get_theme_colors(self.page.theme_mode)
        snackbar = ft.SnackBar(
            content=ft.Text(message, color="white"),
            bgcolor=color or colors.primary
        )
        self.page.snack_bar = snackbar
        snackbar.open = True
        self.page.update()

    def handle_button_error(self, error, action_name):
        """Handle button click errors with proper user feedback"""
        error_message = f"{action_name} failed: {str(error)}"
        print(f"Button error: {error_message}")
        self.show_snackbar(error_message, ft.Colors.RED)

    def handle_new_assessment(self, e):
        """Create new assessment form dialog on dashboard"""
        print("🔧 DEBUG: handle_new_assessment called")
        try:
            print("🔧 DEBUG: Attempting to show assessment dialog")
            self.show_assessment_dialog()
            print("✅ DEBUG: Assessment dialog shown successfully")
        except Exception as error:
            print(f"❌ DEBUG: handle_new_assessment failed: {error}")
            self.handle_button_error(error, "Create New Assessment")

    def show_assessment_dialog(self):
        """Show new assessment creation dialog"""
        print("🔧 DEBUG: show_assessment_dialog called")
        try:
            print("🔧 DEBUG: Importing UnifiedAssessmentForm")
            from src.views.assessments.unified_form import UnifiedAssessmentForm
            print("✅ DEBUG: UnifiedAssessmentForm imported successfully")
            
            print("🔧 DEBUG: Creating assessment form")
            # Create assessment form
            form = UnifiedAssessmentForm(
                self.page,
                self.current_user,
                mode="create",
                assessment=None
            )
            print("✅ DEBUG: AssessmentFormView created successfully")
            
            print("🔧 DEBUG: Creating dialog")
            # Create dialog
            dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text("New Risk Assessment", weight=ft.FontWeight.BOLD),
                content=ft.Container(
                    width=800,
                    height=600,
                    content=form
                ),
                actions=[
                    ft.TextButton("Cancel", on_click=self.close_dialog),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            print("✅ DEBUG: Dialog created successfully")
            
            print("🔧 DEBUG: Setting page dialog and opening")
            self.page.dialog = dialog
            dialog.open = True
            self.page.update()
            print("✅ DEBUG: Dialog opened and page updated successfully")
            
        except Exception as e:
            print(f"❌ DEBUG: show_assessment_dialog failed: {e}")
            import traceback
            traceback.print_exc()
            self.show_snackbar(f"Error creating assessment form: {e}", ft.Colors.RED)

    def close_dialog(self, e):
        """Close the current dialog"""
        if self.page.dialog:
            self.page.dialog.open = False
            self.page.update()

    async def load_dashboard_data(self):
        """Load dashboard data from API"""
        try:
            # Load assessments
            assessments = await self.auditing_client.get_assessments()
            if assessments:
                self.assessments_data = assessments
                
                # Calculate stats
                self.stats['active_assessments'] = len([a for a in assessments if a.get('status') == 'active'])
                self.stats['high_risk_areas'] = len([a for a in assessments if a.get('risk_level') == 'High'])
                self.stats['completed_this_month'] = len([a for a in assessments if a.get('status') == 'completed'])
                self.stats['pending_reviews'] = len([a for a in assessments if a.get('status') == 'pending'])
            
            self.update()
            
        except Exception as ex:
            print(f"Error loading dashboard data: {ex}")
            self.show_snackbar("Failed to load dashboard data", ft.Colors.RED)

    def apply_theme(self, colors):
        """Apply theme colors to the dashboard"""
        try:
            # Update the container's background color
            self.bgcolor = colors.bg
            
            # Rebuild the content with new colors
            self.build()
            
            if hasattr(self, 'page') and self.page:
                self.page.update()
        except Exception as e:
            print(f"Error applying theme to dashboard: {e}")

    def did_mount(self):
        """Called when the view is mounted"""
        # Load data asynchronously - but don't call automatically to avoid warnings
        # Data will be loaded when explicitly requested
        pass