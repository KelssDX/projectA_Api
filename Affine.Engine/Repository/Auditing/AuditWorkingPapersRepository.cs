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
    public class AuditWorkingPapersRepository : IAuditWorkingPapersRepository
    {
        private readonly string _connectionString;

        private const string WorkingPaperSelect = @"
            SELECT
                wp.id AS Id,
                wp.reference_id AS ReferenceId,
                wp.audit_universe_id AS AuditUniverseId,
                wp.procedure_id AS ProcedureId,
                wp.working_paper_code AS WorkingPaperCode,
                wp.title AS Title,
                wp.objective AS Objective,
                wp.description AS Description,
                wp.status_id AS StatusId,
                wp.prepared_by AS PreparedBy,
                wp.prepared_by_user_id AS PreparedByUserId,
                wp.reviewer_name AS ReviewerName,
                wp.reviewer_user_id AS ReviewerUserId,
                wp.conclusion AS Conclusion,
                wp.notes AS Notes,
                wp.prepared_date AS PreparedDate,
                wp.reviewed_date AS ReviewedDate,
                wp.is_template AS IsTemplate,
                wp.source_template_id AS SourceTemplateId,
                wp.applicable_engagement_type_id AS ApplicableEngagementTypeId,
                aet.name AS ApplicableEngagementTypeName,
                wp.template_pack AS TemplatePack,
                wp.template_tags AS TemplateTags,
                wp.is_active AS IsActive,
                wp.created_at AS CreatedAt,
                wp.updated_at AS UpdatedAt,
                st.name AS StatusName,
                st.color AS StatusColor,
                p.procedure_title AS ProcedureTitle,
                au.name AS AuditUniverseName,
                (SELECT COUNT(*) FROM audit_working_paper_signoffs s WHERE s.working_paper_id = wp.id) AS SignOffCount,
                (SELECT COUNT(*) FROM audit_working_paper_references r WHERE r.from_working_paper_id = wp.id) AS ReferenceCount
            FROM audit_working_papers wp
            LEFT JOIN ra_working_paper_status st ON wp.status_id = st.id
            LEFT JOIN ra_engagement_type aet ON wp.applicable_engagement_type_id = aet.id
            LEFT JOIN audit_procedures p ON wp.procedure_id = p.id
            LEFT JOIN audit_universe au ON wp.audit_universe_id = au.id";

        public AuditWorkingPapersRepository(string connectionString)
        {
            _connectionString = connectionString ?? throw new ArgumentNullException(nameof(connectionString));
        }

        public async Task<AuditWorkingPaper> GetWorkingPaperAsync(int id)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();

                var query = $"{WorkingPaperSelect} WHERE wp.id = @Id";
                var result = await db.QueryFirstOrDefaultAsync<AuditWorkingPaper>(query, new { Id = id });
                if (result != null)
                {
                    result.SignOffHistory = await GetSignoffsAsync(id);
                    result.CrossReferences = await GetReferencesAsync(id);
                }
                return result;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in GetWorkingPaperAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<List<AuditWorkingPaper>> GetWorkingPapersByReferenceAsync(int referenceId)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();

                var query = $@"
                    {WorkingPaperSelect}
                    WHERE wp.reference_id = @ReferenceId
                      AND wp.is_template = false
                      AND wp.is_active = true
                    ORDER BY COALESCE(wp.reviewed_date, wp.prepared_date, wp.created_at) DESC, wp.title";

                var result = await db.QueryAsync<AuditWorkingPaper>(query, new { ReferenceId = referenceId });
                return result.ToList();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in GetWorkingPapersByReferenceAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<List<AuditWorkingPaper>> GetWorkingPaperTemplatesAsync(string? searchText = null, int? engagementTypeId = null)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();

                var query = $@"
                    {WorkingPaperSelect}
                    WHERE wp.is_template = true
                      AND wp.is_active = true
                      AND (@EngagementTypeId IS NULL OR wp.applicable_engagement_type_id IS NULL OR wp.applicable_engagement_type_id = @EngagementTypeId)
                      AND (@Search IS NULL OR LOWER(wp.title) LIKE LOWER(@Search) OR LOWER(COALESCE(wp.objective, '')) LIKE LOWER(@Search))
                    ORDER BY wp.title";

                var search = string.IsNullOrWhiteSpace(searchText) ? null : $"%{searchText.Trim()}%";
                var result = await db.QueryAsync<AuditWorkingPaper>(query, new { Search = search, EngagementTypeId = engagementTypeId });
                return result.ToList();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in GetWorkingPaperTemplatesAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<AuditWorkingPaper> CreateWorkingPaperAsync(CreateAuditWorkingPaperRequest request)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();

                var query = @"
                    INSERT INTO audit_working_papers
                    (
                        reference_id,
                        audit_universe_id,
                        procedure_id,
                        title,
                        objective,
                        description,
                        status_id,
                        prepared_by,
                        prepared_by_user_id,
                        reviewer_name,
                        reviewer_user_id,
                        conclusion,
                        notes,
                        prepared_date,
                        reviewed_date,
                        is_template,
                        applicable_engagement_type_id,
                        template_pack,
                        template_tags
                    )
                    VALUES
                    (
                        @ReferenceId,
                        @AuditUniverseId,
                        @ProcedureId,
                        @Title,
                        @Objective,
                        @Description,
                        COALESCE(@StatusId, 1),
                        @PreparedBy,
                        @PreparedByUserId,
                        @ReviewerName,
                        @ReviewerUserId,
                        @Conclusion,
                        @Notes,
                        @PreparedDate,
                        @ReviewedDate,
                        @IsTemplate,
                        @ApplicableEngagementTypeId,
                        @TemplatePack,
                        @TemplateTags
                    )
                    RETURNING id";

                var newId = await db.ExecuteScalarAsync<int>(query, request);
                return await GetWorkingPaperAsync(newId);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in CreateWorkingPaperAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<AuditWorkingPaper> UpdateWorkingPaperAsync(UpdateAuditWorkingPaperRequest request)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();

                var query = @"
                    UPDATE audit_working_papers
                    SET
                        procedure_id = @ProcedureId,
                        title = @Title,
                        objective = @Objective,
                        description = @Description,
                        status_id = @StatusId,
                        prepared_by = @PreparedBy,
                        prepared_by_user_id = @PreparedByUserId,
                        reviewer_name = @ReviewerName,
                        reviewer_user_id = @ReviewerUserId,
                        conclusion = @Conclusion,
                        notes = @Notes,
                        prepared_date = @PreparedDate,
                        reviewed_date = @ReviewedDate,
                        applicable_engagement_type_id = @ApplicableEngagementTypeId,
                        template_pack = @TemplatePack,
                        template_tags = @TemplateTags,
                        is_active = @IsActive
                    WHERE id = @Id";

                await db.ExecuteAsync(query, request);
                return await GetWorkingPaperAsync(request.Id);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in UpdateWorkingPaperAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<AuditWorkingPaper> CreateWorkingPaperFromTemplateAsync(CreateWorkingPaperFromTemplateRequest request)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();

                var query = @"
                    INSERT INTO audit_working_papers
                    (
                        reference_id,
                        audit_universe_id,
                        procedure_id,
                        title,
                        objective,
                        description,
                        status_id,
                        prepared_by,
                        prepared_by_user_id,
                        reviewer_name,
                        reviewer_user_id,
                        conclusion,
                        notes,
                        prepared_date,
                        is_template,
                        source_template_id,
                        applicable_engagement_type_id,
                        template_pack,
                        template_tags
                    )
                    SELECT
                        @ReferenceId,
                        COALESCE(@AuditUniverseId, wp.audit_universe_id),
                        COALESCE(@ProcedureId, wp.procedure_id),
                        wp.title,
                        wp.objective,
                        wp.description,
                        1,
                        @PreparedBy,
                        @PreparedByUserId,
                        wp.reviewer_name,
                        wp.reviewer_user_id,
                        wp.conclusion,
                        wp.notes,
                        CURRENT_DATE,
                        false,
                        wp.id,
                        wp.applicable_engagement_type_id,
                        wp.template_pack,
                        wp.template_tags
                    FROM audit_working_papers wp
                    WHERE wp.id = @TemplateId
                      AND wp.is_template = true
                      AND wp.is_active = true
                    RETURNING id";

                var newId = await db.ExecuteScalarAsync<int>(query, request);
                return await GetWorkingPaperAsync(newId);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in CreateWorkingPaperFromTemplateAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<bool> DeleteWorkingPaperAsync(int id)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();

                var query = "DELETE FROM audit_working_papers WHERE id = @Id";
                var affected = await db.ExecuteAsync(query, new { Id = id });
                return affected > 0;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in DeleteWorkingPaperAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<List<WorkingPaperStatus>> GetWorkingPaperStatusesAsync()
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
                    FROM ra_working_paper_status
                    WHERE is_active = true
                    ORDER BY sort_order, name";

                var result = await db.QueryAsync<WorkingPaperStatus>(query);
                return result.ToList();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in GetWorkingPaperStatusesAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<List<WorkingPaperSignoff>> GetSignoffsAsync(int workingPaperId)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();

                var query = @"
                    SELECT
                        id AS Id,
                        working_paper_id AS WorkingPaperId,
                        action_type AS ActionType,
                        signed_by_user_id AS SignedByUserId,
                        signed_by_name AS SignedByName,
                        comment AS Comment,
                        signed_at AS SignedAt
                    FROM audit_working_paper_signoffs
                    WHERE working_paper_id = @WorkingPaperId
                    ORDER BY signed_at DESC";

                var result = await db.QueryAsync<WorkingPaperSignoff>(query, new { WorkingPaperId = workingPaperId });
                return result.ToList();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in GetSignoffsAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<WorkingPaperSignoff> AddSignoffAsync(AddWorkingPaperSignoffRequest request)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();

                var insertQuery = @"
                    INSERT INTO audit_working_paper_signoffs
                    (
                        working_paper_id,
                        action_type,
                        signed_by_user_id,
                        signed_by_name,
                        comment
                    )
                    VALUES
                    (
                        @WorkingPaperId,
                        @ActionType,
                        @SignedByUserId,
                        @SignedByName,
                        @Comment
                    )
                    RETURNING id";

                var newId = await db.ExecuteScalarAsync<int>(insertQuery, request);

                var fetchQuery = @"
                    SELECT
                        id AS Id,
                        working_paper_id AS WorkingPaperId,
                        action_type AS ActionType,
                        signed_by_user_id AS SignedByUserId,
                        signed_by_name AS SignedByName,
                        comment AS Comment,
                        signed_at AS SignedAt
                    FROM audit_working_paper_signoffs
                    WHERE id = @Id";

                return await db.QueryFirstAsync<WorkingPaperSignoff>(fetchQuery, new { Id = newId });
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in AddSignoffAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<List<WorkingPaperReferenceLink>> GetReferencesAsync(int workingPaperId)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();

                var query = @"
                    SELECT
                        r.id AS Id,
                        r.from_working_paper_id AS FromWorkingPaperId,
                        r.to_working_paper_id AS ToWorkingPaperId,
                        r.reference_type AS ReferenceType,
                        r.notes AS Notes,
                        target.working_paper_code AS TargetWorkingPaperCode,
                        target.title AS TargetWorkingPaperTitle,
                        r.created_at AS CreatedAt
                    FROM audit_working_paper_references r
                    INNER JOIN audit_working_papers target ON r.to_working_paper_id = target.id
                    WHERE r.from_working_paper_id = @WorkingPaperId
                    ORDER BY r.created_at DESC";

                var result = await db.QueryAsync<WorkingPaperReferenceLink>(query, new { WorkingPaperId = workingPaperId });
                return result.ToList();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in GetReferencesAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<WorkingPaperReferenceLink> AddReferenceAsync(AddWorkingPaperReferenceRequest request)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();

                var insertQuery = @"
                    INSERT INTO audit_working_paper_references
                    (
                        from_working_paper_id,
                        to_working_paper_id,
                        reference_type,
                        notes
                    )
                    VALUES
                    (
                        @FromWorkingPaperId,
                        @ToWorkingPaperId,
                        @ReferenceType,
                        @Notes
                    )
                    RETURNING id";

                var newId = await db.ExecuteScalarAsync<int>(insertQuery, request);

                var fetchQuery = @"
                    SELECT
                        r.id AS Id,
                        r.from_working_paper_id AS FromWorkingPaperId,
                        r.to_working_paper_id AS ToWorkingPaperId,
                        r.reference_type AS ReferenceType,
                        r.notes AS Notes,
                        target.working_paper_code AS TargetWorkingPaperCode,
                        target.title AS TargetWorkingPaperTitle,
                        r.created_at AS CreatedAt
                    FROM audit_working_paper_references r
                    INNER JOIN audit_working_papers target ON r.to_working_paper_id = target.id
                    WHERE r.id = @Id";

                return await db.QueryFirstAsync<WorkingPaperReferenceLink>(fetchQuery, new { Id = newId });
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in AddReferenceAsync: {ex.Message}");
                throw;
            }
        }
    }
}
