import flet as ft
from flet import Icons
from src.api.auditing_client import AuditingAPIClient
from src.views.widgets.base_widget import BaseWidget


class ManagementOverrideAnalyticsWidget(BaseWidget):
    def __init__(self, page, reference_id=None, audit_universe_id=None, on_drill_down=None):
        super().__init__(
            page=page,
            title="Management Override Indicators",
            icon=Icons.ADMIN_PANEL_SETTINGS,
            description="Manual, round-amount, period-end, and materiality-sensitive journals"
        )
        self.reference_id = reference_id
        self.audit_universe_id = audit_universe_id
        self.on_drill_down = on_drill_down
        self.auditing_client = AuditingAPIClient()
        self.analytics = None

    def build_content(self):
        self.content_container = ft.Container(
            content=ft.Column(
                [ft.ProgressRing(width=30, height=30), ft.Text("Loading override indicators...", size=12)],
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
            self.analytics = await self.auditing_client.get_management_override_analytics(reference_id=self.reference_id)
            self._update_display()
        except Exception as e:
            self.content_container.content = ft.Text(f"Error: {str(e)}", color="red")
            self.page.update()

    def _metric_card(self, label, value, color):
        return ft.Container(
            width=150,
            padding=12,
            bgcolor="#ffffff",
            border=ft.border.all(1, "#e6e9ed"),
            border_radius=10,
            content=ft.Column([
                ft.Text(label, size=11, color=self.colors.text_secondary),
                ft.Text(str(value), size=22, weight=ft.FontWeight.BOLD, color=color),
            ], spacing=4)
        )

    def _update_display(self):
        data = self.analytics or {}
        total_entries = data.get("totalEntries", 0)
        if total_entries <= 0:
            self.content_container.content = ft.Column([
                ft.Icon(Icons.DATA_THRESHOLDING, size=40, color=self.colors.text_secondary),
                ft.Text("No journal-entry analytics loaded", size=14, weight=ft.FontWeight.BOLD),
                ft.Text("Load journal-entry staging data to assess management-override indicators.", size=12, color=self.colors.text_secondary),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER, expand=True)
            self.page.update()
            return

        cards = ft.Row([
            self._metric_card("Manual", data.get("manualEntries", 0), "#2563eb"),
            self._metric_card("Round Amount", data.get("roundAmountEntries", 0), "#7c3aed"),
            self._metric_card("Period End", data.get("periodEndEntries", 0), "#f59e0b"),
            self._metric_card("Materiality", data.get("materialityBreaches", 0), "#dc2626"),
            self._metric_card("Top User Share", f"{data.get('topUserConcentrationRate', 0)}%", "#0f766e"),
        ], spacing=10, scroll=ft.ScrollMode.AUTO)

        self.content_container.content = ft.Column([
            cards,
            ft.Divider(height=1),
            ft.Text(
                f"Year {data.get('year', 'N/A')} | Manual rate {data.get('manualEntryRate', 0)}% | "
                f"Materiality threshold {data.get('materialityThreshold', 0):,.2f}",
                size=12,
                color=self.colors.text_secondary
            ),
            ft.Text(
                f"Threshold source: {data.get('materialityThresholdSource', 'Not Set')} | "
                f"Benchmark: {data.get('materialityBenchmarkSummary', 'No active benchmark')}",
                size=11,
                color=self.colors.text_secondary
            ),
            ft.Text(
                "Management override indicators focus on unusual manual entries, rounded postings, period-end activity, and entries exceeding planning thresholds.",
                size=11,
                color=self.colors.text_secondary
            )
        ], spacing=10, expand=True)
        self.page.update()

    def set_filters(self, reference_id=None, audit_universe_id=None):
        self.reference_id = reference_id
        self.audit_universe_id = audit_universe_id
        self.load_data()
