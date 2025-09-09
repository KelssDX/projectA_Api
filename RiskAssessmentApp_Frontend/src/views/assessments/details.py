import flet as ft
from flet import Icons
from src.models.user import User
from src.api.client import APIClient
import asyncio
from src.controllers.export_controller import ExportController
from datetime import datetime
from src.views.common.base_view import BaseView


class AssessmentDetailsView(BaseView):
    def __init__(self, page: ft.Page, user: User, assessment_id=None, on_back=None):
        self.page = page
        self.user = user
        self.assessment_id = assessment_id
        self.on_back = on_back
        self.api_client = APIClient()
        self.export_controller = ExportController()
        # Initialize BaseView header with actions
        actions = [
            ft.PopupMenuButton(
                items=[
                    ft.PopupMenuItem(text="Export to PDF", icon=Icons.PICTURE_AS_PDF, on_click=lambda e: self.export_assessment("pdf")),
                    ft.PopupMenuItem(text="Export to Excel", icon=Icons.TABLE_CHART, on_click=lambda e: self.export_assessment("excel")),
                    ft.PopupMenuItem(text="Edit Assessment", icon=Icons.EDIT, on_click=self.edit_assessment),
                    ft.PopupMenuItem(text="Delete Assessment", icon=Icons.DELETE, on_click=self.delete_assessment),
                ],
                tooltip="Actions",
                icon=Icons.MORE_VERT,
            )
        ]
        super().__init__(page, "Assessment Details", on_back=self.handle_back, actions=actions)

        # State
        self.assessment = None

        # Set up details view
        self.setup_view()

        # Load assessment data if ID is provided
        if assessment_id:
            self.page.run_task(self.load_assessment)

    def setup_view(self):
        # Body placeholder card (loading → details)
        self._body = ft.Container(expand=True, content=ft.Column([
            ft.Row([ft.ProgressRing(), ft.Text("Loading assessment details...")], spacing=10)
        ]))
        self.cards_column.controls.clear()
        self.add_card(self._body)

        # Assessment details sections

        # Basic information
        self.basic_info_section = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text(
                            "Basic Information",
                            size=20,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Divider(),
                        ft.Row(
                            [
                                ft.Column(
                                    [
                                        ft.Text("ID:", weight=ft.FontWeight.BOLD),
                                        ft.Text("Title:", weight=ft.FontWeight.BOLD),
                                        ft.Text("Department:", weight=ft.FontWeight.BOLD),
                                        ft.Text("Project:", weight=ft.FontWeight.BOLD),
                                    ],
                                    width=150,
                                ),
                                ft.Column(
                                    [
                                        ft.Text(""),  # ID
                                        ft.Text(""),  # Title
                                        ft.Text(""),  # Department
                                        ft.Text(""),  # Project
                                    ],
                                    expand=True,
                                ),
                                ft.Column(
                                    [
                                        ft.Text("Date:", weight=ft.FontWeight.BOLD),
                                        ft.Text("Auditor:", weight=ft.FontWeight.BOLD),
                                        ft.Text("Risk Level:", weight=ft.FontWeight.BOLD),
                                        ft.Text("Risk Score:", weight=ft.FontWeight.BOLD),
                                    ],
                                    width=150,
                                ),
                                ft.Column(
                                    [
                                        ft.Text(""),  # Date
                                        ft.Text(""),  # Auditor
                                        ft.Text(""),  # Risk Level
                                        ft.Text(""),  # Risk Score
                                    ],
                                    width=150,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                    ],
                    spacing=10,
                ),
                padding=20,
            ),
            elevation=2,
        )

        # Risk factors
        self.risk_factors_section = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text(
                            "Risk Factors",
                            size=20,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Divider(),
                        ft.DataTable(
                            columns=[
                                ft.DataColumn(ft.Text("Factor")),
                                ft.DataColumn(ft.Text("Value")),
                                ft.DataColumn(ft.Text("Description")),
                            ],
                            rows=[
                                # Will be populated from data
                            ],
                        ),
                    ],
                    spacing=10,
                ),
                padding=20,
            ),
            elevation=2,
        )

        # Assessment content
        self.content_section = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text(
                            "Assessment Details",
                            size=20,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Divider(),
                        ft.Text("Scope:", weight=ft.FontWeight.BOLD),
                        ft.Container(
                            content=ft.Text(""),  # Scope
                            bgcolor=ft.Colors.GREY_100,
                            border_radius=5,
                            padding=10,
                            width=800,
                        ),
                        ft.Text("Findings:", weight=ft.FontWeight.BOLD),
                        ft.Container(
                            content=ft.Text(""),  # Findings
                            bgcolor=ft.Colors.GREY_100,
                            border_radius=5,
                            padding=10,
                            width=800,
                        ),
                        ft.Text("Recommendations:", weight=ft.FontWeight.BOLD),
                        ft.Container(
                            content=ft.Text(""),  # Recommendations
                            bgcolor=ft.Colors.GREY_100,
                            border_radius=5,
                            padding=10,
                            width=800,
                        ),
                    ],
                    spacing=10,
                ),
                padding=20,
            ),
            elevation=2,
        )

        # Delete confirmation dialog
        self.delete_dialog = ft.AlertDialog(
            title=ft.Text("Confirm Deletion"),
            content=ft.Text("Are you sure you want to delete this assessment?"),
            actions=[
                ft.TextButton("Cancel", on_click=self.close_dialog),
                ft.TextButton("Delete", on_click=self.confirm_delete_assessment),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        # Export progress dialog
        self.export_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Exporting Assessment"),
            content=ft.Column(
                [
                    ft.ProgressRing(),
                    ft.Text("Please wait while the export is being prepared..."),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )

        # Main layout with loading indicator
        self.loading_indicator = ft.ProgressRing()

        self.content = ft.Column(
            [
                self.header,
                ft.Container(
                    content=ft.Column(
                        [
                            self.loading_indicator,
                            ft.Text("Loading assessment details...", size=16),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    alignment=ft.alignment.center,
                    expand=True,
                ),
            ],
            spacing=10,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

    # Theming hook
    def apply_theme(self, colors):
        # Rebuild to rebind token-based colors, then normalize the tree
        try:
            self.setup_view()
            from src.utils.theme import apply_theme_to_control
            apply_theme_to_control(self, colors)
        except Exception:
            pass

    async def load_assessment(self):
        """Load assessment details from API"""
        try:
            # Show loading indicator
            self.content.controls[1].visible = True
            self.update()

            # Pull assessments list from API and locate this assessment
            from src.api.auditing_client import AuditingAPIClient
            client = AuditingAPIClient()
            data = await client.get_assessments()
            found = None
            # normalize id (can be like A-001)
            for a in (data or []):
                aid = a.get("id")
                if aid == self.assessment_id or (isinstance(self.assessment_id, str) and self.assessment_id.startswith("A-") and isinstance(aid, int) and f"A-{aid:03d}" == self.assessment_id):
                    found = a
                    break
            if not found:
                raise Exception("Assessment not found")

            # Map data to internal structure used by this view
            self.assessment = {
                "id": f"A-{found.get('id'):03d}" if isinstance(found.get('id'), int) else found.get('id'),
                "title": found.get("title"),
                "department": found.get("department"),
                "department_id": found.get("department_id"),
                "project": found.get("project"),
                "project_id": found.get("project_id"),
                "risk_level": found.get("risk_level"),
                "risk_score": found.get("risk_score"),
                "date": found.get("assessment_date") or found.get("created_at"),
                "auditor": found.get("auditor"),
                "auditor_id": found.get("auditor_id"),
                "scope": found.get("scope"),
                "findings": found.get("findings"),
                "recommendations": found.get("recommendations"),
                "risk_factors": found.get("risk_factors") or []
            }

            # Update the UI with assessment details
            self.update_assessment_details()

        except Exception as e:
            # Show error message
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Error loading assessment: {str(e)}"),
                bgcolor=ft.Colors.RED_400
            )
            self.page.snack_bar.open = True
            self.page.update()

    def update_assessment_details(self):
        """Update the UI with loaded assessment details"""
        if not self.assessment:
            return

        # Update header subtitle
        self.header.content.controls[
            1].value = f"Viewing assessment {self.assessment['id']} - {self.assessment['title']}"

        # Basic information section
        basic_info = self.basic_info_section.content.content.controls[2]

        # Left column values
        basic_info.controls[1].controls[0].value = self.assessment["id"]
        basic_info.controls[1].controls[1].value = self.assessment["title"]
        basic_info.controls[1].controls[2].value = self.assessment["department"]
        basic_info.controls[1].controls[3].value = self.assessment["project"]

        # Right column values
        basic_info.controls[3].controls[0].value = self.assessment["date"]
        basic_info.controls[3].controls[1].value = self.assessment["auditor"]

        # Set risk level with color
        risk_level_text = ft.Text(
            self.assessment["risk_level"],
            color=self.get_risk_level_color(self.assessment["risk_level"]),
            weight=ft.FontWeight.BOLD,
        )
        basic_info.controls[3].controls[2] = risk_level_text

        basic_info.controls[3].controls[3].value = str(self.assessment["risk_score"])

        # Risk factors table
        factors_table = self.risk_factors_section.content.content.controls[2]
        factors_table.rows = []

        for factor in self.assessment["risk_factors"]:
            factors_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(factor["name"])),
                        ft.DataCell(
                            ft.Container(
                                content=ft.Text(
                                    str(factor["value"]),
                                    color=ft.Colors.WHITE,
                                    text_align=ft.TextAlign.CENTER,
                                ),
                                bgcolor=self.get_factor_value_color(factor["value"]),
                                border_radius=5,
                                padding=5,
                                width=40,
                                alignment=ft.alignment.center,
                            )
                        ),
                        ft.DataCell(ft.Text(factor.get("description", ""))),
                    ]
                )
            )

        # Assessment content section
        content_section = self.content_section.content.content

        # Scope
        content_section.controls[3].content.value = self.assessment.get("scope", "No scope specified")

        # Findings
        content_section.controls[5].content.value = self.assessment.get("findings", "No findings specified")

        # Recommendations
        content_section.controls[7].content.value = self.assessment.get("recommendations",
                                                                        "No recommendations specified")

        # Replace loading indicator with actual content inside body placeholder
        self._body.content = ft.Column(
            [
                self.basic_info_section,
                ft.Container(height=20),
                self.risk_factors_section,
                ft.Container(height=20),
                self.content_section,
            ],
            spacing=10,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

        self.update()

    def get_risk_level_color(self, risk_level):
        """Get color for risk level"""
        if risk_level == "High":
            return ft.Colors.RED
        elif risk_level == "Medium":
            return ft.Colors.AMBER
        elif risk_level == "Low":
            return ft.Colors.GREEN
        else:
            return ft.Colors.BLACK

    def get_factor_value_color(self, value):
        """Get color for risk factor value"""
        if value >= 4:
            return ft.Colors.RED
        elif value >= 3:
            return ft.Colors.AMBER
        else:
            return ft.Colors.GREEN

    def handle_back(self, e):
        """Handle back button click"""
        if self.on_back:
            self.on_back()

    def edit_assessment(self, e):
        """Navigate to edit assessment form"""
        # In a real app, this would navigate to the assessment form with this assessment loaded
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(f"Editing assessment {self.assessment_id} is not implemented in this demo"),
            bgcolor=ft.Colors.BLUE_400
        )
        self.page.snack_bar.open = True
        self.page.update()

    def delete_assessment(self, e):
        """Show confirmation dialog for assessment deletion"""
        if not self.assessment:
            return

        # Update confirmation message
        self.delete_dialog.content.value = f"Are you sure you want to delete assessment '{self.assessment['id']} - {self.assessment['title']}'?"

        # Show dialog
        self.page.dialog = self.delete_dialog
        self.delete_dialog.open = True
        self.page.update()

    def close_dialog(self, e):
        """Close the current dialog"""
        self.page.dialog.open = False
        self.page.update()

    async def confirm_delete_assessment(self, e):
        """Handle confirmed assessment deletion"""
        if not self.assessment:
            return

        # Close dialog
        self.close_dialog(None)

        # Show loading indicator
        loading_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Deleting Assessment"),
            content=ft.Column(
                [
                    ft.ProgressRing(),
                    ft.Text("Please wait..."),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )

        self.page.dialog = loading_dialog
        loading_dialog.open = True
        self.page.update()

        # Simulate API call to delete assessment
        await asyncio.sleep(1)

        # Close loading dialog
        loading_dialog.open = False
        self.page.update()

        # Show success message
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text("Assessment deleted successfully"),
            bgcolor=ft.Colors.GREEN_400
        )
        self.page.snack_bar.open = True
        self.page.update()

        # Navigate back to list
        if self.on_back:
            self.on_back()

    async def export_assessment(self, format_type):
        """Export assessment in specified format (real file output)"""
        if not self.assessment:
            return

        # Show export dialog
        self.page.dialog = self.export_dialog
        self.export_dialog.open = True
        self.page.update()

        try:
            from src.utils.excel_exporter import ExcelExporter
            from src.utils.pdf_generator import PDFGenerator
            # Build a minimal Assessment-like object for exporters
            class _A:
                pass
            a = _A()
            a.id = self.assessment.get("id")
            a.title = self.assessment.get("title")
            a.department = self.assessment.get("department")
            a.project = self.assessment.get("project")
            a.assessment_date = self.assessment.get("date")
            a.auditor = self.assessment.get("auditor")
            a.risk_level = self.assessment.get("risk_level")
            a.risk_score = self.assessment.get("risk_score")
            a.scope = self.assessment.get("scope")
            a.findings = self.assessment.get("findings")
            a.recommendations = self.assessment.get("recommendations")
            a.risk_factors = self.assessment.get("risk_factors") or []

            if format_type.lower() == "pdf":
                generator = PDFGenerator()
                filename = generator.generate_assessment_report(a)
            else:
                exporter = ExcelExporter()
                filename = exporter.export_assessments([a])
        except Exception as ex:
            self.export_dialog.open = False
            self.page.update()
            self.page.snack_bar = ft.SnackBar(content=ft.Text(f"Export failed: {ex}"), bgcolor=ft.Colors.RED_400)
            self.page.snack_bar.open = True
            self.page.update()
            return

        # Close export dialog
        self.export_dialog.open = False
        self.page.update()

        # Show success dialog with path
        success_dialog = ft.AlertDialog(
            title=ft.Text("Export Successful"),
            content=ft.Column(
                [
                    ft.Text("Assessment has been exported to:"),
                    ft.Text(filename, weight=ft.FontWeight.BOLD),
                ],
                spacing=10,
            ),
            actions=[
                ft.TextButton("OK", on_click=self.close_dialog),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.page.dialog = success_dialog
        success_dialog.open = True
        self.page.update()
