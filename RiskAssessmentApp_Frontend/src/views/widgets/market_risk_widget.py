import flet as ft
import asyncio
from flet import Colors, Icons
from src.utils.theme import get_theme_colors
from src.views.widgets.base_widget import BaseAnalyticsWidget

class MarketRiskWidget(BaseAnalyticsWidget):
    def __init__(self, page, report_client, ref_id, symbol="SHARE_A"):
        super().__init__(page, report_client, f"Market Risk Analysis: {symbol}")
        self.ref_id = ref_id
        self.symbol = symbol
        self.use_mock = False
        self.is_wide = True # Layout hint
        
    def load_data(self):
        self.page.run_task(self._fetch_and_render)

    async def _fetch_and_render(self):
        await asyncio.sleep(0.5)
        
        if self.ref_id is None and not self.use_mock:
            self.content_area.content = ft.Container(
                content=ft.Text("Select assessment context...", italic=True, size=12),
                alignment=ft.alignment.center,
                expand=True
            )
            try: self.update()
            except: pass
            return

        self.show_loading()
        try:
            if self.use_mock:
                print(f"DEBUG: MarketRiskWidget - Using MOCK data")
                price_data = await self.client.get_mock_market_data()
                metrics = await self.client.get_mock_market_metrics()
            else:
                # 1. Trigger Seed (just in case)
                await self.client.seed_market_data()
                
                # 2. Fetch Data
                price_data = await self.client.get_share_price_data(self.symbol)
                metrics = await self.client.calculate_risk_metrics(self.symbol)
                print(f"DEBUG: MarketRiskWidget price_data count: {len(price_data) if price_data else 0}, metrics: {metrics.keys() if metrics else 'None'}")
            
            if not price_data or not metrics:
                print(f"DEBUG: MarketRiskWidget - No data available")
                self.content_area.content = ft.Text("No data available for Market Risk", color=Colors.RED)
                try: self.update()
                except: pass
                return

            if self.view_mode == "table":
                self._render_table(price_data, metrics)
            else:
                self._build_content(price_data, metrics)
            
            try: self.update()
            except: pass
            
        except Exception as e:
            print(f"DEBUG: MarketRiskWidget Error: {e}")
            self.show_error(str(e))

    def _build_content(self, price_data, metrics):
        theme_mode = self.page.theme_mode if self.page else ft.ThemeMode.LIGHT
        colors = get_theme_colors(theme_mode)
        
        # Helper for case-insensitive key access (C# PascalCase vs Python camelCase)
        def get_val(d, *keys, default=0):
            for k in keys:
                if k in d:
                    return d[k]
            return default
        
        # --- 1. Metrics Cards ---
        var_val = get_val(metrics, "vaR95", "VaR95", default=0)
        cvar_val = get_val(metrics, "cVaR95", "CVaR95", default=0)
        vol_val = get_val(metrics, "volatility", "Volatility", default=0)
        
        var_color = Colors.RED if var_val < -0.02 else Colors.ORANGE
        cvar_color = Colors.RED_900 if cvar_val < -0.04 else Colors.RED
        
        cards = ft.Row([
            self._metric_card("VaR (95%)", f"{var_val:.2%}", "Value at Risk", var_color),
            self._metric_card("CVaR (95%)", f"{cvar_val:.2%}", "Expected Shortfall", cvar_color),
            self._metric_card("Volatility", f"{vol_val:.2%}", "Daily Std Dev", Colors.BLUE),
        ], spacing=20)

        # --- 2. Share Price Chart ---
        points = []
        recent_data = price_data[-100:]
        
        def get_price(d):
            return d.get('closePrice') or d.get('ClosePrice') or 0
        def get_date(d):
            val = d.get('date') or d.get('Date') or ''
            return str(val)[:10] if val else ''
        
        min_p = min([get_price(d) for d in recent_data]) if recent_data else 0
        max_p = max([get_price(d) for d in recent_data]) if recent_data else 100
        
        for i, d in enumerate(recent_data):
            price = get_price(d)
            date_str = get_date(d)
            points.append(ft.LineChartDataPoint(i, price, tooltip=f"{date_str}: {price}"))


        chart = ft.LineChart(
            data_series=[
                ft.LineChartData(
                    data_points=points,
                    stroke_width=2,
                    color=colors.primary,
                    curved=True,
                    stroke_cap_round=True,
                    below_line_bgcolor=ft.Colors.with_opacity(0.1, colors.primary),
                )
            ],
            min_y=min_p * 0.95,
            max_y=max_p * 1.05,
            min_x=0,
            max_x=len(recent_data),
            tooltip_bgcolor=colors.surface,
            left_axis=ft.ChartAxis(),
            bottom_axis=ft.ChartAxis(labels_size=0)
        )

        self.content_area.content = ft.Column([
            ft.Chip(label=ft.Text("95% Confidence"), bgcolor=colors.primary_container),
            ft.Divider(height=10, color=Colors.TRANSPARENT),
            cards,
            ft.Divider(height=20, color=Colors.TRANSPARENT),
            ft.Text("Share Price History (Last 100 Days)", size=14, color=colors.text_secondary),
            ft.Container(content=chart, height=200, padding=10, border=ft.border.all(1, colors.border), border_radius=8)
        ])

    def _render_table(self, price_data, metrics):
        # Show price history in a table
        recent = price_data[-20:] # Show last 20 for brevity
        rows = [
            ft.DataRow(cells=[
                ft.DataCell(ft.Text(p.get("date", p.get("Date", ""))[:10])),
                ft.DataCell(ft.Text(f"{p.get('closePrice', p.get('ClosePrice', 0)):.2f}", weight="bold")),
                ft.DataCell(ft.Text(f"{p.get('logReturn', p.get('LogReturn', 0)):.4%}", 
                                    color="red" if p.get('logReturn', 0) < 0 else "green")),
            ]) for p in reversed(recent)
        ]
        
        self.content_area.content = ft.Column([
            ft.Text("Recent Market Data", weight="bold"),
            ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("Date")),
                    ft.DataColumn(ft.Text("Close", numeric=True)),
                    ft.DataColumn(ft.Text("Log Return", numeric=True)),
                ],
                rows=rows,
                border=ft.border.all(1, self.colors.border),
                heading_row_color=self.colors.surface,
                width=float("inf")
            )
        ], scroll=ft.ScrollMode.AUTO, height=400)

    def _metric_card(self, title, value, subtitle, color):
        return ft.Container(
            content=ft.Column([
                ft.Text(title, size=12, color=ft.Colors.GREY),
                ft.Text(value, size=24, weight="bold", color=color),
                ft.Text(subtitle, size=10, color=ft.Colors.GREY_500)
            ], horizontal_alignment="center"),
            padding=10,
            bgcolor=ft.Colors.with_opacity(0.05, color),
            border_radius=8,
            border=ft.border.all(1, ft.Colors.with_opacity(0.2, color)),
            expand=True
        )
