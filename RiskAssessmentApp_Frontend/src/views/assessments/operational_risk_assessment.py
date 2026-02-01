import flet as ft
from src.api.auditing_client import AuditingAPIClient
from src.utils.theme import get_theme_colors, create_modern_button


class OperationalRiskComponent(ft.Column):
    def __init__(self, page, current_user, reference_id=None):
        super().__init__(expand=True, scroll=ft.ScrollMode.ADAPTIVE)
        self.page = page
        self.current_user = current_user
        self.client = AuditingAPIClient()
        self.reference_id = reference_id
        self.assessments = []
        self.data = []

        self._build_ui()
        self.load_data()

    def _build_ui(self):
        colors = get_theme_colors(self.page.theme_mode)

        self.assessment_selector = ft.Dropdown(
            label="Assessment Context",
            hint_text="Select Assessment...",
            options=[],
            text_size=12,
            width=260,
            bgcolor=ft.Colors.SURFACE,
            border_color=colors.primary,
            on_change=self._on_context_change
        )

        self.refresh_button = ft.IconButton(
            icon=ft.Icons.REFRESH,
            icon_size=18,
            tooltip="Reload Operational Risks",
            on_click=lambda _: self.load_data()
        )

        # Header with add button
        header = ft.Row([
            ft.Text("Operational Risk Incidents", size=20, weight="bold", color=colors.text_primary),
            ft.Container(expand=True),
            create_modern_button(colors, "Add New Loss Event", icon=ft.Icons.ADD, style="primary", width=200, on_click=self._show_add_dialog),
        ])

        # Filters row
        filters = ft.Row([
            self.assessment_selector,
            self.refresh_button
        ], spacing=8)

        # Table container (styled like standard assessments)
        self.table_container = ft.Container(
            expand=True,
            width=None,
            content=None
        )

        self.controls = [
            ft.Container(height=10),
            header,
            ft.Container(height=8),
            filters,
            ft.Container(height=10),
            self.table_container
        ]

    def load_data(self):
        if self.page:
            self.page.run_task(self._fetch_data)

    async def _fetch_data(self):
        try:
            if not self.assessments:
                self.assessments = await self.client.get_assessments() or []
                self._populate_assessment_selector()

            # Default to selected reference if none provided
            if self.reference_id is None and self.assessment_selector.options:
                # Pick first assessment in list
                first = self.assessment_selector.options[0]
                try:
                    self.reference_id = int(first.key)
                    self.assessment_selector.value = first.key
                except Exception:
                    pass

            if self.reference_id is None:
                self.data = []
                self._render_table()
                return

            self.data = await self.client.get_operational_risks(self.reference_id)
            self._render_table()
        except Exception as e:
            print(f"Error loading Op Risk: {e}")
            self.data = []
            self._render_table(error=str(e))

    def _populate_assessment_selector(self):
        self.assessment_selector.options.clear()
        for a in self.assessments:
            ref_id = a.get("reference_id") or a.get("id")
            if ref_id is None:
                continue
            title = a.get("title") or f"Assessment Ref #{ref_id}"
            self.assessment_selector.options.append(
                ft.dropdown.Option(key=str(ref_id), text=title)
            )

    def _render_table(self, error=None):
        colors = get_theme_colors(self.page.theme_mode)

        # Header row similar to standard assessments
        header = ft.Container(
            height=44,
            bgcolor=colors.surface,
            border=ft.border.only(bottom=ft.BorderSide(1, colors.border)),
            padding=ft.padding.only(left=24, right=24),
            content=ft.Row([
                ft.Container(expand=1.5, content=ft.Text("Main Process", weight=ft.FontWeight.BOLD, color=colors.text_secondary)),
                ft.Container(expand=1.2, content=ft.Text("Sub Process", weight=ft.FontWeight.BOLD, color=colors.text_secondary)),
                ft.Container(expand=1.2, content=ft.Text("Source", weight=ft.FontWeight.BOLD, color=colors.text_secondary)),
                ft.Container(expand=1, content=ft.Text("Frequency", weight=ft.FontWeight.BOLD, color=colors.text_secondary)),
                ft.Container(expand=0.8, content=ft.Text("Count", weight=ft.FontWeight.BOLD, color=colors.text_secondary, text_align=ft.TextAlign.RIGHT)),
                ft.Container(expand=0.8, content=ft.Text("Prob %", weight=ft.FontWeight.BOLD, color=colors.text_secondary, text_align=ft.TextAlign.RIGHT)),
                ft.Container(expand=1, content=ft.Text("Loss Amount", weight=ft.FontWeight.BOLD, color=colors.text_secondary, text_align=ft.TextAlign.RIGHT)),
                ft.Container(expand=1, content=ft.Text("VaR (Op)", weight=ft.FontWeight.BOLD, color=colors.text_secondary, text_align=ft.TextAlign.RIGHT)),
                ft.Container(expand=1, content=ft.Text("Cum. VaR", weight=ft.FontWeight.BOLD, color=colors.text_secondary, text_align=ft.TextAlign.RIGHT)),
                ft.Container(expand=1, content=ft.Text("Actions", weight=ft.FontWeight.BOLD, color=colors.text_secondary, text_align=ft.TextAlign.CENTER)),
            ], expand=True)
        )

        rows_column = ft.Column(spacing=0)

        if error:
            rows_column.controls.append(
                ft.Container(
                    height=100,
                    alignment=ft.alignment.center,
                    content=ft.Text(f"Error loading operational risks: {error}", color=ft.Colors.RED)
                )
            )
        elif not self.data:
            rows_column.controls.append(
                ft.Container(
                    height=100,
                    alignment=ft.alignment.center,
                    content=ft.Text("No operational risk records found for this assessment", color=colors.text_secondary)
                )
            )
        else:
            for item in self.data:
                rows_column.controls.append(self._create_row(item, colors))

        table = ft.Column([header, rows_column], spacing=0, expand=True, scroll=ft.ScrollMode.AUTO)

        self.table_container.content = ft.Container(
            content=table,
            expand=True,
            width=None,
            bgcolor=colors.surface,
            border_radius=12,
            border=ft.border.all(1, colors.border)
        )

        self.update()

    def _create_row(self, item, colors):
        def safe_num(val, fmt="{:,.2f}"):
            try:
                return fmt.format(float(val))
            except Exception:
                return fmt.format(0)

        return ft.Container(
            height=60,
            bgcolor=colors.surface,
            border=ft.border.only(bottom=ft.BorderSide(1, colors.border)),
            padding=ft.padding.only(left=24, right=24),
            content=ft.Row([
                ft.Container(expand=1.5, content=ft.Text(item.get("mainProcess", ""), color=colors.text_primary, overflow=ft.TextOverflow.ELLIPSIS)),
                ft.Container(expand=1.2, content=ft.Text(item.get("subProcess", ""), color=colors.text_primary, overflow=ft.TextOverflow.ELLIPSIS)),
                ft.Container(expand=1.2, content=ft.Text(item.get("source", ""), color=colors.text_primary, overflow=ft.TextOverflow.ELLIPSIS)),
                ft.Container(expand=1, content=ft.Text(item.get("lossFrequency", ""), color=colors.text_primary)),
                ft.Container(expand=0.8, content=ft.Text(str(item.get("lossEventCount", 0)), color=colors.text_primary, text_align=ft.TextAlign.RIGHT)),
                ft.Container(expand=0.8, content=ft.Text(f"{float(item.get('probability', 0)) * 100:.2f}%", color=colors.text_primary, text_align=ft.TextAlign.RIGHT)),
                ft.Container(expand=1, content=ft.Text(safe_num(item.get("lossAmount", 0)), color=colors.text_primary, text_align=ft.TextAlign.RIGHT)),
                ft.Container(expand=1, content=ft.Text(safe_num(item.get("vaR", 0)), color=colors.text_primary, text_align=ft.TextAlign.RIGHT)),
                ft.Container(expand=1, content=ft.Text(safe_num(item.get("cumulativeVaR", 0)), color=ft.Colors.RED, text_align=ft.TextAlign.RIGHT)),
                ft.Container(
                    expand=1,
                    content=ft.Row([
                        ft.ElevatedButton(text="View", on_click=lambda e, i=item: self._show_details(i)),
                        ft.Container(width=6),
                        ft.ElevatedButton(text="Edit", on_click=lambda e, i=item: self._show_edit_dialog(i)),
                        ft.Container(width=6),
                        ft.ElevatedButton(text="Delete", on_click=lambda e, i=item: self._show_delete_dialog(i)),
                    ], alignment=ft.MainAxisAlignment.CENTER)
                )
            ], expand=True)
        )

    def _on_context_change(self, e):
        try:
            if self.assessment_selector.value:
                self.reference_id = int(self.assessment_selector.value)
                self.load_data()
        except Exception:
            pass

    def _show_add_dialog(self, e):
        self._show_info_dialog("Create Operational Risk", "Create/edit endpoints are not implemented yet.")

    def _show_edit_dialog(self, item):
        self._show_info_dialog("Edit Operational Risk", "Edit endpoints are not implemented yet.")

    def _show_delete_dialog(self, item):
        self._show_info_dialog("Delete Operational Risk", "Delete endpoints are not implemented yet.")

    def _show_details(self, item):
        details = ft.Column([
            ft.Text(f"Main Process: {item.get('mainProcess', '')}"),
            ft.Text(f"Sub Process: {item.get('subProcess', '')}"),
            ft.Text(f"Source: {item.get('source', '')}"),
            ft.Text(f"Frequency: {item.get('lossFrequency', '')}"),
            ft.Text(f"Loss Event Count: {item.get('lossEventCount', 0)}"),
            ft.Text(f"Probability: {item.get('probability', 0)}"),
            ft.Text(f"Loss Amount: {item.get('lossAmount', 0)}"),
            ft.Text(f"VaR: {item.get('vaR', 0)}"),
            ft.Text(f"Cumulative VaR: {item.get('cumulativeVaR', 0)}"),
        ], spacing=6)
        dialog = ft.AlertDialog(
            title=ft.Text("Operational Risk Details"),
            content=details,
            actions=[ft.TextButton("Close", on_click=lambda e: self.page.close(dialog) if hasattr(self.page, "close") else self._close_dialog(dialog))]
        )
        if hasattr(self.page, "open"):
            self.page.open(dialog)
        else:
            self.page.dialog = dialog
            dialog.open = True
            self.page.update()

    def _show_info_dialog(self, title, message):
        dialog = ft.AlertDialog(
            title=ft.Text(title),
            content=ft.Text(message),
            actions=[ft.TextButton("OK", on_click=lambda e: self.page.close(dialog) if hasattr(self.page, "close") else self._close_dialog(dialog))]
        )
        if hasattr(self.page, "open"):
            self.page.open(dialog)
        else:
            self.page.dialog = dialog
            dialog.open = True
            self.page.update()

    def _close_dialog(self, dialog):
        dialog.open = False
        self.page.update()
