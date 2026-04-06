import flet as ft
from flet import Icons
from src.api.auditing_client import AuditingAPIClient
from src.views.widgets.base_widget import BaseWidget


class JournalExceptionAnalyticsWidget(BaseWidget):
    def __init__(self, page, reference_id=None, audit_universe_id=None, on_drill_down=None):
        super().__init__(
            page=page,
            title="Journal Exception Analytics",
            icon=Icons.RECEIPT_LONG,
            description="Weekend, holiday, manual, and threshold-breach journal posting indicators"
        )
        self.reference_id = reference_id
        self.audit_universe_id = audit_universe_id
        self.on_drill_down = on_drill_down
        self.auditing_client = AuditingAPIClient()
        self.analytics = None

    def build_content(self):
        self.content_container = ft.Container(
            content=ft.Column(
                [ft.ProgressRing(width=30, height=30), ft.Text("Loading journal exceptions...", size=12)],
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
            self.analytics = await self.auditing_client.get_journal_exception_analytics(reference_id=self.reference_id)
            self._update_display()
        except Exception as e:
            self.content_container.content = ft.Text(f"Error: {str(e)}", color="red")
            self.page.update()

    def _metric(self, label, value, color):
        return ft.Container(
            width=125,
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
        if data.get("totalEntries", 0) <= 0:
            self.content_container.content = ft.Column([
                ft.Icon(Icons.SOURCE, size=40, color=self.colors.text_secondary),
                ft.Text("No staged journal data found", size=14, weight=ft.FontWeight.BOLD),
                ft.Text("Apply the Phase 5 analytics schema and load journal-entry data to use this widget.", size=12, color=self.colors.text_secondary),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER, expand=True)
            self.page.update()
            return

        metrics = ft.Row([
            self._metric("Total Entries", data.get("totalEntries", 0), "#1d4ed8"),
            self._metric("Weekend", data.get("weekendEntries", 0), "#f59e0b"),
            self._metric("Holiday", data.get("holidayEntries", 0), "#dc2626"),
            self._metric("Manual", data.get("manualEntries", 0), "#7c3aed"),
            self._metric("Weekend/Holiday", data.get("weekendOrHolidayEntries", 0), "#0f766e"),
        ], spacing=10, scroll=ft.ScrollMode.AUTO)

        insight_rows = [
            f"Round-amount entries: {data.get('roundAmountEntries', 0)}",
            f"Entries above planning threshold: {data.get('materialityBreaches', 0)}",
            f"Max journal value: {data.get('maxEntryAmount', 0):,.2f}",
            f"Weekend/holiday rate: {data.get('weekendHolidayRate', 0)}%",
        ]

        self.content_container.content = ft.Column([
            metrics,
            ft.Divider(height=1),
            ft.Text(f"Analytics year: {data.get('year', 'N/A')}", size=12, color=self.colors.text_secondary),
            ft.Text(
                f"Threshold source: {data.get('materialityThresholdSource', 'Not Set')} | "
                f"Benchmark: {data.get('materialityBenchmarkSummary', 'No active benchmark')}",
                size=11,
                color=self.colors.text_secondary
            ),
            ft.Column(
                [ft.Text(f"- {row}", size=12, color=self.colors.text_primary) for row in insight_rows],
                spacing=6
            )
        ], spacing=10, expand=True)
        self.page.update()

    def set_filters(self, reference_id=None, audit_universe_id=None):
        self.reference_id = reference_id
        self.audit_universe_id = audit_universe_id
        self.load_data()
