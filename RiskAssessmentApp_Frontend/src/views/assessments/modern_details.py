import flet as ft
from flet import Icons
import asyncio
from datetime import datetime
from src.controllers.assessment_controller import AssessmentController
from src.utils.export_utils import ExportManager
from src.utils.formatters import format_date, format_currency
from src.views.common.base_view import BaseView
import json


class ModernAssessmentDetails(BaseView):
    def __init__(self, page, user, assessment_id=None, reference_id=None, on_back=None, on_edit=None):
        self.page = page
        self.user = user
        self.assessment_id = assessment_id
        self.reference_id = reference_id
        self.on_back_callback = on_back
        self.on_edit_callback = on_edit
        
        # Controllers
        self.assessment_controller = AssessmentController()
        self.export_manager = ExportManager()
        
        # State
        self.assessment_data = None
        self.heatmap_data = None
        self.current_tab = 0
        self.comments = []
        self.workflow_status = "In Progress"
        
        # Header actions in BaseView
        actions = [
            ft.ElevatedButton(
                text="Start Control Testing",
                icon=Icons.PLAY_ARROW,
                bgcolor="#f39c12",
                color="white",
                on_click=self._start_control_testing,
            ),
            ft.PopupMenuButton(
                items=[
                    ft.PopupMenuItem(text="Export to PDF", icon=Icons.PICTURE_AS_PDF, on_click=lambda e: self._export_assessment("pdf")),
                    ft.PopupMenuItem(text="Export to Excel", icon=Icons.TABLE_VIEW, on_click=lambda e: self._export_assessment("excel")),
                    ft.PopupMenuItem(text="Share Assessment", icon=Icons.SHARE, on_click=self._share_assessment),
                    ft.PopupMenuItem(),
                    ft.PopupMenuItem(text="Edit Assessment", icon=Icons.EDIT, on_click=self._edit_assessment),
                    ft.PopupMenuItem(text="Archive Assessment", icon=Icons.ARCHIVE, on_click=self._archive_assessment),
                ],
                icon=Icons.MORE_VERT,
            )
        ]
        super().__init__(page, f"Risk Assessment: {reference_id or ''}", on_back=self._handle_back, actions=actions)

        # Initialize view
        self._init_view()
    
    def _init_view(self):
        """Initialize the view"""
        self._build_ui()
        if self.reference_id:
            self.page.run_task(self._load_assessment_data)

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
            
            # Convert A-001 format to numeric ID for API if needed
            api_reference_id = self.reference_id
            if isinstance(self.reference_id, str) and self.reference_id.startswith("A-"):
                try:
                    api_reference_id = int(self.reference_id[2:])  # Extract number from A-001 -> 1
                    print(f"DEBUG: Converted {self.reference_id} to {api_reference_id}")
                except ValueError:
                    print(f"DEBUG: Failed to convert {self.reference_id} to numeric ID")
                    self._show_error("Invalid assessment ID format")
                    return
            
            print(f"DEBUG: Loading assessment data for reference_id: {api_reference_id} (type: {type(api_reference_id)})")
            
            # Load assessment and heatmap data concurrently
            tasks = [
                self.assessment_controller.get_risk_assessment(api_reference_id),
                self.assessment_controller.get_heatmap_data(api_reference_id)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            self.assessment_data = results[0] if not isinstance(results[0], Exception) else None
            self.heatmap_data = results[1] if not isinstance(results[1], Exception) else None
            
            print(f"DEBUG: Assessment data loaded: {self.assessment_data is not None}")
            if self.assessment_data:
                print(f"DEBUG: Assessment data keys: {list(self.assessment_data.keys()) if isinstance(self.assessment_data, dict) else 'Not a dict'}")
            
            if self.assessment_data:
                self._update_ui_with_data()
            else:
                self._show_error("Failed to load assessment data")
                
        except Exception as e:
            print(f"DEBUG: Exception in _load_assessment_data: {str(e)}")
            self._show_error(f"Error loading assessment: {str(e)}")
        finally:
            self._hide_loading()
    
    def _build_ui(self):
        """Build the main UI structure"""
        # Main content tabs
        tabs = self._build_content_tabs()
        
        # Action panel
        action_panel = self._build_action_panel()
        
        # Layout
        main_panel = ft.Column([
            tabs,
            ft.Divider(height=1, color="#e6e9ed"),
            action_panel
        ], spacing=0, expand=True, scroll=ft.ScrollMode.AUTO)
        self.cards_column.controls.clear()
        self.add_card(main_panel)
    
    # Legacy header removed; BaseView header is used.
    
    def _build_status_bar(self):
        """Build the status indicator bar"""
        return ft.Container(
            height=50,
            bgcolor="#f8f9fa",
            padding=ft.padding.symmetric(horizontal=30, vertical=10),
            content=ft.Row([
                # Workflow status
                ft.Row([
                    ft.Icon(Icons.ASSIGNMENT, color="#3498db", size=20),
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
                    ft.Icon(Icons.UPDATE, color="#7f8c8d", size=20),
                    ft.Text("Last Updated:", weight=ft.FontWeight.BOLD, color="#2c3e50"),
                    ft.Text("Loading...", color="#7f8c8d")
                ], spacing=10),
                
                ft.Container(expand=True),
                
                # Risk level indicator
                ft.Row([
                    ft.Icon(Icons.WARNING, color="#e74c3c", size=20),
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
                        icon=Icons.DASHBOARD,
                        content=self._build_overview_tab()
                    ),
                    ft.Tab(
                        text="Risk Analysis",
                        icon=Icons.ANALYTICS,
                        content=self._build_risk_analysis_tab()
                    ),
                    ft.Tab(
                        text="Controls",
                        icon=Icons.SECURITY,
                        content=self._build_controls_tab()
                    ),
                    ft.Tab(
                        text="Findings",
                        icon=Icons.SEARCH,
                        content=self._build_findings_tab()
                    ),
                    ft.Tab(
                        text="Heatmap",
                        icon=Icons.VIEW_MODULE,
                        content=self._build_heatmap_tab()
                    ),
                    ft.Tab(
                        text="Collaboration",
                        icon=Icons.GROUP,
                        content=self._build_collaboration_tab()
                    )
                ]
            )
        )
    
    def _build_overview_tab(self):
        """Build the overview tab content"""
        # Get data values with fallbacks
        client = "Loading..."
        assessor = "Loading..."
        start_date = "Loading..."
        end_date = "Loading..."
        approved_by = "Loading..."
        risk_count = 0
        
        if self.assessment_data:
            if isinstance(self.assessment_data, dict):
                client = self.assessment_data.get('Client', 'N/A')
                assessor = self.assessment_data.get('Assessor', 'N/A')
                start_date = self.assessment_data.get('AssessmentStartDate', 'N/A')
                end_date = self.assessment_data.get('AssessmentEndDate', 'N/A')
                approved_by = self.assessment_data.get('ApprovedBy', 'N/A')
                risk_assessments = self.assessment_data.get('RiskAssessments', [])
                risk_count = len(risk_assessments) if risk_assessments else 0
            else:
                client = getattr(self.assessment_data, 'Client', 'N/A')
                assessor = getattr(self.assessment_data, 'Assessor', 'N/A')
                start_date = getattr(self.assessment_data, 'AssessmentStartDate', 'N/A')
                end_date = getattr(self.assessment_data, 'AssessmentEndDate', 'N/A')
                approved_by = getattr(self.assessment_data, 'ApprovedBy', 'N/A')
                risk_assessments = getattr(self.assessment_data, 'RiskAssessments', [])
                risk_count = len(risk_assessments) if risk_assessments else 0
        
        # Format dates
        if start_date != "Loading..." and start_date != "N/A" and start_date:
            try:
                if isinstance(start_date, str):
                    start_date = start_date.split('T')[0]  # Remove time part if present
            except:
                pass
                
        if end_date != "Loading..." and end_date != "N/A" and end_date:
            try:
                if isinstance(end_date, str):
                    end_date = end_date.split('T')[0]  # Remove time part if present
            except:
                pass
        
        return ft.Container(
            padding=20,
            content=ft.Column([
                # Key metrics cards
                ft.Row([
                    self._create_metric_card("Reference ID", str(self.reference_id) if self.reference_id else "N/A", "#3498db", Icons.INFO),
                    self._create_metric_card("Risk Items", str(risk_count), "#2ecc71", Icons.SECURITY),
                    self._create_metric_card("Status", self.workflow_status, "#f39c12", Icons.INFO),
                    self._create_metric_card("Completion", "100%" if risk_count > 0 else "0%", "#9b59b6", Icons.ASSESSMENT)
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
                                    self._create_info_row("Client", client),
                                    self._create_info_row("Assessor", assessor),
                                    self._create_info_row("Start Date", start_date),
                                    self._create_info_row("End Date", end_date),
                                    self._create_info_row("Approved By", approved_by),
                                    self._create_info_row("Risk Items", str(risk_count))
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
        # Build risk assessment items table
        risk_items_content = []
        
        if self.assessment_data:
            risk_assessments = []
            if isinstance(self.assessment_data, dict):
                risk_assessments = self.assessment_data.get('RiskAssessments', [])
            else:
                risk_assessments = getattr(self.assessment_data, 'RiskAssessments', [])
            
            if risk_assessments:
                # Create table header
                risk_items_content.append(
                    ft.Row([
                        ft.Container(ft.Text("Risk Title", weight=ft.FontWeight.BOLD), width=200),
                        ft.Container(ft.Text("Likelihood", weight=ft.FontWeight.BOLD), width=120),
                        ft.Container(ft.Text("Impact", weight=ft.FontWeight.BOLD), width=120),
                        ft.Container(ft.Text("Category", weight=ft.FontWeight.BOLD), width=150),
                        ft.Container(ft.Text("Controls", weight=ft.FontWeight.BOLD), width=200),
                    ], spacing=10)
                )
                
                risk_items_content.append(ft.Divider())
                
                # Add risk assessment rows
                for i, risk in enumerate(risk_assessments):
                    if isinstance(risk, dict):
                        risk_title = risk.get('RisksAssessment_KeyRiskAndFactors', f'Risk {i+1}')
                        likelihood = risk.get('RisksAssessment_RiskLikelihood', 'N/A')
                        impact = risk.get('RisksAssessment_RiskImpact', 'N/A')
                        category = risk.get('RisksAssessment_RiskCategory', 'N/A')
                        controls = risk.get('ControlsAssessment_MitigatingControls', 'N/A')
                    else:
                        risk_title = getattr(risk, 'RisksAssessment_KeyRiskAndFactors', f'Risk {i+1}')
                        likelihood = getattr(risk, 'RisksAssessment_RiskLikelihood', 'N/A')
                        impact = getattr(risk, 'RisksAssessment_RiskImpact', 'N/A')
                        category = getattr(risk, 'RisksAssessment_RiskCategory', 'N/A')
                        controls = getattr(risk, 'ControlsAssessment_MitigatingControls', 'N/A')
                    
                    risk_items_content.append(
                        ft.Container(
                            content=ft.Row([
                                ft.Container(ft.Text(risk_title[:30] + "..." if len(risk_title) > 30 else risk_title), width=200),
                                ft.Container(ft.Text(likelihood), width=120),
                                ft.Container(ft.Text(impact), width=120),
                                ft.Container(ft.Text(category), width=150),
                                ft.Container(ft.Text(controls[:30] + "..." if len(controls) > 30 else controls), width=200),
                            ], spacing=10),
                            padding=ft.padding.symmetric(vertical=8),
                            bgcolor="#f8f9fa" if i % 2 == 0 else None,
                            border_radius=5
                        )
                    )
            else:
                risk_items_content.append(
                    ft.Container(
                        content=ft.Text("No risk assessments found", color="#7f8c8d"),
                        padding=20,
                        alignment=ft.alignment.center
                    )
                )
        else:
            risk_items_content.append(
                ft.Container(
                    content=ft.Text("Loading risk assessments...", color="#7f8c8d"),
                    padding=20,
                    alignment=ft.alignment.center
                )
            )
        
        return ft.Container(
            padding=20,
            content=ft.Column([
                # Risk Assessment Items
                ft.Card(
                    content=ft.Container(
                        padding=20,
                        content=ft.Column([
                            ft.Text("Risk Assessment Items", size=18, weight=ft.FontWeight.BOLD, color="#2c3e50"),
                            ft.Divider(),
                            ft.Container(
                                content=ft.Column(risk_items_content, scroll=ft.ScrollMode.AUTO),
                                height=400
                            )
                        ])
                    )
                )
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
                        icon=Icons.PLAY_ARROW,
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
                                            icon=Icons.MORE_VERT,
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
                        icon=Icons.ADD,
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
                                    icon=Icons.SEND,
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
                        icon=Icons.COMMENT,
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
                                    icon=Icons.SEND,
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
                                    Icons.PLAY_ARROW,
                                    "#3498db"
                                ),
                                self._create_activity_item(
                                    "Sarah Johnson", 
                                    "Updated risk assessment findings", 
                                    "1 day ago",
                                    Icons.EDIT,
                                    "#f39c12"
                                ),
                                self._create_activity_item(
                                    "Mike Davis", 
                                    "Added new control recommendation", 
                                    "2 days ago",
                                    Icons.ADD_CIRCLE,
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
                    icon=Icons.LIST,
                    on_click=self._handle_back,
                    bgcolor="#95a5a6",
                    color="white"
                ),
                ft.Container(expand=True),
                ft.ElevatedButton(
                    text="Generate Report",
                    icon=Icons.DESCRIPTION,
                    bgcolor="#9b59b6",
                    color="white",
                    on_click=self._generate_report
                ),
                ft.Container(width=10),
                ft.ElevatedButton(
                    text="Edit Assessment",
                    icon=Icons.EDIT,
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
        
        try:
            # Update the header title with assessment info
            if hasattr(self.assessment_data, 'Client') or (isinstance(self.assessment_data, dict) and self.assessment_data.get('Client')):
                client_name = self.assessment_data.get('Client') if isinstance(self.assessment_data, dict) else self.assessment_data.Client
                self.header.content.controls[0].value = f"Risk Assessment: {client_name}"
            
            # Update workflow status based on assessment data
            if hasattr(self.assessment_data, 'RiskAssessments') or (isinstance(self.assessment_data, dict) and self.assessment_data.get('RiskAssessments')):
                assessments = self.assessment_data.get('RiskAssessments') if isinstance(self.assessment_data, dict) else self.assessment_data.RiskAssessments
                if assessments and len(assessments) > 0:
                    self.workflow_status = "Completed"
                else:
                    self.workflow_status = "In Progress"
            
            # Rebuild UI with loaded data
            self._build_ui()
            
            # Update status bar and other components with real data
            if hasattr(self, 'page') and self.page:
                self.page.update()
                
        except Exception as e:
            print(f"Error updating UI with data: {str(e)}")
            self._show_error(f"Error displaying assessment data: {str(e)}")
    
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

