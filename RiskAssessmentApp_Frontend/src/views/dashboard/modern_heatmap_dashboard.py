import flet as ft
import asyncio
from datetime import datetime
from src.controllers.assessment_controller import AssessmentController
from src.views.assessment.modern_form import ModernAssessmentForm
from src.utils.formatters import format_date, format_risk_score
import json


class ModernHeatmapDashboard(ft.Container):
    def __init__(self, page, user, on_assessment_created=None):
        super().__init__()
        self.page = page
        self.user = user
        self.on_assessment_created = on_assessment_created
        self.expand = True
        
        # Controllers
        self.assessment_controller = AssessmentController()
        
        # State management
        self.heatmap_data = {}
        self.selected_reference_id = 1
        self.view_mode = "combined"  # combined, split, overlay
        self.filter_settings = {
            "department": "All",
            "time_period": "current",
            "assessment_type": "all"
        }
        self.is_real_time = True
        self.comparison_mode = False
        self.comparison_data = {}
        
        # UI Components
        self.heatmap_container = None
        self.side_panel = None
        self.assessment_form = None
        self.quick_stats = None
        self.selected_cell_info = None
        
        # Animation state
        self.animation_enabled = True
        self.last_update = datetime.now()
        
        # Initialize dashboard
        self._init_dashboard()
    
    def _init_dashboard(self):
        """Initialize the dashboard"""
        self._build_ui()
        asyncio.create_task(self._load_initial_data())
        
        # Set up real-time updates if enabled
        if self.is_real_time:
            asyncio.create_task(self._start_real_time_updates())
    
    async def _load_initial_data(self):
        """Load initial heatmap and assessment data"""
        try:
            self._show_loading_state()
            
            # Load multiple reference IDs for comprehensive view
            reference_ids = [1, 2, 3, 4, 5]
            tasks = [self.assessment_controller.get_heatmap_data(ref_id) for ref_id in reference_ids]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process and combine heatmap data
            self.heatmap_data = self._process_heatmap_results(results, reference_ids)
            
            # Update UI with loaded data
            self._update_heatmap_display()
            self._update_quick_stats()
            
        except Exception as e:
            self._show_error(f"Error loading heatmap data: {str(e)}")
        finally:
            self._hide_loading_state()
    
    def _build_ui(self):
        """Build the main dashboard UI"""
        # Main header with controls
        header = self._build_dashboard_header()
        
        # Main content area based on view mode
        main_content = self._build_main_content()
        
        # Layout
        self.content = ft.Column([
            header,
            ft.Divider(height=1, color="#e6e9ed"),
            main_content
        ], spacing=0, expand=True)
    
    def _build_dashboard_header(self):
        """Build the dashboard header with controls and filters"""
        return ft.Container(
            height=80,
            bgcolor=None,
            padding=ft.padding.symmetric(horizontal=30, vertical=15),
            content=ft.Row([
                # Title and mode selector
                ft.Column([
                    ft.Text(
                        "Risk Heatmap Dashboard",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color="#2c3e50"
                    ),
                    ft.Row([
                        ft.Text("Live Risk Intelligence", size=12, color="#7f8c8d"),
                        ft.Container(
                            width=8,
                            height=8,
                            bgcolor="#2ecc71" if self.is_real_time else "#95a5a6",
                            border_radius=4,
                            margin=ft.margin.only(left=8)
                        )
                    ])
                ], spacing=2),
                
                ft.Container(expand=True),
                
                # View mode controls
                ft.Container(
                    content=ft.Row([
                        ft.Text("View:", size=14, weight=ft.FontWeight.BOLD, color="#2c3e50"),
                        ft.SegmentedButton(
                            selected={"combined"},
                            allow_empty_selection=False,
                            allow_multiple_selection=False,
                            segments=[
                                ft.Segment(
                                    value="combined",
                                    label=ft.Text("Combined"),
                                    icon=ft.Icon(ft.icons.DASHBOARD)
                                ),
                                ft.Segment(
                                    value="split",
                                    label=ft.Text("Split"),
                                    icon=ft.Icon(ft.icons.VIEW_COLUMN)
                                ),
                                ft.Segment(
                                    value="overlay",
                                    label=ft.Text("Overlay"),
                                    icon=ft.Icon(ft.icons.LAYERS)
                                )
                            ],
                            on_change=self._on_view_mode_change
                        )
                    ], spacing=10)
                ),
                
                ft.Container(width=20),
                
                # Action buttons
                ft.Row([
                    ft.ElevatedButton(
                        text="New Assessment",
                        icon=ft.icons.ADD_CIRCLE,
                        bgcolor="#2ecc71",
                        color="white",
                        on_click=self._create_new_assessment,
                        tooltip="Create new risk assessment"
                    ),
                    ft.Container(width=10),
                    ft.PopupMenuButton(
                        items=[
                            ft.PopupMenuItem(
                                text="Compare Scenarios",
                                icon=ft.icons.COMPARE,
                                on_click=self._toggle_comparison_mode
                            ),
                            ft.PopupMenuItem(
                                text="Export Heatmap",
                                icon=ft.icons.DOWNLOAD,
                                on_click=self._export_heatmap
                            ),
                            ft.PopupMenuItem(
                                text="Settings",
                                icon=ft.icons.SETTINGS,
                                on_click=self._show_settings
                            ),
                            ft.PopupMenuItem(),  # Divider
                            ft.PopupMenuItem(
                                text="Toggle Real-time",
                                icon=ft.icons.SYNC if self.is_real_time else ft.icons.SYNC_DISABLED,
                                on_click=self._toggle_real_time
                            )
                        ],
                        icon=ft.icons.MORE_VERT,
                        tooltip="More options"
                    )
                ])
            ])
        )
    
    def _build_main_content(self):
        """Build main content based on view mode"""
        if self.view_mode == "combined":
            return self._build_combined_view()
        elif self.view_mode == "split":
            return self._build_split_view()
        elif self.view_mode == "overlay":
            return self._build_overlay_view()
        else:
            return self._build_combined_view()
    
    def _build_combined_view(self):
        """Build combined dashboard view"""
        return ft.Container(
            expand=True,
            content=ft.Row([
                # Main heatmap area
                ft.Column([
                    self._build_heatmap_controls(),
                    self._build_interactive_heatmap(),
                    self._build_quick_stats_bar()
                ], expand=3),
                
                ft.Container(width=1, bgcolor="#e6e9ed"),
                
                # Side panel for details and quick actions
                ft.Column([
                    self._build_side_panel()
                ], expand=1, scroll=ft.ScrollMode.AUTO)
            ])
        )
    
    def _build_split_view(self):
        """Build split view with heatmap and form side by side"""
        return ft.Container(
            expand=True,
            content=ft.Row([
                # Left: Heatmap
                ft.Column([
                    self._build_heatmap_controls(),
                    self._build_interactive_heatmap(),
                    self._build_quick_stats_bar()
                ], expand=1),
                
                ft.Container(width=2, bgcolor="#34495e"),
                
                # Right: Assessment form or details
                ft.Column([
                    self._build_form_panel()
                ], expand=1, scroll=ft.ScrollMode.AUTO)
            ])
        )
    
    def _build_overlay_view(self):
        """Build overlay view with floating panels"""
        return ft.Container(
            expand=True,
            content=ft.Stack([
                # Main heatmap (full screen)
                ft.Column([
                    self._build_heatmap_controls(),
                    self._build_interactive_heatmap(),
                    self._build_quick_stats_bar()
                ]),
                
                # Floating side panel
                ft.Positioned(
                    right=20,
                    top=20,
                    bottom=20,
                    width=350,
                    child=ft.Card(
                        elevation=8,
                        content=ft.Container(
                            padding=15,
                            content=self._build_side_panel(),
                            bgcolor="white",
                            border_radius=10
                        )
                    )
                )
            ])
        )
    
    def _build_heatmap_controls(self):
        """Build heatmap filter and control panel"""
        return ft.Container(
            height=60,
            bgcolor=None,
            padding=ft.padding.symmetric(horizontal=20, vertical=10),
            content=ft.Row([
                # Filters
                ft.Row([
                    ft.Text("Filters:", weight=ft.FontWeight.BOLD, color="#2c3e50"),
                    ft.Dropdown(
                        label="Department",
                        width=150,
                        value=self.filter_settings["department"],
                        options=[
                            ft.dropdown.Option("All"),
                            ft.dropdown.Option("IT"),
                            ft.dropdown.Option("Finance"),
                            ft.dropdown.Option("Operations"),
                            ft.dropdown.Option("Legal"),
                            ft.dropdown.Option("HR")
                        ],
                        on_change=self._on_filter_change
                    ),
                    ft.Dropdown(
                        label="Time Period",
                        width=120,
                        value=self.filter_settings["time_period"],
                        options=[
                            ft.dropdown.Option("current", "Current"),
                            ft.dropdown.Option("monthly", "Monthly"),
                            ft.dropdown.Option("quarterly", "Quarterly"),
                            ft.dropdown.Option("yearly", "Yearly")
                        ],
                        on_change=self._on_time_filter_change
                    )
                ], spacing=15),
                
                ft.Container(expand=True),
                
                # Reference selector and actions
                ft.Row([
                    ft.Text("Reference:", weight=ft.FontWeight.BOLD, color="#2c3e50"),
                    ft.Dropdown(
                        width=100,
                        value=str(self.selected_reference_id),
                        options=[ft.dropdown.Option(str(i)) for i in range(1, 6)],
                        on_change=self._on_reference_change
                    ),
                    ft.IconButton(
                        icon=ft.icons.REFRESH,
                        tooltip="Refresh data",
                        on_click=self._refresh_data,
                        icon_color="#3498db"
                    ),
                    ft.IconButton(
                        icon=ft.icons.FULLSCREEN,
                        tooltip="Toggle fullscreen",
                        on_click=self._toggle_fullscreen,
                        icon_color="#3498db"
                    )
                ], spacing=10)
            ])
        )
    
    def _build_interactive_heatmap(self):
        """Build the main interactive heatmap"""
        if not self.heatmap_data:
            return ft.Container(
                height=400,
                alignment=ft.alignment.center,
                content=ft.Column([
                    ft.ProgressRing(width=50, height=50),
                    ft.Container(height=20),
                    ft.Text("Loading heatmap data...", size=16)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            )
        
        # Get current heatmap data
        current_data = self.heatmap_data.get(self.selected_reference_id, {})
        heatmap_grid = current_data.get('heatmapGrid', {})
        
        if not heatmap_grid:
            return ft.Container(
                height=400,
                alignment=ft.alignment.center,
                content=ft.Text("No heatmap data available", size=16)
            )
        
        # Build interactive heatmap matrix
        impact_levels = ["Very High", "High", "Medium", "Low", "Very Low"]
        likelihood_levels = ["Very Low", "Low", "Medium", "High", "Very High"]
        
        # Header row
        header_cells = [ft.Container(
            width=120,
            height=50,
            alignment=ft.alignment.center,
            content=ft.Text(
                "Impact ↓ / Likelihood →",
                size=12,
                weight=ft.FontWeight.BOLD,
                color="#2c3e50",
                text_align=ft.TextAlign.CENTER
            )
        )]
        
        for likelihood in likelihood_levels:
            header_cells.append(ft.Container(
                width=100,
                height=50,
                alignment=ft.alignment.center,
                bgcolor="#34495e",
                content=ft.Text(
                    likelihood,
                    size=12,
                    weight=ft.FontWeight.BOLD,
                    color="white",
                    text_align=ft.TextAlign.CENTER
                ),
                border_radius=ft.border_radius.only(top_left=5, top_right=5)
            ))
        
        header_row = ft.Row(header_cells, spacing=2)
        
        # Data rows
        matrix_rows = [header_row]
        
        for impact in impact_levels:
            row_cells = [ft.Container(
                width=120,
                height=80,
                alignment=ft.alignment.center,
                bgcolor="#34495e",
                content=ft.Text(
                    impact,
                    size=12,
                    weight=ft.FontWeight.BOLD,
                    color="white",
                    text_align=ft.TextAlign.CENTER
                ),
                border_radius=ft.border_radius.only(top_left=5, bottom_left=5)
            )]
            
            for likelihood in likelihood_levels:
                count = heatmap_grid.get(impact, {}).get(likelihood, 0)
                risk_level, color = self._calculate_risk_level(impact, likelihood)
                
                # Create animated, interactive cell
                cell = ft.Container(
                    width=100,
                    height=80,
                    alignment=ft.alignment.center,
                    bgcolor=color,
                    border_radius=8,
                    content=ft.Column([
                        ft.Text(
                            str(count),
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            color="white"
                        ),
                        ft.Text(
                            risk_level,
                            size=10,
                            color="white",
                            text_align=ft.TextAlign.CENTER
                        )
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
                    animate_scale=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
                    on_click=lambda e, i=impact, l=likelihood, c=count, r=risk_level: self._on_cell_click(i, l, c, r),
                    on_hover=lambda e, i=impact, l=likelihood: self._on_cell_hover(e, i, l),
                    tooltip=f"{impact} Impact, {likelihood} Likelihood\n{count} assessments\nRisk Level: {risk_level}"
                )
                
                row_cells.append(cell)
            
            matrix_rows.append(ft.Row(row_cells, spacing=2))
        
        return ft.Container(
            padding=20,
            content=ft.Column(
                matrix_rows,
                spacing=2,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            ),
            alignment=ft.alignment.center,
            expand=True
        )
    
    def _build_quick_stats_bar(self):
        """Build quick statistics bar below heatmap"""
        if not self.heatmap_data:
            return ft.Container()
        
        current_data = self.heatmap_data.get(self.selected_reference_id, {})
        stats = self._calculate_heatmap_stats(current_data)
        
        return ft.Container(
            height=80,
            bgcolor=None,
            padding=ft.padding.symmetric(horizontal=20, vertical=10),
            content=ft.Row([
                self._create_stat_pill("Total Assessments", str(stats['total']), "#3498db"),
                self._create_stat_pill("Critical Risk", str(stats['critical']), "#8B0000"),
                self._create_stat_pill("High Risk", str(stats['high']), "#e74c3c"),
                self._create_stat_pill("Medium Risk", str(stats['medium']), "#f39c12"),
                self._create_stat_pill("Low Risk", str(stats['low']), "#2ecc71"),
                ft.Container(expand=True),
                ft.Text(f"Last Updated: {format_date(self.last_update, 'datetime')}", 
                        size=12)
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=15)
        )
    
    def _build_side_panel(self):
        """Build side panel with contextual information and actions"""
        return ft.Column([
            # Selected cell information
            ft.Card(
                content=ft.Container(
                    padding=15,
                    content=ft.Column([
                        ft.Text("Cell Information", size=16, weight=ft.FontWeight.BOLD),
                        ft.Divider(),
                        ft.Text("Click on a heatmap cell to see details")
                    ])
                )
            ),
            
            ft.Container(height=15),
            
            # Quick actions
            ft.Card(
                content=ft.Container(
                    padding=15,
                    content=ft.Column([
                        ft.Text("Quick Actions", size=16, weight=ft.FontWeight.BOLD),
                        ft.Divider(),
                        ft.ElevatedButton(
                            text="Create Assessment",
                            width=200,
                            icon=ft.Icons.ASSIGNMENT_ADD,
                            bgcolor="#2ecc71",
                            color="white",
                            on_click=self._create_new_assessment
                        ),
                        ft.Container(height=10),
                        ft.ElevatedButton(
                            text="View All Assessments",
                            width=200,
                            icon=ft.Icons.ASSIGNMENT,
                            bgcolor="#3498db",
                            color="white",
                            on_click=self._view_all_assessments
                        ),
                        ft.Container(height=10),
                        ft.ElevatedButton(
                            text="Generate Report",
                            width=200,
                            icon=ft.Icons.DESCRIPTION,
                            bgcolor="#9b59b6",
                            color="white",
                            on_click=self._generate_report
                        )
                    ])
                )
            ),
            
            ft.Container(height=15),
            
            # Risk trends (placeholder)
            ft.Card(
                content=ft.Container(
                    padding=15,
                    content=ft.Column([
                        ft.Text("Risk Trends", size=16, weight=ft.FontWeight.BOLD),
                        ft.Divider(),
                        ft.Container(
                            height=150,
                            alignment=ft.alignment.center,
                            content=ft.Text("Trend chart placeholder")
                        )
                    ])
                )
            )
        ], scroll=ft.ScrollMode.AUTO)
    
    def _build_form_panel(self):
        """Build assessment form panel for split view"""
        if not self.assessment_form:
            return ft.Container(
                padding=20,
                content=ft.Column([
                    ft.Text("Assessment Form", size=18, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    ft.Text("Select 'New Assessment' or click on a heatmap cell to begin", 
                           text_align=ft.TextAlign.CENTER),
                    ft.Container(height=20),
                    ft.ElevatedButton(
                        text="Create New Assessment",
                        icon=ft.icons.ADD,
                        bgcolor="#2ecc71",
                        color="white",
                        on_click=self._create_new_assessment,
                        width=200
                    )
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            )
        
        return self.assessment_form
    
    def _create_stat_pill(self, label, value, color):
        """Create a statistic pill component"""
        return ft.Container(
            content=ft.Row([
                ft.Container(
                    width=8,
                    height=40,
                    bgcolor=color,
                    border_radius=4
                ),
                ft.Container(width=8),
                ft.Column([
                    ft.Text(value, size=18, weight=ft.FontWeight.BOLD, color=color),
                    ft.Text(label, size=11, color="#7f8c8d")
                ], spacing=2)
            ]),
            padding=ft.padding.symmetric(horizontal=15, vertical=5),
            bgcolor=None,
            border_radius=20,
            border=ft.border.all(1, "#e6e9ed")
        )
    
    def _calculate_risk_level(self, impact, likelihood):
        """Calculate risk level and color from impact and likelihood"""
        impact_scores = {"Very Low": 1, "Low": 2, "Medium": 3, "High": 4, "Very High": 5}
        likelihood_scores = {"Very Low": 1, "Low": 2, "Medium": 3, "High": 4, "Very High": 5}
        
        impact_score = impact_scores.get(impact, 3)
        likelihood_score = likelihood_scores.get(likelihood, 3)
        risk_score = impact_score * likelihood_score
        
        if risk_score >= 20:
            return "Critical", "#8B0000"
        elif risk_score >= 15:
            return "High", "#e74c3c"
        elif risk_score >= 10:
            return "Medium-High", "#f39c12"
        elif risk_score >= 6:
            return "Medium", "#f1c40f"
        elif risk_score >= 3:
            return "Low", "#2ecc71"
        else:
            return "Very Low", "#27ae60"
    
    def _calculate_heatmap_stats(self, heatmap_data):
        """Calculate statistics from heatmap data"""
        stats = {"total": 0, "critical": 0, "high": 0, "medium": 0, "low": 0}
        
        heatmap_grid = heatmap_data.get('heatmapGrid', {})
        for impact, likelihood_dict in heatmap_grid.items():
            for likelihood, count in likelihood_dict.items():
                risk_level, _ = self._calculate_risk_level(impact, likelihood)
                
                stats["total"] += count
                if risk_level == "Critical":
                    stats["critical"] += count
                elif risk_level in ["High"]:
                    stats["high"] += count
                elif risk_level in ["Medium-High", "Medium"]:
                    stats["medium"] += count
                else:
                    stats["low"] += count
        
        return stats
    
    def _process_heatmap_results(self, results, reference_ids):
        """Process heatmap results from multiple references"""
        processed_data = {}
        
        for i, result in enumerate(results):
            if not isinstance(result, Exception) and result:
                processed_data[reference_ids[i]] = result
        
        return processed_data
    
    # Event handlers
    def _on_view_mode_change(self, e):
        """Handle view mode change"""
        self.view_mode = list(e.control.selected)[0]
        self.content = ft.Column([
            self._build_dashboard_header(),
            ft.Divider(height=1, color="#e6e9ed"),
            self._build_main_content()
        ], spacing=0, expand=True)
        self.page.update()
    
    def _on_cell_click(self, impact, likelihood, count, risk_level):
        """Handle heatmap cell click"""
        # Update side panel with cell information
        self.selected_cell_info = {
            "impact": impact,
            "likelihood": likelihood,
            "count": count,
            "risk_level": risk_level
        }
        
        # Show cell details in side panel
        self._update_side_panel_with_cell_info()
        
        # If in split view, offer to create assessment with these parameters
        if self.view_mode == "split":
            self._offer_assessment_creation(impact, likelihood)
    
    def _on_cell_hover(self, e, impact, likelihood):
        """Handle cell hover for animations"""
        if e.data == "true":  # Mouse enter
            e.control.scale = 1.05
        else:  # Mouse leave
            e.control.scale = 1.0
        e.control.update()
    
    def _on_filter_change(self, e):
        """Handle filter changes"""
        self.filter_settings["department"] = e.control.value
        asyncio.create_task(self._refresh_data(None))
    
    def _on_time_filter_change(self, e):
        """Handle time filter changes"""
        self.filter_settings["time_period"] = e.control.value
        asyncio.create_task(self._refresh_data(None))
    
    def _on_reference_change(self, e):
        """Handle reference ID change"""
        self.selected_reference_id = int(e.control.value)
        self._update_heatmap_display()
    
    async def _refresh_data(self, e):
        """Refresh heatmap data"""
        await self._load_initial_data()
    
    def _toggle_fullscreen(self, e):
        """Toggle fullscreen mode"""
        # Implementation for fullscreen mode
        pass
    
    def _toggle_comparison_mode(self, e):
        """Toggle comparison mode"""
        self.comparison_mode = not self.comparison_mode
        # Implementation for comparison mode
    
    def _toggle_real_time(self, e):
        """Toggle real-time updates"""
        self.is_real_time = not self.is_real_time
        if self.is_real_time:
            asyncio.create_task(self._start_real_time_updates())
    
    async def _start_real_time_updates(self):
        """Start real-time data updates"""
        while self.is_real_time:
            await asyncio.sleep(30)  # Update every 30 seconds
            await self._load_initial_data()
    
    def _create_new_assessment(self, e):
        """Create new assessment"""
        if self.view_mode == "split":
            self._show_assessment_form_in_panel()
        else:
            self._show_assessment_form_dialog()
    
    def _show_assessment_form_in_panel(self):
        """Show assessment form in the split panel"""
        self.assessment_form = ModernAssessmentForm(
            page=self.page,
            user=self.user,
            on_save=self._on_assessment_saved,
            on_cancel=self._on_assessment_cancelled
        )
        self._refresh_ui()
    
    def _show_assessment_form_dialog(self):
        """Show assessment form in a dialog"""
        # Implementation for dialog form
        pass
    
    def _offer_assessment_creation(self, impact, likelihood):
        """Offer to create assessment with pre-filled risk parameters"""
        # Implementation for quick assessment creation
        pass
    
    def _update_side_panel_with_cell_info(self):
        """Update side panel with selected cell information"""
        if not self.selected_cell_info:
            return
        
        # Update side panel content
        # This would update the side panel UI with the selected cell details
        pass
    
    def _on_assessment_saved(self, result):
        """Handle assessment saved"""
        self.assessment_form = None
        asyncio.create_task(self._refresh_data(None))
        self._show_success("Assessment saved successfully!")
        if self.on_assessment_created:
            self.on_assessment_created(result)
    
    def _on_assessment_cancelled(self):
        """Handle assessment cancelled"""
        self.assessment_form = None
        self._refresh_ui()
    
    def _view_all_assessments(self, e):
        """View all assessments"""
        # Implementation for viewing all assessments
        pass
    
    def _generate_report(self, e):
        """Generate heatmap report"""
        # Implementation for report generation
        pass
    
    def _export_heatmap(self, e):
        """Export heatmap data"""
        # Implementation for export
        pass
    
    def _show_settings(self, e):
        """Show dashboard settings"""
        # Implementation for settings dialog
        pass
    
    def _update_heatmap_display(self):
        """Update the heatmap display"""
        self.content = ft.Column([
            self._build_dashboard_header(),
            ft.Divider(height=1, color="#e6e9ed"),
            self._build_main_content()
        ], spacing=0, expand=True)
        if hasattr(self, 'page') and self.page:
            self.page.update()
    
    def _update_quick_stats(self):
        """Update quick statistics"""
        # Implementation for updating stats
        pass
    
    def _refresh_ui(self):
        """Refresh the entire UI"""
        self._update_heatmap_display()
    
    # Utility methods
    def _show_loading_state(self):
        """Show loading state"""
        pass
    
    def _hide_loading_state(self):
        """Hide loading state"""
        pass
    
    def _show_success(self, message):
        """Show success message"""
        self.page.snack_bar = ft.SnackBar(content=ft.Text(message), bgcolor="#2ecc71")
        self.page.snack_bar.open = True
        self.page.update()
    
    def _show_error(self, message):
        """Show error message"""
        self.page.snack_bar = ft.SnackBar(content=ft.Text(message), bgcolor="#e74c3c")
        self.page.snack_bar.open = True
        self.page.update()
    
    async def cleanup(self):
        """Cleanup resources"""
        self.is_real_time = False
        try:
            await self.assessment_controller.close()
        except Exception as e:
            print(f"Error during cleanup: {e}") 
