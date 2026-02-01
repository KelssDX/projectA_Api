import flet as ft
from flet import Icons
from src.api.auditing_client import AuditingAPIClient
from src.views.widgets.base_widget import BaseWidget


class HeatmapEmbedWidget(BaseWidget):
    """
    Embedded Heatmap Widget for the Analytical Dashboard
    Displays a compact risk heatmap with drill-down capabilities
    Supports hierarchy filtering and compact mode for dashboard view
    """

    def __init__(self, page, reference_id=None, audit_universe_id=None, on_drill_down=None, compact_mode=False):
        """
        Args:
            page: Flet page instance
            reference_id: Assessment reference ID to filter by
            audit_universe_id: Audit universe node ID for hierarchy filtering
            on_drill_down: Callback for drill-down actions
            compact_mode: If True, uses smaller cell sizes for dashboard embedding
        """
        super().__init__(
            page=page,
            title="Risk Heatmap",
            icon=Icons.GRID_ON,
            description="Visual risk heat map showing impact vs likelihood"
        )
        self.reference_id = reference_id
        self.audit_universe_id = audit_universe_id
        self.on_drill_down = on_drill_down
        self.compact_mode = compact_mode
        self.auditing_client = AuditingAPIClient()
        self.heatmap_data = None
        self.selected_level = None
        
        # Adjust sizes based on compact mode
        self.cell_size = 30 if compact_mode else 40
        self.font_size = 10 if compact_mode else 12

    def build_content(self):
        """Build the widget content"""
        self.content_container = ft.Container(
            content=ft.Column([
                ft.ProgressRing(width=30, height=30),
                ft.Text("Loading heatmap data...", size=12)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            expand=True,
            alignment=ft.alignment.center
        )
        self.load_data()
        return self.content_container

    def load_data(self):
        """Load heatmap data"""
        if hasattr(self, 'page') and self.page:
            self.page.run_task(self._load_data_async)

    async def _load_data_async(self):
        """Async data loading"""
        try:
            self.heatmap_data = await self.auditing_client.get_heatmap_data(
                reference_id=self.reference_id,
                audit_universe_id=self.audit_universe_id
            )
            self._update_display()
        except Exception as e:
            print(f"Error loading heatmap: {e}")
            self.content_container.content = ft.Text(f"Error: {str(e)}", color="red")
            self.page.update()
            print(f"Error loading heatmap: {e}")
            self.content_container.content = ft.Text(f"Error: {str(e)}", color="red")
            self.page.update()

    def _update_display(self):
        """Update the widget display with loaded data"""
        if not self.heatmap_data:
            self.content_container.content = ft.Text("No heatmap data available", color=self.colors.text_secondary)
            self.page.update()
            return
        # Normalize API payloads (heatmapGrid vs cells/summary)
        cells, summary = self._normalize_heatmap_data(self.heatmap_data)

        # Define risk levels and colors
        risk_colors = {
            "Critical": "#DC2626",
            "High": "#EF4444",
            "Medium": "#F59E0B",
            "Low": "#10B981",
            "Very Low": "#6B7280"
        }

        # Create 5x5 heatmap grid (Impact x Likelihood)
        grid_size = 5
        cell_size = self.cell_size  # Use compact mode size

        # Initialize grid with cell data
        cell_matrix = [[{"count": 0, "level": ""} for _ in range(grid_size)] for _ in range(grid_size)]
        
        for cell in cells:
            impact = cell.get("impact", 1) - 1  # 0-indexed
            likelihood = cell.get("likelihood", 1) - 1  # 0-indexed
            count = cell.get("count", 0)
            level = cell.get("riskLevel", "")
            if 0 <= impact < grid_size and 0 <= likelihood < grid_size:
                cell_matrix[grid_size - 1 - impact][likelihood] = {"count": count, "level": level}

        # Build the heatmap grid
        grid_rows = []
        
        # Y-axis labels (Impact)
        impact_labels = ["5", "4", "3", "2", "1"]
        
        for row_idx, row_data in enumerate(cell_matrix):
            row_controls = []
            # Add impact label
            row_controls.append(
                ft.Container(
                    content=ft.Text(impact_labels[row_idx], size=10, color=self.colors.text_secondary),
                    width=15,
                    alignment=ft.alignment.center
                )
            )
            
            for col_idx, cell_data in enumerate(row_data):
                count = cell_data["count"]
                level = cell_data["level"]
                bg_color = risk_colors.get(level, "#E5E7EB")
                
                # Determine text color for contrast
                text_color = "#FFFFFF" if level in ["Critical", "High", "Medium"] else self.colors.text_primary
                
                cell = ft.Container(
                    width=cell_size,
                    height=cell_size,
                    bgcolor=bg_color if count > 0 else "#F3F4F6",
                    border_radius=4,
                    border=ft.border.all(1, self.colors.border),
                    content=ft.Text(
                        str(count) if count > 0 else "",
                        size=12,
                        weight=ft.FontWeight.BOLD,
                        color=text_color if count > 0 else "#9CA3AF"
                    ),
                    alignment=ft.alignment.center,
                    on_click=lambda e, i=grid_size-row_idx, l=col_idx+1, c=count, lv=level: self._handle_cell_click(i, l, c, lv) if c > 0 else None,
                    tooltip=f"Impact: {grid_size-row_idx}, Likelihood: {col_idx+1}\nRisk Level: {level}\nCount: {count}" if count > 0 else None
                )
                row_controls.append(cell)
            
            grid_rows.append(ft.Row(row_controls, spacing=3))

        # X-axis labels (Likelihood)
        likelihood_row = ft.Row([
            ft.Container(width=15),  # Spacer for y-axis labels
            *[ft.Container(
                content=ft.Text(str(i), size=10, color=self.colors.text_secondary),
                width=cell_size,
                alignment=ft.alignment.center
            ) for i in range(1, grid_size + 1)]
        ], spacing=3)

        # Axis titles
        impact_title = ft.Container(
            content=ft.Text("Impact", size=10, color=self.colors.text_secondary),
            rotate=ft.Rotate(-1.5708),  # -90 degrees
            width=20,
            height=50
        )
        
        likelihood_title = ft.Text("Likelihood →", size=10, color=self.colors.text_secondary)

        # Build grid container
        grid_column = ft.Column(grid_rows + [likelihood_row, ft.Container(content=likelihood_title, alignment=ft.alignment.center)], spacing=3)

        # Summary section
        total_risks = summary.get("totalRisks", 0)
        critical_count = summary.get("critical", 0)
        high_count = summary.get("high", 0)
        medium_count = summary.get("medium", 0)
        low_count = summary.get("low", 0)

        summary_row = ft.Row([
            self._create_summary_chip("Critical", critical_count, "#DC2626"),
            self._create_summary_chip("High", high_count, "#EF4444"),
            self._create_summary_chip("Medium", medium_count, "#F59E0B"),
            self._create_summary_chip("Low", low_count, "#10B981"),
        ], spacing=8, wrap=True)

        # Legend
        legend = ft.Row([
            self._create_legend_item("Critical", "#DC2626"),
            self._create_legend_item("High", "#EF4444"),
            self._create_legend_item("Medium", "#F59E0B"),
            self._create_legend_item("Low", "#10B981"),
        ], spacing=10, wrap=True)

        self.content_container.content = ft.Column([
            ft.Container(
                content=ft.Row([
                    grid_column,
                ], alignment=ft.MainAxisAlignment.CENTER),
                padding=10
            ),
            ft.Divider(height=1),
            legend,
            ft.Divider(height=1),
            summary_row,
        ], spacing=8, expand=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

        self.page.update()

    def _normalize_heatmap_data(self, data):
        """
        Normalize heatmap payloads to {cells, summary} for the widget.
        Supports:
        - New widget format: {cells: [{impact, likelihood, count, riskLevel}], summary: {...}}
        - API format: {heatmapGrid: {ImpactLabel: {LikelihoodLabel: count}}}
        """
        if not isinstance(data, dict):
            return [], {"critical": 0, "high": 0, "medium": 0, "low": 0, "totalRisks": 0}

        cells = data.get("cells")
        summary = data.get("summary")

        # Build from heatmapGrid if present
        if not cells and isinstance(data.get("heatmapGrid"), dict):
            grid = data.get("heatmapGrid") or {}
            cells = []
            for impact_label, likelihoods in grid.items():
                if not isinstance(likelihoods, dict):
                    continue
                impact_score = self._map_level_to_score(impact_label, is_impact=True)
                for likelihood_label, count in likelihoods.items():
                    likelihood_score = self._map_level_to_score(likelihood_label, is_impact=False)
                    if impact_score is None or likelihood_score is None:
                        continue
                    risk_level = self._calculate_risk_level(impact_score, likelihood_score)
                    cells.append({
                        "impact": impact_score,
                        "likelihood": likelihood_score,
                        "count": count or 0,
                        "riskLevel": risk_level
                    })

        # Ensure cells is a list
        if not isinstance(cells, list):
            cells = []

        # Fill in missing risk levels and compute summary if needed
        normalized_cells = []
        for cell in cells:
            if not isinstance(cell, dict):
                continue
            impact = cell.get("impact")
            likelihood = cell.get("likelihood")
            count = cell.get("count", 0) or 0
            level = cell.get("riskLevel")
            if level is None and isinstance(impact, int) and isinstance(likelihood, int):
                level = self._calculate_risk_level(impact, likelihood)
            normalized_cells.append({
                "impact": impact,
                "likelihood": likelihood,
                "count": count,
                "riskLevel": level
            })

        if not isinstance(summary, dict):
            summary = self._calculate_summary(normalized_cells)
        else:
            # Ensure expected keys exist
            summary = {
                "critical": summary.get("critical", 0),
                "high": summary.get("high", 0),
                "medium": summary.get("medium", 0),
                "low": summary.get("low", 0),
                "totalRisks": summary.get("totalRisks", 0)
            }

        return normalized_cells, summary

    def _map_level_to_score(self, label, is_impact):
        """Map impact/likelihood labels to 1-5 scores."""
        if label is None:
            return None
        # Numeric or numeric string
        try:
            num = int(str(label).strip())
            if 1 <= num <= 5:
                return num
        except Exception:
            pass

        text = str(label).strip().lower()
        if is_impact:
            if "negligible" in text or "very low" in text:
                return 1
            if "minor" in text or ("low" in text and "very low" not in text):
                return 2
            if "moderate" in text or "medium" in text:
                return 3
            if "major" in text or "significant" in text or ("high" in text and "very high" not in text):
                return 4
            if "catastrophic" in text or "very high" in text or "extreme" in text:
                return 5
        else:
            if "rare" in text or "very low" in text:
                return 1
            if "unlikely" in text or ("low" in text and "very low" not in text):
                return 2
            if "possible" in text or "medium" in text:
                return 3
            if "probable" in text or ("high" in text and "very high" not in text):
                return 4
            if "certain" in text or "very high" in text:
                return 5

        return None

    def _calculate_risk_level(self, impact, likelihood):
        """Calculate risk level based on numeric impact/likelihood."""
        try:
            score = int(impact) * int(likelihood)
        except Exception:
            return ""
        if score >= 20:
            return "Critical"
        if score >= 15:
            return "High"
        if score >= 10:
            return "Medium"
        if score >= 5:
            return "Low"
        return "Very Low"

    def _calculate_summary(self, cells):
        """Compute summary counts from cells."""
        summary = {"critical": 0, "high": 0, "medium": 0, "low": 0, "totalRisks": 0}
        for cell in cells:
            if not isinstance(cell, dict):
                continue
            count = cell.get("count", 0) or 0
            level = (cell.get("riskLevel") or "").lower()
            if level == "critical":
                summary["critical"] += count
            elif level == "high":
                summary["high"] += count
            elif level == "medium":
                summary["medium"] += count
            elif level == "low":
                summary["low"] += count
            summary["totalRisks"] += count
        return summary

    def _create_legend_item(self, label, color):
        """Create a legend item"""
        return ft.Row([
            ft.Container(width=12, height=12, bgcolor=color, border_radius=2),
            ft.Text(label, size=9, color=self.colors.text_secondary)
        ], spacing=4)

    def _create_summary_chip(self, label, count, color):
        """Create a summary chip"""
        return ft.Container(
            content=ft.Row([
                ft.Container(width=8, height=8, bgcolor=color, border_radius=4),
                ft.Text(f"{label}: {count}", size=10, color=self.colors.text_primary)
            ], spacing=4),
            padding=ft.padding.symmetric(horizontal=8, vertical=4),
            border_radius=12,
            bgcolor=color + "20"
        )

    def _handle_cell_click(self, impact, likelihood, count, level):
        """Handle click on a heatmap cell for drill-down"""
        if self.on_drill_down:
            context = {
                "type": "heatmap_cell",
                "impact": impact,
                "likelihood": likelihood,
                "count": count,
                "riskLevel": level,
                "referenceId": self.reference_id
            }
            self.on_drill_down(context)

    def refresh(self):
        """Refresh the widget data"""
        self.load_data()

    def set_reference(self, reference_id):
        """Update reference ID and refresh"""
        self.reference_id = reference_id
        self.refresh()

    def set_hierarchy_filter(self, audit_universe_id):
        """
        Update hierarchy filter (sync with HierarchySelector).
        This filters the heatmap data to show only risks within the selected
        audit universe node and its children.
        """
        self.audit_universe_id = audit_universe_id
        self.refresh()

    def set_compact_mode(self, compact):
        """Toggle compact mode display"""
        self.compact_mode = compact
        self.cell_size = 30 if compact else 40
        self.font_size = 10 if compact else 12
        self.refresh()

    def set_filters(self, reference_id=None, audit_universe_id=None):
        """Update multiple filters and refresh once"""
        if reference_id is not None:
            self.reference_id = reference_id
        if audit_universe_id is not None:
            self.audit_universe_id = audit_universe_id
        self.refresh()

