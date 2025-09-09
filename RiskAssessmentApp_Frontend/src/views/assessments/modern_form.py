import flet as ft
import asyncio
from datetime import datetime, date
from src.controllers.assessment_controller import AssessmentController
from src.controllers.user_controller import UserController
from src.utils.formatters import format_date, format_currency
from src.views.common.base_view import BaseView
import json


class ModernAssessmentForm(BaseView):
    def __init__(self, page, user, assessment_data=None, reference_id=None, on_save=None, on_cancel=None):
        self.page = page
        self.user = user
        self.assessment_data = assessment_data
        self.reference_id = reference_id
        self.on_save_callback = on_save
        self.on_cancel_callback = on_cancel
        
        # Controllers
        self.assessment_controller = AssessmentController()
        self.user_controller = UserController()
        
        # Form state
        self.current_step = 0
        self.total_steps = 5
        self.lookup_data = {}
        self.form_data = {}
        self.validation_errors = {}
        
        # UI Components
        self.step_indicator = None
        self.content_container = None
        self.navigation_buttons = None
        
        # Initialize BaseView header
        title = "Risk Assessment Wizard" if not self.assessment_data else "Edit Risk Assessment"
        actions = [
            ft.ElevatedButton(text="Cancel", icon=ft.icons.CANCEL, on_click=self._handle_cancel),
            ft.ElevatedButton(text="Save", icon=ft.icons.SAVE, on_click=self._save_assessment),
        ]
        super().__init__(page, title, actions=actions)

        # Initialize form
        self._init_form()
    
    def _init_form(self):
        """Initialize the form components"""
        asyncio.create_task(self._load_lookup_data())
        self._build_ui()

    def apply_theme(self, colors):
        try:
            # Rebuild to pick up tokens, then normalize the tree
            self._build_ui()
            from src.utils.theme import apply_theme_to_control
            apply_theme_to_control(self, colors)
            if hasattr(self, 'page') and self.page:
                self.page.update()
        except Exception:
            pass
    
    async def _load_lookup_data(self):
        """Load all lookup data from the backend APIs"""
        try:
            # Load all lookup data concurrently
            tasks = [
                self.assessment_controller.get_risks(),
                self.assessment_controller.get_controls(),
                self.assessment_controller.get_outcomes(),
                self.assessment_controller.get_risk_likelihoods(),
                self.assessment_controller.get_impacts(),
                self.assessment_controller.get_key_secondary_risks(),
                self.assessment_controller.get_risk_categories(),
                self.assessment_controller.get_data_frequencies(),
                self.assessment_controller.get_outcome_likelihoods(),
                self.assessment_controller.get_evidence()
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Store results
            self.lookup_data = {
                'risks': results[0] if not isinstance(results[0], Exception) else [],
                'controls': results[1] if not isinstance(results[1], Exception) else [],
                'outcomes': results[2] if not isinstance(results[2], Exception) else [],
                'risk_likelihoods': results[3] if not isinstance(results[3], Exception) else [],
                'impacts': results[4] if not isinstance(results[4], Exception) else [],
                'key_secondary_risks': results[5] if not isinstance(results[5], Exception) else [],
                'risk_categories': results[6] if not isinstance(results[6], Exception) else [],
                'data_frequencies': results[7] if not isinstance(results[7], Exception) else [],
                'outcome_likelihoods': results[8] if not isinstance(results[8], Exception) else [],
                'evidence': results[9] if not isinstance(results[9], Exception) else []
            }
            
            # Update UI with loaded data
            self._update_form_with_data()
            
        except Exception as e:
            print(f"Error loading lookup data: {e}")
            self._show_error("Failed to load form data. Please refresh and try again.")
    
    def _build_ui(self):
        """Build the main UI structure"""
        # Step indicator
        self.step_indicator = self._build_step_indicator()
        
        # Content container
        self.content_container = ft.Container(
            content=self._build_step_content(),
            padding=30,
            expand=True
        )
        
        # Navigation buttons
        self.navigation_buttons = self._build_navigation()
        
        # Compose as a single card under BaseView
        main_panel = ft.Column([
            self.step_indicator,
            ft.Divider(height=1, color="#e6e9ed"),
            self.content_container,
            ft.Divider(height=1, color="#e6e9ed"),
            self.navigation_buttons
        ], spacing=0, expand=True)
        self.cards_column.controls.clear()
        self.add_card(main_panel)
    
    # Legacy header removed; BaseView header is used.
    
    def _build_step_indicator(self):
        """Build the step progress indicator"""
        steps = [
            "Basic Info",
            "Risk Details", 
            "Controls",
            "Assessment",
            "Review"
        ]
        
        step_controls = []
        for i, step_name in enumerate(steps):
            # Step circle
            if i < self.current_step:
                # Completed step
                circle = ft.Container(
                    width=30,
                    height=30,
                    border_radius=15,
                    bgcolor="#2ecc71",
                    alignment=ft.alignment.center,
                    content=ft.Icon(ft.icons.CHECK, color="white", size=16)
                )
                text_color = "#2ecc71"
            elif i == self.current_step:
                # Current step
                circle = ft.Container(
                    width=30,
                    height=30,
                    border_radius=15,
                    bgcolor="#3498db",
                    alignment=ft.alignment.center,
                    content=ft.Text(str(i + 1), color="white", weight=ft.FontWeight.BOLD)
                )
                text_color = "#3498db"
            else:
                # Future step
                circle = ft.Container(
                    width=30,
                    height=30,
                    border_radius=15,
                    bgcolor="#ecf0f1",
                    border=ft.border.all(2, "#bdc3c7"),
                    alignment=ft.alignment.center,
                    content=ft.Text(str(i + 1), color="#95a5a6", weight=ft.FontWeight.BOLD)
                )
                text_color = "#95a5a6"
            
            step_control = ft.Column([
                circle,
                ft.Text(step_name, size=12, color=text_color, text_align=ft.TextAlign.CENTER)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5)
            
            step_controls.append(step_control)
            
            # Add connector line (except for last step)
            if i < len(steps) - 1:
                line_color = "#2ecc71" if i < self.current_step else "#ecf0f1"
                step_controls.append(ft.Container(
                    width=50,
                    height=2,
                    bgcolor=line_color,
                    margin=ft.margin.only(top=15)
                ))
        
        return ft.Container(
            content=ft.Row(
                step_controls,
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=0
            ),
            padding=20,
            bgcolor="#f8f9fa"
        )
    
    def _build_step_content(self):
        """Build content for the current step"""
        if self.current_step == 0:
            return self._build_basic_info_step()
        elif self.current_step == 1:
            return self._build_risk_details_step()
        elif self.current_step == 2:
            return self._build_controls_step()
        elif self.current_step == 3:
            return self._build_assessment_step()
        elif self.current_step == 4:
            return self._build_review_step()
        else:
            return ft.Text("Invalid step")
    
    def _build_basic_info_step(self):
        """Build the basic information step"""
        return ft.Column([
            ft.Text("Basic Information", size=24, weight=ft.FontWeight.BOLD, color="#2c3e50"),
            ft.Text("Provide essential details about this risk assessment", size=14, color="#7f8c8d"),
            ft.Container(height=20),
            
            # Assessment Title
            ft.Text("Assessment Title *", size=16, weight=ft.FontWeight.BOLD),
            ft.TextField(
                label="Enter a descriptive title for this assessment",
                value=self.form_data.get('title', ''),
                border=ft.InputBorder.OUTLINE,
                on_change=lambda e: self._update_form_data('title', e.control.value),
                expand=True
            ),
            ft.Container(height=15),
            
            # Reference Information
            ft.Row([
                ft.Column([
                    ft.Text("Reference Number", size=16, weight=ft.FontWeight.BOLD),
                    ft.TextField(
                        label="Auto-generated if empty",
                        value=self.form_data.get('reference_number', ''),
                        border=ft.InputBorder.OUTLINE,
                        on_change=lambda e: self._update_form_data('reference_number', e.control.value),
                        expand=True
                    )
                ], expand=1),
                ft.Container(width=20),
                ft.Column([
                    ft.Text("Assessment Date *", size=16, weight=ft.FontWeight.BOLD),
                    ft.TextField(
                        label="YYYY-MM-DD",
                        value=self.form_data.get('assessment_date', datetime.now().strftime('%Y-%m-%d')),
                        border=ft.InputBorder.OUTLINE,
                        on_change=lambda e: self._update_form_data('assessment_date', e.control.value),
                        expand=True
                    )
                ], expand=1)
            ]),
            ft.Container(height=15),
            
            # Department and Project (placeholders for now)
            ft.Row([
                ft.Column([
                    ft.Text("Department", size=16, weight=ft.FontWeight.BOLD),
                    ft.Dropdown(
                        label="Select department",
                        options=[
                            ft.dropdown.Option("IT"),
                            ft.dropdown.Option("Finance"), 
                            ft.dropdown.Option("Operations"),
                            ft.dropdown.Option("Legal"),
                            ft.dropdown.Option("HR")
                        ],
                        value=self.form_data.get('department', ''),
                        on_change=lambda e: self._update_form_data('department', e.control.value),
                        expand=True
                    )
                ], expand=1),
                ft.Container(width=20),
                ft.Column([
                    ft.Text("Project (Optional)", size=16, weight=ft.FontWeight.BOLD),
                    ft.TextField(
                        label="Associated project name",
                        value=self.form_data.get('project', ''),
                        border=ft.InputBorder.OUTLINE,
                        on_change=lambda e: self._update_form_data('project', e.control.value),
                        expand=True
                    )
                ], expand=1)
            ]),
            ft.Container(height=15),
            
            # Assessment Scope
            ft.Text("Assessment Scope *", size=16, weight=ft.FontWeight.BOLD),
            ft.TextField(
                label="Describe the scope and objectives of this assessment",
                value=self.form_data.get('scope', ''),
                multiline=True,
                min_lines=3,
                max_lines=5,
                border=ft.InputBorder.OUTLINE,
                on_change=lambda e: self._update_form_data('scope', e.control.value),
                expand=True
            )
        ], scroll=ft.ScrollMode.AUTO)
    
    def _build_risk_details_step(self):
        """Build the risk details step"""
        return ft.Column([
            ft.Text("Risk Identification & Analysis", size=24, weight=ft.FontWeight.BOLD, color="#2c3e50"),
            ft.Text("Identify and analyze the risks associated with this assessment", size=14, color="#7f8c8d"),
            ft.Container(height=20),
            
            # Risk Category
            ft.Text("Risk Category *", size=16, weight=ft.FontWeight.BOLD),
            ft.Dropdown(
                label="Select the primary risk category",
                options=self._get_dropdown_options('risk_categories', 'description'),
                value=self.form_data.get('risk_category', ''),
                on_change=lambda e: self._update_form_data('risk_category', e.control.value),
                expand=True
            ),
            ft.Container(height=15),
            
            # Primary Risks
            ft.Text("Primary Risks *", size=16, weight=ft.FontWeight.BOLD),
            ft.Dropdown(
                label="Select the main risk being assessed",
                options=self._get_dropdown_options('risks', 'description'),
                value=self.form_data.get('primary_risk', ''),
                on_change=lambda e: self._update_form_data('primary_risk', e.control.value),
                expand=True
            ),
            ft.Container(height=15),
            
            # Secondary Risks
            ft.Text("Key Secondary Risks", size=16, weight=ft.FontWeight.BOLD),
            ft.Dropdown(
                label="Select any secondary risks (optional)",
                options=self._get_dropdown_options('key_secondary_risks', 'description'),
                value=self.form_data.get('secondary_risk', ''),
                on_change=lambda e: self._update_form_data('secondary_risk', e.control.value),
                expand=True
            ),
            ft.Container(height=15),
            
            # Risk Assessment Matrix
            ft.Text("Risk Assessment Matrix", size=16, weight=ft.FontWeight.BOLD),
            ft.Row([
                ft.Column([
                    ft.Text("Likelihood *", size=14, weight=ft.FontWeight.BOLD),
                    ft.Dropdown(
                        label="Probability of occurrence",
                        options=self._get_dropdown_options('risk_likelihoods', 'description'),
                        value=self.form_data.get('likelihood', ''),
                        on_change=lambda e: self._update_form_data('likelihood', e.control.value),
                        expand=True
                    )
                ], expand=1),
                ft.Container(width=20),
                ft.Column([
                    ft.Text("Impact *", size=14, weight=ft.FontWeight.BOLD),
                    ft.Dropdown(
                        label="Severity of impact",
                        options=self._get_dropdown_options('impacts', 'description'),
                        value=self.form_data.get('impact', ''),
                        on_change=lambda e: self._update_form_data('impact', e.control.value),
                        expand=True
                    )
                ], expand=1)
            ]),
            ft.Container(height=15),
            
            # Risk Description
            ft.Text("Risk Description", size=16, weight=ft.FontWeight.BOLD),
            ft.TextField(
                label="Provide detailed description of the identified risks",
                value=self.form_data.get('risk_description', ''),
                multiline=True,
                min_lines=3,
                max_lines=5,
                border=ft.InputBorder.OUTLINE,
                on_change=lambda e: self._update_form_data('risk_description', e.control.value),
                expand=True
            )
        ], scroll=ft.ScrollMode.AUTO)
    
    def _build_controls_step(self):
        """Build the controls step"""
        return ft.Column([
            ft.Text("Control Framework", size=24, weight=ft.FontWeight.BOLD, color="#2c3e50"),
            ft.Text("Define the controls in place to mitigate identified risks", size=14, color="#7f8c8d"),
            ft.Container(height=20),
            
            # Existing Controls
            ft.Text("Existing Controls *", size=16, weight=ft.FontWeight.BOLD),
            ft.Dropdown(
                label="Select the primary control framework",
                options=self._get_dropdown_options('controls', 'description'),
                value=self.form_data.get('control', ''),
                on_change=lambda e: self._update_form_data('control', e.control.value),
                expand=True
            ),
            ft.Container(height=15),
            
            # Control Effectiveness
            ft.Text("Control Effectiveness Assessment", size=16, weight=ft.FontWeight.BOLD),
            ft.RadioGroup(
                content=ft.Column([
                    ft.Radio(value="effective", label="Effective - Controls are working as designed"),
                    ft.Radio(value="partially_effective", label="Partially Effective - Controls need improvement"),
                    ft.Radio(value="ineffective", label="Ineffective - Controls are not working"),
                    ft.Radio(value="not_tested", label="Not Tested - Controls have not been evaluated")
                ]),
                value=self.form_data.get('control_effectiveness', 'not_tested'),
                on_change=lambda e: self._update_form_data('control_effectiveness', e.control.value)
            ),
            ft.Container(height=15),
            
            # Evidence
            ft.Text("Evidence & Documentation", size=16, weight=ft.FontWeight.BOLD),
            ft.Dropdown(
                label="Type of evidence available",
                options=self._get_dropdown_options('evidence', 'description'),
                value=self.form_data.get('evidence_type', ''),
                on_change=lambda e: self._update_form_data('evidence_type', e.control.value),
                expand=True
            ),
            ft.Container(height=15),
            
            # Testing Frequency
            ft.Text("Testing Frequency", size=16, weight=ft.FontWeight.BOLD),
            ft.Dropdown(
                label="How often should controls be tested",
                options=self._get_dropdown_options('data_frequencies', 'description'),
                value=self.form_data.get('testing_frequency', ''),
                on_change=lambda e: self._update_form_data('testing_frequency', e.control.value),
                expand=True
            ),
            ft.Container(height=15),
            
            # Control Description
            ft.Text("Control Description", size=16, weight=ft.FontWeight.BOLD),
            ft.TextField(
                label="Describe the specific controls in place and their implementation",
                value=self.form_data.get('control_description', ''),
                multiline=True,
                min_lines=3,
                max_lines=5,
                border=ft.InputBorder.OUTLINE,
                on_change=lambda e: self._update_form_data('control_description', e.control.value),
                expand=True
            )
        ], scroll=ft.ScrollMode.AUTO)
    
    def _build_assessment_step(self):
        """Build the assessment findings step"""
        return ft.Column([
            ft.Text("Assessment Findings", size=24, weight=ft.FontWeight.BOLD, color="#2c3e50"),
            ft.Text("Document your findings, outcomes, and recommendations", size=14, color="#7f8c8d"),
            ft.Container(height=20),
            
            # Outcomes
            ft.Text("Assessment Outcome *", size=16, weight=ft.FontWeight.BOLD),
            ft.Dropdown(
                label="Select the overall assessment outcome",
                options=self._get_dropdown_options('outcomes', 'description'),
                value=self.form_data.get('outcome', ''),
                on_change=lambda e: self._update_form_data('outcome', e.control.value),
                expand=True
            ),
            ft.Container(height=15),
            
            # Outcome Likelihood
            ft.Text("Outcome Likelihood", size=16, weight=ft.FontWeight.BOLD),
            ft.Dropdown(
                label="Likelihood of the identified outcome",
                options=self._get_dropdown_options('outcome_likelihoods', 'description'),
                value=self.form_data.get('outcome_likelihood', ''),
                on_change=lambda e: self._update_form_data('outcome_likelihood', e.control.value),
                expand=True
            ),
            ft.Container(height=15),
            
            # Key Findings
            ft.Text("Key Findings *", size=16, weight=ft.FontWeight.BOLD),
            ft.TextField(
                label="Document the key findings from your assessment",
                value=self.form_data.get('findings', ''),
                multiline=True,
                min_lines=4,
                max_lines=8,
                border=ft.InputBorder.OUTLINE,
                on_change=lambda e: self._update_form_data('findings', e.control.value),
                expand=True
            ),
            ft.Container(height=15),
            
            # Recommendations
            ft.Text("Recommendations *", size=16, weight=ft.FontWeight.BOLD),
            ft.TextField(
                label="Provide specific, actionable recommendations",
                value=self.form_data.get('recommendations', ''),
                multiline=True,
                min_lines=4,
                max_lines=8,
                border=ft.InputBorder.OUTLINE,
                on_change=lambda e: self._update_form_data('recommendations', e.control.value),
                expand=True
            ),
            ft.Container(height=15),
            
            # Management Response
            ft.Text("Management Response", size=16, weight=ft.FontWeight.BOLD),
            ft.TextField(
                label="Document management's response to findings (optional)",
                value=self.form_data.get('management_response', ''),
                multiline=True,
                min_lines=3,
                max_lines=5,
                border=ft.InputBorder.OUTLINE,
                on_change=lambda e: self._update_form_data('management_response', e.control.value),
                expand=True
            )
        ], scroll=ft.ScrollMode.AUTO)
    
    def _build_review_step(self):
        """Build the review and submit step"""
        # Calculate risk score
        risk_score = self._calculate_risk_score()
        risk_level = self._determine_risk_level(risk_score)
        
        return ft.Column([
            ft.Text("Review & Submit", size=24, weight=ft.FontWeight.BOLD, color="#2c3e50"),
            ft.Text("Review your assessment before submitting", size=14, color="#7f8c8d"),
            ft.Container(height=20),
            
            # Risk Score Summary
            ft.Card(
                content=ft.Container(
                    padding=20,
                    content=ft.Row([
                        ft.Column([
                            ft.Text("Calculated Risk Score", size=16, weight=ft.FontWeight.BOLD),
                            ft.Text(f"{risk_score:.1f}", size=32, weight=ft.FontWeight.BOLD, color="#3498db")
                        ], expand=1),
                        ft.Column([
                            ft.Text("Risk Level", size=16, weight=ft.FontWeight.BOLD),
                            ft.Container(
                                content=ft.Text(risk_level, size=18, weight=ft.FontWeight.BOLD, color="white"),
                                bgcolor=self._get_risk_color(risk_level),
                                padding=10,
                                border_radius=5
                            )
                        ], expand=1)
                    ])
                )
            ),
            ft.Container(height=20),
            
            # Summary sections
            self._build_summary_section("Basic Information", [
                ("Title", self.form_data.get('title', 'Not specified')),
                ("Department", self.form_data.get('department', 'Not specified')),
                ("Assessment Date", self.form_data.get('assessment_date', 'Not specified')),
                ("Scope", self.form_data.get('scope', 'Not specified')[:100] + "..." if len(self.form_data.get('scope', '')) > 100 else self.form_data.get('scope', 'Not specified'))
            ]),
            
            self._build_summary_section("Risk Analysis", [
                ("Risk Category", self.form_data.get('risk_category', 'Not specified')),
                ("Primary Risk", self.form_data.get('primary_risk', 'Not specified')),
                ("Likelihood", self.form_data.get('likelihood', 'Not specified')),
                ("Impact", self.form_data.get('impact', 'Not specified'))
            ]),
            
            self._build_summary_section("Controls & Outcome", [
                ("Control Framework", self.form_data.get('control', 'Not specified')),
                ("Control Effectiveness", self.form_data.get('control_effectiveness', 'Not tested')),
                ("Assessment Outcome", self.form_data.get('outcome', 'Not specified')),
                ("Evidence Type", self.form_data.get('evidence_type', 'Not specified'))
            ]),
            
            # Validation summary
            self._build_validation_summary()
            
        ], scroll=ft.ScrollMode.AUTO)
    
    def _build_summary_section(self, title, items):
        """Build a summary section for the review step"""
        rows = []
        for label, value in items:
            rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(label, weight=ft.FontWeight.BOLD)),
                    ft.DataCell(ft.Text(str(value), color="#2c3e50"))
                ])
            )
        
        return ft.Card(
            content=ft.Container(
                padding=15,
                content=ft.Column([
                    ft.Text(title, size=16, weight=ft.FontWeight.BOLD, color="#2c3e50"),
                    ft.DataTable(
                        columns=[
                            ft.DataColumn(ft.Text("Field")),
                            ft.DataColumn(ft.Text("Value"))
                        ],
                        rows=rows,
                        border=ft.border.all(1, "#ecf0f1"),
                        border_radius=5
                    )
                ])
            )
        )
    
    def _build_validation_summary(self):
        """Build validation summary for review step"""
        errors = self._validate_form()
        
        if not errors:
            return ft.Card(
                content=ft.Container(
                    padding=15,
                    content=ft.Row([
                        ft.Icon(ft.icons.CHECK_CIRCLE, color="#2ecc71", size=24),
                        ft.Text("All required fields completed. Ready to submit!", 
                               size=16, color="#2ecc71", weight=ft.FontWeight.BOLD)
                    ])
                )
            )
        else:
            error_items = [ft.Text(f"• {error}", color="#e74c3c") for error in errors]
            return ft.Card(
                content=ft.Container(
                    padding=15,
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(ft.icons.ERROR, color="#e74c3c", size=24),
                            ft.Text("Please fix the following issues:", 
                                   size=16, color="#e74c3c", weight=ft.FontWeight.BOLD)
                        ]),
                        ft.Container(height=10),
                        ft.Column(error_items)
                    ])
                )
            )
    
    def _build_navigation(self):
        """Build navigation buttons"""
        return ft.Container(
            padding=20,
            bgcolor="#f8f9fa",
            content=ft.Row([
                ft.ElevatedButton(
                    text="Cancel",
                    icon=ft.icons.CANCEL,
                    on_click=self._handle_cancel,
                    bgcolor="#95a5a6",
                    color="white"
                ),
                ft.Container(expand=True),
                ft.ElevatedButton(
                    text="Previous",
                    icon=ft.icons.ARROW_BACK,
                    on_click=self._previous_step,
                    visible=self.current_step > 0,
                    bgcolor="#7f8c8d",
                    color="white"
                ),
                ft.Container(width=10),
                ft.ElevatedButton(
                    text="Save Draft" if self.current_step < self.total_steps - 1 else "Submit Assessment",
                    icon=ft.icons.SAVE if self.current_step < self.total_steps - 1 else ft.icons.SEND,
                    on_click=self._save_assessment,
                    bgcolor="#3498db",
                    color="white"
                ),
                ft.Container(width=10),
                ft.ElevatedButton(
                    text="Next",
                    icon=ft.icons.ARROW_FORWARD,
                    on_click=self._next_step,
                    visible=self.current_step < self.total_steps - 1,
                    bgcolor="#2ecc71",
                    color="white"
                )
            ])
        )
    
    def _get_dropdown_options(self, data_key, value_field):
        """Get dropdown options from lookup data"""
        data_list = self.lookup_data.get(data_key, [])
        if not data_list:
            return [ft.dropdown.Option("Loading...")]
        
        options = []
        for item in data_list:
            if isinstance(item, dict):
                value = item.get(value_field, str(item))
                label = item.get('name', value)
                options.append(ft.dropdown.Option(key=value, text=f"{label}: {value}"))
            else:
                options.append(ft.dropdown.Option(str(item)))
        
        return options
    
    def _update_form_data(self, key, value):
        """Update form data"""
        self.form_data[key] = value
    
    def _update_form_with_data(self):
        """Update form UI with loaded lookup data"""
        if hasattr(self, 'page') and self.page:
            self.page.update()
    
    def _calculate_risk_score(self):
        """Calculate risk score based on likelihood and impact"""
        likelihood_map = {'Very Low': 1, 'Low': 2, 'Medium': 3, 'High': 4, 'Very High': 5}
        impact_map = {'Very Low': 1, 'Low': 2, 'Medium': 3, 'High': 4, 'Very High': 5}
        
        likelihood = self.form_data.get('likelihood', '')
        impact = self.form_data.get('impact', '')
        
        likelihood_score = likelihood_map.get(likelihood, 0)
        impact_score = impact_map.get(impact, 0)
        
        return likelihood_score * impact_score
    
    def _determine_risk_level(self, score):
        """Determine risk level from score"""
        if score >= 20:
            return "Critical"
        elif score >= 15:
            return "High"
        elif score >= 9:
            return "Medium"
        elif score >= 4:
            return "Low"
        else:
            return "Very Low"
    
    def _get_risk_color(self, risk_level):
        """Get color for risk level"""
        colors = {
            "Critical": "#8B0000",
            "High": "#e74c3c",
            "Medium": "#f39c12", 
            "Low": "#2ecc71",
            "Very Low": "#27ae60"
        }
        return colors.get(risk_level, "#95a5a6")
    
    def _validate_form(self):
        """Validate form data"""
        errors = []
        
        # Required fields
        required_fields = {
            'title': 'Assessment Title',
            'assessment_date': 'Assessment Date',
            'scope': 'Assessment Scope',
            'risk_category': 'Risk Category',
            'primary_risk': 'Primary Risk',
            'likelihood': 'Likelihood',
            'impact': 'Impact',
            'control': 'Control Framework',
            'outcome': 'Assessment Outcome',
            'findings': 'Key Findings',
            'recommendations': 'Recommendations'
        }
        
        for field, label in required_fields.items():
            if not self.form_data.get(field):
                errors.append(f"{label} is required")
        
        # Date validation
        if self.form_data.get('assessment_date'):
            try:
                datetime.strptime(self.form_data['assessment_date'], '%Y-%m-%d')
            except ValueError:
                errors.append("Assessment Date must be in YYYY-MM-DD format")
        
        return errors
    
    def _next_step(self, e):
        """Move to next step"""
        if self.current_step < self.total_steps - 1:
            self.current_step += 1
            self._refresh_ui()
    
    def _previous_step(self, e):
        """Move to previous step"""
        if self.current_step > 0:
            self.current_step -= 1
            self._refresh_ui()
    
    def _refresh_ui(self):
        """Refresh the UI with current step"""
        self.step_indicator.content = self._build_step_indicator().content
        self.content_container.content = self._build_step_content()
        self.navigation_buttons.content = self._build_navigation().content
        if hasattr(self, 'page') and self.page:
            self.page.update()
    
    async def _save_assessment(self, e):
        """Save assessment"""
        # Validate before saving
        errors = self._validate_form()
        if errors and self.current_step == self.total_steps - 1:
            self._show_error("Please fix validation errors before submitting")
            return
        
        try:
            # Show loading
            self._show_loading("Saving assessment...")
            
            # Prepare assessment data for API
            assessment_data = self._prepare_assessment_data()
            
            # Save via API
            if self.assessment_data:
                # Update existing
                result = await self.assessment_controller.update_risk_assessment(
                    self.reference_id, assessment_data
                )
            else:
                # Create new
                result = await self.assessment_controller.create_risk_assessment(assessment_data)
            
            if result:
                self._show_success("Assessment saved successfully!")
                if self.on_save_callback:
                    self.on_save_callback(result)
            else:
                self._show_error("Failed to save assessment")
                
        except Exception as ex:
            self._show_error(f"Error saving assessment: {str(ex)}")
        finally:
            self._hide_loading()
    
    def _prepare_assessment_data(self):
        """Prepare assessment data for API submission"""
        # This should match the backend API structure
        return {
            "assessments": [{
                "riskId": self.form_data.get('primary_risk'),
                "controlId": self.form_data.get('control'),
                "outcomeId": self.form_data.get('outcome'),
                "riskLikelihoodId": self.form_data.get('likelihood'),
                "impactId": self.form_data.get('impact'),
                "keySecondaryRiskId": self.form_data.get('secondary_risk'),
                "riskCategoryId": self.form_data.get('risk_category'),
                "dataFrequencyId": self.form_data.get('testing_frequency'),
                "outcomeLikelihoodId": self.form_data.get('outcome_likelihood'),
                "evidenceId": self.form_data.get('evidence_type')
            }],
            "reference": {
                "title": self.form_data.get('title'),
                "description": self.form_data.get('scope'),
                "department_id": 1,  # TODO: Get from user selection
                "project_id": 1,     # TODO: Get from user selection
                "auditor_id": self.user.id if self.user else 1
            } if not self.reference_id else None,
            "referenceId": self.reference_id
        }
    
    def _handle_cancel(self, e):
        """Handle form cancellation"""
        if self.on_cancel_callback:
            self.on_cancel_callback()
    
    def _show_loading(self, message):
        """Show loading dialog"""
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
        """Hide loading dialog"""
        if self.page.dialog:
            self.page.dialog.open = False
            self.page.update()
    
    def _show_success(self, message):
        """Show success message"""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor="#2ecc71"
        )
        self.page.snack_bar.open = True
        self.page.update()
    
    def _show_error(self, message):
        """Show error message"""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor="#e74c3c"
        )
        self.page.snack_bar.open = True
        self.page.update()
    
    async def cleanup(self):
        """Cleanup resources"""
        try:
            await self.assessment_controller.close()
        except Exception as e:
            print(f"Error during cleanup: {e}") 
