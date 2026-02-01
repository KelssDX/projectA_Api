import flet as ft
from flet import Icons
from src.api.auditing_client import AuditingAPIClient
from src.views.widgets.base_widget import BaseWidget


class ControlEffectivenessWidget(BaseWidget):
    """
    Control Effectiveness Dashboard Widget
    Shows control test results with pie chart and gap analysis
    """

    def __init__(self, page, reference_id=None, audit_universe_id=None, on_drill_down=None):
        super().__init__(
            page=page,
            title="Control Effectiveness",
            icon=Icons.VERIFIED_USER,
            description="Control testing results and gaps"
        )
        self.reference_id = reference_id
        self.audit_universe_id = audit_universe_id
        self.on_drill_down = on_drill_down
        self.auditing_client = AuditingAPIClient()
        self.effectiveness_data = None

    def build_content(self):
        """Build the widget content"""
        self.content_container = ft.Container(
            content=ft.Column([
                ft.ProgressRing(width=30, height=30),
                ft.Text("Loading control data...", size=12)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            expand=True,
            alignment=ft.alignment.center
        )
        self.load_data()
        return self.content_container

    def load_data(self):
        """Load control effectiveness data"""
        if hasattr(self, 'page') and self.page:
            self.page.run_task(self._load_data_async)

    async def _load_data_async(self):
        """Async data loading"""
        try:
            # Generate mock data for now - in production would come from API
            # The API endpoint would be: get_control_effectiveness(reference_id, audit_universe_id)
            self.effectiveness_data = self._generate_mock_data()
            self._update_display()
        except Exception as e:
            print(f"Error loading control effectiveness: {e}")
            self.content_container.content = ft.Text(f"Error: {str(e)}", color="red")
            self.page.update()

    def _generate_mock_data(self):
        """Generate mock control effectiveness data"""
        import random
        random.seed(42)  # Consistent data

        return {
            "categories": [
                {"category": "Effective", "count": random.randint(25, 45), "percentage": 0, "color": "#10B981"},
                {"category": "Partially Effective", "count": random.randint(10, 20), "percentage": 0, "color": "#F59E0B"},
                {"category": "Not Effective", "count": random.randint(3, 10), "percentage": 0, "color": "#EF4444"},
                {"category": "Not Tested", "count": random.randint(5, 15), "percentage": 0, "color": "#6B7280"},
            ],
            "gaps": [
                {"controlName": "Access Control Review", "riskArea": "IT Security", "gapSeverity": "High", "gapDescription": "Quarterly review not performed"},
                {"controlName": "Segregation of Duties", "riskArea": "Finance", "gapSeverity": "Medium", "gapDescription": "Same user can approve and post"},
                {"controlName": "Backup Verification", "riskArea": "IT Operations", "gapSeverity": "High", "gapDescription": "No restoration testing in 6 months"},
            ],
            "summary": {
                "totalControls": 0,
                "testedControls": 0,
                "testingCoverage": 0,
                "overallEffectiveness": 0,
                "controlGaps": 3,
                "lastTestDate": "2026-01-15"
            }
        }

    def _update_display(self):
        """Update the widget display with loaded data"""
        if not self.effectiveness_data:
            self.content_container.content = ft.Text("No data available", color=self.colors.text_secondary)
            self.page.update()
            return

        categories = self.effectiveness_data.get("categories", [])
        gaps = self.effectiveness_data.get("gaps", [])
        summary = self.effectiveness_data.get("summary", {})

        # Calculate totals and percentages
        total = sum(c.get("count", 0) for c in categories)
        tested = total - next((c.get("count", 0) for c in categories if c.get("category") == "Not Tested"), 0)
        effective = next((c.get("count", 0) for c in categories if c.get("category") == "Effective"), 0)

        if total > 0:
            for cat in categories:
                cat["percentage"] = round(cat.get("count", 0) / total * 100, 1)

        testing_coverage = (tested / total * 100) if total > 0 else 0
        effectiveness_rate = (effective / tested * 100) if tested > 0 else 0

        # Update summary
        summary["totalControls"] = total
        summary["testedControls"] = tested
        summary["testingCoverage"] = round(testing_coverage, 1)
        summary["overallEffectiveness"] = round(effectiveness_rate, 1)

        # Build donut chart visualization
        chart_size = 100
        chart_items = []

        # Create pie segments using stacked containers
        # Simple approach: show as horizontal bar segments

        bar_segments = []
        for cat in categories:
            if cat.get("count", 0) > 0:
                width = (cat.get("count", 0) / total) * 200 if total > 0 else 0
                bar_segments.append(
                    ft.Container(
                        width=width,
                        height=24,
                        bgcolor=cat.get("color", "#6B7280"),
                        tooltip=f"{cat.get('category')}: {cat.get('count')} ({cat.get('percentage', 0):.0f}%)"
                    )
                )

        chart_bar = ft.Container(
            content=ft.Row(bar_segments, spacing=0),
            border_radius=6,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            width=200
        )

        # Legend
        legend_items = []
        for cat in categories:
            legend_items.append(
                ft.Row([
                    ft.Container(width=10, height=10, bgcolor=cat.get("color"), border_radius=2),
                    ft.Text(f"{cat.get('category')}: {cat.get('count')}", size=10, color=self.colors.text_secondary),
                ], spacing=4)
            )

        legend = ft.Column(legend_items, spacing=4)

        # Effectiveness gauge
        eff_color = "#10B981" if effectiveness_rate >= 80 else ("#F59E0B" if effectiveness_rate >= 60 else "#EF4444")

        effectiveness_display = ft.Container(
            content=ft.Column([
                ft.Text(f"{effectiveness_rate:.0f}%", size=32, weight=ft.FontWeight.BOLD, color=eff_color),
                ft.Text("Effective", size=10, color=self.colors.text_secondary),
                ft.ProgressBar(value=effectiveness_rate / 100, color=eff_color, bgcolor=self.colors.text_secondary + "30", width=80),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
            padding=10
        )

        # Gaps section (if any)
        gaps_section = None
        if gaps:
            gap_items = []
            for gap in gaps[:3]:  # Show top 3 gaps
                severity_color = {"High": "#EF4444", "Medium": "#F59E0B", "Low": "#10B981"}.get(gap.get("gapSeverity"), "#6B7280")
                gap_items.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Container(width=4, height=30, bgcolor=severity_color, border_radius=2),
                            ft.Column([
                                ft.Text(gap.get("controlName", "Unknown"), size=10, weight=ft.FontWeight.BOLD, color=self.colors.text_primary),
                                ft.Text(gap.get("gapDescription", ""), size=9, color=self.colors.text_secondary),
                            ], spacing=0, expand=True),
                        ], spacing=8),
                        padding=ft.padding.symmetric(vertical=4),
                        on_click=lambda e, g=gap: self._handle_gap_click(g)
                    )
                )

            gaps_section = ft.Column([
                ft.Row([
                    ft.Icon(Icons.WARNING_AMBER, size=14, color="#F59E0B"),
                    ft.Text(f"Control Gaps ({len(gaps)})", size=11, weight=ft.FontWeight.BOLD, color=self.colors.text_primary),
                ], spacing=5),
                ft.Column(gap_items, spacing=2),
            ], spacing=5)

        # Summary metrics
        metrics_row = ft.Row([
            ft.Container(
                content=ft.Column([
                    ft.Text(str(total), size=18, weight=ft.FontWeight.BOLD, color=self.colors.primary),
                    ft.Text("Total", size=9, color=self.colors.text_secondary)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
                expand=True
            ),
            ft.Container(
                content=ft.Column([
                    ft.Text(f"{testing_coverage:.0f}%", size=18, weight=ft.FontWeight.BOLD, color="#3B82F6"),
                    ft.Text("Tested", size=9, color=self.colors.text_secondary)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
                expand=True
            ),
            ft.Container(
                content=ft.Column([
                    ft.Text(str(len(gaps)), size=18, weight=ft.FontWeight.BOLD, color="#F59E0B"),
                    ft.Text("Gaps", size=9, color=self.colors.text_secondary)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
                expand=True
            ),
        ])

        # Main layout
        content_items = [
            ft.Row([
                ft.Column([chart_bar, legend], spacing=10, expand=True),
                effectiveness_display,
            ], spacing=10),
            ft.Divider(height=1),
            metrics_row,
        ]

        if gaps_section:
            content_items.extend([ft.Divider(height=1), gaps_section])

        self.content_container.content = ft.Column(
            content_items,
            spacing=10,
            expand=True,
            scroll=ft.ScrollMode.AUTO
        )

        self.page.update()

    def _handle_gap_click(self, gap):
        """Handle click on a control gap"""
        if self.on_drill_down:
            context = {
                "type": "control_gap",
                "controlName": gap.get("controlName"),
                "riskArea": gap.get("riskArea"),
                "referenceId": self.reference_id,
                "auditUniverseId": self.audit_universe_id
            }
            self.on_drill_down(context)

    def refresh(self):
        """Refresh the widget data"""
        self.load_data()

    def set_filters(self, reference_id=None, audit_universe_id=None):
        """Update filters and refresh"""
        if reference_id is not None:
            self.reference_id = reference_id
        if audit_universe_id is not None:
            self.audit_universe_id = audit_universe_id
        self.refresh()
