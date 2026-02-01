import flet as ft
from flet import Icons
from src.api.auditing_client import AuditingAPIClient
from src.utils.theme import (
    get_theme_colors,
    create_modern_card,
    create_modern_button,
)
from src.views.common.base_view import BaseView


class AuditUniverseView(BaseView):
    """
    Audit Universe Hierarchy Management View
    Displays a tree structure of auditable entities with CRUD operations
    """

    def __init__(self, page):
        self.page = page
        self.hierarchy_data = None
        self.levels = []
        self.departments = []
        self.selected_node = None
        self.expanded_nodes = set()
        self.search_value = ""
        self.auditing_client = AuditingAPIClient()

        colors = get_theme_colors(
            self.page.theme_mode if hasattr(self.page, "theme_mode") else ft.ThemeMode.LIGHT
        )

        actions = [
            create_modern_button(colors, "+ Add Node", icon=Icons.ADD, on_click=self.show_add_node_dialog, style="success", width=130),
            create_modern_button(colors, "Expand All", icon=Icons.UNFOLD_MORE, on_click=self.expand_all, style="secondary", width=120),
            create_modern_button(colors, "Collapse All", icon=Icons.UNFOLD_LESS, on_click=self.collapse_all, style="secondary", width=120),
            create_modern_button(colors, "Refresh", icon=Icons.REFRESH, on_click=lambda e: self.refresh_hierarchy(), style="secondary", width=100),
        ]

        super().__init__(page, "Audit Universe", on_search=self.on_search_change, actions=actions, colors=colors)
        self._build_ui()
        self.load_data()

    def _build_ui(self):
        """Build the main UI components"""
        colors = self.colors

        # Status message area
        self.status_message = ft.Container(
            visible=False,
            padding=10,
            border_radius=5,
            content=ft.Text("")
        )

        # Loading indicator
        self.loading_indicator = ft.ProgressRing(
            width=40, height=40, stroke_width=3, visible=False
        )

        # Level filter dropdown
        self.level_filter = ft.Dropdown(
            label="Filter by Level",
            options=[ft.dropdown.Option("All")],
            value="All",
            on_change=self.filter_by_level,
            width=180
        )

        # Risk rating filter
        self.risk_filter = ft.Dropdown(
            label="Risk Rating",
            options=[
                ft.dropdown.Option("All"),
                ft.dropdown.Option("High"),
                ft.dropdown.Option("Medium"),
                ft.dropdown.Option("Low"),
            ],
            value="All",
            on_change=self.filter_by_risk,
            width=150
        )

        filter_row = ft.Row([
            self.level_filter,
            self.risk_filter,
        ], alignment=ft.MainAxisAlignment.START)

        # Main layout: Tree (left) + Details Panel (right)
        self.tree_container = ft.Container(
            expand=3,
            bgcolor=colors.card_bg,
            border_radius=8,
            padding=15,
            content=ft.Column(
                controls=[ft.Text("Loading hierarchy...", color=colors.text_secondary)],
                scroll=ft.ScrollMode.AUTO,
                expand=True
            )
        )

        self.detail_panel = ft.Container(
            expand=2,
            bgcolor=colors.card_bg,
            border_radius=8,
            padding=15,
            content=self._build_empty_detail_panel()
        )

        main_content = ft.Row(
            controls=[self.tree_container, self.detail_panel],
            expand=True,
            spacing=15
        )

        # Build cards via BaseView
        self.cards_column.controls.clear()
        self.add_card(filter_row)
        self.add_card(ft.Column([
            self.status_message,
            ft.Container(content=self.loading_indicator, alignment=ft.alignment.center, height=40),
        ], spacing=8))
        self.add_card(main_content)

    def _build_empty_detail_panel(self):
        """Build placeholder for detail panel when no node selected"""
        colors = self.colors
        return ft.Column(
            controls=[
                ft.Icon(Icons.ACCOUNT_TREE, size=48, color=colors.text_secondary),
                ft.Text("Select a node", size=18, weight=ft.FontWeight.BOLD, color=colors.text_primary),
                ft.Text("Click on a node in the tree to view its details",
                        color=colors.text_secondary, text_align=ft.TextAlign.CENTER),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            expand=True
        )

    def _build_detail_panel(self, node):
        """Build detail panel for selected node"""
        colors = self.colors

        # Risk rating badge color
        risk_colors = {
            "High": "#EF4444",
            "Medium": "#F59E0B",
            "Low": "#10B981",
            "Critical": "#DC2626"
        }
        risk_color = risk_colors.get(node.get("riskRating", "Medium"), "#6B7280")

        # Level icon
        level_icons = {
            1: Icons.BUSINESS,
            2: Icons.DOMAIN,
            3: Icons.SETTINGS,
            4: Icons.TASK_ALT
        }
        level_icon = level_icons.get(node.get("level", 1), Icons.FOLDER)

        return ft.Column(
            controls=[
                # Header
                ft.Row([
                    ft.Icon(level_icon, size=32, color=colors.primary),
                    ft.Column([
                        ft.Text(node.get("name", "Unknown"), size=20, weight=ft.FontWeight.BOLD, color=colors.text_primary),
                        ft.Text(f"Code: {node.get('code', 'N/A')}", size=12, color=colors.text_secondary),
                    ], spacing=2, expand=True),
                    ft.Container(
                        content=ft.Text(node.get("riskRating", "Medium"), color="white", size=12, weight=ft.FontWeight.BOLD),
                        bgcolor=risk_color,
                        padding=ft.padding.symmetric(horizontal=12, vertical=4),
                        border_radius=12,
                    )
                ], alignment=ft.MainAxisAlignment.START),

                ft.Divider(height=20),

                # Details section
                self._build_detail_row("Level", f"{node.get('levelName', 'Unknown')} (Level {node.get('level', 1)})"),
                self._build_detail_row("Owner", node.get("owner") or "Not assigned"),
                self._build_detail_row("Description", node.get("description") or "No description"),
                self._build_detail_row("Last Audit", str(node.get("lastAuditDate") or "Never")),
                self._build_detail_row("Next Audit", str(node.get("nextAuditDate") or "Not scheduled")),
                self._build_detail_row("Audit Frequency", f"Every {node.get('auditFrequencyMonths', 12)} months"),
                self._build_detail_row("Children", str(node.get("childCount", 0))),
                self._build_detail_row("Open Findings", str(node.get("openFindingsCount", 0))),

                ft.Divider(height=20),

                # Action buttons
                ft.Row([
                    create_modern_button(colors, "Edit", icon=Icons.EDIT, on_click=lambda e: self.show_edit_node_dialog(node), style="primary", width=100),
                    create_modern_button(colors, "Add Child", icon=Icons.ADD, on_click=lambda e: self.show_add_node_dialog(e, parent_id=node.get("id")), style="success", width=110),
                    create_modern_button(colors, "Delete", icon=Icons.DELETE, on_click=lambda e: self.confirm_delete_node(node), style="danger", width=100),
                ], spacing=10, wrap=True),
            ],
            spacing=10,
            scroll=ft.ScrollMode.AUTO,
            expand=True
        )

    def _build_detail_row(self, label, value):
        """Build a detail row for the panel"""
        colors = self.colors
        return ft.Row([
            ft.Text(f"{label}:", weight=ft.FontWeight.BOLD, color=colors.text_secondary, width=120),
            ft.Text(value, color=colors.text_primary, expand=True),
        ])

    def _build_tree_node(self, node, depth=0):
        """Recursively build a tree node"""
        colors = self.colors
        node_id = node.get("id")
        is_expanded = node_id in self.expanded_nodes
        children = node.get("children", [])
        has_children = len(children) > 0

        # Risk rating colors
        risk_colors = {
            "High": "#EF4444",
            "Medium": "#F59E0B",
            "Low": "#10B981",
            "Critical": "#DC2626"
        }
        risk_color = risk_colors.get(node.get("riskRating", "Medium"), "#6B7280")

        # Level icons
        level_icons = {
            1: Icons.BUSINESS,
            2: Icons.DOMAIN,
            3: Icons.SETTINGS,
            4: Icons.TASK_ALT
        }
        level_icon = level_icons.get(node.get("level", 1), Icons.FOLDER)

        # Expand/collapse icon
        expand_icon = Icons.EXPAND_MORE if is_expanded else Icons.CHEVRON_RIGHT
        if not has_children:
            expand_icon = Icons.REMOVE  # Leaf node indicator

        def toggle_expand(e):
            if has_children:
                if node_id in self.expanded_nodes:
                    self.expanded_nodes.remove(node_id)
                else:
                    self.expanded_nodes.add(node_id)
                self.refresh_tree_display()

        def select_node(e):
            self.selected_node = node
            self.detail_panel.content = self._build_detail_panel(node)
            self.page.update()

        is_selected = self.selected_node and self.selected_node.get("id") == node_id

        node_row = ft.Container(
            content=ft.Row([
                # Indentation
                ft.Container(width=depth * 24),
                # Expand icon
                ft.IconButton(
                    icon=expand_icon,
                    icon_size=18,
                    on_click=toggle_expand if has_children else None,
                    disabled=not has_children,
                    style=ft.ButtonStyle(padding=0),
                ),
                # Level icon
                ft.Icon(level_icon, size=18, color=colors.primary),
                # Node name
                ft.Text(
                    node.get("name", "Unknown"),
                    weight=ft.FontWeight.BOLD if is_selected else ft.FontWeight.NORMAL,
                    color=colors.primary if is_selected else colors.text_primary,
                    expand=True
                ),
                # Risk badge
                ft.Container(
                    content=ft.Text(node.get("riskRating", "M")[0], color="white", size=10, weight=ft.FontWeight.BOLD),
                    bgcolor=risk_color,
                    width=22,
                    height=22,
                    border_radius=11,
                    alignment=ft.alignment.center,
                    tooltip=f"Risk: {node.get('riskRating', 'Medium')}"
                ),
                # Findings count
                ft.Container(
                    content=ft.Text(str(node.get("openFindingsCount", 0)), size=10, color=colors.text_secondary),
                    tooltip="Open Findings",
                    visible=node.get("openFindingsCount", 0) > 0
                ),
            ], spacing=5),
            padding=ft.padding.symmetric(vertical=4, horizontal=8),
            border_radius=6,
            bgcolor=colors.primary + "15" if is_selected else "transparent",
            on_click=select_node,
            on_hover=lambda e: setattr(e.control, 'bgcolor', colors.primary + "10" if e.data == "true" and not is_selected else (colors.primary + "15" if is_selected else "transparent")) or e.control.update()
        )

        result = [node_row]

        # Add children if expanded
        if is_expanded and has_children:
            for child in children:
                result.extend(self._build_tree_node(child, depth + 1))

        return result

    def refresh_tree_display(self):
        """Refresh the tree display without reloading data"""
        if not self.hierarchy_data:
            return

        root_nodes = self.hierarchy_data.get("rootNodes", [])
        tree_controls = []

        for node in root_nodes:
            tree_controls.extend(self._build_tree_node(node))

        if not tree_controls:
            tree_controls = [ft.Text("No audit universe nodes found", color=self.colors.text_secondary)]

        self.tree_container.content = ft.Column(
            controls=tree_controls,
            scroll=ft.ScrollMode.AUTO,
            expand=True
        )
        self.page.update()

    def load_data(self):
        """Load hierarchy and supporting data"""
        if hasattr(self, 'page') and self.page:
            self.page.run_task(self._load_data_async)

    async def _load_data_async(self):
        """Async data loading"""
        self.loading_indicator.visible = True
        self.page.update()

        try:
            # Load hierarchy, levels, and departments in parallel
            import asyncio
            hierarchy_task = self.auditing_client.get_audit_universe_hierarchy()
            levels_task = self.auditing_client.get_audit_universe_levels()
            departments_task = self.auditing_client.get_departments()

            results = await asyncio.gather(
                hierarchy_task, levels_task, departments_task,
                return_exceptions=True
            )

            # Process hierarchy
            if not isinstance(results[0], Exception):
                self.hierarchy_data = results[0]
            else:
                print(f"Error loading hierarchy: {results[0]}")
                self.hierarchy_data = {"rootNodes": [], "totalNodes": 0}

            # Process levels
            if not isinstance(results[1], Exception) and results[1]:
                self.levels = results[1]
                # Update level filter dropdown
                level_options = [ft.dropdown.Option("All")]
                for level in self.levels:
                    level_options.append(ft.dropdown.Option(level.get("name", f"Level {level.get('level')}")))
                self.level_filter.options = level_options
            else:
                print(f"Error loading levels: {results[1]}")

            # Process departments
            if not isinstance(results[2], Exception) and results[2]:
                self.departments = results[2]
            else:
                print(f"Error loading departments: {results[2]}")

            # Refresh display
            self.refresh_tree_display()

        except Exception as e:
            print(f"Error loading audit universe data: {e}")
            self.show_status(f"Error loading data: {str(e)}", is_error=True)

        self.loading_indicator.visible = False
        self.page.update()

    def refresh_hierarchy(self):
        """Refresh hierarchy data"""
        self.selected_node = None
        self.detail_panel.content = self._build_empty_detail_panel()
        self.load_data()

    def expand_all(self, e=None):
        """Expand all nodes"""
        def collect_ids(node):
            ids = [node.get("id")]
            for child in node.get("children", []):
                ids.extend(collect_ids(child))
            return ids

        if self.hierarchy_data:
            for root in self.hierarchy_data.get("rootNodes", []):
                self.expanded_nodes.update(collect_ids(root))
        self.refresh_tree_display()

    def collapse_all(self, e=None):
        """Collapse all nodes"""
        self.expanded_nodes.clear()
        self.refresh_tree_display()

    def filter_by_level(self, e):
        """Filter tree by level"""
        # For now just refresh - full filtering would require more complex logic
        self.refresh_tree_display()

    def filter_by_risk(self, e):
        """Filter tree by risk rating"""
        self.refresh_tree_display()

    def on_search_change(self, e):
        """Handle search input"""
        self.search_value = e.control.value if hasattr(e, 'control') else ""
        # Implement search filtering
        self.refresh_tree_display()

    def show_status(self, message, is_error=False):
        """Show status message"""
        self.status_message.content = ft.Text(message, color="red" if is_error else "green")
        self.status_message.bgcolor = "#FEE2E2" if is_error else "#D1FAE5"
        self.status_message.visible = True
        self.page.update()

    def _open_dialog(self, dialog):
        if hasattr(self.page, "open"):
            self.page.open(dialog)
        else:
            self.page.dialog = dialog
            dialog.open = True
        self.page.update()

    def _close_dialog(self, dialog):
        if hasattr(self.page, "close"):
            self.page.close(dialog)
        else:
            dialog.open = False
        self.page.update()

    def show_add_node_dialog(self, e=None, parent_id=None):
        """Show dialog to add a new node"""
        colors = self.colors

        name_field = ft.TextField(label="Name", autofocus=True)
        code_field = ft.TextField(label="Code (unique)")
        description_field = ft.TextField(label="Description", multiline=True, min_lines=2)
        owner_field = ft.TextField(label="Owner")

        risk_dropdown = ft.Dropdown(
            label="Risk Rating",
            options=[
                ft.dropdown.Option("High"),
                ft.dropdown.Option("Medium"),
                ft.dropdown.Option("Low"),
            ],
            value="Medium",
            width=200
        )

        frequency_field = ft.TextField(label="Audit Frequency (months)", value="12", width=200)

        # Parent selector
        parent_options = [ft.dropdown.Option(key="", text="None (Root Level)")]
        if self.hierarchy_data:
            for node in self._flatten_hierarchy(self.hierarchy_data.get("rootNodes", [])):
                parent_options.append(ft.dropdown.Option(
                    key=str(node.get("id")),
                    text=f"{'  ' * (node.get('level', 1) - 1)}{node.get('name')}"
                ))

        parent_dropdown = ft.Dropdown(
            label="Parent Node",
            options=parent_options,
            value=str(parent_id) if parent_id else "",
        )

        async def save_node(e):
            if not name_field.value or not code_field.value:
                self.show_status("Name and Code are required", is_error=True)
                return

            node_data = {
                "name": name_field.value,
                "code": code_field.value,
                "description": description_field.value,
                "owner": owner_field.value,
                "riskRating": risk_dropdown.value,
                "auditFrequencyMonths": int(frequency_field.value or 12),
                "parentId": int(parent_dropdown.value) if parent_dropdown.value else None
            }

            try:
                result = await self.auditing_client.create_audit_universe_node(node_data)
                self._close_dialog(dialog)
                self.show_status("Node created successfully")
                self.refresh_hierarchy()
            except Exception as ex:
                self.show_status(f"Error creating node: {str(ex)}", is_error=True)

        def on_save(e):
            self.page.run_task(save_node, e)

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Add Audit Universe Node"),
            content=ft.Column([
                name_field,
                code_field,
                parent_dropdown,
                description_field,
                ft.Row([risk_dropdown, frequency_field], spacing=10),
                owner_field,
            ], tight=True, spacing=10, width=400, scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: self._close_dialog(dialog)),
                create_modern_button(colors, "Save", icon=Icons.SAVE, on_click=on_save, style="success"),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self._open_dialog(dialog)

    def show_edit_node_dialog(self, node):
        """Show dialog to edit a node"""
        colors = self.colors

        name_field = ft.TextField(label="Name", value=node.get("name", ""))
        code_field = ft.TextField(label="Code", value=node.get("code", ""))
        description_field = ft.TextField(label="Description", value=node.get("description", ""), multiline=True, min_lines=2)
        owner_field = ft.TextField(label="Owner", value=node.get("owner", ""))

        risk_dropdown = ft.Dropdown(
            label="Risk Rating",
            options=[
                ft.dropdown.Option("High"),
                ft.dropdown.Option("Medium"),
                ft.dropdown.Option("Low"),
            ],
            value=node.get("riskRating", "Medium"),
            width=200
        )

        frequency_field = ft.TextField(label="Audit Frequency (months)", value=str(node.get("auditFrequencyMonths", 12)), width=200)

        async def save_changes(e):
            node_data = {
                "id": node.get("id"),
                "name": name_field.value,
                "code": code_field.value,
                "description": description_field.value,
                "owner": owner_field.value,
                "riskRating": risk_dropdown.value,
                "auditFrequencyMonths": int(frequency_field.value or 12),
                "parentId": node.get("parentId"),
                "level": node.get("level", 1),
                "levelName": node.get("levelName"),
                "isActive": True
            }

            try:
                result = await self.auditing_client.update_audit_universe_node(node.get("id"), node_data)
                self._close_dialog(dialog)
                self.show_status("Node updated successfully")
                self.refresh_hierarchy()
            except Exception as ex:
                self.show_status(f"Error updating node: {str(ex)}", is_error=True)

        def on_save(e):
            self.page.run_task(save_changes, e)

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Edit: {node.get('name', 'Node')}"),
            content=ft.Column([
                name_field,
                code_field,
                description_field,
                ft.Row([risk_dropdown, frequency_field], spacing=10),
                owner_field,
            ], tight=True, spacing=10, width=400, scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: self._close_dialog(dialog)),
                create_modern_button(colors, "Save", icon=Icons.SAVE, on_click=on_save, style="success"),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self._open_dialog(dialog)

    def confirm_delete_node(self, node):
        """Show confirmation dialog before deleting"""
        colors = self.colors

        async def delete_node(e):
            try:
                result = await self.auditing_client.delete_audit_universe_node(node.get("id"))
                self._close_dialog(dialog)
                if result:
                    self.show_status("Node deleted successfully")
                    self.selected_node = None
                    self.detail_panel.content = self._build_empty_detail_panel()
                    self.refresh_hierarchy()
                else:
                    self.show_status("Failed to delete node", is_error=True)
            except Exception as ex:
                self.show_status(f"Error deleting node: {str(ex)}", is_error=True)

        def on_delete(e):
            self.page.run_task(delete_node, e)

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirm Delete"),
            content=ft.Text(f"Are you sure you want to delete '{node.get('name')}'?\n\nChildren will be moved to the parent node."),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: self._close_dialog(dialog)),
                create_modern_button(colors, "Delete", icon=Icons.DELETE, on_click=on_delete, style="danger"),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self._open_dialog(dialog)

    def _flatten_hierarchy(self, nodes, result=None):
        """Flatten hierarchy for dropdown options"""
        if result is None:
            result = []
        for node in nodes:
            result.append(node)
            if node.get("children"):
                self._flatten_hierarchy(node.get("children"), result)
        return result
