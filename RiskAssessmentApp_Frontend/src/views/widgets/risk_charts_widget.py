import flet as ft
import asyncio
from flet import Colors
from src.utils.theme import get_theme_colors
from src.views.widgets.base_widget import BaseAnalyticsWidget

# Helper for case-insensitive lookup
def get_val(d, *keys, default=None):
    for k in keys:
        if k in d:
            return d[k]
    return default

class InherentVsResidualWidget(BaseAnalyticsWidget):
    def __init__(self, page, client, ref_id):
        super().__init__(page, client, "Inherent vs Residual Risk")
        self.ref_id = ref_id
        self.ref_id = ref_id
        # self.use_mock = False # Removed
        self.is_wide = True # Layout hint

    def load_data(self):
        self.page.run_task(self._fetch)

    async def _fetch(self):
        # Wait for mount
        await asyncio.sleep(0.5)
        
        if self.ref_id is None:
            self.content_area.content = ft.Container(
                content=ft.Text("Please select an assessment to view analytics...", italic=True, color=ft.Colors.GREY_500),
                alignment=ft.alignment.center,
                expand=True
            )
            try: self.update()
            except: pass
            return

        self.show_loading()
        try:
            raw_data = await self.client.get_analytical_report(self.ref_id)
            print(f"DEBUG: {self.__class__.__name__} raw_data keys: {raw_data.keys() if raw_data else 'None'}")
            # Normalize nesting: Real API nests under 'baseReport'
            data = get_val(raw_data, "baseReport", "BaseReport", default=raw_data) if raw_data else {}
            
            risk_reduction = get_val(data, "riskReduction", "RiskReduction")
            print(f"DEBUG: {self.__class__.__name__} risk_reduction sample: {risk_reduction[:2] if risk_reduction else 'None'}")
            
            if not data or not risk_reduction:
                print(f"DEBUG: {self.__class__.__name__} - No data available")
                self.content_area.content = ft.Text("No data available")
                try: self.update()
                except: pass
                return

            if self.view_mode == "table":
                self._render_table(risk_reduction)
            else:
                self._render_chart(risk_reduction)
            
            try: self.update()
            except: pass
        except Exception as e:
            print(f"DEBUG: {self.__class__.__name__} Error: {e}")
            self.show_error(str(e))

    def _render_chart(self, comparisons):
        level_order = ["Critical", "High", "Medium", "Low", "Very Low"]
        # Map by level, being careful of casing if Level comes back different
        comp_map = {}
        for item in comparisons:
            lvl = get_val(item, "level", "Level", default="Unknown")
            comp_map[lvl] = item
        
        print(f"DEBUG: InherentWidget comp_map keys: {comp_map.keys()}")
            
        bar_groups = []
        x_labels = []

        for i, level in enumerate(level_order):
            # Default to dict if missing, so we get 0s
            data = comp_map.get(level, {})
            inherent = get_val(data, "inherentCount", "InherentCount", default=0)
            residual = get_val(data, "residualCount", "ResidualCount", default=0)
            
            bar_groups.append(
                ft.BarChartGroup(
                    x=i,
                    bar_rods=[
                        ft.BarChartRod(from_y=0, to_y=inherent, width=12, color="#e74c3c", tooltip=f"Inherent: {inherent}", border_radius=2),
                        ft.BarChartRod(from_y=0, to_y=residual, width=12, color="#3498db", tooltip=f"Residual: {residual}", border_radius=2),
                    ],
                )
            )
            x_labels.append(ft.ChartAxisLabel(value=i, label=ft.Text(level[:3], size=10)))

        chart = ft.BarChart(
            bar_groups=bar_groups,
            bottom_axis=ft.ChartAxis(labels=x_labels),
            left_axis=ft.ChartAxis(),
            border=ft.border.all(1, self.colors.border),
            tooltip_bgcolor=self.colors.surface,
            expand=True,
            height=200
        )
        self.content_area.content = chart

    def _render_table(self, comparisons):
        rows = []
        for c in comparisons:
            lvl = get_val(c, "level", "Level", default="")
            inherent = get_val(c, "inherentCount", "InherentCount", default=0)
            residual = get_val(c, "residualCount", "ResidualCount", default=0)
            
            rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(lvl)),
                ft.DataCell(ft.Text(str(inherent), weight="bold", color="red")),
                ft.DataCell(ft.Text(str(residual), weight="bold", color="green")),
            ]))
            
        self.content_area.content = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Risk Level")),
                ft.DataColumn(ft.Text("Inherent", numeric=True)),
                ft.DataColumn(ft.Text("Residual", numeric=True)),
            ],
            rows=rows,
            border=ft.border.all(1, self.colors.border),
            heading_row_color=self.colors.surface,
            width=float("inf")
        )

class RiskCategoryDistributionWidget(BaseAnalyticsWidget):
    def __init__(self, page, client, ref_id):
        super().__init__(page, client, "Risk Categories")
        self.ref_id = ref_id
        self.ref_id = ref_id
        # self.use_mock = False # Removed

    def load_data(self):
        self.page.run_task(self._fetch)

    async def _fetch(self):
        await asyncio.sleep(0.5)
        
        if self.ref_id is None:
            self.content_area.content = ft.Container(
                content=ft.Text("Select assessment context...", italic=True, size=12),
                alignment=ft.alignment.center
            )
            try: self.update()
            except: pass
            return

        self.show_loading()
        try:
            raw_data = await self.client.get_analytical_report(self.ref_id)
            print(f"DEBUG: {self.__class__.__name__} raw_data keys: {raw_data.keys() if raw_data else 'None'}")
            data = get_val(raw_data, "baseReport", "BaseReport", default=raw_data) if raw_data else {}
                
            cat_dist = get_val(data, "categoryDistribution", "CategoryDistribution")
            print(f"DEBUG: {self.__class__.__name__} cat_dist: {cat_dist}")
            
            if not data or not cat_dist:
                print(f"DEBUG: {self.__class__.__name__} - No data available")
                self.content_area.content = ft.Text("No data")
                try: self.update()
                except: pass
                return
            
            if self.view_mode == "table":
                self._render_table(cat_dist)
            else:
                self._render_chart(cat_dist)
            
            try: self.update()
            except: pass
        except Exception as e:
            print(f"DEBUG: {self.__class__.__name__} Error: {e}")
            self.show_error(str(e))

    def _render_chart(self, categories):
        sections = []
        palette = ["#2ecc71", "#3498db", "#9b59b6", "#e67e22", "#f1c40f", "#e74c3c"]
        for i, cat in enumerate(categories):
            count = get_val(cat, "count", "Count", default=0)
            name = get_val(cat, "categoryName", "CategoryName", default="Unknown")
            
            sections.append(
                ft.PieChartSection(value=count, title=str(count), color=palette[i % len(palette)], radius=40)
            )
        
        # Legend
        legend_items = []
        for i, cat in enumerate(categories):
            name = get_val(cat, "categoryName", "CategoryName", default="Unknown")
            legend_items.append(ft.Row([
                ft.Container(width=10, height=10, bgcolor=palette[i % len(palette)]), 
                ft.Text(name, size=10)
            ]))
        
        self.content_area.content = ft.Row([
            ft.PieChart(sections=sections, sections_space=2, center_space_radius=20, width=150, height=150),
            ft.Column(legend_items, scroll=ft.ScrollMode.AUTO, height=150)
        ])

    def _render_table(self, categories):
        rows = []
        for c in categories:
            name = get_val(c, "categoryName", "CategoryName", default="Unknown")
            count = get_val(c, "count", "Count", default=0)
            avg = get_val(c, "averageScore", "AverageScore", default=0)
            
            rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(name)),
                ft.DataCell(ft.Text(str(count), weight="bold")),
                ft.DataCell(ft.Text(f"{avg:.1f}")),
            ]))
            
        self.content_area.content = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Category")),
                ft.DataColumn(ft.Text("Count", numeric=True)),
                ft.DataColumn(ft.Text("Avg Score", numeric=True)),
            ],
            rows=rows,
            border=ft.border.all(1, self.colors.border),
            heading_row_color=self.colors.surface,
            width=float("inf")
        )

class ControlCoverageWidget(BaseAnalyticsWidget):
    def __init__(self, page, client, ref_id):
        super().__init__(page, client, "Control Coverage")
        self.ref_id = ref_id
        self.ref_id = ref_id
        # self.use_mock = False # Removed

    def load_data(self):
        self.page.run_task(self._fetch)

    async def _fetch(self):
        await asyncio.sleep(0.5)
        
        if self.ref_id is None:
            self.content_area.content = ft.Container(
                content=ft.Text("Wait for context selection...", italic=True, size=12),
                alignment=ft.alignment.center
            )
            try: self.update()
            except: pass
            return

        self.show_loading()
        try:
            raw_data = await self.client.get_analytical_report(self.ref_id)
            print(f"DEBUG: {self.__class__.__name__} raw_data keys: {raw_data.keys() if raw_data else 'None'}")
            # Control stats are usually at top level or in baseReport
            base = get_val(raw_data, "baseReport", "BaseReport", default={})
            data = raw_data if "controlStats" in raw_data or "ControlStats" in raw_data else base
                
            stats = get_val(data, "controlStats", "ControlStats", default=[])
            print(f"DEBUG: {self.__class__.__name__} stats count: {len(stats) if stats else 0}")
            
            # Find coverage stat
            # Check safely for statType/StatType
            coverage = None
            for s in stats:
                sType = get_val(s, "statType", "StatType")
                if sType == "Coverage":
                    coverage = s
                    break
            
            val = get_val(coverage, "value", "Value", default="0%") if coverage else "0%"
            
            if self.view_mode == "table":
                self._render_table(stats)
            else:
                self._render_chart(val, coverage)
            
            try: self.update()
            except: pass
        except Exception as e:
            print(f"DEBUG: {self.__class__.__name__} Error: {e}")
            self.show_error(str(e))

    def _render_chart(self, val, coverage):
        desc = get_val(coverage, "description", "Description", default="") if coverage else ""
        
        try:
            pct = int(str(val).replace('%', '').strip())
        except:
            pct = 0
            
        self.content_area.content = ft.Column([
            ft.Stack([
                ft.PieChart(
                    sections=[
                        ft.PieChartSection(value=pct, color="#2ecc71", radius=10),
                        ft.PieChartSection(value=100-pct, color=self.colors.border, radius=10)
                    ],
                    sections_space=0, center_space_radius=40, start_degree_offset=180, width=100, height=100
                ),
                ft.Container(content=ft.Text(val, size=20, weight="bold"), alignment=ft.alignment.center, width=100, height=100)
            ]),
            ft.Text(desc, size=10, color=ft.Colors.GREY)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    def _render_table(self, stats):
        rows = []
        for s in stats:
            sType = get_val(s, "statType", "StatType", default="")
            val = get_val(s, "value", "Value", default="")
            desc = get_val(s, "description", "Description", default="")
            
            rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(sType)),
                ft.DataCell(ft.Text(val, weight="bold")),
                ft.DataCell(ft.Text(desc)),
            ]))
            
        self.content_area.content = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Metric")),
                ft.DataColumn(ft.Text("Value")),
                ft.DataColumn(ft.Text("Description")),
            ],
            rows=rows,
            border=ft.border.all(1, self.colors.border),
            heading_row_color=self.colors.surface,
            width=float("inf")
        )
