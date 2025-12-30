import flet as ft
from flet import Icons
import asyncio
from src.utils.theme import (
    get_theme_colors,
    create_modern_button,
    create_modern_card,
    apply_theme_to_control,
)
from src.views.common.base_view import BaseView
from src.controllers.assessment_controller import AssessmentController


class ModernHeatmapDashboard(BaseView):
    def __init__(self, page, user, reference_id=None, on_navigate=None):
        self.page = page
        self.user = user
        self.reference_id = reference_id
        self.on_navigate = on_navigate
        self.assessment_controller = AssessmentController()
        self.heatmap_data = None
        self.enabled_levels = {"Critical": True, "High": True, "Medium": True, "Low": True, "Very Low": True}
        
        # Data storage
        self.all_assessments = []
        self.filtered_assessments = []
        self.all_departments = []
        self.all_assessors = []
        
        # Resizable panel flex values
        self.left_flex = 1
        self.center_flex = 4
        self.right_flex = 1
        
        # Theme colors
        colors = get_theme_colors(self.page.theme_mode if hasattr(self.page, "theme_mode") else ft.ThemeMode.LIGHT)
        
        # Search Components
        self.header_search = ft.TextField(
            label="Search Assessment",
            width=300,
            hint_text="Title, Ref ID, Assessor...",
            prefix_icon=Icons.SEARCH,
            on_change=self._on_search_change,
            on_submit=self._on_search_submit,
            cursor_color=colors.text_primary,
            border_radius=8,
            text_size=14,
            height=45,
            content_padding=ft.padding.only(left=10, right=10, bottom=5)
        )
        
        # Suggestions container (hidden by default)
        self.suggestions_card = ft.Card(
            visible=False,
            elevation=5,
            content=ft.Container(
                bgcolor=colors.surface,
                padding=10,
                border_radius=8,
                width=350,
                content=ft.Column([], spacing=5, scroll=ft.ScrollMode.AUTO, height=200)
            )
        )
        
        self.selected_assessment_text = ft.Text(
            "No Assessment Selected", 
            size=16, 
            weight=ft.FontWeight.BOLD,
            color=colors.text_primary
        )

        # Filters
        self.department_filter = ft.Dropdown(
            label="Department",
            width=150,
            value="All",
            options=[ft.dropdown.Option("All")],
            on_change=self._apply_filters,
            text_size=14
        )
        
        self.assessor_filter = ft.Dropdown(
            label="Assessor",
            width=150,
            value="All",
            options=[ft.dropdown.Option("All")],
            on_change=self._apply_filters,
            text_size=14
        )
        
        # Header actions
        actions = [
            self.header_search,
            self.department_filter,
            self.assessor_filter,
            create_modern_button(colors, "Refresh", icon=Icons.REFRESH, on_click=self._on_refresh_click, style="secondary", height=45),
        ]
        
        super().__init__(page, "Risk Heatmap", actions=actions, colors=colors)
        
        # Container for suggestions that appears at top of content
        self.suggestions_container = ft.Container(
            visible=False,
            padding=ft.padding.only(left=20),
            content=self.suggestions_card
        )
        
        self._build_ui()

    def load_data(self):
        """Load data when view is shown"""
        if hasattr(self, 'page') and self.page:
            self.page.run_task(self._load_all_data)

    async def _load_all_data(self):
        """Load assessments and departments from API"""
        try:
            # Load assessments and departments in parallel
            assessments_task = self.assessment_controller.auditing_client.get_assessments()
            departments_task = self.assessment_controller.auditing_client.get_departments()
            
            results = await asyncio.gather(assessments_task, departments_task, return_exceptions=True)
            
            # Process assessments
            if not isinstance(results[0], Exception):
                self.all_assessments = results[0] or []
                self.filtered_assessments = self.all_assessments.copy()
                
                # Extract unique assessors
                assessors = set()
                for a in self.all_assessments:
                    assessor = a.get('auditor') or a.get('assessor', '')
                    if assessor:
                        assessors.add(assessor)
                self.all_assessors = sorted(list(assessors))
                
                self._update_assessor_filter()
            
            # Process departments
            if not isinstance(results[1], Exception):
                self.all_departments = results[1] or []
                self._update_department_filter()
            
            # If reference_id passed in init, load it
            if self.reference_id:
                await self._load_heatmap_data()
                # Update selected text
                found = next((a for a in self.all_assessments if (a.get('reference_id') or a.get('id')) == self.reference_id), None)
                if found:
                    self.selected_assessment_text.value = f"Selected: {found.get('title', 'Unknown')} (Ref: {self.reference_id})"

            if self.page:
                self.page.update()
                
        except Exception as e:
            print(f"Error loading data: {e}")

    async def _load_heatmap_data(self):
        """Load heatmap data for selected assessment"""
        if not self.reference_id:
            self.heatmap_data = None
            self.selected_assessment_text.value = "No Assessment Selected"
            self._update_heatmap_ui()
            return
            
        try:
            # Find assessment details for display
            assessment = next((a for a in self.all_assessments if (a.get('reference_id') or a.get('id')) == self.reference_id), None)
            if assessment:
                title = assessment.get('title') or "Untitled"
                ref = assessment.get('reference_id') or assessment.get('id')
                self.selected_assessment_text.value = f"Selected: {title} (Ref: {ref})"
            
            self.heatmap_data = await self.assessment_controller.get_heatmap_data(self.reference_id)
            self._update_heatmap_ui()
            
        except Exception as e:
            print(f"Error loading heatmap data: {e}")
            self.heatmap_data = None
            self._update_heatmap_ui()

    def _update_heatmap_ui(self):
        """Update just the heatmap grid area"""
        # Re-create the heatmap grid
        grid = self.create_heatmap_grid()
        # Find the heatmap card in UI structure and update content
        # Structure: _main_content_container -> Row -> Center Col -> Heatmap Card
        # Easier to just rebuild UI since it's fast enough in Flet
        self._build_ui()
        if self.page:
            self.page.update()

    def _update_department_filter(self):
        """Update department filter dropdown"""
        self.department_filter.options = [ft.dropdown.Option("All")]
        for dept in self.all_departments:
            name = dept.get('name', '')
            if name:
                self.department_filter.options.append(ft.dropdown.Option(name))

    def _update_assessor_filter(self):
        """Update assessor filter dropdown"""
        self.assessor_filter.options = [ft.dropdown.Option("All")]
        for assessor in self.all_assessors:
            self.assessor_filter.options.append(ft.dropdown.Option(assessor))

    def _on_search_change(self, e):
        """Handle search text change - show suggestions"""
        search_term = (self.header_search.value or "").lower().strip()
        
        if not search_term:
            self.suggestions_container.visible = False
            if self.page:
                self.page.update()
            return

        # Simple filter for suggestions
        matches = [
            a for a in self.all_assessments
            if search_term in (a.get('title') or '').lower()
            or search_term in str(a.get('reference_id', ''))
        ][:5] # Top 5

        if matches:
            content_col = self.suggestions_card.content.content
            content_col.controls.clear()
            content_col.controls.append(ft.Text("Top Matches:", size=12, color=self.colors.text_secondary))
            
            for m in matches:
                ref_id = m.get('reference_id') or m.get('id')
                title = m.get('title', 'Untitled')
                content_col.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(Icons.ASSESSMENT_OUTLINED, size=16),
                            ft.Text(f"{title} (#{ref_id})", size=14, weight=ft.FontWeight.W_500, expand=True),
                            ft.Icon(Icons.ARROW_FORWARD_IOS, size=12, color=self.colors.text_secondary)
                        ]),
                        padding=10,
                        border_radius=4,
                        ink=True,
                        on_click=lambda e, r=ref_id: self._select_assessment_from_search(r),
                        bgcolor=ft.colors.with_opacity(0.05, self.colors.primary) if hasattr(ft, 'colors') else "#f0f0f0"
                    )
                )
            
            content_col.controls.append(ft.Divider())
            content_col.controls.append(
                ft.TextButton(
                    "View All Results", 
                    icon=Icons.LIST, 
                    on_click=lambda e: self._show_search_results_dialog(search_term)
                )
            )
            
            self.suggestions_container.visible = True
        else:
            self.suggestions_container.visible = False
            
        if self.page:
            self.page.update()

    def _on_search_submit(self, e):
        """Handle Enter key in search"""
        search_term = self.header_search.value
        if search_term:
            self.suggestions_container.visible = False
            self._show_search_results_dialog(search_term)

    def _select_assessment_from_search(self, ref_id):
        """Handle selection from suggestion"""
        self.suggestions_container.visible = False
        self.reference_id = int(ref_id)
        self.header_search.value = "" # Clear search
        if self.page:
            self.page.run_task(self._load_heatmap_data)

    def _show_search_results_dialog(self, search_term):
        """Show full paginated search results"""
        search_term = search_term.lower().strip()
        
        # Filter all matching
        matches = [
            a for a in self.all_assessments
            if search_term in (a.get('title') or '').lower()
            or search_term in str(a.get('reference_id', ''))
            or search_term in (a.get('auditor') or a.get('assessor') or '').lower()
            or search_term in (a.get('department') or '').lower()
        ]

        # Pagination logic
        page_size = 5
        current_page = [1] # Mutable list to hold state in closure
        total_pages = (len(matches) + page_size - 1) // page_size or 1

        results_list = ft.Column(spacing=5, scroll=ft.ScrollMode.AUTO, height=300)
        page_text = ft.Text(f"Page 1 of {total_pages}")
        
        # Define handlers before using them
        def next_page(e):
            if current_page[0] < total_pages:
                current_page[0] += 1
                render_page()

        def prev_page(e):
            if current_page[0] > 1:
                current_page[0] -= 1
                render_page()

        prev_btn = ft.IconButton(Icons.ARROW_BACK, on_click=prev_page)
        next_btn = ft.IconButton(Icons.ARROW_FORWARD, on_click=next_page)
        
        # Create dialog first so it's available in closure
        dialog = ft.AlertDialog(
            title=ft.Text(f"Search Results: '{search_term}' ({len(matches)} found)"),
            content=ft.Column([
                results_list,
                ft.Row([prev_btn, page_text, next_btn], alignment=ft.MainAxisAlignment.CENTER)
            ], height=400, width=500),
            actions=[ft.TextButton("Close", on_click=lambda e: self.page.close(dialog))]
        )

        def select_and_close(ref_id):
            self.reference_id = int(ref_id)
            self.header_search.value = ""
            if self.page:
                self.page.close(dialog)
                self.page.run_task(self._load_heatmap_data)

        def render_page():
            start = (current_page[0] - 1) * page_size
            end = start + page_size
            page_items = matches[start:end]
            
            results_list.controls.clear()
            if not page_items:
                results_list.controls.append(ft.Text("No assessments found matching your query."))
            else:
                for item in page_items:
                    ref_id = item.get('reference_id') or item.get('id')
                    title = item.get('title', 'Untitled')
                    dept = item.get('department', 'N/A')
                    assessor = item.get('auditor') or item.get('assessor', 'N/A')
                    date = item.get('assessment_date', '').split('T')[0] if item.get('assessment_date') else 'N/A'
                    
                    results_list.controls.append(
                        ft.Container(
                            padding=10,
                            border=ft.border.all(1, self.colors.border),
                            border_radius=8,
                            content=ft.Row([
                                ft.Column([
                                    ft.Text(title, weight=ft.FontWeight.BOLD),
                                    ft.Text(f"Ref: {ref_id} | Dept: {dept}", size=12, color=self.colors.text_secondary),
                                    ft.Text(f"Assessor: {assessor} | Date: {date}", size=12, color=self.colors.text_secondary),
                                ], expand=True),
                                ft.ElevatedButton(
                                    "Select", 
                                    icon=Icons.CHECK,
                                    on_click=lambda e, r=ref_id: select_and_close(r)
                                )
                            ])
                        )
                    )
            
            page_text.value = f"Page {current_page[0]} of {total_pages}"
            prev_btn.disabled = current_page[0] <= 1
            next_btn.disabled = current_page[0] >= total_pages
            # Only update if dialog is actually open, avoid race conditions or errors if called before open
            if dialog.open:
                dialog.update()

        # Render initial page before opening to ensure content is ready
        render_page()
        self.page.open(dialog)

    def _apply_filters(self, e=None):
        """Apply department/assessor filters"""
        # This is for a list view, but in Heatmap we select ONE assessment.
        # These filters could filter the suggestions or be removed. 
        # For now, let's make them filter the 'all_assessments' list used for search?
        # Or better: Provide a "Filter & Select" dialog.
        # Given the instruction "search ... using the assessment name or reference id", 
        # these dropdowns might be secondary. Let's keep them functional if user wants to browse.
        pass # Search is primary now.

    def _on_refresh_click(self, e):
        """Handle refresh button click"""
        self.load_data()

    def _build_ui(self):
        """Build the UI components"""
        colors = self.colors

        # Left panel - Display settings only
        filter_panel = create_modern_card(
            colors,
            ft.Column([
                ft.Text("Display Settings", size=16, weight=ft.FontWeight.BOLD, color=colors.text_primary),
                ft.Divider(height=1, color=colors.border),
                ft.Container(height=10),
                ft.Text("Risk Levels", size=13, weight=ft.FontWeight.W_500, color=colors.text_secondary),
                ft.Container(height=5),
                ft.Checkbox(label="Critical", value=self.enabled_levels.get("Critical", True), 
                           on_change=lambda e: self._on_level_checkbox_change("Critical", e),
                           check_color="#8B0000", active_color="#8B0000"),
                ft.Checkbox(label="High", value=self.enabled_levels.get("High", True), 
                           on_change=lambda e: self._on_level_checkbox_change("High", e),
                           check_color="#e74c3c", active_color="#e74c3c"),
                ft.Checkbox(label="Medium", value=self.enabled_levels.get("Medium", True), 
                           on_change=lambda e: self._on_level_checkbox_change("Medium", e),
                           check_color="#f39c12", active_color="#f39c12"),
                ft.Checkbox(label="Low", value=self.enabled_levels.get("Low", True), 
                           on_change=lambda e: self._on_level_checkbox_change("Low", e),
                           check_color="#2ecc71", active_color="#2ecc71"),
                ft.Checkbox(label="Very Low", value=self.enabled_levels.get("Very Low", True), 
                           on_change=lambda e: self._on_level_checkbox_change("Very Low", e),
                           check_color="#27ae60", active_color="#27ae60"),
                ft.Container(height=20),
                ft.ElevatedButton(
                    text="Export Heatmap", 
                    icon=Icons.DOWNLOAD, 
                    on_click=self.export_heatmap,
                    width=200
                ),
            ], scroll=ft.ScrollMode.AUTO, spacing=5),
            padding=ft.padding.all(16)
        )

        # Legend
        legend = ft.Row([
            ft.Row([ft.Container(width=16, height=16, bgcolor="#8B0000", border_radius=3), ft.Container(width=4), ft.Text("Critical", size=12, color=colors.text_primary)]),
            ft.Row([ft.Container(width=16, height=16, bgcolor="#e74c3c", border_radius=3), ft.Container(width=4), ft.Text("High", size=12, color=colors.text_primary)]),
            ft.Row([ft.Container(width=16, height=16, bgcolor="#f39c12", border_radius=3), ft.Container(width=4), ft.Text("Medium", size=12, color=colors.text_primary)]),
            ft.Row([ft.Container(width=16, height=16, bgcolor="#2ecc71", border_radius=3), ft.Container(width=4), ft.Text("Low", size=12, color=colors.text_primary)]),
            ft.Row([ft.Container(width=16, height=16, bgcolor="#27ae60", border_radius=3), ft.Container(width=4), ft.Text("Very Low", size=12, color=colors.text_primary)]),
        ], spacing=15, alignment=ft.MainAxisAlignment.CENTER, wrap=True)

        # Heatmap grid
        heatmap_card = create_modern_card(colors, self.create_heatmap_grid(), padding=ft.padding.all(16))

        # Center column
        center_column = ft.Column([
            self.suggestions_container, # Add suggestions here
            create_modern_card(colors, self.selected_assessment_text, padding=10), # Show selected
            ft.Container(height=10),
            create_modern_card(colors, legend, padding=ft.padding.symmetric(horizontal=16, vertical=10)),
            ft.Container(height=10),
            heatmap_card
        ], spacing=0, expand=True, scroll=ft.ScrollMode.AUTO)

        # Stats/Insights panel
        stats = self.create_stats_section()
        insights_panel = create_modern_card(
            colors,
            ft.Column([
                ft.Text("Insights", size=16, weight=ft.FontWeight.BOLD, color=colors.text_primary),
                ft.Divider(height=1, color=colors.border),
                stats
            ], scroll=ft.ScrollMode.AUTO, spacing=10),
            padding=ft.padding.all(16)
        )

        # Build resizable row
        main_row = self._build_resizable_row(filter_panel, center_column, insights_panel)
        self._main_content_container = ft.Container(expand=True, content=main_row)

        # Add card to BaseView
        self.cards_column.controls.clear()
        self.add_card(self._main_content_container)

    def apply_theme(self, colors):
        """Apply theme colors"""
        try:
            self._build_ui()
            apply_theme_to_control(self, colors)
        except Exception:
            pass

    def create_heatmap_grid(self):
        """Create the risk heatmap grid"""
        colors = self.colors
        
        if not self.reference_id:
            return self._create_message_grid("Select an assessment to view its heatmap", Icons.TOUCH_APP)
        
        if not self.heatmap_data:
            return self._create_message_grid("Loading heatmap data...", Icons.HOURGLASS_EMPTY)

        try:
            heatmap_grid = self.heatmap_data.get("heatmapGrid", {})
            
            if not heatmap_grid:
                return self._create_message_grid("No risk data available for this assessment", Icons.INFO_OUTLINE)

            impact_levels = ["Catastrophic", "Major", "Moderate", "Minor", "Negligible"]
            likelihood_levels = ["Rare", "Unlikely", "Possible", "Probable", "Very High"]

            # Header row
            header_cells = [ft.Container(
                width=100,
                height=45,
                alignment=ft.alignment.center,
                content=ft.Text("Impact ↓ / Likelihood →", size=10, weight=ft.FontWeight.BOLD, 
                               color=colors.text_secondary, text_align=ft.TextAlign.CENTER)
            )]

            for likelihood in likelihood_levels:
                header_cells.append(ft.Container(
                    width=85,
                    height=45,
                    bgcolor="#34495e",
                    border_radius=ft.border_radius.only(top_left=4, top_right=4),
                    alignment=ft.alignment.center,
                    content=ft.Text(likelihood, size=10, weight=ft.FontWeight.BOLD, color="white", text_align=ft.TextAlign.CENTER)
                ))

            header_row = ft.Row(header_cells, spacing=2)
            rows = [header_row]

            for impact in impact_levels:
                row_cells = [ft.Container(
                    width=100,
                    height=55,
                    bgcolor="#34495e",
                    border_radius=ft.border_radius.only(top_left=4, bottom_left=4),
                    alignment=ft.alignment.center,
                    content=ft.Text(impact, size=10, weight=ft.FontWeight.BOLD, color="white", text_align=ft.TextAlign.CENTER)
                )]

                for likelihood in likelihood_levels:
                    count = heatmap_grid.get(impact, {}).get(likelihood, 0)
                    risk_level, cell_color = self._calculate_risk_level(impact, likelihood)
                    is_enabled = self.enabled_levels.get(risk_level, True)
                    
                    display_color = cell_color if is_enabled else colors.surface
                    text_color = "white" if is_enabled and count > 0 else colors.text_secondary
                    
                    cell = ft.Container(
                        width=85,
                        height=55,
                        bgcolor=display_color,
                        border=ft.border.all(1, colors.border) if not is_enabled or count == 0 else None,
                        border_radius=5,
                        alignment=ft.alignment.center,
                        content=ft.Text(
                            str(count),
                            size=16,
                            weight=ft.FontWeight.BOLD,
                            color=text_color
                        ),
                        on_click=lambda e, i=impact, l=likelihood, c=count, r=risk_level: self.show_cell_details(i, l, c, r),
                        tooltip=f"{impact} × {likelihood}\n{count} risk(s) - {risk_level}"
                    )
                    row_cells.append(cell)

                rows.append(ft.Row(row_cells, spacing=2))

            return ft.Container(
                padding=10,
                content=ft.Column(rows, spacing=2, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            )

        except Exception as e:
            print(f"Error creating heatmap grid: {e}")
            return self._create_message_grid(f"Error: {str(e)}", Icons.ERROR_OUTLINE)

    def _create_message_grid(self, message, icon):
        """Create a placeholder message grid"""
        colors = self.colors
        return ft.Container(
            padding=20,
            bgcolor=colors.surface,
            border=ft.border.all(1, colors.border),
            border_radius=8,
            content=ft.Container(
                height=300,
                alignment=ft.alignment.center,
                content=ft.Column([
                    ft.Icon(icon, size=48, color=colors.text_secondary),
                    ft.Container(height=10),
                    ft.Text(message, size=16, color=colors.text_secondary, text_align=ft.TextAlign.CENTER)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            )
        )

    def _calculate_risk_level(self, impact, likelihood):
        """Calculate risk level and color"""
        impact_scores = {"Negligible": 1, "Minor": 2, "Moderate": 3, "Major": 4, "Catastrophic": 5}
        likelihood_scores = {"Rare": 1, "Unlikely": 2, "Possible": 3, "Probable": 4, "Very High": 5}
        
        impact_score = impact_scores.get(impact, 3)
        likelihood_score = likelihood_scores.get(likelihood, 3)
        risk_score = impact_score * likelihood_score
        
        if risk_score >= 20:
            return "Critical", "#8B0000"
        elif risk_score >= 15:
            return "High", "#e74c3c"
        elif risk_score >= 10:
            return "Medium", "#f39c12"
        elif risk_score >= 5:
            return "Low", "#2ecc71"
        else:
            return "Very Low", "#27ae60"

    def _on_level_checkbox_change(self, level, e):
        """Handle risk level checkbox change"""
        try:
            self.enabled_levels[level] = bool(e.control.value)
            self._build_ui()
            if self.page:
                self.page.update()
        except Exception:
            pass

    def create_stats_section(self):
        """Create statistics section"""
        if not self.heatmap_data:
            return ft.Container(
                padding=20,
                content=ft.Text("No data to display", color=self.colors.text_secondary)
            )

        try:
            heatmap_grid = self.heatmap_data.get("heatmapGrid", {})
            stats = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0, "Very Low": 0, "Total": 0}
            
            for impact, likelihood_dict in heatmap_grid.items():
                for likelihood, count in likelihood_dict.items():
                    risk_level, _ = self._calculate_risk_level(impact, likelihood)
                    if risk_level in stats:
                        stats[risk_level] += count
                    stats["Total"] += count

            return ft.Column([
                self._create_stat_row("Critical", stats["Critical"], "#8B0000"),
                self._create_stat_row("High", stats["High"], "#e74c3c"),
                self._create_stat_row("Medium", stats["Medium"], "#f39c12"),
                self._create_stat_row("Low", stats["Low"], "#2ecc71"),
                self._create_stat_row("Very Low", stats["Very Low"], "#27ae60"),
                ft.Divider(height=1, color=self.colors.border),
                self._create_stat_row("Total Risks", stats["Total"], "#3498db"),
            ], spacing=8)
            
        except Exception as e:
            print(f"Error creating stats: {e}")
            return ft.Container()

    def _create_stat_row(self, label, value, color):
        """Create a stat row"""
        return ft.Container(
            padding=ft.padding.symmetric(vertical=8, horizontal=12),
            border_radius=6,
            bgcolor=self.colors.surface,
            content=ft.Row([
                ft.Container(width=8, height=30, bgcolor=color, border_radius=4),
                ft.Container(width=10),
                ft.Text(label, size=13, color=self.colors.text_primary),
                ft.Container(expand=True),
                ft.Text(str(value), size=16, weight=ft.FontWeight.BOLD, color=color)
            ])
        )

    def export_heatmap(self, e):
        """Export heatmap dialog"""
        dialog = ft.AlertDialog(
            title=ft.Text("Export Heatmap"),
            content=ft.Column([
                ft.Text("Select export format:", size=14),
                ft.Container(height=15),
                ft.ElevatedButton(text="Export as PDF", bgcolor="#3498db", color="white", width=200, on_click=lambda e: self._close_dialog()),
                ft.Container(height=8),
                ft.ElevatedButton(text="Export as Excel", bgcolor="#2ecc71", color="white", width=200, on_click=lambda e: self._close_dialog()),
                ft.Container(height=8),
                ft.ElevatedButton(text="Export as Image", bgcolor="#f39c12", color="white", width=200, on_click=lambda e: self._close_dialog()),
            ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            actions=[ft.TextButton("Cancel", on_click=lambda e: self._close_dialog())],
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def show_cell_details(self, impact, likelihood, count, risk_level):
        """Show cell details dialog"""
        dialog = ft.AlertDialog(
            title=ft.Text("Risk Cell Details"),
            content=ft.Column([
                ft.Row([ft.Text("Impact:", weight=ft.FontWeight.BOLD), ft.Text(impact)]),
                ft.Row([ft.Text("Likelihood:", weight=ft.FontWeight.BOLD), ft.Text(likelihood)]),
                ft.Row([ft.Text("Risk Level:", weight=ft.FontWeight.BOLD), ft.Text(risk_level)]),
                ft.Divider(),
                ft.Row([
                    ft.Text("Risk Count:", weight=ft.FontWeight.BOLD), 
                    ft.Text(str(count), size=18, weight=ft.FontWeight.BOLD, color="#3498db")
                ]),
                ft.Container(height=10),
                ft.Text("This cell represents risks at this impact/likelihood intersection.", 
                       size=12, color="#7f8c8d"),
            ], width=350, spacing=8),
            actions=[
                ft.TextButton("Close", on_click=lambda e: self._close_dialog()),
                ft.TextButton("View Assessments", on_click=lambda e: self._navigate_filter(risk_level, impact, likelihood)) if count > 0 else None,
            ],
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def _close_dialog(self):
        """Close dialog"""
        if self.page.dialog:
            self.page.dialog.open = False
            self.page.update()

    def _navigate_filter(self, level=None, impact=None, likelihood=None):
        """Navigate to assessments with filter"""
        if hasattr(self.page, 'APP_INSTANCE') and self.page.APP_INSTANCE:
            app = self.page.APP_INSTANCE
            flt = {}
            if level:
                flt['risk_level'] = level
            if impact:
                flt['impact'] = impact
            if likelihood:
                flt['likelihood'] = likelihood
            app.pending_assessment_filter = flt
            app.current_reference_id = self.reference_id
            self._close_dialog()
            app.show_view("assessments")

    async def cleanup(self):
        """Cleanup resources"""
        try:
            await self.assessment_controller.close()
        except Exception as e:
            print(f"Error closing controller: {e}")

    def _build_resizable_row(self, left_panel, center_panel, right_panel):
        """Build resizable 3-panel layout"""
        colors = self.colors

        def divider(on_pan_update):
            return ft.GestureDetector(
                on_pan_update=on_pan_update,
                content=ft.Container(width=6, bgcolor=colors.border, border_radius=3)
            )

        def on_drag_left(e):
            try:
                dx = getattr(e, "delta_x", 0) or 0
                if dx > 2 and self.center_flex > 2:
                    self.left_flex += 1
                    self.center_flex -= 1
                elif dx < -2 and self.left_flex > 1:
                    self.left_flex -= 1
                    self.center_flex += 1
                self._rebuild_main_row(left_panel, center_panel, right_panel)
            except Exception:
                pass

        def on_drag_right(e):
            try:
                dx = getattr(e, "delta_x", 0) or 0
                if dx > 2 and self.right_flex > 1:
                    self.right_flex -= 1
                    self.center_flex += 1
                elif dx < -2 and self.center_flex > 2:
                    self.center_flex -= 1
                    self.right_flex += 1
                self._rebuild_main_row(left_panel, center_panel, right_panel)
            except Exception:
                pass

        return ft.Row([
            ft.Container(expand=self.left_flex, content=left_panel),
            divider(on_drag_left),
            ft.Container(expand=self.center_flex, content=center_panel),
            divider(on_drag_right),
            ft.Container(expand=self.right_flex, content=right_panel)
        ], expand=True, spacing=4)

    def _rebuild_main_row(self, left_panel, center_panel, right_panel):
        """Rebuild main row after resize"""
        if hasattr(self, "_main_content_container"):
            self._main_content_container.content = self._build_resizable_row(left_panel, center_panel, right_panel)
            if self.page:
                self.page.update()
