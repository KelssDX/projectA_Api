using Affine.Engine.Model.Auditing.AuditUniverse;
using Dapper;
using Npgsql;
using System;
using System.Collections.Generic;
using System.Data;
using System.Threading.Tasks;

namespace Affine.Engine.Repository.Auditing
{
    public class AuditWorkflowRepository : IAuditWorkflowRepository
    {
        private readonly string _connectionString;

        private const string WorkflowSelect = @"
            SELECT
                w.id AS Id,
                w.reference_id AS ReferenceId,
                w.entity_type AS EntityType,
                w.entity_id AS EntityId,
                w.workflow_definition_id AS WorkflowDefinitionId,
                w.workflow_display_name AS WorkflowDisplayName,
                w.workflow_instance_id AS WorkflowInstanceId,
                w.status AS Status,
                w.current_activity_id AS CurrentActivityId,
                w.current_activity_name AS CurrentActivityName,
                w.started_by_user_id AS StartedByUserId,
                w.started_by_name AS StartedByName,
                w.started_at AS StartedAt,
                w.last_synced_at AS LastSyncedAt,
                w.completed_at AS CompletedAt,
                w.is_active AS IsActive,
                w.metadata_json AS MetadataJson
            FROM audit_workflow_instances w";

        private const string TaskSelect = @"
            SELECT
                t.id AS Id,
                t.workflow_instance_id AS WorkflowInstanceId,
                t.external_task_id AS ExternalTaskId,
                t.external_task_source AS ExternalTaskSource,
                t.reference_id AS ReferenceId,
                t.entity_type AS EntityType,
                t.entity_id AS EntityId,
                wi.workflow_display_name AS WorkflowDisplayName,
                t.task_title AS TaskTitle,
                t.task_description AS TaskDescription,
                t.assignee_user_id AS AssigneeUserId,
                t.assignee_name AS AssigneeName,
                t.status AS Status,
                t.priority AS Priority,
                t.due_date AS DueDate,
                t.action_url AS ActionUrl,
                t.created_at AS CreatedAt,
                t.completed_at AS CompletedAt,
                t.completed_by_user_id AS CompletedByUserId,
                t.completion_notes AS CompletionNotes
            FROM audit_workflow_tasks t
            LEFT JOIN audit_workflow_instances wi ON wi.workflow_instance_id = t.workflow_instance_id";

        private const string NotificationSelect = @"
            SELECT
                n.id AS Id,
                n.reference_id AS ReferenceId,
                n.entity_type AS EntityType,
                n.entity_id AS EntityId,
                n.workflow_instance_id AS WorkflowInstanceId,
                wi.workflow_display_name AS WorkflowDisplayName,
                n.notification_type AS NotificationType,
                n.severity AS Severity,
                n.title AS Title,
                n.message AS Message,
                n.recipient_user_id AS RecipientUserId,
                n.recipient_name AS RecipientName,
                n.is_read AS IsRead,
                n.read_at AS ReadAt,
                n.action_url AS ActionUrl,
                n.created_at AS CreatedAt
            FROM audit_notifications n
            LEFT JOIN audit_workflow_instances wi ON wi.workflow_instance_id = n.workflow_instance_id";

        private const string EventSelect = @"
            SELECT
                e.id AS Id,
                e.workflow_instance_id AS WorkflowInstanceId,
                e.reference_id AS ReferenceId,
                e.entity_type AS EntityType,
                e.entity_id AS EntityId,
                wi.workflow_display_name AS WorkflowDisplayName,
                e.event_type AS EventType,
                e.title AS Title,
                e.description AS Description,
                e.actor_user_id AS ActorUserId,
                e.actor_name AS ActorName,
                e.event_time AS EventTime,
                e.metadata_json AS MetadataJson
            FROM audit_workflow_events e
            LEFT JOIN audit_workflow_instances wi ON wi.workflow_instance_id = e.workflow_instance_id";

        public AuditWorkflowRepository(string connectionString)
        {
            _connectionString = connectionString ?? throw new ArgumentNullException(nameof(connectionString));
        }

        public async Task<AuditWorkflowInstance> CreateWorkflowInstanceAsync(CreateAuditWorkflowInstanceRequest request)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();

                var query = @"
                    INSERT INTO audit_workflow_instances
                    (
                        reference_id,
                        entity_type,
                        entity_id,
                        workflow_definition_id,
                        workflow_display_name,
                        workflow_instance_id,
                        status,
                        current_activity_id,
                        current_activity_name,
                        started_by_user_id,
                        started_by_name,
                        last_synced_at,
                        completed_at,
                        is_active,
                        metadata_json
                    )
                    VALUES
                    (
                        @ReferenceId,
                        @EntityType,
                        @EntityId,
                        @WorkflowDefinitionId,
                        @WorkflowDisplayName,
                        @WorkflowInstanceId,
                        @Status,
                        @CurrentActivityId,
                        @CurrentActivityName,
                        @StartedByUserId,
                        @StartedByName,
                        CURRENT_TIMESTAMP,
                        NULL,
                        @IsActive,
                        @MetadataJson
                    )
                    ON CONFLICT (workflow_instance_id)
                    DO UPDATE SET
                        reference_id = EXCLUDED.reference_id,
                        entity_type = EXCLUDED.entity_type,
                        entity_id = EXCLUDED.entity_id,
                        workflow_definition_id = EXCLUDED.workflow_definition_id,
                        workflow_display_name = EXCLUDED.workflow_display_name,
                        status = EXCLUDED.status,
                        current_activity_id = EXCLUDED.current_activity_id,
                        current_activity_name = EXCLUDED.current_activity_name,
                        started_by_user_id = EXCLUDED.started_by_user_id,
                        started_by_name = EXCLUDED.started_by_name,
                        last_synced_at = CURRENT_TIMESTAMP,
                        completed_at = EXCLUDED.completed_at,
                        is_active = EXCLUDED.is_active,
                        metadata_json = EXCLUDED.metadata_json
                    RETURNING id";

                var id = await db.ExecuteScalarAsync<int>(query, request);
                return await db.QueryFirstOrDefaultAsync<AuditWorkflowInstance>(
                    $"{WorkflowSelect} WHERE w.id = @Id",
                    new { Id = id });
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in CreateWorkflowInstanceAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<AuditWorkflowInstance> GetWorkflowInstanceAsync(string workflowInstanceId)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();
                return await db.QueryFirstOrDefaultAsync<AuditWorkflowInstance>(
                    $"{WorkflowSelect} WHERE w.workflow_instance_id = @WorkflowInstanceId",
                    new { WorkflowInstanceId = workflowInstanceId });
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in GetWorkflowInstanceAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<AuditWorkflowInstance> UpdateWorkflowInstanceStatusAsync(UpdateAuditWorkflowInstanceStatusRequest request)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();

                var query = @"
                    UPDATE audit_workflow_instances
                    SET
                        status = @Status,
                        current_activity_id = @CurrentActivityId,
                        current_activity_name = @CurrentActivityName,
                        is_active = @IsActive,
                        completed_at = @CompletedAt,
                        last_synced_at = CURRENT_TIMESTAMP
                    WHERE workflow_instance_id = @WorkflowInstanceId
                    RETURNING id";

                var id = await db.ExecuteScalarAsync<int?>(query, request);
                if (!id.HasValue)
                {
                    return null;
                }

                return await db.QueryFirstOrDefaultAsync<AuditWorkflowInstance>(
                    $"{WorkflowSelect} WHERE w.id = @Id",
                    new { Id = id.Value });
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in UpdateWorkflowInstanceStatusAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<List<AuditWorkflowInstance>> GetWorkflowInstancesByReferenceAsync(int referenceId)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();
                var items = await db.QueryAsync<AuditWorkflowInstance>(
                    $"{WorkflowSelect} WHERE w.reference_id = @ReferenceId ORDER BY COALESCE(w.last_synced_at, w.started_at) DESC, w.id DESC",
                    new { ReferenceId = referenceId });
                return items.AsList();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in GetWorkflowInstancesByReferenceAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<List<AuditWorkflowInstance>> GetWorkflowInstancesAsync(bool activeOnly = false)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();
                var items = await db.QueryAsync<AuditWorkflowInstance>(
                    $"{WorkflowSelect} WHERE (@ActiveOnly = false OR w.is_active = true) ORDER BY COALESCE(w.last_synced_at, w.started_at) DESC, w.id DESC",
                    new { ActiveOnly = activeOnly });
                return items.AsList();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in GetWorkflowInstancesAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<AuditWorkflowTask> CreateWorkflowTaskAsync(CreateAuditWorkflowTaskRequest request)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();

                var query = @"
                    INSERT INTO audit_workflow_tasks
                    (
                        workflow_instance_id,
                        external_task_id,
                        external_task_source,
                        reference_id,
                        entity_type,
                        entity_id,
                        task_title,
                        task_description,
                        assignee_user_id,
                        assignee_name,
                        status,
                        priority,
                        due_date,
                        action_url
                    )
                    VALUES
                    (
                        @WorkflowInstanceId,
                        @ExternalTaskId,
                        @ExternalTaskSource,
                        @ReferenceId,
                        @EntityType,
                        @EntityId,
                        @TaskTitle,
                        @TaskDescription,
                        @AssigneeUserId,
                        @AssigneeName,
                        @Status,
                        @Priority,
                        @DueDate,
                        @ActionUrl
                    )
                    RETURNING id";

                var id = await db.ExecuteScalarAsync<int>(query, request);
                return await db.QueryFirstOrDefaultAsync<AuditWorkflowTask>(
                    $"{TaskSelect} WHERE t.id = @Id",
                    new { Id = id });
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in CreateWorkflowTaskAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<AuditWorkflowTask> CompleteWorkflowTaskAsync(CompleteAuditWorkflowTaskRequest request)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();

                var query = @"
                    UPDATE audit_workflow_tasks
                    SET
                        status = 'Completed',
                        completed_at = CURRENT_TIMESTAMP,
                        completed_by_user_id = @CompletedByUserId,
                        completion_notes = @CompletionNotes
                    WHERE id = @TaskId
                    RETURNING id";

                var id = await db.ExecuteScalarAsync<int?>(query, request);
                if (!id.HasValue)
                {
                    return null;
                }

                return await db.QueryFirstOrDefaultAsync<AuditWorkflowTask>(
                    $"{TaskSelect} WHERE t.id = @Id",
                    new { Id = id.Value });
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in CompleteWorkflowTaskAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<int> CompleteOpenTasksForWorkflowInstanceAsync(string workflowInstanceId, int? completedByUserId, string completionNotes)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();
                return await db.ExecuteAsync(@"
                    UPDATE audit_workflow_tasks
                    SET
                        status = 'Completed',
                        completed_at = CURRENT_TIMESTAMP,
                        completed_by_user_id = @CompletedByUserId,
                        completion_notes = COALESCE(@CompletionNotes, completion_notes)
                    WHERE workflow_instance_id = @WorkflowInstanceId
                        AND LOWER(COALESCE(status, 'pending')) NOT IN ('completed', 'closed', 'cancelled')",
                    new
                    {
                        WorkflowInstanceId = workflowInstanceId,
                        CompletedByUserId = completedByUserId,
                        CompletionNotes = completionNotes
                    });
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in CompleteOpenTasksForWorkflowInstanceAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<List<AuditWorkflowTask>> GetWorkflowTasksByUserAsync(int? userId, bool pendingOnly = false)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();
                var items = await db.QueryAsync<AuditWorkflowTask>(
                    $@"
                    {TaskSelect}
                    WHERE (@UserId IS NULL OR t.assignee_user_id = @UserId)
                        AND (@PendingOnly = false OR LOWER(COALESCE(t.status, 'pending')) NOT IN ('completed', 'closed', 'cancelled'))
                    ORDER BY
                        CASE WHEN t.due_date IS NULL THEN 1 ELSE 0 END,
                        t.due_date,
                        t.created_at DESC",
                    new { UserId = userId, PendingOnly = pendingOnly });
                return items.AsList();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in GetWorkflowTasksByUserAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<string> GetLatestExternalTaskIdAsync(string workflowInstanceId, string externalTaskSource = null)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();

                var query = @"
                    WITH candidates AS (
                        SELECT
                            COALESCE((""SerializedPayload""::jsonb ->> 'taskId'), ""Id"") AS external_task_id,
                            ""CreatedAt"" AS created_at,
                            ""ActivityTypeName"" AS activity_type_name
                        FROM ""Elsa"".""Bookmarks""
                        WHERE ""WorkflowInstanceId"" = @WorkflowInstanceId

                        UNION ALL

                        SELECT
                            COALESCE((""SerializedBookmarkPayload""::jsonb ->> 'taskId'), ""Id"") AS external_task_id,
                            ""CreatedAt"" AS created_at,
                            ""ActivityTypeName"" AS activity_type_name
                        FROM ""Elsa"".""WorkflowInboxMessages""
                        WHERE ""WorkflowInstanceId"" = @WorkflowInstanceId

                        UNION ALL

                        SELECT
                            COALESCE(""Payload"" ->> 'TaskId', ""Id"") AS external_task_id,
                            ""CreatedAt"" AS created_at,
                            ""ActivityTypeName"" AS activity_type_name
                        FROM ""Risk_Workflow"".""Elsa_Bookmarks""
                        WHERE ""WorkflowInstanceId"" = @WorkflowInstanceId

                        UNION ALL

                        SELECT
                            COALESCE(""Data"" ->> 'TaskId', ""Id"") AS external_task_id,
                            ""CreatedAt"" AS created_at,
                            ""ActivityTypeName"" AS activity_type_name
                        FROM ""Risk_Workflow"".""Elsa_WorkflowInboxMessages""
                        WHERE ""WorkflowInstanceId"" = @WorkflowInstanceId
                    )
                    SELECT external_task_id
                    FROM candidates
                    WHERE external_task_id IS NOT NULL
                        AND (@ExternalTaskSource IS NULL OR COALESCE(activity_type_name, '') ILIKE '%' || @ExternalTaskSource || '%')
                    ORDER BY created_at DESC
                    LIMIT 1";

                return await db.ExecuteScalarAsync<string>(query, new
                {
                    WorkflowInstanceId = workflowInstanceId,
                    ExternalTaskSource = externalTaskSource
                });
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in GetLatestExternalTaskIdAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<AuditNotification> CreateNotificationAsync(CreateAuditNotificationRequest request)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();

                var query = @"
                    INSERT INTO audit_notifications
                    (
                        reference_id,
                        entity_type,
                        entity_id,
                        workflow_instance_id,
                        notification_type,
                        severity,
                        title,
                        message,
                        recipient_user_id,
                        recipient_name,
                        action_url
                    )
                    VALUES
                    (
                        @ReferenceId,
                        @EntityType,
                        @EntityId,
                        @WorkflowInstanceId,
                        @NotificationType,
                        @Severity,
                        @Title,
                        @Message,
                        @RecipientUserId,
                        @RecipientName,
                        @ActionUrl
                    )
                    RETURNING id";

                var id = await db.ExecuteScalarAsync<int>(query, request);
                return await db.QueryFirstOrDefaultAsync<AuditNotification>(
                    $"{NotificationSelect} WHERE n.id = @Id",
                    new { Id = id });
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in CreateNotificationAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<bool> NotificationExistsAsync(string notificationType, string title, int? recipientUserId, string workflowInstanceId)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();
                var result = await db.ExecuteScalarAsync<int?>(@"
                    SELECT 1
                    FROM audit_notifications
                    WHERE notification_type = @NotificationType
                        AND title = @Title
                        AND COALESCE(recipient_user_id, -1) = COALESCE(@RecipientUserId, -1)
                        AND COALESCE(workflow_instance_id, '') = COALESCE(@WorkflowInstanceId, '')
                    LIMIT 1",
                    new
                    {
                        NotificationType = notificationType,
                        Title = title,
                        RecipientUserId = recipientUserId,
                        WorkflowInstanceId = workflowInstanceId
                    });
                return result.HasValue;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in NotificationExistsAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<List<AuditNotification>> GetNotificationsByUserAsync(int? userId, bool unreadOnly = false)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();
                var items = await db.QueryAsync<AuditNotification>(
                    $@"
                    {NotificationSelect}
                    WHERE (@UserId IS NULL OR n.recipient_user_id = @UserId)
                        AND (@UnreadOnly = false OR n.is_read = false)
                    ORDER BY n.created_at DESC",
                    new { UserId = userId, UnreadOnly = unreadOnly });
                return items.AsList();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in GetNotificationsByUserAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<bool> MarkNotificationReadAsync(MarkAuditNotificationReadRequest request)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();
                var affected = await db.ExecuteAsync(@"
                    UPDATE audit_notifications
                    SET
                        is_read = true,
                        read_at = CURRENT_TIMESTAMP
                    WHERE id = @NotificationId",
                    request);
                return affected > 0;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in MarkNotificationReadAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<AuditWorkflowEvent> CreateWorkflowEventAsync(CreateAuditWorkflowEventRequest request)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();

                var query = @"
                    INSERT INTO audit_workflow_events
                    (
                        workflow_instance_id,
                        reference_id,
                        entity_type,
                        entity_id,
                        event_type,
                        title,
                        description,
                        actor_user_id,
                        actor_name,
                        metadata_json
                    )
                    VALUES
                    (
                        @WorkflowInstanceId,
                        @ReferenceId,
                        @EntityType,
                        @EntityId,
                        @EventType,
                        @Title,
                        @Description,
                        @ActorUserId,
                        @ActorName,
                        @MetadataJson
                    )
                    RETURNING id";

                var id = await db.ExecuteScalarAsync<int>(query, request);
                return await db.QueryFirstOrDefaultAsync<AuditWorkflowEvent>(
                    $"{EventSelect} WHERE e.id = @Id",
                    new { Id = id });
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in CreateWorkflowEventAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<List<AuditWorkflowEvent>> GetWorkflowEventsByReferenceAsync(int referenceId, int limit = 100)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();
                var items = await db.QueryAsync<AuditWorkflowEvent>(
                    $"{EventSelect} WHERE e.reference_id = @ReferenceId ORDER BY e.event_time DESC, e.id DESC LIMIT @Limit",
                    new { ReferenceId = referenceId, Limit = limit <= 0 ? 100 : limit });
                return items.AsList();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in GetWorkflowEventsByReferenceAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<AuditWorkflowInbox> GetInboxAsync(int? userId)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();

                var workflows = await db.QueryAsync<AuditWorkflowInstance>(
                    $@"
                    {WorkflowSelect}
                    LEFT JOIN audit_workflow_tasks t ON t.workflow_instance_id = w.workflow_instance_id
                    LEFT JOIN audit_notifications n ON n.workflow_instance_id = w.workflow_instance_id
                    WHERE w.is_active = true
                        AND (@UserId IS NULL
                            OR w.started_by_user_id = @UserId
                            OR t.assignee_user_id = @UserId
                            OR n.recipient_user_id = @UserId)
                    GROUP BY
                        w.id,
                        w.reference_id,
                        w.entity_type,
                        w.entity_id,
                        w.workflow_definition_id,
                        w.workflow_display_name,
                        w.workflow_instance_id,
                        w.status,
                        w.current_activity_id,
                        w.current_activity_name,
                        w.started_by_user_id,
                        w.started_by_name,
                        w.started_at,
                        w.last_synced_at,
                        w.completed_at,
                        w.is_active,
                        w.metadata_json
                    ORDER BY COALESCE(w.last_synced_at, w.started_at) DESC, w.id DESC",
                    new { UserId = userId });

                var tasks = await GetWorkflowTasksByUserAsync(userId, pendingOnly: false);
                var notifications = await GetNotificationsByUserAsync(userId, unreadOnly: false);
                var events = new List<AuditWorkflowEvent>();
                if (workflows.AsList().Count > 0)
                {
                    var firstReferenceId = workflows.AsList()[0].ReferenceId;
                    if (firstReferenceId.HasValue)
                    {
                        events = await GetWorkflowEventsByReferenceAsync(firstReferenceId.Value, 30);
                    }
                }

                return new AuditWorkflowInbox
                {
                    Workflows = workflows.AsList(),
                    Tasks = tasks,
                    Notifications = notifications,
                    Events = events
                };
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in GetInboxAsync: {ex.Message}");
                throw;
            }
        }
    }
}
