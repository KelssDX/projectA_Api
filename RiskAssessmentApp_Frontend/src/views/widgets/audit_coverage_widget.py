import flet as ft
from flet import Icons
from src.api.auditing_client import AuditingAPIClient
from src.views.widgets.base_widget import BaseWidget
from datetime import datetime


class AuditCoverageWidget(BaseWidget):
    """
    Audit Coverage Map Widget
    Displays a treemap-style visualization of audit coverage across the universe
    Color-coded by coverage percentage: Red (<50%), Yellow (50-80%), Green (>80%)
    """

    def __init__(self, page, reference_id=None, audit_universe_id=None, year=None, quarter=None, on_drill_down=None):
        super().__init__(
            page=page,
            title="Audit Coverage Map",
            icon=Icons.MAP,
            description="Coverage across audit universe"
        )
        self.reference_id = reference_id
        self.audit_universe_id = audit_universe_id
        self.year = year or datetime.now().year
        self.quarter = quarter
        self.on_drill_down = on_drill_down
        self.auditing_client = AuditingAPIClient()
        self.coverage_data = None

    def build_content(self):
        """Build the widget content"""
        self.content_container = ft.Container(
            content=ft.Column([
                ft.ProgressRing(width=30, height=30),
                ft.Text("Loading coverage data...", size=12)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            expand=True,
            alignment=ft.alignment.center
        )
        self.load_data()
        return self.content_container

    def load_data(self):
        """Load audit coverage data"""
        if hasattr(self, 'page') and self.page:
            self.page.run_task(self._load_data_async)

    async def _load_data_async(self):
        """Async data loading"""
        try:
            self.coverage_data = await self.auditing_client.get_audit_coverage_map(
                year=self.year,
                quarter=self.quarter
            )
            self._update_display()
        except Exception as e:
            print(f"Error loading audit coverage: {e}")
            self.content_container.content = ft.Text(f"Error: {str(e)}", color="red")
            self.page.update()

    def _update_display(self):
        """Update the widget display with loaded data"""
        if not self.coverage_data:
            self.content_container.content = ft.Text("No coverage data available", color=self.colors.text_secondary)
            self.page.update()
            return

        nodes = self.coverage_data.get("nodes", [])
        summary = self.coverage_data.get("summary", {})

        if not nodes:
            self.content_container.content = ft.Column([
                ft.Icon(Icons.ASSIGNMENT_LATE, size=48, color=self.colors.text_secondary),
                ft.Text("No audit universe data", size=14),
                ft.Text("Set up audit universe to track coverage", size=12, color=self.colors.text_secondary)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER, expand=True)
            self.page.update()
            return

        # Build treemap-style visualization
        # We'll create a grid of coverage tiles

        def get_coverage_color(percentage):
            """Get color based on coverage percentage"""
            if percentage < 50:
                return "#EF4444"  # Red
            elif percentage < 80:
                return "#F59E0B"  # Yellow/Orange
            else:
                return "#10B981"  # Green

        def create_coverage_tile(node, is_root=False):
            """Create a tile for a coverage node"""
            coverage = node.get("coveragePercentage", 0)
            color = get_coverage_color(coverage)
            risk_rating = node.get("riskRating", "Medium")
            name = node.get("name", "Unknown")

            # Risk indicator
            risk_colors = {"High": "#EF4444", "Medium": "#F59E0B", "Low": "#10B981", "Critical": "#DC2626"}
            risk_color = risk_colors.get(risk_rating, "#6B7280")

            tile_width = 140 if is_root else 120
            tile_height = 80 if is_root else 70

            return ft.Container(
                width=tile_width,
                height=tile_height,
                bgcolor=color + "20",  # Light background
                border=ft.border.all(2, color),
                border_radius=8,
                padding=8,
                content=ft.Column([
                    ft.Row([
                        ft.Text(
                            name[:15] + "..." if len(name) > 15 else name,
                            size=11,
                            weight=ft.FontWeight.BOLD,
                            color=self.colors.text_primary,
                            expand=True
                        ),
                        ft.Container(
                            width=8,
                            height=8,
                            bgcolor=risk_color,
                            border_radius=4,
                            tooltip=f"Risk: {risk_rating}"
                        )
                    ], spacing=4),
                    ft.Text(
                        f"{coverage:.0f}%",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color=color
                    ),
                    ft.Row([
                        ft.Text(f"{node.get('completedAudits', 0)}/{node.get('plannedAudits', 0)}", size=9, color=self.colors.text_secondary),
                        ft.Text(f"F:{node.get('openFindings', 0)}", size=9, color="#EF4444" if node.get('openFindings', 0) > 0 else self.colors.text_secondary),
                    ], spacing=10)
                ], spacing=2),
                on_click=lambda e, n=node: self._handle_drill_down(n),
                tooltip=f"{name}\nCoverage: {coverage:.1f}%\nPlanned: {node.get('plannedAudits', 0)}\nCompleted: {node.get('completedAudits', 0)}\nOpen Findings: {node.get('openFindings', 0)}"
            )

        # Create tiles for root nodes and their immediate children
        tiles = []
        for root_node in nodes:
            root_tile = create_coverage_tile(root_node, is_root=True)
            tiles.append(root_tile)

            # Add children tiles (if any)
            children = root_node.get("children", [])
            for child in children[:4]:  # Limit to first 4 children per root
                tiles.append(create_coverage_tile(child))

        # Arrange tiles in a wrapped row
        tiles_container = ft.Container(
            content=ft.Row(
                controls=tiles,
                wrap=True,
                spacing=8,
                run_spacing=8
            ),
            padding=5
        )

        # Summary section
        overall_coverage = summary.get("overallCoverage", 0)
        overall_color = get_coverage_color(overall_coverage)

        summary_row = ft.Row([
            ft.Container(
                content=ft.Column([
                    ft.Text(f"{overall_coverage:.0f}%", size=28, weight=ft.FontWeight.BOLD, color=overall_color),
                    ft.Text("Overall", size=10, color=self.colors.text_secondary)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
                expand=True
            ),
            ft.Container(
                content=ft.Column([
                    ft.Text(str(summary.get("nodesAudited", 0)), size=20, weight=ft.FontWeight.BOLD, color=self.colors.primary),
                    ft.Text(f"of {summary.get('totalNodes', 0)}", size=10, color=self.colors.text_secondary)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
                expand=True
            ),
            ft.Container(
                content=ft.Column([
                    ft.Text(str(summary.get("nodesAtRisk", 0)), size=20, weight=ft.FontWeight.BOLD, color="#EF4444"),
                    ft.Text("<50%", size=10, color=self.colors.text_secondary)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
                expand=True
            ),
        ])

        # Legend
        legend = ft.Row([
            self._create_legend_item("< 50%", "#EF4444"),
            self._create_legend_item("50-80%", "#F59E0B"),
            self._create_legend_item("> 80%", "#10B981"),
        ], spacing=15)

        # Year/Quarter selector
        period_text = f"{self.year}" + (f" Q{self.quarter}" if self.quarter else " (Annual)")

        self.content_container.content = ft.Column([
            ft.Row([
                ft.Text(period_text, size=12, color=self.colors.text_secondary),
                ft.Container(expand=True),
                legend
            ]),
            ft.Divider(height=1),
            ft.Container(
                content=tiles_container,
                expand=True,
                padding=5
            ),
            ft.Divider(height=1),
            summary_row
        ], spacing=8, expand=True)

        self.page.update()

    def _create_legend_item(self, label, color):
        """Create a legend item"""
        return ft.Row([
            ft.Container(width=12, height=12, bgcolor=color, border_radius=2),
            ft.Text(label, size=10, color=self.colors.text_secondary)
        ], spacing=4)

    def _handle_drill_down(self, node):
        """Handle click on a coverage tile for drill-down"""
        if self.on_drill_down:
            context = {
                "type": "audit_coverage",
                "nodeId": node.get("id"),
                "nodeName": node.get("name"),
                "year": self.year,
                "quarter": self.quarter
            }
            self.on_drill_down(context)

    def refresh(self):
        """Refresh the widget data"""
        self.load_data()

    def set_period(self, year, quarter=None):
        """Update period and refresh"""
        self.year = year
        self.quarter = quarter
        self.refresh()
