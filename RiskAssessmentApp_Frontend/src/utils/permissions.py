def _get_field(item, *keys, default=None):
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


def normalize_role(role):
    return (role or "").strip().lower().replace("-", "_").replace(" ", "_")


def get_user_role(user):
    return normalize_role(
        _get_field(user, "role", "Role", "userType", "UserType", default="")
    )


def get_user_id(user):
    value = _get_field(user, "id", "Id", default=None)
    try:
        return int(value) if value is not None and str(value).strip() else None
    except (TypeError, ValueError):
        return None


ADMIN_ROLES = {
    "admin",
    "administrator",
    "superadmin",
}

AUDIT_EDITOR_ROLES = ADMIN_ROLES | {
    "auditor",
    "senior_auditor",
    "internal_auditor",
    "external_auditor",
    "audit_manager",
    "manager",
}

AUDIT_REVIEW_ROLES = ADMIN_ROLES | {
    "reviewer",
    "audit_reviewer",
    "audit_manager",
    "manager",
    "partner",
    "director",
}

CLIENT_OWNER_ROLES = {
    "client_owner",
    "owner",
    "management",
    "process_owner",
    "information_owner",
}


def has_any_role(user, allowed_roles):
    return get_user_role(user) in {normalize_role(role) for role in allowed_roles}


def can_manage_users(user):
    return has_any_role(user, ADMIN_ROLES)


def can_manage_audit_content(user):
    return has_any_role(user, AUDIT_EDITOR_ROLES)


def can_review_audit_content(user):
    return has_any_role(user, AUDIT_REVIEW_ROLES | AUDIT_EDITOR_ROLES)


def can_import_analytics(user):
    return has_any_role(user, AUDIT_EDITOR_ROLES | AUDIT_REVIEW_ROLES)


def can_manage_document_security(user):
    return has_any_role(user, ADMIN_ROLES | {"audit_manager", "manager", "partner", "director"})


def can_run_workflow_admin_actions(user):
    return has_any_role(user, ADMIN_ROLES | {"audit_manager", "manager"})


def can_complete_workflow_task(user, task=None):
    if has_any_role(user, AUDIT_EDITOR_ROLES | AUDIT_REVIEW_ROLES):
        return True

    if task is None:
        return False

    current_user_id = get_user_id(user)
    assignee = _get_field(task, "assigneeUserId", "AssigneeUserId", default=None)
    try:
        return current_user_id is not None and assignee is not None and int(assignee) == current_user_id
    except (TypeError, ValueError):
        return False


def can_review_evidence(user):
    return has_any_role(user, AUDIT_REVIEW_ROLES | AUDIT_EDITOR_ROLES)


def can_submit_evidence(user):
    return has_any_role(user, CLIENT_OWNER_ROLES | AUDIT_EDITOR_ROLES | AUDIT_REVIEW_ROLES)


def can_manage_management_response(user, recommendation=None):
    if has_any_role(user, CLIENT_OWNER_ROLES | AUDIT_EDITOR_ROLES | AUDIT_REVIEW_ROLES):
        return True

    current_user_id = get_user_id(user)
    responsible_user_id = _get_field(
        recommendation,
        "responsibleUserId",
        "ResponsibleUserId",
        default=None,
    )
    try:
        return current_user_id is not None and responsible_user_id is not None and int(responsible_user_id) == current_user_id
    except (TypeError, ValueError):
        return False


def can_start_workflows(user):
    return has_any_role(user, AUDIT_EDITOR_ROLES | AUDIT_REVIEW_ROLES)
