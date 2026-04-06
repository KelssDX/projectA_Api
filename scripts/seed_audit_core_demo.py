import json
import re
from datetime import date, datetime, timedelta
from pathlib import Path

import psycopg2
from psycopg2.extras import Json


ROOT = Path(__file__).resolve().parents[1]
UPLOAD = ROOT / "Affine.Auditing.API" / "uploads"
SCHEMA = '"Risk_Assess_Framework"'

ADMIN_ID, ADMIN = 1, "System Administrator"
MANAGER_ID, MANAGER = 2, "Audit Manager"
PARTNER_ID, PARTNER = 3, "Engagement Partner"


def load_dsn():
    return json.loads((ROOT / "postgres-config.json").read_text(encoding="utf-8"))["postgresConnectionString"]


def fetchone(cur, sql, params=None):
    cur.execute(sql, params or [])
    return cur.fetchone()


def fetchval(cur, sql, params=None):
    row = fetchone(cur, sql, params)
    return row[0] if row else None


def update_row(cur, table, row_id, values, id_col="id"):
    if not values:
        return
    assignments = ", ".join(f"{column} = %s" for column in values.keys())
    cur.execute(
        f"UPDATE {SCHEMA}.{table} SET {assignments} WHERE {id_col} = %s",
        list(values.values()) + [row_id],
    )


def upsert_row(cur, table, key_values, values, id_col="id"):
    if table == "riskassessment":
        key_values = {k: (v[:50] if isinstance(v, str) else v) for k, v in key_values.items()}
        values = {k: (v[:50] if isinstance(v, str) else v) for k, v in values.items()}
    clauses = []
    params = []
    for column, value in key_values.items():
        if value is None:
            clauses.append(f"{column} IS NULL")
        else:
            clauses.append(f"{column} = %s")
            params.append(value)
    where_sql = " AND ".join(clauses)
    row_id = fetchval(
        cur,
        f"SELECT {id_col} FROM {SCHEMA}.{table} WHERE {where_sql} LIMIT 1",
        params,
    )
    payload = {**key_values, **values}
    if row_id is not None:
        update_row(cur, table, row_id, payload, id_col=id_col)
        return row_id
    columns = ", ".join(payload.keys())
    placeholders = ", ".join(["%s"] * len(payload))
    cur.execute(
        f"INSERT INTO {SCHEMA}.{table} ({columns}) VALUES ({placeholders}) RETURNING {id_col}",
        list(payload.values()),
    )
    return cur.fetchone()[0]


def ensure_demo_file(reference_id, filename, content):
    relative_path = Path("audit-documents") / str(reference_id) / filename
    full_path = UPLOAD / relative_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text(content, encoding="utf-8")
    return relative_path.as_posix(), full_path.name, full_path.stat().st_size


def reset_batch_rows(cur, table, batch_id, rows):
    cur.execute(f"DELETE FROM {SCHEMA}.{table} WHERE import_batch_id = %s", [batch_id])
    for row in rows:
        columns = ", ".join(row.keys())
        placeholders = ", ".join(["%s"] * len(row))
        cur.execute(
            f"INSERT INTO {SCHEMA}.{table} ({columns}) VALUES ({placeholders})",
            list(row.values()),
        )


def sync_sequence(cur, table, column):
    default_expr = fetchval(
        cur,
        """
        SELECT column_default
        FROM information_schema.columns
        WHERE table_schema = 'Risk_Assess_Framework'
          AND table_name = %s
          AND column_name = %s
        """,
        [table, column],
    )
    sequence_name = None
    if default_expr:
        match = re.search(r"nextval\\('([^']+)'::regclass\\)", default_expr)
        if match:
            sequence_name = match.group(1)
    if not sequence_name:
        return
    cur.execute(
        f"SELECT setval(%s::regclass, COALESCE((SELECT MAX({column}) FROM {SCHEMA}.{table}), 1), true)",
        [sequence_name],
    )


def seed_internal(cur, now):
    today = now.date()

    project_id = upsert_row(
        cur,
        "projects",
        {"name": "Audit Core Demo - Internal Procurement Engagement"},
        {
            "description": "Internal audit engagement for procure-to-pay governance and payment controls.",
            "status_id": 1,
            "department_id": 4,
            "start_date": today - timedelta(days=14),
            "end_date": today + timedelta(days=45),
            "budget": 125000,
            "risk_level_id": 2,
            "manager": "Head of Internal Audit",
            "created_at": now,
            "updated_at": now,
        },
    )

    reference_id = upsert_row(
        cur,
        "riskassessmentreference",
        {"title": "Demo Internal Audit - Procure to Pay"},
        {
            "client": "Aurora Group Internal Audit",
            "assessor": ADMIN,
            "approved_by": "Chief Audit Executive",
            "created_date": now,
            "assessment_start_date": today - timedelta(days=10),
            "assessment_end_date": today + timedelta(days=35),
            "department_id": 4,
            "project_id": project_id,
            "description": "Internal audit file showing planning, walkthroughs, working papers, findings, workflow queues, and review history.",
            "status_id": 1,
            "updated_at": now,
            "is_archived": False,
            "archived_at": None,
            "archived_by_user_id": None,
            "archived_by_name": None,
            "archive_reason": None,
        },
        id_col="reference_id",
    )

    plan_id = upsert_row(
        cur,
        "audit_engagement_plans",
        {"reference_id": reference_id},
        {
            "engagement_title": "Demo Internal Audit - Procure to Pay",
            "engagement_type_id": 1,
            "plan_year": 2026,
            "annual_plan_name": "FY2026 Internal Audit Plan",
            "business_unit": "Operations",
            "process_area": "Procure to Pay",
            "subprocess_area": "Vendor Master and Payment Processing",
            "fsli": "Accounts Payable and Operating Expenses",
            "scope_summary": "Assess vendor onboarding, three-way match, and duplicate payment controls.",
            "materiality": "Qualitative risk and control impact assessment for internal audit.",
            "risk_strategy": "Control design and operating effectiveness focus on high-risk payment activities.",
            "planning_status_id": 2,
            "scope_letter_document_id": None,
            "is_signed_off": False,
            "signed_off_by_name": None,
            "signed_off_by_user_id": None,
            "signed_off_at": None,
            "notes": "Derived from meeting-note priorities: scope, walkthroughs, procedures, working papers, review readiness.",
            "created_at": now,
            "updated_at": now,
            "materiality_basis": "Qualitative risk and coverage basis",
            "overall_materiality": None,
            "performance_materiality": None,
            "clearly_trivial_threshold": None,
        },
    )

    risk_1 = upsert_row(
        cur,
        "riskassessment",
        {
            "reference_id": reference_id,
            "mainprocess": "Procure to Pay",
            "subprocess": "Vendor Master Maintenance",
            "keyriskandfactors": "Unauthorized vendor creation may enable fraudulent or duplicate payments.",
        },
        {
            "businessobjectives": "Valid vendor onboarding and authorized changes",
            "mitigatingcontrols": "SOD, approval workflow, vendor review",
            "responsibility": "Procurement",
            "authoriser": "Procurement Manager",
            "auditorsrecommendedactionplan": "Quarterly access review and maker-checker",
            "responsibleperson": "Procurement Lead",
            "agreeddate": today + timedelta(days=20),
            "risklikelihoodid": 4,
            "riskimpactid": 4,
            "keysecondaryid": 1,
            "riskcategoryid": 1,
            "datafrequencyid": 2,
            "frequencyid": 2,
            "evidenceid": 1,
            "outcomelikelihoodid": 3,
            "impactid": 2,
            "department_id": 4,
            "project_id": project_id,
            "auditor_id": ADMIN_ID,
            "status_id": 1,
            "created_at": now,
            "updated_at": now,
        },
        id_col="riskassessment_refid",
    )

    risk_2 = upsert_row(
        cur,
        "riskassessment",
        {
            "reference_id": reference_id,
            "mainprocess": "Procure to Pay",
            "subprocess": "Payment Processing",
            "keyriskandfactors": "Duplicate or unsupported payments",
        },
        {
            "businessobjectives": "Supported, accurate, single-instance payments",
            "mitigatingcontrols": "3-way match, duplicate check, approvals",
            "responsibility": "Accounts Payable",
            "authoriser": "Finance Manager",
            "auditorsrecommendedactionplan": "Review overrides and emergency evidence",
            "responsibleperson": "AP Supervisor",
            "agreeddate": today + timedelta(days=24),
            "risklikelihoodid": 3,
            "riskimpactid": 4,
            "keysecondaryid": 1,
            "riskcategoryid": 1,
            "datafrequencyid": 3,
            "frequencyid": 3,
            "evidenceid": 1,
            "outcomelikelihoodid": 2,
            "impactid": 2,
            "department_id": 4,
            "project_id": project_id,
            "auditor_id": ADMIN_ID,
            "status_id": 1,
            "created_at": now,
            "updated_at": now,
        },
        id_col="riskassessment_refid",
    )

    scope_1 = upsert_row(
        cur,
        "audit_scope_items",
        {
            "reference_id": reference_id,
            "process_name": "Procure to Pay",
            "subprocess_name": "Vendor Master Maintenance",
            "fsli": "Accounts Payable",
        },
        {
            "plan_id": plan_id,
            "business_unit": "Operations",
            "scope_status": "In Scope",
            "include_in_scope": True,
            "risk_reference": f"RA-{risk_1}",
            "control_reference": "P2P-C1",
            "procedure_id": None,
            "owner": "Procurement Lead",
            "notes": "Selected due to fraud risk and access sensitivity.",
            "created_at": now,
            "assertions": "Authorization, Completeness",
            "scoping_rationale": "High exposure to vendor fraud and onboarding override risk.",
        },
    )

    scope_2 = upsert_row(
        cur,
        "audit_scope_items",
        {
            "reference_id": reference_id,
            "process_name": "Procure to Pay",
            "subprocess_name": "Payment Processing",
            "fsli": "Operating Expenses",
        },
        {
            "plan_id": plan_id,
            "business_unit": "Finance Operations",
            "scope_status": "In Scope",
            "include_in_scope": True,
            "risk_reference": f"RA-{risk_2}",
            "control_reference": "P2P-C2",
            "procedure_id": None,
            "owner": "AP Supervisor",
            "notes": "Selected for duplicate-payment and support completeness testing.",
            "created_at": now,
            "assertions": "Occurrence, Accuracy",
            "scoping_rationale": "High transaction volume and exception-prone payment process.",
        },
    )

    procedure_1 = upsert_row(
        cur,
        "audit_procedures",
        {"reference_id": reference_id, "procedure_code": "DEMO-INT-PROC-001"},
        {
            "audit_universe_id": None,
            "procedure_title": "Vendor Master Access Review",
            "objective": "Confirm that vendor maintenance is restricted and approved.",
            "procedure_description": "Inspect user access listings, review approval evidence, and test recent vendor changes.",
            "procedure_type_id": 3,
            "status_id": 2,
            "sample_size": 10,
            "expected_evidence": "Access matrix, approval logs, vendor change reports.",
            "working_paper_ref": "WP-INT-001",
            "owner": "Audit Senior",
            "performer_user_id": ADMIN_ID,
            "reviewer_user_id": MANAGER_ID,
            "planned_date": today - timedelta(days=5),
            "performed_date": today - timedelta(days=1),
            "reviewed_date": None,
            "conclusion": "Testing in progress.",
            "notes": "Procedure aligns with Karabo discussion on procedures library and working-paper linkage.",
            "is_template": False,
            "source_template_id": None,
            "created_by_user_id": ADMIN_ID,
            "is_active": True,
            "created_at": now,
            "updated_at": now,
            "applicable_engagement_type_id": 1,
            "template_pack": "Internal Audit Core",
            "template_tags": "access,vendor,procure-to-pay",
        },
    )

    procedure_2 = upsert_row(
        cur,
        "audit_procedures",
        {"reference_id": reference_id, "procedure_code": "DEMO-INT-PROC-002"},
        {
            "audit_universe_id": None,
            "procedure_title": "Duplicate Payment Reperformance",
            "objective": "Identify duplicate payment indicators and assess control response.",
            "procedure_description": "Analyze recent payment runs, investigate duplicate invoice matches, and inspect exception approvals.",
            "procedure_type_id": 4,
            "status_id": 4,
            "sample_size": 2,
            "expected_evidence": "Payment register, duplicate report, exception approvals.",
            "working_paper_ref": "WP-INT-002",
            "owner": "Audit Senior",
            "performer_user_id": ADMIN_ID,
            "reviewer_user_id": MANAGER_ID,
            "planned_date": today - timedelta(days=4),
            "performed_date": today - timedelta(days=2),
            "reviewed_date": None,
            "conclusion": "Ready for review.",
            "notes": "Used to populate review-ready workpaper and review queues.",
            "is_template": False,
            "source_template_id": None,
            "created_by_user_id": ADMIN_ID,
            "is_active": True,
            "created_at": now,
            "updated_at": now,
            "applicable_engagement_type_id": 1,
            "template_pack": "Internal Audit Core",
            "template_tags": "payments,analytics,reperformance",
        },
    )

    matrix_1 = upsert_row(
        cur,
        "audit_risk_control_matrix",
        {
            "reference_id": reference_id,
            "risk_title": "Unauthorized vendor creation",
            "control_name": "Vendor changes require maker-checker approval",
        },
        {
            "scope_item_id": scope_1,
            "procedure_id": procedure_1,
            "risk_description": "Unapproved vendor changes can facilitate fraud or duplicate vendors.",
            "control_description": "System workflow requires separate requester and approver for vendor changes.",
            "control_adequacy": "Adequate",
            "control_effectiveness": "Needs validation",
            "control_classification_id": 1,
            "control_type_id": 2,
            "control_frequency_id": 2,
            "control_owner": "Procurement Lead",
            "notes": "Focus on privileged access and override handling.",
            "created_at": now,
            "updated_at": now,
        },
    )

    upsert_row(
        cur,
        "audit_risk_control_matrix",
        {
            "reference_id": reference_id,
            "risk_title": "Duplicate or unsupported payments",
            "control_name": "Payment run duplicate check and approval",
        },
        {
            "scope_item_id": scope_2,
            "procedure_id": procedure_2,
            "risk_description": "Unsupported or duplicate payments can lead to direct financial loss.",
            "control_description": "AP system flags duplicate invoices and requires finance approval for exceptions.",
            "control_adequacy": "Partially adequate",
            "control_effectiveness": "Exception-prone",
            "control_classification_id": 2,
            "control_type_id": 2,
            "control_frequency_id": 3,
            "control_owner": "AP Supervisor",
            "notes": "Emergency payments bypassing evidence are a noted concern.",
            "created_at": now,
            "updated_at": now,
        },
    )

    upsert_row(
        cur,
        "audit_walkthroughs",
        {"reference_id": reference_id, "process_name": "Procure to Pay Vendor Walkthrough"},
        {
            "scope_item_id": scope_1,
            "procedure_id": procedure_1,
            "risk_control_matrix_id": matrix_1,
            "walkthrough_date": today - timedelta(days=3),
            "participants": "Audit Senior; Procurement Lead; AP Supervisor",
            "process_narrative": "Walkthrough covered vendor request initiation, approval, master update, and downstream payment usage.",
            "evidence_summary": "Screenshots of workflow approvals and vendor-change extracts captured.",
            "control_design_conclusion": "Control design appears sound; user access monitoring needs stronger evidence.",
            "notes": "Use as walkthrough section in execution.",
            "created_at": now,
            "updated_at": now,
        },
    )

    working_paper_1 = upsert_row(
        cur,
        "audit_working_papers",
        {"reference_id": reference_id, "working_paper_code": "WP-INT-001"},
        {
            "audit_universe_id": None,
            "procedure_id": procedure_1,
            "title": "Vendor Master Access Testing",
            "objective": "Document access testing and approval validation.",
            "description": "Working paper for vendor master access sample testing.",
            "status_id": 4,
            "prepared_by": "Audit Senior",
            "prepared_by_user_id": ADMIN_ID,
            "reviewer_name": MANAGER,
            "reviewer_user_id": MANAGER_ID,
            "conclusion": "One privileged account lacked current approval evidence.",
            "notes": "Open review note retained for demo.",
            "prepared_date": today - timedelta(days=1),
            "reviewed_date": None,
            "is_template": False,
            "source_template_id": None,
            "is_active": True,
            "created_at": now,
            "updated_at": now,
            "applicable_engagement_type_id": 1,
            "template_pack": "Internal Audit Core",
            "template_tags": "access,review-ready",
        },
    )

    working_paper_2 = upsert_row(
        cur,
        "audit_working_papers",
        {"reference_id": reference_id, "working_paper_code": "WP-INT-002"},
        {
            "audit_universe_id": None,
            "procedure_id": procedure_2,
            "title": "Duplicate Payment Analysis",
            "objective": "Document reperformance of duplicate-payment analysis.",
            "description": "Working paper for duplicate payment analytics and exception follow-up.",
            "status_id": 5,
            "prepared_by": "Audit Senior",
            "prepared_by_user_id": ADMIN_ID,
            "reviewer_name": MANAGER,
            "reviewer_user_id": MANAGER_ID,
            "conclusion": "Three duplicate-payment exceptions identified and escalated.",
            "notes": "Signed off to support reporting reconciliation counts.",
            "prepared_date": today - timedelta(days=2),
            "reviewed_date": today - timedelta(days=1),
            "is_template": False,
            "source_template_id": None,
            "is_active": True,
            "created_at": now,
            "updated_at": now,
            "applicable_engagement_type_id": 1,
            "template_pack": "Internal Audit Core",
            "template_tags": "analytics,signed-off",
        },
    )

    upsert_row(
        cur,
        "audit_working_paper_signoffs",
        {"working_paper_id": working_paper_2, "action_type": "Reviewer Sign-Off", "signed_by_name": MANAGER},
        {
            "signed_by_user_id": MANAGER_ID,
            "comment": "Evidence complete and ready for reporting.",
            "signed_at": now - timedelta(days=1),
        },
    )

    finding_id = upsert_row(
        cur,
        "audit_findings",
        {"reference_id": reference_id, "finding_number": "INT-F-001"},
        {
            "audit_universe_id": None,
            "finding_title": "Vendor master approvals not consistently evidenced",
            "finding_description": "One high-risk vendor change lacked retained approval support in the sampled population.",
            "severity_id": 3,
            "status_id": 2,
            "identified_date": today - timedelta(days=2),
            "due_date": today + timedelta(days=20),
            "closed_date": None,
            "assigned_to": "Procurement Lead",
            "assigned_to_user_id": 5,
            "root_cause": "Manual evidence retention outside the workflow.",
            "business_impact": "Increases risk of unauthorized vendor setup and weakens detective review.",
            "created_by_user_id": ADMIN_ID,
            "created_at": now,
            "updated_at": now,
        },
    )

    recommendation_id = upsert_row(
        cur,
        "audit_recommendations",
        {"finding_id": finding_id, "recommendation_number": "INT-R-001"},
        {
            "recommendation": "Centralize vendor-change approvals in the workflow and run a quarterly privileged-access review.",
            "priority": 2,
            "management_response": "Management agrees and will configure evidence retention in Q2.",
            "agreed_date": today - timedelta(days=1),
            "target_date": today + timedelta(days=30),
            "implementation_date": None,
            "responsible_person": "Procurement Lead",
            "responsible_user_id": 5,
            "status_id": 2,
            "verification_notes": None,
            "verified_by_user_id": None,
            "verified_date": None,
            "created_at": now,
            "updated_at": now,
        },
    )

    upsert_row(
        cur,
        "audit_management_actions",
        {"reference_id": reference_id, "action_title": "Implement vendor approval evidence retention"},
        {
            "finding_id": finding_id,
            "recommendation_id": recommendation_id,
            "action_description": "Configure vendor change workflow to store approval artifacts and run monthly exception review.",
            "owner_name": "Procurement Lead",
            "owner_user_id": 5,
            "due_date": today + timedelta(days=18),
            "status": "Open",
            "progress_percent": 35,
            "management_response": "Configuration draft prepared.",
            "closure_notes": None,
            "validated_by_name": None,
            "validated_by_user_id": None,
            "validated_at": None,
            "created_at": now,
            "updated_at": now,
        },
    )

    relative_path, stored_file_name, file_size = ensure_demo_file(
        reference_id,
        "demo-int-scope-letter.txt",
        "Demo internal audit scope letter for procure to pay.\nIncludes objectives, scope, and stakeholders.",
    )
    document_1 = upsert_row(
        cur,
        "audit_documents",
        {"reference_id": reference_id, "document_code": "DEMO-INT-DOC-001"},
        {
            "audit_universe_id": None,
            "procedure_id": None,
            "working_paper_id": None,
            "finding_id": None,
            "recommendation_id": None,
            "title": "Internal Scope Letter",
            "original_file_name": "internal-scope-letter.txt",
            "stored_file_name": stored_file_name,
            "stored_relative_path": relative_path,
            "content_type": "text/plain",
            "file_extension": ".txt",
            "file_size": file_size,
            "category_id": 1,
            "source_type": "SeedData",
            "tags": "scope,planning,internal",
            "notes": "Demo planning document",
            "uploaded_by_name": ADMIN,
            "uploaded_by_user_id": ADMIN_ID,
            "uploaded_at": now,
            "is_active": True,
        },
    )

    relative_path, stored_file_name, file_size = ensure_demo_file(
        reference_id,
        "demo-int-walkthrough.txt",
        "Demo walkthrough evidence for vendor change approvals and payment control design review.",
    )
    document_2 = upsert_row(
        cur,
        "audit_documents",
        {"reference_id": reference_id, "document_code": "DEMO-INT-DOC-002"},
        {
            "audit_universe_id": None,
            "procedure_id": procedure_1,
            "working_paper_id": working_paper_1,
            "finding_id": finding_id,
            "recommendation_id": recommendation_id,
            "title": "Vendor Walkthrough Evidence",
            "original_file_name": "vendor-walkthrough.txt",
            "stored_file_name": stored_file_name,
            "stored_relative_path": relative_path,
            "content_type": "text/plain",
            "file_extension": ".txt",
            "file_size": file_size,
            "category_id": 3,
            "source_type": "SeedData",
            "tags": "walkthrough,evidence,vendor",
            "notes": "Demo walkthrough support file",
            "uploaded_by_name": ADMIN,
            "uploaded_by_user_id": ADMIN_ID,
            "uploaded_at": now,
            "is_active": True,
        },
    )

    evidence_request_id = upsert_row(
        cur,
        "audit_evidence_requests",
        {"reference_id": reference_id, "request_number": "INT-EVR-001"},
        {
            "audit_universe_id": None,
            "title": "Provide vendor change approvals",
            "request_description": "Upload approval evidence for sampled vendor changes and any emergency overrides.",
            "requested_from": "Procurement Lead",
            "requested_to_email": "procurement.lead@example.com",
            "priority": 2,
            "due_date": today + timedelta(days=7),
            "status_id": 3,
            "requested_by_user_id": ADMIN_ID,
            "requested_by_name": ADMIN,
            "workflow_instance_id": None,
            "notes": "Supports working paper WP-INT-001",
            "created_at": now,
            "updated_at": now,
        },
    )

    upsert_row(
        cur,
        "audit_evidence_request_items",
        {"request_id": evidence_request_id, "item_description": "Vendor change approval for sample VC-1042"},
        {
            "expected_document_type": "Approval Screenshot",
            "is_required": True,
            "fulfilled_document_id": document_2,
            "submitted_at": now - timedelta(days=1),
            "reviewer_notes": "Initial evidence uploaded.",
            "reviewed_by_user_id": ADMIN_ID,
            "reviewed_at": now - timedelta(days=1),
            "is_accepted": True,
            "created_at": now,
        },
    )

    upsert_row(
        cur,
        "audit_evidence_request_items",
        {"request_id": evidence_request_id, "item_description": "Emergency override approval evidence"},
        {
            "expected_document_type": "Email Approval",
            "is_required": True,
            "fulfilled_document_id": None,
            "submitted_at": None,
            "reviewer_notes": None,
            "reviewed_by_user_id": None,
            "reviewed_at": None,
            "is_accepted": None,
            "created_at": now,
        },
    )

    workflow_plan = f"demo-int-plan-{reference_id}"
    workflow_review = f"demo-int-wp-{reference_id}"

    upsert_row(
        cur,
        "audit_workflow_instances",
        {"workflow_instance_id": workflow_plan},
        {
            "reference_id": reference_id,
            "entity_type": "Planning",
            "entity_id": reference_id,
            "workflow_definition_id": "Audit.Planning.PlanningApproval.v1",
            "workflow_display_name": "Planning Approval",
            "status": "Running",
            "current_activity_id": "approve-planning",
            "current_activity_name": "Awaiting Planning Approval",
            "started_by_user_id": ADMIN_ID,
            "started_by_name": ADMIN,
            "started_at": now - timedelta(days=1),
            "last_synced_at": now - timedelta(hours=2),
            "completed_at": None,
            "is_active": True,
            "metadata_json": Json({"demo": True, "engagementType": "Internal Audit"}),
        },
    )

    upsert_row(
        cur,
        "audit_workflow_instances",
        {"workflow_instance_id": workflow_review},
        {
            "reference_id": reference_id,
            "entity_type": "WorkingPaper",
            "entity_id": reference_id,
            "workflow_definition_id": "Audit.Execution.WorkpaperReview.v1",
            "workflow_display_name": "Working Paper Review",
            "status": "Running",
            "current_activity_id": "review-workpaper",
            "current_activity_name": "Review ready workpaper waiting",
            "started_by_user_id": ADMIN_ID,
            "started_by_name": ADMIN,
            "started_at": now - timedelta(hours=12),
            "last_synced_at": now - timedelta(hours=1),
            "completed_at": None,
            "is_active": True,
            "metadata_json": Json({"demo": True}),
        },
    )

    upsert_row(
        cur,
        "audit_workflow_tasks",
        {"workflow_instance_id": workflow_plan, "task_title": "Approve planning scope for Demo Internal Audit - Procure to Pay"},
        {
            "reference_id": reference_id,
            "entity_type": "Planning",
            "entity_id": reference_id,
            "task_description": "Review planning, scope, material scope notes, and approve the engagement setup.",
            "assignee_user_id": MANAGER_ID,
            "assignee_name": MANAGER,
            "status": "Pending",
            "priority": "High",
            "due_date": now + timedelta(days=5),
            "action_url": f"/assessments/{reference_id}?tab=planning",
            "created_at": now - timedelta(days=1),
            "completed_at": None,
            "completed_by_user_id": None,
            "completion_notes": None,
            "external_task_id": None,
            "external_task_source": None,
        },
    )

    upsert_row(
        cur,
        "audit_workflow_tasks",
        {"workflow_instance_id": workflow_review, "task_title": "Working paper review for duplicate payment analysis"},
        {
            "reference_id": reference_id,
            "entity_type": "WorkingPaper",
            "entity_id": reference_id,
            "task_description": "Review-ready working paper WP-INT-002 is waiting for review and sign-off.",
            "assignee_user_id": MANAGER_ID,
            "assignee_name": MANAGER,
            "status": "Pending",
            "priority": "Medium",
            "due_date": now + timedelta(days=2),
            "action_url": f"/assessments/{reference_id}?tab=working-papers",
            "created_at": now - timedelta(hours=10),
            "completed_at": None,
            "completed_by_user_id": None,
            "completion_notes": None,
            "external_task_id": None,
            "external_task_source": None,
        },
    )

    upsert_row(
        cur,
        "audit_notifications",
        {"workflow_instance_id": workflow_plan, "title": "Action Required: Planning approval pending", "recipient_name": MANAGER},
        {
            "reference_id": reference_id,
            "entity_type": "Planning",
            "entity_id": reference_id,
            "notification_type": "WorkflowTask",
            "severity": "Warning",
            "message": "Action required. Approve planning scope for the internal procurement audit file.",
            "recipient_user_id": MANAGER_ID,
            "is_read": False,
            "read_at": None,
            "action_url": f"/assessments/{reference_id}?tab=planning",
            "created_at": now - timedelta(hours=20),
        },
    )

    upsert_row(
        cur,
        "audit_notifications",
        {"workflow_instance_id": workflow_review, "title": "Review-ready workpaper submitted", "recipient_name": MANAGER},
        {
            "reference_id": reference_id,
            "entity_type": "WorkingPaper",
            "entity_id": reference_id,
            "notification_type": "ReviewReady",
            "severity": "Info",
            "message": "Working paper WP-INT-002 is ready for review.",
            "recipient_user_id": MANAGER_ID,
            "is_read": False,
            "read_at": None,
            "action_url": f"/assessments/{reference_id}?tab=working-papers",
            "created_at": now - timedelta(hours=9),
        },
    )

    review_task_1 = upsert_row(
        cur,
        "audit_tasks",
        {"reference_id": reference_id, "title": "Approve planning scope for Demo Internal Audit - Procure to Pay"},
        {
            "entity_type": "Planning",
            "entity_id": reference_id,
            "workflow_instance_id": workflow_plan,
            "task_type": "Approval",
            "description": "Generic review task for planning approval.",
            "assigned_to_user_id": MANAGER_ID,
            "assigned_to_name": MANAGER,
            "assigned_by_user_id": ADMIN_ID,
            "assigned_by_name": ADMIN,
            "status": "Open",
            "priority": "High",
            "due_date": now + timedelta(days=5),
            "completed_at": None,
            "completed_by_user_id": None,
            "completion_notes": None,
            "source": "Workflow",
            "created_at": now - timedelta(days=1),
            "updated_at": now - timedelta(days=1),
        },
    )

    review_task_2 = upsert_row(
        cur,
        "audit_tasks",
        {"reference_id": reference_id, "title": "Review working paper WP-INT-001"},
        {
            "entity_type": "WorkingPaper",
            "entity_id": reference_id,
            "workflow_instance_id": workflow_review,
            "task_type": "Review",
            "description": "Open review task for vendor access working paper.",
            "assigned_to_user_id": MANAGER_ID,
            "assigned_to_name": MANAGER,
            "assigned_by_user_id": ADMIN_ID,
            "assigned_by_name": ADMIN,
            "status": "Open",
            "priority": "Medium",
            "due_date": now + timedelta(days=3),
            "completed_at": None,
            "completed_by_user_id": None,
            "completion_notes": None,
            "source": "Workflow",
            "created_at": now - timedelta(hours=11),
            "updated_at": now - timedelta(hours=11),
        },
    )

    review_1 = upsert_row(
        cur,
        "audit_reviews",
        {"reference_id": reference_id, "review_type": "Planning Approval", "summary": "Approve internal planning scope and engagement setup"},
        {
            "entity_type": "Planning",
            "entity_id": reference_id,
            "status": "Pending",
            "task_id": review_task_1,
            "workflow_instance_id": workflow_plan,
            "assigned_reviewer_user_id": MANAGER_ID,
            "assigned_reviewer_name": MANAGER,
            "requested_by_user_id": ADMIN_ID,
            "requested_by_name": ADMIN,
            "requested_at": now - timedelta(days=1),
            "due_date": now + timedelta(days=5),
            "completed_at": None,
            "completed_by_user_id": None,
            "created_at": now - timedelta(days=1),
            "updated_at": now - timedelta(days=1),
        },
    )

    review_2 = upsert_row(
        cur,
        "audit_reviews",
        {"reference_id": reference_id, "review_type": "Working Paper Review", "summary": "Review vendor access testing and duplicate payment analysis"},
        {
            "entity_type": "WorkingPaper",
            "entity_id": reference_id,
            "status": "In Progress",
            "task_id": review_task_2,
            "workflow_instance_id": workflow_review,
            "assigned_reviewer_user_id": MANAGER_ID,
            "assigned_reviewer_name": MANAGER,
            "requested_by_user_id": ADMIN_ID,
            "requested_by_name": ADMIN,
            "requested_at": now - timedelta(hours=11),
            "due_date": now + timedelta(days=3),
            "completed_at": None,
            "completed_by_user_id": None,
            "created_at": now - timedelta(hours=11),
            "updated_at": now - timedelta(hours=11),
        },
    )

    upsert_row(
        cur,
        "audit_review_notes",
        {"review_id": review_2, "note_text": "Reviewer note: retain explicit evidence for privileged vendor change approval."},
        {
            "working_paper_section_id": None,
            "note_type": "Review Note",
            "severity": "High",
            "status": "Open",
            "response_text": "Management to attach workflow approval export.",
            "raised_by_user_id": MANAGER_ID,
            "raised_by_name": MANAGER,
            "raised_at": now - timedelta(hours=8),
            "cleared_by_user_id": None,
            "cleared_by_name": None,
            "cleared_at": None,
        },
    )

    upsert_row(
        cur,
        "audit_signoffs",
        {
            "reference_id": reference_id,
            "review_id": review_1,
            "signoff_type": "Planning Sign-Off",
            "signoff_level": "Manager",
        },
        {
            "entity_type": "Planning",
            "entity_id": reference_id,
            "workflow_instance_id": workflow_plan,
            "status": "Signed",
            "signed_by_user_id": MANAGER_ID,
            "signed_by_name": MANAGER,
            "signed_at": now - timedelta(days=7),
            "comment": "Historical planning sign-off retained for demo history",
        },
    )

    trail_event_1 = upsert_row(
        cur,
        "audit_trail_events",
        {"reference_id": reference_id, "action": "PlanningUpdated", "summary": "Internal audit planning and scope prepared"},
        {
            "entity_type": "Planning",
            "entity_id": reference_id,
            "category": "Planning",
            "performed_by_user_id": ADMIN_ID,
            "performed_by_name": ADMIN,
            "icon": "event_note",
            "color": "blue",
            "workflow_instance_id": workflow_plan,
            "correlation_id": f"demo-int-plan-{reference_id}",
            "source": "DemoSeed",
            "details_json": Json({"engagementType": "Internal Audit"}),
            "event_time": now - timedelta(days=1),
        },
    )

    upsert_row(
        cur,
        "audit_trail_entity_changes",
        {"audit_trail_event_id": trail_event_1, "field_name": "scope_summary"},
        {"old_value": "", "new_value": "Assess vendor onboarding, three-way match, and duplicate payment controls."},
    )

    upsert_row(
        cur,
        "audit_trail_events",
        {"reference_id": reference_id, "action": "FindingRaised", "summary": "Internal audit finding raised for vendor master approvals"},
        {
            "entity_type": "Finding",
            "entity_id": reference_id,
            "category": "Execution",
            "performed_by_user_id": ADMIN_ID,
            "performed_by_name": ADMIN,
            "icon": "report_problem",
            "color": "orange",
            "workflow_instance_id": None,
            "correlation_id": f"demo-int-find-{reference_id}",
            "source": "DemoSeed",
            "details_json": Json({"findingNumber": "INT-F-001"}),
            "event_time": now - timedelta(hours=6),
        },
    )

    update_row(
        cur,
        "audit_engagement_plans",
        plan_id,
        {"scope_letter_document_id": document_1, "updated_at": now},
    )

    return reference_id


def seed_external(cur, now):
    today = now.date()

    project_id = upsert_row(
        cur,
        "projects",
        {"name": "Audit Core Demo - External Revenue Engagement"},
        {
            "description": "External audit engagement for revenue recognition, receivables, and manual journal risks.",
            "status_id": 1,
            "department_id": 2,
            "start_date": today - timedelta(days=20),
            "end_date": today + timedelta(days=30),
            "budget": 210000,
            "risk_level_id": 3,
            "manager": "Engagement Partner",
            "created_at": now,
            "updated_at": now,
        },
    )

    reference_id = upsert_row(
        cur,
        "riskassessmentreference",
        {"title": "Demo External Audit - Revenue and Receivables"},
        {
            "client": "Aurora Manufacturing Group",
            "assessor": ADMIN,
            "approved_by": PARTNER,
            "created_date": now,
            "assessment_start_date": today - timedelta(days=15),
            "assessment_end_date": today + timedelta(days=20),
            "department_id": 2,
            "project_id": project_id,
            "description": "External audit file showing materiality, assertions, substantive analytics, workflows, review queues, and reporting reconciliation.",
            "status_id": 1,
            "updated_at": now,
            "is_archived": False,
            "archived_at": None,
            "archived_by_user_id": None,
            "archived_by_name": None,
            "archive_reason": None,
        },
        id_col="reference_id",
    )

    plan_id = upsert_row(
        cur,
        "audit_engagement_plans",
        {"reference_id": reference_id},
        {
            "engagement_title": "Demo External Audit - Revenue and Receivables",
            "engagement_type_id": 2,
            "plan_year": 2026,
            "annual_plan_name": "FY2026 Statutory Audit Plan",
            "business_unit": "Finance",
            "process_area": "Revenue to Cash",
            "subprocess_area": "Billing, Cut-Off and Journal Processing",
            "fsli": "Revenue, Trade Receivables and Journal Entries",
            "scope_summary": "External audit planning for revenue recognition, receivables existence, cut-off, and manual journals.",
            "materiality": "Overall materiality set for revenue and receivables testing.",
            "risk_strategy": "Combine controls, substantive analytics, journal testing, and cut-off testing for high-risk areas.",
            "planning_status_id": 3,
            "scope_letter_document_id": None,
            "is_signed_off": True,
            "signed_off_by_name": PARTNER,
            "signed_off_by_user_id": PARTNER_ID,
            "signed_off_at": now - timedelta(days=9),
            "notes": "Materiality and assertions populated so the external-audit planning view renders correctly.",
            "created_at": now,
            "updated_at": now,
            "materiality_basis": "5% of normalized profit before tax",
            "overall_materiality": 350000,
            "performance_materiality": 262500,
            "clearly_trivial_threshold": 17500,
        },
    )

    risk_1 = upsert_row(
        cur,
        "riskassessment",
        {
            "reference_id": reference_id,
            "mainprocess": "Revenue to Cash",
            "subprocess": "Revenue Cut-Off",
            "keyriskandfactors": "Revenue recognized in wrong period at cut-off",
        },
        {
            "businessobjectives": "Revenue recorded in the correct period",
            "mitigatingcontrols": "Shipment reconcile and cut-off review",
            "responsibility": "Revenue Accounting",
            "authoriser": "Financial Controller",
            "auditorsrecommendedactionplan": "Inspect cut-off evidence and late postings",
            "responsibleperson": "Revenue Manager",
            "agreeddate": today + timedelta(days=10),
            "risklikelihoodid": 4,
            "riskimpactid": 5,
            "keysecondaryid": 1,
            "riskcategoryid": 1,
            "datafrequencyid": 3,
            "frequencyid": 3,
            "evidenceid": 1,
            "outcomelikelihoodid": 4,
            "impactid": 3,
            "department_id": 2,
            "project_id": project_id,
            "auditor_id": ADMIN_ID,
            "status_id": 1,
            "created_at": now,
            "updated_at": now,
        },
        id_col="riskassessment_refid",
    )

    risk_2 = upsert_row(
        cur,
        "riskassessment",
        {
            "reference_id": reference_id,
            "mainprocess": "Record to Report",
            "subprocess": "Manual Journal Entries",
            "keyriskandfactors": "Management override via manual journals",
        },
        {
            "businessobjectives": "Manual journals valid, approved, supported",
            "mitigatingcontrols": "Journal approvals, restricted access, review",
            "responsibility": "Financial Control",
            "authoriser": "Finance Director",
            "auditorsrecommendedactionplan": "Target post-close and weekend journals",
            "responsibleperson": "Financial Controller",
            "agreeddate": today + timedelta(days=8),
            "risklikelihoodid": 4,
            "riskimpactid": 5,
            "keysecondaryid": 1,
            "riskcategoryid": 1,
            "datafrequencyid": 3,
            "frequencyid": 3,
            "evidenceid": 1,
            "outcomelikelihoodid": 4,
            "impactid": 3,
            "department_id": 2,
            "project_id": project_id,
            "auditor_id": ADMIN_ID,
            "status_id": 1,
            "created_at": now,
            "updated_at": now,
        },
        id_col="riskassessment_refid",
    )

    scope_1 = upsert_row(
        cur,
        "audit_scope_items",
        {
            "reference_id": reference_id,
            "process_name": "Revenue to Cash",
            "subprocess_name": "Revenue Cut-Off",
            "fsli": "Revenue",
        },
        {
            "plan_id": plan_id,
            "business_unit": "Finance",
            "scope_status": "In Scope",
            "include_in_scope": True,
            "risk_reference": f"RA-{risk_1}",
            "control_reference": "REV-C1",
            "procedure_id": None,
            "owner": "Revenue Manager",
            "notes": "Material to the financial statements and prone to cut-off error.",
            "created_at": now,
            "assertions": "Occurrence, Cut-off, Accuracy",
            "scoping_rationale": "High risk around year-end shipment and invoice timing.",
        },
    )

    scope_2 = upsert_row(
        cur,
        "audit_scope_items",
        {
            "reference_id": reference_id,
            "process_name": "Record to Report",
            "subprocess_name": "Manual Journal Entries",
            "fsli": "Revenue and Expenses",
        },
        {
            "plan_id": plan_id,
            "business_unit": "Financial Control",
            "scope_status": "In Scope",
            "include_in_scope": True,
            "risk_reference": f"RA-{risk_2}",
            "control_reference": "R2R-C4",
            "procedure_id": None,
            "owner": "Financial Controller",
            "notes": "Management override risk and unusual postings require targeted analytics.",
            "created_at": now,
            "assertions": "Occurrence, Accuracy, Presentation",
            "scoping_rationale": "Manual journals remain a key external-audit fraud risk area.",
        },
    )

    procedure_1 = upsert_row(
        cur,
        "audit_procedures",
        {"reference_id": reference_id, "procedure_code": "DEMO-EXT-PROC-001"},
        {
            "audit_universe_id": None,
            "procedure_title": "Revenue Cut-Off Substantive Test",
            "objective": "Test whether revenue around period end was recognized in the correct period.",
            "procedure_description": "Select shipments and invoices around year-end, inspect support, and evaluate cut-off accuracy.",
            "procedure_type_id": 5,
            "status_id": 4,
            "sample_size": 15,
            "expected_evidence": "Shipping docs, invoices, cut-off review, GL support.",
            "working_paper_ref": "WP-EXT-001",
            "owner": "Audit Senior",
            "performer_user_id": ADMIN_ID,
            "reviewer_user_id": PARTNER_ID,
            "planned_date": today - timedelta(days=7),
            "performed_date": today - timedelta(days=3),
            "reviewed_date": None,
            "conclusion": "Exceptions noted for two late manual postings.",
            "notes": "Used to demonstrate materiality and assertions in planning/execution.",
            "is_template": False,
            "source_template_id": None,
            "created_by_user_id": ADMIN_ID,
            "is_active": True,
            "created_at": now,
            "updated_at": now,
            "applicable_engagement_type_id": 2,
            "template_pack": "External Audit Core",
            "template_tags": "revenue,cut-off,substantive",
        },
    )

    procedure_2 = upsert_row(
        cur,
        "audit_procedures",
        {"reference_id": reference_id, "procedure_code": "DEMO-EXT-PROC-002"},
        {
            "audit_universe_id": None,
            "procedure_title": "Manual Journal Analytics",
            "objective": "Identify unusual journals, weekend postings, and period-end manual entries indicative of override.",
            "procedure_description": "Analyze manual journals by user, date, and timing; inspect large or unusual entries.",
            "procedure_type_id": 4,
            "status_id": 3,
            "sample_size": 12,
            "expected_evidence": "Journal extract, approvals, supporting schedules.",
            "working_paper_ref": "WP-EXT-002",
            "owner": "Audit Senior",
            "performer_user_id": ADMIN_ID,
            "reviewer_user_id": PARTNER_ID,
            "planned_date": today - timedelta(days=6),
            "performed_date": today - timedelta(days=2),
            "reviewed_date": None,
            "conclusion": "Several post-close and weekend journals identified for follow-up.",
            "notes": "Feeds the analytical suite and reconciliation widget.",
            "is_template": False,
            "source_template_id": None,
            "created_by_user_id": ADMIN_ID,
            "is_active": True,
            "created_at": now,
            "updated_at": now,
            "applicable_engagement_type_id": 2,
            "template_pack": "External Audit Core",
            "template_tags": "journals,management-override,analytics",
        },
    )

    upsert_row(
        cur,
        "audit_risk_control_matrix",
        {
            "reference_id": reference_id,
            "risk_title": "Revenue cut-off misstatement",
            "control_name": "Period-end cut-off review",
        },
        {
            "scope_item_id": scope_1,
            "procedure_id": procedure_1,
            "risk_description": "Revenue may be posted before transfer of control or after the period closes.",
            "control_description": "Finance performs period-end cut-off reconciliation between shipments and invoices.",
            "control_adequacy": "Adequate",
            "control_effectiveness": "Pending validation",
            "control_classification_id": 2,
            "control_type_id": 1,
            "control_frequency_id": 3,
            "control_owner": "Revenue Manager",
            "notes": "Assertions emphasize occurrence and cut-off.",
            "created_at": now,
            "updated_at": now,
        },
    )

    matrix_2 = upsert_row(
        cur,
        "audit_risk_control_matrix",
        {
            "reference_id": reference_id,
            "risk_title": "Management override via journals",
            "control_name": "Manual journal approval review",
        },
        {
            "scope_item_id": scope_2,
            "procedure_id": procedure_2,
            "risk_description": "Manual journals can be used to bias reported results.",
            "control_description": "Controller reviews all large and period-end manual journals.",
            "control_adequacy": "Partially adequate",
            "control_effectiveness": "Exception follow-up required",
            "control_classification_id": 2,
            "control_type_id": 1,
            "control_frequency_id": 3,
            "control_owner": "Financial Controller",
            "notes": "Useful for workflow inbox and review sign-off demo.",
            "created_at": now,
            "updated_at": now,
        },
    )

    upsert_row(
        cur,
        "audit_walkthroughs",
        {"reference_id": reference_id, "process_name": "Revenue Close Walkthrough"},
        {
            "scope_item_id": scope_1,
            "procedure_id": procedure_1,
            "risk_control_matrix_id": matrix_2,
            "walkthrough_date": today - timedelta(days=4),
            "participants": "Audit Senior; Revenue Manager; Financial Controller",
            "process_narrative": "Walkthrough covered shipment confirmation, billing, cut-off review, and journal escalation process.",
            "evidence_summary": "Month-end close checklist and sample shipment-to-invoice reconciliation obtained.",
            "control_design_conclusion": "Design largely appropriate; manual journal escalation relies heavily on reviewer judgment.",
            "notes": "Cross-functional walkthrough for external audit demo.",
            "created_at": now,
            "updated_at": now,
        },
    )

    working_paper_1 = upsert_row(
        cur,
        "audit_working_papers",
        {"reference_id": reference_id, "working_paper_code": "WP-EXT-001"},
        {
            "audit_universe_id": None,
            "procedure_id": procedure_1,
            "title": "Revenue Cut-Off Testing",
            "objective": "Document substantive cut-off testing around period end.",
            "description": "Working paper for shipment/invoice cut-off testing.",
            "status_id": 4,
            "prepared_by": "Audit Senior",
            "prepared_by_user_id": ADMIN_ID,
            "reviewer_name": PARTNER,
            "reviewer_user_id": PARTNER_ID,
            "conclusion": "Two late-posted items require management explanation.",
            "notes": "Open reviewer note retained.",
            "prepared_date": today - timedelta(days=3),
            "reviewed_date": None,
            "is_template": False,
            "source_template_id": None,
            "is_active": True,
            "created_at": now,
            "updated_at": now,
            "applicable_engagement_type_id": 2,
            "template_pack": "External Audit Core",
            "template_tags": "revenue,review-ready",
        },
    )

    working_paper_2 = upsert_row(
        cur,
        "audit_working_papers",
        {"reference_id": reference_id, "working_paper_code": "WP-EXT-002"},
        {
            "audit_universe_id": None,
            "procedure_id": procedure_2,
            "title": "Manual Journal Analytics",
            "objective": "Document management override analytics and journal follow-up.",
            "description": "Working paper for manual journal exception analysis.",
            "status_id": 5,
            "prepared_by": "Audit Senior",
            "prepared_by_user_id": ADMIN_ID,
            "reviewer_name": PARTNER,
            "reviewer_user_id": PARTNER_ID,
            "conclusion": "Weekend and post-close journals identified and linked to finding.",
            "notes": "Signed off to support execution summary.",
            "prepared_date": today - timedelta(days=2),
            "reviewed_date": today - timedelta(days=1),
            "is_template": False,
            "source_template_id": None,
            "is_active": True,
            "created_at": now,
            "updated_at": now,
            "applicable_engagement_type_id": 2,
            "template_pack": "External Audit Core",
            "template_tags": "journals,signed-off",
        },
    )

    upsert_row(
        cur,
        "audit_working_paper_signoffs",
        {"working_paper_id": working_paper_2, "action_type": "Partner Sign-Off", "signed_by_name": PARTNER},
        {
            "signed_by_user_id": PARTNER_ID,
            "comment": "Analytics reviewed and accepted for reporting.",
            "signed_at": now - timedelta(days=1),
        },
    )

    finding_id = upsert_row(
        cur,
        "audit_findings",
        {"reference_id": reference_id, "finding_number": "EXT-F-001"},
        {
            "audit_universe_id": None,
            "finding_title": "Late manual journals posted after close review",
            "finding_description": "Multiple manual journals were posted after the documented close review and lacked timely escalation.",
            "severity_id": 2,
            "status_id": 5,
            "identified_date": today - timedelta(days=2),
            "due_date": today - timedelta(days=1),
            "closed_date": None,
            "assigned_to": "Financial Controller",
            "assigned_to_user_id": 3,
            "root_cause": "Late close adjustments and inconsistent escalation protocol.",
            "business_impact": "Creates risk of management override and cut-off misstatement in reported results.",
            "created_by_user_id": ADMIN_ID,
            "created_at": now,
            "updated_at": now,
        },
    )

    recommendation_id = upsert_row(
        cur,
        "audit_recommendations",
        {"finding_id": finding_id, "recommendation_number": "EXT-R-001"},
        {
            "recommendation": "Require documented approval for all post-close manual journals and daily monitoring of unusual postings.",
            "priority": 1,
            "management_response": "Management agrees and is preparing a revised close protocol.",
            "agreed_date": today - timedelta(days=1),
            "target_date": today + timedelta(days=14),
            "implementation_date": None,
            "responsible_person": "Financial Controller",
            "responsible_user_id": 3,
            "status_id": 3,
            "verification_notes": None,
            "verified_by_user_id": None,
            "verified_date": None,
            "created_at": now,
            "updated_at": now,
        },
    )

    upsert_row(
        cur,
        "audit_management_actions",
        {"reference_id": reference_id, "action_title": "Revise post-close journal approval protocol"},
        {
            "finding_id": finding_id,
            "recommendation_id": recommendation_id,
            "action_description": "Implement escalation and approval evidence for all post-close and weekend manual journals.",
            "owner_name": "Financial Controller",
            "owner_user_id": 3,
            "due_date": today - timedelta(days=1),
            "status": "In Progress",
            "progress_percent": 60,
            "management_response": "Draft protocol circulated but not fully implemented.",
            "closure_notes": None,
            "validated_by_name": None,
            "validated_by_user_id": None,
            "validated_at": None,
            "created_at": now,
            "updated_at": now,
        },
    )

    relative_path, stored_file_name, file_size = ensure_demo_file(
        reference_id,
        "demo-ext-materiality-memo.txt",
        "Demo external audit materiality memo. Overall materiality 350000, performance materiality 262500, clearly trivial 17500.",
    )
    document_1 = upsert_row(
        cur,
        "audit_documents",
        {"reference_id": reference_id, "document_code": "DEMO-EXT-DOC-001"},
        {
            "audit_universe_id": None,
            "procedure_id": None,
            "working_paper_id": None,
            "finding_id": None,
            "recommendation_id": None,
            "title": "Materiality and Planning Memo",
            "original_file_name": "materiality-memo.txt",
            "stored_file_name": stored_file_name,
            "stored_relative_path": relative_path,
            "content_type": "text/plain",
            "file_extension": ".txt",
            "file_size": file_size,
            "category_id": 2,
            "source_type": "SeedData",
            "tags": "materiality,planning,external",
            "notes": "Demo planning memo for external audit",
            "uploaded_by_name": ADMIN,
            "uploaded_by_user_id": ADMIN_ID,
            "uploaded_at": now,
            "is_active": True,
        },
    )

    relative_path, stored_file_name, file_size = ensure_demo_file(
        reference_id,
        "demo-ext-journal-analytics.txt",
        "Demo journal analytics summary showing weekend, post-close, and user concentration exceptions.",
    )
    document_2 = upsert_row(
        cur,
        "audit_documents",
        {"reference_id": reference_id, "document_code": "DEMO-EXT-DOC-002"},
        {
            "audit_universe_id": None,
            "procedure_id": procedure_2,
            "working_paper_id": working_paper_2,
            "finding_id": finding_id,
            "recommendation_id": recommendation_id,
            "title": "Journal Analytics Output",
            "original_file_name": "journal-analytics.txt",
            "stored_file_name": stored_file_name,
            "stored_relative_path": relative_path,
            "content_type": "text/plain",
            "file_extension": ".txt",
            "file_size": file_size,
            "category_id": 6,
            "source_type": "SeedData",
            "tags": "analytics,journals,external",
            "notes": "Demo analytics export for analytical suite",
            "uploaded_by_name": ADMIN,
            "uploaded_by_user_id": ADMIN_ID,
            "uploaded_at": now,
            "is_active": True,
        },
    )

    evidence_request_id = upsert_row(
        cur,
        "audit_evidence_requests",
        {"reference_id": reference_id, "request_number": "EXT-EVR-001"},
        {
            "audit_universe_id": None,
            "title": "Provide support for post-close journals",
            "request_description": "Upload approval and business rationale for period-end and weekend manual journals selected by audit.",
            "requested_from": "Financial Controller",
            "requested_to_email": "finance.controller@example.com",
            "priority": 1,
            "due_date": today + timedelta(days=3),
            "status_id": 4,
            "requested_by_user_id": ADMIN_ID,
            "requested_by_name": ADMIN,
            "workflow_instance_id": None,
            "notes": "Linked to management override follow-up.",
            "created_at": now,
            "updated_at": now,
        },
    )

    upsert_row(
        cur,
        "audit_evidence_request_items",
        {"request_id": evidence_request_id, "item_description": "Support for journal JE-9003 posted after close review"},
        {
            "expected_document_type": "Journal Support",
            "is_required": True,
            "fulfilled_document_id": document_2,
            "submitted_at": now - timedelta(hours=5),
            "reviewer_notes": "Support received but escalation evidence still outstanding.",
            "reviewed_by_user_id": ADMIN_ID,
            "reviewed_at": now - timedelta(hours=4),
            "is_accepted": False,
            "created_at": now,
        },
    )

    upsert_row(
        cur,
        "audit_evidence_request_items",
        {"request_id": evidence_request_id, "item_description": "Weekend journal approval evidence"},
        {
            "expected_document_type": "Approval Memo",
            "is_required": True,
            "fulfilled_document_id": None,
            "submitted_at": None,
            "reviewer_notes": None,
            "reviewed_by_user_id": None,
            "reviewed_at": None,
            "is_accepted": None,
            "created_at": now,
        },
    )

    workflow_finding = f"demo-ext-find-{reference_id}"
    workflow_response = f"demo-ext-mgmt-{reference_id}"
    workflow_signoff = f"demo-ext-signoff-{reference_id}"

    upsert_row(
        cur,
        "audit_workflow_instances",
        {"workflow_instance_id": workflow_finding},
        {
            "reference_id": reference_id,
            "entity_type": "Finding",
            "entity_id": reference_id,
            "workflow_definition_id": "Audit.Reporting.FindingApproval.v1",
            "workflow_display_name": "Finding Review",
            "status": "Running",
            "current_activity_id": "review-finding",
            "current_activity_name": "Finding review pending",
            "started_by_user_id": ADMIN_ID,
            "started_by_name": ADMIN,
            "started_at": now - timedelta(hours=18),
            "last_synced_at": now - timedelta(hours=3),
            "completed_at": None,
            "is_active": True,
            "metadata_json": Json({"demo": True, "severity": "High"}),
        },
    )

    upsert_row(
        cur,
        "audit_workflow_instances",
        {"workflow_instance_id": workflow_response},
        {
            "reference_id": reference_id,
            "entity_type": "ManagementResponse",
            "entity_id": reference_id,
            "workflow_definition_id": "Audit.Reporting.ManagementResponse.v1",
            "workflow_display_name": "Management Response Approval",
            "status": "Running",
            "current_activity_id": "awaiting-response",
            "current_activity_name": "Management response overdue",
            "started_by_user_id": ADMIN_ID,
            "started_by_name": ADMIN,
            "started_at": now - timedelta(days=2),
            "last_synced_at": now - timedelta(hours=1),
            "completed_at": None,
            "is_active": True,
            "metadata_json": Json({"demo": True, "overdue": True}),
        },
    )

    upsert_row(
        cur,
        "audit_workflow_instances",
        {"workflow_instance_id": workflow_signoff},
        {
            "reference_id": reference_id,
            "entity_type": "Reporting",
            "entity_id": reference_id,
            "workflow_definition_id": "Audit.Reporting.FinalSignOff.v1",
            "workflow_display_name": "Final Sign-Off",
            "status": "Running",
            "current_activity_id": "final-signoff",
            "current_activity_name": "Awaiting final sign-off",
            "started_by_user_id": ADMIN_ID,
            "started_by_name": ADMIN,
            "started_at": now - timedelta(hours=14),
            "last_synced_at": now - timedelta(hours=2),
            "completed_at": None,
            "is_active": True,
            "metadata_json": Json({"demo": True}),
        },
    )

    upsert_row(
        cur,
        "audit_workflow_tasks",
        {"workflow_instance_id": workflow_finding, "task_title": "Finding review for late manual journals posted after close"},
        {
            "reference_id": reference_id,
            "entity_type": "Finding",
            "entity_id": reference_id,
            "task_description": "Review the high-severity finding and confirm rating and wording.",
            "assignee_user_id": PARTNER_ID,
            "assignee_name": PARTNER,
            "status": "Pending",
            "priority": "High",
            "due_date": now + timedelta(days=2),
            "action_url": f"/assessments/{reference_id}?tab=findings",
            "created_at": now - timedelta(hours=18),
            "completed_at": None,
            "completed_by_user_id": None,
            "completion_notes": None,
            "external_task_id": None,
            "external_task_source": None,
        },
    )

    upsert_row(
        cur,
        "audit_workflow_tasks",
        {"workflow_instance_id": workflow_response, "task_title": "Management response overdue for manual journal finding"},
        {
            "reference_id": reference_id,
            "entity_type": "ManagementResponse",
            "entity_id": reference_id,
            "task_description": "Overdue action. Follow up management response and evidence for EXT-F-001.",
            "assignee_user_id": MANAGER_ID,
            "assignee_name": MANAGER,
            "status": "Pending",
            "priority": "Critical",
            "due_date": now - timedelta(days=1),
            "action_url": f"/assessments/{reference_id}?tab=findings",
            "created_at": now - timedelta(days=2),
            "completed_at": None,
            "completed_by_user_id": None,
            "completion_notes": None,
            "external_task_id": None,
            "external_task_source": None,
        },
    )

    upsert_row(
        cur,
        "audit_workflow_tasks",
        {"workflow_instance_id": workflow_signoff, "task_title": "Final sign-off for Demo External Audit - Revenue and Receivables"},
        {
            "reference_id": reference_id,
            "entity_type": "Reporting",
            "entity_id": reference_id,
            "task_description": "Complete partner sign-off for the external audit report pack.",
            "assignee_user_id": PARTNER_ID,
            "assignee_name": PARTNER,
            "status": "Pending",
            "priority": "High",
            "due_date": now + timedelta(days=4),
            "action_url": f"/assessments/{reference_id}?tab=reporting",
            "created_at": now - timedelta(hours=14),
            "completed_at": None,
            "completed_by_user_id": None,
            "completion_notes": None,
            "external_task_id": None,
            "external_task_source": None,
        },
    )

    upsert_row(
        cur,
        "audit_notifications",
        {"workflow_instance_id": workflow_finding, "title": "Action Required: Finding review pending", "recipient_name": PARTNER},
        {
            "reference_id": reference_id,
            "entity_type": "Finding",
            "entity_id": reference_id,
            "notification_type": "WorkflowTask",
            "severity": "Warning",
            "message": "Action required. Review high-severity finding for manual journals posted after close.",
            "recipient_user_id": PARTNER_ID,
            "is_read": False,
            "read_at": None,
            "action_url": f"/assessments/{reference_id}?tab=findings",
            "created_at": now - timedelta(hours=17),
        },
    )

    upsert_row(
        cur,
        "audit_notifications",
        {"workflow_instance_id": workflow_response, "title": "Escalation: Management response overdue", "recipient_name": MANAGER},
        {
            "reference_id": reference_id,
            "entity_type": "ManagementResponse",
            "entity_id": reference_id,
            "notification_type": "Escalation",
            "severity": "Critical",
            "message": "Escalation. Management response for the manual journal finding is overdue.",
            "recipient_user_id": MANAGER_ID,
            "is_read": False,
            "read_at": None,
            "action_url": f"/assessments/{reference_id}?tab=findings",
            "created_at": now - timedelta(hours=20),
        },
    )

    upsert_row(
        cur,
        "audit_notifications",
        {"workflow_instance_id": workflow_signoff, "title": "Action Required: Final sign-off pending", "recipient_name": PARTNER},
        {
            "reference_id": reference_id,
            "entity_type": "Reporting",
            "entity_id": reference_id,
            "notification_type": "WorkflowTask",
            "severity": "Warning",
            "message": "Action required. Final sign-off is pending for the external audit file.",
            "recipient_user_id": PARTNER_ID,
            "is_read": False,
            "read_at": None,
            "action_url": f"/assessments/{reference_id}?tab=reporting",
            "created_at": now - timedelta(hours=13),
        },
    )

    review_task_1 = upsert_row(
        cur,
        "audit_tasks",
        {"reference_id": reference_id, "title": "Review finding EXT-F-001"},
        {
            "entity_type": "Finding",
            "entity_id": reference_id,
            "workflow_instance_id": workflow_finding,
            "task_type": "Review",
            "description": "Generic review task for finding wording and severity.",
            "assigned_to_user_id": PARTNER_ID,
            "assigned_to_name": PARTNER,
            "assigned_by_user_id": ADMIN_ID,
            "assigned_by_name": ADMIN,
            "status": "Open",
            "priority": "High",
            "due_date": now + timedelta(days=2),
            "completed_at": None,
            "completed_by_user_id": None,
            "completion_notes": None,
            "source": "Workflow",
            "created_at": now - timedelta(hours=18),
            "updated_at": now - timedelta(hours=18),
        },
    )

    review_task_2 = upsert_row(
        cur,
        "audit_tasks",
        {"reference_id": reference_id, "title": "Approve management response for EXT-F-001"},
        {
            "entity_type": "ManagementResponse",
            "entity_id": reference_id,
            "workflow_instance_id": workflow_response,
            "task_type": "Approval",
            "description": "Approve or escalate management response for overdue journal finding.",
            "assigned_to_user_id": MANAGER_ID,
            "assigned_to_name": MANAGER,
            "assigned_by_user_id": ADMIN_ID,
            "assigned_by_name": ADMIN,
            "status": "Open",
            "priority": "Critical",
            "due_date": now - timedelta(days=1),
            "completed_at": None,
            "completed_by_user_id": None,
            "completion_notes": None,
            "source": "Workflow",
            "created_at": now - timedelta(days=2),
            "updated_at": now - timedelta(days=2),
        },
    )

    review_task_3 = upsert_row(
        cur,
        "audit_tasks",
        {"reference_id": reference_id, "title": "Final sign-off for Demo External Audit - Revenue and Receivables"},
        {
            "entity_type": "Reporting",
            "entity_id": reference_id,
            "workflow_instance_id": workflow_signoff,
            "task_type": "Sign-Off",
            "description": "Generic final sign-off task for review workspace.",
            "assigned_to_user_id": PARTNER_ID,
            "assigned_to_name": PARTNER,
            "assigned_by_user_id": ADMIN_ID,
            "assigned_by_name": ADMIN,
            "status": "Open",
            "priority": "High",
            "due_date": now + timedelta(days=4),
            "completed_at": None,
            "completed_by_user_id": None,
            "completion_notes": None,
            "source": "Workflow",
            "created_at": now - timedelta(hours=14),
            "updated_at": now - timedelta(hours=14),
        },
    )

    review_1 = upsert_row(
        cur,
        "audit_reviews",
        {"reference_id": reference_id, "review_type": "Finding Review", "summary": "Review high-severity external finding for manual journals"},
        {
            "entity_type": "Finding",
            "entity_id": reference_id,
            "status": "Pending",
            "task_id": review_task_1,
            "workflow_instance_id": workflow_finding,
            "assigned_reviewer_user_id": PARTNER_ID,
            "assigned_reviewer_name": PARTNER,
            "requested_by_user_id": ADMIN_ID,
            "requested_by_name": ADMIN,
            "requested_at": now - timedelta(hours=18),
            "due_date": now + timedelta(days=2),
            "completed_at": None,
            "completed_by_user_id": None,
            "created_at": now - timedelta(hours=18),
            "updated_at": now - timedelta(hours=18),
        },
    )

    review_2 = upsert_row(
        cur,
        "audit_reviews",
        {"reference_id": reference_id, "review_type": "Management Response Approval", "summary": "Approve overdue management response and evidence submission"},
        {
            "entity_type": "ManagementResponse",
            "entity_id": reference_id,
            "status": "Pending",
            "task_id": review_task_2,
            "workflow_instance_id": workflow_response,
            "assigned_reviewer_user_id": MANAGER_ID,
            "assigned_reviewer_name": MANAGER,
            "requested_by_user_id": ADMIN_ID,
            "requested_by_name": ADMIN,
            "requested_at": now - timedelta(days=2),
            "due_date": now - timedelta(days=1),
            "completed_at": None,
            "completed_by_user_id": None,
            "created_at": now - timedelta(days=2),
            "updated_at": now - timedelta(days=2),
        },
    )

    review_3 = upsert_row(
        cur,
        "audit_reviews",
        {"reference_id": reference_id, "review_type": "Final Sign-Off", "summary": "Partner sign-off pending for external report pack"},
        {
            "entity_type": "Reporting",
            "entity_id": reference_id,
            "status": "Pending",
            "task_id": review_task_3,
            "workflow_instance_id": workflow_signoff,
            "assigned_reviewer_user_id": PARTNER_ID,
            "assigned_reviewer_name": PARTNER,
            "requested_by_user_id": ADMIN_ID,
            "requested_by_name": ADMIN,
            "requested_at": now - timedelta(hours=14),
            "due_date": now + timedelta(days=4),
            "completed_at": None,
            "completed_by_user_id": None,
            "created_at": now - timedelta(hours=14),
            "updated_at": now - timedelta(hours=14),
        },
    )

    upsert_row(
        cur,
        "audit_review_notes",
        {"review_id": review_1, "note_text": "Reviewer note: confirm whether the two post-close journals affected revenue cut-off."},
        {
            "working_paper_section_id": None,
            "note_type": "Review Note",
            "severity": "High",
            "status": "Open",
            "response_text": "Linked analytics and journal support uploaded.",
            "raised_by_user_id": PARTNER_ID,
            "raised_by_name": PARTNER,
            "raised_at": now - timedelta(hours=12),
            "cleared_by_user_id": None,
            "cleared_by_name": None,
            "cleared_at": None,
        },
    )

    upsert_row(
        cur,
        "audit_signoffs",
        {
            "reference_id": reference_id,
            "review_id": review_3,
            "signoff_type": "Partner Sign-Off",
            "signoff_level": "Final",
        },
        {
            "entity_type": "Reporting",
            "entity_id": reference_id,
            "workflow_instance_id": workflow_signoff,
            "status": "Signed",
            "signed_by_user_id": PARTNER_ID,
            "signed_by_name": PARTNER,
            "signed_at": now - timedelta(days=5),
            "comment": "Historical external sign-off retained for demo history",
        },
    )

    batch_1 = upsert_row(
        cur,
        "audit_analytics_import_batches",
        {"reference_id": reference_id, "dataset_type": "journal_entries", "batch_name": "DEMO-EXT-JOURNALS"},
        {
            "source_system": "ERP CSV Import",
            "source_file_name": "demo-ext-journals.csv",
            "row_count": 4,
            "imported_by_user_id": ADMIN_ID,
            "imported_by_name": ADMIN,
            "imported_at": now,
            "notes": "Demo journal dataset for analytical suite",
        },
    )

    reset_batch_rows(
        cur,
        "audit_gl_journal_entries",
        batch_1,
        [
            {"import_batch_id": batch_1, "reference_id": reference_id, "company_code": "AUR", "fiscal_year": 2026, "fiscal_period": 12, "posting_date": today - timedelta(days=1), "document_date": today - timedelta(days=2), "journal_number": "JE-9001", "line_number": 1, "account_number": "400100", "account_name": "Revenue", "fsli": "Revenue", "business_unit": "Sales", "cost_center": "SALES-01", "user_id": "fin.ctrl", "user_name": "Financial Controller", "description": "Post-close revenue adjustment", "amount": 185000, "debit_amount": 0, "credit_amount": 185000, "currency_code": "ZAR", "source_system": "ERP", "source_document_number": "JV-9001", "is_manual": True, "is_period_end": True, "created_at": now},
            {"import_batch_id": batch_1, "reference_id": reference_id, "company_code": "AUR", "fiscal_year": 2026, "fiscal_period": 12, "posting_date": today - timedelta(days=1), "document_date": today - timedelta(days=2), "journal_number": "JE-9001", "line_number": 2, "account_number": "110200", "account_name": "Trade Receivables", "fsli": "Trade Receivables", "business_unit": "Sales", "cost_center": "SALES-01", "user_id": "fin.ctrl", "user_name": "Financial Controller", "description": "Post-close revenue adjustment offset", "amount": -185000, "debit_amount": 185000, "credit_amount": 0, "currency_code": "ZAR", "source_system": "ERP", "source_document_number": "JV-9001", "is_manual": True, "is_period_end": True, "created_at": now},
            {"import_batch_id": batch_1, "reference_id": reference_id, "company_code": "AUR", "fiscal_year": 2026, "fiscal_period": 12, "posting_date": today - timedelta(days=2), "document_date": today - timedelta(days=2), "journal_number": "JE-9003", "line_number": 1, "account_number": "610000", "account_name": "Sales Returns", "fsli": "Revenue", "business_unit": "Sales", "cost_center": "SALES-02", "user_id": "weekend.user", "user_name": "Weekend Processor", "description": "Weekend manual sales return", "amount": 92000, "debit_amount": 92000, "credit_amount": 0, "currency_code": "ZAR", "source_system": "ERP", "source_document_number": "JV-9003", "is_manual": True, "is_period_end": True, "created_at": now},
            {"import_batch_id": batch_1, "reference_id": reference_id, "company_code": "AUR", "fiscal_year": 2026, "fiscal_period": 12, "posting_date": today - timedelta(days=8), "document_date": today - timedelta(days=8), "journal_number": "JE-8841", "line_number": 1, "account_number": "400100", "account_name": "Revenue", "fsli": "Revenue", "business_unit": "Sales", "cost_center": "SALES-03", "user_id": "sales.ops", "user_name": "Sales Ops Analyst", "description": "Manual reclass journal", "amount": 45000, "debit_amount": 0, "credit_amount": 45000, "currency_code": "ZAR", "source_system": "ERP", "source_document_number": "JV-8841", "is_manual": True, "is_period_end": False, "created_at": now},
        ],
    )

    batch_2 = upsert_row(
        cur,
        "audit_analytics_import_batches",
        {"reference_id": reference_id, "dataset_type": "trial_balance", "batch_name": "DEMO-EXT-TB"},
        {
            "source_system": "ERP CSV Import",
            "source_file_name": "demo-ext-tb.csv",
            "row_count": 3,
            "imported_by_user_id": ADMIN_ID,
            "imported_by_name": ADMIN,
            "imported_at": now,
            "notes": "Demo trial balance dataset",
        },
    )

    reset_batch_rows(
        cur,
        "audit_trial_balance_snapshots",
        batch_2,
        [
            {"import_batch_id": batch_2, "reference_id": reference_id, "fiscal_year": 2026, "period_label": "FY2026-P12", "as_of_date": today, "account_number": "400100", "account_name": "Revenue", "fsli": "Revenue", "business_unit": "Sales", "current_balance": 12850000, "currency_code": "ZAR", "created_at": now},
            {"import_batch_id": batch_2, "reference_id": reference_id, "fiscal_year": 2026, "period_label": "FY2026-P12", "as_of_date": today, "account_number": "110200", "account_name": "Trade Receivables", "fsli": "Trade Receivables", "business_unit": "Sales", "current_balance": 4120000, "currency_code": "ZAR", "created_at": now},
            {"import_batch_id": batch_2, "reference_id": reference_id, "fiscal_year": 2026, "period_label": "FY2026-P12", "as_of_date": today, "account_number": "610000", "account_name": "Sales Returns", "fsli": "Revenue", "business_unit": "Sales", "current_balance": -385000, "currency_code": "ZAR", "created_at": now},
        ],
    )

    batch_3 = upsert_row(
        cur,
        "audit_analytics_import_batches",
        {"reference_id": reference_id, "dataset_type": "industry_benchmarks", "batch_name": "DEMO-EXT-BENCH"},
        {
            "source_system": "Benchmark Import",
            "source_file_name": "demo-ext-bench.csv",
            "row_count": 3,
            "imported_by_user_id": ADMIN_ID,
            "imported_by_name": ADMIN,
            "imported_at": now,
            "notes": "Demo benchmark dataset",
        },
    )

    reset_batch_rows(
        cur,
        "audit_industry_benchmarks",
        batch_3,
        [
            {"import_batch_id": batch_3, "reference_id": reference_id, "fiscal_year": 2026, "industry_code": "MFG", "industry_name": "Manufacturing", "metric_name": "Gross Margin %", "unit_of_measure": "Percent", "company_value": 22.5, "benchmark_median": 27.0, "benchmark_lower_quartile": 23.5, "benchmark_upper_quartile": 30.1, "benchmark_source": "DemoSeed", "notes": "Below median", "created_at": now},
            {"import_batch_id": batch_3, "reference_id": reference_id, "fiscal_year": 2026, "industry_code": "MFG", "industry_name": "Manufacturing", "metric_name": "DSO", "unit_of_measure": "Days", "company_value": 64.0, "benchmark_median": 49.0, "benchmark_lower_quartile": 42.0, "benchmark_upper_quartile": 56.0, "benchmark_source": "DemoSeed", "notes": "Receivables collection slower than peers", "created_at": now},
            {"import_batch_id": batch_3, "reference_id": reference_id, "fiscal_year": 2026, "industry_code": "MFG", "industry_name": "Manufacturing", "metric_name": "Manual Journals % of Total", "unit_of_measure": "Percent", "company_value": 7.8, "benchmark_median": 2.4, "benchmark_lower_quartile": 1.8, "benchmark_upper_quartile": 3.1, "benchmark_source": "DemoSeed", "notes": "Higher than expected manual processing", "created_at": now},
        ],
    )

    batch_4 = upsert_row(
        cur,
        "audit_analytics_import_batches",
        {"reference_id": reference_id, "dataset_type": "reasonability_forecasts", "batch_name": "DEMO-EXT-FORECAST"},
        {
            "source_system": "Forecast Import",
            "source_file_name": "demo-ext-forecast.csv",
            "row_count": 3,
            "imported_by_user_id": ADMIN_ID,
            "imported_by_name": ADMIN,
            "imported_at": now,
            "notes": "Demo reasonability dataset",
        },
    )

    reset_batch_rows(
        cur,
        "audit_reasonability_forecasts",
        batch_4,
        [
            {"import_batch_id": batch_4, "reference_id": reference_id, "fiscal_year": 2026, "fiscal_period": 12, "metric_name": "Revenue", "metric_category": "P&L", "forecast_basis": "Prior year plus approved price uplift", "actual_value": 12850000, "expected_value": 12100000, "budget_value": 12250000, "prior_year_value": 11750000, "threshold_amount": 350000, "threshold_percent": 3.0, "explanation": "Actual exceeds expected due to late manual adjustments flagged for review.", "created_at": now},
            {"import_batch_id": batch_4, "reference_id": reference_id, "fiscal_year": 2026, "fiscal_period": 12, "metric_name": "Trade Receivables", "metric_category": "Balance Sheet", "forecast_basis": "Revenue growth and historic collection curve", "actual_value": 4120000, "expected_value": 3680000, "budget_value": 3725000, "prior_year_value": 3440000, "threshold_amount": 200000, "threshold_percent": 4.0, "explanation": "Receivables growth exceeds expectation and aligns with DSO benchmark outlier.", "created_at": now},
            {"import_batch_id": batch_4, "reference_id": reference_id, "fiscal_year": 2026, "fiscal_period": 12, "metric_name": "Sales Returns", "metric_category": "P&L", "forecast_basis": "Returns ratio forecast", "actual_value": -385000, "expected_value": -240000, "budget_value": -250000, "prior_year_value": -210000, "threshold_amount": 50000, "threshold_percent": 5.0, "explanation": "Returns exceed expected threshold and warrant cut-off review.", "created_at": now},
        ],
    )

    trail_event_1 = upsert_row(
        cur,
        "audit_trail_events",
        {"reference_id": reference_id, "action": "MaterialitySet", "summary": "External audit materiality established"},
        {
            "entity_type": "Planning",
            "entity_id": reference_id,
            "category": "Planning",
            "performed_by_user_id": ADMIN_ID,
            "performed_by_name": ADMIN,
            "icon": "calculate",
            "color": "purple",
            "workflow_instance_id": None,
            "correlation_id": f"demo-ext-mat-{reference_id}",
            "source": "DemoSeed",
            "details_json": Json({"overallMateriality": 350000, "performanceMateriality": 262500}),
            "event_time": now - timedelta(days=9),
        },
    )

    upsert_row(
        cur,
        "audit_trail_entity_changes",
        {"audit_trail_event_id": trail_event_1, "field_name": "overall_materiality"},
        {"old_value": "", "new_value": "350000"},
    )

    upsert_row(
        cur,
        "audit_trail_entity_changes",
        {"audit_trail_event_id": trail_event_1, "field_name": "performance_materiality"},
        {"old_value": "", "new_value": "262500"},
    )

    upsert_row(
        cur,
        "audit_trail_events",
        {"reference_id": reference_id, "action": "AnalyticsImported", "summary": "External audit analytics imported for journals and trial balance"},
        {
            "entity_type": "Analytics",
            "entity_id": reference_id,
            "category": "Analytics",
            "performed_by_user_id": ADMIN_ID,
            "performed_by_name": ADMIN,
            "icon": "analytics",
            "color": "green",
            "workflow_instance_id": None,
            "correlation_id": f"demo-ext-ana-{reference_id}",
            "source": "DemoSeed",
            "details_json": Json({"journalRows": 4, "tbRows": 3, "benchmarkMetrics": 3, "forecastMetrics": 3}),
            "event_time": now - timedelta(hours=3),
        },
    )

    update_row(
        cur,
        "audit_engagement_plans",
        plan_id,
        {"scope_letter_document_id": document_1, "updated_at": now},
    )

    return reference_id


def main():
    now = datetime.utcnow().replace(microsecond=0)
    with psycopg2.connect(load_dsn()) as conn:
        with conn.cursor() as cur:
            cur.execute(f"SET search_path TO {SCHEMA}")
            for table, column in [
                ("projects", "id"),
                ("riskassessmentreference", "reference_id"),
                ("riskassessment", "riskassessment_refid"),
                ("audit_engagement_plans", "id"),
                ("audit_scope_items", "id"),
                ("audit_risk_control_matrix", "id"),
                ("audit_walkthroughs", "id"),
                ("audit_findings", "id"),
                ("audit_recommendations", "id"),
                ("audit_procedures", "id"),
                ("audit_working_papers", "id"),
                ("audit_working_paper_signoffs", "id"),
                ("audit_documents", "id"),
                ("audit_evidence_requests", "id"),
                ("audit_evidence_request_items", "id"),
                ("audit_workflow_instances", "id"),
                ("audit_workflow_tasks", "id"),
                ("audit_notifications", "id"),
                ("audit_tasks", "id"),
                ("audit_reviews", "id"),
                ("audit_review_notes", "id"),
                ("audit_signoffs", "id"),
                ("audit_management_actions", "id"),
                ("audit_analytics_import_batches", "id"),
                ("audit_gl_journal_entries", "id"),
                ("audit_trial_balance_snapshots", "id"),
                ("audit_industry_benchmarks", "id"),
                ("audit_reasonability_forecasts", "id"),
                ("audit_trail_events", "id"),
                ("audit_trail_entity_changes", "id"),
            ]:
                sync_sequence(cur, table, column)
            internal_reference_id = seed_internal(cur, now)
            external_reference_id = seed_external(cur, now)
        conn.commit()

    print(
        json.dumps(
            {
                "internal_reference_id": internal_reference_id,
                "external_reference_id": external_reference_id,
                "seeded_at": now.isoformat(),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
