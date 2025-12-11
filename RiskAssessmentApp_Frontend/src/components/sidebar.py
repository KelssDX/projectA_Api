import flet as ft
from flet import Icons
from src.utils.theme import get_theme_colors, build_gradient, darken_color


class Sidebar(ft.Container):
    def __init__(self, page, current_user, nav_change_callback, current_nav_index=0):
        # Generate unique key to force Flet to recognize this as a new control
        import time
        unique_key = f"sidebar_{int(time.time() * 1000)}"
        
        super().__init__(key=unique_key)
        
        print("=" * 60)
        print(f"SIDEBAR: __init__ called - Creating new Sidebar instance with key={unique_key}")
        print("=" * 60)
        
        self.page = page
        self.current_user = current_user
        self.nav_change_callback = nav_change_callback
        self.current_nav_index = current_nav_index
        self.collapsed = False
        self.collapsed_width = 70
        self.expanded_width = 240
        
        colors = get_theme_colors(page.theme_mode)
        
        # Configure this Container properties FIRST
        base_shade = colors.sidebar_bg
        self.width = self.expanded_width
        self.visible = True
        self.alignment = ft.alignment.top_left
        self.gradient = build_gradient(base_shade if self.page.theme_mode == ft.ThemeMode.LIGHT else darken_color(base_shade, 0.35))
        self.animate = ft.Animation(300, ft.AnimationCurve.EASE_IN_OUT)
        self.border = ft.border.only(right=ft.BorderSide(1, colors.border))
        self.shadow = ft.BoxShadow(
            spread_radius=0, 
            blur_radius=20, 
            color=colors.shadow, 
            offset=ft.Offset(2, 0)
        )

        # Build content directly into self.content
        self._build_sidebar_content(colors)
    
    def _build_sidebar_content(self, colors):
        """Build the complete sidebar content"""
        
        # Menu items data
        menu_items_data = [
            {"text": "Dashboard", "index": 0, "icon": Icons.DASHBOARD_OUTLINED},
            {"text": "Assessments", "index": 1, "icon": Icons.FACT_CHECK},
            {"text": "Risk Heatmap", "index": 2, "icon": Icons.GRID_ON},
            {"text": "Departments", "index": 3, "icon": Icons.DOMAIN},
            {"text": "Projects", "index": 4, "icon": Icons.WORK_OUTLINE},
            {"text": "Users", "index": 5, "icon": Icons.ADMIN_PANEL_SETTINGS},
            {"text": "Settings", "index": 6, "icon": Icons.SETTINGS_OUTLINED},
        ]
        
        self.menu_containers = []
        sidebar_controls = []

        # 1. Header
        header_title = ft.Text("Risk Core", size=20, weight=ft.FontWeight.BOLD, color=colors.sidebar_text, visible=not self.collapsed)
        
        def toggle_handler(_=None):
            self.collapsed = not self.collapsed
            new_width = self.collapsed_width if self.collapsed else self.expanded_width
            self.width = new_width
            # Rebuild content to update visibility of texts
            self._build_sidebar_content(colors)
            self.update()
        
        sidebar_header = ft.Container(
            padding=ft.padding.all(16),
            visible=True,
            content=ft.Row([
                header_title,
                ft.Container(expand=True),
                ft.Container(
                    content=ft.IconButton(
                        icon=Icons.MENU, 
                        icon_color=colors.sidebar_text,
                        tooltip="Toggle sidebar", 
                        on_click=toggle_handler,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))
                    ),
                    bgcolor=colors.sidebar_item,
                    border_radius=8
                )
            ])
        )
        sidebar_controls.append(sidebar_header)

        # 2. Menu Items
        for item in menu_items_data:
            index = item["index"]
            is_active = (index == self.current_nav_index)
            
            # Use ListTile instead of Container+Row for better stability
            menu_tile = ft.ListTile(
                leading=ft.Icon(item["icon"]),
                title=ft.Text(item["text"], size=14, visible=not self.collapsed),
                selected=is_active,
                on_click=lambda e, idx=index: self.nav_change_callback(idx),
                selected_color=colors.button_text,
                selected_tile_color=colors.sidebar_item_active,
                text_color=colors.sidebar_text,
                hover_color=ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
            )
            
            self.menu_containers.append(menu_tile)
            sidebar_controls.append(menu_tile)

        # 3. Spacer
        sidebar_controls.append(ft.Container(height=20, expand=True))

        # 4. User Profile
        initials = (self.current_user.get('username') or self.current_user.get('name') or 'U')[:1].upper()
        full_name = self.current_user.get('name') or self.current_user.get('username') or 'User'
        role_text = (self.current_user.get('role') or '').title()
        
        user_profile = ft.Container(
            padding=ft.padding.all(16) if not self.collapsed else ft.padding.all(8),
            visible=True,
            content=ft.Container(
                padding=ft.padding.all(12) if not self.collapsed else ft.padding.all(8),
                gradient=ft.LinearGradient(
                    begin=ft.alignment.top_left, 
                    end=ft.alignment.bottom_right, 
                    colors=["#2E1065", "#4C1D95", "#6D28D9"]
                ),
                border_radius=16,
                border=ft.border.all(1, ft.Colors.with_opacity(0.3, ft.Colors.WHITE)),
                content=ft.Row([
                    ft.Container(
                        width=40, 
                        height=40,
                        gradient=ft.LinearGradient(
                            begin=ft.alignment.top_left, 
                            end=ft.alignment.bottom_right, 
                            colors=["#2E1065", "#4C1D95", "#6D28D9"]
                        ),
                        border_radius=20,
                        alignment=ft.alignment.center,
                        content=ft.Text(initials, color=colors.button_text, size=16, weight=ft.FontWeight.BOLD),
                        border=ft.border.all(1, ft.Colors.with_opacity(0.35, ft.Colors.WHITE))
                    ),
                    ft.Column([
                        ft.Text(full_name, size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                        ft.Text(role_text, size=12, color=ft.Colors.WHITE70, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS)
                    ], spacing=2, expand=True, visible=not self.collapsed)
                ], spacing=12, alignment=ft.MainAxisAlignment.CENTER if self.collapsed else ft.MainAxisAlignment.START)
            )
        )
        sidebar_controls.append(user_profile)

        # Set content directly
        self.content = ft.Column(
            controls=sidebar_controls,
            expand=True,
            spacing=0,
            scroll=ft.ScrollMode.AUTO,
            alignment=ft.MainAxisAlignment.START
        )
        
        print(f"SIDEBAR: Built {len(sidebar_controls)} controls directly into content")
    
    def update_selection(self, new_index):
        """Update which menu item is selected"""
        print(f"SIDEBAR: update_selection called - changing from index {self.current_nav_index} to {new_index}")
        
        self.current_nav_index = new_index
        colors = get_theme_colors(self.page.theme_mode)
        
        for menu_item in self.menu_containers:
            # Handle ListTile
            if isinstance(menu_item, ft.ListTile):
                # We can't access 'data' on ListTile easily if not set, but we can check index from closure if stored
                # Or just iterate by index if we match arrays. 
                # Better: iterate with index
                pass

        # Rebuild content entirely to update selection state reliably
        self._build_sidebar_content(colors)
        if self.page:
            self.update()

