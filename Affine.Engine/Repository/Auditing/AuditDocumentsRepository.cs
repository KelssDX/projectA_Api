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
    public class AuditDocumentsRepository : IAuditDocumentsRepository
    {
        private readonly string _connectionString;

        private const string DocumentSelect = @"
            SELECT
                d.id AS Id,
                d.reference_id AS ReferenceId,
                d.audit_universe_id AS AuditUniverseId,
                d.procedure_id AS ProcedureId,
                d.working_paper_id AS WorkingPaperId,
                d.finding_id AS FindingId,
                d.recommendation_id AS RecommendationId,
                d.document_code AS DocumentCode,
                d.title AS Title,
                d.original_file_name AS OriginalFileName,
                d.stored_file_name AS StoredFileName,
                d.stored_relative_path AS StoredRelativePath,
                d.content_type AS ContentType,
                d.file_extension AS FileExtension,
                d.file_size AS FileSize,
                d.category_id AS CategoryId,
                d.visibility_level_id AS VisibilityLevelId,
                d.source_type AS SourceType,
                d.tags AS Tags,
                d.notes AS Notes,
                d.confidentiality_label AS ConfidentialityLabel,
                d.confidentiality_reason AS ConfidentialityReason,
                d.security_review_required AS SecurityReviewRequired,
                d.security_review_status AS SecurityReviewStatus,
                d.security_review_requested_at AS SecurityReviewRequestedAt,
                d.security_review_requested_by_user_id AS SecurityReviewRequestedByUserId,
                d.security_review_requested_by_name AS SecurityReviewRequestedByName,
                d.security_reviewed_at AS SecurityReviewedAt,
                d.security_reviewed_by_user_id AS SecurityReviewedByUserId,
                d.security_reviewed_by_name AS SecurityReviewedByName,
                d.security_review_notes AS SecurityReviewNotes,
                d.uploaded_by_name AS UploadedByName,
                d.uploaded_by_user_id AS UploadedByUserId,
                d.uploaded_at AS UploadedAt,
                d.is_active AS IsActive,
                c.name AS CategoryName,
                c.color AS CategoryColor,
                COALESCE(c.is_sensitive, false) AS IsSensitiveCategory,
                v.name AS VisibilityLevelName,
                v.color AS VisibilityLevelColor,
                COALESCE(v.is_restricted, false) AS VisibilityIsRestricted,
                p.procedure_title AS ProcedureTitle,
                wp.working_paper_code AS WorkingPaperCode,
                wp.title AS WorkingPaperTitle,
                f.finding_number AS FindingNumber,
                f.finding_title AS FindingTitle,
                r.recommendation_number AS RecommendationNumber,
                r.recommendation AS RecommendationText
            FROM audit_documents d
            LEFT JOIN ra_document_category c ON d.category_id = c.id
            LEFT JOIN ra_document_visibility_level v ON d.visibility_level_id = v.id
            LEFT JOIN audit_procedures p ON d.procedure_id = p.id
            LEFT JOIN audit_working_papers wp ON d.working_paper_id = wp.id
            LEFT JOIN audit_findings f ON d.finding_id = f.id
            LEFT JOIN audit_recommendations r ON d.recommendation_id = r.id";

        private const string EvidenceRequestSelect = @"
            SELECT
                er.id AS Id,
                er.reference_id AS ReferenceId,
                er.audit_universe_id AS AuditUniverseId,
                er.request_number AS RequestNumber,
                er.title AS Title,
                er.request_description AS RequestDescription,
                er.requested_from AS RequestedFrom,
                er.requested_to_email AS RequestedToEmail,
                er.priority AS Priority,
                er.due_date AS DueDate,
                er.status_id AS StatusId,
                er.requested_by_user_id AS RequestedByUserId,
                er.requested_by_name AS RequestedByName,
                er.workflow_instance_id AS WorkflowInstanceId,
                er.notes AS Notes,
                er.created_at AS CreatedAt,
                er.updated_at AS UpdatedAt,
                st.name AS StatusName,
                st.color AS StatusColor,
                (SELECT COUNT(*) FROM audit_evidence_request_items i WHERE i.request_id = er.id) AS TotalItems,
                (SELECT COUNT(*) FROM audit_evidence_request_items i WHERE i.request_id = er.id AND i.fulfilled_document_id IS NOT NULL) AS FulfilledItems
            FROM audit_evidence_requests er
            LEFT JOIN ra_evidence_request_status st ON er.status_id = st.id";

        public AuditDocumentsRepository(string connectionString)
        {
            _connectionString = connectionString ?? throw new ArgumentNullException(nameof(connectionString));
        }

        public async Task<AuditDocument> GetDocumentAsync(int id)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();

                var query = $"{DocumentSelect} WHERE d.id = @Id";
                var document = await db.QueryFirstOrDefaultAsync<AuditDocument>(query, new { Id = id });
                if (document != null)
                {
                    await AttachDocumentSecurityAsync(db, new List<AuditDocument> { document });
                }

                return document;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in GetDocumentAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<List<AuditDocument>> GetDocumentsByReferenceAsync(int referenceId)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();

                var query = $@"
                    {DocumentSelect}
                    WHERE d.reference_id = @ReferenceId
                      AND d.is_active = true
                    ORDER BY COALESCE(d.uploaded_at, CURRENT_TIMESTAMP) DESC, d.title";

                var documents = (await db.QueryAsync<AuditDocument>(query, new { ReferenceId = referenceId })).ToList();
                await AttachDocumentSecurityAsync(db, documents);
                return documents;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in GetDocumentsByReferenceAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<List<AuditDocumentCategory>> GetDocumentCategoriesAsync()
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();

                var query = @"
                    SELECT
                        id AS Id,
                        name AS Name,
                        description AS Description,
                        color AS Color,
                        sort_order AS SortOrder,
                        COALESCE(is_sensitive, false) AS IsSensitive,
                        default_visibility_level_id AS DefaultVisibilityLevelId,
                        COALESCE(requires_security_approval, false) AS RequiresSecurityApproval,
                        default_confidentiality_label AS DefaultConfidentialityLabel,
                        is_active AS IsActive
                    FROM ra_document_category
                    WHERE is_active = true
                    ORDER BY sort_order, name";

                var result = await db.QueryAsync<AuditDocumentCategory>(query);
                return result.ToList();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in GetDocumentCategoriesAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<List<AuditDocumentVisibilityOption>> GetDocumentVisibilityOptionsAsync()
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();

                var query = @"
                    SELECT
                        id AS Id,
                        name AS Name,
                        description AS Description,
                        color AS Color,
                        is_restricted AS IsRestricted,
                        sort_order AS SortOrder,
                        is_active AS IsActive
                    FROM ra_document_visibility_level
                    WHERE is_active = true
                    ORDER BY sort_order, name";

                var result = await db.QueryAsync<AuditDocumentVisibilityOption>(query);
                return result.ToList();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in GetDocumentVisibilityOptionsAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<AuditDocument> CreateDocumentAsync(CreateAuditDocumentRequest request)
        {
            try
            {
                using var db = new NpgsqlConnection(_connectionString);
                await db.OpenAsync();
                using var transaction = await db.BeginTransactionAsync();

                var query = @"
                    INSERT INTO audit_documents
                    (
                        reference_id,
                        audit_universe_id,
                        procedure_id,
                        working_paper_id,
                        finding_id,
                        recommendation_id,
                        title,
                        original_file_name,
                        stored_file_name,
                        stored_relative_path,
                        content_type,
                        file_extension,
                        file_size,
                        category_id,
                        visibility_level_id,
                        source_type,
                        tags,
                        notes,
                        confidentiality_label,
                        confidentiality_reason,
                        security_review_required,
                        security_review_status,
                        security_review_requested_at,
                        security_review_requested_by_user_id,
                        security_review_requested_by_name,
                        security_reviewed_at,
                        security_reviewed_by_user_id,
                        security_reviewed_by_name,
                        security_review_notes,
                        uploaded_by_name,
                        uploaded_by_user_id
                    )
                    VALUES
                    (
                        @ReferenceId,
                        @AuditUniverseId,
                        @ProcedureId,
                        @WorkingPaperId,
                        @FindingId,
                        @RecommendationId,
                        @Title,
                        @OriginalFileName,
                        @StoredFileName,
                        @StoredRelativePath,
                        @ContentType,
                        @FileExtension,
                        @FileSize,
                        @CategoryId,
                        COALESCE(
                            @VisibilityLevelId,
                            (
                                SELECT id
                                FROM ra_document_visibility_level
                                WHERE name = 'Engagement Team'
                                LIMIT 1
                            )
                        ),
                        @SourceType,
                        @Tags,
                        @Notes,
                        @ConfidentialityLabel,
                        @ConfidentialityReason,
                        @SecurityReviewRequired,
                        @SecurityReviewStatus,
                        @SecurityReviewRequestedAt,
                        @SecurityReviewRequestedByUserId,
                        @SecurityReviewRequestedByName,
                        @SecurityReviewedAt,
                        @SecurityReviewedByUserId,
                        @SecurityReviewedByName,
                        @SecurityReviewNotes,
                        @UploadedByName,
                        @UploadedByUserId
                    )
                    RETURNING id";

                var newId = await db.ExecuteScalarAsync<int>(query, request, transaction);

                await InsertDocumentPermissionGrantsAsync(db, transaction, newId, request);

                await transaction.CommitAsync();
                return await GetDocumentAsync(newId);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in CreateDocumentAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<AuditDocument> UpdateDocumentSecurityAsync(int id, UpdateAuditDocumentSecurityRequest request)
        {
            if (id <= 0)
            {
                throw new ArgumentException("Document ID must be greater than zero.", nameof(id));
            }

            if (request == null)
            {
                throw new ArgumentNullException(nameof(request));
            }

            try
            {
                using var db = new NpgsqlConnection(_connectionString);
                await db.OpenAsync();
                using var transaction = await db.BeginTransactionAsync();

                var resolvedVisibilityLevelId = await ResolveVisibilityLevelIdAsync(
                    db,
                    request.VisibilityLevelId,
                    request.VisibilityLevelName,
                    transaction);

                const string updateDocument = @"
                    UPDATE audit_documents
                    SET
                        visibility_level_id = COALESCE(@VisibilityLevelId, visibility_level_id),
                        confidentiality_label = @ConfidentialityLabel,
                        confidentiality_reason = @ConfidentialityReason
                    WHERE id = @Id;";

                var affected = await db.ExecuteAsync(updateDocument, new
                {
                    Id = id,
                    VisibilityLevelId = resolvedVisibilityLevelId,
                    request.ConfidentialityLabel,
                    request.ConfidentialityReason
                }, transaction);

                if (affected == 0)
                {
                    await transaction.RollbackAsync();
                    throw new InvalidOperationException($"Document {id} was not found.");
                }

                await db.ExecuteAsync(
                    "DELETE FROM audit_document_permission_grants WHERE document_id = @DocumentId;",
                    new { DocumentId = id },
                    transaction);

                var createRequest = new CreateAuditDocumentRequest
                {
                    GrantedByName = request.UpdatedByName,
                    GrantedByUserId = request.UpdatedByUserId,
                    GrantedUserIds = (request.GrantedUserIds ?? new List<int>()).ToList(),
                    GrantedRoleNames = (request.GrantedRoleNames ?? new List<string>()).ToList(),
                    ConfidentialityReason = request.ConfidentialityReason
                };

                await InsertDocumentPermissionGrantsAsync(db, transaction, id, createRequest);
                await transaction.CommitAsync();

                return await GetDocumentAsync(id);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in UpdateDocumentSecurityAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<AuditDocument> ReviewDocumentSecurityAsync(int id, ReviewAuditDocumentSecurityRequest request)
        {
            if (id <= 0)
            {
                throw new ArgumentException("Document ID must be greater than zero.", nameof(id));
            }

            if (request == null)
            {
                throw new ArgumentNullException(nameof(request));
            }

            try
            {
                using var db = new NpgsqlConnection(_connectionString);
                await db.OpenAsync();

                const string updateDocument = @"
                    UPDATE audit_documents
                    SET
                        security_review_status = @SecurityReviewStatus,
                        security_reviewed_at = CURRENT_TIMESTAMP,
                        security_reviewed_by_user_id = @ReviewedByUserId,
                        security_reviewed_by_name = @ReviewedByName,
                        security_review_notes = @ReviewNotes
                    WHERE id = @Id;";

                var affected = await db.ExecuteAsync(updateDocument, new
                {
                    Id = id,
                    SecurityReviewStatus = request.IsApproved ? "Approved" : "Rejected",
                    request.ReviewedByUserId,
                    request.ReviewedByName,
                    request.ReviewNotes
                });

                if (affected == 0)
                {
                    throw new InvalidOperationException($"Document {id} was not found.");
                }

                return await GetDocumentAsync(id);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in ReviewDocumentSecurityAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<bool> DeleteDocumentAsync(int id)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();

                var query = "DELETE FROM audit_documents WHERE id = @Id";
                var affected = await db.ExecuteAsync(query, new { Id = id });
                return affected > 0;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in DeleteDocumentAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<AuditEvidenceRequestAssignmentContext> GetEvidenceRequestAssignmentContextByItemAsync(int requestItemId)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();

                const string query = @"
                    SELECT
                        i.id AS RequestItemId,
                        er.id AS RequestId,
                        er.reference_id AS ReferenceId,
                        er.title AS Title,
                        er.requested_from AS RequestedFrom,
                        er.requested_to_email AS RequestedToEmail,
                        er.requested_by_user_id AS RequestedByUserId,
                        er.requested_by_name AS RequestedByName,
                        i.item_description AS ItemDescription,
                        i.is_required AS IsRequired,
                        i.fulfilled_document_id AS FulfilledDocumentId
                    FROM audit_evidence_request_items i
                    INNER JOIN audit_evidence_requests er ON er.id = i.request_id
                    WHERE i.id = @RequestItemId;";

                return await db.QueryFirstOrDefaultAsync<AuditEvidenceRequestAssignmentContext>(
                    query,
                    new { RequestItemId = requestItemId });
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in GetEvidenceRequestAssignmentContextByItemAsync: {ex.Message}");
                throw;
            }
        }

        private async Task AttachDocumentSecurityAsync(IDbConnection db, List<AuditDocument> documents)
        {
            if (documents == null || documents.Count == 0)
            {
                return;
            }

            var documentIds = documents
                .Where(document => document != null && document.Id > 0)
                .Select(document => document.Id)
                .Distinct()
                .ToArray();

            if (documentIds.Length == 0)
            {
                return;
            }

            var grants = (await db.QueryAsync<AuditDocumentAccessGrant>(@"
                SELECT
                    g.id AS Id,
                    g.document_id AS DocumentId,
                    g.grantee_user_id AS GranteeUserId,
                    COALESCE(u.name, u.username, g.grantee_role_name, 'Granted User') AS GrantedUserName,
                    g.grantee_role_name AS GranteeRoleName,
                    g.permission_level AS PermissionLevel,
                    g.can_download AS CanDownload,
                    g.granted_by_user_id AS GrantedByUserId,
                    g.granted_by_name AS GrantedByName,
                    g.notes AS Notes,
                    g.granted_at AS GrantedAt,
                    g.expires_at AS ExpiresAt
                FROM audit_document_permission_grants g
                LEFT JOIN users u ON g.grantee_user_id = u.id
                WHERE g.document_id = ANY(@DocumentIds)
                ORDER BY g.granted_at, g.id", new { DocumentIds = documentIds })).ToList();

            var grantLookup = grants
                .GroupBy(grant => grant.DocumentId)
                .ToDictionary(group => group.Key, group => group.ToList());

            foreach (var document in documents)
            {
                document.AccessGrants = grantLookup.TryGetValue(document.Id, out var documentGrants)
                    ? documentGrants
                    : new List<AuditDocumentAccessGrant>();

                if (string.IsNullOrWhiteSpace(document.VisibilityLevelName))
                {
                    document.VisibilityLevelName = "Engagement Team";
                }

                if (string.IsNullOrWhiteSpace(document.VisibilityLevelColor))
                {
                    document.VisibilityLevelColor = "#2563EB";
                }

                document.AccessSummary = BuildAccessSummary(document);
            }
        }

        private async Task InsertDocumentPermissionGrantsAsync(
            NpgsqlConnection db,
            NpgsqlTransaction transaction,
            int documentId,
            CreateAuditDocumentRequest request)
        {
            if (documentId <= 0 || request == null || !request.HasExplicitGrants)
            {
                return;
            }

            const string insertGrant = @"
                INSERT INTO audit_document_permission_grants
                (
                    document_id,
                    grantee_user_id,
                    grantee_role_name,
                    permission_level,
                    can_download,
                    granted_by_user_id,
                    granted_by_name,
                    notes
                )
                VALUES
                (
                    @DocumentId,
                    @GranteeUserId,
                    @GranteeRoleName,
                    @PermissionLevel,
                    @CanDownload,
                    @GrantedByUserId,
                    @GrantedByName,
                    @Notes
                )
                ON CONFLICT DO NOTHING";

            foreach (var userId in (request.GrantedUserIds ?? new List<int>()).Where(id => id > 0).Distinct())
            {
                await db.ExecuteAsync(insertGrant, new
                {
                    DocumentId = documentId,
                    GranteeUserId = userId,
                    GranteeRoleName = (string)null,
                    PermissionLevel = "View",
                    CanDownload = true,
                    request.GrantedByUserId,
                    request.GrantedByName,
                    Notes = request.ConfidentialityReason
                }, transaction);
            }

            foreach (var roleName in (request.GrantedRoleNames ?? new List<string>())
                .Where(role => !string.IsNullOrWhiteSpace(role))
                .Select(role => role.Trim())
                .Distinct(StringComparer.OrdinalIgnoreCase))
            {
                await db.ExecuteAsync(insertGrant, new
                {
                    DocumentId = documentId,
                    GranteeUserId = (int?)null,
                    GranteeRoleName = roleName,
                    PermissionLevel = "View",
                    CanDownload = true,
                    request.GrantedByUserId,
                    request.GrantedByName,
                    Notes = request.ConfidentialityReason
                }, transaction);
            }
        }

        private static async Task<int?> ResolveVisibilityLevelIdAsync(
            NpgsqlConnection db,
            int? requestedVisibilityLevelId,
            string requestedVisibilityLevelName,
            NpgsqlTransaction transaction)
        {
            if (requestedVisibilityLevelId.HasValue && requestedVisibilityLevelId.Value > 0)
            {
                return requestedVisibilityLevelId.Value;
            }

            if (string.IsNullOrWhiteSpace(requestedVisibilityLevelName))
            {
                return null;
            }

            const string query = @"
                SELECT id
                FROM ra_document_visibility_level
                WHERE LOWER(name) = LOWER(@Name)
                LIMIT 1;";

            return await db.ExecuteScalarAsync<int?>(query, new
            {
                Name = requestedVisibilityLevelName.Trim()
            }, transaction);
        }

        private static string BuildAccessSummary(AuditDocument document)
        {
            var baseVisibility = string.IsNullOrWhiteSpace(document.VisibilityLevelName)
                ? "Engagement Team"
                : document.VisibilityLevelName.Trim();

            if (document.AccessGrants == null || document.AccessGrants.Count == 0)
            {
                return baseVisibility;
            }

            var grantLabels = document.AccessGrants
                .Select(grant =>
                {
                    if (grant.GranteeUserId.HasValue && !string.IsNullOrWhiteSpace(grant.GrantedUserName))
                    {
                        return grant.GrantedUserName.Trim();
                    }

                    if (!string.IsNullOrWhiteSpace(grant.GranteeRoleName))
                    {
                        return grant.GranteeRoleName.Trim();
                    }

                    return null;
                })
                .Where(label => !string.IsNullOrWhiteSpace(label))
                .Distinct(StringComparer.OrdinalIgnoreCase)
                .ToList();

            if (grantLabels.Count == 0)
            {
                return baseVisibility;
            }

            return $"{baseVisibility} + {string.Join(", ", grantLabels.Take(3))}{(grantLabels.Count > 3 ? ", ..." : string.Empty)}";
        }

        public async Task<List<AuditEvidenceRequest>> GetEvidenceRequestsByReferenceAsync(int referenceId)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();

                var query = $@"
                    {EvidenceRequestSelect}
                    WHERE er.reference_id = @ReferenceId
                    ORDER BY COALESCE(er.due_date, er.created_at) DESC, er.title";

                var requests = (await db.QueryAsync<AuditEvidenceRequest>(query, new { ReferenceId = referenceId })).ToList();
                foreach (var request in requests)
                {
                    request.Items = await GetEvidenceRequestItemsAsync(db, request.Id);
                }
                return requests;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in GetEvidenceRequestsByReferenceAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<List<EvidenceRequestStatus>> GetEvidenceRequestStatusesAsync()
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();

                var query = @"
                    SELECT
                        id AS Id,
                        name AS Name,
                        description AS Description,
                        color AS Color,
                        is_closed AS IsClosed,
                        sort_order AS SortOrder,
                        is_active AS IsActive
                    FROM ra_evidence_request_status
                    WHERE is_active = true
                    ORDER BY sort_order, name";

                var result = await db.QueryAsync<EvidenceRequestStatus>(query);
                return result.ToList();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in GetEvidenceRequestStatusesAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<AuditEvidenceRequest> CreateEvidenceRequestAsync(CreateAuditEvidenceRequestRequest request)
        {
            try
            {
                using var db = new NpgsqlConnection(_connectionString);
                await db.OpenAsync();
                using var transaction = await db.BeginTransactionAsync();

                var insertRequest = @"
                    INSERT INTO audit_evidence_requests
                    (
                        reference_id,
                        audit_universe_id,
                        title,
                        request_description,
                        requested_from,
                        requested_to_email,
                        priority,
                        due_date,
                        status_id,
                        requested_by_user_id,
                        requested_by_name,
                        workflow_instance_id,
                        notes
                    )
                    VALUES
                    (
                        @ReferenceId,
                        @AuditUniverseId,
                        @Title,
                        @RequestDescription,
                        @RequestedFrom,
                        @RequestedToEmail,
                        COALESCE(@Priority, 2),
                        @DueDate,
                        COALESCE(@StatusId, 2),
                        @RequestedByUserId,
                        @RequestedByName,
                        @WorkflowInstanceId,
                        @Notes
                    )
                    RETURNING id";

                var requestId = await db.ExecuteScalarAsync<int>(insertRequest, request, transaction);

                if (request.Items != null && request.Items.Any())
                {
                    var insertItem = @"
                        INSERT INTO audit_evidence_request_items
                        (
                            request_id,
                            item_description,
                            expected_document_type,
                            is_required
                        )
                        VALUES
                        (
                            @RequestId,
                            @ItemDescription,
                            @ExpectedDocumentType,
                            @IsRequired
                        )";

                    foreach (var item in request.Items.Where(i => !string.IsNullOrWhiteSpace(i.ItemDescription)))
                    {
                        await db.ExecuteAsync(insertItem, new
                        {
                            RequestId = requestId,
                            ItemDescription = item.ItemDescription.Trim(),
                            ExpectedDocumentType = item.ExpectedDocumentType,
                            IsRequired = item.IsRequired
                        }, transaction);
                    }
                }

                await transaction.CommitAsync();
                return await GetEvidenceRequestAsync(requestId);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in CreateEvidenceRequestAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<bool> FulfillEvidenceRequestItemAsync(int requestItemId, int documentId)
        {
            try
            {
                using var db = new NpgsqlConnection(_connectionString);
                await db.OpenAsync();
                using var transaction = await db.BeginTransactionAsync();

                var updateItem = @"
                    UPDATE audit_evidence_request_items
                    SET
                        fulfilled_document_id = @DocumentId,
                        submitted_at = CURRENT_TIMESTAMP
                    WHERE id = @RequestItemId";

                var affected = await db.ExecuteAsync(updateItem, new
                {
                    DocumentId = documentId,
                    RequestItemId = requestItemId
                }, transaction);

                if (affected == 0)
                {
                    await transaction.RollbackAsync();
                    return false;
                }

                var requestId = await db.ExecuteScalarAsync<int?>(@"
                    SELECT request_id
                    FROM audit_evidence_request_items
                    WHERE id = @RequestItemId", new { RequestItemId = requestItemId }, transaction);

                if (requestId.HasValue)
                {
                    await RefreshEvidenceRequestStatusAsync(db, requestId.Value, transaction);
                }

                await transaction.CommitAsync();
                return true;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in FulfillEvidenceRequestItemAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<AuditEvidenceRequestItem> ReviewEvidenceRequestItemAsync(ReviewEvidenceRequestItemRequest request)
        {
            try
            {
                using var db = new NpgsqlConnection(_connectionString);
                await db.OpenAsync();
                using var transaction = await db.BeginTransactionAsync();

                var updateItem = @"
                    UPDATE audit_evidence_request_items
                    SET
                        reviewer_notes = @ReviewerNotes,
                        reviewed_by_user_id = @ReviewedByUserId,
                        reviewed_at = CURRENT_TIMESTAMP,
                        is_accepted = @IsAccepted
                    WHERE id = @RequestItemId";

                var affected = await db.ExecuteAsync(updateItem, request, transaction);
                if (affected == 0)
                {
                    await transaction.RollbackAsync();
                    throw new InvalidOperationException($"Evidence request item {request.RequestItemId} was not found.");
                }

                var requestId = await db.ExecuteScalarAsync<int?>(@"
                    SELECT request_id
                    FROM audit_evidence_request_items
                    WHERE id = @RequestItemId", new { request.RequestItemId }, transaction);

                if (requestId.HasValue)
                {
                    await RefreshEvidenceRequestStatusAsync(db, requestId.Value, transaction);
                }

                await transaction.CommitAsync();
                return await GetEvidenceRequestItemAsync(request.RequestItemId);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in ReviewEvidenceRequestItemAsync: {ex.Message}");
                throw;
            }
        }

        private async Task<AuditEvidenceRequest> GetEvidenceRequestAsync(int id)
        {
            using IDbConnection db = new NpgsqlConnection(_connectionString);
            db.Open();

            var query = $"{EvidenceRequestSelect} WHERE er.id = @Id";
            var request = await db.QueryFirstOrDefaultAsync<AuditEvidenceRequest>(query, new { Id = id });
            if (request != null)
            {
                request.Items = await GetEvidenceRequestItemsAsync(db, id);
            }
            return request;
        }

        private async Task<List<AuditEvidenceRequestItem>> GetEvidenceRequestItemsAsync(IDbConnection db, int requestId)
        {
            var query = @"
                SELECT
                    i.id AS Id,
                    i.request_id AS RequestId,
                    i.item_description AS ItemDescription,
                    i.expected_document_type AS ExpectedDocumentType,
                    i.is_required AS IsRequired,
                    i.fulfilled_document_id AS FulfilledDocumentId,
                    i.submitted_at AS SubmittedAt,
                    i.reviewer_notes AS ReviewerNotes,
                    i.reviewed_by_user_id AS ReviewedByUserId,
                    i.reviewed_at AS ReviewedAt,
                    i.is_accepted AS IsAccepted,
                    i.created_at AS CreatedAt,
                    d.document_code AS FulfilledDocumentCode,
                    d.title AS FulfilledDocumentTitle
                FROM audit_evidence_request_items i
                LEFT JOIN audit_documents d ON i.fulfilled_document_id = d.id
                WHERE i.request_id = @RequestId
                ORDER BY i.id";

            var result = await db.QueryAsync<AuditEvidenceRequestItem>(query, new { RequestId = requestId });
            return result.ToList();
        }

        private async Task<AuditEvidenceRequestItem> GetEvidenceRequestItemAsync(int requestItemId)
        {
            using IDbConnection db = new NpgsqlConnection(_connectionString);
            db.Open();
            var query = @"
                SELECT
                    i.id AS Id,
                    i.request_id AS RequestId,
                    i.item_description AS ItemDescription,
                    i.expected_document_type AS ExpectedDocumentType,
                    i.is_required AS IsRequired,
                    i.fulfilled_document_id AS FulfilledDocumentId,
                    i.submitted_at AS SubmittedAt,
                    i.reviewer_notes AS ReviewerNotes,
                    i.reviewed_by_user_id AS ReviewedByUserId,
                    i.reviewed_at AS ReviewedAt,
                    i.is_accepted AS IsAccepted,
                    i.created_at AS CreatedAt,
                    d.document_code AS FulfilledDocumentCode,
                    d.title AS FulfilledDocumentTitle
                FROM audit_evidence_request_items i
                LEFT JOIN audit_documents d ON i.fulfilled_document_id = d.id
                WHERE i.id = @RequestItemId";
            return await db.QueryFirstOrDefaultAsync<AuditEvidenceRequestItem>(query, new { RequestItemId = requestItemId });
        }

        private async Task RefreshEvidenceRequestStatusAsync(NpgsqlConnection db, int requestId, NpgsqlTransaction transaction)
        {
            var summary = await db.QueryFirstOrDefaultAsync<(int TotalItems, int FulfilledItems, int AcceptedItems)>(@"
                SELECT
                    COUNT(*) AS TotalItems,
                    COUNT(CASE WHEN fulfilled_document_id IS NOT NULL THEN 1 END) AS FulfilledItems,
                    COUNT(CASE WHEN fulfilled_document_id IS NOT NULL AND is_accepted = true THEN 1 END) AS AcceptedItems
                FROM audit_evidence_request_items
                WHERE request_id = @RequestId", new { RequestId = requestId }, transaction);

            if (summary.TotalItems <= 0)
            {
                return;
            }

            var statusName = "In Progress";
            if (summary.AcceptedItems >= summary.TotalItems)
            {
                statusName = "Closed";
            }
            else if (summary.FulfilledItems >= summary.TotalItems)
            {
                statusName = "Fulfilled";
            }
            else if (summary.FulfilledItems > 0)
            {
                statusName = "Partially Fulfilled";
            }

            var updateRequest = @"
                UPDATE audit_evidence_requests
                SET
                    status_id = (
                        SELECT id
                        FROM ra_evidence_request_status
                        WHERE name = @StatusName
                        LIMIT 1
                    ),
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = @RequestId";

            await db.ExecuteAsync(updateRequest, new
            {
                RequestId = requestId,
                StatusName = statusName
            }, transaction);
        }
    }
}
