import flet as ft
from flet import Icons
import asyncio
import csv
from datetime import datetime, timedelta
import os
from src.controllers.assessment_controller import AssessmentController
from src.api.identity_client import IdentityAPIClient
from src.utils.export_manager import ExportManager
from src.utils.formatters import format_date, format_currency
from src.utils.logger import get_logger
from src.utils.permissions import can_manage_audit_content, can_manage_document_security, can_manage_management_response, can_review_evidence, can_start_workflows, can_submit_evidence
from src.views.common.base_view import BaseView
import json


class ModernAssessmentDetails(BaseView):
    def __init__(self, page, user, assessment_id=None, reference_id=None, on_back=None, on_edit=None, initial_tab=0):
        self.page = page
        self.user = user
        self.assessment_id = assessment_id
        self.reference_id = reference_id
        self.on_back_callback = on_back
        self.on_edit_callback = on_edit
        
        # Controllers
        self.assessment_controller = AssessmentController(user)
        self.identity_client = IdentityAPIClient()
        self.export_manager = ExportManager()
        self.logger = get_logger()
        
        # State
        self.assessment_data = None
        self.heatmap_data = None
        self.planning_data = None
        self.materiality_workspace = None
        self.finance_audit_workspace = None
        self.scope_items_data = []
        self.findings_data = []
        self.recommendations_data = []
        self.procedures_data = []
        self.procedure_library = []
        self.walkthroughs_data = []
        self.working_papers_data = []
        self.working_paper_templates = []
        self.documents_data = []
        self.document_categories = []
        self.document_visibility_options = []
        self.document_access_logs = []
        self.collaborator_roles = []
        self.reference_collaborators = []
        self.available_collaboration_users = []
        self.evidence_requests_data = []
        self.management_actions_data = []
        self.audit_coverage_map = None
        self.workflow_instances = []
        self.workflow_timeline = []
        self.audit_trail_events = []
        self.audit_trail_dashboard = None
        self.risk_control_matrix_data = []
        self.engagement_types = []
        self.planning_statuses = []
        self.finding_severities = []
        self.finding_statuses = []
        self.recommendation_statuses = []
        self.procedure_types = []
        self.procedure_statuses = []
        self.working_paper_statuses = []
        self.evidence_request_statuses = []
        self.control_classifications = []
        self.control_types = []
        self.control_frequencies = []
        self.pending_document_file = None
        self.document_upload_mode = "general"
        self.document_file_picker = None
        self.materiality_import_file_picker = None
        self.pending_materiality_import_file = None
        self.materiality_import_validation = None
        self.materiality_import_dataset_type = "trial_balance"
        self.materiality_dialog_reference_id = None
        self.materiality_form_state = {}
        self.finance_tab_index = 10
        self.current_tab = initial_tab or 0
        self.comments = []
        self.activity_log = []
        self.workflow_state = {}
        self.workflow_status = "In Progress"

        menu_items = [
            ft.PopupMenuItem(text="Export to PDF", icon=Icons.PICTURE_AS_PDF, on_click=lambda e: self._export_assessment("pdf")),
            ft.PopupMenuItem(text="Export to Excel", icon=Icons.TABLE_VIEW, on_click=lambda e: self._export_assessment("excel")),
        ]
        if can_start_workflows(user):
            menu_items.append(ft.PopupMenuItem(text="Start Final Sign-Off", icon=Icons.VERIFIED, on_click=self._open_final_signoff_workflow_dialog))
        menu_items.extend([
            ft.PopupMenuItem(text="Share Audit File", icon=Icons.SHARE, on_click=self._share_assessment),
            ft.PopupMenuItem(),
            ft.PopupMenuItem(text="Edit Assessment", icon=Icons.EDIT, on_click=self._edit_assessment),
            ft.PopupMenuItem(text="Archive Audit File", icon=Icons.ARCHIVE, on_click=self._archive_assessment),
        ])
        
        # Header actions in BaseView
        actions = [
            ft.ElevatedButton(
                text="Start Control Testing",
                icon=Icons.PLAY_ARROW,
                bgcolor="#f39c12",
                color="white",
                on_click=self._start_control_testing,
                visible=can_start_workflows(user),
            ),
            ft.PopupMenuButton(
                items=menu_items,
                icon=Icons.MORE_VERT,
            )
        ]
        super().__init__(page, f"Audit File: {reference_id or ''}", on_back=self._handle_back, actions=actions)
        self._ensure_document_picker()
        self._ensure_materiality_import_picker()

        # Initialize view
        self._init_view()
    
    def _init_view(self):
        """Initialize the view"""
        self._build_ui()
        if self.reference_id:
            self.page.run_task(self._load_assessment_data)

    def _ensure_document_picker(self):
        if self.document_file_picker:
            return
        self.document_file_picker = ft.FilePicker(on_result=self._on_document_file_selected)
        self.page.overlay.append(self.document_file_picker)

    def _pick_document_file(self, e=None):
        self._ensure_document_picker()
        self.document_file_picker.pick_files(
            allow_multiple=False,
            dialog_title="Select audit document"
        )

    def _ensure_materiality_import_picker(self):
        if self.materiality_import_file_picker:
            return
        self.materiality_import_file_picker = ft.FilePicker(on_result=self._on_materiality_import_file_selected)
        self.page.overlay.append(self.materiality_import_file_picker)
        if self.page:
            self.page.update()

    def _pick_materiality_import_file(self, e=None):
        self._ensure_materiality_import_picker()
        try:
            self._log_materiality_event(
                "select_csv_clicked",
                picker_ready=bool(self.materiality_import_file_picker),
                overlay_items=len(self.page.overlay) if self.page and hasattr(self.page, "overlay") else None,
            )
            if hasattr(self, "materiality_validation_text") and self.materiality_validation_text:
                dataset_label = "trial balance" if self.materiality_import_dataset_type == "trial_balance" else "journal-entry"
                self.materiality_validation_text.value = f"Opening file picker. Select a {dataset_label} CSV to continue."
                self.materiality_validation_text.color = "#475569"
            # Keep the picker call compatible with older Flet builds.
            self.materiality_import_file_picker.pick_files(allow_multiple=False)
            if self.page:
                self.page.update()
        except Exception as ex:
            self._log_materiality_event("select_csv_failed", level="error", error=str(ex))
            self._show_error(f"Unable to open the file picker: {str(ex)}")

    def _update_materiality_form_state(self, key, value):
        if self.materiality_form_state is None:
            self.materiality_form_state = {}
        self.materiality_form_state[key] = value

    def _log_materiality_event(self, message, level="info", **context):
        payload = {
            "reference_id": self._normalize_reference_id(),
            "user": self._get_current_user_name(),
            **context,
        }
        try:
            log_message = f"[materiality] {message} | {json.dumps(payload, default=str)}"
        except Exception:
            log_message = f"[materiality] {message} | {payload}"

        log_method = getattr(self.logger, level, self.logger.info)
        log_method(log_message)

    async def _refresh_materiality_view_state(self):
        reference_id = self._normalize_reference_id()
        if not reference_id:
            return

        self._log_materiality_event("refresh_materiality_view_state_started")
        planning_task = self.assessment_controller.auditing_client.get_planning_by_reference(reference_id)
        workspace_task = self.assessment_controller.auditing_client.get_materiality_workspace(reference_id)
        planning_result, workspace_result = await asyncio.gather(planning_task, workspace_task, return_exceptions=True)

        if not isinstance(planning_result, Exception):
            self.planning_data = planning_result
        else:
            self._log_materiality_event("refresh_materiality_view_state_planning_failed", level="error", error=str(planning_result))

        if not isinstance(workspace_result, Exception):
            self.materiality_workspace = workspace_result
        else:
            self._log_materiality_event("refresh_materiality_view_state_workspace_failed", level="error", error=str(workspace_result))

        self._build_ui()
        if self.page:
            self.page.update()
        self._log_materiality_event(
            "refresh_materiality_view_state_completed",
            candidate_count=len(self._get_materiality_candidates()),
            calculation_count=len(self._get_materiality_calculations()),
            active_calculation=self._get_field(self._get_active_materiality_calculation(), "calculationSummary", "CalculationSummary"),
        )

    async def _finalize_materiality_action(self, success_message, activity_action, icon, color):
        self._log_materiality_event(
            "finalize_materiality_action_started",
            success_message=success_message,
            activity_action=activity_action,
        )

        try:
            if getattr(self, "materiality_dialog", None):
                self._close_active_dialog(self.materiality_dialog)
                self._log_materiality_event("finalize_materiality_action_dialog_closed")
        except Exception as ex:
            self._log_materiality_event("finalize_materiality_action_dialog_close_failed", level="error", error=str(ex))

        try:
            await self._append_activity_event(activity_action, icon, color)
            self._log_materiality_event("finalize_materiality_action_activity_recorded")
        except Exception as ex:
            self._log_materiality_event("finalize_materiality_action_activity_failed", level="error", error=str(ex))

        try:
            self._show_success(success_message)
            self._log_materiality_event("finalize_materiality_action_success_shown")
        except Exception as ex:
            self._log_materiality_event("finalize_materiality_action_success_failed", level="error", error=str(ex))

        try:
            await self._refresh_materiality_view_state()
            self._log_materiality_event("finalize_materiality_action_refresh_completed")
        except Exception as ex:
            self._log_materiality_event("finalize_materiality_action_refresh_failed", level="error", error=str(ex))

    def _on_document_file_selected(self, e):
        if not e or not getattr(e, "files", None):
            self.document_upload_mode = "general"
            return
        selected = e.files[0]
        self.pending_document_file = {
            "path": getattr(selected, "path", None),
            "name": getattr(selected, "name", None),
            "size": getattr(selected, "size", None)
        }
        if not self.pending_document_file.get("path"):
            self._show_error("Selected file path is not available in this runtime")
            return
        self._open_upload_document_dialog()

    def _on_materiality_import_file_selected(self, e):
        if not e or not getattr(e, "files", None):
            self._log_materiality_event("csv_selection_cancelled")
            return
        selected = e.files[0]
        self.pending_materiality_import_file = {
            "path": getattr(selected, "path", None),
            "name": getattr(selected, "name", None),
            "size": getattr(selected, "size", None),
        }
        self._log_materiality_event(
            "csv_selected",
            file_name=self.pending_materiality_import_file.get("name"),
            file_path=self.pending_materiality_import_file.get("path"),
            file_size=self.pending_materiality_import_file.get("size"),
        )
        if not self.pending_materiality_import_file.get("path"):
            self._log_materiality_event("csv_selected_without_path", level="warning")
            self._show_error("Selected file path is not available in this runtime")
            return

        validation = self._validate_materiality_import_csv(
            self.pending_materiality_import_file["path"],
            self.materiality_import_dataset_type,
        )
        self.materiality_import_validation = validation
        self._log_materiality_event(
            "csv_validated",
            is_valid=validation.get("is_valid"),
            row_count=validation.get("row_count"),
            error=validation.get("error"),
        )

        if hasattr(self, "materiality_selected_file_text") and self.materiality_selected_file_text:
            file_name = self.pending_materiality_import_file.get("name") or os.path.basename(self.pending_materiality_import_file["path"])
            self.materiality_selected_file_text.value = f"Selected file: {file_name}"

        if hasattr(self, "materiality_validation_text") and self.materiality_validation_text:
            if validation.get("is_valid"):
                dataset_label = "trial balance" if self.materiality_import_dataset_type == "trial_balance" else "journal-entry"
                self.materiality_validation_text.value = (
                    f"Validated {validation.get('row_count', 0):,} {dataset_label} rows. Required columns are present."
                )
                self.materiality_validation_text.color = "#15803d"
            else:
                self.materiality_validation_text.value = validation.get("error") or "Validation failed."
                self.materiality_validation_text.color = "#dc2626"

        if hasattr(self, "materiality_preview_column") and self.materiality_preview_column is not None:
            preview_rows = validation.get("preview_rows", [])
            if preview_rows:
                self.materiality_preview_column.controls = [
                    ft.Container(
                        padding=8,
                        bgcolor="#ffffff",
                        border=ft.border.all(1, "#e2e8f0"),
                        border_radius=8,
                        content=ft.Column([
                            ft.Text(f"Sample Row {index + 1}", size=11, weight=ft.FontWeight.W_600),
                            ft.Text(
                                " | ".join(f"{key}: {value}" for key, value in row.items()),
                                size=11,
                                color="#64748b"
                            ),
                        ], spacing=4),
                    )
                    for index, row in enumerate(preview_rows[:5])
                ]
            else:
                self.materiality_preview_column.controls = [
                    ft.Text("No preview available", size=12, color="#64748b")
                ]

        if hasattr(self, "materiality_import_button") and self.materiality_import_button:
            self.materiality_import_button.disabled = not validation.get("is_valid", False)

        if self.page:
            self.page.update()

    def apply_theme(self, colors):
        try:
            # Rebuild to apply theme tokens, then normalize
            self._build_ui()
            from src.utils.theme import apply_theme_to_control
            apply_theme_to_control(self, colors)
            if hasattr(self, 'page') and self.page:
                self.page.update()
        except Exception:
            pass
    
    async def _load_assessment_data(self):
        """Load assessment data from API"""
        try:
            self._show_loading()
            
            # Convert A-001 format to numeric ID for API if needed
            api_reference_id = self.reference_id
            if isinstance(self.reference_id, str) and self.reference_id.startswith("A-"):
                try:
                    api_reference_id = int(self.reference_id[2:])  # Extract number from A-001 -> 1
                    print(f"DEBUG: Converted {self.reference_id} to {api_reference_id}")
                except ValueError:
                    print(f"DEBUG: Failed to convert {self.reference_id} to numeric ID")
                    self._show_error("Invalid assessment ID format")
                    return
            
            print(f"DEBUG: Loading assessment data for reference_id: {api_reference_id} (type: {type(api_reference_id)})")
            
            # Load assessment, heatmap, and findings context concurrently.
            tasks = [
                self.assessment_controller.get_risk_assessment(api_reference_id),
                self.assessment_controller.get_heatmap_data(api_reference_id),
                self.assessment_controller.auditing_client.get_findings_by_reference(api_reference_id),
                self.assessment_controller.auditing_client.get_procedures_by_reference(api_reference_id),
                self.assessment_controller.auditing_client.get_procedure_library(),
                self.assessment_controller.auditing_client.get_planning_by_reference(api_reference_id),
                self.assessment_controller.auditing_client.get_scope_items_by_reference(api_reference_id),
                self.assessment_controller.auditing_client.get_engagement_types(),
                self.assessment_controller.auditing_client.get_planning_statuses(),
                self.assessment_controller.auditing_client.get_risk_control_matrix_by_reference(api_reference_id),
                self.assessment_controller.auditing_client.get_control_classifications(),
                self.assessment_controller.auditing_client.get_control_types(),
                self.assessment_controller.auditing_client.get_control_frequencies(),
                self.assessment_controller.auditing_client.get_walkthroughs_by_reference(api_reference_id),
                self.assessment_controller.auditing_client.get_working_papers_by_reference(api_reference_id),
                self.assessment_controller.auditing_client.get_working_paper_templates(),
                self.assessment_controller.auditing_client.get_finding_severities(),
                self.assessment_controller.auditing_client.get_finding_statuses(),
                self.assessment_controller.auditing_client.get_recommendation_statuses(),
                self.assessment_controller.auditing_client.get_procedure_types(),
                self.assessment_controller.auditing_client.get_procedure_statuses(),
                self.assessment_controller.auditing_client.get_working_paper_statuses(),
                self.assessment_controller.auditing_client.get_documents_by_reference(api_reference_id),
                self.assessment_controller.auditing_client.get_document_categories(),
                self.assessment_controller.auditing_client.get_document_visibility_options(),
                self.assessment_controller.auditing_client.get_evidence_requests_by_reference(api_reference_id),
                self.assessment_controller.auditing_client.get_evidence_request_statuses(),
                self.assessment_controller.auditing_client.get_management_actions_by_reference(api_reference_id),
                self.assessment_controller.auditing_client.get_workflow_instances_by_reference(api_reference_id),
                self.assessment_controller.auditing_client.get_workflow_timeline(api_reference_id, limit=50),
                self.assessment_controller.auditing_client.get_audit_trail_events(api_reference_id, limit=100),
                self.assessment_controller.auditing_client.get_audit_trail_dashboard(api_reference_id, limit=25),
                self.assessment_controller.auditing_client.get_materiality_workspace(api_reference_id),
                self.assessment_controller.auditing_client.get_collaborator_roles(),
                self.assessment_controller.auditing_client.get_reference_collaborators(api_reference_id),
                self.assessment_controller.auditing_client.get_document_access_logs(api_reference_id, limit=25),
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            self.assessment_data = results[0] if not isinstance(results[0], Exception) else None
            self.heatmap_data = results[1] if not isinstance(results[1], Exception) else None
            self.findings_data = results[2] if not isinstance(results[2], Exception) and results[2] else []
            self.procedures_data = results[3] if not isinstance(results[3], Exception) and results[3] else []
            self.procedure_library = results[4] if not isinstance(results[4], Exception) and results[4] else []
            self.planning_data = results[5] if not isinstance(results[5], Exception) else None
            self.scope_items_data = results[6] if not isinstance(results[6], Exception) and results[6] else []
            self.engagement_types = results[7] if not isinstance(results[7], Exception) and results[7] else []
            self.planning_statuses = results[8] if not isinstance(results[8], Exception) and results[8] else []
            self.risk_control_matrix_data = results[9] if not isinstance(results[9], Exception) and results[9] else []
            self.control_classifications = results[10] if not isinstance(results[10], Exception) and results[10] else []
            self.control_types = results[11] if not isinstance(results[11], Exception) and results[11] else []
            self.control_frequencies = results[12] if not isinstance(results[12], Exception) and results[12] else []
            self.walkthroughs_data = results[13] if not isinstance(results[13], Exception) and results[13] else []
            self.working_papers_data = results[14] if not isinstance(results[14], Exception) and results[14] else []
            self.working_paper_templates = results[15] if not isinstance(results[15], Exception) and results[15] else []
            self.finding_severities = results[16] if not isinstance(results[16], Exception) and results[16] else []
            self.finding_statuses = results[17] if not isinstance(results[17], Exception) and results[17] else []
            self.recommendation_statuses = results[18] if not isinstance(results[18], Exception) and results[18] else []
            self.procedure_types = results[19] if not isinstance(results[19], Exception) and results[19] else []
            self.procedure_statuses = results[20] if not isinstance(results[20], Exception) and results[20] else []
            self.working_paper_statuses = results[21] if not isinstance(results[21], Exception) and results[21] else []
            self.documents_data = results[22] if not isinstance(results[22], Exception) and results[22] else []
            self.document_categories = results[23] if not isinstance(results[23], Exception) and results[23] else []
            self.document_visibility_options = results[24] if not isinstance(results[24], Exception) and results[24] else []
            self.evidence_requests_data = results[25] if not isinstance(results[25], Exception) and results[25] else []
            self.evidence_request_statuses = results[26] if not isinstance(results[26], Exception) and results[26] else []
            self.management_actions_data = results[27] if not isinstance(results[27], Exception) and results[27] else []
            self.workflow_instances = results[28] if not isinstance(results[28], Exception) and results[28] else []
            self.workflow_timeline = results[29] if not isinstance(results[29], Exception) and results[29] else []
            self.audit_trail_events = results[30] if not isinstance(results[30], Exception) and results[30] else []
            self.audit_trail_dashboard = results[31] if not isinstance(results[31], Exception) else None
            self.materiality_workspace = results[32] if not isinstance(results[32], Exception) else None
            self.collaborator_roles = results[33] if not isinstance(results[33], Exception) and results[33] else []
            self.reference_collaborators = results[34] if not isinstance(results[34], Exception) and results[34] else []
            self.document_access_logs = results[35] if not isinstance(results[35], Exception) and results[35] else []
            self.audit_coverage_map = None

            if self._is_internal_audit():
                try:
                    self.audit_coverage_map = await self.assessment_controller.auditing_client.get_audit_coverage_map(
                        self._get_coverage_reporting_year()
                    )
                except Exception:
                    self.audit_coverage_map = None

            await self._load_collaboration_state()
            await self._load_workflow_state()

            self.recommendations_data = []
            if self.findings_data:
                recommendation_tasks = [
                    self.assessment_controller.auditing_client.get_recommendations_by_finding(
                        self._get_field(finding, "id", "Id")
                    )
                    for finding in self.findings_data
                    if self._get_field(finding, "id", "Id")
                ]
                if recommendation_tasks:
                    recommendation_results = await asyncio.gather(*recommendation_tasks, return_exceptions=True)
                    for result in recommendation_results:
                        if not isinstance(result, Exception) and result:
                            self.recommendations_data.extend(result)

            self.workflow_status = self._derive_workflow_status()
            
            print(f"DEBUG: Assessment data loaded: {self.assessment_data is not None}")
            if self.assessment_data:
                print(f"DEBUG: Assessment data keys: {list(self.assessment_data.keys()) if isinstance(self.assessment_data, dict) else 'Not a dict'}")
            
            if self.assessment_data:
                self._update_ui_with_data()
                if self.current_tab == self.finance_tab_index:
                    self.page.run_task(self._refresh_finance_audit_workspace)
            else:
                self._show_error("Failed to load assessment data")
                
        except Exception as e:
            print(f"DEBUG: Exception in _load_assessment_data: {str(e)}")
            self._show_error(f"Error loading assessment: {str(e)}")
        finally:
            self._hide_loading()
    
    def _build_ui(self):
        """Build the main UI structure"""
        # Main content tabs
        tabs = self._build_content_tabs()
        
        # Action panel
        action_panel = self._build_action_panel()
        
        # Layout
        main_panel = ft.Column([
            tabs,
            ft.Divider(height=1, color="#e6e9ed"),
            action_panel
        ], spacing=0, expand=True, scroll=ft.ScrollMode.AUTO)
        self.cards_column.controls.clear()
        self.add_card(main_panel)
    
    # Legacy header removed; BaseView header is used.
    
    def _build_status_bar(self):
        """Build the status indicator bar"""
        return ft.Container(
            height=50,
            bgcolor="#f8f9fa",
            padding=ft.padding.symmetric(horizontal=30, vertical=10),
            content=ft.Row([
                # Workflow status
                ft.Row([
                    ft.Icon(Icons.ASSIGNMENT, color="#3498db", size=20),
                    ft.Text("Status:", weight=ft.FontWeight.BOLD, color="#2c3e50"),
                    ft.Container(
                        content=ft.Text(
                            self.workflow_status,
                            color="white",
                            weight=ft.FontWeight.BOLD,
                            size=12
                        ),
                        bgcolor=self._get_status_color(self.workflow_status),
                        padding=ft.padding.symmetric(horizontal=10, vertical=5),
                        border_radius=12
                    )
                ], spacing=10),
                
                ft.Container(width=30),
                
                # Last updated
                ft.Row([
                    ft.Icon(Icons.UPDATE, color="#7f8c8d", size=20),
                    ft.Text("Last Updated:", weight=ft.FontWeight.BOLD, color="#2c3e50"),
                    ft.Text("Loading...", color="#7f8c8d")
                ], spacing=10),
                
                ft.Container(expand=True),
                
                # Risk level indicator
                ft.Row([
                    ft.Icon(Icons.WARNING, color="#e74c3c", size=20),
                    ft.Text("Risk Level:", weight=ft.FontWeight.BOLD, color="#2c3e50"),
                    ft.Container(
                        content=ft.Text(
                            "Loading...",
                            color="white",
                            weight=ft.FontWeight.BOLD,
                            size=12
                        ),
                        bgcolor="#95a5a6",
                        padding=ft.padding.symmetric(horizontal=10, vertical=5),
                        border_radius=12
                    )
                ], spacing=10)
            ])
        )
    
    def _build_content_tabs(self):
        """Build the main content tabs"""
        return ft.Container(
            height=860,
            content=ft.Tabs(
                selected_index=self.current_tab,
                on_change=self._on_tab_change,
                scrollable=True,
                tabs=[
                    ft.Tab(
                        text="Overview",
                        icon=Icons.DASHBOARD,
                        content=self._build_overview_tab()
                    ),
                    ft.Tab(
                        text="Planning",
                        icon=Icons.EVENT_NOTE,
                        content=self._build_planning_tab()
                    ),
                    ft.Tab(
                        text="Risk & Controls",
                        icon=Icons.ANALYTICS,
                        content=self._build_risk_analysis_tab()
                    ),
                    ft.Tab(
                        text="Controls",
                        icon=Icons.SECURITY,
                        content=self._build_controls_tab()
                    ),
                    ft.Tab(
                        text="Procedures",
                        icon=Icons.ASSIGNMENT,
                        content=self._build_procedures_tab()
                    ),
                    ft.Tab(
                        text="Walkthroughs",
                        icon=Icons.ROUTE,
                        content=self._build_walkthroughs_tab()
                    ),
                    ft.Tab(
                        text="Working Papers",
                        icon=Icons.DESCRIPTION,
                        content=self._build_working_papers_tab()
                    ),
                    ft.Tab(
                        text="Documents",
                        icon=Icons.FOLDER_OPEN,
                        content=self._build_documents_tab()
                    ),
                    ft.Tab(
                        text="Findings",
                        icon=Icons.SEARCH,
                        content=self._build_findings_tab()
                    ),
                    ft.Tab(
                        text="Management Actions",
                        icon=Icons.TASK_ALT,
                        content=self._build_management_actions_tab()
                    ),
                    ft.Tab(
                        text="Finance Reporting",
                        icon=Icons.ACCOUNT_BALANCE,
                        content=self._build_finance_reporting_tab()
                    ),
                    ft.Tab(
                        text="Heatmap",
                        icon=Icons.VIEW_MODULE,
                        content=self._build_heatmap_tab()
                    ),
                    ft.Tab(
                        text="Collaboration",
                        icon=Icons.GROUP,
                        content=self._build_collaboration_tab()
                    ),
                    ft.Tab(
                        text="Audit Trail",
                        icon=Icons.HISTORY,
                        content=self._build_audit_trail_tab()
                    )
                ]
            )
        )
    
    def _build_overview_tab(self):
        """Build the overview tab content"""
        # Get data values with fallbacks
        client = "Loading..."
        assessor = "Loading..."
        start_date = "Loading..."
        end_date = "Loading..."
        approved_by = "Loading..."
        risk_count = 0
        
        if self.assessment_data:
            if isinstance(self.assessment_data, dict):
                client = self.assessment_data.get('Client', 'N/A')
                assessor = self.assessment_data.get('Assessor', 'N/A')
                start_date = self.assessment_data.get('AssessmentStartDate', 'N/A')
                end_date = self.assessment_data.get('AssessmentEndDate', 'N/A')
                approved_by = self.assessment_data.get('ApprovedBy', 'N/A')
                risk_assessments = self.assessment_data.get('RiskAssessments', [])
                risk_count = len(risk_assessments) if risk_assessments else 0
            else:
                client = getattr(self.assessment_data, 'Client', 'N/A')
                assessor = getattr(self.assessment_data, 'Assessor', 'N/A')
                start_date = getattr(self.assessment_data, 'AssessmentStartDate', 'N/A')
                end_date = getattr(self.assessment_data, 'AssessmentEndDate', 'N/A')
                approved_by = getattr(self.assessment_data, 'ApprovedBy', 'N/A')
                risk_assessments = getattr(self.assessment_data, 'RiskAssessments', [])
                risk_count = len(risk_assessments) if risk_assessments else 0
        
        # Format dates
        if start_date != "Loading..." and start_date != "N/A" and start_date:
            try:
                if isinstance(start_date, str):
                    start_date = start_date.split('T')[0]  # Remove time part if present
            except:
                pass
                
        if end_date != "Loading..." and end_date != "N/A" and end_date:
            try:
                if isinstance(end_date, str):
                    end_date = end_date.split('T')[0]  # Remove time part if present
            except:
                pass
        
        completion_pct = self._calculate_completion_percentage(risk_count, approved_by)
        progress_value = completion_pct / 100
        timeline_items = self._build_timeline_data(approved_by)
        overall_materiality = self._get_active_materiality_value("overallMateriality", "OverallMateriality")
        dynamic_metric_title = "Completion"
        dynamic_metric_value = f"{completion_pct}%"
        dynamic_metric_color = "#9b59b6"
        dynamic_metric_icon = Icons.ASSESSMENT
        if self._is_internal_audit():
            dynamic_metric_title = "Open Actions"
            dynamic_metric_value = str(self._count_open_management_actions())
            dynamic_metric_color = "#0f766e"
            dynamic_metric_icon = Icons.TASK_ALT
        elif self._is_external_audit() or self._has_materiality_data():
            dynamic_metric_title = "Materiality"
            dynamic_metric_value = "Set" if overall_materiality not in (None, "", 0, 0.0) else "Pending"
            dynamic_metric_color = "#2563eb"
            dynamic_metric_icon = Icons.ACCOUNT_BALANCE

        return ft.Container(
            padding=20,
            content=ft.Column([
                # Key metrics cards
                ft.Row([
                    self._create_metric_card("Reference ID", str(self.reference_id) if self.reference_id else "N/A", "#3498db", Icons.INFO),
                    self._create_metric_card("Risk Items", str(risk_count), "#2ecc71", Icons.SECURITY),
                    self._create_metric_card("Status", self.workflow_status, "#f39c12", Icons.INFO),
                    self._create_metric_card(dynamic_metric_title, dynamic_metric_value, dynamic_metric_color, dynamic_metric_icon)
                ], spacing=20),
                
                ft.Container(height=20),
                self._build_engagement_mode_card(),
                ft.Container(height=20),
                self._build_coverage_snapshot_card("Coverage Outlook", compact=True) if self._is_internal_audit() else ft.Container(),
                ft.Container(height=20) if self._is_internal_audit() else ft.Container(),
                
                # Assessment summary
                ft.Row([
                    # Left column - Basic info
                    ft.Column([
                        ft.Card(
                            content=ft.Container(
                                padding=20,
                                content=ft.Column([
                                    ft.Text("Audit File Summary", size=18, weight=ft.FontWeight.BOLD, color="#2c3e50"),
                                    ft.Divider(),
                                    self._create_info_row("Client", client),
                                    self._create_info_row("Assessor", assessor),
                                    self._create_info_row("Start Date", start_date),
                                    self._create_info_row("End Date", end_date),
                                    self._create_info_row("Approved By", approved_by),
                                    self._create_info_row("Risk Items", str(risk_count))
                                ])
                            )
                        )
                    ], expand=1),
                    
                    ft.Container(width=20),
                    
                    # Right column - Progress and timeline
                    ft.Column([
                        ft.Card(
                            content=ft.Container(
                                padding=20,
                                content=ft.Column([
                                    ft.Text("Audit Workflow Progress", size=18, weight=ft.FontWeight.BOLD, color="#2c3e50"),
                                    ft.Divider(),
                                    ft.Container(
                                        content=ft.ProgressBar(value=progress_value, bgcolor="#ecf0f1", color="#3498db"),
                                        width=300
                                    ),
                                    ft.Text(f"{completion_pct}% Complete", color="#7f8c8d"),
                                    ft.Container(height=20),
                                    ft.Text("Timeline", size=16, weight=ft.FontWeight.BOLD),
                                    ft.Container(height=10),
                                    ft.Column(
                                        [self._create_timeline_item(item["title"], item["status"], item["color"]) for item in timeline_items],
                                        spacing=0
                                    )
                                ])
                            )
                        )
                    ], expand=1)
                ])
            ], scroll=ft.ScrollMode.AUTO)
        )

    def _build_planning_tab(self):
        planning_status = self._get_field(self.planning_data, "planningStatusName", "PlanningStatusName", default="Not Started")
        engagement_profile = self._get_engagement_profile()
        return ft.Container(
            padding=20,
            content=ft.Column([
                ft.Row([
                    ft.Text("Planning and Scoping", size=20, weight=ft.FontWeight.BOLD, color="#2c3e50"),
                    ft.Container(expand=True),
                    ft.OutlinedButton(
                        text="Request Approval",
                        icon=Icons.GAVEL,
                        on_click=self._open_planning_approval_workflow_dialog,
                        visible=can_start_workflows(self.user)
                    ),
                    ft.OutlinedButton(
                        text="Annual Plan Approval",
                        icon=Icons.CALENDAR_MONTH,
                        on_click=self._open_annual_plan_approval_workflow_dialog,
                        visible=can_start_workflows(self.user)
                    ) if self._is_internal_audit() else ft.Container(),
                    ft.OutlinedButton(
                        text="Scope Sign-Off",
                        icon=Icons.RULE,
                        on_click=self._open_scope_approval_workflow_dialog,
                        visible=can_start_workflows(self.user)
                    ),
                    ft.OutlinedButton(
                        text="Calculate Materiality",
                        icon=Icons.CALCULATE,
                        on_click=self._open_materiality_calculator_dialog,
                        visible=self._is_external_audit()
                    ),
                    ft.OutlinedButton(
                        text="Add Scope Item",
                        icon=Icons.ADD_TASK,
                        on_click=self._open_scope_item_dialog
                    ),
                    ft.ElevatedButton(
                        text="Update Planning",
                        icon=Icons.EDIT_NOTE,
                        bgcolor="#1d4ed8",
                        color="white",
                        on_click=self._open_planning_dialog
                    )
                ]),
                ft.Container(height=20),
                self._build_engagement_mode_card(),
                ft.Container(height=20),
                ft.Row(self._build_planning_summary_cards(), spacing=15, scroll=ft.ScrollMode.AUTO),
                ft.Container(height=20) if self._is_internal_audit() else ft.Container(),
                self._build_coverage_snapshot_card("Annual Audit Plan Coverage") if self._is_internal_audit() else ft.Container(),
                ft.Container(height=20),
                self._build_materiality_workspace_card() if self._is_external_audit() else ft.Container(),
                ft.Container(height=20) if self._is_external_audit() else ft.Container(),
                ft.Card(
                    content=ft.Container(
                        padding=20,
                        content=ft.Column([
                            ft.Row([
                                ft.Text("Planning Workspace", size=16, weight=ft.FontWeight.BOLD),
                                ft.Container(expand=True),
                                ft.Container(
                                    content=ft.Text(planning_status, size=11, color="white"),
                                    bgcolor=self._get_field(self.planning_data, "planningStatusColor", "PlanningStatusColor", default="#64748b"),
                                    padding=ft.padding.symmetric(horizontal=10, vertical=5),
                                    border_radius=12
                                )
                            ]),
                            ft.Divider(),
                            ft.Column([
                                self._create_info_row("Engagement", self._get_field(self.planning_data, "engagementTitle", "EngagementTitle", default="Not set")),
                                self._create_info_row("Engagement Type", self._get_field(self.planning_data, "engagementTypeName", "EngagementTypeName", default="Not set")),
                                self._create_info_row("Annual Plan", self._get_field(self.planning_data, "annualPlanName", "AnnualPlanName", default="Not set")),
                                self._create_info_row("Coverage Year", str(self._get_coverage_reporting_year())) if self._is_internal_audit() else ft.Container(),
                                self._create_info_row("Scope Letter", self._get_field(self.planning_data, "scopeLetterDocumentTitle", "ScopeLetterDocumentTitle", default="Not linked")),
                                self._create_info_row("Signed Off", "Yes" if self._get_field(self.planning_data, "isSignedOff", "IsSignedOff", default=False) else "No"),
                                self._create_info_row("Focus", engagement_profile.get("focus_label", "Balanced audit workflow")),
                            ], spacing=8),
                            ft.Container(height=10),
                            ft.Text(self._get_field(self.planning_data, "scopeSummary", "ScopeSummary", default="No scope summary captured yet."), size=12, color="#475569"),
                            ft.Text(self._get_field(self.planning_data, "riskStrategy", "RiskStrategy", default=""), size=12, color="#64748b"),
                            ft.Text(
                                self._build_materiality_summary_text(),
                                size=12,
                                color="#475569"
                            )
                        ], spacing=8)
                    )
                ),
                ft.Container(height=20) if (self._is_external_audit() or self._has_materiality_data()) else ft.Container(),
                self._build_materiality_details_card() if (self._is_external_audit() or self._has_materiality_data()) else ft.Container(),
                ft.Container(height=20) if (self._is_external_audit() or self._has_materiality_data()) else ft.Container(),
                self._build_materiality_application_card() if (self._is_external_audit() or self._has_materiality_data()) else ft.Container(),
                ft.Container(height=20),
                ft.Card(
                    content=ft.Container(
                        padding=20,
                        content=ft.Column([
                            ft.Row([
                                ft.Text("Scope Register", size=16, weight=ft.FontWeight.BOLD),
                                ft.Container(expand=True),
                                ft.Text(f"{len(self.scope_items_data)} items", size=12, color="#7f8c8d")
                            ]),
                            ft.Divider(),
                            ft.Container(
                                content=ft.Column(self._build_scope_item_controls(), spacing=12),
                                bgcolor="#f8f9fa",
                                padding=15,
                                border_radius=5,
                                width=920
                            )
                        ])
                    )
                )
            ], scroll=ft.ScrollMode.AUTO)
        )

    def _build_planning_summary_cards(self):
        in_scope = sum(1 for item in self.scope_items_data if self._get_field(item, "includeInScope", "IncludeInScope", default=True))
        fsli_items = sum(1 for item in self.scope_items_data if self._get_field(item, "fsli", "Fsli", default=""))
        assigned_procedures = sum(1 for item in self.scope_items_data if self._get_field(item, "procedureId", "ProcedureId"))
        assertions_count = sum(1 for item in self.scope_items_data if self._get_field(item, "assertions", "Assertions", default=""))
        control_focused = sum(
            1 for item in self.scope_items_data
            if "control" in (self._get_field(item, "scopeStatus", "ScopeStatus", default="") or "").lower()
        )
        cards = [("Scope Items", len(self.scope_items_data), "#1d4ed8"), ("In Scope", in_scope, "#0f766e")]
        if self._is_external_audit():
            cards.extend([
                ("FSLI Scoped", fsli_items, "#7c3aed"),
                ("Assertions Mapped", assertions_count, "#2563eb"),
                ("Procedure Linked", assigned_procedures, "#f59e0b"),
            ])
        elif self._is_internal_audit():
            cards.extend([
                ("Control Focused", control_focused, "#7c3aed"),
                ("Open Actions", self._count_open_management_actions(), "#dc2626"),
                ("Procedure Linked", assigned_procedures, "#f59e0b"),
            ])
        else:
            cards.extend([
                ("FSLI Tagged", fsli_items, "#7c3aed"),
                ("Procedure Linked", assigned_procedures, "#f59e0b"),
            ])
        return [
            ft.Container(
                width=180,
                padding=15,
                bgcolor="white",
                border=ft.border.all(1, "#e6e9ed"),
                border_radius=10,
                content=ft.Column([
                    ft.Text(label, size=12, color="#7f8c8d"),
                    ft.Text(str(value), size=24, weight=ft.FontWeight.BOLD, color=color)
                ], spacing=4)
            )
            for label, value, color in cards
        ]

    def _build_scope_item_controls(self):
        if not self.scope_items_data:
            return [ft.Text("No scope items defined yet.", color="#7f8c8d")]

        controls = []
        for item in self.scope_items_data:
            label = self._get_scope_item_label(item)
            controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text(label, weight=ft.FontWeight.BOLD, size=14),
                            ft.Container(expand=True),
                            ft.Container(
                                content=ft.Text(
                                    "In Scope" if self._get_field(item, "includeInScope", "IncludeInScope", default=True) else "Out of Scope",
                                    size=11,
                                    color="white"
                                ),
                                bgcolor="#16a34a" if self._get_field(item, "includeInScope", "IncludeInScope", default=True) else "#64748b",
                                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                border_radius=10
                            )
                        ]),
                        ft.Text(f"Status: {self._get_field(item, 'scopeStatus', 'ScopeStatus', default='Planned')}", size=11, color="#64748b"),
                        ft.Text(
                            f"Risk Ref: {self._get_field(item, 'riskReference', 'RiskReference', default='-')} | Control Ref: {self._get_field(item, 'controlReference', 'ControlReference', default='-')}",
                            size=11,
                            color="#475569"
                        ),
                        ft.Text(
                            f"Assertions: {self._get_field(item, 'assertions', 'Assertions', default='Not mapped')}",
                            size=11,
                            color="#475569"
                        ) if self._is_external_audit() else ft.Container(),
                        ft.Text(
                            f"Rationale: {self._get_field(item, 'scopingRationale', 'ScopingRationale', default='Not captured')}",
                            size=11,
                            color="#64748b"
                        ) if self._get_field(item, "scopingRationale", "ScopingRationale", default="") else ft.Container(),
                        ft.Text(
                            f"Procedure: {self._get_field(item, 'procedureTitle', 'ProcedureTitle', default='Not linked')}",
                            size=11,
                            color="#475569"
                        ),
                        ft.Row([
                            ft.Text(f"Owner: {self._get_field(item, 'owner', 'Owner', default='Unassigned')}", size=11, color="#7f8c8d"),
                            ft.Container(expand=True),
                            ft.TextButton("Edit", icon=Icons.EDIT, on_click=lambda _, scope_item=item: self._open_edit_scope_item_dialog(scope_item)),
                            ft.TextButton("Delete", icon=Icons.DELETE, on_click=lambda _, scope_item=item: self._delete_scope_item(scope_item))
                        ])
                    ], spacing=5),
                    padding=12,
                    bgcolor="white",
                    border_radius=8,
                    border=ft.border.all(1, "#e6e9ed")
                )
            )
        return controls
    
    def _build_risk_analysis_tab(self):
        """Build the risk analysis tab"""
        matrix_rows = []
        for entry in self.risk_control_matrix_data or []:
            scope_item = next(
                (
                    item for item in self.scope_items_data or []
                    if str(self._get_field(item, "id", "Id", default="")) == str(self._get_field(entry, "scopeItemId", "ScopeItemId", default=""))
                ),
                None
            )
            matrix_rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(self._get_field(entry, "riskTitle", "RiskTitle", default="Risk"), size=12)),
                        ft.DataCell(ft.Text(self._get_field(entry, "riskDescription", "RiskDescription", default="Not captured"), size=12)),
                        ft.DataCell(ft.Text(self._get_field(entry, "controlName", "ControlName", default="Control"), size=12)),
                        ft.DataCell(ft.Text(self._get_field(entry, "controlDescription", "ControlDescription", default="Not captured"), size=12)),
                        ft.DataCell(ft.Text(self._get_field(entry, "controlAdequacy", "ControlAdequacy", default="Not assessed"), size=12)),
                        ft.DataCell(ft.Text(self._get_field(entry, "controlEffectiveness", "ControlEffectiveness", default="Not tested"), size=12)),
                        ft.DataCell(ft.Text(self._get_scope_item_label(scope_item) if scope_item else "Not linked", size=12)),
                    ]
                )
            )

        if not matrix_rows:
            risk_assessments = []
            if self.assessment_data:
                if isinstance(self.assessment_data, dict):
                    risk_assessments = self.assessment_data.get("RiskAssessments", [])
                else:
                    risk_assessments = getattr(self.assessment_data, "RiskAssessments", [])

            for i, risk in enumerate(risk_assessments or []):
                risk_title = self._get_field(risk, "RisksAssessment_KeyRiskAndFactors", default=f"Risk {i + 1}")
                business_context = " | ".join(
                    [
                        str(self._get_field(risk, "ProcessObjectivesAssessment_BusinessObjectives", default="") or "").strip(),
                        str(self._get_field(risk, "ProcessObjectivesAssessment_MainProcess", default="") or "").strip(),
                        str(self._get_field(risk, "ProcessObjectivesAssessment_SubProcess", default="") or "").strip(),
                    ]
                ).strip(" |")
                matrix_rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(risk_title, size=12)),
                            ft.DataCell(ft.Text(business_context or "Business context not captured", size=12)),
                            ft.DataCell(ft.Text(self._get_field(risk, "ControlsAssessment_MitigatingControls", default="Control not captured"), size=12)),
                            ft.DataCell(ft.Text(self._get_field(risk, "OutcomeAssessment_AuditorsRecommendedActionPlan", default="Control description not captured"), size=12)),
                            ft.DataCell(ft.Text(self._get_field(risk, "RisksAssessment_RiskLikelihood", default="N/A"), size=12)),
                            ft.DataCell(ft.Text(self._get_field(risk, "RisksAssessment_RiskImpact", default="N/A"), size=12)),
                            ft.DataCell(ft.Text(self._get_field(risk, "RisksAssessment_RiskCategory", default="N/A"), size=12)),
                        ]
                    )
                )

        risk_table = (
            ft.Row(
                [
                    ft.DataTable(
                        columns=[
                            ft.DataColumn(ft.Text("Risk Title")),
                            ft.DataColumn(ft.Text("Description / Context")),
                            ft.DataColumn(ft.Text("Control")),
                            ft.DataColumn(ft.Text("Control Description / Action")),
                            ft.DataColumn(ft.Text("Adequacy / Likelihood")),
                            ft.DataColumn(ft.Text("Effectiveness / Impact")),
                            ft.DataColumn(ft.Text("Scope / Category")),
                        ],
                        rows=matrix_rows,
                        heading_row_color="#f8f9fa",
                        border=ft.border.all(1, "#e6e9ed"),
                        border_radius=8,
                        data_row_min_height=56,
                        data_row_max_height=80,
                        column_spacing=18,
                    )
                ],
                scroll=ft.ScrollMode.AUTO,
            )
            if matrix_rows
            else ft.Container(
                content=ft.Text("No risk assessment or matrix items found yet.", color="#7f8c8d"),
                padding=20,
                alignment=ft.alignment.center
            )
        )
        
        return ft.Container(
            padding=20,
            content=ft.Column([
                ft.Row([
                    ft.Text("Risk and Control Matrix", size=20, weight=ft.FontWeight.BOLD, color="#2c3e50"),
                    ft.Container(expand=True),
                    ft.ElevatedButton(
                        text="Add Matrix Entry",
                        icon=Icons.POST_ADD,
                        bgcolor="#2563eb",
                        color="white",
                        on_click=self._open_risk_control_matrix_entry_dialog
                    )
                ]),
                ft.Container(height=20),
                ft.Card(
                    content=ft.Container(
                        padding=20,
                        content=ft.Column([
                            ft.Text("Risk Assessment Items", size=16, weight=ft.FontWeight.BOLD, color="#2c3e50"),
                            ft.Divider(),
                            ft.Container(
                                content=risk_table,
                                height=280
                            )
                        ])
                    )
                ),
                ft.Container(height=20),
                ft.Card(
                    content=ft.Container(
                        padding=20,
                        content=ft.Column([
                            ft.Row([
                                ft.Text("Matrix Register", size=16, weight=ft.FontWeight.BOLD),
                                ft.Container(expand=True),
                                ft.Text(f"{len(self.risk_control_matrix_data)} entries", size=12, color="#7f8c8d")
                            ]),
                            ft.Divider(),
                            ft.Container(
                                content=ft.Column(self._build_risk_control_matrix_controls(), spacing=12),
                                bgcolor="#f8f9fa",
                                padding=15,
                                border_radius=5,
                                width=920
                            )
                        ])
                    )
                )
            ], scroll=ft.ScrollMode.AUTO)
        )
    
    def _build_controls_tab(self):
        """Build the controls tab"""
        return ft.Container(
            padding=20,
            content=ft.Column([
                # Controls header with actions
                ft.Row([
                    ft.Text("Control Framework", size=20, weight=ft.FontWeight.BOLD, color="#2c3e50"),
                    ft.Container(expand=True),
                    ft.ElevatedButton(
                        text="Test Controls",
                        icon=Icons.PLAY_ARROW,
                        bgcolor="#3498db",
                        color="white",
                        on_click=self._start_control_testing,
                        visible=can_start_workflows(self.user)
                    )
                ]),
                
                ft.Container(height=20),
                
                # Controls effectiveness summary
                ft.Card(
                    content=ft.Container(
                        padding=20,
                        content=ft.Column([
                            ft.Text("Control Effectiveness Summary", size=16, weight=ft.FontWeight.BOLD),
                            ft.Divider(),
                            ft.Row([
                                self._create_control_status_card("Effective", "8", "#2ecc71"),
                                self._create_control_status_card("Needs Improvement", "3", "#f39c12"),
                                self._create_control_status_card("Ineffective", "1", "#e74c3c"),
                                self._create_control_status_card("Not Tested", "2", "#95a5a6")
                            ], spacing=20)
                        ])
                    )
                ),
                
                ft.Container(height=20),
                
                # Controls detail table
                ft.Card(
                    content=ft.Container(
                        padding=20,
                        content=ft.Column([
                            ft.Text("Control Details", size=16, weight=ft.FontWeight.BOLD),
                            ft.Divider(),
                            ft.DataTable(
                                columns=[
                                    ft.DataColumn(ft.Text("Control ID")),
                                    ft.DataColumn(ft.Text("Description")),
                                    ft.DataColumn(ft.Text("Type")),
                                    ft.DataColumn(ft.Text("Effectiveness")),
                                    ft.DataColumn(ft.Text("Last Tested")),
                                    ft.DataColumn(ft.Text("Actions"))
                                ],
                                rows=[
                                    # Will be populated with actual data
                                    ft.DataRow(cells=[
                                        ft.DataCell(ft.Text("CTRL-001")),
                                        ft.DataCell(ft.Text("Access Control Management")),
                                        ft.DataCell(ft.Text("Preventive")),
                                        ft.DataCell(ft.Container(
                                            content=ft.Text("Effective", color="white", size=12),
                                            bgcolor="#2ecc71",
                                            padding=5,
                                            border_radius=3
                                        )),
                                        ft.DataCell(ft.Text("2025-03-01")),
                                        ft.DataCell(ft.IconButton(
                                            icon=Icons.MORE_VERT,
                                            tooltip="Control actions"
                                        ))
                                    ])
                                ],
                                border=ft.border.all(1, "#e6e9ed"),
                                border_radius=5,
                                heading_row_color="#f8f9fa"
                            )
                        ])
                    )
                )
            ], scroll=ft.ScrollMode.AUTO)
        )

    def _build_risk_control_matrix_controls(self):
        if not self.risk_control_matrix_data:
            return [ft.Text("No risk/control matrix entries captured yet.", color="#7f8c8d")]

        controls = []
        for entry in self.risk_control_matrix_data:
            controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text(self._get_field(entry, "riskTitle", "RiskTitle", default="Risk"), weight=ft.FontWeight.BOLD, size=14),
                            ft.Container(expand=True),
                            ft.Container(
                                content=ft.Text(self._get_field(entry, "controlClassificationName", "ControlClassificationName", default="Unclassified"), size=11, color="white"),
                                bgcolor="#334155",
                                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                border_radius=10
                            )
                        ]),
                        ft.Text(
                            f"Control: {self._get_field(entry, 'controlName', 'ControlName', default='Not set')}",
                            size=12,
                            color="#1f2937"
                        ),
                        ft.Text(
                            f"Adequacy: {self._get_field(entry, 'controlAdequacy', 'ControlAdequacy', default='Not assessed')} | Effectiveness: {self._get_field(entry, 'controlEffectiveness', 'ControlEffectiveness', default='Not assessed')}",
                            size=11,
                            color="#475569"
                        ),
                        ft.Text(
                            f"Type: {self._get_field(entry, 'controlTypeName', 'ControlTypeName', default='Not set')} | Frequency: {self._get_field(entry, 'controlFrequencyName', 'ControlFrequencyName', default='Not set')} | Owner: {self._get_field(entry, 'controlOwner', 'ControlOwner', default='Unassigned')}",
                            size=11,
                            color="#64748b"
                        ),
                        ft.Text(
                            f"Scope: {self._get_field(entry, 'scopeItemLabel', 'ScopeItemLabel', default='Not linked')} | Procedure: {self._get_field(entry, 'procedureTitle', 'ProcedureTitle', default='Not linked')}",
                            size=11,
                            color="#64748b"
                        ),
                        ft.Row([
                            ft.TextButton("Edit", icon=Icons.EDIT, on_click=lambda _, matrix_entry=entry: self._open_edit_risk_control_matrix_entry_dialog(matrix_entry)),
                            ft.TextButton("Delete", icon=Icons.DELETE, on_click=lambda _, matrix_entry=entry: self._delete_risk_control_matrix_entry(matrix_entry))
                        ])
                    ], spacing=5),
                    padding=12,
                    bgcolor="white",
                    border_radius=8,
                    border=ft.border.all(1, "#e6e9ed")
                )
            )
        return controls

    def _build_walkthroughs_tab(self):
        return ft.Container(
            padding=20,
            content=ft.Column([
                ft.Row([
                    ft.Text("Walkthroughs", size=20, weight=ft.FontWeight.BOLD, color="#2c3e50"),
                    ft.Container(expand=True),
                    ft.OutlinedButton(
                        text="Request Review",
                        icon=Icons.FACT_CHECK,
                        on_click=self._open_latest_walkthrough_workflow_dialog
                    ),
                    ft.ElevatedButton(
                        text="Add Walkthrough",
                        icon=Icons.ADD,
                        bgcolor="#7c3aed",
                        color="white",
                        on_click=self._open_walkthrough_dialog
                    )
                ]),
                ft.Container(height=20),
                ft.Row(self._build_walkthrough_summary_cards(), spacing=15, scroll=ft.ScrollMode.AUTO),
                ft.Container(height=20),
                ft.Card(
                    content=ft.Container(
                        padding=20,
                        content=ft.Column([
                            ft.Row([
                                ft.Text("Walkthrough Register", size=16, weight=ft.FontWeight.BOLD),
                                ft.Container(expand=True),
                                ft.Text(f"{len(self.walkthroughs_data)} walkthroughs", size=12, color="#7f8c8d")
                            ]),
                            ft.Divider(),
                            ft.Container(
                                content=ft.Column(self._build_walkthrough_controls(), spacing=12),
                                bgcolor="#f8f9fa",
                                padding=15,
                                border_radius=5,
                                width=920
                            )
                        ])
                    )
                )
            ], scroll=ft.ScrollMode.AUTO)
        )

    def _build_walkthrough_summary_cards(self):
        exceptions = sum(self._get_field(item, "exceptionCount", "ExceptionCount", default=0) or 0 for item in self.walkthroughs_data)
        linked_scope = sum(1 for item in self.walkthroughs_data if self._get_field(item, "scopeItemId", "ScopeItemId"))
        cards = [
            ("Walkthroughs", len(self.walkthroughs_data), "#7c3aed"),
            ("Exceptions", exceptions, "#dc2626"),
            ("Scope Linked", linked_scope, "#0f766e"),
        ]
        return [
            ft.Container(
                width=180,
                padding=15,
                bgcolor="white",
                border=ft.border.all(1, "#e6e9ed"),
                border_radius=10,
                content=ft.Column([
                    ft.Text(label, size=12, color="#7f8c8d"),
                    ft.Text(str(value), size=24, weight=ft.FontWeight.BOLD, color=color)
                ], spacing=4)
            )
            for label, value, color in cards
        ]

    def _build_walkthrough_controls(self):
        if not self.walkthroughs_data:
            return [ft.Text("No walkthroughs captured yet.", color="#7f8c8d")]

        controls = []
        for walkthrough in self.walkthroughs_data:
            walkthrough_date = self._get_field(walkthrough, "walkthroughDate", "WalkthroughDate", default="")
            if isinstance(walkthrough_date, str) and "T" in walkthrough_date:
                walkthrough_date = walkthrough_date.split("T")[0]
            exception_controls = []
            for exception in self._get_field(walkthrough, "exceptions", "Exceptions", default=[]) or []:
                exception_controls.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Text(self._get_field(exception, "exceptionTitle", "ExceptionTitle", default="Exception"), weight=ft.FontWeight.BOLD, size=11),
                            ft.Text(self._get_field(exception, "exceptionDescription", "ExceptionDescription", default=""), size=11, color="#475569"),
                            ft.Text(
                                f"Severity: {self._get_field(exception, 'severity', 'Severity', default='Medium')} | Linked Finding: {self._get_field(exception, 'linkedFindingNumber', 'LinkedFindingNumber', default='None')}",
                                size=10,
                                color="#7f8c8d"
                            )
                        ], spacing=2),
                        padding=8,
                        bgcolor="white",
                        border=ft.border.all(1, "#e6e9ed"),
                        border_radius=8
                    )
                )

            controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text(self._get_field(walkthrough, "processName", "ProcessName", default="Walkthrough"), weight=ft.FontWeight.BOLD, size=14),
                            ft.Container(expand=True),
                            ft.Text(walkthrough_date or "No date", size=11, color="#64748b")
                        ]),
                        ft.Text(
                            f"Scope: {self._get_field(walkthrough, 'scopeItemLabel', 'ScopeItemLabel', default='Not linked')} | Procedure: {self._get_field(walkthrough, 'procedureTitle', 'ProcedureTitle', default='Not linked')}",
                            size=11,
                            color="#64748b"
                        ),
                        ft.Text(self._get_field(walkthrough, "participants", "Participants", default=""), size=11, color="#475569"),
                        ft.Text(self._get_field(walkthrough, "processNarrative", "ProcessNarrative", default=""), size=11, color="#475569"),
                        ft.Text(f"Evidence: {self._get_field(walkthrough, 'evidenceSummary', 'EvidenceSummary', default='Not captured')}", size=11, color="#475569"),
                        ft.Row(
                            ([
                                ft.TextButton("Request Review", icon=Icons.FACT_CHECK, on_click=lambda _, wt=walkthrough: self._open_walkthrough_workflow_dialog(wt))
                            ] if can_start_workflows(self.user) else [])
                            + [
                                ft.TextButton("Add Exception", icon=Icons.WARNING_AMBER, on_click=lambda _, wt=walkthrough: self._open_add_walkthrough_exception_dialog(wt)),
                                ft.TextButton("Edit", icon=Icons.EDIT, on_click=lambda _, wt=walkthrough: self._open_edit_walkthrough_dialog(wt)),
                                ft.TextButton("Delete", icon=Icons.DELETE, on_click=lambda _, wt=walkthrough: self._delete_walkthrough(wt))
                            ]
                        ),
                        ft.Column(exception_controls, spacing=6)
                    ], spacing=5),
                    padding=12,
                    bgcolor="white",
                    border_radius=8,
                    border=ft.border.all(1, "#e6e9ed")
                )
            )
        return controls

    def _build_procedures_tab(self):
        """Build the procedures tab"""
        filtered_templates = self._get_filtered_procedure_templates()
        return ft.Container(
            padding=20,
            content=ft.Column([
                ft.Row([
                    ft.Text("Audit Procedures", size=20, weight=ft.FontWeight.BOLD, color="#2c3e50"),
                    ft.Container(expand=True),
                    ft.OutlinedButton(
                        text="Use Template",
                        icon=Icons.FILE_COPY,
                        on_click=self._open_add_procedure_from_template_dialog
                    ),
                    ft.ElevatedButton(
                        text="Add Procedure",
                        icon=Icons.ADD,
                        bgcolor="#2563eb",
                        color="white",
                        on_click=self._add_procedure
                    )
                ]),
                ft.Container(height=20),
                ft.Row(self._build_procedure_summary_cards(), spacing=15, scroll=ft.ScrollMode.AUTO),
                ft.Container(height=20),
                ft.Card(
                    content=ft.Container(
                        padding=20,
                        content=ft.Column([
                            ft.Text("Assessment Procedure Register", size=16, weight=ft.FontWeight.BOLD),
                            ft.Divider(),
                            ft.Container(
                                content=ft.Column(self._build_procedure_item_controls(), spacing=12),
                                bgcolor="#f8f9fa",
                                padding=15,
                                border_radius=5,
                                width=900
                            )
                        ])
                    )
                ),
                ft.Container(height=20),
                ft.Card(
                    content=ft.Container(
                        padding=20,
                        content=ft.Column([
                            ft.Row([
                                ft.Text("Reusable Procedure Templates", size=16, weight=ft.FontWeight.BOLD),
                                ft.Container(expand=True),
                                ft.Text(f"{len(filtered_templates)} matched to this audit type", size=12, color="#7f8c8d")
                            ]),
                            ft.Divider(),
                            ft.Container(
                                content=ft.Column(self._build_procedure_template_controls(), spacing=12),
                                bgcolor="#f8f9fa",
                                padding=15,
                                border_radius=5,
                                width=900
                            )
                        ])
                    )
                )
            ], scroll=ft.ScrollMode.AUTO)
        )

    def _build_working_papers_tab(self):
        """Build the working papers tab"""
        filtered_templates = self._get_filtered_working_paper_templates()
        return ft.Container(
            padding=20,
            content=ft.Column([
                ft.Row([
                    ft.Text("Working Papers", size=20, weight=ft.FontWeight.BOLD, color="#2c3e50"),
                    ft.Container(expand=True),
                    ft.OutlinedButton(
                        text="Use Template",
                        icon=Icons.FILE_COPY,
                        on_click=self._open_add_working_paper_from_template_dialog
                    ),
                    ft.ElevatedButton(
                        text="Add Working Paper",
                        icon=Icons.ADD,
                        bgcolor="#0f766e",
                        color="white",
                        on_click=self._add_working_paper
                    )
                ]),
                ft.Container(height=20),
                ft.Row(self._build_working_paper_summary_cards(), spacing=15, scroll=ft.ScrollMode.AUTO),
                ft.Container(height=20),
                ft.Card(
                    content=ft.Container(
                        padding=20,
                        content=ft.Column([
                            ft.Text("Working Paper Register", size=16, weight=ft.FontWeight.BOLD),
                            ft.Divider(),
                            ft.Container(
                                content=ft.Column(self._build_working_paper_item_controls(), spacing=12),
                                bgcolor="#f8f9fa",
                                padding=15,
                                border_radius=5,
                                width=920
                            )
                        ])
                    )
                ),
                ft.Container(height=20),
                ft.Card(
                    content=ft.Container(
                        padding=20,
                        content=ft.Column([
                            ft.Row([
                                ft.Text("Working Paper Templates", size=16, weight=ft.FontWeight.BOLD),
                                ft.Container(expand=True),
                                ft.Text(f"{len(filtered_templates)} matched to this audit type", size=12, color="#7f8c8d")
                            ]),
                            ft.Divider(),
                            ft.Container(
                                content=ft.Column(self._build_working_paper_template_controls(), spacing=12),
                                bgcolor="#f8f9fa",
                                padding=15,
                                border_radius=5,
                                width=920
                            )
                        ])
                    )
                )
            ], scroll=ft.ScrollMode.AUTO)
        )

    def _build_documents_tab(self):
        """Build the document library and evidence request tab"""
        visible_requests = self._get_visible_evidence_requests()
        return ft.Container(
            padding=20,
            content=ft.Column([
                ft.Row([
                    ft.Text("Document Library", size=20, weight=ft.FontWeight.BOLD, color="#2c3e50"),
                    ft.Container(expand=True),
                    ft.OutlinedButton(
                        text="Request Evidence",
                        icon=Icons.MAIL_OUTLINE,
                        on_click=self._open_add_evidence_request_dialog,
                        visible=self._can_create_evidence_requests()
                    ),
                    ft.ElevatedButton(
                        text="Upload Document",
                        icon=Icons.UPLOAD_FILE,
                        bgcolor="#2563eb",
                        color="white",
                        on_click=self._start_general_document_upload,
                        visible=self._can_general_document_upload()
                    )
                ]),
                ft.Container(
                    padding=12,
                    bgcolor="#eff6ff",
                    border=ft.border.all(1, "#bfdbfe"),
                    border_radius=8,
                    content=ft.Text(
                        "Your evidence workspace is limited to requests assigned to you. General uploads stay hidden until an auditor issues a request.",
                        size=12,
                        color="#1d4ed8",
                    )
                ) if self._is_client_evidence_user() else ft.Container(),
                ft.Container(height=20),
                ft.Row(self._build_document_summary_cards(), spacing=15, scroll=ft.ScrollMode.AUTO),
                ft.Container(height=20),
                ft.Card(
                    content=ft.Container(
                        padding=20,
                        content=ft.Column([
                            ft.Text("Evidence Register", size=16, weight=ft.FontWeight.BOLD),
                            ft.Divider(),
                            ft.Container(
                                content=ft.Column(self._build_document_item_controls(), spacing=12),
                                bgcolor="#f8f9fa",
                                padding=15,
                                border_radius=5,
                                width=920
                            )
                        ])
                    )
                ),
                ft.Container(height=20),
                ft.Card(
                    content=ft.Container(
                        padding=20,
                        content=ft.Column([
                            ft.Row([
                                ft.Text("Evidence Requests", size=16, weight=ft.FontWeight.BOLD),
                                ft.Container(expand=True),
                                ft.Text(f"{len(visible_requests)} requests", size=12, color="#7f8c8d")
                            ]),
                            ft.Divider(),
                            ft.Container(
                                content=ft.Column(self._build_evidence_request_controls(), spacing=12),
                                bgcolor="#f8f9fa",
                                padding=15,
                                border_radius=5,
                                width=920
                            )
                        ])
                    )
                ),
                ft.Container(height=20),
                ft.Card(
                    visible=self._can_manage_document_activity(),
                    content=ft.Container(
                        padding=20,
                        content=ft.Column([
                            ft.Text("Document Access Activity", size=16, weight=ft.FontWeight.BOLD),
                            ft.Divider(),
                            ft.Container(
                                content=ft.Column(self._build_document_access_log_controls(), spacing=10),
                                bgcolor="#f8f9fa",
                                padding=15,
                                border_radius=5,
                                width=920
                            )
                        ])
                    )
                )
            ], scroll=ft.ScrollMode.AUTO)
        )

    def _build_document_summary_cards(self):
        total_documents = len(self.documents_data or [])
        visible_requests = self._get_visible_evidence_requests()
        linked_documents = sum(
            1 for doc in self.documents_data or []
            if any([
                self._get_field(doc, "procedureId", "ProcedureId"),
                self._get_field(doc, "workingPaperId", "WorkingPaperId"),
                self._get_field(doc, "findingId", "FindingId"),
                self._get_field(doc, "recommendationId", "RecommendationId"),
            ])
        )
        client_documents = sum(
            1 for doc in self.documents_data or []
            if (self._get_field(doc, "sourceType", "SourceType", default="") or "").lower() == "client"
        )
        restricted_documents = sum(
            1 for doc in self.documents_data or []
            if self._is_restricted_document(doc)
        )
        open_requests = sum(
            1 for request in visible_requests
            if (self._get_field(request, "statusName", "StatusName", default="Sent") or "").lower() not in {"fulfilled", "closed", "cancelled"}
        )

        cards = [
            ("Documents", total_documents, "#2563eb"),
            ("Linked Evidence", linked_documents, "#0f766e"),
            ("Client Provided", client_documents, "#9333ea"),
            ("Restricted", restricted_documents, "#dc2626"),
            ("Open Requests", open_requests, "#f59e0b"),
        ]

        return [
            ft.Container(
                width=180,
                padding=15,
                bgcolor="white",
                border=ft.border.all(1, "#e6e9ed"),
                border_radius=10,
                content=ft.Column([
                    ft.Text(label, size=12, color="#7f8c8d"),
                    ft.Text(str(value), size=24, weight=ft.FontWeight.BOLD, color=color)
                ], spacing=4)
            )
            for label, value, color in cards
        ]

    def _is_restricted_document(self, document):
        visibility_name = self._get_field(document, "visibilityLevelName", "VisibilityLevelName", default="")
        normalized_visibility = (visibility_name or "").strip().lower().replace("-", "_").replace(" ", "_")
        return normalized_visibility in {"managers_and_reviewers", "private_draft", "restricted"}

    def _is_truthy(self, value):
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.strip().lower() in {"1", "true", "yes", "y"}
        return bool(value)

    def _get_document_category_config(self, category_id):
        if category_id in (None, "", 0):
            return None
        for category in self.document_categories or []:
            if str(self._get_field(category, "id", "Id", default="")) == str(category_id):
                return category
        return None

    def _get_document_visibility_config(self, visibility_id):
        if visibility_id in (None, "", 0):
            return None
        for option in self.document_visibility_options or []:
            if str(self._get_field(option, "id", "Id", default="")) == str(visibility_id):
                return option
        return None

    def _category_requires_security_review(self, category):
        if not category:
            return False
        return (
            self._is_truthy(self._get_field(category, "requiresSecurityApproval", "RequiresSecurityApproval", default=False))
            or self._is_truthy(self._get_field(category, "isSensitive", "IsSensitive", default=False))
        )

    def _visibility_requires_security_review(self, visibility):
        if not visibility:
            return False
        return self._is_truthy(self._get_field(visibility, "isRestricted", "IsRestricted", default=False))

    def _document_requires_security_review(self, document):
        return (
            self._is_truthy(self._get_field(document, "securityReviewRequired", "SecurityReviewRequired", default=False))
            or self._is_truthy(self._get_field(document, "isSensitiveCategory", "IsSensitiveCategory", default=False))
            or self._is_truthy(self._get_field(document, "visibilityIsRestricted", "VisibilityIsRestricted", default=False))
        )

    def _normalize_security_review_status(self, value):
        normalized = (value or "").strip()
        return normalized or "Not Required"

    def _get_security_review_status_style(self, value):
        normalized = self._normalize_security_review_status(value).lower()
        if normalized == "approved":
            return "Approved", "#15803d"
        if normalized == "pending approval":
            return "Pending Approval", "#b45309"
        if normalized == "rejected":
            return "Rejected", "#b91c1c"
        return self._normalize_security_review_status(value), "#64748b"

    def _build_document_item_controls(self):
        if not self.documents_data:
            return [ft.Text("No audit documents uploaded yet.", color="#7f8c8d")]

        controls = []
        for document in self.documents_data:
            document_id = self._get_field(document, "id", "Id")
            category_name = self._get_field(document, "categoryName", "CategoryName", default="Uncategorized")
            category_color = self._get_field(document, "categoryColor", "CategoryColor", default="#94a3b8")
            visibility_name = self._get_field(document, "visibilityLevelName", "VisibilityLevelName", default="Engagement Team")
            visibility_color = self._get_field(document, "visibilityLevelColor", "VisibilityLevelColor", default="#2563eb")
            access_summary = self._get_field(document, "accessSummary", "AccessSummary", default=visibility_name)
            confidentiality_label = self._get_field(document, "confidentialityLabel", "ConfidentialityLabel", default="")
            confidentiality_reason = self._get_field(document, "confidentialityReason", "ConfidentialityReason", default="")
            uploaded_at = self._get_field(document, "uploadedAt", "UploadedAt", default="")
            if isinstance(uploaded_at, str) and "T" in uploaded_at:
                uploaded_at = uploaded_at.replace("T", " ")[:16]
            security_review_required = self._document_requires_security_review(document)
            security_review_status = self._normalize_security_review_status(
                self._get_field(document, "securityReviewStatus", "SecurityReviewStatus", default="")
            )
            security_status_label, security_status_color = self._get_security_review_status_style(security_review_status)
            security_requested_at = self._format_activity_time_value(
                self._get_field(document, "securityReviewRequestedAt", "SecurityReviewRequestedAt", default="")
            )
            security_requested_by = self._get_field(
                document,
                "securityReviewRequestedByName",
                "SecurityReviewRequestedByName",
                default=""
            )
            security_reviewed_at = self._format_activity_time_value(
                self._get_field(document, "securityReviewedAt", "SecurityReviewedAt", default="")
            )
            security_reviewed_by = self._get_field(
                document,
                "securityReviewedByName",
                "SecurityReviewedByName",
                default=""
            )
            security_review_notes = self._get_field(document, "securityReviewNotes", "SecurityReviewNotes", default="")
            linked_parts = []
            if self._get_field(document, "procedureTitle", "ProcedureTitle"):
                linked_parts.append(f"Procedure: {self._get_field(document, 'procedureTitle', 'ProcedureTitle')}")
            if self._get_field(document, "workingPaperCode", "WorkingPaperCode"):
                linked_parts.append(f"Working Paper: {self._get_field(document, 'workingPaperCode', 'WorkingPaperCode')}")
            if self._get_field(document, "findingNumber", "FindingNumber"):
                linked_parts.append(f"Finding: {self._get_field(document, 'findingNumber', 'FindingNumber')}")
            if self._get_field(document, "recommendationNumber", "RecommendationNumber"):
                linked_parts.append(f"Recommendation: {self._get_field(document, 'recommendationNumber', 'RecommendationNumber')}")

            action_controls = [
                ft.TextButton("Open", icon=Icons.OPEN_IN_NEW, on_click=lambda _, doc_id=document_id: self._open_document_link(doc_id))
            ]
            if can_manage_document_security(self.user):
                if security_review_status.lower() == "pending approval":
                    action_controls.append(
                        ft.TextButton(
                            "Approve",
                            icon=Icons.CHECK_CIRCLE,
                            on_click=lambda _, doc=document: self._open_document_security_review_dialog(doc, True)
                        )
                    )
                    action_controls.append(
                        ft.TextButton(
                            "Reject",
                            icon=Icons.CANCEL,
                            on_click=lambda _, doc=document: self._open_document_security_review_dialog(doc, False)
                        )
                    )
                action_controls.append(
                    ft.TextButton("Manage Security", icon=Icons.LOCK, on_click=lambda _, doc=document: self._open_document_security_dialog(doc))
                )
            if self._can_delete_document(document):
                action_controls.append(
                    ft.TextButton("Delete", icon=Icons.DELETE, on_click=lambda _, doc=document: self._delete_document(doc))
                )

            controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text(self._get_field(document, "title", "Title", default="Document"), weight=ft.FontWeight.BOLD, size=14),
                            ft.Container(expand=True),
                            ft.Container(
                                content=ft.Text(visibility_name, size=11, color="white"),
                                bgcolor=visibility_color,
                                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                border_radius=10
                            ),
                            ft.Container(
                                content=ft.Text(category_name, size=11, color="white"),
                                bgcolor=category_color,
                                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                border_radius=10
                            )
                        ]),
                        ft.Text(
                            f"{self._get_field(document, 'originalFileName', 'OriginalFileName', default='File')} • {self._format_file_size(self._get_field(document, 'fileSize', 'FileSize'))}",
                            size=11,
                            color="#64748b"
                        ),
                        ft.Text(
                            " | ".join(linked_parts) if linked_parts else "Not yet linked to a procedure, working paper, finding, or recommendation.",
                            size=11,
                            color="#475569"
                        ),
                        ft.Text(
                            f"Confidentiality: {confidentiality_label}",
                            size=11,
                            color="#dc2626"
                        ) if confidentiality_label else ft.Container(),
                        ft.Text(
                            confidentiality_reason,
                            size=11,
                            color="#7f1d1d"
                        ) if confidentiality_reason else ft.Container(),
                        ft.Row([
                            ft.Container(
                                content=ft.Text(f"Security Review: {security_status_label}", size=11, color="white"),
                                bgcolor=security_status_color,
                                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                border_radius=10
                            ),
                            ft.Text(
                                f"Requested by {security_requested_by or 'Audit User'} on {security_requested_at}"
                                if security_review_status.lower() == "pending approval" and security_review_required
                                else (
                                    f"Reviewed by {security_reviewed_by or 'Audit User'} on {security_reviewed_at}"
                                    if security_review_required and security_review_status.lower() in {"approved", "rejected"} and security_reviewed_at
                                    else "Sensitive evidence workflow not required."
                                ),
                                size=11,
                                color="#7f8c8d"
                            )
                        ], spacing=8, wrap=True) if security_review_required else ft.Container(),
                        ft.Text(
                            security_review_notes,
                            size=11,
                            color="#92400e" if security_review_status.lower() == "pending approval" else "#475569"
                        ) if security_review_notes else ft.Container(),
                        ft.Text(
                            self._get_field(document, "notes", "Notes", default=""),
                            size=11,
                            color="#5f6b7a"
                        ) if self._get_field(document, "notes", "Notes") else ft.Container(),
                        ft.Row([
                            ft.Text(f"Source: {self._get_field(document, 'sourceType', 'SourceType', default='Audit Team')}", size=11, color="#7f8c8d"),
                            ft.Text(f"Visible to: {access_summary}", size=11, color="#7f8c8d"),
                            ft.Text(f"Uploaded: {uploaded_at or 'Unknown'}", size=11, color="#7f8c8d"),
                            ft.Container(expand=True),
                            *action_controls
                        ], spacing=6, wrap=True)
                    ], spacing=6),
                    padding=12,
                    bgcolor="white",
                    border_radius=8,
                    border=ft.border.all(1, "#e6e9ed")
                )
            )
        return controls

    def _build_document_access_log_controls(self):
        if not self.document_access_logs:
            return [ft.Text("No document access activity recorded yet.", color="#7f8c8d")]

        controls = []
        for entry in self.document_access_logs:
            action = self._get_field(entry, "actionType", "ActionType", default="Activity")
            document_title = self._get_field(entry, "documentTitle", "DocumentTitle", default="Document")
            document_code = self._get_field(entry, "documentCode", "DocumentCode", default="")
            accessed_by = self._get_field(entry, "accessedByName", "AccessedByName", default="Unknown user")
            accessed_at = self._get_field(entry, "accessedAt", "AccessedAt", default="")
            success = bool(self._get_field(entry, "success", "Success", default=True))
            details_json = self._get_field(entry, "detailsJson", "DetailsJson", default="")
            if isinstance(accessed_at, str) and "T" in accessed_at:
                accessed_at = accessed_at.replace("T", " ")[:19]

            detail_line = ""
            if details_json:
                try:
                    details = json.loads(details_json)
                    if isinstance(details, dict):
                        detail_line = details.get("reason") or details.get("VisibilityLevelName") or ""
                except Exception:
                    detail_line = ""

            controls.append(
                ft.Container(
                    padding=10,
                    bgcolor="white",
                    border=ft.border.all(1, "#e6e9ed"),
                    border_radius=8,
                    content=ft.Column([
                        ft.Row([
                            ft.Text(action, weight=ft.FontWeight.BOLD, size=12, color="#1d4ed8" if success else "#dc2626"),
                            ft.Container(expand=True),
                            ft.Text("Success" if success else "Denied", size=11, color="#16a34a" if success else "#dc2626"),
                        ]),
                        ft.Text(
                            f"{document_code} - {document_title}" if document_code else document_title,
                            size=12,
                            color="#0f172a"
                        ),
                        ft.Text(f"By: {accessed_by} | At: {accessed_at or 'Unknown'}", size=11, color="#64748b"),
                        ft.Text(detail_line, size=11, color="#7f1d1d") if detail_line else ft.Container()
                    ], spacing=4)
                )
            )

        return controls

    def _build_evidence_request_controls(self):
        visible_requests = self._get_visible_evidence_requests()
        if not visible_requests:
            empty_message = "No evidence requests assigned to you yet." if self._is_client_evidence_user() else "No evidence requests have been issued yet."
            return [ft.Text(empty_message, color="#7f8c8d")]

        controls = []
        for request in visible_requests:
            status_name = self._get_field(request, "statusName", "StatusName", default="Sent")
            status_color = self._get_field(request, "statusColor", "StatusColor", default="#64748b")
            due_date = self._get_field(request, "dueDate", "DueDate", default="")
            if isinstance(due_date, str) and "T" in due_date:
                due_date = due_date.split("T")[0]
            request_items = self._get_field(request, "items", "Items", default=[]) or []
            item_controls = []
            for item in request_items:
                fulfilled_document_id = self._get_field(item, "fulfilledDocumentId", "FulfilledDocumentId")
                fulfilled_title = self._get_field(item, "fulfilledDocumentTitle", "FulfilledDocumentTitle", default="")
                has_restricted_evidence = (fulfilled_title or "").strip().lower() == "restricted document"
                reviewed_at = self._get_field(item, "reviewedAt", "ReviewedAt", default="")
                reviewer_notes = self._get_field(item, "reviewerNotes", "ReviewerNotes", default="")
                is_accepted = self._get_field(item, "isAccepted", "IsAccepted", default=None)
                if isinstance(reviewed_at, str) and "T" in reviewed_at:
                    reviewed_at = reviewed_at.replace("T", " ")[:16]

                if fulfilled_document_id and is_accepted is True:
                    item_icon = Icons.CHECK_CIRCLE
                    item_color = "#16a34a"
                    review_state = "Accepted"
                elif fulfilled_document_id and reviewed_at:
                    item_icon = Icons.CANCEL
                    item_color = "#dc2626"
                    review_state = "Rejected"
                elif fulfilled_document_id:
                    item_icon = Icons.FACT_CHECK
                    item_color = "#2563eb"
                    review_state = "Awaiting Review"
                else:
                    item_icon = Icons.HOURGLASS_EMPTY
                    item_color = "#f59e0b"
                    review_state = "Awaiting Upload"

                action_controls = []
                if fulfilled_document_id:
                    if not has_restricted_evidence:
                        action_controls.append(
                            ft.TextButton(
                                "Open Evidence",
                                icon=Icons.OPEN_IN_NEW,
                                on_click=lambda _, doc_id=fulfilled_document_id: self._open_document_link(doc_id)
                            )
                        )
                    if can_review_evidence(self.user) and not has_restricted_evidence:
                        action_controls.append(
                            ft.TextButton(
                                "Accept",
                                icon=Icons.CHECK,
                                on_click=lambda _, request_item=item: self._review_evidence_request_item(request_item, True)
                            )
                        )
                        action_controls.append(
                            ft.TextButton(
                                "Reject",
                                icon=Icons.CLOSE,
                                on_click=lambda _, request_item=item: self._review_evidence_request_item(request_item, False)
                            )
                        )
                else:
                    if can_submit_evidence(self.user):
                        action_controls.append(
                            ft.TextButton(
                                "Submit Evidence",
                                icon=Icons.UPLOAD_FILE,
                                on_click=lambda _, req=request, request_item=item: self._start_requested_evidence_upload(req, request_item)
                            )
                        )

                item_controls.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(item_icon, color=item_color, size=16),
                                ft.Column([
                                    ft.Text(self._get_field(item, "itemDescription", "ItemDescription", default="Requested item"), size=12, weight=ft.FontWeight.BOLD),
                                    ft.Text(
                                        fulfilled_title if fulfilled_title else "Awaiting upload",
                                        size=11,
                                        color="#dc2626" if has_restricted_evidence else "#64748b"
                                    ),
                                    ft.Text(review_state, size=11, color=item_color)
                                ], spacing=2, expand=True)
                            ]),
                            ft.Text(
                                f"Reviewed: {reviewed_at}" if reviewed_at else "Reviewed: Not yet reviewed",
                                size=10,
                                color="#7f8c8d"
                            ),
                            ft.Text(reviewer_notes, size=10, color="#5f6b7a") if reviewer_notes else ft.Container(),
                            ft.Row(action_controls, spacing=6)
                        ], spacing=6),
                        padding=8,
                        bgcolor="#ffffff",
                        border=ft.border.all(1, "#e6e9ed"),
                        border_radius=8
                    )
                )

            controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text(self._get_field(request, "title", "Title", default="Evidence Request"), weight=ft.FontWeight.BOLD, size=14),
                            ft.Container(expand=True),
                            ft.Container(
                                content=ft.Text(status_name, size=11, color="white"),
                                bgcolor=status_color,
                                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                border_radius=10
                            )
                        ]),
                        ft.Text(self._get_field(request, "requestDescription", "RequestDescription", default=""), size=11, color="#475569"),
                        ft.Row([
                            ft.Text(f"Requested From: {self._get_field(request, 'requestedFrom', 'RequestedFrom', default='Not specified')}", size=11, color="#7f8c8d"),
                            ft.Text(f"Due: {due_date or 'Not set'}", size=11, color="#7f8c8d"),
                            ft.Text(
                                f"Items: {self._get_field(request, 'fulfilledItems', 'FulfilledItems', default=0)}/{self._get_field(request, 'totalItems', 'TotalItems', default=0)} fulfilled",
                                size=11,
                                color="#7f8c8d"
                            )
                        ]),
                        ft.Column(item_controls, spacing=8)
                    ], spacing=6),
                    padding=12,
                    bgcolor="white",
                    border_radius=8,
                    border=ft.border.all(1, "#e6e9ed")
                )
            )
        return controls
    
    def _build_findings_tab(self):
        """Build the findings tab"""
        issue_plural = self._term("finding_plural")
        issue_singular = self._term("finding_singular")
        recommendation_plural = self._term("recommendation_plural")
        findings_summary = self._build_findings_summary_controls()
        recommendations_summary = self._build_recommendations_summary_controls()
        management_response_text = self._build_management_response_summary()
        materiality_context_card = self._build_findings_materiality_context_card()

        return ft.Container(
            padding=20,
            content=ft.Column([
                # Findings summary
                ft.Row([
                    ft.Text(f"Assessment {issue_plural}", size=20, weight=ft.FontWeight.BOLD, color="#2c3e50"),
                    ft.Container(expand=True),
                    ft.OutlinedButton(
                        text="Request Review",
                        icon=Icons.GAVEL,
                        on_click=self._open_finding_review_workflow_dialog,
                        visible=can_start_workflows(self.user)
                    ),
                    ft.ElevatedButton(
                        text=f"Add {issue_singular}",
                        icon=Icons.ADD,
                        bgcolor="#2ecc71",
                        color="white",
                        on_click=self._add_finding
                    )
                ]),
                
                ft.Container(height=20),

                materiality_context_card if materiality_context_card else ft.Container(),
                ft.Container(height=20) if materiality_context_card else ft.Container(),
                
                # Key findings
                ft.Card(
                    content=ft.Container(
                        padding=20,
                        content=ft.Column([
                            ft.Text(f"Key {issue_plural}", size=16, weight=ft.FontWeight.BOLD),
                            ft.Divider(),
                            ft.Container(
                                content=ft.Column(findings_summary, spacing=12),
                                bgcolor="#f8f9fa",
                                padding=15,
                                border_radius=5,
                                width=800
                            )
                        ])
                    )
                ),
                
                ft.Container(height=20),
                
                # Recommendations
                ft.Card(
                    content=ft.Container(
                        padding=20,
                        content=ft.Column([
                            ft.Text(recommendation_plural, size=16, weight=ft.FontWeight.BOLD),
                            ft.Divider(),
                            ft.Container(
                                content=ft.Column(recommendations_summary, spacing=12),
                                bgcolor="#f8f9fa",
                                padding=15,
                                border_radius=5,
                                width=800
                            )
                        ])
                    )
                ),
                
                ft.Container(height=20),
                
                # Management response
                ft.Card(
                    content=ft.Container(
                        padding=20,
                        content=ft.Column([
                            ft.Row([
                                ft.Text("Management Response", size=16, weight=ft.FontWeight.BOLD),
                                ft.Container(expand=True),
                                ft.OutlinedButton(
                                    text="Start Follow-Up",
                                    icon=Icons.ASSIGNMENT_TURNED_IN,
                                    on_click=self._open_remediation_followup_workflow_dialog,
                                    visible=can_start_workflows(self.user)
                                ),
                                ft.ElevatedButton(
                                    text="Request Response",
                                    icon=Icons.SEND,
                                    bgcolor="#3498db",
                                    color="white",
                                    on_click=self._request_management_response,
                                    visible=can_start_workflows(self.user)
                                )
                            ]),
                            ft.Divider(),
                            ft.Container(
                                content=ft.Text(management_response_text, color="#7f8c8d", style=ft.TextThemeStyle.BODY_MEDIUM),
                                bgcolor="#f8f9fa",
                                padding=15,
                                border_radius=5,
                                width=800
                            )
                        ])
                    )
                )
            ], scroll=ft.ScrollMode.AUTO)
        )

    def _build_findings_materiality_context_card(self):
        if not (self._is_external_audit() or self._has_materiality_data()):
            return None

        application = self._get_materiality_application_summary()
        misstatement = self._get_materiality_misstatement_summary()
        active_calculation = self._get_active_materiality_calculation() or {}
        benchmark_summary = self._get_field(active_calculation, "calculationSummary", "CalculationSummary", default="Manual planning values")
        threshold_source = self._get_field(application, "thresholdSource", "ThresholdSource", default="Not Set")

        return ft.Card(
            content=ft.Container(
                padding=18,
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Text("Materiality Context", size=16, weight=ft.FontWeight.BOLD),
                                ft.Container(expand=True),
                                ft.Container(
                                    content=ft.Text(threshold_source, size=11, color="white"),
                                    bgcolor="#2563eb" if threshold_source == "Calculated" else "#64748b",
                                    padding=ft.padding.symmetric(horizontal=10, vertical=5),
                                    border_radius=999,
                                ),
                            ]
                        ),
                        ft.Text(benchmark_summary, size=12, color="#475569"),
                        ft.ResponsiveRow(
                            [
                                ft.Container(col={"sm": 12, "md": 4}, content=self._create_info_row("Overall", self._format_materiality_value(self._get_field(application, "overallMateriality", "OverallMateriality", default=0)))),
                                ft.Container(col={"sm": 12, "md": 4}, content=self._create_info_row("Performance", self._format_materiality_value(self._get_field(application, "performanceMateriality", "PerformanceMateriality", default=0)))),
                                ft.Container(col={"sm": 12, "md": 4}, content=self._create_info_row("Clearly Trivial", self._format_materiality_value(self._get_field(application, "clearlyTrivialThreshold", "ClearlyTrivialThreshold", default=0)))),
                            ],
                            run_spacing=8,
                        ),
                        ft.Row(
                            [
                                self._create_control_status_card("Recorded Misstatements", str(self._get_field(misstatement, "totalRecordedMisstatements", "TotalRecordedMisstatements", default=0)), "#2563eb"),
                                self._create_control_status_card("Above PM", str(self._get_field(misstatement, "abovePerformanceMaterialityCount", "AbovePerformanceMaterialityCount", default=0)), "#dc2626"),
                                self._create_control_status_card("Above OM", str(self._get_field(misstatement, "aboveOverallMaterialityCount", "AboveOverallMaterialityCount", default=0)), "#7f1d1d"),
                            ],
                            spacing=12,
                            scroll=ft.ScrollMode.AUTO,
                        ),
                    ],
                    spacing=10,
                ),
            )
        )

    def _build_management_actions_tab(self):
        summary_cards = self._build_management_action_summary_cards()
        action_controls = self._build_management_action_controls()
        empty_message = (
            "Management actions are most useful for internal audit follow-up and remediation tracking."
            if self._is_external_audit() and not self.management_actions_data
            else "No management actions have been recorded yet."
        )

        return ft.Container(
            padding=20,
            content=ft.Column([
                ft.Row([
                    ft.Text("Management Actions", size=20, weight=ft.FontWeight.BOLD, color="#2c3e50"),
                    ft.Container(expand=True),
                    ft.ElevatedButton(
                        text="Add Action",
                        icon=Icons.ADD_TASK,
                        bgcolor="#0f766e",
                        color="white",
                        on_click=self._open_management_action_dialog
                    )
                ]),
                ft.Container(height=20),
                self._build_engagement_mode_card(),
                ft.Container(height=20),
                ft.Row(summary_cards, spacing=15, scroll=ft.ScrollMode.AUTO),
                ft.Container(height=20),
                ft.Card(
                    content=ft.Container(
                        padding=20,
                        content=ft.Column([
                            ft.Row([
                                ft.Text("Action Register", size=16, weight=ft.FontWeight.BOLD),
                                ft.Container(expand=True),
                                ft.Text(f"{len(self.management_actions_data)} actions", size=12, color="#7f8c8d")
                            ]),
                            ft.Divider(),
                            ft.Container(
                                content=ft.Column(action_controls if action_controls else [ft.Text(empty_message, color="#7f8c8d")], spacing=12),
                                bgcolor="#f8f9fa",
                                padding=15,
                                border_radius=5,
                                width=920
                            )
                        ])
                    )
                )
            ], scroll=ft.ScrollMode.AUTO)
        )
    
    def _build_heatmap_tab(self):
        """Build the heatmap visualization tab"""
        return ft.Container(
            padding=20,
            content=ft.Column([
                ft.Text("Risk Heatmap Visualization", size=20, weight=ft.FontWeight.BOLD, color="#2c3e50"),
                ft.Text("Visual representation of risk assessment data", color="#7f8c8d"),
                ft.Container(height=20),
                
                # Heatmap container
                ft.Container(
                    content=ft.Text("Loading heatmap...", size=16, color="#7f8c8d"),
                    alignment=ft.alignment.center,
                    height=400,
                    bgcolor="#f8f9fa",
                    border_radius=5,
                    border=ft.border.all(1, "#e6e9ed")
                )
            ])
        )
    
    def _build_collaboration_tab(self):
        """Build the collaboration tab"""
        if not hasattr(self, "comment_input") or self.comment_input is None:
            self.comment_input = ft.TextField(
                label="Add an audit comment...",
                multiline=True,
                min_lines=2,
                max_lines=4,
                border=ft.InputBorder.OUTLINE,
                expand=True
            )

        return ft.Container(
            padding=20,
            content=ft.Column([
                # Collaboration header
                ft.Row([
                    ft.Text("Audit Collaboration", size=20, weight=ft.FontWeight.BOLD, color="#2c3e50"),
                    ft.Container(expand=True),
                    ft.ElevatedButton(
                        text="Manage Access",
                        icon=Icons.GROUP,
                        bgcolor="#0f766e",
                        color="white",
                        visible=self._can_manage_collaboration(),
                        on_click=lambda e: self.page.run_task(self._open_reference_collaborators_dialog_async())
                    ),
                    ft.Container(width=10),
                    ft.ElevatedButton(
                        text="Add Comment",
                        icon=Icons.COMMENT,
                        bgcolor="#3498db",
                        color="white",
                        on_click=self._add_comment
                    )
                ]),
                
                ft.Container(height=20),
                
                # Team members
                ft.Card(
                    content=ft.Container(
                        padding=20,
                        content=ft.Column([
                            ft.Text("Audit Team", size=16, weight=ft.FontWeight.BOLD),
                            ft.Divider(),
                            ft.Row(self._build_team_members(), spacing=20)
                        ])
                    )
                ),
                
                ft.Container(height=20),
                
                # Comments and activity
                ft.Card(
                    content=ft.Container(
                        padding=20,
                        content=ft.Column([
                            ft.Text("Comments & Activity", size=16, weight=ft.FontWeight.BOLD),
                            ft.Divider(),
                            
                            # Comment input
                            self.comment_input,
                            ft.Container(height=10),
                            ft.Row([
                                ft.Container(expand=True),
                                ft.ElevatedButton(
                                    text="Post Comment",
                                    icon=Icons.SEND,
                                    bgcolor="#2ecc71",
                                    color="white",
                                    on_click=lambda e: self.page.run_task(self._save_comment(self.comment_input.value))
                                )
                            ]),
                            
                            ft.Container(height=20),
                            
                            ft.Text("Comment History", size=16, weight=ft.FontWeight.BOLD),
                            ft.Column(self._build_comment_items(), spacing=10),
                            ft.Container(height=20),
                            ft.Text("Activity Feed", size=16, weight=ft.FontWeight.BOLD),
                            ft.Column(self._build_activity_items(), spacing=10)
                        ])
                    )
                )
            ], scroll=ft.ScrollMode.AUTO)
        )

    def _build_audit_trail_tab(self):
        dashboard = self.audit_trail_dashboard or {}
        categories = dashboard.get("categories", []) if isinstance(dashboard, dict) else []
        recent_events = self.audit_trail_events or []
        if not recent_events and isinstance(dashboard, dict):
            recent_events = dashboard.get("recentEvents", []) or []

        category_cards = []
        for category in categories[:4]:
            category_cards.append(
                ft.Container(
                    width=170,
                    padding=12,
                    bgcolor="#ffffff",
                    border=ft.border.all(1, "#e6e9ed"),
                    border_radius=10,
                    content=ft.Column([
                        ft.Text(category.get("category", "Category"), size=11, color="#7f8c8d"),
                        ft.Text(str(category.get("eventCount", 0)), size=20, weight=ft.FontWeight.BOLD, color="#2563eb"),
                    ], spacing=4)
                )
            )

        if not category_cards:
            category_cards = [ft.Text("No persisted audit trail categories yet.", color="#7f8c8d")]

        event_items = self._build_audit_trail_event_items(recent_events)

        return ft.Container(
            padding=20,
            content=ft.Column([
                ft.Row([
                    ft.Text("Audit Trail Review", size=20, weight=ft.FontWeight.BOLD, color="#2c3e50"),
                    ft.Container(expand=True),
                    ft.Text(
                        f"Total events: {(dashboard or {}).get('totalEvents', 0)} | "
                        f"Field changes: {(dashboard or {}).get('changeRecords', 0)}",
                        size=12,
                        color="#7f8c8d"
                    )
                ]),
                ft.Container(height=10),
                ft.Row(category_cards, spacing=10, scroll=ft.ScrollMode.AUTO),
                ft.Container(height=20),
                ft.Card(
                    content=ft.Container(
                        padding=20,
                        content=ft.Column([
                            ft.Text("Recent Audit Trail Events", size=16, weight=ft.FontWeight.BOLD),
                            ft.Divider(),
                            ft.Column(event_items, spacing=10)
                        ])
                    )
                )
            ], scroll=ft.ScrollMode.AUTO)
        )

    def _build_action_panel(self):
        """Build the bottom action panel"""
        return ft.Container(
            height=60,
            bgcolor="#f8f9fa",
            padding=ft.padding.symmetric(horizontal=30, vertical=10),
            content=ft.Row([
                ft.ElevatedButton(
                    text="Back to List",
                    icon=Icons.LIST,
                    on_click=self._handle_back,
                    bgcolor="#95a5a6",
                    color="white"
                ),
                ft.Container(expand=True),
                ft.ElevatedButton(
                    text="Generate Audit Report",
                    icon=Icons.DESCRIPTION,
                    bgcolor="#9b59b6",
                    color="white",
                    on_click=self._generate_report
                ),
                ft.Container(width=10),
                ft.ElevatedButton(
                    text="Edit Assessment",
                    icon=Icons.EDIT,
                    bgcolor="#3498db",
                    color="white",
                    on_click=self._edit_assessment
                )
            ])
        )
    
    # Helper methods for UI components
    def _create_metric_card(self, title, value, color, icon):
        """Create a metric display card"""
        value_text = str(value)
        value_font_size = 24 if len(value_text) <= 16 else 20 if len(value_text) <= 30 else 16
        return ft.Card(
            content=ft.Container(
                width=200,
                height=150,
                padding=20,
                content=ft.Column([
                    ft.Row([
                        ft.Text(title, size=14, color="#7f8c8d"),
                        ft.Container(expand=True),
                        ft.Icon(icon, color=color, size=24)
                    ]),
                    ft.Container(height=10),
                    ft.Text(
                        value_text,
                        size=value_font_size,
                        weight=ft.FontWeight.BOLD,
                        color=color,
                        max_lines=3,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    )
                ], spacing=0)
            )
        )
    
    def _create_info_row(self, label, value):
        """Create an information row"""
        return ft.Container(
            content=ft.Row([
                ft.Text(f"{label}:", weight=ft.FontWeight.BOLD, width=120),
                ft.Text(str(value), color="#2c3e50", expand=True)
            ]),
            margin=ft.margin.only(bottom=8)
        )
    
    def _create_timeline_item(self, title, status, color):
        """Create a timeline item"""
        return ft.Container(
            content=ft.Row([
                ft.Container(
                    width=12,
                    height=12,
                    bgcolor=color,
                    border_radius=6
                ),
                ft.Container(width=10),
                ft.Column([
                    ft.Text(title, size=14, weight=ft.FontWeight.BOLD),
                    ft.Text(status, size=12, color=color)
                ], spacing=2)
            ]),
            margin=ft.margin.only(bottom=15)
        )
    
    def _create_control_status_card(self, status, count, color):
        """Create control status card"""
        return ft.Card(
            content=ft.Container(
                width=150,
                height=80,
                padding=15,
                content=ft.Column([
                    ft.Text(status, size=12, color="#7f8c8d"),
                    ft.Text(count, size=24, weight=ft.FontWeight.BOLD, color=color)
                ], alignment=ft.MainAxisAlignment.CENTER)
            )
        )
    
    def _create_team_member(self, name, role, color):
        """Create team member card"""
        return ft.Container(
            content=ft.Column([
                ft.Container(
                    width=60,
                    height=60,
                    bgcolor=color,
                    border_radius=30,
                    alignment=ft.alignment.center,
                    content=ft.Text(name[0], color="white", size=20, weight=ft.FontWeight.BOLD)
                ),
                ft.Text(name, size=14, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                ft.Text(role, size=12, color="#7f8c8d", text_align=ft.TextAlign.CENTER)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5)
        )
    
    def _create_activity_item(self, user, action, time, icon, color):
        """Create activity feed item"""
        return ft.Container(
            content=ft.Row([
                ft.Icon(icon, color=color, size=20),
                ft.Container(width=10),
                ft.Column([
                    ft.Text(f"{user} {action}", size=14),
                    ft.Text(time, size=12, color="#7f8c8d")
                ], spacing=2, expand=True)
            ]),
            margin=ft.margin.only(bottom=15),
            padding=10,
            bgcolor="#f8f9fa",
            border_radius=5
        )
    
    def _get_status_color(self, status):
        """Get color for workflow status"""
        colors = {
            "In Progress": "#3498db",
            "Completed": "#2ecc71",
            "On Hold": "#f39c12",
            "Cancelled": "#e74c3c"
        }
        return colors.get(status, "#95a5a6")

    def _build_team_members(self):
        members = []
        for collaborator in self.reference_collaborators or []:
            if not isinstance(collaborator, dict):
                continue
            name = collaborator.get("user_name") or collaborator.get("user_email") or f"User {collaborator.get('user_id', '')}".strip()
            role_name = collaborator.get("collaborator_role_name") or collaborator.get("user_system_role") or "Collaborator"
            if collaborator.get("is_inherited_from_project"):
                role_name = f"{role_name} | Project"
            color = collaborator.get("collaborator_role_color") or "#3498db"
            members.append((name, role_name, color))

        if not members:
            current_user_name = self._get_current_user_name()
            assessor_name = self._get_assessor_name()
            if assessor_name:
                members.append((assessor_name, "Assessor", "#3498db"))
            if current_user_name and current_user_name != assessor_name:
                members.append((current_user_name, "Current User", "#2ecc71"))
            if not members:
                members.append(("Audit User", "Collaborator", "#3498db"))
        return [self._create_team_member(name, role, color) for name, role, color in members]

    def _can_manage_collaboration(self):
        return can_manage_audit_content(self.user) or can_manage_document_security(self.user)

    def _normalize_email_value(self, value):
        return (value or "").strip().lower()

    def _get_current_user_email(self):
        if isinstance(self.user, dict):
            return self.user.get("email") or self.user.get("Email")
        return getattr(self.user, "email", None)

    def _is_client_evidence_user(self):
        return can_submit_evidence(self.user) and not can_review_evidence(self.user)

    def _can_create_evidence_requests(self):
        return can_review_evidence(self.user)

    def _can_general_document_upload(self):
        return can_review_evidence(self.user)

    def _can_manage_document_activity(self):
        return can_manage_document_security(self.user)

    def _is_evidence_request_assigned_to_current_user(self, request):
        requested_to = self._normalize_email_value(
            self._get_field(request, "requestedToEmail", "RequestedToEmail", default="")
        )
        if not requested_to:
            return False

        candidates = {
            self._normalize_email_value(self._get_current_user_email()),
            self._normalize_email_value(self._get_current_user_name()),
        }
        return requested_to in {candidate for candidate in candidates if candidate}

    def _get_visible_evidence_requests(self):
        requests = list(self.evidence_requests_data or [])
        if not self._is_client_evidence_user():
            return requests
        return [request for request in requests if self._is_evidence_request_assigned_to_current_user(request)]

    def _can_delete_document(self, document):
        if can_manage_audit_content(self.user) or can_manage_document_security(self.user):
            return True

        current_user_id = self._normalize_user_id()
        document_user_id = self._get_field(document, "uploadedByUserId", "UploadedByUserId", default=None)
        try:
            if current_user_id is not None and document_user_id is not None and int(document_user_id) == current_user_id:
                return True
        except (TypeError, ValueError):
            pass

        uploaded_by_name = (self._get_field(document, "uploadedByName", "UploadedByName", default="") or "").strip().lower()
        current_name = (self._get_current_user_name() or "").strip().lower()
        return bool(uploaded_by_name and current_name and uploaded_by_name == current_name)

    def _normalize_collaboration_users(self, raw_users):
        normalized = []
        for user_data in raw_users or []:
            if isinstance(user_data, dict):
                user_id = user_data.get("id")
                name = user_data.get("name") or user_data.get("username") or user_data.get("email") or "Unknown User"
                normalized.append({
                    "id": user_id,
                    "name": name,
                    "email": user_data.get("email", ""),
                    "role": user_data.get("role", ""),
                })
            else:
                user_id = getattr(user_data, "id", None)
                name = getattr(user_data, "name", None) or getattr(user_data, "username", None) or getattr(user_data, "email", None) or "Unknown User"
                normalized.append({
                    "id": user_id,
                    "name": name,
                    "email": getattr(user_data, "email", ""),
                    "role": getattr(user_data, "role", ""),
                })

        normalized = [item for item in normalized if item.get("id") not in (None, "", 0)]
        normalized.sort(key=lambda item: (item.get("name") or "").lower())
        return normalized

    async def _open_reference_collaborators_dialog_async(self):
        if not self._can_manage_collaboration():
            self._show_error("You do not have permission to manage audit file collaborators.")
            return

        reference_id = self._normalize_reference_id()
        if not reference_id:
            self._show_error("Save the audit file before managing collaborators.")
            return

        try:
            collaborators_result, roles_result, users_result = await asyncio.gather(
                self.assessment_controller.auditing_client.get_reference_collaborators(reference_id),
                self.assessment_controller.auditing_client.get_collaborator_roles(),
                self.identity_client.get_users(),
                return_exceptions=True,
            )

            self.reference_collaborators = collaborators_result if not isinstance(collaborators_result, Exception) else []
            self.collaborator_roles = roles_result if not isinstance(roles_result, Exception) else []
            self.available_collaboration_users = self._normalize_collaboration_users(users_result if not isinstance(users_result, Exception) else [])

            if not self.available_collaboration_users:
                self._show_error("No users were returned from the identity service.")
                return

            explicit_collaborators = [
                item for item in (self.reference_collaborators or [])
                if isinstance(item, dict) and not item.get("is_inherited_from_project")
            ]
            inherited_collaborators = [
                item for item in (self.reference_collaborators or [])
                if isinstance(item, dict) and item.get("is_inherited_from_project")
            ]

            user_options = [
                ft.dropdown.Option(
                    key=str(user.get("id")),
                    text=f"{user.get('name')} | {user.get('email') or 'no email'} | {user.get('role') or 'role not set'}"
                )
                for user in self.available_collaboration_users
            ]
            role_options = [ft.dropdown.Option(key="", text="No specific audit role")]
            role_options.extend(
                ft.dropdown.Option(key=str(role.get("id")), text=role.get("name", "Collaborator"))
                for role in (self.collaborator_roles or [])
            )

            rows_column = ft.Column(spacing=12, scroll=ft.ScrollMode.AUTO)
            collaborator_rows = []

            def remove_row(row_state):
                if row_state in collaborator_rows:
                    collaborator_rows.remove(row_state)
                if row_state["container"] in rows_column.controls:
                    rows_column.controls.remove(row_state["container"])
                if not rows_column.controls:
                    add_row()
                self.page.update()

            def add_row(assignment=None):
                assignment = assignment or {}
                user_dropdown = ft.Dropdown(
                    label="User",
                    options=user_options,
                    value=str(assignment.get("user_id")) if assignment.get("user_id") not in (None, "") else None,
                    expand=3,
                )
                role_dropdown = ft.Dropdown(
                    label="Audit Role",
                    options=role_options,
                    value=str(assignment.get("collaborator_role_id")) if assignment.get("collaborator_role_id") not in (None, "") else "",
                    expand=2,
                )
                can_edit = ft.Checkbox(label="Edit", value=assignment.get("can_edit", True))
                can_review = ft.Checkbox(label="Review", value=assignment.get("can_review", False))
                can_upload = ft.Checkbox(label="Upload Evidence", value=assignment.get("can_upload_evidence", True))
                can_manage = ft.Checkbox(label="Manage Access", value=assignment.get("can_manage_access", False))
                notes_field = ft.TextField(
                    label="Notes",
                    value=assignment.get("notes", ""),
                    multiline=True,
                    min_lines=1,
                    max_lines=2,
                )
                remove_button = ft.IconButton(icon=Icons.DELETE_OUTLINE, tooltip="Remove collaborator")

                row_state = {
                    "user": user_dropdown,
                    "role": role_dropdown,
                    "can_edit": can_edit,
                    "can_review": can_review,
                    "can_upload": can_upload,
                    "can_manage": can_manage,
                    "notes": notes_field,
                    "container": None,
                }

                container = ft.Container(
                    padding=12,
                    border=ft.border.all(1, "#dbe4f0"),
                    border_radius=12,
                    bgcolor="#f8fafc",
                    content=ft.Column([
                        ft.Row([user_dropdown, role_dropdown, remove_button], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                        ft.Row([can_edit, can_review, can_upload, can_manage], spacing=12),
                        notes_field,
                    ], spacing=8),
                )

                row_state["container"] = container
                remove_button.on_click = lambda e, state=row_state: remove_row(state)
                collaborator_rows.append(row_state)
                rows_column.controls.append(container)

            for collaborator in explicit_collaborators or [{}]:
                add_row(collaborator)

            inherited_items = []
            if inherited_collaborators:
                for collaborator in inherited_collaborators:
                    inherited_items.append(
                        ft.Container(
                            padding=10,
                            border=ft.border.all(1, "#d1fae5"),
                            border_radius=10,
                            bgcolor="#ecfdf5",
                            content=ft.Row([
                                ft.Icon(Icons.GROUP_WORK, color="#0f766e", size=18),
                                ft.Container(width=8),
                                ft.Column([
                                    ft.Text(collaborator.get("user_name", "Collaborator"), weight=ft.FontWeight.BOLD),
                                    ft.Text(
                                        f"{collaborator.get('collaborator_role_name') or collaborator.get('user_system_role') or 'Collaborator'} | inherited from project",
                                        size=12,
                                        color="#0f766e",
                                    ),
                                ], spacing=2, expand=True),
                            ]),
                        )
                    )
            else:
                inherited_items.append(ft.Text("No project-level collaborators are inherited into this audit file.", color="#64748b"))

            dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text("Manage Audit File Access", size=18, weight=ft.FontWeight.BOLD),
                content=ft.Container(
                    width=980,
                    height=680,
                    content=ft.Column([
                        ft.Text(
                            "Project collaborators flow into this audit file automatically. Use explicit audit-file assignments below when the file needs tighter or additional access.",
                            color="#475569",
                        ),
                        ft.Container(height=6),
                        ft.Text("Inherited From Project", size=14, weight=ft.FontWeight.BOLD),
                        ft.Column(inherited_items, spacing=8),
                        ft.Divider(),
                        ft.Row([
                            ft.Text("Explicit Audit File Access", size=14, weight=ft.FontWeight.BOLD),
                            ft.Container(expand=True),
                            ft.TextButton("Add Collaborator", icon=Icons.PERSON_ADD, on_click=lambda e: (add_row(), self.page.update())),
                        ]),
                        ft.Container(expand=True, content=rows_column),
                    ], spacing=10),
                ),
                actions=[
                    ft.TextButton("Cancel", on_click=lambda e: self._close_active_dialog(dialog)),
                    ft.ElevatedButton(
                        "Save Access",
                        icon=Icons.SAVE,
                        on_click=lambda e: self.page.run_task(self._save_reference_collaborators_async(collaborator_rows, dialog)),
                    ),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            self._open_dialog(dialog)
        except Exception as ex:
            print(f"Error opening audit file collaborator dialog: {ex}")
            self._show_error(f"Failed to load audit file collaborators: {str(ex)}")

    async def _save_reference_collaborators_async(self, collaborator_rows, dialog):
        reference_id = self._normalize_reference_id()
        if not reference_id:
            self._show_error("Unable to determine the audit file reference.")
            return

        try:
            payload = []
            for row in collaborator_rows:
                user_value = row["user"].value
                if user_value in (None, "", "0"):
                    continue
                payload.append({
                    "userId": int(user_value),
                    "collaboratorRoleId": int(row["role"].value) if row["role"].value not in (None, "", "0") else None,
                    "canEdit": bool(row["can_edit"].value),
                    "canReview": bool(row["can_review"].value),
                    "canUploadEvidence": bool(row["can_upload"].value),
                    "canManageAccess": bool(row["can_manage"].value),
                    "notes": (row["notes"].value or "").strip(),
                })

            self.reference_collaborators = await self.assessment_controller.auditing_client.save_reference_collaborators(reference_id, payload)
            self._build_ui()
            self.page.update()
            self._close_active_dialog(dialog)
            self._show_success("Audit file collaborators updated")
        except Exception as ex:
            print(f"Error saving audit file collaborators: {ex}")
            self._show_error(f"Failed to save audit file collaborators: {str(ex)}")

    def _build_comment_items(self):
        if not self.comments:
            return [ft.Text("No comments recorded yet.", color="#7f8c8d")]
        items = []
        for comment in reversed(self.comments[-10:]):
            items.append(
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text(comment.get("user_name", "User"), size=13, weight=ft.FontWeight.BOLD),
                            ft.Container(expand=True),
                            ft.Text(comment.get("created_at", ""), size=11, color="#7f8c8d")
                        ]),
                        ft.Text(comment.get("text", ""), size=12, color="#2c3e50")
                    ], spacing=4),
                    bgcolor="white",
                    padding=12,
                    border_radius=8,
                    border=ft.border.all(1, "#e6e9ed")
                )
            )
        return items

    def _build_activity_items(self):
        combined_items = []

        for activity in self.activity_log or []:
            combined_items.append({
                "sort_key": self._parse_activity_timestamp(activity.get("time")),
                "user": activity.get("user", "System"),
                "action": activity.get("action", "updated the audit file"),
                "time": activity.get("time", ""),
                "icon": getattr(Icons, activity.get("icon", "INFO"), Icons.INFO),
                "color": activity.get("color", "#3498db")
            })

        for event in self.audit_trail_events or []:
            category = (self._get_field(event, "category", "Category", default="Business") or "Business").lower()
            if category == "workflow":
                continue
            raw_event_time = self._get_field(event, "eventTime", "EventTime", default="")
            combined_items.append({
                "sort_key": self._parse_activity_timestamp(raw_event_time),
                "user": self._get_field(event, "performedByName", "PerformedByName", default="System"),
                "action": self._get_field(event, "summary", "Summary", default="updated the audit file"),
                "time": self._format_activity_time_value(raw_event_time),
                "icon": getattr(Icons, self._get_field(event, "icon", "Icon", default="INFO"), Icons.INFO),
                "color": self._get_field(event, "color", "Color", default="#2563eb")
            })

        for event in self.workflow_timeline or []:
            event_type = (self._get_field(event, "eventType", "EventType", default="WorkflowEvent") or "WorkflowEvent")
            icon_name, color = self._workflow_event_style(event_type)
            title = self._get_field(event, "title", "Title", default="workflow event")
            description = self._get_field(event, "description", "Description", default="")
            raw_event_time = self._get_field(event, "eventTime", "EventTime", default="")
            combined_items.append({
                "sort_key": self._parse_activity_timestamp(raw_event_time),
                "user": self._get_field(event, "actorName", "ActorName", default="Workflow Engine"),
                "action": f"{title}. {description}".strip(),
                "time": self._format_activity_time_value(raw_event_time),
                "icon": getattr(Icons, icon_name, Icons.ROUTE),
                "color": color
            })

        if not combined_items:
            return [ft.Text("No audit activity has been recorded yet.", color="#7f8c8d")]

        items = []
        for activity in sorted(combined_items, key=lambda item: item["sort_key"], reverse=True)[:12]:
            items.append(
                self._create_activity_item(
                    activity.get("user", "System"),
                    activity.get("action", "updated the audit file"),
                    activity.get("time", ""),
                    activity.get("icon", Icons.INFO),
                    activity.get("color", "#3498db")
                )
            )
        return items

    def _build_audit_trail_event_items(self, events):
        if not events:
            return [ft.Text("No persisted audit trail events are available yet.", color="#7f8c8d")]

        items = []
        for event in events[:20]:
            changes = self._get_field(event, "changes", "Changes", default=[]) or []
            change_text = ""
            if changes:
                change_parts = []
                for change in changes[:3]:
                    field_name = self._get_field(change, "fieldName", "FieldName", default="field")
                    old_value = self._get_field(change, "oldValue", "OldValue", default="")
                    new_value = self._get_field(change, "newValue", "NewValue", default="")
                    change_parts.append(f"{field_name}: {old_value} -> {new_value}")
                change_text = " | ".join(change_parts)

            icon_name = self._get_field(event, "icon", "Icon", default="INFO")
            color = self._get_field(event, "color", "Color", default="#2563eb")
            performed_by = self._get_field(event, "performedByName", "PerformedByName", default="System")
            category = self._get_field(event, "category", "Category", default="Business")
            summary = self._get_field(event, "summary", "Summary", default="Audit event recorded")
            event_time = self._format_activity_time_value(self._get_field(event, "eventTime", "EventTime", default=""))

            items.append(
                ft.Container(
                    padding=12,
                    bgcolor="#ffffff",
                    border=ft.border.all(1, "#e6e9ed"),
                    border_radius=8,
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(getattr(Icons, icon_name, Icons.INFO), color=color, size=20),
                            ft.Container(width=10),
                            ft.Text(summary, size=13, weight=ft.FontWeight.BOLD, expand=True),
                            ft.Container(
                                content=ft.Text(category, size=10, color="white"),
                                bgcolor=color,
                                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                border_radius=10
                            )
                        ]),
                        ft.Text(f"{performed_by} | {event_time}", size=11, color="#7f8c8d"),
                        ft.Text(change_text, size=11, color="#475569", visible=bool(change_text))
                    ], spacing=5)
                )
            )
        return items

    def _parse_activity_timestamp(self, value):
        if not value:
            return datetime.min
        if isinstance(value, datetime):
            return value.replace(tzinfo=None) if value.tzinfo else value
        text = str(value).strip()
        try:
            parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
            return parsed.replace(tzinfo=None) if parsed.tzinfo else parsed
        except ValueError:
            for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d"):
                try:
                    return datetime.strptime(text, fmt)
                except ValueError:
                    continue
        return datetime.min

    def _format_activity_time_value(self, value):
        parsed = self._parse_activity_timestamp(value)
        if parsed == datetime.min:
            return str(value or "")
        return parsed.strftime("%Y-%m-%d %H:%M")

    def _workflow_event_style(self, event_type):
        normalized = (event_type or "").lower()
        if "started" in normalized:
            return "PLAY_ARROW", "#2563eb"
        if "assigned" in normalized or "reviewready" in normalized:
            return "ASSIGNMENT", "#0f766e"
        if "completed" in normalized:
            return "CHECK_CIRCLE", "#16a34a"
        if "overdue" in normalized or "escalation" in normalized:
            return "WARNING_AMBER", "#dc2626"
        if "synchronized" in normalized:
            return "SYNC", "#7c3aed"
        return "ROUTE", "#2563eb"

    def _get_field(self, obj, *keys, default=None):
        """Safely read a field from a dict or object using multiple candidate names."""
        for key in keys:
            if isinstance(obj, dict) and key in obj:
                return obj.get(key)
            if hasattr(obj, key):
                return getattr(obj, key)
        return default

    def _get_scope_item_label(self, item, default="Scope item"):
        label_parts = [
            str(part).strip()
            for part in [
                self._get_field(item, "businessUnit", "BusinessUnit", default=""),
                self._get_field(item, "processName", "ProcessName", default=""),
                self._get_field(item, "subProcessName", "SubProcessName", default=""),
                self._get_field(item, "fsli", "Fsli", default="")
            ]
            if part and str(part).strip()
        ]
        return " / ".join(label_parts) if label_parts else default

    def _get_engagement_type_id(self):
        value = self._get_field(self.planning_data, "engagementTypeId", "EngagementTypeId", default=None)
        try:
            return int(value) if value is not None and str(value).strip() else None
        except (TypeError, ValueError):
            return None

    def _get_engagement_type_name(self):
        return (self._get_field(self.planning_data, "engagementTypeName", "EngagementTypeName", default="") or "").strip()

    def _is_internal_audit(self):
        return "internal" in self._get_engagement_type_name().lower()

    def _is_external_audit(self):
        return "external" in self._get_engagement_type_name().lower()

    def _get_engagement_profile(self):
        if self._is_internal_audit():
            return {
                "mode_title": "Internal Audit Mode",
                "focus_label": "Control coverage, walkthrough quality, and remediation tracking",
                "scope_status_default": "Control Coverage",
                "planning_hint": "Use this mode for assurance, advisory, and follow-up work focused on process and control effectiveness.",
                "template_hint": "Control-focused templates, walkthrough packs, and remediation follow-up workpapers are prioritized.",
                "dashboard_label": "Assurance Dashboard",
                "supports_assertions": False,
                "supports_materiality": False,
                "supports_management_actions": True,
                "terms": {
                    "finding_singular": "Observation",
                    "finding_plural": "Observations",
                    "recommendation_plural": "Recommendations",
                },
            }
        if self._is_external_audit():
            return {
                "mode_title": "External Audit Mode",
                "focus_label": "Materiality, FSLI coverage, assertions, and substantive testing",
                "scope_status_default": "FSLI Scoped",
                "planning_hint": "Use this mode for financial-statement audit work focused on balances, assertions, and audit thresholds.",
                "template_hint": "Substantive analytics/testing packs, journal testing, and management override procedures are prioritized.",
                "dashboard_label": "Financial Statement Audit Dashboard",
                "supports_assertions": True,
                "supports_materiality": True,
                "supports_management_actions": False,
                "terms": {
                    "finding_singular": "Finding",
                    "finding_plural": "Findings",
                    "recommendation_plural": "Recommendations",
                },
            }
        return {
            "mode_title": "General Audit Mode",
            "focus_label": "Balanced planning, execution, and reporting workflow",
            "scope_status_default": "Planned",
            "planning_hint": "Capture the engagement type in planning to unlock audit-type-specific templates and prompts.",
            "template_hint": "General templates remain available until an audit type is selected.",
            "dashboard_label": "Audit Dashboard",
            "supports_assertions": False,
            "supports_materiality": False,
            "supports_management_actions": True,
            "terms": {
                "finding_singular": "Finding",
                "finding_plural": "Findings",
                "recommendation_plural": "Recommendations",
            },
        }

    def _term(self, key):
        return self._get_engagement_profile().get("terms", {}).get(key, key.replace("_", " ").title())

    def _matches_engagement_type(self, item):
        applicable_type_id = self._get_field(item, "applicableEngagementTypeId", "ApplicableEngagementTypeId", default=None)
        selected_type_id = self._get_engagement_type_id()
        if applicable_type_id in (None, "", 0) or selected_type_id is None:
            return True
        return str(applicable_type_id) == str(selected_type_id)

    def _get_filtered_procedure_templates(self):
        return [item for item in self.procedure_library or [] if self._matches_engagement_type(item)]

    def _get_filtered_working_paper_templates(self):
        return [item for item in self.working_paper_templates or [] if self._matches_engagement_type(item)]

    def _build_engagement_mode_card(self):
        profile = self._get_engagement_profile()
        engagement_type_name = self._get_engagement_type_name() or "Not selected"
        chip_color = "#2563eb" if self._is_external_audit() else "#0f766e" if self._is_internal_audit() else "#64748b"
        return ft.Card(
            content=ft.Container(
                padding=18,
                content=ft.Column([
                    ft.Row([
                        ft.Text(profile["mode_title"], size=16, weight=ft.FontWeight.BOLD, color="#2c3e50"),
                        ft.Container(expand=True),
                        ft.Container(
                            content=ft.Text(engagement_type_name, size=11, color="white"),
                            bgcolor=chip_color,
                            padding=ft.padding.symmetric(horizontal=10, vertical=5),
                            border_radius=999
                        )
                    ]),
                    ft.Text(profile["focus_label"], size=12, color="#475569"),
                    ft.Text(profile["planning_hint"], size=11, color="#64748b"),
                    ft.Text(f"Template focus: {profile['template_hint']}", size=11, color="#7f8c8d")
                ], spacing=6)
            )
        )

    def _build_materiality_summary_text(self):
        active_calculation = self._get_active_materiality_calculation()
        materiality_text = self._get_field(self.planning_data, "materiality", "Materiality", default="")
        basis = self._get_materiality_basis_label(active_calculation)
        overall = self._get_active_materiality_value("overallMateriality", "OverallMateriality")
        performance = self._get_active_materiality_value("performanceMateriality", "PerformanceMateriality")
        clearly_trivial = self._get_active_materiality_value("clearlyTrivialThreshold", "ClearlyTrivialThreshold")
        if not any([
            materiality_text and str(materiality_text).strip(),
            basis and str(basis).strip() and str(basis).strip().lower() != "not captured",
            overall not in (None, "", 0, 0.0),
            performance not in (None, "", 0, 0.0),
            clearly_trivial not in (None, "", 0, 0.0),
        ]):
            return "Materiality / thresholds not set yet."
        return (
            f"Materiality note: {materiality_text or 'Not captured'} | "
            f"Basis: {basis or 'Not captured'} | "
            f"Overall: {overall if overall is not None else 'Not set'} | "
            f"Performance: {performance if performance is not None else 'Not set'} | "
            f"Clearly trivial: {clearly_trivial if clearly_trivial is not None else 'Not set'}"
        )

    def _has_materiality_data(self):
        values = [
            self._get_field(self.planning_data, "materiality", "Materiality", default=""),
            self._get_materiality_basis_label(),
            self._get_active_materiality_value("overallMateriality", "OverallMateriality"),
            self._get_active_materiality_value("performanceMateriality", "PerformanceMateriality"),
            self._get_active_materiality_value("clearlyTrivialThreshold", "ClearlyTrivialThreshold"),
        ]
        for value in values:
            if value not in (None, "", 0, 0.0, "0"):
                return True
        return False

    def _get_active_materiality_calculation(self):
        return self._get_field(self.materiality_workspace, "activeCalculation", "ActiveCalculation", default=None)

    def _get_materiality_candidates(self):
        return self._get_field(self.materiality_workspace, "benchmarkCandidates", "BenchmarkCandidates", default=[]) or []

    def _get_materiality_calculations(self):
        return self._get_field(self.materiality_workspace, "calculations", "Calculations", default=[]) or []

    def _get_materiality_benchmark_profiles(self):
        return self._get_field(self.materiality_workspace, "benchmarkProfiles", "BenchmarkProfiles", default=[]) or []

    def _get_materiality_approval_history(self):
        return self._get_field(self.materiality_workspace, "approvalHistory", "ApprovalHistory", default=[]) or []

    def _get_materiality_application_summary(self):
        return self._get_field(self.materiality_workspace, "applicationSummary", "ApplicationSummary", default={}) or {}

    def _get_materiality_misstatement_summary(self):
        return self._get_field(self.materiality_workspace, "misstatementSummary", "MisstatementSummary", default={}) or {}

    def _get_materiality_scope_links(self):
        return self._get_field(self.materiality_workspace, "scopeLinks", "ScopeLinks", default=[]) or []

    def _get_materiality_misstatements(self):
        return self._get_field(self.materiality_workspace, "misstatements", "Misstatements", default=[]) or []

    def _get_active_materiality_value(self, camel_key, pascal_key):
        active = self._get_active_materiality_calculation()
        if isinstance(active, dict):
            value = active.get(camel_key)
            if value in (None, ""):
                value = active.get(pascal_key)
            if value not in (None, ""):
                return value
        return self._get_field(self.planning_data, camel_key, pascal_key, default=None)

    def _get_materiality_basis_label(self, active_calculation=None):
        active = active_calculation or self._get_active_materiality_calculation()
        if isinstance(active, dict):
            benchmark_name = active.get("benchmarkName") or active.get("BenchmarkName")
            percentage = active.get("percentageApplied")
            if percentage in (None, ""):
                percentage = active.get("PercentageApplied")
            if benchmark_name:
                if percentage not in (None, ""):
                    return f"{benchmark_name} @ {percentage}%"
                return str(benchmark_name)
        return self._get_field(self.planning_data, "materialityBasis", "MaterialityBasis", default="Not captured")

    def _find_materiality_profile(self, profile_id):
        if profile_id in (None, "", 0, "0"):
            return None
        for profile in self._get_materiality_benchmark_profiles():
            if str(self._get_field(profile, "id", "Id", default="")) == str(profile_id):
                return profile
        return None

    def _get_selected_materiality_profile(self):
        active_calculation = self._get_active_materiality_calculation() or {}
        selected_profile_id = self._get_field(active_calculation, "benchmarkProfileId", "BenchmarkProfileId", default=None)
        if selected_profile_id in (None, "", 0, "0"):
            selected_profile_id = self._get_field(self.materiality_workspace, "selectedBenchmarkProfileId", "SelectedBenchmarkProfileId", default=None)
        profile = self._find_materiality_profile(selected_profile_id)
        if profile:
            return profile
        profiles = self._get_materiality_benchmark_profiles()
        return profiles[0] if profiles else None

    def _format_materiality_value(self, value):
        if value in (None, "", 0, 0.0, "0"):
            return "Not set"
        try:
            return format_currency(value)
        except Exception:
            return str(value)

    def _build_materiality_workspace_card(self):
        workspace = self.materiality_workspace or {}
        active_calculation = self._get_active_materiality_calculation()
        selected_profile = self._get_selected_materiality_profile() or {}
        latest_year = self._get_field(workspace, "latestTrialBalanceYear", "LatestTrialBalanceYear", default="Not available")
        account_count = self._get_field(workspace, "trialBalanceAccountCount", "TrialBalanceAccountCount", default=0)
        import_at = self._get_field(workspace, "latestAnalyticsImportAt", "LatestAnalyticsImportAt", default=None)
        import_label = format_date(import_at) if import_at else "No analytics import yet"
        active_summary = self._get_field(active_calculation, "calculationSummary", "CalculationSummary", default="No active calculation")
        source_label = "Calculated from imported financial data" if active_calculation else "Manual planning values currently active"
        profile_name = self._get_field(selected_profile, "profileName", "ProfileName", default=self._get_field(workspace, "selectedBenchmarkProfileName", "SelectedBenchmarkProfileName", default="Not selected"))
        validation_status = self._get_field(selected_profile, "validationStatus", "ValidationStatus", default=self._get_field(active_calculation, "benchmarkProfileValidationStatus", "BenchmarkProfileValidationStatus", default="Not captured"))
        context_bits = [
            self._get_field(workspace, "materialityEntityType", "MaterialityEntityType", default=""),
            self._get_field(workspace, "materialityIndustryName", "MaterialityIndustryName", default=""),
        ]
        context_label = " | ".join(bit for bit in context_bits if bit) or "Not captured"

        return ft.Card(
            content=ft.Container(
                padding=20,
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Text("Materiality Calculator", size=16, weight=ft.FontWeight.BOLD),
                                ft.Container(expand=True),
                                ft.Container(
                                    content=ft.Text(
                                        "Ready" if self._get_field(workspace, "hasTrialBalanceData", "HasTrialBalanceData", default=False) else "Awaiting Trial Balance Import",
                                        size=11,
                                        color="white",
                                    ),
                                    bgcolor="#0f766e" if self._get_field(workspace, "hasTrialBalanceData", "HasTrialBalanceData", default=False) else "#64748b",
                                    padding=ft.padding.symmetric(horizontal=10, vertical=5),
                                    border_radius=12,
                                ),
                            ]
                        ),
                        ft.Divider(),
                        ft.ResponsiveRow(
                            [
                                ft.Container(
                                    col={"sm": 12, "md": 6, "xl": 3},
                                    content=self._create_info_row("Trial Balance Year", latest_year),
                                ),
                                ft.Container(
                                    col={"sm": 12, "md": 6, "xl": 3},
                                    content=self._create_info_row("Accounts Imported", account_count),
                                ),
                                ft.Container(
                                    col={"sm": 12, "md": 6, "xl": 3},
                                    content=self._create_info_row("Candidate Set", len(self._get_materiality_candidates())),
                                ),
                                ft.Container(
                                    col={"sm": 12, "md": 6, "xl": 3},
                                    content=self._create_info_row("Calculation History", len(self._get_materiality_calculations())),
                                ),
                            ],
                            run_spacing=8,
                        ),
                        self._create_info_row("Latest Analytics Import", import_label),
                        self._create_info_row("Active Benchmark", active_summary),
                        self._create_info_row("Benchmark Profile", profile_name),
                        self._create_info_row("Validation Status", validation_status),
                        self._create_info_row("Entity / Industry Context", context_label),
                        self._create_info_row("Approval History", len(self._get_materiality_approval_history())),
                        ft.Text(source_label, size=12, color="#475569"),
                        ft.Text(
                            "Imported trial balance data should drive benchmark selection. Manual materiality fields remain available as an override.",
                            size=11,
                            color="#64748b",
                        ),
                    ],
                    spacing=8,
                ),
            )
        )

    def _build_materiality_details_card(self):
        materiality_text = self._get_field(self.planning_data, "materiality", "Materiality", default="Not captured")
        basis = self._get_materiality_basis_label()
        overall = self._get_active_materiality_value("overallMateriality", "OverallMateriality")
        performance = self._get_active_materiality_value("performanceMateriality", "PerformanceMateriality")
        clearly_trivial = self._get_active_materiality_value("clearlyTrivialThreshold", "ClearlyTrivialThreshold")
        active_calculation = self._get_active_materiality_calculation()
        selected_profile = self._get_selected_materiality_profile() or {}
        active_summary = self._get_field(active_calculation, "calculationSummary", "CalculationSummary", default="Manual planning values")
        validation_status = self._get_field(active_calculation, "benchmarkProfileValidationStatus", "BenchmarkProfileValidationStatus", default=self._get_field(selected_profile, "validationStatus", "ValidationStatus", default="Not captured"))
        selection_rationale = self._get_field(active_calculation, "benchmarkSelectionRationale", "BenchmarkSelectionRationale", default=self._get_field(self.materiality_workspace, "materialityBenchmarkSelectionRationale", "MaterialityBenchmarkSelectionRationale", default="Not captured"))
        context_bits = [
            self._get_field(active_calculation, "entityType", "EntityType", default=self._get_field(self.materiality_workspace, "materialityEntityType", "MaterialityEntityType", default="")),
            self._get_field(active_calculation, "industryName", "IndustryName", default=self._get_field(self.materiality_workspace, "materialityIndustryName", "MaterialityIndustryName", default="")),
        ]
        context_label = " | ".join(bit for bit in context_bits if bit) or "Not captured"

        return ft.Card(
            content=ft.Container(
                padding=20,
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Text("Materiality & Thresholds", size=16, weight=ft.FontWeight.BOLD),
                                ft.Container(expand=True),
                                ft.Container(
                                    content=ft.Text("Calculated" if active_calculation else ("External Audit" if self._is_external_audit() else "Captured Values"), size=11, color="white"),
                                    bgcolor="#2563eb" if (self._is_external_audit() or active_calculation) else "#64748b",
                                    padding=ft.padding.symmetric(horizontal=10, vertical=5),
                                    border_radius=12,
                                ),
                            ]
                        ),
                        ft.Divider(),
                        self._create_info_row("Active Source", active_summary),
                        self._create_info_row("Materiality Note", materiality_text or "Not captured"),
                        self._create_info_row("Basis", basis or "Not captured"),
                        self._create_info_row("Overall", self._format_materiality_value(overall)),
                        self._create_info_row("Performance", self._format_materiality_value(performance)),
                        self._create_info_row("Clearly Trivial", self._format_materiality_value(clearly_trivial)),
                        self._create_info_row("Validation Status", validation_status),
                        self._create_info_row("Entity / Industry", context_label),
                        self._create_info_row("Selection Rationale", selection_rationale or "Not captured"),
                    ],
                    spacing=8,
                ),
            )
        )

    def _build_materiality_population_controls(self, items, empty_message, action_builder=None):
        if not items:
            return [ft.Text(empty_message, size=12, color="#64748b")]

        controls = []
        for item in items:
            identifier = self._get_field(item, "itemIdentifier", "ItemIdentifier", default="Item")
            description = self._get_field(item, "description", "Description", default="")
            amount = self._format_materiality_value(self._get_field(item, "basisAmount", "BasisAmount", default=0))
            account_number = self._get_field(item, "accountNumber", "AccountNumber", default="")
            fsli = self._get_field(item, "fsli", "Fsli", default="")
            action = self._get_field(item, "recommendedAction", "RecommendedAction", default="")
            source_dataset = self._get_field(item, "sourceDataset", "SourceDataset", default="")
            action_controls = action_builder(item) if action_builder else []

            meta_parts = [part for part in [account_number, fsli, source_dataset] if part]
            controls.append(
                ft.Container(
                    padding=12,
                    bgcolor="#ffffff",
                    border=ft.border.all(1, "#e2e8f0"),
                    border_radius=8,
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Text(identifier, size=12, weight=ft.FontWeight.BOLD, color="#1e293b"),
                                    ft.Container(expand=True),
                                    ft.Text(amount, size=12, weight=ft.FontWeight.BOLD, color="#0f172a"),
                                ]
                            ),
                            ft.Text(description or "No description", size=12, color="#334155"),
                            ft.Text(" | ".join(meta_parts), size=11, color="#64748b") if meta_parts else ft.Container(),
                            ft.Text(action, size=11, color="#2563eb") if action else ft.Container(),
                            ft.Row(action_controls, spacing=8, scroll=ft.ScrollMode.AUTO) if action_controls else ft.Container(),
                        ],
                        spacing=4,
                    ),
                )
            )
        return controls

    def _build_materiality_scope_link_controls(self):
        links = self._get_materiality_scope_links()
        if not links:
            return [ft.Text("No scope decisions have been recorded from materiality yet.", size=12, color="#64748b")]

        controls = []
        for link in links[:8]:
            scope_label = self._get_field(link, "scopeItemLabel", "ScopeItemLabel", default="Not linked to a scope item")
            fsli = self._get_field(link, "fsli", "Fsli", default="Not set")
            coverage_percent = self._get_field(link, "coveragePercent", "CoveragePercent", default=None)
            relevance = self._get_field(link, "benchmarkRelevance", "BenchmarkRelevance", default="Materiality scope decision")
            inclusion_reason = self._get_field(link, "inclusionReason", "InclusionReason", default="No rationale captured")
            created_at = self._get_field(link, "createdAt", "CreatedAt", default=None)
            if isinstance(coverage_percent, (int, float)):
                coverage_text = f"{coverage_percent:.1f}%"
            elif coverage_percent not in (None, ""):
                coverage_text = f"{coverage_percent}%"
            else:
                coverage_text = "Not set"

            controls.append(
                ft.Container(
                    padding=12,
                    bgcolor="#ffffff",
                    border=ft.border.all(1, "#e2e8f0"),
                    border_radius=8,
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Text(fsli, size=12, weight=ft.FontWeight.BOLD, color="#1e293b"),
                                    ft.Container(expand=True),
                                    ft.Container(
                                        content=ft.Text("Linked" if self._get_field(link, "scopeItemId", "ScopeItemId", default=None) else "Suggested", size=11, color="white"),
                                        bgcolor="#0f766e" if self._get_field(link, "scopeItemId", "ScopeItemId", default=None) else "#7c3aed",
                                        padding=ft.padding.symmetric(horizontal=10, vertical=5),
                                        border_radius=999,
                                    ),
                                ]
                            ),
                            ft.Text(f"Scope: {scope_label}", size=12, color="#334155"),
                            ft.Text(f"{relevance} | Coverage: {coverage_text}", size=11, color="#64748b"),
                            ft.Text(inclusion_reason, size=11, color="#475569"),
                            ft.Row(
                                [
                                    ft.TextButton(
                                        "Edit",
                                        icon=Icons.EDIT,
                                        on_click=lambda _, selected=link: self._open_materiality_scope_link_dialog(existing_link=selected),
                                    ),
                                    ft.TextButton(
                                        "Delete",
                                        icon=Icons.DELETE_OUTLINE,
                                        on_click=lambda _, selected=link: self._confirm_delete_materiality_scope_link(selected),
                                    ),
                                    ft.Container(expand=True),
                                    ft.Text(format_date(created_at), size=11, color="#94a3b8") if created_at else ft.Container(),
                                ],
                                spacing=8,
                            ),
                        ],
                        spacing=4,
                    ),
                )
            )
        return controls

    def _build_materiality_misstatement_controls(self):
        misstatements = self._get_materiality_misstatements()
        if not misstatements:
            return [ft.Text("No misstatements have been recorded yet.", size=12, color="#64748b")]

        controls = []
        for misstatement in misstatements[:8]:
            description = self._get_field(misstatement, "description", "Description", default="Misstatement")
            actual_amount = self._format_materiality_value(self._get_field(misstatement, "actualAmount", "ActualAmount", default=0))
            projected_value = self._get_field(misstatement, "projectedAmount", "ProjectedAmount", default=self._get_field(misstatement, "actualAmount", "ActualAmount", default=0))
            projected_amount = self._format_materiality_value(projected_value)
            status = self._get_field(misstatement, "status", "Status", default="Open")
            threshold_flags = []
            if self._get_field(misstatement, "exceedsClearlyTrivial", "ExceedsClearlyTrivial", default=False):
                threshold_flags.append("Above CT")
            if self._get_field(misstatement, "exceedsPerformanceMateriality", "ExceedsPerformanceMateriality", default=False):
                threshold_flags.append("Above PM")
            if self._get_field(misstatement, "exceedsOverallMateriality", "ExceedsOverallMateriality", default=False):
                threshold_flags.append("Above OM")
            threshold_label = " | ".join(threshold_flags) if threshold_flags else "Below thresholds"
            meta_parts = [
                self._get_field(misstatement, "transactionIdentifier", "TransactionIdentifier", default=""),
                self._get_field(misstatement, "accountNumber", "AccountNumber", default=""),
                self._get_field(misstatement, "fsli", "Fsli", default=""),
            ]
            meta_text = " | ".join(part for part in meta_parts if part)
            linked_finding_title = self._get_field(misstatement, "findingTitle", "FindingTitle", default="")
            can_escalate_to_finding = (
                not self._get_field(misstatement, "findingId", "FindingId", default=None)
                and (
                    self._get_field(misstatement, "exceedsPerformanceMateriality", "ExceedsPerformanceMateriality", default=False)
                    or self._get_field(misstatement, "exceedsOverallMateriality", "ExceedsOverallMateriality", default=False)
                )
            )

            action_buttons = []
            if can_escalate_to_finding:
                action_buttons.append(
                    ft.TextButton(
                        "Create Finding",
                        icon=Icons.BUG_REPORT,
                        on_click=lambda _, selected=misstatement: self._open_finding_from_misstatement_dialog(selected),
                    )
                )
            action_buttons.extend(
                [
                    ft.TextButton(
                        "Edit",
                        icon=Icons.EDIT,
                        on_click=lambda _, selected=misstatement: self._open_materiality_misstatement_dialog(existing_misstatement=selected),
                    ),
                    ft.TextButton(
                        "Delete",
                        icon=Icons.DELETE_OUTLINE,
                        on_click=lambda _, selected=misstatement: self._confirm_delete_materiality_misstatement(selected),
                    ),
                ]
            )

            controls.append(
                ft.Container(
                    padding=12,
                    bgcolor="#ffffff",
                    border=ft.border.all(1, "#e2e8f0"),
                    border_radius=8,
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Text(description, size=12, weight=ft.FontWeight.BOLD, color="#1e293b"),
                                    ft.Container(expand=True),
                                    ft.Container(
                                        content=ft.Text(status, size=11, color="white"),
                                        bgcolor="#dc2626" if "open" in str(status).lower() else "#0f766e",
                                        padding=ft.padding.symmetric(horizontal=10, vertical=5),
                                        border_radius=999,
                                    ),
                                ]
                            ),
                            ft.Text(meta_text, size=11, color="#64748b") if meta_text else ft.Container(),
                            ft.Text(f"Actual: {actual_amount} | Projected: {projected_amount}", size=11, color="#334155"),
                            ft.Text(threshold_label, size=11, color="#7c2d12" if "Above" in threshold_label else "#64748b"),
                            ft.Text(f"Linked finding: {linked_finding_title}", size=11, color="#2563eb") if linked_finding_title else ft.Container(),
                            ft.Row(action_buttons, spacing=8, scroll=ft.ScrollMode.AUTO),
                        ],
                        spacing=4,
                    ),
                )
            )
        return controls

    def _get_materiality_misstatement_status_counts(self):
        counts = {
            "open": 0,
            "adjustment_requested": 0,
            "corrected": 0,
            "carried_forward": 0,
            "linked_findings": 0,
        }
        for misstatement in self._get_materiality_misstatements():
            status = (self._get_field(misstatement, "status", "Status", default="Open") or "").strip().lower()
            if status == "management adjustment requested":
                counts["adjustment_requested"] += 1
            elif status == "corrected":
                counts["corrected"] += 1
            elif status == "carried forward":
                counts["carried_forward"] += 1
            else:
                counts["open"] += 1

            if self._get_field(misstatement, "findingId", "FindingId", default=None):
                counts["linked_findings"] += 1
        return counts

    def _get_materiality_misstatement_band_counts(self):
        counts = {
            "below_ct": 0,
            "ct_to_pm": 0,
            "pm_to_om": 0,
            "above_om": 0,
        }
        for misstatement in self._get_materiality_misstatements():
            above_ct = self._get_field(misstatement, "exceedsClearlyTrivial", "ExceedsClearlyTrivial", default=False)
            above_pm = self._get_field(misstatement, "exceedsPerformanceMateriality", "ExceedsPerformanceMateriality", default=False)
            above_om = self._get_field(misstatement, "exceedsOverallMateriality", "ExceedsOverallMateriality", default=False)
            if above_om:
                counts["above_om"] += 1
            elif above_pm:
                counts["pm_to_om"] += 1
            elif above_ct:
                counts["ct_to_pm"] += 1
            else:
                counts["below_ct"] += 1
        return counts

    def _build_materiality_evaluation_workspace(self):
        misstatement_summary = self._get_materiality_misstatement_summary()
        misstatements = self._get_materiality_misstatements()
        if not misstatements:
            return ft.Container(
                padding=14,
                bgcolor="#f8fafc",
                border=ft.border.all(1, "#e2e8f0"),
                border_radius=10,
                content=ft.Text("No misstatements have been recorded yet, so there is nothing to evaluate against clearly trivial, performance materiality, or overall materiality.", size=12, color="#64748b"),
            )

        status_counts = self._get_materiality_misstatement_status_counts()
        band_counts = self._get_materiality_misstatement_band_counts()
        conclusion = self._get_field(misstatement_summary, "evaluationConclusion", "EvaluationConclusion", default="No evaluation conclusion available.")
        projected_amount = self._get_field(misstatement_summary, "totalProjectedAmount", "TotalProjectedAmount", default=0)
        overall_materiality = self._get_field(misstatement_summary, "overallMateriality", "OverallMateriality", default=0)
        performance_materiality = self._get_field(misstatement_summary, "performanceMateriality", "PerformanceMateriality", default=0)
        clearly_trivial = self._get_field(misstatement_summary, "clearlyTrivialThreshold", "ClearlyTrivialThreshold", default=0)

        return ft.Container(
            padding=14,
            bgcolor="#f8fafc",
            border=ft.border.all(1, "#e2e8f0"),
            border_radius=10,
            content=ft.Column(
                [
                    ft.Text("Misstatement Evaluation Workspace", size=14, weight=ft.FontWeight.BOLD, color="#1f2937"),
                    ft.Text(conclusion, size=12, color="#475569"),
                    ft.Row(
                        [
                            self._create_control_status_card("Open", str(status_counts["open"]), "#dc2626"),
                            self._create_control_status_card("Adj. Requested", str(status_counts["adjustment_requested"]), "#f59e0b"),
                            self._create_control_status_card("Corrected", str(status_counts["corrected"]), "#16a34a"),
                            self._create_control_status_card("Carried", str(status_counts["carried_forward"]), "#7c3aed"),
                            self._create_control_status_card("Linked Findings", str(status_counts["linked_findings"]), "#2563eb"),
                        ],
                        spacing=12,
                        scroll=ft.ScrollMode.AUTO,
                    ),
                    ft.Row(
                        [
                            self._create_control_status_card("Below CT", str(band_counts["below_ct"]), "#64748b"),
                            self._create_control_status_card("CT to PM", str(band_counts["ct_to_pm"]), "#f59e0b"),
                            self._create_control_status_card("PM to OM", str(band_counts["pm_to_om"]), "#dc2626"),
                            self._create_control_status_card("Above OM", str(band_counts["above_om"]), "#7f1d1d"),
                        ],
                        spacing=12,
                        scroll=ft.ScrollMode.AUTO,
                    ),
                    ft.ResponsiveRow(
                        [
                            ft.Container(col={"sm": 12, "md": 6}, content=self._create_info_row("Projected Misstatements", self._format_materiality_value(projected_amount))),
                            ft.Container(col={"sm": 12, "md": 6}, content=self._create_info_row("Threshold Source", self._get_field(misstatement_summary, "thresholdSource", "ThresholdSource", default="Not Set"))),
                            ft.Container(col={"sm": 12, "md": 4}, content=self._create_info_row("Clearly Trivial", self._format_materiality_value(clearly_trivial))),
                            ft.Container(col={"sm": 12, "md": 4}, content=self._create_info_row("Performance", self._format_materiality_value(performance_materiality))),
                            ft.Container(col={"sm": 12, "md": 4}, content=self._create_info_row("Overall", self._format_materiality_value(overall_materiality))),
                        ],
                        run_spacing=8,
                    ),
                ],
                spacing=10,
            ),
        )

    def _build_materiality_application_card(self):
        application = self._get_materiality_application_summary()
        misstatement = self._get_materiality_misstatement_summary()

        guidance = self._get_field(application, "guidance", "Guidance", default="Apply active materiality to imported journal or trial balance data.")
        source = self._get_field(application, "populationSource", "PopulationSource", default="No population available")
        year = self._get_field(application, "populationFiscalYear", "PopulationFiscalYear", default="Not set")
        key_items = self._get_field(application, "keyItems", "KeyItems", default=[]) or []
        sample_pool = self._get_field(application, "samplePoolItems", "SamplePoolItems", default=[]) or []
        scope_candidates = self._get_field(application, "scopeCandidates", "ScopeCandidates", default=[]) or []
        conclusion = self._get_field(misstatement, "evaluationConclusion", "EvaluationConclusion", default="No misstatement evaluation available yet.")

        return ft.Card(
            content=ft.Container(
                padding=20,
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Text("Materiality Application", size=16, weight=ft.FontWeight.BOLD),
                                ft.Container(expand=True),
                                ft.OutlinedButton(
                                    "Record Misstatement",
                                    icon=Icons.REPORT_PROBLEM,
                                    on_click=lambda _: self._open_materiality_misstatement_dialog(),
                                ),
                                ft.OutlinedButton(
                                    "Add Scope Decision",
                                    icon=Icons.RULE_FOLDER,
                                    on_click=lambda _: self._open_materiality_scope_link_dialog(),
                                ),
                                ft.Container(
                                    content=ft.Text(
                                        self._get_field(application, "thresholdSource", "ThresholdSource", default="Not Set"),
                                        size=11,
                                        color="white",
                                    ),
                                    bgcolor="#2563eb" if self._get_active_materiality_calculation() else "#64748b",
                                    padding=ft.padding.symmetric(horizontal=10, vertical=5),
                                    border_radius=12,
                                ),
                            ]
                        ),
                        ft.Divider(),
                        ft.Text(guidance, size=12, color="#475569"),
                        ft.ResponsiveRow(
                            [
                                ft.Container(col={"sm": 12, "md": 6, "xl": 3}, content=self._create_info_row("Population", source)),
                                ft.Container(col={"sm": 12, "md": 6, "xl": 3}, content=self._create_info_row("Fiscal Year", year)),
                                ft.Container(col={"sm": 12, "md": 6, "xl": 3}, content=self._create_info_row("Overall", self._format_materiality_value(self._get_field(application, "overallMateriality", "OverallMateriality", default=0)))),
                                ft.Container(col={"sm": 12, "md": 6, "xl": 3}, content=self._create_info_row("Performance", self._format_materiality_value(self._get_field(application, "performanceMateriality", "PerformanceMateriality", default=0)))),
                            ],
                            run_spacing=8,
                        ),
                        ft.Row(
                            [
                                self._create_control_status_card("Population", str(self._get_field(application, "populationItemCount", "PopulationItemCount", default=0)), "#2563eb"),
                                self._create_control_status_card("Key Items", str(self._get_field(application, "keyItemCount", "KeyItemCount", default=0)), "#dc2626"),
                                self._create_control_status_card("Sample Pool", str(self._get_field(application, "samplePoolCount", "SamplePoolCount", default=0)), "#16a34a"),
                                self._create_control_status_card("Scope Candidates", str(self._get_field(application, "scopeCandidateCount", "ScopeCandidateCount", default=0)), "#7c3aed"),
                            ],
                            spacing=12,
                            scroll=ft.ScrollMode.AUTO,
                        ),
                        ft.ResponsiveRow(
                            [
                                ft.Container(
                                    col={"sm": 12, "lg": 6},
                                    content=ft.Column(
                                        [
                                            ft.Text("Key Items / 100% Testing", size=14, weight=ft.FontWeight.BOLD, color="#1f2937"),
                                            *self._build_materiality_population_controls(
                                                key_items,
                                                "No imported items currently exceed performance materiality.",
                                                action_builder=lambda item: [
                                                    ft.TextButton(
                                                        "Record Misstatement",
                                                        icon=Icons.REPORT_PROBLEM,
                                                        on_click=lambda _, selected=item: self._open_materiality_misstatement_dialog(source_item=selected),
                                                    )
                                                ],
                                            )
                                        ],
                                        spacing=8,
                                    ),
                                ),
                                ft.Container(
                                    col={"sm": 12, "lg": 6},
                                    content=ft.Column(
                                        [
                                            ft.Text("Sample Pool", size=14, weight=ft.FontWeight.BOLD, color="#1f2937"),
                                            *self._build_materiality_population_controls(
                                                sample_pool,
                                                "No sample-pool items available from the current import.",
                                                action_builder=lambda item: [
                                                    ft.TextButton(
                                                        "Record Misstatement",
                                                        icon=Icons.REPORT_PROBLEM,
                                                        on_click=lambda _, selected=item: self._open_materiality_misstatement_dialog(source_item=selected),
                                                    )
                                                ],
                                            )
                                        ],
                                        spacing=8,
                                    ),
                                ),
                            ],
                            run_spacing=12,
                        ),
                        ft.Divider(),
                        ft.Text("FSLI / Balance Scope Candidates", size=14, weight=ft.FontWeight.BOLD, color="#1f2937"),
                        *self._build_materiality_population_controls(
                            scope_candidates,
                            "No trial-balance balances currently exceed overall materiality for scope suggestion.",
                            action_builder=lambda item: [
                                ft.TextButton(
                                    "Add Scope Decision",
                                    icon=Icons.RULE_FOLDER,
                                    on_click=lambda _, selected=item: self._open_materiality_scope_link_dialog(source_item=selected),
                                )
                            ],
                        ),
                        ft.Text("Recorded Scope Decisions", size=14, weight=ft.FontWeight.BOLD, color="#1f2937"),
                        *self._build_materiality_scope_link_controls(),
                        ft.Divider(),
                        ft.Text("Summary of Audit Differences", size=14, weight=ft.FontWeight.BOLD, color="#1f2937"),
                        ft.Text(conclusion, size=12, color="#475569"),
                        ft.Row(
                            [
                                self._create_control_status_card("Recorded", str(self._get_field(misstatement, "totalRecordedMisstatements", "TotalRecordedMisstatements", default=0)), "#2563eb"),
                                self._create_control_status_card("Above CT", str(self._get_field(misstatement, "aboveClearlyTrivialCount", "AboveClearlyTrivialCount", default=0)), "#f59e0b"),
                                self._create_control_status_card("Above PM", str(self._get_field(misstatement, "abovePerformanceMaterialityCount", "AbovePerformanceMaterialityCount", default=0)), "#dc2626"),
                                self._create_control_status_card("Above OM", str(self._get_field(misstatement, "aboveOverallMaterialityCount", "AboveOverallMaterialityCount", default=0)), "#7f1d1d"),
                            ],
                            spacing=12,
                            scroll=ft.ScrollMode.AUTO,
                        ),
                        ft.ResponsiveRow(
                            [
                                ft.Container(col={"sm": 12, "md": 6}, content=self._create_info_row("Total Actual", self._format_materiality_value(self._get_field(misstatement, "totalActualAmount", "TotalActualAmount", default=0)))),
                                ft.Container(col={"sm": 12, "md": 6}, content=self._create_info_row("Total Projected", self._format_materiality_value(self._get_field(misstatement, "totalProjectedAmount", "TotalProjectedAmount", default=0)))),
                            ],
                            run_spacing=8,
                        ),
                        self._build_materiality_evaluation_workspace(),
                        ft.Text("Recorded Misstatements", size=14, weight=ft.FontWeight.BOLD, color="#1f2937"),
                        *self._build_materiality_misstatement_controls(),
                    ],
                    spacing=10,
                ),
            )
        )

    def _get_coverage_reporting_year(self):
        plan_year = self._get_field(self.planning_data, "planYear", "PlanYear", default=None)
        try:
            return int(plan_year) if plan_year not in (None, "", 0, "0") else datetime.now().year
        except (TypeError, ValueError):
            return datetime.now().year

    def _get_coverage_summary(self):
        return self._get_field(self.audit_coverage_map, "summary", "Summary", default={}) or {}

    def _flatten_coverage_nodes(self, nodes):
        flattened = []
        for node in nodes or []:
            flattened.append(node)
            children = self._get_field(node, "children", "Children", default=[]) or []
            flattened.extend(self._flatten_coverage_nodes(children))
        return flattened

    def _get_priority_coverage_nodes(self, limit=5):
        nodes = self._flatten_coverage_nodes(self._get_field(self.audit_coverage_map, "nodes", "Nodes", default=[]))
        if not nodes:
            return []

        risk_rank = {"critical": 4, "high": 3, "medium": 2, "low": 1}

        prioritized = sorted(
            [
                node for node in nodes
                if self._get_field(node, "level", "Level", default=0) > 0
            ],
            key=lambda node: (
                float(self._get_field(node, "coveragePercentage", "CoveragePercentage", default=0) or 0),
                -risk_rank.get((self._get_field(node, "riskRating", "RiskRating", default="") or "").lower(), 0),
                -int(self._get_field(node, "openFindings", "OpenFindings", default=0) or 0),
                -int(self._get_field(node, "plannedAudits", "PlannedAudits", default=0) or 0),
            )
        )
        return prioritized[:limit]

    def _build_coverage_summary_cards(self):
        summary = self._get_coverage_summary()
        overall_coverage = float(self._get_field(summary, "overallCoverage", "OverallCoverage", default=0) or 0)
        nodes_audited = int(self._get_field(summary, "nodesAudited", "NodesAudited", default=0) or 0)
        below_target = int(self._get_field(summary, "nodesBelowTarget", "NodesBelowTarget", default=0) or 0)
        at_risk = int(self._get_field(summary, "nodesAtRisk", "NodesAtRisk", default=0) or 0)
        planned = int(self._get_field(summary, "totalPlannedAudits", "TotalPlannedAudits", default=0) or 0)
        completed = int(self._get_field(summary, "totalCompletedAudits", "TotalCompletedAudits", default=0) or 0)

        return [
            self._create_control_status_card("Overall", f"{overall_coverage:.0f}%", "#2563eb"),
            self._create_control_status_card("Nodes Audited", str(nodes_audited), "#16a34a"),
            self._create_control_status_card("Below Target", str(below_target), "#f59e0b"),
            self._create_control_status_card("At Risk", str(at_risk), "#dc2626"),
            self._create_control_status_card("Planned/Done", f"{completed}/{planned}", "#7c3aed"),
        ]

    def _build_coverage_focus_controls(self):
        focus_nodes = self._get_priority_coverage_nodes(limit=5)
        if not focus_nodes:
            return [ft.Text("Coverage register is not populated for the selected planning year yet.", color="#7f8c8d")]

        controls = []
        for node in focus_nodes:
            name = self._get_field(node, "name", "Name", default="Audit universe node")
            coverage = float(self._get_field(node, "coveragePercentage", "CoveragePercentage", default=0) or 0)
            risk_rating = self._get_field(node, "riskRating", "RiskRating", default="Unrated")
            planned = int(self._get_field(node, "plannedAudits", "PlannedAudits", default=0) or 0)
            completed = int(self._get_field(node, "completedAudits", "CompletedAudits", default=0) or 0)
            open_findings = int(self._get_field(node, "openFindings", "OpenFindings", default=0) or 0)
            status_color = "#dc2626" if coverage < 50 else "#f59e0b" if coverage < 80 else "#16a34a"

            controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text(name, size=13, weight=ft.FontWeight.BOLD, color="#1f2937"),
                            ft.Container(expand=True),
                            ft.Container(
                                content=ft.Text(f"{coverage:.0f}% covered", size=11, color="white"),
                                bgcolor=status_color,
                                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                border_radius=10
                            )
                        ]),
                        ft.Text(
                            f"Risk: {risk_rating} | Planned audits: {planned} | Completed: {completed} | Open findings: {open_findings}",
                            size=11,
                            color="#64748b"
                        )
                    ], spacing=4),
                    padding=12,
                    bgcolor="white",
                    border=ft.border.all(1, "#e6e9ed"),
                    border_radius=8
                )
            )
        return controls

    def _build_coverage_snapshot_card(self, title, compact=False):
        plan_name = self._get_field(self.planning_data, "annualPlanName", "AnnualPlanName", default="Not set")
        summary = self._get_coverage_summary()
        overall_coverage = float(self._get_field(summary, "overallCoverage", "OverallCoverage", default=0) or 0)
        below_target = int(self._get_field(summary, "nodesBelowTarget", "NodesBelowTarget", default=0) or 0)
        at_risk = int(self._get_field(summary, "nodesAtRisk", "NodesAtRisk", default=0) or 0)
        content_controls = [
            ft.Row([
                ft.Text(title, size=16, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),
                ft.Text(f"Plan Year {self._get_coverage_reporting_year()}", size=11, color="#64748b")
            ]),
            ft.Text(
                f"Annual plan: {plan_name}. Overall coverage is {overall_coverage:.1f}% with {below_target} nodes below target and {at_risk} at risk.",
                size=12,
                color="#475569"
            ),
            ft.Row(self._build_coverage_summary_cards(), spacing=12, scroll=ft.ScrollMode.AUTO),
        ]

        if not compact:
            content_controls.extend([
                ft.Divider(),
                ft.Text("Priority Coverage Gaps", size=14, weight=ft.FontWeight.BOLD, color="#1f2937"),
                ft.Column(self._build_coverage_focus_controls(), spacing=10)
            ])

        return ft.Card(
            content=ft.Container(
                padding=18,
                content=ft.Column(content_controls, spacing=10)
            )
        )

    def _get_working_paper_ref_options(self, current_ref=None):
        options = []
        seen = set()

        current_ref = (current_ref or "").strip()
        if current_ref:
            options.append(ft.dropdown.Option(key=current_ref, text=current_ref))
            seen.add(current_ref)

        for paper in self.working_papers_data or []:
            working_paper_ref = self._get_field(paper, "workingPaperCode", "WorkingPaperCode")
            title = self._get_field(paper, "title", "Title", default="Working paper")
            ref_value = str(working_paper_ref or title or "").strip()
            if not ref_value or ref_value in seen:
                continue

            option_text = ref_value if not title or title == ref_value else f"{ref_value} - {title}"
            options.append(ft.dropdown.Option(key=ref_value, text=option_text))
            seen.add(ref_value)

        return options

    def _get_requested_evidence_context(self):
        if not isinstance(self.document_upload_mode, str) or not self.document_upload_mode.startswith("request_item:"):
            return None, None

        try:
            request_item_id = int(self.document_upload_mode.split(":", 1)[1])
        except (TypeError, ValueError):
            return None, None

        for request in self.evidence_requests_data or []:
            for item in self._get_field(request, "items", "Items", default=[]) or []:
                if self._get_field(item, "id", "Id") == request_item_id:
                    return request, item
        return None, None

    def _reset_document_upload_state(self):
        self.pending_document_file = None
        self.document_upload_mode = "general"

    def _start_general_document_upload(self, e=None):
        self.document_upload_mode = "general"
        self._pick_document_file()

    def _start_requested_evidence_upload(self, request, request_item):
        request_item_id = self._get_field(request_item, "id", "Id")
        if not request_item_id:
            self._show_error("Unable to determine the evidence request item")
            return

        self.document_upload_mode = f"request_item:{request_item_id}"
        self._pick_document_file()

    def _build_procedure_summary_cards(self):
        total = len(self.procedures_data)
        planned = 0
        active = 0
        completed = 0
        overdue = 0

        for procedure in self.procedures_data:
            status_name = (self._get_field(procedure, "statusName", "StatusName", default="Planned") or "").lower()
            if "planned" in status_name:
                planned += 1
            if status_name in {"in progress", "performed", "under review"}:
                active += 1
            if status_name in {"completed", "not applicable"}:
                completed += 1
            if self._get_field(procedure, "isOverdue", "IsOverdue", default=False):
                overdue += 1

        return [
            self._create_control_status_card("Total", str(total), "#2563eb"),
            self._create_control_status_card("Planned", str(planned), "#3b82f6"),
            self._create_control_status_card("Active", str(active), "#8b5cf6"),
            self._create_control_status_card("Completed", str(completed), "#16a34a"),
            self._create_control_status_card("Overdue", str(overdue), "#dc2626"),
        ]

    def _build_procedure_item_controls(self):
        if not self.procedures_data:
            return [ft.Text("No procedures have been assigned to this assessment yet.", color="#7f8c8d")]

        controls = []
        for procedure in self.procedures_data:
            planned_date = self._get_field(procedure, "plannedDate", "PlannedDate")
            performed_date = self._get_field(procedure, "performedDate", "PerformedDate")
            if isinstance(planned_date, str) and "T" in planned_date:
                planned_date = planned_date.split("T")[0]
            if isinstance(performed_date, str) and "T" in performed_date:
                performed_date = performed_date.split("T")[0]

            status_name = self._get_field(procedure, "statusName", "StatusName", default="Planned")
            status_color = self._get_field(procedure, "statusColor", "StatusColor", default="#3b82f6")
            procedure_type = self._get_field(procedure, "procedureTypeName", "ProcedureTypeName", default="Procedure")
            objective = self._get_field(procedure, "objective", "Objective", default="No objective recorded.")
            title = self._get_field(procedure, "procedureTitle", "ProcedureTitle", default="Untitled procedure")
            procedure_code = self._get_field(procedure, "procedureCode", "ProcedureCode", default="Draft")
            working_paper_ref = self._get_field(procedure, "workingPaperRef", "WorkingPaperRef", default="Not linked")
            owner = self._get_field(procedure, "owner", "Owner", default="Not assigned")
            sample_size = self._get_field(procedure, "sampleSize", "SampleSize", default=None)
            overdue = self._get_field(procedure, "isOverdue", "IsOverdue", default=False)

            controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text(procedure_code, size=12, color="#7f8c8d"),
                            ft.Container(expand=True),
                            ft.PopupMenuButton(
                                items=[
                                    ft.PopupMenuItem(
                                        text="Edit Procedure",
                                        icon=Icons.EDIT,
                                        on_click=lambda _, p=procedure: self._open_edit_procedure_dialog(p)
                                    ),
                                    ft.PopupMenuItem(
                                        text="Delete Procedure",
                                        icon=Icons.DELETE,
                                        on_click=lambda _, p=procedure: self._delete_procedure(p)
                                    ),
                                ]
                            ),
                            ft.Container(
                                content=ft.Text(status_name, size=11, color="white"),
                                bgcolor=status_color if not overdue else "#dc2626",
                                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                border_radius=999
                            )
                        ]),
                        ft.Text(title, size=15, weight=ft.FontWeight.BOLD, color="#2c3e50"),
                        ft.Text(objective, size=12, color="#5f6b7a"),
                        ft.Row([
                            ft.Text(f"Type: {procedure_type}", size=11, color="#7f8c8d"),
                            ft.Text(f"Planned: {planned_date or 'Not set'}", size=11, color="#7f8c8d"),
                            ft.Text(f"Performed: {performed_date or 'Not set'}", size=11, color="#7f8c8d"),
                        ], spacing=18),
                        ft.Row([
                            ft.Text(f"Working paper: {working_paper_ref}", size=11, color="#7f8c8d"),
                            ft.Text(f"Owner: {owner}", size=11, color="#7f8c8d"),
                            ft.Text(f"Sample size: {sample_size if sample_size is not None else 'N/A'}", size=11, color="#7f8c8d"),
                        ], spacing=18),
                    ], spacing=6),
                    padding=12,
                    bgcolor="white",
                    border_radius=8,
                    border=ft.border.all(1, "#e6e9ed")
                )
            )
        return controls

    def _build_procedure_template_controls(self):
        filtered_templates = self._get_filtered_procedure_templates()
        if not filtered_templates:
            return [ft.Text("No reusable procedure templates are available yet.", color="#7f8c8d")]

        controls = []
        for template in filtered_templates[:6]:
            pack_name = self._get_field(template, "templatePack", "TemplatePack", default="")
            pack_text = f" | Pack: {pack_name}" if pack_name else ""
            controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Column([
                            ft.Text(
                                self._get_field(template, "procedureTitle", "ProcedureTitle", default="Procedure template"),
                                size=14,
                                weight=ft.FontWeight.BOLD,
                                color="#2c3e50"
                            ),
                            ft.Text(
                                self._get_field(template, "objective", "Objective", default="No objective recorded."),
                                size=12,
                                color="#5f6b7a"
                            ),
                            ft.Text(
                                f"Type: {self._get_field(template, 'procedureTypeName', 'ProcedureTypeName', default='Procedure')}{pack_text}",
                                size=11,
                                color="#7f8c8d"
                            )
                        ], expand=True, spacing=4),
                        ft.OutlinedButton(
                            text="Use Template",
                            icon=Icons.FILE_COPY,
                            on_click=lambda _, t=template: self._open_add_procedure_from_template_dialog(None, t)
                        )
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=12,
                    bgcolor="white",
                    border_radius=8,
                    border=ft.border.all(1, "#e6e9ed")
                )
            )
        return controls

    def _build_working_paper_summary_cards(self):
        total = len(self.working_papers_data)
        draft = 0
        review_ready = 0
        approved = 0
        signoffs = 0

        for paper in self.working_papers_data:
            status_name = (self._get_field(paper, "statusName", "StatusName", default="Draft") or "").lower()
            if status_name in {"draft", "in preparation"}:
                draft += 1
            if status_name in {"ready for review", "review notes raised"}:
                review_ready += 1
            if status_name in {"approved", "archived"}:
                approved += 1
            signoffs += int(self._get_field(paper, "signOffCount", "SignOffCount", default=0) or 0)

        return [
            self._create_control_status_card("Total", str(total), "#0f766e"),
            self._create_control_status_card("Draft", str(draft), "#6b7280"),
            self._create_control_status_card("Review", str(review_ready), "#f59e0b"),
            self._create_control_status_card("Approved", str(approved), "#16a34a"),
            self._create_control_status_card("Sign-offs", str(signoffs), "#2563eb"),
        ]

    def _build_working_paper_item_controls(self):
        if not self.working_papers_data:
            return [ft.Text("No working papers have been created for this assessment yet.", color="#7f8c8d")]

        controls = []
        for paper in self.working_papers_data:
            status_name = self._get_field(paper, "statusName", "StatusName", default="Draft")
            status_color = self._get_field(paper, "statusColor", "StatusColor", default="#6b7280")
            prepared_date = self._get_field(paper, "preparedDate", "PreparedDate")
            reviewed_date = self._get_field(paper, "reviewedDate", "ReviewedDate")
            if isinstance(prepared_date, str) and "T" in prepared_date:
                prepared_date = prepared_date.split("T")[0]
            if isinstance(reviewed_date, str) and "T" in reviewed_date:
                reviewed_date = reviewed_date.split("T")[0]

            controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text(
                                self._get_field(paper, "workingPaperCode", "WorkingPaperCode", default="Draft"),
                                size=12,
                                color="#7f8c8d"
                            ),
                            ft.Container(expand=True),
                            ft.PopupMenuButton(
                                items=(
                                    [
                                        ft.PopupMenuItem(
                                            text="Request Review",
                                            icon=Icons.GAVEL,
                                            on_click=lambda _, wp=paper: self._open_working_paper_review_workflow_dialog(wp)
                                        )
                                    ] if can_start_workflows(self.user) else []
                                ) + [
                                    ft.PopupMenuItem(
                                        text="Add Sign-off",
                                        icon=Icons.CHECK_CIRCLE,
                                        on_click=lambda _, wp=paper: self._open_working_paper_signoff_dialog(wp)
                                    ),
                                    ft.PopupMenuItem(
                                        text="Link Cross-reference",
                                        icon=Icons.LINK,
                                        on_click=lambda _, wp=paper: self._open_working_paper_reference_dialog(wp)
                                    ),
                                    ft.PopupMenuItem(
                                        text="Edit Working Paper",
                                        icon=Icons.EDIT,
                                        on_click=lambda _, wp=paper: self._open_edit_working_paper_dialog(wp)
                                    ),
                                    ft.PopupMenuItem(
                                        text="Delete Working Paper",
                                        icon=Icons.DELETE,
                                        on_click=lambda _, wp=paper: self._delete_working_paper(wp)
                                    )
                                ]
                            ),
                            ft.Container(
                                content=ft.Text(status_name, size=11, color="white"),
                                bgcolor=status_color,
                                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                border_radius=999
                            )
                        ]),
                        ft.Text(
                            self._get_field(paper, "title", "Title", default="Untitled working paper"),
                            size=15,
                            weight=ft.FontWeight.BOLD,
                            color="#2c3e50"
                        ),
                        ft.Text(
                            self._get_field(paper, "objective", "Objective", default="No objective recorded."),
                            size=12,
                            color="#5f6b7a"
                        ),
                        ft.Row([
                            ft.Text(
                                f"Prepared by: {self._get_field(paper, 'preparedBy', 'PreparedBy', default='Unassigned')}",
                                size=11,
                                color="#7f8c8d"
                            ),
                            ft.Text(
                                f"Reviewer: {self._get_field(paper, 'reviewerName', 'ReviewerName', default='Unassigned')}",
                                size=11,
                                color="#7f8c8d"
                            ),
                            ft.Text(f"Prepared: {prepared_date or 'Not set'}", size=11, color="#7f8c8d"),
                            ft.Text(f"Reviewed: {reviewed_date or 'Not set'}", size=11, color="#7f8c8d"),
                        ], spacing=18),
                        ft.Row([
                            ft.Text(
                                f"Procedure: {self._get_field(paper, 'procedureTitle', 'ProcedureTitle', default='Not linked')}",
                                size=11,
                                color="#7f8c8d"
                            ),
                            ft.Text(
                                f"Cross-refs: {self._get_field(paper, 'referenceCount', 'ReferenceCount', default=0)}",
                                size=11,
                                color="#7f8c8d"
                            ),
                            ft.Text(
                                f"Sign-offs: {self._get_field(paper, 'signOffCount', 'SignOffCount', default=0)}",
                                size=11,
                                color="#7f8c8d"
                            ),
                        ], spacing=18),
                        ft.Text(
                            f"Conclusion: {self._get_field(paper, 'conclusion', 'Conclusion', default='No conclusion recorded.')}",
                            size=11,
                            color="#334155"
                        )
                    ], spacing=6),
                    padding=12,
                    bgcolor="white",
                    border_radius=8,
                    border=ft.border.all(1, "#e6e9ed")
                )
            )
        return controls

    def _build_working_paper_template_controls(self):
        filtered_templates = self._get_filtered_working_paper_templates()
        if not filtered_templates:
            return [ft.Text("No reusable working paper templates are available yet.", color="#7f8c8d")]

        controls = []
        for template in filtered_templates[:6]:
            pack_name = self._get_field(template, "templatePack", "TemplatePack", default="")
            pack_text = f" | Pack: {pack_name}" if pack_name else ""
            controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Column([
                            ft.Text(
                                self._get_field(template, "title", "Title", default="Working paper template"),
                                size=14,
                                weight=ft.FontWeight.BOLD,
                                color="#2c3e50"
                            ),
                            ft.Text(
                                self._get_field(template, "objective", "Objective", default="No objective recorded."),
                                size=12,
                                color="#5f6b7a"
                            ),
                            ft.Text(
                                f"Conclusion: {self._get_field(template, 'conclusion', 'Conclusion', default='Template conclusion guidance')}{pack_text}",
                                size=11,
                                color="#7f8c8d"
                            )
                        ], expand=True, spacing=4),
                        ft.OutlinedButton(
                            text="Use Template",
                            icon=Icons.FILE_COPY,
                            on_click=lambda _, wp=template: self._open_add_working_paper_from_template_dialog(None, wp)
                        )
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=12,
                    bgcolor="white",
                    border_radius=8,
                    border=ft.border.all(1, "#e6e9ed")
                )
            )
        return controls

    def _build_findings_summary_controls(self):
        if not self.findings_data:
            return [ft.Text(f"No {self._term('finding_plural').lower()} captured for this assessment yet.", color="#7f8c8d")]

        controls = []
        for finding in self.findings_data:
            title = self._get_field(finding, "findingTitle", "FindingTitle", default="Untitled finding")
            severity = self._get_field(finding, "severityName", "SeverityName", default="Unspecified")
            status = self._get_field(finding, "statusName", "StatusName", default="Open")
            due_date = self._get_field(finding, "dueDate", "DueDate")
            description = self._get_field(finding, "findingDescription", "FindingDescription", default="No description provided.")
            finding_number = self._get_field(finding, "findingNumber", "FindingNumber", default="Draft")

            if isinstance(due_date, str) and "T" in due_date:
                due_date = due_date.split("T")[0]

            controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text(finding_number, size=12, color="#7f8c8d"),
                            ft.Container(expand=True),
                            ft.PopupMenuButton(
                                items=[
                                    ft.PopupMenuItem(
                                        text="Add Recommendation",
                                        icon=Icons.ADD_COMMENT,
                                        on_click=lambda _, f=finding: self._open_add_recommendation_dialog(f)
                                    ),
                                    ft.PopupMenuItem(
                                        text=f"Edit {self._term('finding_singular')}",
                                        icon=Icons.EDIT,
                                        on_click=lambda _, f=finding: self._open_edit_finding_dialog(f)
                                    ),
                                    ft.PopupMenuItem(
                                        text=f"Delete {self._term('finding_singular')}",
                                        icon=Icons.DELETE,
                                        on_click=lambda _, f=finding: self._delete_finding(f)
                                    )
                                ]
                            ),
                            ft.Container(
                                content=ft.Text(f"{severity} | {status}", size=11, color="white"),
                                bgcolor=self._get_finding_chip_color(severity, status),
                                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                border_radius=999
                            )
                        ]),
                        ft.Text(title, size=15, weight=ft.FontWeight.BOLD, color="#2c3e50"),
                        ft.Text(description, size=12, color="#5f6b7a"),
                        ft.Text(f"Due: {due_date or 'Not set'}", size=11, color="#7f8c8d")
                    ], spacing=6),
                    padding=12,
                    bgcolor="white",
                    border_radius=8,
                    border=ft.border.all(1, "#e6e9ed")
                )
            )
        return controls

    def _build_recommendations_summary_controls(self):
        if not self.recommendations_data:
            return [ft.Text(f"No {self._term('recommendation_plural').lower()} linked to {self._term('finding_plural').lower()} yet.", color="#7f8c8d")]

        controls = []
        for recommendation in self.recommendations_data:
            text = self._get_field(recommendation, "recommendation", "Recommendation", default="No recommendation text")
            status = self._get_field(recommendation, "statusName", "StatusName", default="Pending")
            responsible = self._get_field(recommendation, "responsiblePerson", "ResponsiblePerson", default="Not assigned")
            target_date = self._get_field(recommendation, "targetDate", "TargetDate")
            menu_items = []
            if can_manage_management_response(self.user, recommendation):
                menu_items.append(
                    ft.PopupMenuItem(
                        text="Update Management Response",
                        icon=Icons.REPLY,
                        on_click=lambda _, r=recommendation: self._open_management_response_dialog(r)
                    )
                )
            if self._is_internal_audit():
                menu_items.append(
                    ft.PopupMenuItem(
                        text="Create Management Action",
                        icon=Icons.TASK_ALT,
                        on_click=lambda _, r=recommendation: self._open_management_action_dialog(linked_recommendation=r)
                    )
                )
            menu_items.append(
                ft.PopupMenuItem(
                    text="Delete Recommendation",
                    icon=Icons.DELETE,
                    on_click=lambda _, r=recommendation: self._delete_recommendation(r)
                )
            )

            if isinstance(target_date, str) and "T" in target_date:
                target_date = target_date.split("T")[0]

            controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text(status, size=12, weight=ft.FontWeight.W_600, color="#2c3e50"),
                            ft.Container(expand=True),
                            ft.Text(f"Owner: {responsible}", size=11, color="#7f8c8d"),
                            ft.PopupMenuButton(items=menu_items) if menu_items else ft.Container()
                        ]),
                        ft.Text(text, size=13, color="#2c3e50"),
                        ft.Text(f"Target date: {target_date or 'Not set'}", size=11, color="#7f8c8d")
                    ], spacing=6),
                    padding=12,
                    bgcolor="white",
                    border_radius=8,
                    border=ft.border.all(1, "#e6e9ed")
                )
            )
        return controls

    def _build_management_response_summary(self):
        response_count = 0
        pending_count = 0
        for recommendation in self.recommendations_data:
            response = self._get_field(recommendation, "managementResponse", "ManagementResponse", default="")
            if response:
                response_count += 1
            else:
                pending_count += 1

        if not self.recommendations_data:
            return f"No {self._term('recommendation_plural').lower()} available yet, so no management responses are expected."

        return (
            f"Management responses captured: {response_count}. "
            f"Recommendations still awaiting response: {pending_count}."
        )

    def _count_open_management_actions(self):
        return sum(
            1 for action in self.management_actions_data
            if (self._get_field(action, "status", "Status", default="Open") or "").lower() not in {"closed", "validated", "complete", "completed"}
        )

    def _build_management_action_summary_cards(self):
        open_count = self._count_open_management_actions()
        overdue_count = sum(1 for action in self.management_actions_data if self._get_field(action, "isOverdue", "IsOverdue", default=False))
        validated_count = sum(
            1 for action in self.management_actions_data
            if (self._get_field(action, "status", "Status", default="Open") or "").lower() in {"validated", "closed", "complete", "completed"}
        )
        avg_progress = 0
        if self.management_actions_data:
            avg_progress = round(
                sum(int(self._get_field(action, "progressPercent", "ProgressPercent", default=0) or 0) for action in self.management_actions_data)
                / max(len(self.management_actions_data), 1)
            )
        return [
            self._create_control_status_card("Total", str(len(self.management_actions_data)), "#0f766e"),
            self._create_control_status_card("Open", str(open_count), "#2563eb"),
            self._create_control_status_card("Overdue", str(overdue_count), "#dc2626"),
            self._create_control_status_card("Validated", str(validated_count), "#16a34a"),
            self._create_control_status_card("Avg Progress", f"{avg_progress}%", "#7c3aed"),
        ]

    def _build_management_action_controls(self):
        controls = []
        for action in self.management_actions_data or []:
            due_date = self._get_field(action, "dueDate", "DueDate", default=None)
            if isinstance(due_date, str) and "T" in due_date:
                due_date = due_date.split("T")[0]

            status = self._get_field(action, "status", "Status", default="Open")
            status_color = "#16a34a" if status.lower() in {"validated", "closed", "complete", "completed"} else "#dc2626" if self._get_field(action, "isOverdue", "IsOverdue", default=False) else "#2563eb"
            linked_issue = self._get_field(action, "recommendationNumber", "RecommendationNumber", default="") or self._get_field(action, "findingNumber", "FindingNumber", default="Unlinked")
            linked_title = self._get_field(action, "recommendationText", "RecommendationText", default="") or self._get_field(action, "findingTitle", "FindingTitle", default="")

            controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text(self._get_field(action, "actionTitle", "ActionTitle", default="Management action"), size=15, weight=ft.FontWeight.BOLD, color="#2c3e50"),
                            ft.Container(expand=True),
                            ft.PopupMenuButton(
                                items=[
                                    ft.PopupMenuItem(
                                        text="Edit Action",
                                        icon=Icons.EDIT,
                                        on_click=lambda _, action_item=action: self._open_management_action_dialog(selected_action=action_item)
                                    ),
                                    ft.PopupMenuItem(
                                        text="Delete Action",
                                        icon=Icons.DELETE,
                                        on_click=lambda _, action_item=action: self._delete_management_action(action_item)
                                    )
                                ]
                            ),
                            ft.Container(
                                content=ft.Text(status, size=11, color="white"),
                                bgcolor=status_color,
                                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                border_radius=999
                            )
                        ]),
                        ft.Text(self._get_field(action, "actionDescription", "ActionDescription", default="No description provided."), size=12, color="#5f6b7a"),
                        ft.Text(f"Linked issue: {linked_issue}", size=11, color="#475569"),
                        ft.Text(linked_title, size=11, color="#64748b") if linked_title else ft.Container(),
                        ft.Row([
                            ft.Text(f"Owner: {self._get_field(action, 'ownerName', 'OwnerName', default='Unassigned')}", size=11, color="#7f8c8d"),
                            ft.Text(f"Due: {due_date or 'Not set'}", size=11, color="#7f8c8d"),
                            ft.Text(f"Progress: {self._get_field(action, 'progressPercent', 'ProgressPercent', default=0)}%", size=11, color="#7f8c8d"),
                        ], spacing=18),
                        ft.Text(
                            f"Response: {self._get_field(action, 'managementResponse', 'ManagementResponse', default='Not captured')}",
                            size=11,
                            color="#334155"
                        ),
                        ft.Text(
                            f"Validated by: {self._get_field(action, 'validatedByName', 'ValidatedByName', default='Not validated')}",
                            size=11,
                            color="#64748b"
                        )
                    ], spacing=6),
                    padding=12,
                    bgcolor="white",
                    border_radius=8,
                    border=ft.border.all(1, "#e6e9ed")
                )
            )
        return controls

    def _get_finding_chip_color(self, severity, status):
        severity = (severity or "").lower()
        status = (status or "").lower()
        if "critical" in severity:
            return "#b91c1c"
        if "high" in severity or "overdue" in status:
            return "#dc2626"
        if "medium" in severity:
            return "#d97706"
        if "closed" in status:
            return "#15803d"
        return "#2563eb"

    def _normalize_reference_id(self):
        if isinstance(self.reference_id, str) and self.reference_id.startswith("A-"):
            try:
                return int(self.reference_id[2:])
            except ValueError:
                return None
        return self.reference_id

    def _normalize_user_id(self):
        user_id = self.user.get("id") if isinstance(self.user, dict) else getattr(self.user, "id", None)
        try:
            return int(user_id) if user_id is not None and str(user_id).strip() else None
        except (TypeError, ValueError):
            return None

    def _get_current_user_name(self):
        if isinstance(self.user, dict):
            return self.user.get("name") or self.user.get("username") or self.user.get("email")
        return getattr(self.user, "name", None) or getattr(self.user, "username", None)

    def _get_assessor_name(self):
        return self._get_field(self.assessment_data, "Assessor", "assessor", default=None)

    def _comments_storage_key(self):
        return f"audit_comments_{self._normalize_reference_id()}"

    def _activity_storage_key(self):
        return f"audit_activity_{self._normalize_reference_id()}"

    def _workflow_storage_key(self):
        return f"audit_workflow_state_{self._normalize_reference_id()}"

    async def _load_collaboration_state(self):
        if not self.page or not hasattr(self.page, "client_storage"):
            return
        try:
            stored_comments = await self.page.client_storage.get_async(self._comments_storage_key())
            self.comments = json.loads(stored_comments) if stored_comments else []
        except Exception:
            self.comments = []
        try:
            stored_activity = await self.page.client_storage.get_async(self._activity_storage_key())
            self.activity_log = json.loads(stored_activity) if stored_activity else []
        except Exception:
            self.activity_log = []

    async def _persist_comments(self):
        if self.page and hasattr(self.page, "client_storage"):
            await self.page.client_storage.set_async(self._comments_storage_key(), json.dumps(self.comments))

    async def _persist_activity_log(self):
        if self.page and hasattr(self.page, "client_storage"):
            await self.page.client_storage.set_async(self._activity_storage_key(), json.dumps(self.activity_log))

    async def _save_comment(self, comment_text):
        text = (comment_text or "").strip()
        if not text:
            self._show_error("Comment text is required")
            return
        comment = {
            "id": len(self.comments) + 1,
            "user_id": self._normalize_user_id(),
            "user_name": self._get_current_user_name() or "Audit User",
            "text": text,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        self.comments.append(comment)
        await self._persist_comments()
        await self._append_activity_event("added a collaboration comment", "COMMENT", "#3498db")
        if hasattr(self, "comment_input") and self.comment_input:
            self.comment_input.value = ""
        self._build_ui()
        self.page.update()
        self._show_success("Comment saved")

    async def _append_activity_event(
        self,
        action,
        icon="INFO",
        color="#3498db",
        category="Business",
        entity_type="Assessment",
        entity_id=None,
        changes=None,
        details=None,
        source="Assessment"
    ):
        current_user_name = self._get_current_user_name() or "Audit User"
        recorded_event = None

        try:
            api_reference_id = self._normalize_reference_id()
            if api_reference_id:
                recorded_event = await self.assessment_controller.auditing_client.record_audit_trail_event({
                    "referenceId": api_reference_id,
                    "entityType": entity_type,
                    "entityId": str(entity_id if entity_id is not None else api_reference_id),
                    "category": category,
                    "action": action,
                    "summary": action[:1].upper() + action[1:] if action else "Audit event",
                    "performedByUserId": self._normalize_user_id(),
                    "performedByName": current_user_name,
                    "icon": icon,
                    "color": color,
                    "source": source,
                    "detailsJson": json.dumps(details) if details else None,
                    "changes": changes or []
                })
        except Exception:
            recorded_event = None

        if recorded_event:
            self.audit_trail_events = [recorded_event] + [event for event in self.audit_trail_events if self._get_field(event, "id", "Id") != self._get_field(recorded_event, "id", "Id")]
            self._update_audit_trail_dashboard_counts(recorded_event)
            return

        event = {
            "user": current_user_name,
            "action": action,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "icon": icon,
            "color": color
        }
        self.activity_log.append(event)
        await self._persist_activity_log()

    def _update_audit_trail_dashboard_counts(self, event):
        if not isinstance(self.audit_trail_dashboard, dict):
            self.audit_trail_dashboard = {
                "totalEvents": 0,
                "changeRecords": 0,
                "categories": [],
                "recentEvents": []
            }

        self.audit_trail_dashboard["totalEvents"] = int(self.audit_trail_dashboard.get("totalEvents", 0) or 0) + 1
        changes = self._get_field(event, "changes", "Changes", default=[]) or []
        self.audit_trail_dashboard["changeRecords"] = int(self.audit_trail_dashboard.get("changeRecords", 0) or 0) + len(changes)

        category_name = self._get_field(event, "category", "Category", default="Business") or "Business"
        categories = list(self.audit_trail_dashboard.get("categories", []))
        matched = False
        for category in categories:
            if (category.get("category") or "").lower() == category_name.lower():
                category["eventCount"] = int(category.get("eventCount", 0) or 0) + 1
                matched = True
                break
        if not matched:
            categories.append({"category": category_name, "eventCount": 1})
        self.audit_trail_dashboard["categories"] = categories

    async def _load_workflow_state(self):
        if not self.page or not hasattr(self.page, "client_storage"):
            self.workflow_state = {}
            return
        try:
            stored_state = await self.page.client_storage.get_async(self._workflow_storage_key())
            self.workflow_state = json.loads(stored_state) if stored_state else {}
        except Exception:
            self.workflow_state = {}

    async def _persist_workflow_state(self):
        if self.page and hasattr(self.page, "client_storage"):
            await self.page.client_storage.set_async(self._workflow_storage_key(), json.dumps(self.workflow_state))

    def _count_open_findings(self):
        return sum(
            1 for finding in self.findings_data
            if (self._get_field(finding, "statusName", "StatusName", default="Open") or "").lower() not in {"closed", "accepted"}
        )

    def _count_pending_management_responses(self):
        return sum(
            1 for recommendation in self.recommendations_data
            if not self._get_field(recommendation, "managementResponse", "ManagementResponse", default="")
        )

    def _count_open_evidence_requests(self):
        return sum(
            1 for request in self.evidence_requests_data
            if (self._get_field(request, "statusName", "StatusName", default="Sent") or "").lower() not in {"fulfilled", "closed", "cancelled"}
        )

    def _get_latest_workflow_instance(self):
        if not self.workflow_instances:
            return None
        return sorted(
            self.workflow_instances,
            key=lambda item: (
                str(self._get_field(item, "lastSyncedAt", "LastSyncedAt", default="") or ""),
                str(self._get_field(item, "startedAt", "StartedAt", default="") or ""),
                int(self._get_field(item, "id", "Id", default=0) or 0),
            ),
            reverse=True,
        )[0]

    def _derive_workflow_status(self):
        approved_by = self._get_field(self.assessment_data, "ApprovedBy", "approvedBy", default="") or ""
        latest_workflow = self._get_latest_workflow_instance()
        latest_workflow_status = self._get_field(latest_workflow, "status", "Status", default="") if latest_workflow else ""
        if latest_workflow_status:
            return latest_workflow_status
        if self.workflow_state.get("status"):
            return self.workflow_state["status"]
        if approved_by and self._count_open_findings() == 0 and self._count_pending_management_responses() == 0:
            return "Approved"
        if self._is_internal_audit() and self._count_open_management_actions() > 0:
            return "Action Tracking"
        if self._count_pending_management_responses() > 0:
            return "Awaiting Management Response"
        if self._count_open_findings() > 0:
            return "Findings Raised"
        if self.working_papers_data:
            incomplete_working_papers = sum(
                1 for paper in self.working_papers_data
                if (self._get_field(paper, "statusName", "StatusName", default="Draft") or "").lower() not in {"approved", "archived"}
            )
            if incomplete_working_papers > 0:
                return "Working Paper Preparation"
            return "Working Papers Approved"
        if self.walkthroughs_data:
            return "Walkthrough Execution"
        if self.procedures_data:
            incomplete_procedures = sum(
                1 for procedure in self.procedures_data
                if (self._get_field(procedure, "statusName", "StatusName", default="Planned") or "").lower() not in {"completed", "not applicable"}
            )
            if incomplete_procedures > 0:
                return "Procedure Execution"
            return "Procedures Completed"
        if self.risk_control_matrix_data:
            return "Risk and Control Matrix"
        if self._count_open_evidence_requests() > 0:
            return "Evidence Gathering"
        if self.documents_data:
            return "Evidence Collected"
        if self.scope_items_data:
            return "Scope Defined"
        if self.planning_data:
            return self._get_field(self.planning_data, "planningStatusName", "PlanningStatusName", default="Planning")
        if self.findings_data:
            return "Fieldwork Complete"
        if self._get_field(self.assessment_data, "RiskAssessments", default=[]):
            return "Assessment Prepared"
        return "In Progress"

    def _calculate_completion_percentage(self, risk_count, approved_by):
        pct = 0
        latest_workflow = self._get_latest_workflow_instance()
        if self.planning_data:
            pct += 8
        if self.scope_items_data:
            pct += 8
        if self.risk_control_matrix_data:
            pct += 8
        if self.walkthroughs_data:
            pct += 8
        if risk_count > 0:
            pct += 18
        if latest_workflow or self.workflow_state.get("workflowInstanceId"):
            pct += 12
        if self.documents_data:
            pct += 10
        if self.working_papers_data:
            pct += 10
        if self.procedures_data:
            pct += 10
        if self.findings_data:
            pct += 20
        if self.recommendations_data and self._count_pending_management_responses() == 0:
            pct += 15
        if self._is_internal_audit() and self.management_actions_data and self._count_open_management_actions() == 0:
            pct += 10
        if self._is_external_audit() and self._get_field(self.planning_data, "overallMateriality", "OverallMateriality", default=None) not in (None, "", 0, 0.0):
            pct += 10
        if approved_by and approved_by not in ("N/A", "Loading...", ""):
            pct += 15
        return min(pct, 100)

    def _build_timeline_data(self, approved_by):
        has_assessment = bool(self._get_field(self.assessment_data, "RiskAssessments", default=[]))
        latest_workflow = self._get_latest_workflow_instance()
        workflow_status = (
            self._get_field(latest_workflow, "status", "Status", default=None)
            or self.workflow_state.get("status", "Pending")
        )
        workflow_active = bool(latest_workflow or self.workflow_state.get("workflowInstanceId"))
        finding_title = f"{self._term('finding_plural')} Logged"
        action_title = "Management Actions" if self._is_internal_audit() else "Management Response"
        action_status = (
            f"{len(self.management_actions_data)} tracked"
            if self._is_internal_audit() and self.management_actions_data
            else f"{self._count_pending_management_responses()} pending"
            if not self._is_internal_audit() and self.recommendations_data
            else "Pending"
        )
        action_color = (
            "#0f766e"
            if self._is_internal_audit() and self.management_actions_data
            else "#3498db"
            if not self._is_internal_audit() and self.recommendations_data
            else "#95a5a6"
        )
        return [
            {"title": "Assessment Prepared", "status": "Completed" if has_assessment else "Pending", "color": "#2ecc71" if has_assessment else "#95a5a6"},
            {"title": "Planning", "status": self._get_field(self.planning_data, "planningStatusName", "PlanningStatusName", default="Pending"), "color": self._get_field(self.planning_data, "planningStatusColor", "PlanningStatusColor", default="#95a5a6") if self.planning_data else "#95a5a6"},
            {"title": "Scope", "status": f"{len(self.scope_items_data)} items" if self.scope_items_data else "Pending", "color": "#1d4ed8" if self.scope_items_data else "#95a5a6"},
            {"title": "Risk & Controls", "status": f"{len(self.risk_control_matrix_data)} entries" if self.risk_control_matrix_data else "Pending", "color": "#334155" if self.risk_control_matrix_data else "#95a5a6"},
            {"title": "Walkthroughs", "status": f"{len(self.walkthroughs_data)} recorded" if self.walkthroughs_data else "Pending", "color": "#7c3aed" if self.walkthroughs_data else "#95a5a6"},
            {"title": "Control Testing", "status": workflow_status, "color": "#f39c12" if workflow_active else "#95a5a6"},
            {"title": "Procedures", "status": f"{len(self.procedures_data)} recorded" if self.procedures_data else "Pending", "color": "#2563eb" if self.procedures_data else "#95a5a6"},
            {"title": "Working Papers", "status": f"{len(self.working_papers_data)} recorded" if self.working_papers_data else "Pending", "color": "#0f766e" if self.working_papers_data else "#95a5a6"},
            {"title": "Evidence", "status": f"{len(self.documents_data)} uploaded" if self.documents_data else "Pending", "color": "#7c3aed" if self.documents_data else "#95a5a6"},
            {"title": finding_title, "status": f"{len(self.findings_data)} recorded" if self.findings_data else "Pending", "color": "#3498db" if self.findings_data else "#95a5a6"},
            {"title": action_title, "status": action_status, "color": action_color},
            {"title": "Final Review", "status": "Approved" if approved_by and approved_by not in ("N/A", "Loading...", "") else "Pending Approval", "color": "#2ecc71" if approved_by and approved_by not in ("N/A", "Loading...", "") else "#95a5a6"},
        ]

    async def _refresh_finance_audit_workspace(self):
        reference_id = self._normalize_reference_id()
        if not reference_id:
            return

        try:
            self.finance_audit_workspace = await self.assessment_controller.auditing_client.get_finance_audit_workspace(reference_id)
            self._build_ui()
            if self.page:
                self.page.update()
        except Exception as ex:
            self._show_error(f"Unable to load finance reporting workspace: {str(ex)}")

    def _build_finance_reporting_tab(self):
        workspace = self.finance_audit_workspace or {}
        if not workspace:
            return ft.Container(
                padding=20,
                content=ft.Column([
                    ft.Text("Finance Reporting Workspace", size=20, weight=ft.FontWeight.BOLD, color="#2c3e50"),
                    ft.Text(
                        "Load the trial-balance mapping, draft financial statement, support-queue, and finalization workspace for this audit file.",
                        size=12,
                        color="#64748b"
                    ),
                    ft.ElevatedButton(
                        text="Load Finance Workspace",
                        icon=Icons.REFRESH,
                        bgcolor="#1d4ed8",
                        color="white",
                        on_click=lambda e: self.page.run_task(self._refresh_finance_audit_workspace)
                    )
                ], spacing=12)
            )

        summary_cards = [
            self._create_control_status_card("TB Accounts", str(self._get_field(workspace, "trialBalanceAccountCount", "TrialBalanceAccountCount", default=0)), "#1d4ed8"),
            self._create_control_status_card("Mapped", str(self._get_field(workspace, "mappingCount", "MappingCount", default=0)), "#0f766e"),
            self._create_control_status_card("Unmapped", str(self._get_field(workspace, "unmappedAccountCount", "UnmappedAccountCount", default=0)), "#dc2626"),
            self._create_control_status_card("Support Queue", str(self._get_field(workspace, "supportRequestCount", "SupportRequestCount", default=0)), "#7c3aed"),
            self._create_control_status_card("Open Requests", str(self._get_field(workspace, "openSupportRequestCount", "OpenSupportRequestCount", default=0)), "#f59e0b"),
            self._create_control_status_card("Draft Statements", str(len(self._get_field(workspace, "draftStatements", "DraftStatements", default=[]) or [])), "#2563eb"),
        ]

        action_row = ft.Row([
            ft.ElevatedButton(text="Refresh", icon=Icons.REFRESH, on_click=lambda e: self.page.run_task(self._refresh_finance_audit_workspace)),
            ft.ElevatedButton(text="Import GL / TB", icon=Icons.UPLOAD_FILE, on_click=self._open_materiality_calculator_dialog),
            ft.ElevatedButton(text="Auto-Map TB", icon=Icons.AUTO_FIX_HIGH, bgcolor="#1d4ed8", color="white", on_click=self._open_trial_balance_mapping_generation_dialog),
            ft.ElevatedButton(text="Save Profile", icon=Icons.BOOKMARK_ADD, bgcolor="#0f766e", color="white", on_click=self._open_save_mapping_profile_dialog),
            ft.ElevatedButton(text="Generate Draft FS", icon=Icons.REQUEST_PAGE, bgcolor="#7c3aed", color="white", on_click=self._open_generate_draft_statements_dialog),
            ft.ElevatedButton(text="Build Support Queue", icon=Icons.RULE, bgcolor="#f59e0b", color="white", on_click=self._open_generate_support_queue_dialog),
            ft.ElevatedButton(text="Finalization", icon=Icons.CHECKLIST_RTL, bgcolor="#334155", color="white", on_click=self._open_finance_finalization_dialog),
        ], wrap=True, spacing=10, run_spacing=10)

        return ft.Container(
            padding=20,
            content=ft.Column([
                ft.Row([
                    ft.Text("Finance Reporting Workspace", size=20, weight=ft.FontWeight.BOLD, color="#2c3e50"),
                    ft.Container(expand=True),
                    ft.Text(
                        f"Rule Package: {self._get_field(workspace, 'rulePackageName', 'RulePackageName', default='Finance Audit Core')}",
                        size=12,
                        color="#475569"
                    ),
                ]),
                ft.Text(
                    "Use this workspace to finish the finance-audit flow from trial-balance mapping through substantive support requests and release readiness.",
                    size=12,
                    color="#64748b"
                ),
                ft.Row(summary_cards, wrap=True, spacing=12, run_spacing=12),
                action_row,
                ft.Card(
                    content=ft.Container(
                        padding=16,
                        content=ft.Column([
                            ft.Text("Active Mapping Context", size=16, weight=ft.FontWeight.BOLD),
                            ft.ResponsiveRow([
                                ft.Container(col={"sm": 12, "md": 4}, content=self._create_info_row("Engagement", self._get_field(workspace, "engagementTitle", "EngagementTitle", default="Audit file"))),
                                ft.Container(col={"sm": 12, "md": 4}, content=self._create_info_row("Plan Year", str(self._get_field(workspace, "planYear", "PlanYear", default="Not captured")))),
                                ft.Container(col={"sm": 12, "md": 4}, content=self._create_info_row("Active Profile", self._get_field(workspace, "activeMappingProfileName", "ActiveMappingProfileName", default="No active profile"))),
                            ]),
                        ], spacing=10)
                    )
                ),
                self._build_finance_mapping_section(workspace),
                self._build_finance_draft_statement_section(workspace),
                self._build_finance_support_queue_section(workspace),
                self._build_finance_finalization_section(workspace),
            ], spacing=16, scroll=ft.ScrollMode.AUTO)
        )

    def _build_finance_mapping_section(self, workspace):
        mappings = self._get_field(workspace, "trialBalanceMappings", "TrialBalanceMappings", default=[]) or []
        visible_mappings = mappings[:25]

        if not visible_mappings:
            table_content = ft.Container(
                padding=20,
                content=ft.Text("No trial-balance mappings are available yet. Generate the mapping workspace first.", color="#64748b")
            )
        else:
            rows = []
            for mapping in visible_mappings:
                status_text = "Reviewed" if self._get_field(mapping, "isReviewed", "IsReviewed", default=False) else "Needs review"
                rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(self._get_field(mapping, "accountNumber", "AccountNumber", default="-"), size=12)),
                        ft.DataCell(ft.Text(self._get_field(mapping, "accountName", "AccountName", default="Unnamed account"), size=12)),
                        ft.DataCell(ft.Text(self._format_materiality_value(self._get_field(mapping, "currentBalance", "CurrentBalance", default=0)), size=12)),
                        ft.DataCell(ft.Text(self._get_field(mapping, "statementType", "StatementType", default="Unmapped"), size=12)),
                        ft.DataCell(ft.Text(self._get_field(mapping, "sectionName", "SectionName", default="-"), size=12)),
                        ft.DataCell(ft.Text(self._get_field(mapping, "lineName", "LineName", default="-"), size=12)),
                        ft.DataCell(ft.Text(status_text, size=12, color="#0f766e" if "Reviewed" in status_text else "#dc2626")),
                        ft.DataCell(ft.TextButton("Edit", icon=Icons.EDIT, on_click=lambda _, item=mapping: self._open_finance_mapping_edit_dialog(item))),
                    ])
                )
            table_content = ft.Row([
                ft.DataTable(
                    columns=[
                        ft.DataColumn(ft.Text("Account")),
                        ft.DataColumn(ft.Text("Name")),
                        ft.DataColumn(ft.Text("Balance")),
                        ft.DataColumn(ft.Text("Statement")),
                        ft.DataColumn(ft.Text("Section")),
                        ft.DataColumn(ft.Text("Line")),
                        ft.DataColumn(ft.Text("Status")),
                        ft.DataColumn(ft.Text("Action")),
                    ],
                    rows=rows,
                    border=ft.border.all(1, "#e2e8f0"),
                    border_radius=8,
                    data_row_min_height=50,
                    column_spacing=18,
                )
            ], scroll=ft.ScrollMode.AUTO)

        return ft.Card(
            content=ft.Container(
                padding=16,
                content=ft.Column([
                    ft.Row([
                        ft.Text("Trial Balance Mapping", size=16, weight=ft.FontWeight.BOLD),
                        ft.Container(expand=True),
                        ft.Text(f"Showing {min(len(mappings), 25)} of {len(mappings)} accounts", size=11, color="#64748b"),
                    ]),
                    table_content,
                ], spacing=12)
            )
        )

    def _build_finance_draft_statement_section(self, workspace):
        statements = self._get_field(workspace, "draftStatements", "DraftStatements", default=[]) or []
        if not statements:
            content = ft.Text("No draft financial statements generated yet.", color="#64748b")
        else:
            statement_cards = []
            for statement in statements:
                lines = self._get_field(statement, "lines", "Lines", default=[]) or []
                statement_cards.append(
                    ft.Container(
                        width=360,
                        padding=14,
                        bgcolor="#f8fafc",
                        border_radius=10,
                        border=ft.border.all(1, "#e2e8f0"),
                        content=ft.Column([
                            ft.Text(self._get_field(statement, "statementType", "StatementType", default="Statement"), size=15, weight=ft.FontWeight.BOLD),
                            ft.Text(
                                f"Total: {self._format_materiality_value(self._get_field(statement, 'totalAmount', 'TotalAmount', default=0))}",
                                size=12,
                                color="#0f766e"
                            ),
                            *[
                                ft.Row([
                                    ft.Text(self._get_field(line, "lineName", "LineName", default="Line"), size=11, expand=True),
                                    ft.Text(self._format_materiality_value(self._get_field(line, "amount", "Amount", default=0)), size=11, color="#334155"),
                                ])
                                for line in lines[:12]
                            ],
                        ], spacing=6)
                    )
                )
            content = ft.Row(statement_cards, wrap=True, spacing=12, run_spacing=12)

        return ft.Card(
            content=ft.Container(
                padding=16,
                content=ft.Column([
                    ft.Text("Draft Financial Statements", size=16, weight=ft.FontWeight.BOLD),
                    content,
                ], spacing=12)
            )
        )

    def _build_finance_support_queue_section(self, workspace):
        support_requests = self._get_field(workspace, "supportRequests", "SupportRequests", default=[]) or []
        if not support_requests:
            content = ft.Text("No substantive support requests have been generated yet.", color="#64748b")
        else:
            cards = []
            for request in support_requests[:20]:
                cards.append(
                    ft.Container(
                        width=340,
                        padding=14,
                        bgcolor="white",
                        border_radius=10,
                        border=ft.border.all(1, "#e2e8f0"),
                        content=ft.Column([
                            ft.Row([
                                ft.Text(self._get_field(request, "triageReason", "TriageReason", default="Support request"), size=13, weight=ft.FontWeight.BOLD, expand=True),
                                ft.Container(
                                    padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                    border_radius=12,
                                    bgcolor="#e2e8f0",
                                    content=ft.Text(self._get_field(request, "supportStatus", "SupportStatus", default="Requested"), size=10),
                                )
                            ]),
                            ft.Text(
                                f"{self._get_field(request, 'journalNumber', 'JournalNumber', default='Journal')} | {self._get_field(request, 'accountName', 'AccountName', default='Account')}",
                                size=11,
                                color="#475569"
                            ),
                            ft.Text(
                                self._format_materiality_value(self._get_field(request, "amount", "Amount", default=0)),
                                size=12,
                                color="#0f766e"
                            ),
                            ft.Text(self._get_field(request, "riskFlags", "RiskFlags", default=""), size=10, color="#7c3aed"),
                            ft.Text(self._get_field(request, "supportSummary", "SupportSummary", default="No support summary recorded."), size=11, color="#64748b"),
                            ft.TextButton("Manage Links", icon=Icons.LINK, on_click=lambda _, item=request: self._open_support_request_edit_dialog(item)),
                        ], spacing=6)
                    )
                )
            content = ft.Row(cards, wrap=True, spacing=12, run_spacing=12)

        return ft.Card(
            content=ft.Container(
                padding=16,
                content=ft.Column([
                    ft.Text("Substantive Support Queue", size=16, weight=ft.FontWeight.BOLD),
                    content,
                ], spacing=12)
            )
        )

    def _build_finance_finalization_section(self, workspace):
        finalization = self._get_field(workspace, "finalization", "Finalization", default={}) or {}
        return ft.Card(
            content=ft.Container(
                padding=16,
                content=ft.Column([
                    ft.Row([
                        ft.Text("Finance Finalization", size=16, weight=ft.FontWeight.BOLD),
                        ft.Container(expand=True),
                        ft.TextButton("Edit", icon=Icons.EDIT_NOTE, on_click=self._open_finance_finalization_dialog),
                    ]),
                    ft.ResponsiveRow([
                        ft.Container(col={"sm": 12, "md": 4}, content=self._create_info_row("Release Readiness", self._get_field(finalization, "releaseReadinessStatus", "ReleaseReadinessStatus", default="In Preparation"))),
                        ft.Container(col={"sm": 12, "md": 4}, content=self._create_info_row("Draft Status", self._get_field(finalization, "draftStatementStatus", "DraftStatementStatus", default="Not Generated"))),
                        ft.Container(col={"sm": 12, "md": 4}, content=self._create_info_row("Ready for Release", "Yes" if self._get_field(finalization, "readyForRelease", "ReadyForRelease", default=False) else "No")),
                    ]),
                    self._create_info_row("Conclusion", self._get_field(finalization, "overallConclusion", "OverallConclusion", default="Not captured")),
                    self._create_info_row("Recommendations", self._get_field(finalization, "recommendationSummary", "RecommendationSummary", default="Not captured")),
                    self._create_info_row("Outstanding Items", self._get_field(finalization, "outstandingItems", "OutstandingItems", default="None captured")),
                    self._create_info_row("Reviewer Notes", self._get_field(finalization, "reviewerNotes", "ReviewerNotes", default="Not captured")),
                ], spacing=10)
            )
        )

    def _open_trial_balance_mapping_generation_dialog(self, e=None):
        workspace = self.finance_audit_workspace or {}
        reference_id = self._normalize_reference_id()
        if not reference_id:
            self._show_error("Unable to determine the audit file reference.")
            return

        profiles = self._get_field(workspace, "mappingProfiles", "MappingProfiles", default=[]) or []
        latest_year = self._get_field(workspace, "latestTrialBalanceYear", "LatestTrialBalanceYear", default="")
        year_field = ft.TextField(label="Fiscal Year", value=str(latest_year or ""), width=180)
        profile_dropdown = ft.Dropdown(
            label="Mapping Profile",
            width=320,
            value=str(self._get_field(workspace, "activeMappingProfileId", "ActiveMappingProfileId", default="") or ""),
            options=[ft.dropdown.Option("", "Use active/default profile")] + [
                ft.dropdown.Option(str(self._get_field(profile, "id", "Id")), self._get_field(profile, "profileName", "ProfileName", default="Profile"))
                for profile in profiles
            ]
        )
        overwrite_checkbox = ft.Checkbox(label="Overwrite reviewed mappings", value=False)

        async def submit(_=None):
            try:
                await self.assessment_controller.auditing_client.generate_trial_balance_mappings({
                    "referenceId": reference_id,
                    "fiscalYear": int(year_field.value) if str(year_field.value).strip() else None,
                    "mappingProfileId": int(profile_dropdown.value) if str(profile_dropdown.value).strip() else None,
                    "overwriteReviewedMappings": bool(overwrite_checkbox.value),
                    "generatedByUserId": self._normalize_user_id(),
                    "generatedByName": self._get_current_user_name(),
                })
                self._close_active_dialog(dialog)
                self._show_success("Trial-balance mappings generated.")
                await self._refresh_finance_audit_workspace()
            except Exception as ex:
                self._show_error(f"Unable to generate mappings: {str(ex)}")

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Generate Trial-Balance Mappings"),
            content=ft.Column([year_field, profile_dropdown, overwrite_checkbox], tight=True, spacing=12),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: self._close_active_dialog(dialog)),
                ft.ElevatedButton("Generate", icon=Icons.AUTO_FIX_HIGH, on_click=lambda _: self.page.run_task(submit)),
            ],
        )
        self._open_dialog(dialog)

    def _open_finance_mapping_edit_dialog(self, mapping):
        reference_id = self._normalize_reference_id()
        if not reference_id:
            self._show_error("Unable to determine the audit file reference.")
            return

        statement_field = ft.Dropdown(
            label="Statement Type",
            width=220,
            value=self._get_field(mapping, "statementType", "StatementType", default="") or "",
            options=[
                ft.dropdown.Option("", "Unmapped"),
                ft.dropdown.Option("Income Statement"),
                ft.dropdown.Option("Balance Sheet"),
            ]
        )
        section_field = ft.TextField(label="Section", value=self._get_field(mapping, "sectionName", "SectionName", default=""), width=260)
        line_field = ft.TextField(label="Line", value=self._get_field(mapping, "lineName", "LineName", default=""), width=260)
        classification_field = ft.TextField(label="Classification", value=self._get_field(mapping, "classification", "Classification", default=""), width=220)
        notes_field = ft.TextField(label="Notes", value=self._get_field(mapping, "notes", "Notes", default=""), multiline=True, min_lines=2, max_lines=4)
        reviewed_checkbox = ft.Checkbox(label="Reviewed", value=self._get_field(mapping, "isReviewed", "IsReviewed", default=False))

        async def submit(_=None):
            try:
                await self.assessment_controller.auditing_client.save_trial_balance_mapping({
                    "id": self._get_field(mapping, "id", "Id", default=None),
                    "referenceId": reference_id,
                    "fiscalYear": self._get_field(mapping, "fiscalYear", "FiscalYear", default=0),
                    "mappingProfileId": self._get_field(mapping, "mappingProfileId", "MappingProfileId", default=None),
                    "accountNumber": self._get_field(mapping, "accountNumber", "AccountNumber", default=""),
                    "accountName": self._get_field(mapping, "accountName", "AccountName", default=""),
                    "fsli": self._get_field(mapping, "fsli", "Fsli", default=""),
                    "businessUnit": self._get_field(mapping, "businessUnit", "BusinessUnit", default=""),
                    "currentBalance": self._get_field(mapping, "currentBalance", "CurrentBalance", default=0),
                    "statementType": statement_field.value or None,
                    "sectionName": section_field.value or None,
                    "lineName": line_field.value or None,
                    "classification": classification_field.value or None,
                    "displayOrder": self._get_field(mapping, "displayOrder", "DisplayOrder", default=100),
                    "notes": notes_field.value or None,
                    "isAutoMapped": False,
                    "isReviewed": bool(reviewed_checkbox.value),
                })
                self._close_active_dialog(dialog)
                self._show_success("Mapping updated.")
                await self._refresh_finance_audit_workspace()
            except Exception as ex:
                self._show_error(f"Unable to save mapping: {str(ex)}")

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Edit Mapping: {self._get_field(mapping, 'accountNumber', 'AccountNumber', default='Account')}"),
            content=ft.Column([statement_field, section_field, line_field, classification_field, notes_field, reviewed_checkbox], tight=True, spacing=12, scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: self._close_active_dialog(dialog)),
                ft.ElevatedButton("Save", icon=Icons.SAVE, on_click=lambda _: self.page.run_task(submit)),
            ],
        )
        self._open_dialog(dialog)

    def _open_save_mapping_profile_dialog(self, e=None):
        workspace = self.finance_audit_workspace or {}
        reference_id = self._normalize_reference_id()
        if not reference_id:
            self._show_error("Unable to determine the audit file reference.")
            return

        profile_name_field = ft.TextField(label="Profile Name", hint_text="Finance mapping profile", autofocus=True)
        entity_type_field = ft.TextField(label="Entity Type", value="")
        industry_field = ft.TextField(label="Industry", value="")
        notes_field = ft.TextField(label="Notes", multiline=True, min_lines=2, max_lines=4)
        reusable_checkbox = ft.Checkbox(label="Make reusable for future audits", value=True)
        active_checkbox = ft.Checkbox(label="Set as active mapping profile", value=True)
        latest_year = self._get_field(workspace, "latestTrialBalanceYear", "LatestTrialBalanceYear", default="")
        year_field = ft.TextField(label="Fiscal Year", value=str(latest_year or ""), width=180)

        async def submit(_=None):
            try:
                await self.assessment_controller.auditing_client.save_mapping_profile_from_current({
                    "referenceId": reference_id,
                    "fiscalYear": int(year_field.value) if str(year_field.value).strip() else None,
                    "profileName": profile_name_field.value,
                    "entityType": entity_type_field.value or None,
                    "industryName": industry_field.value or None,
                    "notes": notes_field.value or None,
                    "isReusable": bool(reusable_checkbox.value),
                    "setAsActive": bool(active_checkbox.value),
                    "createdByUserId": self._normalize_user_id(),
                    "createdByName": self._get_current_user_name(),
                })
                self._close_active_dialog(dialog)
                self._show_success("Mapping profile saved.")
                await self._refresh_finance_audit_workspace()
            except Exception as ex:
                self._show_error(f"Unable to save mapping profile: {str(ex)}")

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Save Reusable Mapping Profile"),
            content=ft.Column([profile_name_field, year_field, entity_type_field, industry_field, notes_field, reusable_checkbox, active_checkbox], tight=True, spacing=12, scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: self._close_active_dialog(dialog)),
                ft.ElevatedButton("Save Profile", icon=Icons.BOOKMARK_ADD, on_click=lambda _: self.page.run_task(submit)),
            ],
        )
        self._open_dialog(dialog)

    def _open_generate_draft_statements_dialog(self, e=None):
        workspace = self.finance_audit_workspace or {}
        reference_id = self._normalize_reference_id()
        profiles = self._get_field(workspace, "mappingProfiles", "MappingProfiles", default=[]) or []
        latest_year = self._get_field(workspace, "latestTrialBalanceYear", "LatestTrialBalanceYear", default="")
        year_field = ft.TextField(label="Fiscal Year", value=str(latest_year or ""), width=180)
        profile_dropdown = ft.Dropdown(
            label="Mapping Profile",
            width=320,
            value=str(self._get_field(workspace, "activeMappingProfileId", "ActiveMappingProfileId", default="") or ""),
            options=[ft.dropdown.Option("", "Use active/default profile")] + [
                ft.dropdown.Option(str(self._get_field(profile, "id", "Id")), self._get_field(profile, "profileName", "ProfileName", default="Profile"))
                for profile in profiles
            ]
        )

        async def submit(_=None):
            try:
                await self.assessment_controller.auditing_client.generate_draft_financial_statements({
                    "referenceId": reference_id,
                    "fiscalYear": int(year_field.value) if str(year_field.value).strip() else None,
                    "mappingProfileId": int(profile_dropdown.value) if str(profile_dropdown.value).strip() else None,
                    "generatedByUserId": self._normalize_user_id(),
                    "generatedByName": self._get_current_user_name(),
                })
                self._close_active_dialog(dialog)
                self._show_success("Draft financial statements generated.")
                await self._refresh_finance_audit_workspace()
            except Exception as ex:
                self._show_error(f"Unable to generate draft financial statements: {str(ex)}")

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Generate Draft Financial Statements"),
            content=ft.Column([year_field, profile_dropdown], tight=True, spacing=12),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: self._close_active_dialog(dialog)),
                ft.ElevatedButton("Generate", icon=Icons.REQUEST_PAGE, on_click=lambda _: self.page.run_task(submit)),
            ],
        )
        self._open_dialog(dialog)

    def _open_generate_support_queue_dialog(self, e=None):
        workspace = self.finance_audit_workspace or {}
        reference_id = self._normalize_reference_id()
        latest_year = self._get_field(workspace, "latestJournalYear", "LatestJournalYear", default="")
        year_field = ft.TextField(label="Fiscal Year", value=str(latest_year or ""), width=180)
        include_materiality = ft.Checkbox(label="Include materiality selections", value=True)
        include_journal = ft.Checkbox(label="Include journal risk selections", value=True)
        include_revenue = ft.Checkbox(label="Include revenue-risk selections", value=True)

        async def submit(_=None):
            try:
                await self.assessment_controller.auditing_client.generate_support_queue({
                    "referenceId": reference_id,
                    "fiscalYear": int(year_field.value) if str(year_field.value).strip() else None,
                    "includeMaterialitySelections": bool(include_materiality.value),
                    "includeJournalRiskSelections": bool(include_journal.value),
                    "includeRevenueRiskSelections": bool(include_revenue.value),
                    "generatedByUserId": self._normalize_user_id(),
                    "generatedByName": self._get_current_user_name(),
                })
                self._close_active_dialog(dialog)
                self._show_success("Support queue generated.")
                await self._refresh_finance_audit_workspace()
            except Exception as ex:
                self._show_error(f"Unable to generate support queue: {str(ex)}")

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Generate Support Queue"),
            content=ft.Column([year_field, include_materiality, include_journal, include_revenue], tight=True, spacing=12),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: self._close_active_dialog(dialog)),
                ft.ElevatedButton("Generate", icon=Icons.RULE, on_click=lambda _: self.page.run_task(submit)),
            ],
        )
        self._open_dialog(dialog)

    def _open_support_request_edit_dialog(self, request):
        reference_id = self._normalize_reference_id()
        status_dropdown = ft.Dropdown(
            label="Support Status",
            width=220,
            value=self._get_field(request, "supportStatus", "SupportStatus", default="Requested"),
            options=[
                ft.dropdown.Option("Requested"),
                ft.dropdown.Option("In Review"),
                ft.dropdown.Option("Received"),
                ft.dropdown.Option("Cleared"),
                ft.dropdown.Option("Escalated"),
                ft.dropdown.Option("Unresolved"),
            ]
        )
        summary_field = ft.TextField(label="Support Summary", value=self._get_field(request, "supportSummary", "SupportSummary", default=""), multiline=True, min_lines=2, max_lines=4)
        notes_field = ft.TextField(label="Notes", value=self._get_field(request, "notes", "Notes", default=""), multiline=True, min_lines=2, max_lines=4)
        procedure_dropdown = ft.Dropdown(
            label="Linked Procedure",
            value=str(self._get_field(request, "linkedProcedureId", "LinkedProcedureId", default="") or ""),
            options=[ft.dropdown.Option("", "Not linked")] + [
                ft.dropdown.Option(str(self._get_field(item, "id", "Id")), self._get_field(item, "procedureTitle", "ProcedureTitle", default="Procedure"))
                for item in self.procedures_data
            ]
        )
        walkthrough_dropdown = ft.Dropdown(
            label="Linked Walkthrough",
            value=str(self._get_field(request, "linkedWalkthroughId", "LinkedWalkthroughId", default="") or ""),
            options=[ft.dropdown.Option("", "Not linked")] + [
                ft.dropdown.Option(str(self._get_field(item, "id", "Id")), self._get_field(item, "processName", "ProcessName", default="Walkthrough"))
                for item in self.walkthroughs_data
            ]
        )
        control_dropdown = ft.Dropdown(
            label="Linked Control",
            value=str(self._get_field(request, "linkedControlId", "LinkedControlId", default="") or ""),
            options=[ft.dropdown.Option("", "Not linked")] + [
                ft.dropdown.Option(str(self._get_field(item, "id", "Id")), self._get_field(item, "controlName", "ControlName", default="Control"))
                for item in self.risk_control_matrix_data
            ]
        )
        finding_dropdown = ft.Dropdown(
            label="Linked Finding",
            value=str(self._get_field(request, "linkedFindingId", "LinkedFindingId", default="") or ""),
            options=[ft.dropdown.Option("", "Not linked")] + [
                ft.dropdown.Option(str(self._get_field(item, "id", "Id")), self._get_field(item, "findingTitle", "FindingTitle", default="Finding"))
                for item in self.findings_data
            ]
        )

        async def submit(_=None):
            try:
                await self.assessment_controller.auditing_client.update_support_request({
                    "id": self._get_field(request, "id", "Id"),
                    "referenceId": reference_id,
                    "supportStatus": status_dropdown.value,
                    "supportSummary": summary_field.value or None,
                    "linkedProcedureId": int(procedure_dropdown.value) if str(procedure_dropdown.value).strip() else None,
                    "linkedWalkthroughId": int(walkthrough_dropdown.value) if str(walkthrough_dropdown.value).strip() else None,
                    "linkedControlId": int(control_dropdown.value) if str(control_dropdown.value).strip() else None,
                    "linkedFindingId": int(finding_dropdown.value) if str(finding_dropdown.value).strip() else None,
                    "notes": notes_field.value or None,
                })
                self._close_active_dialog(dialog)
                self._show_success("Support request updated.")
                await self._refresh_finance_audit_workspace()
            except Exception as ex:
                self._show_error(f"Unable to update support request: {str(ex)}")

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Manage Support Request Links"),
            content=ft.Column([status_dropdown, summary_field, procedure_dropdown, walkthrough_dropdown, control_dropdown, finding_dropdown, notes_field], tight=True, spacing=12, scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: self._close_active_dialog(dialog)),
                ft.ElevatedButton("Save", icon=Icons.SAVE, on_click=lambda _: self.page.run_task(submit)),
            ],
        )
        self._open_dialog(dialog)

    def _open_finance_finalization_dialog(self, e=None):
        workspace = self.finance_audit_workspace or {}
        finalization = self._get_field(workspace, "finalization", "Finalization", default={}) or {}
        reference_id = self._normalize_reference_id()

        release_dropdown = ft.Dropdown(
            label="Release Readiness",
            value=self._get_field(finalization, "releaseReadinessStatus", "ReleaseReadinessStatus", default="In Preparation"),
            options=[
                ft.dropdown.Option("In Preparation"),
                ft.dropdown.Option("Pending Review"),
                ft.dropdown.Option("Ready for Release"),
                ft.dropdown.Option("Blocked"),
            ]
        )
        draft_dropdown = ft.Dropdown(
            label="Draft Statement Status",
            value=self._get_field(finalization, "draftStatementStatus", "DraftStatementStatus", default="Not Generated"),
            options=[
                ft.dropdown.Option("Not Generated"),
                ft.dropdown.Option("Generated"),
                ft.dropdown.Option("Reviewed"),
                ft.dropdown.Option("Finalized"),
            ]
        )
        conclusion_field = ft.TextField(label="Overall Conclusion", value=self._get_field(finalization, "overallConclusion", "OverallConclusion", default=""), multiline=True, min_lines=2, max_lines=4)
        recommendation_field = ft.TextField(label="Recommendation Summary", value=self._get_field(finalization, "recommendationSummary", "RecommendationSummary", default=""), multiline=True, min_lines=2, max_lines=4)
        outstanding_field = ft.TextField(label="Outstanding Items", value=self._get_field(finalization, "outstandingItems", "OutstandingItems", default=""), multiline=True, min_lines=2, max_lines=4)
        reviewer_notes_field = ft.TextField(label="Reviewer Notes", value=self._get_field(finalization, "reviewerNotes", "ReviewerNotes", default=""), multiline=True, min_lines=2, max_lines=4)
        ready_checkbox = ft.Checkbox(label="Ready for release", value=self._get_field(finalization, "readyForRelease", "ReadyForRelease", default=False))

        async def submit(_=None):
            try:
                await self.assessment_controller.auditing_client.upsert_finance_finalization({
                    "referenceId": reference_id,
                    "activeMappingProfileId": self._get_field(finalization, "activeMappingProfileId", "ActiveMappingProfileId", default=None),
                    "activeRulePackageId": self._get_field(finalization, "activeRulePackageId", "ActiveRulePackageId", default=None),
                    "overallConclusion": conclusion_field.value or None,
                    "recommendationSummary": recommendation_field.value or None,
                    "releaseReadinessStatus": release_dropdown.value,
                    "draftStatementStatus": draft_dropdown.value,
                    "outstandingItems": outstanding_field.value or None,
                    "reviewerNotes": reviewer_notes_field.value or None,
                    "readyForRelease": bool(ready_checkbox.value),
                    "updatedByUserId": self._normalize_user_id(),
                    "updatedByName": self._get_current_user_name(),
                })
                self._close_active_dialog(dialog)
                self._show_success("Finance finalization saved.")
                await self._refresh_finance_audit_workspace()
            except Exception as ex:
                self._show_error(f"Unable to save finalization: {str(ex)}")

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Finance Finalization"),
            content=ft.Column([release_dropdown, draft_dropdown, conclusion_field, recommendation_field, outstanding_field, reviewer_notes_field, ready_checkbox], tight=True, spacing=12, scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: self._close_active_dialog(dialog)),
                ft.ElevatedButton("Save", icon=Icons.SAVE, on_click=lambda _: self.page.run_task(submit)),
            ],
        )
        self._open_dialog(dialog)
    
    # Event handlers
    def _on_tab_change(self, e):
        """Handle tab change"""
        self.current_tab = e.control.selected_index
        if self.current_tab == self.finance_tab_index and self.finance_audit_workspace is None:
            self.page.run_task(self._refresh_finance_audit_workspace)
    
    def _update_ui_with_data(self):
        """Update UI with loaded assessment data"""
        if not self.assessment_data:
            return
        
        try:
            # Update the header title with assessment info
            if hasattr(self.assessment_data, 'Client') or (isinstance(self.assessment_data, dict) and self.assessment_data.get('Client')):
                client_name = self.assessment_data.get('Client') if isinstance(self.assessment_data, dict) else self.assessment_data.Client
                if hasattr(self, "header_title") and self.header_title:
                    self.header_title.value = f"Audit File: {client_name}"
            
            self.workflow_status = self._derive_workflow_status()
            
            # Rebuild UI with loaded data
            self._build_ui()
            
            # Update status bar and other components with real data
            if hasattr(self, 'page') and self.page:
                self.page.update()
                
        except Exception as e:
            print(f"Error updating UI with data: {str(e)}")
            self._show_error(f"Error displaying assessment data: {str(e)}")
    
    # Action handlers
    def _handle_back(self, e):
        """Handle back navigation"""
        if self.on_back_callback:
            self.on_back_callback()
    
    def _edit_assessment(self, e):
        """Edit assessment"""
        if self.on_edit_callback:
            self.on_edit_callback(self.reference_id)
    
    async def _start_control_testing(self, e):
        """Start control testing workflow"""
        if not can_start_workflows(self.user):
            self._show_error("You do not have permission to start control testing workflows.")
            return
        try:
            # Call API to start control testing
            result = await self.assessment_controller.start_control_testing(
                self._normalize_reference_id(),
                {
                    "controlId": "CTRL-001",
                    "testerId": str(self._normalize_user_id() or 1),
                    "testFrequency": "Monthly"
                }
            )
            
            if result:
                workflow_instance_id = result.get("WorkflowInstanceId") if isinstance(result, dict) else None
                workflow_record = result.get("Workflow") if isinstance(result, dict) else None
                if workflow_record:
                    self.workflow_instances = [
                        workflow_record,
                        *[item for item in self.workflow_instances if self._get_field(item, "workflowInstanceId", "WorkflowInstanceId") != workflow_instance_id]
                    ]
                self.workflow_state = {
                    "status": self._get_field(workflow_record, "status", "Status", default="Control Testing In Progress"),
                    "workflowInstanceId": workflow_instance_id,
                    "updatedAt": datetime.now().strftime("%Y-%m-%d %H:%M")
                }
                await self._persist_workflow_state()
                await self._append_activity_event("started control testing workflow", "PLAY_ARROW", "#f39c12")
                self._show_success("Control testing workflow started successfully")
                self.page.run_task(self._load_assessment_data)
            else:
                self._show_error("Failed to start control testing")
                
        except Exception as e:
            self._show_error(f"Error starting control testing: {str(e)}")
    
    def _export_assessment(self, format_type):
        """Export assessment to specified format"""
        try:
            data, headers, metadata = self._prepare_export_payload()
            title = f"Audit Assessment {self._normalize_reference_id() or ''}".strip()
            if format_type == "excel":
                result = self.export_manager.export_excel(data, headers, title, "audit_assessment", metadata=metadata)
            elif format_type == "pdf":
                result = self.export_manager.export_pdf(data, headers, title, "audit_assessment", metadata=metadata)
            else:
                result = self.export_manager.export_csv(data, headers, "audit_assessment", metadata=metadata)

            if result and result.get("data_uri"):
                self.page.launch_url(result["data_uri"])
                self._show_success(f"{format_type.upper()} export started")
        except Exception as e:
            self._show_error(f"Export failed: {str(e)}")
    
    def _share_assessment(self, e):
        """Share assessment with team members"""
        # Implementation for sharing
        self._show_info("Sharing functionality to be implemented")
    
    def _archive_assessment(self, e):
        """Archive assessment"""
        reference_id = self._normalize_reference_id()
        if not reference_id:
            self._show_error("Unable to determine the assessment reference ID.")
            return

        reason_field = ft.TextField(
            label="Archive Reason",
            multiline=True,
            min_lines=3,
            max_lines=5,
            hint_text="Explain why this audit file is being archived."
        )

        async def confirm_archive():
            try:
                result = await self.assessment_controller.auditing_client.archive_assessment(reference_id, {
                    "reason": reason_field.value.strip() if reason_field.value else "Archived from assessment details"
                })
                try:
                    await self.assessment_controller.auditing_client.record_usage_event({
                        "moduleName": "assessments",
                        "featureName": "archive_assessment",
                        "eventName": "archive_completed",
                        "referenceId": reference_id,
                        "source": "modern-details",
                        "metadataJson": json.dumps({
                            "success": result.get("success", True),
                            "alreadyArchived": result.get("alreadyArchived", False)
                        })
                    })
                except Exception as usage_ex:
                    print(f"Failed to record archive usage event: {usage_ex}")
                self._close_active_dialog(self.archive_assessment_dialog)
                self._show_success(result.get("message", "Assessment archived successfully."))
                self.page.run_task(self._load_assessment_data)
            except Exception as ex:
                self._show_error(f"Failed to archive assessment: {str(ex)}")

        self.archive_assessment_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Archive Audit File"),
            content=ft.Column([reason_field], tight=True, width=520),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: self._close_active_dialog(self.archive_assessment_dialog)),
                ft.FilledButton(
                    "Archive",
                    style=ft.ButtonStyle(bgcolor="#b45309", color="white"),
                    on_click=lambda _: self.page.run_task(confirm_archive)
                ),
            ],
        )
        self._open_dialog(self.archive_assessment_dialog)

    def _add_working_paper(self, e):
        """Open dialog to create a working paper"""
        title_field = ft.TextField(label="Working Paper Title", autofocus=True)
        objective_field = ft.TextField(label="Objective", multiline=True, min_lines=2, max_lines=4)
        description_field = ft.TextField(label="Description", multiline=True, min_lines=2, max_lines=4)
        conclusion_field = ft.TextField(label="Conclusion", multiline=True, min_lines=2, max_lines=4)
        notes_field = ft.TextField(label="Notes", multiline=True, min_lines=2, max_lines=4)
        prepared_by_field = ft.TextField(label="Prepared By", value=self._get_current_user_name() or "")
        reviewer_field = ft.TextField(label="Reviewer")
        prepared_date_field = ft.TextField(label="Prepared Date (YYYY-MM-DD)")

        procedure_dropdown = ft.Dropdown(
            label="Linked Procedure",
            options=[
                ft.dropdown.Option(
                    key=str(self._get_field(item, "id", "Id")),
                    text=self._get_field(item, "procedureTitle", "ProcedureTitle", default="Procedure")
                )
                for item in self.procedures_data or []
            ]
        )
        status_dropdown = ft.Dropdown(
            label="Status",
            options=[
                ft.dropdown.Option(
                    key=str(self._get_field(item, "id", "Id")),
                    text=self._get_field(item, "name", "Name", default="Status")
                )
                for item in self.working_paper_statuses or []
            ],
            value=str(self._get_field(self.working_paper_statuses[0], "id", "Id")) if self.working_paper_statuses else None
        )

        async def save_working_paper():
            payload = {
                "referenceId": self._normalize_reference_id(),
                "auditUniverseId": None,
                "procedureId": int(procedure_dropdown.value) if procedure_dropdown.value else None,
                "title": title_field.value.strip() if title_field.value else "",
                "objective": objective_field.value.strip() if objective_field.value else "",
                "description": description_field.value.strip() if description_field.value else "",
                "statusId": int(status_dropdown.value) if status_dropdown.value else None,
                "preparedBy": prepared_by_field.value.strip() if prepared_by_field.value else "",
                "preparedByUserId": self._normalize_user_id(),
                "reviewerName": reviewer_field.value.strip() if reviewer_field.value else "",
                "reviewerUserId": None,
                "conclusion": conclusion_field.value.strip() if conclusion_field.value else "",
                "notes": notes_field.value.strip() if notes_field.value else "",
                "preparedDate": prepared_date_field.value.strip() if prepared_date_field.value else None,
                "reviewedDate": None,
                "isTemplate": False
            }

            if not payload["title"]:
                self._show_error("Working paper title is required")
                return

            try:
                self._show_loading("Creating working paper...")
                await self.assessment_controller.auditing_client.create_working_paper(payload)
                self._hide_loading()
                self._close_active_dialog(self.working_paper_dialog)
                await self._append_activity_event("created a working paper", "DESCRIPTION", "#0f766e")
                self._show_success("Working paper created successfully")
                self.page.run_task(self._load_assessment_data)
            except Exception as ex:
                self._hide_loading()
                self._show_error(f"Failed to create working paper: {str(ex)}")

        self.working_paper_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Add Working Paper"),
            content=ft.Column([
                title_field,
                objective_field,
                description_field,
                procedure_dropdown,
                status_dropdown,
                prepared_by_field,
                reviewer_field,
                prepared_date_field,
                conclusion_field,
                notes_field
            ], tight=True, width=560, scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: self._close_active_dialog(self.working_paper_dialog)),
                ft.FilledButton("Save", on_click=lambda _: self.page.run_task(save_working_paper))
            ]
        )
        self._open_dialog(self.working_paper_dialog)

    def _open_add_working_paper_from_template_dialog(self, e=None, selected_template=None):
        """Create a working paper from a template"""
        filtered_templates = self._get_filtered_working_paper_templates()
        template_dropdown = ft.Dropdown(
            label="Template",
            options=[
                ft.dropdown.Option(
                    key=str(self._get_field(item, "id", "Id")),
                    text=self._get_field(item, "title", "Title", default="Template")
                )
                for item in filtered_templates
            ],
            value=str(self._get_field(selected_template, "id", "Id")) if selected_template else None
        )
        procedure_dropdown = ft.Dropdown(
            label="Linked Procedure",
            options=[
                ft.dropdown.Option(
                    key=str(self._get_field(item, "id", "Id")),
                    text=self._get_field(item, "procedureTitle", "ProcedureTitle", default="Procedure")
                )
                for item in self.procedures_data or []
            ]
        )
        prepared_by_field = ft.TextField(label="Prepared By", value=self._get_current_user_name() or "")

        async def create_from_template():
            payload = {
                "templateId": int(template_dropdown.value) if template_dropdown.value else None,
                "referenceId": self._normalize_reference_id(),
                "auditUniverseId": None,
                "procedureId": int(procedure_dropdown.value) if procedure_dropdown.value else None,
                "preparedBy": prepared_by_field.value.strip() if prepared_by_field.value else "",
                "preparedByUserId": self._normalize_user_id()
            }

            if not payload["templateId"] or not payload["referenceId"]:
                self._show_error("Template and assessment reference are required")
                return

            try:
                self._show_loading("Creating working paper from template...")
                await self.assessment_controller.auditing_client.create_working_paper_from_template(payload)
                self._hide_loading()
                self._close_active_dialog(self.working_paper_template_dialog)
                await self._append_activity_event("added a working paper from a template", "FILE_COPY", "#0f766e")
                self._show_success("Working paper created from template")
                self.page.run_task(self._load_assessment_data)
            except Exception as ex:
                self._hide_loading()
                self._show_error(f"Failed to use working paper template: {str(ex)}")

        self.working_paper_template_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Use Working Paper Template"),
            content=ft.Column([
                template_dropdown,
                procedure_dropdown,
                prepared_by_field
            ], tight=True, width=560),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: self._close_active_dialog(self.working_paper_template_dialog)),
                ft.FilledButton("Create", on_click=lambda _: self.page.run_task(create_from_template))
            ]
        )
        self._open_dialog(self.working_paper_template_dialog)

    def _open_edit_working_paper_dialog(self, paper):
        """Open dialog to edit a working paper"""
        prepared_date = self._get_field(paper, "preparedDate", "PreparedDate")
        reviewed_date = self._get_field(paper, "reviewedDate", "ReviewedDate")
        if isinstance(prepared_date, str) and "T" in prepared_date:
            prepared_date = prepared_date.split("T")[0]
        if isinstance(reviewed_date, str) and "T" in reviewed_date:
            reviewed_date = reviewed_date.split("T")[0]

        title_field = ft.TextField(label="Working Paper Title", value=self._get_field(paper, "title", "Title", default=""))
        objective_field = ft.TextField(
            label="Objective",
            multiline=True,
            min_lines=2,
            max_lines=4,
            value=self._get_field(paper, "objective", "Objective", default="")
        )
        description_field = ft.TextField(
            label="Description",
            multiline=True,
            min_lines=2,
            max_lines=4,
            value=self._get_field(paper, "description", "Description", default="")
        )
        prepared_by_field = ft.TextField(label="Prepared By", value=self._get_field(paper, "preparedBy", "PreparedBy", default=""))
        reviewer_field = ft.TextField(label="Reviewer", value=self._get_field(paper, "reviewerName", "ReviewerName", default=""))
        conclusion_field = ft.TextField(
            label="Conclusion",
            multiline=True,
            min_lines=2,
            max_lines=4,
            value=self._get_field(paper, "conclusion", "Conclusion", default="")
        )
        notes_field = ft.TextField(
            label="Notes",
            multiline=True,
            min_lines=2,
            max_lines=4,
            value=self._get_field(paper, "notes", "Notes", default="")
        )
        prepared_date_field = ft.TextField(label="Prepared Date (YYYY-MM-DD)", value=prepared_date or "")
        reviewed_date_field = ft.TextField(label="Reviewed Date (YYYY-MM-DD)", value=reviewed_date or "")

        procedure_dropdown = ft.Dropdown(
            label="Linked Procedure",
            options=[
                ft.dropdown.Option(
                    key=str(self._get_field(item, "id", "Id")),
                    text=self._get_field(item, "procedureTitle", "ProcedureTitle", default="Procedure")
                )
                for item in self.procedures_data or []
            ],
            value=str(self._get_field(paper, "procedureId", "ProcedureId")) if self._get_field(paper, "procedureId", "ProcedureId") else None
        )
        status_dropdown = ft.Dropdown(
            label="Status",
            options=[
                ft.dropdown.Option(
                    key=str(self._get_field(item, "id", "Id")),
                    text=self._get_field(item, "name", "Name", default="Status")
                )
                for item in self.working_paper_statuses or []
            ],
            value=str(self._get_field(paper, "statusId", "StatusId")) if self._get_field(paper, "statusId", "StatusId") else None
        )

        async def save_changes():
            payload = {
                "id": self._get_field(paper, "id", "Id"),
                "procedureId": int(procedure_dropdown.value) if procedure_dropdown.value else None,
                "title": title_field.value.strip() if title_field.value else "",
                "objective": objective_field.value.strip() if objective_field.value else "",
                "description": description_field.value.strip() if description_field.value else "",
                "statusId": int(status_dropdown.value) if status_dropdown.value else None,
                "preparedBy": prepared_by_field.value.strip() if prepared_by_field.value else "",
                "preparedByUserId": self._normalize_user_id(),
                "reviewerName": reviewer_field.value.strip() if reviewer_field.value else "",
                "reviewerUserId": None,
                "conclusion": conclusion_field.value.strip() if conclusion_field.value else "",
                "notes": notes_field.value.strip() if notes_field.value else "",
                "preparedDate": prepared_date_field.value.strip() if prepared_date_field.value else None,
                "reviewedDate": reviewed_date_field.value.strip() if reviewed_date_field.value else None,
                "isActive": True
            }

            if not payload["id"] or not payload["title"]:
                self._show_error("Working paper ID and title are required")
                return

            try:
                self._show_loading("Updating working paper...")
                await self.assessment_controller.auditing_client.update_working_paper(payload["id"], payload)
                self._hide_loading()
                self._close_active_dialog(self.edit_working_paper_dialog)
                await self._append_activity_event("updated a working paper", "EDIT", "#0f766e")
                self._show_success("Working paper updated successfully")
                self.page.run_task(self._load_assessment_data)
            except Exception as ex:
                self._hide_loading()
                self._show_error(f"Failed to update working paper: {str(ex)}")

        self.edit_working_paper_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Edit Working Paper"),
            content=ft.Column([
                title_field,
                objective_field,
                description_field,
                procedure_dropdown,
                status_dropdown,
                prepared_by_field,
                reviewer_field,
                prepared_date_field,
                reviewed_date_field,
                conclusion_field,
                notes_field
            ], tight=True, width=560, scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: self._close_active_dialog(self.edit_working_paper_dialog)),
                ft.FilledButton("Save", on_click=lambda _: self.page.run_task(save_changes))
            ]
        )
        self._open_dialog(self.edit_working_paper_dialog)

    def _open_working_paper_signoff_dialog(self, paper):
        """Open dialog to add and view sign-offs for a working paper"""
        history_column = ft.Column([ft.Text("Loading sign-off history...", color="#7f8c8d")], spacing=8, scroll=ft.ScrollMode.AUTO)
        action_dropdown = ft.Dropdown(
            label="Sign-off Action",
            options=[
                ft.dropdown.Option(key="Prepared", text="Prepared"),
                ft.dropdown.Option(key="Reviewed", text="Reviewed"),
                ft.dropdown.Option(key="Approved", text="Approved"),
            ],
            value="Reviewed"
        )
        comment_field = ft.TextField(label="Comment", multiline=True, min_lines=2, max_lines=4)

        async def load_signoffs():
            try:
                signoffs = await self.assessment_controller.auditing_client.get_working_paper_signoffs(
                    self._get_field(paper, "id", "Id")
                )
                if not signoffs:
                    history_column.controls = [ft.Text("No sign-off history recorded yet.", color="#7f8c8d")]
                else:
                    items = []
                    for signoff in signoffs:
                        signed_at = self._get_field(signoff, "signedAt", "SignedAt", default="")
                        if isinstance(signed_at, str) and "T" in signed_at:
                            signed_at = signed_at.replace("T", " ")[:16]
                        items.append(
                            ft.Container(
                                content=ft.Column([
                                    ft.Row([
                                        ft.Text(self._get_field(signoff, "actionType", "ActionType", default="Sign-off"), weight=ft.FontWeight.BOLD),
                                        ft.Container(expand=True),
                                        ft.Text(signed_at, size=11, color="#7f8c8d")
                                    ]),
                                    ft.Text(self._get_field(signoff, "signedByName", "SignedByName", default="Unknown"), size=12),
                                    ft.Text(self._get_field(signoff, "comment", "Comment", default=""), size=11, color="#5f6b7a")
                                ], spacing=3),
                                padding=10,
                                bgcolor="white",
                                border_radius=8,
                                border=ft.border.all(1, "#e6e9ed")
                            )
                        )
                    history_column.controls = items
                self.page.update()
            except Exception as ex:
                history_column.controls = [ft.Text(f"Failed to load history: {str(ex)}", color="#dc2626")]
                self.page.update()

        async def save_signoff():
            payload = {
                "workingPaperId": self._get_field(paper, "id", "Id"),
                "actionType": action_dropdown.value,
                "signedByUserId": self._normalize_user_id(),
                "signedByName": self._get_current_user_name() or "Audit User",
                "comment": comment_field.value.strip() if comment_field.value else ""
            }

            if not payload["workingPaperId"] or not payload["actionType"]:
                self._show_error("Working paper and sign-off action are required")
                return

            try:
                self._show_loading("Saving sign-off...")
                await self.assessment_controller.auditing_client.add_working_paper_signoff(payload)
                self._hide_loading()
                self._close_active_dialog(self.working_paper_signoff_dialog)
                await self._append_activity_event("added a working paper sign-off", "CHECK_CIRCLE", "#16a34a")
                self._show_success("Working paper sign-off saved")
                self.page.run_task(self._load_assessment_data)
            except Exception as ex:
                self._hide_loading()
                self._show_error(f"Failed to save sign-off: {str(ex)}")

        self.working_paper_signoff_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Working Paper Sign-off"),
            content=ft.Column([
                ft.Text(self._get_field(paper, "title", "Title", default="Working paper"), size=12, color="#7f8c8d"),
                action_dropdown,
                comment_field,
                ft.Text("History", weight=ft.FontWeight.BOLD),
                history_column
            ], tight=True, width=560, height=420),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: self._close_active_dialog(self.working_paper_signoff_dialog)),
                ft.FilledButton("Save", on_click=lambda _: self.page.run_task(save_signoff))
            ]
        )
        self._open_dialog(self.working_paper_signoff_dialog)
        self.page.run_task(load_signoffs)

    def _open_working_paper_reference_dialog(self, paper):
        """Open dialog to create a cross-reference between working papers"""
        reference_dropdown = ft.Dropdown(
            label="Reference Target",
            options=[
                ft.dropdown.Option(
                    key=str(self._get_field(item, "id", "Id")),
                    text=f"{self._get_field(item, 'workingPaperCode', 'WorkingPaperCode', default='WP')} - {self._get_field(item, 'title', 'Title', default='Working paper')}"
                )
                for item in self.working_papers_data or []
                if self._get_field(item, "id", "Id") != self._get_field(paper, "id", "Id")
            ]
        )
        reference_type_dropdown = ft.Dropdown(
            label="Reference Type",
            options=[
                ft.dropdown.Option(key="Supporting", text="Supporting"),
                ft.dropdown.Option(key="Lead Schedule", text="Lead Schedule"),
                ft.dropdown.Option(key="Related Testing", text="Related Testing"),
            ],
            value="Supporting"
        )
        notes_field = ft.TextField(label="Notes", multiline=True, min_lines=2, max_lines=4)

        async def save_reference():
            payload = {
                "fromWorkingPaperId": self._get_field(paper, "id", "Id"),
                "toWorkingPaperId": int(reference_dropdown.value) if reference_dropdown.value else None,
                "referenceType": reference_type_dropdown.value,
                "notes": notes_field.value.strip() if notes_field.value else ""
            }

            if not payload["fromWorkingPaperId"] or not payload["toWorkingPaperId"]:
                self._show_error("Select a working paper to reference")
                return

            try:
                self._show_loading("Creating cross-reference...")
                await self.assessment_controller.auditing_client.add_working_paper_reference(payload)
                self._hide_loading()
                self._close_active_dialog(self.working_paper_reference_dialog)
                await self._append_activity_event("linked a working paper cross-reference", "LINK", "#2563eb")
                self._show_success("Cross-reference saved")
                self.page.run_task(self._load_assessment_data)
            except Exception as ex:
                self._hide_loading()
                self._show_error(f"Failed to save cross-reference: {str(ex)}")

        self.working_paper_reference_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Link Cross-reference"),
            content=ft.Column([
                ft.Text(self._get_field(paper, "title", "Title", default="Working paper"), size=12, color="#7f8c8d"),
                reference_dropdown,
                reference_type_dropdown,
                notes_field
            ], tight=True, width=540),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: self._close_active_dialog(self.working_paper_reference_dialog)),
                ft.FilledButton("Save", on_click=lambda _: self.page.run_task(save_reference))
            ]
        )
        self._open_dialog(self.working_paper_reference_dialog)

    def _delete_working_paper(self, paper):
        working_paper_id = self._get_field(paper, "id", "Id")
        if not working_paper_id:
            self._show_error("Unable to determine working paper ID")
            return

        async def confirm_delete():
            try:
                self._show_loading("Deleting working paper...")
                await self.assessment_controller.auditing_client.delete_working_paper(working_paper_id)
                self._hide_loading()
                self._close_active_dialog(self.delete_working_paper_dialog)
                await self._append_activity_event("deleted a working paper", "DELETE", "#dc2626")
                self._show_success("Working paper deleted successfully")
                self.page.run_task(self._load_assessment_data)
            except Exception as ex:
                self._hide_loading()
                self._show_error(f"Failed to delete working paper: {str(ex)}")

        self.delete_working_paper_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Delete Working Paper"),
            content=ft.Text("Delete this working paper and its sign-off/reference history?"),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: self._close_active_dialog(self.delete_working_paper_dialog)),
                ft.FilledButton("Delete", on_click=lambda _: self.page.run_task(confirm_delete))
            ]
        )
        self._open_dialog(self.delete_working_paper_dialog)

    def _open_upload_document_dialog(self):
        if not self.pending_document_file or not self.pending_document_file.get("path"):
            self._show_error("Select a file first")
            return

        file_name = self.pending_document_file.get("name") or os.path.basename(self.pending_document_file["path"])
        title_default = os.path.splitext(file_name)[0]
        request_context, request_item_context = self._get_requested_evidence_context()
        if request_item_context:
            title_default = self._get_field(request_item_context, "itemDescription", "ItemDescription", default=title_default) or title_default

        title_field = ft.TextField(label="Document Title", value=title_default, autofocus=True)
        tags_field = ft.TextField(label="Tags", hint_text="comma separated")
        notes_field = ft.TextField(label="Notes", multiline=True, min_lines=2, max_lines=4)
        source_dropdown = ft.Dropdown(
            label="Source",
            options=[
                ft.dropdown.Option(key="Audit Team", text="Audit Team"),
                ft.dropdown.Option(key="Client", text="Client"),
                ft.dropdown.Option(key="Management", text="Management"),
                ft.dropdown.Option(key="System", text="System"),
                ft.dropdown.Option(key="Third Party", text="Third Party"),
            ],
            value="Client" if request_item_context else "Audit Team"
        )
        category_dropdown = ft.Dropdown(
            label="Category",
            options=[
                ft.dropdown.Option(
                    key=str(self._get_field(category, "id", "Id")),
                    text=self._get_field(category, "name", "Name", default="Category")
                )
                for category in self.document_categories or []
            ],
            value=str(self._get_field(self.document_categories[0], "id", "Id")) if self.document_categories else None
        )
        visibility_options = [
            ft.dropdown.Option(
                key=str(self._get_field(option, "id", "Id")),
                text=self._get_field(option, "name", "Name", default="Visibility")
            )
            for option in self.document_visibility_options or []
        ]
        visibility_dropdown = ft.Dropdown(
            label="Visibility",
            options=visibility_options,
            value=str(self._get_field(self.document_visibility_options[0], "id", "Id")) if self.document_visibility_options else None
        )
        confidentiality_label_field = ft.TextField(
            label="Confidentiality Label",
            hint_text="Optional, for example Payroll or Executive Compensation"
        )
        confidentiality_reason_field = ft.TextField(
            label="Confidentiality Notes",
            multiline=True,
            min_lines=2,
            max_lines=3,
            hint_text="Why access is restricted or what this evidence contains"
        )
        security_notice_title = ft.Text("Security review required", size=12, weight=ft.FontWeight.BOLD, color="#92400e")
        security_notice_text = ft.Text("", size=11, color="#92400e")
        security_notice = ft.Container(
            visible=False,
            padding=12,
            border_radius=10,
            bgcolor="#fef3c7",
            border=ft.border.all(1, "#fcd34d"),
            content=ft.Column([
                security_notice_title,
                security_notice_text
            ], spacing=4)
        )
        restricted_grants_hint = ft.Text("", size=11, color="#92400e", visible=False)
        allowed_roles_field = ft.TextField(
            label="Allowed Roles",
            hint_text="Optional comma-separated roles for restricted access"
        )
        allowed_user_ids_field = ft.TextField(
            label="Allowed User IDs",
            hint_text="Optional comma-separated user IDs for restricted access"
        )
        procedure_dropdown = ft.Dropdown(
            label="Link Procedure",
            options=[
                ft.dropdown.Option(
                    key=str(self._get_field(item, "id", "Id")),
                    text=self._get_field(item, "procedureTitle", "ProcedureTitle", default="Procedure")
                )
                for item in self.procedures_data or []
            ]
        )
        working_paper_dropdown = ft.Dropdown(
            label="Link Working Paper",
            options=[
                ft.dropdown.Option(
                    key=str(self._get_field(item, "id", "Id")),
                    text=f"{self._get_field(item, 'workingPaperCode', 'WorkingPaperCode', default='WP')} - {self._get_field(item, 'title', 'Title', default='Working paper')}"
                )
                for item in self.working_papers_data or []
            ]
        )
        finding_dropdown = ft.Dropdown(
            label="Link Finding",
            options=[
                ft.dropdown.Option(
                    key=str(self._get_field(item, "id", "Id")),
                    text=f"{self._get_field(item, 'findingNumber', 'FindingNumber', default='FND')} - {self._get_field(item, 'findingTitle', 'FindingTitle', default='Finding')}"
                )
                for item in self.findings_data or []
            ]
        )
        recommendation_dropdown = ft.Dropdown(
            label="Link Recommendation",
            options=[
                ft.dropdown.Option(
                    key=str(self._get_field(item, "id", "Id")),
                    text=self._get_field(item, "recommendationNumber", "RecommendationNumber", default=f"Recommendation {self._get_field(item, 'id', 'Id', default='')}")
                )
                for item in self.recommendations_data or []
            ]
        )

        request_item_options = []
        visible_requests = self._get_visible_evidence_requests()
        for request in visible_requests:
            request_number = self._get_field(request, "requestNumber", "RequestNumber", default="EDR")
            for item in self._get_field(request, "items", "Items", default=[]) or []:
                if self._get_field(item, "fulfilledDocumentId", "FulfilledDocumentId"):
                    continue
                item_id = self._get_field(item, "id", "Id")
                if item_id:
                    request_item_options.append(
                        ft.dropdown.Option(
                            key=str(item_id),
                            text=f"{request_number} - {self._get_field(item, 'itemDescription', 'ItemDescription', default='Requested item')}"
                        )
                    )
        request_item_dropdown = ft.Dropdown(
            label="Fulfil Evidence Request Item",
            options=request_item_options,
            value=str(self._get_field(request_item_context, "id", "Id")) if request_item_context else None
        )

        if request_context and request_item_context:
            requested_from = self._get_field(request_context, "requestedFrom", "RequestedFrom", default="")
            notes_field.value = f"Response to evidence request from {requested_from}" if requested_from else "Response to evidence request"

        def sync_document_security_state(source=None):
            selected_category = self._get_document_category_config(category_dropdown.value)
            if selected_category and source == "category":
                default_visibility_id = self._get_field(
                    selected_category,
                    "defaultVisibilityLevelId",
                    "DefaultVisibilityLevelId",
                    default=None
                )
                if default_visibility_id:
                    visibility_dropdown.value = str(default_visibility_id)
                default_confidentiality_label = self._get_field(
                    selected_category,
                    "defaultConfidentialityLabel",
                    "DefaultConfidentialityLabel",
                    default=""
                )
                if default_confidentiality_label and not (confidentiality_label_field.value or "").strip():
                    confidentiality_label_field.value = default_confidentiality_label

            selected_visibility = self._get_document_visibility_config(visibility_dropdown.value)
            requires_security_review = (
                self._category_requires_security_review(selected_category)
                or self._visibility_requires_security_review(selected_visibility)
            )
            visibility_name = (self._get_field(selected_visibility, "name", "Name", default="") or "").strip().lower()
            requires_explicit_grants = visibility_name == "restricted" and not can_manage_document_security(self.user)

            security_notice.visible = requires_security_review
            if requires_security_review:
                if can_manage_document_security(self.user):
                    security_notice.bgcolor = "#dcfce7"
                    security_notice.border = ft.border.all(1, "#86efac")
                    security_notice_title.value = "Sensitive upload will auto-approve"
                    security_notice_text.value = (
                        "This category or visibility is restricted. Because you manage document security, the upload will be saved as approved."
                    )
                else:
                    security_notice.bgcolor = "#fef3c7"
                    security_notice.border = ft.border.all(1, "#fcd34d")
                    security_notice_title.value = "Security review required"
                    security_notice_text.value = (
                        "This category or visibility is sensitive. The document will stay pending until a document security manager approves it."
                    )

            restricted_grants_hint.visible = requires_explicit_grants
            restricted_grants_hint.value = (
                "Restricted visibility needs at least one allowed role or allowed user ID unless a document security manager is uploading it."
                if requires_explicit_grants
                else ""
            )

            if self.page:
                self.page.update()

        category_dropdown.on_change = lambda _: sync_document_security_state("category")
        visibility_dropdown.on_change = lambda _: sync_document_security_state("visibility")
        sync_document_security_state("category")

        async def save_document():
            payload = {
                "referenceId": self._normalize_reference_id(),
                "auditUniverseId": None,
                "procedureId": int(procedure_dropdown.value) if procedure_dropdown.value else None,
                "workingPaperId": int(working_paper_dropdown.value) if working_paper_dropdown.value else None,
                "findingId": int(finding_dropdown.value) if finding_dropdown.value else None,
                "recommendationId": int(recommendation_dropdown.value) if recommendation_dropdown.value else None,
                "categoryId": int(category_dropdown.value) if category_dropdown.value else None,
                "visibilityLevelId": int(visibility_dropdown.value) if visibility_dropdown.value else None,
                "requestItemId": int(request_item_dropdown.value) if request_item_dropdown.value else None,
                "title": title_field.value.strip() if title_field.value else title_default,
                "sourceType": source_dropdown.value,
                "tags": tags_field.value.strip() if tags_field.value else "",
                "notes": notes_field.value.strip() if notes_field.value else "",
                "confidentialityLabel": confidentiality_label_field.value.strip() if confidentiality_label_field.value else "",
                "confidentialityReason": confidentiality_reason_field.value.strip() if confidentiality_reason_field.value else "",
                "grantedRoleNamesCsv": allowed_roles_field.value.strip() if allowed_roles_field.value else "",
                "grantedUserIdsCsv": allowed_user_ids_field.value.strip() if allowed_user_ids_field.value else "",
                "uploadedByName": self._get_current_user_name() or "Audit User",
                "uploadedByUserId": self._normalize_user_id()
            }
            selected_category = self._get_document_category_config(category_dropdown.value)
            selected_visibility = self._get_document_visibility_config(visibility_dropdown.value)
            requires_security_review = (
                self._category_requires_security_review(selected_category)
                or self._visibility_requires_security_review(selected_visibility)
            )
            selected_visibility_name = (self._get_field(selected_visibility, "name", "Name", default="") or "").strip().lower()

            if not payload["referenceId"]:
                self._show_error("Assessment reference is required")
                return
            if self._is_client_evidence_user() and not payload["requestItemId"]:
                self._show_error("Client evidence uploads must be linked to an assigned request item.")
                return
            if requires_security_review and (not payload["confidentialityLabel"] or not payload["confidentialityReason"]):
                self._show_error("Sensitive uploads require both a confidentiality label and confidentiality notes.")
                return
            if (
                selected_visibility_name == "restricted"
                and not payload["grantedRoleNamesCsv"]
                and not payload["grantedUserIdsCsv"]
                and not can_manage_document_security(self.user)
            ):
                self._show_error("Restricted visibility requires at least one allowed role or allowed user ID.")
                return

            try:
                self._show_loading("Uploading document...")
                created_document = await self.assessment_controller.auditing_client.upload_audit_document(
                    self.pending_document_file["path"],
                    payload
                )
                self._hide_loading()
                self._reset_document_upload_state()
                self._close_active_dialog(self.upload_document_dialog)
                review_status = self._normalize_security_review_status(
                    self._get_field(created_document, "securityReviewStatus", "SecurityReviewStatus", default="")
                ).lower()
                activity_message = "uploaded audit evidence"
                success_message = "Document uploaded successfully"
                if review_status == "pending approval":
                    activity_message = "submitted restricted audit evidence for security approval"
                    success_message = "Document uploaded and sent for security approval"
                elif review_status == "approved" and requires_security_review:
                    success_message = "Sensitive document uploaded and approved"
                await self._append_activity_event(activity_message, "UPLOAD_FILE", "#2563eb")
                self._show_success(success_message)
                self.page.run_task(self._load_assessment_data)
            except Exception as ex:
                self._hide_loading()
                self._show_error(f"Failed to upload document: {str(ex)}")

        def cancel_upload(_):
            self._reset_document_upload_state()
            self._close_active_dialog(self.upload_document_dialog)

        self.upload_document_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Upload Audit Document"),
            content=ft.Column([
                ft.Text(f"Selected file: {file_name}", size=12, color="#64748b"),
                ft.Text(
                    f"Requested item: {self._get_field(request_item_context, 'itemDescription', 'ItemDescription', default='')}",
                    size=11,
                    color="#2563eb"
                ) if request_item_context else ft.Container(),
                security_notice,
                title_field,
                category_dropdown,
                visibility_dropdown,
                restricted_grants_hint,
                source_dropdown,
                confidentiality_label_field,
                confidentiality_reason_field,
                allowed_roles_field,
                allowed_user_ids_field,
                tags_field,
                notes_field,
                procedure_dropdown,
                working_paper_dropdown,
                finding_dropdown,
                recommendation_dropdown,
                request_item_dropdown
            ], tight=True, width=560, height=520, scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.TextButton("Cancel", on_click=cancel_upload),
                ft.FilledButton("Upload", on_click=lambda _: self.page.run_task(save_document))
            ]
        )
        self._open_dialog(self.upload_document_dialog)

    def _open_document_security_dialog(self, document):
        if not can_manage_document_security(self.user):
            self._show_error("You do not have permission to change document security.")
            return

        document_id = self._get_field(document, "id", "Id")
        if not document_id:
            self._show_error("Unable to determine document ID")
            return

        existing_grants = self._get_field(document, "accessGrants", "AccessGrants", default=[]) or []
        granted_role_names = sorted({
            (self._get_field(grant, "granteeRoleName", "GranteeRoleName", default="") or "").strip()
            for grant in existing_grants
            if (self._get_field(grant, "granteeRoleName", "GranteeRoleName", default="") or "").strip()
        })
        granted_user_ids = sorted({
            str(self._get_field(grant, "granteeUserId", "GranteeUserId"))
            for grant in existing_grants
            if self._get_field(grant, "granteeUserId", "GranteeUserId", default=None) not in (None, "", 0)
        })

        visibility_dropdown = ft.Dropdown(
            label="Visibility",
            options=[
                ft.dropdown.Option(
                    key=str(self._get_field(option, "id", "Id")),
                    text=self._get_field(option, "name", "Name", default="Visibility")
                )
                for option in self.document_visibility_options or []
            ],
            value=str(self._get_field(document, "visibilityLevelId", "VisibilityLevelId")) if self._get_field(document, "visibilityLevelId", "VisibilityLevelId") else None
        )
        confidentiality_label_field = ft.TextField(
            label="Confidentiality Label",
            value=self._get_field(document, "confidentialityLabel", "ConfidentialityLabel", default="") or ""
        )
        confidentiality_reason_field = ft.TextField(
            label="Confidentiality Notes",
            value=self._get_field(document, "confidentialityReason", "ConfidentialityReason", default="") or "",
            multiline=True,
            min_lines=2,
            max_lines=3
        )
        allowed_roles_field = ft.TextField(
            label="Allowed Roles",
            hint_text="Comma-separated roles",
            value=", ".join(granted_role_names)
        )
        allowed_user_ids_field = ft.TextField(
            label="Allowed User IDs",
            hint_text="Comma-separated user IDs",
            value=", ".join(granted_user_ids)
        )
        review_status = self._normalize_security_review_status(
            self._get_field(document, "securityReviewStatus", "SecurityReviewStatus", default="")
        )
        review_status_label, review_status_color = self._get_security_review_status_style(review_status)
        review_notes = self._get_field(document, "securityReviewNotes", "SecurityReviewNotes", default="")
        reviewed_by = self._get_field(document, "securityReviewedByName", "SecurityReviewedByName", default="")
        reviewed_at = self._format_activity_time_value(
            self._get_field(document, "securityReviewedAt", "SecurityReviewedAt", default="")
        )

        async def save_security():
            payload = {
                "visibilityLevelId": int(visibility_dropdown.value) if visibility_dropdown.value else None,
                "confidentialityLabel": confidentiality_label_field.value.strip() if confidentiality_label_field.value else "",
                "confidentialityReason": confidentiality_reason_field.value.strip() if confidentiality_reason_field.value else "",
                "updatedByUserId": self._normalize_user_id(),
                "updatedByName": self._get_current_user_name() or "Audit User",
                "grantedRoleNames": [
                    value.strip() for value in (allowed_roles_field.value or "").split(",")
                    if value and value.strip()
                ],
                "grantedUserIds": [
                    int(value.strip()) for value in (allowed_user_ids_field.value or "").split(",")
                    if value and value.strip().isdigit()
                ],
            }

            try:
                self._show_loading("Saving document security...")
                await self.assessment_controller.auditing_client.update_audit_document_security(document_id, payload)
                self._hide_loading()
                self._close_active_dialog(self.document_security_dialog)
                self._show_success("Document security updated")
                self.page.run_task(self._load_assessment_data)
            except Exception as ex:
                self._hide_loading()
                self._show_error(f"Failed to update document security: {str(ex)}")

        self.document_security_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Manage Document Security"),
            content=ft.Column([
                ft.Text(self._get_field(document, "title", "Title", default="Document"), size=12, color="#64748b"),
                ft.Row([
                    ft.Container(
                        content=ft.Text(f"Security Review: {review_status_label}", size=11, color="white"),
                        bgcolor=review_status_color,
                        padding=ft.padding.symmetric(horizontal=8, vertical=4),
                        border_radius=10
                    ),
                    ft.Text(
                        f"Reviewed by {reviewed_by} on {reviewed_at}" if reviewed_by and reviewed_at else "No review decision recorded yet.",
                        size=11,
                        color="#7f8c8d"
                    )
                ], spacing=8, wrap=True),
                ft.Text(review_notes, size=11, color="#475569") if review_notes else ft.Container(),
                visibility_dropdown,
                confidentiality_label_field,
                confidentiality_reason_field,
                allowed_roles_field,
                allowed_user_ids_field,
            ], tight=True, width=520, scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: self._close_active_dialog(self.document_security_dialog)),
                ft.FilledButton("Save", on_click=lambda _: self.page.run_task(save_security))
            ]
        )
        self._open_dialog(self.document_security_dialog)

    def _open_document_security_review_dialog(self, document, is_approved):
        if not can_manage_document_security(self.user):
            self._show_error("You do not have permission to review restricted evidence.")
            return

        document_id = self._get_field(document, "id", "Id")
        if not document_id:
            self._show_error("Unable to determine document ID")
            return

        action_label = "Approve" if is_approved else "Reject"
        review_notes_field = ft.TextField(
            label="Review Notes",
            value=self._get_field(document, "securityReviewNotes", "SecurityReviewNotes", default="") or "",
            multiline=True,
            min_lines=3,
            max_lines=5,
            hint_text="Capture the approval rationale or rejection instructions"
        )

        async def save_review():
            payload = {
                "isApproved": is_approved,
                "reviewNotes": review_notes_field.value.strip() if review_notes_field.value else "",
                "reviewedByUserId": self._normalize_user_id(),
                "reviewedByName": self._get_current_user_name() or "Audit User"
            }

            try:
                self._show_loading(f"{action_label}ing document...")
                await self.assessment_controller.auditing_client.review_audit_document_security(document_id, payload)
                self._hide_loading()
                self._close_active_dialog(self.document_security_review_dialog)
                self._show_success(f"Document {action_label.lower()}d")
                self.page.run_task(self._load_assessment_data)
            except Exception as ex:
                self._hide_loading()
                self._show_error(f"Failed to {action_label.lower()} document security: {str(ex)}")

        self.document_security_review_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"{action_label} Restricted Document"),
            content=ft.Column([
                ft.Text(self._get_field(document, "title", "Title", default="Document"), size=12, color="#64748b"),
                ft.Text(
                    "Approving will release the document to users who match its visibility and grant rules."
                    if is_approved
                    else "Rejecting will keep the document unavailable to the wider team until it is replaced or re-reviewed.",
                    size=11,
                    color="#475569"
                ),
                review_notes_field
            ], tight=True, width=520),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: self._close_active_dialog(self.document_security_review_dialog)),
                ft.FilledButton(action_label, on_click=lambda _: self.page.run_task(save_review))
            ]
        )
        self._open_dialog(self.document_security_review_dialog)

    def _open_add_evidence_request_dialog(self, e=None):
        title_field = ft.TextField(label="Request Title", autofocus=True)
        requested_from_field = ft.TextField(label="Requested From")
        requested_to_email_field = ft.TextField(label="Recipient Email")
        due_date_field = ft.TextField(label="Due Date (YYYY-MM-DD)")
        description_field = ft.TextField(label="Request Description", multiline=True, min_lines=2, max_lines=4)
        items_field = ft.TextField(
            label="Requested Items",
            multiline=True,
            min_lines=4,
            max_lines=8,
            hint_text="Enter one requested item per line"
        )
        notes_field = ft.TextField(label="Internal Notes", multiline=True, min_lines=2, max_lines=3)
        priority_dropdown = ft.Dropdown(
            label="Priority",
            options=[
                ft.dropdown.Option(key="1", text="High"),
                ft.dropdown.Option(key="2", text="Medium"),
                ft.dropdown.Option(key="3", text="Low")
            ],
            value="2"
        )

        async def save_request():
            item_lines = [
                line.strip() for line in (items_field.value or "").splitlines()
                if line and line.strip()
            ]
            payload = {
                "referenceId": self._normalize_reference_id(),
                "auditUniverseId": None,
                "title": title_field.value.strip() if title_field.value else "",
                "requestDescription": description_field.value.strip() if description_field.value else "",
                "requestedFrom": requested_from_field.value.strip() if requested_from_field.value else "",
                "requestedToEmail": requested_to_email_field.value.strip() if requested_to_email_field.value else "",
                "priority": int(priority_dropdown.value) if priority_dropdown.value else 2,
                "dueDate": due_date_field.value.strip() if due_date_field.value else None,
                "statusId": None,
                "requestedByUserId": self._normalize_user_id(),
                "requestedByName": self._get_current_user_name() or "Audit User",
                "workflowInstanceId": None,
                "notes": notes_field.value.strip() if notes_field.value else "",
                "items": [
                    {
                        "itemDescription": item,
                        "expectedDocumentType": "",
                        "isRequired": True
                    }
                    for item in item_lines
                ]
            }

            if not payload["referenceId"] or not payload["title"]:
                self._show_error("Assessment reference and request title are required")
                return
            if not payload["items"]:
                self._show_error("Add at least one requested item")
                return

            try:
                self._show_loading("Creating evidence request...")
                await self.assessment_controller.auditing_client.create_evidence_request(payload)
                self._hide_loading()
                self._close_active_dialog(self.evidence_request_dialog)
                await self._append_activity_event("created an evidence request", "FORWARD_TO_INBOX", "#f59e0b")
                self._show_success("Evidence request created")
                self.page.run_task(self._load_assessment_data)
            except Exception as ex:
                self._hide_loading()
                self._show_error(f"Failed to create evidence request: {str(ex)}")

        self.evidence_request_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("New Evidence Request"),
            content=ft.Column([
                title_field,
                requested_from_field,
                requested_to_email_field,
                due_date_field,
                priority_dropdown,
                description_field,
                items_field,
                notes_field
            ], tight=True, width=560, height=520, scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: self._close_active_dialog(self.evidence_request_dialog)),
                ft.FilledButton("Create", on_click=lambda _: self.page.run_task(save_request))
            ]
        )
        self._open_dialog(self.evidence_request_dialog)

    def _open_document_link(self, document_id):
        if not document_id:
            self._show_error("Unable to determine document ID")
            return
        url = self.assessment_controller.auditing_client.get_audit_document_download_url(document_id)
        self.page.launch_url(url)

    def _delete_document(self, document):
        document_id = self._get_field(document, "id", "Id")
        if not document_id:
            self._show_error("Unable to determine document ID")
            return

        async def confirm_delete():
            try:
                self._show_loading("Deleting document...")
                await self.assessment_controller.auditing_client.delete_audit_document(document_id)
                self._hide_loading()
                self._close_active_dialog(self.delete_document_dialog)
                await self._append_activity_event("deleted audit evidence", "DELETE", "#dc2626")
                self._show_success("Document deleted successfully")
                self.page.run_task(self._load_assessment_data)
            except Exception as ex:
                self._hide_loading()
                self._show_error(f"Failed to delete document: {str(ex)}")

        self.delete_document_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Delete Document"),
            content=ft.Text("Delete this document from the evidence library?"),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: self._close_active_dialog(self.delete_document_dialog)),
                ft.FilledButton("Delete", on_click=lambda _: self.page.run_task(confirm_delete))
            ]
        )
        self._open_dialog(self.delete_document_dialog)

    def _review_evidence_request_item(self, request_item, is_accepted):
        if not can_review_evidence(self.user):
            self._show_error("You do not have permission to review evidence items.")
            return
        request_item_id = self._get_field(request_item, "id", "Id")
        fulfilled_document_id = self._get_field(request_item, "fulfilledDocumentId", "FulfilledDocumentId")
        fulfilled_title = self._get_field(request_item, "fulfilledDocumentTitle", "FulfilledDocumentTitle", default="Uploaded evidence")

        if not request_item_id or not fulfilled_document_id:
            self._show_error("This request item does not have uploaded evidence to review")
            return
        if (fulfilled_title or "").strip().lower() == "restricted document":
            self._show_error("This evidence item is restricted and cannot be reviewed from your current access scope.")
            return

        notes_field = ft.TextField(label="Reviewer Notes", multiline=True, min_lines=2, max_lines=4)
        action_label = "Accept" if is_accepted else "Reject"
        action_color = "#16a34a" if is_accepted else "#dc2626"

        async def save_review():
            payload = {
                "requestItemId": request_item_id,
                "isAccepted": is_accepted,
                "reviewerNotes": notes_field.value.strip() if notes_field.value else "",
                "reviewedByUserId": self._normalize_user_id()
            }

            try:
                self._show_loading(f"{action_label}ing evidence item...")
                await self.assessment_controller.auditing_client.review_evidence_request_item(payload)
                self._hide_loading()
                self._close_active_dialog(self.evidence_review_dialog)
                await self._append_activity_event(
                    f"{action_label.lower()}ed an evidence request item",
                    "FACT_CHECK",
                    action_color
                )
                self._show_success(f"Evidence item {action_label.lower()}ed")
                self.page.run_task(self._load_assessment_data)
            except Exception as ex:
                self._hide_loading()
                self._show_error(f"Failed to review evidence item: {str(ex)}")

        self.evidence_review_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"{action_label} Evidence Item"),
            content=ft.Column([
                ft.Text(self._get_field(request_item, "itemDescription", "ItemDescription", default="Requested item"), weight=ft.FontWeight.BOLD),
                ft.Text(f"Evidence: {fulfilled_title}", size=12, color="#64748b"),
                notes_field
            ], tight=True, width=520),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: self._close_active_dialog(self.evidence_review_dialog)),
                ft.FilledButton(action_label, bgcolor=action_color, color="white", on_click=lambda _: self.page.run_task(save_review))
            ]
        )
        self._open_dialog(self.evidence_review_dialog)

    def _open_materiality_scope_link_dialog(self, source_item=None, existing_link=None):
        reference_id = self._normalize_reference_id()
        if not reference_id:
            self._show_error("Save the audit file before recording scope decisions.")
            return

        active_calculation = self._get_active_materiality_calculation() or {}
        calculation_id = self._get_field(existing_link, "materialityCalculationId", "MaterialityCalculationId", default=None) or self._get_field(active_calculation, "id", "Id", default=None)
        if not calculation_id:
            self._show_error("Activate a materiality calculation before recording scope decisions.")
            return

        source_amount = self._get_field(source_item, "basisAmount", "BasisAmount", default=None)
        overall_materiality = self._get_active_materiality_value("overallMateriality", "OverallMateriality")
        suggested_coverage = None
        try:
            if source_amount not in (None, "", 0, 0.0) and overall_materiality not in (None, "", 0, 0.0):
                suggested_coverage = round((float(source_amount) / float(overall_materiality)) * 100, 2)
        except Exception:
            suggested_coverage = None

        scope_options = [ft.dropdown.Option("", "Not linked to a scope item yet")]
        for item in self.scope_items_data or []:
            scope_options.append(
                ft.dropdown.Option(
                    str(self._get_field(item, "id", "Id", default="")),
                    self._get_scope_item_label(item),
                )
            )

        scope_item_field = ft.Dropdown(
            label="Linked Scope Item",
            options=scope_options,
            value=str(self._get_field(existing_link, "scopeItemId", "ScopeItemId", default="") or ""),
        )
        fsli_field = ft.TextField(
            label="FSLI",
            value=(
                self._get_field(existing_link, "fsli", "Fsli", default="")
                or self._get_field(source_item, "fsli", "Fsli", default="")
                or ""
            ),
        )
        relevance_field = ft.TextField(
            label="Benchmark Relevance",
            value=(
                self._get_field(existing_link, "benchmarkRelevance", "BenchmarkRelevance", default="")
                or self._get_field(source_item, "classification", "Classification", default="")
                or "Above overall materiality"
            ),
        )
        inclusion_reason_field = ft.TextField(
            label="Inclusion Reason",
            multiline=True,
            min_lines=2,
            max_lines=4,
            value=(
                self._get_field(existing_link, "inclusionReason", "InclusionReason", default="")
                or self._get_field(source_item, "recommendedAction", "RecommendedAction", default="")
                or ""
            ),
        )
        coverage_field = ft.TextField(
            label="Coverage Percent",
            value=str(self._get_field(existing_link, "coveragePercent", "CoveragePercent", default=suggested_coverage) or ""),
        )
        above_threshold_field = ft.Checkbox(
            label="Above overall materiality threshold",
            value=bool(self._get_field(existing_link, "isAboveThreshold", "IsAboveThreshold", default=True)),
        )
        status_text = ft.Text("", size=12, color="#64748b")

        async def save_scope_link():
            coverage_percent = self._parse_optional_decimal(coverage_field.value)
            payload = {
                "referenceId": reference_id,
                "materialityCalculationId": calculation_id,
                "scopeItemId": int(scope_item_field.value) if scope_item_field.value not in (None, "", "None") else None,
                "fsli": fsli_field.value.strip() if fsli_field.value else "",
                "benchmarkRelevance": relevance_field.value.strip() if relevance_field.value else "",
                "inclusionReason": inclusion_reason_field.value.strip() if inclusion_reason_field.value else "",
                "isAboveThreshold": bool(above_threshold_field.value),
                "coveragePercent": coverage_percent,
            }
            if not payload["fsli"]:
                status_text.value = "FSLI is required."
                status_text.color = "#dc2626"
                self.page.update()
                return

            try:
                status_text.value = "Saving scope decision..."
                status_text.color = "#475569"
                self.page.update()
                link_id = self._get_field(existing_link, "id", "Id", default=None)
                if link_id:
                    await self.assessment_controller.auditing_client.update_materiality_scope_link(link_id, payload)
                else:
                    await self.assessment_controller.auditing_client.create_materiality_scope_link(payload)
                await self._refresh_materiality_view_state()
                await self._append_activity_event("recorded a materiality scope decision", "RULE_FOLDER", "#7c3aed")
                self._show_success("Materiality scope decision saved.")
                self._close_active_dialog(self.materiality_scope_link_dialog)
                if self.page:
                    self.page.update()
            except Exception as ex:
                status_text.value = f"Failed to save scope decision: {str(ex)}"
                status_text.color = "#dc2626"
                if self.page:
                    self.page.update()

        self.materiality_scope_link_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Materiality Scope Decision"),
            content=ft.Column(
                [
                    scope_item_field,
                    fsli_field,
                    relevance_field,
                    inclusion_reason_field,
                    ft.ResponsiveRow(
                        [
                            ft.Container(col={"sm": 12, "md": 6}, content=coverage_field),
                            ft.Container(col={"sm": 12, "md": 6}, content=above_threshold_field),
                        ],
                        run_spacing=10,
                    ),
                    status_text,
                ],
                width=640,
                tight=True,
                scroll=ft.ScrollMode.AUTO,
            ),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: self._close_active_dialog(self.materiality_scope_link_dialog)),
                ft.FilledButton("Save Scope Decision", icon=Icons.SAVE, on_click=lambda _: self.page.run_task(save_scope_link)),
            ],
        )
        self._open_dialog(self.materiality_scope_link_dialog)

    def _confirm_delete_materiality_scope_link(self, scope_link):
        link_id = self._get_field(scope_link, "id", "Id", default=None)
        if not link_id:
            self._show_error("Scope link ID is missing.")
            return

        async def delete_scope_link():
            try:
                await self.assessment_controller.auditing_client.delete_materiality_scope_link(link_id)
                await self._refresh_materiality_view_state()
                await self._append_activity_event("deleted a materiality scope decision", "DELETE_OUTLINE", "#dc2626")
                self._show_success("Materiality scope decision deleted.")
            except Exception as ex:
                self._show_error(f"Failed to delete scope decision: {str(ex)}")

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Delete Scope Decision"),
            content=ft.Text("Delete this materiality scope decision?"),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: self._close_active_dialog(dialog)),
                ft.TextButton("Delete", on_click=lambda _: (self._close_active_dialog(dialog), self.page.run_task(delete_scope_link))),
            ],
        )
        self._open_dialog(dialog)

    def _open_materiality_misstatement_dialog(self, source_item=None, existing_misstatement=None):
        reference_id = self._normalize_reference_id()
        if not reference_id:
            self._show_error("Save the audit file before recording misstatements.")
            return

        active_calculation = self._get_active_materiality_calculation() or {}
        calculation_id = self._get_field(existing_misstatement, "materialityCalculationId", "MaterialityCalculationId", default=None) or self._get_field(active_calculation, "id", "Id", default=None)
        finding_options = [ft.dropdown.Option("", "Not linked to a finding")]
        for finding in self.findings_data or []:
            finding_options.append(
                ft.dropdown.Option(
                    str(self._get_field(finding, "id", "Id", default="")),
                    self._get_field(finding, "findingTitle", "FindingTitle", default=self._get_field(finding, "title", "Title", default="Finding")),
                )
            )

        description_field = ft.TextField(
            label="Description",
            multiline=True,
            min_lines=2,
            max_lines=4,
            value=(
                self._get_field(existing_misstatement, "description", "Description", default="")
                or self._get_field(source_item, "description", "Description", default="")
                or ""
            ),
        )
        finding_field = ft.Dropdown(
            label="Linked Finding",
            options=finding_options,
            value=str(self._get_field(existing_misstatement, "findingId", "FindingId", default="") or ""),
        )
        fsli_field = ft.TextField(
            label="FSLI",
            value=(
                self._get_field(existing_misstatement, "fsli", "Fsli", default="")
                or self._get_field(source_item, "fsli", "Fsli", default="")
                or ""
            ),
        )
        account_number_field = ft.TextField(
            label="Account Number",
            value=(
                self._get_field(existing_misstatement, "accountNumber", "AccountNumber", default="")
                or self._get_field(source_item, "accountNumber", "AccountNumber", default="")
                or ""
            ),
        )
        transaction_id_field = ft.TextField(
            label="Transaction Identifier",
            value=(
                self._get_field(existing_misstatement, "transactionIdentifier", "TransactionIdentifier", default="")
                or self._get_field(source_item, "itemIdentifier", "ItemIdentifier", default="")
                or ""
            ),
        )
        actual_amount_field = ft.TextField(
            label="Actual Amount",
            value=str(self._get_field(existing_misstatement, "actualAmount", "ActualAmount", default=self._get_field(source_item, "basisAmount", "BasisAmount", default="")) or ""),
        )
        projected_amount_field = ft.TextField(
            label="Projected Amount",
            value=str(self._get_field(existing_misstatement, "projectedAmount", "ProjectedAmount", default="") or ""),
        )
        evaluation_basis_field = ft.TextField(
            label="Evaluation Basis",
            value=self._get_field(existing_misstatement, "evaluationBasis", "EvaluationBasis", default="Projected amount against active thresholds"),
        )
        status_field = ft.Dropdown(
            label="Status",
            value=self._get_field(existing_misstatement, "status", "Status", default="Open"),
            options=[
                ft.dropdown.Option("Open", "Open"),
                ft.dropdown.Option("Management Adjustment Requested", "Management Adjustment Requested"),
                ft.dropdown.Option("Corrected", "Corrected"),
                ft.dropdown.Option("Carried Forward", "Carried Forward"),
                ft.dropdown.Option("Closed", "Closed"),
            ],
        )
        status_text = ft.Text("", size=12, color="#64748b")

        async def save_misstatement():
            actual_amount = self._parse_optional_decimal(actual_amount_field.value)
            projected_amount = self._parse_optional_decimal(projected_amount_field.value)
            if actual_amount is None:
                status_text.value = "Actual amount is required."
                status_text.color = "#dc2626"
                if self.page:
                    self.page.update()
                return
            if not description_field.value or not description_field.value.strip():
                status_text.value = "Description is required."
                status_text.color = "#dc2626"
                if self.page:
                    self.page.update()
                return

            payload = {
                "referenceId": reference_id,
                "findingId": int(finding_field.value) if finding_field.value not in (None, "", "None") else None,
                "materialityCalculationId": calculation_id,
                "fsli": fsli_field.value.strip() if fsli_field.value else "",
                "accountNumber": account_number_field.value.strip() if account_number_field.value else "",
                "transactionIdentifier": transaction_id_field.value.strip() if transaction_id_field.value else "",
                "description": description_field.value.strip(),
                "actualAmount": actual_amount,
                "projectedAmount": projected_amount,
                "evaluationBasis": evaluation_basis_field.value.strip() if evaluation_basis_field.value else "",
                "status": status_field.value or "Open",
                "createdByUserId": self._normalize_user_id(),
                "createdByName": self._get_current_user_name(),
            }

            try:
                status_text.value = "Saving misstatement..."
                status_text.color = "#475569"
                if self.page:
                    self.page.update()
                misstatement_id = self._get_field(existing_misstatement, "id", "Id", default=None)
                if misstatement_id:
                    await self.assessment_controller.auditing_client.update_materiality_misstatement(misstatement_id, payload)
                else:
                    await self.assessment_controller.auditing_client.create_materiality_misstatement(payload)
                await self._refresh_materiality_view_state()
                await self._append_activity_event("recorded a materiality misstatement", "REPORT_PROBLEM", "#dc2626")
                self._show_success("Materiality misstatement saved.")
                self._close_active_dialog(self.materiality_misstatement_dialog)
                if self.page:
                    self.page.update()
            except Exception as ex:
                status_text.value = f"Failed to save misstatement: {str(ex)}"
                status_text.color = "#dc2626"
                if self.page:
                    self.page.update()

        self.materiality_misstatement_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Record Misstatement"),
            content=ft.Column(
                [
                    description_field,
                    finding_field,
                    ft.ResponsiveRow(
                        [
                            ft.Container(col={"sm": 12, "md": 4}, content=fsli_field),
                            ft.Container(col={"sm": 12, "md": 4}, content=account_number_field),
                            ft.Container(col={"sm": 12, "md": 4}, content=transaction_id_field),
                        ],
                        run_spacing=10,
                    ),
                    ft.ResponsiveRow(
                        [
                            ft.Container(col={"sm": 12, "md": 4}, content=actual_amount_field),
                            ft.Container(col={"sm": 12, "md": 4}, content=projected_amount_field),
                            ft.Container(col={"sm": 12, "md": 4}, content=status_field),
                        ],
                        run_spacing=10,
                    ),
                    evaluation_basis_field,
                    status_text,
                ],
                width=680,
                tight=True,
                scroll=ft.ScrollMode.AUTO,
            ),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: self._close_active_dialog(self.materiality_misstatement_dialog)),
                ft.FilledButton("Save Misstatement", icon=Icons.SAVE, on_click=lambda _: self.page.run_task(save_misstatement)),
            ],
        )
        self._open_dialog(self.materiality_misstatement_dialog)

    def _confirm_delete_materiality_misstatement(self, misstatement):
        misstatement_id = self._get_field(misstatement, "id", "Id", default=None)
        if not misstatement_id:
            self._show_error("Misstatement ID is missing.")
            return

        async def delete_misstatement():
            try:
                await self.assessment_controller.auditing_client.delete_materiality_misstatement(misstatement_id)
                await self._refresh_materiality_view_state()
                await self._append_activity_event("deleted a materiality misstatement", "DELETE_OUTLINE", "#dc2626")
                self._show_success("Materiality misstatement deleted.")
            except Exception as ex:
                self._show_error(f"Failed to delete misstatement: {str(ex)}")

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Delete Misstatement"),
            content=ft.Text("Delete this recorded misstatement?"),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: self._close_active_dialog(dialog)),
                ft.TextButton("Delete", on_click=lambda _: (self._close_active_dialog(dialog), self.page.run_task(delete_misstatement))),
            ],
        )
        self._open_dialog(dialog)

    def _open_materiality_calculator_dialog(self, e=None):
        reference_id = self._normalize_reference_id()
        if not reference_id:
            self._show_error("Save the audit file before calculating materiality.")
            return

        self.materiality_dialog_reference_id = reference_id
        workspace = self.materiality_workspace or {}
        active_calculation = self._get_active_materiality_calculation() or {}
        candidate_defaults = self._get_materiality_candidates()
        preferred_candidate = candidate_defaults[0] if candidate_defaults else {}
        benchmark_profiles = self._get_materiality_benchmark_profiles()
        selected_profile = self._get_selected_materiality_profile() or {}

        def resolve_materiality_default(*values, fallback=""):
            for value in values:
                if value is None:
                    continue
                text = str(value).strip()
                if text:
                    return text
            return fallback

        def resolve_profile_percentage(profile, camel_key, pascal_key, fallback):
            return resolve_materiality_default(
                self._get_field(active_calculation, camel_key, pascal_key, default=""),
                self._get_field(profile, camel_key, pascal_key, default=""),
                fallback=fallback,
            )

        selected_profile_id = resolve_materiality_default(
            self._get_field(active_calculation, "benchmarkProfileId", "BenchmarkProfileId", default=""),
            self._get_field(workspace, "selectedBenchmarkProfileId", "SelectedBenchmarkProfileId", default=""),
            self._get_field(selected_profile, "id", "Id", default=""),
        )

        profile_dropdown = ft.Dropdown(
            label="Benchmark Profile",
            value=selected_profile_id or None,
            options=[
                ft.dropdown.Option(
                    str(self._get_field(profile, "id", "Id")),
                    self._get_field(profile, "profileName", "ProfileName", default="Profile"),
                )
                for profile in benchmark_profiles
            ],
        )
        profile_status_text = ft.Text("", size=11, color="#475569")
        profile_notes_text = ft.Text("", size=11, color="#64748b")
        entity_type_field = ft.TextField(
            label="Entity Type",
            value=resolve_materiality_default(
                self._get_field(active_calculation, "entityType", "EntityType", default=""),
                self._get_field(workspace, "materialityEntityType", "MaterialityEntityType", default=""),
                self._get_field(selected_profile, "entityType", "EntityType", default=""),
                fallback="General",
            ),
        )
        industry_name_field = ft.TextField(
            label="Industry / Client Context",
            value=resolve_materiality_default(
                self._get_field(active_calculation, "industryName", "IndustryName", default=""),
                self._get_field(workspace, "materialityIndustryName", "MaterialityIndustryName", default=""),
                self._get_field(selected_profile, "industryName", "IndustryName", default=""),
            ),
        )
        benchmark_selection_rationale_field = ft.TextField(
            label="Benchmark Selection Rationale",
            multiline=True,
            min_lines=2,
            max_lines=4,
            value=resolve_materiality_default(
                self._get_field(active_calculation, "benchmarkSelectionRationale", "BenchmarkSelectionRationale", default=""),
                self._get_field(workspace, "materialityBenchmarkSelectionRationale", "MaterialityBenchmarkSelectionRationale", default=""),
            ),
        )
        profit_before_tax_field = ft.TextField(label="Profit Before Tax %", value=resolve_profile_percentage(selected_profile, "profitBeforeTaxPercentage", "ProfitBeforeTaxPercentage", "5"))
        revenue_field = ft.TextField(label="Revenue %", value=resolve_profile_percentage(selected_profile, "revenuePercentage", "RevenuePercentage", "1"))
        total_assets_field = ft.TextField(label="Total Assets %", value=resolve_profile_percentage(selected_profile, "totalAssetsPercentage", "TotalAssetsPercentage", "1"))
        expenses_field = ft.TextField(label="Expenses %", value=resolve_profile_percentage(selected_profile, "expensesPercentage", "ExpensesPercentage", "1"))
        performance_field = ft.TextField(
            label="Performance Materiality %",
            value=resolve_materiality_default(
                self._get_field(active_calculation, "performancePercentageApplied", "PerformancePercentageApplied", default=""),
                self._get_field(selected_profile, "performancePercentage", "PerformancePercentage", default=""),
                fallback="75",
            )
        )
        clearly_trivial_field = ft.TextField(
            label="Clearly Trivial %",
            value=resolve_materiality_default(
                self._get_field(active_calculation, "clearlyTrivialPercentageApplied", "ClearlyTrivialPercentageApplied", default=""),
                self._get_field(selected_profile, "clearlyTrivialPercentage", "ClearlyTrivialPercentage", default=""),
                fallback="5",
            )
        )
        fiscal_year_field = ft.TextField(
            label="Fiscal Year",
            value=str(self._get_field(workspace, "latestTrialBalanceYear", "LatestTrialBalanceYear", default="") or "")
        )
        rationale_field = ft.TextField(
            label="Override / approval note",
            multiline=True,
            min_lines=2,
            max_lines=4,
            value=self._get_field(active_calculation, "rationale", "Rationale", default=""),
        )
        self.materiality_selected_file_text = ft.Text("No trial balance CSV selected", size=12, color="#64748b")
        self.materiality_validation_text = ft.Text(
            "Select a trial balance or journal-entry CSV to import into the materiality workflow.",
            size=12,
            color="#64748b",
        )
        self.materiality_preview_column = ft.Column(
            controls=[ft.Text("No preview available", size=12, color="#64748b")],
            spacing=6,
            scroll=ft.ScrollMode.AUTO,
        )
        self.materiality_import_button = ft.FilledButton(
            "Import Materiality Data",
            icon=Icons.UPLOAD_FILE,
            disabled=True,
            on_click=lambda _: self.page.run_task(import_trial_balance_csv),
        )
        dataset_label_map = {
            "trial_balance": "Trial Balance",
            "journal_entries": "Journal Entries",
        }
        materiality_dataset_dropdown = ft.Dropdown(
            label="Import Dataset",
            value=self.materiality_import_dataset_type,
            options=[
                ft.dropdown.Option("trial_balance", "Trial Balance"),
                ft.dropdown.Option("journal_entries", "Journal Entries"),
            ],
        )
        manual_benchmark_name_field = ft.TextField(
            label="Manual Benchmark Name",
            value=resolve_materiality_default(
                self._get_field(active_calculation, "benchmarkName", "BenchmarkName"),
                self._get_field(preferred_candidate, "candidateName", "CandidateName"),
                fallback="Custom Benchmark",
            ),
        )
        manual_benchmark_code_field = ft.TextField(
            label="Manual Benchmark Code",
            value=resolve_materiality_default(
                self._get_field(active_calculation, "benchmarkCode", "BenchmarkCode"),
                fallback="manual_custom",
            ),
        )
        manual_benchmark_amount_field = ft.TextField(
            label="Manual Benchmark Amount",
            value=resolve_materiality_default(
                self._get_field(active_calculation, "benchmarkAmount", "BenchmarkAmount"),
                self._get_field(preferred_candidate, "benchmarkAmount", "BenchmarkAmount"),
            ),
        )
        manual_percentage_field = ft.TextField(
            label="Manual Benchmark %",
            value=resolve_materiality_default(
                self._get_field(active_calculation, "percentageApplied", "PercentageApplied"),
                self._get_field(preferred_candidate, "recommendedPercentage", "RecommendedPercentage"),
                fallback="1",
            ),
        )
        status_text = ft.Text(
            "Import or update trial balance data, generate candidates, or create a manual calculation for this audit file.",
            size=12,
            color="#475569",
        )
        candidates_column = ft.Column(spacing=10)
        history_column = ft.Column(spacing=10)
        approval_history_column = ft.Column(spacing=10)
        self.materiality_form_state = {
            "benchmark_profile_id": profile_dropdown.value,
            "entity_type": entity_type_field.value,
            "industry_name": industry_name_field.value,
            "benchmark_selection_rationale": benchmark_selection_rationale_field.value,
            "fiscal_year": fiscal_year_field.value,
            "profit_before_tax_percentage": profit_before_tax_field.value,
            "revenue_percentage": revenue_field.value,
            "total_assets_percentage": total_assets_field.value,
            "expenses_percentage": expenses_field.value,
            "performance_percentage": performance_field.value,
            "clearly_trivial_percentage": clearly_trivial_field.value,
            "rationale": rationale_field.value,
            "manual_benchmark_name": manual_benchmark_name_field.value,
            "manual_benchmark_code": manual_benchmark_code_field.value,
            "manual_benchmark_amount": manual_benchmark_amount_field.value,
            "manual_percentage": manual_percentage_field.value,
        }
        self._log_materiality_event(
            "materiality_dialog_opened",
            has_trial_balance_data=self._get_field(workspace, "hasTrialBalanceData", "HasTrialBalanceData", default=False),
            latest_trial_balance_year=self._get_field(workspace, "latestTrialBalanceYear", "LatestTrialBalanceYear"),
            candidate_count=len(self._get_materiality_candidates()),
            calculation_count=len(self._get_materiality_calculations()),
            active_calculation=self._get_field(active_calculation, "calculationSummary", "CalculationSummary"),
            form_state=self.materiality_form_state.copy(),
        )

        def update_profile_summary(profile):
            profile_name = self._get_field(profile, "profileName", "ProfileName", default="No profile selected")
            validation_status = self._get_field(profile, "validationStatus", "ValidationStatus", default="No validation status captured")
            profile_status_text.value = f"Profile: {profile_name} | Validation: {validation_status}"
            profile_status_text.color = "#475569"
            profile_notes_text.value = self._get_field(profile, "validationNotes", "ValidationNotes", default=self._get_field(profile, "benchmarkRationale", "BenchmarkRationale", default="Select a profile to load benchmark defaults and capture the engagement rationale."))

        def apply_profile_defaults(profile):
            if not profile:
                update_profile_summary({})
                return

            default_map = [
                (profit_before_tax_field, "profitBeforeTaxPercentage", "ProfitBeforeTaxPercentage"),
                (revenue_field, "revenuePercentage", "RevenuePercentage"),
                (total_assets_field, "totalAssetsPercentage", "TotalAssetsPercentage"),
                (expenses_field, "expensesPercentage", "ExpensesPercentage"),
                (performance_field, "performancePercentage", "PerformancePercentage"),
                (clearly_trivial_field, "clearlyTrivialPercentage", "ClearlyTrivialPercentage"),
            ]
            for field, camel_key, pascal_key in default_map:
                field.value = str(self._get_field(profile, camel_key, pascal_key, default="") or "")
            if self._get_field(profile, "entityType", "EntityType", default=""):
                entity_type_field.value = self._get_field(profile, "entityType", "EntityType", default="")
            if self._get_field(profile, "industryName", "IndustryName", default=""):
                industry_name_field.value = self._get_field(profile, "industryName", "IndustryName", default="")

            self.materiality_form_state.update(
                {
                    "benchmark_profile_id": str(self._get_field(profile, "id", "Id", default="") or ""),
                    "entity_type": entity_type_field.value,
                    "industry_name": industry_name_field.value,
                    "profit_before_tax_percentage": profit_before_tax_field.value,
                    "revenue_percentage": revenue_field.value,
                    "total_assets_percentage": total_assets_field.value,
                    "expenses_percentage": expenses_field.value,
                    "performance_percentage": performance_field.value,
                    "clearly_trivial_percentage": clearly_trivial_field.value,
                }
            )
            update_profile_summary(profile)

        def on_profile_change(change):
            selected_profile_value = (change.control.value or "").strip()
            self._update_materiality_form_state("benchmark_profile_id", selected_profile_value)
            apply_profile_defaults(self._find_materiality_profile(selected_profile_value))
            self._log_materiality_event("materiality_profile_changed", benchmark_profile_id=selected_profile_value)
            if self.page:
                self.page.update()

        profile_dropdown.on_change = on_profile_change
        apply_profile_defaults(selected_profile)

        for key, field in [
            ("entity_type", entity_type_field),
            ("industry_name", industry_name_field),
            ("benchmark_selection_rationale", benchmark_selection_rationale_field),
            ("fiscal_year", fiscal_year_field),
            ("profit_before_tax_percentage", profit_before_tax_field),
            ("revenue_percentage", revenue_field),
            ("total_assets_percentage", total_assets_field),
            ("expenses_percentage", expenses_field),
            ("performance_percentage", performance_field),
            ("clearly_trivial_percentage", clearly_trivial_field),
            ("rationale", rationale_field),
            ("manual_benchmark_name", manual_benchmark_name_field),
            ("manual_benchmark_code", manual_benchmark_code_field),
            ("manual_benchmark_amount", manual_benchmark_amount_field),
            ("manual_percentage", manual_percentage_field),
        ]:
            field.on_change = lambda change, state_key=key: self._update_materiality_form_state(state_key, change.control.value)

        def on_dataset_change(change):
            selected_dataset = (change.control.value or "trial_balance").strip() or "trial_balance"
            self.materiality_import_dataset_type = selected_dataset
            self.pending_materiality_import_file = None
            self.materiality_import_validation = None
            self.materiality_selected_file_text.value = f"No {dataset_label_map.get(selected_dataset, 'materiality')} CSV selected"
            if selected_dataset == "trial_balance":
                self.materiality_validation_text.value = "Import a trial balance CSV to calculate benchmark candidates from balances."
            else:
                self.materiality_validation_text.value = "Import a journal-entry CSV to stratify transactions into key items and sample pool."
            self.materiality_validation_text.color = "#475569"
            self.materiality_preview_column.controls = [ft.Text("No preview available", size=12, color="#64748b")]
            self.materiality_import_button.disabled = True
            self._log_materiality_event("materiality_import_dataset_changed", dataset_type=selected_dataset)
            if self.page:
                self.page.update()

        materiality_dataset_dropdown.on_change = on_dataset_change

        def render_candidates():
            candidates_column.controls.clear()
            candidates = self._get_materiality_candidates()
            if not candidates:
                candidates_column.controls.append(
                    ft.Container(
                        padding=12,
                        bgcolor="#f8fafc",
                        border_radius=10,
                        content=ft.Text("No benchmark candidates generated yet.", size=12, color="#64748b"),
                    )
                )
                return

            for candidate in candidates:
                candidate_name = self._get_field(candidate, "candidateName", "CandidateName", default="Candidate")
                recommended_percentage = self._get_field(candidate, "recommendedPercentage", "RecommendedPercentage", default=0)
                overall_value = self._get_field(candidate, "recommendedOverallMateriality", "RecommendedOverallMateriality", default=0)
                performance_value = self._get_field(candidate, "recommendedPerformanceMateriality", "RecommendedPerformanceMateriality", default=0)
                trivial_value = self._get_field(candidate, "recommendedClearlyTrivialThreshold", "RecommendedClearlyTrivialThreshold", default=0)
                profile_name = self._get_field(candidate, "benchmarkProfileName", "BenchmarkProfileName", default="No profile")
                validation_status = self._get_field(candidate, "benchmarkProfileValidationStatus", "BenchmarkProfileValidationStatus", default="Not validated")
                context_bits = [
                    self._get_field(candidate, "entityType", "EntityType", default=""),
                    self._get_field(candidate, "industryName", "IndustryName", default=""),
                ]

                candidates_column.controls.append(
                    ft.Card(
                        content=ft.Container(
                            padding=14,
                            content=ft.Column(
                                [
                                    ft.Row(
                                        [
                                            ft.Text(candidate_name, weight=ft.FontWeight.BOLD, color="#1e293b"),
                                            ft.Container(expand=True),
                                            ft.Container(
                                                content=ft.Text(f"{recommended_percentage}%", size=11, color="white"),
                                                bgcolor="#2563eb",
                                                padding=ft.padding.symmetric(horizontal=10, vertical=5),
                                                border_radius=999,
                                            ),
                                            ft.FilledButton(
                                                "Set Active",
                                                icon=Icons.CHECK_CIRCLE,
                                                on_click=lambda _, selected=candidate: self.page.run_task(activate_candidate(selected)),
                                            ),
                                        ]
                                    ),
                                    ft.Text(
                                        self._get_field(candidate, "notes", "Notes", default=""),
                                        size=11,
                                        color="#64748b",
                                    ),
                                    ft.Text(
                                        " | ".join(bit for bit in [profile_name, validation_status] if bit),
                                        size=11,
                                        color="#334155",
                                    ),
                                    ft.Text(
                                        " | ".join(bit for bit in context_bits if bit) or "No entity or industry context captured",
                                        size=11,
                                        color="#64748b",
                                    ),
                                    ft.ResponsiveRow(
                                        [
                                            ft.Container(col={"sm": 12, "md": 4}, content=self._create_info_row("Benchmark", self._format_materiality_value(self._get_field(candidate, "benchmarkAmount", "BenchmarkAmount", default=0)))),
                                            ft.Container(col={"sm": 12, "md": 4}, content=self._create_info_row("Overall", self._format_materiality_value(overall_value))),
                                            ft.Container(col={"sm": 12, "md": 4}, content=self._create_info_row("Performance", self._format_materiality_value(performance_value))),
                                        ],
                                        run_spacing=8,
                                    ),
                                    self._create_info_row("Clearly Trivial", self._format_materiality_value(trivial_value)),
                                ],
                                spacing=6,
                            ),
                        )
                    )
                )

        def render_history():
            history_column.controls.clear()
            calculations = self._get_materiality_calculations()
            if not calculations:
                history_column.controls.append(
                    ft.Container(
                        padding=12,
                        bgcolor="#f8fafc",
                        border_radius=10,
                        content=ft.Text("No calculation history captured yet.", size=12, color="#64748b"),
                    )
                )
                return

            for calculation in calculations[:5]:
                is_active = bool(self._get_field(calculation, "isActive", "IsActive", default=False))
                profile_name = self._get_field(calculation, "benchmarkProfileName", "BenchmarkProfileName", default="No profile")
                validation_status = self._get_field(calculation, "benchmarkProfileValidationStatus", "BenchmarkProfileValidationStatus", default="No validation state")
                selection_rationale = self._get_field(calculation, "benchmarkSelectionRationale", "BenchmarkSelectionRationale", default="")
                history_column.controls.append(
                    ft.Container(
                        padding=12,
                        bgcolor="#eff6ff" if is_active else "#f8fafc",
                        border_radius=10,
                        content=ft.Row(
                            [
                                ft.Column(
                                    [
                                        ft.Text(
                                            self._get_field(calculation, "calculationSummary", "CalculationSummary", default="Calculation"),
                                            weight=ft.FontWeight.BOLD,
                                            color="#1e293b",
                                        ),
                                        ft.Text(
                                            f"Overall {self._format_materiality_value(self._get_field(calculation, 'overallMateriality', 'OverallMateriality', default=0))} | "
                                            f"Performance {self._format_materiality_value(self._get_field(calculation, 'performanceMateriality', 'PerformanceMateriality', default=0))}",
                                            size=11,
                                            color="#64748b",
                                        ),
                                        ft.Text(
                                            " | ".join(bit for bit in [profile_name, validation_status] if bit),
                                            size=11,
                                            color="#334155",
                                        ),
                                        ft.Text(
                                            selection_rationale or "No benchmark selection rationale captured",
                                            size=11,
                                            color="#64748b",
                                        ),
                                    ],
                                    spacing=4,
                                    expand=True,
                                ),
                                ft.Container(
                                    content=ft.Text("Active" if is_active else "History", size=11, color="white"),
                                    bgcolor="#0f766e" if is_active else "#64748b",
                                    padding=ft.padding.symmetric(horizontal=10, vertical=5),
                                    border_radius=999,
                                ),
                            ]
                        ),
                    )
                )

        def render_approval_history():
            approval_history_column.controls.clear()
            entries = self._get_materiality_approval_history()
            if not entries:
                approval_history_column.controls.append(
                    ft.Container(
                        padding=12,
                        bgcolor="#f8fafc",
                        border_radius=10,
                        content=ft.Text("No approval history captured yet.", size=12, color="#64748b"),
                    )
                )
                return

            for entry in entries[:6]:
                approval_history_column.controls.append(
                    ft.Container(
                        padding=12,
                        bgcolor="#ffffff",
                        border=ft.border.all(1, "#e2e8f0"),
                        border_radius=10,
                        content=ft.Column(
                            [
                                ft.Row(
                                    [
                                        ft.Text(
                                            self._get_field(entry, "actionLabel", "ActionLabel", default="Materiality approval"),
                                            weight=ft.FontWeight.BOLD,
                                            color="#1e293b",
                                        ),
                                        ft.Container(expand=True),
                                        ft.Text(
                                            format_date(self._get_field(entry, "approvedAt", "ApprovedAt", default=None)) or "Pending date",
                                            size=11,
                                            color="#64748b",
                                        ),
                                    ]
                                ),
                                ft.Text(
                                    " | ".join(
                                        bit for bit in [
                                            self._get_field(entry, "benchmarkProfileName", "BenchmarkProfileName", default=""),
                                            self._get_field(entry, "approvedByName", "ApprovedByName", default=""),
                                        ] if bit
                                    ) or "No profile or approver captured",
                                    size=11,
                                    color="#334155",
                                ),
                                ft.Text(
                                    self._get_field(entry, "benchmarkSelectionRationale", "BenchmarkSelectionRationale", default="")
                                    or self._get_field(entry, "overrideReason", "OverrideReason", default="")
                                    or "No rationale captured",
                                    size=11,
                                    color="#64748b",
                                ),
                                ft.Text(
                                    f"Overall {self._format_materiality_value(self._get_field(entry, 'overallMateriality', 'OverallMateriality', default=0))} | "
                                    f"Performance {self._format_materiality_value(self._get_field(entry, 'performanceMateriality', 'PerformanceMateriality', default=0))} | "
                                    f"Clearly trivial {self._format_materiality_value(self._get_field(entry, 'clearlyTrivialThreshold', 'ClearlyTrivialThreshold', default=0))}",
                                    size=11,
                                    color="#0f172a",
                                ),
                            ],
                            spacing=4,
                        ),
                    )
                )

        async def refresh_workspace():
            self.materiality_workspace = await self.assessment_controller.auditing_client.get_materiality_workspace(reference_id)
            refreshed_profile = self._get_selected_materiality_profile() or {}
            if self._get_field(refreshed_profile, "id", "Id", default=None):
                profile_dropdown.value = str(self._get_field(refreshed_profile, "id", "Id"))
                apply_profile_defaults(refreshed_profile)
            else:
                update_profile_summary({})
            self._log_materiality_event(
                "workspace_refreshed",
                candidate_count=len(self._get_materiality_candidates()),
                calculation_count=len(self._get_materiality_calculations()),
                active_calculation=self._get_field(self._get_active_materiality_calculation(), "calculationSummary", "CalculationSummary"),
            )
            render_candidates()
            render_history()
            render_approval_history()

        async def refresh_planning_snapshot():
            try:
                self.planning_data = await self.assessment_controller.auditing_client.get_planning_by_reference(reference_id)
                self._log_materiality_event(
                    "planning_snapshot_refreshed",
                    materiality_basis=self._get_materiality_basis_label(),
                    overall=self._get_active_materiality_value("overallMateriality", "OverallMateriality"),
                )
            except Exception as ex:
                self._log_materiality_event("planning_snapshot_refresh_failed", level="error", error=str(ex))

        async def keep_dialog_open_after_success(success_message, activity_action, icon, color):
            try:
                await refresh_workspace()
                await refresh_planning_snapshot()
                await self._append_activity_event(activity_action, icon, color)
                self._log_materiality_event("materiality_dialog_success_activity_recorded", activity_action=activity_action)
            except Exception as ex:
                self._log_materiality_event("materiality_dialog_success_followup_failed", level="error", error=str(ex))

            status_text.value = success_message
            status_text.color = "#15803d"
            try:
                self._show_success(success_message)
            except Exception as ex:
                self._log_materiality_event("materiality_dialog_success_snackbar_failed", level="error", error=str(ex))
            if self.page:
                self.page.update()

        async def import_trial_balance_csv():
            self._log_materiality_event(
                "import_csv_clicked",
                pending_file=self.pending_materiality_import_file,
                validation=self.materiality_import_validation,
                dataset_type=self.materiality_import_dataset_type,
            )
            if not self.pending_materiality_import_file or not self.pending_materiality_import_file.get("path"):
                status_text.value = "Select a trial balance CSV file first."
                status_text.color = "#dc2626"
                self._log_materiality_event("import_csv_blocked_no_file", level="warning")
                self.page.update()
                return
            if not self.materiality_import_validation or not self.materiality_import_validation.get("is_valid"):
                status_text.value = "Fix the CSV validation issue before importing."
                status_text.color = "#dc2626"
                self._log_materiality_event("import_csv_blocked_validation", level="warning", validation=self.materiality_import_validation)
                self.page.update()
                return

            try:
                dataset_type = self.materiality_import_dataset_type or "trial_balance"
                dataset_label = "trial balance" if dataset_type == "trial_balance" else "journal-entry"
                status_text.value = f"Importing {dataset_label} CSV..."
                status_text.color = "#475569"
                self.materiality_import_button.disabled = True
                self._log_materiality_event("import_csv_started", file_path=self.pending_materiality_import_file.get("path"), dataset_type=dataset_type)
                self.page.update()
                result = await self.assessment_controller.auditing_client.upload_audit_analytics_file(
                    self.pending_materiality_import_file["path"],
                    {
                        "referenceId": reference_id,
                        "datasetType": dataset_type,
                        "batchName": f"Materiality {dataset_label.title()} {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                        "sourceSystem": "Materiality Calculator",
                        "importedByUserId": self._normalize_user_id(),
                        "importedByName": self._get_current_user_name(),
                        "notes": "Imported from the materiality calculator workflow",
                    },
                )
                await refresh_workspace()
                rows_imported = result.get("rowCount", 0) if isinstance(result, dict) else 0
                if dataset_type == "trial_balance":
                    status_text.value = f"Imported {rows_imported:,} trial balance rows. Generate candidates to refresh benchmarks."
                else:
                    status_text.value = f"Imported {rows_imported:,} journal-entry rows. The materiality application summary will use them against performance materiality."
                status_text.color = "#15803d"
                self.materiality_import_button.disabled = False
                self._log_materiality_event("import_csv_completed", rows_imported=rows_imported, result=result, dataset_type=dataset_type)
                self.page.update()
            except Exception as ex:
                status_text.value = f"Trial balance import failed: {str(ex)}"
                status_text.color = "#dc2626"
                self.materiality_import_button.disabled = False
                self._log_materiality_event("import_csv_failed", level="error", error=str(ex))
                self.page.update()

        async def create_manual_calculation():
            self._log_materiality_event("create_manual_clicked", form_state=self.materiality_form_state.copy())
            benchmark_amount = self._parse_optional_decimal(self.materiality_form_state.get("manual_benchmark_amount"))
            benchmark_percentage = self._parse_optional_decimal(self.materiality_form_state.get("manual_percentage"))
            performance_percentage = self._parse_optional_decimal(self.materiality_form_state.get("performance_percentage"))
            clearly_trivial_percentage = self._parse_optional_decimal(self.materiality_form_state.get("clearly_trivial_percentage"))

            if benchmark_amount is None or benchmark_percentage is None or performance_percentage is None or clearly_trivial_percentage is None:
                status_text.value = "Enter valid benchmark, percentage, performance, and clearly trivial values before saving."
                status_text.color = "#dc2626"
                self._log_materiality_event(
                    "create_manual_blocked_invalid_numbers",
                    level="warning",
                    benchmark_amount=self.materiality_form_state.get("manual_benchmark_amount"),
                    benchmark_percentage=self.materiality_form_state.get("manual_percentage"),
                    performance_percentage=self.materiality_form_state.get("performance_percentage"),
                    clearly_trivial_percentage=self.materiality_form_state.get("clearly_trivial_percentage"),
                )
                self.page.update()
                return
            benchmark_name = (self.materiality_form_state.get("manual_benchmark_name") or "").strip()
            benchmark_code = (self.materiality_form_state.get("manual_benchmark_code") or "manual_custom").strip()
            rationale = (self.materiality_form_state.get("rationale") or "").strip()
            benchmark_profile_id = self._parse_optional_int(self.materiality_form_state.get("benchmark_profile_id"))
            entity_type = (self.materiality_form_state.get("entity_type") or "").strip()
            industry_name = (self.materiality_form_state.get("industry_name") or "").strip()
            benchmark_selection_rationale = (self.materiality_form_state.get("benchmark_selection_rationale") or "").strip()
            if not benchmark_name:
                status_text.value = "Manual benchmark name is required."
                status_text.color = "#dc2626"
                self.page.update()
                self._log_materiality_event("create_manual_blocked_missing_name", level="warning")
                self._show_error("Manual benchmark name is required")
                return

            try:
                status_text.value = "Saving manual materiality calculation..."
                status_text.color = "#475569"
                self._log_materiality_event(
                    "create_manual_started",
                    benchmark_name=benchmark_name,
                    benchmark_code=benchmark_code,
                    benchmark_amount=benchmark_amount,
                    benchmark_percentage=benchmark_percentage,
                    performance_percentage=performance_percentage,
                    clearly_trivial_percentage=clearly_trivial_percentage,
                    benchmark_profile_id=benchmark_profile_id,
                    entity_type=entity_type,
                    industry_name=industry_name,
                )
                self.page.update()
                result = await self.assessment_controller.auditing_client.create_materiality_calculation(
                    {
                        "referenceId": reference_id,
                        "benchmarkProfileId": benchmark_profile_id,
                        "benchmarkCode": benchmark_code,
                        "benchmarkName": benchmark_name,
                        "benchmarkAmount": benchmark_amount,
                        "percentageApplied": benchmark_percentage,
                        "performancePercentageApplied": performance_percentage,
                        "clearlyTrivialPercentageApplied": clearly_trivial_percentage,
                        "isManualOverride": True,
                        "setAsActive": True,
                        "rationale": rationale,
                        "entityType": entity_type,
                        "industryName": industry_name,
                        "benchmarkSelectionRationale": benchmark_selection_rationale,
                        "createdByUserId": self._normalize_user_id(),
                        "createdByName": self._get_current_user_name(),
                    }
                )
                self._log_materiality_event("create_manual_completed", result=result)
                await keep_dialog_open_after_success(
                    "Manual materiality calculation activated. Review the updated history below or close the dialog when done.",
                    "created a manual materiality calculation",
                    "EDIT_NOTE",
                    "#7c3aed",
                )
            except Exception as ex:
                status_text.value = f"Failed to save manual calculation: {str(ex)}"
                status_text.color = "#dc2626"
                self._log_materiality_event("create_manual_failed", level="error", error=str(ex))
                self.page.update()

        async def generate_candidates():
            self._log_materiality_event("generate_candidates_clicked", form_state=self.materiality_form_state.copy())
            fiscal_year = self._parse_optional_int(self.materiality_form_state.get("fiscal_year"))
            benchmark_profile_id = self._parse_optional_int(self.materiality_form_state.get("benchmark_profile_id"))
            entity_type = (self.materiality_form_state.get("entity_type") or "").strip()
            industry_name = (self.materiality_form_state.get("industry_name") or "").strip()
            percentage_values = {
                "profitBeforeTaxPercentage": self._parse_optional_decimal(self.materiality_form_state.get("profit_before_tax_percentage")),
                "revenuePercentage": self._parse_optional_decimal(self.materiality_form_state.get("revenue_percentage")),
                "totalAssetsPercentage": self._parse_optional_decimal(self.materiality_form_state.get("total_assets_percentage")),
                "expensesPercentage": self._parse_optional_decimal(self.materiality_form_state.get("expenses_percentage")),
                "performancePercentage": self._parse_optional_decimal(self.materiality_form_state.get("performance_percentage")),
                "clearlyTrivialPercentage": self._parse_optional_decimal(self.materiality_form_state.get("clearly_trivial_percentage")),
            }
            if any(value is None for value in percentage_values.values()):
                status_text.value = "Enter valid numeric percentages before generating candidates."
                status_text.color = "#dc2626"
                self._log_materiality_event("generate_candidates_blocked_invalid_numbers", level="warning", percentage_values=self.materiality_form_state.copy())
                self.page.update()
                return

            try:
                status_text.value = "Generating benchmark candidates..."
                status_text.color = "#475569"
                self._log_materiality_event(
                    "generate_candidates_started",
                    fiscal_year=fiscal_year,
                    benchmark_profile_id=benchmark_profile_id,
                    entity_type=entity_type,
                    industry_name=industry_name,
                    percentage_values=percentage_values,
                )
                self.page.update()
                result = await self.assessment_controller.auditing_client.generate_materiality_candidates(
                    {
                        "referenceId": reference_id,
                        "fiscalYear": fiscal_year,
                        "benchmarkProfileId": benchmark_profile_id,
                        "entityType": entity_type,
                        "industryName": industry_name,
                        "generatedByUserId": self._normalize_user_id(),
                        "generatedByName": self._get_current_user_name(),
                        **percentage_values,
                    }
                )
                await refresh_workspace()
                status_text.value = "Benchmark candidates generated. Choose the one that fits the engagement."
                status_text.color = "#15803d"
                self._log_materiality_event("generate_candidates_completed", result=result)
                self.page.update()
            except Exception as ex:
                status_text.value = f"Candidate generation failed: {str(ex)}"
                status_text.color = "#dc2626"
                self._log_materiality_event("generate_candidates_failed", level="error", error=str(ex))
                self.page.update()

        async def activate_candidate(candidate):
            try:
                status_text.value = "Creating active materiality calculation..."
                self.page.update()
                self._log_materiality_event(
                    "activate_candidate_started",
                    candidate_id=self._get_field(candidate, "id", "Id"),
                    candidate_name=self._get_field(candidate, "candidateName", "CandidateName"),
                )
                result = await self.assessment_controller.auditing_client.create_materiality_calculation(
                    {
                        "referenceId": reference_id,
                        "candidateId": self._get_field(candidate, "id", "Id"),
                        "benchmarkProfileId": self._parse_optional_int(self.materiality_form_state.get("benchmark_profile_id")),
                        "setAsActive": True,
                        "rationale": rationale_field.value.strip() if rationale_field.value else "",
                        "entityType": (self.materiality_form_state.get("entity_type") or "").strip(),
                        "industryName": (self.materiality_form_state.get("industry_name") or "").strip(),
                        "benchmarkSelectionRationale": (self.materiality_form_state.get("benchmark_selection_rationale") or "").strip(),
                        "createdByUserId": self._normalize_user_id(),
                        "createdByName": self._get_current_user_name(),
                    }
                )
                self._log_materiality_event("activate_candidate_completed", result=result)
                await keep_dialog_open_after_success(
                    "Materiality calculation activated. Review the updated history below or close the dialog when done.",
                    "calculated materiality from imported financial data",
                    "CALCULATE",
                    "#2563eb",
                )
            except Exception as ex:
                status_text.value = f"Failed to activate calculation: {str(ex)}"
                status_text.color = "#dc2626"
                self._log_materiality_event("activate_candidate_failed", level="error", error=str(ex))
                self.page.update()

        render_candidates()
        render_history()
        render_approval_history()

        self.materiality_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Materiality Calculator"),
            content=ft.Column(
                [
                    ft.Text(
                        "Import or update the trial balance here, generate benchmark candidates from those balances, or create a manual calculation directly in this workflow.",
                        size=12,
                        color="#475569",
                    ),
                    ft.Container(
                        padding=12,
                        bgcolor="#f8fafc",
                        border=ft.border.all(1, "#e2e8f0"),
                        border_radius=10,
                        content=ft.Column(
                            [
                                ft.Text("Materiality Data Import", weight=ft.FontWeight.BOLD),
                                materiality_dataset_dropdown,
                                ft.Row(
                                    [
                                        ft.OutlinedButton("Select CSV", icon=Icons.UPLOAD_FILE, on_click=self._pick_materiality_import_file),
                                        self.materiality_import_button,
                                    ],
                                    spacing=10,
                                ),
                                self.materiality_selected_file_text,
                                self.materiality_validation_text,
                                ft.Container(
                                    height=110,
                                    padding=8,
                                    bgcolor="#ffffff",
                                    border=ft.border.all(1, "#dbe3ef"),
                                    border_radius=8,
                                    content=self.materiality_preview_column,
                                ),
                            ],
                            spacing=8,
                        ),
                    ),
                    ft.Container(
                        padding=12,
                        bgcolor="#fff7ed",
                        border=ft.border.all(1, "#fdba74"),
                        border_radius=10,
                        content=ft.Column(
                            [
                                ft.Text("Benchmark Profile & Context", weight=ft.FontWeight.BOLD),
                                profile_dropdown,
                                profile_status_text,
                                profile_notes_text,
                                ft.ResponsiveRow(
                                    [
                                        ft.Container(col={"sm": 12, "md": 6}, content=entity_type_field),
                                        ft.Container(col={"sm": 12, "md": 6}, content=industry_name_field),
                                    ],
                                    run_spacing=10,
                                ),
                                benchmark_selection_rationale_field,
                            ],
                            spacing=8,
                        ),
                    ),
                    ft.ResponsiveRow(
                        [
                            ft.Container(col={"sm": 12, "md": 4}, content=fiscal_year_field),
                            ft.Container(col={"sm": 12, "md": 4}, content=profit_before_tax_field),
                            ft.Container(col={"sm": 12, "md": 4}, content=revenue_field),
                            ft.Container(col={"sm": 12, "md": 4}, content=total_assets_field),
                            ft.Container(col={"sm": 12, "md": 4}, content=expenses_field),
                            ft.Container(col={"sm": 12, "md": 4}, content=performance_field),
                            ft.Container(col={"sm": 12, "md": 4}, content=clearly_trivial_field),
                        ],
                        run_spacing=10,
                    ),
                    rationale_field,
                    status_text,
                    ft.Divider(),
                    ft.Text("Manual Calculation", weight=ft.FontWeight.BOLD),
                    ft.ResponsiveRow(
                        [
                            ft.Container(col={"sm": 12, "md": 6}, content=manual_benchmark_name_field),
                            ft.Container(col={"sm": 12, "md": 6}, content=manual_benchmark_code_field),
                            ft.Container(col={"sm": 12, "md": 6}, content=manual_benchmark_amount_field),
                            ft.Container(col={"sm": 12, "md": 6}, content=manual_percentage_field),
                        ],
                        run_spacing=10,
                    ),
                    ft.Row(
                        [
                            ft.Container(expand=True),
                            ft.OutlinedButton("Create Manual Calculation", icon=Icons.EDIT_NOTE, on_click=lambda _: self.page.run_task(create_manual_calculation)),
                        ],
                        alignment=ft.MainAxisAlignment.END,
                    ),
                    ft.Divider(),
                    ft.Text("Benchmark Candidates", weight=ft.FontWeight.BOLD),
                    candidates_column,
                    ft.Divider(),
                    ft.Text("Recent Calculation History", weight=ft.FontWeight.BOLD),
                    history_column,
                    ft.Divider(),
                    ft.Text("Approval History", weight=ft.FontWeight.BOLD),
                    approval_history_column,
                ],
                width=820,
                height=640,
                scroll=ft.ScrollMode.AUTO,
            ),
            actions=[
                ft.TextButton(
                    "Close",
                    on_click=lambda _: (
                        self._close_active_dialog(self.materiality_dialog),
                        self.page.run_task(self._refresh_materiality_view_state)
                    ),
                ),
                ft.FilledButton("Generate Candidates", icon=Icons.AUTO_GRAPH, on_click=lambda _: self.page.run_task(generate_candidates)),
            ],
        )
        self._open_dialog(self.materiality_dialog)

    def _open_planning_dialog(self, e=None):
        current_plan = self.planning_data or {}
        current_signed_off = bool(self._get_field(current_plan, "isSignedOff", "IsSignedOff", default=False))
        current_signed_off_at = self._get_field(current_plan, "signedOffAt", "SignedOffAt")
        current_scope_letter = self._get_field(current_plan, "scopeLetterDocumentId", "ScopeLetterDocumentId")

        engagement_title_field = ft.TextField(
            label="Engagement Title",
            value=self._get_field(current_plan, "engagementTitle", "EngagementTitle", default=""),
            autofocus=True
        )
        plan_year_field = ft.TextField(
            label="Plan Year",
            value=str(self._get_field(current_plan, "planYear", "PlanYear", default="") or "")
        )
        annual_plan_field = ft.TextField(
            label="Annual Plan Name",
            value=self._get_field(current_plan, "annualPlanName", "AnnualPlanName", default="")
        )
        business_unit_field = ft.TextField(
            label="Business Unit",
            value=self._get_field(current_plan, "businessUnit", "BusinessUnit", default="")
        )
        process_area_field = ft.TextField(
            label="Process Area",
            value=self._get_field(current_plan, "processArea", "ProcessArea", default="")
        )
        sub_process_field = ft.TextField(
            label="Sub-process Area",
            value=self._get_field(current_plan, "subProcessArea", "SubProcessArea", default="")
        )
        fsli_field = ft.TextField(
            label="FSLI",
            value=self._get_field(current_plan, "fsli", "Fsli", default="")
        )
        scope_summary_field = ft.TextField(
            label="Scope Summary",
            multiline=True,
            min_lines=2,
            max_lines=4,
            value=self._get_field(current_plan, "scopeSummary", "ScopeSummary", default="")
        )
        materiality_field = ft.TextField(
            label="Materiality / Thresholds",
            multiline=True,
            min_lines=2,
            max_lines=3,
            value=self._get_field(current_plan, "materiality", "Materiality", default="")
        )
        materiality_basis_field = ft.TextField(
            label="Materiality Basis (External Audit)",
            value=self._get_field(current_plan, "materialityBasis", "MaterialityBasis", default="")
        )
        overall_materiality_field = ft.TextField(
            label="Overall Materiality",
            value=str(self._get_field(current_plan, "overallMateriality", "OverallMateriality", default="") or "")
        )
        performance_materiality_field = ft.TextField(
            label="Performance Materiality",
            value=str(self._get_field(current_plan, "performanceMateriality", "PerformanceMateriality", default="") or "")
        )
        clearly_trivial_threshold_field = ft.TextField(
            label="Clearly Trivial Threshold",
            value=str(self._get_field(current_plan, "clearlyTrivialThreshold", "ClearlyTrivialThreshold", default="") or "")
        )
        risk_strategy_field = ft.TextField(
            label="Risk Strategy",
            multiline=True,
            min_lines=2,
            max_lines=3,
            value=self._get_field(current_plan, "riskStrategy", "RiskStrategy", default="")
        )
        notes_field = ft.TextField(
            label="Planning Notes",
            multiline=True,
            min_lines=2,
            max_lines=4,
            value=self._get_field(current_plan, "notes", "Notes", default="")
        )
        engagement_type_dropdown = ft.Dropdown(
            label="Engagement Type",
            options=[
                ft.dropdown.Option(
                    key=str(self._get_field(item, "id", "Id")),
                    text=self._get_field(item, "name", "Name", default="Type")
                )
                for item in self.engagement_types or []
            ],
            value=str(self._get_field(current_plan, "engagementTypeId", "EngagementTypeId")) if self._get_field(current_plan, "engagementTypeId", "EngagementTypeId") else None
        )
        planning_status_dropdown = ft.Dropdown(
            label="Planning Status",
            options=[
                ft.dropdown.Option(
                    key=str(self._get_field(item, "id", "Id")),
                    text=self._get_field(item, "name", "Name", default="Status")
                )
                for item in self.planning_statuses or []
            ],
            value=str(self._get_field(current_plan, "planningStatusId", "PlanningStatusId")) if self._get_field(current_plan, "planningStatusId", "PlanningStatusId") else None
        )
        scope_letter_dropdown = ft.Dropdown(
            label="Scope Letter Document",
            options=[
                ft.dropdown.Option(
                    key=str(self._get_field(document, "id", "Id")),
                    text=self._get_field(document, "title", "Title", default="Document")
                )
                for document in self.documents_data or []
            ],
            value=str(current_scope_letter) if current_scope_letter else None
        )
        sign_off_checkbox = ft.Checkbox(label="Planning signed off", value=current_signed_off)
        signed_off_by_field = ft.TextField(
            label="Signed Off By",
            value=self._get_field(current_plan, "signedOffByName", "SignedOffByName", default=self._get_current_user_name() if current_signed_off else "")
        )

        def on_signoff_change(event):
            if event.control.value and not signed_off_by_field.value:
                signed_off_by_field.value = self._get_current_user_name() or ""
            if not event.control.value:
                signed_off_by_field.value = ""
            self.page.update()

        sign_off_checkbox.on_change = on_signoff_change

        async def save_planning():
            plan_year_value = None
            if plan_year_field.value and plan_year_field.value.strip():
                if not plan_year_field.value.strip().isdigit():
                    self._show_error("Plan year must be numeric")
                    return
                plan_year_value = int(plan_year_field.value.strip())

            overall_materiality_value = self._parse_optional_decimal(overall_materiality_field.value)
            performance_materiality_value = self._parse_optional_decimal(performance_materiality_field.value)
            clearly_trivial_threshold_value = self._parse_optional_decimal(clearly_trivial_threshold_field.value)
            numeric_fields = [
                (overall_materiality_field.value, overall_materiality_value),
                (performance_materiality_field.value, performance_materiality_value),
                (clearly_trivial_threshold_field.value, clearly_trivial_threshold_value),
            ]
            if any((raw or "").strip() and parsed is None for raw, parsed in numeric_fields):
                return

            planning_status_id = int(planning_status_dropdown.value) if planning_status_dropdown.value else None
            if sign_off_checkbox.value:
                signed_off_status_id = next(
                    (
                        self._get_field(item, "id", "Id")
                        for item in self.planning_statuses or []
                        if (self._get_field(item, "name", "Name", default="") or "").strip().lower() == "signed off"
                    ),
                    None
                )
                if signed_off_status_id:
                    planning_status_id = int(signed_off_status_id)

            payload = {
                "id": self._get_field(current_plan, "id", "Id"),
                "referenceId": self._normalize_reference_id(),
                "engagementTitle": engagement_title_field.value.strip() if engagement_title_field.value else "",
                "engagementTypeId": int(engagement_type_dropdown.value) if engagement_type_dropdown.value else None,
                "planYear": plan_year_value,
                "annualPlanName": annual_plan_field.value.strip() if annual_plan_field.value else "",
                "businessUnit": business_unit_field.value.strip() if business_unit_field.value else "",
                "processArea": process_area_field.value.strip() if process_area_field.value else "",
                "subProcessArea": sub_process_field.value.strip() if sub_process_field.value else "",
                "fsli": fsli_field.value.strip() if fsli_field.value else "",
                "scopeSummary": scope_summary_field.value.strip() if scope_summary_field.value else "",
                "materiality": materiality_field.value.strip() if materiality_field.value else "",
                "materialityBasis": materiality_basis_field.value.strip() if materiality_basis_field.value else "",
                "overallMateriality": overall_materiality_value,
                "performanceMateriality": performance_materiality_value,
                "clearlyTrivialThreshold": clearly_trivial_threshold_value,
                "riskStrategy": risk_strategy_field.value.strip() if risk_strategy_field.value else "",
                "planningStatusId": planning_status_id,
                "scopeLetterDocumentId": int(scope_letter_dropdown.value) if scope_letter_dropdown.value else None,
                "isSignedOff": bool(sign_off_checkbox.value),
                "signedOffByName": signed_off_by_field.value.strip() if sign_off_checkbox.value and signed_off_by_field.value else "",
                "signedOffByUserId": self._normalize_user_id() if sign_off_checkbox.value else None,
                "signedOffAt": current_signed_off_at if sign_off_checkbox.value and current_signed_off_at else (datetime.now().isoformat() if sign_off_checkbox.value else None),
                "notes": notes_field.value.strip() if notes_field.value else ""
            }

            if not payload["referenceId"] or not payload["engagementTitle"]:
                self._show_error("Reference and engagement title are required")
                return

            try:
                self._show_loading("Saving planning workspace...")
                await self.assessment_controller.auditing_client.upsert_planning(payload)
                self._hide_loading()
                self._close_active_dialog(self.planning_dialog)
                await self._append_activity_event("updated planning and scoping", "EDIT_NOTE", "#1d4ed8")
                self._show_success("Planning workspace updated")
                self.page.run_task(self._load_assessment_data)
            except Exception as ex:
                self._hide_loading()
                self._show_error(f"Failed to save planning workspace: {str(ex)}")

        self.planning_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Planning Workspace"),
            content=ft.Column([
                engagement_title_field,
                engagement_type_dropdown,
                planning_status_dropdown,
                plan_year_field,
                annual_plan_field,
                business_unit_field,
                process_area_field,
                sub_process_field,
                fsli_field,
                scope_summary_field,
                materiality_field,
                materiality_basis_field,
                overall_materiality_field,
                performance_materiality_field,
                clearly_trivial_threshold_field,
                risk_strategy_field,
                ft.Text("Upload the scope letter in Documents first, then link it here.", size=11, color="#64748b"),
                scope_letter_dropdown,
                sign_off_checkbox,
                signed_off_by_field,
                notes_field
            ], tight=True, width=580, height=620, scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: self._close_active_dialog(self.planning_dialog)),
                ft.FilledButton("Save", on_click=lambda _: self.page.run_task(save_planning))
            ]
        )
        self._open_dialog(self.planning_dialog)

    def _open_scope_item_dialog(self, e=None, selected_item=None):
        plan_id = self._get_field(self.planning_data, "id", "Id")
        if not plan_id:
            self._show_error("Save the planning workspace before adding scope items")
            return

        current_item = selected_item or {}
        business_unit_field = ft.TextField(
            label="Business Unit",
            value=self._get_field(current_item, "businessUnit", "BusinessUnit", default="")
        )
        process_name_field = ft.TextField(
            label="Process Name",
            value=self._get_field(current_item, "processName", "ProcessName", default=""),
            autofocus=selected_item is None
        )
        sub_process_field = ft.TextField(
            label="Sub-process Name",
            value=self._get_field(current_item, "subProcessName", "SubProcessName", default="")
        )
        fsli_field = ft.TextField(
            label="FSLI",
            value=self._get_field(current_item, "fsli", "Fsli", default="")
        )
        assertions_field = ft.TextField(
            label="Assertions (comma separated)",
            value=self._get_field(current_item, "assertions", "Assertions", default="")
        )
        scoping_rationale_field = ft.TextField(
            label="Scoping Rationale",
            multiline=True,
            min_lines=2,
            max_lines=4,
            value=self._get_field(current_item, "scopingRationale", "ScopingRationale", default="")
        )
        scope_status_field = ft.TextField(
            label="Scope Status",
            value=self._get_field(current_item, "scopeStatus", "ScopeStatus", default=self._get_engagement_profile().get("scope_status_default", "Planned"))
        )
        include_checkbox = ft.Checkbox(
            label="Include in scope",
            value=bool(self._get_field(current_item, "includeInScope", "IncludeInScope", default=True))
        )
        risk_reference_field = ft.TextField(
            label="Risk Reference",
            value=self._get_field(current_item, "riskReference", "RiskReference", default="")
        )
        control_reference_field = ft.TextField(
            label="Control Reference",
            value=self._get_field(current_item, "controlReference", "ControlReference", default="")
        )
        owner_field = ft.TextField(
            label="Owner",
            value=self._get_field(current_item, "owner", "Owner", default="")
        )
        notes_field = ft.TextField(
            label="Notes",
            multiline=True,
            min_lines=2,
            max_lines=4,
            value=self._get_field(current_item, "notes", "Notes", default="")
        )
        procedure_dropdown = ft.Dropdown(
            label="Procedure",
            options=[
                ft.dropdown.Option(
                    key=str(self._get_field(item, "id", "Id")),
                    text=self._get_field(item, "procedureTitle", "ProcedureTitle", default="Procedure")
                )
                for item in self.procedures_data or []
            ],
            value=str(self._get_field(current_item, "procedureId", "ProcedureId")) if self._get_field(current_item, "procedureId", "ProcedureId") else None
        )

        async def save_scope_item():
            payload = {
                "id": self._get_field(current_item, "id", "Id"),
                "planId": plan_id,
                "referenceId": self._normalize_reference_id(),
                "businessUnit": business_unit_field.value.strip() if business_unit_field.value else "",
                "processName": process_name_field.value.strip() if process_name_field.value else "",
                "subProcessName": sub_process_field.value.strip() if sub_process_field.value else "",
                "fsli": fsli_field.value.strip() if fsli_field.value else "",
                "assertions": assertions_field.value.strip() if assertions_field.value else "",
                "scopingRationale": scoping_rationale_field.value.strip() if scoping_rationale_field.value else "",
                "scopeStatus": scope_status_field.value.strip() if scope_status_field.value else "Planned",
                "includeInScope": bool(include_checkbox.value),
                "riskReference": risk_reference_field.value.strip() if risk_reference_field.value else "",
                "controlReference": control_reference_field.value.strip() if control_reference_field.value else "",
                "procedureId": int(procedure_dropdown.value) if procedure_dropdown.value else None,
                "owner": owner_field.value.strip() if owner_field.value else "",
                "notes": notes_field.value.strip() if notes_field.value else ""
            }

            if not payload["referenceId"] or not payload["processName"]:
                self._show_error("Reference and process name are required")
                return

            try:
                self._show_loading("Saving scope item...")
                if payload["id"]:
                    await self.assessment_controller.auditing_client.update_scope_item(payload["id"], payload)
                    activity = "updated a scope item"
                    message = "Scope item updated"
                else:
                    await self.assessment_controller.auditing_client.create_scope_item(payload)
                    activity = "created a scope item"
                    message = "Scope item created"
                self._hide_loading()
                self._close_active_dialog(self.scope_item_dialog)
                await self._append_activity_event(activity, "ADD_TASK", "#0f766e")
                self._show_success(message)
                self.page.run_task(self._load_assessment_data)
            except Exception as ex:
                self._hide_loading()
                self._show_error(f"Failed to save scope item: {str(ex)}")

        self.scope_item_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Edit Scope Item" if selected_item else "Add Scope Item"),
            content=ft.Column([
                business_unit_field,
                process_name_field,
                sub_process_field,
                fsli_field,
                assertions_field,
                scoping_rationale_field,
                scope_status_field,
                include_checkbox,
                risk_reference_field,
                control_reference_field,
                procedure_dropdown,
                owner_field,
                notes_field
            ], tight=True, width=560, height=540, scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: self._close_active_dialog(self.scope_item_dialog)),
                ft.FilledButton("Save", on_click=lambda _: self.page.run_task(save_scope_item))
            ]
        )
        self._open_dialog(self.scope_item_dialog)

    def _open_edit_scope_item_dialog(self, scope_item):
        self._open_scope_item_dialog(selected_item=scope_item)

    def _delete_scope_item(self, scope_item):
        scope_item_id = self._get_field(scope_item, "id", "Id")
        if not scope_item_id:
            self._show_error("Unable to determine scope item ID")
            return

        async def confirm_delete():
            try:
                self._show_loading("Deleting scope item...")
                await self.assessment_controller.auditing_client.delete_scope_item(scope_item_id)
                self._hide_loading()
                self._close_active_dialog(self.delete_scope_item_dialog)
                await self._append_activity_event("deleted a scope item", "DELETE", "#dc2626")
                self._show_success("Scope item deleted")
                self.page.run_task(self._load_assessment_data)
            except Exception as ex:
                self._hide_loading()
                self._show_error(f"Failed to delete scope item: {str(ex)}")

        self.delete_scope_item_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Delete Scope Item"),
            content=ft.Text(f"Delete scope item '{self._get_scope_item_label(scope_item)}'?"),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: self._close_active_dialog(self.delete_scope_item_dialog)),
                ft.FilledButton("Delete", on_click=lambda _: self.page.run_task(confirm_delete))
            ]
        )
        self._open_dialog(self.delete_scope_item_dialog)

    def _open_risk_control_matrix_entry_dialog(self, e=None, selected_entry=None):
        current_entry = selected_entry or {}
        risk_title_field = ft.TextField(
            label="Risk Title",
            value=self._get_field(current_entry, "riskTitle", "RiskTitle", default=""),
            autofocus=selected_entry is None
        )
        risk_description_field = ft.TextField(
            label="Risk Description",
            multiline=True,
            min_lines=2,
            max_lines=4,
            value=self._get_field(current_entry, "riskDescription", "RiskDescription", default="")
        )
        control_name_field = ft.TextField(
            label="Control Name",
            value=self._get_field(current_entry, "controlName", "ControlName", default="")
        )
        control_description_field = ft.TextField(
            label="Control Description",
            multiline=True,
            min_lines=2,
            max_lines=4,
            value=self._get_field(current_entry, "controlDescription", "ControlDescription", default="")
        )
        adequacy_dropdown = ft.Dropdown(
            label="Control Adequacy",
            options=[
                ft.dropdown.Option(key="Adequate", text="Adequate"),
                ft.dropdown.Option(key="Partially Adequate", text="Partially Adequate"),
                ft.dropdown.Option(key="Inadequate", text="Inadequate"),
                ft.dropdown.Option(key="Not Assessed", text="Not Assessed"),
            ],
            value=self._get_field(current_entry, "controlAdequacy", "ControlAdequacy", default="Not Assessed")
        )
        effectiveness_dropdown = ft.Dropdown(
            label="Control Effectiveness",
            options=[
                ft.dropdown.Option(key="Effective", text="Effective"),
                ft.dropdown.Option(key="Needs Improvement", text="Needs Improvement"),
                ft.dropdown.Option(key="Ineffective", text="Ineffective"),
                ft.dropdown.Option(key="Not Tested", text="Not Tested"),
            ],
            value=self._get_field(current_entry, "controlEffectiveness", "ControlEffectiveness", default="Not Tested")
        )
        classification_dropdown = ft.Dropdown(
            label="Control Classification",
            options=[
                ft.dropdown.Option(
                    key=str(self._get_field(item, "id", "Id")),
                    text=self._get_field(item, "name", "Name", default="Classification")
                )
                for item in self.control_classifications or []
            ],
            value=str(self._get_field(current_entry, "controlClassificationId", "ControlClassificationId")) if self._get_field(current_entry, "controlClassificationId", "ControlClassificationId") else None
        )
        type_dropdown = ft.Dropdown(
            label="Control Type",
            options=[
                ft.dropdown.Option(
                    key=str(self._get_field(item, "id", "Id")),
                    text=self._get_field(item, "name", "Name", default="Type")
                )
                for item in self.control_types or []
            ],
            value=str(self._get_field(current_entry, "controlTypeId", "ControlTypeId")) if self._get_field(current_entry, "controlTypeId", "ControlTypeId") else None
        )
        frequency_dropdown = ft.Dropdown(
            label="Control Frequency",
            options=[
                ft.dropdown.Option(
                    key=str(self._get_field(item, "id", "Id")),
                    text=self._get_field(item, "name", "Name", default="Frequency")
                )
                for item in self.control_frequencies or []
            ],
            value=str(self._get_field(current_entry, "controlFrequencyId", "ControlFrequencyId")) if self._get_field(current_entry, "controlFrequencyId", "ControlFrequencyId") else None
        )
        scope_item_dropdown = ft.Dropdown(
            label="Scope Item",
            options=[
                ft.dropdown.Option(
                    key=str(self._get_field(item, "id", "Id")),
                    text=self._get_scope_item_label(item)
                )
                for item in self.scope_items_data or []
            ],
            value=str(self._get_field(current_entry, "scopeItemId", "ScopeItemId")) if self._get_field(current_entry, "scopeItemId", "ScopeItemId") else None
        )
        procedure_dropdown = ft.Dropdown(
            label="Procedure",
            options=[
                ft.dropdown.Option(
                    key=str(self._get_field(item, "id", "Id")),
                    text=self._get_field(item, "procedureTitle", "ProcedureTitle", default="Procedure")
                )
                for item in self.procedures_data or []
            ],
            value=str(self._get_field(current_entry, "procedureId", "ProcedureId")) if self._get_field(current_entry, "procedureId", "ProcedureId") else None
        )
        control_owner_field = ft.TextField(
            label="Control Owner",
            value=self._get_field(current_entry, "controlOwner", "ControlOwner", default="")
        )
        notes_field = ft.TextField(
            label="Notes",
            multiline=True,
            min_lines=2,
            max_lines=4,
            value=self._get_field(current_entry, "notes", "Notes", default="")
        )

        async def save_matrix_entry():
            payload = {
                "id": self._get_field(current_entry, "id", "Id"),
                "referenceId": self._normalize_reference_id(),
                "scopeItemId": int(scope_item_dropdown.value) if scope_item_dropdown.value else None,
                "procedureId": int(procedure_dropdown.value) if procedure_dropdown.value else None,
                "riskTitle": risk_title_field.value.strip() if risk_title_field.value else "",
                "riskDescription": risk_description_field.value.strip() if risk_description_field.value else "",
                "controlName": control_name_field.value.strip() if control_name_field.value else "",
                "controlDescription": control_description_field.value.strip() if control_description_field.value else "",
                "controlAdequacy": adequacy_dropdown.value,
                "controlEffectiveness": effectiveness_dropdown.value,
                "controlClassificationId": int(classification_dropdown.value) if classification_dropdown.value else None,
                "controlTypeId": int(type_dropdown.value) if type_dropdown.value else None,
                "controlFrequencyId": int(frequency_dropdown.value) if frequency_dropdown.value else None,
                "controlOwner": control_owner_field.value.strip() if control_owner_field.value else "",
                "notes": notes_field.value.strip() if notes_field.value else ""
            }

            if not payload["referenceId"] or not payload["riskTitle"] or not payload["controlName"]:
                self._show_error("Reference, risk title, and control name are required")
                return

            try:
                self._show_loading("Saving risk and control matrix entry...")
                if payload["id"]:
                    await self.assessment_controller.auditing_client.update_risk_control_matrix_entry(payload["id"], payload)
                    activity = "updated a risk and control matrix entry"
                    message = "Matrix entry updated"
                else:
                    await self.assessment_controller.auditing_client.create_risk_control_matrix_entry(payload)
                    activity = "created a risk and control matrix entry"
                    message = "Matrix entry created"
                self._hide_loading()
                self._close_active_dialog(self.risk_control_matrix_dialog)
                await self._append_activity_event(activity, "FACT_CHECK", "#2563eb")
                self._show_success(message)
                self.page.run_task(self._load_assessment_data)
            except Exception as ex:
                self._hide_loading()
                self._show_error(f"Failed to save matrix entry: {str(ex)}")

        self.risk_control_matrix_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Edit Matrix Entry" if selected_entry else "Add Matrix Entry"),
            content=ft.Column([
                risk_title_field,
                risk_description_field,
                control_name_field,
                control_description_field,
                adequacy_dropdown,
                effectiveness_dropdown,
                classification_dropdown,
                type_dropdown,
                frequency_dropdown,
                scope_item_dropdown,
                procedure_dropdown,
                control_owner_field,
                notes_field
            ], tight=True, width=580, height=620, scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: self._close_active_dialog(self.risk_control_matrix_dialog)),
                ft.FilledButton("Save", on_click=lambda _: self.page.run_task(save_matrix_entry))
            ]
        )
        self._open_dialog(self.risk_control_matrix_dialog)

    def _open_edit_risk_control_matrix_entry_dialog(self, matrix_entry):
        self._open_risk_control_matrix_entry_dialog(selected_entry=matrix_entry)

    def _delete_risk_control_matrix_entry(self, matrix_entry):
        entry_id = self._get_field(matrix_entry, "id", "Id")
        if not entry_id:
            self._show_error("Unable to determine matrix entry ID")
            return

        async def confirm_delete():
            try:
                self._show_loading("Deleting risk/control matrix entry...")
                await self.assessment_controller.auditing_client.delete_risk_control_matrix_entry(entry_id)
                self._hide_loading()
                self._close_active_dialog(self.delete_risk_control_matrix_dialog)
                await self._append_activity_event("deleted a risk and control matrix entry", "DELETE", "#dc2626")
                self._show_success("Matrix entry deleted")
                self.page.run_task(self._load_assessment_data)
            except Exception as ex:
                self._hide_loading()
                self._show_error(f"Failed to delete matrix entry: {str(ex)}")

        self.delete_risk_control_matrix_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Delete Matrix Entry"),
            content=ft.Text(f"Delete matrix entry '{self._get_field(matrix_entry, 'riskTitle', 'RiskTitle', default='Risk')}'?"),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: self._close_active_dialog(self.delete_risk_control_matrix_dialog)),
                ft.FilledButton("Delete", on_click=lambda _: self.page.run_task(confirm_delete))
            ]
        )
        self._open_dialog(self.delete_risk_control_matrix_dialog)

    def _open_walkthrough_dialog(self, e=None, selected_walkthrough=None):
        current_walkthrough = selected_walkthrough or {}
        walkthrough_date = self._get_field(current_walkthrough, "walkthroughDate", "WalkthroughDate", default="")
        if isinstance(walkthrough_date, str) and "T" in walkthrough_date:
            walkthrough_date = walkthrough_date.split("T")[0]

        process_name_field = ft.TextField(
            label="Process Name",
            value=self._get_field(current_walkthrough, "processName", "ProcessName", default=""),
            autofocus=selected_walkthrough is None
        )
        walkthrough_date_field = ft.TextField(label="Walkthrough Date (YYYY-MM-DD)", value=walkthrough_date or "")
        participants_field = ft.TextField(
            label="Participants",
            multiline=True,
            min_lines=2,
            max_lines=3,
            value=self._get_field(current_walkthrough, "participants", "Participants", default="")
        )
        process_narrative_field = ft.TextField(
            label="Process Narrative",
            multiline=True,
            min_lines=3,
            max_lines=6,
            value=self._get_field(current_walkthrough, "processNarrative", "ProcessNarrative", default="")
        )
        evidence_summary_field = ft.TextField(
            label="Evidence Summary",
            multiline=True,
            min_lines=2,
            max_lines=4,
            value=self._get_field(current_walkthrough, "evidenceSummary", "EvidenceSummary", default="")
        )
        design_conclusion_field = ft.TextField(
            label="Control Design Conclusion",
            multiline=True,
            min_lines=2,
            max_lines=4,
            value=self._get_field(current_walkthrough, "controlDesignConclusion", "ControlDesignConclusion", default="")
        )
        notes_field = ft.TextField(
            label="Notes",
            multiline=True,
            min_lines=2,
            max_lines=4,
            value=self._get_field(current_walkthrough, "notes", "Notes", default="")
        )
        scope_item_dropdown = ft.Dropdown(
            label="Scope Item",
            options=[
                ft.dropdown.Option(
                    key=str(self._get_field(item, "id", "Id")),
                    text=self._get_scope_item_label(item)
                )
                for item in self.scope_items_data or []
            ],
            value=str(self._get_field(current_walkthrough, "scopeItemId", "ScopeItemId")) if self._get_field(current_walkthrough, "scopeItemId", "ScopeItemId") else None
        )
        procedure_dropdown = ft.Dropdown(
            label="Procedure",
            options=[
                ft.dropdown.Option(
                    key=str(self._get_field(item, "id", "Id")),
                    text=self._get_field(item, "procedureTitle", "ProcedureTitle", default="Procedure")
                )
                for item in self.procedures_data or []
            ],
            value=str(self._get_field(current_walkthrough, "procedureId", "ProcedureId")) if self._get_field(current_walkthrough, "procedureId", "ProcedureId") else None
        )
        matrix_dropdown = ft.Dropdown(
            label="Risk/Control Matrix Entry",
            options=[
                ft.dropdown.Option(
                    key=str(self._get_field(item, "id", "Id")),
                    text=f"{self._get_field(item, 'riskTitle', 'RiskTitle', default='Risk')} / {self._get_field(item, 'controlName', 'ControlName', default='Control')}"
                )
                for item in self.risk_control_matrix_data or []
            ],
            value=str(self._get_field(current_walkthrough, "riskControlMatrixId", "RiskControlMatrixId")) if self._get_field(current_walkthrough, "riskControlMatrixId", "RiskControlMatrixId") else None
        )

        async def save_walkthrough():
            payload = {
                "id": self._get_field(current_walkthrough, "id", "Id"),
                "referenceId": self._normalize_reference_id(),
                "scopeItemId": int(scope_item_dropdown.value) if scope_item_dropdown.value else None,
                "procedureId": int(procedure_dropdown.value) if procedure_dropdown.value else None,
                "riskControlMatrixId": int(matrix_dropdown.value) if matrix_dropdown.value else None,
                "processName": process_name_field.value.strip() if process_name_field.value else "",
                "walkthroughDate": walkthrough_date_field.value.strip() if walkthrough_date_field.value else None,
                "participants": participants_field.value.strip() if participants_field.value else "",
                "processNarrative": process_narrative_field.value.strip() if process_narrative_field.value else "",
                "evidenceSummary": evidence_summary_field.value.strip() if evidence_summary_field.value else "",
                "controlDesignConclusion": design_conclusion_field.value.strip() if design_conclusion_field.value else "",
                "notes": notes_field.value.strip() if notes_field.value else ""
            }

            if not payload["referenceId"] or not payload["processName"]:
                self._show_error("Reference and process name are required")
                return

            try:
                self._show_loading("Saving walkthrough...")
                if payload["id"]:
                    await self.assessment_controller.auditing_client.update_walkthrough(payload["id"], payload)
                    activity = "updated a walkthrough"
                    message = "Walkthrough updated"
                else:
                    await self.assessment_controller.auditing_client.create_walkthrough(payload)
                    activity = "created a walkthrough"
                    message = "Walkthrough created"
                self._hide_loading()
                self._close_active_dialog(self.walkthrough_dialog)
                await self._append_activity_event(activity, "ALT_ROUTE", "#7c3aed")
                self._show_success(message)
                self.page.run_task(self._load_assessment_data)
            except Exception as ex:
                self._hide_loading()
                self._show_error(f"Failed to save walkthrough: {str(ex)}")

        self.walkthrough_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Edit Walkthrough" if selected_walkthrough else "Add Walkthrough"),
            content=ft.Column([
                process_name_field,
                walkthrough_date_field,
                scope_item_dropdown,
                procedure_dropdown,
                matrix_dropdown,
                participants_field,
                process_narrative_field,
                evidence_summary_field,
                design_conclusion_field,
                notes_field
            ], tight=True, width=580, height=620, scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: self._close_active_dialog(self.walkthrough_dialog)),
                ft.FilledButton("Save", on_click=lambda _: self.page.run_task(save_walkthrough))
            ]
        )
        self._open_dialog(self.walkthrough_dialog)

    def _open_edit_walkthrough_dialog(self, walkthrough):
        self._open_walkthrough_dialog(selected_walkthrough=walkthrough)

    def _delete_walkthrough(self, walkthrough):
        walkthrough_id = self._get_field(walkthrough, "id", "Id")
        if not walkthrough_id:
            self._show_error("Unable to determine walkthrough ID")
            return

        async def confirm_delete():
            try:
                self._show_loading("Deleting walkthrough...")
                await self.assessment_controller.auditing_client.delete_walkthrough(walkthrough_id)
                self._hide_loading()
                self._close_active_dialog(self.delete_walkthrough_dialog)
                await self._append_activity_event("deleted a walkthrough", "DELETE", "#dc2626")
                self._show_success("Walkthrough deleted")
                self.page.run_task(self._load_assessment_data)
            except Exception as ex:
                self._hide_loading()
                self._show_error(f"Failed to delete walkthrough: {str(ex)}")

        self.delete_walkthrough_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Delete Walkthrough"),
            content=ft.Text(f"Delete walkthrough '{self._get_field(walkthrough, 'processName', 'ProcessName', default='Process walkthrough')}'?"),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: self._close_active_dialog(self.delete_walkthrough_dialog)),
                ft.FilledButton("Delete", on_click=lambda _: self.page.run_task(confirm_delete))
            ]
        )
        self._open_dialog(self.delete_walkthrough_dialog)

    def _open_add_walkthrough_exception_dialog(self, walkthrough):
        walkthrough_id = self._get_field(walkthrough, "id", "Id")
        if not walkthrough_id:
            self._show_error("Unable to determine walkthrough ID")
            return

        title_field = ft.TextField(label="Exception Title", autofocus=True)
        description_field = ft.TextField(label="Exception Description", multiline=True, min_lines=2, max_lines=4)
        severity_dropdown = ft.Dropdown(
            label="Severity",
            options=[
                ft.dropdown.Option(key="Low", text="Low"),
                ft.dropdown.Option(key="Medium", text="Medium"),
                ft.dropdown.Option(key="High", text="High"),
                ft.dropdown.Option(key="Critical", text="Critical"),
            ],
            value="Medium"
        )
        finding_dropdown = ft.Dropdown(
            label="Linked Finding",
            options=[
                ft.dropdown.Option(
                    key=str(self._get_field(item, "id", "Id")),
                    text=f"{self._get_field(item, 'findingNumber', 'FindingNumber', default='FND')} - {self._get_field(item, 'findingTitle', 'FindingTitle', default='Finding')}"
                )
                for item in self.findings_data or []
            ]
        )
        resolved_checkbox = ft.Checkbox(label="Resolved", value=False)

        async def save_exception():
            payload = {
                "walkthroughId": walkthrough_id,
                "exceptionTitle": title_field.value.strip() if title_field.value else "",
                "exceptionDescription": description_field.value.strip() if description_field.value else "",
                "severity": severity_dropdown.value or "Medium",
                "linkedFindingId": int(finding_dropdown.value) if finding_dropdown.value else None,
                "isResolved": bool(resolved_checkbox.value)
            }

            if not payload["exceptionTitle"]:
                self._show_error("Exception title is required")
                return

            try:
                self._show_loading("Saving walkthrough exception...")
                await self.assessment_controller.auditing_client.add_walkthrough_exception(payload)
                self._hide_loading()
                self._close_active_dialog(self.walkthrough_exception_dialog)
                await self._append_activity_event("added a walkthrough exception", "WARNING_AMBER", "#dc2626")
                self._show_success("Walkthrough exception added")
                self.page.run_task(self._load_assessment_data)
            except Exception as ex:
                self._hide_loading()
                self._show_error(f"Failed to save walkthrough exception: {str(ex)}")

        self.walkthrough_exception_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Add Walkthrough Exception"),
            content=ft.Column([
                ft.Text(self._get_field(walkthrough, "processName", "ProcessName", default="Walkthrough"), size=12, color="#64748b"),
                title_field,
                description_field,
                severity_dropdown,
                finding_dropdown,
                resolved_checkbox
            ], tight=True, width=540),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: self._close_active_dialog(self.walkthrough_exception_dialog)),
                ft.FilledButton("Save", on_click=lambda _: self.page.run_task(save_exception))
            ]
        )
        self._open_dialog(self.walkthrough_exception_dialog)

    def _add_procedure(self, e):
        """Open dialog to create an audit procedure"""
        title_field = ft.TextField(label="Procedure Title", autofocus=True)
        objective_field = ft.TextField(label="Objective", multiline=True, min_lines=2, max_lines=4)
        description_field = ft.TextField(label="Procedure Description", multiline=True, min_lines=2, max_lines=4)
        evidence_field = ft.TextField(label="Expected Evidence", multiline=True, min_lines=2, max_lines=3)
        working_paper_dropdown = ft.Dropdown(
            label="Working Paper Reference",
            options=self._get_working_paper_ref_options()
        )
        planned_date_field = ft.TextField(label="Planned Date (YYYY-MM-DD)")
        owner_field = ft.TextField(label="Owner")
        sample_size_field = ft.TextField(label="Sample Size")

        type_dropdown = ft.Dropdown(
            label="Procedure Type",
            options=[
                ft.dropdown.Option(
                    key=str(self._get_field(item, "id", "Id")),
                    text=self._get_field(item, "name", "Name", default="Type")
                )
                for item in self.procedure_types or []
            ],
            value=str(self._get_field(self.procedure_types[0], "id", "Id")) if self.procedure_types else None
        )

        async def save_procedure():
            payload = {
                "referenceId": self._normalize_reference_id(),
                "auditUniverseId": None,
                "procedureTitle": title_field.value.strip() if title_field.value else "",
                "objective": objective_field.value.strip() if objective_field.value else "",
                "procedureDescription": description_field.value.strip() if description_field.value else "",
                "procedureTypeId": int(type_dropdown.value) if type_dropdown.value else None,
                "statusId": 1,
                "sampleSize": int(sample_size_field.value) if sample_size_field.value and sample_size_field.value.strip().isdigit() else None,
                "expectedEvidence": evidence_field.value.strip() if evidence_field.value else "",
                "workingPaperRef": working_paper_dropdown.value.strip() if working_paper_dropdown.value else "",
                "owner": owner_field.value.strip() if owner_field.value else "",
                "plannedDate": planned_date_field.value.strip() if planned_date_field.value else None,
                "createdByUserId": self._normalize_user_id(),
                "isTemplate": False
            }

            if not payload["procedureTitle"]:
                self._show_error("Procedure title is required")
                return

            try:
                self._show_loading("Creating procedure...")
                await self.assessment_controller.auditing_client.create_procedure(payload)
                self._hide_loading()
                self._close_active_dialog(self.procedure_dialog)
                await self._append_activity_event("created an audit procedure", "FACT_CHECK", "#2563eb")
                self._show_success("Procedure created successfully")
                self.page.run_task(self._load_assessment_data)
            except Exception as ex:
                self._hide_loading()
                self._show_error(f"Failed to create procedure: {str(ex)}")

        self.procedure_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Add Procedure"),
            content=ft.Column([
                title_field,
                objective_field,
                description_field,
                type_dropdown,
                evidence_field,
                working_paper_dropdown,
                owner_field,
                sample_size_field,
                planned_date_field
            ], tight=True, width=540),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: self._close_active_dialog(self.procedure_dialog)),
                ft.FilledButton("Save", on_click=lambda _: self.page.run_task(save_procedure))
            ]
        )
        self._open_dialog(self.procedure_dialog)

    def _open_add_procedure_from_template_dialog(self, e=None, selected_template=None):
        """Create an assessment procedure from a library template"""
        filtered_templates = self._get_filtered_procedure_templates()
        template_dropdown = ft.Dropdown(
            label="Template",
            options=[
                ft.dropdown.Option(
                    key=str(self._get_field(item, "id", "Id")),
                    text=f"{self._get_field(item, 'procedureTitle', 'ProcedureTitle', default='Template')} ({self._get_field(item, 'procedureTypeName', 'ProcedureTypeName', default='Procedure')})"
                )
                for item in filtered_templates
            ],
            value=str(self._get_field(selected_template, "id", "Id")) if selected_template else None
        )
        planned_date_field = ft.TextField(label="Planned Date (YYYY-MM-DD)")

        async def create_from_template():
            payload = {
                "templateId": int(template_dropdown.value) if template_dropdown.value else None,
                "referenceId": self._normalize_reference_id(),
                "auditUniverseId": None,
                "plannedDate": planned_date_field.value.strip() if planned_date_field.value else None,
                "createdByUserId": self._normalize_user_id()
            }

            if not payload["templateId"] or not payload["referenceId"]:
                self._show_error("Template and assessment reference are required")
                return

            try:
                self._show_loading("Creating procedure from template...")
                await self.assessment_controller.auditing_client.create_procedure_from_template(payload)
                self._hide_loading()
                self._close_active_dialog(self.procedure_template_dialog)
                await self._append_activity_event("added a procedure from the library", "PLAYLIST_ADD", "#2563eb")
                self._show_success("Procedure created from template")
                self.page.run_task(self._load_assessment_data)
            except Exception as ex:
                self._hide_loading()
                self._show_error(f"Failed to use template: {str(ex)}")

        self.procedure_template_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Use Procedure Template"),
            content=ft.Column([
                template_dropdown,
                planned_date_field
            ], tight=True, width=540),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: self._close_active_dialog(self.procedure_template_dialog)),
                ft.FilledButton("Create", on_click=lambda _: self.page.run_task(create_from_template))
            ]
        )
        self._open_dialog(self.procedure_template_dialog)

    def _open_edit_procedure_dialog(self, procedure):
        """Open dialog to edit an audit procedure"""
        planned_date = self._get_field(procedure, "plannedDate", "PlannedDate")
        performed_date = self._get_field(procedure, "performedDate", "PerformedDate")
        reviewed_date = self._get_field(procedure, "reviewedDate", "ReviewedDate")
        if isinstance(planned_date, str) and "T" in planned_date:
            planned_date = planned_date.split("T")[0]
        if isinstance(performed_date, str) and "T" in performed_date:
            performed_date = performed_date.split("T")[0]
        if isinstance(reviewed_date, str) and "T" in reviewed_date:
            reviewed_date = reviewed_date.split("T")[0]

        title_field = ft.TextField(
            label="Procedure Title",
            value=self._get_field(procedure, "procedureTitle", "ProcedureTitle", default="")
        )
        objective_field = ft.TextField(
            label="Objective",
            multiline=True,
            min_lines=2,
            max_lines=4,
            value=self._get_field(procedure, "objective", "Objective", default="")
        )
        description_field = ft.TextField(
            label="Procedure Description",
            multiline=True,
            min_lines=2,
            max_lines=4,
            value=self._get_field(procedure, "procedureDescription", "ProcedureDescription", default="")
        )
        evidence_field = ft.TextField(
            label="Expected Evidence",
            multiline=True,
            min_lines=2,
            max_lines=3,
            value=self._get_field(procedure, "expectedEvidence", "ExpectedEvidence", default="")
        )
        current_working_paper_ref = self._get_field(procedure, "workingPaperRef", "WorkingPaperRef", default="")
        working_paper_dropdown = ft.Dropdown(
            label="Working Paper Reference",
            options=self._get_working_paper_ref_options(current_working_paper_ref),
            value=current_working_paper_ref if current_working_paper_ref else None
        )
        owner_field = ft.TextField(
            label="Owner",
            value=self._get_field(procedure, "owner", "Owner", default="")
        )
        sample_size_field = ft.TextField(
            label="Sample Size",
            value=str(self._get_field(procedure, "sampleSize", "SampleSize", default="") or "")
        )
        conclusion_field = ft.TextField(
            label="Conclusion",
            multiline=True,
            min_lines=2,
            max_lines=4,
            value=self._get_field(procedure, "conclusion", "Conclusion", default="")
        )
        notes_field = ft.TextField(
            label="Notes",
            multiline=True,
            min_lines=2,
            max_lines=4,
            value=self._get_field(procedure, "notes", "Notes", default="")
        )
        planned_date_field = ft.TextField(label="Planned Date (YYYY-MM-DD)", value=planned_date or "")
        performed_date_field = ft.TextField(label="Performed Date (YYYY-MM-DD)", value=performed_date or "")
        reviewed_date_field = ft.TextField(label="Reviewed Date (YYYY-MM-DD)", value=reviewed_date or "")

        type_dropdown = ft.Dropdown(
            label="Procedure Type",
            options=[
                ft.dropdown.Option(
                    key=str(self._get_field(item, "id", "Id")),
                    text=self._get_field(item, "name", "Name", default="Type")
                )
                for item in self.procedure_types or []
            ],
            value=str(self._get_field(procedure, "procedureTypeId", "ProcedureTypeId")) if self._get_field(procedure, "procedureTypeId", "ProcedureTypeId") else None
        )
        status_dropdown = ft.Dropdown(
            label="Status",
            options=[
                ft.dropdown.Option(
                    key=str(self._get_field(item, "id", "Id")),
                    text=self._get_field(item, "name", "Name", default="Status")
                )
                for item in self.procedure_statuses or []
            ],
            value=str(self._get_field(procedure, "statusId", "StatusId")) if self._get_field(procedure, "statusId", "StatusId") else None
        )

        async def save_changes():
            payload = {
                "id": self._get_field(procedure, "id", "Id"),
                "procedureTitle": title_field.value.strip() if title_field.value else "",
                "objective": objective_field.value.strip() if objective_field.value else "",
                "procedureDescription": description_field.value.strip() if description_field.value else "",
                "procedureTypeId": int(type_dropdown.value) if type_dropdown.value else None,
                "statusId": int(status_dropdown.value) if status_dropdown.value else None,
                "sampleSize": int(sample_size_field.value) if sample_size_field.value and sample_size_field.value.strip().isdigit() else None,
                "expectedEvidence": evidence_field.value.strip() if evidence_field.value else "",
                "workingPaperRef": working_paper_dropdown.value.strip() if working_paper_dropdown.value else "",
                "owner": owner_field.value.strip() if owner_field.value else "",
                "plannedDate": planned_date_field.value.strip() if planned_date_field.value else None,
                "performedDate": performed_date_field.value.strip() if performed_date_field.value else None,
                "reviewedDate": reviewed_date_field.value.strip() if reviewed_date_field.value else None,
                "conclusion": conclusion_field.value.strip() if conclusion_field.value else "",
                "notes": notes_field.value.strip() if notes_field.value else "",
                "isActive": True
            }

            if not payload["id"] or not payload["procedureTitle"]:
                self._show_error("Procedure ID and title are required")
                return

            try:
                self._show_loading("Updating procedure...")
                await self.assessment_controller.auditing_client.update_procedure(payload["id"], payload)
                self._hide_loading()
                self._close_active_dialog(self.edit_procedure_dialog)
                await self._append_activity_event("updated an audit procedure", "EDIT_NOTE", "#f59e0b")
                self._show_success("Procedure updated successfully")
                self.page.run_task(self._load_assessment_data)
            except Exception as ex:
                self._hide_loading()
                self._show_error(f"Failed to update procedure: {str(ex)}")

        self.edit_procedure_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Edit Procedure"),
            content=ft.Column([
                title_field,
                objective_field,
                description_field,
                type_dropdown,
                status_dropdown,
                evidence_field,
                working_paper_dropdown,
                owner_field,
                sample_size_field,
                planned_date_field,
                performed_date_field,
                reviewed_date_field,
                conclusion_field,
                notes_field
            ], tight=True, width=560, scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: self._close_active_dialog(self.edit_procedure_dialog)),
                ft.FilledButton("Save", on_click=lambda _: self.page.run_task(save_changes))
            ]
        )
        self._open_dialog(self.edit_procedure_dialog)

    def _delete_procedure(self, procedure):
        procedure_id = self._get_field(procedure, "id", "Id")
        if not procedure_id:
            self._show_error("Unable to determine procedure ID")
            return

        async def confirm_delete():
            try:
                self._show_loading("Deleting procedure...")
                await self.assessment_controller.auditing_client.delete_procedure(procedure_id)
                self._hide_loading()
                self._close_active_dialog(self.delete_procedure_dialog)
                await self._append_activity_event("deleted an audit procedure", "DELETE", "#dc2626")
                self._show_success("Procedure deleted successfully")
                self.page.run_task(self._load_assessment_data)
            except Exception as ex:
                self._hide_loading()
                self._show_error(f"Failed to delete procedure: {str(ex)}")

        self.delete_procedure_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Delete Procedure"),
            content=ft.Text("Delete this procedure from the assessment?"),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: self._close_active_dialog(self.delete_procedure_dialog)),
                ft.FilledButton("Delete", on_click=lambda _: self.page.run_task(confirm_delete))
            ]
        )
        self._open_dialog(self.delete_procedure_dialog)

    async def _link_misstatement_to_finding(self, misstatement, created_finding):
        finding_id = self._get_field(created_finding, "id", "Id", default=None)
        if not finding_id:
            return

        misstatement_id = self._get_field(misstatement, "id", "Id", default=None)
        if not misstatement_id:
            return

        payload = {
            "referenceId": self._normalize_reference_id(),
            "findingId": finding_id,
            "materialityCalculationId": self._get_field(misstatement, "materialityCalculationId", "MaterialityCalculationId", default=None),
            "fsli": self._get_field(misstatement, "fsli", "Fsli", default=""),
            "accountNumber": self._get_field(misstatement, "accountNumber", "AccountNumber", default=""),
            "transactionIdentifier": self._get_field(misstatement, "transactionIdentifier", "TransactionIdentifier", default=""),
            "description": self._get_field(misstatement, "description", "Description", default="Misstatement"),
            "actualAmount": self._get_field(misstatement, "actualAmount", "ActualAmount", default=0),
            "projectedAmount": self._get_field(misstatement, "projectedAmount", "ProjectedAmount", default=self._get_field(misstatement, "actualAmount", "ActualAmount", default=0)),
            "evaluationBasis": self._get_field(misstatement, "evaluationBasis", "EvaluationBasis", default="Projected amount against active thresholds"),
            "status": "Management Adjustment Requested",
            "createdByUserId": self._normalize_user_id(),
            "createdByName": self._get_current_user_name(),
        }

        await self.assessment_controller.auditing_client.update_materiality_misstatement(misstatement_id, payload)
        await self._refresh_materiality_view_state()
        await self._append_activity_event("linked a materiality misstatement to a finding", "BUG_REPORT", "#dc2626")

    def _open_finding_from_misstatement_dialog(self, misstatement):
        severity_name = "Medium"
        if self._get_field(misstatement, "exceedsOverallMateriality", "ExceedsOverallMateriality", default=False):
            severity_name = "High"
        elif self._get_field(misstatement, "exceedsPerformanceMateriality", "ExceedsPerformanceMateriality", default=False):
            severity_name = "Medium"

        severity_id = None
        for severity in self.finding_severities or []:
            if (self._get_field(severity, "name", "Name", default="") or "").lower() == severity_name.lower():
                severity_id = self._get_field(severity, "id", "Id")
                break

        actual_amount = self._format_materiality_value(self._get_field(misstatement, "actualAmount", "ActualAmount", default=0))
        projected_amount = self._format_materiality_value(self._get_field(misstatement, "projectedAmount", "ProjectedAmount", default=self._get_field(misstatement, "actualAmount", "ActualAmount", default=0)))
        threshold_basis = self._get_field(misstatement, "evaluationBasis", "EvaluationBasis", default="Projected amount against active thresholds")
        title = f"Materiality Misstatement - {self._get_field(misstatement, 'fsli', 'Fsli', default='Account')}"
        description = (
            f"{self._get_field(misstatement, 'description', 'Description', default='Misstatement identified during materiality evaluation.')}\n\n"
            f"Actual amount: {actual_amount}\n"
            f"Projected amount: {projected_amount}\n"
            f"Evaluation basis: {threshold_basis}"
        )

        self._add_finding(
            None,
            prefill={
                "findingTitle": title,
                "findingDescription": description,
                "severityId": severity_id,
            },
            on_saved=lambda created_finding: self._link_misstatement_to_finding(misstatement, created_finding),
        )

    def _add_finding(self, e, prefill=None, on_saved=None):
        """Open dialog to create a finding"""
        issue_singular = self._term("finding_singular")
        prefill = prefill or {}
        title_field = ft.TextField(
            label=f"{issue_singular} Title",
            autofocus=True,
            value=prefill.get("findingTitle", "")
        )
        description_field = ft.TextField(
            label="Description",
            multiline=True,
            min_lines=3,
            max_lines=5,
            value=prefill.get("findingDescription", "")
        )
        due_date_field = ft.TextField(label="Due Date (YYYY-MM-DD)", value=prefill.get("dueDate", ""))

        severity_options = []
        for severity in self.finding_severities or []:
            severity_id = self._get_field(severity, "id", "Id")
            severity_name = self._get_field(severity, "name", "Name", default=f"Severity {severity_id}")
            severity_options.append(ft.dropdown.Option(key=str(severity_id), text=severity_name))

        severity_dropdown = ft.Dropdown(
            label="Severity",
            options=severity_options,
            value=str(prefill.get("severityId")) if prefill.get("severityId") else (severity_options[0].key if severity_options else None)
        )

        async def save_finding(_):
            payload = {
                "referenceId": self._normalize_reference_id(),
                "auditUniverseId": None,
                "findingTitle": title_field.value.strip() if title_field.value else "",
                "findingDescription": description_field.value.strip() if description_field.value else "",
                "severityId": int(severity_dropdown.value) if severity_dropdown.value else None,
                "dueDate": due_date_field.value.strip() if due_date_field.value else None,
                "createdByUserId": self._normalize_user_id()
            }

            if not payload["findingTitle"]:
                self._show_error(f"{issue_singular} title is required")
                return

            try:
                self._show_loading(f"Creating {issue_singular.lower()}...")
                created_finding = await self.assessment_controller.auditing_client.create_finding(payload)
                self._hide_loading()
                if hasattr(self.page, "close"):
                    self.page.close(self.finding_dialog)
                else:
                    self.finding_dialog.open = False
                if on_saved:
                    callback_result = on_saved(created_finding)
                    if asyncio.iscoroutine(callback_result):
                        await callback_result
                await self._append_activity_event(f"created a {issue_singular.lower()}", "BUG_REPORT", "#dc2626")
                self._show_success(f"{issue_singular} created successfully")
                self.page.run_task(self._load_assessment_data)
            except Exception as ex:
                self._hide_loading()
                self._show_error(f"Failed to create {issue_singular.lower()}: {str(ex)}")

        self.finding_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Add {issue_singular}"),
            content=ft.Column([
                title_field,
                description_field,
                severity_dropdown,
                due_date_field
            ], tight=True, width=500),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: self._close_active_dialog(self.finding_dialog)),
                ft.FilledButton("Save", on_click=lambda _: self.page.run_task(save_finding))
            ]
        )

        if hasattr(self.page, "open"):
            self.page.open(self.finding_dialog)
        else:
            self.page.dialog = self.finding_dialog
            self.finding_dialog.open = True
        self.page.update()

    def _open_edit_finding_dialog(self, finding):
        """Open dialog to edit a finding"""
        issue_singular = self._term("finding_singular")
        title_field = ft.TextField(
            label=f"{issue_singular} Title",
            value=self._get_field(finding, "findingTitle", "FindingTitle", default="")
        )
        description_field = ft.TextField(
            label="Description",
            multiline=True,
            min_lines=3,
            max_lines=5,
            value=self._get_field(finding, "findingDescription", "FindingDescription", default="")
        )
        due_date = self._get_field(finding, "dueDate", "DueDate")
        if isinstance(due_date, str) and "T" in due_date:
            due_date = due_date.split("T")[0]
        due_date_field = ft.TextField(label="Due Date (YYYY-MM-DD)", value=due_date or "")

        severity_dropdown = ft.Dropdown(
            label="Severity",
            options=[
                ft.dropdown.Option(
                    key=str(self._get_field(severity, "id", "Id")),
                    text=self._get_field(severity, "name", "Name", default="Severity")
                )
                for severity in self.finding_severities or []
            ],
            value=str(self._get_field(finding, "severityId", "SeverityId")) if self._get_field(finding, "severityId", "SeverityId") else None
        )
        status_dropdown = ft.Dropdown(
            label="Status",
            options=[
                ft.dropdown.Option(
                    key=str(self._get_field(status, "id", "Id")),
                    text=self._get_field(status, "name", "Name", default="Status")
                )
                for status in self.finding_statuses or []
            ],
            value=str(self._get_field(finding, "statusId", "StatusId")) if self._get_field(finding, "statusId", "StatusId") else None
        )

        async def save_changes():
            payload = {
                "id": self._get_field(finding, "id", "Id"),
                "findingTitle": title_field.value.strip() if title_field.value else "",
                "findingDescription": description_field.value.strip() if description_field.value else "",
                "severityId": int(severity_dropdown.value) if severity_dropdown.value else None,
                "statusId": int(status_dropdown.value) if status_dropdown.value else None,
                "dueDate": due_date_field.value.strip() if due_date_field.value else None,
                "assignedTo": self._get_field(finding, "assignedTo", "AssignedTo"),
                "assignedToUserId": self._get_field(finding, "assignedToUserId", "AssignedToUserId"),
                "rootCause": self._get_field(finding, "rootCause", "RootCause"),
                "businessImpact": self._get_field(finding, "businessImpact", "BusinessImpact")
            }

            if not payload["id"] or not payload["findingTitle"]:
                self._show_error(f"{issue_singular} ID and title are required")
                return

            try:
                self._show_loading(f"Updating {issue_singular.lower()}...")
                await self.assessment_controller.auditing_client.update_finding(payload["id"], payload)
                self._hide_loading()
                self._close_active_dialog(self.edit_finding_dialog)
                await self._append_activity_event(f"updated a {issue_singular.lower()}", "EDIT", "#f39c12")
                self._show_success(f"{issue_singular} updated successfully")
                self.page.run_task(self._load_assessment_data)
            except Exception as ex:
                self._hide_loading()
                self._show_error(f"Failed to update {issue_singular.lower()}: {str(ex)}")

        self.edit_finding_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Edit {issue_singular}"),
            content=ft.Column([
                title_field,
                description_field,
                severity_dropdown,
                status_dropdown,
                due_date_field
            ], tight=True, width=500),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: self._close_active_dialog(self.edit_finding_dialog)),
                ft.FilledButton("Save", on_click=lambda _: self.page.run_task(save_changes))
            ]
        )
        self._open_dialog(self.edit_finding_dialog)

    def _open_add_recommendation_dialog(self, finding):
        """Open dialog to add a recommendation to a finding"""
        recommendation_field = ft.TextField(label="Recommendation", multiline=True, min_lines=3, max_lines=5)
        responsible_field = ft.TextField(label="Responsible Person")
        target_date_field = ft.TextField(label="Target Date (YYYY-MM-DD)")
        priority_dropdown = ft.Dropdown(
            label="Priority",
            options=[
                ft.dropdown.Option(key="1", text="High"),
                ft.dropdown.Option(key="2", text="Medium"),
                ft.dropdown.Option(key="3", text="Low")
            ],
            value="2"
        )

        async def save_recommendation():
            payload = {
                "findingId": self._get_field(finding, "id", "Id"),
                "recommendation": recommendation_field.value.strip() if recommendation_field.value else "",
                "priority": int(priority_dropdown.value) if priority_dropdown.value else 2,
                "targetDate": target_date_field.value.strip() if target_date_field.value else None,
                "responsiblePerson": responsible_field.value.strip() if responsible_field.value else "",
                "responsibleUserId": None
            }

            if not payload["findingId"] or not payload["recommendation"]:
                self._show_error("Finding and recommendation text are required")
                return

            try:
                self._show_loading("Creating recommendation...")
                await self.assessment_controller.auditing_client.create_recommendation(payload)
                self._hide_loading()
                self._close_active_dialog(self.add_recommendation_dialog)
                await self._append_activity_event("added a recommendation", "ADD_CIRCLE", "#2ecc71")
                self._show_success("Recommendation created successfully")
                self.page.run_task(self._load_assessment_data)
            except Exception as ex:
                self._hide_loading()
                self._show_error(f"Failed to create recommendation: {str(ex)}")

        self.add_recommendation_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Add Recommendation"),
            content=ft.Column([
                ft.Text(
                    self._get_field(finding, "findingTitle", "FindingTitle", default="Selected finding"),
                    size=12,
                    color="#7f8c8d"
                ),
                recommendation_field,
                priority_dropdown,
                responsible_field,
                target_date_field
            ], tight=True, width=500),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: self._close_active_dialog(self.add_recommendation_dialog)),
                ft.FilledButton("Save", on_click=lambda _: self.page.run_task(save_recommendation))
            ]
        )
        self._open_dialog(self.add_recommendation_dialog)

    def _open_management_response_dialog(self, recommendation):
        """Open dialog to update management response for a recommendation"""
        if not can_manage_management_response(self.user, recommendation):
            self._show_error("You do not have permission to update this management response.")
            return
        response_field = ft.TextField(
            label="Management Response",
            multiline=True,
            min_lines=3,
            max_lines=5,
            value=self._get_field(recommendation, "managementResponse", "ManagementResponse", default="")
        )
        status_dropdown = ft.Dropdown(
            label="Status",
            options=[
                ft.dropdown.Option(
                    key=str(self._get_field(status, "id", "Id")),
                    text=self._get_field(status, "name", "Name", default="Status")
                )
                for status in self.recommendation_statuses or []
            ],
            value=str(self._get_field(recommendation, "statusId", "StatusId")) if self._get_field(recommendation, "statusId", "StatusId") else None
        )

        async def save_response():
            payload = {
                "id": self._get_field(recommendation, "id", "Id"),
                "recommendation": self._get_field(recommendation, "recommendation", "Recommendation"),
                "priority": self._get_field(recommendation, "priority", "Priority", default=2),
                "managementResponse": response_field.value.strip() if response_field.value else "",
                "agreedDate": self._get_field(recommendation, "agreedDate", "AgreedDate"),
                "targetDate": self._get_field(recommendation, "targetDate", "TargetDate"),
                "implementationDate": self._get_field(recommendation, "implementationDate", "ImplementationDate"),
                "responsiblePerson": self._get_field(recommendation, "responsiblePerson", "ResponsiblePerson"),
                "responsibleUserId": self._get_field(recommendation, "responsibleUserId", "ResponsibleUserId"),
                "statusId": int(status_dropdown.value) if status_dropdown.value else self._get_field(recommendation, "statusId", "StatusId"),
                "verificationNotes": self._get_field(recommendation, "verificationNotes", "VerificationNotes"),
                "verifiedByUserId": self._get_field(recommendation, "verifiedByUserId", "VerifiedByUserId"),
                "verifiedDate": self._get_field(recommendation, "verifiedDate", "VerifiedDate")
            }

            if not payload["id"] or not payload["recommendation"]:
                self._show_error("Recommendation details are incomplete")
                return

            try:
                self._show_loading("Updating management response...")
                await self.assessment_controller.auditing_client.update_recommendation(payload["id"], payload)
                self._hide_loading()
                self._close_active_dialog(self.management_response_dialog)
                await self._append_activity_event("updated management response", "REPLY", "#3498db")
                self._show_success("Management response updated successfully")
                self.page.run_task(self._load_assessment_data)
            except Exception as ex:
                self._hide_loading()
                self._show_error(f"Failed to update management response: {str(ex)}")

        self.management_response_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Update Management Response"),
            content=ft.Column([
                ft.Text(
                    self._get_field(recommendation, "recommendation", "Recommendation", default="Recommendation"),
                    size=12,
                    color="#7f8c8d"
                ),
                response_field,
                status_dropdown
            ], tight=True, width=500),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: self._close_active_dialog(self.management_response_dialog)),
                ft.FilledButton("Save", on_click=lambda _: self.page.run_task(save_response))
            ]
        )
        self._open_dialog(self.management_response_dialog)

    def _delete_finding(self, finding):
        finding_id = self._get_field(finding, "id", "Id")
        if not finding_id:
            self._show_error("Unable to determine finding ID")
            return

        async def confirm_delete():
            try:
                self._show_loading("Deleting finding...")
                await self.assessment_controller.auditing_client.delete_finding(finding_id)
                self._hide_loading()
                self._close_active_dialog(self.delete_finding_dialog)
                await self._append_activity_event("deleted a finding", "DELETE", "#dc2626")
                self._show_success("Finding deleted successfully")
                self.page.run_task(self._load_assessment_data)
            except Exception as ex:
                self._hide_loading()
                self._show_error(f"Failed to delete finding: {str(ex)}")

        self.delete_finding_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Delete Finding"),
            content=ft.Text("Delete this finding and any linked recommendations?"),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: self._close_active_dialog(self.delete_finding_dialog)),
                ft.FilledButton("Delete", on_click=lambda _: self.page.run_task(confirm_delete))
            ]
        )
        self._open_dialog(self.delete_finding_dialog)

    def _delete_recommendation(self, recommendation):
        recommendation_id = self._get_field(recommendation, "id", "Id")
        if not recommendation_id:
            self._show_error("Unable to determine recommendation ID")
            return

        async def confirm_delete():
            try:
                self._show_loading("Deleting recommendation...")
                await self.assessment_controller.auditing_client.delete_recommendation(recommendation_id)
                self._hide_loading()
                self._close_active_dialog(self.delete_recommendation_dialog)
                await self._append_activity_event("deleted a recommendation", "DELETE", "#dc2626")
                self._show_success("Recommendation deleted successfully")
                self.page.run_task(self._load_assessment_data)
            except Exception as ex:
                self._hide_loading()
                self._show_error(f"Failed to delete recommendation: {str(ex)}")

        self.delete_recommendation_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Delete Recommendation"),
            content=ft.Text("Delete this recommendation?"),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: self._close_active_dialog(self.delete_recommendation_dialog)),
                ft.FilledButton("Delete", on_click=lambda _: self.page.run_task(confirm_delete))
            ]
        )
        self._open_dialog(self.delete_recommendation_dialog)

    def _open_management_action_dialog(self, e=None, selected_action=None, linked_recommendation=None):
        current_action = selected_action or {}
        linked_finding_id = (
            self._get_field(current_action, "findingId", "FindingId", default=None)
            or self._get_field(linked_recommendation, "findingId", "FindingId", default=None)
        )
        linked_recommendation_id = (
            self._get_field(current_action, "recommendationId", "RecommendationId", default=None)
            or self._get_field(linked_recommendation, "id", "Id", default=None)
        )
        due_date = self._get_field(current_action, "dueDate", "DueDate", default=None)
        validated_at = self._get_field(current_action, "validatedAt", "ValidatedAt", default=None)
        if isinstance(due_date, str) and "T" in due_date:
            due_date = due_date.split("T")[0]
        if isinstance(validated_at, str) and "T" in validated_at:
            validated_at = validated_at.split("T")[0]

        action_title_field = ft.TextField(
            label="Action Title",
            value=self._get_field(current_action, "actionTitle", "ActionTitle", default=self._get_field(linked_recommendation, "recommendation", "Recommendation", default="")),
            autofocus=selected_action is None
        )
        action_description_field = ft.TextField(
            label="Action Description",
            multiline=True,
            min_lines=2,
            max_lines=4,
            value=self._get_field(current_action, "actionDescription", "ActionDescription", default="")
        )
        owner_name_field = ft.TextField(
            label="Owner Name",
            value=self._get_field(current_action, "ownerName", "OwnerName", default=self._get_field(linked_recommendation, "responsiblePerson", "ResponsiblePerson", default=""))
        )
        owner_user_id_field = ft.TextField(
            label="Owner User ID (optional)",
            value=str(
                self._get_field(current_action, "ownerUserId", "OwnerUserId", default=self._get_field(linked_recommendation, "responsibleUserId", "ResponsibleUserId", default=""))
                or ""
            )
        )
        due_date_field = ft.TextField(label="Due Date (YYYY-MM-DD)", value=due_date or "")
        progress_field = ft.TextField(
            label="Progress Percent",
            value=str(self._get_field(current_action, "progressPercent", "ProgressPercent", default=0) or 0)
        )
        status_dropdown = ft.Dropdown(
            label="Status",
            options=[
                ft.dropdown.Option(key="Open", text="Open"),
                ft.dropdown.Option(key="In Progress", text="In Progress"),
                ft.dropdown.Option(key="Awaiting Validation", text="Awaiting Validation"),
                ft.dropdown.Option(key="Validated", text="Validated"),
                ft.dropdown.Option(key="Closed", text="Closed"),
            ],
            value=self._get_field(current_action, "status", "Status", default="Open")
        )
        management_response_field = ft.TextField(
            label="Management Response / Update",
            multiline=True,
            min_lines=2,
            max_lines=4,
            value=self._get_field(current_action, "managementResponse", "ManagementResponse", default="")
        )
        closure_notes_field = ft.TextField(
            label="Closure / Validation Notes",
            multiline=True,
            min_lines=2,
            max_lines=4,
            value=self._get_field(current_action, "closureNotes", "ClosureNotes", default="")
        )
        validated_by_name_field = ft.TextField(
            label="Validated By",
            value=self._get_field(current_action, "validatedByName", "ValidatedByName", default="")
        )
        validated_by_user_id_field = ft.TextField(
            label="Validated By User ID (optional)",
            value=str(self._get_field(current_action, "validatedByUserId", "ValidatedByUserId", default="") or "")
        )
        validated_at_field = ft.TextField(label="Validated At (YYYY-MM-DD)", value=validated_at or "")
        finding_dropdown = ft.Dropdown(
            label="Linked Observation / Finding",
            options=[
                ft.dropdown.Option(
                    key=str(self._get_field(item, "id", "Id")),
                    text=self._get_field(item, "findingNumber", "FindingNumber", default=f"Finding {self._get_field(item, 'id', 'Id', default='')}") + " - " + self._get_field(item, "findingTitle", "FindingTitle", default="Untitled")
                )
                for item in self.findings_data or []
            ],
            value=str(linked_finding_id) if linked_finding_id else None
        )
        recommendation_dropdown = ft.Dropdown(
            label="Linked Recommendation",
            options=[
                ft.dropdown.Option(
                    key=str(self._get_field(item, "id", "Id")),
                    text=self._get_field(item, "recommendationNumber", "RecommendationNumber", default=f"Recommendation {self._get_field(item, 'id', 'Id', default='')}") + " - " + self._get_field(item, "recommendation", "Recommendation", default="Recommendation")
                )
                for item in self.recommendations_data or []
            ],
            value=str(linked_recommendation_id) if linked_recommendation_id else None
        )

        def on_recommendation_change(event):
            selected_id = event.control.value
            selected_recommendation = next(
                (item for item in self.recommendations_data if str(self._get_field(item, "id", "Id")) == str(selected_id)),
                None
            )
            if selected_recommendation:
                rec_finding_id = self._get_field(selected_recommendation, "findingId", "FindingId", default=None)
                if rec_finding_id:
                    finding_dropdown.value = str(rec_finding_id)
                if not owner_name_field.value:
                    owner_name_field.value = self._get_field(selected_recommendation, "responsiblePerson", "ResponsiblePerson", default="") or ""
                if not action_title_field.value:
                    action_title_field.value = self._get_field(selected_recommendation, "recommendation", "Recommendation", default="") or ""
                self.page.update()

        recommendation_dropdown.on_change = on_recommendation_change

        async def save_action():
            progress_text = (progress_field.value or "").strip()
            if progress_text and not progress_text.isdigit():
                self._show_error("Progress percent must be numeric")
                return
            progress_value = int(progress_text) if progress_text else 0
            if progress_value < 0 or progress_value > 100:
                self._show_error("Progress percent must be between 0 and 100")
                return

            payload = {
                "id": self._get_field(current_action, "id", "Id", default=None),
                "referenceId": self._normalize_reference_id(),
                "findingId": self._parse_optional_int(finding_dropdown.value),
                "recommendationId": self._parse_optional_int(recommendation_dropdown.value),
                "actionTitle": action_title_field.value.strip() if action_title_field.value else "",
                "actionDescription": action_description_field.value.strip() if action_description_field.value else "",
                "ownerName": owner_name_field.value.strip() if owner_name_field.value else "",
                "ownerUserId": self._parse_optional_int(owner_user_id_field.value),
                "dueDate": due_date_field.value.strip() if due_date_field.value else None,
                "status": status_dropdown.value or "Open",
                "progressPercent": progress_value,
                "managementResponse": management_response_field.value.strip() if management_response_field.value else "",
                "closureNotes": closure_notes_field.value.strip() if closure_notes_field.value else "",
                "validatedByName": validated_by_name_field.value.strip() if validated_by_name_field.value else "",
                "validatedByUserId": self._parse_optional_int(validated_by_user_id_field.value),
                "validatedAt": validated_at_field.value.strip() if validated_at_field.value else None,
            }

            if not payload["referenceId"] or not payload["actionTitle"]:
                self._show_error("Reference and action title are required")
                return

            try:
                self._show_loading("Saving management action...")
                if payload["id"]:
                    await self.assessment_controller.auditing_client.update_management_action(payload["id"], payload)
                    activity_text = "updated a management action"
                    success_message = "Management action updated"
                else:
                    await self.assessment_controller.auditing_client.create_management_action(payload)
                    activity_text = "created a management action"
                    success_message = "Management action created"
                self._hide_loading()
                self._close_active_dialog(self.management_action_dialog)
                await self._append_activity_event(activity_text, "TASK_ALT", "#0f766e")
                self._show_success(success_message)
                self.page.run_task(self._load_assessment_data)
            except Exception as ex:
                self._hide_loading()
                self._show_error(f"Failed to save management action: {str(ex)}")

        self.management_action_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Edit Management Action" if selected_action else "Add Management Action"),
            content=ft.Column([
                action_title_field,
                action_description_field,
                finding_dropdown,
                recommendation_dropdown,
                owner_name_field,
                owner_user_id_field,
                due_date_field,
                progress_field,
                status_dropdown,
                management_response_field,
                closure_notes_field,
                validated_by_name_field,
                validated_by_user_id_field,
                validated_at_field
            ], tight=True, width=560, height=620, scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: self._close_active_dialog(self.management_action_dialog)),
                ft.FilledButton("Save", on_click=lambda _: self.page.run_task(save_action))
            ]
        )
        self._open_dialog(self.management_action_dialog)

    def _delete_management_action(self, action):
        action_id = self._get_field(action, "id", "Id")
        if not action_id:
            self._show_error("Unable to determine management action ID")
            return

        async def confirm_delete():
            try:
                self._show_loading("Deleting management action...")
                await self.assessment_controller.auditing_client.delete_management_action(action_id)
                self._hide_loading()
                self._close_active_dialog(self.delete_management_action_dialog)
                await self._append_activity_event("deleted a management action", "DELETE", "#dc2626")
                self._show_success("Management action deleted")
                self.page.run_task(self._load_assessment_data)
            except Exception as ex:
                self._hide_loading()
                self._show_error(f"Failed to delete management action: {str(ex)}")

        self.delete_management_action_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Delete Management Action"),
            content=ft.Text("Delete this management action?"),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: self._close_active_dialog(self.delete_management_action_dialog)),
                ft.FilledButton("Delete", on_click=lambda _: self.page.run_task(confirm_delete))
            ]
        )
        self._open_dialog(self.delete_management_action_dialog)
    
    def _add_comment(self, e):
        """Add new comment"""
        comment_field = ft.TextField(label="Comment", multiline=True, min_lines=3, max_lines=5, autofocus=True)

        async def save_comment_dialog():
            await self._save_comment(comment_field.value)
            self._close_active_dialog(self.comment_dialog)

        self.comment_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Add Audit Comment"),
            content=ft.Column([comment_field], tight=True, width=500),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: self._close_active_dialog(self.comment_dialog)),
                ft.FilledButton("Save", on_click=lambda _: self.page.run_task(save_comment_dialog))
            ]
        )
        self._open_dialog(self.comment_dialog)
    
    def _request_management_response(self, e):
        """Request management response"""
        pending = sum(
            1 for recommendation in self.recommendations_data
            if not self._get_field(recommendation, "managementResponse", "ManagementResponse", default="")
        )
        if pending == 0:
            self._show_info("All visible recommendations already have management responses.")
            return
        self._open_management_response_workflow_dialog()

    def _parse_optional_int(self, value):
        try:
            return int(str(value).strip()) if value is not None and str(value).strip() else None
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _normalize_import_header(value):
        if not value:
            return ""
        normalized = "".join(ch if ch.isalnum() else "_" for ch in value.strip().lower())
        while "__" in normalized:
            normalized = normalized.replace("__", "_")
        return normalized.strip("_")

    def _validate_materiality_import_csv(self, file_path, dataset_type="trial_balance"):
        required_columns_map = {
            "trial_balance": ["fiscal_year", "account_number", "current_balance"],
            "journal_entries": ["fiscal_year", "posting_date", "journal_number", "amount"],
        }
        selected_dataset = dataset_type if dataset_type in required_columns_map else "trial_balance"
        required_columns = required_columns_map[selected_dataset]
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
                        preview_rows.append(
                            {
                                self._normalize_import_header(key): (value or "").strip()
                                for key, value in raw_row.items()
                                if key
                            }
                        )

                if not headers:
                    return {"is_valid": False, "error": "The selected CSV file does not contain headers.", "preview_rows": []}
                if row_count == 0:
                    return {"is_valid": False, "error": "The selected CSV file does not contain data rows.", "preview_rows": []}
                if missing:
                    return {
                        "is_valid": False,
                        "error": f"Missing required columns: {', '.join(missing)}",
                        "preview_rows": preview_rows,
                    }

                return {
                    "is_valid": True,
                    "dataset_type": selected_dataset,
                    "row_count": row_count,
                    "headers": headers,
                    "preview_rows": preview_rows,
                }
        except UnicodeDecodeError:
            return {"is_valid": False, "error": "Unable to read CSV file. Save the file as UTF-8 and try again.", "preview_rows": []}
        except Exception as ex:
            return {"is_valid": False, "error": str(ex), "preview_rows": []}

    def _parse_optional_decimal(self, value):
        text = str(value).strip() if value is not None else ""
        if not text:
            return None
        try:
            return float(text.replace(",", ""))
        except ValueError:
            self._show_error("Numeric amount fields must contain valid numbers")
            return None

    def _format_due_date_for_api(self, value):
        value = (value or "").strip()
        if not value:
            return None
        if "T" in value:
            return value
        return f"{value}T17:00:00"

    async def _register_started_workflow(self, result, fallback_status, activity_action, icon="ROUTE", color="#2563eb"):
        workflow_instance_id = result.get("WorkflowInstanceId") if isinstance(result, dict) else None
        workflow_record = result.get("Workflow") if isinstance(result, dict) else None
        if workflow_record:
            self.workflow_instances = [
                workflow_record,
                *[
                    item for item in self.workflow_instances
                    if self._get_field(item, "workflowInstanceId", "WorkflowInstanceId") != workflow_instance_id
                ]
            ]
        self.workflow_state = {
            "status": self._get_field(workflow_record, "status", "Status", default=fallback_status),
            "workflowInstanceId": workflow_instance_id,
            "updatedAt": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        await self._persist_workflow_state()
        await self._append_activity_event(activity_action, icon, color)
        self.workflow_status = self._derive_workflow_status()

    def _open_workflow_request_dialog(
        self,
        title,
        assignee_label,
        action_label,
        default_assignee_name="",
        default_assignee_user_id=None,
        default_due_days=3,
        notes_hint="",
        on_submit=None
    ):
        if not can_start_workflows(self.user):
            self._show_error("You do not have permission to start audit workflows.")
            return
        assignee_name_field = ft.TextField(label=assignee_label, value=default_assignee_name or "")
        assignee_user_id_field = ft.TextField(
            label=f"{assignee_label} User ID (optional)",
            value=str(default_assignee_user_id) if default_assignee_user_id is not None else ""
        )
        due_date_field = ft.TextField(
            label="Due Date (YYYY-MM-DD)",
            value=(datetime.now() + timedelta(days=default_due_days)).strftime("%Y-%m-%d")
        )
        notes_field = ft.TextField(
            label="Workflow Notes",
            value=notes_hint or "",
            multiline=True,
            min_lines=2,
            max_lines=4
        )

        async def save_workflow_request():
            if on_submit is None:
                return
            try:
                await on_submit(
                    assignee_name_field.value.strip() if assignee_name_field.value else "",
                    self._parse_optional_int(assignee_user_id_field.value),
                    self._format_due_date_for_api(due_date_field.value),
                    notes_field.value.strip() if notes_field.value else ""
                )
                self._close_active_dialog(self.workflow_request_dialog)
            except Exception as ex:
                self._show_error(f"Failed to start workflow: {str(ex)}")

        self.workflow_request_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(title),
            content=ft.Column(
                [assignee_name_field, assignee_user_id_field, due_date_field, notes_field],
                tight=True,
                width=520
            ),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: self._close_active_dialog(self.workflow_request_dialog)),
                ft.FilledButton(action_label, on_click=lambda _: self.page.run_task(save_workflow_request))
            ]
        )
        self._open_dialog(self.workflow_request_dialog)

    def _open_planning_approval_workflow_dialog(self, e=None):
        engagement_title = self._get_field(self.planning_data, "engagementTitle", "EngagementTitle", default=f"Assessment {self._normalize_reference_id()}")

        async def submit(approver_name, approver_user_id, due_date, notes):
            result = await self.assessment_controller.auditing_client.start_planning_approval_workflow({
                "referenceId": self._normalize_reference_id(),
                "engagementTitle": engagement_title,
                "requestedByUserId": self._normalize_user_id(),
                "requestedByName": self._get_current_user_name(),
                "approverUserId": approver_user_id,
                "approverName": approver_name,
                "dueDate": due_date,
                "notes": notes
            })
            await self._register_started_workflow(result, "Planning Approval In Progress", "requested planning approval", "GAVEL", "#1d4ed8")
            self._show_success("Planning approval workflow started")
            self.page.run_task(self._load_assessment_data)

        self._open_workflow_request_dialog(
            title="Start Planning Approval Workflow",
            assignee_label="Approver Name",
            action_label="Start Approval",
            default_due_days=3,
            notes_hint=f"Review planning and scoping for {engagement_title}.",
            on_submit=submit
        )

    def _open_annual_plan_approval_workflow_dialog(self, e=None):
        if not self._is_internal_audit():
            self._show_info("Annual audit plan approval is only available in internal audit mode.")
            return

        annual_plan_name = self._get_field(self.planning_data, "annualPlanName", "AnnualPlanName", default="").strip()
        if not annual_plan_name:
            self._show_info("Set the annual plan name in Planning before requesting annual plan approval.")
            return

        plan_year = self._get_coverage_reporting_year()

        async def submit(approver_name, approver_user_id, due_date, notes):
            result = await self.assessment_controller.auditing_client.start_annual_audit_plan_approval_workflow({
                "referenceId": self._normalize_reference_id(),
                "annualPlanName": annual_plan_name,
                "planYear": plan_year,
                "requestedByUserId": self._normalize_user_id(),
                "requestedByName": self._get_current_user_name(),
                "approverUserId": approver_user_id,
                "approverName": approver_name,
                "dueDate": due_date,
                "notes": notes
            })
            await self._register_started_workflow(result, "Annual Plan Approval In Progress", "requested annual audit plan approval", "CALENDAR_MONTH", "#0f766e")
            self._show_success("Annual audit plan approval workflow started")
            self.page.run_task(self._load_assessment_data)

        self._open_workflow_request_dialog(
            title=f"Start Annual Plan Approval: {annual_plan_name}",
            assignee_label="Approver Name",
            action_label="Start Approval",
            default_due_days=5,
            notes_hint=f"Review annual audit plan coverage for {annual_plan_name} ({plan_year}).",
            on_submit=submit
        )

    def _open_scope_approval_workflow_dialog(self, e=None):
        scope_summary = self._get_field(self.planning_data, "scopeSummary", "ScopeSummary", default="")
        if not scope_summary and not self.scope_items_data:
            self._show_info("Add planning detail or scope items before starting a scope approval workflow.")
            return

        async def submit(approver_name, approver_user_id, due_date, notes):
            result = await self.assessment_controller.auditing_client.start_scope_approval_workflow({
                "referenceId": self._normalize_reference_id(),
                "scopeSummary": scope_summary or f"{len(self.scope_items_data)} scope items prepared",
                "requestedByUserId": self._normalize_user_id(),
                "requestedByName": self._get_current_user_name(),
                "approverUserId": approver_user_id,
                "approverName": approver_name,
                "dueDate": due_date,
                "notes": notes
            })
            await self._register_started_workflow(result, "Scope Approval In Progress", "requested scope approval", "RULE", "#1d4ed8")
            self._show_success("Scope approval workflow started")
            self.page.run_task(self._load_assessment_data)

        self._open_workflow_request_dialog(
            title="Start Scope Approval Workflow",
            assignee_label="Approver Name",
            action_label="Start Approval",
            default_due_days=2,
            notes_hint=f"Review scope boundaries and scope items for assessment {self._normalize_reference_id()}.",
            on_submit=submit
        )

    def _open_latest_walkthrough_workflow_dialog(self, e=None):
        if not self.walkthroughs_data:
            self._show_info("Capture at least one walkthrough before requesting a walkthrough workflow.")
            return
        self._open_walkthrough_workflow_dialog(self.walkthroughs_data[0])

    def _open_walkthrough_workflow_dialog(self, walkthrough):
        walkthrough_id = self._get_field(walkthrough, "id", "Id")
        process_name = self._get_field(walkthrough, "processName", "ProcessName", default="Walkthrough")
        if not walkthrough_id:
            self._show_error("Unable to determine walkthrough ID")
            return

        async def submit(reviewer_name, reviewer_user_id, due_date, notes):
            result = await self.assessment_controller.auditing_client.start_walkthrough_workflow({
                "referenceId": self._normalize_reference_id(),
                "walkthroughId": walkthrough_id,
                "processName": process_name,
                "requestedByUserId": self._normalize_user_id(),
                "requestedByName": self._get_current_user_name(),
                "reviewerUserId": reviewer_user_id,
                "reviewerName": reviewer_name,
                "dueDate": due_date,
                "notes": notes
            })
            await self._register_started_workflow(result, "Walkthrough Review In Progress", f"requested walkthrough review for {process_name}", "ALT_ROUTE", "#7c3aed")
            self._show_success("Walkthrough review workflow started")
            self.page.run_task(self._load_assessment_data)

        self._open_workflow_request_dialog(
            title=f"Start Walkthrough Review: {process_name}",
            assignee_label="Reviewer Name",
            action_label="Start Review",
            default_due_days=3,
            notes_hint=f"Review walkthrough evidence and conclusions for {process_name}.",
            on_submit=submit
        )

    def _open_working_paper_review_workflow_dialog(self, paper):
        reviewer_name = self._get_field(paper, "reviewerName", "ReviewerName", default="")
        reviewer_user_id = self._get_field(paper, "reviewerUserId", "ReviewerUserId", default=None)
        working_paper_id = self._get_field(paper, "id", "Id")
        working_paper_code = self._get_field(paper, "workingPaperCode", "WorkingPaperCode", default="")
        working_paper_title = self._get_field(paper, "title", "Title", default="Working paper")

        async def submit(assignee_name, assignee_user_id, due_date, notes):
            result = await self.assessment_controller.auditing_client.start_working_paper_review_workflow({
                "referenceId": self._normalize_reference_id(),
                "workingPaperId": working_paper_id,
                "workingPaperCode": working_paper_code,
                "workingPaperTitle": working_paper_title,
                "requestedByUserId": self._normalize_user_id(),
                "requestedByName": self._get_current_user_name(),
                "reviewerUserId": assignee_user_id,
                "reviewerName": assignee_name,
                "dueDate": due_date,
                "notes": notes
            })
            await self._register_started_workflow(result, "Workpaper Review In Progress", f"requested review for working paper {working_paper_code or working_paper_title}", "DESCRIPTION", "#0f766e")
            self._show_success("Working paper review workflow started")
            self.page.run_task(self._load_assessment_data)

        self._open_workflow_request_dialog(
            title=f"Start Working Paper Review: {working_paper_code or working_paper_title}",
            assignee_label="Reviewer Name",
            action_label="Start Review",
            default_assignee_name=reviewer_name,
            default_assignee_user_id=reviewer_user_id,
            default_due_days=4,
            notes_hint=f"Review working paper {working_paper_title}.",
            on_submit=submit
        )

    def _open_finding_review_workflow_dialog(self, e=None):
        if not self.findings_data:
            self._show_info("Add at least one finding before starting a findings review workflow.")
            return

        lead_finding = self.findings_data[0]
        finding_id = self._get_field(lead_finding, "id", "Id", default=None)
        finding_number = self._get_field(lead_finding, "findingNumber", "FindingNumber", default="")
        finding_title = self._get_field(lead_finding, "title", "Title", default=f"{len(self.findings_data)} findings")

        async def submit(reviewer_name, reviewer_user_id, due_date, notes):
            result = await self.assessment_controller.auditing_client.start_finding_review_workflow({
                "referenceId": self._normalize_reference_id(),
                "findingId": finding_id,
                "findingNumber": finding_number,
                "findingTitle": finding_title,
                "requestedByUserId": self._normalize_user_id(),
                "requestedByName": self._get_current_user_name(),
                "reviewerUserId": reviewer_user_id,
                "reviewerName": reviewer_name,
                "dueDate": due_date,
                "notes": notes
            })
            await self._register_started_workflow(result, "Finding Review In Progress", "requested findings review", "FACT_CHECK", "#dc2626")
            self._show_success("Finding review workflow started")
            self.page.run_task(self._load_assessment_data)

        self._open_workflow_request_dialog(
            title="Start Findings Review Workflow",
            assignee_label="Reviewer Name",
            action_label="Start Review",
            default_due_days=3,
            notes_hint=f"Review findings and recommendations for assessment {self._normalize_reference_id()}.",
            on_submit=submit
        )

    def _open_management_response_workflow_dialog(self, recommendation=None):
        pending_recommendation = recommendation or next(
            (
                item for item in self.recommendations_data
                if not self._get_field(item, "managementResponse", "ManagementResponse", default="")
            ),
            None
        )

        if pending_recommendation is None:
            self._show_info("All visible recommendations already have management responses.")
            return

        recommendation_id = self._get_field(pending_recommendation, "id", "Id")
        recommendation_number = self._get_field(pending_recommendation, "recommendationNumber", "RecommendationNumber", default="")
        recommendation_text = self._get_field(pending_recommendation, "recommendation", "Recommendation", default="Recommendation")
        responsible_name = self._get_field(pending_recommendation, "responsiblePerson", "ResponsiblePerson", default="")
        responsible_user_id = self._get_field(pending_recommendation, "responsibleUserId", "ResponsibleUserId", default=None)

        async def submit(assignee_name, assignee_user_id, due_date, notes):
            result = await self.assessment_controller.auditing_client.start_management_response_workflow({
                "referenceId": self._normalize_reference_id(),
                "recommendationId": recommendation_id,
                "recommendationNumber": recommendation_number,
                "recommendationTitle": recommendation_text,
                "requestedByUserId": self._normalize_user_id(),
                "requestedByName": self._get_current_user_name(),
                "responsibleUserId": assignee_user_id,
                "responsibleName": assignee_name,
                "dueDate": due_date,
                "notes": notes
            })
            await self._register_started_workflow(result, "Management Response In Progress", f"requested management response for {recommendation_number or recommendation_text}", "FORWARD_TO_INBOX", "#3498db")
            self._show_success("Management response workflow started")
            self.page.run_task(self._load_assessment_data)

        self._open_workflow_request_dialog(
            title=f"Request Management Response: {recommendation_number or 'Recommendation'}",
            assignee_label="Responsible Person",
            action_label="Request Response",
            default_assignee_name=responsible_name,
            default_assignee_user_id=responsible_user_id,
            default_due_days=5,
            notes_hint=f"Provide management response for {recommendation_text}.",
            on_submit=submit
        )

    def _open_remediation_followup_workflow_dialog(self, e=None, recommendation=None):
        followup_recommendation = recommendation or next(
            (
                item for item in self.recommendations_data
                if self._get_field(item, "managementResponse", "ManagementResponse", default="")
            ),
            None
        )

        if followup_recommendation is None:
            self._show_info("Capture at least one management response before starting remediation follow-up.")
            return

        recommendation_id = self._get_field(followup_recommendation, "id", "Id")
        recommendation_number = self._get_field(followup_recommendation, "recommendationNumber", "RecommendationNumber", default="")
        recommendation_text = self._get_field(followup_recommendation, "recommendation", "Recommendation", default="Recommendation")

        async def submit(reviewer_name, reviewer_user_id, due_date, notes):
            result = await self.assessment_controller.auditing_client.start_remediation_followup_workflow({
                "referenceId": self._normalize_reference_id(),
                "recommendationId": recommendation_id,
                "recommendationNumber": recommendation_number,
                "recommendationTitle": recommendation_text,
                "requestedByUserId": self._normalize_user_id(),
                "requestedByName": self._get_current_user_name(),
                "reviewerUserId": reviewer_user_id,
                "reviewerName": reviewer_name,
                "dueDate": due_date,
                "notes": notes
            })
            await self._register_started_workflow(result, "Remediation Follow-Up In Progress", f"started remediation follow-up for {recommendation_number or recommendation_text}", "ASSIGNMENT_TURNED_IN", "#16a34a")
            self._show_success("Remediation follow-up workflow started")
            self.page.run_task(self._load_assessment_data)

        self._open_workflow_request_dialog(
            title=f"Start Remediation Follow-Up: {recommendation_number or 'Recommendation'}",
            assignee_label="Reviewer Name",
            action_label="Start Follow-Up",
            default_due_days=10,
            notes_hint=f"Verify remediation progress for {recommendation_text}.",
            on_submit=submit
        )

    def _open_final_signoff_workflow_dialog(self, e=None):
        report_title = f"Audit Report {self._normalize_reference_id()}"

        async def submit(approver_name, approver_user_id, due_date, notes):
            result = await self.assessment_controller.auditing_client.start_final_report_signoff_workflow({
                "referenceId": self._normalize_reference_id(),
                "reportTitle": report_title,
                "requestedByUserId": self._normalize_user_id(),
                "requestedByName": self._get_current_user_name(),
                "approverUserId": approver_user_id,
                "approverName": approver_name,
                "dueDate": due_date,
                "notes": notes
            })
            await self._register_started_workflow(result, "Final Sign-Off In Progress", "requested final report sign-off", "VERIFIED", "#16a34a")
            self._show_success("Final report sign-off workflow started")
            self.page.run_task(self._load_assessment_data)

        self._open_workflow_request_dialog(
            title="Start Final Report Sign-Off Workflow",
            assignee_label="Approver Name",
            action_label="Start Sign-Off",
            default_due_days=5,
            notes_hint=f"Review the final audit pack for assessment {self._normalize_reference_id()}.",
            on_submit=submit
        )
    
    def _generate_report(self, e):
        """Generate comprehensive report"""
        self._export_assessment("pdf")

    def _prepare_export_payload(self):
        risk_items = self._get_field(self.assessment_data, "RiskAssessments", default=[]) or []
        data = []
        for idx, risk in enumerate(risk_items, start=1):
            data.append({
                "item": idx,
                "risk_title": self._get_field(risk, "RisksAssessment_KeyRiskAndFactors", default=""),
                "likelihood": self._get_field(risk, "RisksAssessment_RiskLikelihood", default=""),
                "impact": self._get_field(risk, "RisksAssessment_RiskImpact", default=""),
                "category": self._get_field(risk, "RisksAssessment_RiskCategory", default=""),
                "controls": self._get_field(risk, "ControlsAssessment_MitigatingControls", default="")
            })

        if not data:
            data.append({
                "item": "",
                "risk_title": "No risk items available",
                "likelihood": "",
                "impact": "",
                "category": "",
                "controls": ""
            })

        headers = {
            "item": "#",
            "risk_title": "Risk Title",
            "likelihood": "Likelihood",
            "impact": "Impact",
            "category": "Category",
            "controls": "Controls"
        }
        metadata = {
            "Reference ID": self._normalize_reference_id() or self.reference_id or "",
            "Assessor": self._get_assessor_name() or "N/A",
            "Workflow Status": self.workflow_status,
            "Planning Status": self._get_field(self.planning_data, "planningStatusName", "PlanningStatusName", default="Not Started"),
            "Coverage Year": self._get_coverage_reporting_year() if self._is_internal_audit() else "N/A",
            "Overall Coverage": f"{float(self._get_field(self._get_coverage_summary(), 'overallCoverage', 'OverallCoverage', default=0) or 0):.1f}%"
            if self._is_internal_audit() else "N/A",
            "Scope Items Count": len(self.scope_items_data),
            "Risk Control Matrix Count": len(self.risk_control_matrix_data),
            "Walkthroughs Count": len(self.walkthroughs_data),
            "Procedures Count": len(self.procedures_data),
            "Working Papers Count": len(self.working_papers_data),
            "Documents Count": len(self.documents_data),
            "Evidence Requests Count": len(self.evidence_requests_data),
            "Management Actions Count": len(self.management_actions_data),
            "Findings Count": len(self.findings_data),
            "Recommendations Count": len(self.recommendations_data),
            "Approved By": self._get_field(self.assessment_data, "ApprovedBy", default="Pending Approval") or "Pending Approval"
        }
        return data, headers, metadata
    
    # Utility methods
    def _format_file_size(self, value):
        try:
            if value is None:
                return "Unknown size"
            size = float(value)
            for unit in ["B", "KB", "MB", "GB"]:
                if size < 1024 or unit == "GB":
                    return f"{size:.1f} {unit}" if unit != "B" else f"{int(size)} {unit}"
                size /= 1024
        except Exception:
            return "Unknown size"

    def _show_loading(self, message="Loading..."):
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
        self.page.snack_bar = ft.SnackBar(content=ft.Text(message), bgcolor="#2ecc71")
        self.page.snack_bar.open = True
        self.page.update()
    
    def _show_error(self, message):
        """Show error message"""
        self.page.snack_bar = ft.SnackBar(content=ft.Text(message), bgcolor="#e74c3c")
        self.page.snack_bar.open = True
        self.page.update()
    
    def _show_info(self, message):
        """Show info message"""
        self.page.snack_bar = ft.SnackBar(content=ft.Text(message), bgcolor="#3498db")
        self.page.snack_bar.open = True
        self.page.update()

    def _close_active_dialog(self, dialog):
        if hasattr(self.page, "close"):
            self.page.close(dialog)
        else:
            dialog.open = False
        self.page.update()

    def _open_dialog(self, dialog):
        if hasattr(self.page, "open"):
            self.page.open(dialog)
        else:
            self.page.dialog = dialog
            dialog.open = True
        self.page.update()
    
    async def cleanup(self):
        """Cleanup resources"""
        try:
            await self.assessment_controller.close()
        except Exception as e:
            print(f"Error during cleanup: {e}") 

