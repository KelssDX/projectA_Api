import flet as ft
from flet import Icons, Colors
import asyncio
import json
import csv
import os
from src.utils.theme import get_theme_colors, create_modern_card
from src.utils.permissions import can_import_analytics
from src.views.common.base_view import BaseView
from src.controllers.assessment_controller import AssessmentController
from src.core.config import POWER_BI_CONFIG

# Widget Imports
from src.views.widgets.risk_charts_widget import (
    InherentVsResidualWidget, 
    RiskCategoryDistributionWidget, 
    ControlCoverageWidget
)
from src.views.widgets.top_risks_widget import TopRisksWidget
from src.views.widgets.market_risk_widget import MarketRiskWidget
from src.views.widgets.base_widget import BaseWidget

# Phase 6 Analytics Widgets
from src.views.widgets.findings_aging_widget import FindingsAgingWidget
from src.views.widgets.audit_coverage_widget import AuditCoverageWidget
from src.views.widgets.risk_trend_widget import RiskTrendWidget
from src.views.widgets.risk_velocity_widget import RiskVelocityWidget
from src.views.widgets.department_comparison_widget import DepartmentComparisonWidget
from src.views.widgets.control_effectiveness_widget import ControlEffectivenessWidget
from src.views.widgets.heatmap_embed_widget import HeatmapEmbedWidget
from src.views.widgets.compliance_scorecard_widget import ComplianceScorecardWidget
from src.views.widgets.management_override_widget import ManagementOverrideAnalyticsWidget
from src.views.widgets.journal_exception_widget import JournalExceptionAnalyticsWidget
from src.views.widgets.user_posting_concentration_widget import UserPostingConcentrationWidget
from src.views.widgets.trial_balance_movement_widget import TrialBalanceMovementWidget
from src.views.widgets.industry_benchmark_widget import IndustryBenchmarkWidget
from src.views.widgets.reasonability_forecast_widget import ReasonabilityForecastWidget
from src.views.widgets.power_bi_reconciliation_widget import PowerBIReconciliationWidget

from src.views.components.drill_down_panel import DrillDownPanel
from src.views.components.hierarchy_selector import HierarchySelector


class AnalyticalDashboard(BaseView):
    def __init__(self, page, user, on_navigate=None, platform_config=None):
        self.platform_config = platform_config or {}
        self.feature_flags = self._normalize_feature_flags(self.platform_config.get("featureFlags"))
        self.power_bi_config = self._resolve_power_bi_config()
        self.assessment_controller = AssessmentController(user)
        
        actions = []
        if can_import_analytics(user) and self._feature_enabled("analytics_import", True):
            actions.append(ft.FilledTonalButton("Import Analytics", icon=Icons.UPLOAD_FILE, on_click=self._open_analytics_import_dialog))
        actions.extend([
            ft.OutlinedButton("Customize Layout", icon=Icons.DASHBOARD_CUSTOMIZE, on_click=self._open_customize_dialog),
            ft.FilledButton("Export Report", icon=Icons.PICTURE_AS_PDF, on_click=self._export_report)
        ])
        
        super().__init__(page, "Analytical Suite", actions=actions)
        self.user = user
        self.on_navigate = on_navigate
        self.colors = get_theme_colors(page.theme_mode)

        # Widget Registry (Mapping IDs to Classes)
        self.widget_registry = {
            # Original Widgets
            "market_risk": {"class": MarketRiskWidget, "title": "Market Risk Analysis", "default": True},
            "inherent_residual": {"class": InherentVsResidualWidget, "title": "Inherent vs Residual Risk", "default": True},
            "top_risks": {"class": TopRisksWidget, "title": "Top 10 Residual Risks", "default": True},
            "risk_categories": {"class": RiskCategoryDistributionWidget, "title": "Risk Category Distribution", "default": True},
            "control_coverage": {"class": ControlCoverageWidget, "title": "Control Coverage", "default": True},
            
            # Phase 6 Analytics Widgets
            "findings_aging": {"class": FindingsAgingWidget, "title": "Open Findings Aging", "default": False},
            "audit_map": {"class": AuditCoverageWidget, "title": "Audit Coverage Map", "default": True},
            "risk_trend": {"class": RiskTrendWidget, "title": "Risk Trend Analysis", "default": False},
            "risk_velocity": {"class": RiskVelocityWidget, "title": "Risk Velocity Meter", "default": False},
            "dept_comparison": {"class": DepartmentComparisonWidget, "title": "Department Risk Comparison", "default": False},
            "control_effectiveness": {"class": ControlEffectivenessWidget, "title": "Control Effectiveness Dashboard", "default": False},
            "heatmap_embed": {"class": HeatmapEmbedWidget, "title": "Embedded Risk Heatmap", "default": True},
            "compliance_scorecard": {"class": ComplianceScorecardWidget, "title": "Compliance Scorecard", "default": False},
            "management_override": {"class": ManagementOverrideAnalyticsWidget, "title": "Management Override Indicators", "default": False},
            "journal_exceptions": {"class": JournalExceptionAnalyticsWidget, "title": "Journal Exception Analytics", "default": False},
            "user_posting_concentration": {"class": UserPostingConcentrationWidget, "title": "User Posting Concentration", "default": False},
            "tb_movement": {"class": TrialBalanceMovementWidget, "title": "Trial Balance Movement", "default": False},
            "industry_benchmark": {"class": IndustryBenchmarkWidget, "title": "Industry Benchmark Analytics", "default": False},
            "reasonability_forecast": {"class": ReasonabilityForecastWidget, "title": "Reasonability and Forecast Analytics", "default": False},
            "power_bi_reconciliation": {"class": PowerBIReconciliationWidget, "title": "Power BI Reconciliation", "default": False},
        }
        if not self._feature_enabled("power_bi_reporting", True):
            self.widget_registry.pop("power_bi_reconciliation", None)
        
        # State: List of active widget IDs
        self.active_widget_ids = [k for k, v in self.widget_registry.items() if v["default"]]
        self.active_instances = {} # Map ID -> Instance
        self.selected_ref_id = None  # No default - user must select
        self.selected_audit_universe_id = None
        self.selected_audit_universe_node = None
        self.grid_columns = 12 # Density setting
        self.layout_mode = "grid" # grid, horizontal, vertical, equal, sidebar_left, sidebar_right, featured_top, featured_bottom, quad
        self.favorite_layouts = [] # List of {name, layout_mode, grid_columns, active_ids}
        self.report_mode = "native"
        self.power_bi_reconciliation_data = None
        self.power_bi_reconciliation_loading = False
        self.power_bi_reconciliation_ref_id = None
        self.analytics_import_file_picker = None
        self.pending_analytics_import_file = None
        self.analytics_import_validation = None
        self.analytics_import_batches = []
        self.analytics_import_dialog = None
        
        # Drill down panel (hidden by default)
        self.drill_down_panel = DrillDownPanel(page, on_close=self._close_drill_down, on_navigate=self._handle_panel_navigation)
        self.drill_down_container = None
        
        print(f"DEBUG: [AnalyticalDashboard] Initializing Dashboard (ID: {id(self)})")
        self._build_ui()
        print(f"DEBUG: [AnalyticalDashboard] UI Built. load_data() will be called by view manager.")

    @staticmethod
    def _normalize_feature_flags(flags):
        if not isinstance(flags, dict):
            return {}
        normalized = {}
        for key, value in flags.items():
            normalized_key = "".join(ch if ch.isalnum() else "_" for ch in str(key)).strip("_").lower()
            normalized[normalized_key] = bool(value)
        return normalized

    def _feature_enabled(self, flag_name, default=True):
        return self.feature_flags.get(flag_name, default)

    def _resolve_power_bi_config(self):
        config = dict(POWER_BI_CONFIG)
        server_config = self.platform_config.get("powerBI") if isinstance(self.platform_config, dict) else None
        if isinstance(server_config, dict):
            config.update({
                "enabled": server_config.get("enabled", config.get("enabled")),
                "mode": server_config.get("mode", config.get("mode")),
                "report_url": server_config.get("reportUrl", config.get("report_url", "")),
                "workspace_id": server_config.get("workspaceId", config.get("workspace_id", "")),
                "report_id": server_config.get("reportId", config.get("report_id", "")),
                "dataset_id": server_config.get("datasetId", config.get("dataset_id", "")),
            })
        if not self._feature_enabled("power_bi_reporting", True):
            config["enabled"] = False
        return config

    def _build_ui(self):
        self._ensure_analytics_import_picker()

        # Assessment Selector
        self.assessment_selector = ft.Dropdown(
            label="Assessment Context",
            hint_text="Select Assessment...",
            options=[], 
            text_size=12,
            width=250,
            bgcolor=ft.Colors.SURFACE,
            border_color=self.colors.primary,
            on_change=self._on_context_change
        )
        
        self.refresh_button = ft.IconButton(
            icon=ft.Icons.REFRESH,
            icon_size=18,
            tooltip="Reload Assessments",
            on_click=lambda _: self.load_data()
        )

        self.report_mode_selector = ft.Dropdown(
            label="Report Mode",
            value="native",
            width=180,
            text_size=12,
            options=(
                [
                    ft.dropdown.Option(key="native", text="Native Dashboard"),
                    ft.dropdown.Option(key="power_bi", text="Microsoft Power BI"),
                ] if self._feature_enabled("power_bi_reporting", True) else [
                    ft.dropdown.Option(key="native", text="Native Dashboard"),
                ]
            ),
            on_change=self._on_report_mode_change
        )

        self.power_bi_button = ft.FilledTonalButton(
            "Open Power BI",
            icon=Icons.OPEN_IN_NEW,
            visible=False,
            on_click=self._open_power_bi_report
        )

        # Audit Universe selector
        self.hierarchy_selector = HierarchySelector(
            self.page,
            on_selection_change=self._on_hierarchy_change
        )
        
        # Favorites Chips
        self.favorites_row = ft.Row(spacing=10, scroll=ft.ScrollMode.AUTO)

        # Main Grid/Column
        self.dashboard_container = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO)
        self.dashboard_grid = ft.ResponsiveRow(run_spacing=20, spacing=20)
        self.dashboard_container.controls = [self.dashboard_grid]
        self.power_bi_panel = self._build_power_bi_panel()
        
        # Main Layout including drill-down panel as an overlay or side panel
        # Using a Stack to allow drill-down panel to slide in/appear
        self.main_stack = ft.Stack([
            ft.Column([
                ft.Row([
                    ft.Column([
                        self.favorites_row
                    ], spacing=5, expand=True),
                    ft.Row([
                        self.assessment_selector,
                        self.report_mode_selector,
                        self.hierarchy_selector,
                        self.refresh_button,
                        self.power_bi_button
                    ], spacing=8)
                ], alignment=ft.MainAxisAlignment.END, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Container(content=self.dashboard_container, padding=ft.padding.only(bottom=50), expand=True)
            ], expand=True),
            
            # Drill down panel container (positioned absolute right)
            self._build_drill_down_container()
        ], expand=True)

        self.cards_column.controls.clear()
        self.add_card(self.main_stack)

    def load_data(self):
        self.page.run_task(self._load_data_async)
        try:
            if self.hierarchy_selector:
                self.hierarchy_selector.load_hierarchy()
        except Exception:
            pass

    async def _load_data_async(self):
        # Load favorites from storage
        try:
            stored = await self.page.client_storage.get_async("favorite_layouts")
            if stored:
                import json
                self.favorite_layouts = json.loads(stored)
                self._update_favorites_ui()
        except Exception as e:
            print(f"Error loading favorites: {e}")

        # Fetch real assessments for the dropdown
        try:
            print(f"DEBUG: [AnalyticalDashboard] ID: {id(self)} fetching assessments via API client...")
            self.assessment_selector.hint_text = "Loading assessments..."
            if self.page: self.page.update()
            
            assessments = await self.assessment_controller.auditing_client.get_assessments()
            print(f"DEBUG: [AnalyticalDashboard] ID: {id(self)} found {len(assessments) if assessments else 0} assessments.")
            
            if assessments:
                options = [
                    ft.dropdown.Option(
                        key=str(a.get("reference_id")), 
                        text=a.get("title") if a.get("title") else f"Assessment Ref #{a.get('reference_id')}"
                    ) for a in assessments
                ]
                print(f"DEBUG: [AnalyticalDashboard] Setting {len(options)} options to selector (ID: {id(self.assessment_selector)})")
                
                # Safer way to update options in Flet async
                self.assessment_selector.options.clear()
                self.assessment_selector.options.extend(options)
                
                print(f"DEBUG: [AnalyticalDashboard] ID: {id(self)} Options list verified:")
                for i, opt in enumerate(self.assessment_selector.options):
                    print(f"  - [{i}] Key: {opt.key}, Text: '{opt.text}'")
                
                self.assessment_selector.hint_text = "Select Assessment Context..."
                self.assessment_selector.value = None
                self.selected_ref_id = None
                
                # Explicitly update the control and its parent
                if self.assessment_selector.page:
                    print(f"DEBUG: [AnalyticalDashboard] ID: {id(self)} Selector is MOUNTED, calling updates.")
                    self.assessment_selector.update()
                    if hasattr(self, 'main_stack') and self.main_stack.page:
                        self.main_stack.update()
                else:
                    print(f"DEBUG: [AnalyticalDashboard] ID: {id(self)} Selector NOT MOUNTED yet.")
            else:
                print(f"DEBUG: [AnalyticalDashboard] No assessments found to populate dropdown.")
                self.assessment_selector.options.clear()
                self.assessment_selector.options.append(ft.dropdown.Option("0", "No Assessments Found"))
                self.assessment_selector.hint_text = "No assessments available"
                self.assessment_selector.value = "0"
            
            # Final page update to be sure
            if self.page:
                print(f"DEBUG: [AnalyticalDashboard] Calling page.update() (Page ID: {id(self.page)})")
                self.page.update()
                
        except Exception as e:
            print(f"Error loading assessments: {e}")
            import traceback
            traceback.print_exc()
            self.assessment_selector.options = [ft.dropdown.Option("0", "Error Loading Data")]
            self.assessment_selector.value = "0"
            if self.page:
                self.page.update()
            
        self._refresh_dashboard()

    def _refresh_dashboard(self):
        if self.report_mode == "power_bi":
            self.dashboard_container.controls = [self.power_bi_panel]
            self._sync_power_bi_ui()
            self.page.update()
            return

        self.dashboard_grid.controls.clear()
        self.dashboard_container.controls = [self.dashboard_grid]
        self.active_instances = {}
        
        # Layout metrics
        units = 4
        if self.grid_columns == 6: units = 6
        elif self.grid_columns == 4: units = 12
        elif self.grid_columns == 16: units = 3
        
        instances = []
        # Re-instantiate active widgets
        for wid in self.active_widget_ids:
            config = self.widget_registry.get(wid)
            if not config or not config["class"]: continue
            
            w_class = config["class"]
            widget = None
            
            # Determine instantiation based on widget type
            try:
                if issubclass(w_class, BaseWidget):
                    # New Phase 6 widgets
                    widget = w_class(
                        page=self.page, 
                        reference_id=self.selected_ref_id,
                        audit_universe_id=self.selected_audit_universe_id,
                        on_drill_down=self._handle_drill_down
                    )
                    # Special cases for extra params
                    if wid == "heatmap_embed":
                        widget.set_compact_mode(True)
                else:
                    # Old widgets
                    widget = w_class(self.page, self.assessment_controller.auditing_client, self.selected_ref_id)
            except Exception as e:
                print(f"Error instantiating widget {wid}: {e}")
                continue
            
            # Common properties for old widgets (BaseAnalyticsWidget)
            if hasattr(widget, 'on_maximize_requested'):
                widget.on_maximize_requested = self._handle_maximize
            if hasattr(widget, 'on_close_requested'):
                widget.on_close_requested = self._handle_close_widget
                
            widget.data = wid
            
            self.active_instances[wid] = widget
            instances.append(widget)

        if not instances:
            self.dashboard_grid.controls.append(ft.Text("No widgets selected. Click 'Customize Layout' to add some.", italic=True))
            self.page.update()
            return

        # APPLY COMPLEX MODES
        if self.layout_mode == "grid":
            for widget in instances:
                if hasattr(widget, 'is_wide') and widget.is_wide:
                    widget.col = {"sm": 12, "xl": 12 if units == 12 else units * 2 if units <= 6 else 12}
                else:
                    widget.col = {"sm": 12, "md": 6, "xl": units}
                if widget.data == "top_risks": widget.col = {"sm": 12}
                self.dashboard_grid.controls.append(widget)

        elif self.layout_mode == "vertical":
            for widget in instances:
                widget.col = {"sm": 12}
                self.dashboard_grid.controls.append(widget)

        elif self.layout_mode == "horizontal":
            for widget in instances:
                widget.width = 400
                widget.col = None
                widget.load_data() # Load data for horizontal widgets
            self.dashboard_container.controls = [ft.Row(instances, scroll=ft.ScrollMode.AUTO, spacing=20)]

        elif self.layout_mode == "equal":
            row = ft.Row(expand=True, spacing=20)
            for w in instances:
                # Widgets handle their own load_data in their constructor or via load_data()
                # To avoid redundant calls, we just call load_data() once here for the new instances
                w.load_data()
                w.expand = True
                row.controls.append(w)
            self.dashboard_container.controls = [row]

        elif self.layout_mode in ["sidebar_left", "sidebar_right"]:
            featured = instances[0]
            secondary = instances[1:]
            featured.expand = True
            
            sidebar_col = ft.Column([ft.Container(w, height=300) for w in secondary], scroll=ft.ScrollMode.AUTO, expand=True)
            
            main_row = ft.Row([
                ft.Container(featured, expand=3 if self.layout_mode == "sidebar_left" else 1),
                ft.Container(sidebar_col, expand=1 if self.layout_mode == "sidebar_left" else 3)
            ], expand=True, spacing=20)
            
            if self.layout_mode == "sidebar_right":
                main_row.controls = [ft.Container(sidebar_col, expand=1), ft.Container(featured, expand=3)]
            
            self.dashboard_container.controls = [main_row]

        elif self.layout_mode in ["featured_top", "featured_bottom"]:
            featured = instances[0]
            secondary = instances[1:]
            featured.col = {"sm": 12}
            
            sec_grid = ft.ResponsiveRow(spacing=20, run_spacing=20)
            for w in secondary:
                w.col = {"sm": 12, "md": 6, "xl": 4}
                sec_grid.controls.append(w)
            
            children = [featured, ft.Container(sec_grid, padding=ft.padding.only(top=20))]
            if self.layout_mode == "featured_bottom":
                children.reverse()
            
            self.dashboard_container.controls = [ft.Column(children, scroll=ft.ScrollMode.AUTO)]

        elif self.layout_mode == "quad":
            grid = ft.ResponsiveRow(spacing=20, run_spacing=20)
            for i, w in enumerate(instances[:4]):
                w.col = {"sm": 12, "md": 6}
                grid.controls.append(w)
            self.dashboard_container.controls = [grid]

        self.page.update()
        for widget in instances:
            widget.load_data()

    def _sync_power_bi_ui(self):
        enabled = bool(self.power_bi_config.get("enabled")) and bool(self._build_power_bi_url())
        self.power_bi_button.visible = self.report_mode == "power_bi" and enabled

        if enabled:
            status = "Power BI is available for this Analytical Report."
            detail = "Use the button to open the Microsoft Power BI report with the current analytical context."
            badge_text = "Configured"
            badge_color = ft.Colors.GREEN_100
        else:
            status = "Power BI is not configured yet."
            detail = "Set the auditing API `PowerBI` environment configuration and refresh the client."
            badge_text = "Not Configured"
            badge_color = ft.Colors.ORANGE_100

        self.power_bi_status_text.value = status
        self.power_bi_detail_text.value = detail
        self.power_bi_url_text.value = self._build_power_bi_url() or "No Power BI report URL configured"
        self.power_bi_context_text.value = (
            f"Reference ID: {self.selected_ref_id} | Audit Universe ID: {self.selected_audit_universe_id or 'not selected'}"
            if self.selected_ref_id else "Reference ID: not selected"
        )
        self.power_bi_badge.content.value = badge_text
        self.power_bi_badge.bgcolor = badge_color
        self._update_power_bi_reconciliation_ui()

        if (
            self.selected_ref_id
            and self.selected_ref_id != self.power_bi_reconciliation_ref_id
            and not self.power_bi_reconciliation_loading
        ):
            self.power_bi_reconciliation_loading = True
            self.page.run_task(self._load_power_bi_reconciliation_async)

        if self.page:
            self.page.update()

    def _build_power_bi_panel(self):
        self.power_bi_status_text = ft.Text(
            "Power BI is not configured yet.",
            size=18,
            weight=ft.FontWeight.W_600
        )
        self.power_bi_detail_text = ft.Text(
            "Set the auditing API `PowerBI` environment configuration to enable Microsoft Power BI for analytical reporting.",
            size=13,
            color=ft.Colors.GREY_700
        )
        self.power_bi_url_text = ft.Text(
            "No Power BI report URL configured",
            size=12,
            selectable=True,
            color=self.colors.primary
        )
        self.power_bi_context_text = ft.Text(
            "Reference ID: not selected",
            size=12
        )
        self.power_bi_badge = ft.Container(
            content=ft.Text("Not Configured", size=11, weight=ft.FontWeight.W_600),
            bgcolor=ft.Colors.ORANGE_100,
            border_radius=999,
            padding=ft.padding.symmetric(horizontal=10, vertical=6)
        )
        self.power_bi_reconciliation_section = ft.Container(
            content=ft.Column([
                ft.Text("Reporting Reconciliation", size=12, weight=ft.FontWeight.W_600),
                ft.Text(
                    "Select an assessment to compare native analytics with reporting-layer values.",
                    size=12,
                    color=ft.Colors.GREY_700
                )
            ], spacing=8),
            bgcolor=ft.Colors.SURFACE,
            border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
            border_radius=10,
            padding=12
        )

        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(Icons.ANALYTICS, size=24, color=self.colors.primary),
                    ft.Text("Microsoft Power BI", size=22, weight=ft.FontWeight.W_700),
                    self.power_bi_badge
                ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                self.power_bi_status_text,
                self.power_bi_detail_text,
                ft.Container(
                    content=ft.Column([
                        ft.Text("Assessment Context", size=12, weight=ft.FontWeight.W_600),
                        self.power_bi_context_text
                    ], spacing=4),
                    bgcolor=self.colors.hover_bg,
                    border_radius=10,
                    padding=12
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Text("Power BI URL", size=12, weight=ft.FontWeight.W_600),
                        self.power_bi_url_text
                    ], spacing=6),
                    bgcolor=ft.Colors.SURFACE,
                    border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
                    border_radius=10,
                    padding=12
                ),
                self.power_bi_reconciliation_section,
                ft.Row([
                    ft.FilledButton("Open Microsoft Power BI", icon=Icons.OPEN_IN_BROWSER, on_click=self._open_power_bi_report),
                    ft.OutlinedButton("Use Native Dashboard", icon=Icons.DASHBOARD, on_click=lambda _: self._set_report_mode("native"))
                ], spacing=10),
                ft.Text(
                    "Current implementation opens the Power BI report in the browser. The native widget dashboard remains available in this view.",
                    size=12,
                    color=ft.Colors.GREY_700
                )
            ], spacing=16),
            padding=20,
            border_radius=16,
            bgcolor=ft.Colors.WHITE,
            border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT)
        )

    async def _load_power_bi_reconciliation_async(self):
        reference_id = self.selected_ref_id
        if not reference_id:
            self.power_bi_reconciliation_loading = False
            self._update_power_bi_reconciliation_ui()
            return

        try:
            data = await self.assessment_controller.auditing_client.get_power_bi_reconciliation(reference_id)
            if reference_id != self.selected_ref_id:
                return
            self.power_bi_reconciliation_data = data
            self.power_bi_reconciliation_ref_id = reference_id
        except Exception as e:
            if reference_id != self.selected_ref_id:
                return
            self.power_bi_reconciliation_data = {"error": str(e)}
            self.power_bi_reconciliation_ref_id = reference_id
        finally:
            if reference_id == self.selected_ref_id:
                self.power_bi_reconciliation_loading = False
                self._update_power_bi_reconciliation_ui()

    def _update_power_bi_reconciliation_ui(self):
        if not hasattr(self, "power_bi_reconciliation_section"):
            return

        if not self.selected_ref_id:
            self.power_bi_reconciliation_section.content = ft.Column([
                ft.Text("Reporting Reconciliation", size=12, weight=ft.FontWeight.W_600),
                ft.Text(
                    "Select an assessment to compare native analytics with reporting-layer values.",
                    size=12,
                    color=ft.Colors.GREY_700
                )
            ], spacing=8)
            if self.page:
                self.page.update()
            return

        if self.power_bi_reconciliation_loading:
            self.power_bi_reconciliation_section.content = ft.Column([
                ft.Text("Reporting Reconciliation", size=12, weight=ft.FontWeight.W_600),
                ft.Row([
                    ft.ProgressRing(width=16, height=16, stroke_width=2),
                    ft.Text("Checking reporting data mart alignment...", size=12)
                ], spacing=10)
            ], spacing=8)
            if self.page:
                self.page.update()
            return

        data = self.power_bi_reconciliation_data or {}
        error_message = data.get("error") if isinstance(data, dict) else None
        if error_message:
            self.power_bi_reconciliation_section.content = ft.Column([
                ft.Text("Reporting Reconciliation", size=12, weight=ft.FontWeight.W_600),
                ft.Text(
                    f"Reconciliation failed: {error_message}",
                    size=12,
                    color=ft.Colors.RED_700
                )
            ], spacing=8)
            if self.page:
                self.page.update()
            return

        metrics = data.get("metrics", []) if isinstance(data, dict) else []
        matched = data.get("matchedMetrics", 0) if isinstance(data, dict) else 0
        mismatched = data.get("mismatchedMetrics", 0) if isinstance(data, dict) else 0
        data_mart_status = data.get("dataMartStatus", "Unknown") if isinstance(data, dict) else "Unknown"
        generated_at = data.get("generatedAt", "") if isinstance(data, dict) else ""

        if not metrics:
            self.power_bi_reconciliation_section.content = ft.Column([
                ft.Text("Reporting Reconciliation", size=12, weight=ft.FontWeight.W_600),
                ft.Text(
                    "No reconciliation metrics are available yet. Apply the reporting data mart views and refresh the assessment.",
                    size=12,
                    color=ft.Colors.GREY_700
                )
            ], spacing=8)
            if self.page:
                self.page.update()
            return

        summary_cards = ft.Row([
            self._build_power_bi_summary_card("Status", data_mart_status, ft.Colors.BLUE_700),
            self._build_power_bi_summary_card("Matched", matched, ft.Colors.GREEN_700),
            self._build_power_bi_summary_card("Mismatched", mismatched, ft.Colors.RED_700 if mismatched else ft.Colors.GREEN_700),
            self._build_power_bi_summary_card("Metrics", len(metrics), ft.Colors.BLUE_GREY_700),
        ], spacing=10, scroll=ft.ScrollMode.AUTO)

        sorted_metrics = sorted(
            metrics,
            key=lambda metric: (metric.get("isMatched", True), metric.get("category", ""), metric.get("metricName", ""))
        )
        metric_rows = []
        for metric in sorted_metrics[:6]:
            matched_flag = bool(metric.get("isMatched", False))
            metric_rows.append(
                ft.Container(
                    padding=10,
                    bgcolor=ft.Colors.WHITE,
                    border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
                    border_radius=8,
                    content=ft.Column([
                        ft.Row([
                            ft.Text(metric.get("metricName", "Metric"), size=12, weight=ft.FontWeight.W_600),
                            ft.Container(expand=True),
                            ft.Container(
                                content=ft.Text("Matched" if matched_flag else "Mismatch", size=10, color=ft.Colors.WHITE),
                                bgcolor=ft.Colors.GREEN_700 if matched_flag else ft.Colors.RED_700,
                                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                border_radius=999
                            )
                        ]),
                        ft.Text(
                            f"{metric.get('category', 'Reporting')} | Native {self._format_power_bi_metric(metric.get('nativeValue'))} | "
                            f"Reporting {self._format_power_bi_metric(metric.get('reportingValue'))}",
                            size=11,
                            color=ft.Colors.GREY_700
                        ),
                        ft.Text(
                            f"Variance {self._format_power_bi_metric(metric.get('variance'))}",
                            size=11,
                            color=ft.Colors.RED_700 if not matched_flag else ft.Colors.GREEN_700
                        )
                    ], spacing=4)
                )
            )

        footer_text = "All sampled metrics match the reporting layer." if mismatched == 0 else "Review mismatched metrics before relying on Power BI output."
        if generated_at:
            footer_text = f"{footer_text} Generated at {generated_at}."

        self.power_bi_reconciliation_section.content = ft.Column([
            ft.Text("Reporting Reconciliation", size=12, weight=ft.FontWeight.W_600),
            summary_cards,
            ft.Column(metric_rows, spacing=8),
            ft.Text(footer_text, size=11, color=ft.Colors.GREY_700),
        ], spacing=10)
        if self.page:
            self.page.update()

    def _build_power_bi_summary_card(self, label, value, color):
        return ft.Container(
            width=150,
            padding=12,
            bgcolor=ft.Colors.WHITE,
            border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
            border_radius=10,
            content=ft.Column([
                ft.Text(label, size=11, color=ft.Colors.GREY_700),
                ft.Text(str(value), size=20, weight=ft.FontWeight.W_700, color=color),
            ], spacing=4)
        )

    @staticmethod
    def _format_power_bi_metric(value):
        try:
            numeric = float(value or 0)
            return f"{numeric:,.0f}" if numeric.is_integer() else f"{numeric:,.2f}"
        except (TypeError, ValueError):
            return str(value or 0)

    def _ensure_analytics_import_picker(self):
        if self.analytics_import_file_picker:
            return
        self.analytics_import_file_picker = ft.FilePicker(on_result=self._on_analytics_import_file_selected)
        self.page.overlay.append(self.analytics_import_file_picker)

    def _open_analytics_import_dialog(self, e=None):
        if not self._feature_enabled("analytics_import", True):
            self._show_message("Analytics import is disabled in this environment.", error=True)
            return
        if not can_import_analytics(self.user):
            self._show_message("You do not have permission to import analytics data.", error=True)
            return
        self._ensure_analytics_import_picker()

        self.analytics_dataset_dropdown = ft.Dropdown(
            label="Dataset Type",
            value="journal_entries",
            options=[
                ft.dropdown.Option(key="journal_entries", text="Journal Entries"),
                ft.dropdown.Option(key="trial_balance", text="Trial Balance"),
                ft.dropdown.Option(key="industry_benchmarks", text="Industry Benchmarks"),
                ft.dropdown.Option(key="reasonability_forecasts", text="Reasonability Forecasts"),
            ],
            on_change=self._on_analytics_dataset_change
        )
        self.analytics_source_system_field = ft.TextField(label="Source System", hint_text="SAP, Oracle, Dynamics, Sage, Xero, CSV export")
        self.analytics_batch_name_field = ft.TextField(label="Batch Name", hint_text="Optional import batch label")
        self.analytics_notes_field = ft.TextField(label="Notes", multiline=True, min_lines=2, max_lines=4)
        self.analytics_reference_text = ft.Text(
            f"Assessment Reference: {self.selected_ref_id}" if self.selected_ref_id else "Assessment Reference: not selected (import will remain unscoped)",
            size=12,
            color=self.colors.text_secondary
        )
        self.analytics_selected_file_text = ft.Text("No CSV file selected", size=12, color=self.colors.text_secondary)
        self.analytics_validation_text = ft.Text(
            "Choose a dataset type and select a CSV file to validate required columns.",
            size=12,
            color=self.colors.text_secondary
        )
        self.analytics_preview_column = ft.Column(spacing=6, scroll=ft.ScrollMode.AUTO, height=180)
        self.analytics_batches_column = ft.Column(
            controls=[ft.Text("Loading recent import batches...", size=12, color=self.colors.text_secondary)],
            spacing=6,
            scroll=ft.ScrollMode.AUTO,
            height=160
        )
        self.analytics_import_button = ft.FilledButton("Import CSV", icon=Icons.CLOUD_UPLOAD, on_click=self._submit_analytics_import)
        self.analytics_import_button.disabled = True

        self.analytics_import_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Import Analytics Data"),
            content=ft.Container(
                width=760,
                content=ft.Column([
                    self.analytics_reference_text,
                    ft.Row([
                        self.analytics_dataset_dropdown,
                        self.analytics_source_system_field,
                    ], spacing=12),
                    ft.Row([
                        self.analytics_batch_name_field,
                        ft.OutlinedButton("Select CSV", icon=Icons.UPLOAD_FILE, on_click=self._pick_analytics_import_file),
                    ], spacing=12),
                    self.analytics_selected_file_text,
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Validation", size=12, weight=ft.FontWeight.W_600),
                            self.analytics_validation_text
                        ], spacing=6),
                        bgcolor=self.colors.hover_bg,
                        border_radius=10,
                        padding=12
                    ),
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Preview", size=12, weight=ft.FontWeight.W_600),
                            self.analytics_preview_column
                        ], spacing=8),
                        bgcolor=ft.Colors.SURFACE,
                        border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
                        border_radius=10,
                        padding=12
                    ),
                    self.analytics_notes_field,
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Recent Import Batches", size=12, weight=ft.FontWeight.W_600),
                            self.analytics_batches_column
                        ], spacing=8),
                        bgcolor=ft.Colors.SURFACE,
                        border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
                        border_radius=10,
                        padding=12
                    ),
                ], spacing=14, scroll=ft.ScrollMode.AUTO),
            ),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: self._close_analytics_import_dialog()),
                self.analytics_import_button,
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.page.dialog = self.analytics_import_dialog
        self.analytics_import_dialog.open = True
        self.page.update()
        self.page.run_task(self._load_analytics_import_batches_async)

    def _close_analytics_import_dialog(self):
        if self.analytics_import_dialog:
            self.analytics_import_dialog.open = False
        if self.page:
            self.page.update()

    def _pick_analytics_import_file(self, e=None):
        self._ensure_analytics_import_picker()
        self.analytics_import_file_picker.pick_files(
            allow_multiple=False,
            dialog_title="Select analytics CSV file",
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["csv"]
        )

    def _on_analytics_import_file_selected(self, e):
        if not e or not getattr(e, "files", None):
            return

        selected = e.files[0]
        self.pending_analytics_import_file = {
            "path": getattr(selected, "path", None),
            "name": getattr(selected, "name", None),
            "size": getattr(selected, "size", None),
        }
        if not self.pending_analytics_import_file.get("path"):
            self._show_message("Selected file path is not available in this runtime", error=True)
            return

        if hasattr(self, "analytics_selected_file_text"):
            file_name = self.pending_analytics_import_file.get("name") or os.path.basename(self.pending_analytics_import_file["path"])
            file_size = self.pending_analytics_import_file.get("size")
            size_text = f" ({file_size:,} bytes)" if isinstance(file_size, int) else ""
            self.analytics_selected_file_text.value = f"Selected file: {file_name}{size_text}"
            self._revalidate_selected_analytics_file()
            self.page.update()

    def _on_analytics_dataset_change(self, e=None):
        self._revalidate_selected_analytics_file()
        if self.page:
            self.page.run_task(self._load_analytics_import_batches_async)

    def _revalidate_selected_analytics_file(self):
        if not self.pending_analytics_import_file or not self.pending_analytics_import_file.get("path"):
            if hasattr(self, "analytics_validation_text"):
                self.analytics_validation_text.value = "Choose a dataset type and select a CSV file to validate required columns."
                self.analytics_import_button.disabled = True
                self.analytics_preview_column.controls = [ft.Text("No preview available", size=12, color=self.colors.text_secondary)]
                self.page.update()
            return

        dataset_type = self.analytics_dataset_dropdown.value or "journal_entries"
        validation = self._validate_analytics_csv_file(self.pending_analytics_import_file["path"], dataset_type)
        self.analytics_import_validation = validation
        self.analytics_import_button.disabled = not validation.get("is_valid", False)

        if validation.get("is_valid"):
            self.analytics_validation_text.value = (
                f"Validated {validation.get('row_count', 0):,} rows. "
                f"Required columns present for {dataset_type.replace('_', ' ')}."
            )
            self.analytics_validation_text.color = ft.Colors.GREEN_700
        else:
            error = validation.get("error") or "Validation failed."
            self.analytics_validation_text.value = error
            self.analytics_validation_text.color = ft.Colors.RED_700

        preview_rows = validation.get("preview_rows", [])
        if preview_rows:
            self.analytics_preview_column.controls = [
                ft.Container(
                    padding=8,
                    bgcolor=ft.Colors.WHITE,
                    border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
                    border_radius=8,
                    content=ft.Column([
                        ft.Text(f"Sample Row {index + 1}", size=11, weight=ft.FontWeight.W_600),
                        ft.Text(
                            " | ".join(f"{key}: {value}" for key, value in row.items()),
                            size=11,
                            color=self.colors.text_secondary
                        )
                    ], spacing=4)
                )
                for index, row in enumerate(preview_rows)
            ]
        else:
            self.analytics_preview_column.controls = [ft.Text("No preview available", size=12, color=self.colors.text_secondary)]

        self.page.update()

    def _validate_analytics_csv_file(self, file_path, dataset_type):
        required_columns = {
            "journal_entries": ["fiscal_year", "posting_date", "journal_number"],
            "trial_balance": ["fiscal_year", "account_number", "current_balance"],
            "industry_benchmarks": ["fiscal_year", "metric_name", "company_value", "benchmark_median"],
            "reasonability_forecasts": ["fiscal_year", "metric_name", "actual_value", "expected_value"],
        }.get(dataset_type, [])

        try:
            with open(file_path, "r", encoding="utf-8-sig", newline="") as handle:
                reader = csv.DictReader(handle)
                headers = [self._normalize_import_header(header) for header in (reader.fieldnames or [])]
                missing = [column for column in required_columns if column not in headers]

                row_count = 0
                preview_rows = []
                for raw_row in reader:
                    row_count += 1
                    if len(preview_rows) < 5:
                        preview_rows.append({
                            self._normalize_import_header(key): (value or "").strip()
                            for key, value in raw_row.items()
                            if key
                        })

                if not headers:
                    return {"is_valid": False, "error": "The selected CSV file does not contain headers."}
                if row_count == 0:
                    return {"is_valid": False, "error": "The selected CSV file does not contain data rows."}
                if missing:
                    return {"is_valid": False, "error": f"Missing required columns: {', '.join(missing)}", "preview_rows": preview_rows}

                return {
                    "is_valid": True,
                    "row_count": row_count,
                    "headers": headers,
                    "preview_rows": preview_rows,
                }
        except UnicodeDecodeError:
            return {"is_valid": False, "error": "Unable to read CSV file. Save the file as UTF-8 and try again."}
        except Exception as ex:
            return {"is_valid": False, "error": str(ex)}

    @staticmethod
    def _normalize_import_header(value):
        if not value:
            return ""
        normalized = "".join(ch if ch.isalnum() else "_" for ch in value.strip().lower())
        while "__" in normalized:
            normalized = normalized.replace("__", "_")
        return normalized.strip("_")

    async def _load_analytics_import_batches_async(self):
        try:
            dataset_type = self.analytics_dataset_dropdown.value if hasattr(self, "analytics_dataset_dropdown") else None
            batches = await self.assessment_controller.auditing_client.get_analytics_import_batches(
                reference_id=self.selected_ref_id,
                dataset_type=dataset_type,
                limit=8
            )
            self.analytics_import_batches = batches or []
        except Exception as ex:
            self.analytics_import_batches = [{"error": str(ex)}]

        self._refresh_analytics_import_batches_ui()

    def _refresh_analytics_import_batches_ui(self):
        if not hasattr(self, "analytics_batches_column"):
            return

        if self.analytics_import_batches and isinstance(self.analytics_import_batches[0], dict) and self.analytics_import_batches[0].get("error"):
            self.analytics_batches_column.controls = [
                ft.Text(f"Failed to load import batches: {self.analytics_import_batches[0]['error']}", size=12, color=ft.Colors.RED_700)
            ]
        elif not self.analytics_import_batches:
            self.analytics_batches_column.controls = [
                ft.Text("No import batches recorded yet for this context.", size=12, color=self.colors.text_secondary)
            ]
        else:
            controls = []
            for batch in self.analytics_import_batches:
                imported_at = (batch.get("importedAt") or "").replace("T", " ")[:16]
                controls.append(
                    ft.Container(
                        padding=8,
                        bgcolor=ft.Colors.WHITE,
                        border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
                        border_radius=8,
                        content=ft.Column([
                            ft.Row([
                                ft.Text((batch.get("batchName") or batch.get("sourceFileName") or "Import Batch"), size=12, weight=ft.FontWeight.W_600),
                                ft.Container(expand=True),
                                ft.Text(f"{batch.get('rowCount', 0):,} rows", size=11, color=self.colors.primary)
                            ]),
                            ft.Text(
                                f"{(batch.get('datasetType') or '').replace('_', ' ')} | {batch.get('sourceSystem') or 'Source not set'} | {imported_at or 'Unknown time'}",
                                size=11,
                                color=self.colors.text_secondary
                            )
                        ], spacing=4)
                    )
                )
            self.analytics_batches_column.controls = controls

        if self.page:
            self.page.update()

    def _submit_analytics_import(self, e=None):
        self.page.run_task(self._submit_analytics_import_async)

    async def _submit_analytics_import_async(self):
        if not self.pending_analytics_import_file or not self.pending_analytics_import_file.get("path"):
            self._show_message("Select a CSV file before importing.", error=True)
            return

        if not self.analytics_import_validation or not self.analytics_import_validation.get("is_valid"):
            self._show_message("Fix the CSV validation issues before importing.", error=True)
            return

        import_data = {
            "referenceId": self.selected_ref_id,
            "datasetType": self.analytics_dataset_dropdown.value or "journal_entries",
            "batchName": self.analytics_batch_name_field.value.strip() if self.analytics_batch_name_field.value else None,
            "sourceSystem": self.analytics_source_system_field.value.strip() if self.analytics_source_system_field.value else None,
            "importedByUserId": self.user.get("id") if isinstance(self.user, dict) else None,
            "importedByName": self.user.get("name") if isinstance(self.user, dict) else None,
            "notes": self.analytics_notes_field.value.strip() if self.analytics_notes_field.value else None,
        }

        self.analytics_import_button.disabled = True
        self.analytics_import_button.text = "Importing..."
        self.page.update()

        try:
            await self._record_usage_event("analytics", "analytics_import", "import_started", {
                "datasetType": import_data.get("datasetType"),
                "referenceId": import_data.get("referenceId")
            })
            result = await self.assessment_controller.auditing_client.upload_audit_analytics_file(
                self.pending_analytics_import_file["path"],
                import_data
            )
            await self._record_usage_event("analytics", "analytics_import", "import_completed", {
                "datasetType": result.get("datasetType"),
                "referenceId": result.get("referenceId"),
                "rowCount": result.get("rowCount", 0)
            })
            self._show_message(
                f"Imported {result.get('rowCount', 0):,} rows into {result.get('datasetType', 'analytics staging')}."
            )
            await self._load_analytics_import_batches_async()
            self._close_analytics_import_dialog()
            self._refresh_dashboard()
        except Exception as ex:
            await self._record_usage_event("analytics", "analytics_import", "import_failed", {
                "datasetType": import_data.get("datasetType"),
                "referenceId": import_data.get("referenceId"),
                "error": str(ex)
            })
            self._show_message(f"Analytics import failed: {str(ex)}", error=True)
            self.analytics_import_button.disabled = False
            self.analytics_import_button.text = "Import CSV"
            self.page.update()

    def _build_power_bi_url(self):
        template = self.power_bi_config.get("report_url", "")
        if not template:
            return ""

        try:
            return template.format(
                referenceId=self.selected_ref_id or "",
                auditUniverseId=self.selected_audit_universe_id or ""
            )
        except Exception as e:
            print(f"Error building Power BI URL: {e}")
            return template

    def _open_power_bi_report(self, e):
        url = self._build_power_bi_url()
        if not self.power_bi_config.get("enabled") or not url:
            self.page.show_snack_bar(
                ft.SnackBar(content=ft.Text("Microsoft Power BI is not configured for this environment."))
            )
            return

        self.page.run_task(self._record_usage_event, "analytics", "power_bi", "open_report", {
            "referenceId": self.selected_ref_id,
            "auditUniverseId": self.selected_audit_universe_id,
            "urlConfigured": bool(url)
        })
        self.page.launch_url(url)

    def _set_report_mode(self, mode):
        self.report_mode = mode
        self.report_mode_selector.value = mode
        self._refresh_dashboard()

    def _on_report_mode_change(self, e):
        self.report_mode = self.report_mode_selector.value or "native"
        self._refresh_dashboard()

    async def _record_usage_event(self, module_name, feature_name, event_name, metadata=None):
        try:
            await self.assessment_controller.auditing_client.record_usage_event({
                "moduleName": module_name,
                "featureName": feature_name,
                "eventName": event_name,
                "referenceId": self.selected_ref_id,
                "source": "analytical-dashboard",
                "metadataJson": json.dumps(metadata or {})
            })
        except Exception as ex:
            print(f"Failed to record analytical usage event: {ex}")

    def _handle_maximize(self, widget):
        # Instantiate with correct params based on class
        if isinstance(widget, MarketRiskWidget):
            maximized_widget = widget.__class__(self.page, widget.client, symbol=widget.symbol)
        elif isinstance(widget, TopRisksWidget):
            maximized_widget = widget.__class__(self.page, widget.client, count=widget.count)
        elif isinstance(widget, RiskCategoryDistributionWidget):
            maximized_widget = widget.__class__(self.page, widget.client, ref_id=widget.ref_id)
        else: # Other Risk Chart Widgets
            maximized_widget = widget.__class__(self.page, widget.client, ref_id=widget.ref_id)
            
        # maximized_widget.use_mock = widget.use_mock # Removed
        maximized_widget.view_mode = widget.view_mode
        
        def close_max(e):
            self.max_dialog.open = False
            self.page.update()

        self.max_dialog = ft.AlertDialog(
            title=ft.Text(widget.title_text, weight="bold"),
            content=ft.Container(content=maximized_widget, width=1200, height=800),
            actions=[ft.TextButton("Close", on_click=close_max)],
            on_dismiss=lambda _: maximized_widget.clean()
        )
        self.page.dialog = self.max_dialog
        self.max_dialog.open = True
        self.page.update()
        maximized_widget.load_data()

    def _handle_close_widget(self, widget):
        wid = widget.data
        if wid in self.active_widget_ids:
            self.active_widget_ids.remove(wid)
            self._refresh_dashboard()



    def _update_favorites_ui(self):
        self.favorites_row.controls = []
        for i, fav in enumerate(self.favorite_layouts):
            self.favorites_row.controls.append(
                ft.Chip(
                    label=ft.Text(fav["name"], size=10),
                    on_click=lambda e, f=fav: self._apply_favorite(f),
                    on_delete=lambda e, idx=i: self._remove_favorite(idx),
                    bgcolor=ft.Colors.SURFACE
                )
            )
        self.page.update()

    def _apply_favorite(self, fav):
        self.layout_mode = fav["layout_mode"]
        self.grid_columns = fav["grid_columns"]
        self.active_widget_ids = fav["active_ids"]
        self._refresh_dashboard()

    async def _save_current_layout(self, name):
        if not name: return
        new_fav = {
            "name": name,
            "layout_mode": self.layout_mode,
            "grid_columns": self.grid_columns,
            "active_ids": self.active_widget_ids[:]
        }
        self.favorite_layouts.append(new_fav)
        await self.page.client_storage.set_async("favorite_layouts", json.dumps(self.favorite_layouts))
        self._update_favorites_ui()

    async def _remove_favorite(self, idx):
        self.favorite_layouts.pop(idx)
        await self.page.client_storage.set_async("favorite_layouts", json.dumps(self.favorite_layouts))
        self._update_favorites_ui()

    def _open_customize_dialog(self, e):
        print("DEBUG: Entered _open_customize_dialog")
        try:
            # Layout Mode Icons (Container cards)
            layout_options = [
                {"mode": "grid", "icon": Icons.GRID_VIEW, "label": "Grid"},
                {"mode": "horizontal", "icon": Icons.ALIGN_HORIZONTAL_LEFT, "label": "H-Stack"},
                {"mode": "vertical", "icon": Icons.ALIGN_VERTICAL_TOP, "label": "V-Stack"},
                {"mode": "sidebar_left", "icon": Icons.VIEW_SIDEBAR, "label": "Sidebar L"},
                {"mode": "sidebar_right", "icon": Icons.VIEW_SIDEBAR_OUTLINED, "label": "Sidebar R"},
                {"mode": "featured_top", "icon": Icons.VIEW_AGENDA, "label": "Top Focus"},
                {"mode": "quad", "icon": Icons.DASHBOARD_CUSTOMIZE, "label": "Quad (2x2)"}
            ]

            layout_cards = []
            selected_mode = [self.layout_mode] # Use list for closure modification

            def select_mode(mode):
                selected_mode[0] = mode
                for card in layout_cards:
                    card.border = ft.border.all(2, Colors.BLUE if card.data == mode else Colors.GREY_300)
                    card.update()

            for opt in layout_options:
                card = ft.Container(
                    content=ft.Column([
                        ft.Icon(name=opt["icon"], size=24, color=self.colors.primary),
                        ft.Text(value=opt["label"], size=8, text_align=ft.TextAlign.CENTER)
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    width=60, height=60,
                    border_radius=8,
                    border=ft.border.all(2, Colors.BLUE if self.layout_mode == opt["mode"] else Colors.GREY_300),
                    on_click=lambda e, m=opt["mode"]: select_mode(m),
                    data=opt["mode"],
                    tooltip=opt["label"]
                )
                layout_cards.append(card)

            # Widget Selection
            print("DEBUG: Creating widget checkboxes...")
            checkboxes = [ft.Checkbox(label=c["title"], value=(wid in self.active_widget_ids), data=wid) 
                         for wid, c in self.widget_registry.items() if c["class"]]
            print(f"DEBUG: Created {len(checkboxes)} checkboxes")

            fav_name_input = ft.TextField(label="Favorite Name", text_size=12, height=45)

            def apply_changes(e):
                self.active_widget_ids = [cb.data for cb in checkboxes if cb.value]
                self.layout_mode = selected_mode[0]
                self.grid_columns = int(density_radio.value)
                self._close_dialog()
                self._refresh_dashboard()

            async def save_and_apply(e):
                if fav_name_input.value:
                    await self._save_current_layout(fav_name_input.value)
                apply_changes(e)

            density_radio = ft.RadioGroup(content=ft.Row([
                ft.Radio(value="16", label="4-col"),
                ft.Radio(value="12", label="3-col"),
                ft.Radio(value="6", label="2-col"),
                ft.Radio(value="4", label="1-col")
            ]), value=str(self.grid_columns))

            self.custom_dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text("Dashboard Customization"),
                content_padding=ft.padding.all(20),
                content=ft.Column([
                    ft.Text("1. Layout Style", weight="bold", size=14),
                    ft.Container(
                        content=ft.Row(layout_cards, wrap=True, spacing=10, alignment=ft.MainAxisAlignment.START),
                        padding=ft.padding.symmetric(vertical=10)
                    ),
                    ft.Divider(),
                    ft.Text("2. Grid Density", weight="bold", size=14),
                    ft.Container(content=density_radio, padding=ft.padding.symmetric(vertical=5)),
                    ft.Divider(),
                    ft.Text("3. Included Metrics", weight="bold", size=14),
                    ft.Container(
                        content=ft.Column(checkboxes, scroll=ft.ScrollMode.AUTO, spacing=5),
                        height=150,
                        padding=ft.padding.symmetric(vertical=5)
                    ),
                    ft.Divider(),
                    ft.Text("4. Save Template", weight="bold", size=14),
                    ft.Container(
                        content=ft.Row([
                            fav_name_input, 
                            ft.IconButton(
                                icon=Icons.FAVORITE, 
                                icon_color=self.colors.primary,
                                on_click=save_and_apply,
                                tooltip="Save as Favorite"
                            )
                        ], spacing=10),
                        padding=ft.padding.only(top=10)
                    )
                ], spacing=10, width=500, scroll=ft.ScrollMode.AUTO),
                actions=[
                    ft.TextButton("Cancel", on_click=lambda _: self._close_dialog()),
                    ft.FilledButton("Apply Configuration", on_click=apply_changes)
                ]
            )
            
            print(f"DEBUG: Showing dialog (ID: {id(self.custom_dialog)})")
            
            # Use modern open if available, else fallback
            if hasattr(self.page, "open"):
                self.page.open(self.custom_dialog)
            else:
                self.page.dialog = self.custom_dialog
                self.custom_dialog.open = True
                
            self.page.update()
            print("DEBUG: Page.update() completed for dialog show")
            print("DEBUG: Dialog opened and page updated")
        except Exception as ex:
            print(f"ERROR in _open_customize_dialog: {ex}")
            import traceback
            traceback.print_exc()

    def _close_dialog(self):
        if hasattr(self.page, "close"):
            self.page.close(self.custom_dialog)
        else:
            self.custom_dialog.open = False
        self.page.update()

    def _handle_drill_down(self, context=None):
        """Handle drill-down events from widgets"""
        print(f"DEBUG: Drill-down triggered: {context}")
        if context:
            ctx = dict(context) if isinstance(context, dict) else {"type": "generic", "data": context}
            if self.selected_ref_id is not None and "referenceId" not in ctx and "reference_id" not in ctx:
                ctx["referenceId"] = self.selected_ref_id
            if self.selected_audit_universe_id is not None and "auditUniverseId" not in ctx and "audit_universe_id" not in ctx:
                ctx["auditUniverseId"] = self.selected_audit_universe_id
            self.drill_down_panel.show(ctx)
            # Animate panel in
            if self.drill_down_container:
                self.drill_down_container.visible = True
                self.drill_down_container.offset = ft.Offset(0, 0)
                self.drill_down_container.update()
            elif self.drill_down_panel.parent:
                self.drill_down_panel.parent.offset = ft.Offset(0, 0)
                self.drill_down_panel.parent.update()

    def _close_drill_down(self):
        """Close the drill-down panel"""
        if self.drill_down_container:
            self.drill_down_container.offset = ft.Offset(1.1, 0)
            self.drill_down_container.update()
        elif self.drill_down_panel.parent:
            self.drill_down_panel.parent.offset = ft.Offset(1.1, 0)
            self.drill_down_panel.parent.update()
        
    def _handle_panel_navigation(self, destination, context):
        """Handle navigation requests from the drill-down panel"""
        if self.on_navigate:
            params = context if isinstance(context, dict) else {}
            # Ensure selected context is included
            if isinstance(params, dict):
                if self.selected_ref_id is not None and "reference_id" not in params and "referenceId" not in params:
                    params["reference_id"] = self.selected_ref_id
                if self.selected_audit_universe_id is not None and "audit_universe_id" not in params and "auditUniverseId" not in params:
                    params["audit_universe_id"] = self.selected_audit_universe_id
            if destination == "findings":
                params["initial_tab"] = 8
                self.on_navigate("assessments", "details", params)
            elif destination == "risks":
                params["initial_tab"] = 2
                self.on_navigate("assessments", "details", params)
            elif destination in {"controls", "gaps"}:
                params["initial_tab"] = 3
                self.on_navigate("assessments", "details", params)
            elif destination == "audits":
                self.on_navigate("audit_universe", None, params)
            else:
                self.on_navigate(destination, None, params)

    def _show_message(self, message, error=False):
        self.page.show_snack_bar(
            ft.SnackBar(
                content=ft.Text(message),
                bgcolor=ft.Colors.RED_700 if error else ft.Colors.GREEN_700
            )
        )

    def _export_report(self, e):
        # Identify checked widgets
        selected_to_export = []
        for wid, widget in self.active_instances.items():
            # Access the checkbox in the widget's header
            # Widget structure: Column -> [Row(Header), Divider, Content]
            # Header Row -> [Text, Spacer, Icon, Checkbox]
            # Checkbox is the last item in header controls
            try:
                if hasattr(widget, 'content') and isinstance(widget.content, ft.Column):
                    header_row = widget.content.controls[0]
                    # This logic might need adjustment based on specific widget implementation
                    # For now just export all visible if logic is complex
                    selected_to_export.append(self.widget_registry[wid]["title"])
            except:
                pass
        
        if not selected_to_export:
             selected_to_export = [self.widget_registry[wid]["title"] for wid in self.active_widget_ids]
        
        msq = f"Generating PDF for: {', '.join(selected_to_export)}..."
        self.page.show_snack_bar(ft.SnackBar(content=ft.Text(msq), action="Open"))

    def _on_context_change(self, e):
        print(f"DEBUG: [AnalyticalDashboard] Context Change Triggered! Value: {self.assessment_selector.value}")
        if self.assessment_selector.value:
            try:
                self.selected_ref_id = int(self.assessment_selector.value)
                self.power_bi_reconciliation_data = None
                self.power_bi_reconciliation_ref_id = None
                print(f"DEBUG: [AnalyticalDashboard] Selected Ref ID: {self.selected_ref_id}")
                self._refresh_dashboard()
            except ValueError:
                print(f"DEBUG: [AnalyticalDashboard] ERROR: Invalid selected_ref_id: {self.assessment_selector.value}")

    def _on_hierarchy_change(self, node):
        """Handle audit universe selection changes"""
        self.selected_audit_universe_node = node
        self.selected_audit_universe_id = node.get("id") if node else None
        print(f"DEBUG: [AnalyticalDashboard] Selected Audit Universe ID: {self.selected_audit_universe_id}")
        self._refresh_dashboard()

    def _build_drill_down_container(self):
        """Build the drill-down container for the stack"""
        self.drill_down_container = ft.Container(
            content=self.drill_down_panel,
            right=0, top=0, bottom=0,
            width=400,
            bgcolor=self.colors.surface,
            shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLACK54),
            offset=ft.Offset(1.1, 0), # Start hidden (off-screen right)
            animate_offset=ft.Animation(300, ft.AnimationCurve.EASE_OUT),
            visible=True # Always present but offset
        )
        return self.drill_down_container

