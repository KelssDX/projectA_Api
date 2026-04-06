using Affine.Engine.Model.Auditing.AuditUniverse;
using Dapper;
using Npgsql;
using System.Collections.Generic;
using System.Linq;

namespace Affine.Engine.Repository.Auditing
{
    public class AuditAccessLogRepository : IAuditAccessLogRepository
    {
        private readonly string _connectionString;

        public AuditAccessLogRepository(string connectionString)
        {
            _connectionString = connectionString;
        }

        public async Task LogDocumentAccessAsync(AuditDocumentAccessLogEntry entry)
        {
            const string sql = @"
                INSERT INTO audit_document_access_logs (
                    document_id,
                    reference_id,
                    action_type,
                    accessed_by_user_id,
                    accessed_by_name,
                    ip_address,
                    client_context,
                    correlation_id,
                    success,
                    details_json
                )
                VALUES (
                    @DocumentId,
                    @ReferenceId,
                    @ActionType,
                    @AccessedByUserId,
                    @AccessedByName,
                    @IpAddress,
                    @ClientContext,
                    @CorrelationId,
                    @Success,
                    CAST(@DetailsJson AS jsonb)
                );";

            await using var connection = new NpgsqlConnection(_connectionString);
            await connection.OpenAsync();
            await connection.ExecuteAsync(sql, new
            {
                entry.DocumentId,
                entry.ReferenceId,
                entry.ActionType,
                entry.AccessedByUserId,
                entry.AccessedByName,
                entry.IpAddress,
                entry.ClientContext,
                entry.CorrelationId,
                entry.Success,
                DetailsJson = string.IsNullOrWhiteSpace(entry.DetailsJson) ? null : entry.DetailsJson
            });
        }

        public async Task<IReadOnlyList<AuditDocumentAccessLogRecord>> GetDocumentAccessLogsByReferenceAsync(int referenceId, int? documentId = null, int limit = 100)
        {
            const string sql = @"
                SELECT
                    l.id AS Id,
                    l.document_id AS DocumentId,
                    l.reference_id AS ReferenceId,
                    l.action_type AS ActionType,
                    l.accessed_by_user_id AS AccessedByUserId,
                    l.accessed_by_name AS AccessedByName,
                    l.ip_address AS IpAddress,
                    l.client_context AS ClientContext,
                    l.correlation_id AS CorrelationId,
                    l.success AS Success,
                    l.details_json::text AS DetailsJson,
                    l.accessed_at AS AccessedAt,
                    d.title AS DocumentTitle,
                    d.document_code AS DocumentCode
                FROM audit_document_access_logs l
                LEFT JOIN audit_documents d ON d.id = l.document_id
                WHERE l.reference_id = @ReferenceId
                  AND (@DocumentId IS NULL OR l.document_id = @DocumentId)
                ORDER BY l.accessed_at DESC, l.id DESC
                LIMIT @Limit;";

            await using var connection = new NpgsqlConnection(_connectionString);
            await connection.OpenAsync();
            var rows = await connection.QueryAsync<AuditDocumentAccessLogRecord>(sql, new
            {
                ReferenceId = referenceId,
                DocumentId = documentId,
                Limit = limit <= 0 ? 100 : limit
            });

            return rows.ToList();
        }

        public async Task LogLoginEventAsync(AuditLoginEventEntry entry)
        {
            const string sql = @"
                INSERT INTO audit_login_events (
                    user_id,
                    username,
                    display_name,
                    event_type,
                    status,
                    ip_address,
                    user_agent,
                    client_context,
                    failure_reason,
                    correlation_id
                )
                VALUES (
                    @UserId,
                    @Username,
                    @DisplayName,
                    @EventType,
                    @Status,
                    @IpAddress,
                    @UserAgent,
                    @ClientContext,
                    @FailureReason,
                    @CorrelationId
                );";

            await using var connection = new NpgsqlConnection(_connectionString);
            await connection.OpenAsync();
            await connection.ExecuteAsync(sql, entry);
        }
    }
}
