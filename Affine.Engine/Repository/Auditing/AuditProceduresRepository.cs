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
    public class AuditProceduresRepository : IAuditProceduresRepository
    {
        private readonly string _connectionString;

        public AuditProceduresRepository(string connectionString)
        {
            _connectionString = connectionString ?? throw new ArgumentNullException(nameof(connectionString));
        }

        public async Task<AuditProcedure> GetProcedureAsync(int id)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();

                var query = @"
                    SELECT
                        p.id AS Id,
                        p.reference_id AS ReferenceId,
                        p.audit_universe_id AS AuditUniverseId,
                        p.procedure_code AS ProcedureCode,
                        p.procedure_title AS ProcedureTitle,
                        p.objective AS Objective,
                        p.procedure_description AS ProcedureDescription,
                        p.procedure_type_id AS ProcedureTypeId,
                        p.status_id AS StatusId,
                        p.sample_size AS SampleSize,
                        p.expected_evidence AS ExpectedEvidence,
                        p.working_paper_ref AS WorkingPaperRef,
                        p.owner AS Owner,
                        p.performer_user_id AS PerformerUserId,
                        p.reviewer_user_id AS ReviewerUserId,
                        p.planned_date AS PlannedDate,
                        p.performed_date AS PerformedDate,
                        p.reviewed_date AS ReviewedDate,
                        p.conclusion AS Conclusion,
                        p.notes AS Notes,
                        p.is_template AS IsTemplate,
                        p.source_template_id AS SourceTemplateId,
                        p.applicable_engagement_type_id AS ApplicableEngagementTypeId,
                        aet.name AS ApplicableEngagementTypeName,
                        p.template_pack AS TemplatePack,
                        p.template_tags AS TemplateTags,
                        p.created_by_user_id AS CreatedByUserId,
                        p.is_active AS IsActive,
                        p.created_at AS CreatedAt,
                        p.updated_at AS UpdatedAt,
                        pt.name AS ProcedureTypeName,
                        pt.color AS ProcedureTypeColor,
                        ps.name AS StatusName,
                        ps.color AS StatusColor,
                        au.name AS AuditUniverseName,
                        (p.planned_date IS NOT NULL AND p.performed_date IS NULL AND p.planned_date < CURRENT_DATE AND COALESCE(ps.is_closed, false) = false) AS IsOverdue,
                        CASE
                            WHEN p.planned_date IS NOT NULL AND p.performed_date IS NULL AND p.planned_date < CURRENT_DATE AND COALESCE(ps.is_closed, false) = false
                            THEN (CURRENT_DATE - p.planned_date)
                            ELSE NULL
                        END AS DaysPastPlanned
                    FROM audit_procedures p
                    LEFT JOIN ra_procedure_type pt ON p.procedure_type_id = pt.id
                    LEFT JOIN ra_procedure_status ps ON p.status_id = ps.id
                    LEFT JOIN ra_engagement_type aet ON p.applicable_engagement_type_id = aet.id
                    LEFT JOIN audit_universe au ON p.audit_universe_id = au.id
                    WHERE p.id = @Id";

                return await db.QueryFirstOrDefaultAsync<AuditProcedure>(query, new { Id = id });
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in GetProcedureAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<List<AuditProcedure>> GetProceduresByReferenceAsync(int referenceId)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();

                var query = @"
                    SELECT
                        p.id AS Id,
                        p.reference_id AS ReferenceId,
                        p.audit_universe_id AS AuditUniverseId,
                        p.procedure_code AS ProcedureCode,
                        p.procedure_title AS ProcedureTitle,
                        p.objective AS Objective,
                        p.procedure_description AS ProcedureDescription,
                        p.procedure_type_id AS ProcedureTypeId,
                        p.status_id AS StatusId,
                        p.sample_size AS SampleSize,
                        p.expected_evidence AS ExpectedEvidence,
                        p.working_paper_ref AS WorkingPaperRef,
                        p.owner AS Owner,
                        p.performer_user_id AS PerformerUserId,
                        p.reviewer_user_id AS ReviewerUserId,
                        p.planned_date AS PlannedDate,
                        p.performed_date AS PerformedDate,
                        p.reviewed_date AS ReviewedDate,
                        p.conclusion AS Conclusion,
                        p.notes AS Notes,
                        p.is_template AS IsTemplate,
                        p.source_template_id AS SourceTemplateId,
                        p.applicable_engagement_type_id AS ApplicableEngagementTypeId,
                        aet.name AS ApplicableEngagementTypeName,
                        p.template_pack AS TemplatePack,
                        p.template_tags AS TemplateTags,
                        p.created_by_user_id AS CreatedByUserId,
                        p.is_active AS IsActive,
                        p.created_at AS CreatedAt,
                        p.updated_at AS UpdatedAt,
                        pt.name AS ProcedureTypeName,
                        pt.color AS ProcedureTypeColor,
                        ps.name AS StatusName,
                        ps.color AS StatusColor,
                        au.name AS AuditUniverseName,
                        (p.planned_date IS NOT NULL AND p.performed_date IS NULL AND p.planned_date < CURRENT_DATE AND COALESCE(ps.is_closed, false) = false) AS IsOverdue,
                        CASE
                            WHEN p.planned_date IS NOT NULL AND p.performed_date IS NULL AND p.planned_date < CURRENT_DATE AND COALESCE(ps.is_closed, false) = false
                            THEN (CURRENT_DATE - p.planned_date)
                            ELSE NULL
                        END AS DaysPastPlanned
                    FROM audit_procedures p
                    LEFT JOIN ra_procedure_type pt ON p.procedure_type_id = pt.id
                    LEFT JOIN ra_procedure_status ps ON p.status_id = ps.id
                    LEFT JOIN ra_engagement_type aet ON p.applicable_engagement_type_id = aet.id
                    LEFT JOIN audit_universe au ON p.audit_universe_id = au.id
                    WHERE p.reference_id = @ReferenceId
                      AND p.is_template = false
                      AND p.is_active = true
                    ORDER BY COALESCE(p.planned_date, p.created_at) DESC, p.procedure_title";

                var result = await db.QueryAsync<AuditProcedure>(query, new { ReferenceId = referenceId });
                return result.ToList();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in GetProceduresByReferenceAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<List<AuditProcedure>> GetLibraryProceduresAsync(string? searchText = null, int? engagementTypeId = null)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();

                var query = @"
                    SELECT
                        p.id AS Id,
                        p.procedure_code AS ProcedureCode,
                        p.procedure_title AS ProcedureTitle,
                        p.objective AS Objective,
                        p.procedure_description AS ProcedureDescription,
                        p.procedure_type_id AS ProcedureTypeId,
                        p.sample_size AS SampleSize,
                        p.expected_evidence AS ExpectedEvidence,
                        p.working_paper_ref AS WorkingPaperRef,
                        p.owner AS Owner,
                        p.notes AS Notes,
                        p.is_template AS IsTemplate,
                        p.applicable_engagement_type_id AS ApplicableEngagementTypeId,
                        aet.name AS ApplicableEngagementTypeName,
                        p.template_pack AS TemplatePack,
                        p.template_tags AS TemplateTags,
                        p.is_active AS IsActive,
                        p.created_at AS CreatedAt,
                        p.updated_at AS UpdatedAt,
                        pt.name AS ProcedureTypeName,
                        pt.color AS ProcedureTypeColor,
                        ps.name AS StatusName,
                        ps.color AS StatusColor
                    FROM audit_procedures p
                    LEFT JOIN ra_procedure_type pt ON p.procedure_type_id = pt.id
                    LEFT JOIN ra_procedure_status ps ON p.status_id = ps.id
                    LEFT JOIN ra_engagement_type aet ON p.applicable_engagement_type_id = aet.id
                    WHERE p.is_template = true
                      AND p.is_active = true
                      AND (@EngagementTypeId IS NULL OR p.applicable_engagement_type_id IS NULL OR p.applicable_engagement_type_id = @EngagementTypeId)
                      AND (@Search IS NULL OR LOWER(p.procedure_title) LIKE LOWER(@Search) OR LOWER(COALESCE(p.objective, '')) LIKE LOWER(@Search))
                    ORDER BY pt.sort_order NULLS LAST, p.procedure_title";

                var search = string.IsNullOrWhiteSpace(searchText) ? null : $"%{searchText.Trim()}%";
                var result = await db.QueryAsync<AuditProcedure>(query, new { Search = search, EngagementTypeId = engagementTypeId });
                return result.ToList();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in GetLibraryProceduresAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<AuditProcedure> CreateProcedureAsync(CreateAuditProcedureRequest request)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();

                var query = @"
                    INSERT INTO audit_procedures
                    (
                        reference_id,
                        audit_universe_id,
                        procedure_title,
                        objective,
                        procedure_description,
                        procedure_type_id,
                        status_id,
                        sample_size,
                        expected_evidence,
                        working_paper_ref,
                        owner,
                        performer_user_id,
                        reviewer_user_id,
                        planned_date,
                        performed_date,
                        reviewed_date,
                        conclusion,
                        notes,
                        is_template,
                        applicable_engagement_type_id,
                        template_pack,
                        template_tags,
                        created_by_user_id
                    )
                    VALUES
                    (
                        @ReferenceId,
                        @AuditUniverseId,
                        @ProcedureTitle,
                        @Objective,
                        @ProcedureDescription,
                        @ProcedureTypeId,
                        COALESCE(@StatusId, 1),
                        @SampleSize,
                        @ExpectedEvidence,
                        @WorkingPaperRef,
                        @Owner,
                        @PerformerUserId,
                        @ReviewerUserId,
                        @PlannedDate,
                        @PerformedDate,
                        @ReviewedDate,
                        @Conclusion,
                        @Notes,
                        @IsTemplate,
                        @ApplicableEngagementTypeId,
                        @TemplatePack,
                        @TemplateTags,
                        @CreatedByUserId
                    )
                    RETURNING id";

                var newId = await db.ExecuteScalarAsync<int>(query, request);
                return await GetProcedureAsync(newId);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in CreateProcedureAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<AuditProcedure> UpdateProcedureAsync(UpdateAuditProcedureRequest request)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();

                var query = @"
                    UPDATE audit_procedures
                    SET
                        procedure_title = @ProcedureTitle,
                        objective = @Objective,
                        procedure_description = @ProcedureDescription,
                        procedure_type_id = @ProcedureTypeId,
                        status_id = @StatusId,
                        sample_size = @SampleSize,
                        expected_evidence = @ExpectedEvidence,
                        working_paper_ref = @WorkingPaperRef,
                        owner = @Owner,
                        performer_user_id = @PerformerUserId,
                        reviewer_user_id = @ReviewerUserId,
                        planned_date = @PlannedDate,
                        performed_date = @PerformedDate,
                        reviewed_date = @ReviewedDate,
                        conclusion = @Conclusion,
                        notes = @Notes,
                        applicable_engagement_type_id = @ApplicableEngagementTypeId,
                        template_pack = @TemplatePack,
                        template_tags = @TemplateTags,
                        is_active = @IsActive
                    WHERE id = @Id";

                await db.ExecuteAsync(query, request);
                return await GetProcedureAsync(request.Id);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in UpdateProcedureAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<AuditProcedure> CreateProcedureFromTemplateAsync(CreateProcedureFromTemplateRequest request)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();

                var query = @"
                    INSERT INTO audit_procedures
                    (
                        reference_id,
                        audit_universe_id,
                        procedure_title,
                        objective,
                        procedure_description,
                        procedure_type_id,
                        status_id,
                        sample_size,
                        expected_evidence,
                        working_paper_ref,
                        owner,
                        planned_date,
                        notes,
                        is_template,
                        source_template_id,
                        applicable_engagement_type_id,
                        template_pack,
                        template_tags,
                        created_by_user_id
                    )
                    SELECT
                        @ReferenceId,
                        COALESCE(@AuditUniverseId, p.audit_universe_id),
                        p.procedure_title,
                        p.objective,
                        p.procedure_description,
                        p.procedure_type_id,
                        1,
                        p.sample_size,
                        p.expected_evidence,
                        NULL,
                        p.owner,
                        @PlannedDate,
                        p.notes,
                        false,
                        p.id,
                        p.applicable_engagement_type_id,
                        p.template_pack,
                        p.template_tags,
                        @CreatedByUserId
                    FROM audit_procedures p
                    WHERE p.id = @TemplateId
                      AND p.is_template = true
                      AND p.is_active = true
                    RETURNING id";

                var newId = await db.ExecuteScalarAsync<int>(query, request);
                return await GetProcedureAsync(newId);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in CreateProcedureFromTemplateAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<bool> DeleteProcedureAsync(int id)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();

                var query = "DELETE FROM audit_procedures WHERE id = @Id";
                var affected = await db.ExecuteAsync(query, new { Id = id });
                return affected > 0;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in DeleteProcedureAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<List<ProcedureType>> GetProcedureTypesAsync()
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
                        is_active AS IsActive
                    FROM ra_procedure_type
                    WHERE is_active = true
                    ORDER BY sort_order, name";

                var result = await db.QueryAsync<ProcedureType>(query);
                return result.ToList();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in GetProcedureTypesAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<List<ProcedureStatus>> GetProcedureStatusesAsync()
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
                    FROM ra_procedure_status
                    WHERE is_active = true
                    ORDER BY sort_order, name";

                var result = await db.QueryAsync<ProcedureStatus>(query);
                return result.ToList();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in GetProcedureStatusesAsync: {ex.Message}");
                throw;
            }
        }
    }
}
