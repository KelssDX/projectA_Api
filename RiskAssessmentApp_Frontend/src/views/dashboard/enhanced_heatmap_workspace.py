import flet as ft
import asyncio
from datetime import datetime, timedelta
from src.controllers.assessment_controller import AssessmentController
from src.views.assessment.modern_form import ModernAssessmentForm
from src.views.assessment.modern_details import ModernAssessmentDetails
from src.utils.formatters import format_date, format_risk_score
import json


class EnhancedHeatmapWorkspace(ft.Container):
    def __init__(self, page, user, on_navigation=None):
        super().__init__()
        self.page = page
        self.user = user
        self.on_navigation = on_navigation
        self.expand = True
        
        # Controllers
        self.assessment_controller = AssessmentController()
        
        # Advanced state management
        self.workspace_mode = "dashboard"  # dashboard, focused, comparison, collaborative
        self.active_panels = {"heatmap": True, "form": False, "details": False, "analytics": False}
        self.heatmap_data = {}
        self.selected_cells = []  # For multi-selection
        self.assessment_queue = []  # Queue of assessments being worked on
        self.real_time_updates = True
        self.collaboration_mode = False
        self.scenario_mode = False
        self.scenario_data = {}
        self.assessment_form = None
        
        # Panel management
        self.panels = {
            "heatmap": None,
            "form": None,
            "details": None,
            "analytics": None,
            "notifications": None
        }
        
        # Filter and view settings
        self.filters = {
            "department": "All",
            "time_range": "current",
            "risk_threshold": "all",
            "assessment_status": "all",
            "auditor": "all"
        }
        
        # Animation and interaction state
        self.hover_animations = True
        self.auto_refresh_interval = 30  # seconds
        self.last_interaction = datetime.now()
        
        # Initialize workspace
        self._init_workspace()
    
    def _init_workspace(self):
        """Initialize the enhanced workspace"""
        self._build_workspace_ui()
        asyncio.create_task(self._load_workspace_data())
        
        # Start background tasks
        if self.real_time_updates:
            asyncio.create_task(self._start_real_time_updates())
        asyncio.create_task(self._start_auto_save_monitor())
    
    async def _load_workspace_data(self):
        """Load comprehensive workspace data"""
        try:
            self._show_workspace_loading()
            
            # Load multiple data sources concurrently
            reference_ids = [1, 2, 3, 4, 5]
            tasks = [
                self.assessment_controller.get_heatmap_data(ref_id) for ref_id in reference_ids
            ]
            
            # Add assessment list loading
            tasks.extend([
                self._load_recent_assessments(),
                self._load_team_activity(),
                self._load_risk_trends()
            ])
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process heatmap results
            heatmap_results = results[:len(reference_ids)]
            self.heatmap_data = self._process_heatmap_results(heatmap_results, reference_ids)
            
            # Process other results
            self.recent_assessments = results[len(reference_ids)] if len(results) > len(reference_ids) else []
            self.team_activity = results[len(reference_ids) + 1] if len(results) > len(reference_ids) + 1 else []
            self.risk_trends = results[len(reference_ids) + 2] if len(results) > len(reference_ids) + 2 else {}
            
            # Update all active panels
            self._update_all_panels()
            
        except Exception as e:
            self._show_error(f"Error loading workspace data: {str(e)}")
        finally:
            self._hide_workspace_loading()
    
    def _build_workspace_ui(self):
        """Build the main workspace UI with dynamic panels"""
        # Dynamic header based on mode
        header = self._build_dynamic_header()
        
        # Main workspace area
        workspace_area = self._build_workspace_area()
        
        # Smart notification panel
        notification_panel = self._build_notification_panel()
        
        # Layout
        self.content = ft.Column([
            header,
            ft.Container(
                expand=True,
                content=ft.Stack([
                    workspace_area,
                    notification_panel
                ])
            )
        ], spacing=0, expand=True)

    def apply_theme(self, colors):
        try:
            # Rebuild to bind theme tokens like Dashboard
            self._build_workspace_ui()
            from src.utils.theme import apply_theme_to_control
            apply_theme_to_control(self, colors)
        except Exception:
            pass
    
    def _build_dynamic_header(self):
        """Build dynamic header that changes based on workspace mode"""
        return ft.Container(
            height=90,
            bgcolor=None,
            padding=ft.padding.symmetric(horizontal=30, vertical=15),
            content=ft.Column([
                # Main title row
                ft.Row([
                    ft.Column([
                        ft.Text(
                            self._get_mode_title(),
                            size=20,
                            weight=ft.FontWeight.BOLD,
                            color="#2c3e50"
                        ),
                        ft.Row([
                            ft.Text("Smart Risk Intelligence", size=12, color="#7f8c8d"),
                            self._build_status_indicators()
                        ])
                    ], spacing=2),
                    
                    ft.Container(expand=True),
                    
                    # Mode selector
                    ft.SegmentedButton(
                        selected={self.workspace_mode},
                        allow_empty_selection=False,
                        segments=[
                            ft.Segment(value="dashboard", label=ft.Text("Dashboard"), icon=ft.Icon(ft.icons.DASHBOARD)),
                            ft.Segment(value="focused", label=ft.Text("Focus"), icon=ft.Icon(ft.icons.CENTER_FOCUS_STRONG)),
                            ft.Segment(value="comparison", label=ft.Text("Compare"), icon=ft.Icon(ft.icons.COMPARE_ARROWS)),
                            ft.Segment(value="collaborative", label=ft.Text("Collaborate"), icon=ft.Icon(ft.icons.GROUP_WORK))
                        ],
                        on_change=self._on_workspace_mode_change
                    ),
                    
                    ft.Container(width=20),
                    
                    # Quick actions
                    self._build_quick_actions()
                ]),
                
                # Smart toolbar
                self._build_smart_toolbar()
            ])
        )
    
    def _build_smart_toolbar(self):
        """Build context-aware smart toolbar"""
        return ft.Row([
            # Dynamic filters based on current context
            ft.Row([
                        ft.Text("Smart Filters:", weight=ft.FontWeight.BOLD, size=12),
                ft.Dropdown(
                    label="Focus",
                    width=120,
                    height=35,
                    value=self.filters["risk_threshold"],
                    options=[
                        ft.dropdown.Option("all", "All Risks"),
                        ft.dropdown.Option("critical", "Critical Only"),
                        ft.dropdown.Option("high", "High+ Only"),
                        ft.dropdown.Option("medium", "Medium+ Only")
                    ],
                    on_change=self._on_risk_filter_change,
                    text_size=11
                ),
                ft.Dropdown(
                    label="Department",
                    width=120,
                    height=35,
                    value=self.filters["department"],
                    options=[
                        ft.dropdown.Option("All"),
                        ft.dropdown.Option("IT"),
                        ft.dropdown.Option("Finance"),
                        ft.dropdown.Option("Operations"),
                        ft.dropdown.Option("Legal")
                    ],
                    on_change=self._on_department_filter_change,
                    text_size=11
                )
            ], spacing=10),
            
            ft.Container(expand=True),
            
            # Context actions
            ft.Row([
                ft.IconButton(
                    icon=ft.icons.ADD_CIRCLE,
                    tooltip="Quick Assessment",
                    icon_color="#2ecc71",
                    on_click=self._quick_assessment_creation
                ),
                ft.IconButton(
                    icon=ft.icons.ANALYTICS,
                    tooltip="Analytics Panel",
                    icon_color="#3498db",
                    on_click=self._toggle_analytics_panel
                ),
                ft.IconButton(
                    icon=ft.icons.SYNC if self.real_time_updates else ft.icons.SYNC_DISABLED,
                    tooltip="Real-time Updates",
                    icon_color="#2ecc71" if self.real_time_updates else "#95a5a6",
                    on_click=self._toggle_real_time
                ),
                ft.PopupMenuButton(
                    items=[
                        ft.PopupMenuItem(text="Export Dashboard", icon=ft.icons.DOWNLOAD),
                        ft.PopupMenuItem(text="Share Workspace", icon=ft.icons.SHARE),
                        ft.PopupMenuItem(text="Configure Alerts", icon=ft.icons.NOTIFICATIONS),
                        ft.PopupMenuItem(),
                        ft.PopupMenuItem(text="Workspace Settings", icon=ft.icons.SETTINGS)
                    ],
                    icon=ft.icons.MORE_HORIZ,
                    tooltip="More options"
                )
            ])
        ])
    
    def _build_workspace_area(self):
        """Build the main workspace area with dynamic panels"""
        if self.workspace_mode == "dashboard":
            return self._build_dashboard_layout()
        elif self.workspace_mode == "focused":
            return self._build_focused_layout()
        elif self.workspace_mode == "comparison":
            return self._build_comparison_layout()
        elif self.workspace_mode == "collaborative":
            return self._build_collaborative_layout()
        else:
            return self._build_dashboard_layout()
    
    def _build_dashboard_layout(self):
        """Build comprehensive dashboard layout"""
        return ft.Row([
            # Main heatmap area
            ft.Column([
                self._build_enhanced_heatmap(),
                self._build_intelligent_insights()
            ], expand=2),
            
            ft.Container(width=2),
            
            # Multi-function side panel
            ft.Column([
                self._build_multi_function_panel()
            ], expand=1, scroll=ft.ScrollMode.AUTO)
        ])
    
    def _build_focused_layout(self):
        """Build focused work layout with minimal distractions"""
        return ft.Container(
            content=ft.Stack([
                # Full-screen heatmap
                self._build_enhanced_heatmap(),
                
                # Floating action panel
                ft.Positioned(
                    right=20,
                    top=20,
                    child=self._build_floating_action_panel()
                ),
                
                # Floating assessment form (if active)
                ft.Positioned(
                    left=20,
                    top=20,
                    bottom=20,
                    width=400,
                    child=self._build_floating_form() if self.active_panels["form"] else ft.Container()
                )
            ])
        )
    
    def _build_comparison_layout(self):
        """Build comparison layout for scenario analysis"""
        return ft.Column([
            # Comparison controls
            self._build_comparison_controls(),
            
            # Side-by-side heatmaps
            ft.Row([
                ft.Column([
                    ft.Text("Current State", size=16, weight=ft.FontWeight.BOLD),
                    self._build_enhanced_heatmap(variant="current")
                ], expand=1),
                
            ft.Container(width=2),
                
                ft.Column([
                    ft.Text("Scenario", size=16, weight=ft.FontWeight.BOLD),
                    self._build_enhanced_heatmap(variant="scenario")
                ], expand=1)
            ], expand=True),
            
            # Comparison insights
            self._build_comparison_insights()
        ])
    
    def _build_collaborative_layout(self):
        """Build collaborative workspace with team features"""
        return ft.Row([
            # Main workspace
            ft.Column([
                self._build_enhanced_heatmap(),
                self._build_team_activity_feed()
            ], expand=2),
            
            ft.Container(width=2, bgcolor="#e6e9ed"),
            
            # Collaboration panel
            ft.Column([
                self._build_collaboration_panel()
            ], expand=1)
        ])
    
    def _build_enhanced_heatmap(self, variant="main"):
        """Build enhanced interactive heatmap with advanced features"""
        if not self.heatmap_data:
            return self._build_heatmap_placeholder()
        
        # Select data based on variant
        if variant == "scenario" and self.scenario_data:
            current_data = self.scenario_data
        else:
            current_data = self.heatmap_data.get(1, {})  # Default to reference 1
        
        heatmap_grid = current_data.get('heatmapGrid', {})
        
        if not heatmap_grid:
            return self._build_heatmap_placeholder()
        
        # Enhanced heatmap with advanced interactions
        return ft.Container(
            content=self._create_interactive_matrix(heatmap_grid, variant),
            padding=20,
            expand=True
        )
    
    def _create_interactive_matrix(self, heatmap_grid, variant="main"):
        """Create interactive heatmap matrix with advanced features"""
        impact_levels = ["Very High", "High", "Medium", "Low", "Very Low"]
        likelihood_levels = ["Very Low", "Low", "Medium", "High", "Very High"]
        
        # Enhanced header with sorting capabilities
        header_cells = [self._create_corner_cell()]
        
        for likelihood in likelihood_levels:
            header_cells.append(self._create_header_cell(likelihood, "likelihood"))
        
        header_row = ft.Row(header_cells, spacing=1)
        
        # Enhanced data rows with drag-drop and multi-selection
        matrix_rows = [header_row]
        
        for impact in impact_levels:
            row_cells = [self._create_header_cell(impact, "impact")]
            
            for likelihood in likelihood_levels:
                count = heatmap_grid.get(impact, {}).get(likelihood, 0)
                risk_level, color = self._calculate_risk_level(impact, likelihood)
                
                cell = self._create_enhanced_cell(
                    impact, likelihood, count, risk_level, color, variant
                )
                row_cells.append(cell)
            
            matrix_rows.append(ft.Row(row_cells, spacing=1))
        
        return ft.Column(matrix_rows, spacing=1, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    
    def _create_enhanced_cell(self, impact, likelihood, count, risk_level, color, variant):
        """Create enhanced interactive cell with advanced features"""
        is_selected = {"impact": impact, "likelihood": likelihood} in self.selected_cells
        
        cell_content = ft.Container(
            width=90,
            height=90,
            alignment=ft.alignment.center,
            bgcolor=color,
            border_radius=12,
            border=ft.border.all(3, "#ffffff" if is_selected else "transparent"),
            content=ft.Column([
                ft.Text(
                    str(count),
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color="white"
                ),
                ft.Text(
                    risk_level.split('-')[0] if '-' in risk_level else risk_level,
                    size=9,
                    color="white",
                    text_align=ft.TextAlign.CENTER
                ),
                # Progress indicator for real-time changes
                ft.Container(
                    width=30,
                    height=2,
                    bgcolor="white" if count > 0 else "transparent",
                    opacity=0.7
                )
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=1),
            
            # Enhanced animations
            animate_scale=ft.Animation(300, ft.AnimationCurve.ELASTIC_OUT),
            animate_opacity=ft.Animation(200, ft.AnimationCurve.EASE_IN_OUT),
            
            # Advanced event handlers
            on_click=lambda e: self._on_enhanced_cell_click(impact, likelihood, count, risk_level, e),
            on_long_press=lambda e: self._on_cell_long_press(impact, likelihood, count, risk_level),
            on_hover=lambda e: self._on_enhanced_cell_hover(e, impact, likelihood),
            
            # Rich tooltip
            tooltip=self._create_rich_tooltip(impact, likelihood, count, risk_level)
        )
        
        # Add drag-drop capabilities in collaborative mode
        if self.workspace_mode == "collaborative":
            return ft.Draggable(
                group="risk_cells",
                content=cell_content,
                data={"impact": impact, "likelihood": likelihood, "count": count}
            )
        else:
            return cell_content
    
    def _create_rich_tooltip(self, impact, likelihood, count, risk_level):
        """Create rich tooltip with contextual information"""
        return f"""Risk Cell Details
Impact: {impact}
Likelihood: {likelihood}
Assessments: {count}
Risk Level: {risk_level}

Click: View details
Long press: Quick actions
Ctrl+Click: Multi-select"""
    
    def _build_multi_function_panel(self):
        """Build multi-function side panel with tabs"""
        return ft.Container(
            content=ft.Tabs(
                tabs=[
                    ft.Tab(
                        text="Insights",
                        icon=ft.icons.LIGHTBULB,
                        content=self._build_insights_tab()
                    ),
                    ft.Tab(
                        text="Queue",
                        icon=ft.icons.QUEUE,
                        content=self._build_assessment_queue_tab()
                    ),
                    ft.Tab(
                        text="Actions",
                        icon=ft.icons.BOLT,
                        content=self._build_quick_actions_tab()
                    ),
                    ft.Tab(
                        text="Activity",
                        icon=ft.icons.TIMELINE,
                        content=self._build_activity_tab()
                    )
                ],
                selected_index=0
            )
        )
    
    def _build_insights_tab(self):
        """Build AI-powered insights tab"""
        return ft.Container(
            padding=15,
            content=ft.Column([
                ft.Text("Smart Insights", size=16, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                
                # Risk alerts
                ft.Card(
                    content=ft.Container(
                        padding=10,
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(ft.icons.WARNING, color="#f39c12", size=20),
                                ft.Text("Risk Alerts", weight=ft.FontWeight.BOLD)
                            ]),
                            ft.Text("3 new high-risk assessments detected", size=12),
                            ft.Text("Critical threshold exceeded in IT dept", size=12, color="#e74c3c")
                        ])
                    )
                ),
                
                ft.Container(height=10),
                
                # Recommendations
                ft.Card(
                    content=ft.Container(
                        padding=10,
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(ft.icons.PSYCHOLOGY, color="#3498db", size=20),
                                ft.Text("AI Recommendations", weight=ft.FontWeight.BOLD)
                            ]),
                            ft.Text("Focus on High/High quadrant", size=12),
                            ft.Text("Schedule control testing for CTRL-001", size=12),
                            ft.ElevatedButton(
                                text="Apply Suggestions",
                                height=30,
                                bgcolor="#3498db",
                                color="white"
                            )
                        ])
                    )
                ),
                
                ft.Container(height=10),
                
                # Trends
                ft.Card(
                    content=ft.Container(
                        padding=10,
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(ft.icons.TRENDING_UP, color="#2ecc71", size=20),
                                ft.Text("Risk Trends", weight=ft.FontWeight.BOLD)
                            ]),
                            ft.Text("↗ 15% increase in medium risks", size=12),
                            ft.Text("↘ 8% decrease in critical risks", size=12, color="#2ecc71")
                        ])
                    )
                )
            ], scroll=ft.ScrollMode.AUTO)
        )
    
    def _build_assessment_queue_tab(self):
        """Build assessment work queue tab"""
        return ft.Container(
            padding=15,
            content=ft.Column([
                ft.Row([
                    ft.Text("Work Queue", size=16, weight=ft.FontWeight.BOLD),
                    ft.Container(expand=True),
                    ft.IconButton(
                        icon=ft.icons.ADD,
                        tooltip="Add to queue",
                        icon_color="#2ecc71"
                    )
                ]),
                ft.Divider(),
                
                # Queue items
                ft.Column([
                    self._create_queue_item("Assessment A-001", "In Progress", "#3498db"),
                    self._create_queue_item("Assessment A-002", "Pending Review", "#f39c12"),
                    self._create_queue_item("Assessment A-003", "Draft", "#95a5a6")
                ]),
                
                ft.Container(height=20),
                
                # Quick actions
                ft.ElevatedButton(
                    text="Process Next",
                    width=200,
                    bgcolor="#2ecc71",
                    color="white",
                    on_click=self._process_next_in_queue
                )
            ], scroll=ft.ScrollMode.AUTO)
        )
    
    def _create_queue_item(self, title, status, color):
        """Create assessment queue item"""
        return ft.Card(
            content=ft.Container(
                padding=10,
                content=ft.Row([
                    ft.Column([
                        ft.Text(title, weight=ft.FontWeight.BOLD, size=12),
                        ft.Text(status, size=10, color=color)
                    ], expand=True),
                    ft.IconButton(
                        icon=ft.icons.PLAY_ARROW,
                        icon_color=color,
                        tooltip=f"Work on {title}",
                        icon_size=16
                    )
                ])
            ),
            margin=ft.margin.only(bottom=5)
        )
    
    def _build_intelligent_insights(self):
        """Build intelligent insights bar"""
        return ft.Container(
            height=100,
            bgcolor=None,
            padding=20,
            content=ft.Row([
                # Smart metrics
                self._create_smart_metric("Risk Velocity", "+12%", "#e74c3c", "Increasing"),
                self._create_smart_metric("Control Effectiveness", "87%", "#2ecc71", "Good"),
                self._create_smart_metric("Assessment Backlog", "5", "#f39c12", "Moderate"),
                self._create_smart_metric("Team Productivity", "+8%", "#3498db", "Improving"),
                
                ft.Container(expand=True),
                
                # AI assistant
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.icons.SMART_TOY, color="#9b59b6"),
                        ft.Column([
                            ft.Text("AI Assistant", size=12, weight=ft.FontWeight.BOLD),
                            ft.Text("3 suggestions available", size=10, color="#7f8c8d")
                        ], spacing=2)
                    ]),
                    padding=10,
                    bgcolor=None,
                    border_radius=10,
                    border=ft.border.all(1, "#e6e9ed")
                )
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=20)
        )
    
    def _create_smart_metric(self, label, value, color, trend):
        """Create smart metric display"""
        return ft.Container(
            content=ft.Column([
                ft.Text(value, size=18, weight=ft.FontWeight.BOLD, color=color),
                ft.Text(label, size=11),
                ft.Text(trend, size=9)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
            padding=15,
            bgcolor=None,
            border_radius=10,
            border=ft.border.all(1, "#e6e9ed"),
            width=120
        )
    
    # Enhanced event handlers
    def _on_enhanced_cell_click(self, impact, likelihood, count, risk_level, e):
        """Handle enhanced cell click with multi-selection support"""
        # Check for modifier keys (Ctrl for multi-select)
        if hasattr(e, 'ctrl_key') and e.ctrl_key:
            self._toggle_cell_selection(impact, likelihood)
        else:
            # Single selection
            self.selected_cells = [{"impact": impact, "likelihood": likelihood}]
            self._handle_cell_action(impact, likelihood, count, risk_level)
    
    def _on_cell_long_press(self, impact, likelihood, count, risk_level):
        """Handle cell long press for context menu"""
        self._show_cell_context_menu(impact, likelihood, count, risk_level)
    
    def _on_enhanced_cell_hover(self, e, impact, likelihood):
        """Enhanced cell hover with smart previews"""
        if e.data == "true":  # Mouse enter
            e.control.scale = 1.08
            e.control.animate_scale.duration = 150
            self._show_cell_preview(impact, likelihood)
        else:  # Mouse leave
            e.control.scale = 1.0
            self._hide_cell_preview()
        e.control.update()
    
    def _toggle_cell_selection(self, impact, likelihood):
        """Toggle cell selection for multi-select operations"""
        cell_key = {"impact": impact, "likelihood": likelihood}
        if cell_key in self.selected_cells:
            self.selected_cells.remove(cell_key)
        else:
            self.selected_cells.append(cell_key)
        
        self._update_heatmap_display()
    
    async def _quick_assessment_creation(self, e):
        """Quick assessment creation with smart defaults"""
        if self.selected_cells:
            # Pre-fill with selected cell data
            cell = self.selected_cells[0]
            await self._create_assessment_with_params(
                impact=cell["impact"],
                likelihood=cell["likelihood"]
            )
        else:
            # Standard new assessment
            await self._create_new_assessment(e)
    
    async def _create_assessment_with_params(self, impact, likelihood):
        """Create assessment with pre-filled risk parameters"""
        if self.workspace_mode == "focused":
            self._show_floating_form_with_params(impact, likelihood)
        else:
            self._show_split_form_with_params(impact, likelihood)
    
    def _show_floating_form_with_params(self, impact, likelihood):
        """Show floating form with pre-filled parameters"""
        self.assessment_form = ModernAssessmentForm(
            page=self.page,
            user=self.user,
            on_save=self._on_assessment_saved,
            on_cancel=self._on_assessment_cancelled
        )
        
        # Pre-fill form data
        self.assessment_form.form_data.update({
            'impact': impact,
            'likelihood': likelihood
        })
        
        self.active_panels["form"] = True
        self._refresh_workspace()
    
    async def _start_real_time_updates(self):
        """Start real-time updates with smart batching"""
        while self.real_time_updates:
            await asyncio.sleep(self.auto_refresh_interval)
            
            # Only update if user has been inactive
            if (datetime.now() - self.last_interaction).seconds > 10:
                await self._incremental_data_update()
    
    async def _incremental_data_update(self):
        """Perform incremental data updates"""
        try:
            # Only update active reference
            new_data = await self.assessment_controller.get_heatmap_data(1)
            if new_data:
                old_data = self.heatmap_data.get(1, {})
                if self._has_data_changed(old_data, new_data):
                    self.heatmap_data[1] = new_data
                    self._animate_changes(old_data, new_data)
                    self._update_heatmap_display()
        except Exception as e:
            print(f"Real-time update error: {e}")
    
    def _has_data_changed(self, old_data, new_data):
        """Check if heatmap data has meaningful changes"""
        old_grid = old_data.get('heatmapGrid', {})
        new_grid = new_data.get('heatmapGrid', {})
        return old_grid != new_grid
    
    def _animate_changes(self, old_data, new_data):
        """Animate changes in heatmap data"""
        # Implementation for smooth change animations
        pass
    
    # Utility methods
    def _get_mode_title(self):
        """Get title based on current workspace mode"""
        titles = {
            "dashboard": "Risk Intelligence Dashboard",
            "focused": "Focused Risk Analysis",
            "comparison": "Scenario Comparison",
            "collaborative": "Team Risk Workspace"
        }
        return titles.get(self.workspace_mode, "Risk Assessment Workspace")
    
    def _build_status_indicators(self):
        """Build real-time status indicators"""
        return ft.Row([
            ft.Container(
                width=8,
                height=8,
            bgcolor="#2ecc71" if self.real_time_updates else None,
                border_radius=4,
                margin=ft.margin.only(left=8)
            ),
            ft.Text(
                f"{len(self.assessment_queue)} in queue",
                size=10,
                color="#7f8c8d",
                margin=ft.margin.only(left=5)
            )
        ])
    
    def _refresh_workspace(self):
        """Refresh entire workspace"""
        self._build_workspace_ui()
        if hasattr(self, 'page') and self.page:
            self.page.update()
    
    async def cleanup(self):
        """Enhanced cleanup with state persistence"""
        self.real_time_updates = False
        
        # Save workspace state
        await self._save_workspace_state()
        
        try:
            await self.assessment_controller.close()
        except Exception as e:
            print(f"Error during cleanup: {e}")
    
    async def _save_workspace_state(self):
        """Save current workspace state for restoration"""
        workspace_state = {
            "mode": self.workspace_mode,
            "active_panels": self.active_panels,
            "filters": self.filters,
            "selected_cells": self.selected_cells,
            "assessment_queue": self.assessment_queue
        }
        
        # In a real application, this would save to persistent storage
        print(f"Saving workspace state: {workspace_state}")
    
    # Placeholder methods for missing functionality
    def _build_heatmap_placeholder(self):
        return ft.Container(height=400, content=ft.Text("Loading..."))
    
    def _create_corner_cell(self):
        return ft.Container(width=90, height=50, content=ft.Text(""))
    
    def _create_header_cell(self, text, cell_type):
        return ft.Container(
            width=90, height=50,
            content=ft.Text(text, size=10, weight=ft.FontWeight.BOLD),
            bgcolor="#34495e", alignment=ft.alignment.center
        )
    
    def _calculate_risk_level(self, impact, likelihood):
        """Calculate risk level and color"""
        # Implementation from the original heatmap
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
    
    # Additional placeholder methods
    def _build_quick_actions(self): return ft.Container()
    def _build_notification_panel(self): return ft.Container()
    def _build_floating_action_panel(self): return ft.Container()
    def _build_floating_form(self): return ft.Container()
    def _build_comparison_controls(self): return ft.Container()
    def _build_comparison_insights(self): return ft.Container()
    def _build_team_activity_feed(self): return ft.Container()
    def _build_collaboration_panel(self): return ft.Container()
    def _build_quick_actions_tab(self): return ft.Container()
    def _build_activity_tab(self): return ft.Container()
    def _show_workspace_loading(self): pass
    def _hide_workspace_loading(self): pass
    def _show_error(self, msg): pass
    def _show_success(self, msg): pass
    def _update_all_panels(self): pass
    def _update_heatmap_display(self): pass
    def _process_heatmap_results(self, results, ids): return {}
    async def _load_recent_assessments(self): return []
    async def _load_team_activity(self): return []
    async def _load_risk_trends(self): return {}
    def _on_workspace_mode_change(self, e): pass
    def _on_risk_filter_change(self, e): pass
    def _on_department_filter_change(self, e): pass
    def _toggle_analytics_panel(self, e): pass
    def _toggle_real_time(self, e): pass
    def _handle_cell_action(self, i, l, c, r): pass
    def _show_cell_context_menu(self, i, l, c, r): pass
    def _show_cell_preview(self, i, l): pass
    def _hide_cell_preview(self): pass
    async def _create_new_assessment(self, e): pass
    def _on_assessment_saved(self, result): pass
    def _on_assessment_cancelled(self): pass
    def _process_next_in_queue(self, e): pass
    async def _start_auto_save_monitor(self): pass 
