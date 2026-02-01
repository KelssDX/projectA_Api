import flet as ft
from flet import Icons
from src.api.auditing_client import AuditingAPIClient
from src.views.widgets.base_widget import BaseWidget
from datetime import datetime


class ComplianceScorecardWidget(BaseWidget):
    """
    Compliance Scorecard Widget
    Displays compliance metrics across regulatory frameworks with scoring
    """

    def __init__(self, page, reference_id=None, audit_universe_id=None, on_drill_down=None):
        super().__init__(
            page=page,
            title="Compliance Scorecard",
            icon=Icons.FACT_CHECK,
            description="Compliance status across regulatory frameworks"
        )
        self.reference_id = reference_id
        self.audit_universe_id = audit_universe_id
        self.on_drill_down = on_drill_down
        self.auditing_client = AuditingAPIClient()
        self.compliance_data = None

    def build_content(self):
        """Build the widget content"""
        self.content_container = ft.Container(
            content=ft.Column([
                ft.ProgressRing(width=30, height=30),
                ft.Text("Loading compliance data...", size=12)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            expand=True,
            alignment=ft.alignment.center
        )
        self.load_data()
        return self.content_container

    def load_data(self):
        """Load compliance scorecard data"""
        if hasattr(self, 'page') and self.page:
            self.page.run_task(self._load_data_async)

    async def _load_data_async(self):
        """Async data loading"""
        try:
            # Generate mock data - in production would come from API
            self.compliance_data = self._generate_mock_data()
            self._update_display()
        except Exception as e:
            print(f"Error loading compliance scorecard: {e}")
            self.content_container.content = ft.Text(f"Error: {str(e)}", color="red")
            self.page.update()

    def _generate_mock_data(self):
        """Generate mock compliance scorecard data"""
        import random
        random.seed(43)  # Consistent data

        frameworks = [
            {"name": "SOX", "fullName": "Sarbanes-Oxley", "icon": Icons.GAVEL},
            {"name": "GDPR", "fullName": "General Data Protection Regulation", "icon": Icons.SECURITY},
            {"name": "ISO 27001", "fullName": "Information Security Management", "icon": Icons.SHIELD},
            {"name": "PCI-DSS", "fullName": "Payment Card Industry", "icon": Icons.CREDIT_CARD},
            {"name": "HIPAA", "fullName": "Health Insurance Portability", "icon": Icons.LOCAL_HOSPITAL},
        ]

        scorecard = []
        for fw in frameworks:
            total_controls = random.randint(30, 100)
            compliant = random.randint(int(total_controls * 0.6), total_controls)
            partial = random.randint(0, total_controls - compliant)
            non_compliant = total_controls - compliant - partial
            
            score = round((compliant + partial * 0.5) / total_controls * 100, 1)
            
            scorecard.append({
                "framework": fw["name"],
                "fullName": fw["fullName"],
                "icon": fw["icon"],
                "totalControls": total_controls,
                "compliant": compliant,
                "partiallyCompliant": partial,
                "nonCompliant": non_compliant,
                "score": score,
                "trend": random.choice(["up", "down", "stable"]),
                "lastAssessment": f"2026-01-{random.randint(1, 25):02d}",
                "nextDue": f"2026-{random.randint(2, 6):02d}-{random.randint(1, 28):02d}"
            })

        overall_score = round(sum(fw["score"] for fw in scorecard) / len(scorecard), 1) if scorecard else 0
        
        return {
            "frameworks": scorecard,
            "summary": {
                "overallScore": overall_score,
                "totalFrameworks": len(scorecard),
                "fullyCompliant": sum(1 for fw in scorecard if fw["score"] >= 95),
                "atRisk": sum(1 for fw in scorecard if fw["score"] < 70),
                "improvingTrend": sum(1 for fw in scorecard if fw["trend"] == "up"),
            }
        }

    def _update_display(self):
        """Update the widget display with loaded data"""
        if not self.compliance_data:
            self.content_container.content = ft.Text("No data available", color=self.colors.text_secondary)
            self.page.update()
            return

        frameworks = self.compliance_data.get("frameworks", [])
        summary = self.compliance_data.get("summary", {})

        if not frameworks:
            self.content_container.content = ft.Column([
                ft.Icon(Icons.CHECKLIST, size=48, color=self.colors.text_secondary),
                ft.Text("No compliance frameworks configured", size=14),
                ft.Text("Set up regulatory frameworks to track compliance", size=12, color=self.colors.text_secondary)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER, expand=True)
            self.page.update()
            return

        def get_score_color(score):
            """Get color based on compliance score"""
            if score >= 90:
                return "#10B981"  # Green
            elif score >= 70:
                return "#F59E0B"  # Yellow/Orange
            else:
                return "#EF4444"  # Red

        def get_trend_icon(trend):
            """Get trend indicator"""
            if trend == "up":
                return (Icons.TRENDING_UP, "#10B981")
            elif trend == "down":
                return (Icons.TRENDING_DOWN, "#EF4444")
            else:
                return (Icons.TRENDING_FLAT, "#6B7280")

        # Build framework scorecards
        framework_cards = []
        for fw in frameworks:
            score = fw.get("score", 0)
            score_color = get_score_color(score)
            trend_icon, trend_color = get_trend_icon(fw.get("trend", "stable"))
            
            # Progress bar showing compliance breakdown
            total = fw.get("totalControls", 1)
            compliant_width = (fw.get("compliant", 0) / total) * 120
            partial_width = (fw.get("partiallyCompliant", 0) / total) * 120
            non_compliant_width = (fw.get("nonCompliant", 0) / total) * 120

            progress_bar = ft.Container(
                content=ft.Row([
                    ft.Container(width=compliant_width, height=6, bgcolor="#10B981"),
                    ft.Container(width=partial_width, height=6, bgcolor="#F59E0B"),
                    ft.Container(width=non_compliant_width, height=6, bgcolor="#EF4444"),
                ], spacing=0),
                border_radius=3,
                clip_behavior=ft.ClipBehavior.HARD_EDGE,
                width=120
            )

            card = ft.Container(
                content=ft.Row([
                    # Framework icon and name
                    ft.Column([
                        ft.Row([
                            ft.Icon(fw.get("icon", Icons.CHECK_CIRCLE), size=16, color=self.colors.primary),
                            ft.Text(fw.get("framework", "Unknown"), size=12, weight=ft.FontWeight.BOLD, color=self.colors.text_primary),
                        ], spacing=5),
                        progress_bar,
                        ft.Text(f"{fw.get('compliant', 0)}/{total} controls", size=9, color=self.colors.text_secondary),
                    ], spacing=4, expand=True),
                    
                    # Score display
                    ft.Column([
                        ft.Row([
                            ft.Text(f"{score:.0f}%", size=18, weight=ft.FontWeight.BOLD, color=score_color),
                            ft.Icon(trend_icon, size=14, color=trend_color),
                        ], spacing=2),
                        ft.Text("Score", size=9, color=self.colors.text_secondary),
                    ], horizontal_alignment=ft.CrossAxisAlignment.END, spacing=0),
                ], spacing=10),
                padding=8,
                border=ft.border.all(1, self.colors.border),
                border_radius=8,
                on_click=lambda e, f=fw: self._handle_framework_click(f),
                ink=True
            )
            framework_cards.append(card)

        # Overall score display
        overall_score = summary.get("overallScore", 0)
        overall_color = get_score_color(overall_score)

        overall_display = ft.Container(
            content=ft.Row([
                ft.Column([
                    ft.Text(f"{overall_score:.0f}%", size=28, weight=ft.FontWeight.BOLD, color=overall_color),
                    ft.Text("Overall Score", size=10, color=self.colors.text_secondary),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
                ft.Container(width=1, height=40, bgcolor=self.colors.border),
                ft.Column([
                    ft.Row([
                        ft.Container(width=8, height=8, bgcolor="#10B981", border_radius=4),
                        ft.Text(f"{summary.get('fullyCompliant', 0)} Compliant", size=10),
                    ], spacing=4),
                    ft.Row([
                        ft.Container(width=8, height=8, bgcolor="#EF4444", border_radius=4),
                        ft.Text(f"{summary.get('atRisk', 0)} At Risk", size=10),
                    ], spacing=4),
                    ft.Row([
                        ft.Container(width=8, height=8, bgcolor="#3B82F6", border_radius=4),
                        ft.Text(f"{summary.get('improvingTrend', 0)} Improving", size=10),
                    ], spacing=4),
                ], spacing=2),
            ], spacing=15),
            padding=10,
            bgcolor=overall_color + "10",
            border_radius=8
        )

        # Legend
        legend = ft.Row([
            self._create_legend_item("Compliant", "#10B981"),
            self._create_legend_item("Partial", "#F59E0B"),
            self._create_legend_item("Non-Compliant", "#EF4444"),
        ], spacing=15)

        self.content_container.content = ft.Column([
            overall_display,
            ft.Divider(height=1),
            legend,
            ft.Container(
                content=ft.Column(framework_cards, spacing=8, scroll=ft.ScrollMode.AUTO),
                expand=True
            ),
        ], spacing=10, expand=True)

        self.page.update()

    def _create_legend_item(self, label, color):
        """Create a legend item"""
        return ft.Row([
            ft.Container(width=12, height=6, bgcolor=color, border_radius=2),
            ft.Text(label, size=9, color=self.colors.text_secondary)
        ], spacing=4)

    def _handle_framework_click(self, framework):
        """Handle click on a framework for drill-down"""
        if self.on_drill_down:
            context = {
                "type": "compliance_framework",
                "framework": framework.get("framework"),
                "fullName": framework.get("fullName"),
                "score": framework.get("score"),
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
