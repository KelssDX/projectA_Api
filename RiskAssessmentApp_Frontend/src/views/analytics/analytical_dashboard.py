import flet as ft
from flet import Icons, Colors
import asyncio
import json
from src.utils.theme import get_theme_colors, create_modern_card
from src.views.common.base_view import BaseView
from src.controllers.assessment_controller import AssessmentController

# Widget Imports
from src.views.widgets.risk_charts_widget import (
    InherentVsResidualWidget, 
    RiskCategoryDistributionWidget, 
    ControlCoverageWidget
)
from src.views.widgets.top_risks_widget import TopRisksWidget
from src.views.widgets.market_risk_widget import MarketRiskWidget

class AnalyticalDashboard(BaseView):
    def __init__(self, page, user, on_navigate=None):
        self.assessment_controller = AssessmentController()
        # State: Mock Data Mode
        self.use_mock = True # Default to True for now as requested to "see what it looks like"
        
        # Actions for the top bar
        self.mock_toggle = ft.Switch(
            label="Mock Data", 
            value=self.use_mock, 
            on_change=self._toggle_mock
        )
        
        actions = [
            self.mock_toggle,
            ft.OutlinedButton("Customize Layout", icon=Icons.DASHBOARD_CUSTOMIZE, on_click=self._open_customize_dialog),
            ft.FilledButton("Export Report", icon=Icons.PICTURE_AS_PDF, on_click=self._export_report)
        ]
        
        super().__init__(page, "Analytical Suite", actions=actions)
        self.user = user
        self.on_navigate = on_navigate
        self.colors = get_theme_colors(page.theme_mode)

        # Widget Registry (Mapping IDs to Classes)
        self.widget_registry = {
            "market_risk": {"class": MarketRiskWidget, "title": "Market Risk Analysis", "default": True},
            "inherent_residual": {"class": InherentVsResidualWidget, "title": "Inherent vs Residual Risk", "default": True},
            "top_risks": {"class": TopRisksWidget, "title": "Top 10 Residual Risks", "default": True},
            "risk_categories": {"class": RiskCategoryDistributionWidget, "title": "Risk Category Distribution", "default": True},
            "control_coverage": {"class": ControlCoverageWidget, "title": "Control Coverage", "default": True},
            # Placeholders for the full 13-tool suite
            "loss_scatter": {"class": None, "title": "Loss Frequency vs Severity", "default": False},
            "findings_aging": {"class": None, "title": "Open Findings Aging", "default": False},
            "audit_map": {"class": None, "title": "Audit Coverage Map", "default": False},
        }
        
        # State: List of active widget IDs
        self.active_widget_ids = [k for k, v in self.widget_registry.items() if v["default"]]
        self.active_instances = {} # Map ID -> Instance
        self.selected_ref_id = None  # No default - user must select
        self.grid_columns = 12 # Density setting
        self.layout_mode = "grid" # grid, horizontal, vertical, equal, sidebar_left, sidebar_right, featured_top, featured_bottom, quad
        self.favorite_layouts = [] # List of {name, layout_mode, grid_columns, active_ids}
        
        print(f"DEBUG: [AnalyticalDashboard] Initializing Dashboard (ID: {id(self)})")
        self._build_ui()
        print(f"DEBUG: [AnalyticalDashboard] UI Built. load_data() will be called by view manager.")

    def _build_ui(self):
        # Assessment Selector
        self.assessment_selector = ft.Dropdown(
            label="Assessment Context",
            hint_text="Select Assessment...",
            options=[], 
            text_size=12,
            width=250,
            bgcolor=ft.Colors.SURFACE_VARIANT,
            border_color=self.colors.primary,
            on_change=self._on_context_change
        )
        
        self.refresh_button = ft.IconButton(
            icon=ft.icons.REFRESH,
            icon_size=18,
            tooltip="Reload Assessments",
            on_click=lambda _: self.load_data()
        )
        
        # Favorites Chips
        self.favorites_row = ft.Row(spacing=10, scroll=ft.ScrollMode.AUTO)
        
        # Main Grid/Column
        self.dashboard_container = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO)
        self.dashboard_grid = ft.ResponsiveRow(run_spacing=20, spacing=20)
        self.dashboard_container.controls = [self.dashboard_grid]
        
        self.content_area = ft.Column([
            ft.Row([
                ft.Column([
                    ft.Text("MOCK DATA ENABLED" if self.use_mock else "REAL DATA MODE", 
                            size=10, weight="bold", color=Colors.ORANGE if self.use_mock else Colors.GREEN),
                    self.favorites_row
                ], spacing=5, expand=True),
                ft.Row([
                    self.assessment_selector,
                    self.refresh_button
                ], spacing=0)
            ], alignment=ft.MainAxisAlignment.END, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ft.Container(content=self.dashboard_container, padding=ft.padding.only(bottom=50), expand=True)
        ], expand=True)

        self.cards_column.controls.clear()
        self.add_card(self.content_area)

    def load_data(self):
        self.page.run_task(self._load_data_async)

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
                    if hasattr(self, 'content_area') and self.content_area.page:
                        self.content_area.update()
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
            # All widgets now take (page, client, ref_id)
            widget = w_class(self.page, self.assessment_controller.auditing_client, self.selected_ref_id)
            
            widget.use_mock = self.use_mock
            widget.on_maximize_requested = self._handle_maximize
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
            
        maximized_widget.use_mock = widget.use_mock
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

    def _toggle_mock(self, e):
        self.use_mock = self.mock_toggle.value
        self._build_ui() 
        self._refresh_dashboard()

    def _update_favorites_ui(self):
        self.favorites_row.controls = []
        for i, fav in enumerate(self.favorite_layouts):
            self.favorites_row.controls.append(
                ft.Chip(
                    label=ft.Text(fav["name"], size=10),
                    on_click=lambda e, f=fav: self._apply_favorite(f),
                    on_delete=lambda e, idx=i: self._remove_favorite(idx),
                    bgcolor=ft.Colors.SURFACE_VARIANT
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

    def _export_report(self, e):
        # Identify checked widgets
        selected_to_export = []
        for wid, widget in self.active_instances.items():
            # Access the checkbox in the widget's header
            # Widget structure: Column -> [Row(Header), Divider, Content]
            # Header Row -> [Text, Spacer, Icon, Checkbox]
            # Checkbox is the last item in header controls
            try:
                header_row = widget.content.controls[0]
                checkbox = header_row.controls[-1]
                if isinstance(checkbox, ft.Checkbox) and checkbox.value:
                    selected_to_export.append(self.widget_registry[wid]["title"])
            except:
                pass
        
        if not selected_to_export:
            self.page.show_snack_bar(ft.SnackBar(content=ft.Text("Please select at least one widget to export via the checkboxes.")))
            return

        msq = f"Generating PDF for: {', '.join(selected_to_export)}..."
        self.page.show_snack_bar(ft.SnackBar(content=ft.Text(msq), action="Open"))

    async def _on_context_change(self, e):
        print(f"DEBUG: [AnalyticalDashboard] Context Change Triggered! Value: {self.assessment_selector.value}")
        if self.assessment_selector.value:
            try:
                self.selected_ref_id = int(self.assessment_selector.value)
                print(f"DEBUG: [AnalyticalDashboard] Selected Ref ID: {self.selected_ref_id}")
                self._refresh_dashboard()
            except ValueError:
                print(f"DEBUG: [AnalyticalDashboard] ERROR: Invalid selected_ref_id: {self.assessment_selector.value}")
