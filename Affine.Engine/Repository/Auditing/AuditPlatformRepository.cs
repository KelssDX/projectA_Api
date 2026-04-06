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
    public class AuditPlatformRepository : IAuditPlatformRepository
    {
        private readonly string _connectionString;

        public AuditPlatformRepository(string connectionString)
        {
            _connectionString = connectionString ?? throw new ArgumentNullException(nameof(connectionString));
        }

        public async Task<List<AuditRetentionPolicy>> GetRetentionPoliciesAsync()
        {
            using IDbConnection db = new NpgsqlConnection(_connectionString);
            db.Open();

            var query = @"
                SELECT
                    id AS Id,
                    policy_name AS PolicyName,
                    entity_type AS EntityType,
                    retention_days AS RetentionDays,
                    archive_action AS ArchiveAction,
                    is_enabled AS IsEnabled,
                    notes AS Notes,
                    created_at AS CreatedAt,
                    updated_at AS UpdatedAt
                FROM audit_retention_policies
                WHERE is_enabled = true
                ORDER BY entity_type, policy_name";

            return (await db.QueryAsync<AuditRetentionPolicy>(query)).ToList();
        }

        public async Task<ArchiveAssessmentResult> ArchiveAssessmentAsync(ArchiveAssessmentRequest request)
        {
            if (request == null)
                throw new ArgumentNullException(nameof(request));

            using IDbConnection db = new NpgsqlConnection(_connectionString);
            db.Open();
            using var tx = db.BeginTransaction();

            var current = await db.QueryFirstOrDefaultAsync<AssessmentArchiveState>(
                @"SELECT
                    reference_id AS ReferenceId,
                    COALESCE(is_archived, false) AS IsArchived,
                    archived_at AS ArchivedAt
                  FROM riskassessmentreference
                  WHERE reference_id = @ReferenceId",
                new { request.ReferenceId }, tx);

            if (current == null)
            {
                tx.Rollback();
                return new ArchiveAssessmentResult
                {
                    Success = false,
                    ReferenceId = request.ReferenceId,
                    Message = "Assessment reference not found."
                };
            }

            if (current.IsArchived)
            {
                tx.Rollback();
                return new ArchiveAssessmentResult
                {
                    Success = true,
                    ReferenceId = request.ReferenceId,
                    AlreadyArchived = true,
                    ArchivedAt = current.ArchivedAt,
                    Message = "Assessment already archived."
                };
            }

            var archivedAt = DateTime.UtcNow;
            await db.ExecuteAsync(
                @"UPDATE riskassessmentreference
                  SET
                    is_archived = true,
                    archived_at = @ArchivedAt,
                    archived_by_user_id = @ArchivedByUserId,
                    archived_by_name = @ArchivedByName,
                    archive_reason = @Reason
                  WHERE reference_id = @ReferenceId",
                new
                {
                    request.ReferenceId,
                    ArchivedAt = archivedAt,
                    request.ArchivedByUserId,
                    request.ArchivedByName,
                    request.Reason
                }, tx);

            var eventId = await db.ExecuteScalarAsync<int>(
                @"INSERT INTO audit_archival_events
                    (
                        reference_id,
                        entity_type,
                        entity_id,
                        archive_action,
                        reason,
                        retention_policy_id,
                        archived_by_user_id,
                        archived_by_name,
                        archived_at,
                        details_json
                    )
                  VALUES
                    (
                        @ReferenceId,
                        'Assessment',
                        @EntityId,
                        'Archive',
                        @Reason,
                        (
                            SELECT id FROM audit_retention_policies
                            WHERE entity_type = 'Assessment'
                            ORDER BY id
                            LIMIT 1
                        ),
                        @ArchivedByUserId,
                        @ArchivedByName,
                        @ArchivedAt,
                        @DetailsJson
                    )
                  RETURNING id",
                new
                {
                    request.ReferenceId,
                    EntityId = request.ReferenceId.ToString(),
                    request.Reason,
                    request.ArchivedByUserId,
                    request.ArchivedByName,
                    ArchivedAt = archivedAt,
                    DetailsJson = System.Text.Json.JsonSerializer.Serialize(new
                    {
                        request.ReferenceId,
                        request.Reason
                    })
                }, tx);

            var archivalEvent = await db.QueryFirstOrDefaultAsync<AuditArchivalEvent>(
                @"SELECT
                    id AS Id,
                    reference_id AS ReferenceId,
                    entity_type AS EntityType,
                    entity_id AS EntityId,
                    archive_action AS ArchiveAction,
                    reason AS Reason,
                    retention_policy_id AS RetentionPolicyId,
                    archived_by_user_id AS ArchivedByUserId,
                    archived_by_name AS ArchivedByName,
                    archived_at AS ArchivedAt,
                    details_json AS DetailsJson
                  FROM audit_archival_events
                  WHERE id = @Id",
                new { Id = eventId }, tx);

            tx.Commit();

            return new ArchiveAssessmentResult
            {
                Success = true,
                ReferenceId = request.ReferenceId,
                ArchivedAt = archivedAt,
                Event = archivalEvent,
                Message = "Assessment archived successfully."
            };
        }

        public async Task<AuditUsageEvent> RecordUsageEventAsync(RecordAuditUsageEventRequest request)
        {
            if (request == null)
                throw new ArgumentNullException(nameof(request));

            using IDbConnection db = new NpgsqlConnection(_connectionString);
            db.Open();

            var eventId = await db.ExecuteScalarAsync<int>(
                @"INSERT INTO audit_usage_events
                    (
                        module_name,
                        feature_name,
                        event_name,
                        reference_id,
                        performed_by_user_id,
                        performed_by_name,
                        role_name,
                        session_id,
                        source,
                        metadata_json
                    )
                  VALUES
                    (
                        @ModuleName,
                        @FeatureName,
                        @EventName,
                        @ReferenceId,
                        @PerformedByUserId,
                        @PerformedByName,
                        @RoleName,
                        @SessionId,
                        @Source,
                        @MetadataJson
                    )
                  RETURNING id",
                request);

            return await db.QueryFirstOrDefaultAsync<AuditUsageEvent>(
                @"SELECT
                    id AS Id,
                    module_name AS ModuleName,
                    feature_name AS FeatureName,
                    event_name AS EventName,
                    reference_id AS ReferenceId,
                    performed_by_user_id AS PerformedByUserId,
                    performed_by_name AS PerformedByName,
                    role_name AS RoleName,
                    session_id AS SessionId,
                    source AS Source,
                    metadata_json AS MetadataJson,
                    event_time AS EventTime
                  FROM audit_usage_events
                  WHERE id = @Id",
                new { Id = eventId });
        }

        public async Task<List<AuditUsageSummary>> GetUsageSummaryAsync(int days = 30)
        {
            using IDbConnection db = new NpgsqlConnection(_connectionString);
            db.Open();

            var query = @"
                SELECT
                    module_name AS ModuleName,
                    feature_name AS FeatureName,
                    event_name AS EventName,
                    COUNT(*)::INT AS EventCount,
                    MAX(event_time) AS LastEventTime
                FROM audit_usage_events
                WHERE event_time >= CURRENT_TIMESTAMP - make_interval(days => @Days)
                GROUP BY module_name, feature_name, event_name
                ORDER BY COUNT(*) DESC, MAX(event_time) DESC";

            return (await db.QueryAsync<AuditUsageSummary>(query, new { Days = days <= 0 ? 30 : days })).ToList();
        }

        private sealed class AssessmentArchiveState
        {
            public int ReferenceId { get; set; }
            public bool IsArchived { get; set; }
            public DateTime? ArchivedAt { get; set; }
        }
    }
}
