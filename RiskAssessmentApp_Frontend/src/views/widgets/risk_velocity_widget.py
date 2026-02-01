import flet as ft
from flet import Icons
import math
from src.api.auditing_client import AuditingAPIClient
from src.views.widgets.base_widget import BaseWidget


class RiskVelocityWidget(BaseWidget):
    """
    Risk Velocity Meter Widget
    Displays a gauge showing the speed of risk level changes
    Indicates if risks are increasing (bad) or decreasing (good)
    """

    def __init__(self, page, reference_id=None, audit_universe_id=None, on_drill_down=None):
        super().__init__(
            page=page,
            title="Risk Velocity",
            icon=Icons.SPEED,
            description="Rate of risk change"
        )
        self.reference_id = reference_id
        self.audit_universe_id = audit_universe_id
        self.on_drill_down = on_drill_down
        self.auditing_client = AuditingAPIClient()
        self.velocity_data = None

    def build_content(self):
        """Build the widget content"""
        self.content_container = ft.Container(
            content=ft.Column([
                ft.ProgressRing(width=30, height=30),
                ft.Text("Loading velocity data...", size=12)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            expand=True,
            alignment=ft.alignment.center
        )
        self.load_data()
        return self.content_container

    def load_data(self):
        """Load risk velocity data"""
        if hasattr(self, 'page') and self.page:
            self.page.run_task(self._load_data_async)

    async def _load_data_async(self):
        """Async data loading"""
        try:
            self.velocity_data = await self.auditing_client.get_risk_velocity(
                reference_id=self.reference_id,
                audit_universe_id=self.audit_universe_id
            )
            self._update_display()
        except Exception as e:
            print(f"Error loading risk velocity: {e}")
            self.content_container.content = ft.Text(f"Error: {str(e)}", color="red")
            self.page.update()

    def _update_display(self):
        """Update the widget display with loaded data"""
        if not self.velocity_data:
            self.content_container.content = ft.Text("No velocity data available", color=self.colors.text_secondary)
            self.page.update()
            return

        velocity_score = self.velocity_data.get("velocityScore", 0)  # -100 to +100
        net_change = self.velocity_data.get("netChange", 0)
        trend_indicator = self.velocity_data.get("trendIndicator", "stable")
        velocity_direction = self.velocity_data.get("velocityDirection", "stable")
        comparison_text = self.velocity_data.get("comparisonText", "")
        risks_added = self.velocity_data.get("risksAdded", 0)
        risks_closed = self.velocity_data.get("risksClosed", 0)
        risks_escalated = self.velocity_data.get("risksEscalated", 0)
        risks_deescalated = self.velocity_data.get("risksDeescalated", 0)

        # Determine colors based on trend
        if trend_indicator == "improving":
            main_color = "#10B981"  # Green
            bg_color = "#D1FAE5"
            icon = Icons.TRENDING_DOWN
        elif trend_indicator == "worsening":
            main_color = "#EF4444"  # Red
            bg_color = "#FEE2E2"
            icon = Icons.TRENDING_UP
        else:
            main_color = "#6B7280"  # Gray
            bg_color = "#F3F4F6"
            icon = Icons.TRENDING_FLAT

        # Build gauge visualization
        # Simple semi-circular gauge using stacked containers
        gauge_size = 140
        gauge_thickness = 12

        # Calculate needle position based on velocity score
        # -100 = full left (improving), +100 = full right (worsening), 0 = center
        # Map to angle: -100 -> 180°, 0 -> 90°, +100 -> 0°
        angle_deg = 90 - (velocity_score * 0.9)  # Map -100..100 to 180..0
        angle_rad = math.radians(angle_deg)

        # Create the gauge visual
        gauge = ft.Stack([
            # Background arc (gray)
            ft.Container(
                width=gauge_size,
                height=gauge_size // 2 + 10,
                content=ft.Stack([
                    # Green zone (left side - improving)
                    ft.Container(
                        width=gauge_size,
                        height=gauge_size // 2,
                        border_radius=ft.border_radius.only(
                            top_left=gauge_size // 2,
                            top_right=gauge_size // 2
                        ),
                        bgcolor="#10B98130",
                        clip_behavior=ft.ClipBehavior.HARD_EDGE,
                    ),
                    # Yellow zone (center)
                    ft.Container(
                        width=gauge_size * 0.7,
                        height=gauge_size // 2 * 0.7,
                        left=(gauge_size - gauge_size * 0.7) / 2,
                        top=(gauge_size // 2 - gauge_size // 2 * 0.7) / 2,
                        border_radius=ft.border_radius.only(
                            top_left=gauge_size // 2,
                            top_right=gauge_size // 2
                        ),
                        bgcolor="#F59E0B30",
                    ),
                    # Red zone indicator (right side - worsening)
                    ft.Container(
                        width=gauge_size * 0.4,
                        height=gauge_size // 2 * 0.4,
                        left=(gauge_size - gauge_size * 0.4) / 2,
                        top=(gauge_size // 2 - gauge_size // 2 * 0.4) / 2,
                        border_radius=ft.border_radius.only(
                            top_left=gauge_size // 2,
                            top_right=gauge_size // 2
                        ),
                        bgcolor="#EF444430",
                    ),
                    # Center cover
                    ft.Container(
                        width=gauge_size - gauge_thickness * 4,
                        height=(gauge_size - gauge_thickness * 4) // 2,
                        left=gauge_thickness * 2,
                        top=gauge_thickness * 2,
                        border_radius=ft.border_radius.only(
                            top_left=gauge_size // 2,
                            top_right=gauge_size // 2
                        ),
                        bgcolor=self.colors.card_bg,
                    ),
                    # Needle indicator
                    ft.Container(
                        width=6,
                        height=gauge_size // 2 - 15,
                        bgcolor=main_color,
                        border_radius=3,
                        left=gauge_size // 2 - 3,
                        top=15,
                        rotate=ft.Rotate(angle=-angle_rad + math.pi/2, alignment=ft.alignment.bottom_center),
                    ),
                    # Center dot
                    ft.Container(
                        width=16,
                        height=16,
                        bgcolor=main_color,
                        border_radius=8,
                        left=gauge_size // 2 - 8,
                        top=gauge_size // 2 - 8,
                    ),
                ])
            ),
        ])

        # Score display
        score_display = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(icon, size=24, color=main_color),
                    ft.Text(
                        f"{'+' if net_change > 0 else ''}{net_change}",
                        size=32,
                        weight=ft.FontWeight.BOLD,
                        color=main_color
                    ),
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=5),
                ft.Text(
                    trend_indicator.upper() if trend_indicator else "UNKNOWN",
                    size=12,
                    weight=ft.FontWeight.BOLD,
                    color=main_color
                ),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
            bgcolor=bg_color,
            padding=ft.padding.symmetric(horizontal=20, vertical=10),
            border_radius=8,
        )

        # Metrics row
        metrics_row = ft.Row([
            self._create_metric("Added", risks_added, "#EF4444"),
            self._create_metric("Closed", risks_closed, "#10B981"),
            self._create_metric("Escalated", risks_escalated, "#F59E0B"),
            self._create_metric("De-escalated", risks_deescalated, "#3B82F6"),
        ], spacing=5, alignment=ft.MainAxisAlignment.SPACE_EVENLY)

        # Comparison text
        comparison = ft.Text(
            comparison_text,
            size=11,
            color=self.colors.text_secondary,
            text_align=ft.TextAlign.CENTER
        )

        self.content_container.content = ft.Column([
            ft.Container(
                content=gauge,
                alignment=ft.alignment.center,
                height=gauge_size // 2 + 20
            ),
            score_display,
            ft.Divider(height=1),
            metrics_row,
            comparison,
        ], spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True)

        self.page.update()

    def _create_metric(self, label, value, color):
        """Create a metric display"""
        return ft.Container(
            content=ft.Column([
                ft.Text(str(value), size=16, weight=ft.FontWeight.BOLD, color=color),
                ft.Text(label, size=9, color=self.colors.text_secondary),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
            padding=5,
        )

    def refresh(self):
        """Refresh the widget data"""
        self.load_data()

    def set_filters(self, reference_id=None, audit_universe_id=None):
        """Update filters and refresh"""
        if reference_id is not None:
            self.reference_id = reference_id
        if audit_universe_id is not None:
            self.audit_universe_id = audit_universe_id
        self.refresh()
