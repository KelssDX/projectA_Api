import flet as ft
from flet import Icons
from src.api.auditing_client import AuditingAPIClient
from src.views.widgets.base_widget import BaseWidget


class RiskTrendWidget(BaseWidget):
    """
    Risk Trend Analysis Widget
    Shows risk level changes over time with trend indicators
    """

    def __init__(self, page, reference_id=None, audit_universe_id=None, months=12, on_drill_down=None):
        super().__init__(
            page=page,
            title="Risk Trend Analysis",
            icon=Icons.TRENDING_UP,
            description="Risk level changes over time"
        )
        self.reference_id = reference_id
        self.audit_universe_id = audit_universe_id
        self.months = months
        self.on_drill_down = on_drill_down
        self.auditing_client = AuditingAPIClient()
        self.trend_data = None

    def build_content(self):
        """Build the widget content"""
        self.content_container = ft.Container(
            content=ft.Column([
                ft.ProgressRing(width=30, height=30),
                ft.Text("Loading risk trend data...", size=12)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            expand=True,
            alignment=ft.alignment.center
        )
        self.load_data()
        return self.content_container

    def load_data(self):
        """Load risk trend data"""
        if hasattr(self, 'page') and self.page:
            self.page.run_task(self._load_data_async)

    async def _load_data_async(self):
        """Async data loading"""
        try:
            self.trend_data = await self.auditing_client.get_risk_trend(
                reference_id=self.reference_id,
                audit_universe_id=self.audit_universe_id,
                months=self.months
            )
            self._update_display()
        except Exception as e:
            print(f"Error loading risk trend: {e}")
            self.content_container.content = ft.Text(f"Error: {str(e)}", color="red")
            self.page.update()

    def _update_display(self):
        """Update the widget display with loaded data"""
        if not self.trend_data:
            self.content_container.content = ft.Text("No trend data available", color=self.colors.text_secondary)
            self.page.update()
            return

        data_points = self.trend_data.get("dataPoints", [])
        summary = self.trend_data.get("summary", {})

        if not data_points:
            self.content_container.content = ft.Column([
                ft.Icon(Icons.SHOW_CHART, size=48, color=self.colors.text_secondary),
                ft.Text("No trend data available", size=14),
                ft.Text("Trend data will appear after multiple assessment periods", size=12, color=self.colors.text_secondary)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER, expand=True)
            self.page.update()
            return

        # Build mini chart visualization
        # We'll create a simple line chart using containers

        # Find max value for scaling
        all_values = []
        for dp in data_points:
            all_values.extend([
                dp.get("criticalCount", 0),
                dp.get("highCount", 0),
                dp.get("mediumCount", 0),
                dp.get("lowCount", 0)
            ])
        max_val = max(all_values) if all_values else 1

        chart_height = 120
        chart_width = min(len(data_points) * 40, 300)

        # Colors for each risk level
        level_colors = {
            "critical": "#DC2626",
            "high": "#EA580C",
            "medium": "#CA8A04",
            "low": "#16A34A"
        }

        # Create stacked bar chart
        bars = []
        for i, dp in enumerate(data_points[-8:]):  # Show last 8 data points
            critical = dp.get("criticalCount", 0)
            high = dp.get("highCount", 0)
            medium = dp.get("mediumCount", 0)
            low = dp.get("lowCount", 0)
            total = critical + high + medium + low

            # Calculate heights proportionally
            scale = (chart_height - 20) / max_val if max_val > 0 else 0

            bar_stack = ft.Column([
                # Bars stacked from bottom to top
                ft.Container(height=low * scale, width=30, bgcolor=level_colors["low"], border_radius=ft.border_radius.only(top_left=3, top_right=3) if critical + high + medium == 0 else 0),
                ft.Container(height=medium * scale, width=30, bgcolor=level_colors["medium"]),
                ft.Container(height=high * scale, width=30, bgcolor=level_colors["high"]),
                ft.Container(height=critical * scale, width=30, bgcolor=level_colors["critical"], border_radius=ft.border_radius.only(top_left=3, top_right=3)),
            ], spacing=0, alignment=ft.MainAxisAlignment.END)

            bar_container = ft.Container(
                content=ft.Column([
                    bar_stack,
                    ft.Text(dp.get("periodLabel", "")[:3], size=8, color=self.colors.text_secondary, text_align=ft.TextAlign.CENTER),
                ], spacing=2, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                height=chart_height,
                width=35,
                alignment=ft.alignment.bottom_center,
                on_click=lambda e, d=dp: self._handle_drill_down(d),
                tooltip=f"{dp.get('periodLabel', '')}: {total} total risks"
            )
            bars.append(bar_container)

        chart = ft.Row(bars, spacing=5, alignment=ft.MainAxisAlignment.CENTER)

        # Legend
        legend = ft.Row([
            self._create_legend_item("Critical", level_colors["critical"]),
            self._create_legend_item("High", level_colors["high"]),
            self._create_legend_item("Medium", level_colors["medium"]),
            self._create_legend_item("Low", level_colors["low"]),
        ], spacing=15, wrap=True)

        # Trend summary
        trend_direction = summary.get("trendDirection", "stable")
        change_count = summary.get("changeCount", 0)

        trend_icon = Icons.TRENDING_UP if trend_direction == "worsening" else (Icons.TRENDING_DOWN if trend_direction == "improving" else Icons.TRENDING_FLAT)
        trend_color = "#EF4444" if trend_direction == "worsening" else ("#10B981" if trend_direction == "improving" else self.colors.text_secondary)

        trend_summary = ft.Row([
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(trend_icon, size=20, color=trend_color),
                        ft.Text(trend_direction.title(), size=14, weight=ft.FontWeight.BOLD, color=trend_color),
                    ], spacing=5),
                    ft.Text(f"{'+' if change_count > 0 else ''}{change_count} risks", size=12, color=self.colors.text_secondary)
                ], spacing=2),
                expand=True
            ),
            ft.Container(
                content=ft.Column([
                    ft.Text(str(summary.get("currentTotal", 0)), size=24, weight=ft.FontWeight.BOLD, color=self.colors.primary),
                    ft.Text("Current Total", size=10, color=self.colors.text_secondary)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
            ),
        ])

        self.content_container.content = ft.Column([
            ft.Container(content=chart, padding=ft.padding.only(top=10, bottom=5)),
            ft.Container(content=legend, padding=ft.padding.symmetric(vertical=5)),
            ft.Divider(height=1),
            ft.Container(content=trend_summary, padding=10)
        ], spacing=5, expand=True)

        self.page.update()

    def _create_legend_item(self, label, color):
        """Create a legend item"""
        return ft.Row([
            ft.Container(width=12, height=12, bgcolor=color, border_radius=2),
            ft.Text(label, size=10, color=self.colors.text_secondary)
        ], spacing=4)

    def _handle_drill_down(self, data_point):
        """Handle click on a data point for drill-down"""
        if self.on_drill_down:
            context = {
                "type": "risk_trend",
                "period": data_point.get("periodLabel"),
                "date": str(data_point.get("date")),
                "referenceId": self.reference_id,
                "auditUniverseId": self.audit_universe_id
            }
            self.on_drill_down(context)

    def refresh(self):
        """Refresh the widget data"""
        self.load_data()

    def set_filters(self, reference_id=None, audit_universe_id=None, months=None):
        """Update filters and refresh"""
        if reference_id is not None:
            self.reference_id = reference_id
        if audit_universe_id is not None:
            self.audit_universe_id = audit_universe_id
        if months is not None:
            self.months = months
        self.refresh()
