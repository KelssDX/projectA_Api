import flet as ft
from src.api.auditing_client import AuditingAPIClient
from src.utils.theme import get_theme_colors

class OperationalRiskComponent(ft.Column):
    def __init__(self, page, current_user):
        super().__init__(expand=True, scroll=ft.ScrollMode.ADAPTIVE)
        self.page = page
        self.current_user = current_user
        self.client = AuditingAPIClient()
        
        self._build_ui()
        self.load_data()

    def _build_ui(self):
        colors = get_theme_colors(self.page.theme_mode)
        
        # Header with add button
        header = ft.Row([
            ft.Text("Operational Risk Incidents", size=20, weight="bold", color=colors.text_primary),
            ft.Container(expand=True),
            ft.FilledButton("Add New Loss Event", icon=ft.Icons.ADD)
        ])
        
        # Table
        self.table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Main Process")),
                ft.DataColumn(ft.Text("Source")),
                ft.DataColumn(ft.Text("Frequency")),
                ft.DataColumn(ft.Text("Count", tooltip="Loss Event Count"), numeric=True),
                ft.DataColumn(ft.Text("Prob %", tooltip="Probability"), numeric=True),
                ft.DataColumn(ft.Text("Loss Amount"), numeric=True),
                ft.DataColumn(ft.Text("VaR (Op)"), numeric=True),
                ft.DataColumn(ft.Text("Cum. VaR"), numeric=True),
            ],
            rows=[],
            border=ft.border.all(1, colors.border),
            vertical_lines=ft.border.BorderSide(1, colors.border),
            horizontal_lines=ft.border.BorderSide(1, colors.border),
            heading_row_color=colors.surface,
            width=float("inf") # Allow horizontal scroll
        )
        
        # Wrap table in container for styling
        table_container = ft.Container(
            content=self.table, # Table handles its own scroll or column does
            border=ft.border.all(1, colors.border),
            border_radius=10,
            padding=10
        )
        
        self.controls = [
            ft.Container(height=20),
            header,
            ft.Divider(color=ft.Colors.TRANSPARENT, height=10),
            table_container
        ]

    def load_data(self):
        if self.page:
            self.page.run_task(self._fetch_data)
        
    async def _fetch_data(self):
        try:
            # Hardcoded reference ID for demo, or pass it in
            data = await self.client.get_operational_risks(1)
            
            self.table.rows.clear()
            if data:
                for item in data:
                    self.table.rows.append(
                        ft.DataRow(cells=[
                            ft.DataCell(ft.Text(item.get('mainProcess', ''))),
                            ft.DataCell(ft.Text(item.get('source', ''))),
                            ft.DataCell(ft.Text(item.get('lossFrequency', ''))),
                            ft.DataCell(ft.Text(str(item.get('lossEventCount', 0)))),
                            ft.DataCell(ft.Text(f"{item.get('probability', 0):.4f}")),
                            ft.DataCell(ft.Text(f"{item.get('lossAmount', 0):,.2f}")),
                            ft.DataCell(ft.Text(f"{item.get('vaR', 0):,.2f}")),
                            ft.DataCell(ft.Text(f"{item.get('cumulativeVaR', 0):,.2f}", color=ft.Colors.RED)),
                        ])
                    )
            else:
                self.table.rows.append(ft.DataRow(cells=[ft.DataCell(ft.Text("No records found"))] * 8))
                
            self.update()
        except Exception as e:
            print(f"Error loading Op Risk: {e}")
            self.table.rows.append(ft.DataRow(cells=[ft.DataCell(ft.Text(f"Error: {e}"))] * 8))
            self.update()
