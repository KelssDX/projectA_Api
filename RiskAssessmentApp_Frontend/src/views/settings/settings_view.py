import flet as ft
from flet import Icons
from src.views.common.base_view import BaseView
from src.utils.theme import get_theme_colors, create_modern_button


class SettingsView(BaseView):
    def __init__(self, page, user=None):
        self.page = page
        self.user = user
        colors = get_theme_colors(self.page.theme_mode if hasattr(self.page, "theme_mode") else ft.ThemeMode.LIGHT)
        actions = [
            create_modern_button(colors, "Save Settings", icon=Icons.SAVE, on_click=self.save_settings, style="primary")
        ]
        super().__init__(page, "Settings", actions=actions, colors=colors)

        # General section
        general = ft.Column([
            ft.Text("Appearance", size=16, weight=ft.FontWeight.BOLD, color=colors.text_primary),
            ft.Row([
                ft.Text("Theme", color=colors.text_secondary),
                ft.Container(width=12),
                ft.Dropdown(
                    width=180,
                    options=[ft.dropdown.Option("System"), ft.dropdown.Option("Light"), ft.dropdown.Option("Dark")],
                    value="System",
                ),
            ], alignment=ft.MainAxisAlignment.START),
            ft.Container(height=8),
            ft.Text("Notifications", size=16, weight=ft.FontWeight.BOLD, color=colors.text_primary),
            ft.Checkbox(label="Email alerts", value=True),
            ft.Checkbox(label="Desktop notifications", value=False),
        ], spacing=10)

        security = ft.Column([
            ft.Text("Security", size=16, weight=ft.FontWeight.BOLD, color=colors.text_primary),
            ft.Checkbox(label="Require 2FA", value=False),
            ft.Checkbox(label="Session timeout warnings", value=True),
        ], spacing=10)

        # Add as cards
        self.cards_column.controls.clear()
        self.add_card(general)
        self.add_card(security)

    def save_settings(self, e):
        if hasattr(self, 'page') and self.page:
            self.page.snack_bar = ft.SnackBar(content=ft.Text("Settings saved"))
            self.page.snack_bar.open = True
            self.page.update()

