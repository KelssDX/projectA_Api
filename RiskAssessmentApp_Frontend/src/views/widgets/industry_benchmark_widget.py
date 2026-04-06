import flet as ft
from flet import Icons
from src.api.auditing_client import AuditingAPIClient
from src.views.widgets.base_widget import BaseWidget


class IndustryBenchmarkWidget(BaseWidget):
    def __init__(self, page, reference_id=None, audit_universe_id=None, on_drill_down=None):
        super().__init__(
            page=page,
            title="Industry Benchmark Analytics",
            icon=Icons.QUERY_STATS,
            description="Compares key client metrics against industry benchmark medians and quartiles"
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
                [ft.ProgressRing(width=30, height=30), ft.Text("Loading benchmark analytics...", size=12)],
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
            self.analytics = await self.auditing_client.get_industry_benchmark_analytics(reference_id=self.reference_id)
            self._update_display()
        except Exception as e:
            self.content_container.content = ft.Text(f"Error: {str(e)}", color="red")
            self.page.update()

    def _summary_card(self, label, value, color):
        return ft.Container(
            width=165,
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
        metrics = data.get("metrics", [])
        if not metrics:
            self.content_container.content = ft.Column([
                ft.Icon(Icons.ANALYTICS_OUTLINED, size=40, color=self.colors.text_secondary),
                ft.Text("No industry benchmark data available", size=14, weight=ft.FontWeight.BOLD),
                ft.Text(
                    "Load benchmark metrics into the Phase 5 staging tables to compare client ratios to peer data.",
                    size=12,
                    color=self.colors.text_secondary
                ),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER, expand=True)
            self.page.update()
            return

        summary = ft.Row([
            self._summary_card("Year", data.get("year", "N/A"), "#2563eb"),
            self._summary_card("Metrics Compared", data.get("metricsCompared", 0), "#0f766e"),
            self._summary_card("Outside Range", data.get("outsideBenchmarkCount", 0), "#dc2626"),
            self._summary_card("Largest Variance", f"{data.get('largestVariancePercent', 0)}%", "#7c3aed"),
        ], spacing=10, scroll=ft.ScrollMode.AUTO)

        metric_rows = []
        for metric in metrics[:6]:
            is_outlier = bool(metric.get("isOutsideBenchmarkRange", False))
            lower_quartile = metric.get("benchmarkLowerQuartile")
            upper_quartile = metric.get("benchmarkUpperQuartile")
            metric_rows.append(
                ft.Container(
                    padding=10,
                    bgcolor="#ffffff",
                    border=ft.border.all(1, "#e6e9ed"),
                    border_radius=8,
                    content=ft.Column([
                        ft.Row([
                            ft.Text(metric.get("metricName", "Metric"), size=12, weight=ft.FontWeight.BOLD),
                            ft.Container(expand=True),
                            ft.Container(
                                content=ft.Text("Outside range" if is_outlier else "Within range", size=10, color="white"),
                                bgcolor="#dc2626" if is_outlier else "#2563eb",
                                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                border_radius=10
                            )
                        ]),
                        ft.Text(
                            f"Client: {metric.get('companyValue', 0):,.2f} {metric.get('unitOfMeasure', '')} | "
                            f"Median: {metric.get('benchmarkMedian', 0):,.2f}",
                            size=11,
                            color=self.colors.text_secondary
                        ),
                        ft.Text(
                            f"Range: {lower_quartile if lower_quartile is not None else 'N/A'} to "
                            f"{upper_quartile if upper_quartile is not None else 'N/A'} | "
                            f"Variance: {metric.get('variancePercent', 0)}%",
                            size=11,
                            color=self.colors.text_primary
                        ),
                        ft.Text(
                            f"Source: {metric.get('benchmarkSource', 'Benchmark dataset')}",
                            size=11,
                            color=self.colors.text_secondary
                        )
                    ], spacing=5)
                )
            )

        self.content_container.content = ft.Column([
            summary,
            ft.Text(
                f"Industry: {data.get('industryName', 'Industry Benchmark')} | Code: {data.get('industryCode', 'General')}",
                size=12,
                color=self.colors.text_secondary
            ),
            ft.Column(metric_rows, spacing=8, scroll=ft.ScrollMode.AUTO),
        ], spacing=10, expand=True)
        self.page.update()

    def set_filters(self, reference_id=None, audit_universe_id=None):
        self.reference_id = reference_id
        self.audit_universe_id = audit_universe_id
        self.load_data()
