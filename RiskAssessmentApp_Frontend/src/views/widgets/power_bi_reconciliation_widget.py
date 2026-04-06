import flet as ft
from flet import Icons
from src.api.auditing_client import AuditingAPIClient
from src.views.widgets.base_widget import BaseWidget


class PowerBIReconciliationWidget(BaseWidget):
    def __init__(self, page, reference_id=None, audit_universe_id=None, on_drill_down=None):
        super().__init__(
            page=page,
            title="Power BI Reconciliation",
            icon=Icons.FACT_CHECK,
            description="Compares native audit metrics to the reporting data mart that Power BI consumes"
        )
        self.reference_id = reference_id
        self.audit_universe_id = audit_universe_id
        self.on_drill_down = on_drill_down
        self.auditing_client = AuditingAPIClient()
        self.reconciliation = None
        self.is_wide = True

    def build_content(self):
        self.content_container = ft.Container(
            content=ft.Column(
                [ft.ProgressRing(width=30, height=30), ft.Text("Loading Power BI reconciliation...", size=12)],
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
        if not self.reference_id:
            self.content_container.content = ft.Column([
                ft.Icon(Icons.FILTER_ALT_OFF, size=40, color=self.colors.text_secondary),
                ft.Text("Select an assessment to run reconciliation", size=14, weight=ft.FontWeight.BOLD),
                ft.Text(
                    "This widget compares native counts to the reporting data mart for the selected audit file.",
                    size=12,
                    color=self.colors.text_secondary
                ),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER, expand=True)
            self.page.update()
            return

        try:
            self.reconciliation = await self.auditing_client.get_power_bi_reconciliation(reference_id=self.reference_id)
            self._update_display()
        except Exception as e:
            self.content_container.content = ft.Text(f"Error: {str(e)}", color="red")
            self.page.update()

    def _summary_card(self, label, value, color):
        return ft.Container(
            width=160,
            padding=12,
            bgcolor="#ffffff",
            border=ft.border.all(1, "#e6e9ed"),
            border_radius=10,
            content=ft.Column([
                ft.Text(label, size=11, color=self.colors.text_secondary),
                ft.Text(str(value), size=20, weight=ft.FontWeight.BOLD, color=color),
            ], spacing=4)
        )

    @staticmethod
    def _format_metric(value):
        try:
            numeric = float(value or 0)
            return f"{numeric:,.0f}" if numeric.is_integer() else f"{numeric:,.2f}"
        except (TypeError, ValueError):
            return str(value or 0)

    def _update_display(self):
        data = self.reconciliation or {}
        metrics = data.get("metrics", [])
        if not metrics:
            self.content_container.content = ft.Column([
                ft.Icon(Icons.ANALYTICS_OUTLINED, size=40, color=self.colors.text_secondary),
                ft.Text("No reconciliation metrics available", size=14, weight=ft.FontWeight.BOLD),
                ft.Text(
                    "Apply the reporting data mart SQL and refresh the assessment context to compare Power BI counts.",
                    size=12,
                    color=self.colors.text_secondary
                ),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER, expand=True)
            self.page.update()
            return

        mismatches = [metric for metric in metrics if not metric.get("isMatched", False)]
        displayed_metrics = mismatches[:8] if mismatches else metrics[:6]

        summary = ft.Row([
            self._summary_card("Data Mart", data.get("dataMartStatus", "Unknown"), "#2563eb"),
            self._summary_card("Matched", data.get("matchedMetrics", 0), "#0f766e"),
            self._summary_card(
                "Mismatched",
                data.get("mismatchedMetrics", 0),
                "#dc2626" if data.get("mismatchedMetrics", 0) else "#0f766e"
            ),
            self._summary_card("Metrics", len(metrics), "#7c3aed"),
        ], spacing=10, scroll=ft.ScrollMode.AUTO)

        metric_rows = []
        for metric in displayed_metrics:
            matched_flag = bool(metric.get("isMatched", False))
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
                                content=ft.Text("Matched" if matched_flag else "Mismatch", size=10, color="white"),
                                bgcolor="#0f766e" if matched_flag else "#dc2626",
                                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                border_radius=10
                            )
                        ]),
                        ft.Text(
                            f"{metric.get('category', 'Reporting')} | Native {self._format_metric(metric.get('nativeValue'))} | "
                            f"Reporting {self._format_metric(metric.get('reportingValue'))}",
                            size=11,
                            color=self.colors.text_secondary
                        ),
                        ft.Text(
                            f"Variance {self._format_metric(metric.get('variance'))}",
                            size=11,
                            color="#0f766e" if matched_flag else "#dc2626"
                        )
                    ], spacing=4)
                )
            )

        footer = "All sampled metrics are aligned." if not mismatches else "Review mismatched metrics before relying on Power BI outputs."

        self.content_container.content = ft.Column([
            summary,
            ft.Text(
                f"Assessment reference {data.get('referenceId', self.reference_id)} | Generated {data.get('generatedAt', 'N/A')}",
                size=12,
                color=self.colors.text_secondary
            ),
            ft.Column(metric_rows, spacing=8, scroll=ft.ScrollMode.AUTO),
            ft.Text(footer, size=11, color=self.colors.text_secondary)
        ], spacing=10, expand=True)
        self.page.update()

    def set_filters(self, reference_id=None, audit_universe_id=None):
        self.reference_id = reference_id
        self.audit_universe_id = audit_universe_id
        self.load_data()
