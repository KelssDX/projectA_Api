import flet as ft
from flet import Icons
from src.utils.theme import create_modern_button, ThemeColors


def build_risk_distribution_card(colors: ThemeColors, on_navigate) -> ft.Column:
    """Build card showing risk distribution by department."""
    departments = ["IT", "Finance", "Operations", "Marketing"]
    risk_data = [
        {"dept": "IT", "high": 35, "medium": 25, "low": 15},
        {"dept": "Finance", "high": 20, "medium": 30, "low": 25},
        {"dept": "Operations", "high": 15, "medium": 15, "low": 40},
        {"dept": "Marketing", "high": 10, "medium": 25, "low": 35},
    ]
    chart_rows = []
    for data in risk_data:
        chart_rows.append(
            ft.Row(
                [
                    ft.Container(ft.Text(data["dept"], color=colors.text_primary, weight=ft.FontWeight.W_500), width=100),
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Container(
                                    content=ft.Text(f"{data['high']}%", color="white", size=12, weight=ft.FontWeight.BOLD),
                                    bgcolor=colors.danger,
                                    padding=5,
                                    width=data["high"] * 2,
                                    alignment=ft.alignment.center,
                                ),
                                ft.Container(
                                    content=ft.Text(f"{data['medium']}%", color="white", size=12, weight=ft.FontWeight.BOLD),
                                    bgcolor=colors.warning,
                                    padding=5,
                                    width=data["medium"] * 2,
                                    alignment=ft.alignment.center,
                                ),
                                ft.Container(
                                    content=ft.Text(f"{data['low']}%", color="white", size=12, weight=ft.FontWeight.BOLD),
                                    bgcolor=colors.success,
                                    padding=5,
                                    width=data["low"] * 2,
                                    alignment=ft.alignment.center,
                                ),
                            ]
                        ),
                        expand=True,
                    ),
                ],
                spacing=0,
            )
        )
    return ft.Column(
        [
            ft.Row(
                [
                    ft.Text("Risk Distribution by Department", size=20, weight=ft.FontWeight.BOLD, color=colors.text_primary),
                    create_modern_button(colors, "View Heatmap", icon=Icons.GRID_VIEW, on_click=lambda _: on_navigate("heatmap"), style="secondary", width=140),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            ft.Divider(color=colors.border, height=20),
            ft.Column(chart_rows, spacing=10),
        ],
        spacing=16,
    )
