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


class ProjectsView(BaseView):
    def __init__(self, page, user=None, api_base_url="http://localhost:8000/api"):
        self.page = page
        self.user = user
        self.api_base_url = api_base_url  # Store API base URL for future use
        self.projects = []
        self.filtered_projects = []
        self.auditing_client = AuditingAPIClient()
        # Theme and header actions
        colors = get_theme_colors(self.page.theme_mode if hasattr(self.page, "theme_mode") else ft.ThemeMode.LIGHT)
        actions = [
            create_modern_button(colors, "Add Project", icon=Icons.ADD, on_click=self.show_add_project_dialog, style="success"),
            create_modern_button(colors, "Refresh", icon=Icons.REFRESH, on_click=lambda e: self.refresh_projects(), style="secondary"),
        ]
        super().__init__(page, "Projects", on_search=self.on_search_change, actions=actions, colors=colors)

        # Build the controls area and table as cards
        self._build_ui()
        self.load_projects()  # Load projects from API

    def refresh_table(self):
        """Build table like user_management: header + rows, with empty state."""
        colors = get_theme_colors(self.page.theme_mode if hasattr(self.page, "theme_mode") else ft.ThemeMode.LIGHT)

        header = ft.Container(
            height=40,
            bgcolor=None,
            border=ft.border.only(bottom=ft.BorderSide(1, colors.border)),
            padding=ft.padding.only(left=30, right=30),
            content=ft.Row([
                ft.Container(width=240, content=ft.Text("Name", weight=ft.FontWeight.BOLD, color=colors.text_secondary)),
                ft.Container(width=160, content=ft.Text("Status", weight=ft.FontWeight.BOLD, color=colors.text_secondary)),
                ft.Container(width=220, content=ft.Text("Department", weight=ft.FontWeight.BOLD, color=colors.text_secondary)),
                ft.Container(width=180, content=ft.Text("Manager", weight=ft.FontWeight.BOLD, color=colors.text_secondary)),
                ft.Container(width=180, content=ft.Text("Timeline", weight=ft.FontWeight.BOLD, color=colors.text_secondary)),
                ft.Container(width=200, content=ft.Text("Actions", weight=ft.FontWeight.BOLD, color=colors.text_secondary, text_align=ft.TextAlign.CENTER)),
            ])
        )

        rows = ft.Column(spacing=0)
        for i, proj in enumerate(self.filtered_projects or []):
            rows.controls.append(self.create_project_row(proj, i))

        if not self.filtered_projects:
            rows.controls.append(
                ft.Container(
                    height=100,
                    alignment=ft.alignment.center,
                    content=ft.Column([
                        ft.Icon(Icons.SEARCH_OFF, size=40, color="#95a5a6"),
                        ft.Text("No projects found", size=16, color="#95a5a6")
                    ], spacing=10, alignment=ft.MainAxisAlignment.CENTER)
                )
            )

        list_view = ft.ListView(expand=True, spacing=0, auto_scroll=False)
        for c in rows.controls:
            list_view.controls.append(c)

        table = ft.Container(expand=True, content=ft.Column([header, list_view], spacing=0))
        self.projects_table_container.content = table
        if hasattr(self, "page") and self.page:
            self.page.update()

    def create_project_row(self, proj, row_index):
        colors = get_theme_colors(self.page.theme_mode if hasattr(self.page, "theme_mode") else ft.ThemeMode.LIGHT)
        row_bg = colors.surface
        status_color = self.get_status_color(proj.get("status"))

        # Format dates for timeline
        start_date = proj.get("start_date")
        if start_date and not isinstance(start_date, str):
            start_date = start_date.strftime("%Y-%m-%d")
        end_date = proj.get("end_date")
        if end_date and not isinstance(end_date, str):
            end_date = end_date.strftime("%Y-%m-%d")
        timeline = f"{start_date or '-'} - {end_date or '-'}"

        return ft.Container(
            height=60,
            bgcolor=row_bg,
            border=ft.border.only(bottom=ft.BorderSide(1, colors.border)),
            padding=ft.padding.only(left=30, right=30),
            content=ft.Row([
                ft.Container(width=240, content=ft.Text(proj.get("name", "-"), color=colors.text_primary)),
                ft.Container(
                    width=160,
                    content=ft.Container(
                        width=100,
                        height=30,
                        bgcolor=status_color,
                        border_radius=15,
                        alignment=ft.alignment.center,
                        content=ft.Text(proj.get("status", "-"), color="white", size=12, weight=ft.FontWeight.BOLD)
                    )
                ),
                ft.Container(width=220, content=ft.Text(proj.get("department_name", "-"), color=colors.text_primary)),
                ft.Container(width=180, content=ft.Text(proj.get("manager", "-"), color=colors.text_primary)),
                ft.Container(width=180, content=ft.Text(timeline, color=colors.text_primary)),
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
                            on_click=lambda e, p=proj: self.view_project_details(p)
                        ),
                        ft.Container(width=10),
                        ft.Container(
                            width=40,
                            height=30,
                            bgcolor="#2ecc71",
                            border_radius=5,
                            alignment=ft.alignment.center,
                            content=ft.Icon(Icons.EDIT, color="white", size=16),
                            on_click=lambda e, p=proj: self.edit_project(p)
                        ),
                        ft.Container(width=10),
                        ft.Container(
                            width=40,
                            height=30,
                            bgcolor="#e74c3c",
                            border_radius=5,
                            alignment=ft.alignment.center,
                            content=ft.Icon(Icons.DELETE, color="white", size=16),
                            on_click=lambda e, p=proj: self.delete_project(p)
                        ),
                    ], alignment=ft.MainAxisAlignment.CENTER)
                )
            ])
        )

    def load_projects(self):
        """Load projects from API"""
        if hasattr(self, 'page') and self.page:
            self.page.run_task(self._load_projects_async)

    async def _load_projects_async(self):
        """Load projects data from the API"""
        print("🔧 DEBUG: _load_projects_async called")
        try:
            print("🔧 DEBUG: Loading projects from src.api...")
            
            # Get projects data from API
            print("🔧 DEBUG: Calling auditing_client.get_projects()")
            api_projects = await self.auditing_client.get_projects()
            print(f"🔧 DEBUG: API returned {len(api_projects) if api_projects else 0} projects")
            
            if api_projects:
                # Convert API data to dictionaries if needed
                self.projects = []
                for proj_data in api_projects:
                    if isinstance(proj_data, dict):
                        # Normalize expected keys
                        normalized = {
                            'id': proj_data.get('id') or proj_data.get('Id'),
                            'name': proj_data.get('name') or proj_data.get('Name', 'Unknown'),
                            'description': proj_data.get('description') or proj_data.get('Description', ''),
                            'status_id': proj_data.get('status_id') or proj_data.get('StatusId'),
                            # UI expects 'status' string - map if provided, else default to id
                            'status': proj_data.get('status') or proj_data.get('Status'),
                            'department_id': proj_data.get('department_id') or proj_data.get('DepartmentId'),
                            'start_date': proj_data.get('start_date') or proj_data.get('StartDate'),
                            'end_date': proj_data.get('end_date') or proj_data.get('EndDate'),
                            'budget': proj_data.get('budget') or proj_data.get('Budget'),
                            'risk_level_id': proj_data.get('risk_level_id') or proj_data.get('RiskLevelId'),
                            'manager': proj_data.get('manager') or proj_data.get('Manager')
                        }
                        self.projects.append(normalized)
                    else:
                        # Convert object to dict if needed
                        self.projects.append({
                            'id': getattr(proj_data, 'Id', getattr(proj_data, 'id', None)),
                            'name': getattr(proj_data, 'Name', getattr(proj_data, 'name', 'Unknown')),
                            'description': getattr(proj_data, 'Description', getattr(proj_data, 'description', '')),
                            'status_id': getattr(proj_data, 'StatusId', getattr(proj_data, 'status_id', None)),
                            'status': getattr(proj_data, 'Status', getattr(proj_data, 'status', None)),
                            'department_id': getattr(proj_data, 'DepartmentId', getattr(proj_data, 'department_id', None)),
                            'start_date': getattr(proj_data, 'StartDate', getattr(proj_data, 'start_date', None)),
                            'end_date': getattr(proj_data, 'EndDate', getattr(proj_data, 'end_date', None)),
                            'budget': getattr(proj_data, 'Budget', getattr(proj_data, 'budget', None)),
                            'risk_level_id': getattr(proj_data, 'RiskLevelId', getattr(proj_data, 'risk_level_id', None)),
                            'manager': getattr(proj_data, 'Manager', getattr(proj_data, 'manager', None))
                        })
                
                print(f"Loaded {len(self.projects)} projects from API")
            else:
                print("No projects data available from API")
                self.projects = []
                
            self.filtered_projects = self.projects.copy()
            self.refresh_table()
            
            if hasattr(self, 'page') and self.page:
                self.page.update()
                
        except Exception as e:
            print(f"Error loading projects from API: {e}")
            self.projects = []
            self.filtered_projects = []
            if hasattr(self, 'page') and self.page:
                self.page.update()

    def _build_ui(self):
        colors = get_theme_colors(self.page.theme_mode if hasattr(self.page, "theme_mode") else ft.ThemeMode.LIGHT)

        # Search field styled like user_management
        self._search_input = ft.TextField(
            border=ft.InputBorder.NONE,
            color="#2c3e50",
            hint_text="Search projects",
            hint_style=ft.TextStyle(color="#95a5a6", size=14),
            expand=True,
            height=30,
            content_padding=5,
            on_change=self.filter_projects,
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

        # Status filter dropdown
        self.status_filter = ft.Dropdown(
            label="Status",
            options=[
                ft.dropdown.Option("All"),
                ft.dropdown.Option("Not Started"),
                ft.dropdown.Option("In Progress"),
                ft.dropdown.Option("Completed"),
                ft.dropdown.Option("On Hold"),
            ],
            value="All",
            on_change=self.filter_projects,
            width=150
        )

        # Risk level filter dropdown
        self.risk_filter = ft.Dropdown(
            label="Risk Level",
            options=[
                ft.dropdown.Option("All"),
                ft.dropdown.Option("High"),
                ft.dropdown.Option("Medium"),
                ft.dropdown.Option("Low"),
            ],
            value="All",
            on_change=self.filter_projects,
            width=150
        )

        # Status message area
        self.status_message = ft.Container(
            visible=False,
            padding=10,
            margin=10,
            border_radius=5,
            bgcolor="#e3f2fd",
            content=ft.Text("", color="#0d47a1")
        )

        # Loading indicator
        self.loading_indicator = ft.ProgressRing(
            width=40,
            height=40,
            stroke_width=3,
            visible=False
        )

        # Projects table container
        self.projects_table_container = ft.Container(expand=True, content=None)

        # Controls card (filters). Search is provided by BaseView header; keep combinational filters here
        controls_bar = ft.Row([
            self.status_filter,
            ft.Container(width=10),
            self.risk_filter,
        ], alignment=ft.MainAxisAlignment.START)
        self.add_card(controls_bar)

        # Status + loading card
        status_section = ft.Column([
            self.status_message,
            ft.Container(content=self.loading_indicator, alignment=ft.alignment.center, height=40),
        ], spacing=8)
        self.add_card(status_section)

        # Build initial table
        self.refresh_table()
        self.add_card(self.projects_table_container)

    def refresh_projects(self):
        """Refresh projects from database"""
        self.loading_indicator.visible = True
        self.update()

        try:
            # Direct database connection
            self.load_projects()
            self.refresh_table()
            self.show_status("Projects refreshed successfully")

            # API version (commented out)
            # response = requests.get(f"{self.api_base_url}/projects")
            # if response.status_code == 200:
            #     self.projects = response.json()
            #
            #     # Load department names for each project from API
            #     for project in self.projects:
            #         if project["department_id"]:
            #             dept_response = requests.get(f"{self.api_base_url}/departments/{project['department_id']}")
            #             if dept_response.status_code == 200:
            #                 department = dept_response.json()
            #                 project["department_name"] = department["name"]
            #             else:
            #                 project["department_name"] = "Unknown"
            #         else:
            #             project["department_name"] = "None"
            #
            #     self.filtered_projects = self.projects.copy()
            #     self.update_project_cards()
            #     self.show_status("Projects refreshed successfully")
            # else:
            #     self.show_status(f"Error refreshing: {response.status_code}", is_error=True)
        except Exception as e:
            print(f"Error refreshing projects: {e}")
            self.show_status(f"Error refreshing projects: {str(e)}", is_error=True)

        self.loading_indicator.visible = False
        self.update()

    # Legacy cards function kept for backward references; redirect to table
    def update_project_cards(self):
        self.refresh_table()

        # Add card for each project
        for proj in self.filtered_projects:
            # Set color based on status and risk level
            status_color = self.get_status_color(proj["status"])
            risk_color = self.get_risk_color(proj["risk_level"])

            # Format dates if they exist
            start_date = proj.get("start_date", "Not set")
            if start_date and not isinstance(start_date, str):
                start_date = start_date.strftime("%Y-%m-%d")

            end_date = proj.get("end_date", "Not set")
            if end_date and not isinstance(end_date, str):
                end_date = end_date.strftime("%Y-%m-%d")

            # Create action buttons
            view_button = ft.ElevatedButton(
                text="View",
                tooltip="View Details",
                on_click=lambda e, p=proj: self.view_project_details(p)
            )

            edit_button = ft.ElevatedButton(
                text="Edit",
                tooltip="Edit Project",
                on_click=lambda e, p=proj: self.edit_project(p)
            )

            delete_button = ft.ElevatedButton(
                text="Delete",
                tooltip="Delete Project",
                on_click=lambda e, p=proj: self.delete_project(p)
            )

            # Create project card
            card = create_modern_card(
                colors,
                ft.Column([
                    ft.Row([
                        ft.Text(proj["name"], size=18, weight=ft.FontWeight.BOLD),
                        ft.Container(
                            content=ft.Text(proj["status"], color="white", size=12),
                            bgcolor=status_color,
                            border_radius=12,
                            padding=ft.padding.symmetric(horizontal=10, vertical=5),
                            alignment=ft.alignment.center
                        )
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Container(height=8),
                    ft.Text(f"Department: {proj.get('department_name', 'None')}", size=14),
                    ft.Text(f"Manager: {proj.get('manager', 'Not assigned')}", size=14),
                    ft.Container(height=8),
                    ft.Row([
                        ft.Container(
                            content=ft.Text(proj["risk_level"], color="white", size=12),
                            bgcolor=risk_color,
                            border_radius=12,
                            padding=ft.padding.symmetric(horizontal=10, vertical=5),
                            alignment=ft.alignment.center
                        ),
                        ft.Text(f"{start_date} - {end_date}", size=12, color=colors.text_secondary)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Container(height=12),
                    ft.Row([
                        view_button,
                        edit_button,
                        delete_button
                    ], alignment=ft.MainAxisAlignment.END)
                ], spacing=6),
            )

            # Add card to column
            self.project_cards.controls.append(card)

        # If no projects found, show message
        if len(self.filtered_projects) == 0:
            self.project_cards.controls.append(
                create_modern_card(
                    colors,
                    ft.Column([
                        ft.Container(height=4),
                        ft.Text("No projects found", size=16, color=colors.text_secondary, text_align=ft.TextAlign.CENTER),
                        ft.Container(height=10),
                        create_modern_button(colors, "Add Your First Project", icon=Icons.ADD, on_click=self.show_add_project_dialog, style="primary")
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER),
                )
            )

        # Update UI
        self.update()

    def filter_projects(self, e):
        # Get search term, status and risk level
        search_term = getattr(self, "search_value", "")
        status = self.status_filter.value
        risk_level = self.risk_filter.value

        # Filter projects based on search term, status and risk level
        self.filtered_projects = [
            proj for proj in self.projects
            if (search_term == "" or
                search_term in proj["name"].lower() or
                search_term in (proj.get("description", "")).lower() or
                search_term in (proj.get("manager", "")).lower()) and
               (status == "All" or proj["status"] == status) and
               (risk_level == "All" or proj["risk_level"] == risk_level)
        ]

        # Refresh table
        self.refresh_table()

        # Show status message
        if search_term or status != "All" or risk_level != "All":
            count = len(self.filtered_projects)
            total = len(self.projects)
            self.show_status(f"Showing {count} of {total} projects")
        else:
            self.hide_status()

    def on_search_change(self, e: ft.ControlEvent):
        """Search handler for BaseView header search."""
        try:
            self.search_value = (e.control.value or "").lower()
        except Exception:
            self.search_value = ""
        self.filter_projects(None)

    async def get_departments(self):
        """Get all departments for dropdown selection via API"""
        try:
            departments = await self.auditing_client.get_departments()
            return departments or []
        except Exception as e:
            print(f"Error loading departments: {e}")
            return []

    def show_add_project_dialog(self, e):
        # Create form fields
        name_field = ft.TextField(
            label="Project Name",
            autofocus=True,
            border_radius=5
        )

        description_field = ft.TextField(
            label="Description",
            multiline=True,
            min_lines=2,
            max_lines=4,
            border_radius=5
        )

        manager_field = ft.TextField(
            label="Project Manager",
            border_radius=5
        )

        # Get departments for dropdown (synchronously from async)
        departments = []
        try:
            import asyncio as _asyncio
            loop = _asyncio.get_event_loop()
            if loop.is_running():
                # If we're already in an event loop, skip immediate population
                departments = []
            else:
                departments = loop.run_until_complete(self.get_departments())
        except Exception:
            departments = []
        department_options = [ft.dropdown.Option("None", "0")]
        department_options.extend([
            ft.dropdown.Option(d.get("name"), str(d.get("id"))) for d in (departments or []) if isinstance(d, dict)
        ])

        department_dropdown = ft.Dropdown(
            label="Department",
            options=department_options,
            value="0",
            width=200
        )

        status_dropdown = ft.Dropdown(
            label="Status",
            options=[
                ft.dropdown.Option("Not Started"),
                ft.dropdown.Option("In Progress"),
                ft.dropdown.Option("On Hold"),
                ft.dropdown.Option("Completed"),
            ],
            value="Not Started",
            width=200
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

        # Simple text fields for dates instead of date pickers
        start_date_field = ft.TextField(
            label="Start Date (YYYY-MM-DD)",
            hint_text="e.g., 2023-01-15",
            border_radius=5
        )

        end_date_field = ft.TextField(
            label="End Date (YYYY-MM-DD)",
            hint_text="e.g., 2023-12-31",
            border_radius=5
        )

        budget_field = ft.TextField(
            label="Budget",
            keyboard_type=ft.KeyboardType.NUMBER,
            prefix_text="$",
            border_radius=5
        )

        # Define dialog close function
        def close_dialog(e):
            dialog.open = False
            self.page.update()

        # Define save function
        def save_project(e):
            # Validate fields
            if not name_field.value:
                self.show_status("Project name is required", is_error=True)
                return

            # Get department ID (convert to None if "0")
            dept_id = int(department_dropdown.value) if department_dropdown.value != "0" else None

            # Parse dates
            start_date = None
            end_date = None

            if start_date_field.value:
                try:
                    # Simple validation - check if it matches YYYY-MM-DD format
                    if len(start_date_field.value.split('-')) == 3:
                        start_date = start_date_field.value
                    else:
                        self.show_status("Invalid start date format. Use YYYY-MM-DD", is_error=True)
                        return
                except:
                    self.show_status("Invalid start date", is_error=True)
                    return

            if end_date_field.value:
                try:
                    # Simple validation - check if it matches YYYY-MM-DD format
                    if len(end_date_field.value.split('-')) == 3:
                        end_date = end_date_field.value
                    else:
                        self.show_status("Invalid end date format. Use YYYY-MM-DD", is_error=True)
                        return
                except:
                    self.show_status("Invalid end date", is_error=True)
                    return

            # Get budget (convert to float if provided)
            budget = None
            if budget_field.value:
                try:
                    budget = float(budget_field.value)
                except ValueError:
                    self.show_status("Invalid budget amount", is_error=True)
                    return

            # Create new project
            try:
                # Direct database connection
                conn = get_db_connection()
                cursor = conn.cursor(cursor_factory=RealDictCursor)
                cursor.execute("""
                    INSERT INTO projects 
                    (name, description, status, department_id, start_date, end_date, budget, risk_level, manager)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id, name, description, status, department_id, start_date, end_date, budget, risk_level, manager
                """, (
                    name_field.value,
                    description_field.value,
                    status_dropdown.value,
                    dept_id,
                    start_date,
                    end_date,
                    budget,
                    risk_level_dropdown.value,
                    manager_field.value
                ))

                new_proj = cursor.fetchone()
                conn.commit()

                # Get department name for the new project
                if dept_id:
                    cursor.execute("SELECT name FROM departments WHERE id = %s", (dept_id,))
                    result = cursor.fetchone()
                    if result:
                        new_proj["department_name"] = result["name"]
                    else:
                        new_proj["department_name"] = "Unknown"
                else:
                    new_proj["department_name"] = "None"

                cursor.close()
                conn.close()

                # Convert to a regular dictionary
                new_proj = dict(new_proj)

                # API version (commented out)
                # new_proj_data = {
                #     "name": name_field.value,
                #     "description": description_field.value,
                #     "status": status_dropdown.value,
                #     "department_id": dept_id,
                #     "start_date": start_date,
                #     "end_date": end_date,
                #     "budget": budget,
                #     "risk_level": risk_level_dropdown.value,
                #     "manager": manager_field.value
                # }
                # response = requests.post(f"{self.api_base_url}/projects", json=new_proj_data)
                # if response.status_code == 201:
                #     new_proj = response.json()
                #
                #     # Get department name if available
                #     if dept_id:
                #         dept_response = requests.get(f"{self.api_base_url}/departments/{dept_id}")
                #         if dept_response.status_code == 200:
                #             department = dept_response.json()
                #             new_proj["department_name"] = department["name"]
                #         else:
                #             new_proj["department_name"] = "Unknown"
                #     else:
                #         new_proj["department_name"] = "None"
                # else:
                #     raise Exception(f"API returned status {response.status_code}")

                # Add to projects list
                self.projects.append(new_proj)
                self.filtered_projects = self.projects.copy()

                # Close dialog
                close_dialog(e)

                # Refresh table
                self.refresh_table()

                # Show success message
                self.show_status(f"Project '{new_proj['name']}' added successfully")
            except Exception as ex:
                print(f"Error adding project: {ex}")
                self.show_status(f"Error adding project: {str(ex)}", is_error=True)

        # Create dialog
        dialog = ft.AlertDialog(
            title=ft.Text("Add New Project"),
            content=ft.Column([
                ft.Text("Project Details", weight=ft.FontWeight.BOLD, size=16),
                name_field,
                description_field,

                ft.Text("Project Assignment", weight=ft.FontWeight.BOLD, size=16),
                ft.Container(height=5),
                ft.Row([department_dropdown, manager_field], spacing=10),

                ft.Text("Project Status", weight=ft.FontWeight.BOLD, size=16),
                ft.Container(height=5),
                ft.Row([status_dropdown, risk_level_dropdown], spacing=10),

                ft.Text("Project Timeline", weight=ft.FontWeight.BOLD, size=16),
                ft.Container(height=5),
                ft.Row([start_date_field, end_date_field], spacing=10),

                ft.Text("Project Budget", weight=ft.FontWeight.BOLD, size=16),
                ft.Container(height=5),
                budget_field,
            ], tight=True, spacing=15, scroll=ft.ScrollMode.AUTO, height=450),
            actions=[
                ft.TextButton("Cancel", on_click=close_dialog),
                ft.ElevatedButton("Save", on_click=save_project, bgcolor="#3498db", color="white"),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        # Show dialog
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def edit_project(self, proj):
        # Create form fields
        name_field = ft.TextField(
            label="Project Name",
            value=proj["name"],
            autofocus=True,
            border_radius=5
        )

        description_field = ft.TextField(
            label="Description",
            value=proj.get("description", ""),
            multiline=True,
            min_lines=2,
            max_lines=4,
            border_radius=5
        )

        manager_field = ft.TextField(
            label="Project Manager",
            value=proj.get("manager", ""),
            border_radius=5
        )

        # Get departments for dropdown (synchronously from async)
        departments = []
        try:
            import asyncio as _asyncio
            loop = _asyncio.get_event_loop()
            if loop.is_running():
                departments = []
            else:
                departments = loop.run_until_complete(self.get_departments())
        except Exception:
            departments = []
        department_options = [ft.dropdown.Option("None", "0")]
        department_options.extend([
            ft.dropdown.Option(d.get("name"), str(d.get("id"))) for d in (departments or []) if isinstance(d, dict)
        ])

        department_dropdown = ft.Dropdown(
            label="Department",
            options=department_options,
            value=str(proj["department_id"]) if proj["department_id"] else "0",
            width=200
        )

        status_dropdown = ft.Dropdown(
            label="Status",
            options=[
                ft.dropdown.Option("Not Started"),
                ft.dropdown.Option("In Progress"),
                ft.dropdown.Option("On Hold"),
                ft.dropdown.Option("Completed"),
            ],
            value=proj["status"],
            width=200
        )

        risk_level_dropdown = ft.Dropdown(
            label="Risk Level",
            options=[
                ft.dropdown.Option("High"),
                ft.dropdown.Option("Medium"),
                ft.dropdown.Option("Low"),
            ],
            value=proj["risk_level"],
            width=200
        )

        # Format current dates for display
        start_date = ""
        if proj.get("start_date"):
            if isinstance(proj["start_date"], str):
                start_date = proj["start_date"]
            else:
                start_date = proj["start_date"].strftime("%Y-%m-%d")

        end_date = ""
        if proj.get("end_date"):
            if isinstance(proj["end_date"], str):
                end_date = proj["end_date"]
            else:
                end_date = proj["end_date"].strftime("%Y-%m-%d")

        # Simple text fields for dates instead of date pickers
        start_date_field = ft.TextField(
            label="Start Date (YYYY-MM-DD)",
            value=start_date,
            hint_text="e.g., 2023-01-15",
            border_radius=5
        )

        end_date_field = ft.TextField(
            label="End Date (YYYY-MM-DD)",
            value=end_date,
            hint_text="e.g., 2023-12-31",
            border_radius=5
        )

        budget_field = ft.TextField(
            label="Budget",
            value=str(proj.get("budget", "")),
            keyboard_type=ft.KeyboardType.NUMBER,
            prefix_text="$",
            border_radius=5
        )

        # Define dialog close function
        def close_dialog(e):
            dialog.open = False
            self.page.update()

        # Define update function
        def update_project(e):
            # Validate fields
            if not name_field.value:
                self.show_status("Project name is required", is_error=True)
                return

            # Get department ID (convert to None if "0")
            dept_id = int(department_dropdown.value) if department_dropdown.value != "0" else None

            # Parse dates
            start_date = None
            end_date = None

            if start_date_field.value:
                try:
                    # Simple validation - check if it matches YYYY-MM-DD format
                    if len(start_date_field.value.split('-')) == 3:
                        start_date = start_date_field.value
                    else:
                        self.show_status("Invalid start date format. Use YYYY-MM-DD", is_error=True)
                        return
                except:
                    self.show_status("Invalid start date", is_error=True)
                    return

            if end_date_field.value:
                try:
                    # Simple validation - check if it matches YYYY-MM-DD format
                    if len(end_date_field.value.split('-')) == 3:
                        end_date = end_date_field.value
                    else:
                        self.show_status("Invalid end date format. Use YYYY-MM-DD", is_error=True)
                        return
                except:
                    self.show_status("Invalid end date", is_error=True)
                    return

            # Get budget (convert to float if provided)
            budget = None
            if budget_field.value:
                try:
                    budget = float(budget_field.value)
                except ValueError:
                    self.show_status("Invalid budget amount", is_error=True)
                    return

            try:
                # Direct database connection
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE projects
                    SET name = %s, description = %s, status = %s, department_id = %s,
                        start_date = %s, end_date = %s, budget = %s, risk_level = %s, manager = %s
                    WHERE id = %s
                """, (
                    name_field.value,
                    description_field.value,
                    status_dropdown.value,
                    dept_id,
                    start_date,
                    end_date,
                    budget,
                    risk_level_dropdown.value,
                    manager_field.value,
                    proj["id"]
                ))
                conn.commit()

                # Get department name
                department_name = "None"
                if dept_id:
                    cursor.execute("SELECT name FROM departments WHERE id = %s", (dept_id,))
                    result = cursor.fetchone()
                    if result:
                        department_name = result[0]
                    else:
                        department_name = "Unknown"

                cursor.close()
                conn.close()

                # API version (commented out)
                # updated_proj = {
                #     "id": proj["id"],
                #     "name": name_field.value,
                #     "description": description_field.value,
                #     "status": status_dropdown.value,
                #     "department_id": dept_id,
                #     "start_date": start_date,
                #     "end_date": end_date,
                #     "budget": budget,
                #     "risk_level": risk_level_dropdown.value,
                #     "manager": manager_field.value
                # }
                # response = requests.put(f"{self.api_base_url}/projects/{proj['id']}", json=updated_proj)
                # if response.status_code != 200:
                #     raise Exception(f"API returned status {response.status_code}")
                #
                # # Get department name
                # department_name = "None"
                # if dept_id:
                #     dept_response = requests.get(f"{self.api_base_url}/departments/{dept_id}")
                #     if dept_response.status_code == 200:
                #         department = dept_response.json()
                #         department_name = department["name"]
                #     else:
                #         department_name = "Unknown"

                # Update in local projects list
                for p in self.projects:
                    if p["id"] == proj["id"]:
                        p["name"] = name_field.value
                        p["description"] = description_field.value
                        p["status"] = status_dropdown.value
                        p["department_id"] = dept_id
                        p["department_name"] = department_name
                        p["start_date"] = start_date
                        p["end_date"] = end_date
                        p["budget"] = budget
                        p["risk_level"] = risk_level_dropdown.value
                        p["manager"] = manager_field.value
                        break

                # Update filtered projects
                self.filter_projects(None)

                # Close dialog
                close_dialog(e)

                # Show success message
                self.show_status(f"Project '{name_field.value}' updated successfully")
            except Exception as ex:
                print(f"Error updating project: {ex}")
                self.show_status(f"Error updating project: {str(ex)}", is_error=True)

        # Create dialog
        dialog = ft.AlertDialog(
            title=ft.Text(f"Edit Project: {proj['name']}"),
            content=ft.Column([
                ft.Text("Project Details", weight=ft.FontWeight.BOLD, size=16),
                name_field,
                description_field,

                ft.Text("Project Assignment", weight=ft.FontWeight.BOLD, size=16),
                ft.Container(height=5),
                ft.Row([department_dropdown, manager_field], spacing=10),

                ft.Text("Project Status", weight=ft.FontWeight.BOLD, size=16),
                ft.Container(height=5),
                ft.Row([status_dropdown, risk_level_dropdown], spacing=10),

                ft.Text("Project Timeline", weight=ft.FontWeight.BOLD, size=16),
                ft.Container(height=5),
                ft.Row([start_date_field, end_date_field], spacing=10),

                ft.Text("Project Budget", weight=ft.FontWeight.BOLD, size=16),
                ft.Container(height=5),
                budget_field,
            ], tight=True, spacing=15, scroll=ft.ScrollMode.AUTO, height=450),
            actions=[
                ft.TextButton("Cancel", on_click=close_dialog),
                ft.ElevatedButton("Update", on_click=update_project, bgcolor="#3498db", color="white"),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        # Show dialog
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def delete_project(self, proj):
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
                cursor.execute("DELETE FROM projects WHERE id = %s", (proj["id"],))
                conn.commit()
                cursor.close()
                conn.close()

                # API version (commented out)
                # response = requests.delete(f"{self.api_base_url}/projects/{proj['id']}")
                # if response.status_code != 204:
                #     raise Exception(f"API returned status {response.status_code}")

                # Remove from local lists
                self.projects = [p for p in self.projects if p["id"] != proj["id"]]
                self.filtered_projects = [p for p in self.filtered_projects if p["id"] != proj["id"]]

                # Close dialog
                close_dialog(e)

                # Update project cards
                self.update_project_cards()

                # Show success message
                self.show_status(f"Project '{proj['name']}' deleted successfully")
            except Exception as ex:
                print(f"Error deleting project: {ex}")
                self.show_status(f"Error deleting project: {str(ex)}", is_error=True)

        # Create dialog with improved layout
        dialog = ft.AlertDialog(
            title=ft.Text("Confirm Delete"),
            content=ft.Column([
                ft.Container(
                    width=50,
                    height=50,
                    bgcolor="#e74c3c",
                    border_radius=25,
                    alignment=ft.alignment.center,
                    content=ft.Text("⚠️", size=24)
                ),
                ft.Container(height=10),
                ft.Text(f"Are you sure you want to delete the project '{proj['name']}'?",
                        text_align=ft.TextAlign.CENTER),
                ft.Text("This action cannot be undone.",
                        color="#666666", italic=True, size=12, text_align=ft.TextAlign.CENTER)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            actions=[
                ft.TextButton("Cancel", on_click=close_dialog),
                ft.ElevatedButton(
                    "Delete",
                    on_click=confirm_delete,
                    bgcolor="#e74c3c",
                    color="white",
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        # Show dialog
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def view_project_details(self, proj):
        # Show loading indicator
        self.loading_indicator.visible = True
        self.update()

        # Get colors
        status_color = self.get_status_color(proj["status"])
        risk_color = self.get_risk_color(proj["risk_level"])

        # Format dates if they exist
        start_date = proj.get("start_date", "Not set")
        if start_date and not isinstance(start_date, str):
            start_date = start_date.strftime("%Y-%m-%d")

        end_date = proj.get("end_date", "Not set")
        if end_date and not isinstance(end_date, str):
            end_date = end_date.strftime("%Y-%m-%d")

        # Format budget
        budget = proj.get("budget")
        budget_display = f"${budget:,.2f}" if budget else "Not set"

        # Get assessments for this project - database version
        project_assessments = []
        try:
            conn = get_db_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("""
                SELECT id, name, status, created_at 
                FROM assessments 
                WHERE project_id = %s 
                ORDER BY created_at DESC LIMIT 3
            """, (proj["id"],))
            project_assessments = cursor.fetchall()
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Error fetching project assessments: {e}")

        # API version (commented out)
        # try:
        #     response = requests.get(f"{self.api_base_url}/projects/{proj['id']}/assessments")
        #     if response.status_code == 200:
        #         project_assessments = response.json()
        #     else:
        #         print(f"Error fetching project assessments: API returned status {response.status_code}")
        # except Exception as e:
        #     print(f"Error fetching project assessments: {e}")

        # Create project details section with improved layout
        details_section = ft.Column([
            ft.Row([
                ft.Text("Department:", size=14, weight=ft.FontWeight.BOLD, width=120),
                ft.Text(proj.get("department_name", "None"), size=14)
            ]),
            ft.Divider(height=1),
            ft.Row([
                ft.Text("Manager:", size=14, weight=ft.FontWeight.BOLD, width=120),
                ft.Text(proj.get("manager", "Not assigned"), size=14)
            ]),
            ft.Divider(height=1),
            ft.Row([
                ft.Text("Timeline:", size=14, weight=ft.FontWeight.BOLD, width=120),
                ft.Text(f"{start_date} to {end_date}", size=14)
            ]),
            ft.Divider(height=1),
            ft.Row([
                ft.Text("Budget:", size=14, weight=ft.FontWeight.BOLD, width=120),
                ft.Text(budget_display, size=14)
            ]),
            ft.Divider(height=1),
            ft.Container(height=10),
            ft.Text("Description:", size=14, weight=ft.FontWeight.BOLD),
            ft.Container(
                content=ft.Text(proj.get("description", "No description provided."), size=14),
                padding=15,
                bgcolor="#f5f5f5",
                border_radius=5,
                width=400
            ),
        ])

        # Create status indicators with improved styling
        status_section = ft.Row([
            ft.Container(
                padding=15,
                border_radius=10,
                bgcolor=None,
                border=ft.border.all(1, "#EEEEEE"),
                content=ft.Column([
                    ft.Container(
                        content=ft.Text(proj["status"], color="white", size=16, weight=ft.FontWeight.BOLD),
                        bgcolor=status_color,
                        border_radius=15,
                        padding=ft.padding.only(left=15, right=15, top=8, bottom=8),
                        alignment=ft.alignment.center
                    ),
                    ft.Container(height=8),
                    ft.Text("Status", size=14, color="#666666"),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                width=140,
            ),
            ft.Container(width=20),
            ft.Container(
                padding=15,
                border_radius=10,
                bgcolor=None,
                border=ft.border.all(1, "#EEEEEE"),
                content=ft.Column([
                    ft.Container(
                        content=ft.Text(proj["risk_level"], color="white", size=16, weight=ft.FontWeight.BOLD),
                        bgcolor=risk_color,
                        border_radius=15,
                        padding=ft.padding.only(left=15, right=15, top=8, bottom=8),
                        alignment=ft.alignment.center
                    ),
                    ft.Container(height=8),
                    ft.Text("Risk Level", size=14, color="#666666"),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                width=140,
            ),
        ], alignment=ft.MainAxisAlignment.CENTER)

        # Create assessments section if available
        assessments_section = ft.Column([
            ft.Text("No assessments found for this project", size=14, color="#666666", italic=True)
        ])

        if project_assessments:
            assessments_section = ft.Column([
                ft.Text("Recent Assessments", size=16, weight=ft.FontWeight.BOLD),
                ft.Container(height=10),
                ft.Column([
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
                            ft.Column([
                                ft.Text(a["name"], size=14, weight=ft.FontWeight.BOLD),
                                ft.Text(f"Status: {a['status']}", size=12, color="#666666")
                            ])
                        ]),
                        padding=10,
                        margin=5,
                        border_radius=5,
                        bgcolor="#f5f5f5"
                    ) for a in project_assessments
                ])
            ])

        # Hide loading indicator
        self.loading_indicator.visible = False
        self.update()

        # Define dialog close function
        def close_dialog(e):
            dialog.open = False
            self.page.update()

        # Create dialog with improved layout
        dialog = ft.AlertDialog(
            title=ft.Text(f"Project Details: {proj['name']}", size=20),
            content=ft.Column([
                status_section,
                ft.Container(height=30),
                details_section,
                ft.Container(height=20),
                assessments_section
            ], height=500, scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.TextButton("Close", on_click=close_dialog),
                ft.ElevatedButton(
                    "Edit Project",
                    on_click=lambda e: (close_dialog(e), self.edit_project(proj)),
                    bgcolor="#3498db",
                    color="white",
                ),
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
            self.status_message.bgcolor = "#ffebee"  # Light red
            self.status_message.content = ft.Text(message, color="#c62828")  # Dark red
        else:
            self.status_message.bgcolor = "#e3f2fd"  # Light blue
            self.status_message.content = ft.Text(message, color="#0d47a1")  # Dark blue

        # Show message
        self.status_message.visible = True
        self.update()

        # Auto-hide after 5 seconds
        def hide_message():
            import time
            time.sleep(5)
            # Check if the message is still the same before hiding
            current_message = self.status_message.content.value if self.status_message.content else ""
            if current_message == message:
                self.status_message.visible = False
                self.update()

        # Start a thread to hide the message after delay
        import threading
        threading.Thread(target=hide_message, daemon=True).start()

    def hide_status(self):
        # Hide message
        self.status_message.visible = False
        self.update()

    def get_status_color(self, status):
        # Return color based on status
        if status == "Completed":
            return "#2ecc71"  # Green
        elif status == "In Progress":
            return "#3498db"  # Blue
        elif status == "On Hold":
            return "#f39c12"  # Orange
        else:  # Not Started
            return "#95a5a6"  # Gray

    def get_risk_color(self, risk_level):
        # Return color based on risk level
        if risk_level == "High":
            return "#e74c3c"  # Red
        elif risk_level == "Medium":
            return "#f39c12"  # Orange
        else:
            return "#2ecc71"  # Green

    def apply_theme(self, colors):
        """Apply theme colors to the projects view"""
        try:
            self.bgcolor = colors.bg
            # Rebuild following Dashboard's pattern to refresh tokens
            self._build_ui()
            apply_theme_to_control(self, colors)
            if hasattr(self, 'page') and self.page:
                self.page.update()
        except Exception as e:
            print(f"Error applying theme to projects view: {e}")
