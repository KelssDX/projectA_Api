import flet as ft
from src.models.user import User
import time


class LoginView(ft.Container):
    def __init__(self, page, on_login_success):
        super().__init__()
        self.page = page
        self.on_login_success = on_login_success
        self.expand = True
        self.bgcolor = "#f5f7fa"

        # Error message container for displaying login errors
        self.error_container = ft.Container(
            visible=False,
            padding=10,
            bgcolor="#ffebee",
            border_radius=5,
            content=ft.Text("", color="#b71c1c")
        )

        # Username field
        self.username_field = ft.TextField(
            label="Username",
            hint_text="Enter your username",
            border=ft.InputBorder.OUTLINE,
            width=350,
            height=50
        )

        # Password field
        self.password_field = ft.TextField(
            label="Password",
            hint_text="Enter your password",
            password=True,
            can_reveal_password=True,
            border=ft.InputBorder.OUTLINE,
            width=350,
            height=50
        )

        # Login button
        self.login_button = ft.ElevatedButton(
            text="Login",
            width=350,
            bgcolor="#3498db",
            color="white",
            on_click=self.handle_login
        )

        # Create login card
        self.login_card = ft.Card(
            elevation=5,
            content=ft.Container(
                width=400,
                padding=30,
                bgcolor="white",
                content=ft.Column(
                    [
                        ft.Container(
                            content=ft.Text(
                                "Risk Assessment App",
                                size=24,
                                weight=ft.FontWeight.BOLD,
                                color="#2c3e50"
                            ),
                            alignment=ft.alignment.center,
                            margin=ft.margin.only(bottom=10)
                        ),
                        ft.Container(
                            content=ft.Text(
                                "Sign in to your account",
                                size=16,
                                color="#95a5a6"
                            ),
                            alignment=ft.alignment.center,
                            margin=ft.margin.only(bottom=20)
                        ),
                        self.error_container,
                        ft.Container(
                            content=self.username_field,
                            margin=ft.margin.only(top=10, bottom=10)
                        ),
                        ft.Container(
                            content=self.password_field,
                            margin=ft.margin.only(top=10, bottom=20)
                        ),
                        ft.Container(
                            content=self.login_button,
                            margin=ft.margin.only(top=10)
                        ),
                        ft.Container(
                            content=ft.Text(
                                "Forgot password?",
                                color="#3498db",
                                size=14
                            ),
                            alignment=ft.alignment.center,
                            margin=ft.margin.only(top=20)
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                )
            )
        )

        # Center the login card in the page
        self.content = ft.Container(
            content=self.login_card,
            alignment=ft.alignment.center
        )

    def handle_login(self, e):
        """Handle login button click"""
        username = self.username_field.value
        password = self.password_field.value

        # Basic validation
        if not username or not password:
            self.error_container.content.value = "Please enter both username and password"
            self.error_container.visible = True
            self.page.update()
            return

        # Disable login button and show loading state
        self.login_button.text = "Logging in..."
        self.login_button.disabled = True
        self.page.update()

        # Simulate network delay
        time.sleep(0.5)

        # Check credentials - in a real app, this would call the API
        if username == "admin" and password == "admin":
            # Create a mock user object
            user = User(
                id=1,
                username="admin",
                name="Admin User",
                email="admin@example.com",
                role="admin"
            )

            # Call the success callback
            self.on_login_success(user)
        else:
            # Show error message
            self.error_container.content.value = "Invalid username or password"
            self.error_container.visible = True
            self.login_button.text = "Login"
            self.login_button.disabled = False
            self.page.update()
