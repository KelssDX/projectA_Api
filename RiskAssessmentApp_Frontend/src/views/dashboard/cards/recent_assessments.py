import flet as ft
from flet import Icons
from src.utils.theme import create_modern_button, ThemeColors


def build_recent_assessments_card(colors: ThemeColors, on_navigate) -> ft.Column:
    """Build card listing recent assessments."""
    table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Assessment")),
            ft.DataColumn(ft.Text("Department")),
            ft.DataColumn(ft.Text("Risk Level")),
        ],
        rows=[
            ft.DataRow([ft.DataCell(ft.Text("Q3 IT Audit")), ft.DataCell(ft.Text("IT")), ft.DataCell(ft.Text("High"))]),
            ft.DataRow([ft.DataCell(ft.Text("Finance Review")), ft.DataCell(ft.Text("Finance")), ft.DataCell(ft.Text("Medium"))]),
        ],
    )
    return ft.Column(
        [
            ft.Row(
                [
                    ft.Text("Recent Assessments", size=20, weight=ft.FontWeight.BOLD, color=colors.text_primary),
                    create_modern_button(colors, "View All", icon=Icons.LIST_ALT, on_click=lambda _: on_navigate("assessments", "list"), style="secondary", width=100),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            ft.Divider(color=colors.border, height=20),
            table,
        ],
        spacing=16,
    )
