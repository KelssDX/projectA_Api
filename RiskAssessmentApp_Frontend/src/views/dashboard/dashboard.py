import flet as ft
from flet import Icons

from src.utils.theme import get_theme_colors, create_modern_button
from src.views.common.base_view import BaseView
from .cards.statistics import build_statistics_row
from .cards.risk_distribution import build_risk_distribution_card
from .cards.recent_assessments import build_recent_assessments_card


class DashboardView(BaseView):
    """Main dashboard composed of modular card sections."""

    def __init__(self, page, auditing_client, on_navigate, current_user=None):
        self.auditing_client = auditing_client
        self.on_navigate = on_navigate
        self.current_user = current_user
        self.assessments_data = []
        self.stats = {
            "active_assessments": 0,
            "high_risk_areas": 0,
            "completed_this_month": 0,
            "pending_reviews": 0,
        }

        colors = get_theme_colors(
            page.theme_mode if hasattr(page, "theme_mode") else ft.ThemeMode.LIGHT
        )
        actions = [
            create_modern_button(
                colors,
                "Export Data",
                icon=Icons.DOWNLOAD,
                on_click=self.export_assessments,
                style="primary",
            ),
            create_modern_button(
                colors,
                "New Assessment",
                icon=Icons.ADD,
                on_click=self.handle_new_assessment,
                style="success",
            ),
        ]

        super().__init__(page, "Risk Assessment Dashboard", actions=actions, colors=colors)
        self.build_dashboard()

    def build_dashboard(self) -> None:
        colors = self.colors
        self.cards_column.controls.clear()
        self.add_card(build_statistics_row(self.stats, colors, self.on_navigate))
        self.add_card(build_risk_distribution_card(colors, self.on_navigate))
        self.add_card(build_recent_assessments_card(colors, self.on_navigate))

    # Placeholder handlers
    def export_assessments(self, _):
        pass

    def handle_new_assessment(self, _):
        pass
