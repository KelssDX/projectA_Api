import re
from datetime import datetime, timezone

import flet as ft
from flet import Icons

from src.api.auditing_client import AuditingAPIClient
from src.utils.permissions import can_manage_management_response, can_review_evidence, can_run_workflow_admin_actions, can_submit_evidence, get_user_id
from src.utils.theme import get_theme_colors, create_modern_button
from src.views.common.base_view import BaseView


class NotificationsCenterView(BaseView):
    def __init__(self, page, user, on_navigate=None):
        self.page = page
        self.user = user
        self.on_navigate = on_navigate
        self.client = AuditingAPIClient()
        self.client.set_current_user(user)
        self.colors = get_theme_colors(page.theme_mode if hasattr(page, "theme_mode") else ft.ThemeMode.LIGHT)
        self.notifications = []
        self.loading = False
        self.unread_only = False

        actions = [
            create_modern_button(self.colors, "Refresh", icon=Icons.REFRESH, on_click=self._handle_refresh, style="secondary"),
            create_modern_button(
                self.colors,
                "Unread Only",
                icon=Icons.MARK_EMAIL_UNREAD_OUTLINED,
                on_click=self._toggle_unread_only,
                style="secondary",
            ),
        ]

        super().__init__(page, "Notifications Center", actions=actions, colors=self.colors)
        self._build_view()
        self.page.run_task(self.load_data)

    def apply_theme(self, colors):
        self.colors = colors
        self._build_view()
        if self.page:
            self.page.update()

    def _handle_refresh(self, e):
        self.page.run_task(self.load_data)

    def _toggle_unread_only(self, e):
        self.unread_only = not self.unread_only
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

        try:
            self.notifications = await self.client.get_workflow_notifications(
                user_id=self._requested_user_scope(),
                unread_only=self.unread_only,
            ) or []
        except Exception as ex:
            self.notifications = []
            self._show_snackbar(f"Failed to load notifications: {str(ex)}", self.colors.danger)
        finally:
            self.loading = False
            self._build_view()
            if self.page:
                self.page.update()

    def _show_snackbar(self, message, color):
        snackbar = ft.SnackBar(content=ft.Text(message), bgcolor=color)
        self.page.snack_bar = snackbar
        snackbar.open = True
        self.page.update()

    def _build_view(self):
        self.cards_column.controls.clear()
        self.add_card(self._build_summary_section())
        self.add_card(self._build_role_guidance())
        self.add_card(self._build_notification_tabs())

    def _build_summary_section(self):
        unread_count = len([note for note in self.notifications if not self._is_read(note)])
        action_required = len(self._action_required_notifications())
        escalations = len(self._escalation_notifications())
        today_count = len([note for note in self.notifications if self._created_today(note)])

        metrics = [
            ("Unread", unread_count, self.colors.primary, Icons.MARK_EMAIL_UNREAD_OUTLINED),
            ("Action Required", action_required, self.colors.warning, Icons.PRIORITY_HIGH),
            ("Escalations", escalations, self.colors.danger, Icons.WARNING_AMBER),
            ("Today", today_count, self.colors.success, Icons.TODAY),
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

        filter_label = "Unread only" if self.unread_only else "All notifications"
        return ft.Column(
            [
                ft.Row(
                    [
                        ft.Text("Notification workload", size=18, weight=ft.FontWeight.BOLD, color=self.colors.text_primary),
                        ft.Container(expand=True),
                        ft.Text("Loading..." if self.loading else filter_label, size=12, color=self.colors.text_secondary),
                    ]
                ),
                ft.Row([metric(*item) for item in metrics], spacing=12),
            ],
            spacing=14,
        )

    def _build_role_guidance(self):
        is_client_action_user = can_submit_evidence(self.user) or can_manage_management_response(self.user)
        supports_review = can_review_evidence(self.user)
        guidance_lines = []

        if is_client_action_user:
            guidance_lines.append("Client-owner actions such as evidence upload and management responses are surfaced here first.")
        if supports_review:
            guidance_lines.append("Reviewer actions remain linked back to the audit file and workflow queues.")
        if not guidance_lines:
            guidance_lines.append("Use this workspace to monitor workflow alerts, escalations, and linked audit-file actions.")

        return ft.Container(
            padding=ft.padding.all(16),
            bgcolor=self.colors.surface,
            border=ft.border.all(1, self.colors.border),
            border_radius=14,
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Icon(Icons.INFO_OUTLINE, color=self.colors.primary, size=20),
                            ft.Text("Role Guidance", size=16, weight=ft.FontWeight.BOLD, color=self.colors.text_primary),
                        ],
                        spacing=8,
                    ),
                    *[ft.Text(line, size=12, color=self.colors.text_secondary) for line in guidance_lines],
                ],
                spacing=10,
            ),
        )

    def _build_notification_tabs(self):
        unread_notifications = [note for note in self.notifications if not self._is_read(note)]
        today_notifications = [note for note in self.notifications if self._created_today(note)]
        tabs = ft.Tabs(
            selected_index=0,
            animation_duration=150,
            scrollable=True,
            tabs=[
                ft.Tab(
                    text=f"Action Required ({len(self._action_required_notifications())})",
                    content=self._build_notification_table(
                        self._action_required_notifications(),
                        "No action-required notifications right now.",
                    ),
                ),
                ft.Tab(
                    text=f"Escalations ({len(self._escalation_notifications())})",
                    content=self._build_notification_table(
                        self._escalation_notifications(),
                        "No escalation or overdue notifications.",
                    ),
                ),
                ft.Tab(
                    text=f"Unread ({len(unread_notifications)})",
                    content=self._build_notification_table(
                        unread_notifications,
                        "No unread notifications.",
                    ),
                ),
                ft.Tab(
                    text=f"Today ({len(today_notifications)})",
                    content=self._build_notification_table(
                        today_notifications,
                        "No notifications were created today.",
                    ),
                ),
                ft.Tab(
                    text=f"All Notifications ({len(self.notifications)})",
                    content=self._build_notification_table(
                        self.notifications,
                        "No notifications available.",
                    ),
                ),
            ],
        )
        return ft.Column(
            [
                ft.Row(
                    [
                        ft.Text("Notification Queues", size=18, weight=ft.FontWeight.BOLD, color=self.colors.text_primary),
                        ft.Container(expand=True),
                        ft.Text("Tabbed tables for faster review", size=12, color=self.colors.text_secondary),
                    ]
                ),
                ft.Container(content=tabs, height=640),
            ],
            spacing=14,
        )

    def _build_notification_table(self, notifications, empty_message):
        if not notifications:
            return self._build_empty_state(empty_message, Icons.NOTIFICATIONS_NONE)

        rows = []
        for note in notifications:
            is_read = self._is_read(note)
            severity = self._get_field(note, "severity", "Severity", default="Info")
            notification_id = self._get_field(note, "id", "Id")
            reference_id = self._extract_reference_id(note)
            created_at = self._format_datetime(self._get_field(note, "createdDate", "CreatedDate", default=""))

            actions = []
            if reference_id:
                actions.append(ft.TextButton("Open Audit File", on_click=lambda e, ref_id=reference_id: self._open_reference(ref_id)))
            if notification_id and not is_read:
                actions.append(ft.TextButton("Mark Read", on_click=lambda e, current_id=notification_id: self._queue_mark_read(current_id)))

            state_label = "Escalated" if self._is_escalation(note) else "Action Required" if self._is_action_required(note) else "Informational"
            state_color = self.colors.danger if self._is_escalation(note) else self.colors.warning if self._is_action_required(note) else self.colors.primary

            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(
                            ft.Column(
                                [
                                    ft.Text(
                                        self._get_field(note, "title", "Title", default="Workflow notification"),
                                        size=12,
                                        weight=ft.FontWeight.BOLD,
                                        color=self.colors.text_primary,
                                    ),
                                    ft.Text(
                                        self._get_field(note, "message", "Message", default=""),
                                        size=11,
                                        color=self.colors.text_secondary,
                                    ),
                                ],
                                spacing=2,
                            )
                        ),
                        ft.DataCell(self._tag(severity, self._severity_color(severity))),
                        ft.DataCell(ft.Text(str(reference_id or "-"), size=12)),
                        ft.DataCell(ft.Text(created_at or "-", size=12)),
                        ft.DataCell(self._tag("Read" if is_read else "Unread", self.colors.success if is_read else self.colors.warning)),
                        ft.DataCell(self._tag(state_label, state_color)),
                        ft.DataCell(ft.Row(actions, spacing=6)),
                    ]
                )
            )

        return self._build_data_table(
            ["Notification", "Severity", "Reference", "Created", "State", "Queue", "Actions"],
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

    def _build_notification_section(self, title, icon, color, notifications, empty_message):
        return ft.Column(
            [
                ft.Row(
                    [
                        ft.Icon(icon, color=color, size=20),
                        ft.Text(title, size=16, weight=ft.FontWeight.BOLD, color=self.colors.text_primary),
                    ],
                    spacing=8,
                ),
                self._build_empty_state(empty_message, icon)
                if not notifications else ft.Column([self._build_notification_row(note) for note in notifications], spacing=10),
            ],
            spacing=12,
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

    def _build_notification_row(self, note):
        is_read = self._is_read(note)
        severity = self._get_field(note, "severity", "Severity", default="Info")
        notification_id = self._get_field(note, "id", "Id")
        reference_id = self._extract_reference_id(note)
        created_at = self._format_datetime(self._get_field(note, "createdDate", "CreatedDate", default=""))

        actions = []
        if reference_id:
            actions.append(ft.TextButton("Open Audit File", on_click=lambda e, ref_id=reference_id: self._open_reference(ref_id)))
        if notification_id and not is_read:
            actions.append(ft.TextButton("Mark Read", on_click=lambda e, current_id=notification_id: self._queue_mark_read(current_id)))

        return ft.Container(
            padding=ft.padding.all(14),
            border=ft.border.all(1, self.colors.border),
            border_radius=14,
            bgcolor=self.colors.surface,
            content=ft.Row(
                [
                    ft.Container(
                        width=10,
                        height=58,
                        border_radius=8,
                        bgcolor=self._severity_color(severity),
                    ),
                    ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Text(
                                        self._get_field(note, "title", "Title", default="Workflow notification"),
                                        size=15,
                                        weight=ft.FontWeight.BOLD,
                                        color=self.colors.text_primary,
                                    ),
                                    self._tag("Read" if is_read else "Unread", self.colors.success if is_read else self.colors.warning),
                                    self._tag(severity, self._severity_color(severity)),
                                ],
                                spacing=8,
                                wrap=True,
                            ),
                            ft.Text(self._get_field(note, "message", "Message", default=""), size=12, color=self.colors.text_secondary),
                            ft.Row(
                                [
                                    ft.Text(created_at or "Date not recorded", size=11, color=self.colors.text_secondary),
                                    self._tag("Action Required", self.colors.warning) if self._is_action_required(note) else ft.Container(),
                                    self._tag("Escalated", self.colors.danger) if self._is_escalation(note) else ft.Container(),
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

    def _queue_mark_read(self, notification_id):
        async def runner():
            await self._mark_read(notification_id)

        self.page.run_task(runner)

    async def _mark_read(self, notification_id):
        try:
            await self.client.mark_workflow_notification_read(
                notification_id,
                {"readByUserId": get_user_id(self.user)},
            )
            self._show_snackbar("Notification marked as read", self.colors.success)
            await self.load_data()
        except Exception as ex:
            self._show_snackbar(f"Failed to update notification: {str(ex)}", self.colors.danger)

    def _open_reference(self, reference_id):
        if not self.on_navigate:
            return
        self.on_navigate("assessments", "details", {"reference_id": reference_id, "id": reference_id})

    def _action_required_notifications(self):
        return [note for note in self.notifications if self._is_action_required(note)]

    def _escalation_notifications(self):
        return [note for note in self.notifications if self._is_escalation(note)]

    def _is_action_required(self, note):
        text = self._notification_text(note)
        keywords = (
            "action required",
            "upload evidence",
            "management response",
            "review",
            "approve",
            "approval",
            "sign-off",
            "sign off",
            "follow-up",
            "follow up",
        )
        return any(keyword in text for keyword in keywords)

    def _is_escalation(self, note):
        severity = (self._get_field(note, "severity", "Severity", default="") or "").lower()
        text = self._notification_text(note)
        return severity in {"critical", "error", "warning"} or "overdue" in text or "escalat" in text

    def _notification_text(self, note):
        return " ".join(
            [
                str(self._get_field(note, "title", "Title", default="") or ""),
                str(self._get_field(note, "message", "Message", default="") or ""),
            ]
        ).lower()

    def _is_read(self, note):
        return bool(self._get_field(note, "isRead", "IsRead", default=False))

    def _created_today(self, note):
        created = self._parse_datetime(self._get_field(note, "createdDate", "CreatedDate", default=""))
        if not created:
            return False
        if created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)
        return created.date() == datetime.now(timezone.utc).date()

    def _parse_datetime(self, value):
        if not value:
            return None
        try:
            normalized = str(value).replace("Z", "+00:00")
            return datetime.fromisoformat(normalized)
        except Exception:
            return None

    def _format_datetime(self, value):
        parsed = self._parse_datetime(value)
        if not parsed:
            return ""
        return parsed.strftime("%Y-%m-%d %H:%M")

    def _extract_reference_id(self, item):
        reference_id = self._get_field(item, "referenceId", "ReferenceId", default=None)
        if reference_id:
            return reference_id

        action_url = self._get_field(item, "actionUrl", "ActionUrl", default="") or ""
        match = re.search(r"/assessments/(\d+)", action_url)
        if match:
            return int(match.group(1))
        return None

    def _severity_color(self, severity):
        normalized = (severity or "").lower()
        if normalized in {"critical", "error"}:
            return self.colors.danger
        if normalized == "warning":
            return self.colors.warning
        return self.colors.primary

    def _tag(self, text, color):
        return ft.Container(
            padding=ft.padding.symmetric(horizontal=10, vertical=4),
            border_radius=999,
            bgcolor=f"{color}20",
            content=ft.Text(text, size=11, color=color, weight=ft.FontWeight.BOLD),
        )

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
