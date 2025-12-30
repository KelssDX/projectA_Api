import flet as ft
from flet import Icons
from src.api.auditing_client import AuditingAPIClient
from src.utils.theme import (
    get_theme_colors,
    create_modern_card,
    create_modern_button,
    apply_theme_to_control,
)
from src.views.common.base_view import BaseView


class DepartmentsView(BaseView):
    def __init__(self, page):
        self.page = page
        self.departments = []
        self.filtered_departments = []
        self.search_value = ""
        # Resizable panel flex values (filters | table)
        self.left_flex = getattr(self, "left_flex", 1)
        self.center_flex = getattr(self, "center_flex", 4)
        self.auditing_client = AuditingAPIClient()
        colors = get_theme_colors(self.page.theme_mode if hasattr(self.page, "theme_mode") else ft.ThemeMode.LIGHT)
        actions = [
            create_modern_button(colors, "+ Add", icon=Icons.ADD, on_click=self.show_add_department_dialog, style="success", width=120),
            create_modern_button(colors, "Refresh", icon=Icons.REFRESH, on_click=lambda e: self.refresh_departments(), style="secondary", width=120),
        ]
        super().__init__(page, "Departments", on_search=self.on_search_change, actions=actions, colors=colors)
        self._build_ui()
        self.load_departments()  # Load departments from API

    def _open_dialog(self, dialog: ft.AlertDialog):
        if hasattr(self.page, "open"):
            self.page.open(dialog)
            return
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def _close_dialog(self, dialog: ft.AlertDialog):
        if hasattr(self.page, "close"):
            self.page.close(dialog)
            return
        try:
            dialog.open = False
        except Exception:
            if hasattr(self.page, "dialog") and self.page.dialog:
                self.page.dialog.open = False
        self.page.update()

    def _risk_level_to_id(self, risk_level: str):
        mapping = {"High": 1, "Medium": 2, "Low": 3}
        return mapping.get(risk_level, 3)

    def load_departments(self):
        """Load departments from API"""
        if hasattr(self, 'page') and self.page:
            self.page.run_task(self._load_departments_async)

    async def _load_departments_async(self):
        """Load departments data from the API"""
        print("DEBUG: _load_departments_async called")
        try:
            print("DEBUG: Loading departments from src.api...")
            
            # Get departments data from API
            print("DEBUG: Calling auditing_client.get_departments()")
            api_departments = await self.auditing_client.get_departments()
            print(f"DEBUG: API returned {len(api_departments) if api_departments else 0} departments")
            
            if api_departments:
                # Convert API data to dictionaries if needed
                self.departments = []
                for dept_data in api_departments:
                    if isinstance(dept_data, dict):
                        # Normalize keys expected by the UI
                        normalized = {
                            'id': dept_data.get('id') or dept_data.get('Id'),
                            'name': dept_data.get('name') or dept_data.get('Name', 'Unknown'),
                            'head': dept_data.get('head') or dept_data.get('Head'),
                            # Backend model exposes RiskLevelId, map to a readable level if provided
                            'risk_level': dept_data.get('risk_level') or dept_data.get('RiskLevel') or dept_data.get('RiskLevelId'),
                            'assessments': dept_data.get('assessments') or dept_data.get('Assessments', 0)
                        }
                        self.departments.append(normalized)
                    else:
                        # Convert object to dict if needed
                        self.departments.append({
                            'id': getattr(dept_data, 'Id', getattr(dept_data, 'id', None)),
                            'name': getattr(dept_data, 'Name', getattr(dept_data, 'name', 'Unknown')),
                            'head': getattr(dept_data, 'Head', getattr(dept_data, 'head', None)),
                            'risk_level': getattr(dept_data, 'RiskLevel', getattr(dept_data, 'RiskLevelId', None)),
                            'assessments': getattr(dept_data, 'Assessments', getattr(dept_data, 'assessments', 0))
                        })
                
                print(f"Loaded {len(self.departments)} departments from API")
            else:
                print("No departments data available from API")
                self.departments = []
                
            self.filtered_departments = self.departments.copy()
            self.update_department_cards()
            
            if hasattr(self, 'page') and self.page:
                self.page.update()
                
        except Exception as e:
            print(f"Error loading departments from API: {e}")
            self.departments = []
            self.filtered_departments = []
            if hasattr(self, 'page') and self.page:
                self.page.update()

    def _build_ui(self):
        # Use BaseView-provided colors and header; only build filters and body cards here
        colors = self.colors

        self.risk_filter = ft.Dropdown(
            label="Risk Level",
            options=[
                ft.dropdown.Option("All"),
                ft.dropdown.Option("High"),
                ft.dropdown.Option("Medium"),
                ft.dropdown.Option("Low"),
            ],
            value="All",
            on_change=self.filter_departments,
            width=150
        )

        filter_row = ft.Row([
            self.risk_filter,
        ], alignment=ft.MainAxisAlignment.START)

        # Compose cards via BaseView

        # Status message area
        self.status_message = ft.Container(
            visible=False,
            padding=10,
            border_radius=5,
            bgcolor=None,
            content=ft.Text("")
        )

        # Loading indicator
        self.loading_indicator = ft.ProgressRing(
            width=40,
            height=40,
            stroke_width=3,
            visible=False
        )

        # Departments table container
        self.departments_table_container = ft.Container(expand=True, content=None)
        # Build cards under BaseView
        self.cards_column.controls.clear()
        self.add_card(filter_row)
        status_section = ft.Column([
            self.status_message,
            ft.Container(content=self.loading_indicator, alignment=ft.alignment.center, height=40),
        ], spacing=8)
        self.add_card(status_section)
        self.refresh_table()
        self.add_card(self.departments_table_container)

    def refresh_departments(self):
        """Refresh departments from database"""
        self.loading_indicator.visible = True
        self.update()

        try:
            # Direct database connection
            self.load_departments()
            self.update_department_cards()
            self.show_status("Departments refreshed successfully")

            # API version (commented out)
            # response = requests.get(f"{self.api_base_url}/departments")
            # if response.status_code == 200:
            #     self.departments = response.json()
            #     self.filtered_departments = self.departments.copy()
            #     self.update_department_cards()
            #     self.show_status("Departments refreshed successfully")
            # else:
            #     self.show_status(f"Error refreshing: {response.status_code}", is_error=True)
        except Exception as e:
            print(f"Error refreshing departments: {e}")
            self.show_status(f"Error refreshing departments: {str(e)}", is_error=True)

        self.loading_indicator.visible = False
        if hasattr(self, 'page') and self.page:
            self.page.update()

    def update_department_cards(self):
        """Legacy hook used elsewhere – now refreshes the table."""
        self.refresh_table()

    def refresh_table(self):
        """Build a table of departments styled like user_management.py"""
        colors = get_theme_colors(self.page.theme_mode if hasattr(self.page, "theme_mode") else ft.ThemeMode.LIGHT)

        # Header (responsive: stretch main columns)
        header = ft.Container(
            height=40,
            bgcolor=colors.surface,
            border=ft.border.only(bottom=ft.BorderSide(1, colors.border)),
            padding=ft.padding.only(left=30, right=30),
            content=ft.Row([
                ft.Container(expand=2, content=ft.Text("Name", weight=ft.FontWeight.BOLD, color=colors.text_secondary)),
                ft.Container(expand=1, content=ft.Text("Head", weight=ft.FontWeight.BOLD, color=colors.text_secondary)),
                ft.Container(expand=1, content=ft.Text("Risk Level", weight=ft.FontWeight.BOLD, color=colors.text_secondary)),
                ft.Container(expand=1, content=ft.Text("Assessments", weight=ft.FontWeight.BOLD, color=colors.text_secondary)),
                ft.Container(expand=1.5, content=ft.Text("Actions", weight=ft.FontWeight.BOLD, color=colors.text_secondary, text_align=ft.TextAlign.CENTER)),
            ], expand=True)
        )

        # Rows
        rows = ft.Column(spacing=0)
        for i, dept in enumerate(self.filtered_departments):
            rows.controls.append(self.create_department_row(dept, i))

        # Empty state
        if not self.filtered_departments:
            rows.controls.append(
                ft.Container(
                    height=100,
                    alignment=ft.alignment.center,
                    content=ft.Column([
                        ft.Icon(Icons.SEARCH_OFF, size=40, color="#95a5a6"),
                        ft.Text("No departments found", color="#95a5a6", size=16),
                    ], spacing=10, alignment=ft.MainAxisAlignment.CENTER),
                )
            )

        list_view = ft.ListView(expand=True, spacing=0, auto_scroll=False)
        for c in rows.controls:
            list_view.controls.append(c)

        table = ft.Container(
            expand=True,
            content=ft.Column([header, list_view], spacing=0)
        )

        self.departments_table_container.content = table
        if hasattr(self, 'page') and self.page:
            self.page.update()

    # ---- Resizable layout helpers (2-panels) ----
    def _build_resizable_row(self, left_panel, center_panel):
        colors = get_theme_colors(self.page.theme_mode if hasattr(self.page, "theme_mode") else ft.ThemeMode.LIGHT)

        def divider(on_pan_update):
            return ft.GestureDetector(
                on_pan_update=on_pan_update,
                content=ft.Container(width=8, bgcolor=colors.border, border_radius=4)
            )

        def on_drag(e):
            try:
                dx = getattr(e, "delta_x", 0) or 0
                if dx > 2 and self.center_flex > 1:
                    self.left_flex += 1
                    self.center_flex -= 1
                elif dx < -2 and self.left_flex > 1:
                    self.left_flex -= 1
                    self.center_flex += 1
                # Rebuild
                self._main_row.content = self._build_resizable_row(left_panel, center_panel).content
                if hasattr(self, 'page') and self.page:
                    self.page.update()
            except Exception:
                pass

        row = ft.Row([
            ft.Container(expand=self.left_flex, content=left_panel),
            divider(on_drag),
            ft.Container(expand=self.center_flex, content=center_panel),
        ], expand=True, spacing=8, alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        # Store for live rebuilds
        self._main_row = ft.Container(content=row, expand=True)
        return self._main_row

    def create_department_row(self, dept, row_index):
        colors = get_theme_colors(self.page.theme_mode if hasattr(self.page, "theme_mode") else ft.ThemeMode.LIGHT)
        row_bg = colors.surface
        risk_color = self.get_risk_color(dept.get("risk_level"))

        return ft.Container(
            height=60,
            bgcolor=row_bg,
            border=ft.border.only(bottom=ft.BorderSide(1, colors.border)),
            padding=ft.padding.only(left=30, right=30),
            content=ft.Row([
                ft.Container(expand=2, content=ft.Text(dept.get("name", "-"), color=colors.text_primary, overflow=ft.TextOverflow.ELLIPSIS)),
                ft.Container(expand=1, content=ft.Text(dept.get("head", "-"), color=colors.text_primary, overflow=ft.TextOverflow.ELLIPSIS)),
                ft.Container(
                    expand=1,
                    content=ft.Container(
                        width=90,
                        height=30,
                        bgcolor=risk_color,
                        border_radius=15,
                        alignment=ft.alignment.center,
                        content=ft.Text(str(dept.get("risk_level", "-")), color="white", size=12, weight=ft.FontWeight.BOLD),
                    ),
                ),
                ft.Container(expand=1, content=ft.Text(str(dept.get("assessments", 0)), color=colors.text_primary)),
                ft.Container(
                    expand=1.5,
                    content=ft.Row([
                        ft.ElevatedButton(text="View", on_click=lambda e, d=dept: self.view_department_details(d)),
                        ft.Container(width=10),
                        ft.ElevatedButton(text="Edit", on_click=lambda e, d=dept: self.edit_department(d)),
                        ft.Container(width=10),
                        ft.ElevatedButton(text="Delete", on_click=lambda e, d=dept: self.delete_department(d)),
                    ], alignment=ft.MainAxisAlignment.CENTER),
                ),
            ], expand=True)
        )

    def filter_departments(self, e):
        # Get search term and risk level
        search_term = self.search_value or ""
        risk_level = self.risk_filter.value

        # Filter departments based on search term and risk level
        self.filtered_departments = [
            dept for dept in self.departments
            if (search_term == "" or
                search_term in dept["name"].lower() or
                search_term in dept["head"].lower()) and
               (risk_level == "All" or dept["risk_level"] == risk_level)
        ]

        # Update table
        self.refresh_table()

        # Show status message
        if search_term or risk_level != "All":
            count = len(self.filtered_departments)
            total = len(self.departments)
            self.show_status(f"Showing {count} of {total} departments")
        else:
            self.hide_status()

    def show_add_department_dialog(self, e):
        # Create form fields
        name_field = ft.TextField(
            label="Department Name",
            autofocus=True,
            border_radius=5
        )

        head_field = ft.TextField(
            label="Department Head",
            border_radius=5
        )

        risk_level_dropdown = ft.Dropdown(
            label="Risk Level",
            options=[
                ft.dropdown.Option("High"),
                ft.dropdown.Option("Medium"),
                ft.dropdown.Option("Low"),
            ],
            value="Medium",
            width=200
        )

        # Define dialog close function
        def close_dialog(e):
            self._close_dialog(dialog)

        # Define save function
        def save_department(e):
            # Validate fields
            if not name_field.value or not head_field.value:
                return

            self.page.run_task(
                self._create_department_async,
                dialog,
                name_field.value,
                head_field.value,
                risk_level_dropdown.value,
            )

        # Create dialog
        dialog = ft.AlertDialog(
            title=ft.Text("Add New Department"),
            content=ft.Column([
                name_field,
                head_field,
                risk_level_dropdown,
            ], tight=True, spacing=20, height=200),
            actions=[
                ft.TextButton("Cancel", on_click=close_dialog),
                ft.ElevatedButton("Save", on_click=save_department, bgcolor="#3498db", color="white"),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        # Show dialog
        self._open_dialog(dialog)

    async def _create_department_async(self, dialog, name: str, head: str, risk_level: str):
        try:
            payload = {
                "name": name,
                "head": head,
                "riskLevelId": self._risk_level_to_id(risk_level),
                "assessments": 0,
            }
            await self.auditing_client.create_department(payload)
            self._close_dialog(dialog)
            await self._load_departments_async()
            self.show_status(f"Department '{name}' added successfully")
        except Exception as ex:
            print(f"Error adding department: {ex}")
            self.show_status(f"Error adding department: {str(ex)}", is_error=True)
        if hasattr(self, 'page') and self.page:
            self.page.update()

    def edit_department(self, dept):
        # Create form fields
        name_field = ft.TextField(
            label="Department Name",
            value=dept["name"],
            autofocus=True,
            border_radius=5
        )

        head_field = ft.TextField(
            label="Department Head",
            value=dept["head"],
            border_radius=5
        )

        risk_level_dropdown = ft.Dropdown(
            label="Risk Level",
            options=[
                ft.dropdown.Option("High"),
                ft.dropdown.Option("Medium"),
                ft.dropdown.Option("Low"),
            ],
            value=dept["risk_level"],
            width=200
        )

        # Define dialog close function
        def close_dialog(e):
            self._close_dialog(dialog)

        # Define update function
        def update_department(e):
            # Validate fields
            if not name_field.value or not head_field.value:
                return

            self.page.run_task(
                self._update_department_async,
                dialog,
                dept.get("id"),
                name_field.value,
                head_field.value,
                risk_level_dropdown.value,
                dept.get("assessments", 0),
            )

        # Create dialog
        dialog = ft.AlertDialog(
            title=ft.Text(f"Edit Department: {dept['name']}"),
            content=ft.Column([
                name_field,
                head_field,
                risk_level_dropdown,
            ], tight=True, spacing=20, height=200),
            actions=[
                ft.TextButton("Cancel", on_click=close_dialog),
                ft.ElevatedButton("Update", on_click=update_department, bgcolor="#3498db", color="white"),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        # Show dialog
        self._open_dialog(dialog)

    async def _update_department_async(self, dialog, dept_id, name: str, head: str, risk_level: str, assessments: int):
        try:
            payload = {
                "id": dept_id,
                "name": name,
                "head": head,
                "riskLevelId": self._risk_level_to_id(risk_level),
                "assessments": assessments,
            }
            await self.auditing_client.update_department(dept_id, payload)
            self._close_dialog(dialog)
            await self._load_departments_async()
            self.show_status(f"Department '{name}' updated successfully")
        except Exception as ex:
            print(f"Error updating department: {ex}")
            self.show_status(f"Error updating department: {str(ex)}", is_error=True)
        if hasattr(self, 'page') and self.page:
            self.page.update()

    def delete_department(self, dept):
        # Define dialog close function
        def close_dialog(e):
            self._close_dialog(dialog)

        # Define delete function
        def confirm_delete(e):
            self.page.run_task(self._delete_department_async, dialog, dept.get("id"), dept.get("name", "Department"))

        # Create dialog
        dialog = ft.AlertDialog(
            title=ft.Text("Confirm Delete"),
            content=ft.Text(f"Are you sure you want to delete the department '{dept['name']}'?"),
            actions=[
                ft.TextButton("Cancel", on_click=close_dialog),
                ft.ElevatedButton("Delete", on_click=confirm_delete, bgcolor="#e74c3c", color="white"),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        # Show dialog
        self._open_dialog(dialog)

    async def _delete_department_async(self, dialog, dept_id, dept_name):
        try:
            await self.auditing_client.delete_department(dept_id)
            self._close_dialog(dialog)
            await self._load_departments_async()
            self.show_status(f"Department '{dept_name}' deleted successfully")
        except Exception as ex:
            print(f"Error deleting department: {ex}")
            self.show_status(f"Error deleting department: {str(ex)}", is_error=True)
        if hasattr(self, 'page') and self.page:
            self.page.update()

    def view_department_details(self, dept):
        colors = get_theme_colors(self.page.theme_mode if hasattr(self.page, "theme_mode") else ft.ThemeMode.LIGHT)
        risk_color = self.get_risk_color(dept.get("risk_level"))

        dialog = ft.AlertDialog(
            title=ft.Text(f"Department: {dept.get('name', '-') }"),
            content=ft.Column([
                ft.Row([ft.Text("Head:", weight=ft.FontWeight.BOLD), ft.Text(str(dept.get("head", "-")))]),
                ft.Row([ft.Text("Risk Level:", weight=ft.FontWeight.BOLD), ft.Text(str(dept.get("risk_level", "-")), color=risk_color)]),
                ft.Row([ft.Text("Assessments:", weight=ft.FontWeight.BOLD), ft.Text(str(dept.get("assessments", 0)))]),
            ], tight=True, spacing=10),
            actions=[ft.TextButton("Close", on_click=lambda e: self._close_dialog(dialog))],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self._open_dialog(dialog)

    def show_status(self, message, is_error=False):
        # Set message color and background
        if is_error:
            self.status_message.bgcolor = None
            self.status_message.content = ft.Text(message)
        else:
            self.status_message.bgcolor = None
            self.status_message.content = ft.Text(message)

        # Show message
        self.status_message.visible = True
        self.update()

    def hide_status(self):
        # Hide message
        self.status_message.visible = False
        self.update()

    def get_risk_color(self, risk_level):
        # Return color based on risk level
        if risk_level == "High":
            return "#e74c3c"  # Red
        elif risk_level == "Medium":
            return "#f39c12"  # Orange
        else:
            return "#2ecc71"  # Green

    def on_search_change(self, e):
        """Update search value from input and refilter."""
        try:
            self.search_value = (e.control.value or "").lower()
        except Exception:
            self.search_value = ""
        self.filter_departments(None)

    def apply_theme(self, colors):
        """Apply theme colors to the departments view"""
        try:
            self.bgcolor = colors.bg
            # Rebuild like Dashboard so token-based borders/backgrounds update
            self._build_ui()
            apply_theme_to_control(self, colors)
            if hasattr(self, 'page') and self.page:
                self.page.update()
        except Exception as e:
            print(f"Error applying theme to departments view: {e}")
