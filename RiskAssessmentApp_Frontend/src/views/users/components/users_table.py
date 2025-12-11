import flet as ft
from src.utils.theme import ThemeColors


def build_users_table(view: "UserManagementView", colors: ThemeColors) -> ft.Container:
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
        bgcolor=colors.surface,
        border=ft.border.only(bottom=ft.BorderSide(1, colors.border)),
        padding=ft.padding.only(left=30, right=30),
        content=ft.Row(
            [
                ft.Container(expand=2, content=ft.Text("Name", weight=ft.FontWeight.BOLD, color=colors.text_secondary)),
                ft.Container(expand=1, content=ft.Text("Username", weight=ft.FontWeight.BOLD, color=colors.text_secondary)),
                ft.Container(expand=2, content=ft.Text("Email", weight=ft.FontWeight.BOLD, color=colors.text_secondary)),
                ft.Container(expand=1, content=ft.Text("Role", weight=ft.FontWeight.BOLD, color=colors.text_secondary)),
                ft.Container(expand=1, content=ft.Text("Department", weight=ft.FontWeight.BOLD, color=colors.text_secondary)),
            ],
            expand=True,
        ),
    )

    list_view = ft.ListView(expand=True, spacing=0, auto_scroll=False)
    for user in filtered_users:
        list_view.controls.append(
            ft.Container(
                height=50,
                bgcolor=colors.surface,
                padding=ft.padding.only(left=30, right=30),
                border=ft.border.only(bottom=ft.BorderSide(1, colors.border)),
                content=ft.Row(
                    [
                        ft.Container(expand=2, content=ft.Text(user["name"], color=colors.text_primary, overflow=ft.TextOverflow.ELLIPSIS)),
                        ft.Container(expand=1, content=ft.Text(user["username"], color=colors.text_primary, overflow=ft.TextOverflow.ELLIPSIS)),
                        ft.Container(expand=2, content=ft.Text(user["email"], color=colors.text_primary, overflow=ft.TextOverflow.ELLIPSIS)),
                        ft.Container(expand=1, content=ft.Text(user["role"], color=colors.text_primary, overflow=ft.TextOverflow.ELLIPSIS)),
                        ft.Container(expand=1, content=ft.Text(user.get("department", ""), color=colors.text_primary, overflow=ft.TextOverflow.ELLIPSIS)),
                    ],
                    expand=True
                ),
            )
        )

    table = ft.Column([header, list_view], spacing=0, expand=True)
    return ft.Container(expand=True, content=table)
