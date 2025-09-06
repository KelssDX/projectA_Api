import flet as ft
from flet import Icons
from src.api.auditing_client import AuditingAPIClient
from src.utils.theme import (
    get_theme_colors,
    create_modern_card,
    create_modern_button,
    apply_theme_to_control,
)


class DepartmentsView(ft.Container):
    def __init__(self, page):
        super().__init__()
        self.page = page
        self.departments = []
        self.filtered_departments = []
        self.search_value = ""
        # Resizable panel flex values (filters | table)
        self.left_flex = getattr(self, "left_flex", 1)
        self.center_flex = getattr(self, "center_flex", 4)
        self.auditing_client = AuditingAPIClient()
        self._build_ui()
        self.load_departments()  # Load departments from API

    def load_departments(self):
        """Load departments from API"""
        if hasattr(self, 'page') and self.page:
            self.page.run_task(self._load_departments_async)

    async def _load_departments_async(self):
        """Load departments data from the API"""
        print("🔧 DEBUG: _load_departments_async called")
        try:
            print("🔧 DEBUG: Loading departments from src.api...")
            
            # Get departments data from API
            print("🔧 DEBUG: Calling auditing_client.get_departments()")
            api_departments = await self.auditing_client.get_departments()
            print(f"🔧 DEBUG: API returned {len(api_departments) if api_departments else 0} departments")
            
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
        colors = get_theme_colors(self.page.theme_mode if hasattr(self.page, "theme_mode") else ft.ThemeMode.LIGHT)

        # Search and filter controls (styled like user_management.py)
        self._search_input = ft.TextField(
            border=ft.InputBorder.NONE,
            color="#2c3e50",
            hint_text="Search departments",
            hint_style=ft.TextStyle(color="#95a5a6", size=14),
            expand=True,
            height=30,
            content_padding=5,
            on_change=self.on_search_change,
        )
        self.search_field = ft.Container(
            width=240,
            height=30,
            bgcolor="#f5f7fa",
            border=ft.border.all(1, "#e6e9ed"),
            border_radius=15,
            padding=ft.padding.only(left=10, right=10),
            content=ft.Row([
                ft.Icon(Icons.SEARCH, color="#95a5a6", size=18),
                self._search_input,
            ])
        )

        header = ft.Container(
            content=ft.Row([
                ft.Column([
                    ft.Text("Departments", size=24, weight=ft.FontWeight.BOLD, color=colors.text_primary),
                    ft.Text("Manage organizational departments", size=14, color=colors.text_secondary),
                ], alignment=ft.CrossAxisAlignment.START),
                ft.Row([
                    self.search_field,
                ], spacing=12)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        )

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

        filters_card = create_modern_card(
            colors,
            ft.Row([
                filter_row
            ], alignment=ft.MainAxisAlignment.START)
        )

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
        self.refresh_table()

        # Top panel: search + risk filter + actions
        top_panel = create_modern_card(
            colors,
            ft.Column([
                ft.Row([self.risk_filter], spacing=10),
                ft.Row([
                    ft.Container(expand=True),
                    create_modern_button(colors, "Add Department", icon=Icons.ADD, on_click=self.show_add_department_dialog, style="success"),
                    create_modern_button(colors, "Refresh", icon=Icons.REFRESH, on_click=lambda e: self.refresh_departments(), style="secondary"),
                ], alignment=ft.MainAxisAlignment.END)
            ], spacing=10)
        )


        main_content = ft.Column([
            header,
            ft.Container(height=16),
            top_panel,
            ft.Container(height=12),
            self.status_message,
            ft.Container(content=self.loading_indicator, alignment=ft.alignment.center, height=40),
            create_modern_card(colors, self.departments_table_container),
        ], spacing=0, expand=True)

        self.content = ft.Container(
            content=main_content,
            padding=ft.padding.all(24),
            bgcolor=colors.bg,
            expand=True,
        )
        self.bgcolor = colors.bg
        self.expand = True

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
        self.update()

    def update_department_cards(self):
        """Legacy hook used elsewhere – now refreshes the table."""
        self.refresh_table()

    def refresh_table(self):
        """Build a table of departments styled like user_management.py"""
        colors = get_theme_colors(self.page.theme_mode if hasattr(self.page, "theme_mode") else ft.ThemeMode.LIGHT)

        # Header
        header = ft.Container(
            height=40,
            bgcolor=None,
            border=ft.border.only(bottom=ft.BorderSide(1, colors.border)),
            padding=ft.padding.only(left=30, right=30),
            content=ft.Row([
                ft.Container(width=240, content=ft.Text("Name", weight=ft.FontWeight.BOLD, color=colors.text_secondary)),
                ft.Container(width=220, content=ft.Text("Head", weight=ft.FontWeight.BOLD, color=colors.text_secondary)),
                ft.Container(width=150, content=ft.Text("Risk Level", weight=ft.FontWeight.BOLD, color=colors.text_secondary)),
                ft.Container(width=150, content=ft.Text("Assessments", weight=ft.FontWeight.BOLD, color=colors.text_secondary)),
                ft.Container(width=200, content=ft.Text("Actions", weight=ft.FontWeight.BOLD, color=colors.text_secondary, text_align=ft.TextAlign.CENTER)),
            ])
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
        self.update()

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
                ft.Container(width=240, content=ft.Text(dept.get("name", "-"), color=colors.text_primary)),
                ft.Container(width=220, content=ft.Text(dept.get("head", "-"), color=colors.text_primary)),
                ft.Container(
                    width=150,
                    content=ft.Container(
                        width=90,
                        height=30,
                        bgcolor=risk_color,
                        border_radius=15,
                        alignment=ft.alignment.center,
                        content=ft.Text(str(dept.get("risk_level", "-")), color="white", size=12, weight=ft.FontWeight.BOLD),
                    ),
                ),
                ft.Container(width=150, content=ft.Text(str(dept.get("assessments", 0)), color=colors.text_primary)),
                ft.Container(
                    width=200,
                    content=ft.Row([
                        ft.Container(
                            width=40,
                            height=30,
                            bgcolor="#3498db",
                            border_radius=5,
                            alignment=ft.alignment.center,
                            content=ft.Icon(Icons.VISIBILITY, color="white", size=16),
                            on_click=lambda e, d=dept: self.view_department_details(d),
                        ),
                        ft.Container(width=10),
                        ft.Container(
                            width=40,
                            height=30,
                            bgcolor="#2ecc71",
                            border_radius=5,
                            alignment=ft.alignment.center,
                            content=ft.Icon(Icons.EDIT, color="white", size=16),
                            on_click=lambda e, d=dept: self.edit_department(d),
                        ),
                        ft.Container(width=10),
                        ft.Container(
                            width=40,
                            height=30,
                            bgcolor="#e74c3c",
                            border_radius=5,
                            alignment=ft.alignment.center,
                            content=ft.Icon(Icons.DELETE, color="white", size=16),
                            on_click=lambda e, d=dept: self.delete_department(d),
                        ),
                    ], alignment=ft.MainAxisAlignment.CENTER),
                ),
            ])
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
            dialog.open = False
            self.page.update()

        # Define save function
        def save_department(e):
            # Validate fields
            if not name_field.value or not head_field.value:
                return

            # Create new department
            try:
                # Direct database connection
                conn = get_db_connection()
                cursor = conn.cursor(cursor_factory=RealDictCursor)
                cursor.execute("""
                    INSERT INTO departments (name, head, risk_level, assessments)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id, name, head, risk_level, assessments
                """, (name_field.value, head_field.value, risk_level_dropdown.value, 0))

                new_dept = cursor.fetchone()
                conn.commit()
                cursor.close()
                conn.close()

                # Convert to a regular dictionary
                new_dept = dict(new_dept)

                # API version (commented out)
                # new_dept_data = {
                #     "name": name_field.value,
                #     "head": head_field.value,
                #     "risk_level": risk_level_dropdown.value,
                #     "assessments": 0
                # }
                # response = requests.post(f"{self.api_base_url}/departments", json=new_dept_data)
                # if response.status_code == 201:
                #     new_dept = response.json()

                # Add to departments list
                self.departments.append(new_dept)
                self.filtered_departments = self.departments.copy()

                # Close dialog
                close_dialog(e)

                # Update department cards
                self.update_department_cards()

                # Show success message
                self.show_status(f"Department '{new_dept['name']}' added successfully")
            except Exception as ex:
                print(f"Error adding department: {ex}")
                self.show_status(f"Error adding department: {str(ex)}", is_error=True)

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
        self.page.dialog = dialog
        dialog.open = True
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
            dialog.open = False
            self.page.update()

        # Define update function
        def update_department(e):
            # Validate fields
            if not name_field.value or not head_field.value:
                return

            try:
                # Direct database connection
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE departments
                    SET name = %s, head = %s, risk_level = %s
                    WHERE id = %s
                """, (name_field.value, head_field.value, risk_level_dropdown.value, dept["id"]))
                conn.commit()
                cursor.close()
                conn.close()

                # API version (commented out)
                # updated_dept = {
                #     "id": dept["id"],
                #     "name": name_field.value,
                #     "head": head_field.value,
                #     "risk_level": risk_level_dropdown.value,
                #     "assessments": dept["assessments"]
                # }
                # response = requests.put(f"{self.api_base_url}/departments/{dept['id']}", json=updated_dept)
                # if response.status_code != 200:
                #     raise Exception(f"API returned status {response.status_code}")

                # Update in local departments list
                for d in self.departments:
                    if d["id"] == dept["id"]:
                        d["name"] = name_field.value
                        d["head"] = head_field.value
                        d["risk_level"] = risk_level_dropdown.value
                        break

                # Update filtered departments
                self.filter_departments(None)

                # Close dialog
                close_dialog(e)

                # Show success message
                self.show_status(f"Department '{name_field.value}' updated successfully")
            except Exception as ex:
                print(f"Error updating department: {ex}")
                self.show_status(f"Error updating department: {str(ex)}", is_error=True)

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
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def delete_department(self, dept):
        # Define dialog close function
        def close_dialog(e):
            dialog.open = False
            self.page.update()

        # Define delete function
        def confirm_delete(e):
            try:
                # Direct database connection
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM departments WHERE id = %s", (dept["id"],))
                conn.commit()
                cursor.close()
                conn.close()

                # API version (commented out)
                # response = requests.delete(f"{self.api_base_url}/departments/{dept['id']}")
                # if response.status_code != 204:
                #     raise Exception(f"API returned status {response.status_code}")

                # Remove from local lists
                self.departments = [d for d in self.departments if d["id"] != dept["id"]]
                self.filtered_departments = [d for d in self.filtered_departments if d["id"] != dept["id"]]

                # Close dialog
                close_dialog(e)

                # Update department cards
                self.update_department_cards()

                # Show success message
                self.show_status(f"Department '{dept['name']}' deleted successfully")
            except Exception as ex:
                print(f"Error deleting department: {ex}")
                self.show_status(f"Error deleting department: {str(ex)}", is_error=True)

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
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def view_department_details(self, dept):
        # Show loading indicator
        self.loading_indicator.visible = True
        self.update()

        # Get risk color
        risk_color = self.get_risk_color(dept["risk_level"])

        # Create stats section
        stats_row = ft.Row([
            ft.Container(
                padding=15,
                border_radius=10,
                bgcolor="white",
                border=ft.border.all(1, "#EEEEEE"),
                content=ft.Column([
                    ft.Text(str(dept["assessments"]), size=24, weight=ft.FontWeight.BOLD, color="#3498db"),
                            ft.Text("Assessments", size=14),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                width=120,
            ),
            ft.Container(width=10),
            ft.Container(
                padding=15,
                border_radius=10,
                bgcolor="white",
                border=ft.border.all(1, "#EEEEEE"),
                content=ft.Column([
                    ft.Text(dept["risk_level"], size=24, weight=ft.FontWeight.BOLD, color=risk_color),
                            ft.Text("Risk Level", size=14),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                width=120,
            ),
        ])

        # Get assessments from database
        department_assessments = []
        try:
            # Direct database connection
            conn = get_db_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("""
                SELECT id, department_id, name, status
                FROM assessments
                WHERE department_id = %s
                ORDER BY id DESC
                LIMIT 3
            """, (dept["id"],))
            department_assessments = cursor.fetchall()
            # Convert to regular dictionaries
            department_assessments = [dict(a) for a in department_assessments]
            cursor.close()
            conn.close()

            # API version (commented out)
            # response = requests.get(f"{self.api_base_url}/departments/{dept['id']}/assessments")
            # if response.status_code == 200:
            #     department_assessments = response.json()
            #     if len(department_assessments) > 3:
            #         department_assessments = department_assessments[:3]
        except Exception as e:
            print(f"Error getting assessments: {e}")
            department_assessments = []

        # Hide loading indicator
        self.loading_indicator.visible = False
        self.update()

        # Create recent assessments section
        recent_assessments = ft.Column([
            ft.Text("No recent assessments", size=14, color="#666666", italic=True)
        ])

        if department_assessments:
            recent_assessments.controls = [
                ft.Container(
                    content=ft.Row([
                        ft.Container(
                            width=16,
                            height=16,
                            bgcolor="#3498db",
                            border_radius=8,
                            alignment=ft.alignment.center,
                            content=ft.Text("A", color="white", size=10, weight=ft.FontWeight.BOLD)
                        ),
                        ft.Text(f"{assessment['name']} - {assessment['status']}", size=14),
                    ]),
                    padding=5,
                )
                for assessment in department_assessments
            ]
        elif dept["assessments"] > 0:  # Fallback if we have assessment count but no specific data
            recent_assessments.controls = [
                ft.Container(
                    content=ft.Row([
                        ft.Container(
                            width=16,
                            height=16,
                            bgcolor="#3498db",
                            border_radius=8,
                            alignment=ft.alignment.center,
                            content=ft.Text("A", color="white", size=10, weight=ft.FontWeight.BOLD)
                        ),
                        ft.Text(f"Assessment #{i + 1} - {['Completed', 'In Progress'][i % 2]}", size=14),
                    ]),
                    padding=5,
                )
                for i in range(min(dept["assessments"], 3))
            ]

        # Define dialog close function
        def close_dialog(e):
            dialog.open = False
            self.page.update()

        # Define run assessment function
        def run_assessment(e):
            try:
                # Direct database connection
                conn = get_db_connection()
                cursor = conn.cursor()

                # Insert new assessment
                cursor.execute("""
                    INSERT INTO assessments (department_id, name, status)
                    VALUES (%s, %s, %s)
                """, (dept["id"], "Security Assessment", "In Progress"))

                # Update department assessment count
                cursor.execute("""
                    UPDATE departments
                    SET assessments = assessments + 1
                    WHERE id = %s
                """, (dept["id"],))

                conn.commit()
                cursor.close()
                conn.close()

                # API version (commented out)
                # new_assessment = {
                #     "department_id": dept["id"],
                #     "name": "Security Assessment",
                #     "status": "In Progress"
                # }
                # response = requests.post(f"{self.api_base_url}/assessments", json=new_assessment)
                # if response.status_code == 201:
                #     update_response = requests.patch(f"{self.api_base_url}/departments/{dept['id']}/increment-assessments")
                #     if update_response.status_code != 200:
                #         raise Exception(f"Error updating assessment count: {update_response.status_code}")

                # Update local data
                for d in self.departments:
                    if d["id"] == dept["id"]:
                        d["assessments"] += 1
                        break

                # Close dialog
                close_dialog(e)

                # Update department cards
                self.update_department_cards()

                # Show success message
                self.show_status(f"Started new assessment for '{dept['name']}'")
            except Exception as ex:
                print(f"Error starting assessment: {ex}")
                self.show_status(f"Error starting assessment: {str(ex)}", is_error=True)

        # Create dialog
        dialog = ft.AlertDialog(
            title=ft.Text(f"Department Details: {dept['name']}"),
            content=ft.Column([
                ft.Text(f"Department Head: {dept['head']}", size=16),
                ft.Container(height=20),
                ft.Text("Department Statistics", size=16, weight=ft.FontWeight.BOLD),
                stats_row,
                ft.Container(height=20),
                ft.Text("Recent Assessments", size=16, weight=ft.FontWeight.BOLD),
                recent_assessments,
            ], height=300, scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.TextButton("Close", on_click=close_dialog),
                ft.ElevatedButton("Run Assessment", on_click=run_assessment, bgcolor="#3498db", color="white"),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        # Show dialog
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

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
