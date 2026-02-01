"""
Hierarchy Selector Component
Provides a dropdown for filtering dashboard data by audit universe hierarchy levels.
"""

import flet as ft
from flet import Icons
from src.utils.theme import get_theme_colors
from src.api.auditing_client import AuditingAPIClient


class HierarchySelector(ft.Container):
    """
    A dropdown component for selecting audit universe hierarchy nodes
    to filter dashboard widgets by organizational scope.
    """
    
    def __init__(self, page, on_selection_change=None, allow_multi_select=False):
        """
        Args:
            page: The Flet page instance
            on_selection_change: Callback when selection changes, receives selected node(s)
            allow_multi_select: If True, allows selecting multiple nodes
        """
        super().__init__()
        self.page = page
        self.on_selection_change = on_selection_change
        self.allow_multi_select = allow_multi_select
        self.colors = get_theme_colors(page.theme_mode)
        self.auditing_client = AuditingAPIClient()
        
        self.hierarchy_data = []
        self.selected_node = None
        self.selected_nodes = []  # For multi-select
        
        # Build UI
        self._build_ui()
    
    def _build_ui(self):
        """Build the selector UI"""
        self.dropdown = ft.Dropdown(
            label="Filter by Hierarchy",
            hint_text="All Levels",
            options=[],
            on_change=self._handle_change,
            width=250,
            dense=True,
            bgcolor=self.colors.surface,
            border_color=self.colors.border
        )
        
        self.clear_btn = ft.IconButton(
            icon=Icons.CLEAR,
            icon_size=16,
            tooltip="Clear Filter",
            on_click=self._clear_selection,
            visible=False
        )
        
        self.refresh_btn = ft.IconButton(
            icon=Icons.REFRESH,
            icon_size=16,
            tooltip="Refresh Hierarchy",
            on_click=lambda e: self.load_hierarchy()
        )
        
        self.content = ft.Row([
            self.dropdown,
            self.clear_btn,
            self.refresh_btn
        ], spacing=5, vertical_alignment=ft.CrossAxisAlignment.CENTER)
    
    def load_hierarchy(self):
        """Load hierarchy data from API"""
        if self.page:
            self.page.run_task(self._load_hierarchy_async)
    
    async def _load_hierarchy_async(self):
        """Async hierarchy loading"""
        try:
            self.dropdown.options = [ft.dropdown.Option("loading", "Loading...")]
            self.page.update()
            
            # Fetch hierarchy from API
            hierarchy = await self.auditing_client.get_audit_universe_hierarchy()
            
            if hierarchy:
                nodes = self._extract_nodes(hierarchy)
                self.hierarchy_data = nodes
                self._populate_dropdown(nodes)
            else:
                self.dropdown.options = [ft.dropdown.Option("none", "No hierarchy available")]
            
            self.page.update()
            
        except Exception as e:
            print(f"Error loading hierarchy: {e}")
            self.dropdown.options = [ft.dropdown.Option("error", "Error loading")]
            self.page.update()
    
    def _populate_dropdown(self, hierarchy, depth=0, parent_path=""):
        """Populate dropdown options from hierarchy data"""
        nodes = self._extract_nodes(hierarchy)
        options = [ft.dropdown.Option("all", "📊 All Levels")]
        
        def add_nodes(nodes, current_depth, path_prefix):
            for node in nodes:
                node_id = str(node.get("id", ""))
                node_name = node.get("name", "Unknown")
                level = node.get("level", 0)
                
                # Create indented label based on depth
                indent = "  " * current_depth
                level_icons = {0: "🏢", 1: "📁", 2: "📂", 3: "📋", 4: "📄"}
                icon = level_icons.get(level, "•")
                label = f"{indent}{icon} {node_name}"
                
                current_path = f"{path_prefix}/{node_name}" if path_prefix else node_name
                
                options.append(ft.dropdown.Option(
                    key=node_id,
                    text=label,
                    data={"node": node, "path": current_path, "depth": current_depth}
                ))
                
                # Recursively add children
                children = node.get("children", [])
                if children:
                    add_nodes(children, current_depth + 1, current_path)
        
        add_nodes(nodes, 0, "")
        self.dropdown.options = options
    
    def _handle_change(self, e):
        """Handle dropdown selection change"""
        value = e.control.value
        
        if value == "all" or value == "loading" or value == "none" or value == "error":
            self.selected_node = None
            self.clear_btn.visible = False
        else:
            # Find the selected node
            node = self._find_node_by_id(value)
            self.selected_node = node
            self.clear_btn.visible = True
        
        self.page.update()
        
        # Trigger callback
        if self.on_selection_change:
            self.on_selection_change(self.selected_node)
    
    def _find_node_by_id(self, node_id, nodes=None):
        """Find a node by its ID in the hierarchy"""
        if nodes is None:
            nodes = self.hierarchy_data
        
        for node in nodes:
            if str(node.get("id")) == str(node_id):
                return node
            children = node.get("children", [])
            if children:
                found = self._find_node_by_id(node_id, children)
                if found:
                    return found
        return None

    def _extract_nodes(self, hierarchy):
        """Normalize API hierarchy payload to a list of nodes."""
        if isinstance(hierarchy, dict):
            return hierarchy.get("rootNodes", []) or []
        if isinstance(hierarchy, list):
            return hierarchy
        return []
    
    def _clear_selection(self, e):
        """Clear the current selection"""
        self.dropdown.value = "all"
        self.selected_node = None
        self.clear_btn.visible = False
        self.page.update()
        
        if self.on_selection_change:
            self.on_selection_change(None)
    
    def get_selected_node(self):
        """Get the currently selected node"""
        return self.selected_node
    
    def get_selected_node_id(self):
        """Get the ID of the currently selected node"""
        return self.selected_node.get("id") if self.selected_node else None
    
    def set_selection(self, node_id):
        """Programmatically set the selection"""
        if node_id:
            self.dropdown.value = str(node_id)
            self.selected_node = self._find_node_by_id(node_id)
            self.clear_btn.visible = True
        else:
            self.dropdown.value = "all"
            self.selected_node = None
            self.clear_btn.visible = False
        
        self.page.update()


class HierarchyTreeSelector(ft.Container):
    """
    An alternative tree-view based hierarchy selector for more complex hierarchies.
    Shows the full tree structure in a scrollable panel.
    """
    
    def __init__(self, page, on_selection_change=None):
        super().__init__()
        self.page = page
        self.on_selection_change = on_selection_change
        self.colors = get_theme_colors(page.theme_mode)
        self.auditing_client = AuditingAPIClient()
        
        self.hierarchy_data = []
        self.selected_node = None
        self.expanded_nodes = set()
        
        # Styling
        self.width = 300
        self.height = 400
        self.bgcolor = self.colors.surface
        self.border = ft.border.all(1, self.colors.border)
        self.border_radius = 8
        self.padding = 10
        
        # Build UI
        self._build_ui()
    
    def _build_ui(self):
        """Build the tree selector UI"""
        self.search_field = ft.TextField(
            hint_text="Search hierarchy...",
            prefix_icon=Icons.SEARCH,
            dense=True,
            on_change=self._handle_search,
            border_radius=8
        )
        
        self.tree_container = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            spacing=2
        )
        
        self.content = ft.Column([
            self.search_field,
            ft.Divider(height=1),
            self.tree_container
        ], spacing=10, expand=True)
    
    def load_hierarchy(self):
        """Load hierarchy data"""
        if self.page:
            self.page.run_task(self._load_hierarchy_async)
    
    async def _load_hierarchy_async(self):
        """Async hierarchy loading"""
        try:
            self.tree_container.controls = [
                ft.Container(
                    content=ft.ProgressRing(width=20, height=20),
                    alignment=ft.alignment.center,
                    expand=True
                )
            ]
            self.page.update()
            
            hierarchy = await self.auditing_client.get_audit_universe_hierarchy()
            
            if hierarchy:
                nodes = self._extract_nodes(hierarchy)
                self.hierarchy_data = nodes
                self._render_tree(nodes)
            else:
                self.tree_container.controls = [
                    ft.Text("No hierarchy data", color=self.colors.text_secondary)
                ]
            
            self.page.update()
            
        except Exception as e:
            print(f"Error loading hierarchy: {e}")
            self.tree_container.controls = [
                ft.Text("Error loading hierarchy", color="red")
            ]
            self.page.update()
    
    def _render_tree(self, nodes, depth=0):
        """Render the tree nodes"""
        nodes = self._extract_nodes(nodes)
        self.tree_container.controls.clear()
        
        def add_node(node, current_depth):
            node_id = node.get("id")
            node_name = node.get("name", "Unknown")
            children = node.get("children", [])
            has_children = len(children) > 0
            is_expanded = node_id in self.expanded_nodes
            is_selected = self.selected_node and self.selected_node.get("id") == node_id
            
            # Node row
            row = ft.Row([
                # Indent
                ft.Container(width=current_depth * 20),
                # Expand/collapse button
                ft.IconButton(
                    icon=Icons.EXPAND_MORE if is_expanded else Icons.CHEVRON_RIGHT,
                    icon_size=16,
                    on_click=lambda e, n=node: self._toggle_expand(n),
                    visible=has_children
                ) if has_children else ft.Container(width=32),
                # Node text
                ft.Container(
                    content=ft.Text(
                        node_name,
                        size=13,
                        weight=ft.FontWeight.BOLD if is_selected else ft.FontWeight.NORMAL,
                        color=self.colors.primary if is_selected else self.colors.text_primary
                    ),
                    bgcolor=self.colors.primary + "20" if is_selected else None,
                    padding=ft.padding.symmetric(horizontal=8, vertical=4),
                    border_radius=4,
                    on_click=lambda e, n=node: self._select_node(n),
                    expand=True
                )
            ], spacing=2)
            
            self.tree_container.controls.append(row)
            
            # Render children if expanded
            if has_children and is_expanded:
                for child in children:
                    add_node(child, current_depth + 1)
        
        for node in nodes:
            add_node(node, 0)
    
    def _toggle_expand(self, node):
        """Toggle node expansion"""
        node_id = node.get("id")
        if node_id in self.expanded_nodes:
            self.expanded_nodes.remove(node_id)
        else:
            self.expanded_nodes.add(node_id)
        
        self._render_tree(self.hierarchy_data)
        self.page.update()
    
    def _select_node(self, node):
        """Select a node"""
        self.selected_node = node
        self._render_tree(self.hierarchy_data)
        self.page.update()
        
        if self.on_selection_change:
            self.on_selection_change(node)
    
    def _handle_search(self, e):
        """Handle search input"""
        query = e.control.value.lower()
        if not query:
            self._render_tree(self.hierarchy_data)
        else:
            # Filter nodes matching search
            # For now, just expand all and highlight matches
            # A more sophisticated implementation would filter the tree
            self._render_tree(self.hierarchy_data)
        self.page.update()
    
    def get_selected_node(self):
        """Get the currently selected node"""
        return self.selected_node

    def _extract_nodes(self, hierarchy):
        """Normalize API hierarchy payload to a list of nodes."""
        if isinstance(hierarchy, dict):
            return hierarchy.get("rootNodes", []) or []
        if isinstance(hierarchy, list):
            return hierarchy
        return []
