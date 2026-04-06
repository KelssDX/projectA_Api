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
    public class AuditTrailRepository : IAuditTrailRepository
    {
        private readonly string _connectionString;

        public AuditTrailRepository(string connectionString)
        {
            _connectionString = connectionString ?? throw new ArgumentNullException(nameof(connectionString));
        }

        public async Task<AuditTrailEvent> CreateEventAsync(CreateAuditTrailEventRequest request)
        {
            if (request == null)
                throw new ArgumentNullException(nameof(request));

            using IDbConnection db = new NpgsqlConnection(_connectionString);
            db.Open();
            using var transaction = db.BeginTransaction();

            var eventId = await db.ExecuteScalarAsync<long>(@"
                INSERT INTO audit_trail_events (
                    reference_id,
                    entity_type,
                    entity_id,
                    category,
                    action,
                    summary,
                    performed_by_user_id,
                    performed_by_name,
                    icon,
                    color,
                    workflow_instance_id,
                    correlation_id,
                    source,
                    details_json
                )
                VALUES (
                    @ReferenceId,
                    @EntityType,
                    @EntityId,
                    @Category,
                    @Action,
                    @Summary,
                    @PerformedByUserId,
                    @PerformedByName,
                    @Icon,
                    @Color,
                    @WorkflowInstanceId,
                    @CorrelationId,
                    @Source,
                    CAST(@DetailsJson AS jsonb)
                )
                RETURNING id;",
                new
                {
                    request.ReferenceId,
                    request.EntityType,
                    request.EntityId,
                    request.Category,
                    request.Action,
                    request.Summary,
                    request.PerformedByUserId,
                    request.PerformedByName,
                    request.Icon,
                    request.Color,
                    request.WorkflowInstanceId,
                    request.CorrelationId,
                    request.Source,
                    DetailsJson = string.IsNullOrWhiteSpace(request.DetailsJson) ? null : request.DetailsJson
                },
                transaction);

            if (request.Changes != null && request.Changes.Any())
            {
                foreach (var change in request.Changes.Where(change => !string.IsNullOrWhiteSpace(change.FieldName)))
                {
                    await db.ExecuteAsync(@"
                        INSERT INTO audit_trail_entity_changes (
                            audit_trail_event_id,
                            field_name,
                            old_value,
                            new_value
                        )
                        VALUES (
                            @AuditTrailEventId,
                            @FieldName,
                            @OldValue,
                            @NewValue
                        );",
                        new
                        {
                            AuditTrailEventId = eventId,
                            change.FieldName,
                            change.OldValue,
                            change.NewValue
                        },
                        transaction);
                }
            }

            transaction.Commit();
            return await GetEventAsync(db, eventId);
        }

        public async Task<List<AuditTrailEvent>> GetEventsByReferenceAsync(int referenceId, int limit = 100)
        {
            using IDbConnection db = new NpgsqlConnection(_connectionString);
            db.Open();

            var events = (await db.QueryAsync<AuditTrailEvent>(@"
                SELECT
                    id,
                    reference_id AS ReferenceId,
                    entity_type AS EntityType,
                    entity_id AS EntityId,
                    category AS Category,
                    action AS Action,
                    summary AS Summary,
                    performed_by_user_id AS PerformedByUserId,
                    performed_by_name AS PerformedByName,
                    icon AS Icon,
                    color AS Color,
                    workflow_instance_id AS WorkflowInstanceId,
                    correlation_id AS CorrelationId,
                    source AS Source,
                    details_json::text AS DetailsJson,
                    event_time AS EventTime
                FROM audit_trail_events
                WHERE reference_id = @ReferenceId
                ORDER BY event_time DESC, id DESC
                LIMIT @Limit;",
                new
                {
                    ReferenceId = referenceId,
                    Limit = limit <= 0 ? 100 : limit
                })).ToList();

            await LoadChangesAsync(db, events);
            return events;
        }

        public async Task<AuditTrailDashboard> GetDashboardByReferenceAsync(int referenceId, int limit = 50)
        {
            using IDbConnection db = new NpgsqlConnection(_connectionString);
            db.Open();

            var summary = await db.QueryFirstOrDefaultAsync<AuditTrailDashboard>(@"
                SELECT
                    @ReferenceId AS ReferenceId,
                    COUNT(*) AS TotalEvents,
                    COALESCE((
                        SELECT COUNT(*)
                        FROM audit_trail_entity_changes c
                        INNER JOIN audit_trail_events e2 ON e2.id = c.audit_trail_event_id
                        WHERE e2.reference_id = @ReferenceId
                    ), 0) AS ChangeRecords
                FROM audit_trail_events
                WHERE reference_id = @ReferenceId;",
                new { ReferenceId = referenceId }) ?? new AuditTrailDashboard { ReferenceId = referenceId };

            summary.Categories = (await db.QueryAsync<AuditTrailCategoryCount>(@"
                SELECT
                    COALESCE(category, 'Business') AS Category,
                    COUNT(*) AS EventCount
                FROM audit_trail_events
                WHERE reference_id = @ReferenceId
                GROUP BY category
                ORDER BY COUNT(*) DESC, category;",
                new { ReferenceId = referenceId })).ToList();

            summary.RecentEvents = await GetEventsByReferenceAsync(referenceId, limit <= 0 ? 20 : limit);
            return summary;
        }

        private async Task<AuditTrailEvent> GetEventAsync(IDbConnection db, long eventId)
        {
            var auditEvent = await db.QueryFirstOrDefaultAsync<AuditTrailEvent>(@"
                SELECT
                    id,
                    reference_id AS ReferenceId,
                    entity_type AS EntityType,
                    entity_id AS EntityId,
                    category AS Category,
                    action AS Action,
                    summary AS Summary,
                    performed_by_user_id AS PerformedByUserId,
                    performed_by_name AS PerformedByName,
                    icon AS Icon,
                    color AS Color,
                    workflow_instance_id AS WorkflowInstanceId,
                    correlation_id AS CorrelationId,
                    source AS Source,
                    details_json::text AS DetailsJson,
                    event_time AS EventTime
                FROM audit_trail_events
                WHERE id = @EventId;",
                new { EventId = eventId });

            if (auditEvent == null)
                return null;

            var changes = await db.QueryAsync<AuditTrailChange>(@"
                SELECT
                    id,
                    audit_trail_event_id AS AuditTrailEventId,
                    field_name AS FieldName,
                    old_value AS OldValue,
                    new_value AS NewValue
                FROM audit_trail_entity_changes
                WHERE audit_trail_event_id = @EventId
                ORDER BY id;",
                new { EventId = eventId });

            auditEvent.Changes = changes.ToList();
            return auditEvent;
        }

        private async Task LoadChangesAsync(IDbConnection db, List<AuditTrailEvent> events)
        {
            if (events == null || events.Count == 0)
                return;

            var eventIds = events.Select(auditEvent => auditEvent.Id).ToArray();
            var changes = (await db.QueryAsync<AuditTrailChange>(@"
                SELECT
                    id,
                    audit_trail_event_id AS AuditTrailEventId,
                    field_name AS FieldName,
                    old_value AS OldValue,
                    new_value AS NewValue
                FROM audit_trail_entity_changes
                WHERE audit_trail_event_id = ANY(@EventIds)
                ORDER BY audit_trail_event_id, id;",
                new { EventIds = eventIds })).ToList();

            var grouped = changes.GroupBy(change => change.AuditTrailEventId)
                .ToDictionary(group => group.Key, group => group.ToList());

            foreach (var auditEvent in events)
            {
                auditEvent.Changes = grouped.TryGetValue(auditEvent.Id, out var eventChanges)
                    ? eventChanges
                    : new List<AuditTrailChange>();
            }
        }
    }
}
