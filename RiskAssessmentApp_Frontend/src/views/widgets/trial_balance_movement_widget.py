import flet as ft
from flet import Icons
from src.api.auditing_client import AuditingAPIClient
from src.views.widgets.base_widget import BaseWidget


class TrialBalanceMovementWidget(BaseWidget):
    def __init__(self, page, reference_id=None, audit_universe_id=None, on_drill_down=None):
        super().__init__(
            page=page,
            title="Trial Balance Movement",
            icon=Icons.SSID_CHART,
            description="Compares prior-year and current-year trial balance movements"
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
                [ft.ProgressRing(width=30, height=30), ft.Text("Loading TB movement analytics...", size=12)],
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
            self.analytics = await self.auditing_client.get_trial_balance_movement(reference_id=self.reference_id)
            self._update_display()
        except Exception as e:
            self.content_container.content = ft.Text(f"Error: {str(e)}", color="red")
            self.page.update()

    def _summary_card(self, label, value, color):
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
        accounts = data.get("accounts", [])
        if not accounts:
            self.content_container.content = ft.Column([
                ft.Icon(Icons.ACCOUNT_TREE_OUTLINED, size=40, color=self.colors.text_secondary),
                ft.Text("No trial balance snapshots available", size=14, weight=ft.FontWeight.BOLD),
                ft.Text("Load current-year and prior-year TB snapshots to compare movements.", size=12, color=self.colors.text_secondary),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER, expand=True)
            self.page.update()
            return

        summary = ft.Row([
            self._summary_card("Current Year", data.get("currentYear", "N/A"), "#2563eb"),
            self._summary_card("Prior Year", data.get("priorYear", "N/A"), "#64748b"),
            self._summary_card("Above Materiality", data.get("significantMovementsCount", 0), "#dc2626"),
            self._summary_card("Largest Movement", f"{data.get('largestMovementAmount', 0):,.2f}", "#0f766e"),
        ], spacing=10, scroll=ft.ScrollMode.AUTO)

        rows = []
        for account in accounts[:6]:
            is_material = bool(account.get("isAboveMateriality", False))
            rows.append(
                ft.Container(
                    padding=10,
                    bgcolor="#ffffff",
                    border=ft.border.all(1, "#e6e9ed"),
                    border_radius=8,
                    content=ft.Column([
                        ft.Row([
                            ft.Text(
                                f"{account.get('accountNumber', '')} - {account.get('accountName', 'Account')}",
                                size=12,
                                weight=ft.FontWeight.BOLD
                            ),
                            ft.Container(expand=True),
                            ft.Container(
                                content=ft.Text("Above materiality" if is_material else "Tracked", size=10, color="white"),
                                bgcolor="#dc2626" if is_material else "#2563eb",
                                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                border_radius=10
                            )
                        ]),
                        ft.Text(
                            f"FSLI: {account.get('fsli', 'Unmapped')} | Prior: {account.get('priorYearBalance', 0):,.2f} | "
                            f"Current: {account.get('currentYearBalance', 0):,.2f}",
                            size=11,
                            color=self.colors.text_secondary
                        ),
                        ft.Text(
                            f"Movement: {account.get('movementAmount', 0):,.2f} | "
                            f"Movement %: {account.get('movementPercent', 'N/A')}",
                            size=11,
                            color="#1f2937"
                        )
                    ], spacing=5)
                )
            )

        self.content_container.content = ft.Column([
            summary,
            ft.Text(
                f"Materiality threshold: {data.get('materialityThreshold', 0):,.2f}",
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
