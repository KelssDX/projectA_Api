import flet as ft
from flet import Colors
import asyncio
from src.views.widgets.base_widget import BaseAnalyticsWidget

class TopRisksWidget(BaseAnalyticsWidget):
    def __init__(self, page, client, ref_id, count=10):
        super().__init__(page, client, f"Top {count} Residual Risks")
        self.ref_id = ref_id
        self.count = count
        self.use_mock = False

    def load_data(self):
        self.page.run_task(self._fetch)

    async def _fetch(self):
        await asyncio.sleep(0.5)
        
        if self.ref_id is None and not self.use_mock:
            self.content_area.content = ft.Container(
                content=ft.Text("Select assessment context...", italic=True, size=12),
                alignment=ft.alignment.center
            )
            try: self.update()
            except: pass
            return

        self.show_loading()
        try:
            if self.use_mock:
                risks = await self.client.get_mock_top_risks()
                print(f"DEBUG: TopRisksWidget - Using MOCK data")
            else:
                print(f"DEBUG: TopRisksWidget fetching for ref_id: {self.ref_id}")
                raw_data = await self.client.get_top_risks(self.count, self.ref_id)
                print(f"DEBUG: TopRisksWidget raw_data type: {type(raw_data)}")
                # The API might be returning a wrapper or a direct list
                risks = raw_data.get("topResidualRisks", raw_data) if isinstance(raw_data, dict) else raw_data
                
            print(f"DEBUG: TopRisksWidget risks count: {len(risks) if risks else 0}")
            if not risks:
                self.content_area.content = ft.Text("No high risks found.", color=ft.Colors.GREEN)
                try: self.update()
                except: pass
                return

            if self.view_mode == "chart":
                self._render_chart(risks)
            else:
                self._render_table(risks)
            
            try: self.update()
            except: pass
        except Exception as e:
            print(f"DEBUG: TopRisksWidget Error: {e}")
            self.show_error(str(e))

    def _render_table(self, risks):
        rows = []
        for r in risks:
            # Map API response fields to columns. 
            # API returns OperationalRiskAssessmentDto: MainProcess, Source, VaR, LossAmount
            # Or the legacy structure?
            # The Repo uses `OperationalRiskAssessmentDto`.
            # Fields: MainProcess, Source, VaR, CumulativeVaR.
            
            # We want to show "Risk Title" (Process), "Source", "VaR" (as Score/Impact).
            # Note: VaR is negative (loss). Layout likely expects generic "Score".
            
            title = r.get("mainProcess") or r.get("MainProcess") or "Unknown"
            source = r.get("source") or r.get("Source") or "-"
            var_val = r.get("vaR") if "vaR" in r else r.get("VaR")
            
            # Formating Value
            score_str = f"{var_val:,.2f}" if var_val is not None else "0.00"
            
            rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(title, width=200, no_wrap=False)),
                    ft.DataCell(ft.Text(source)),
                    ft.DataCell(ft.Text(score_str, weight="bold", color="red")),
                ])
            )

        table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Business Process")),
                ft.DataColumn(ft.Text("Risk Source")),
                ft.DataColumn(ft.Text("VaR (95%)"), numeric=True),
            ],
            rows=rows,
            border=ft.border.all(1, self.colors.border),
            vertical_lines=ft.border.BorderSide(1, self.colors.border),
            heading_row_color=self.colors.surface,
            width=float("inf")
        )
        
        self.content_area.content = ft.Column([table], scroll=ft.ScrollMode.AUTO)

    def _render_chart(self, risks):
        # Render a horizontal bar chart of top risks by VaR
        bar_groups = []
        x_labels = []
        
        # Sort by VaR magnitude for chart
        sorted_risks = sorted(risks, key=lambda x: abs(x.get("vaR", x.get("VaR", 0))), reverse=True)[:5]
        
        for i, r in enumerate(sorted_risks):
            val = abs(r.get("vaR") if "vaR" in r else r.get("VaR", 0))
            title = r.get("mainProcess") or r.get("MainProcess") or "Unknown"
            
            bar_groups.append(
                ft.BarChartGroup(
                    x=i,
                    bar_rods=[ft.BarChartRod(from_y=0, to_y=val, color="#e74c3c", width=20, border_radius=4)],
                )
            )
            label = title[:15] + ".." if len(title) > 15 else title
            x_labels.append(ft.ChartAxisLabel(value=i, label=ft.Text(label, size=8, italic=True)))
            
        chart = ft.BarChart(
            bar_groups=bar_groups,
            bottom_axis=ft.ChartAxis(labels=x_labels),
            left_axis=ft.ChartAxis(title=ft.Text("VaR (Impact)", size=10)),
            expand=True,
            height=200
        )
        self.content_area.content = ft.Column([ft.Text("Top 5 Risks by Impact", size=12, weight="bold"), chart])
