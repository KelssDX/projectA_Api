import flet as ft
from flet import Icons
from src.api.auditing_client import AuditingAPIClient
from src.views.widgets.base_widget import BaseWidget


class DepartmentComparisonWidget(BaseWidget):
    """
    Department Risk Comparison Widget
    Compares risk metrics across departments with bar charts and rankings
    """

    def __init__(self, page, reference_id=None, audit_universe_id=None, on_drill_down=None):
        super().__init__(
            page=page,
            title="Department Risk Comparison",
            icon=Icons.COMPARE_ARROWS,
            description="Risk comparison across departments"
        )
        self.reference_id = reference_id
        self.audit_universe_id = audit_universe_id
        self.on_drill_down = on_drill_down
        self.auditing_client = AuditingAPIClient()
        self.comparison_data = None
        self.sort_by = "totalRisks"  # Default sort

    def build_content(self):
        """Build the widget content"""
        self.content_container = ft.Container(
            content=ft.Column([
                ft.ProgressRing(width=30, height=30),
                ft.Text("Loading department data...", size=12)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            expand=True,
            alignment=ft.alignment.center
        )
        self.load_data()
        return self.content_container

    def load_data(self):
        """Load department comparison data"""
        if hasattr(self, 'page') and self.page:
            self.page.run_task(self._load_data_async)

    async def _load_data_async(self):
        """Async data loading"""
        try:
            # Get departments data - we'll calculate comparison metrics
            departments = await self.auditing_client.get_departments()

            # For now, create mock comparison data based on departments
            # In production, this would come from a dedicated API endpoint
            self.comparison_data = self._build_comparison_data(departments)
            self._update_display()
        except Exception as e:
            print(f"Error loading department comparison: {e}")
            self.content_container.content = ft.Text(f"Error: {str(e)}", color="red")
            self.page.update()

    def _build_comparison_data(self, departments):
        """Build comparison data from departments"""
        if not departments:
            return {"departments": [], "summary": {}}

        # Map risk levels to scores for comparison
        risk_scores = {"High": 3, "Medium": 2, "Low": 1}

        dept_data = []
        for dept in departments[:10]:  # Limit to top 10
            risk_level = dept.get("risk_level", "Medium")
            assessments = dept.get("assessments", 0)

            # Generate realistic-looking metrics
            import random
            random.seed(dept.get("id", 0))  # Consistent random per department

            dept_data.append({
                "departmentId": dept.get("id"),
                "departmentName": dept.get("name", "Unknown"),
                "departmentHead": dept.get("head", "Unknown"),
                "totalRisks": random.randint(5, 50),
                "criticalRisks": random.randint(0, 5),
                "highRisks": random.randint(2, 15),
                "mediumRisks": random.randint(5, 20),
                "lowRisks": random.randint(3, 15),
                "averageResidualScore": round(random.uniform(5, 18), 1),
                "riskReduction": round(random.uniform(10, 45), 1),
                "controlEffectiveness": round(random.uniform(60, 95), 1),
                "openFindings": random.randint(0, 12),
                "riskScore": risk_scores.get(risk_level, 2) * 33,
            })

        # Sort by total risks
        dept_data.sort(key=lambda x: x.get(self.sort_by, 0), reverse=True)

        # Calculate summary
        total_depts = len(dept_data)
        if total_depts > 0:
            avg_risk = sum(d["averageResidualScore"] for d in dept_data) / total_depts
            avg_effectiveness = sum(d["controlEffectiveness"] for d in dept_data) / total_depts
            highest_risk = max(dept_data, key=lambda x: x["averageResidualScore"])
            lowest_risk = min(dept_data, key=lambda x: x["averageResidualScore"])
        else:
            avg_risk = 0
            avg_effectiveness = 0
            highest_risk = {}
            lowest_risk = {}

        return {
            "departments": dept_data,
            "summary": {
                "totalDepartments": total_depts,
                "highestRiskDepartment": highest_risk.get("departmentName", "N/A"),
                "lowestRiskDepartment": lowest_risk.get("departmentName", "N/A"),
                "averageRiskScore": round(avg_risk, 1),
                "averageControlEffectiveness": round(avg_effectiveness, 1)
            }
        }

    def _update_display(self):
        """Update the widget display with loaded data"""
        if not self.comparison_data:
            self.content_container.content = ft.Text("No data available", color=self.colors.text_secondary)
            self.page.update()
            return

        departments = self.comparison_data.get("departments", [])
        summary = self.comparison_data.get("summary", {})

        if not departments:
            self.content_container.content = ft.Column([
                ft.Icon(Icons.BUSINESS, size=48, color=self.colors.text_secondary),
                ft.Text("No departments found", size=14),
                ft.Text("Add departments to see comparison", size=12, color=self.colors.text_secondary)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER, expand=True)
            self.page.update()
            return

        # Find max values for scaling
        max_risks = max(d.get("totalRisks", 1) for d in departments)
        max_score = max(d.get("averageResidualScore", 1) for d in departments)

        # Build comparison bars
        dept_rows = []
        for i, dept in enumerate(departments[:6]):  # Show top 6
            name = dept.get("departmentName", "Unknown")
            total_risks = dept.get("totalRisks", 0)
            avg_score = dept.get("averageResidualScore", 0)
            critical = dept.get("criticalRisks", 0)
            high = dept.get("highRisks", 0)
            effectiveness = dept.get("controlEffectiveness", 0)

            # Risk bar width (scaled to container)
            risk_bar_width = (total_risks / max_risks) * 150 if max_risks > 0 else 0

            # Color based on average score
            if avg_score >= 15:
                score_color = "#EF4444"
            elif avg_score >= 10:
                score_color = "#F59E0B"
            else:
                score_color = "#10B981"

            row = ft.Container(
                content=ft.Row([
                    # Rank
                    ft.Container(
                        content=ft.Text(f"#{i+1}", size=10, color=self.colors.text_secondary, weight=ft.FontWeight.BOLD),
                        width=25
                    ),
                    # Department name
                    ft.Container(
                        content=ft.Text(
                            name[:12] + "..." if len(name) > 12 else name,
                            size=11,
                            weight=ft.FontWeight.BOLD,
                            color=self.colors.text_primary
                        ),
                        width=90,
                        tooltip=name
                    ),
                    # Risk bar with segments
                    ft.Container(
                        content=ft.Stack([
                            # Background
                            ft.Container(
                                width=150,
                                height=16,
                                bgcolor=self.colors.text_secondary + "20",
                                border_radius=3
                            ),
                            # Risk bar
                            ft.Container(
                                width=risk_bar_width,
                                height=16,
                                bgcolor=score_color + "80",
                                border_radius=3
                            ),
                            # Total count
                            ft.Container(
                                content=ft.Text(str(total_risks), size=10, color=self.colors.text_primary),
                                width=150,
                                height=16,
                                alignment=ft.alignment.center_right,
                                padding=ft.padding.only(right=5)
                            )
                        ]),
                        width=150
                    ),
                    # Critical/High indicators
                    ft.Container(
                        content=ft.Row([
                            ft.Container(
                                content=ft.Text(str(critical), size=9, color="white"),
                                bgcolor="#DC2626" if critical > 0 else self.colors.text_secondary + "40",
                                width=20,
                                height=16,
                                border_radius=3,
                                alignment=ft.alignment.center,
                                tooltip="Critical"
                            ),
                            ft.Container(
                                content=ft.Text(str(high), size=9, color="white"),
                                bgcolor="#EA580C" if high > 0 else self.colors.text_secondary + "40",
                                width=20,
                                height=16,
                                border_radius=3,
                                alignment=ft.alignment.center,
                                tooltip="High"
                            ),
                        ], spacing=2),
                        width=45
                    ),
                ], spacing=8),
                padding=ft.padding.symmetric(vertical=4),
                on_click=lambda e, d=dept: self._handle_drill_down(d),
            )
            dept_rows.append(row)

        # Header row
        header = ft.Row([
            ft.Container(width=25),
            ft.Text("Department", size=10, color=self.colors.text_secondary, width=90),
            ft.Text("Total Risks", size=10, color=self.colors.text_secondary, width=150),
            ft.Text("C/H", size=10, color=self.colors.text_secondary, width=45),
        ], spacing=8)

        # Summary section
        summary_row = ft.Row([
            ft.Container(
                content=ft.Column([
                    ft.Text(str(summary.get("totalDepartments", 0)), size=20, weight=ft.FontWeight.BOLD, color=self.colors.primary),
                    ft.Text("Depts", size=9, color=self.colors.text_secondary)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
                expand=True
            ),
            ft.Container(
                content=ft.Column([
                    ft.Text(f"{summary.get('averageRiskScore', 0):.1f}", size=20, weight=ft.FontWeight.BOLD, color="#F59E0B"),
                    ft.Text("Avg Score", size=9, color=self.colors.text_secondary)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
                expand=True
            ),
            ft.Container(
                content=ft.Column([
                    ft.Text(f"{summary.get('averageControlEffectiveness', 0):.0f}%", size=20, weight=ft.FontWeight.BOLD, color="#10B981"),
                    ft.Text("Ctrl Eff", size=9, color=self.colors.text_secondary)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
                expand=True
            ),
        ])

        self.content_container.content = ft.Column([
            header,
            ft.Divider(height=1),
            ft.Column(dept_rows, spacing=0, scroll=ft.ScrollMode.AUTO, expand=True),
            ft.Divider(height=1),
            summary_row
        ], spacing=5, expand=True)

        self.page.update()

    def _handle_drill_down(self, department):
        """Handle click on a department for drill-down"""
        if self.on_drill_down:
            context = {
                "type": "department_comparison",
                "departmentId": department.get("departmentId"),
                "departmentName": department.get("departmentName"),
                "referenceId": self.reference_id
            }
            self.on_drill_down(context)

    def refresh(self):
        """Refresh the widget data"""
        self.load_data()

    def set_sort(self, sort_by):
        """Change sort order and refresh"""
        self.sort_by = sort_by
        if self.comparison_data:
            departments = self.comparison_data.get("departments", [])
            departments.sort(key=lambda x: x.get(sort_by, 0), reverse=True)
            self._update_display()
