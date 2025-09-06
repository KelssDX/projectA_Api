import flet as ft
from flet import Icons
from src.utils.theme import (
    get_theme_colors,
    apply_theme_to_control,
    create_modern_card,
    create_modern_button,
)
from src.api.identity_client import IdentityAPIClient


class UserManagementView(ft.Container):
    def __init__(self, page, user):
        super().__init__()
        self.page = page
        self.user = user
        self.expand = True
        self.search_value = ""
        self.current_role_filter = "All Roles"
        self.current_dept_filter = "All Departments"

        # Get username safely from either dict or object
        if isinstance(user, dict):
            self.username = user.get("username", "A")
        else:
            self.username = getattr(user, "username", "A") if user else "A"

        # Initialize API client and users list
        self.identity_client = IdentityAPIClient()
        self.users = []
        
        # Load users from API
        self.load_users()

        # Initialize search field
        self.search_field = ft.Container(
            width=240,
            height=30,
            bgcolor="#f5f7fa",
            border=ft.border.all(1, "#e6e9ed"),
            border_radius=15,
            padding=ft.padding.only(left=10, right=10),
            content=ft.Row([
                ft.Icon(Icons.SEARCH, color="#95a5a6", size=18),
                ft.TextField(
                    border=ft.InputBorder.NONE,
                    color="#2c3e50",
                    hint_text="Search users...",
                    hint_style=ft.TextStyle(color="#95a5a6", size=14),
                    expand=True,
                    height=30,
                    content_padding=5,
                    on_change=self.on_search_change
                )
            ])
        )

        colors = get_theme_colors(self.page.theme_mode if hasattr(self.page, "theme_mode") else ft.ThemeMode.LIGHT)

        # Header
        header = ft.Container(
            content=ft.Row([
                ft.Column([
                    ft.Text("User Management", size=24, weight=ft.FontWeight.BOLD, color=colors.text_primary),
                    ft.Text("Manage users and roles", size=14, color=colors.text_secondary)
                ], alignment=ft.CrossAxisAlignment.START),
                ft.Row([
                    self.search_field,
                    ft.Container(
                        margin=ft.margin.only(left=12),
                        content=ft.Container(
                            width=30,
                            height=30,
                            border_radius=15,
                            bgcolor=colors.button_primary,
                            alignment=ft.alignment.center,
                            content=ft.Text(self.username[0].upper() if self.username else "A",
                                            color=colors.button_text, weight=ft.FontWeight.BOLD)
                        )
                    )
                ], spacing=12)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        )

        # Role filter dropdown
        self.role_filter = ft.Container(
            width=150,
            height=30,
            bgcolor="white",
            border=ft.border.all(1, "#e6e9ed"),
            border_radius=5,
            padding=ft.padding.only(left=20, right=10),
            content=ft.Row([
                ft.Text(self.current_role_filter, size=14, color="#2c3e50"),
                ft.Container(expand=True),
                ft.Container(
                    width=20,
                    height=20,
                    content=ft.Text("▼", size=10, color="#95a5a6")
                )
            ]),
            on_click=self.show_role_filter
        )

        # Department filter dropdown
        self.dept_filter = ft.Container(
            width=150,
            height=30,
            bgcolor="white",
            border=ft.border.all(1, "#e6e9ed"),
            border_radius=5,
            margin=ft.margin.only(left=20),
            padding=ft.padding.only(left=20, right=10),
            content=ft.Row([
                ft.Text(self.current_dept_filter, size=14, color="#2c3e50"),
                ft.Container(expand=True),
                ft.Container(
                    width=20,
                    height=20,
                    content=ft.Text("▼", size=10, color="#95a5a6")
                )
            ]),
            on_click=self.show_department_filter
        )

        # Action bar
        # Responsive action bar: filters wrap on small widths; button stays right-aligned
        action_bar = create_modern_card(
            colors,
            ft.Column([
                ft.Row([
                    self.role_filter,
                    self.dept_filter,
                ], spacing=10),
                ft.Row([
                    ft.Container(expand=True),
                    create_modern_button(colors, "Add New User", icon=Icons.PERSON_ADD, on_click=self.add_new_user, style="primary"),
                ], alignment=ft.MainAxisAlignment.END),
            ], spacing=10)
        )

        # Users table
        self.users_table_container = ft.Container(expand=True, content=None)

        # Refresh the table with initial data
        self.refresh_table()

        # Main content
        main_content = ft.Container(
            expand=True,
            bgcolor=None,
            content=ft.Column([
                action_bar,
                ft.Container(height=12),
                create_modern_card(colors, self.users_table_container)
            ], spacing=0, expand=True)
        )


        # Assemble the view
        self.content = ft.Column([
            header,
            main_content
        ], spacing=0, expand=True, scroll=ft.ScrollMode.AUTO)

        # Normalize immediately
        try:
            apply_theme_to_control(self, colors)
        except Exception:
            pass

    # Theming hook
    def apply_theme(self, colors):
        try:
            # Rebuild header/body like Dashboard to refresh tokens
            self.__init__(self.page, self.user)
            apply_theme_to_control(self, colors)
        except Exception:
            pass

    def on_search_change(self, e):
        """Handle search input changes"""
        self.search_value = e.control.value.lower()
        self.refresh_table()

    def load_users(self):
        """Load users from Identity API"""
        if hasattr(self, 'page') and self.page:
            self.page.run_task(self._load_users_async)

    async def _load_users_async(self):
        """Load users data from the Identity API"""
        print("🔧 DEBUG: _load_users_async called")
        try:
            print("🔧 DEBUG: Loading users from Identity API...")
            
            # Get users data from API
            print("🔧 DEBUG: Calling identity_client.get_users()")
            api_users = await self.identity_client.get_users()
            print(f"🔧 DEBUG: API returned {len(api_users) if api_users else 0} users")
            
            if api_users:
                # Convert API data to expected format
                self.users = []
                for user_data in api_users:
                    if isinstance(user_data, dict):
                        self.users.append({
                            'id': user_data.get('id'),
                            'name': user_data.get('name', 'Unknown'),
                            'username': user_data.get('username', 'unknown'),
                            'email': user_data.get('email', 'unknown@example.com'),
                            'role': user_data.get('role', 'User'),
                            'department': user_data.get('department', None)
                        })
                    else:
                        # Convert object to dict if needed
                        self.users.append({
                            'id': getattr(user_data, 'id', None),
                            'name': getattr(user_data, 'name', 'Unknown'),
                            'username': getattr(user_data, 'username', 'unknown'),
                            'email': getattr(user_data, 'email', 'unknown@example.com'),
                            'role': getattr(user_data, 'role', 'User'),
                            'department': getattr(user_data, 'department', None)
                        })
                
                print(f"Loaded {len(self.users)} users from Identity API")
            else:
                print("No users data available from Identity API")
                self.users = []
                
            # Rebuild the UI with new data
            self.refresh_table()
            
            if hasattr(self, 'page') and self.page:
                self.page.update()
                
        except Exception as e:
            print(f"Error loading users from Identity API: {e}")
            self.users = []
            if hasattr(self, 'page') and self.page:
                self.page.update()

    def refresh_table(self):
        """Refresh the users table based on current filters and search"""
        filtered_users = self.users
        colors = get_theme_colors(self.page.theme_mode if hasattr(self.page, "theme_mode") else ft.ThemeMode.LIGHT)

        # Apply search filter
        if self.search_value:
            filtered_users = [user for user in filtered_users
                              if (self.search_value in user["name"].lower() or
                                  self.search_value in user["username"].lower() or
                                  self.search_value in user["email"].lower())]

        # Apply role filter
        if self.current_role_filter != "All Roles":
            filtered_users = [user for user in filtered_users if user["role"] == self.current_role_filter]

        # Apply department filter
        if self.current_dept_filter != "All Departments":
            filtered_users = [user for user in filtered_users if user["department"] == self.current_dept_filter]

        # Create table header
        header = ft.Container(
            height=40,
            bgcolor=None,
            border=ft.border.only(bottom=ft.BorderSide(1, colors.border)),
            padding=ft.padding.only(left=30, right=30),
            content=ft.Row([
                ft.Container(width=200, content=ft.Text("Name", weight=ft.FontWeight.BOLD, color=colors.text_secondary)),
                ft.Container(width=200, content=ft.Text("Username", weight=ft.FontWeight.BOLD, color=colors.text_secondary)),
                ft.Container(width=200, content=ft.Text("Email", weight=ft.FontWeight.BOLD, color=colors.text_secondary)),
                ft.Container(width=150, content=ft.Text("Role", weight=ft.FontWeight.BOLD, color=colors.text_secondary)),
                ft.Container(width=150, content=ft.Text("Department", weight=ft.FontWeight.BOLD, color=colors.text_secondary)),
                ft.Container(width=200, content=ft.Text("Actions", weight=ft.FontWeight.BOLD, color=colors.text_secondary,
                                                        text_align=ft.TextAlign.CENTER))
            ])
        )

        # Create user rows
        rows = ft.Column(spacing=0)
        for i, user in enumerate(filtered_users):
            rows.controls.append(self.create_user_row(
                user.get("id"),
                user["name"],
                user["username"],
                user["email"],
                user["role"],
                user["department"],
                i
            ))

        # Empty state if no users
        if not filtered_users:
            empty_state = ft.Container(
                height=100,
                alignment=ft.alignment.center,
                content=ft.Column([
                    ft.Icon(Icons.SEARCH_OFF, size=40, color="#95a5a6"),
                    ft.Text("No users found", color="#95a5a6", size=16)
                ], spacing=10, alignment=ft.MainAxisAlignment.CENTER)
            )
            rows.controls.append(empty_state)

        # For Flet 0.19.0, use a ListView for scrolling
        # Use a ListView instead of a Container with scroll
        scrollable_rows = ft.ListView(
            expand=True,
            spacing=0,
            auto_scroll=False
        )
        for control in rows.controls:
            scrollable_rows.controls.append(control)

        # Wrap in a container without scroll parameter
        table = ft.Container(
            expand=True,
            content=ft.Column([
                header,
                scrollable_rows
            ], spacing=0)
        )

        # Update the table container
        self.users_table_container.content = table
        self.update()

    def create_user_row(self, user_id, name, username, email, role, department, row_index):
        colors = get_theme_colors(self.page.theme_mode if hasattr(self.page, "theme_mode") else ft.ThemeMode.LIGHT)
        row_bgcolor = colors.surface

        # Set role color
        role_color = "#95a5a6"  # Default gray
        if role == "Admin":
            role_color = "#e74c3c"  # Red
        elif role == "Auditor":
            role_color = "#3498db"  # Blue
        elif role == "User":
            role_color = "#2ecc71"  # Green

        return ft.Container(
            height=60,
            bgcolor=row_bgcolor,
            border=ft.border.only(bottom=ft.BorderSide(1, colors.border)),
            padding=ft.padding.only(left=30, right=30),
            content=ft.Row([
                ft.Container(width=200, content=ft.Text(name, color=colors.text_primary)),
                ft.Container(width=200, content=ft.Text(username, color=colors.text_primary)),
                ft.Container(width=200, content=ft.Text(email, color=colors.text_primary)),
                ft.Container(
                    width=150,
                    content=ft.Container(
                        width=80,
                        height=30,
                        bgcolor=role_color,
                        border_radius=15,
                        alignment=ft.alignment.center,
                        content=ft.Text(role, color="white", size=12, weight=ft.FontWeight.BOLD)
                    )
                ),
                ft.Container(width=150, content=ft.Text(department if department else "-", color=colors.text_primary)),
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
                            on_click=lambda e, uid=user_id: self.view_user(uid)
                        ),
                        ft.Container(width=10),
                        ft.Container(
                            width=40,
                            height=30,
                            bgcolor="#2ecc71",
                            border_radius=5,
                            alignment=ft.alignment.center,
                            content=ft.Icon(Icons.EDIT, color="white", size=16),
                            on_click=lambda e, uid=user_id: self.edit_user(uid)
                        ),
                        ft.Container(width=10),
                        ft.Container(
                            width=40,
                            height=30,
                            bgcolor="#e74c3c",
                            border_radius=5,
                            alignment=ft.alignment.center,
                            content=ft.Icon(Icons.DELETE, color="white", size=16),
                            on_click=lambda e, uid=user_id: self.delete_user(uid)
                        )
                    ], alignment=ft.MainAxisAlignment.CENTER)
                )
            ])
        )

    def show_role_filter(self, e):
        """Show role filter dropdown"""
        dialog = ft.AlertDialog(
            title=ft.Text("Select Role"),
            content=ft.Column([
                ft.Container(
                    padding=10,
                    content=ft.Text("All Roles"),
                    on_click=lambda e: self.apply_role_filter("All Roles")
                ),
                ft.Container(
                    padding=10,
                    content=ft.Text("Admin"),
                    on_click=lambda e: self.apply_role_filter("Admin")
                ),
                ft.Container(
                    padding=10,
                    content=ft.Text("Auditor"),
                    on_click=lambda e: self.apply_role_filter("Auditor")
                ),
                ft.Container(
                    padding=10,
                    content=ft.Text("User"),
                    on_click=lambda e: self.apply_role_filter("User")
                ),
            ], spacing=0, height=160),
        )

        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def apply_role_filter(self, role):
        """Apply selected role filter"""
        self.current_role_filter = role
        self.role_filter.content.controls[0].value = role
        self.close_dialog(None)
        self.refresh_table()

    def show_department_filter(self, e):
        """Show department filter dropdown"""
        dialog = ft.AlertDialog(
            title=ft.Text("Select Department"),
            content=self._build_departments_filter_content(),
        )

        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def apply_dept_filter(self, department):
        """Apply selected department filter"""
        self.current_dept_filter = department
        self.dept_filter.content.controls[0].value = department
        self.close_dialog(None)
        self.refresh_table()

    def _build_departments_filter_content(self):
        """Build department filter options from API departments"""
        try:
            # Fetch department names synchronously for the dialog
            import asyncio as _asyncio
            from src.api.auditing_client import AuditingAPIClient
            client = AuditingAPIClient()
            departments = _asyncio.get_event_loop().run_until_complete(client.get_departments())
            names = [d.get("name") for d in (departments or []) if isinstance(d, dict) and d.get("name")]
        except Exception:
            names = ["IT", "Finance", "Operations", "Marketing", "Human Resources"]

        items = [
            ft.Container(
                padding=10,
                content=ft.Text("All Departments"),
                on_click=lambda e: self.apply_dept_filter("All Departments")
            )
        ]
        for n in names:
            items.append(
                ft.Container(
                    padding=10,
                    content=ft.Text(n),
                    on_click=lambda e, name=n: self.apply_dept_filter(name)
                )
            )

        return ft.Column(items, spacing=0, height=min(40 * max(1, len(items)), 360))

    def add_new_user(self, e):
        """Show dialog to add a new user"""
        # Create form fields
        name_field = ft.TextField(
            label="Full Name",
            border=ft.InputBorder.OUTLINE,
            width=400
        )

        username_field = ft.TextField(
            label="Username",
            border=ft.InputBorder.OUTLINE,
            width=400
        )

        email_field = ft.TextField(
            label="Email",
            border=ft.InputBorder.OUTLINE,
            width=400
        )

        password_field = ft.TextField(
            label="Password",
            password=True,
            can_reveal_password=True,
            border=ft.InputBorder.OUTLINE,
            width=400
        )

        role_dropdown = ft.Dropdown(
            label="Role",
            width=400,
            options=[
                ft.dropdown.Option("Admin"),
                ft.dropdown.Option("Auditor"),
                ft.dropdown.Option("User"),
            ],
            border=ft.InputBorder.OUTLINE,
        )

        department_dropdown = ft.Dropdown(
            label="Department",
            width=400,
            options=[
                ft.dropdown.Option("IT"),
                ft.dropdown.Option("Finance"),
                ft.dropdown.Option("Operations"),
                ft.dropdown.Option("Marketing"),
                ft.dropdown.Option("Human Resources"),
            ],
            border=ft.InputBorder.OUTLINE,
        )

        # For Flet 0.19.0, avoid using scroll parameter on Container
        form_column = ft.Column([
            name_field,
            username_field,
            email_field,
            password_field,
            role_dropdown,
            department_dropdown,
        ], width=400, spacing=20)

        # Create dialog without scroll parameter
        dialog = ft.AlertDialog(
            title=ft.Text("Add New User"),
            content=form_column,
            actions=[
                ft.TextButton("Cancel", on_click=self.close_dialog),
                ft.TextButton("Save", on_click=lambda e: self.page.run_task(self.save_new_user(
                    name_field.value,
                    username_field.value,
                    email_field.value,
                    password_field.value,
                    role_dropdown.value,
                    department_dropdown.value
                ))),
            ],
        )

        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    async def save_new_user(self, name, username, email, password, role, department):
        """Save a new user via Identity API"""
        if not name or not username or not email or not password or not role:
            # Show validation error
            error_dialog = ft.AlertDialog(
                title=ft.Text("Validation Error"),
                content=ft.Text("Please fill in all required fields."),
                actions=[
                    ft.TextButton("OK", on_click=self.close_dialog),
                ],
            )

            self.page.dialog = error_dialog
            error_dialog.open = True
            self.page.update()
            return

        # Resolve role_id
        role_map = {"Admin": 1, "Auditor": 2, "User": 3}
        role_id = role_map.get(role, 3)

        # Resolve department_id from name
        department_id = None
        try:
            from src.api.auditing_client import AuditingAPIClient
            client = AuditingAPIClient()
            departments = await client.get_departments()
            for d in departments or []:
                if isinstance(d, dict) and d.get("name") == department:
                    department_id = d.get("id")
                    break
        except Exception:
            department_id = None

        # Split name into firstname/lastname
        parts = (name or "").strip().split()
        firstname = parts[0] if parts else username
        lastname = " ".join(parts[1:]) if len(parts) > 1 else ""

        # Call Identity API
        try:
            payload = {
                "username": username,
                "password": password,
                "firstname": firstname,
                "lastname": lastname,
                "email": email,
                "roleId": role_id,
                "departmentId": department_id,
            }
            await self.identity_client.create_user(payload)
            # Reload users
            await self._load_users_async()
        except Exception as ex:
            err = ft.AlertDialog(title=ft.Text("Create Failed"), content=ft.Text(str(ex)), actions=[ft.TextButton("OK", on_click=self.close_dialog)])
            self.page.dialog = err
            err.open = True
            self.page.update()
            return

        # Close any dialog and show success
        self.page.dialog.open = False
        success_dialog = ft.AlertDialog(
            title=ft.Text("Success"),
            content=ft.Text("User has been created successfully."),
            actions=[ft.TextButton("OK", on_click=self.close_dialog)],
        )
        self.page.dialog = success_dialog
        success_dialog.open = True
        self.page.update()

    def view_user(self, user_id_or_username):
        """View user details"""
        # Find the user in our list
        user = None
        for u in self.users:
            if u.get("id") == user_id_or_username or u.get("username") == user_id_or_username:
                user = u
                break
        if not user:
            self.show_error_dialog("User not found")
            return

        name = user["name"]
        email = user["email"]
        role = user["role"]
        department = user["department"]

        # Set role color
        role_color = "#95a5a6"  # Default gray
        if role == "Admin":
            role_color = "#e74c3c"  # Red
        elif role == "Auditor":
            role_color = "#3498db"  # Blue
        elif role == "User":
            role_color = "#2ecc71"  # Green

        # Create dialog with user details
        dialog = ft.AlertDialog(
            title=ft.Text(f"User Details: {user.get('username')}") ,
            content=ft.Column([
                ft.Container(
                    alignment=ft.alignment.center,
                    content=ft.Container(
                        width=100,
                        height=100,
                        border_radius=50,
                        bgcolor=role_color,
                        alignment=ft.alignment.center,
                        content=ft.Text(name[0], size=40, color="white", weight=ft.FontWeight.BOLD)
                    )
                ),
                ft.Container(height=20),
                ft.Container(
                    alignment=ft.alignment.center,
                    content=ft.Text(name, size=24, weight=ft.FontWeight.BOLD, color="#2c3e50")
                ),
                ft.Container(
                    alignment=ft.alignment.center,
                    content=ft.Container(
                        padding=10,
                        bgcolor=role_color,
                        border_radius=15,
                        content=ft.Text(role, color="white", weight=ft.FontWeight.BOLD)
                    )
                ),
                ft.Container(height=20),
                ft.Row([
                    ft.Text("Username:", weight=ft.FontWeight.BOLD),
                    ft.Container(width=10),
                    ft.Text(username)
                ]),
                ft.Row([
                    ft.Text("Email:", weight=ft.FontWeight.BOLD),
                    ft.Container(width=10),
                    ft.Text(email)
                ]),
                ft.Row([
                    ft.Text("Department:", weight=ft.FontWeight.BOLD),
                    ft.Container(width=10),
                    ft.Text(department if department else "-")
                ]),
                ft.Container(height=20),
                ft.Text("Activity", weight=ft.FontWeight.BOLD),
                ft.Container(
                    bgcolor="#f5f7fa",
                    border_radius=5,
                    padding=10,
                    content=ft.Column([
                        ft.Text("Last login: 2025-03-15 09:30:22"),
                        ft.Text("Assessments created: 12"),
                        ft.Text("Assessments reviewed: 8"),
                    ])
                )
            ], width=400, spacing=5),
            actions=[
                ft.TextButton("Close", on_click=self.close_dialog),
                # Remove the color parameter
                ft.TextButton("Edit User", on_click=lambda e: self.edit_user(username)),
            ],
        )

        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def edit_user(self, user_id_or_username):
        """Edit user"""
        # Find the user in our list
        user = None
        for u in self.users:
            if u.get("id") == user_id_or_username or u.get("username") == user_id_or_username:
                user = u
                break
        if not user:
            self.show_error_dialog("User not found")
            return

        name = user["name"]
        email = user["email"]
        role = user["role"]
        department = user["department"]

        # Create form fields
        name_field = ft.TextField(
            label="Full Name",
            value=name,
            border=ft.InputBorder.OUTLINE,
            width=400
        )

        username_field = ft.TextField(
            label="Username",
            value=username,
            border=ft.InputBorder.OUTLINE,
            width=400,
            disabled=True  # Username cannot be changed
        )

        email_field = ft.TextField(
            label="Email",
            value=email,
            border=ft.InputBorder.OUTLINE,
            width=400
        )

        password_field = ft.TextField(
            label="Password",
            hint_text="Leave blank to keep current password",
            password=True,
            can_reveal_password=True,
            border=ft.InputBorder.OUTLINE,
            width=400
        )

        role_dropdown = ft.Dropdown(
            label="Role",
            value=role,
            width=400,
            options=[
                ft.dropdown.Option("Admin"),
                ft.dropdown.Option("Auditor"),
                ft.dropdown.Option("User"),
            ],
            border=ft.InputBorder.OUTLINE,
        )

        dept_options = [
            ft.dropdown.Option("IT"),
            ft.dropdown.Option("Finance"),
            ft.dropdown.Option("Operations"),
            ft.dropdown.Option("Marketing"),
            ft.dropdown.Option("Human Resources"),
        ]

        department_dropdown = ft.Dropdown(
            label="Department",
            value=department,
            width=400,
            options=dept_options,
            border=ft.InputBorder.OUTLINE,
        )

        # Create a column without scroll parameter
        form_column = ft.Column([
            name_field,
            username_field,
            email_field,
            password_field,
            role_dropdown,
            department_dropdown,
        ], width=400, spacing=20)

        # Create dialog
        dialog = ft.AlertDialog(
            title=ft.Text(f"Edit User: {user['username']}"),
            content=form_column,
            actions=[
                ft.TextButton("Cancel", on_click=self.close_dialog),
                ft.TextButton("Save", on_click=lambda e, uid=user.get('id'): self.save_edited_user(
                    uid,
                    name_field.value,
                    email_field.value,
                    password_field.value,
                    role_dropdown.value,
                    department_dropdown.value
                )),
            ],
        )

        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    async def save_edited_user(self, user_id, name, email, password, role, department):
        """Save edited user information"""
        if not name or not email or not role:
            # Show validation error
            error_dialog = ft.AlertDialog(
                title=ft.Text("Validation Error"),
                content=ft.Text("Please fill in all required fields."),
                actions=[
                    ft.TextButton("OK", on_click=self.close_dialog),
                ],
            )

            self.page.dialog = error_dialog
            error_dialog.open = True
            self.page.update()
            return

        # Map department name to department_id via Auditing API
        department_id = None
        try:
            import asyncio as _asyncio
            from src.api.auditing_client import AuditingAPIClient
            client = AuditingAPIClient()
            departments = await client.get_departments()
            for d in departments or []:
                if isinstance(d, dict) and d.get("name") == department:
                    department_id = d.get("id")
                    break
        except Exception:
            department_id = None

        # Prepare update payload
        update_data = {
            "name": name,
            "email": email,
            "department_id": department_id
        }
        # Optional role mapping
        role_map = {"Admin": 1, "Auditor": 2, "User": 3}
        if role in role_map:
            update_data["role_id"] = role_map[role]
        if password:
            update_data["password"] = password

        # Call Identity API
        try:
            updated = await self.identity_client.update_user(user_id, update_data)
            # Refresh list
            await self._load_users_async()
        except Exception as ex:
            self.show_error_dialog(f"Failed to update user: {ex}")
            return

        # Close the form dialog
        self.page.dialog.open = False

        # Show success message
        success_dialog = ft.AlertDialog(
            title=ft.Text("Success"),
            content=ft.Text("User has been updated successfully."),
            actions=[
                ft.TextButton("OK", on_click=self.close_dialog),
            ],
        )

        self.page.dialog = success_dialog
        success_dialog.open = True
        self.page.update()

        # Refresh the table
        self.refresh_table()

    def delete_user(self, user_id_or_username):
        """Delete user"""
        dialog = ft.AlertDialog(
            title=ft.Text("Confirm Deletion"),
            content=ft.Column([
                ft.Text("Are you sure you want to delete this user?"),
                ft.Container(height=10),
                ft.Text("This action cannot be undone.", color="#e74c3c"),
            ]),
            actions=[
                ft.TextButton("Cancel", on_click=self.close_dialog),
                ft.TextButton("Delete", on_click=lambda e, uid=user_id_or_username: self.confirm_delete_user(uid)),
            ],
        )

        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def confirm_delete_user(self, user_id_or_username):
        """Confirm user deletion"""
        # Close the confirmation dialog
        self.page.dialog.open = False

        # Show a loading indicator
        loading_dialog = ft.AlertDialog(
            modal=True,
            content=ft.Column([
                ft.ProgressRing(),
                ft.Text("Deleting user..."),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        )

        self.page.dialog = loading_dialog
        loading_dialog.open = True
        self.page.update()

        # Perform API delete
        async def _do_delete():
            try:
                # Find id if username was provided
                uid = None
                if isinstance(user_id_or_username, int):
                    uid = user_id_or_username
                else:
                    for u in self.users:
                        if u.get("username") == user_id_or_username:
                            uid = u.get("id")
                            break
                if uid is None:
                    raise Exception("Unable to resolve user id")
                await self.identity_client.delete_user(uid)
                await self._load_users_async()
            except Exception as ex:
                self.page.snack_bar = ft.SnackBar(content=ft.Text(f"Delete failed: {ex}"), bgcolor=ft.colors.RED_400)
                self.page.snack_bar.open = True
                self.page.update()
            finally:
                # finalize dialog
                self.finalize_delete_user(None)

        try:
            # Run the async deletion
            self.page.run_task(_do_delete)
        except Exception:
            self.finalize_delete_user(None)

        # Instead of using page.after, use a Timer from the threading module
        import threading
        timer = threading.Timer(1.0, lambda: self.finalize_delete_user(username))
        timer.start()

    def finalize_delete_user(self, _):
        """Finalize user deletion"""
        # Close the loading dialog
        self.page.dialog.open = False

        # Show success message
        success_dialog = ft.AlertDialog(
            title=ft.Text("Success"),
            content=ft.Text("User has been deleted successfully."),
            actions=[
                ft.TextButton("OK", on_click=self.close_dialog),
            ],
        )

        self.page.dialog = success_dialog
        success_dialog.open = True
        self.page.update()

        # Refresh the table
        self.refresh_table()

    def show_error_dialog(self, message):
        """Show error dialog"""
        dialog = ft.AlertDialog(
            title=ft.Text("Error"),
            content=ft.Text(message),
            actions=[
                ft.TextButton("OK", on_click=self.close_dialog),
            ],
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def close_dialog(self, e):
        """Close the current dialog"""
        self.page.dialog.open = False
        self.page.update()

    def apply_theme(self, colors):
        """Apply theme colors to the user management view"""
        try:
            # Update the container's background color
            self.bgcolor = colors.bg
            
            # Apply theme to existing controls
            def apply_colors_to_control(control):
                if isinstance(control, ft.Text):
                    if not control.color or control.color in ["#333333", "#666666", "#999999"]:
                        control.color = colors.text_primary
                elif isinstance(control, ft.Container):
                    if not control.bgcolor or control.bgcolor in ["white", "#f5f5f5", "#e6e9ed"]:
                        control.bgcolor = colors.surface
                
                # Recursively apply to children
                if hasattr(control, 'controls'):
                    for child in control.controls:
                        apply_colors_to_control(child)
                elif hasattr(control, 'content') and control.content:
                    apply_colors_to_control(control.content)
            
            apply_colors_to_control(self)
            
            if hasattr(self, 'page') and self.page:
                self.page.update()
        except Exception as e:
            print(f"Error applying theme to user management: {e}")
