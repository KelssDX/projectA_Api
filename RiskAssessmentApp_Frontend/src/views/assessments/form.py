import flet as ft
from flet import Icons
from src.models.assessment import Assessment
from datetime import datetime
import asyncio
from src.controllers.assessment_controller import AssessmentController


class AssessmentFormView(ft.Container):
    def __init__(self, page, user, assessment=None, on_save=None, on_cancel=None):
        super().__init__()
        self.page = page
        self.user = user
        self.assessment = assessment or Assessment(
            id=None,
            assessment_date=datetime.now().date(),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        self.on_save_callback = on_save
        self.on_cancel_callback = on_cancel
        self.expand = True
        self.assessment_controller = AssessmentController()

        # Lookup data
        self.likelihoods = []
        self.impacts = []
        self.controls = []
        self.outcomes = []
        self.evidence_items = []
        self.categories = []
        self.secondary_risks = []
        self.data_frequencies = []
        self.outcome_likelihoods = []
        # Keep raw lookup items for id resolution
        self._likelihood_items_raw = []
        self._impact_items_raw = []
        self._category_items_raw = []
        self._secondary_items_raw = []
        self._data_freq_items_raw = []
        self._outcome_likelihood_items_raw = []

        # Department and project: free text to avoid mock data

        # Define risk factor UI elements here for easy access later
        self.risk_factors_container = ft.Column(spacing=10)
        # New: full risks sheet container
        self.risks_container = ft.Column(spacing=16)
        self.risk_rows = []  # list of dicts of controls per row

        # Create form fields
        self.title_field = ft.TextField(
            label="Title",
            value=self.assessment.title or "",
            border=ft.InputBorder.OUTLINE,
            expand=True
        )

        self.department_dropdown = ft.Dropdown(label="Department", width=300, options=[], border=ft.InputBorder.OUTLINE)

        self.project_dropdown = ft.Dropdown(label="Project (Optional)", width=300, options=[], border=ft.InputBorder.OUTLINE)

        # Format date for date picker
        assessment_date = self.assessment.assessment_date
        date_value = None
        if hasattr(assessment_date, "strftime"):
            date_value = assessment_date.strftime("%Y-%m-%d")

        self.date_picker = ft.TextField(
            label="Assessment Date",
            value=date_value,
            border=ft.InputBorder.OUTLINE,
            width=300,
            hint_text="YYYY-MM-DD"
        )

        self.scope_field = ft.TextField(
            label="Scope",
            value=self.assessment.scope or "",
            multiline=True,
            min_lines=3,
            max_lines=5,
            border=ft.InputBorder.OUTLINE,
            expand=True
        )

        self.findings_field = ft.TextField(
            label="Findings",
            value=self.assessment.findings or "",
            multiline=True,
            min_lines=3,
            max_lines=5,
            border=ft.InputBorder.OUTLINE,
            expand=True
        )

        self.recommendations_field = ft.TextField(
            label="Recommendations",
            value=self.assessment.recommendations or "",
            multiline=True,
            min_lines=3,
            max_lines=5,
            border=ft.InputBorder.OUTLINE,
            expand=True
        )

        # Create header
        header = ft.Container(
            height=60,
            bgcolor=None,
            border=ft.border.only(bottom=ft.BorderSide(1, "#e6e9ed")),
            padding=ft.padding.only(left=30, right=30),
            content=ft.Row([
                ft.IconButton(
                    icon=Icons.ARROW_BACK,
                    icon_color=None,
                    tooltip="Back to assessments",
                    on_click=self.cancel_form
                ),
                ft.Text(
                    "New Assessment" if self.assessment.id is None else f"Edit Assessment: {self.assessment.id}",
                    size=22,
                    weight=ft.FontWeight.BOLD
                ),
                ft.Container(expand=True),
                ft.Container(
                    margin=ft.margin.only(left=20),
                    content=ft.Container(
                        width=30,
                        height=30,
                        border_radius=15,
                        bgcolor=None,
                        alignment=ft.alignment.center,
                        content=ft.Text(
                            self.user["username"][0].upper() if isinstance(self.user,
                                                                           dict) and "username" in self.user else "A",
                            color=None,
                            weight=ft.FontWeight.BOLD
                        )
                    )
                )
            ])
        )

        # Build tabs content
        overview_tab = ft.Container(
            padding=ft.padding.all(20),
            content=ft.Column([
                ft.Text("Basic Information", size=16, weight=ft.FontWeight.BOLD),
                self.title_field,
                ft.Row([self.department_dropdown, ft.Container(width=20), self.project_dropdown]),
                self.date_picker,
                ft.Text("Scope", size=14, weight=ft.FontWeight.BOLD),
                self.scope_field,
                ft.Text("Findings", size=14, weight=ft.FontWeight.BOLD),
                self.findings_field,
                ft.Text("Recommendations", size=14, weight=ft.FontWeight.BOLD),
                self.recommendations_field,
            ], spacing=10)
        )

        factors_tab = ft.Container(
            padding=ft.padding.all(20),
            content=ft.Column([
                ft.Row([
                    ft.Text("Risk Factors (simple scoring)", size=16, weight=ft.FontWeight.BOLD),
                    ft.Container(expand=True),
                    ft.ElevatedButton(text="Add Factor", icon=Icons.ADD, on_click=self.add_risk_factor)
                ]),
                self.risk_factors_container
            ], spacing=10)
        )

        # Placeholders for likelihood/impact dropdowns (populated after API fetch)
        self.likelihood_dropdown = ft.Dropdown(label="Likelihood", width=250, options=[], border=ft.InputBorder.OUTLINE)
        self.impact_dropdown = ft.Dropdown(label="Impact", width=250, options=[], border=ft.InputBorder.OUTLINE)

        def on_matrix_change(e):
            # Recompute risk level label based on selections
            likelihood = self.likelihood_dropdown.value
            impact = self.impact_dropdown.value
            if likelihood and impact:
                # Map to a simple score to update assessment level label
                level = self.estimate_matrix_level(impact, likelihood)
                self.assessment.risk_level = level
                self.page.update()

        self.likelihood_dropdown.on_change = on_matrix_change
        self.impact_dropdown.on_change = on_matrix_change

        matrix_tab = ft.Container(
            padding=ft.padding.all(20),
            content=ft.Column([
                ft.Text("Risk Matrix", size=16, weight=ft.FontWeight.BOLD),
                ft.Row([self.likelihood_dropdown, self.impact_dropdown], spacing=20),
                ft.Text("Calculated", size=14, weight=ft.FontWeight.BOLD),
                ft.Row([
                    ft.Container(padding=10, content=ft.Column([
                        ft.Text("Risk Score", size=12),
                        ft.Text(f"{self.assessment.risk_score:.1f}" if self.assessment.risk_score is not None else "N/A", size=22, weight=ft.FontWeight.BOLD)
                    ])),
                    ft.Container(padding=10, bgcolor=self.get_risk_color(self.assessment.risk_level), border_radius=5, content=ft.Column([
                        ft.Text("Risk Level", size=12, color="white"),
                        ft.Text(self.assessment.risk_level or "N/A", size=22, weight=ft.FontWeight.BOLD, color="white")
                    ]))
                ], spacing=20)
            ], spacing=10)
        )

        evidence_tab = ft.Container(
            padding=ft.padding.all(20),
            content=ft.Column([
                ft.Text("Evidence", size=16, weight=ft.FontWeight.BOLD),
                ft.Text("Linked evidence from API (read-only)")
            ])
        )

        controls_tab = ft.Container(
            padding=ft.padding.all(20),
            content=ft.Column([
                ft.Text("Controls", size=16, weight=ft.FontWeight.BOLD),
                ft.Text("Available controls from API (read-only)")
            ])
        )

        # Attributes tab with modern grid of dropdowns
        self.risk_category_dropdown = ft.Dropdown(label="Risk Category", width=300, options=[], border=ft.InputBorder.OUTLINE)
        self.key_secondary_dropdown = ft.Dropdown(label="Key Secondary Risk", width=300, options=[], border=ft.InputBorder.OUTLINE)
        self.data_frequency_dropdown = ft.Dropdown(label="Data Frequency", width=300, options=[], border=ft.InputBorder.OUTLINE)
        self.frequency_dropdown = ft.Dropdown(label="Frequency", width=300, options=[], border=ft.InputBorder.OUTLINE)
        self.outcome_likelihood_dropdown = ft.Dropdown(label="Outcome Likelihood", width=300, options=[], border=ft.InputBorder.OUTLINE)

        attributes_tab = ft.Container(
            padding=ft.padding.all(20),
            content=ft.Column([
                ft.Text("Attributes", size=16, weight=ft.FontWeight.BOLD),
                ft.Row([
                    self.risk_category_dropdown,
                    ft.Container(width=20),
                    self.key_secondary_dropdown
                ], spacing=20),
                ft.Row([
                    self.data_frequency_dropdown,
                    ft.Container(width=20),
                    self.frequency_dropdown
                ], spacing=20),
                ft.Row([
                    self.outcome_likelihood_dropdown,
                    ft.Container(width=20),
                    ft.Container(expand=True)
                ], spacing=20)
            ], spacing=12)
        )

        # Risks sheet tab (Excel-aligned)
        def add_risk_row(_=None, initial=None):
            idx = len(self.risk_rows)
            business_obj = ft.TextField(label="Business objective", expand=True)
            main_process = ft.TextField(label="Main process", width=260)
            sub_process = ft.TextField(label="Sub process", width=260)

            key_risk = ft.TextField(label="Key risk and factors", multiline=True, min_lines=2, max_lines=4, expand=True)
            like_dd = ft.Dropdown(label="Likelihood", width=220, options=[ft.dropdown.Option(v) for v in self.likelihoods])
            impact_dd = ft.Dropdown(label="Impact", width=220, options=[ft.dropdown.Option(v) for v in self.impacts])
            key_secondary_dd = ft.Dropdown(label="Key/Secondary", width=220, options=[ft.dropdown.Option(v) for v in (self.secondary_risks or ["Key risk","Secondary risk"])])
            category_dd = ft.Dropdown(label="Risk category", width=220, options=[ft.dropdown.Option(v) for v in self.categories])

            data_freq_dd = ft.Dropdown(label="Data", width=220, options=[ft.dropdown.Option(v) for v in self.data_frequencies])
            nature_dd = ft.Dropdown(label="Nature", width=220, options=[ft.dropdown.Option(v) for v in ["Preventive","Detective","Corrective"]])
            responsibility_tf = ft.TextField(label="Responsibility", width=220)
            frequency_dd = ft.Dropdown(label="Frequency", width=220, options=[ft.dropdown.Option(v) for v in self.data_frequencies])
            evidence_dd = ft.Dropdown(label="Evidence", width=260, options=[ft.dropdown.Option((ev.get("name") if isinstance(ev, dict) else str(ev))) for ev in self.evidence_items])

            authoriser_tf = ft.TextField(label="Authoriser", width=220)
            action_plan_tf = ft.TextField(label="Auditors recommended action plan", multiline=True, min_lines=2, max_lines=4, expand=True)
            responsible_tf = ft.TextField(label="Responsible", width=220)
            agreed_date_tf = ft.TextField(label="Agreed date (YYYY-MM-DD)", width=220)

            adj_like_dd = ft.Dropdown(label="Adjusted likelihood", width=220, options=[ft.dropdown.Option(v) for v in self.outcome_likelihoods or self.likelihoods])
            adj_impact_dd = ft.Dropdown(label="Adjusted impact", width=220, options=[ft.dropdown.Option(v) for v in self.impacts])

            remove_btn = ft.IconButton(icon=Icons.DELETE, tooltip="Remove row", on_click=lambda e, i=idx: remove_risk_row(i))

            if isinstance(initial, dict):
                business_obj.value = initial.get("BusinessObjectives") or ""
                main_process.value = initial.get("MainProcess") or ""
                sub_process.value = initial.get("SubProcess") or ""
                key_risk.value = initial.get("KeyRiskAndFactors") or ""
                # Other dropdowns will be assigned by label if present
                for ctrl, key in [
                    (like_dd, "Likelihood"), (impact_dd, "Impact"), (key_secondary_dd, "KeySecondary"),
                    (category_dd, "RiskCategory"), (data_freq_dd, "Data"), (nature_dd, "Nature"),
                    (frequency_dd, "Frequency"), (evidence_dd, "Evidence"), (adj_like_dd, "AdjustedLikelihood"),
                    (adj_impact_dd, "AdjustedImpact")
                ]:
                    val = initial.get(key)
                    if val is not None:
                        ctrl.value = str(val)
                responsibility_tf.value = initial.get("Responsibility") or ""
                authoriser_tf.value = initial.get("Authoriser") or ""
                action_plan_tf.value = initial.get("AuditorsRecommendedActionPlan") or ""
                responsible_tf.value = initial.get("ResponsiblePerson") or ""
                agreed_date_tf.value = initial.get("AgreedDate") or ""

            card = ft.Container(
                border=ft.border.all(1, ft.Colors.with_opacity(0.08, ft.Colors.BLACK)),
                border_radius=10,
                padding=15,
                content=ft.Column([
                    ft.Row([ft.Text(f"Risk row {idx+1}", weight=ft.FontWeight.BOLD), ft.Container(expand=True), remove_btn]),
                    ft.Row([business_obj, main_process, sub_process], spacing=12),
                    ft.Row([key_risk], spacing=12),
                    ft.Row([like_dd, impact_dd, key_secondary_dd, category_dd], spacing=12),
                    ft.Row([data_freq_dd, nature_dd, responsibility_tf, frequency_dd, evidence_dd], spacing=12),
                    ft.Row([authoriser_tf, responsible_tf, agreed_date_tf], spacing=12),
                    ft.Row([action_plan_tf], spacing=12),
                    ft.Row([adj_like_dd, adj_impact_dd], spacing=12),
                ], spacing=8)
            )

            row_dict = {
                "container": card,
                "BusinessObjectives": business_obj,
                "MainProcess": main_process,
                "SubProcess": sub_process,
                "KeyRiskAndFactors": key_risk,
                "Likelihood": like_dd,
                "Impact": impact_dd,
                "KeySecondary": key_secondary_dd,
                "RiskCategory": category_dd,
                "Data": data_freq_dd,
                "Nature": nature_dd,
                "Responsibility": responsibility_tf,
                "Frequency": frequency_dd,
                "Evidence": evidence_dd,
                "Authoriser": authoriser_tf,
                "AuditorsRecommendedActionPlan": action_plan_tf,
                "ResponsiblePerson": responsible_tf,
                "AgreedDate": agreed_date_tf,
                "AdjustedLikelihood": adj_like_dd,
                "AdjustedImpact": adj_impact_dd,
            }
            self.risk_rows.append(row_dict)
            self.risks_container.controls.append(card)
            self.page.update()

        def remove_risk_row(index):
            if 0 <= index < len(self.risk_rows):
                row = self.risk_rows.pop(index)
                try:
                    self.risks_container.controls.remove(row["container"])
                except Exception:
                    pass
                # Re-label remaining rows
                for i, rd in enumerate(self.risk_rows):
                    if isinstance(rd.get("container"), ft.Container) and isinstance(rd["container"].content, ft.Column):
                        header_row = rd["container"].content.controls[0]
                        if isinstance(header_row, ft.Row) and isinstance(header_row.controls[0], ft.Text):
                            header_row.controls[0].value = f"Risk row {i+1}"
                self.page.update()

        risks_tab = ft.Container(
            padding=ft.padding.all(20),
            content=ft.Column([
                ft.Row([
                    ft.Text("Risks (Excel-style)", size=16, weight=ft.FontWeight.BOLD),
                    ft.Container(expand=True),
                    ft.ElevatedButton(text="Add risk", icon=Icons.ADD, on_click=add_risk_row)
                ]),
                self.risks_container
            ], spacing=12)
        )

        form_tabs = ft.Tabs(selected_index=0, tabs=[
            ft.Tab(text="Overview", content=overview_tab),
            ft.Tab(text="Risks", content=risks_tab),
            ft.Tab(text="Risk Factors", content=factors_tab),
            ft.Tab(text="Risk Matrix", content=matrix_tab),
            ft.Tab(text="Attributes", content=attributes_tab),
            ft.Tab(text="Evidence", content=evidence_tab),
            ft.Tab(text="Controls", content=controls_tab)
        ])

        # Actions row
        actions_row = ft.Row([
            ft.Container(expand=True),
            ft.ElevatedButton(text="Cancel", icon=Icons.CANCEL, on_click=self.cancel_form),
            ft.Container(width=10),
            ft.ElevatedButton(text="Calculate Risk", icon=Icons.CALCULATE, on_click=self.calculate_risk),
            ft.Container(width=10),
            ft.ElevatedButton(text="Save Assessment", icon=Icons.SAVE, on_click=self.save_assessment)
        ], alignment=ft.MainAxisAlignment.END)

        # Load existing risk factors if any
        if self.assessment.risk_factors:
            for factor in self.assessment.risk_factors:
                if isinstance(factor, dict) and "name" in factor and "value" in factor:
                    self.add_risk_factor_row(factor["name"], factor["value"])
        else:
            # Add some default risk factors
            self.add_risk_factor_row("Control Environment", 0)
            self.add_risk_factor_row("Risk Assessment Process", 0)
            self.add_risk_factor_row("Control Activities", 0)

        # Assemble the view
        self.content = ft.Column([
            header,
            ft.Column(expand=True, scroll=ft.ScrollMode.AUTO, controls=[form_tabs])  # Use Column for scrolling
        ], spacing=0, expand=True)

        # Trigger async lookup loading for dropdowns and tabs
        self._init_async()

    # Theming hook to apply current theme colors to this view
    def apply_theme(self, colors):
        try:
            # Rebuild the view to refresh theme tokens, then normalize
            self.__init__(self.page, self.user, self.assessment, self.on_save_callback, self.on_cancel_callback)
            from src.utils.theme import apply_theme_to_control
            apply_theme_to_control(self, colors)
        except Exception:
            pass

    def estimate_matrix_level(self, impact, likelihood):
        # Align with Heatmap calculation ranges
        impact_order = ["Very Low", "Low", "Medium", "High", "Very High"]
        likelihood_order = ["Very Low", "Low", "Medium", "High", "Very High"]
        try:
            i = impact_order.index(impact) + 1
            l = likelihood_order.index(likelihood) + 1
            score = i * l
            if score >= 20:
                return "Critical"
            elif score >= 15:
                return "High"
            elif score >= 10:
                return "Medium-High"
            elif score >= 6:
                return "Medium"
            elif score >= 3:
                return "Low"
            else:
                return "Very Low"
        except ValueError:
            return self.assessment.risk_level or "N/A"

    def _init_async(self):
        self.page.run_task(self._load_lookups)  # Use Flet run_task for async from sync

    async def _load_lookups(self):
        try:
            like = await self.assessment_controller.get_risk_likelihoods()
            imps = await self.assessment_controller.get_impacts()
            ctrls = await self.assessment_controller.get_controls()
            outs = await self.assessment_controller.get_outcomes()
            evid = await self.assessment_controller.get_evidence()
            cats = await self.assessment_controller.get_risk_categories()
            secs = await self.assessment_controller.get_key_secondary_risks()
            data_freqs = await self.assessment_controller.get_data_frequencies()
            outcome_likes = await self.assessment_controller.get_outcome_likelihoods()
            # New: departments & projects
            from src.api.auditing_client import AuditingAPIClient
            client = AuditingAPIClient()
            departments = await client.get_departments()
            projects = await client.get_projects()

            # Normalize to text lists
            def to_text_list(items, key_candidates=("name", "title", "value", "label")):
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

            self._likelihood_items_raw = like or []
            self._impact_items_raw = imps or []
            self._category_items_raw = cats or []
            self._secondary_items_raw = secs or []
            self._data_freq_items_raw = data_freqs or []
            self._outcome_likelihood_items_raw = outcome_likes or []

            self.likelihoods = to_text_list(self._likelihood_items_raw)
            self.impacts = to_text_list(self._impact_items_raw)
            self.controls = ctrls if isinstance(ctrls, list) else []
            self.outcomes = outs if isinstance(outs, list) else []
            self.evidence_items = evid if isinstance(evid, list) else []
            self.categories = to_text_list(self._category_items_raw)
            self.secondary_risks = to_text_list(self._secondary_items_raw)
            self.data_frequencies = to_text_list(self._data_freq_items_raw)
            self.outcome_likelihoods = to_text_list(self._outcome_likelihood_items_raw)
            dept_names = [d.get("name") if isinstance(d, dict) else str(d) for d in (departments or [])]
            proj_names = [p.get("name") if isinstance(p, dict) else str(p) for p in (projects or [])]

            # Populate dropdowns
            self.likelihood_dropdown.options = [ft.dropdown.Option(v) for v in self.likelihoods]
            self.impact_dropdown.options = [ft.dropdown.Option(v) for v in self.impacts]
            self.department_dropdown.options = [ft.dropdown.Option(n) for n in dept_names]
            self.project_dropdown.options = [ft.dropdown.Option(n) for n in proj_names]
            self.risk_category_dropdown.options = [ft.dropdown.Option(v) for v in self.categories]
            self.key_secondary_dropdown.options = [ft.dropdown.Option(v) for v in self.secondary_risks]
            self.data_frequency_dropdown.options = [ft.dropdown.Option(v) for v in self.data_frequencies]
            # For Frequency, mirror DataFrequency list for now (if API differentiates, adjust mapping)
            self.frequency_dropdown.options = [ft.dropdown.Option(v) for v in self.data_frequencies]
            self.outcome_likelihood_dropdown.options = [ft.dropdown.Option(v) for v in self.outcome_likelihoods]
            # Try to set defaults
            if self.likelihoods:
                self.likelihood_dropdown.value = self.likelihoods[len(self.likelihoods)//2]
            if self.impacts:
                self.impact_dropdown.value = self.impacts[len(self.impacts)//2]
            if not self.assessment.department and dept_names:
                self.department_dropdown.value = dept_names[0]
            else:
                self.department_dropdown.value = self.assessment.department
            if not self.assessment.project and proj_names:
                self.project_dropdown.value = None
            else:
                self.project_dropdown.value = self.assessment.project

            # Populate evidence and controls tabs
            # Evidence list
            evid_list = ft.ListView(expand=True, spacing=5)
            for ev in self.evidence_items:
                text = ev.get("name") if isinstance(ev, dict) else str(ev)
                evid_list.controls.append(ft.ListTile(title=ft.Text(text)))
            # Controls list
            ctrl_list = ft.ListView(expand=True, spacing=5)
            for c in self.controls:
                text = c.get("name") if isinstance(c, dict) else str(c)
                ctrl_list.controls.append(ft.ListTile(title=ft.Text(text)))

            # Replace content in tabs (tab order changed)
            tabs = self.content.controls[1].controls[0]  # inner Column -> Tabs
            # Evidence at index 5 now
            tabs.tabs[5].content = ft.Container(padding=10, content=evid_list)
            tabs.tabs[6].content = ft.Container(padding=10, content=ctrl_list)

            self.page.update()
        except Exception as ex:
            print(f"Lookup load failed: {str(ex)}")
            if self.page:
                self.page.snack_bar = ft.SnackBar(content=ft.Text(f"Failed to load some data: {str(ex)}"))
                self.page.snack_bar.open = True
                self.page.update()

    def _resolve_department_id(self, name, departments):
        if not isinstance(departments, list):
            return None
        for d in departments:
            if isinstance(d, dict) and d.get("name") == name:
                return d.get("id")
        return None

    def _resolve_project_id(self, name, projects):
        if not isinstance(projects, list):
            return None
        for p in projects:
            if isinstance(p, dict) and p.get("name") == name:
                return p.get("id")
        return None

    def get_risk_color(self, risk_level):
        """Get color based on risk level"""
        if risk_level == "High":
            return "#e74c3c"  # Red
        elif risk_level == "Medium":
            return "#f39c12"  # Orange
        elif risk_level == "Low":
            return "#2ecc71"  # Green
        else:
            return "#95a5a6"  # Gray

    def add_risk_factor(self, e=None):
        """Add a new risk factor row"""
        self.add_risk_factor_row("", 0)

    # In your add_risk_factor_row method, make the row more compact:
    def add_risk_factor_row(self, name="", value=0):
        """Add a risk factor row with the given name and value"""
        # Create a unique ID for this row
        row_id = len(self.risk_factors_container.controls)

        # Create the factor name field
        name_field = ft.TextField(
            hint_text="Factor name",
            value=name,
            border=ft.InputBorder.OUTLINE,
            expand=True
        )

        # Create the rating dropdown - Fix for Flet version compatibility
        # Convert value to int for proper selection
        value_int = int(value) if isinstance(value, (int, float)) else 0

        # Map the value to the display text
        value_to_text = {
            0: "0 - No Risk",
            1: "1 - Very Low",
            2: "2 - Low",
            3: "3 - Medium",
            4: "4 - High",
            5: "5 - Very High"
        }

        rating_value = value_to_text.get(value_int, "0 - No Risk")

        rating_dropdown = ft.Dropdown(
            width=160,
            value=rating_value,
            options=[
                ft.dropdown.Option("0 - No Risk"),
                ft.dropdown.Option("1 - Very Low"),
                ft.dropdown.Option("2 - Low"),
                ft.dropdown.Option("3 - Medium"),
                ft.dropdown.Option("4 - High"),
                ft.dropdown.Option("5 - Very High")
            ],
            border=ft.InputBorder.OUTLINE
        )

        # Create a remove button
        remove_button = ft.IconButton(
            icon=ft.Icons.DELETE,
            icon_color="#e74c3c",
            tooltip="Remove factor",
            on_click=lambda e, id=row_id: self.remove_risk_factor(id)
        )

        # Create the row
        factor_row = ft.Row([
            name_field,
            rating_dropdown,
            remove_button
        ])

        # Add to our container
        self.risk_factors_container.controls.append(factor_row)
        self.page.update()

    def remove_risk_factor(self, row_id):
        """Remove a risk factor row"""
        if row_id < len(self.risk_factors_container.controls):
            self.risk_factors_container.controls.pop(row_id)
            # Update row IDs for remaining controls
            for i, row in enumerate(self.risk_factors_container.controls):
                # Update the remove button's callback
                row.controls[2].on_click = lambda e, id=i: self.remove_risk_factor(id)
            self.page.update()

    # In your calculate_risk method (in AssessmentFormView):
    def calculate_risk(self, e=None):
        """Calculate risk score and level based on risk factors"""
        print("Calculating risk...")
        # Get risk factors from UI
        risk_factors = []
        for row in self.risk_factors_container.controls:
            name_field = row.controls[0]
            rating_dropdown = row.controls[1]

            # Skip empty factors
            if not name_field.value:
                continue

            # Get rating value from dropdown text (extract first character)
            try:
                dropdown_text = rating_dropdown.value or "0 - No Risk"
                # Extract the first character which should be the numeric value
                value = float(dropdown_text[0])
                print(f"Risk factor: {name_field.value}, Value: {value}, from: {dropdown_text}")
            except (ValueError, IndexError):
                value = 0
                print(f"Failed to parse rating value from: {rating_dropdown.value}")

            risk_factors.append({
                "name": name_field.value,
                "value": value
            })

        # Update assessment with risk factors
        self.assessment.risk_factors = risk_factors

        # Calculate risk score
        self.assessment.update_risk_assessment()

        # Debug output
        print(f"Calculated risk score: {self.assessment.risk_score}, level: {self.assessment.risk_level}")

        # Update UI
        self.page.update()

    def save_assessment(self, e=None):
        """Save the assessment"""
        # Show a loading indicator
        loading = ft.ProgressBar(width=400)
        self.page.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Processing Assessment"),
            content=ft.Column([
                ft.Text("Calculating risk score and saving assessment..."),
                loading
            ], width=400, height=100, alignment=ft.MainAxisAlignment.CENTER),
        )
        self.page.dialog.open = True
        self.page.update()

        # Validate required fields
        if not self.title_field.value:
            self.close_dialog()
            self.show_error_dialog("Title is required")
            return

        if not (self.department_dropdown.value):
            self.close_dialog()
            self.show_error_dialog("Department is required")
            return

        # Update assessment object with form values
        self.assessment.title = self.title_field.value
        self.assessment.department = self.department_dropdown.value
        self.assessment.project = self.project_dropdown.value

        # Parse date
        try:
            if self.date_picker.value:
                self.assessment.assessment_date = datetime.strptime(self.date_picker.value, "%Y-%m-%d").date()
        except ValueError:
            self.close_dialog()
            self.show_error_dialog("Invalid date format. Please use YYYY-MM-DD")
            return

        self.assessment.scope = self.scope_field.value
        self.assessment.findings = self.findings_field.value
        self.assessment.recommendations = self.recommendations_field.value

        # Get risk factors from UI
        risk_factors = []
        for row in self.risk_factors_container.controls:
            name_field = row.controls[0]
            rating_dropdown = row.controls[1]

            # Skip empty factors
            if not name_field.value:
                continue

            # Get rating value
            try:
                # Extract the first character which is the numeric value
                option_text = rating_dropdown.value or "0"
                value = float(option_text[0]) if option_text else 0
            except (ValueError, IndexError):
                value = 0

            risk_factors.append({
                "name": name_field.value,
                "value": value
            })

        self.assessment.risk_factors = risk_factors

        # Calculate risk score and level
        self.assessment.update_risk_assessment()

        # Update timestamps
        self.assessment.updated_at = datetime.now()
        if not self.assessment.created_at:
            self.assessment.created_at = datetime.now()

        # Set auditor info if not set
        if not self.assessment.auditor_id and not self.assessment.auditor:
            if isinstance(self.user, dict):
                self.assessment.auditor_id = self.user.get("id")
                self.assessment.auditor = self.user.get("username")

        # Simulate API call delay (remove in production)
        import time
        time.sleep(1)  # Simulate processing time

        # Persist via API
        # Start async save to backend
        asyncio.create_task(self._save_to_backend_async())

        # Close the loading dialog
        self.close_dialog()

    async def _save_to_backend_async(self):
        """Handle async saving to backend"""
        try:
            from src.controllers.assessment_controller import AssessmentController
            controller = AssessmentController()
            # Helper to resolve ID by label
            def resolve_id(items, label):
                if not items or not label:
                    return None
                for it in items:
                    if isinstance(it, dict):
                        name = next((it.get(k) for k in ("name","title","value","label") if it.get(k) is not None), None)
                        if str(name) == str(label):
                            return next((it.get(k) for k in ("id","value","key","code") if it.get(k) is not None), None)
                return None

            # Construct wrapper payload for create
            assessments_payload = []
            if self.risk_rows:
                for rd in self.risk_rows:
                    assessments_payload.append({
                        "BusinessObjectives": rd["BusinessObjectives"].value,
                        "MainProcess": rd["MainProcess"].value,
                        "SubProcess": rd["SubProcess"].value,
                        "KeyRiskAndFactors": rd["KeyRiskAndFactors"].value,
                        "MitigatingControls": None,
                        "Responsibility": rd["Responsibility"].value,
                        "Authoriser": rd["Authoriser"].value,
                        "AuditorsRecommendedActionPlan": rd["AuditorsRecommendedActionPlan"].value,
                        "ResponsiblePerson": rd["ResponsiblePerson"].value,
                        "AgreedDate": rd["AgreedDate"].value or None,
                        "RiskLikelihoodId": resolve_id(self._likelihood_items_raw, rd["Likelihood"].value),
                        "RiskImpactId": resolve_id(self._impact_items_raw, rd["Impact"].value),
                        "KeySecondaryId": resolve_id(self._secondary_items_raw, rd["KeySecondary"].value),
                        "RiskCategoryId": resolve_id(self._category_items_raw, rd["RiskCategory"].value),
                        "DataFrequencyId": resolve_id(self._data_freq_items_raw, rd["Data"].value),
                        "FrequencyId": resolve_id(self._data_freq_items_raw, rd["Frequency"].value),
                        "EvidenceId": None,
                        "OutcomeLikelihoodId": resolve_id(self._outcome_likelihood_items_raw, rd["AdjustedLikelihood"].value),
                        "ImpactId": resolve_id(self._impact_items_raw, rd["AdjustedImpact"].value)
                    })
            else:
                assessments_payload.append({
                    "BusinessObjectives": self.assessment.scope or "",
                    "MainProcess": self.assessment.title or "",
                    "SubProcess": self.assessment.project or "",
                    "KeyRiskAndFactors": ", ".join([f.get("name") for f in (self.assessment.risk_factors or []) if isinstance(f, dict) and f.get("name")]),
                    "MitigatingControls": None,
                    "Responsibility": self.assessment.auditor or "",
                    "Authoriser": None,
                    "AuditorsRecommendedActionPlan": None,
                    "ResponsiblePerson": None,
                    "AgreedDate": None,
                    "RiskLikelihoodId": resolve_id(self._likelihood_items_raw, self.likelihood_dropdown.value),
                    "RiskImpactId": resolve_id(self._impact_items_raw, self.impact_dropdown.value),
                    "KeySecondaryId": resolve_id(self._secondary_items_raw, self.key_secondary_dropdown.value),
                    "RiskCategoryId": resolve_id(self._category_items_raw, self.risk_category_dropdown.value),
                    "DataFrequencyId": resolve_id(self._data_freq_items_raw, self.data_frequency_dropdown.value),
                    "FrequencyId": resolve_id(self._data_freq_items_raw, self.frequency_dropdown.value),
                    "EvidenceId": None,
                    "OutcomeLikelihoodId": resolve_id(self._outcome_likelihood_items_raw, self.outcome_likelihood_dropdown.value),
                    "ImpactId": resolve_id(self._impact_items_raw, self.impact_dropdown.value)
                })

            wrapper = {
                "Assessments": assessments_payload,
                "Reference": {
                    "Client": self.assessment.department or "",
                    "AssessmentStartDate": self.assessment.assessment_date.strftime("%Y-%m-%d") if hasattr(self.assessment.assessment_date, "strftime") else None,
                    "AssessmentEndDate": None,
                    "Assessor": self.assessment.auditor or "",
                    "ApprovedBy": None
                }
            }
            await controller.create_risk_assessment(wrapper)
        except Exception as _:
            # Allow UI to proceed; persistence errors will be visible in logs
            pass

        # Show success dialog
        self.page.dialog = ft.AlertDialog(
            title=ft.Text("Assessment Saved"),
            content=ft.Column([
                ft.Text(f"Assessment {self.assessment.id} has been saved successfully."),
                ft.Container(height=10),
                ft.Text(f"Risk Score: {self.assessment.risk_score:.1f}", size=16, weight=ft.FontWeight.BOLD),
                ft.Container(
                    padding=10,
                    bgcolor=self.get_risk_color(self.assessment.risk_level),
                    border_radius=5,
                    content=ft.Text(f"Risk Level: {self.assessment.risk_level}",
                                    color="white", size=16, weight=ft.FontWeight.BOLD)
                )
            ], width=400),
            actions=[
                ft.TextButton("Close", on_click=lambda e: self.complete_save())
            ],
        )
        self.page.dialog.open = True
        self.page.update()

    def complete_save(self):
        """Complete the save process and return to list view"""
        self.close_dialog()
        # If we have a callback, call it
        if self.on_save_callback:
            self.on_save_callback(self.assessment)

    # In your AssessmentFormView class:

    def cancel_form(self, e=None):
        """Cancel the form with confirmation"""
        # Show confirmation dialog
        self.page.dialog = ft.AlertDialog(
            title=ft.Text("Confirm Cancel"),
            content=ft.Text("Are you sure you want to cancel? Any unsaved changes will be lost."),
            actions=[
                ft.TextButton("No", on_click=self.close_dialog),
                ft.TextButton("Yes", on_click=self.direct_cancel)
            ],
        )
        self.page.dialog.open = True
        self.page.update()

    def direct_cancel(self, e=None):
        """Cancel without using callback - direct navigation approach"""
        self.close_dialog(None)

        print("Direct cancel initiated")

        # Try different navigation approaches
        try:
            # Approach 1: Use APP_INSTANCE if available
            if hasattr(self.page, 'APP_INSTANCE') and self.page.APP_INSTANCE:
                app = self.page.APP_INSTANCE
                if hasattr(app, 'show_view'):
                    print("Using app.show_view navigation")
                    app.show_view("assessments")
                    return

            # Approach 2: Re-create the list view directly
            print("Recreating list view directly")
            from src.views.assessment.list import AssessmentListView
            list_view = AssessmentListView(self.page, self.user)

            # Clear the page and add the new view
            if hasattr(self.page, 'controls'):
                self.page.controls.clear()
                self.page.controls.append(list_view)
                self.page.update()
                return

            # Approach 3: Use cleaner API if available
            if hasattr(self.page, 'clean'):
                self.page.clean()
                self.page.add(list_view)
                self.page.update()
                return

        except Exception as e:
            print(f"Error in direct_cancel: {str(e)}")

            # Approach 4: Last resort - try to go back to previous state
            try:
                # If we have an on_cancel_callback, try using it directly
                if self.on_cancel_callback and callable(self.on_cancel_callback):
                    self.on_cancel_callback()
            except Exception as e2:
                print(f"Failed to use callback: {str(e2)}")

    # In your AssessmentFormView class, modify the confirm_cancel method:
    def confirm_cancel(self):
        """Confirm cancellation and return to list view"""
        self.close_dialog()

        # Keep a reference to the page before it potentially gets lost
        page_ref = self.page

        # Call the original callback with a check
        if self.on_cancel_callback and callable(self.on_cancel_callback):
            try:
                self.on_cancel_callback()
            except Exception as e:
                print(f"Error in cancel callback: {str(e)}")

                # Try to handle the navigation more directly
                if page_ref:
                    try:
                        # Try to return to the list view through the app
                        if hasattr(page_ref, 'APP_INSTANCE') and page_ref.APP_INSTANCE:
                            app = page_ref.APP_INSTANCE
                            if hasattr(app, 'show_view'):
                                app.show_view("assessments")
                                return

                        # If that fails, try to recreate the list view
                        from src.views.assessment.list import AssessmentListView
                        list_view = AssessmentListView(page_ref, self.user)
                        page_ref.controls = [list_view]
                        page_ref.update()
                    except Exception as inner_e:
                        print(f"Failed to handle navigation after cancel: {str(inner_e)}")

    def show_error_dialog(self, message):
        """Show an error dialog"""
        dialog = ft.AlertDialog(
            title=ft.Text("Error"),
            content=ft.Text(message),
            actions=[
                ft.TextButton("OK", on_click=self.close_dialog),
            ],
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def close_dialog(self, e=None):
        """Close any open dialog"""
        if self.page.dialog:
            self.page.dialog.open = False
            self.page.update()
