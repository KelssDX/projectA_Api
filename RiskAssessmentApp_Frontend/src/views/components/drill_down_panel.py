"""
Drill-Down Panel Component
Provides a side panel or modal for displaying detailed data when users click on chart elements.
"""

import flet as ft
from flet import Icons, Colors
from src.utils.theme import get_theme_colors


class DrillDownPanel(ft.Container):
    """
    A panel component that displays detailed drill-down data from analytics widgets.
    Can be displayed as a side panel or full-screen modal.
    """
    
    def __init__(self, page, on_close=None, on_navigate=None, display_mode="panel"):
        """
        Args:
            page: The Flet page instance
            on_close: Callback when panel is closed
            on_navigate: Callback for navigation actions (e.g., navigate to assessment)
            display_mode: "panel" for side panel, "modal" for full-screen modal
        """
        super().__init__()
        self.page = page
        self.on_close_callback = on_close
        self.on_navigate_callback = on_navigate
        self.display_mode = display_mode
        self.colors = get_theme_colors(page.theme_mode)
        self.context = None
        self.data = None
        
        # Styling based on display mode
        if display_mode == "panel":
            self.width = 400
            self.height = None  # Full height
            self.border_radius = ft.border_radius.only(top_left=12, bottom_left=12)
        else:
            self.width = None
            self.height = None
            self.border_radius = 12
            
        self.bgcolor = self.colors.surface
        self.border = ft.border.all(1, self.colors.border)
        self.padding = 20
        self.animate = ft.Animation(300, ft.AnimationCurve.EASE_OUT)
        self.visible = False
        
        # Build the panel structure
        self._build_panel()
    
    def _build_panel(self):
        """Build the panel UI structure"""
        # Close button
        self.close_btn = ft.IconButton(
            icon=Icons.CLOSE,
            icon_size=20,
            tooltip="Close",
            on_click=self._handle_close
        )
        
        # Title
        self.title_text = ft.Text(
            "Drill-Down Details",
            size=18,
            weight=ft.FontWeight.BOLD,
            color=self.colors.text_primary
        )
        
        # Subtitle/breadcrumb
        self.subtitle_text = ft.Text(
            "",
            size=12,
            color=self.colors.text_secondary
        )
        
        # Header
        header = ft.Row([
            ft.Column([
                self.title_text,
                self.subtitle_text
            ], spacing=2, expand=True),
            self.close_btn
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        
        # Content area
        self.content_area = ft.Container(expand=True)
        
        # Action buttons
        self.action_row = ft.Row([], spacing=10)
        
        # Main layout
        self.content = ft.Column([
            header,
            ft.Divider(height=1, color=self.colors.border),
            self.content_area,
            ft.Container(height=10),
            self.action_row
        ], spacing=15, expand=True)
    
    def show(self, context, data=None):
        """
        Show the drill-down panel with the given context and data.
        
        Args:
            context: Dictionary describing what was clicked, e.g.:
                     {"type": "heatmap_cell", "impact": 5, "likelihood": 4, "riskLevel": "Critical"}
                     {"type": "findings_aging", "severity": "High", "ageBucket": "90+ days"}
            data: Optional data to display (list of items, details, etc.)
        """
        self.context = context
        self.data = data
        self.visible = True
        
        # Update title and content based on context type
        context_type = context.get("type", "generic")
        
        if context_type == "heatmap_cell":
            self._render_heatmap_details(context, data)
        elif context_type == "findings_aging":
            self._render_findings_details(context, data)
        elif context_type == "risk_trend":
            self._render_trend_details(context, data)
        elif context_type == "audit_coverage":
            self._render_coverage_details(context, data)
        elif context_type == "department_comparison":
            self._render_department_details(context, data)
        elif context_type == "control_effectiveness":
            self._render_control_details(context, data)
        elif context_type == "compliance_framework":
            self._render_compliance_details(context, data)
        else:
            self._render_generic_details(context, data)
        
        self.update()
    
    def hide(self):
        """Hide the drill-down panel"""
        self.visible = False
        self.context = None
        self.data = None
        self.update()
    
    def _handle_close(self, e=None):
        """Handle close button click"""
        self.hide()
        if self.on_close_callback:
            self.on_close_callback()
    
    def _render_heatmap_details(self, context, data):
        """Render heatmap cell drill-down"""
        self.title_text.value = f"{context.get('riskLevel', 'Unknown')} Risk"
        self.subtitle_text.value = f"Impact: {context.get('impact', 'N/A')} | Likelihood: {context.get('likelihood', 'N/A')}"
        
        risk_level = context.get('riskLevel', 'Medium')
        level_color = {"Critical": "#DC2626", "High": "#EF4444", "Medium": "#F59E0B", "Low": "#10B981"}.get(risk_level, "#6B7280")
        
        # Summary card
        summary = ft.Container(
            content=ft.Row([
                ft.Icon(Icons.WARNING if risk_level in ["Critical", "High"] else Icons.INFO, size=24, color=level_color),
                ft.Column([
                    ft.Text(f"{context.get('count', 0)} Risks", size=20, weight=ft.FontWeight.BOLD, color=level_color),
                    ft.Text("in this cell", size=12, color=self.colors.text_secondary)
                ], spacing=0)
            ], spacing=10),
            padding=15,
            bgcolor=level_color + "15",
            border_radius=8
        )
        
        # Action buttons
        self.action_row.controls = [
            ft.FilledButton("View All Risks", icon=Icons.LIST, on_click=lambda e: self._navigate_to("risks", context)),
            ft.OutlinedButton("Export", icon=Icons.DOWNLOAD, on_click=lambda e: self._export_data(context))
        ]
        
        self.content_area.content = ft.Column([
            summary,
            ft.Container(height=10),
            ft.Text("Risk List", size=14, weight=ft.FontWeight.BOLD),
            ft.Text("Click 'View All Risks' to see detailed risk items", size=12, color=self.colors.text_secondary)
        ], spacing=10)
    
    def _render_findings_details(self, context, data):
        """Render findings aging drill-down"""
        self.title_text.value = f"{context.get('severity', 'Unknown')} Severity Findings"
        self.subtitle_text.value = f"Age Bucket: {context.get('ageBucket', 'N/A')}"
        
        severity = context.get('severity', 'Medium')
        severity_color = {"Critical": "#DC2626", "High": "#EF4444", "Medium": "#F59E0B", "Low": "#10B981"}.get(severity, "#6B7280")
        
        summary = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Container(width=10, height=10, bgcolor=severity_color, border_radius=5),
                    ft.Text(f"{severity} Findings", size=16, weight=ft.FontWeight.BOLD)
                ], spacing=8),
                ft.Text(f"Age: {context.get('ageBucket', 'Unknown')}", size=12, color=self.colors.text_secondary)
            ], spacing=5),
            padding=15,
            bgcolor=severity_color + "15",
            border_radius=8
        )
        
        self.action_row.controls = [
            ft.FilledButton("View Findings", icon=Icons.BUG_REPORT, on_click=lambda e: self._navigate_to("findings", context)),
            ft.OutlinedButton("Export", icon=Icons.DOWNLOAD)
        ]
        
        self.content_area.content = ft.Column([summary], spacing=10)
    
    def _render_trend_details(self, context, data):
        """Render risk trend drill-down"""
        self.title_text.value = "Trend Analysis"
        self.subtitle_text.value = f"Period: {context.get('period', 'N/A')}"
        
        self.action_row.controls = [
            ft.FilledButton("View History", icon=Icons.TIMELINE),
            ft.OutlinedButton("Compare Periods", icon=Icons.COMPARE_ARROWS)
        ]
        
        self.content_area.content = ft.Column([
            ft.Text("Trend details will be displayed here", size=12, color=self.colors.text_secondary)
        ], spacing=10)
    
    def _render_coverage_details(self, context, data):
        """Render audit coverage drill-down"""
        self.title_text.value = context.get('nodeName', 'Audit Coverage')
        self.subtitle_text.value = f"Year: {context.get('year', 'N/A')}"
        
        self.action_row.controls = [
            ft.FilledButton("View Audits", icon=Icons.ASSIGNMENT),
            ft.OutlinedButton("Schedule Audit", icon=Icons.CALENDAR_MONTH)
        ]
        
        self.content_area.content = ft.Column([
            ft.Text("Coverage details for this node", size=12, color=self.colors.text_secondary)
        ], spacing=10)
    
    def _render_department_details(self, context, data):
        """Render department comparison drill-down"""
        self.title_text.value = context.get('departmentName', 'Department')
        self.subtitle_text.value = f"Risk Score: {context.get('riskScore', 'N/A')}"
        
        self.action_row.controls = [
            ft.FilledButton("View Risks", icon=Icons.LIST),
            ft.OutlinedButton("Compare", icon=Icons.COMPARE)
        ]
        
        self.content_area.content = ft.Column([
            ft.Text("Department risk breakdown", size=12, color=self.colors.text_secondary)
        ], spacing=10)
    
    def _render_control_details(self, context, data):
        """Render control effectiveness drill-down"""
        self.title_text.value = context.get('controlName', 'Control')
        self.subtitle_text.value = f"Risk Area: {context.get('riskArea', 'N/A')}"
        
        self.action_row.controls = [
            ft.FilledButton("View Control", icon=Icons.VERIFIED_USER),
            ft.OutlinedButton("Create Finding", icon=Icons.BUG_REPORT)
        ]
        
        self.content_area.content = ft.Column([
            ft.Text("Control effectiveness details", size=12, color=self.colors.text_secondary)
        ], spacing=10)
    
    def _render_compliance_details(self, context, data):
        """Render compliance framework drill-down"""
        self.title_text.value = context.get('framework', 'Framework')
        self.subtitle_text.value = context.get('fullName', '')
        
        score = context.get('score', 0)
        score_color = "#10B981" if score >= 90 else ("#F59E0B" if score >= 70 else "#EF4444")
        
        summary = ft.Container(
            content=ft.Column([
                ft.Text(f"{score:.0f}%", size=32, weight=ft.FontWeight.BOLD, color=score_color),
                ft.Text("Compliance Score", size=12, color=self.colors.text_secondary)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=20,
            bgcolor=score_color + "15",
            border_radius=8,
            alignment=ft.alignment.center
        )
        
        self.action_row.controls = [
            ft.FilledButton("View Controls", icon=Icons.CHECKLIST),
            ft.OutlinedButton("View Gaps", icon=Icons.WARNING)
        ]
        
        self.content_area.content = ft.Column([summary], spacing=10)
    
    def _render_generic_details(self, context, data):
        """Render generic drill-down for unknown types"""
        self.title_text.value = "Details"
        self.subtitle_text.value = str(context.get("type", "Unknown"))
        
        # Display context as key-value pairs
        items = []
        for key, value in context.items():
            if key != "type":
                items.append(
                    ft.Row([
                        ft.Text(f"{key}:", size=12, color=self.colors.text_secondary),
                        ft.Text(str(value), size=12)
                    ], spacing=10)
                )
        
        self.action_row.controls = [
            ft.OutlinedButton("Close", icon=Icons.CLOSE, on_click=self._handle_close)
        ]
        
        self.content_area.content = ft.Column(items, spacing=5)
    
    def _navigate_to(self, destination, context):
        """Navigate to a specific view"""
        if self.on_navigate_callback:
            self.on_navigate_callback(destination, context)
    
    def _export_data(self, context):
        """Export the current data"""
        if self.page:
            self.page.show_snack_bar(ft.SnackBar(
                content=ft.Text("Exporting data..."),
                action="OK"
            ))


class DrillDownDialog(ft.AlertDialog):
    """
    Alternative drill-down display as a modal dialog
    """
    
    def __init__(self, page, context, data=None, on_navigate=None):
        self.page = page
        self.context = context
        self.data = data
        self.on_navigate = on_navigate
        self.colors = get_theme_colors(page.theme_mode)
        
        # Create the drill-down panel content
        self.panel = DrillDownPanel(page, display_mode="modal")
        self.panel.on_navigate_callback = on_navigate
        self.panel.visible = True
        
        super().__init__(
            modal=True,
            title=ft.Text(context.get("type", "Details").replace("_", " ").title()),
            content=ft.Container(
                content=self.panel,
                width=500,
                height=400
            ),
            actions=[
                ft.TextButton("Close", on_click=lambda e: self._close())
            ]
        )
        
        self.panel.show(context, data)
    
    def _close(self):
        self.open = False
        self.page.update()
