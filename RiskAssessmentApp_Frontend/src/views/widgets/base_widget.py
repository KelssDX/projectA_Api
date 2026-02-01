import flet as ft
from flet import Colors
from src.utils.theme import get_theme_colors

class BaseAnalyticsWidget(ft.Container):
    """Base class for analytics widgets providing common styling and structure"""
    def __init__(self, page, client, title):
        super().__init__()
        self.page = page
        self.client = client
        self.title_text = title
        self.padding = 15
        self.border_radius = 12
        self.colors = get_theme_colors(page.theme_mode)
        self.bgcolor = self.colors.surface
        self.border = ft.border.all(1, self.colors.border)
        
        # State
        self.view_mode = "chart" # "chart" or "table"
        self.use_mock = False
        self.is_collapsed = False
        
        # Callbacks
        self.on_maximize_requested = None 
        self.on_close_requested = None
        self.on_minimize_toggle = None
        
        # Header Actions
        self.view_toggle_btn = ft.IconButton(
            icon=ft.Icons.TABLE_CHART, 
            tooltip="Switch to Table View", 
            icon_size=16, 
            on_click=self.toggle_view_mode
        )
        
        self.minimize_btn = ft.IconButton(
            icon=ft.Icons.REMOVE, 
            tooltip="Minimize/Expand", 
            icon_size=16, 
            on_click=self.toggle_minimize
        )
        
        self.header = ft.Row([
            ft.Text(title, size=14, weight="bold", color=self.colors.text_primary, no_wrap=True),
            ft.Container(expand=True),
            self.view_toggle_btn,
            self.minimize_btn,
            ft.IconButton(icon=ft.Icons.OPEN_IN_FULL, tooltip="Pop-out", icon_size=16, on_click=self.on_maximize_click),
            ft.IconButton(icon=ft.Icons.CLOSE, tooltip="Close", icon_size=16, on_click=self.on_close_click),
        ], spacing=0)

        # Metadata for auto-detection
        self.is_wide = False # Hint for layout engine
        
        self.content_area = ft.Container(expand=True, animate_size=300)
        
        # Resize handle
        self.resize_handle = ft.GestureDetector(
            content=ft.Container(
                content=ft.Icon(ft.Icons.DRAG_HANDLE, size=12, color=self.colors.border),
                alignment=ft.alignment.bottom_right,
                padding=2
            ),
            on_pan_update=self._handle_resize
        )

        self.content = ft.Column([
            self.header,
            ft.Divider(height=1, color=self.colors.border),
            self.content_area,
            ft.Row([ft.Container(expand=True), self.resize_handle], spacing=0)
        ], spacing=10)

    def _handle_resize(self, e: ft.DragUpdateEvent):
        # Allow vertical resizing
        new_height = (self.height or 300) + e.delta_y
        if 150 < new_height < 800:
            self.height = new_height
            self.update()

    def toggle_minimize(self, e):
        self.is_collapsed = not self.is_collapsed
        self.content_area.visible = not self.is_collapsed
        self.minimize_btn.icon = ft.Icons.ADD if self.is_collapsed else ft.Icons.REMOVE
        self.minimize_btn.tooltip = "Expand" if self.is_collapsed else "Minimize"
        if self.on_minimize_toggle:
            self.on_minimize_toggle(self)
        self.update()

    def on_close_click(self, e):
        if self.on_close_requested:
            self.on_close_requested(self)

    def show_loading(self):
        self.content_area.content = ft.Container(
            content=ft.ProgressRing(width=20, height=20, stroke_width=2),
            alignment=ft.alignment.center,
            expand=True,
            height=200
        )
        try:
            if self.page: self.update()
        except Exception:
            pass

    def show_error(self, message):
        self.content_area.content = ft.Container(
            content=ft.Text(f"Error: {message}", color=ft.Colors.RED, size=12),
            padding=10,
            alignment=ft.alignment.center
        )
        try:
            if self.page: self.update()
        except Exception:
            pass
        
    def toggle_view_mode(self, e):
        self.view_mode = "table" if self.view_mode == "chart" else "chart"
        self.view_toggle_btn.icon = ft.Icons.BAR_CHART if self.view_mode == "table" else ft.Icons.TABLE_CHART
        self.view_toggle_btn.tooltip = "Switch to Chart View" if self.view_mode == "table" else "Switch to Table View"
        self.load_data() # Reload data to render the correct view
        
    def on_maximize_click(self, e):
        if self.on_maximize_requested:
            self.on_maximize_requested(self)


class BaseWidget(ft.Container):
    """
    Base class for new analytics widgets with simplified interface.
    Uses build_content(), load_data() pattern.
    """
    def __init__(self, page, title, icon=None, description=None):
        super().__init__()
        self.page = page
        self.title = title
        self.icon = icon
        self.description = description
        self.colors = get_theme_colors(page.theme_mode)
        
        # Container styling
        self.padding = 15
        self.border_radius = 12
        self.bgcolor = self.colors.surface
        self.border = ft.border.all(1, self.colors.border)
        
        # State
        self.is_loading = False
        self.error_message = None
        
        # Build the widget structure
        self._build_widget()

    def _build_widget(self):
        """Build the widget frame with header and content area"""
        # Header with icon and title
        header_items = []
        if self.icon:
            header_items.append(ft.Icon(self.icon, size=18, color=self.colors.primary))
        header_items.append(ft.Text(self.title, size=14, weight=ft.FontWeight.BOLD, color=self.colors.text_primary))
        if self.description:
            header_items.append(ft.Container(expand=True))
            header_items.append(ft.Icon(
                ft.Icons.INFO_OUTLINE, 
                size=14, 
                color=self.colors.text_secondary,
                tooltip=self.description
            ))
        
        header = ft.Row(header_items, spacing=8)
        
        # Content area - will be populated by build_content()
        self.content_area = ft.Container(expand=True)
        content = self.build_content()
        if content:
            self.content_area.content = content

        # Resize handle (vertical)
        self.resize_handle = ft.GestureDetector(
            content=ft.Container(
                content=ft.Icon(ft.Icons.DRAG_HANDLE, size=12, color=self.colors.border),
                alignment=ft.alignment.bottom_right,
                padding=2
            ),
            on_pan_update=self._handle_resize
        )
        
        self.content = ft.Column([
            header,
            ft.Divider(height=1, color=self.colors.border),
            self.content_area,
            ft.Row([ft.Container(expand=True), self.resize_handle], spacing=0)
        ], spacing=10, expand=True)
    
    def build_content(self):
        """Override this method to build widget content. Should return a Flet control."""
        return ft.Text("Widget content not implemented", size=12, color=self.colors.text_secondary)
    
    def load_data(self):
        """Override this method to load data asynchronously"""
        pass
    
    def show_loading(self):
        """Show loading indicator"""
        self.content_area.content = ft.Container(
            content=ft.Column([
                ft.ProgressRing(width=30, height=30, stroke_width=3),
                ft.Text("Loading...", size=12, color=self.colors.text_secondary)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
            alignment=ft.alignment.center,
            expand=True
        )
        if self.page:
            try:
                self.page.update()
            except:
                pass
    
    def show_error(self, message):
        """Show error message"""
        self.content_area.content = ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.ERROR_OUTLINE, size=32, color=Colors.RED),
                ft.Text(f"Error: {message}", size=12, color=Colors.RED)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
            alignment=ft.alignment.center,
            expand=True
        )
        if self.page:
            try:
                self.page.update()
            except:
                pass
    
    def refresh(self):
        """Refresh widget data"""
        self.load_data()

    def _handle_resize(self, e: ft.DragUpdateEvent):
        """Allow vertical resizing for embedded widgets"""
        current_height = self.height or 300
        new_height = current_height + getattr(e, "delta_y", 0)
        if 160 < new_height < 900:
            self.height = new_height
            try:
                self.update()
            except Exception:
                pass
