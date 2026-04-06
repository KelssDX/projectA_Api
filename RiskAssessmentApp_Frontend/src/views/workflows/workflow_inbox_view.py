import re
import json
from datetime import datetime, timezone

import flet as ft
from flet import Icons

from src.api.auditing_client import AuditingAPIClient
from src.core.config import WORKFLOW_CONFIG, get_workflow_studio_url
from src.utils.permissions import can_complete_workflow_task, can_manage_users, can_run_workflow_admin_actions, get_user_role
from src.utils.theme import get_theme_colors, create_modern_button
from src.views.common.base_view import BaseView


class WorkflowInboxView(BaseView):
    def __init__(self, page, user, on_navigate=None):
        self.page = page
        self.user = user
        self.on_navigate = on_navigate
        self.client = AuditingAPIClient()
        self.client.set_current_user(user)
        self.colors = get_theme_colors(page.theme_mode if hasattr(page, "theme_mode") else ft.ThemeMode.LIGHT)
        self.workflows = []
        self.tasks = []
        self.notifications = []
        self.loading = False

        actions = [
            create_modern_button(self.colors, "Refresh", icon=Icons.REFRESH, on_click=self._handle_refresh, style="secondary"),
        ]
        if self.on_navigate:
            actions.append(
                create_modern_button(
                    self.colors,
                    "Notifications",
                    icon=Icons.NOTIFICATIONS_NONE,
                    on_click=lambda e: self.on_navigate("notifications"),
                    style="secondary",
                )
            )
            actions.append(
                create_modern_button(
                    self.colors,
                    "Review & Sign-Off",
                    icon=Icons.VERIFIED_OUTLINED,
                    on_click=lambda e: self.on_navigate("reviews"),
                    style="secondary",
                )
            )
        if can_run_workflow_admin_actions(self.user):
            actions.append(
                create_modern_button(self.colors, "Run Reminders", icon=Icons.NOTIFICATIONS_ACTIVE, on_click=self._run_reminder_sweep, style="secondary")
            )
        if self._can_open_studio():
            actions.append(
                create_modern_button(self.colors, "Open Elsa Studio", icon=Icons.OPEN_IN_NEW, on_click=self._open_elsa_studio, style="primary")
            )

        super().__init__(page, "Workflow Inbox", actions=actions, colors=self.colors)
        self._build_view()
        self.page.run_task(self.load_data)

    def apply_theme(self, colors):
        self.colors = colors
        self._build_view()
        if self.page:
            self.page.update()

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

    def _normalize_user_id(self):
        user_id = self._get_field(self.user, "id", "Id")
        try:
            return int(user_id) if user_id is not None and str(user_id).strip() else None
        except (TypeError, ValueError):
            return None

    def _requested_user_scope(self):
        if can_run_workflow_admin_actions(self.user):
            return None
        return self._normalize_user_id()

    def _current_user_role(self):
        return get_user_role(self.user)

    def _can_open_studio(self):
        if not WORKFLOW_CONFIG.get("enabled", False):
            return False
        if not WORKFLOW_CONFIG.get("open_studio_for_admin_only", False):
            return True
        return can_manage_users(self.user)

    def _handle_refresh(self, e):
        self.page.run_task(self.load_data)

    def _run_reminder_sweep(self, e):
        if not can_run_workflow_admin_actions(self.user):
            self._show_snackbar("You do not have permission to run reminder sweeps", self.colors.danger)
            return
        self.page.run_task(self._run_reminder_sweep_async)

    def _open_elsa_studio(self, e):
        studio_url = get_workflow_studio_url()
        if not studio_url:
            self._show_snackbar("Elsa Studio URL is not configured", self.colors.danger)
            return
        self.page.launch_url(studio_url)

    async def load_data(self):
        self.loading = True
        self._build_view()
        if self.page:
            self.page.update()

        try:
            inbox = await self.client.get_workflow_inbox(self._requested_user_scope())
            self.workflows = self._get_field(inbox, "workflows", "Workflows", default=[]) or []
            self.tasks = self._get_field(inbox, "tasks", "Tasks", default=[]) or []
            self.notifications = self._get_field(inbox, "notifications", "Notifications", default=[]) or []
        except Exception as ex:
            self.workflows = []
            self.tasks = []
            self.notifications = []
            self._show_snackbar(f"Failed to load workflow inbox: {str(ex)}", self.colors.danger)
        finally:
            self.loading = False
            self._build_view()
            if self.page:
                self.page.update()

    async def _run_reminder_sweep_async(self):
        try:
            result = await self.client.run_workflow_reminder_sweep()
            try:
                await self.client.record_usage_event({
                    "moduleName": "workflows",
                    "featureName": "reminder_sweep",
                    "eventName": "run_completed",
                    "source": "workflow-inbox",
                    "metadataJson": json.dumps(result or {})
                })
            except Exception as usage_ex:
                print(f"Failed to record workflow reminder usage: {usage_ex}")
            due_soon = self._get_field(result, "dueSoonRemindersCreated", "DueSoonRemindersCreated", default=0)
            review_ready = self._get_field(result, "reviewReadyNotificationsCreated", "ReviewReadyNotificationsCreated", default=0)
            overdue = self._get_field(result, "overdueRemindersCreated", "OverdueRemindersCreated", default=0)
            escalations = self._get_field(result, "escalationsCreated", "EscalationsCreated", default=0)
            self._show_snackbar(
                f"Reminder sweep completed. Due soon: {due_soon}, review-ready: {review_ready}, overdue: {overdue}, escalations: {escalations}",
                self.colors.success,
            )
            await self.load_data()
        except Exception as ex:
            self._show_snackbar(f"Failed to run reminder sweep: {str(ex)}", self.colors.danger)

    def _show_snackbar(self, message, color):
        snackbar = ft.SnackBar(content=ft.Text(message), bgcolor=color)
        self.page.snack_bar = snackbar
        snackbar.open = True
        self.page.update()

    def _build_view(self):
        self.cards_column.controls.clear()

        self.add_card(self._build_summary_section())
        self.add_card(self._build_workspace_tabs())

    def _build_summary_section(self):
        metrics = [
            ("Active workflows", len([wf for wf in self.workflows if self._get_field(wf, "isActive", "IsActive", default=False)]), self.colors.primary, Icons.ROUTE),
            ("Pending tasks", len(self._pending_tasks()), self.colors.warning, Icons.TASK_ALT),
            ("Pending approvals", len(self._pending_approvals()), self.colors.primary, Icons.GAVEL),
            ("Overdue actions", len(self._overdue_tasks()), self.colors.danger, Icons.WARNING_AMBER),
            ("Unread alerts", len([note for note in self.notifications if not self._get_field(note, "isRead", "IsRead", default=False)]), self.colors.danger, Icons.NOTIFICATIONS_ACTIVE),
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
                        ft.Container(
                            width=42,
                            height=42,
                            bgcolor=f"{color}20",
                            border_radius=12,
                            alignment=ft.alignment.center,
                            content=ft.Icon(icon, color=color, size=22),
                        ),
                        ft.Column(
                            [
                                ft.Text(str(value), size=24, weight=ft.FontWeight.BOLD, color=self.colors.text_primary),
                                ft.Text(title, size=12, color=self.colors.text_secondary),
                            ],
                            spacing=2,
                        ),
                    ],
                    spacing=12,
                ),
            )

        top_row = ft.Row([metric(*item) for item in metrics[:3]], spacing=12)
        bottom_row = ft.Row([metric(*item) for item in metrics[3:]], spacing=12)

        return ft.Column(
            [
                ft.Row(
                    [
                        ft.Text("Workflow workload", size=18, weight=ft.FontWeight.BOLD, color=self.colors.text_primary),
                        ft.Container(expand=True),
                        ft.Text("Loading..." if self.loading else "Live from workflow API", size=12, color=self.colors.text_secondary),
                    ]
                ),
                top_row,
                bottom_row,
            ],
            spacing=14,
        )

    def _build_workspace_tabs(self):
        tabs = ft.Tabs(
            selected_index=0,
            animation_duration=150,
            scrollable=True,
            tabs=[
                ft.Tab(text=f"Pending Tasks ({len(self._pending_tasks())})", content=self._build_task_table(self._pending_tasks(), "No workflow tasks assigned")),
                ft.Tab(text=f"Pending Approvals ({len(self._pending_approvals())})", content=self._build_task_table(self._pending_approvals(), "No approval or review tasks waiting")),
                ft.Tab(text=f"Overdue ({len(self._overdue_tasks())})", content=self._build_task_table(self._overdue_tasks(), "No overdue workflow actions")),
                ft.Tab(text=f"Review Ready ({len(self._review_ready_tasks())})", content=self._build_task_table(self._review_ready_tasks(), "No workpaper review tasks detected")),
                ft.Tab(text=f"Active Workflows ({len(self.workflows)})", content=self._build_workflow_table()),
                ft.Tab(text=f"Notifications ({len(self.notifications)})", content=self._build_notifications_table()),
            ],
        )
        return ft.Column(
            [
                ft.Row(
                    [
                        ft.Text("Workflow Queues", size=18, weight=ft.FontWeight.BOLD, color=self.colors.text_primary),
                        ft.Container(expand=True),
                        ft.Text("Tabbed queues for faster triage", size=12, color=self.colors.text_secondary),
                    ]
                ),
                ft.Container(content=tabs, height=640),
            ],
            spacing=14,
        )

    def _build_task_table(self, tasks, empty_message):
        if not tasks:
            return self._build_empty_state(empty_message, Icons.INBOX_OUTLINED)

        rows = []
        for task in tasks:
            status = self._get_field(task, "status", "Status", default="Pending")
            due_date = self._format_due_date(self._get_field(task, "dueDate", "DueDate", default=""))
            reference_id = self._extract_reference_id(task)
            task_id = self._get_field(task, "id", "Id")

            actions = []
            if reference_id:
                actions.append(ft.TextButton("Open", on_click=lambda e, ref_id=reference_id: self._open_reference(ref_id)))
            if task_id and self._is_open_status(status) and can_complete_workflow_task(self.user, task):
                actions.append(ft.TextButton("Complete", on_click=lambda e, current_task_id=task_id: self._queue_complete_task(current_task_id)))

            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(
                            ft.Column(
                                [
                                    ft.Text(self._get_field(task, "taskTitle", "TaskTitle", default="Workflow task"), size=12, weight=ft.FontWeight.BOLD, color=self.colors.text_primary),
                                    ft.Text(self._get_field(task, "taskDescription", "TaskDescription", default=""), size=11, color=self.colors.text_secondary),
                                ],
                                spacing=2,
                            )
                        ),
                        ft.DataCell(ft.Text(str(reference_id or "-"), size=12)),
                        ft.DataCell(ft.Text(self._get_field(task, "assigneeName", "AssigneeName", default=self._get_field(task, "assignee_name", "Assignee_Name", default="Unassigned")) or "Unassigned", size=12)),
                        ft.DataCell(self._tag(status, self._status_color(status))),
                        ft.DataCell(self._tag(self._get_field(task, "priority", "Priority", default="Medium"), self._priority_color(self._get_field(task, "priority", "Priority", default="Medium")))),
                        ft.DataCell(ft.Text(due_date or "No due date", size=12)),
                        ft.DataCell(ft.Row(actions, spacing=6)),
                    ]
                )
            )

        return self._build_data_table(
            [
                "Task",
                "Reference",
                "Assignee",
                "Status",
                "Priority",
                "Due Date",
                "Actions",
            ],
            rows,
        )

    def _build_workflow_table(self):
        if not self.workflows:
            return self._build_empty_state("No active workflow instances", Icons.ROUTE)

        rows = []
        for workflow in self.workflows:
            status = self._get_field(workflow, "status", "Status", default="Running")
            reference_id = self._extract_reference_id(workflow)
            actions = []
            if reference_id:
                actions.append(ft.TextButton("Open", on_click=lambda e, ref_id=reference_id: self._open_reference(ref_id)))

            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(self._get_field(workflow, "workflowDisplayName", "WorkflowDisplayName", default="Workflow"), size=12, weight=ft.FontWeight.BOLD)),
                        ft.DataCell(ft.Text(str(reference_id or "-"), size=12)),
                        ft.DataCell(self._tag(status, self._status_color(status))),
                        ft.DataCell(ft.Text(self._get_field(workflow, "currentActivityName", "CurrentActivityName", default="No activity recorded"), size=12)),
                        ft.DataCell(ft.Text(self._format_due_date(self._get_field(workflow, "startedAt", "StartedAt", default="")) or "-", size=12)),
                        ft.DataCell(ft.Row(actions, spacing=6)),
                    ]
                )
            )

        return self._build_data_table(
            ["Workflow", "Reference", "Status", "Current Activity", "Started", "Actions"],
            rows,
        )

    def _build_notifications_table(self):
        if not self.notifications:
            return self._build_empty_state("No workflow notifications", Icons.NOTIFICATIONS_NONE)

        rows = []
        for note in self.notifications:
            reference_id = self._extract_reference_id(note)
            notification_id = self._get_field(note, "id", "Id")
            is_read = bool(self._get_field(note, "isRead", "IsRead", default=False))
            severity = self._get_field(note, "severity", "Severity", default="Info")

            actions = []
            if reference_id:
                actions.append(ft.TextButton("Open", on_click=lambda e, ref_id=reference_id: self._open_reference(ref_id)))
            if notification_id and not is_read:
                actions.append(ft.TextButton("Mark Read", on_click=lambda e, current_id=notification_id: self._queue_mark_read(current_id)))

            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(
                            ft.Column(
                                [
                                    ft.Text(self._get_field(note, "title", "Title", default="Workflow notification"), size=12, weight=ft.FontWeight.BOLD),
                                    ft.Text(self._get_field(note, "message", "Message", default=""), size=11, color=self.colors.text_secondary),
                                ],
                                spacing=2,
                            )
                        ),
                        ft.DataCell(self._tag(severity, self._severity_color(severity))),
                        ft.DataCell(ft.Text(str(reference_id or "-"), size=12)),
                        ft.DataCell(ft.Text(self._format_due_date(self._get_field(note, "createdAt", "CreatedAt", "createdDate", "CreatedDate", default="")) or "-", size=12)),
                        ft.DataCell(self._tag("Read" if is_read else "Unread", self.colors.success if is_read else self.colors.warning)),
                        ft.DataCell(ft.Row(actions, spacing=6)),
                    ]
                )
            )

        return self._build_data_table(
            ["Notification", "Severity", "Reference", "Created", "State", "Actions"],
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

    def _build_queue_section(self, title, icon, color, tasks, empty_message):
        return ft.Column(
            [
                self._section_header(title, icon, color),
                self._build_empty_state(empty_message, icon)
                if not tasks else ft.Column([self._build_task_row(task) for task in tasks], spacing=10),
            ],
            spacing=12,
        )

    def _build_workflows_section(self):
        return ft.Column(
            [
                self._section_header("Active Workflows", Icons.ROUTE, self.colors.primary),
                self._build_empty_state("No active workflow instances", Icons.ROUTE)
                if not self.workflows else ft.Column([self._build_workflow_row(workflow) for workflow in self.workflows], spacing=10),
            ],
            spacing=12,
        )

    def _build_notifications_section(self):
        return ft.Column(
            [
                self._section_header("Notifications", Icons.NOTIFICATIONS, self.colors.danger),
                self._build_empty_state("No workflow notifications", Icons.NOTIFICATIONS_NONE)
                if not self.notifications else ft.Column([self._build_notification_row(note) for note in self.notifications], spacing=10),
            ],
            spacing=12,
        )

    def _section_header(self, title, icon, color):
        return ft.Row(
            [
                ft.Icon(icon, color=color, size=20),
                ft.Text(title, size=16, weight=ft.FontWeight.BOLD, color=self.colors.text_primary),
            ],
            spacing=8,
        )

    def _build_empty_state(self, message, icon):
        return ft.Container(
            padding=ft.padding.all(18),
            border=ft.border.all(1, self.colors.border),
            border_radius=14,
            bgcolor=self.colors.surface,
            content=ft.Row(
                [
                    ft.Icon(icon, color=self.colors.text_secondary, size=20),
                    ft.Text(message, color=self.colors.text_secondary, size=13),
                ],
                spacing=10,
            ),
        )

    def _build_task_row(self, task):
        status = self._get_field(task, "status", "Status", default="Pending")
        due_date = self._format_due_date(self._get_field(task, "dueDate", "DueDate", default=""))
        reference_id = self._extract_reference_id(task)
        task_id = self._get_field(task, "id", "Id")

        actions = []
        if reference_id:
            actions.append(ft.TextButton("Open", on_click=lambda e, ref_id=reference_id: self._open_reference(ref_id)))
        if task_id and self._is_open_status(status) and can_complete_workflow_task(self.user, task):
            actions.append(ft.TextButton("Complete", on_click=lambda e, current_task_id=task_id: self._queue_complete_task(current_task_id)))

        overdue = self._is_overdue(task)
        return ft.Container(
            padding=ft.padding.all(14),
            border=ft.border.all(1, self.colors.border),
            border_radius=14,
            bgcolor=self.colors.surface,
            content=ft.Row(
                [
                    ft.Container(
                        width=10,
                        height=54,
                        border_radius=8,
                        bgcolor=self.colors.danger if overdue else self._priority_color(self._get_field(task, "priority", "Priority", default="Medium")),
                    ),
                    ft.Column(
                        [
                            ft.Text(self._get_field(task, "taskTitle", "TaskTitle", default="Workflow task"), size=15, weight=ft.FontWeight.BOLD, color=self.colors.text_primary),
                            ft.Text(self._get_field(task, "taskDescription", "TaskDescription", default=""), size=12, color=self.colors.text_secondary),
                            ft.Row(
                                [
                                    self._tag(status, self._status_color(status)),
                                    self._tag(self._get_field(task, "priority", "Priority", default="Medium"), self._priority_color(self._get_field(task, "priority", "Priority", default="Medium"))),
                                    self._tag("Overdue", self.colors.danger) if overdue else ft.Container(),
                                    ft.Text(f"Due: {due_date}" if due_date else "No due date", size=11, color=self.colors.text_secondary),
                                ],
                                wrap=True,
                                spacing=8,
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

    def _build_workflow_row(self, workflow):
        status = self._get_field(workflow, "status", "Status", default="Running")
        reference_id = self._extract_reference_id(workflow)

        actions = []
        if reference_id:
            actions.append(ft.TextButton("Open", on_click=lambda e, ref_id=reference_id: self._open_reference(ref_id)))

        return ft.Container(
            padding=ft.padding.all(14),
            border=ft.border.all(1, self.colors.border),
            border_radius=14,
            bgcolor=self.colors.surface,
            content=ft.Row(
                [
                    ft.Column(
                        [
                            ft.Text(self._get_field(workflow, "workflowDisplayName", "WorkflowDisplayName", default="Workflow"), size=15, weight=ft.FontWeight.BOLD, color=self.colors.text_primary),
                            ft.Text(self._get_field(workflow, "currentActivityName", "CurrentActivityName", default="No activity recorded"), size=12, color=self.colors.text_secondary),
                            ft.Row(
                                [
                                    self._tag(status, self._status_color(status)),
                                    ft.Text(f"Instance: {self._get_field(workflow, 'workflowInstanceId', 'WorkflowInstanceId', default='')}", size=11, color=self.colors.text_secondary),
                                ],
                                wrap=True,
                                spacing=8,
                            ),
                        ],
                        expand=True,
                        spacing=6,
                    ),
                    ft.Row(actions, spacing=6),
                ],
                spacing=12,
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
        )

    def _build_notification_row(self, note):
        is_read = bool(self._get_field(note, "isRead", "IsRead", default=False))
        reference_id = self._extract_reference_id(note)
        notification_id = self._get_field(note, "id", "Id")

        actions = []
        if reference_id:
            actions.append(ft.TextButton("Open", on_click=lambda e, ref_id=reference_id: self._open_reference(ref_id)))
        if notification_id and not is_read:
            actions.append(ft.TextButton("Mark Read", on_click=lambda e, current_id=notification_id: self._queue_mark_read(current_id)))

        severity = self._get_field(note, "severity", "Severity", default="Info")

        return ft.Container(
            padding=ft.padding.all(14),
            border=ft.border.all(1, self.colors.border),
            border_radius=14,
            bgcolor=self.colors.surface,
            content=ft.Row(
                [
                    ft.Container(
                        width=10,
                        height=52,
                        border_radius=8,
                        bgcolor=self._severity_color(severity),
                    ),
                    ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Text(self._get_field(note, "title", "Title", default="Workflow notification"), size=15, weight=ft.FontWeight.BOLD, color=self.colors.text_primary),
                                    self._tag("Read" if is_read else "Unread", self.colors.success if is_read else self.colors.warning),
                                ],
                                spacing=10,
                                wrap=True,
                            ),
                            ft.Text(self._get_field(note, "message", "Message", default=""), size=12, color=self.colors.text_secondary),
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

    def _pending_tasks(self):
        return [task for task in self.tasks if self._is_open_status(self._get_field(task, "status", "Status", default="Pending"))]

    def _pending_approvals(self):
        keywords = ("approve", "approval", "review", "sign-off", "sign off")
        return [task for task in self._pending_tasks() if self._task_matches_keywords(task, keywords)]

    def _overdue_tasks(self):
        return [task for task in self._pending_tasks() if self._is_overdue(task)]

    def _review_ready_tasks(self):
        keywords = ("working paper", "workpaper", "review ready", "review-ready")
        return [task for task in self._pending_tasks() if self._task_matches_keywords(task, keywords)]

    def _task_matches_keywords(self, task, keywords):
        text = " ".join([
            str(self._get_field(task, "taskTitle", "TaskTitle", default="") or ""),
            str(self._get_field(task, "taskDescription", "TaskDescription", default="") or ""),
        ]).lower()
        return any(keyword in text for keyword in keywords)

    def _parse_datetime(self, value):
        if not value:
            return None
        try:
            if isinstance(value, datetime):
                return value
            normalized = str(value).replace("Z", "+00:00")
            return datetime.fromisoformat(normalized)
        except Exception:
            return None

    def _format_due_date(self, value):
        due_date = self._parse_datetime(value)
        if not due_date:
            return ""
        return due_date.strftime("%Y-%m-%d %H:%M")

    def _is_overdue(self, task):
        due_date = self._parse_datetime(self._get_field(task, "dueDate", "DueDate", default=""))
        if not due_date or not self._is_open_status(self._get_field(task, "status", "Status", default="Pending")):
            return False
        if due_date.tzinfo is None:
            due_date = due_date.replace(tzinfo=timezone.utc)
        return due_date < datetime.now(timezone.utc)

    def _tag(self, text, color):
        return ft.Container(
            padding=ft.padding.symmetric(horizontal=10, vertical=4),
            border_radius=999,
            bgcolor=f"{color}20",
            content=ft.Text(text, size=11, color=color, weight=ft.FontWeight.BOLD),
        )

    def _status_color(self, status):
        value = (status or "").lower()
        if "approved" in value or "completed" in value:
            return self.colors.success
        if "overdue" in value or "failed" in value or "rejected" in value:
            return self.colors.danger
        if "pending" in value or "awaiting" in value:
            return self.colors.warning
        return self.colors.primary

    def _priority_color(self, priority):
        value = (priority or "").lower()
        if "high" in value or "critical" in value:
            return self.colors.danger
        if "medium" in value:
            return self.colors.warning
        return self.colors.success

    def _severity_color(self, severity):
        value = (severity or "").lower()
        if "error" in value or "critical" in value:
            return self.colors.danger
        if "warning" in value:
            return self.colors.warning
        return self.colors.primary

    def _is_open_status(self, status):
        return (status or "").strip().lower() not in {"completed", "closed", "cancelled"}

    def _extract_reference_id(self, item):
        reference_id = self._get_field(item, "referenceId", "ReferenceId", default=None)
        if reference_id:
            return reference_id

        action_url = self._get_field(item, "actionUrl", "ActionUrl", default="") or ""
        match = re.search(r"/assessments/(\d+)", action_url)
        if match:
            return int(match.group(1))
        return None

    def _open_reference(self, reference_id):
        if not self.on_navigate:
            return
        self.on_navigate("assessments", "details", {"reference_id": reference_id, "id": reference_id})

    def _queue_complete_task(self, task_id):
        async def runner():
            await self._complete_task(task_id)
        self.page.run_task(runner)

    async def _complete_task(self, task_id):
        task = next((item for item in self.tasks if self._get_field(item, "id", "Id") == task_id), None)
        if not can_complete_workflow_task(self.user, task):
            self._show_snackbar("You do not have permission to complete this workflow task", self.colors.danger)
            return
        try:
            await self.client.complete_workflow_task(task_id, {
                "completedByUserId": self._normalize_user_id(),
                "completionNotes": "Completed from workflow inbox"
            })
            try:
                await self.client.record_usage_event({
                    "moduleName": "workflows",
                    "featureName": "task_completion",
                    "eventName": "complete_task",
                    "referenceId": self._extract_reference_id(task),
                    "source": "workflow-inbox",
                    "metadataJson": json.dumps({"taskId": task_id})
                })
            except Exception as usage_ex:
                print(f"Failed to record workflow completion usage: {usage_ex}")
            self._show_snackbar("Workflow task completed", self.colors.success)
            await self.load_data()
        except Exception as ex:
            self._show_snackbar(f"Failed to complete task: {str(ex)}", self.colors.danger)

    def _queue_mark_read(self, notification_id):
        async def runner():
            await self._mark_read(notification_id)
        self.page.run_task(runner)

    async def _mark_read(self, notification_id):
        try:
            await self.client.mark_workflow_notification_read(notification_id, {
                "readByUserId": self._normalize_user_id()
            })
            self._show_snackbar("Notification marked as read", self.colors.success)
            await self.load_data()
        except Exception as ex:
            self._show_snackbar(f"Failed to update notification: {str(ex)}", self.colors.danger)
