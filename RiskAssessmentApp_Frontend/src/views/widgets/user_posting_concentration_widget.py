import flet as ft
from flet import Icons
from src.api.auditing_client import AuditingAPIClient
from src.views.widgets.base_widget import BaseWidget


class UserPostingConcentrationWidget(BaseWidget):
    def __init__(self, page, reference_id=None, audit_universe_id=None, on_drill_down=None):
        super().__init__(
            page=page,
            title="User Posting Concentration",
            icon=Icons.PEOPLE_ALT,
            description="Highlights unusual journal-posting concentration by user"
        )
        self.reference_id = reference_id
        self.audit_universe_id = audit_universe_id
        self.on_drill_down = on_drill_down
        self.auditing_client = AuditingAPIClient()
        self.analytics = None

    def build_content(self):
        self.content_container = ft.Container(
            content=ft.Column(
                [ft.ProgressRing(width=30, height=30), ft.Text("Loading user posting concentration...", size=12)],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            ),
            expand=True,
            alignment=ft.alignment.center
        )
        self.load_data()
        return self.content_container

    def load_data(self):
        if self.page:
            self.page.run_task(self._load_data_async)

    async def _load_data_async(self):
        try:
            self.analytics = await self.auditing_client.get_user_posting_concentration(reference_id=self.reference_id)
            self._update_display()
        except Exception as e:
            self.content_container.content = ft.Text(f"Error: {str(e)}", color="red")
            self.page.update()

    def _update_display(self):
        data = self.analytics or {}
        users = data.get("users", [])
        if not users:
            self.content_container.content = ft.Column([
                ft.Icon(Icons.PERSON_OFF, size=40, color=self.colors.text_secondary),
                ft.Text("No user posting data available", size=14, weight=ft.FontWeight.BOLD),
                ft.Text("Load journal-entry staging data to analyse posting concentration.", size=12, color=self.colors.text_secondary),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER, expand=True)
            self.page.update()
            return

        rows = []
        for user in users:
            share = float(user.get("percentageOfEntries", 0) or 0)
            rows.append(
                ft.Container(
                    padding=10,
                    bgcolor="#ffffff",
                    border=ft.border.all(1, "#e6e9ed"),
                    border_radius=8,
                    content=ft.Column([
                        ft.Row([
                            ft.Text(user.get("userName", "Unassigned"), size=12, weight=ft.FontWeight.BOLD),
                            ft.Container(expand=True),
                            ft.Text(f"{share:.1f}% of entries", size=11, color=self.colors.text_secondary),
                        ]),
                        ft.ProgressBar(value=min(share / 100, 1), color="#2563eb", bgcolor="#dbeafe"),
                        ft.Text(
                            f"Entries: {user.get('entryCount', 0)} | Amount: {user.get('totalAmount', 0):,.2f} | "
                            f"Value share: {user.get('percentageOfValue', 0)}%",
                            size=11,
                            color=self.colors.text_secondary
                        ),
                    ], spacing=6)
                )
            )

        self.content_container.content = ft.Column([
            ft.Row([
                ft.Text(f"Year {data.get('year', 'N/A')}", size=12, color=self.colors.text_secondary),
                ft.Container(expand=True),
                ft.Text(f"Top user concentration: {data.get('topUserConcentrationRate', 0)}%", size=12, color="#dc2626"),
            ]),
            ft.Column(rows, spacing=8, scroll=ft.ScrollMode.AUTO),
        ], spacing=10, expand=True)
        self.page.update()

    def set_filters(self, reference_id=None, audit_universe_id=None):
        self.reference_id = reference_id
        self.audit_universe_id = audit_universe_id
        self.load_data()
