import flet as ft
from flet import Icons
from src.utils.theme import create_stat_card, ThemeColors


def build_statistics_row(stats: dict, colors: ThemeColors, on_navigate) -> ft.Row:
    """Create the row of statistic cards for dashboard."""
    return ft.Row(
        [
            ft.Container(
                content=create_stat_card(
                    colors,
                    "Active Assessments",
                    str(stats.get("active_assessments", 0)),
                    Icons.ASSIGNMENT_OUTLINED,
                    colors.primary,
                    on_click=lambda _: on_navigate("assessments", "list", {"status": "active"}),
                ),
                expand=True,
            ),
            ft.Container(
                content=create_stat_card(
                    colors,
                    "High Risk Areas",
                    str(stats.get("high_risk_areas", 0)),
                    Icons.ERROR_OUTLINE,
                    colors.danger,
                    on_click=lambda _: on_navigate("heatmap", None, {"filter": "high_risk"}),
                ),
                expand=True,
            ),
            ft.Container(
                content=create_stat_card(
                    colors,
                    "Completed This Month",
                    str(stats.get("completed_this_month", 0)),
                    Icons.CHECK_CIRCLE_OUTLINE,
                    colors.success,
                    on_click=lambda _: on_navigate("assessments", "list", {"status": "completed"}),
                ),
                expand=True,
            ),
            ft.Container(
                content=create_stat_card(
                    colors,
                    "Pending Reviews",
                    str(stats.get("pending_reviews", 0)),
                    Icons.SCHEDULE,
                    colors.warning,
                    on_click=lambda _: on_navigate("assessments", "list", {"status": "pending"}),
                ),
                expand=True,
            ),
        ],
        spacing=16,
    )
