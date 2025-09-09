import flet as ft
from src.utils.theme import ThemeColors


def build_users_table(view: "UserManagementView", colors: ThemeColors) -> ft.Column:
    """Build table displaying filtered users."""
    filtered_users = view.users
    if view.search_value:
        filtered_users = [
            u
            for u in filtered_users
            if view.search_value in u["name"].lower()
            or view.search_value in u["username"].lower()
            or view.search_value in u["email"].lower()
        ]
    if view.current_role_filter != "All Roles":
        filtered_users = [u for u in filtered_users if u["role"] == view.current_role_filter]
    if view.current_dept_filter != "All Departments":
        filtered_users = [u for u in filtered_users if u["department"] == view.current_dept_filter]

    header = ft.Container(
        height=40,
        bgcolor=None,
        border=ft.border.only(bottom=ft.BorderSide(1, colors.border)),
        padding=ft.padding.only(left=30, right=30),
        content=ft.Row(
            [
                ft.Container(expand=True, content=ft.Text("Name", weight=ft.FontWeight.W_600, color=colors.text_primary)),
                ft.Container(width=150, content=ft.Text("Username", color=colors.text_primary)),
                ft.Container(width=200, content=ft.Text("Email", color=colors.text_primary)),
                ft.Container(width=120, content=ft.Text("Role", color=colors.text_primary)),
                ft.Container(width=150, content=ft.Text("Department", color=colors.text_primary)),
            ],
            alignment=ft.MainAxisAlignment.START,
        ),
    )

    rows = []
    for user in filtered_users:
        rows.append(
            ft.Container(
                height=50,
                padding=ft.padding.only(left=30, right=30),
                border=ft.border.only(bottom=ft.BorderSide(1, colors.border)),
                content=ft.Row(
                    [
                        ft.Container(expand=True, content=ft.Text(user["name"], color=colors.text_secondary)),
                        ft.Container(width=150, content=ft.Text(user["username"], color=colors.text_secondary)),
                        ft.Container(width=200, content=ft.Text(user["email"], color=colors.text_secondary)),
                        ft.Container(width=120, content=ft.Text(user["role"], color=colors.text_secondary)),
                        ft.Container(width=150, content=ft.Text(user.get("department", ""), color=colors.text_secondary)),
                    ]
                ),
            )
        )

    return ft.Column([header, *rows], spacing=0)
