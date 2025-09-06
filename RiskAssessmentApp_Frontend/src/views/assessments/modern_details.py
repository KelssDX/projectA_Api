import flet as ft
import asyncio
from datetime import datetime
from src.controllers.assessment_controller import AssessmentController
from src.utils.export_utils import ExportManager
from src.utils.formatters import format_date, format_currency
import json


class ModernAssessmentDetails(ft.Container):
    def __init__(self, page, user, assessment_id=None, reference_id=None, on_back=None, on_edit=None):
        super().__init__()
        self.page = page
        self.user = user
        self.assessment_id = assessment_id
        self.reference_id = reference_id
        self.on_back_callback = on_back
        self.on_edit_callback = on_edit
        self.expand = True
        
        # Controllers
        self.assessment_controller = AssessmentController()
        self.export_manager = ExportManager()
        
        # State
        self.assessment_data = None
        self.heatmap_data = None
        self.current_tab = 0
        self.comments = []
        self.workflow_status = "In Progress"
        
        # Initialize view
        self._init_view()
    
    def _init_view(self):
        """Initialize the view"""
        self._build_ui()
        if self.reference_id:
            asyncio.create_task(self._load_assessment_data())

    def apply_theme(self, colors):
        try:
            # Rebuild to apply theme tokens, then normalize
            self._build_ui()
            from src.utils.theme import apply_theme_to_control
            apply_theme_to_control(self, colors)
            if hasattr(self, 'page') and self.page:
                self.page.update()
        except Exception:
            pass
    
    async def _load_assessment_data(self):
        """Load assessment data from API"""
        try:
            self._show_loading()
            
            # Load assessment and heatmap data concurrently
            tasks = [
                self.assessment_controller.get_risk_assessment(self.reference_id),
                self.assessment_controller.get_heatmap_data(self.reference_id)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            self.assessment_data = results[0] if not isinstance(results[0], Exception) else None
            self.heatmap_data = results[1] if not isinstance(results[1], Exception) else None
            
            if self.assessment_data:
                self._update_ui_with_data()
            else:
                self._show_error("Failed to load assessment data")
                
        except Exception as e:
            self._show_error(f"Error loading assessment: {str(e)}")
        finally:
            self._hide_loading()
    
    def _build_ui(self):
        """Build the main UI structure"""
        # Header with actions
        header = self._build_header()
        
        
        # Main content tabs
        tabs = self._build_content_tabs()
        
        # Action panel
        action_panel = self._build_action_panel()
        
        # Layout
        self.content = ft.Column([
            header,
            ft.Divider(height=1, color="#e6e9ed"),
            tabs,
            ft.Divider(height=1, color="#e6e9ed"),
            action_panel
        ], spacing=0, expand=True)
    
    def _build_header(self):
        """Build the header section"""
        return ft.Container(
            height=80,
            bgcolor="white",
            padding=ft.padding.symmetric(horizontal=30, vertical=15),
            content=ft.Row([
                ft.IconButton(
                    icon=ft.icons.ARROW_BACK,
                    icon_size=24,
                    on_click=self._handle_back,
                    tooltip="Back to assessments"
                ),
                ft.Column([
                    ft.Text(
                        f"Risk Assessment: {self.reference_id or 'Loading...'}",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color="#2c3e50"
                    ),
                    ft.Text(
                        "Comprehensive assessment details and management",
                        size=12,
                        color="#7f8c8d"
                    )
                ], spacing=2),
                ft.Container(expand=True),
                
                # Quick actions
                ft.Row([
                    ft.ElevatedButton(
                        text="Start Control Testing",
                        icon=ft.Icons.PLAY_CIRCLE_OUTLINE,
                        bgcolor="#f39c12",
                        color="white",
                        on_click=self._start_control_testing,
                        tooltip="Initiate control testing workflow"
                    ),
                    ft.Container(width=10),
                    ft.PopupMenuButton(
                        items=[
                            ft.PopupMenuItem(
                                text="Export to PDF",
                                icon=ft.Icons.PICTURE_AS_PDF,
                                on_click=lambda e: self._export_assessment("pdf")
                            ),
                            ft.PopupMenuItem(
                                text="Export to Excel",
                                icon=ft.Icons.TABLE_VIEW,
                                on_click=lambda e: self._export_assessment("excel")
                            ),
                            ft.PopupMenuItem(
                                text="Share Assessment",
                                icon=ft.Icons.SHARE,
                                on_click=self._share_assessment
                            ),
                            ft.PopupMenuItem(),  # Divider
                            ft.PopupMenuItem(
                                text="Edit Assessment",
                                icon=ft.Icons.EDIT,
                                on_click=self._edit_assessment
                            ),
                            ft.PopupMenuItem(
                                text="Archive Assessment",
                                icon=ft.Icons.ARCHIVE,
                                on_click=self._archive_assessment
                            )
                        ],
                        icon=ft.Icons.MORE_VERT,
                        tooltip="More actions"
                    )
                ])
            ])
        )
    
    def _build_status_bar(self):
        """Build the status indicator bar"""
        return ft.Container(
            height=50,
            bgcolor="#f8f9fa",
            padding=ft.padding.symmetric(horizontal=30, vertical=10),
            content=ft.Row([
                # Workflow status
                ft.Row([
                    ft.Icon(ft.icons.ASSIGNMENT, color="#3498db", size=20),
                    ft.Text("Status:", weight=ft.FontWeight.BOLD, color="#2c3e50"),
                    ft.Container(
                        content=ft.Text(
                            self.workflow_status,
                            color="white",
                            weight=ft.FontWeight.BOLD,
                            size=12
                        ),
                        bgcolor=self._get_status_color(self.workflow_status),
                        padding=ft.padding.symmetric(horizontal=10, vertical=5),
                        border_radius=12
                    )
                ], spacing=10),
                
                ft.Container(width=30),
                
                # Last updated
                ft.Row([
                    ft.Icon(ft.icons.UPDATE, color="#7f8c8d", size=20),
                    ft.Text("Last Updated:", weight=ft.FontWeight.BOLD, color="#2c3e50"),
                    ft.Text("Loading...", color="#7f8c8d")
                ], spacing=10),
                
                ft.Container(expand=True),
                
                # Risk level indicator
                ft.Row([
                    ft.Icon(ft.icons.WARNING, color="#e74c3c", size=20),
                    ft.Text("Risk Level:", weight=ft.FontWeight.BOLD, color="#2c3e50"),
                    ft.Container(
                        content=ft.Text(
                            "Loading...",
                            color="white",
                            weight=ft.FontWeight.BOLD,
                            size=12
                        ),
                        bgcolor="#95a5a6",
                        padding=ft.padding.symmetric(horizontal=10, vertical=5),
                        border_radius=12
                    )
                ], spacing=10)
            ])
        )
    
    def _build_content_tabs(self):
        """Build the main content tabs"""
        return ft.Container(
            expand=True,
            content=ft.Tabs(
                selected_index=self.current_tab,
                on_change=self._on_tab_change,
                tabs=[
                    ft.Tab(
                        text="Overview",
                        icon=ft.icons.DASHBOARD,
                        content=self._build_overview_tab()
                    ),
                    ft.Tab(
                        text="Risk Analysis",
                        icon=ft.icons.ANALYTICS,
                        content=self._build_risk_analysis_tab()
                    ),
                    ft.Tab(
                        text="Controls",
                        icon=ft.icons.SECURITY,
                        content=self._build_controls_tab()
                    ),
                    ft.Tab(
                        text="Findings",
                        icon=ft.icons.SEARCH,
                        content=self._build_findings_tab()
                    ),
                    ft.Tab(
                        text="Heatmap",
                        icon=ft.icons.GRID_VIEW,
                        content=self._build_heatmap_tab()
                    ),
                    ft.Tab(
                        text="Collaboration",
                        icon=ft.icons.GROUP,
                        content=self._build_collaboration_tab()
                    )
                ]
            )
        )
    
    def _build_overview_tab(self):
        """Build the overview tab content"""
        return ft.Container(
            padding=20,
            content=ft.Column([
                # Key metrics cards
                ft.Row([
                    self._create_metric_card("Risk Score", "Loading...", "#3498db", ft.icons.SCORE),
                    self._create_metric_card("Controls Tested", "Loading...", "#2ecc71", ft.icons.SECURITY),
                    self._create_metric_card("Findings", "Loading...", "#f39c12", ft.icons.WARNING),
                    self._create_metric_card("Completion", "Loading...", "#9b59b6", ft.icons.PERCENT)
                ], spacing=20),
                
                ft.Container(height=20),
                
                # Assessment summary
                ft.Row([
                    # Left column - Basic info
                    ft.Column([
                        ft.Card(
                            content=ft.Container(
                                padding=20,
                                content=ft.Column([
                                    ft.Text("Assessment Information", size=18, weight=ft.FontWeight.BOLD, color="#2c3e50"),
                                    ft.Divider(),
                                    self._create_info_row("Title", "Loading..."),
                                    self._create_info_row("Department", "Loading..."),
                                    self._create_info_row("Project", "Loading..."),
                                    self._create_info_row("Auditor", "Loading..."),
                                    self._create_info_row("Assessment Date", "Loading..."),
                                    self._create_info_row("Created", "Loading...")
                                ])
                            )
                        )
                    ], expand=1),
                    
                    ft.Container(width=20),
                    
                    # Right column - Progress and timeline
                    ft.Column([
                        ft.Card(
                            content=ft.Container(
                                padding=20,
                                content=ft.Column([
                                    ft.Text("Assessment Progress", size=18, weight=ft.FontWeight.BOLD, color="#2c3e50"),
                                    ft.Divider(),
                                    ft.Container(
                                        content=ft.ProgressBar(value=0.75, bgcolor="#ecf0f1", color="#3498db"),
                                        width=300
                                    ),
                                    ft.Text("75% Complete", color="#7f8c8d"),
                                    ft.Container(height=20),
                                    ft.Text("Timeline", size=16, weight=ft.FontWeight.BOLD),
                                    ft.Container(height=10),
                                    self._create_timeline_item("Assessment Created", "Completed", "#2ecc71"),
                                    self._create_timeline_item("Risk Analysis", "Completed", "#2ecc71"),
                                    self._create_timeline_item("Control Testing", "In Progress", "#f39c12"),
                                    self._create_timeline_item("Final Review", "Pending", "#95a5a6")
                                ])
                            )
                        )
                    ], expand=1)
                ])
            ], scroll=ft.ScrollMode.AUTO)
        )
    
    def _build_risk_analysis_tab(self):
        """Build the risk analysis tab"""
        return ft.Container(
            padding=20,
            content=ft.Column([
                # Risk matrix visualization
                ft.Card(
                    content=ft.Container(
                        padding=20,
                        content=ft.Column([
                            ft.Text("Risk Assessment Matrix", size=18, weight=ft.FontWeight.BOLD, color="#2c3e50"),
                            ft.Divider(),
                            ft.Row([
                                ft.Column([
                                    ft.Text("Inherent Risk", size=14, weight=ft.FontWeight.BOLD),
                                    ft.Container(
                                        width=100,
                                        height=100,
                                        bgcolor="#e74c3c",
                                        border_radius=50,
                                        alignment=ft.alignment.center,
                                        content=ft.Text("HIGH", color="white", weight=ft.FontWeight.BOLD)
                                    )
                                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                                ft.Container(width=50),
                                ft.Icon(ft.icons.ARROW_FORWARD, size=30, color="#7f8c8d"),
                                ft.Container(width=50),
                                ft.Column([
                                    ft.Text("Residual Risk", size=14, weight=ft.FontWeight.BOLD),
                                    ft.Container(
                                        width=100,
                                        height=100,
                                        bgcolor="#f39c12",
                                        border_radius=50,
                                        alignment=ft.alignment.center,
                                        content=ft.Text("MEDIUM", color="white", weight=ft.FontWeight.BOLD)
                                    )
                                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                            ], alignment=ft.MainAxisAlignment.CENTER)
                        ])
                    )
                ),
                
                ft.Container(height=20),
                
                # Risk details
                ft.Row([
                    ft.Column([
                        ft.Card(
                            content=ft.Container(
                                padding=20,
                                content=ft.Column([
                                    ft.Text("Risk Details", size=16, weight=ft.FontWeight.BOLD, color="#2c3e50"),
                                    ft.Divider(),
                                    self._create_info_row("Risk Category", "Loading..."),
                                    self._create_info_row("Primary Risk", "Loading..."),
                                    self._create_info_row("Secondary Risks", "Loading..."),
                                    ft.Container(height=10),
                                    ft.Text("Risk Description", size=14, weight=ft.FontWeight.BOLD),
                                    ft.Container(
                                        content=ft.Text("Loading risk description...", color="#7f8c8d"),
                                        bgcolor="#f8f9fa",
                                        padding=15,
                                        border_radius=5
                                    )
                                ])
                            )
                        )
                    ], expand=1),
                    
                    ft.Container(width=20),
                    
                    ft.Column([
                        ft.Card(
                            content=ft.Container(
                                padding=20,
                                content=ft.Column([
                                    ft.Text("Risk Assessment", size=16, weight=ft.FontWeight.BOLD, color="#2c3e50"),
                                    ft.Divider(),
                                    self._create_info_row("Likelihood", "Loading..."),
                                    self._create_info_row("Impact", "Loading..."),
                                    self._create_info_row("Risk Score", "Loading..."),
                                    self._create_info_row("Risk Rating", "Loading..."),
                                    ft.Container(height=10),
                                    ft.Text("Risk Appetite", size=14, weight=ft.FontWeight.BOLD),
                                    ft.ProgressBar(value=0.8, bgcolor="#ecf0f1", color="#e74c3c"),
                                    ft.Text("Above appetite threshold", color="#e74c3c", size=12)
                                ])
                            )
                        )
                    ], expand=1)
                ])
            ], scroll=ft.ScrollMode.AUTO)
        )
    
    def _build_controls_tab(self):
        """Build the controls tab"""
        return ft.Container(
            padding=20,
            content=ft.Column([
                # Controls header with actions
                ft.Row([
                    ft.Text("Control Framework", size=20, weight=ft.FontWeight.BOLD, color="#2c3e50"),
                    ft.Container(expand=True),
                    ft.ElevatedButton(
                        text="Test Controls",
                        icon=ft.icons.PLAY_ARROW,
                        bgcolor="#3498db",
                        color="white",
                        on_click=self._start_control_testing
                    )
                ]),
                
                ft.Container(height=20),
                
                # Controls effectiveness summary
                ft.Card(
                    content=ft.Container(
                        padding=20,
                        content=ft.Column([
                            ft.Text("Control Effectiveness Summary", size=16, weight=ft.FontWeight.BOLD),
                            ft.Divider(),
                            ft.Row([
                                self._create_control_status_card("Effective", "8", "#2ecc71"),
                                self._create_control_status_card("Needs Improvement", "3", "#f39c12"),
                                self._create_control_status_card("Ineffective", "1", "#e74c3c"),
                                self._create_control_status_card("Not Tested", "2", "#95a5a6")
                            ], spacing=20)
                        ])
                    )
                ),
                
                ft.Container(height=20),
                
                # Controls detail table
                ft.Card(
                    content=ft.Container(
                        padding=20,
                        content=ft.Column([
                            ft.Text("Control Details", size=16, weight=ft.FontWeight.BOLD),
                            ft.Divider(),
                            ft.DataTable(
                                columns=[
                                    ft.DataColumn(ft.Text("Control ID")),
                                    ft.DataColumn(ft.Text("Description")),
                                    ft.DataColumn(ft.Text("Type")),
                                    ft.DataColumn(ft.Text("Effectiveness")),
                                    ft.DataColumn(ft.Text("Last Tested")),
                                    ft.DataColumn(ft.Text("Actions"))
                                ],
                                rows=[
                                    # Will be populated with actual data
                                    ft.DataRow(cells=[
                                        ft.DataCell(ft.Text("CTRL-001")),
                                        ft.DataCell(ft.Text("Access Control Management")),
                                        ft.DataCell(ft.Text("Preventive")),
                                        ft.DataCell(ft.Container(
                                            content=ft.Text("Effective", color="white", size=12),
                                            bgcolor="#2ecc71",
                                            padding=5,
                                            border_radius=3
                                        )),
                                        ft.DataCell(ft.Text("2025-03-01")),
                                        ft.DataCell(ft.IconButton(
                                            icon=ft.Icons.MORE_VERT,
                                            tooltip="Control actions"
                                        ))
                                    ])
                                ],
                                border=ft.border.all(1, "#e6e9ed"),
                                border_radius=5,
                                heading_row_color="#f8f9fa"
                            )
                        ])
                    )
                )
            ], scroll=ft.ScrollMode.AUTO)
        )
    
    def _build_findings_tab(self):
        """Build the findings tab"""
        return ft.Container(
            padding=20,
            content=ft.Column([
                # Findings summary
                ft.Row([
                    ft.Text("Assessment Findings", size=20, weight=ft.FontWeight.BOLD, color="#2c3e50"),
                    ft.Container(expand=True),
                    ft.ElevatedButton(
                        text="Add Finding",
                        icon=ft.icons.ADD,
                        bgcolor="#2ecc71",
                        color="white",
                        on_click=self._add_finding
                    )
                ]),
                
                ft.Container(height=20),
                
                # Key findings
                ft.Card(
                    content=ft.Container(
                        padding=20,
                        content=ft.Column([
                            ft.Text("Key Findings", size=16, weight=ft.FontWeight.BOLD),
                            ft.Divider(),
                            ft.Container(
                                content=ft.Text("Loading findings...", color="#7f8c8d"),
                                bgcolor="#f8f9fa",
                                padding=15,
                                border_radius=5,
                                width=800
                            )
                        ])
                    )
                ),
                
                ft.Container(height=20),
                
                # Recommendations
                ft.Card(
                    content=ft.Container(
                        padding=20,
                        content=ft.Column([
                            ft.Text("Recommendations", size=16, weight=ft.FontWeight.BOLD),
                            ft.Divider(),
                            ft.Container(
                                content=ft.Text("Loading recommendations...", color="#7f8c8d"),
                                bgcolor="#f8f9fa",
                                padding=15,
                                border_radius=5,
                                width=800
                            )
                        ])
                    )
                ),
                
                ft.Container(height=20),
                
                # Management response
                ft.Card(
                    content=ft.Container(
                        padding=20,
                        content=ft.Column([
                            ft.Row([
                                ft.Text("Management Response", size=16, weight=ft.FontWeight.BOLD),
                                ft.Container(expand=True),
                                ft.ElevatedButton(
                                    text="Request Response",
                                    icon=ft.icons.SEND,
                                    bgcolor="#3498db",
                                    color="white",
                                    on_click=self._request_management_response
                                )
                            ]),
                            ft.Divider(),
                            ft.Container(
                                content=ft.Text("Awaiting management response...", color="#7f8c8d", style=ft.TextThemeStyle.BODY_MEDIUM),
                                bgcolor="#f8f9fa",
                                padding=15,
                                border_radius=5,
                                width=800
                            )
                        ])
                    )
                )
            ], scroll=ft.ScrollMode.AUTO)
        )
    
    def _build_heatmap_tab(self):
        """Build the heatmap visualization tab"""
        return ft.Container(
            padding=20,
            content=ft.Column([
                ft.Text("Risk Heatmap Visualization", size=20, weight=ft.FontWeight.BOLD, color="#2c3e50"),
                ft.Text("Visual representation of risk assessment data", color="#7f8c8d"),
                ft.Container(height=20),
                
                # Heatmap container
                ft.Container(
                    content=ft.Text("Loading heatmap...", size=16, color="#7f8c8d"),
                    alignment=ft.alignment.center,
                    height=400,
                    bgcolor="#f8f9fa",
                    border_radius=5,
                    border=ft.border.all(1, "#e6e9ed")
                )
            ])
        )
    
    def _build_collaboration_tab(self):
        """Build the collaboration tab"""
        return ft.Container(
            padding=20,
            content=ft.Column([
                # Collaboration header
                ft.Row([
                    ft.Text("Team Collaboration", size=20, weight=ft.FontWeight.BOLD, color="#2c3e50"),
                    ft.Container(expand=True),
                    ft.ElevatedButton(
                        text="Add Comment",
                        icon=ft.icons.COMMENT,
                        bgcolor="#3498db",
                        color="white",
                        on_click=self._add_comment
                    )
                ]),
                
                ft.Container(height=20),
                
                # Team members
                ft.Card(
                    content=ft.Container(
                        padding=20,
                        content=ft.Column([
                            ft.Text("Assessment Team", size=16, weight=ft.FontWeight.BOLD),
                            ft.Divider(),
                            ft.Row([
                                self._create_team_member("John Smith", "Lead Auditor", "#3498db"),
                                self._create_team_member("Sarah Johnson", "Risk Analyst", "#2ecc71"),
                                self._create_team_member("Mike Davis", "Control Specialist", "#f39c12")
                            ], spacing=20)
                        ])
                    )
                ),
                
                ft.Container(height=20),
                
                # Comments and activity
                ft.Card(
                    content=ft.Container(
                        padding=20,
                        content=ft.Column([
                            ft.Text("Comments & Activity", size=16, weight=ft.FontWeight.BOLD),
                            ft.Divider(),
                            
                            # Comment input
                            ft.TextField(
                                label="Add a comment...",
                                multiline=True,
                                min_lines=2,
                                max_lines=4,
                                border=ft.InputBorder.OUTLINE,
                                expand=True
                            ),
                            ft.Container(height=10),
                            ft.Row([
                                ft.Container(expand=True),
                                ft.ElevatedButton(
                                    text="Post Comment",
                                    icon=ft.icons.SEND,
                                    bgcolor="#2ecc71",
                                    color="white"
                                )
                            ]),
                            
                            ft.Container(height=20),
                            
                            # Activity feed
                            ft.Column([
                                self._create_activity_item(
                                    "John Smith", 
                                    "Started control testing for CTRL-001", 
                                    "2 hours ago",
                                    ft.icons.PLAY_ARROW,
                                    "#3498db"
                                ),
                                self._create_activity_item(
                                    "Sarah Johnson", 
                                    "Updated risk assessment findings", 
                                    "1 day ago",
                                    ft.icons.EDIT,
                                    "#f39c12"
                                ),
                                self._create_activity_item(
                                    "Mike Davis", 
                                    "Added new control recommendation", 
                                    "2 days ago",
                                    ft.icons.ADD_CIRCLE,
                                    "#2ecc71"
                                )
                            ])
                        ])
                    )
                )
            ], scroll=ft.ScrollMode.AUTO)
        )
    
    def _build_action_panel(self):
        """Build the bottom action panel"""
        return ft.Container(
            height=60,
            bgcolor="#f8f9fa",
            padding=ft.padding.symmetric(horizontal=30, vertical=10),
            content=ft.Row([
                ft.ElevatedButton(
                    text="Back to List",
                    icon=ft.icons.LIST,
                    on_click=self._handle_back,
                    bgcolor="#95a5a6",
                    color="white"
                ),
                ft.Container(expand=True),
                ft.ElevatedButton(
                    text="Generate Report",
                    icon=ft.icons.DESCRIPTION,
                    bgcolor="#9b59b6",
                    color="white",
                    on_click=self._generate_report
                ),
                ft.Container(width=10),
                ft.ElevatedButton(
                    text="Edit Assessment",
                    icon=ft.icons.EDIT,
                    bgcolor="#3498db",
                    color="white",
                    on_click=self._edit_assessment
                )
            ])
        )
    
    # Helper methods for UI components
    def _create_metric_card(self, title, value, color, icon):
        """Create a metric display card"""
        return ft.Card(
            content=ft.Container(
                width=200,
                height=120,
                padding=20,
                content=ft.Column([
                    ft.Row([
                        ft.Text(title, size=14, color="#7f8c8d"),
                        ft.Container(expand=True),
                        ft.Icon(icon, color=color, size=24)
                    ]),
                    ft.Container(height=10),
                    ft.Text(value, size=24, weight=ft.FontWeight.BOLD, color=color)
                ])
            )
        )
    
    def _create_info_row(self, label, value):
        """Create an information row"""
        return ft.Container(
            content=ft.Row([
                ft.Text(f"{label}:", weight=ft.FontWeight.BOLD, width=120),
                ft.Text(str(value), color="#2c3e50", expand=True)
            ]),
            margin=ft.margin.only(bottom=8)
        )
    
    def _create_timeline_item(self, title, status, color):
        """Create a timeline item"""
        return ft.Container(
            content=ft.Row([
                ft.Container(
                    width=12,
                    height=12,
                    bgcolor=color,
                    border_radius=6
                ),
                ft.Container(width=10),
                ft.Column([
                    ft.Text(title, size=14, weight=ft.FontWeight.BOLD),
                    ft.Text(status, size=12, color=color)
                ], spacing=2)
            ]),
            margin=ft.margin.only(bottom=15)
        )
    
    def _create_control_status_card(self, status, count, color):
        """Create control status card"""
        return ft.Card(
            content=ft.Container(
                width=150,
                height=80,
                padding=15,
                content=ft.Column([
                    ft.Text(status, size=12, color="#7f8c8d"),
                    ft.Text(count, size=24, weight=ft.FontWeight.BOLD, color=color)
                ], alignment=ft.MainAxisAlignment.CENTER)
            )
        )
    
    def _create_team_member(self, name, role, color):
        """Create team member card"""
        return ft.Container(
            content=ft.Column([
                ft.Container(
                    width=60,
                    height=60,
                    bgcolor=color,
                    border_radius=30,
                    alignment=ft.alignment.center,
                    content=ft.Text(name[0], color="white", size=20, weight=ft.FontWeight.BOLD)
                ),
                ft.Text(name, size=14, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                ft.Text(role, size=12, color="#7f8c8d", text_align=ft.TextAlign.CENTER)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5)
        )
    
    def _create_activity_item(self, user, action, time, icon, color):
        """Create activity feed item"""
        return ft.Container(
            content=ft.Row([
                ft.Icon(icon, color=color, size=20),
                ft.Container(width=10),
                ft.Column([
                    ft.Text(f"{user} {action}", size=14),
                    ft.Text(time, size=12, color="#7f8c8d")
                ], spacing=2, expand=True)
            ]),
            margin=ft.margin.only(bottom=15),
            padding=10,
            bgcolor="#f8f9fa",
            border_radius=5
        )
    
    def _get_status_color(self, status):
        """Get color for workflow status"""
        colors = {
            "In Progress": "#3498db",
            "Completed": "#2ecc71",
            "On Hold": "#f39c12",
            "Cancelled": "#e74c3c"
        }
        return colors.get(status, "#95a5a6")
    
    # Event handlers
    def _on_tab_change(self, e):
        """Handle tab change"""
        self.current_tab = e.control.selected_index
    
    def _update_ui_with_data(self):
        """Update UI with loaded assessment data"""
        if not self.assessment_data:
            return
        
        # Update status bar and other components with real data
        if hasattr(self, 'page') and self.page:
            self.page.update()
    
    # Action handlers
    def _handle_back(self, e):
        """Handle back navigation"""
        if self.on_back_callback:
            self.on_back_callback()
    
    def _edit_assessment(self, e):
        """Edit assessment"""
        if self.on_edit_callback:
            self.on_edit_callback(self.reference_id)
    
    async def _start_control_testing(self, e):
        """Start control testing workflow"""
        try:
            # Call API to start control testing
            result = await self.assessment_controller.start_control_testing(
                self.reference_id,
                {
                    "controlId": "CTRL-001",
                    "testerId": self.user.id if self.user else "1",
                    "testFrequency": "Monthly"
                }
            )
            
            if result:
                self._show_success("Control testing workflow started successfully")
            else:
                self._show_error("Failed to start control testing")
                
        except Exception as e:
            self._show_error(f"Error starting control testing: {str(e)}")
    
    async def _export_assessment(self, format_type):
        """Export assessment to specified format"""
        try:
            self._show_loading(f"Exporting to {format_type.upper()}...")
            
            # Simulate export process
            await asyncio.sleep(2)
            
            self._show_success(f"Assessment exported to {format_type.upper()} successfully")
            
        except Exception as e:
            self._show_error(f"Export failed: {str(e)}")
        finally:
            self._hide_loading()
    
    def _share_assessment(self, e):
        """Share assessment with team members"""
        # Implementation for sharing
        self._show_info("Sharing functionality to be implemented")
    
    def _archive_assessment(self, e):
        """Archive assessment"""
        # Implementation for archiving
        self._show_info("Archive functionality to be implemented")
    
    def _add_finding(self, e):
        """Add new finding"""
        self._show_info("Add finding functionality to be implemented")
    
    def _add_comment(self, e):
        """Add new comment"""
        self._show_info("Add comment functionality to be implemented")
    
    def _request_management_response(self, e):
        """Request management response"""
        self._show_info("Management response request functionality to be implemented")
    
    def _generate_report(self, e):
        """Generate comprehensive report"""
        self._show_info("Report generation functionality to be implemented")
    
    # Utility methods
    def _show_loading(self, message="Loading..."):
        """Show loading dialog"""
        self.page.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Processing"),
            content=ft.Column([
                ft.ProgressRing(),
                ft.Text(message)
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, height=100)
        )
        self.page.dialog.open = True
        self.page.update()
    
    def _hide_loading(self):
        """Hide loading dialog"""
        if self.page.dialog:
            self.page.dialog.open = False
            self.page.update()
    
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
    
    def _show_info(self, message):
        """Show info message"""
        self.page.snack_bar = ft.SnackBar(content=ft.Text(message), bgcolor="#3498db")
        self.page.snack_bar.open = True
        self.page.update()
    
    async def cleanup(self):
        """Cleanup resources"""
        try:
            await self.assessment_controller.close()
        except Exception as e:
            print(f"Error during cleanup: {e}") 
