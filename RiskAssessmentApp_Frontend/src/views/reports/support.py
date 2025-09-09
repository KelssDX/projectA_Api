import flet as ft
from flet import Icons
from src.models.user import User
from src.utils.theme import get_theme_colors, create_modern_card, create_modern_button, apply_theme_to_control
from src.views.common.base_view import BaseView


class SupportView(BaseView):
    def __init__(self, page, user):
        self.page = page
        self.user = user
        colors = get_theme_colors(self.page.theme_mode if hasattr(self.page, "theme_mode") else ft.ThemeMode.LIGHT)
        actions = [create_modern_button(colors, "New Ticket", icon=Icons.ADD, on_click=self.create_new_ticket, style="primary")]
        super().__init__(page, "Support Tickets", actions=actions, colors=colors)

        # Action bar
        action_bar = create_modern_card(
            colors,
            ft.Row([
                ft.Container(
                    width=150,
                    height=30,
                    content=ft.Row([
                        ft.Text("All Status", size=14, color=colors.text_primary),
                        ft.Container(expand=True),
                        ft.Container(width=20, height=20, content=ft.Text("▼", size=10, color=colors.text_secondary))
                    ]),
                    on_click=self.show_status_filter
                ),
                ft.Container(
                    width=150,
                    height=30,
                    margin=ft.margin.only(left=20),
                    content=ft.Row([
                        ft.Text("All Priority", size=14, color=colors.text_primary),
                        ft.Container(expand=True),
                        ft.Container(width=20, height=20, content=ft.Text("▼", size=10, color=colors.text_secondary))
                    ]),
                    on_click=self.show_priority_filter
                ),
                ft.Container(expand=True),
                create_modern_button(colors, "New Ticket", icon=Icons.ADD, on_click=self.create_new_ticket, style="primary")
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        )

        # Tickets table
        tickets_table = self.create_tickets_table()

        # Compose as cards under BaseView
        self.cards_column.controls.clear()
        self.add_card(action_bar)
        self.add_card(tickets_table)

        try:
            apply_theme_to_control(self, colors)
            if hasattr(self, 'page') and self.page:
                self.page.update()
        except Exception:
            pass

    def apply_theme(self, colors):
        try:
            self.bgcolor = colors.bg
            # Rebuild like Dashboard to refresh color tokens
            self.__init__(self.page, self.user)
            apply_theme_to_control(self, colors)
            if hasattr(self, 'page') and self.page:
                self.page.update()
        except Exception as e:
            print(f"Error applying theme to support view: {e}")

    def create_tickets_table(self):
        # Table header
        header = ft.Container(
            height=40,
            bgcolor="#f5f7fa",
            border=ft.border.only(bottom=ft.BorderSide(1, "#e6e9ed")),
            padding=ft.padding.only(left=30, right=30),
            content=ft.Row([
                ft.Container(width=80, content=ft.Text("ID", weight=ft.FontWeight.BOLD, color="#2c3e50")),
                ft.Container(width=300, content=ft.Text("Title", weight=ft.FontWeight.BOLD, color="#2c3e50")),
                ft.Container(width=150, content=ft.Text("Status", weight=ft.FontWeight.BOLD, color="#2c3e50")),
                ft.Container(width=150, content=ft.Text("Priority", weight=ft.FontWeight.BOLD, color="#2c3e50")),
                ft.Container(width=150, content=ft.Text("Created", weight=ft.FontWeight.BOLD, color="#2c3e50")),
                ft.Container(width=200, content=ft.Text("Actions", weight=ft.FontWeight.BOLD, color="#2c3e50",
                                                        text_align=ft.TextAlign.CENTER))
            ])
        )

        # No tickets available - show empty state
        rows = ft.Column([
            ft.Container(
                height=200,
                content=ft.Column([
                    ft.Icon(Icons.SUPPORT_AGENT, size=48, color="#95a5a6"),
                    ft.Text("No support tickets found", size=16, color="#95a5a6"),
                    ft.Text("Submit a ticket to get started", size=12, color="#95a5a6")
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            )
        ], spacing=0)

        # Wrap in a container
        table = ft.Container(
            expand=True,
            content=ft.Column([header, rows], spacing=0)
        )

        return table

    def create_ticket_row(self, id, title, status, priority, created_date, row_index):
        row_bgcolor = "#f9f9f9" if row_index % 2 == 1 else "white"

        # Set status color
        status_color = "#95a5a6"  # Default gray
        if status == "Open":
            status_color = "#3498db"  # Blue
        elif status == "In Progress":
            status_color = "#f39c12"  # Orange
        elif status == "Closed":
            status_color = "#2ecc71"  # Green

        # Set priority color
        priority_color = "#95a5a6"  # Default gray
        if priority == "Critical":
            priority_color = "#e74c3c"  # Red
        elif priority == "High":
            priority_color = "#e67e22"  # Dark orange
        elif priority == "Medium":
            priority_color = "#f39c12"  # Orange
        elif priority == "Low":
            priority_color = "#2ecc71"  # Green

        return ft.Container(
            height=60,
            bgcolor=row_bgcolor,
            border=ft.border.only(bottom=ft.BorderSide(1, "#e6e9ed")),
            padding=ft.padding.only(left=30, right=30),
            content=ft.Row([
                ft.Container(width=80, content=ft.Text(id, color="#2c3e50")),
                ft.Container(width=300, content=ft.Text(title, color="#2c3e50")),
                ft.Container(
                    width=150,
                    content=ft.Container(
                        bgcolor=status_color,
                        border_radius=15,
                        padding=ft.padding.only(left=10, right=10, top=5, bottom=5),
                        content=ft.Text(status, color="white", size=12, weight=ft.FontWeight.BOLD)
                    )
                ),
                ft.Container(
                    width=150,
                    content=ft.Container(
                        bgcolor=priority_color,
                        border_radius=15,
                        padding=ft.padding.only(left=10, right=10, top=5, bottom=5),
                        content=ft.Text(priority, color="white", size=12, weight=ft.FontWeight.BOLD)
                    )
                ),
                ft.Container(width=150, content=ft.Text(created_date, color="#2c3e50")),
                ft.Container(
                    width=200,
                    content=ft.Row([
                        ft.Container(
                            width=40,
                            height=30,
                            bgcolor="#3498db",
                            border_radius=5,
                            alignment=ft.alignment.center,
                            content=ft.Icon(ft.icons.VISIBILITY, color="white", size=16),
                            on_click=lambda e, id=id: self.view_ticket(id)
                        ),
                        ft.Container(width=10),
                        ft.Container(
                            width=40,
                            height=30,
                            bgcolor="#2ecc71",
                            border_radius=5,
                            alignment=ft.alignment.center,
                            content=ft.Icon(ft.icons.EDIT, color="white", size=16),
                            on_click=lambda e, id=id: self.edit_ticket(id)
                        ),
                        ft.Container(width=10),
                        ft.Container(
                            width=40,
                            height=30,
                            bgcolor="#e74c3c",
                            border_radius=5,
                            alignment=ft.alignment.center,
                            content=ft.Icon(ft.icons.DELETE, color="white", size=16),
                            on_click=lambda e, id=id: self.delete_ticket(id)
                        )
                    ], alignment=ft.MainAxisAlignment.CENTER)
                )
            ])
        )

    def show_status_filter(self, e):
        """Show status filter dropdown"""
        dialog = ft.AlertDialog(
            title=ft.Text("Select Status"),
            content=ft.Column([
                ft.Container(
                    content=ft.Text("All Status"),
                    on_click=self.close_dialog
                ),
                ft.Container(
                    content=ft.Text("Open"),
                    on_click=self.close_dialog
                ),
                ft.Container(
                    content=ft.Text("In Progress"),
                    on_click=self.close_dialog
                ),
                ft.Container(
                    content=ft.Text("Closed"),
                    on_click=self.close_dialog
                ),
            ], spacing=10, height=150),
        )

        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def show_priority_filter(self, e):
        """Show priority filter dropdown"""
        dialog = ft.AlertDialog(
            title=ft.Text("Select Priority"),
            content=ft.Column([
                ft.Container(
                    content=ft.Text("All Priority"),
                    on_click=self.close_dialog
                ),
                ft.Container(
                    content=ft.Text("Critical"),
                    on_click=self.close_dialog
                ),
                ft.Container(
                    content=ft.Text("High"),
                    on_click=self.close_dialog
                ),
                ft.Container(
                    content=ft.Text("Medium"),
                    on_click=self.close_dialog
                ),
                ft.Container(
                    content=ft.Text("Low"),
                    on_click=self.close_dialog
                ),
            ], spacing=10, height=180),
        )

        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def create_new_ticket(self, e):
        """Show dialog to create a new ticket"""
        # Create form fields
        title_field = ft.TextField(
            label="Title",
            hint_text="Enter a brief title for your issue",
            border=ft.InputBorder.OUTLINE,
            width=400
        )

        description_field = ft.TextField(
            label="Description",
            hint_text="Describe your issue in detail",
            multiline=True,
            min_lines=5,
            max_lines=10,
            border=ft.InputBorder.OUTLINE,
            width=400
        )

        priority_dropdown = ft.Dropdown(
            label="Priority",
            width=400,
            options=[
                ft.dropdown.Option("Critical"),
                ft.dropdown.Option("High"),
                ft.dropdown.Option("Medium"),
                ft.dropdown.Option("Low"),
            ],
            border=ft.InputBorder.OUTLINE,
        )

        # Create dialog
        dialog = ft.AlertDialog(
            title=ft.Text("Create New Support Ticket"),
            content=ft.Column([
                title_field,
                description_field,
                priority_dropdown,
            ], width=400, height=350, spacing=20, scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.TextButton("Cancel", on_click=self.close_dialog),
                ft.TextButton("Submit", on_click=lambda e: self.submit_ticket(
                    title_field.value,
                    description_field.value,
                    priority_dropdown.value
                )),
            ],
        )

        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def submit_ticket(self, title, description, priority):
        """Submit a new ticket"""
        if not title or not description or not priority:
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

        # Close the form dialog
        self.page.dialog.open = False

        # Show success message
        success_dialog = ft.AlertDialog(
            title=ft.Text("Success"),
            content=ft.Text("Your support ticket has been submitted successfully."),
            actions=[
                ft.TextButton("OK", on_click=self.close_dialog),
            ],
        )

        self.page.dialog = success_dialog
        success_dialog.open = True
        self.page.update()

    def view_ticket(self, ticket_id):
        """View ticket details"""
        # No ticket data available - show error
        title = "Ticket not found"
        status = "Unknown"
        priority = "Unknown"

        # Create comments section
        comments = ft.Column([
            self.create_comment("Support Team", "2023-03-11",
                                "We're looking into this issue. Could you provide more details about the error you're seeing?"),
            self.create_comment("John Smith", "2023-03-12",
                                "When I click on the dashboard tab, it takes about 30 seconds to load and sometimes shows a timeout error."),
            self.create_comment("Support Team", "2023-03-13",
                                "Thanks for the information. We've identified the issue and are working on a fix. It should be resolved in the next update."),
        ], spacing=10)

        # Create dialog with ticket details
        dialog = ft.AlertDialog(
            title=ft.Text(f"Ticket: {ticket_id} - {title}"),
            content=ft.Column([
                ft.Row([
                    ft.Text("Status:", weight=ft.FontWeight.BOLD),
                    ft.Container(width=10),
                    ft.Container(
                        bgcolor=self.get_status_color(status),
                        border_radius=15,
                        padding=ft.padding.only(left=10, right=10, top=5, bottom=5),
                        content=ft.Text(status, color="white", size=12, weight=ft.FontWeight.BOLD)
                    ),
                    ft.Container(width=20),
                    ft.Text("Priority:", weight=ft.FontWeight.BOLD),
                    ft.Container(width=10),
                    ft.Container(
                        bgcolor=self.get_priority_color(priority),
                        border_radius=15,
                        padding=ft.padding.only(left=10, right=10, top=5, bottom=5),
                        content=ft.Text(priority, color="white", size=12, weight=ft.FontWeight.BOLD)
                    ),
                ]),
                ft.Container(height=10),
                ft.Text("Description:", weight=ft.FontWeight.BOLD),
                ft.Container(
                    bgcolor="#f5f7fa",
                    border_radius=5,
                    padding=10,
                    content=ft.Text("The dashboard is taking too long to load and sometimes shows errors.")
                ),
                ft.Container(height=20),
                ft.Text("Comments:", weight=ft.FontWeight.BOLD),
                comments,
                ft.Container(height=10),
                ft.Text("Add Comment:", weight=ft.FontWeight.BOLD),
                ft.TextField(
                    hint_text="Type your comment here...",
                    multiline=True,
                    min_lines=2,
                    max_lines=5,
                    border=ft.InputBorder.OUTLINE,
                ),
            ], width=500, height=400, spacing=10, scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.TextButton("Close", on_click=self.close_dialog),
                ft.TextButton("Add Comment", on_click=self.close_dialog, color="#3498db"),
            ],
        )

        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def create_comment(self, user, date, text):
        """Create a comment container"""
        return ft.Container(
            bgcolor="#f5f7fa",
            border_radius=5,
            padding=10,
            content=ft.Column([
                ft.Row([
                    ft.Text(user, weight=ft.FontWeight.BOLD, color="#2c3e50"),
                    ft.Container(width=10),
                    ft.Text(date, color="#95a5a6", size=12),
                ]),
                ft.Container(height=5),
                ft.Text(text, color="#2c3e50")
            ], spacing=0)
        )

    def get_status_color(self, status):
        """Get color for status"""
        if status == "Open":
            return "#3498db"  # Blue
        elif status == "In Progress":
            return "#f39c12"  # Orange
        elif status == "Closed":
            return "#2ecc71"  # Green
        return "#95a5a6"  # Gray

    def get_priority_color(self, priority):
        """Get color for priority"""
        if priority == "Critical":
            return "#e74c3c"  # Red
        elif priority == "High":
            return "#e67e22"  # Dark orange
        elif priority == "Medium":
            return "#f39c12"  # Orange
        elif priority == "Low":
            return "#2ecc71"  # Green
        return "#95a5a6"  # Gray

    def edit_ticket(self, ticket_id):
        """Edit ticket"""
        dialog = ft.AlertDialog(
            title=ft.Text(f"Edit Ticket {ticket_id}"),
            content=ft.Text(f"Editing ticket {ticket_id}."),
            actions=[
                ft.TextButton("Close", on_click=self.close_dialog),
            ],
        )

        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def delete_ticket(self, ticket_id):
        """Delete ticket"""
        dialog = ft.AlertDialog(
            title=ft.Text("Confirm Deletion"),
            content=ft.Text(f"Are you sure you want to delete ticket {ticket_id}?"),
            actions=[
                ft.TextButton("Cancel", on_click=self.close_dialog),
                ft.TextButton("Delete", on_click=self.close_dialog, color="#e74c3c"),
            ],
        )

        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def close_dialog(self, e):
        """Close the current dialog"""
        self.page.dialog.open = False
        self.page.update()
