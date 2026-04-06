import inspect

import flet as ft
from flet import Icons
from typing import Callable, List, Optional

from src.utils.theme import get_theme_colors, create_modern_card, ThemeColors


class BaseView(ft.Container):
    """Reusable page layout with consistent header and card panels."""

    def __init__(
        self,
        page: ft.Page,
        title: str,
        on_back: Optional[Callable] = None,
        on_search: Optional[Callable[[ft.ControlEvent], None]] = None,
        actions: Optional[List[ft.Control]] = None,
        colors: Optional[ThemeColors] = None,
    ) -> None:
        super().__init__()
        self.page = page
        self.on_back = on_back
        self.on_search = on_search
        self.colors = colors or get_theme_colors(
            page.theme_mode if hasattr(page, "theme_mode") else ft.ThemeMode.LIGHT
        )
        self.expand = True

        # Optional search field
        self.search_field = None
        if on_search:
            self.search_field = ft.Container(
                width=240,
                height=30,
                bgcolor="#f5f7fa",
                border=ft.border.all(1, "#e6e9ed"),
                border_radius=15,
                padding=ft.padding.only(left=10, right=10),
                content=ft.Row(
                    [
                        ft.Icon(Icons.SEARCH, color="#95a5a6", size=18),
                        ft.TextField(
                            border=ft.InputBorder.NONE,
                            color="#2c3e50",
                            hint_text="Search",
                            hint_style=ft.TextStyle(color="#95a5a6", size=14),
                            expand=True,
                            height=30,
                            content_padding=5,
                            on_change=on_search,
                        ),
                    ]
                ),
            )

        # Header setup
        left_controls: List[ft.Control] = []
        if on_back:
            left_controls.append(
                ft.IconButton(
                    Icons.ARROW_BACK,
                    icon_color=self.colors.primary,
                    on_click=lambda e: self._invoke_callback(on_back, e),
                )
            )
        self.header_title = ft.Text(title, size=22, weight=ft.FontWeight.BOLD, color=self.colors.text_primary)
        left_controls.append(self.header_title)

        right_controls: List[ft.Control] = []
        if self.search_field:
            right_controls.append(self.search_field)
        if actions:
            if right_controls:
                right_controls.append(ft.Container(width=12))
            right_controls.extend(actions)

        header = ft.Row(
            [
                ft.Row(left_controls, spacing=10),
                ft.Container(expand=True),
                ft.Row(right_controls, spacing=12) if right_controls else ft.Container(),
            ],
            alignment=ft.MainAxisAlignment.START if not right_controls else ft.MainAxisAlignment.SPACE_BETWEEN,
        )
        self.header = header

        # Column for all cards (stretch children to full width)
        self.cards_column = ft.Column(
            spacing=16,
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        )

        # Wrap main content in a Container to apply padding/bg color
        self.content = ft.Container(
            padding=ft.padding.all(24),
            bgcolor=self.colors.bg,
            content=ft.Column(
                [header, self.cards_column],
                spacing=16,
                expand=True,
                scroll=ft.ScrollMode.AUTO,
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            ),
        )

    @staticmethod
    def _invoke_callback(callback: Callable, event: Optional[ft.ControlEvent] = None) -> None:
        """Support both zero-arg callbacks and Flet event handlers."""
        try:
            signature = inspect.signature(callback)
            required_args = [
                parameter
                for parameter in signature.parameters.values()
                if parameter.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)
                and parameter.default is inspect.Parameter.empty
            ]
        except (TypeError, ValueError):
            required_args = [object()]

        if required_args:
            callback(event)
            return

        callback()

    def add_card(self, control: ft.Control) -> ft.Control:
        """Wrap content in a themed card and add it to the view."""
        card = create_modern_card(self.colors, control)
        self.cards_column.controls.append(card)
        return card
