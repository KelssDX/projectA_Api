import flet as ft
from flet import Icons
from src.utils.theme import create_modern_button, ThemeColors


def build_action_bar(view: "UserManagementView", colors: ThemeColors) -> ft.Column:
    """Create the filter and action bar for user management."""
    view.role_filter = ft.Container(
        width=150,
        height=30,
        bgcolor="white",
        border=ft.border.all(1, "#e6e9ed"),
        border_radius=5,
        padding=ft.padding.only(left=20, right=10),
        content=ft.Row([
            ft.Text(view.current_role_filter, size=14, color="#2c3e50"),
            ft.Container(expand=True),
            ft.Container(width=20, height=20, content=ft.Text("▼", size=10, color="#95a5a6")),
        ]),
        on_click=view.show_role_filter,
    )

    view.dept_filter = ft.Container(
        width=150,
        height=30,
        bgcolor="white",
        border=ft.border.all(1, "#e6e9ed"),
        border_radius=5,
        margin=ft.margin.only(left=20),
        padding=ft.padding.only(left=20, right=10),
        content=ft.Row([
            ft.Text(view.current_dept_filter, size=14, color="#2c3e50"),
            ft.Container(expand=True),
            ft.Container(width=20, height=20, content=ft.Text("▼", size=10, color="#95a5a6")),
        ]),
        on_click=view.show_department_filter,
    )

    return ft.Column(
        [
            ft.Row([view.role_filter, view.dept_filter], spacing=10),
            ft.Row(
                [
                    ft.Container(expand=True),
                    create_modern_button(
                        colors,
                        "Add New User",
                        icon=Icons.PERSON_ADD,
                        on_click=view.add_new_user,
                        style="primary",
                    ),
                ],
                alignment=ft.MainAxisAlignment.END,
            ),
        ],
        spacing=10,
    )
