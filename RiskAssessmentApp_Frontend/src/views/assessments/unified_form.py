import flet as ft
from flet import Icons
import asyncio
from datetime import datetime
from src.controllers.assessment_controller import AssessmentController
from src.api.auditing_client import AuditingAPIClient
from src.utils.theme import (
    get_theme_colors,
    apply_theme_to_control,
    create_modern_card,
    create_modern_button,
)


class UnifiedAssessmentForm(ft.Container):
    def __init__(self, page, user, mode="create", reference_id=None, assessment=None, on_save=None, on_cancel=None):
        super().__init__()
        self.page = page
        self.user = user
        self.mode = mode  # "create" | "edit" | "view"
        self.reference_id = reference_id
        self.assessment = assessment or {}
        self.on_save_callback = on_save
        self.on_cancel_callback = on_cancel
        self.expand = True

        # Controllers
        self.assessment_controller = AssessmentController()
        self.api_client = AuditingAPIClient()

        # State
        self.items = []  # child assessments (risks)

        # Main fields
        self.title_tf = ft.TextField(label="Assessment Name", hint_text="e.g., 2025 Q3 – Operations Risk Review", expand=True, border=ft.InputBorder.OUTLINE)
        self.category_dd = ft.Dropdown(label="Category", options=[
            ft.dropdown.Option("Operational"), ft.dropdown.Option("Market"), ft.dropdown.Option("Credit"),
            ft.dropdown.Option("Compliance"), ft.dropdown.Option("IT & Security"), ft.dropdown.Option("Other")
        ], width=260)
        self.process_tf = ft.TextField(label="Process / Area", hint_text="e.g., Billing, Customer Onboarding", width=260, border=ft.InputBorder.OUTLINE)
        self.assessor_tf = ft.TextField(label="Assessor", hint_text="Your name", width=260, border=ft.InputBorder.OUTLINE)
        self.date_tf = ft.TextField(label="Assessment Date", hint_text="YYYY-MM-DD", width=180, border=ft.InputBorder.OUTLINE)
        self.status_dd = ft.Dropdown(label="Status", options=[
            ft.dropdown.Option("Draft"), ft.dropdown.Option("In Review"), ft.dropdown.Option("Approved"), ft.dropdown.Option("Archived")
        ], width=180)
        self.overview_ta = ft.TextField(label="Overview / Scope", hint_text="Briefly describe scope, boundaries and objectives", multiline=True, min_lines=3, max_lines=5, expand=True, border=ft.InputBorder.OUTLINE)
        self.comments_ta = ft.TextField(label="General Comments / Notes", multiline=True, min_lines=3, max_lines=6, expand=True, border=ft.InputBorder.OUTLINE)

        # Table container
        self.table_body = ft.Column(spacing=0)

        # Build UI
        self._build_ui()
        # Initialize data
        self._init_data()
        # Load lookups
        try:
            if hasattr(self.page, "run_task"):
                self.page.run_task(self._load_lookups)
            else:
                asyncio.create_task(self._load_lookups())
        except Exception:
            pass

    def _build_ui(self):
        colors = get_theme_colors(self.page.theme_mode if hasattr(self.page, "theme_mode") else ft.ThemeMode.LIGHT)

        header = ft.Container(
            padding=ft.padding.symmetric(horizontal=20, vertical=12),
            border=ft.border.only(bottom=ft.BorderSide(1, colors.border)),
            content=ft.Row([
                ft.Column([
                    ft.Text("Risk Assessment Form", size=18, weight=ft.FontWeight.BOLD),
                    ft.Text("Use this form to create, edit, or view a risk assessment", size=12, color="#cbd5e1")
                ], spacing=4),
                ft.Container(expand=True),
                create_modern_button(colors, "← Back", on_click=self._handle_back, style="secondary", width=90),
                ft.Dropdown(value=self.mode, options=[
                    ft.dropdown.Option("create"), ft.dropdown.Option("edit"), ft.dropdown.Option("view")
                ], on_change=self._on_mode_change, width=120),
                ft.Container(content=create_modern_button(colors, "Save", icon=Icons.SAVE, on_click=self._handle_save, style="primary", width=100), ref=lambda c: setattr(self, "save_btn_header", c))
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        )

        # Main meta grid
        meta_grid = ft.Column([
            ft.Row([self.title_tf, self.category_dd, self.process_tf], spacing=12),
            ft.Row([self.assessor_tf, self.date_tf, self.status_dd], spacing=12),
            self.overview_ta
        ], spacing=12)
        meta_card = create_modern_card(colors, meta_grid)

        # Assessments table header
        self.actions_header_cell = ft.Container(width=120, content=ft.Text("Actions", weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.RIGHT, no_wrap=True))
        table_header = ft.Container(
            padding=ft.padding.symmetric(horizontal=10, vertical=8),
            content=ft.Row([
                ft.Container(width=180, content=ft.Text("Risk Title", weight=ft.FontWeight.BOLD, no_wrap=True)),
                ft.Container(expand=True, content=ft.Text("Description", weight=ft.FontWeight.BOLD, no_wrap=True)),
                ft.Container(width=150, content=ft.Text("Likelihood (1–5)", weight=ft.FontWeight.BOLD, no_wrap=True)),
                ft.Container(width=120, content=ft.Text("Impact (1–5)", weight=ft.FontWeight.BOLD, no_wrap=True)),
                ft.Container(width=100, content=ft.Text("Inherent", weight=ft.FontWeight.BOLD, no_wrap=True)),
                ft.Container(width=160, content=ft.Text("Control(s)", weight=ft.FontWeight.BOLD, no_wrap=True)),
                ft.Container(width=160, content=ft.Text("Effectiveness (1–5)", weight=ft.FontWeight.BOLD, no_wrap=True)),
                ft.Container(width=90, content=ft.Text("Res L", weight=ft.FontWeight.BOLD, no_wrap=True)),
                ft.Container(width=90, content=ft.Text("Res I", weight=ft.FontWeight.BOLD, no_wrap=True)),
                ft.Container(width=100, content=ft.Text("Residual", weight=ft.FontWeight.BOLD, no_wrap=True)),
                ft.Container(width=140, content=ft.Text("Owner", weight=ft.FontWeight.BOLD, no_wrap=True)),
                ft.Container(width=120, content=ft.Text("Due", weight=ft.FontWeight.BOLD, no_wrap=True)),
                self.actions_header_cell
            ], spacing=8)
        )

        # Panel header with title and Add button
        self.add_btn = ft.Container(
            content=create_modern_button(colors, "+ Add", icon=Icons.ADD, on_click=lambda e: self._open_item_modal(), style="secondary", width=110)
        )
        panel_header = ft.Row([
            ft.Text("Assessments", size=16, weight=ft.FontWeight.BOLD),
            ft.Container(expand=True),
            ft.Text("Add multiple risks under the main assessment", color="#94a3b8", size=12),
            self.add_btn
        ])

        # One panel: header + table
        table_content = ft.Column([panel_header, table_header, self.table_body], spacing=10)
        table_wrap = create_modern_card(colors, table_content)

        footer = ft.Row([
            ft.Container(content=create_modern_button(colors, "Clear", on_click=self._clear_all, style="secondary", width=100), ref=lambda c: setattr(self, "clear_btn", c)),
            ft.Container(expand=True),
            ft.Container(content=create_modern_button(colors, "Save", icon=Icons.SAVE, on_click=self._handle_save, style="primary", width=120), ref=lambda c: setattr(self, "save_btn_footer", c)),
        ], alignment=ft.MainAxisAlignment.END)

        self.content = ft.Column([
            header,
            ft.Container(padding=20, content=meta_card),
            ft.Container(padding=20, content=table_wrap),
            ft.Container(padding=20, content=create_modern_card(colors, self.comments_ta)),
            ft.Container(padding=ft.padding.symmetric(horizontal=20, vertical=12), content=footer)
        ], expand=True, scroll=ft.ScrollMode.AUTO)

        # Prepare modal for add/edit item
        self._build_item_modal()

        # Immediate theme normalization to match dashboard
        try:
            self.bgcolor = colors.bg
            apply_theme_to_control(self, colors)
        except Exception:
            pass

    def _on_mode_change(self, e):
        self.mode = e.control.value
        self._apply_mode_disabled()

    def _apply_mode_disabled(self):
        disabled = self.mode == "view"
        for ctrl in [self.title_tf, self.category_dd, self.process_tf, self.assessor_tf, self.date_tf, self.status_dd, self.overview_ta, self.comments_ta]:
            ctrl.read_only = disabled if isinstance(ctrl, ft.TextField) else False
            if isinstance(ctrl, ft.Dropdown):
                ctrl.disabled = disabled
        # Item table rows
        for r in self.table_body.controls:
            # Last column is actions container
            if isinstance(r, ft.Container) and isinstance(r.content, ft.Row):
                actions = r.content.controls[-1]
                if isinstance(actions, ft.Container) and isinstance(actions.content, ft.Row):
                    actions.visible = not disabled
        # Save buttons
        if hasattr(self, "save_btn_header") and self.save_btn_header:
            self.save_btn_header.visible = not disabled
        if hasattr(self, "save_btn_footer") and self.save_btn_footer:
            self.save_btn_footer.visible = not disabled
        if hasattr(self, "clear_btn") and self.clear_btn:
            self.clear_btn.visible = not disabled
        if hasattr(self, "add_btn") and self.add_btn:
            self.add_btn.visible = not disabled
        if hasattr(self, "actions_header_cell") and self.actions_header_cell:
            self.actions_header_cell.visible = not disabled
        if hasattr(self, 'page') and self.page:
            self.page.update()

    def _init_data(self):
        # Populate from existing assessment if provided
        try:
            src = self.assessment
            # Support Assessment model and dict
            if hasattr(src, "title") or isinstance(src, dict):
                getv = (lambda k: getattr(src, k, None)) if not isinstance(src, dict) else (lambda k: src.get(k))
                self.title_tf.value = (getv("title") or "")
                self.assessor_tf.value = (getv("auditor") or "")
                dt = (getv("assessment_date") or getv("date"))
                if isinstance(dt, str):
                    self.date_tf.value = dt.split("T")[0]
                elif hasattr(dt, "strftime"):
                    self.date_tf.value = dt.strftime("%Y-%m-%d")
                self.status_dd.value = getv("risk_level") or self.status_dd.value
                self.overview_ta.value = (getv("scope") or "")
                # Map simple comments from recommendations/findings if present
                self.comments_ta.value = (getv("recommendations") or getv("findings") or "")

                risks = []
                # Prefer rich items if available
                if isinstance(src, dict):
                    risks = src.get("risk_items") or []
                # Fallback: convert risk_factors -> rows
                rf = getv("risk_factors") or []
                if not risks and isinstance(rf, list):
                    for f in rf:
                        if isinstance(f, dict):
                            val = f.get("value")
                            risks.append({
                                "title": f.get("name"),
                                "desc": f.get("description") or "",
                                "likelihood": val if isinstance(val, (int, float)) else 3,
                                "impact": val if isinstance(val, (int, float)) else 3,
                                "controls": "",
                                "effectiveness": 3,
                                "resL": 2,
                                "resI": 2,
                                "owner": getv("auditor") or "",
                                "due": "",
                                "notes": ""
                            })
                self.items = risks
        except Exception:
            pass
        # Render
        self._render_items()
        self._apply_mode_disabled()

    async def _load_lookups(self):
        try:
            cats = await self.assessment_controller.get_risk_categories()
            evid = await self.assessment_controller.get_evidence()
            freqs = await self.assessment_controller.get_data_frequencies()

            def to_text_list(items, key_candidates=("name", "title", "value", "label", "description")):
                out = []
                if isinstance(items, list):
                    for it in items:
                        if isinstance(it, dict):
                            val = next((it.get(k) for k in key_candidates if it.get(k) is not None), None)
                            if val:
                                out.append(str(val))
                        else:
                            out.append(str(it))
                return out

            self._category_items_raw = cats or []
            self._evidence_items_raw = evid or []
            self._data_freq_items_raw = freqs or []

            categories = to_text_list(self._category_items_raw)
            # Populate category dropdowns
            self.category_dd.options = [ft.dropdown.Option(c) for c in categories]
            if not self.category_dd.value and categories:
                self.category_dd.value = categories[0]
            if hasattr(self, 'm_risk_category'):
                self.m_risk_category.options = [ft.dropdown.Option(c) for c in categories]
                if categories:
                    self.m_risk_category.value = categories[0]

            if hasattr(self, 'm_frequency'):
                freqs_text = to_text_list(self._data_freq_items_raw)
                self.m_frequency.options = [ft.dropdown.Option(f) for f in freqs_text]
            if hasattr(self, 'm_evidence'):
                evid_text = to_text_list(self._evidence_items_raw)
                self.m_evidence.options = [ft.dropdown.Option(e) for e in evid_text]

            if hasattr(self, 'page') and self.page:
                self.page.update()
        except Exception:
            pass

    def _render_items(self):
        self.table_body.controls.clear()
        colors = get_theme_colors(self.page.theme_mode if hasattr(self.page, "theme_mode") else ft.ThemeMode.LIGHT)
        for idx, it in enumerate(self.items):
            inherent = self._compute_inherent(it.get("likelihood"), it.get("impact"))
            residual = self._compute_inherent(it.get("resL"), it.get("resI"))
            row = ft.Container(
                padding=ft.padding.symmetric(horizontal=10, vertical=8),
                border=ft.border.only(bottom=ft.BorderSide(1, colors.border)),
                content=ft.Row([
                    ft.Container(width=180, content=ft.Text(it.get("title", ""))),
                    ft.Container(expand=True, content=ft.Text(it.get("desc", ""))),
                    ft.Container(width=120, content=ft.Text(str(it.get("likelihood", "")))),
                    ft.Container(width=120, content=ft.Text(str(it.get("impact", "")))),
                    ft.Container(width=90, content=ft.Container(content=ft.Text(str(inherent) if inherent else ""), bgcolor=colors.hover_bg, border_radius=12, padding=6, alignment=ft.alignment.center, border=ft.border.all(1, colors.border))),
                    ft.Container(width=160, content=ft.Text(it.get("controls", ""))),
                    ft.Container(width=120, content=ft.Text(str(it.get("effectiveness", "")))),
                    ft.Container(width=90, content=ft.Text(str(it.get("resL", "")))),
                    ft.Container(width=90, content=ft.Text(str(it.get("resI", "")))),
                    ft.Container(width=90, content=ft.Container(content=ft.Text(str(residual) if residual else ""), bgcolor=colors.hover_bg, border_radius=12, padding=6, alignment=ft.alignment.center, border=ft.border.all(1, colors.border))),
                    ft.Container(width=140, content=ft.Text(it.get("owner", ""))),
                    ft.Container(width=120, content=ft.Text(it.get("due", ""))),
                    ft.Container(width=120, content=ft.Row([
                        create_modern_button(colors, "Edit", icon=Icons.EDIT, on_click=lambda e, i=idx: self._open_item_modal(i), style="secondary", width=80),
                        create_modern_button(colors, "Delete", icon=Icons.DELETE, on_click=lambda e, i=idx: self._delete_item(i), style="danger", width=90)
                    ], alignment=ft.MainAxisAlignment.END))
                ], spacing=8)
            )
            self.table_body.controls.append(row)
        if hasattr(self, 'page') and self.page:
            self.page.update()

    # Theming hook to support dynamic theme changes
    def apply_theme(self, colors):
        try:
            self.bgcolor = colors.bg
            apply_theme_to_control(self, colors)
            if hasattr(self, 'page') and self.page:
                self.page.update()
        except Exception:
            pass

    def _compute_inherent(self, l, i):
        try:
            l = int(l or 0)
            i = int(i or 0)
            return l * i if l and i else ""
        except Exception:
            return ""

    def _build_item_modal(self):
        self.m_title = ft.TextField(label="Risk Title", expand=True, border=ft.InputBorder.OUTLINE)
        self.m_owner = ft.TextField(label="Owner", width=260, border=ft.InputBorder.OUTLINE)
        self.m_desc = ft.TextField(label="Description", multiline=True, min_lines=2, max_lines=4, expand=True, border=ft.InputBorder.OUTLINE)
        self.m_likelihood = ft.Dropdown(label="Likelihood (1–5)", width=200, options=[ft.dropdown.Option(str(i)) for i in range(1,6)])
        self.m_impact = ft.Dropdown(label="Impact (1–5)", width=200, options=[ft.dropdown.Option(str(i)) for i in range(1,6)])
        self.m_controls = ft.TextField(label="Controls", expand=True, border=ft.InputBorder.OUTLINE)
        self.m_effectiveness = ft.Dropdown(label="Control Effectiveness (1–5)", width=220, options=[ft.dropdown.Option(str(i)) for i in range(1,6)])
        self.m_resL = ft.Dropdown(label="Residual Likelihood (1–5)", width=220, options=[ft.dropdown.Option(str(i)) for i in range(1,6)])
        self.m_resI = ft.Dropdown(label="Residual Impact (1–5)", width=220, options=[ft.dropdown.Option(str(i)) for i in range(1,6)])
        self.m_due = ft.TextField(label="Due Date (YYYY-MM-DD)", width=220)
        self.m_notes = ft.TextField(label="Notes", expand=True, border=ft.InputBorder.OUTLINE)
        self.m_risk_category = ft.Dropdown(label="Risk Category", width=260, options=[])
        self.m_preventive = ft.Dropdown(label="Preventive", width=160, options=[ft.dropdown.Option("N/A"), ft.dropdown.Option("Yes"), ft.dropdown.Option("No")])
        self.m_responsive = ft.Dropdown(label="Responsive", width=160, options=[ft.dropdown.Option("N/A"), ft.dropdown.Option("Yes"), ft.dropdown.Option("No")])
        self.m_frequency = ft.Dropdown(label="Frequency", width=180, options=[])
        self.m_evidence = ft.Dropdown(label="Evidence", width=220, options=[])

        def close_modal(_):
            if self.page and self.page.dialog:
                self.page.dialog.open = False
                self.page.update()

        def save_item(_):
            if self.mode == "view":
                close_modal(None)
                return
            item = {
                "title": self.m_title.value.strip(),
                "owner": self.m_owner.value.strip(),
                "desc": self.m_desc.value.strip(),
                "likelihood": int(self.m_likelihood.value or 0),
                "impact": int(self.m_impact.value or 0),
                "controls": self.m_controls.value.strip(),
                "effectiveness": int(self.m_effectiveness.value or 0),
                "resL": int(self.m_resL.value or 0),
                "resI": int(self.m_resI.value or 0),
                "due": self.m_due.value.strip(),
                "notes": self.m_notes.value.strip(),
                "riskCategory": self.m_risk_category.value,
                "preventive": self.m_preventive.value,
                "responsive": self.m_responsive.value,
                "frequency": self.m_frequency.value,
                "evidence": self.m_evidence.value
            }
            idx = getattr(self, "_edit_index", None)
            if idx is None:
                self.items.append(item)
            else:
                self.items[idx] = item
            self._edit_index = None
            close_modal(None)
            self._render_items()

        self.item_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Assessment (Risk) – Details"),
            content=ft.Container(
                width=900,
                content=ft.Column([
                    ft.Row([self.m_title, self.m_owner], spacing=12),
                    self.m_desc,
                    ft.Row([self.m_likelihood, self.m_impact, self.m_controls, self.m_effectiveness], spacing=12),
                    ft.Row([self.m_risk_category, self.m_preventive, self.m_responsive, self.m_frequency], spacing=12),
                    ft.Row([self.m_evidence, self.m_resL, self.m_resI], spacing=12),
                    ft.Row([self.m_due, self.m_notes], spacing=12)
                ], spacing=12)
            ),
            actions=[
                ft.TextButton("Cancel", on_click=close_modal),
                ft.TextButton("Save Item", on_click=save_item)
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )

    def _open_item_modal(self, index=None):
        self._edit_index = index
        if index is not None and 0 <= index < len(self.items):
            it = self.items[index]
            self.m_title.value = it.get("title", "")
            self.m_owner.value = it.get("owner", "")
            self.m_desc.value = it.get("desc", "")
            self.m_likelihood.value = str(it.get("likelihood", ""))
            self.m_impact.value = str(it.get("impact", ""))
            self.m_controls.value = it.get("controls", "")
            self.m_effectiveness.value = str(it.get("effectiveness", ""))
            self.m_resL.value = str(it.get("resL", ""))
            self.m_resI.value = str(it.get("resI", ""))
            self.m_due.value = it.get("due", "")
            self.m_notes.value = it.get("notes", "")
        else:
            for tf in [self.m_title, self.m_owner, self.m_desc, self.m_likelihood, self.m_impact, self.m_controls, self.m_effectiveness, self.m_resL, self.m_resI, self.m_due, self.m_notes]:
                tf.value = ""
        self.page.dialog = self.item_dialog
        self.item_dialog.open = True
        self.page.update()

    def _delete_item(self, index):
        if self.mode == "view":
            return
        if 0 <= index < len(self.items):
            del self.items[index]
            self._render_items()

    def _clear_all(self, e):
        if self.mode == "view":
            return
        self.title_tf.value = ""
        self.category_dd.value = None
        self.process_tf.value = ""
        self.assessor_tf.value = ""
        self.date_tf.value = ""
        self.status_dd.value = None
        self.overview_ta.value = ""
        self.comments_ta.value = ""
        self.items = []
        if hasattr(self, 'page') and self.page:
            self.page.update()
        self._render_items()

    def _handle_back(self, e):
        if callable(self.on_cancel_callback):
            self.on_cancel_callback()

    def _handle_save(self, e):
        if self.mode == "view":
            # No-op in view mode
            return
        # Validate basic fields
        if not self.title_tf.value:
            self._show_error("Assessment Name is required")
            return
        # Build payload aligned with existing controller wrapper
        wrapper = {
            "Assessments": [
                {
                    "BusinessObjectives": it.get("desc"),
                    "MainProcess": self.process_tf.value,
                    "SubProcess": None,
                    "KeyRiskAndFactors": it.get("title"),
                    "MitigatingControls": it.get("controls"),
                    "Responsibility": it.get("owner"),
                    "Authoriser": None,
                    "AuditorsRecommendedActionPlan": it.get("notes"),
                    "ResponsiblePerson": it.get("owner"),
                    "AgreedDate": it.get("due") or None,
                    "RiskLikelihoodId": it.get("likelihood"),
                    "RiskImpactId": it.get("impact"),
                    "KeySecondaryId": None,
                    "RiskCategoryId": self.category_dd.value,
                    "DataFrequencyId": None,
                    "FrequencyId": None,
                    "EvidenceId": None,
                    "OutcomeLikelihoodId": None,
                    "ImpactId": it.get("impact")
                } for it in self.items
            ] or [
                {
                    "BusinessObjectives": self.overview_ta.value,
                    "MainProcess": self.process_tf.value,
                    "SubProcess": None,
                    "KeyRiskAndFactors": self.title_tf.value,
                    "MitigatingControls": None,
                    "Responsibility": self.assessor_tf.value or (self.user.get("username") if isinstance(self.user, dict) else None),
                    "Authoriser": None,
                    "AuditorsRecommendedActionPlan": None,
                    "ResponsiblePerson": None,
                    "AgreedDate": None,
                    "RiskLikelihoodId": None,
                    "RiskImpactId": None,
                    "KeySecondaryId": None,
                    "RiskCategoryId": self.category_dd.value,
                    "DataFrequencyId": None,
                    "FrequencyId": None,
                    "EvidenceId": None,
                    "OutcomeLikelihoodId": None,
                    "ImpactId": None
                }
            ],
            "Reference": {
                "Client": self.process_tf.value or "",
                "AssessmentStartDate": self.date_tf.value or None,
                "AssessmentEndDate": None,
                "Assessor": self.assessor_tf.value or (self.user.get("username") if isinstance(self.user, dict) else None),
                "ApprovedBy": None,
                "Title": self.title_tf.value,
                "Status": self.status_dd.value or "Draft",
                "Overview": self.overview_ta.value,
                "Comments": self.comments_ta.value
            }
        }

        asyncio.create_task(self._save_async(wrapper))

    async def _save_async(self, payload):
        try:
            self._show_loading("Saving assessment...")
            if self.mode == "edit" and self.reference_id:
                # For update, send simplified list payload
                result = await self.assessment_controller.update_risk_assessment(self.reference_id, payload.get("Assessments") or [])
            else:
                result = await self.assessment_controller.create_risk_assessment(payload)
            self._hide_loading()
            if result is None:
                self._show_error("Failed to save assessment")
                return
            if callable(self.on_save_callback):
                self.on_save_callback(result)
            else:
                self._show_success("Assessment saved")
        except Exception as ex:
            self._hide_loading()
            self._show_error(f"Error: {ex}")

    def _show_loading(self, message):
        self.page.dialog = ft.AlertDialog(modal=True, title=ft.Text("Processing"), content=ft.Column([
            ft.ProgressRing(), ft.Text(message)
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, height=100))
        self.page.dialog.open = True
        self.page.update()

    def _hide_loading(self):
        if self.page.dialog:
            self.page.dialog.open = False
            self.page.update()

    def _show_success(self, message):
        self.page.snack_bar = ft.SnackBar(content=ft.Text(message), bgcolor="#2ecc71")
        self.page.snack_bar.open = True
        self.page.update()

    def _show_error(self, message):
        self.page.snack_bar = ft.SnackBar(content=ft.Text(message), bgcolor="#e74c3c")
        self.page.snack_bar.open = True
        self.page.update()


