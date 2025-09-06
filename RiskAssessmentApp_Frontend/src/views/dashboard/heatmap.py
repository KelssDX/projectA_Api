import flet as ft
from flet import Icons
import asyncio
from src.utils.theme import (
    get_theme_colors,
    create_modern_button,
    create_glass_card,
    create_modern_card,
    create_stat_card,
    apply_theme_to_control,
)
from src.controllers.assessment_controller import AssessmentController


class HeatmapView(ft.Container):
    def __init__(self, page, user, reference_id=None, on_navigate=None):
        super().__init__()
        self.page = page
        self.user = user
        self.reference_id = reference_id or 1  # Default reference ID
        self.on_navigate = on_navigate
        self.assessment_controller = AssessmentController()
        self.heatmap_data = None
        self.expand = True
        self.enabled_levels = {"Critical": True, "High": True, "Medium": True, "Low": True, "Very Low": True}
        # Resizable panel flex values
        self.left_flex = getattr(self, "left_flex", 1)
        self.center_flex = getattr(self, "center_flex", 3)
        self.right_flex = getattr(self, "right_flex", 1)
        
        # Initialize the view
        self._init_async()

    def _init_async(self):
        """Initialize the view asynchronously"""
        # Don't create task immediately, let the page handle async operations
        # Build UI first with loading state
        self._build_ui()
        
    def load_data(self):
        """Load heatmap data when view is shown"""
        if hasattr(self, 'page') and self.page:
            self.page.run_task(self._load_heatmap_data)

    async def _load_heatmap_data(self):
        """Load heatmap data from the API"""
        try:
            self.heatmap_data = await self.assessment_controller.get_heatmap_data(self.reference_id)
            self._build_ui()
            if hasattr(self, 'page') and self.page:
                self.page.update()
        except Exception as e:
            print(f"Error loading heatmap data: {e}")
            self._build_ui()  # Build UI with error state
            if hasattr(self, 'page') and self.page:
                self.page.update()

    def _build_ui(self):
        """Build the UI components"""
        # Header
        self.colors = get_theme_colors(self.page.theme_mode if hasattr(self.page, "theme_mode") else ft.ThemeMode.LIGHT)
        colors = self.colors

        # Reference input (store for later use)
        self.reference_field = ft.TextField(
            value=str(self.reference_id),
            width=160,
            label="Reference ID",
            cursor_color=colors.text_primary,
        )

        header = ft.Container(
            content=ft.Row([
                ft.Column([
                    ft.Text("Risk Heatmap", size=24, weight=ft.FontWeight.BOLD, color=colors.text_primary),
                    ft.Text("Interactive risk matrix", size=14, color=colors.text_secondary),
                ], alignment=ft.CrossAxisAlignment.START),
                ft.Row([
                    self.reference_field,
                    ft.Container(width=8),
                    create_modern_button(colors, "Apply", icon=Icons.PLAY_ARROW, on_click=self.apply_reference_filter, style="primary"),
                    create_modern_button(colors, "Refresh", icon=Icons.REFRESH, on_click=self.refresh_heatmap, style="secondary"),
                ], spacing=8)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        )

        # Filter bar
        # Left filter panel (Dashboard-style card)
        # Department dropdown will be populated asynchronously
        self.department_dropdown = ft.Dropdown(
            label="Department",
            width=220,
            options=[],
            on_change=lambda e: self.page.run_task(self._load_heatmap_data)
        )

        from src.utils.theme import create_modern_card
        filter_panel = create_modern_card(
            colors,
            ft.Column([
                ft.Text("Filters", size=16, weight=ft.FontWeight.BOLD, color=colors.text_primary),
                ft.Text("Department", size=12, color=colors.text_secondary),
                self.department_dropdown,
                ft.Text("Risk Levels", size=12, color=colors.text_secondary),
                ft.Checkbox(label="Critical", value=True, on_change=lambda e: self._on_level_checkbox_change("Critical", e)),
                ft.Checkbox(label="High", value=True, on_change=lambda e: self._on_level_checkbox_change("High", e)),
                ft.Checkbox(label="Medium", value=True, on_change=lambda e: self._on_level_checkbox_change("Medium", e)),
                ft.Checkbox(label="Low", value=True, on_change=lambda e: self._on_level_checkbox_change("Low", e)),
                ft.Checkbox(label="Very Low", value=True, on_change=lambda e: self._on_level_checkbox_change("Very Low", e)),
                ft.Container(height=10),
                ft.ElevatedButton(text="Export Heatmap", icon=Icons.DOWNLOAD, on_click=self.export_heatmap),
            ], scroll=ft.ScrollMode.AUTO, spacing=10),
            padding=ft.padding.all(16)
        )

        # Legend inline for center panel
        legend = ft.Row([
            ft.Row([ft.Container(width=16, height=16, bgcolor="#8B0000", border_radius=3), ft.Container(width=6), ft.Text("Critical", color=colors.text_primary)]),
            ft.Row([ft.Container(width=16, height=16, bgcolor="#e74c3c", border_radius=3), ft.Container(width=6), ft.Text("High", color=colors.text_primary)]),
            ft.Row([ft.Container(width=16, height=16, bgcolor="#f39c12", border_radius=3), ft.Container(width=6), ft.Text("Medium", color=colors.text_primary)]),
            ft.Row([ft.Container(width=16, height=16, bgcolor="#2ecc71", border_radius=3), ft.Container(width=6), ft.Text("Low", color=colors.text_primary)]),
            ft.Row([ft.Container(width=16, height=16, bgcolor="#27ae60", border_radius=3), ft.Container(width=6), ft.Text("Very Low", color=colors.text_primary)]),
        ], spacing=20, alignment=ft.MainAxisAlignment.CENTER)

        # Heatmap grid wrapped in a dashboard-style card
        heatmap_card = create_modern_card(colors, self.create_heatmap_grid(), padding=ft.padding.all(16))

        # Statistics
        stats = self.create_stats_section()

        # Three-pane layout
        center_column = ft.Column([
            create_modern_card(colors, legend, padding=ft.padding.symmetric(horizontal=16, vertical=12)),
            ft.Container(height=12),
            heatmap_card
        ], spacing=0, expand=True, scroll=ft.ScrollMode.AUTO)

        insights_panel = create_modern_card(
            colors,
            ft.Column([
                ft.Text("Insights", size=16, weight=ft.FontWeight.BOLD, color=colors.text_primary),
                stats
            ], scroll=ft.ScrollMode.AUTO, spacing=10),
            padding=ft.padding.all(16)
        )

        # Build resizable row using current flex values
        main_row = self._build_resizable_row(filter_panel, center_column, insights_panel)

        # Keep a reference to replace on drag
        self._main_content_container = ft.Container(expand=True, content=main_row, padding=ft.padding.all(24), bgcolor=colors.bg)

        # Assemble the view
        self.content = ft.Column([
            header,
            self._main_content_container
        ], spacing=0, expand=True)

    # Theming hook
    def apply_theme(self, colors):
        # Normalize the entire view tree to theme colors
        try:
            # Rebuild to rebind token-based colors like Dashboard
            self._build_ui()
            apply_theme_to_control(self, colors)
        except Exception:
            pass

    def create_heatmap_grid(self):
        """Create the risk heatmap grid using API data"""
        colors = getattr(self, 'colors', get_theme_colors(self.page.theme_mode if hasattr(self.page, "theme_mode") else ft.ThemeMode.LIGHT))
        if not self.heatmap_data:
            return self._create_loading_or_error_grid("Loading heatmap data...")

        try:
            # Extract heatmap grid from API response
            heatmap_grid = self.heatmap_data.get("heatmapGrid", {})
            
            if not heatmap_grid:
                return self._create_loading_or_error_grid("No heatmap data available")

            # Define standard likelihood and impact levels
            # The API returns nested dictionary: {impact: {likelihood: count}}
            impact_levels = ["Very High", "High", "Medium", "Low", "Very Low"]
            likelihood_levels = ["Very Low", "Low", "Medium", "High", "Very High"]

            # Create header row with likelihood levels
            header_cells = [ft.Container(
                width=120,
                height=40,
                alignment=ft.alignment.center,
                content=ft.Text("Impact \\ Likelihood", size=12, weight=ft.FontWeight.BOLD, color=colors.text_secondary)
            )]

            for likelihood in likelihood_levels:
                header_cells.append(ft.Container(
                    width=100,
                    height=40,
                    alignment=ft.alignment.center,
                    content=ft.Text(likelihood, size=12, weight=ft.FontWeight.BOLD, color=colors.text_secondary)
                ))

            header_row = ft.Row(header_cells)

            # Create impact rows with risk cells
            rows = [header_row]

            for impact in impact_levels:
                row_cells = [ft.Container(
                    width=120,
                    height=60,
                    padding=10,
                    alignment=ft.alignment.center,
                    content=ft.Text(impact, size=12, weight=ft.FontWeight.BOLD, color=colors.text_secondary)
                )]

                for likelihood in likelihood_levels:
                    # Get count from API data
                    count = 0
                    if impact in heatmap_grid and likelihood in heatmap_grid[impact]:
                        count = heatmap_grid[impact][likelihood]

                    # Determine cell color and risk level based on impact/likelihood combination
                    risk_level, color = self._calculate_risk_level(impact, likelihood)

                    # Skip drawing values for disabled levels (keeps grid but greys out)
                    is_enabled = self.enabled_levels.get(risk_level, True)
                    cell = ft.Container(
                        width=100,
                        height=60,
                        padding=5,
                        alignment=ft.alignment.center,
                        content=ft.Container(
                            bgcolor=(color if is_enabled else colors.surface),
                            border=ft.border.all(1, colors.border) if count == 0 else None,
                            border_radius=5,
                            padding=5,
                            alignment=ft.alignment.center,
                            content=ft.Text(
                                str(count) if count > 0 else "0",
                                size=14,
                                weight=ft.FontWeight.BOLD,
                                color=("white" if (count > 0 and is_enabled) else colors.text_secondary)
                            )
                        ),
                        on_click=lambda e, i=impact, l=likelihood, c=count, r=risk_level: self.show_cell_details(i, l, c, r)
                    )

                    row_cells.append(cell)

                rows.append(ft.Row(row_cells))

            # Wrap in a container
            return ft.Container(
                padding=10,
                bgcolor=colors.surface,
                border=ft.border.all(1, colors.border),
                border_radius=8,
                content=ft.Column(rows, spacing=10, scroll=ft.ScrollMode.AUTO)
            )

        except Exception as e:
            print(f"Error creating heatmap grid: {e}")
            return self._create_loading_or_error_grid(f"Error loading heatmap: {str(e)}")

    def _create_loading_or_error_grid(self, message):
        """Create a placeholder grid for loading or error states"""
        colors = getattr(self, 'colors', get_theme_colors(self.page.theme_mode if hasattr(self.page, "theme_mode") else ft.ThemeMode.LIGHT))
        return ft.Container(
            padding=20,
            bgcolor=colors.surface,
            border=ft.border.all(1, colors.border),
            border_radius=8,
            content=ft.Container(
                height=300,
                alignment=ft.alignment.center,
                content=ft.Column([
                    ft.Icon(Icons.ASSESSMENT, size=48, color=colors.text_secondary),
                    ft.Container(height=10),
                    ft.Text(message, size=16, color=colors.text_secondary, text_align=ft.TextAlign.CENTER)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            )
        )

    def _calculate_risk_level(self, impact, likelihood):
        """Calculate risk level and color based on impact and likelihood"""
        # Risk matrix calculation (simplified)
        impact_scores = {"Very Low": 1, "Low": 2, "Medium": 3, "High": 4, "Very High": 5}
        likelihood_scores = {"Very Low": 1, "Low": 2, "Medium": 3, "High": 4, "Very High": 5}
        
        impact_score = impact_scores.get(impact, 3)
        likelihood_score = likelihood_scores.get(likelihood, 3)
        
        risk_score = impact_score * likelihood_score
        
        if risk_score >= 20:
            return "Critical", "#8B0000"  # Dark red
        elif risk_score >= 15:
            return "High", "#e74c3c"     # Red
        elif risk_score >= 10:
            return "Medium-High", "#f39c12"  # Orange
        elif risk_score >= 6:
            return "Medium", "#f1c40f"   # Yellow
        elif risk_score >= 3:
            return "Low", "#2ecc71"      # Green
        else:
            return "Very Low", "#27ae60"  # Dark green

    def _on_level_checkbox_change(self, level, e):
        try:
            self.enabled_levels[level] = bool(getattr(e.control, "value", True))
            # Just rebuild grid visual state
            self._build_ui()
            if hasattr(self, 'page') and self.page:
                self.page.update()
        except Exception:
            pass

    def create_stats_section(self):
        """Create statistics cards based on API data"""
        if not self.heatmap_data:
            return ft.Container()

        try:
            # Calculate statistics from heatmap data
            heatmap_grid = self.heatmap_data.get("heatmapGrid", {})
            stats = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0, "Total": 0}
            
            for impact, likelihood_dict in heatmap_grid.items():
                for likelihood, count in likelihood_dict.items():
                    risk_level, _ = self._calculate_risk_level(impact, likelihood)
                    
                    if risk_level in ["Critical"]:
                        stats["Critical"] += count
                    elif risk_level in ["High"]:
                        stats["High"] += count
                    elif risk_level in ["Medium-High", "Medium"]:
                        stats["Medium"] += count
                    elif risk_level in ["Low", "Very Low"]:
                        stats["Low"] += count
                    
                    stats["Total"] += count

            # Create statistics cards (clickable)
            return ft.Container(
                margin=ft.margin.only(top=20, bottom=30, left=30, right=30),
                content=ft.Row([
                    self.create_stat_card("Critical Risk", str(stats["Critical"]), "#8B0000", lambda e: self._navigate_filter(level="Critical")),
                    self.create_stat_card("High Risk", str(stats["High"]), "#e74c3c", lambda e: self._navigate_filter(level="High")),
                    self.create_stat_card("Medium Risk", str(stats["Medium"]), "#f39c12", lambda e: self._navigate_filter(level="Medium")),
                    self.create_stat_card("Low Risk", str(stats["Low"]), "#2ecc71", lambda e: self._navigate_filter(level="Low")),
                    self.create_stat_card("Total Items", str(stats["Total"]), "#3498db", lambda e: self._navigate_filter())
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=15)
            )
            
        except Exception as e:
            print(f"Error creating stats section: {e}")
            return ft.Container()

    def create_stat_card(self, title, value, color, on_click=None):
        colors = getattr(self, 'colors', get_theme_colors(self.page.theme_mode if hasattr(self.page, "theme_mode") else ft.ThemeMode.LIGHT))
        return ft.Container(
            width=200,
            height=100,
            border=ft.border.all(1, colors.border),
            border_radius=8,
            padding=20,
            bgcolor=colors.surface,
            content=ft.Column([
                ft.Text(title, size=14, color=colors.text_secondary),
                ft.Container(height=6),
                ft.Text(value, size=28, weight=ft.FontWeight.BOLD, color=color)
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            on_click=on_click
        )

    def show_reference_filter(self, e):
        """Show reference filter dropdown"""
        dialog = ft.AlertDialog(
            title=ft.Text("Select Reference ID"),
            content=ft.Column([
                ft.Container(
                    content=ft.Text("Reference 1"),
                    on_click=lambda e: self.change_reference(1)
                ),
                ft.Container(
                    content=ft.Text("Reference 2"),
                    on_click=lambda e: self.change_reference(2)
                ),
                ft.Container(
                    content=ft.Text("Reference 3"),
                    on_click=lambda e: self.change_reference(3)
                ),
                ft.Container(
                    content=ft.Text("Reference 4"),
                    on_click=lambda e: self.change_reference(4)
                ),
                ft.Container(
                    content=ft.Text("Reference 5"),
                    on_click=lambda e: self.change_reference(5)
                ),
            ], spacing=10, height=200),
            actions=[
                ft.TextButton("Cancel", on_click=self.close_dialog),
            ],
        )

        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    async def change_reference(self, new_reference_id):
        """Change the reference ID and reload heatmap data"""
        self.reference_id = new_reference_id
        self.close_dialog(None)
        await self._load_heatmap_data()

    async def refresh_heatmap(self, e):
        """Refresh the heatmap data"""
        await self._load_heatmap_data()

    def export_heatmap(self, e):
        """Export heatmap"""
        dialog = ft.AlertDialog(
            title=ft.Text("Export Heatmap"),
            content=ft.Column([
                ft.Text("Select export format:"),
                ft.Container(height=10),
                ft.ElevatedButton(
                    text="Export as PDF",
                    bgcolor="#3498db",
                    color="white",
                    width=200,
                    on_click=self.close_dialog
                ),
                ft.ElevatedButton(
                    text="Export as Excel",
                    bgcolor="#2ecc71",
                    color="white",
                    width=200,
                    on_click=self.close_dialog
                ),
                ft.ElevatedButton(
                    text="Export as Image",
                    bgcolor="#f39c12",
                    color="white",
                    width=200,
                    on_click=self.close_dialog
                ),
            ], spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            actions=[
                ft.TextButton("Cancel", on_click=self.close_dialog),
            ],
        )

        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def show_cell_details(self, impact, likelihood, count, risk_level):
        """Show details for a heatmap cell"""
        def view_assessments(_):
            self._navigate_filter(level=risk_level, impact=impact, likelihood=likelihood)

        dialog = ft.AlertDialog(
            title=ft.Text(f"Risk Cell Details"),
            content=ft.Column([
                ft.Text(f"Impact Level: {impact}", size=14, weight=ft.FontWeight.BOLD),
                ft.Text(f"Likelihood Level: {likelihood}", size=14, weight=ft.FontWeight.BOLD),
                ft.Text(f"Risk Level: {risk_level}", size=14, weight=ft.FontWeight.BOLD),
                ft.Container(height=10),
                ft.Text(f"Assessment Count: {count}", size=16, weight=ft.FontWeight.BOLD, color="#3498db"),
                ft.Container(height=10),
                ft.Text(f"Reference ID: {self.reference_id}", size=14),
                ft.Container(height=10),
                ft.Text("This cell represents the intersection of:", weight=ft.FontWeight.BOLD),
                ft.Text(f"• Impact: {impact}"),
                ft.Text(f"• Likelihood: {likelihood}"),
                ft.Text(f"• Total assessments in this category: {count}"),
                ft.Container(height=10),
                ft.Text("Risk Matrix Information:", weight=ft.FontWeight.BOLD),
                ft.Text(f"• Combined Risk Level: {risk_level}"),
                ft.Text("• This represents the intersection of impact and likelihood"),
                ft.Text("• Higher numbers indicate more assessments in this risk category"),
            ], width=450),
            actions=[
                ft.TextButton("Close", on_click=self.close_dialog),
                ft.TextButton("View Assessments", on_click=view_assessments) if count > 0 else None,
            ],
        )

        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def close_dialog(self, e):
        """Close the current dialog"""
        self.page.dialog.open = False
        self.page.update()

    async def cleanup(self):
        """Cleanup resources when view is destroyed"""
        try:
            await self.assessment_controller.close()
        except Exception as e:
            print(f"Error closing assessment controller: {e}")

    def _navigate_filter(self, level=None, impact=None, likelihood=None):
        # Use app instance to navigate to assessments with filters
        if hasattr(self.page, 'APP_INSTANCE') and self.page.APP_INSTANCE:
            app = self.page.APP_INSTANCE
            # Build filter object
            flt = {}
            if level:
                flt['risk_level'] = level
            if impact:
                flt['impact'] = impact
            if likelihood:
                flt['likelihood'] = likelihood
            app.pending_assessment_filter = flt
            app.current_reference_id = self.reference_id
            self.close_dialog(None)
            app.show_view("assessments")

    def apply_reference_filter(self, e):
        """Apply reference filter and reload heatmap data"""
        print("🔧 DEBUG: apply_reference_filter called")
        try:
            # Get reference ID from text field if available
            if hasattr(self, 'reference_field'):
                old_id = self.reference_id
                self.reference_id = int(self.reference_field.value or 1)
                print(f"🔧 DEBUG: Changed reference ID from {old_id} to {self.reference_id}")
            print("🔧 DEBUG: Calling load_data()")
            self.load_data()
            print("✅ DEBUG: Reference filter applied successfully")
        except Exception as error:
            print(f"❌ DEBUG: Error applying reference filter: {error}")
            import traceback
            traceback.print_exc()

    def refresh_heatmap(self, e):
        """Refresh heatmap data"""
        print("🔧 DEBUG: refresh_heatmap called")
        try:
            print("🔧 DEBUG: Calling load_data()")
            self.load_data()
            print("✅ DEBUG: Heatmap refreshed successfully")
        except Exception as error:
            print(f"❌ DEBUG: Error refreshing heatmap: {error}")
            import traceback
            traceback.print_exc()

    # ---- Resizable layout helpers ----
    def _build_resizable_row(self, left_panel, center_panel, right_panel):
        colors = self.colors

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
