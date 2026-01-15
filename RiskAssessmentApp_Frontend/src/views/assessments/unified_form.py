import flet as ft
from flet import Icons
import asyncio
from datetime import datetime, date
from src.controllers.assessment_controller import AssessmentController
from src.api.auditing_client import AuditingAPIClient
from src.utils.theme import (
    get_theme_colors,
    apply_theme_to_control,
    create_modern_card,
    create_modern_button,
)
from src.utils.export_manager import ExportManager
from src.views.common.base_view import BaseView
import csv
import io


class UnifiedAssessmentForm(BaseView):
    """
    Dual-mode Risk Assessment Form:
    - Table View: Inline editing with sortable/filterable table
    - Card View: Master-detail layout with tabbed forms
    - User can toggle between views using icon button
    """

    def __init__(self, page, user, mode="create", reference_id=None, assessment=None, on_save=None, on_cancel=None):
        self.page = page
        self.user = user
        self.mode = mode
        self.reference_id = reference_id
        self.assessment = assessment or {}
        self.on_save_callback = on_save
        self.on_cancel_callback = on_cancel
        
        colors = get_theme_colors(self.page.theme_mode if hasattr(self.page, "theme_mode") else ft.ThemeMode.LIGHT)
        self._score_text_map = {
            "1": "1 - Very Low",
            "2": "2 - Low",
            "3": "3 - Medium",
            "4": "4 - High",
            "5": "5 - Very High",
        }

        self.date_picker = ft.DatePicker(on_change=self._on_header_date_pick)
        self.d_due_picker = ft.DatePicker(on_change=self._on_detail_due_pick)
        self.m_due_picker = ft.DatePicker(on_change=self._on_modal_due_pick)

        actions = [
            create_modern_button(colors, "Back", on_click=self._handle_back, style="secondary", width=90),
            create_modern_button(colors, "Save All", icon=Icons.SAVE, on_click=self._handle_save, style="primary", width=120),
        ]
        super().__init__(page, "Risk Assessment Form", actions=actions, colors=colors)

        # Controllers
        self.assessment_controller = AssessmentController()
        self.api_client = AuditingAPIClient()

        # State
        self.items = []
        self.selected_item_index = None
        self._auto_save_enabled = True
        self._view_mode = "table"  # "table" or "cards"

        self._category_items_raw = []
        self._evidence_items_raw = []
        self._data_freq_items_raw = []

        self._register_date_pickers()

        # Table state
        self.filter_tf: ft.TextField | None = None
        self.table: ft.DataTable | None = None
        self._sort_index: int = 0
        self._sort_asc: bool = True

        # Common header fields
        self.title_tf = ft.TextField(label="Assessment Name", hint_text="e.g., 2025 Q3 – Operations Risk Review", expand=True, border=ft.InputBorder.OUTLINE)
        self.category_dd = ft.Dropdown(label="Category", options=[
            ft.dropdown.Option("Operational"), ft.dropdown.Option("Market"), ft.dropdown.Option("Credit"),
            ft.dropdown.Option("Compliance"), ft.dropdown.Option("IT & Security"), ft.dropdown.Option("Other")
        ], width=200)
        self.process_tf = ft.TextField(label="Process / Area", hint_text="e.g., Billing", width=200, border=ft.InputBorder.OUTLINE)
        self.assessor_tf = ft.TextField(label="Assessor", hint_text="Your name", width=180, border=ft.InputBorder.OUTLINE)
        self.date_tf = ft.TextField(
            label="Date",
            hint_text="YYYY-MM-DD",
            width=160,
            border=ft.InputBorder.OUTLINE,
            read_only=True,
            suffix=ft.IconButton(icon=Icons.CALENDAR_MONTH, on_click=lambda e: self._open_date_picker(self.date_picker)),
        )
        self.status_dd = ft.Dropdown(label="Status", options=[
            ft.dropdown.Option("Draft"), ft.dropdown.Option("In Review"), ft.dropdown.Option("Approved"), ft.dropdown.Option("Archived")
        ], width=140)
        self.approved_by_tf = ft.TextField(
            label="Approved By", 
            value="Pending Approval",
            width=180, 
            read_only=True,
            border=ft.InputBorder.OUTLINE,
            text_style=ft.TextStyle(italic=True)
        )

        # Build UI
        self._build_ui()
        self._build_item_modal()
        self._init_data()
        
        if self.mode == "edit" and self.assessment:
            self._load_assessment_data()
            
        try:
            if self.page:
                self.page.run_task(self._load_lookups)
        except Exception:
            pass

    def _build_ui(self):
        colors = get_theme_colors(self.page.theme_mode if hasattr(self.page, "theme_mode") else ft.ThemeMode.LIGHT)

        # Header Section (same for both views)
        meta_section = ft.Container(
            content=ft.Column([
                ft.Row([self.title_tf], spacing=12),
                ft.Row([
                    self.category_dd, self.process_tf,
                    self.assessor_tf, self.date_tf, self.status_dd, self.approved_by_tf
                ], spacing=12),
            ], spacing=12),
            padding=16,
            bgcolor=colors.hover_bg,
            border_radius=8
        )

        # View toggle button
        self.view_toggle_btn = ft.IconButton(
            icon=Icons.VIEW_LIST,
            tooltip="Switch to Card View",
            on_click=self._toggle_view,
            icon_size=24
        )

        # Build both views
        self._build_table_view(colors)
        self._build_card_view(colors)

        # Container to hold the current view
        self.view_container = ft.Container(
            content=self.table_view,
            expand=True,
        )

        # Compose
        self.cards_column.controls.clear()
        
        # Mode selector
        header_controls = ft.Row([
            ft.Text("Mode:", size=12, color="#94a3b8"),
            ft.Dropdown(value=self.mode, options=[
                ft.dropdown.Option("create"), ft.dropdown.Option("edit"), ft.dropdown.Option("view")
            ], on_change=self._on_mode_change, width=140),
            ft.Container(expand=True),
            self.view_toggle_btn
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        
        self.add_card(header_controls)
        self.cards_column.controls.append(meta_section)
        self.cards_column.controls.append(self.view_container)

        try:
            self.bgcolor = colors.bg
            apply_theme_to_control(self, colors)
        except Exception:
            pass
        
        # Refresh lists after UI is built
        try:
            self._refresh_items_list()
            self._refresh_table_rows()
        except Exception as e:
            print(f"DEBUG: Error refreshing lists after UI build: {e}")

    def _toggle_view(self, e):
        """Toggle between table and card views"""
        if self._view_mode == "table":
            self._view_mode = "cards"
            self.view_container.content = self.card_view
            self.view_toggle_btn.icon = Icons.TABLE_CHART
            self.view_toggle_btn.tooltip = "Switch to Table View"
        else:
            self._view_mode = "table"
            self.view_container.content = self.table_view
            self.view_toggle_btn.icon = Icons.VIEW_LIST
            self.view_toggle_btn.tooltip = "Switch to Card View"
        
        if hasattr(self, 'page') and self.page:
            self.page.update()

    def _build_table_view(self, colors):
        """Build the table view with inline editing"""
        # Filter and controls
        self.filter_tf = ft.TextField(
            label="Filter risks...",
            hint_text="title, category, process, owner, evidence...",
            width=340,
            prefix_icon=Icons.SEARCH,
            on_change=lambda e: self._refresh_table_rows(),
        )

        self.export_btn = create_modern_button(colors, "Export", icon=Icons.DOWNLOAD, on_click=self._show_export_options, style="secondary", width=120)
        self.add_table_btn = create_modern_button(colors, "+ Add", icon=Icons.ADD, on_click=lambda e: self._add_new_risk(select_current=False), style="secondary", width=110)

        panel_header = ft.Row([
            ft.Text("Risk Items", size=16, weight=ft.FontWeight.BOLD),
            ft.Container(expand=True),
            self.filter_tf,
            self.export_btn,
            self.add_table_btn,
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        # Build DataTable
        self._build_table()

        # Scrollable container with BOTH horizontal and vertical scroll
        table_container = ft.Container(
            content=ft.Row(
                controls=[self.table],
                scroll=ft.ScrollMode.ALWAYS,  # Enable horizontal scroll
                spacing=0,
            ),
            bgcolor=colors.bg,
            border=ft.border.all(1, colors.border),
            border_radius=8,
            padding=0,
            expand=True,
        )

        self.table_view = ft.Column([
            panel_header,
            table_container
        ], spacing=16, expand=True)

    def _build_card_view(self, colors):
        """Build the master-detail card view"""
        # Left Panel - Risk Items List
        self.search_tf = ft.TextField(
            hint_text="Search risks...",
            prefix_icon=Icons.SEARCH,
            border=ft.InputBorder.OUTLINE,
            on_change=lambda e: self._filter_items(),
            dense=True
        )

        self.add_card_btn = ft.ElevatedButton(
            "Add Risk",
            icon=Icons.ADD,
            on_click=lambda e: self._add_new_risk(select_current=True),
            style=ft.ButtonStyle(bgcolor="#2196F3", color="white")
        )

        self.items_list = ft.Column(
            controls=[],
            spacing=8,
            scroll=ft.ScrollMode.AUTO,
            expand=True
        )

        left_panel = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("Risk Items", size=16, weight=ft.FontWeight.BOLD),
                    ft.Container(expand=True),
                    self.add_card_btn
                ]),
                self.search_tf,
                ft.Divider(height=1),
                self.items_list
            ], spacing=12),
            padding=12,
            width=350,
            bgcolor=colors.bg,
            border=ft.border.only(right=ft.BorderSide(1, colors.border))
        )

        # Right Panel - Detail Form
        self._build_detail_panel(colors)

        # Master-Detail Layout
        self.card_view = ft.Row([
            left_panel,
            ft.Container(
                content=self.detail_panel,
                expand=True,
                padding=12
            )
        ], spacing=0, height=500)

    def _build_detail_panel(self, colors):
        """Build the right panel detail form with tabs"""
        # Risk Details Tab
        self.d_title = ft.TextField(label="Risk Title", border=ft.InputBorder.OUTLINE, on_change=lambda e: self._on_detail_change(), expand=True)
        self.d_desc = ft.TextField(label="Description", multiline=True, min_lines=3, max_lines=5, border=ft.InputBorder.OUTLINE, on_change=lambda e: self._on_detail_change(), expand=True)
        self.d_category = ft.Dropdown(label="Risk Category", options=[], on_change=lambda e: self._on_detail_change())
        self.d_process = ft.TextField(label="Process", border=ft.InputBorder.OUTLINE, on_change=lambda e: self._on_detail_change())
        self.d_owner = ft.TextField(label="Owner", border=ft.InputBorder.OUTLINE, on_change=lambda e: self._on_detail_change())

        # Inherent Risk Section
        self.d_likelihood = ft.Dropdown(
            label="Likelihood",
            options=[ft.dropdown.Option(str(i), f"{i} - {['Very Low', 'Low', 'Medium', 'High', 'Very High'][i-1]}") for i in range(1, 6)],
            on_change=lambda e: self._on_detail_change()
        )
        self.d_impact = ft.Dropdown(
            label="Impact",
            options=[ft.dropdown.Option(str(i), f"{i} - {['Very Low', 'Low', 'Medium', 'High', 'Very High'][i-1]}") for i in range(1, 6)],
            on_change=lambda e: self._on_detail_change()
        )
        
        self.inherent_score_text = ft.Text("0", size=32, weight=ft.FontWeight.BOLD)
        self.inherent_label_text = ft.Text("N/A", size=14)
        
        self.d_inherent_score = ft.Container(
            content=ft.Column([
                ft.Text("Inherent Risk", size=12, color="#64748b"),
                self.inherent_score_text,
                self.inherent_label_text
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=16,
            border_radius=8,
            bgcolor=colors.hover_bg,
            alignment=ft.alignment.center
        )

        risk_details_tab = ft.Container(
            content=ft.Column([
                self.d_title,
                self.d_desc,
                ft.Row([self.d_category, self.d_process, self.d_owner], spacing=12),
                ft.Divider(),
                ft.Text("Inherent Risk Assessment", size=14, weight=ft.FontWeight.BOLD),
                ft.Row([
                    self.d_likelihood,
                    ft.Text("×", size=24),
                    self.d_impact,
                    ft.Text("=", size=24),
                    self.d_inherent_score
                ], alignment=ft.MainAxisAlignment.START, spacing=12)
            ], spacing=12),
            padding=10
        )

        # Controls Tab
        self.d_controls = ft.TextField(label="Mitigating Controls", multiline=True, min_lines=3, max_lines=5, border=ft.InputBorder.OUTLINE, on_change=lambda e: self._on_detail_change())
        self.d_effectiveness = ft.Dropdown(
            label="Control Effectiveness",
            options=[ft.dropdown.Option(str(i), f"{i} - {['Very Low', 'Low', 'Medium', 'High', 'Very High'][i-1]}") for i in range(1, 6)],
            on_change=lambda e: self._on_detail_change()
        )
        self.d_preventive = ft.Dropdown(label="Preventive", options=[ft.dropdown.Option("N/A"), ft.dropdown.Option("Yes"), ft.dropdown.Option("No")], on_change=lambda e: self._on_detail_change())
        self.d_responsive = ft.Dropdown(label="Responsive", options=[ft.dropdown.Option("N/A"), ft.dropdown.Option("Yes"), ft.dropdown.Option("No")], on_change=lambda e: self._on_detail_change())
        self.d_frequency = ft.Dropdown(label="Frequency", options=[], on_change=lambda e: self._on_detail_change())

        controls_tab = ft.Container(
            content=ft.Column([
                self.d_controls,
                ft.Row([self.d_effectiveness, self.d_preventive, self.d_responsive], spacing=12),
                self.d_frequency
            ], spacing=12),
            padding=10
        )

        # Residual Risk Tab
        self.d_resL = ft.Dropdown(
            label="Residual Likelihood",
            options=[ft.dropdown.Option(str(i), f"{i} - {['Very Low', 'Low', 'Medium', 'High', 'Very High'][i-1]}") for i in range(1, 6)],
            on_change=lambda e: self._on_detail_change()
        )
        self.d_resI = ft.Dropdown(
            label="Residual Impact",
            options=[ft.dropdown.Option(str(i), f"{i} - {['Very Low', 'Low', 'Medium', 'High', 'Very High'][i-1]}") for i in range(1, 6)],
            on_change=lambda e: self._on_detail_change()
        )
        
        self.residual_score_text = ft.Text("0", size=32, weight=ft.FontWeight.BOLD)
        self.residual_label_text = ft.Text("N/A", size=14)
        
        self.d_residual_score = ft.Container(
            content=ft.Column([
                ft.Text("Residual Risk", size=12, color="#64748b"),
                self.residual_score_text,
                self.residual_label_text
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=16,
            border_radius=8,
            bgcolor=colors.hover_bg,
            alignment=ft.alignment.center
        )
        
        self.d_evidence = ft.Dropdown(label="Evidence", options=[], on_change=lambda e: self._on_detail_change())
        self.d_responsible = ft.TextField(label="Responsible Person", border=ft.InputBorder.OUTLINE, on_change=lambda e: self._on_detail_change())
        self.d_due = ft.TextField(
            label="Due Date",
            hint_text="YYYY-MM-DD",
            border=ft.InputBorder.OUTLINE,
            read_only=True,
            suffix=ft.IconButton(icon=Icons.CALENDAR_MONTH, on_click=lambda e: self._open_date_picker(self.d_due_picker)),
        )
        self.d_notes = ft.TextField(label="Action Plan / Notes", multiline=True, min_lines=3, max_lines=5, border=ft.InputBorder.OUTLINE, on_change=lambda e: self._on_detail_change())

        residual_tab = ft.Container(
            content=ft.Column([
                ft.Text("Residual Risk Assessment", size=14, weight=ft.FontWeight.BOLD),
                ft.Row([
                    self.d_resL,
                    ft.Text("×", size=24),
                    self.d_resI,
                    ft.Text("=", size=24),
                    self.d_residual_score
                ], alignment=ft.MainAxisAlignment.START, spacing=12),
                ft.Divider(),
                ft.Row([self.d_evidence, self.d_responsible, self.d_due], spacing=12),
                self.d_notes
            ], spacing=12),
            padding=10
        )

        # Tabs
        self.detail_tabs = ft.Tabs(
            selected_index=0,
            tabs=[
                ft.Tab(text="Risk Details", icon=Icons.ASSESSMENT, content=risk_details_tab),
                ft.Tab(text="Controls", icon=Icons.SHIELD, content=controls_tab),
                ft.Tab(text="Outcome", icon=Icons.CHECK_CIRCLE, content=residual_tab),
            ]
        )

        # Empty state
        self.empty_state = ft.Container(
            content=ft.Column([
                ft.Icon(Icons.ASSESSMENT_OUTLINED, size=64, color="#94a3b8"),
                ft.Text("No Risk Selected", size=18, weight=ft.FontWeight.BOLD),
                ft.Text("Select a risk from the list or add a new one", color="#64748b")
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=12),
            expand=True,
            alignment=ft.alignment.center
        )

        # Action buttons
        self.delete_btn = ft.OutlinedButton("Delete Risk", icon=Icons.DELETE, on_click=lambda e: self._delete_selected_risk(), style=ft.ButtonStyle(color="#ef4444"))
        self.duplicate_btn = ft.OutlinedButton("Duplicate", icon=Icons.CONTENT_COPY, on_click=lambda e: self._duplicate_risk())
        self.save_risk_btn = ft.FilledButton("Save Risk", icon=Icons.SAVE, on_click=lambda e: self._handle_save_selected_risk())

        action_row = ft.Row([
            self.delete_btn,
            self.duplicate_btn,
            self.save_risk_btn,
            ft.Container(expand=True),
            ft.Text("Auto-save enabled", size=12, color="#64748b", italic=True)
        ], visible=False)
        self.detail_action_row = action_row

        self.detail_form_container = ft.Container(
            content=ft.Column([
                self.detail_tabs,
                ft.Divider(),
                action_row
            ], spacing=12),
            visible=False
        )

        self.detail_panel = ft.Container(
            content=ft.Column([
                self.empty_state,
                self.detail_form_container
            ]),
            expand=True
        )

    def _build_table(self):
        colors = get_theme_colors(self.page.theme_mode if hasattr(self.page, "theme_mode") else ft.ThemeMode.LIGHT)
        self.table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Title", size=11, weight=ft.FontWeight.BOLD), on_sort=lambda e: self._on_sort(0)),
                ft.DataColumn(ft.Text("Category", size=11, weight=ft.FontWeight.BOLD), on_sort=lambda e: self._on_sort(1)),
                ft.DataColumn(ft.Text("Process", size=11, weight=ft.FontWeight.BOLD), on_sort=lambda e: self._on_sort(2)),
                ft.DataColumn(ft.Text("L", size=11, weight=ft.FontWeight.BOLD), numeric=True, on_sort=lambda e: self._on_sort(3)),
                ft.DataColumn(ft.Text("I", size=11, weight=ft.FontWeight.BOLD), numeric=True, on_sort=lambda e: self._on_sort(4)),
                ft.DataColumn(ft.Text("Inherent", size=11, weight=ft.FontWeight.BOLD), numeric=True, on_sort=lambda e: self._on_sort(5)),
                ft.DataColumn(ft.Text("Res L", size=11, weight=ft.FontWeight.BOLD), numeric=True, on_sort=lambda e: self._on_sort(6)),
                ft.DataColumn(ft.Text("Res I", size=11, weight=ft.FontWeight.BOLD), numeric=True, on_sort=lambda e: self._on_sort(7)),
                ft.DataColumn(ft.Text("Res Score", size=11, weight=ft.FontWeight.BOLD), numeric=True, on_sort=lambda e: self._on_sort(8)),
                ft.DataColumn(ft.Text("Owner", size=11, weight=ft.FontWeight.BOLD), on_sort=lambda e: self._on_sort(9)),
                ft.DataColumn(ft.Text("Due", size=11, weight=ft.FontWeight.BOLD), on_sort=lambda e: self._on_sort(10)),
                ft.DataColumn(ft.Text("Evidence", size=11, weight=ft.FontWeight.BOLD), on_sort=lambda e: self._on_sort(11)),
                ft.DataColumn(ft.Text("Actions", size=11, weight=ft.FontWeight.BOLD)),
            ],
            rows=[],
            column_spacing=6,
            heading_row_color=colors.hover_bg,
            heading_row_height=38,
            data_row_min_height=40,
            data_row_max_height=60,
            divider_thickness=1,
            sort_column_index=self._sort_index,
            sort_ascending=self._sort_asc,
            visible=True,
            horizontal_margin=4,
            vertical_lines=ft.BorderSide(1, colors.border),
            horizontal_lines=ft.BorderSide(1, colors.border),
        )

    # Card view methods
    def _get_risk_color(self, score):
        if score is None or score == 0:
            return "#94a3b8"
        elif score <= 4:
            return "#10b981"
        elif score <= 9:
            return "#f59e0b"
        elif score <= 16:
            return "#f97316"
        else:
            return "#ef4444"

    def _get_risk_label(self, score):
        if score is None or score == 0:
            return "N/A"
        elif score <= 4:
            return "Low"
        elif score <= 9:
            return "Medium"
        elif score <= 16:
            return "High"
        else:
            return "Critical"

    def _on_detail_change(self):
        if self.selected_item_index is not None and self._auto_save_enabled:
            self._update_selected_item()
            self._update_risk_scores()
            self._refresh_items_list()

    def _update_risk_scores(self):
        try:
            l = self._parse_likelihood(self.d_likelihood.value) or 0
            i = self._parse_impact(self.d_impact.value) or 0
            inherent = l * i if l and i else 0
            
            if hasattr(self, "inherent_score_text") and self.inherent_score_text:
                self.inherent_score_text.value = str(inherent)
                self.inherent_score_text.color = self._get_risk_color(inherent)
                if hasattr(self.inherent_score_text, '_page') and self.inherent_score_text._page:
                    self.inherent_score_text.update()
            
            if hasattr(self, "inherent_label_text") and self.inherent_label_text:
                self.inherent_label_text.value = self._get_risk_label(inherent)
                if hasattr(self.inherent_label_text, '_page') and self.inherent_label_text._page:
                    self.inherent_label_text.update()
            
            resL = self._parse_likelihood(self.d_resL.value) or 0
            resI = self._parse_impact(self.d_resI.value) or 0
            residual = resL * resI if resL and resI else 0
            
            if hasattr(self, "residual_score_text") and self.residual_score_text:
                self.residual_score_text.value = str(residual)
                self.residual_score_text.color = self._get_risk_color(residual)
                if hasattr(self.residual_score_text, '_page') and self.residual_score_text._page:
                    self.residual_score_text.update()
            
            if hasattr(self, "residual_label_text") and self.residual_label_text:
                self.residual_label_text.value = self._get_risk_label(residual)
                if hasattr(self.residual_label_text, '_page') and self.residual_label_text._page:
                    self.residual_label_text.update()
            
        except Exception as e:
            print(f"Error updating scores: {e}")

    def _update_selected_item(self):
        if self.selected_item_index is None or self.selected_item_index >= len(self.items):
            return
            
        item = self.items[self.selected_item_index]
        item["title"] = self.d_title.value or ""
        item["desc"] = self.d_desc.value or ""
        item["riskCategory"] = self.d_category.value or ""
        item["category"] = self.d_category.value or ""
        item["process"] = self.d_process.value or ""
        item["owner"] = self.d_owner.value or ""
        
        parsed_l = self._parse_likelihood(self.d_likelihood.value)
        item["likelihood"] = parsed_l if parsed_l is not None else None
        item["likelihood_label"] = self._score_text(parsed_l)

        parsed_i = self._parse_impact(self.d_impact.value)
        item["impact"] = parsed_i if parsed_i is not None else None
        item["impact_label"] = self._score_text(parsed_i)

        item["controls"] = self.d_controls.value or ""
        
        eff = self._parse_likelihood(self.d_effectiveness.value)
        item["effectiveness"] = eff if eff is not None else None
        item["effectiveness_label"] = self._score_text(eff)
            
        item["preventive"] = self.d_preventive.value
        item["responsive"] = self.d_responsive.value
        item["data_frequency"] = self.d_frequency.value or ""
        item["frequency"] = self.d_frequency.value or ""
        
        parsed_resL = self._parse_likelihood(self.d_resL.value)
        item["resL"] = parsed_resL if parsed_resL is not None else None
        item["resL_label"] = self._score_text(parsed_resL)

        parsed_resI = self._parse_impact(self.d_resI.value)
        item["resI"] = parsed_resI if parsed_resI is not None else None
        item["resI_label"] = self._score_text(parsed_resI)
            
        item["evidence"] = self.d_evidence.value or ""
        item["responsible"] = self.d_responsible.value or ""
        item["due"] = self.d_due.value or ""
        item["notes"] = self.d_notes.value or ""

    def _load_item_to_form(self, index):
        if index is None or index >= len(self.items):
            print(f"DEBUG: Invalid index {index} or no items available")
            return
            
        item = self.items[index]
        print(f"DEBUG: Loading item {index}: {item.get('title', 'Untitled')}")
        
        self.d_title.value = item.get("title", "")
        self.d_desc.value = item.get("desc", "")
        self.d_category.value = item.get("riskCategory") or item.get("category")
        self.d_process.value = item.get("process", "")
        self.d_owner.value = item.get("owner", "")
        self.d_likelihood.value = str(item.get("likelihood")) if item.get("likelihood") else None
        self.d_impact.value = str(item.get("impact")) if item.get("impact") else None
        self.d_controls.value = item.get("controls", "")
        self.d_effectiveness.value = str(item.get("effectiveness")) if item.get("effectiveness") else None
        self.d_preventive.value = item.get("preventive")
        self.d_responsive.value = item.get("responsive")
        self.d_frequency.value = item.get("data_frequency") or item.get("frequency")
        self.d_resL.value = str(item.get("resL")) if item.get("resL") else None
        self.d_resI.value = str(item.get("resI")) if item.get("resI") else None
        self.d_evidence.value = item.get("evidence")
        self.d_responsible.value = item.get("responsible", "")
        due_value = item.get("due", "")
        self.d_due.value = self._format_date(due_value) if due_value else ""
        self._set_date_picker_value(self.d_due_picker, self.d_due.value)
        self.d_notes.value = item.get("notes", "")
        
        self._update_risk_scores()
        print(f"DEBUG: Item {index} loaded into form successfully")

    def _select_item(self, index):
        print(f"DEBUG: Selecting item at index {index}")
        self.selected_item_index = index
        self.empty_state.visible = False
        self.detail_form_container.visible = True
        if hasattr(self, "detail_action_row"):
            self.detail_action_row.visible = True
        
        self._load_item_to_form(index)
        self._refresh_items_list()
        
        # Force page update to ensure UI changes are visible
        if hasattr(self, 'page') and self.page:
            self.page.update()
            print(f"DEBUG: Page updated after selecting item {index}")

    def _add_new_risk(self, select_current=True):
        self._open_item_modal(None)

    def _delete_selected_risk(self):
        if self.selected_item_index is not None and self.selected_item_index < len(self.items):
            del self.items[self.selected_item_index]
            self.selected_item_index = None
            self.empty_state.visible = True
            self.detail_form_container.visible = False
            if getattr(self, "detail_action_row", None):
                self.detail_action_row.visible = False
            self._refresh_items_list()
            self._refresh_table_rows()

    def _duplicate_risk(self):
        if self.selected_item_index is not None and self.selected_item_index < len(self.items):
            original = self.items[self.selected_item_index]
            duplicate = dict(original)
            duplicate["title"] = f"{original.get('title', 'Risk')} (Copy)"
            self.items.append(duplicate)
            self._refresh_items_list()
            self._refresh_table_rows()
            self._select_item(len(self.items) - 1)

    def _filter_items(self):
        self._refresh_items_list()

    def _create_risk_card(self, item, index, is_selected):
        colors = get_theme_colors(self.page.theme_mode if hasattr(self.page, "theme_mode") else ft.ThemeMode.LIGHT)
        
        l = self._parse_likelihood(item.get("likelihood") or item.get("likelihood_label")) or 0
        i = self._parse_impact(item.get("impact") or item.get("impact_label")) or 0
        inherent = l * i if l and i else 0
        
        resL = self._parse_likelihood(item.get("resL") or item.get("resL_label")) or 0
        resI = self._parse_impact(item.get("resI") or item.get("resI_label")) or 0
        residual = resL * resI if resL and resI else 0

        card = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Container(
                        content=ft.Text(str(inherent), size=16, weight=ft.FontWeight.BOLD, color="white"),
                        padding=8,
                        border_radius=4,
                        bgcolor=self._get_risk_color(inherent),
                        width=40,
                        height=40,
                        alignment=ft.alignment.center
                    ),
                    ft.Column([
                        ft.Text(item.get("title", "Untitled")[:40], size=14, weight=ft.FontWeight.BOLD, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                        ft.Text(f"{item.get('riskCategory', 'N/A')} • {item.get('process', 'N/A')}", size=11, color="#64748b", max_lines=1, overflow=ft.TextOverflow.ELLIPSIS)
                    ], spacing=2, expand=True),
                    ft.Container(
                        content=ft.Text(str(residual), size=12, weight=ft.FontWeight.BOLD, color=self._get_risk_color(residual)),
                        alignment=ft.alignment.center,
                        width=30
                    )
                ], spacing=12)
            ]),
            padding=12,
            border_radius=8,
            bgcolor="#2196F3" if is_selected else colors.hover_bg,
            border=ft.border.all(2, "#2196F3" if is_selected else "transparent"),
            on_click=lambda e, idx=index: self._handle_card_click(idx)
        )
        
        return card

    def _handle_card_click(self, index):
        """Handle card click with debugging"""
        print(f"DEBUG: Card clicked for index {index}")
        self._select_item(index)

    def _refresh_items_list(self):
        search_query = (self.search_tf.value or "").lower().strip()
        
        self.items_list.controls.clear()
        
        for idx, item in enumerate(self.items):
            if search_query:
                searchable = f"{item.get('title', '')} {item.get('desc', '')} {item.get('riskCategory', '')} {item.get('process', '')}".lower()
                if search_query not in searchable:
                    continue
            
            is_selected = idx == self.selected_item_index
            card = self._create_risk_card(item, idx, is_selected)
            self.items_list.controls.append(card)
        
        if not self.items_list.controls:
            self.items_list.controls.append(
                ft.Container(
                    content=ft.Text("No risks found", color="#64748b", text_align=ft.TextAlign.CENTER),
                    padding=20,
                    alignment=ft.alignment.center
                )
            )
        
        # Only update if the control is already added to the page
        if hasattr(self, 'items_list') and self.items_list and hasattr(self.items_list, '_page') and self.items_list._page:
            self.items_list.update()

    def _load_assessment_data(self):
        try:
            print(f"DEBUG: Loading assessment data for edit mode")
            
            if hasattr(self.assessment, 'title'):
                self.title_tf.value = self.assessment.title
            if hasattr(self.assessment, 'risk_level') and self.assessment.risk_level:
                risk_to_category = {
                    'Low': 'Compliance',
                    'Medium': 'Operational',
                    'High': 'Market',
                    'Critical': 'Credit'
                }
                category = risk_to_category.get(self.assessment.risk_level, 'Other')
                self.category_dd.value = category
            if hasattr(self.assessment, 'auditor'):
                self.assessor_tf.value = self.assessment.auditor
            if hasattr(self.assessment, 'assessment_date'):
                self.date_tf.value = self.assessment.assessment_date
            if hasattr(self.assessment, 'department'):
                self.process_tf.value = self.assessment.department
            
            if hasattr(self.assessment, 'id') and self.page:
                self.page.run_task(self._load_risk_assessments_async, self.assessment.id)
                    
            self.page.update()
            print("DEBUG: Assessment data loaded into form")
            
        except Exception as e:
            print(f"ERROR: Error loading assessment data: {e}")
            import traceback
            traceback.print_exc()

    async def _load_risk_assessments_async(self, assessment_id):
        try:
            print(f"DEBUG: Loading risk assessments for assessment ID: {assessment_id}")
            
            reference_id = getattr(self.assessment, 'reference_id', assessment_id)
            assessment_data = await self.assessment_controller.get_risk_assessment(reference_id)
            
            if assessment_data and 'riskAssessments' in assessment_data:
                print(f"DEBUG: Loaded {len(assessment_data['riskAssessments'])} risk assessments")
                
                self.items = []
                for risk_data in assessment_data['riskAssessments']:
                    item = {
                        'id': risk_data.get('riskAssessment_RefID'),
                        'ref_id': risk_data.get('riskAssessment_RefID'),
                        'title': risk_data.get('risksAssessment_KeyRiskAndFactors', ''),
                        'desc': risk_data.get('processObjectivesAssessment_BusinessObjectives', ''),
                        'riskCategory': risk_data.get('risksAssessment_RiskCategory', ''),
                        'process': risk_data.get('processObjectivesAssessment_MainProcess', ''),
                        'sub_process': risk_data.get('processObjectivesAssessment_SubProcess', ''),
                        'likelihood': risk_data.get('risksAssessment_RiskLikelihood', ''),
                        'impact': risk_data.get('risksAssessment_RiskImpact', ''),
                        'resL': risk_data.get('outcomeAssessment_OutcomeLikelihood', ''),
                        'resI': risk_data.get('outcomeAssessment_Impact', ''),
                        'owner': risk_data.get('controlsAssessment_Responsibility', ''),
                        'responsible': risk_data.get('outcomeAssessment_ResponsiblePerson', ''),
                        'due': risk_data.get('outcomeAssessment_AgreedDate', ''),
                        'evidence': risk_data.get('outcomeAssessment_Evidence', ''),
                        'controls': risk_data.get('controlsAssessment_MitigatingControls', ''),
                        'effectiveness': risk_data.get('controlsAssessment_Effectiveness', ''),
                        'preventive': risk_data.get('controlsAssessment_Preventive'),
                        'responsive': risk_data.get('controlsAssessment_Responsive'),
                        'data_frequency': risk_data.get('controlsAssessment_DataFrequency', ''),
                        'frequency': risk_data.get('controlsAssessment_Frequency', ''),
                        'keyOrSecondary': risk_data.get('risksAssessment_KeyOrSecondary', ''),
                        'notes': risk_data.get('outcomeAssessment_AuditorsRecommendedActionPlan', ''),
                        'authoriser': risk_data.get('outcomeAssessment_Authoriser', ''),
                    }
                    self.items.append(self._normalize_risk_item(item))
                
                self._refresh_items_list()
                self._refresh_table_rows()
                print(f"DEBUG: Views refreshed with {len(self.items)} items")
            else:
                print("DEBUG: No risk assessment data found")
                
        except Exception as e:
            print(f"ERROR: Error loading risk assessments: {e}")
            import traceback
            traceback.print_exc()

    def _on_mode_change(self, e):
        self.mode = e.control.value
        self._apply_mode_disabled()
        self._refresh_table_rows()

    def _apply_mode_disabled(self):
        disabled = self.mode == "view"
        # Note: approved_by_tf is always read-only (set via approval workflow)
        for ctrl in [self.title_tf, self.category_dd, self.process_tf, self.assessor_tf, self.date_tf, self.status_dd]:
            if isinstance(ctrl, ft.TextField):
                ctrl.read_only = disabled
            if isinstance(ctrl, ft.Dropdown):
                ctrl.disabled = disabled
        if hasattr(self, 'page') and self.page:
            self.page.update()

    def _compute_inherent(self, l, i):
        try:
            l_val = self._parse_likelihood(l) or 0
            i_val = self._parse_impact(i) or 0
            return l_val * i_val if l_val and i_val else 0
        except Exception:
            return 0

    def _parse_likelihood(self, value):
        if isinstance(value, (int, float)):
            return int(value)
        if isinstance(value, str):
            likelihood_map = {
                'very low': 1, 'low': 2, 'medium': 3, 'high': 4, 'very high': 5,
                'rare': 1, 'unlikely': 2, 'possible': 3, 'likely': 4, 'almost certain': 5
            }
            stripped = value.strip()
            if not stripped:
                return None
            if stripped.isdigit():
                return int(stripped)
            if stripped[0].isdigit():
                leading = ''.join(ch for ch in stripped if ch.isdigit())
                if leading:
                    return int(leading)
            key = stripped.lower()
            return likelihood_map.get(key)
        return None

    def _parse_impact(self, value):
        if isinstance(value, (int, float)):
            return int(value)
        if isinstance(value, str):
            impact_map = {
                'negligible': 1, 'minor': 2, 'moderate': 3, 'major': 4, 'catastrophic': 5,
                'lower': 1, 'low': 2, 'medium': 3, 'high': 4, 'very high': 5
            }
            stripped = value.strip()
            if not stripped:
                return None
            if stripped.isdigit():
                return int(stripped)
            if stripped[0].isdigit():
                leading = ''.join(ch for ch in stripped if ch.isdigit())
                if leading:
                    return int(leading)
            key = stripped.lower()
            return impact_map.get(key)
        return None

    def _format_date(self, date_value):
        """Format date value to YYYY-MM-DD string, extracting date-only from datetime strings"""
        if not date_value:
            return ""
        if isinstance(date_value, str):
            # Handle datetime strings like "2025-03-01T12:00:00" or ISO format
            cleaned = date_value.strip()
            if "T" in cleaned:
                return cleaned.split("T")[0]
            # If it's already YYYY-MM-DD format, return as-is
            if len(cleaned) >= 10:
                return cleaned[:10]
            return cleaned
        if isinstance(date_value, date):
            return date_value.strftime("%Y-%m-%d")
        if isinstance(date_value, datetime):
            return date_value.date().strftime("%Y-%m-%d")
        if hasattr(date_value, "strftime"):
            return date_value.strftime("%Y-%m-%d")
        return str(date_value)

    def _register_date_pickers(self):
        if not hasattr(self.page, "overlay"):
            return
        for picker in [self.date_picker, self.d_due_picker, self.m_due_picker]:
            if picker and picker not in self.page.overlay:
                self.page.overlay.append(picker)

    def _open_date_picker(self, picker):
        """Open a date picker dialog"""
        if picker and hasattr(self.page, "update"):
            picker.open = True
            self.page.update()

    def _set_date_picker_value(self, picker, value):
        if not picker:
            return
        if not value:
            picker.value = None
            return
        if isinstance(value, date):
            picker.value = value
            return
        if isinstance(value, datetime):
            picker.value = value.date()
            return
        if isinstance(value, str):
            try:
                parsed = datetime.strptime(value[:10], "%Y-%m-%d")
                picker.value = parsed.date()
            except Exception:
                picker.value = None
                return

    def _parse_date_input(self, value):
        if not value:
            return None
        if isinstance(value, (datetime, date)):
            return value.strftime("%Y-%m-%d")
        if isinstance(value, str):
            cleaned = value.strip()
            if not cleaned:
                return None
            try:
                parsed = datetime.strptime(cleaned[:10], "%Y-%m-%d")
                return parsed.strftime("%Y-%m-%d")
            except Exception:
                return cleaned
        return str(value)

    def _resolve_lookup_id(self, items, value, label_keys=("description", "name", "title", "value", "label")):
        if not value or not items:
            return None
        target = str(value).strip().lower()
        if not target:
            return None
        for entry in items or []:
            if isinstance(entry, dict):
                label = next((entry.get(k) for k in label_keys if entry.get(k) is not None), None)
                entry_id = entry.get("id") or entry.get("Id")
                if label is not None and entry_id is not None:
                    if str(label).strip().lower() == target:
                        return entry_id
            else:
                if str(entry).strip().lower() == target:
                    return entry
        return None

    def _on_header_date_pick(self, e):
        if e.control.value:
            # Extract date-only value (YYYY-MM-DD)
            if isinstance(e.control.value, date):
                formatted = e.control.value.strftime("%Y-%m-%d")
            elif isinstance(e.control.value, datetime):
                formatted = e.control.value.date().strftime("%Y-%m-%d")
            else:
                formatted = self._format_date(e.control.value)
            self.date_tf.value = formatted
        if hasattr(self.page, "update"):
            self.page.update()

    def _on_detail_due_pick(self, e):
        if e.control.value:
            # Extract date-only value (YYYY-MM-DD)
            if isinstance(e.control.value, date):
                formatted = e.control.value.strftime("%Y-%m-%d")
            elif isinstance(e.control.value, datetime):
                formatted = e.control.value.date().strftime("%Y-%m-%d")
            else:
                formatted = self._format_date(e.control.value)
            self.d_due.value = formatted
            self._on_detail_change()
        if hasattr(self.page, "update"):
            self.page.update()

    def _on_modal_due_pick(self, e):
        if e.control.value:
            # Extract date-only value (YYYY-MM-DD)
            if isinstance(e.control.value, date):
                formatted = e.control.value.strftime("%Y-%m-%d")
            elif isinstance(e.control.value, datetime):
                formatted = e.control.value.date().strftime("%Y-%m-%d")
            else:
                formatted = self._format_date(e.control.value)
            self.m_due.value = formatted
        if hasattr(self.page, "update"):
            self.page.update()

    def _score_label_from_numeric(self, numeric_value):
        if numeric_value in (None, "", "None"):
            return ""
        try:
            numeric_int = int(float(numeric_value))
            return "" if numeric_int == 0 else str(numeric_int)
        except (TypeError, ValueError):
            return str(numeric_value)

    def _score_text(self, numeric_value):
        if numeric_value in (None, "", "None"):
            return ""
        try:
            numeric_int = int(float(numeric_value))
        except (TypeError, ValueError):
            numeric_int = None
        if numeric_int is None or numeric_int == 0:
            return ""
        return self._score_text_map.get(str(numeric_int), str(numeric_int))

    def _normalize_risk_item(self, item):
        if not isinstance(item, dict):
            return {}
        normalized = dict(item)
        
        for key in ["likelihood", "impact", "resL", "resI", "effectiveness"]:
            value = normalized.get(key)
            parser = self._parse_likelihood if key in ("likelihood", "resL", "effectiveness") else self._parse_impact
            parsed = parser(value)
            normalized[key] = parsed if parsed is not None else (0 if isinstance(value, (int, float)) else None)
        
        # Always format due date to ensure it's date-only (YYYY-MM-DD)
        if normalized.get("due"):
            normalized["due"] = self._format_date(normalized.get("due"))
        
        normalized.setdefault("likelihood_label", self._score_text(normalized.get("likelihood")))
        normalized.setdefault("impact_label", self._score_text(normalized.get("impact")))
        normalized.setdefault("resL_label", self._score_text(normalized.get("resL")))
        normalized.setdefault("resI_label", self._score_text(normalized.get("resI")))
        normalized.setdefault("effectiveness_label", self._score_text(normalized.get("effectiveness")))
        normalized.setdefault("riskCategory", normalized.get("riskCategory") or normalized.get("category") or "")
        normalized.setdefault("category", normalized.get("riskCategory", ""))
        normalized.setdefault("process", normalized.get("process") or self.process_tf.value or "")
        normalized.setdefault("sub_process", normalized.get("sub_process") or normalized.get("subProcess") or "")
        normalized.setdefault("keyOrSecondary", normalized.get("keyOrSecondary") or normalized.get("risk_type") or "")
        normalized.setdefault("responsible", normalized.get("responsible") or normalized.get("owner") or "")
        normalized.setdefault("data_frequency", normalized.get("data_frequency") or normalized.get("frequency") or "")
        normalized.setdefault("frequency", normalized.get("frequency") or normalized.get("data_frequency") or "")
        normalized.setdefault("evidence", normalized.get("evidence") or "")
        normalized.setdefault("authoriser", normalized.get("authoriser") or normalized.get("authorizer") or "")
        normalized.setdefault("title", normalized.get("title") or "Untitled risk")
        normalized.setdefault("desc", normalized.get("desc") or "")
        normalized.setdefault("controls", normalized.get("controls") or "")
        normalized.setdefault("notes", normalized.get("notes") or "")
        
        return normalized

    def _init_data(self):
        try:
            src = self.assessment
            if hasattr(src, "title") or isinstance(src, dict):
                getv = (lambda k: getattr(src, k, None)) if not isinstance(src, dict) else (lambda k: src.get(k))

                # Robustly check for API data keys (handling PascalCase and camelCase)
                if isinstance(src, dict) and any(k in src for k in ["referenceId", "ReferenceId", "riskAssessments", "RiskAssessments"]):
                    print(f"DEBUG: Initializing from API dict. Keys: {list(src.keys())}")
                    
                    self.title_tf.value = src.get("title") or src.get("Title") or src.get("client", "") or src.get("Client", "")
                    self.assessor_tf.value = src.get("assessor") or src.get("Assessor") or src.get("auditor", "")
                    
                    # Display ApprovedBy from database (read-only)
                    approved_by = src.get("approvedBy") or src.get("ApprovedBy") or src.get("approved_by", "")
                    self.approved_by_tf.value = approved_by if approved_by else "Pending Approval"

                    primary_process = src.get("process") or src.get("mainProcess") or src.get("MainProcess")
                    if primary_process:
                        self.process_tf.value = primary_process

                    dt = src.get("assessmentStartDate") or src.get("AssessmentStartDate")
                    if dt:
                        if isinstance(dt, str):
                            self.date_tf.value = dt.split("T")[0]
                        elif hasattr(dt, "strftime"):
                            self.date_tf.value = dt.strftime("%Y-%m-%d")
                    else:
                        self.date_tf.value = ""
                    self._set_date_picker_value(self.date_picker, self.date_tf.value)

                    status_value = src.get("status") or src.get("Status") or self.status_dd.value or "Draft"
                    self.status_dd.value = status_value

                    risks = []
                    risk_assessments = src.get("riskAssessments") or src.get("RiskAssessments") or []
                    print(f"DEBUG: Found {len(risk_assessments)} risk assessments in API response")
                    if risk_assessments and isinstance(risk_assessments[0], dict):
                         print(f"DEBUG: First risk item keys: {list(risk_assessments[0].keys())}")
                    
                    for ra in risk_assessments:
                        if isinstance(ra, dict):
                            likelihood_text = ra.get("risksAssessment_RiskLikelihood")
                            impact_text = ra.get("risksAssessment_RiskImpact")
                            residual_likelihood_text = ra.get("outcomeAssessment_OutcomeLikelihood")
                            residual_impact_text = ra.get("outcomeAssessment_Impact")
                            effectiveness_text = ra.get("controlsAssessment_Effectiveness")

                            risk_item = {
                                "title": ra.get("risksAssessment_KeyRiskAndFactors", ""),
                                "desc": ra.get("processObjectivesAssessment_BusinessObjectives", ""),
                                "likelihood": self._parse_likelihood(likelihood_text),
                                "likelihood_label": likelihood_text,
                                "impact": self._parse_impact(impact_text),
                                "impact_label": impact_text,
                                "controls": ra.get("controlsAssessment_MitigatingControls", ""),
                                "effectiveness": self._parse_likelihood(effectiveness_text) if effectiveness_text else None,
                                "effectiveness_label": effectiveness_text,
                                "resL": self._parse_likelihood(residual_likelihood_text),
                                "resL_label": residual_likelihood_text,
                                "resI": self._parse_impact(residual_impact_text),
                                "resI_label": residual_impact_text,
                                "owner": ra.get("controlsAssessment_Responsibility", ""),
                                "responsible": ra.get("outcomeAssessment_ResponsiblePerson", ""),
                                "authoriser": ra.get("outcomeAssessment_Authoriser", ""),
                                "due": self._format_date(ra.get("outcomeAssessment_AgreedDate")),
                                "notes": ra.get("outcomeAssessment_AuditorsRecommendedActionPlan", ""),
                                "riskCategory": ra.get("risksAssessment_RiskCategory", ""),
                                "keyOrSecondary": ra.get("risksAssessment_KeyOrSecondary", ""),
                                "process": ra.get("processObjectivesAssessment_MainProcess", ""),
                                "sub_process": ra.get("processObjectivesAssessment_SubProcess", ""),
                                "data_frequency": ra.get("controlsAssessment_DataFrequency", ""),
                                "frequency": ra.get("controlsAssessment_Frequency", ""),
                                "evidence": ra.get("outcomeAssessment_Evidence", ""),
                                "preventive": ra.get("controlsAssessment_Preventive"),
                                "responsive": ra.get("controlsAssessment_Responsive"),
                                "ref_id": ra.get("riskAssessment_RefID"),
                            }
                            risks.append(self._normalize_risk_item(risk_item))

                    if not primary_process:
                        first_process = next((r.get("process") for r in risks if r.get("process")), "")
                        if first_process:
                            self.process_tf.value = first_process

                    first_category = next((r.get("riskCategory") for r in risks if r.get("riskCategory")), None)
                    if first_category:
                        self.category_dd.value = first_category

                    self.items = risks

                else:
                    self.title_tf.value = getv("title") or ""
                    self.assessor_tf.value = getv("auditor") or ""
                    dt = getv("assessment_date") or getv("date")
                    if isinstance(dt, str):
                        self.date_tf.value = dt.split("T")[0]
                    elif hasattr(dt, "strftime"):
                        self.date_tf.value = dt.strftime("%Y-%m-%d")
                    else:
                        self.date_tf.value = ""
                    self._set_date_picker_value(self.date_picker, self.date_tf.value)
                    status_guess = getv("risk_level") or self.status_dd.value
                    if status_guess:
                        self.status_dd.value = status_guess

                    risks = []
                    if isinstance(src, dict):
                        rich_items = src.get("risk_items")
                        if isinstance(rich_items, list) and rich_items:
                            risks = [self._normalize_risk_item(r) for r in rich_items if isinstance(r, dict)]

                    if not risks:
                        rf = getv("risk_factors") or []
                        if isinstance(rf, list):
                            for f in rf:
                                if isinstance(f, dict):
                                    val = f.get("value")
                                    numeric = None
                                    if isinstance(val, (int, float)):
                                        numeric = int(val)
                                    fallback_risk = {
                                        "title": f.get("name"),
                                        "desc": f.get("description") or "",
                                        "likelihood": numeric,
                                        "impact": numeric,
                                        "controls": "",
                                        "effectiveness": None,
                                        "resL": None,
                                        "resI": None,
                                        "owner": getv("auditor") or "",
                                        "due": "",
                                        "notes": "",
                                    }
                                    risks.append(self._normalize_risk_item(fallback_risk))

                    self.items = risks

        except Exception as ex:
            print(f"DEBUG: Error in _init_data: {ex}")
            import traceback
            traceback.print_exc()

        # Add sample data if no items exist
        if not self.items:
            print("DEBUG: No items found, adding sample data")
            sample_items = [
                {
                    "title": "Stock shortages due to delayed shipments",
                    "desc": "Risk of inventory shortages when suppliers fail to deliver on time",
                    "riskCategory": "Operational Risk",
                    "category": "Operational Risk",
                    "process": "Supply Chain Management",
                    "owner": "Team A",
                    "likelihood": 3,
                    "likelihood_label": "3",
                    "impact": 4,
                    "impact_label": "4",
                    "controls": "Maintain safety stock levels and diversify suppliers",
                    "effectiveness": 3,
                    "effectiveness_label": "3",
                    "preventive": "Yes",
                    "responsive": "Yes",
                    "data_frequency": "Monthly",
                    "frequency": "Monthly",
                    "resL": 2,
                    "resL_label": "2",
                    "resI": 3,
                    "resI_label": "3",
                    "evidence": "Inventory reports",
                    "responsible": "Supply Chain Manager",
                    "due": "2025-03-15",
                    "notes": "Implement automated reorder points"
                },
                {
                    "title": "Risk 1",
                    "desc": "Compliance risk related to regulatory requirements",
                    "riskCategory": "Compliance Risk",
                    "category": "Compliance Risk",
                    "process": "Process A",
                    "owner": "Team A",
                    "likelihood": 2,
                    "likelihood_label": "2",
                    "impact": 3,
                    "impact_label": "3",
                    "controls": "Regular compliance audits and training",
                    "effectiveness": 4,
                    "effectiveness_label": "4",
                    "preventive": "Yes",
                    "responsive": "No",
                    "data_frequency": "Quarterly",
                    "frequency": "Quarterly",
                    "resL": 1,
                    "resL_label": "1",
                    "resI": 2,
                    "resI_label": "2",
                    "evidence": "Audit reports",
                    "responsible": "Compliance Officer",
                    "due": "2025-02-28",
                    "notes": "Update compliance procedures"
                },
                {
                    "title": "Risk 2",
                    "desc": "Operational risk in business processes",
                    "riskCategory": "Operational Risk",
                    "category": "Operational Risk",
                    "process": "Process B",
                    "owner": "Team B",
                    "likelihood": 4,
                    "likelihood_label": "4",
                    "impact": 2,
                    "impact_label": "2",
                    "controls": "Process automation and monitoring",
                    "effectiveness": 3,
                    "effectiveness_label": "3",
                    "preventive": "Yes",
                    "responsive": "Yes",
                    "data_frequency": "Weekly",
                    "frequency": "Weekly",
                    "resL": 3,
                    "resL_label": "3",
                    "resI": 1,
                    "resI_label": "1",
                    "evidence": "Process metrics",
                    "responsible": "Operations Manager",
                    "due": "2025-03-01",
                    "notes": "Implement process improvements"
                }
            ]
            self.items = sample_items
            print(f"DEBUG: Added {len(sample_items)} sample items")

        # Don't refresh lists during initialization - wait until UI is built
        self._apply_mode_disabled()
        
        # Explicitly refresh table rows to show the loaded data
        if self.items:
            print(f"DEBUG: Initial refresh of table with {len(self.items)} items")
            self._refresh_table_rows()

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
            if categories:
                self.category_dd.options = [ft.dropdown.Option(c) for c in categories]
                self.d_category.options = [ft.dropdown.Option(c) for c in categories]
                if not self.category_dd.value:
                    self.category_dd.value = categories[0]
                if not self.d_category.value:
                    self.d_category.value = categories[0]
            
            evid_text = to_text_list(self._evidence_items_raw)
            if evid_text:
                self.d_evidence.options = [ft.dropdown.Option(e) for e in evid_text]
            
            freqs_text = to_text_list(self._data_freq_items_raw)
            if freqs_text:
                self.d_frequency.options = [ft.dropdown.Option(f) for f in freqs_text]

            if hasattr(self, 'm_risk_category'):
                self.m_risk_category.options = [ft.dropdown.Option(c) for c in categories]
            if hasattr(self, 'm_evidence'):
                self.m_evidence.options = [ft.dropdown.Option(e) for e in evid_text]
            if hasattr(self, 'm_frequency'):
                self.m_frequency.options = [ft.dropdown.Option(f) for f in freqs_text]

            if hasattr(self, 'page') and self.page:
                self.page.update()
        except Exception as e:
            print(f"Error loading lookups: {e}")

    def _safe_lower(self, v):
        if v is None:
            return ""
        return str(v).lower()

    def _on_sort(self, col_index):
        if self._sort_index == col_index:
            self._sort_asc = not self._sort_asc
        else:
            self._sort_index = col_index
            self._sort_asc = True
        self._refresh_table_rows()

    def _inherent_of(self, it):
        return self._compute_inherent(it.get("likelihood"), it.get("impact"))

    def _residual_of(self, it):
        return self._compute_inherent(it.get("resL"), it.get("resI"))

    def _sort_key_tuple(self, it):
        mapping = [
            self._safe_lower(it.get("title")),
            self._safe_lower(it.get("riskCategory") or it.get("category")),
            self._safe_lower(it.get("process")),
            self._parse_likelihood(it.get("likelihood")) or 0,
            self._parse_impact(it.get("impact")) or 0,
            self._inherent_of(it),
            self._parse_likelihood(it.get("resL")) or 0,
            self._parse_impact(it.get("resI")) or 0,
            self._residual_of(it),
            self._safe_lower(it.get("owner")),
            self._safe_lower(it.get("due")),
            self._safe_lower(it.get("evidence")),
        ]
        idx = max(0, min(self._sort_index, len(mapping) - 1))
        return mapping[idx]

    def _filter_match(self, it, q):
        if not q:
            return True
        q = q.lower()
        fields = [
            it.get("title"), it.get("riskCategory") or it.get("category"), it.get("process"),
            it.get("owner"), it.get("evidence"), it.get("desc"), it.get("notes"), it.get("sub_process"),
        ]
        for f in fields:
            if f and q in str(f).lower():
                return True
        return False

    def _refresh_table_rows(self):
        if not self.table:
            return
        query = (self.filter_tf.value or "").strip()

        data = [self._normalize_risk_item(it) for it in (self.items or [])]
        data = [it for it in data if self._filter_match(it, query)]
        try:
            data.sort(key=lambda it: self._sort_key_tuple(it), reverse=not self._sort_asc)
        except Exception:
            pass

        rows = []
        show_actions = self.mode != "view"
        colors = get_theme_colors(self.page.theme_mode if hasattr(self.page, "theme_mode") else ft.ThemeMode.LIGHT)

        def create_text_cell(text, width, max_chars=30):
            text = text or ""
            text_widget = ft.Text(
                text, 
                size=11, 
                overflow=ft.TextOverflow.ELLIPSIS,
                max_lines=2,
                color=colors.text_primary,
                no_wrap=False
            )
            return ft.Container(
                content=text_widget, 
                width=width,
                tooltip=text if text else None
            )

        def create_dropdown_cell(value, options, width, on_change_handler, tooltip_text=None):
            dropdown = ft.Dropdown(
                value=value,
                options=options,
                border=ft.InputBorder.NONE,
                content_padding=ft.padding.symmetric(horizontal=2, vertical=2),
                text_size=11,
                width=width,
                on_change=on_change_handler,
                disabled=self.mode == "view"
            )
            return ft.Container(
                content=dropdown,
                tooltip=tooltip_text if tooltip_text else None
            )

        if not data:
            pass
        else:
            for idx, it in enumerate(data):
                inherent = self._inherent_of(it)
                residual = self._residual_of(it)

                try:
                    orig_index = self.items.index(it)
                except ValueError:
                    orig_index = next((i for i, x in enumerate(self.items)
                                       if x.get('title') == it.get('title') and x.get('desc') == it.get('desc')), idx)

                title_text = it.get("title", "") or ""
                process_text = it.get("process", "") or ""
                owner_text = it.get("owner", "") or ""
                due_text = it.get("due", "") or ""
                
                title_cell = create_text_cell(title_text, 150)
                
                category_text = it.get("riskCategory") or it.get("category") or ""
                category_options = [
                    ft.dropdown.Option("Operational Risk"),
                    ft.dropdown.Option("Market Risk"),
                    ft.dropdown.Option("Credit Risk"),
                    ft.dropdown.Option("Compliance Risk"),
                    ft.dropdown.Option("IT & Security Risk"),
                    ft.dropdown.Option("Strategic Risk"),
                ]
                category_cell = create_dropdown_cell(
                    category_text,
                    category_options,
                    150,
                    lambda e, i=orig_index: self._update_item_field(i, "riskCategory", e.control.value),
                    category_text
                )
                
                process_cell = create_text_cell(process_text, 130)
                
                likelihood_value = it.get("likelihood_label") or it.get("likelihood")
                likelihood_display = str(self._parse_likelihood(likelihood_value) or 1)
                likelihood_labels = ['Very Low', 'Low', 'Medium', 'High', 'Very High']
                likelihood_full = f"{likelihood_display} - {likelihood_labels[int(likelihood_display)-1]}" if likelihood_display.isdigit() else likelihood_display
                
                likelihood_cell = create_dropdown_cell(
                    likelihood_display,
                    [ft.dropdown.Option(str(i), f"{i} - {likelihood_labels[i-1]}") for i in range(1, 6)],
                    130,
                    lambda e, i=orig_index: self._update_item_field(i, "likelihood_label", e.control.value),
                    likelihood_full
                )
                
                impact_value = it.get("impact_label") or it.get("impact")
                impact_display = str(self._parse_impact(impact_value) or 1)
                impact_full = f"{impact_display} - {likelihood_labels[int(impact_display)-1]}" if impact_display.isdigit() else impact_display
                
                impact_cell = create_dropdown_cell(
                    impact_display,
                    [ft.dropdown.Option(str(i), f"{i} - {likelihood_labels[i-1]}") for i in range(1, 6)],
                    130,
                    lambda e, i=orig_index: self._update_item_field(i, "impact_label", e.control.value),
                    impact_full
                )
                
                inherent_field = ft.Container(
                    content=ft.Text(str(inherent) if inherent else "--", size=11, color=self._get_risk_color(inherent)),
                    tooltip=f"Inherent Risk Score: {inherent}" if inherent else "Not calculated"
                )
                
                resL_value = it.get("resL_label") or it.get("resL")
                if resL_value in ["1", "2", "3", "4", "5"]:
                    resL_display = resL_value
                elif resL_value in ["Very Low", "Low", "Medium", "High", "Very High"]:
                    resL_map = {"Very Low": "1", "Low": "2", "Medium": "3", "High": "4", "Very High": "5"}
                    resL_display = resL_map.get(resL_value, "1")
                else:
                    resL_display = "1"
                resL_full = f"{resL_display} - {likelihood_labels[int(resL_display)-1]}" if resL_display.isdigit() else resL_display
                
                resL_cell = create_dropdown_cell(
                    resL_display,
                    [ft.dropdown.Option(str(i), f"{i} - {likelihood_labels[i-1]}") for i in range(1, 6)],
                    130,
                    lambda e, i=orig_index: self._update_item_field(i, "resL_label", e.control.value),
                    resL_full
                )
                
                resI_value = it.get("resI_label") or it.get("resI")
                if resI_value in ["1", "2", "3", "4", "5"]:
                    resI_display = resI_value
                elif resI_value in ["Very Low", "Low", "Medium", "High", "Very High"]:
                    resI_map = {"Very Low": "1", "Low": "2", "Medium": "3", "High": "4", "Very High": "5"}
                    resI_display = resI_map.get(resI_value, "1")
                else:
                    resI_display = "1"
                resI_full = f"{resI_display} - {likelihood_labels[int(resI_display)-1]}" if resI_display.isdigit() else resI_display
                
                resI_cell = create_dropdown_cell(
                    resI_display,
                    [ft.dropdown.Option(str(i), f"{i} - {likelihood_labels[i-1]}") for i in range(1, 6)],
                    130,
                    lambda e, i=orig_index: self._update_item_field(i, "resI_label", e.control.value),
                    resI_full
                )
                
                residual_field = ft.Container(
                    content=ft.Text(str(residual) if residual else "--", size=11, color=self._get_risk_color(residual)),
                    tooltip=f"Residual Risk Score: {residual}" if residual else "Not calculated"
                )
                
                owner_cell = create_text_cell(owner_text, 120)
                
                due_display = due_text[:10] if due_text else ""
                due_cell = ft.Container(
                    content=ft.Text(due_display, size=11, color=colors.text_primary),
                    width=90,
                    tooltip=due_text if due_text else "No date set"
                )
                
                evidence_text = it.get("evidence", "") or ""
                evidence_options = [
                    ft.dropdown.Option("Compliance Programs"),
                    ft.dropdown.Option("Committee or Board decision"),
                    ft.dropdown.Option("System timestamp"),
                    ft.dropdown.Option("External audit report"),
                    ft.dropdown.Option("Internal audit report"),
                    ft.dropdown.Option("Management certification"),
                ]
                evidence_cell = create_dropdown_cell(
                    evidence_text,
                    evidence_options,
                    200,
                    lambda e, i=orig_index: self._update_item_field(i, "evidence", e.control.value),
                    evidence_text
                )

                current_idx = orig_index
                edit_btn = ft.IconButton(
                    icon=Icons.EDIT,
                    icon_color="#2196F3",
                    icon_size=16,
                    tooltip="Edit Risk Item",
                    on_click=lambda e, idx=current_idx: self._open_item_modal(idx),
                    bgcolor="transparent",
                    width=28,
                    height=28,
                )
                
                delete_btn = ft.IconButton(
                    icon=Icons.DELETE,
                    icon_color="#f44336",
                    icon_size=16,
                    tooltip="Delete Risk Item",
                    on_click=lambda e, idx=current_idx: self._delete_item(idx),
                    bgcolor="transparent",
                    width=28,
                    height=28,
                )

                action_buttons = ft.Row([edit_btn, delete_btn], spacing=2, visible=show_actions)

                rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(title_cell),
                            ft.DataCell(category_cell),
                            ft.DataCell(process_cell),
                            ft.DataCell(likelihood_cell),
                            ft.DataCell(impact_cell),
                            ft.DataCell(inherent_field),
                            ft.DataCell(resL_cell),
                            ft.DataCell(resI_cell),
                            ft.DataCell(residual_field),
                            ft.DataCell(owner_cell),
                            ft.DataCell(due_cell),
                            ft.DataCell(evidence_cell),
                            ft.DataCell(action_buttons),
                        ]
                    )
                )

        self.table.rows = rows
        if hasattr(self, 'page') and self.page:
            self.page.update()

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
        self.m_due = ft.TextField(
            label="Due Date",
            hint_text="YYYY-MM-DD",
            width=220,
            read_only=True,
            suffix=ft.IconButton(icon=Icons.CALENDAR_MONTH, on_click=lambda e: self._open_date_picker(self.m_due_picker)),
        )
        self.m_notes = ft.TextField(label="Notes", expand=True, border=ft.InputBorder.OUTLINE)
        self.m_risk_category = ft.Dropdown(label="Risk Category", width=260, options=[])
        self.m_preventive = ft.Dropdown(label="Preventive", width=160, options=[ft.dropdown.Option("N/A"), ft.dropdown.Option("Yes"), ft.dropdown.Option("No")])
        self.m_responsive = ft.Dropdown(label="Responsive", width=160, options=[ft.dropdown.Option("N/A"), ft.dropdown.Option("Yes"), ft.dropdown.Option("No")])
        self.m_frequency = ft.Dropdown(label="Frequency", width=180, options=[])
        self.m_evidence = ft.Dropdown(label="Evidence", width=220, options=[])

        def close_modal(_):
            try:
                if hasattr(self.page, 'close'):
                    self.page.close(self.item_dialog)
                elif hasattr(self.page, 'dialog') and self.page.dialog:
                    self.page.dialog.open = False
                    self.page.update()
                else:
                    self.item_dialog.open = False
                    self.page.update()
            except Exception as ex:
                print(f"DEBUG: Error closing modal: {ex}")
                self.item_dialog.open = False
                self.page.update()

        def save_item(_):
            if self.mode == "view":
                close_modal(None)
                return
            
            missing_fields = []
            if not (self.m_title.value or "").strip():
                missing_fields.append("Risk Title")
            if not (self.m_owner.value or "").strip():
                missing_fields.append("Owner")
            if not self.m_likelihood.value:
                missing_fields.append("Likelihood")
            if not self.m_impact.value:
                missing_fields.append("Impact")
            if not self.m_risk_category.value:
                missing_fields.append("Risk Category")
            if not self.m_resL.value:
                missing_fields.append("Residual Likelihood")
            if not self.m_resI.value:
                missing_fields.append("Residual Impact")
            if not self.m_evidence.value:
                missing_fields.append("Evidence")
            if not (self.m_due.value or "").strip():
                missing_fields.append("Due Date")
            
            if missing_fields:
                self._show_error(f"Required fields missing: {', '.join(missing_fields)}")
                return
            
            likelihood_value = self._parse_likelihood(self.m_likelihood.value)
            impact_value = self._parse_impact(self.m_impact.value)
            effectiveness_value = self._parse_likelihood(self.m_effectiveness.value)
            resL_value = self._parse_likelihood(self.m_resL.value)
            resI_value = self._parse_impact(self.m_resI.value)
            item = {
                "title": (self.m_title.value or "").strip(),
                "owner": (self.m_owner.value or "").strip(),
                "responsible": (self.m_owner.value or "").strip(),
                "desc": (self.m_desc.value or "").strip(),
                "likelihood": likelihood_value,
                "likelihood_label": self._score_text(self.m_likelihood.value),
                "impact": impact_value,
                "impact_label": self._score_text(self.m_impact.value),
                "controls": (self.m_controls.value or "").strip(),
                "effectiveness": effectiveness_value,
                "effectiveness_label": self._score_text(self.m_effectiveness.value),
                "resL": resL_value,
                "resL_label": self._score_text(self.m_resL.value),
                "resI": resI_value,
                "resI_label": self._score_text(self.m_resI.value),
                "due": (self.m_due.value or "").strip(),
                "notes": (self.m_notes.value or "").strip(),
                "riskCategory": self.m_risk_category.value,
                "category": self.m_risk_category.value,
                "preventive": self.m_preventive.value,
                "responsive": self.m_responsive.value,
                "data_frequency": self.m_frequency.value,
                "frequency": self.m_frequency.value,
                "evidence": self.m_evidence.value,
                "process": (self.process_tf.value or "").strip(),
                "sub_process": "",
            }
            item = self._normalize_risk_item(item)
            idx = getattr(self, "_edit_index", None)
            if idx is None:
                self.items.append(item)
            else:
                self.items[idx] = item
            self._edit_index = None
            close_modal(None)
            self._refresh_table_rows()
            self._refresh_items_list()

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
        print(f"DEBUG: _open_item_modal called with index={index}, total items={len(self.items)}")
        self._edit_index = index
        if index is not None and 0 <= index < len(self.items):
            it = self.items[index]
            self.m_title.value = it.get("title", "")
            self.m_owner.value = it.get("owner", "")
            self.m_desc.value = it.get("desc", "")
            self.m_likelihood.value = str(it.get("likelihood")) if it.get("likelihood") not in (None, "") else None
            self.m_impact.value = str(it.get("impact")) if it.get("impact") not in (None, "") else None
            self.m_controls.value = it.get("controls", "")
            self.m_effectiveness.value = str(it.get("effectiveness")) if it.get("effectiveness") not in (None, "") else None
            self.m_resL.value = str(it.get("resL")) if it.get("resL") not in (None, "") else None
            self.m_resI.value = str(it.get("resI")) if it.get("resI") not in (None, "") else None
            due_value = it.get("due", "")
            self.m_due.value = self._format_date(due_value) if due_value else ""
            self._set_date_picker_value(self.m_due_picker, self.m_due.value)
            self.m_notes.value = it.get("notes", "")
            self.m_risk_category.value = it.get("riskCategory") or it.get("category") or None
            self.m_preventive.value = it.get("preventive") or None
            self.m_responsive.value = it.get("responsive") or None
            self.m_frequency.value = it.get("data_frequency") or it.get("frequency") or None
            self.m_evidence.value = it.get("evidence") or None
        else:
            for tf in [self.m_title, self.m_owner, self.m_desc, self.m_controls, self.m_due, self.m_notes]:
                tf.value = ""
            for dd in [
                self.m_likelihood, self.m_impact, self.m_effectiveness, self.m_resL, self.m_resI,
                self.m_risk_category, self.m_preventive, self.m_responsive, self.m_frequency, self.m_evidence,
            ]:
                dd.value = None
            self._set_date_picker_value(self.m_due_picker, None)
        
        try:
            if hasattr(self.page, 'open'):
                self.page.open(self.item_dialog)
            else:
                self.page.dialog = self.item_dialog
                self.item_dialog.open = True
                self.page.update()
        except Exception as ex:
            print(f"DEBUG: Error opening modal: {ex}")
        self.page.dialog = self.item_dialog
        self.item_dialog.open = True
        self.page.update()

    def _update_item_field(self, index, field_name, new_value):
        if self.mode == "view":
            return
        if 0 <= index < len(self.items):
            special_fields = {
                "likelihood_label": ("likelihood", self._parse_likelihood),
                "impact_label": ("impact", self._parse_impact),
                "resL_label": ("resL", self._parse_likelihood),
                "resI_label": ("resI", self._parse_impact),
                "effectiveness_label": ("effectiveness", self._parse_likelihood),
            }
            if field_name in special_fields:
                numeric_key, parser = special_fields[field_name]
                parsed = parser(new_value)
                self.items[index][numeric_key] = parsed if parsed is not None else None
                self.items[index][field_name] = self._score_text(parsed)
            else:
                self.items[index][field_name] = new_value
            if hasattr(self, 'page') and self.page:
                self.page.update()
            self._refresh_table_rows()
            self._refresh_items_list()

    def _delete_item(self, index):
        if self.mode == "view":
            return
        if 0 <= index < len(self.items):
            item = self.items[index]
            item_title = item.get("title", "this item")
            
            def confirm_delete(_):
                try:
                    if hasattr(self.page, 'close'):
                        self.page.close(self._delete_confirm_dialog)
                    else:
                        self._delete_confirm_dialog.open = False
                        self.page.update()
                except:
                    pass
                self._execute_delete(index)
            
            def cancel_delete(_):
                try:
                    if hasattr(self.page, 'close'):
                        self.page.close(self._delete_confirm_dialog)
                    else:
                        self._delete_confirm_dialog.open = False
                        self.page.update()
                except:
                    pass
            
            self._delete_confirm_dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text("Confirm Delete"),
                content=ft.Text(f"Are you sure you want to delete '{item_title}'? This action cannot be undone."),
                actions=[
                    ft.TextButton("Cancel", on_click=cancel_delete),
                    ft.TextButton("Delete", on_click=confirm_delete, style=ft.ButtonStyle(color="#ef4444")),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            
            try:
                if hasattr(self.page, 'open'):
                    self.page.open(self._delete_confirm_dialog)
                else:
                    self.page.dialog = self._delete_confirm_dialog
                    self._delete_confirm_dialog.open = True
                    self.page.update()
            except Exception as ex:
                print(f"DEBUG: Error showing delete dialog: {ex}")
                self._execute_delete(index)

    def _execute_delete(self, index):
        if 0 <= index < len(self.items):
            item = self.items[index]
            assessment_id = item.get("ref_id") or item.get("id") or item.get("RiskAssessment_RefID")
            
            if assessment_id and self.reference_id:
                self._enqueue_async_task(self._delete_item_async(index, assessment_id))
            else:
                del self.items[index]
                self._refresh_table_rows()
                self._refresh_items_list()
                if hasattr(self, 'page') and self.page:
                    self.page.update()

    async def _delete_item_async(self, index, assessment_id):
        try:
            result = await self.api_client.delete_risk_assessment(self.reference_id, assessment_id)
            if result:
                if 0 <= index < len(self.items):
                    del self.items[index]
                self._refresh_table_rows()
                self._refresh_items_list()
                self._show_success("Risk assessment deleted successfully")
            else:
                self._show_error("Failed to delete risk assessment from database")
        except Exception as ex:
            del self.items[index]
            self._refresh_table_rows()
            self._refresh_items_list()
            self._show_error(f"Error deleting from server: {str(ex)}. Removed locally.")

    def _clear_all(self, e):
        if self.mode == "view":
            return
        self.title_tf.value = ""
        self.category_dd.value = None
        self.process_tf.value = ""
        self.assessor_tf.value = ""
        self.date_tf.value = ""
        self.status_dd.value = None
        self.approved_by_tf.value = "Pending Approval"
        self._set_date_picker_value(self.date_picker, None)
        self._set_date_picker_value(self.d_due_picker, None)
        self.items = []
        if hasattr(self, 'page') and self.page:
            self.page.update()
        self._refresh_table_rows()
        self._refresh_items_list()

    def _handle_back(self, e):
        print("DEBUG: _handle_back called")
        try:
            if hasattr(self.page, 'APP_INSTANCE') and self.page.APP_INSTANCE:
                app = self.page.APP_INSTANCE
                if hasattr(app, 'show_view'):
                    app.show_view("assessments")
                    return
        except Exception as ex:
            print(f"DEBUG: Error navigating back via APP_INSTANCE: {ex}")
        
        if callable(self.on_cancel_callback):
            self.on_cancel_callback()
        else:
            print("DEBUG: No on_cancel_callback set")
            self._show_error("Cannot navigate back")

    def _enqueue_async_task(self, coro):
        import threading
        
        def run_in_thread():
            try:
                if self.assessment_controller and hasattr(self.assessment_controller, 'api_client'):
                    self.assessment_controller.api_client.session = None
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    loop.run_until_complete(coro)
                finally:
                    try:
                        loop.run_until_complete(loop.shutdown_asyncgens())
                    except:
                        pass
                    loop.close()
            except Exception as ex:
                print(f"DEBUG: Error in async thread: {ex}")
                import traceback
                traceback.print_exc()
                try:
                    self._show_error(f"Operation failed: {ex}")
                except:
                    pass
        
        thread = threading.Thread(target=run_in_thread, daemon=True)
        thread.start()

    def _handle_save(self, e):
        print("DEBUG: _handle_save called")
        if self.mode == "view":
            self._show_error("Cannot save in view mode")
            return
        if not self.title_tf.value:
            self._show_error("Assessment Name is required")
            return
        if not self.items:
            self._show_error("No risk items to save. Add at least one risk item.")
            return
        if self.selected_item_index is not None:
            self._update_selected_item()
        self._enqueue_async_task(self._save_async(scope="all"))

    def _handle_save_selected_risk(self, e=None):
        if self.mode == "view":
            return
        if self.selected_item_index is None or self.selected_item_index >= len(self.items):
            self._show_error("Select a risk to save")
            return
        self._update_selected_item()
        self._enqueue_async_task(self._save_async(scope="risk", items_override=[self.items[self.selected_item_index]]))

    def _build_create_payload(self, items, reference_id=None):
        item_payloads = []
        for it in items:
            likelihood_id = self._parse_likelihood(it.get("likelihood") or it.get("likelihood_label"))
            impact_id = self._parse_impact(it.get("impact") or it.get("impact_label"))
            residual_likelihood_id = self._parse_likelihood(it.get("resL") or it.get("resL_label"))
            residual_impact_id = self._parse_impact(it.get("resI") or it.get("resI_label"))
            risk_category_id = self._resolve_lookup_id(self._category_items_raw, it.get("riskCategory") or it.get("category"))
            data_frequency_id = self._resolve_lookup_id(self._data_freq_items_raw, it.get("data_frequency") or it.get("frequency"))
            frequency_id = self._resolve_lookup_id(self._data_freq_items_raw, it.get("frequency") or it.get("data_frequency"))
            evidence_id = self._resolve_lookup_id(self._evidence_items_raw, it.get("evidence"))

            item_payloads.append({
                "BusinessObjectives": it.get("desc"),
                "MainProcess": self.process_tf.value,
                "SubProcess": it.get("sub_process"),
                "KeyRiskAndFactors": it.get("title"),
                "MitigatingControls": it.get("controls"),
                "Responsibility": it.get("owner"),
                "Authoriser": it.get("authoriser"),
                "AuditorsRecommendedActionPlan": it.get("notes"),
                "ResponsiblePerson": it.get("responsible"),
                "AgreedDate": self._parse_date_input(it.get("due")),
                "RiskLikelihoodId": likelihood_id,
                "RiskImpactId": impact_id,
                "KeySecondaryId": None,
                "RiskCategoryId": risk_category_id,
                "DataFrequencyId": data_frequency_id,
                "FrequencyId": frequency_id,
                "EvidenceId": evidence_id,
                "OutcomeLikelihoodId": residual_likelihood_id,
                "ImpactId": residual_impact_id
            })

        if not item_payloads:
            item_payloads = [{
                "BusinessObjectives": "",
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
                "RiskCategoryId": self._resolve_lookup_id(self._category_items_raw, self.category_dd.value),
                "DataFrequencyId": None,
                "FrequencyId": None,
                "EvidenceId": None,
                "OutcomeLikelihoodId": None,
                "ImpactId": None
            }]

        payload = {"Assessments": item_payloads}

        if reference_id:
            payload["ReferenceId"] = reference_id
        else:
            payload["Reference"] = {
                "Client": self.process_tf.value or "",
                "AssessmentStartDate": self._parse_date_input(self.date_tf.value) or None,
                "AssessmentEndDate": None,
                "Assessor": self.assessor_tf.value or (self.user.get("username") if isinstance(self.user, dict) else None),
                "ApprovedBy": None,
                "Title": self.title_tf.value,
                "Status": self.status_dd.value or "Draft",
                "Overview": "",
                "Comments": ""
            }

        return payload

    def _build_update_requests(self, items):
        update_requests = []
        for item in items:
            ref_id = item.get("ref_id") or item.get("id")
            if not ref_id:
                continue

            update_payload = {
                "RiskAssessmentRefId": ref_id,
                "BusinessObjectives": item.get("desc", ""),
                "MainProcess": self.process_tf.value or "",
                "SubProcess": item.get("sub_process", ""),
                "KeyRiskAndFactors": item.get("title", ""),
                "MitigatingControls": item.get("controls", ""),
                "Responsibility": item.get("owner", ""),
                "Authoriser": item.get("authoriser", ""),
                "AuditorsRecommendedActionPlan": item.get("notes", ""),
                "ResponsiblePerson": item.get("responsible", ""),
                "AgreedDate": self._parse_date_input(item.get("due"))
            }

            likelihood_id = self._parse_likelihood(item.get("likelihood") or item.get("likelihood_label"))
            impact_id = self._parse_impact(item.get("impact") or item.get("impact_label"))
            residual_likelihood_id = self._parse_likelihood(item.get("resL") or item.get("resL_label"))
            residual_impact_id = self._parse_impact(item.get("resI") or item.get("resI_label"))
            risk_category_id = self._resolve_lookup_id(self._category_items_raw, item.get("riskCategory") or item.get("category"))
            data_frequency_id = self._resolve_lookup_id(self._data_freq_items_raw, item.get("data_frequency") or item.get("frequency"))
            frequency_id = self._resolve_lookup_id(self._data_freq_items_raw, item.get("frequency") or item.get("data_frequency"))
            evidence_id = self._resolve_lookup_id(self._evidence_items_raw, item.get("evidence"))

            if likelihood_id is not None:
                update_payload["RiskLikelihoodId"] = likelihood_id
            if impact_id is not None:
                update_payload["RiskImpactId"] = impact_id
            if residual_likelihood_id is not None:
                update_payload["OutcomeLikelihoodId"] = residual_likelihood_id
            if residual_impact_id is not None:
                update_payload["ImpactId"] = residual_impact_id
            if risk_category_id is not None:
                update_payload["RiskCategoryId"] = risk_category_id
            if data_frequency_id is not None:
                update_payload["DataFrequencyId"] = data_frequency_id
            if frequency_id is not None:
                update_payload["FrequencyId"] = frequency_id
            if evidence_id is not None:
                update_payload["EvidenceId"] = evidence_id

            update_requests.append(update_payload)
        return update_requests

    async def _save_async(self, scope="all", items_override=None):
        try:
            print(f"DEBUG: _save_async started, scope={scope}, mode={self.mode}, reference_id={self.reference_id}")
            items_to_use = items_override if items_override is not None else list(self.items)
            print(f"DEBUG: Items to save: {len(items_to_use)}")

            result = None
            reference_updated = False
            reference_error = None
            
            if self.mode == "edit" and self.reference_id:
                # Update the reference header (Assessor, Title, etc.)
                # ApprovedBy is read-only - pass existing value or empty string
                approved_by_value = self.approved_by_tf.value if self.approved_by_tf.value != "Pending Approval" else ""
                reference_data = {
                    "Client": self.process_tf.value or "",
                    "AssessmentStartDate": self._parse_date_input(self.date_tf.value),
                    "AssessmentEndDate": self._parse_date_input(self.date_tf.value),
                    "Assessor": self.assessor_tf.value or "",
                    "ApprovedBy": approved_by_value
                }
                print(f"DEBUG: Updating reference with data: {reference_data}")
                try:
                    ref_result = await self.api_client.update_reference(self.reference_id, reference_data)
                    print(f"DEBUG: Reference update result: {ref_result}")
                    reference_updated = True
                except Exception as ref_err:
                    print(f"DEBUG: Reference update error: {ref_err}")
                    reference_error = str(ref_err)
                
                # Update the risk items
                existing_items = [it for it in items_to_use if it.get("ref_id") or it.get("id") or it.get("RiskAssessment_RefID")]
                new_items = [it for it in items_to_use if not (it.get("ref_id") or it.get("id") or it.get("RiskAssessment_RefID"))]
                print(f"DEBUG: Existing items: {len(existing_items)}, New items: {len(new_items)}")

                if existing_items:
                    update_requests = self._build_update_requests(existing_items)
                    print(f"DEBUG: Update requests built: {len(update_requests)}")
                    if update_requests:
                        result = await self.assessment_controller.update_risk_assessment(self.reference_id, update_requests)
                        print(f"DEBUG: Update result: {result}")

                if new_items:
                    create_payload = self._build_create_payload(new_items, reference_id=self.reference_id)
                    create_result = await self.assessment_controller.create_risk_assessment(create_payload)
                    result = create_result or result
                
                # If no items were updated/created but reference was updated, consider it a success
                if result is None and reference_data:
                    result = {"success": True, "message": "Reference updated"}
            else:
                payload = self._build_create_payload(items_to_use)
                result = await self.assessment_controller.create_risk_assessment(payload)
            
            if result:
                # Build appropriate message based on what succeeded/failed
                if reference_error and self.mode == "edit":
                    # Risk items saved but reference (Assessor, etc.) failed
                    self._show_error(f"Risk items saved, but header fields (Assessor, Date) failed to save: {reference_error}")
                    print(f"DEBUG: Partial save - items OK, reference FAILED: {reference_error}")
                else:
                    success_message = "Assessment saved successfully!" if scope == "all" else "Risk item saved successfully!"
                    print(f"DEBUG: Save successful - {success_message}")
                self._show_success(success_message)
                
                if self.mode == "edit" and self.reference_id:
                    try:
                        await self._load_risk_assessments_async(self.reference_id)
                    except Exception as refresh_err:
                        print(f"DEBUG: Unable to refresh assessment data: {refresh_err}")
                if callable(self.on_save_callback):
                    self.on_save_callback(result)
            elif reference_updated and not result:
                # Only reference was updated (no risk items changed)
                self._show_success("Assessment header updated successfully!")
                print("DEBUG: Reference updated, no risk items to update")
                if callable(self.on_save_callback):
                    self.on_save_callback({"success": True, "referenceId": self.reference_id})
            elif reference_error and not result:
                # Everything failed
                self._show_error(f"Failed to save: {reference_error}")
                print(f"DEBUG: Save failed completely: {reference_error}")
            else:
                print("DEBUG: Save failed - no result returned")
                self._show_error("Failed to save assessment - no response from server")
        except Exception as e:
            print(f"DEBUG: Save error: {e}")
            import traceback
            traceback.print_exc()
            self._show_error(f"Save failed: {e}")

    def _show_loading(self, message):
        self.page.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Processing"),
            content=ft.Column([
                ft.ProgressRing(),
                ft.Text(message)
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, height=100)
        )
        self.page.dialog.open = True
        self.page.update()

    def _hide_loading(self):
        if self.page.dialog:
            self.page.dialog.open = False
            self.page.update()

    def _show_success(self, message):
        print(f"DEBUG: _show_success called with message: {message}")
        try:
            snack = ft.SnackBar(
                content=ft.Text(message, color="white", weight=ft.FontWeight.W_500), 
                bgcolor="#10b981",
                duration=3000,
                open=True
            )
            self.page.overlay.append(snack)
            self.page.update()
            print("DEBUG: Success snackbar should be visible now")
        except Exception as e:
            print(f"DEBUG: Error showing success snackbar: {e}")

    def _show_error(self, message):
        print(f"DEBUG: _show_error called with message: {message}")
        try:
            snack = ft.SnackBar(
                content=ft.Text(message, color="white", weight=ft.FontWeight.W_500), 
                bgcolor="#ef4444",
                duration=5000,
                open=True
            )
            self.page.overlay.append(snack)
            self.page.update()
            print("DEBUG: Error snackbar should be visible now")
        except Exception as e:
            print(f"DEBUG: Error showing error snackbar: {e}")

    def _show_export_options(self, e):
        print("DEBUG: _show_export_options called")
        
        def close_dlg(e):
            print("DEBUG: Export dialog canceled")
            self.page.close(self.export_dialog)

        def export(fmt):
            self.page.close(self.export_dialog)
            self._handle_export(fmt)

        self.export_dialog = ft.AlertDialog(
            title=ft.Text("Export Report"),
            content=ft.Column([
                ft.ListTile(leading=ft.Icon(Icons.TABLE_CHART), title=ft.Text("CSV"), on_click=lambda e: export("csv")),
                ft.ListTile(leading=ft.Icon(Icons.GRID_ON), title=ft.Text("Excel"), on_click=lambda e: export("excel")),
                ft.ListTile(leading=ft.Icon(Icons.PICTURE_AS_PDF), title=ft.Text("PDF"), on_click=lambda e: export("pdf")),
            ], height=180, width=300, spacing=0),
            actions=[ft.TextButton("Cancel", on_click=close_dlg)],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.open(self.export_dialog)

    def _handle_export(self, format_type):
        print(f"DEBUG: _handle_export called with format {format_type}")
        self._show_success(f"Generating {format_type.upper()} export...")
        
        try:
            data = self._prepare_export_data()
            headers = {
                "title": "Title",
                "category_display": "Category",
                "process": "Process",
                "likelihood": "Likelihood",
                "impact": "Impact",
                "inherent": "Inherent",
                "resL": "Residual L",
                "resI": "Residual I",
                "residual": "Residual Score",
                "owner": "Owner",
                "due": "Due",
                "evidence": "Evidence"
            }
            
            # Gather assessment header metadata
            assessment_info = {
                "Assessment Name": self.title_tf.value or "",
                "Category": self.category_dd.value if hasattr(self, 'category_dd') and self.category_dd else "",
                "Process / Area": self.process_tf.value if hasattr(self, 'process_tf') and self.process_tf else "",
                "Assessor": self.assessor_tf.value if hasattr(self, 'assessor_tf') and self.assessor_tf else "",
                "Date": self.date_tf.value if hasattr(self, 'date_tf') and self.date_tf else "",
                "Status": self.status_dd.value if hasattr(self, 'status_dd') and self.status_dd else "",
                "Approved By": self.approved_by_tf.value if hasattr(self, 'approved_by_tf') and self.approved_by_tf else "Pending Approval",
            }
            
            exporter = ExportManager()
            result = None
            title = self.title_tf.value or "Risk Assessment"
            
            if format_type == "csv":
                result = exporter.export_csv(data, headers, "risk_assessment", metadata=assessment_info)
            elif format_type == "excel":
                result = exporter.export_excel(data, headers, title, "risk_assessment", metadata=assessment_info)
            elif format_type == "pdf":
                result = exporter.export_pdf(data, headers, title, "risk_assessment", metadata=assessment_info)
                
            if result:
                self.page.launch_url(result["data_uri"])
                self._show_success("Download started")
                
        except Exception as e:
            print(f"Export failed: {e}")
            import traceback
            traceback.print_exc()
            self._show_error(f"Export failed: {str(e)}")

    def _prepare_export_data(self):
        query = (self.filter_tf.value or "").strip()
        raw_data = [self._normalize_risk_item(it) for it in (self.items or [])]
        filtered = [it for it in raw_data if self._filter_match(it, query)]
        try:
            filtered.sort(key=lambda it: self._sort_key_tuple(it), reverse=not self._sort_asc)
        except: pass
        
        export_data = []
        for it in filtered:
            row = it.copy()
            row["inherent"] = self._inherent_of(it) or ""
            row["residual"] = self._residual_of(it) or ""
            row["category_display"] = it.get("riskCategory") or it.get("category") or ""
            row["likelihood"] = str(it.get("likelihood") or "")
            row["impact"] = str(it.get("impact") or "")
            row["resL"] = str(it.get("resL") or "")
            row["resI"] = str(it.get("resI") or "")
            export_data.append(row)
        return export_data
