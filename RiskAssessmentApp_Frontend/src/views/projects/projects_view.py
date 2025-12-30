import flet as ft
from flet import Icons
import asyncio
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
        self.departments = []
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

    def _status_to_id(self, status: str):
        mapping = {"Planning": 1, "Active": 2, "Completed": 3, "On Hold": 4, "Cancelled": 5}
        return mapping.get(status, 1)

    def _risk_level_to_id(self, risk_level: str):
        mapping = {"High": 1, "Medium": 2, "Low": 3}
        return mapping.get(risk_level, 3)

    def refresh_table(self):
        """Build table like user_management: header + rows, with empty state."""
        colors = get_theme_colors(self.page.theme_mode if hasattr(self.page, "theme_mode") else ft.ThemeMode.LIGHT)

        header = ft.Container(
            height=40,
            bgcolor=colors.surface,
            border=ft.border.only(bottom=ft.BorderSide(1, colors.border)),
            padding=ft.padding.only(left=30, right=30),
            content=ft.Row([
                ft.Container(expand=2, content=ft.Text("Name", weight=ft.FontWeight.BOLD, color=colors.text_secondary)),
                ft.Container(expand=1, content=ft.Text("Status", weight=ft.FontWeight.BOLD, color=colors.text_secondary)),
                ft.Container(expand=1, content=ft.Text("Department", weight=ft.FontWeight.BOLD, color=colors.text_secondary)),
                ft.Container(expand=1, content=ft.Text("Manager", weight=ft.FontWeight.BOLD, color=colors.text_secondary)),
                ft.Container(expand=1.5, content=ft.Text("Timeline", weight=ft.FontWeight.BOLD, color=colors.text_secondary)),
                ft.Container(expand=1.5, content=ft.Text("Actions", weight=ft.FontWeight.BOLD, color=colors.text_secondary, text_align=ft.TextAlign.CENTER)),
            ], expand=True)
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
                ft.Container(expand=2, content=ft.Text(proj.get("name", "-"), color=colors.text_primary, overflow=ft.TextOverflow.ELLIPSIS)),
                ft.Container(
                    expand=1,
                    content=ft.Container(
                        width=100,
                        height=30,
                        bgcolor=status_color,
                        border_radius=15,
                        alignment=ft.alignment.center,
                        content=ft.Text(proj.get("status", "-"), color="white", size=12, weight=ft.FontWeight.BOLD)
                    )
                ),
                ft.Container(expand=1, content=ft.Text(proj.get("department_name", "-"), color=colors.text_primary, overflow=ft.TextOverflow.ELLIPSIS)),
                ft.Container(expand=1, content=ft.Text(proj.get("manager", "-"), color=colors.text_primary, overflow=ft.TextOverflow.ELLIPSIS)),
                ft.Container(expand=1.5, content=ft.Text(timeline, color=colors.text_primary)),
                ft.Container(
                    expand=1.5,
                    content=ft.Row([
                        ft.ElevatedButton(text="View", on_click=lambda e, p=proj: self.view_project_details(p)),
                        ft.Container(width=10),
                        ft.ElevatedButton(text="Edit", on_click=lambda e, p=proj: self.edit_project(p)),
                        ft.Container(width=10),
                        ft.ElevatedButton(text="Delete", on_click=lambda e, p=proj: self.delete_project(p)),
                    ], alignment=ft.MainAxisAlignment.CENTER)
                )
            ], expand=True)
        )

    def load_projects(self):
        """Load projects from API"""
        if hasattr(self, 'page') and self.page:
            self.page.run_task(self._load_projects_async)

    async def _load_projects_async(self):
        """Load projects data from the API"""
        print("DEBUG: _load_projects_async called")
        try:
            print("DEBUG: Loading projects from src.api...")
            
            # Load projects and departments (for dropdown + optional name mapping)
            print("DEBUG: Calling auditing_client.get_projects()")
            projects_task = self.auditing_client.get_projects()
            departments_task = self.auditing_client.get_departments()
            api_projects, api_departments = await asyncio.gather(projects_task, departments_task, return_exceptions=True)
            if not isinstance(api_departments, Exception) and api_departments:
                self.departments = api_departments
            print(f"DEBUG: API returned {len(api_projects) if api_projects else 0} projects")
            
            if api_projects and not isinstance(api_projects, Exception):
                # API client already normalizes the data, just add department_name mapping
                self.projects = []
                for proj_data in api_projects:
                    if isinstance(proj_data, dict):
                        # Use the already-normalized data from API client
                        normalized = proj_data.copy()
                        # Map department name if available
                        dept_id = normalized.get("department_id")
                        if dept_id and isinstance(self.departments, list):
                            match = next((d for d in self.departments if isinstance(d, dict) and d.get("id") == dept_id), None)
                            if match:
                                normalized["department_name"] = match.get("name", "-")
                            else:
                                normalized["department_name"] = "-"
                        else:
                            normalized["department_name"] = "-"
                        # Ensure manager is a string, not a date
                        if normalized.get("manager") and not isinstance(normalized.get("manager"), str):
                            normalized["manager"] = str(normalized.get("manager", "-"))
                        if not normalized.get("manager"):
                            normalized["manager"] = "-"
                        self.projects.append(normalized)
                
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
                ft.dropdown.Option("Planning"),
                ft.dropdown.Option("Active"),
                ft.dropdown.Option("Completed"),
                ft.dropdown.Option("On Hold"),
                ft.dropdown.Option("Cancelled"),
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
        colors = get_theme_colors(self.page.theme_mode if hasattr(self.page, "theme_mode") else ft.ThemeMode.LIGHT)
        if not hasattr(self, "project_cards") or self.project_cards is None:
            self.project_cards = ft.Column()
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
                ft.dropdown.Option("Planning"),
                ft.dropdown.Option("Active"),
                ft.dropdown.Option("On Hold"),
                ft.dropdown.Option("Completed"),
                ft.dropdown.Option("Cancelled"),
            ],
            value="Planning",
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
            self._close_dialog(dialog)

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

            self.page.run_task(
                self._create_project_async,
                dialog,
                name_field.value,
                description_field.value,
                status_dropdown.value,
                dept_id,
                start_date,
                end_date,
                budget,
                risk_level_dropdown.value,
                manager_field.value,
            )

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
        self._open_dialog(dialog)

    async def _create_project_async(self, dialog, name, description, status, dept_id, start_date, end_date, budget, risk_level, manager):
        try:
            payload = {
                "name": name,
                "description": description,
                "statusId": self._status_to_id(status),
                "departmentId": dept_id,
                "startDate": start_date,
                "endDate": end_date,
                "budget": budget,
                "riskLevelId": self._risk_level_to_id(risk_level),
                "manager": manager,
            }
            await self.auditing_client.create_project(payload)
            self._close_dialog(dialog)
            await self._load_projects_async()
            self.show_status(f"Project '{name}' added successfully")
        except Exception as ex:
            print(f"Error adding project: {ex}")
            self.show_status(f"Error adding project: {str(ex)}", is_error=True)
        if hasattr(self, 'page') and self.page:
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
                ft.dropdown.Option("Planning"),
                ft.dropdown.Option("Active"),
                ft.dropdown.Option("On Hold"),
                ft.dropdown.Option("Completed"),
                ft.dropdown.Option("Cancelled"),
            ],
            value=proj.get("status") or "Planning",
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
            self._close_dialog(dialog)

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

            self.page.run_task(
                self._update_project_async,
                dialog,
                proj.get("id"),
                name_field.value,
                description_field.value,
                status_dropdown.value,
                dept_id,
                start_date,
                end_date,
                budget,
                risk_level_dropdown.value,
                manager_field.value,
            )

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
        self._open_dialog(dialog)

    async def _update_project_async(self, dialog, project_id, name, description, status, dept_id, start_date, end_date, budget, risk_level, manager):
        try:
            payload = {
                "id": project_id,
                "name": name,
                "description": description,
                "statusId": self._status_to_id(status),
                "departmentId": dept_id,
                "startDate": start_date,
                "endDate": end_date,
                "budget": budget,
                "riskLevelId": self._risk_level_to_id(risk_level),
                "manager": manager,
            }
            await self.auditing_client.update_project(project_id, payload)
            self._close_dialog(dialog)
            await self._load_projects_async()
            self.show_status(f"Project '{name}' updated successfully")
        except Exception as ex:
            print(f"Error updating project: {ex}")
            self.show_status(f"Error updating project: {str(ex)}", is_error=True)
        if hasattr(self, 'page') and self.page:
            self.page.update()

    def delete_project(self, proj):
        # Define dialog close function
        def close_dialog(e):
            self._close_dialog(dialog)

        # Define delete function
        def confirm_delete(e):
            self.page.run_task(self._delete_project_async, dialog, proj.get("id"), proj.get("name", "Project"))

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
        self._open_dialog(dialog)

    async def _delete_project_async(self, dialog, project_id, project_name):
        try:
            await self.auditing_client.delete_project(project_id)
            self._close_dialog(dialog)
            await self._load_projects_async()
            self.show_status(f"Project '{project_name}' deleted successfully")
        except Exception as ex:
            print(f"Error deleting project: {ex}")
            self.show_status(f"Error deleting project: {str(ex)}", is_error=True)
        if hasattr(self, 'page') and self.page:
            self.page.update()

    def view_project_details(self, proj):
        colors = get_theme_colors(self.page.theme_mode if hasattr(self.page, "theme_mode") else ft.ThemeMode.LIGHT)
        status_color = self.get_status_color(proj.get("status"))
        risk_color = self.get_risk_color(proj.get("risk_level"))

        start_date = proj.get("start_date") or "-"
        end_date = proj.get("end_date") or "-"
        timeline = f"{start_date} - {end_date}"

        dialog = ft.AlertDialog(
            title=ft.Text(f"Project: {proj.get('name', '-')}", size=20),
            content=ft.Column([
                ft.Row([ft.Text("Status:", weight=ft.FontWeight.BOLD), ft.Text(str(proj.get("status", "-")), color=status_color)]),
                ft.Row([ft.Text("Risk Level:", weight=ft.FontWeight.BOLD), ft.Text(str(proj.get("risk_level", "-")), color=risk_color)]),
                ft.Row([ft.Text("Department:", weight=ft.FontWeight.BOLD), ft.Text(str(proj.get("department_name", "-")))]),
                ft.Row([ft.Text("Manager:", weight=ft.FontWeight.BOLD), ft.Text(str(proj.get("manager", "-")))]),
                ft.Row([ft.Text("Timeline:", weight=ft.FontWeight.BOLD), ft.Text(timeline)]),
                ft.Row([ft.Text("Budget:", weight=ft.FontWeight.BOLD), ft.Text(str(proj.get("budget", "-")))]),
                ft.Divider(),
                ft.Text("Description:", weight=ft.FontWeight.BOLD),
                ft.Text(str(proj.get("description", "")) or "-", color=colors.text_primary),
            ], height=420, scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.TextButton("Close", on_click=lambda e: self._close_dialog(dialog)),
                ft.ElevatedButton("Edit", on_click=lambda e: (self._close_dialog(dialog), self.edit_project(proj))),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self._open_dialog(dialog)

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
        elif status == "Active":
            return "#3498db"  # Blue
        elif status == "On Hold":
            return "#f39c12"  # Orange
        elif status == "Cancelled":
            return "#e74c3c"  # Red
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
