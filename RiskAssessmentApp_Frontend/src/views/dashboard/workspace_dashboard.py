import flet as ft
from src.views.common.base_view import BaseView
from src.views.widgets.market_risk_widget import MarketRiskWidget
from src.views.widgets.operational_risk_widget import OperationalRiskWidget
from src.api.auditing_client import AuditingAPIClient
from src.utils.theme import get_theme_colors

class WorkspaceDashboard(BaseView):
    def __init__(self, page, current_user):
        super().__init__(page, title="Audit Workspace 2.0")
        self.current_user = current_user
        self.client = AuditingAPIClient()
        self.active_widgets = {"market": True, "operational": True}
        self.widgets = {}
        
        # Build the content
        self._build_widgets()

    def _build_widgets(self):
        colors = get_theme_colors(self.page.theme_mode)
        
        # Header Row
        header = ft.Row([
            ft.Container(expand=True),
            ft.OutlinedButton(
                "Customize Layout", 
                icon=ft.Icons.EDIT_OUTLINED,
                on_click=self._toggle_edit_mode
            ),
            ft.FilledButton(
                "Export Report", 
                icon=ft.Icons.PICTURE_AS_PDF,
                style=ft.ButtonStyle(bgcolor=colors.primary)
            )
        ])
        
        # Widget Grid
        self.grid = ft.Column(spacing=20, scroll=ft.ScrollMode.AUTO, expand=True)
        
        # Add to cards column
        self.add_card(header)
        self.add_card(self.grid)

    def load_data(self):
        # Clear existing
        self.grid.controls.clear()
        
        colors = get_theme_colors(self.page.theme_mode)

        # Add Market Risk Widget if active
        if self.active_widgets["market"]:
            mw = MarketRiskWidget(self.page, self.client)
            self.grid.controls.append(mw)
            mw.load_data()
            
        # Add Operational Risk Widget if active
        if self.active_widgets["operational"]:
            op_widget = OperationalRiskWidget(self.page, self.client)
            self.grid.controls.append(op_widget)
            op_widget.load_data()

        self.page.update()

    def _toggle_edit_mode(self, e):
        # Demo toggle: flip the state of 'market' widget
        self.active_widgets["market"] = not self.active_widgets["market"]
        self.load_data()
        
        state = "Enabled" if self.active_widgets["market"] else "Disabled"
        self.page.show_snack_bar(
             ft.SnackBar(content=ft.Text(f"Market Risk Widget {state}"), open=True)
        )
