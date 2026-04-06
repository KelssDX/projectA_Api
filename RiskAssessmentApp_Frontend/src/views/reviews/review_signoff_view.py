import re
from datetime import datetime

import flet as ft
from flet import Icons

from src.api.auditing_client import AuditingAPIClient
from src.utils.permissions import can_complete_workflow_task, can_review_audit_content, can_run_workflow_admin_actions, get_user_id
from src.utils.theme import create_modern_button, get_theme_colors
from src.views.common.base_view import BaseView


class ReviewSignoffView(BaseView):
    def __init__(self, page, user, on_navigate=None):
        self.page = page
        self.user = user
        self.on_navigate = on_navigate
        self.client = AuditingAPIClient()
        self.client.set_current_user(user)
        self.colors = get_theme_colors(page.theme_mode if hasattr(page, "theme_mode") else ft.ThemeMode.LIGHT)
        self.reviews = []
        self.review_notes = []
        self.signoffs = []
        self.workflows = []
        self.notifications = []
        self.loading = False

        actions = [create_modern_button(self.colors, "Refresh", icon=Icons.REFRESH, on_click=self._handle_refresh, style="secondary")]
        if on_navigate:
            actions.append(
                create_modern_button(
                    self.colors,
                    "Open Workflow Inbox",
                    icon=Icons.INBOX_OUTLINED,
                    on_click=lambda e: self.on_navigate("workflows"),
                    style="primary",
                )
            )

        super().__init__(page, "Review And Sign-Off", actions=actions, colors=self.colors)
        self._build_view()
        self.page.run_task(self.load_data)

    def apply_theme(self, colors):
        self.colors = colors
        self._build_view()
        if self.page:
            self.page.update()

    def _handle_refresh(self, e):
        self.page.run_task(self.load_data)

    def _requested_user_scope(self):
        if can_run_workflow_admin_actions(self.user):
            return None
        return get_user_id(self.user)

    async def load_data(self):
        self.loading = True
        self._build_view()
        if self.page:
            self.page.update()

        if not can_review_audit_content(self.user):
            self.loading = False
            self._build_view()
            if self.page:
                self.page.update()
            return

        try:
            user_id = self._requested_user_scope()
            workspace = await self.client.get_review_workspace(user_id)
            inbox = await self.client.get_workflow_inbox(user_id)
            self.reviews = self._get_field(workspace, "reviews", "Reviews", default=[]) or []
            self.review_notes = self._get_field(workspace, "reviewNotes", "ReviewNotes", default=[]) or []
            self.signoffs = self._get_field(workspace, "signoffs", "Signoffs", default=[]) or []
            self.workflows = self._get_field(inbox, "workflows", "Workflows", default=[]) or []
            self.notifications = self._get_field(inbox, "notifications", "Notifications", default=[]) or []
        except Exception as ex:
            self.reviews = []
            self.review_notes = []
            self.signoffs = []
            self.workflows = []
            self.notifications = []
            self._show_snackbar(f"Failed to load review workspace: {str(ex)}", self.colors.danger)
        finally:
            self.loading = False
            self._build_view()
            if self.page:
                self.page.update()

    def _build_view(self):
        self.cards_column.controls.clear()
        self.add_card(self._build_summary())
        self.add_card(self._banner())
        if not can_review_audit_content(self.user):
            return
        self.add_card(self._build_review_tabs())

    def _build_summary(self):
        metrics = [
            ("Approvals", len(self._approval_reviews()), self.colors.primary, Icons.GAVEL),
            ("Reviews", len(self._review_items()), self.colors.warning, Icons.RATE_REVIEW),
            ("Final Sign-Off", len(self._signoff_reviews()), self.colors.success, Icons.VERIFIED),
            ("Open Notes", len([n for n in self.review_notes if self._is_note_open(n)]), self.colors.danger, Icons.ANNOUNCEMENT_OUTLINED),
        ]

        def metric(title, value, color, icon):
            return ft.Container(
                expand=True,
                padding=ft.padding.all(16),
                bgcolor=self.colors.surface,
                border=ft.border.all(1, self.colors.border),
                border_radius=14,
                content=ft.Row(
                    [
                        ft.Container(width=42, height=42, bgcolor=f"{color}20", border_radius=12, alignment=ft.alignment.center, content=ft.Icon(icon, color=color, size=22)),
                        ft.Column([ft.Text(str(value), size=24, weight=ft.FontWeight.BOLD, color=self.colors.text_primary), ft.Text(title, size=12, color=self.colors.text_secondary)], spacing=2),
                    ],
                    spacing=12,
                ),
            )

        return ft.Column(
            [
                ft.Row([ft.Text("Review workload", size=18, weight=ft.FontWeight.BOLD, color=self.colors.text_primary), ft.Container(expand=True), ft.Text("Loading..." if self.loading else "Generic reviews plus workflow state", size=12, color=self.colors.text_secondary)]),
                ft.Row([metric(*item) for item in metrics], spacing=12),
            ],
            spacing=14,
        )

    def _banner(self):
        text = "This workspace is backed by generic audit review records, review notes, and sign-off history." if can_review_audit_content(self.user) else "Review and sign-off actions are limited to audit reviewers and audit leads."
        color = self.colors.primary if can_review_audit_content(self.user) else self.colors.warning
        icon = Icons.TASK_ALT if can_review_audit_content(self.user) else Icons.LOCK_OUTLINE
        return ft.Container(
            padding=ft.padding.all(16),
            bgcolor=self.colors.surface,
            border=ft.border.all(1, self.colors.border),
            border_radius=14,
            content=ft.Row([ft.Icon(icon, color=color, size=22), ft.Text(text, size=13, color=self.colors.text_secondary)], spacing=10),
        )

    def _build_review_tabs(self):
        open_notes = [note for note in self.review_notes if self._is_note_open(note)]
        alerts = [note for note in self.notifications if self._is_attention_notification(note)]
        tabs = ft.Tabs(
            selected_index=0,
            animation_duration=150,
            scrollable=True,
            tabs=[
                ft.Tab(text=f"Approvals ({len(self._approval_reviews())})", content=self._build_review_table(self._approval_reviews(), "No approval reviews waiting.")),
                ft.Tab(text=f"Reviews ({len(self._review_items())})", content=self._build_review_table(self._review_items(), "No review items waiting.")),
                ft.Tab(text=f"Final Sign-Off ({len(self._signoff_reviews())})", content=self._build_review_table(self._signoff_reviews(), "No final sign-off items waiting.")),
                ft.Tab(text=f"Open Notes ({len(open_notes)})", content=self._build_note_table(open_notes, "No open review notes.")),
                ft.Tab(text=f"History ({len(self.signoffs[:20])})", content=self._build_signoff_table(self.signoffs[:20], "No sign-offs recorded yet.")),
                ft.Tab(text=f"Workflows ({len(self._review_workflows())})", content=self._build_workflow_table(self._review_workflows(), "No active review workflows.")),
                ft.Tab(text=f"Alerts ({len(alerts)})", content=self._build_alert_table(alerts, "No escalations or review alerts.")),
            ],
        )
        return ft.Column(
            [
                ft.Row(
                    [
                        ft.Text("Review Queues", size=18, weight=ft.FontWeight.BOLD, color=self.colors.text_primary),
                        ft.Container(expand=True),
                        ft.Text("Tabbed tables by review process", size=12, color=self.colors.text_secondary),
                    ]
                ),
                ft.Container(content=tabs, height=640),
            ],
            spacing=14,
        )

    def _build_review_table(self, reviews, empty_message):
        if not reviews:
            return self._empty_state(empty_message, Icons.RATE_REVIEW)

        rows = []
        for review in reviews:
            task_id = self._get_field(review, "taskId", "TaskId")
            reference_id = self._get_field(review, "referenceId", "ReferenceId")
            review_type = self._get_field(review, "reviewType", "ReviewType", default="Review")
            status = self._get_field(review, "status", "Status", default="Pending")
            title = self._get_field(review, "taskTitle", "TaskTitle", default="") or self._get_field(review, "workflowDisplayName", "WorkflowDisplayName", default=review_type)
            due_date = self._format_datetime(self._get_field(review, "dueDate", "DueDate"))
            open_notes = int(self._get_field(review, "openNoteCount", "OpenNoteCount", default=0) or 0)

            actions = []
            if reference_id:
                actions.append(ft.TextButton("Open Audit File", on_click=lambda e, ref_id=reference_id: self._open_reference(ref_id)))
            if task_id and self._is_open_status(status) and can_complete_workflow_task(self.user, {"id": task_id}):
                actions.append(ft.TextButton("Complete", on_click=lambda e, current_task_id=task_id: self._queue_complete_task(current_task_id)))
            actions.append(ft.TextButton("Add Note", on_click=lambda e, current_review=review: self._open_add_note_dialog(current_review)))

            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(
                            ft.Column(
                                [
                                    ft.Text(title, size=12, weight=ft.FontWeight.BOLD),
                                    ft.Text(self._get_field(review, "summary", "Summary", default="") or self._get_field(review, "taskDescription", "TaskDescription", default=""), size=11, color=self.colors.text_secondary),
                                ],
                                spacing=2,
                            )
                        ),
                        ft.DataCell(ft.Text(str(reference_id or "-"), size=12)),
                        ft.DataCell(self._tag(review_type, self._review_type_color(review_type))),
                        ft.DataCell(self._tag(status, self._status_color(status))),
                        ft.DataCell(ft.Text(self._get_field(review, "assignedReviewerName", "AssignedReviewerName", default="Unassigned"), size=12)),
                        ft.DataCell(ft.Text(due_date or "No due date", size=12)),
                        ft.DataCell(self._tag(f"{open_notes} open notes", self.colors.danger) if open_notes else ft.Text("0", size=12)),
                        ft.DataCell(ft.Row(actions, spacing=6)),
                    ]
                )
            )

        return self._build_data_table(
            ["Review Item", "Reference", "Type", "Status", "Reviewer", "Due", "Notes", "Actions"],
            rows,
        )

    def _build_note_table(self, notes, empty_message):
        if not notes:
            return self._empty_state(empty_message, Icons.ANNOUNCEMENT_OUTLINED)

        rows = []
        for note in notes:
            reference_id = self._get_field(note, "referenceId", "ReferenceId")
            actions = [ft.TextButton("Open Audit File", on_click=lambda e, ref_id=reference_id: self._open_reference(ref_id))] if reference_id else []
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(self._get_field(note, "reviewType", "ReviewType", default="Review Note"), size=12, weight=ft.FontWeight.BOLD)),
                        ft.DataCell(ft.Text(self._get_field(note, "noteText", "NoteText", default=""), size=12)),
                        ft.DataCell(self._tag(self._get_field(note, "severity", "Severity", default="Medium"), self._severity_color(self._get_field(note, "severity", "Severity", default="Medium")))),
                        ft.DataCell(self._tag(self._get_field(note, "status", "Status", default="Open"), self._status_color(self._get_field(note, "status", "Status", default="Open")))),
                        ft.DataCell(ft.Text(self._get_field(note, "raisedByName", "RaisedByName", default="Unknown"), size=12)),
                        ft.DataCell(ft.Text(self._format_datetime(self._get_field(note, "raisedAt", "RaisedAt")) or "-", size=12)),
                        ft.DataCell(ft.Row(actions, spacing=6)),
                    ]
                )
            )

        return self._build_data_table(
            ["Note Type", "Note", "Severity", "Status", "Raised By", "Raised At", "Actions"],
            rows,
        )

    def _build_signoff_table(self, signoffs, empty_message):
        if not signoffs:
            return self._empty_state(empty_message, Icons.HISTORY)

        rows = []
        for signoff in signoffs:
            reference_id = self._get_field(signoff, "referenceId", "ReferenceId")
            actions = [ft.TextButton("Open Audit File", on_click=lambda e, ref_id=reference_id: self._open_reference(ref_id))] if reference_id else []
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(self._get_field(signoff, "signoffType", "SignoffType", default="Sign-Off"), size=12, weight=ft.FontWeight.BOLD)),
                        ft.DataCell(ft.Text(str(reference_id or "-"), size=12)),
                        ft.DataCell(ft.Text(self._get_field(signoff, "signedByName", "SignedByName", default="Unknown"), size=12)),
                        ft.DataCell(ft.Text(self._format_datetime(self._get_field(signoff, "signedAt", "SignedAt")) or "-", size=12)),
                        ft.DataCell(self._tag(self._get_field(signoff, "status", "Status", default="Signed"), self.colors.success)),
                        ft.DataCell(ft.Text(self._get_field(signoff, "comment", "Comment", default=""), size=12)),
                        ft.DataCell(ft.Row(actions, spacing=6)),
                    ]
                )
            )

        return self._build_data_table(
            ["Sign-Off", "Reference", "Signed By", "Signed At", "Status", "Comment", "Actions"],
            rows,
        )

    def _build_workflow_table(self, workflows, empty_message):
        if not workflows:
            return self._empty_state(empty_message, Icons.ROUTE)

        rows = []
        for workflow in workflows:
            reference_id = self._extract_reference_id(workflow)
            actions = [ft.TextButton("Open Audit File", on_click=lambda e, ref_id=reference_id: self._open_reference(ref_id))] if reference_id else []
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(self._get_field(workflow, "workflowDisplayName", "WorkflowDisplayName", default="Workflow"), size=12, weight=ft.FontWeight.BOLD)),
                        ft.DataCell(ft.Text(str(reference_id or "-"), size=12)),
                        ft.DataCell(self._tag(self._get_field(workflow, "status", "Status", default="Running"), self._status_color(self._get_field(workflow, "status", "Status", default="Running")))),
                        ft.DataCell(ft.Text(self._get_field(workflow, "currentActivityName", "CurrentActivityName", default="No activity recorded"), size=12)),
                        ft.DataCell(ft.Text(self._get_field(workflow, "workflowInstanceId", "WorkflowInstanceId", default=""), size=12)),
                        ft.DataCell(ft.Row(actions, spacing=6)),
                    ]
                )
            )

        return self._build_data_table(
            ["Workflow", "Reference", "Status", "Current Activity", "Instance", "Actions"],
            rows,
        )

    def _build_alert_table(self, alerts, empty_message):
        if not alerts:
            return self._empty_state(empty_message, Icons.NOTIFICATIONS_ACTIVE)

        rows = []
        for note in alerts:
            reference_id = self._extract_reference_id(note)
            actions = [ft.TextButton("Open Audit File", on_click=lambda e, ref_id=reference_id: self._open_reference(ref_id))] if reference_id else []
            severity = self._get_field(note, "severity", "Severity", default="Info")
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(self._get_field(note, "title", "Title", default="Alert"), size=12, weight=ft.FontWeight.BOLD)),
                        ft.DataCell(ft.Text(self._get_field(note, "message", "Message", default=""), size=12)),
                        ft.DataCell(self._tag(severity, self._severity_color(severity))),
                        ft.DataCell(ft.Text(self._format_datetime(self._get_field(note, "createdDate", "CreatedDate")) or "-", size=12)),
                        ft.DataCell(ft.Text(str(reference_id or "-"), size=12)),
                        ft.DataCell(ft.Row(actions, spacing=6)),
                    ]
                )
            )

        return self._build_data_table(
            ["Alert", "Message", "Severity", "Created", "Reference", "Actions"],
            rows,
        )

    def _build_data_table(self, headers, rows):
        return ft.Row(
            [
                ft.DataTable(
                    columns=[ft.DataColumn(ft.Text(header, weight=ft.FontWeight.BOLD)) for header in headers],
                    rows=rows,
                    heading_row_color=self.colors.hover_bg,
                    border=ft.border.all(1, self.colors.border),
                    border_radius=12,
                    data_row_min_height=54,
                    data_row_max_height=76,
                    column_spacing=18,
                )
            ],
            scroll=ft.ScrollMode.AUTO,
        )

    def _section(self, title, icon, color, items, row_builder, empty_message):
        content = self._empty_state(empty_message, icon) if not items else ft.Column([row_builder(item) for item in items], spacing=10)
        return ft.Column([ft.Row([ft.Icon(icon, color=color, size=20), ft.Text(title, size=16, weight=ft.FontWeight.BOLD, color=self.colors.text_primary)], spacing=8), content], spacing=12)

    def _empty_state(self, message, icon):
        return ft.Container(
            padding=ft.padding.all(18),
            border=ft.border.all(1, self.colors.border),
            border_radius=14,
            bgcolor=self.colors.surface,
            content=ft.Row([ft.Icon(icon, color=self.colors.text_secondary, size=20), ft.Text(message, color=self.colors.text_secondary, size=13)], spacing=10),
        )

    def _build_review_row(self, review):
        task_id = self._get_field(review, "taskId", "TaskId")
        reference_id = self._get_field(review, "referenceId", "ReferenceId")
        review_type = self._get_field(review, "reviewType", "ReviewType", default="Review")
        status = self._get_field(review, "status", "Status", default="Pending")
        title = self._get_field(review, "taskTitle", "TaskTitle", default="") or self._get_field(review, "workflowDisplayName", "WorkflowDisplayName", default=review_type)
        description = self._get_field(review, "summary", "Summary", default="") or self._get_field(review, "taskDescription", "TaskDescription", default="")
        due_date = self._format_datetime(self._get_field(review, "dueDate", "DueDate"))
        open_notes = int(self._get_field(review, "openNoteCount", "OpenNoteCount", default=0) or 0)

        actions = []
        if reference_id:
            actions.append(ft.TextButton("Open Audit File", on_click=lambda e, ref_id=reference_id: self._open_reference(ref_id)))
        if task_id and self._is_open_status(status) and can_complete_workflow_task(self.user, {"id": task_id}):
            actions.append(ft.TextButton("Complete", on_click=lambda e, current_task_id=task_id: self._queue_complete_task(current_task_id)))
        actions.append(ft.TextButton("Add Note", on_click=lambda e, current_review=review: self._open_add_note_dialog(current_review)))

        return ft.Container(
            padding=ft.padding.all(14),
            border=ft.border.all(1, self.colors.border),
            border_radius=14,
            bgcolor=self.colors.surface,
            content=ft.Row(
                [
                    ft.Container(width=10, height=64, border_radius=8, bgcolor=self._review_type_color(review_type)),
                    ft.Column(
                        [
                            ft.Row([ft.Text(title, size=15, weight=ft.FontWeight.BOLD, color=self.colors.text_primary), self._tag(review_type, self._review_type_color(review_type)), self._tag(status, self._status_color(status))], spacing=8, wrap=True),
                            ft.Text(description, size=12, color=self.colors.text_secondary),
                            ft.Row(
                                [
                                    ft.Text(f"Reviewer: {self._get_field(review, 'assignedReviewerName', 'AssignedReviewerName', default='Unassigned')}", size=11, color=self.colors.text_secondary),
                                    ft.Text(f"Due: {due_date}" if due_date else "No due date", size=11, color=self.colors.text_secondary),
                                    self._tag(f"{open_notes} open notes", self.colors.danger) if open_notes else ft.Container(),
                                ],
                                spacing=8,
                                wrap=True,
                            ),
                        ],
                        expand=True,
                        spacing=6,
                    ),
                    ft.Row(actions, spacing=6),
                ],
                spacing=12,
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.START,
            ),
        )

    def _build_note_row(self, note):
        return self._simple_event_row(
            title=self._get_field(note, "reviewType", "ReviewType", default="Review Note"),
            subtitle=self._get_field(note, "noteText", "NoteText", default=""),
            meta=f"Raised by {self._get_field(note, 'raisedByName', 'RaisedByName', default='Unknown')} on {self._format_datetime(self._get_field(note, 'raisedAt', 'RaisedAt')) or 'unknown date'}",
            color=self._severity_color(self._get_field(note, "severity", "Severity", default="Medium")),
            tags=[self._tag(self._get_field(note, "severity", "Severity", default="Medium"), self._severity_color(self._get_field(note, "severity", "Severity", default="Medium"))), self._tag(self._get_field(note, "status", "Status", default="Open"), self._status_color(self._get_field(note, "status", "Status", default="Open")))],
            reference_id=self._get_field(note, "referenceId", "ReferenceId"),
        )

    def _build_signoff_row(self, signoff):
        comment = self._get_field(signoff, "comment", "Comment", default="")
        return self._simple_event_row(
            title=self._get_field(signoff, "signoffType", "SignoffType", default="Sign-Off"),
            subtitle=f"Signed by {self._get_field(signoff, 'signedByName', 'SignedByName', default='Unknown')}",
            meta=self._format_datetime(self._get_field(signoff, "signedAt", "SignedAt")) or "Date not recorded",
            color=self.colors.success,
            tags=[self._tag(self._get_field(signoff, "status", "Status", default="Signed"), self.colors.success)],
            reference_id=self._get_field(signoff, "referenceId", "ReferenceId"),
            extra_text=comment,
        )

    def _build_workflow_row(self, workflow):
        return self._simple_event_row(
            title=self._get_field(workflow, "workflowDisplayName", "WorkflowDisplayName", default="Workflow"),
            subtitle=self._get_field(workflow, "currentActivityName", "CurrentActivityName", default="No activity recorded"),
            meta=f"Instance: {self._get_field(workflow, 'workflowInstanceId', 'WorkflowInstanceId', default='')}",
            color=self.colors.primary,
            tags=[self._tag(self._get_field(workflow, "status", "Status", default="Running"), self._status_color(self._get_field(workflow, "status", "Status", default="Running")))],
            reference_id=self._extract_reference_id(workflow),
        )

    def _build_notification_row(self, note):
        return self._simple_event_row(
            title=self._get_field(note, "title", "Title", default="Workflow notification"),
            subtitle=self._get_field(note, "message", "Message", default=""),
            meta=self._format_datetime(self._get_field(note, "createdDate", "CreatedDate")) or "Date not recorded",
            color=self._severity_color(self._get_field(note, "severity", "Severity", default="Info")),
            tags=[self._tag(self._get_field(note, "severity", "Severity", default="Info"), self._severity_color(self._get_field(note, "severity", "Severity", default="Info")))],
            reference_id=self._extract_reference_id(note),
        )

    def _simple_event_row(self, title, subtitle, meta, color, tags, reference_id=None, extra_text=None):
        actions = [ft.TextButton("Open Audit File", on_click=lambda e, ref_id=reference_id: self._open_reference(ref_id))] if reference_id else []
        return ft.Container(
            padding=ft.padding.all(14),
            border=ft.border.all(1, self.colors.border),
            border_radius=14,
            bgcolor=self.colors.surface,
            content=ft.Row(
                [
                    ft.Container(width=10, height=52, border_radius=8, bgcolor=color),
                    ft.Column(
                        [
                            ft.Row([ft.Text(title, size=15, weight=ft.FontWeight.BOLD, color=self.colors.text_primary), *tags], spacing=8, wrap=True),
                            ft.Text(subtitle, size=12, color=self.colors.text_secondary),
                            ft.Text(meta, size=11, color=self.colors.text_secondary),
                            ft.Text(extra_text, size=11, color=self.colors.text_secondary) if extra_text else ft.Container(),
                        ],
                        expand=True,
                        spacing=6,
                    ),
                    ft.Row(actions, spacing=6),
                ],
                spacing=12,
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.START,
            ),
        )

    def _open_add_note_dialog(self, review):
        review_id = self._get_field(review, "id", "Id", default=0)
        if not review_id:
            self._show_snackbar("Unable to determine review ID", self.colors.danger)
            return

        note_field = ft.TextField(label="Review Note", multiline=True, min_lines=3, max_lines=6)
        severity_field = ft.Dropdown(label="Severity", value="Medium", options=[ft.dropdown.Option("Low"), ft.dropdown.Option("Medium"), ft.dropdown.Option("High"), ft.dropdown.Option("Critical")])

        async def save_note():
            payload = {
                "reviewId": review_id,
                "noteType": "Review Note",
                "severity": severity_field.value or "Medium",
                "status": "Open",
                "noteText": note_field.value.strip() if note_field.value else "",
            }
            if not payload["noteText"]:
                self._show_snackbar("Review note text is required", self.colors.danger)
                return
            try:
                await self.client.add_review_note(payload)
                self._close_dialog(dialog)
                self._show_snackbar("Review note added", self.colors.success)
                await self.load_data()
            except Exception as ex:
                self._show_snackbar(f"Failed to add review note: {str(ex)}", self.colors.danger)

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Add Review Note"),
            content=ft.Column([note_field, severity_field], spacing=12, tight=True, width=520),
            actions=[ft.TextButton("Cancel", on_click=lambda e: self._close_dialog(dialog)), ft.FilledButton("Save Note", on_click=lambda e: self.page.run_task(save_note))],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self._open_dialog(dialog)

    def _open_dialog(self, dialog):
        if hasattr(self.page, "open"):
            self.page.open(dialog)
        else:
            self.page.dialog = dialog
            dialog.open = True
        self.page.update()

    def _close_dialog(self, dialog):
        if hasattr(self.page, "close"):
            self.page.close(dialog)
        else:
            dialog.open = False
        self.page.update()

    def _queue_complete_task(self, task_id):
        async def runner():
            await self._complete_task(task_id)
        self.page.run_task(runner)

    async def _complete_task(self, task_id):
        review = next((item for item in self.reviews if self._get_field(item, "taskId", "TaskId") == task_id), None)
        if not can_complete_workflow_task(self.user, {"id": task_id}):
            self._show_snackbar("You do not have permission to complete this review task", self.colors.danger)
            return
        try:
            await self.client.complete_workflow_task(task_id, {"completedByUserId": get_user_id(self.user), "completionNotes": "Completed from review and sign-off workspace"})
            self._show_snackbar("Review task completed", self.colors.success)
            await self.load_data()
            if review:
                await self.client.record_usage_event({"moduleName": "reviews", "featureName": "task_completion", "eventName": "complete_review", "referenceId": self._get_field(review, "referenceId", "ReferenceId"), "source": "review-signoff-workspace"})
        except Exception as ex:
            self._show_snackbar(f"Failed to complete review task: {str(ex)}", self.colors.danger)

    def _show_snackbar(self, message, color):
        snackbar = ft.SnackBar(content=ft.Text(message), bgcolor=color)
        self.page.snack_bar = snackbar
        snackbar.open = True
        self.page.update()

    def _open_reference(self, reference_id):
        if self.on_navigate:
            self.on_navigate("assessments", "details", {"reference_id": reference_id, "id": reference_id})

    def _approval_reviews(self):
        return [review for review in self._open_reviews() if self._review_matches(review, ("approve", "approval", "scope", "planning", "management response"))]

    def _review_items(self):
        return [review for review in self._open_reviews() if self._review_matches(review, ("review", "walkthrough", "working paper", "workpaper", "finding", "follow-up", "follow up"))]

    def _signoff_reviews(self):
        return [review for review in self._open_reviews() if self._review_matches(review, ("sign-off", "sign off", "final"))]

    def _open_reviews(self):
        return [review for review in self.reviews if self._is_open_status(self._get_field(review, "status", "Status", default="Pending"))]

    def _review_workflows(self):
        return [workflow for workflow in self.workflows if self._review_matches(workflow, ("review", "approval", "sign-off", "sign off", "follow-up", "follow up"), workflow=True)]

    def _review_matches(self, item, keywords, workflow=False):
        text = " ".join(
            [
                str(self._get_field(item, "reviewType", "ReviewType", default="") if not workflow else ""),
                str(self._get_field(item, "taskTitle", "TaskTitle", default="") if not workflow else ""),
                str(self._get_field(item, "workflowDisplayName", "WorkflowDisplayName", default="") or ""),
                str(self._get_field(item, "summary", "Summary", default="") if not workflow else self._get_field(item, "currentActivityName", "CurrentActivityName", default="")),
            ]
        ).lower()
        return any(keyword in text for keyword in keywords)

    def _is_attention_notification(self, note):
        severity = (self._get_field(note, "severity", "Severity", default="") or "").lower()
        text = " ".join([str(self._get_field(note, "title", "Title", default="") or ""), str(self._get_field(note, "message", "Message", default="") or "")]).lower()
        return severity in {"warning", "critical", "error"} or "overdue" in text or "escalat" in text or "review" in text

    def _is_note_open(self, note):
        return (self._get_field(note, "status", "Status", default="Open") or "").strip().lower() not in {"closed", "cleared", "resolved"}

    def _parse_datetime(self, value):
        if not value:
            return None
        try:
            return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except Exception:
            return None

    def _format_datetime(self, value):
        parsed = self._parse_datetime(value)
        return parsed.strftime("%Y-%m-%d %H:%M") if parsed else ""

    def _is_open_status(self, status):
        return (status or "").strip().lower() not in {"completed", "closed", "cancelled", "signed", "approved"}

    def _extract_reference_id(self, item):
        reference_id = self._get_field(item, "referenceId", "ReferenceId")
        if reference_id:
            return reference_id
        action_url = self._get_field(item, "actionUrl", "ActionUrl", default="") or ""
        match = re.search(r"/assessments/(\\d+)", action_url)
        return int(match.group(1)) if match else None

    def _status_color(self, status):
        value = (status or "").lower()
        if "approved" in value or "completed" in value or "signed" in value:
            return self.colors.success
        if "overdue" in value or "failed" in value or "rejected" in value:
            return self.colors.danger
        if "pending" in value or "awaiting" in value or "open" in value:
            return self.colors.warning
        return self.colors.primary

    def _review_type_color(self, review_type):
        value = (review_type or "").lower()
        if "sign" in value:
            return self.colors.success
        if "approval" in value:
            return self.colors.primary
        return self.colors.warning

    def _severity_color(self, severity):
        value = (severity or "").lower()
        if value in {"critical", "error", "high"}:
            return self.colors.danger
        if value in {"warning", "medium"}:
            return self.colors.warning
        return self.colors.primary

    def _tag(self, text, color):
        return ft.Container(padding=ft.padding.symmetric(horizontal=10, vertical=4), border_radius=999, bgcolor=f"{color}20", content=ft.Text(text, size=11, color=color, weight=ft.FontWeight.BOLD))

    def _get_field(self, item, *keys, default=None):
        if item is None:
            return default
        if isinstance(item, dict):
            for key in keys:
                if key in item and item[key] is not None:
                    return item[key]
                camel = key[:1].lower() + key[1:] if key else key
                if camel in item and item[camel] is not None:
                    return item[camel]
        else:
            for key in keys:
                value = getattr(item, key, None)
                if value is not None:
                    return value
        return default
