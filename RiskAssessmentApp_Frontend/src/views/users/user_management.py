import flet as ft
from src.utils.theme import get_theme_colors, apply_theme_to_control
from src.views.common.base_view import BaseView
from src.api.identity_client import IdentityAPIClient
from .components.action_bar import build_action_bar
from .components.users_table import build_users_table


class UserManagementView(BaseView):
    """View for managing users with shared layout and modular components."""

    def __init__(self, page, user):
        self.page = page
        self.user = user
        self.search_value = ""
        self.current_role_filter = "All Roles"
        self.current_dept_filter = "All Departments"

        if isinstance(user, dict):
            self.username = user.get("username", "A")
        else:
            self.username = getattr(user, "username", "A") if user else "A"

        self.identity_client = IdentityAPIClient()
        self.users = []

        colors = get_theme_colors(
            self.page.theme_mode if hasattr(self.page, "theme_mode") else ft.ThemeMode.LIGHT
        )
        avatar = ft.Container(
            width=30,
            height=30,
            border_radius=15,
            bgcolor=colors.button_primary,
            alignment=ft.alignment.center,
            content=ft.Text(
                self.username[0].upper() if self.username else "A",
                color=colors.button_text,
                weight=ft.FontWeight.BOLD,
            ),
        )

        super().__init__(page, "User Management", on_search=self.on_search_change, actions=[avatar], colors=colors)

        # Build modular action bar and table placeholder
        self.add_card(build_action_bar(self, colors))
        self.users_table_container = ft.Container(expand=True)
        self.add_card(self.users_table_container)

        self.refresh_table()
        self.load_users()

        try:
            apply_theme_to_control(self, colors)
        except Exception:
            pass

    # Theming hook
    def apply_theme(self, colors):
        try:
            self.__init__(self.page, self.user)
            apply_theme_to_control(self, colors)
        except Exception:
            pass

    def on_search_change(self, e):
        self.search_value = e.control.value.lower()
        self.refresh_table()

    def load_users(self):
        if hasattr(self, "page") and self.page:
            self.page.run_task(self._load_users_async)

    async def _load_users_async(self):
        try:
            api_users = await self.identity_client.get_users()
            if api_users:
                self.users = []
                for user_data in api_users:
                    if isinstance(user_data, dict):
                        self.users.append({
                            "id": user_data.get("id"),
                            "name": user_data.get("name", "Unknown"),
                            "username": user_data.get("username", "unknown"),
                            "email": user_data.get("email", "unknown@example.com"),
                            "role": user_data.get("role", "User"),
                            "department": user_data.get("department", None),
                        })
                    else:
                        self.users.append({
                            "id": getattr(user_data, "id", None),
                            "name": getattr(user_data, "name", "Unknown"),
                            "username": getattr(user_data, "username", "unknown"),
                            "email": getattr(user_data, "email", "unknown@example.com"),
                            "role": getattr(user_data, "role", "User"),
                            "department": getattr(user_data, "department", None),
                        })
            self.refresh_table()
            if hasattr(self, "page") and self.page:
                self.page.update()
        except Exception as e:
            print(f"Error loading users from Identity API: {e}")
            self.users = []
            if hasattr(self, "page") and self.page:
                self.page.update()

    def refresh_table(self):
        colors = get_theme_colors(self.page.theme_mode if hasattr(self.page, "theme_mode") else ft.ThemeMode.LIGHT)
        self.users_table_container.content = build_users_table(self, colors)
        if hasattr(self, "page") and self.page:
            self.page.update()

    # Placeholder handlers for modular components
    def show_role_filter(self, _):
        pass

    def show_department_filter(self, _):
        pass

    def add_new_user(self, _):
        pass
