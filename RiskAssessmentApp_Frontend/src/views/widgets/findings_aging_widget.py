import flet as ft
from flet import Icons
from src.api.auditing_client import AuditingAPIClient
from src.views.widgets.base_widget import BaseWidget


class FindingsAgingWidget(BaseWidget):
    """
    Open Findings Aging Analysis Widget
    Displays a horizontal stacked bar chart showing findings by severity and age
    """

    def __init__(self, page, reference_id=None, audit_universe_id=None, on_drill_down=None):
        super().__init__(
            page=page,
            title="Findings Aging Analysis",
            icon=Icons.HOURGLASS_EMPTY,
            description="Open findings grouped by age and severity"
        )
        self.reference_id = reference_id
        self.audit_universe_id = audit_universe_id
        self.on_drill_down = on_drill_down
        self.auditing_client = AuditingAPIClient()
        self.aging_data = None

    def build_content(self):
        """Build the widget content"""
        self.content_container = ft.Container(
            content=ft.Column([
                ft.ProgressRing(width=30, height=30),
                ft.Text("Loading findings aging data...", size=12)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            expand=True,
            alignment=ft.alignment.center
        )
        self.load_data()
        return self.content_container

    def load_data(self):
        """Load findings aging data"""
        if hasattr(self, 'page') and self.page:
            self.page.run_task(self._load_data_async)

    async def _load_data_async(self):
        """Async data loading"""
        try:
            self.aging_data = await self.auditing_client.get_findings_aging(
                reference_id=self.reference_id,
                audit_universe_id=self.audit_universe_id
            )
            self._update_display()
        except Exception as e:
            print(f"Error loading findings aging: {e}")
            self.content_container.content = ft.Text(f"Error: {str(e)}", color="red")
            self.page.update()

    def _update_display(self):
        """Update the widget display with loaded data"""
        if not self.aging_data:
            self.content_container.content = ft.Text("No data available", color=self.colors.text_secondary)
            self.page.update()
            return

        buckets = self.aging_data.get("agingBuckets", [])
        summary = self.aging_data.get("summary", {})

        if not buckets:
            self.content_container.content = ft.Column([
                ft.Icon(Icons.CHECK_CIRCLE, size=48, color="#10B981"),
                ft.Text("No open findings!", size=16, weight=ft.FontWeight.BOLD),
                ft.Text("All findings have been addressed", size=12, color=self.colors.text_secondary)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER, expand=True)
            self.page.update()
            return

        # Build the aging chart
        chart_rows = []

        # Age bucket headers
        header_row = ft.Row([
            ft.Container(width=80),  # Severity label space
            ft.Text("0-30d", size=10, width=60, text_align=ft.TextAlign.CENTER, color=self.colors.text_secondary),
            ft.Text("31-60d", size=10, width=60, text_align=ft.TextAlign.CENTER, color=self.colors.text_secondary),
            ft.Text("61-90d", size=10, width=60, text_align=ft.TextAlign.CENTER, color=self.colors.text_secondary),
            ft.Text("90+d", size=10, width=60, text_align=ft.TextAlign.CENTER, color=self.colors.text_secondary),
            ft.Text("Total", size=10, width=50, text_align=ft.TextAlign.CENTER, weight=ft.FontWeight.BOLD),
        ], spacing=5)
        chart_rows.append(header_row)

        # Build bars for each severity
        for bucket in buckets:
            severity = bucket.get("severity", "Unknown")
            severity_color = bucket.get("severityColor", "#6B7280")
            d0_30 = bucket.get("days0To30", 0)
            d31_60 = bucket.get("days31To60", 0)
            d61_90 = bucket.get("days61To90", 0)
            d90_plus = bucket.get("days90Plus", 0)
            total = bucket.get("totalOpen", 0)

            # Calculate max for scaling
            max_val = max(d0_30, d31_60, d61_90, d90_plus, 1)

            def create_bar_cell(value, max_v, color, age_bucket, sev):
                bar_width = (value / max_v) * 50 if max_v > 0 else 0
                return ft.Container(
                    width=60,
                    height=24,
                    content=ft.Stack([
                        ft.Container(
                            width=bar_width,
                            height=20,
                            bgcolor=color + "80",
                            border_radius=3,
                        ),
                        ft.Container(
                            content=ft.Text(str(value) if value > 0 else "", size=10, color=self.colors.text_primary),
                            alignment=ft.alignment.center,
                            width=60,
                            height=20
                        )
                    ]),
                    on_click=lambda e, s=sev, a=age_bucket: self._handle_drill_down(s, a) if value > 0 else None,
                    tooltip=f"{sev}: {value} findings ({age_bucket})"
                )

            row = ft.Row([
                ft.Container(
                    width=80,
                    content=ft.Row([
                        ft.Container(
                            width=10, height=10, bgcolor=severity_color, border_radius=5
                        ),
                        ft.Text(severity, size=11, weight=ft.FontWeight.BOLD, color=self.colors.text_primary),
                    ], spacing=5)
                ),
                create_bar_cell(d0_30, max_val, severity_color, "0-30 days", severity),
                create_bar_cell(d31_60, max_val, severity_color, "31-60 days", severity),
                create_bar_cell(d61_90, max_val, severity_color, "61-90 days", severity),
                create_bar_cell(d90_plus, max_val, "#EF4444", "90+ days", severity),  # Red for old findings
                ft.Container(
                    width=50,
                    content=ft.Text(str(total), size=12, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                )
            ], spacing=5)
            chart_rows.append(row)

        # Summary section
        summary_row = ft.Row([
            ft.Container(
                content=ft.Column([
                    ft.Text(str(summary.get("totalOpen", 0)), size=24, weight=ft.FontWeight.BOLD, color=self.colors.primary),
                    ft.Text("Open", size=10, color=self.colors.text_secondary)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
                expand=True
            ),
            ft.Container(
                content=ft.Column([
                    ft.Text(str(summary.get("totalOverdue", 0)), size=24, weight=ft.FontWeight.BOLD, color="#EF4444"),
                    ft.Text("Overdue", size=10, color=self.colors.text_secondary)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
                expand=True
            ),
            ft.Container(
                content=ft.Column([
                    ft.Text(f"{summary.get('averageAgeInDays', 0):.0f}d", size=24, weight=ft.FontWeight.BOLD, color=self.colors.text_primary),
                    ft.Text("Avg Age", size=10, color=self.colors.text_secondary)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
                expand=True
            ),
        ], spacing=10)

        self.content_container.content = ft.Column([
            ft.Container(
                content=ft.Column(chart_rows, spacing=8),
                padding=10,
            ),
            ft.Divider(height=1),
            ft.Container(
                content=summary_row,
                padding=10
            )
        ], spacing=5, expand=True)

        self.page.update()

    def _handle_drill_down(self, severity, age_bucket):
        """Handle click on a bar segment for drill-down"""
        if self.on_drill_down:
            context = {
                "type": "findings_aging",
                "severity": severity,
                "ageBucket": age_bucket,
                "referenceId": self.reference_id,
                "auditUniverseId": self.audit_universe_id
            }
            self.on_drill_down(context)

    def refresh(self):
        """Refresh the widget data"""
        self.load_data()

    def set_filters(self, reference_id=None, audit_universe_id=None):
        """Update filters and refresh"""
        self.reference_id = reference_id
        self.audit_universe_id = audit_universe_id
        self.refresh()
