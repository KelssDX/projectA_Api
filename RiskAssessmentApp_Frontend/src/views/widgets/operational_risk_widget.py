import flet as ft
from flet import Colors, Icons
from src.utils.theme import get_theme_colors

class OperationalRiskWidget(ft.Container):
    def __init__(self, page, report_client, reference_id=1):
        super().__init__()
        self.page = page
        self.client = report_client
        self.reference_id = reference_id
        self.padding = 20
        self.border_radius = 16
        self.bgcolor = ft.Colors.with_opacity(0.05, ft.Colors.DEEP_ORANGE)
        self.border = ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.GREY))
        
        self.content = self._build_loading()
        
    def _build_loading(self):
        return ft.Center(ft.ProgressRing())

    def load_data(self):
        if self.page:
            self.page.run_task(self._fetch_and_render)

    async def _fetch_and_render(self):
        try:
            # Fetch generic op risks
            data = await self.client.get_operational_risks(self.reference_id)
            
            if not data:
                self.content = self._build_empty_state()
            else:
                self.content = self._build_content(data)
            self.update()
        except Exception as e:
            self.content = ft.Text(f"Error loading Op Risk: {e}", color=Colors.RED)
            self.update()

    def _build_empty_state(self):
        return ft.Column([
            ft.Text("Operational Risk", size=20, weight="bold"),
            ft.Text("No data found for this assessment.")
        ])

    def _build_content(self, data):
        colors = get_theme_colors(self.page.theme_mode)
        
        # Calculate totals
        total_loss = sum(d.get('lossAmount', 0) for d in data)
        total_cumulative_var = sum(d.get('cumulativeVaR', 0) for d in data)
        
        # Header
        header = ft.Row([
            ft.Icon(Icons.WARNING_AMBER_ROUNDED, color=Colors.DEEP_ORANGE),
            ft.Text("Operational Risk Monitor", size=20, weight="bold", color=colors.text_primary),
            ft.Container(expand=True),
            ft.Chip(label=ft.Text(f"Total Events: {len(data)}"), bgcolor=Colors.DEEP_ORANGE_100)
        ])

        # Metrics
        metrics = ft.Row([
            self._metric_card("Total Potential Loss", f"${total_loss:,.0f}", "Sum of Loss Amounts", Colors.ORANGE),
            self._metric_card("Cumulative VaR", f"${total_cumulative_var:,.0f}", "Aggregation of Tail Risk", Colors.RED),
        ], spacing=20)

        # Top Risks Table
        # Columns: MainProcess, LossFrequency, VaR
        data_rows = []
        # Sort by worst CumulativeVaR (lowest negative number)
        sorted_data = sorted(data, key=lambda x: x.get('cumulativeVaR', 0))[:5]
        
        for item in sorted_data:
            data_rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(item.get('mainProcess', 'Unknown'))),
                    ft.DataCell(ft.Text(item.get('lossFrequency', '-'))),
                    ft.DataCell(ft.Text(f"{item.get('cumulativeVaR', 0):,.2f}", color=Colors.RED_700, weight="bold")),
                ])
            )

        table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Process")),
                ft.DataColumn(ft.Text("Frequency")),
                ft.DataColumn(ft.Text("Cumulative VaR")),
            ],
            rows=data_rows,
            border=ft.border.all(1, colors.border),
            border_radius=8,
            heading_row_color=colors.surface,
        )

        return ft.Column([
            header,
            ft.Divider(height=20, color=Colors.TRANSPARENT),
            metrics,
            ft.Divider(height=20, color=Colors.TRANSPARENT),
            ft.Text("Top High-Risk Processes", size=16, weight="bold"),
            table
        ])

    def _metric_card(self, title, value, subtitle, color):
        return ft.Container(
            content=ft.Column([
                ft.Text(title, size=12, color=ft.Colors.GREY),
                ft.Text(value, size=24, weight="bold", color=color),
                ft.Text(subtitle, size=10, color=ft.Colors.GREY_500)
            ], horizontal_alignment="center"),
            padding=15,
            bgcolor=ft.Colors.with_opacity(0.05, color),
            border_radius=8,
            border=ft.border.all(1, ft.Colors.with_opacity(0.2, color)),
            expand=True
        )
