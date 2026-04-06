using Affine.Engine.Model.Auditing.AuditUniverse;
using Dapper;
using Npgsql;
using System;
using System.Collections.Generic;
using System.Data;
using System.Linq;
using System.Threading.Tasks;

namespace Affine.Engine.Repository.Auditing
{
    public class AuditReviewsRepository : IAuditReviewsRepository
    {
        private readonly string _connectionString;

        private const string ReviewSelect = @"
            SELECT
                r.id AS Id,
                r.reference_id AS ReferenceId,
                r.entity_type AS EntityType,
                r.entity_id AS EntityId,
                r.review_type AS ReviewType,
                r.status AS Status,
                r.task_id AS TaskId,
                r.workflow_instance_id AS WorkflowInstanceId,
                r.assigned_reviewer_user_id AS AssignedReviewerUserId,
                r.assigned_reviewer_name AS AssignedReviewerName,
                r.requested_by_user_id AS RequestedByUserId,
                r.requested_by_name AS RequestedByName,
                r.requested_at AS RequestedAt,
                r.due_date AS DueDate,
                r.completed_at AS CompletedAt,
                r.completed_by_user_id AS CompletedByUserId,
                r.summary AS Summary,
                r.created_at AS CreatedAt,
                r.updated_at AS UpdatedAt,
                t.title AS TaskTitle,
                t.description AS TaskDescription,
                t.status AS TaskStatus,
                t.priority AS TaskPriority,
                wi.workflow_display_name AS WorkflowDisplayName,
                (
                    SELECT COUNT(*)
                    FROM audit_review_notes rn
                    WHERE rn.review_id = r.id
                      AND COALESCE(rn.status, 'Open') <> 'Closed'
                ) AS OpenNoteCount,
                (
                    SELECT COUNT(*)
                    FROM audit_review_notes rn
                    WHERE rn.review_id = r.id
                ) AS TotalNoteCount,
                (
                    SELECT COUNT(*)
                    FROM audit_signoffs s
                    WHERE s.review_id = r.id
                ) AS SignoffCount
            FROM audit_reviews r
            LEFT JOIN audit_tasks t ON r.task_id = t.id
            LEFT JOIN audit_workflow_instances wi ON r.workflow_instance_id = wi.workflow_instance_id";

        private const string TaskSelect = @"
            SELECT
                id AS Id,
                reference_id AS ReferenceId,
                entity_type AS EntityType,
                entity_id AS EntityId,
                workflow_instance_id AS WorkflowInstanceId,
                task_type AS TaskType,
                title AS Title,
                description AS Description,
                assigned_to_user_id AS AssignedToUserId,
                assigned_to_name AS AssignedToName,
                assigned_by_user_id AS AssignedByUserId,
                assigned_by_name AS AssignedByName,
                status AS Status,
                priority AS Priority,
                due_date AS DueDate,
                completed_at AS CompletedAt,
                completed_by_user_id AS CompletedByUserId,
                completion_notes AS CompletionNotes,
                source AS Source,
                created_at AS CreatedAt,
                updated_at AS UpdatedAt
            FROM audit_tasks";

        private const string ReviewNoteSelect = @"
            SELECT
                rn.id AS Id,
                rn.review_id AS ReviewId,
                rn.working_paper_section_id AS WorkingPaperSectionId,
                rn.note_type AS NoteType,
                rn.severity AS Severity,
                rn.status AS Status,
                rn.note_text AS NoteText,
                rn.response_text AS ResponseText,
                rn.raised_by_user_id AS RaisedByUserId,
                rn.raised_by_name AS RaisedByName,
                rn.raised_at AS RaisedAt,
                rn.cleared_by_user_id AS ClearedByUserId,
                rn.cleared_by_name AS ClearedByName,
                rn.cleared_at AS ClearedAt,
                r.reference_id AS ReferenceId,
                r.entity_type AS EntityType,
                r.entity_id AS EntityId,
                r.review_type AS ReviewType,
                r.assigned_reviewer_name AS AssignedReviewerName
            FROM audit_review_notes rn
            INNER JOIN audit_reviews r ON rn.review_id = r.id";

        private const string SignoffSelect = @"
            SELECT
                id AS Id,
                reference_id AS ReferenceId,
                entity_type AS EntityType,
                entity_id AS EntityId,
                review_id AS ReviewId,
                workflow_instance_id AS WorkflowInstanceId,
                signoff_type AS SignoffType,
                signoff_level AS SignoffLevel,
                status AS Status,
                signed_by_user_id AS SignedByUserId,
                signed_by_name AS SignedByName,
                signed_at AS SignedAt,
                comment AS Comment
            FROM audit_signoffs";

        public AuditReviewsRepository(string connectionString)
        {
            _connectionString = connectionString ?? throw new ArgumentNullException(nameof(connectionString));
        }

        public async Task<AuditReviewWorkspace> GetWorkspaceAsync(int? userId)
        {
            using IDbConnection db = new NpgsqlConnection(_connectionString);
            db.Open();

            var workspace = new AuditReviewWorkspace();

            var reviewQuery = $@"
                {ReviewSelect}
                WHERE (@UserId IS NULL OR r.assigned_reviewer_user_id = @UserId)
                ORDER BY
                    CASE
                        WHEN r.status IN ('Pending', 'Open', 'In Progress') THEN 0
                        ELSE 1
                    END,
                    COALESCE(r.due_date, r.requested_at, r.created_at) ASC,
                    r.id DESC";

            var taskQuery = $@"
                {TaskSelect}
                WHERE (@UserId IS NULL OR assigned_to_user_id = @UserId)
                ORDER BY
                    CASE
                        WHEN status IN ('Open', 'Pending', 'In Progress') THEN 0
                        ELSE 1
                    END,
                    COALESCE(due_date, created_at) ASC,
                    id DESC";

            var noteQuery = $@"
                {ReviewNoteSelect}
                WHERE (@UserId IS NULL OR r.assigned_reviewer_user_id = @UserId)
                ORDER BY rn.raised_at DESC
                LIMIT 100";

            var signoffQuery = $@"
                {SignoffSelect}
                WHERE (
                    @UserId IS NULL
                    OR signed_by_user_id = @UserId
                    OR review_id IN (
                        SELECT id FROM audit_reviews
                        WHERE assigned_reviewer_user_id = @UserId
                    )
                )
                ORDER BY signed_at DESC
                LIMIT 100";

            workspace.Reviews = (await db.QueryAsync<AuditReview>(reviewQuery, new { UserId = userId })).ToList();
            workspace.Tasks = (await db.QueryAsync<AuditTask>(taskQuery, new { UserId = userId })).ToList();
            workspace.ReviewNotes = (await db.QueryAsync<AuditReviewNote>(noteQuery, new { UserId = userId })).ToList();
            workspace.Signoffs = (await db.QueryAsync<AuditSignoff>(signoffQuery, new { UserId = userId })).ToList();
            return workspace;
        }

        public async Task<List<AuditReview>> GetReviewsByReferenceAsync(int referenceId)
        {
            using IDbConnection db = new NpgsqlConnection(_connectionString);
            db.Open();

            var query = $@"
                {ReviewSelect}
                WHERE r.reference_id = @ReferenceId
                ORDER BY COALESCE(r.due_date, r.requested_at, r.created_at) ASC, r.id DESC";

            return (await db.QueryAsync<AuditReview>(query, new { ReferenceId = referenceId })).ToList();
        }

        public async Task<List<AuditReviewNote>> GetReviewNotesAsync(int reviewId)
        {
            using IDbConnection db = new NpgsqlConnection(_connectionString);
            db.Open();

            var query = $@"
                {ReviewNoteSelect}
                WHERE rn.review_id = @ReviewId
                ORDER BY rn.raised_at DESC, rn.id DESC";

            return (await db.QueryAsync<AuditReviewNote>(query, new { ReviewId = reviewId })).ToList();
        }

        public async Task<List<AuditSignoff>> GetSignoffsByReferenceAsync(int referenceId, int limit = 100)
        {
            using IDbConnection db = new NpgsqlConnection(_connectionString);
            db.Open();

            var query = $@"
                {SignoffSelect}
                WHERE reference_id = @ReferenceId
                ORDER BY signed_at DESC
                LIMIT @Limit";

            return (await db.QueryAsync<AuditSignoff>(query, new { ReferenceId = referenceId, Limit = limit })).ToList();
        }

        public async Task<AuditTask> CreateTaskAsync(CreateAuditTaskRequest request)
        {
            using IDbConnection db = new NpgsqlConnection(_connectionString);
            db.Open();

            var insertQuery = @"
                INSERT INTO audit_tasks
                (
                    reference_id,
                    entity_type,
                    entity_id,
                    workflow_instance_id,
                    task_type,
                    title,
                    description,
                    assigned_to_user_id,
                    assigned_to_name,
                    assigned_by_user_id,
                    assigned_by_name,
                    status,
                    priority,
                    due_date,
                    source
                )
                VALUES
                (
                    @ReferenceId,
                    @EntityType,
                    @EntityId,
                    @WorkflowInstanceId,
                    @TaskType,
                    @Title,
                    @Description,
                    @AssignedToUserId,
                    @AssignedToName,
                    @AssignedByUserId,
                    @AssignedByName,
                    COALESCE(@Status, 'Open'),
                    COALESCE(@Priority, 'Medium'),
                    @DueDate,
                    COALESCE(@Source, 'Manual')
                )
                RETURNING id";

            var newId = await db.ExecuteScalarAsync<int>(insertQuery, request);
            var fetchQuery = $"{TaskSelect} WHERE id = @Id";
            return await db.QueryFirstAsync<AuditTask>(fetchQuery, new { Id = newId });
        }

        public async Task<int> CompleteOpenTasksByWorkflowInstanceAsync(CompleteAuditTaskRequest request)
        {
            using IDbConnection db = new NpgsqlConnection(_connectionString);
            db.Open();

            var query = @"
                UPDATE audit_tasks
                SET
                    status = 'Completed',
                    completed_at = CURRENT_TIMESTAMP,
                    completed_by_user_id = @CompletedByUserId,
                    completion_notes = @CompletionNotes
                WHERE workflow_instance_id = @WorkflowInstanceId
                  AND status IN ('Open', 'Pending', 'In Progress')";

            return await db.ExecuteAsync(query, request);
        }

        public async Task<AuditReview> CreateReviewAsync(CreateAuditReviewRequest request)
        {
            using IDbConnection db = new NpgsqlConnection(_connectionString);
            db.Open();

            var existing = await GetReviewByWorkflowInstanceAsync(request.WorkflowInstanceId);
            if (existing != null)
            {
                return existing;
            }

            var insertQuery = @"
                INSERT INTO audit_reviews
                (
                    reference_id,
                    entity_type,
                    entity_id,
                    review_type,
                    status,
                    task_id,
                    workflow_instance_id,
                    assigned_reviewer_user_id,
                    assigned_reviewer_name,
                    requested_by_user_id,
                    requested_by_name,
                    due_date,
                    summary
                )
                VALUES
                (
                    @ReferenceId,
                    @EntityType,
                    @EntityId,
                    @ReviewType,
                    COALESCE(@Status, 'Pending'),
                    @TaskId,
                    @WorkflowInstanceId,
                    @AssignedReviewerUserId,
                    @AssignedReviewerName,
                    @RequestedByUserId,
                    @RequestedByName,
                    @DueDate,
                    @Summary
                )
                RETURNING id";

            var newId = await db.ExecuteScalarAsync<int>(insertQuery, request);
            var fetchQuery = $"{ReviewSelect} WHERE r.id = @Id";
            return await db.QueryFirstAsync<AuditReview>(fetchQuery, new { Id = newId });
        }

        public async Task<AuditReview?> GetReviewByWorkflowInstanceAsync(string workflowInstanceId)
        {
            if (string.IsNullOrWhiteSpace(workflowInstanceId))
            {
                return null;
            }

            using IDbConnection db = new NpgsqlConnection(_connectionString);
            db.Open();

            var query = $"{ReviewSelect} WHERE r.workflow_instance_id = @WorkflowInstanceId ORDER BY r.id DESC LIMIT 1";
            return await db.QueryFirstOrDefaultAsync<AuditReview>(query, new { WorkflowInstanceId = workflowInstanceId });
        }

        public async Task<AuditReview?> CompleteReviewByWorkflowInstanceAsync(CompleteAuditReviewRequest request)
        {
            if (string.IsNullOrWhiteSpace(request.WorkflowInstanceId))
            {
                return null;
            }

            using IDbConnection db = new NpgsqlConnection(_connectionString);
            db.Open();

            var query = @"
                UPDATE audit_reviews
                SET
                    status = COALESCE(@Status, 'Completed'),
                    completed_at = CURRENT_TIMESTAMP,
                    completed_by_user_id = @CompletedByUserId,
                    summary = COALESCE(@Summary, summary)
                WHERE workflow_instance_id = @WorkflowInstanceId
                  AND status IN ('Pending', 'Open', 'In Progress', 'Awaiting Approval', 'Awaiting Review')";

            await db.ExecuteAsync(query, request);

            var fetchQuery = $"{ReviewSelect} WHERE r.workflow_instance_id = @WorkflowInstanceId ORDER BY r.id DESC LIMIT 1";
            return await db.QueryFirstOrDefaultAsync<AuditReview>(fetchQuery, new { request.WorkflowInstanceId });
        }

        public async Task<AuditReviewNote> AddReviewNoteAsync(CreateAuditReviewNoteRequest request)
        {
            using IDbConnection db = new NpgsqlConnection(_connectionString);
            db.Open();

            var insertQuery = @"
                INSERT INTO audit_review_notes
                (
                    review_id,
                    working_paper_section_id,
                    note_type,
                    severity,
                    status,
                    note_text,
                    response_text,
                    raised_by_user_id,
                    raised_by_name
                )
                VALUES
                (
                    @ReviewId,
                    @WorkingPaperSectionId,
                    COALESCE(@NoteType, 'Review Note'),
                    COALESCE(@Severity, 'Medium'),
                    COALESCE(@Status, 'Open'),
                    @NoteText,
                    @ResponseText,
                    @RaisedByUserId,
                    @RaisedByName
                )
                RETURNING id";

            var newId = await db.ExecuteScalarAsync<int>(insertQuery, request);
            var fetchQuery = $"{ReviewNoteSelect} WHERE rn.id = @Id";
            return await db.QueryFirstAsync<AuditReviewNote>(fetchQuery, new { Id = newId });
        }

        public async Task<AuditSignoff> AddSignoffAsync(CreateAuditSignoffRequest request)
        {
            using IDbConnection db = new NpgsqlConnection(_connectionString);
            db.Open();

            var insertQuery = @"
                INSERT INTO audit_signoffs
                (
                    reference_id,
                    entity_type,
                    entity_id,
                    review_id,
                    workflow_instance_id,
                    signoff_type,
                    signoff_level,
                    status,
                    signed_by_user_id,
                    signed_by_name,
                    comment
                )
                VALUES
                (
                    @ReferenceId,
                    @EntityType,
                    @EntityId,
                    @ReviewId,
                    @WorkflowInstanceId,
                    @SignoffType,
                    @SignoffLevel,
                    COALESCE(@Status, 'Signed'),
                    @SignedByUserId,
                    @SignedByName,
                    @Comment
                )
                RETURNING id";

            var newId = await db.ExecuteScalarAsync<int>(insertQuery, request);
            var fetchQuery = $"{SignoffSelect} WHERE id = @Id";
            return await db.QueryFirstAsync<AuditSignoff>(fetchQuery, new { Id = newId });
        }
    }
}
