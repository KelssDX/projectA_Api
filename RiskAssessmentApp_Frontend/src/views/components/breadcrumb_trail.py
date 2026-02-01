"""
Breadcrumb Trail Component
Provides navigation breadcrumbs for drill-down hierarchy navigation.
"""

import flet as ft
from flet import Icons
from src.utils.theme import get_theme_colors


class BreadcrumbTrail(ft.Row):
    """
    A breadcrumb navigation component for tracking drill-down hierarchy.
    Shows the path of navigation and allows users to go back to any level.
    """
    
    def __init__(self, page, on_navigate=None, separator="›"):
        """
        Args:
            page: The Flet page instance
            on_navigate: Callback when a breadcrumb is clicked, receives (level, context)
            separator: Character to use between breadcrumb items
        """
        super().__init__()
        self.page = page
        self.on_navigate_callback = on_navigate
        self.separator = separator
        self.colors = get_theme_colors(page.theme_mode)
        self.crumbs = []  # List of {"label": str, "context": dict}
        
        # Styling
        self.spacing = 5
        self.scroll = ft.ScrollMode.AUTO
        self.vertical_alignment = ft.CrossAxisAlignment.CENTER
        
        # Initialize with home
        self.reset()
    
    def reset(self, home_label="Dashboard"):
        """Reset breadcrumbs to just the home/root level"""
        self.crumbs = [{"label": home_label, "context": {"level": 0, "type": "home"}}]
        self._render()
    
    def push(self, label, context=None):
        """
        Add a new breadcrumb level.
        
        Args:
            label: Display text for the breadcrumb
            context: Dictionary with navigation context
        """
        self.crumbs.append({
            "label": label,
            "context": context or {"level": len(self.crumbs)}
        })
        self._render()
    
    def pop(self):
        """Remove the last breadcrumb level (go back one level)"""
        if len(self.crumbs) > 1:
            self.crumbs.pop()
            self._render()
            return True
        return False
    
    def navigate_to(self, level):
        """
        Navigate to a specific level in the breadcrumb trail.
        
        Args:
            level: The index of the breadcrumb to navigate to (0 = home)
        """
        if 0 <= level < len(self.crumbs):
            self.crumbs = self.crumbs[:level + 1]
            self._render()
            if self.on_navigate_callback:
                self.on_navigate_callback(level, self.crumbs[level]["context"])
    
    def get_current_context(self):
        """Get the context of the current (last) breadcrumb"""
        if self.crumbs:
            return self.crumbs[-1]["context"]
        return None
    
    def get_current_level(self):
        """Get the current depth level"""
        return len(self.crumbs) - 1
    
    def _render(self):
        """Render the breadcrumb trail"""
        self.controls.clear()
        
        for i, crumb in enumerate(self.crumbs):
            is_last = i == len(self.crumbs) - 1
            is_first = i == 0
            
            # Home icon for first item
            if is_first:
                icon = ft.Icon(
                    Icons.HOME,
                    size=16,
                    color=self.colors.primary if is_last else self.colors.text_secondary
                )
                self.controls.append(icon)
            
            # Breadcrumb button/text
            if is_last:
                # Current level - just text, not clickable
                text = ft.Text(
                    crumb["label"],
                    size=13,
                    weight=ft.FontWeight.BOLD,
                    color=self.colors.text_primary
                )
                self.controls.append(text)
            else:
                # Previous levels - clickable
                btn = ft.TextButton(
                    content=ft.Text(
                        crumb["label"],
                        size=13,
                        color=self.colors.primary
                    ),
                    style=ft.ButtonStyle(
                        padding=ft.padding.symmetric(horizontal=8, vertical=4),
                    ),
                    on_click=lambda e, level=i: self.navigate_to(level)
                )
                self.controls.append(btn)
            
            # Separator (except for last item)
            if not is_last:
                sep = ft.Text(
                    self.separator,
                    size=14,
                    color=self.colors.text_secondary
                )
                self.controls.append(sep)
        
        # Update the control
        try:
            if self.page:
                self.update()
        except:
            pass
    
    def to_path_string(self):
        """Get the current path as a string"""
        return " › ".join(c["label"] for c in self.crumbs)


class CompactBreadcrumb(ft.Container):
    """
    A compact version of breadcrumbs that shows only the current level
    with back button for limited space scenarios.
    """
    
    def __init__(self, page, on_back=None):
        super().__init__()
        self.page = page
        self.on_back_callback = on_back
        self.colors = get_theme_colors(page.theme_mode)
        self.history = []  # Stack of labels
        
        # Build UI
        self.back_btn = ft.IconButton(
            icon=Icons.ARROW_BACK_IOS,
            icon_size=16,
            tooltip="Go Back",
            on_click=self._handle_back,
            visible=False
        )
        
        self.current_label = ft.Text(
            "Dashboard",
            size=14,
            weight=ft.FontWeight.BOLD,
            color=self.colors.text_primary
        )
        
        self.content = ft.Row([
            self.back_btn,
            self.current_label
        ], spacing=5, vertical_alignment=ft.CrossAxisAlignment.CENTER)
    
    def push(self, label):
        """Push a new level"""
        self.history.append(self.current_label.value)
        self.current_label.value = label
        self.back_btn.visible = True
        self.update()
    
    def pop(self):
        """Go back one level"""
        if self.history:
            self.current_label.value = self.history.pop()
            self.back_btn.visible = len(self.history) > 0
            self.update()
            return True
        return False
    
    def reset(self, label="Dashboard"):
        """Reset to initial state"""
        self.history.clear()
        self.current_label.value = label
        self.back_btn.visible = False
        self.update()
    
    def _handle_back(self, e):
        """Handle back button click"""
        if self.pop() and self.on_back_callback:
            self.on_back_callback()
