import flet as ft
from flet import Icons
from src.api.auditing_client import AuditingAPIClient
from src.views.widgets.base_widget import BaseWidget


class ReasonabilityForecastWidget(BaseWidget):
    def __init__(self, page, reference_id=None, audit_universe_id=None, on_drill_down=None):
        super().__init__(
            page=page,
            title="Reasonability and Forecast Analytics",
            icon=Icons.TIMELINE,
            description="Compares actuals to expected, budget, or forecast values and flags significant variances"
        )
        self.reference_id = reference_id
        self.audit_universe_id = audit_universe_id
        self.on_drill_down = on_drill_down
        self.auditing_client = AuditingAPIClient()
        self.analytics = None
        self.is_wide = True

    def build_content(self):
        self.content_container = ft.Container(
            content=ft.Column(
                [ft.ProgressRing(width=30, height=30), ft.Text("Loading reasonability analytics...", size=12)],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            ),
            expand=True,
            alignment=ft.alignment.center
        )
        self.load_data()
        return self.content_container

    def load_data(self):
        if self.page:
            self.page.run_task(self._load_data_async)

    async def _load_data_async(self):
        try:
            self.analytics = await self.auditing_client.get_reasonability_forecast_analytics(reference_id=self.reference_id)
            self._update_display()
        except Exception as e:
            self.content_container.content = ft.Text(f"Error: {str(e)}", color="red")
            self.page.update()

    def _metric_card(self, label, value, color):
        return ft.Container(
            width=170,
            padding=12,
            bgcolor="#ffffff",
            border=ft.border.all(1, "#e6e9ed"),
            border_radius=10,
            content=ft.Column([
                ft.Text(label, size=11, color=self.colors.text_secondary),
                ft.Text(str(value), size=20, weight=ft.FontWeight.BOLD, color=color),
            ], spacing=4)
        )

    def _update_display(self):
        data = self.analytics or {}
        items = data.get("items", [])
        if not items:
            self.content_container.content = ft.Column([
                ft.Icon(Icons.SSID_CHART_OUTLINED, size=40, color=self.colors.text_secondary),
                ft.Text("No reasonability or forecast data available", size=14, weight=ft.FontWeight.BOLD),
                ft.Text(
                    "Load expected-versus-actual metrics into the Phase 5 staging tables to use this widget.",
                    size=12,
                    color=self.colors.text_secondary
                ),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER, expand=True)
            self.page.update()
            return

        summary = ft.Row([
            self._metric_card("Year", data.get("year", "N/A"), "#2563eb"),
            self._metric_card("Forecast Basis", data.get("forecastBasis", "Reasonability"), "#7c3aed"),
            self._metric_card("Flagged Variances", data.get("significantVarianceCount", 0), "#dc2626"),
            self._metric_card("Largest Variance", f"{data.get('largestVarianceAmount', 0):,.2f}", "#0f766e"),
        ], spacing=10, scroll=ft.ScrollMode.AUTO)

        rows = []
        for item in items[:6]:
            is_flagged = bool(item.get("isAboveThreshold", False))
            rows.append(
                ft.Container(
                    padding=10,
                    bgcolor="#ffffff",
                    border=ft.border.all(1, "#e6e9ed"),
                    border_radius=8,
                    content=ft.Column([
                        ft.Row([
                            ft.Text(item.get("metricName", "Metric"), size=12, weight=ft.FontWeight.BOLD),
                            ft.Container(expand=True),
                            ft.Container(
                                content=ft.Text("Investigate" if is_flagged else "Within threshold", size=10, color="white"),
                                bgcolor="#dc2626" if is_flagged else "#2563eb",
                                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                border_radius=10
                            )
                        ]),
                        ft.Text(
                            f"Category: {item.get('metricCategory', 'General')} | Basis: {item.get('forecastBasis', 'Reasonability')}",
                            size=11,
                            color=self.colors.text_secondary
                        ),
                        ft.Text(
                            f"Actual: {item.get('actualValue', 0):,.2f} | Expected: {item.get('expectedValue', 0):,.2f} | "
                            f"Variance: {item.get('varianceAmount', 0):,.2f}",
                            size=11,
                            color=self.colors.text_primary
                        ),
                        ft.Text(
                            f"Budget: {item.get('budgetValue', 'N/A')} | Prior year: {item.get('priorYearValue', 'N/A')} | "
                            f"Variance %: {item.get('variancePercent', 'N/A')}",
                            size=11,
                            color=self.colors.text_secondary
                        ),
                        ft.Text(
                            item.get("explanation") or "No explanation captured.",
                            size=11,
                            color=self.colors.text_secondary
                        )
                    ], spacing=5)
                )
            )

        self.content_container.content = ft.Column([
            summary,
            ft.Text(
                f"Materiality threshold: {data.get('materialityThreshold', 0):,.2f} | Metrics evaluated: {data.get('metricsEvaluated', 0)}",
                size=12,
                color=self.colors.text_secondary
            ),
            ft.Text(
                f"Threshold source: {data.get('materialityThresholdSource', 'Not Set')} | "
                f"Benchmark: {data.get('materialityBenchmarkSummary', 'No active benchmark')}",
                size=11,
                color=self.colors.text_secondary
            ),
            ft.Column(rows, spacing=8, scroll=ft.ScrollMode.AUTO),
        ], spacing=10, expand=True)
        self.page.update()

    def set_filters(self, reference_id=None, audit_universe_id=None):
        self.reference_id = reference_id
        self.audit_universe_id = audit_universe_id
        self.load_data()
