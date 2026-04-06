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
    public class AuditExecutionRepository : IAuditExecutionRepository
    {
        private readonly string _connectionString;

        private const string PlanningSelect = @"
            SELECT
                p.id AS Id,
                p.reference_id AS ReferenceId,
                p.engagement_title AS EngagementTitle,
                p.engagement_type_id AS EngagementTypeId,
                et.name AS EngagementTypeName,
                p.plan_year AS PlanYear,
                p.annual_plan_name AS AnnualPlanName,
                p.business_unit AS BusinessUnit,
                p.process_area AS ProcessArea,
                p.subprocess_area AS SubProcessArea,
                p.fsli AS Fsli,
                p.scope_summary AS ScopeSummary,
                p.materiality AS Materiality,
                p.materiality_basis AS MaterialityBasis,
                p.overall_materiality AS OverallMateriality,
                p.performance_materiality AS PerformanceMateriality,
                p.clearly_trivial_threshold AS ClearlyTrivialThreshold,
                p.risk_strategy AS RiskStrategy,
                p.planning_status_id AS PlanningStatusId,
                ps.name AS PlanningStatusName,
                ps.color AS PlanningStatusColor,
                p.scope_letter_document_id AS ScopeLetterDocumentId,
                d.title AS ScopeLetterDocumentTitle,
                p.is_signed_off AS IsSignedOff,
                p.signed_off_by_name AS SignedOffByName,
                p.signed_off_by_user_id AS SignedOffByUserId,
                p.signed_off_at AS SignedOffAt,
                p.notes AS Notes,
                p.created_at AS CreatedAt,
                p.updated_at AS UpdatedAt
            FROM audit_engagement_plans p
            LEFT JOIN ra_engagement_type et ON p.engagement_type_id = et.id
            LEFT JOIN ra_planning_status ps ON p.planning_status_id = ps.id
            LEFT JOIN audit_documents d ON p.scope_letter_document_id = d.id";

        private const string ScopeItemSelect = @"
            SELECT
                si.id AS Id,
                si.plan_id AS PlanId,
                si.reference_id AS ReferenceId,
                si.business_unit AS BusinessUnit,
                si.process_name AS ProcessName,
                si.subprocess_name AS SubProcessName,
                si.fsli AS Fsli,
                si.assertions AS Assertions,
                si.scoping_rationale AS ScopingRationale,
                si.scope_status AS ScopeStatus,
                si.include_in_scope AS IncludeInScope,
                si.risk_reference AS RiskReference,
                si.control_reference AS ControlReference,
                si.procedure_id AS ProcedureId,
                p.procedure_title AS ProcedureTitle,
                si.owner AS Owner,
                si.notes AS Notes,
                si.created_at AS CreatedAt
            FROM audit_scope_items si
            LEFT JOIN audit_procedures p ON si.procedure_id = p.id";

        private const string RcmSelect = @"
            SELECT
                rcm.id AS Id,
                rcm.reference_id AS ReferenceId,
                rcm.scope_item_id AS ScopeItemId,
                rcm.procedure_id AS ProcedureId,
                rcm.risk_title AS RiskTitle,
                rcm.risk_description AS RiskDescription,
                rcm.control_name AS ControlName,
                rcm.control_description AS ControlDescription,
                rcm.control_adequacy AS ControlAdequacy,
                rcm.control_effectiveness AS ControlEffectiveness,
                rcm.control_classification_id AS ControlClassificationId,
                cc.name AS ControlClassificationName,
                rcm.control_type_id AS ControlTypeId,
                ct.name AS ControlTypeName,
                rcm.control_frequency_id AS ControlFrequencyId,
                cf.name AS ControlFrequencyName,
                rcm.control_owner AS ControlOwner,
                CASE
                    WHEN si.id IS NULL THEN NULL
                    ELSE CONCAT_WS(' / ', si.business_unit, si.process_name, si.subprocess_name, si.fsli)
                END AS ScopeItemLabel,
                p.procedure_title AS ProcedureTitle,
                rcm.notes AS Notes,
                rcm.created_at AS CreatedAt,
                rcm.updated_at AS UpdatedAt
            FROM audit_risk_control_matrix rcm
            LEFT JOIN audit_scope_items si ON rcm.scope_item_id = si.id
            LEFT JOIN audit_procedures p ON rcm.procedure_id = p.id
            LEFT JOIN ra_control_classification cc ON rcm.control_classification_id = cc.id
            LEFT JOIN ra_control_type ct ON rcm.control_type_id = ct.id
            LEFT JOIN ra_control_frequency cf ON rcm.control_frequency_id = cf.id";

        private const string WalkthroughSelect = @"
            SELECT
                w.id AS Id,
                w.reference_id AS ReferenceId,
                w.scope_item_id AS ScopeItemId,
                w.procedure_id AS ProcedureId,
                w.risk_control_matrix_id AS RiskControlMatrixId,
                w.process_name AS ProcessName,
                w.walkthrough_date AS WalkthroughDate,
                w.participants AS Participants,
                w.process_narrative AS ProcessNarrative,
                w.evidence_summary AS EvidenceSummary,
                w.control_design_conclusion AS ControlDesignConclusion,
                w.notes AS Notes,
                CASE
                    WHEN si.id IS NULL THEN NULL
                    ELSE CONCAT_WS(' / ', si.business_unit, si.process_name, si.subprocess_name, si.fsli)
                END AS ScopeItemLabel,
                p.procedure_title AS ProcedureTitle,
                rcm.risk_title AS RiskTitle,
                (SELECT COUNT(*) FROM audit_walkthrough_exceptions ex WHERE ex.walkthrough_id = w.id) AS ExceptionCount,
                w.created_at AS CreatedAt
            FROM audit_walkthroughs w
            LEFT JOIN audit_scope_items si ON w.scope_item_id = si.id
            LEFT JOIN audit_procedures p ON w.procedure_id = p.id
            LEFT JOIN audit_risk_control_matrix rcm ON w.risk_control_matrix_id = rcm.id";

        private const string ManagementActionSelect = @"
            SELECT
                ma.id AS Id,
                ma.reference_id AS ReferenceId,
                ma.finding_id AS FindingId,
                f.finding_number AS FindingNumber,
                f.title AS FindingTitle,
                ma.recommendation_id AS RecommendationId,
                r.recommendation_number AS RecommendationNumber,
                r.recommendation AS RecommendationText,
                ma.action_title AS ActionTitle,
                ma.action_description AS ActionDescription,
                ma.owner_name AS OwnerName,
                ma.owner_user_id AS OwnerUserId,
                ma.due_date AS DueDate,
                ma.status AS Status,
                ma.progress_percent AS ProgressPercent,
                ma.management_response AS ManagementResponse,
                ma.closure_notes AS ClosureNotes,
                ma.validated_by_name AS ValidatedByName,
                ma.validated_by_user_id AS ValidatedByUserId,
                ma.validated_at AS ValidatedAt,
                ma.created_at AS CreatedAt,
                ma.updated_at AS UpdatedAt,
                (
                    ma.due_date IS NOT NULL
                    AND COALESCE(LOWER(ma.status), 'open') NOT IN ('closed', 'validated', 'complete', 'completed')
                    AND ma.due_date < CURRENT_DATE
                ) AS IsOverdue
            FROM audit_management_actions ma
            LEFT JOIN audit_findings f ON ma.finding_id = f.id
            LEFT JOIN audit_recommendations r ON ma.recommendation_id = r.id";

        public AuditExecutionRepository(string connectionString)
        {
            _connectionString = connectionString ?? throw new ArgumentNullException(nameof(connectionString));
        }

        public async Task<AuditEngagementPlan> GetPlanningByReferenceAsync(int referenceId)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();
                return await db.QueryFirstOrDefaultAsync<AuditEngagementPlan>(
                    $"{PlanningSelect} WHERE p.reference_id = @ReferenceId",
                    new { ReferenceId = referenceId }
                );
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in GetPlanningByReferenceAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<AuditEngagementPlan> UpsertPlanningAsync(UpsertAuditEngagementPlanRequest request)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();

                var query = @"
                    INSERT INTO audit_engagement_plans
                    (
                        reference_id,
                        engagement_title,
                        engagement_type_id,
                        plan_year,
                        annual_plan_name,
                        business_unit,
                        process_area,
                        subprocess_area,
                        fsli,
                        scope_summary,
                        materiality,
                        materiality_basis,
                        overall_materiality,
                        performance_materiality,
                        clearly_trivial_threshold,
                        risk_strategy,
                        planning_status_id,
                        scope_letter_document_id,
                        is_signed_off,
                        signed_off_by_name,
                        signed_off_by_user_id,
                        signed_off_at,
                        notes
                    )
                    VALUES
                    (
                        @ReferenceId,
                        @EngagementTitle,
                        @EngagementTypeId,
                        @PlanYear,
                        @AnnualPlanName,
                        @BusinessUnit,
                        @ProcessArea,
                        @SubProcessArea,
                        @Fsli,
                        @ScopeSummary,
                        @Materiality,
                        @MaterialityBasis,
                        @OverallMateriality,
                        @PerformanceMateriality,
                        @ClearlyTrivialThreshold,
                        @RiskStrategy,
                        COALESCE(@PlanningStatusId, 1),
                        @ScopeLetterDocumentId,
                        @IsSignedOff,
                        @SignedOffByName,
                        @SignedOffByUserId,
                        @SignedOffAt,
                        @Notes
                    )
                    ON CONFLICT (reference_id)
                    DO UPDATE SET
                        engagement_title = EXCLUDED.engagement_title,
                        engagement_type_id = EXCLUDED.engagement_type_id,
                        plan_year = EXCLUDED.plan_year,
                        annual_plan_name = EXCLUDED.annual_plan_name,
                        business_unit = EXCLUDED.business_unit,
                        process_area = EXCLUDED.process_area,
                        subprocess_area = EXCLUDED.subprocess_area,
                        fsli = EXCLUDED.fsli,
                        scope_summary = EXCLUDED.scope_summary,
                        materiality = EXCLUDED.materiality,
                        materiality_basis = EXCLUDED.materiality_basis,
                        overall_materiality = EXCLUDED.overall_materiality,
                        performance_materiality = EXCLUDED.performance_materiality,
                        clearly_trivial_threshold = EXCLUDED.clearly_trivial_threshold,
                        risk_strategy = EXCLUDED.risk_strategy,
                        planning_status_id = COALESCE(EXCLUDED.planning_status_id, audit_engagement_plans.planning_status_id),
                        scope_letter_document_id = EXCLUDED.scope_letter_document_id,
                        is_signed_off = EXCLUDED.is_signed_off,
                        signed_off_by_name = EXCLUDED.signed_off_by_name,
                        signed_off_by_user_id = EXCLUDED.signed_off_by_user_id,
                        signed_off_at = EXCLUDED.signed_off_at,
                        notes = EXCLUDED.notes
                    RETURNING id";

                var id = await db.ExecuteScalarAsync<int>(query, request);
                return await db.QueryFirstOrDefaultAsync<AuditEngagementPlan>($"{PlanningSelect} WHERE p.id = @Id", new { Id = id });
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in UpsertPlanningAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<List<EngagementTypeOption>> GetEngagementTypesAsync()
        {
            return await GetLookupAsync<EngagementTypeOption>("ra_engagement_type");
        }

        public async Task<List<PlanningStatusOption>> GetPlanningStatusesAsync()
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
                        is_closed AS IsClosed,
                        is_active AS IsActive
                    FROM ra_planning_status
                    WHERE is_active = true
                    ORDER BY sort_order, name";
                var result = await db.QueryAsync<PlanningStatusOption>(query);
                return result.ToList();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in GetPlanningStatusesAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<List<AuditScopeItem>> GetScopeItemsByReferenceAsync(int referenceId)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();
                var query = $@"
                    {ScopeItemSelect}
                    WHERE si.reference_id = @ReferenceId
                    ORDER BY si.id DESC";
                var result = await db.QueryAsync<AuditScopeItem>(query, new { ReferenceId = referenceId });
                return result.ToList();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in GetScopeItemsByReferenceAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<AuditScopeItem> CreateScopeItemAsync(CreateAuditScopeItemRequest request)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();
                var query = @"
                    INSERT INTO audit_scope_items
                    (
                        plan_id,
                        reference_id,
                        business_unit,
                        process_name,
                        subprocess_name,
                        fsli,
                        assertions,
                        scoping_rationale,
                        scope_status,
                        include_in_scope,
                        risk_reference,
                        control_reference,
                        procedure_id,
                        owner,
                        notes
                    )
                    VALUES
                    (
                        @PlanId,
                        @ReferenceId,
                        @BusinessUnit,
                        @ProcessName,
                        @SubProcessName,
                        @Fsli,
                        @Assertions,
                        @ScopingRationale,
                        @ScopeStatus,
                        @IncludeInScope,
                        @RiskReference,
                        @ControlReference,
                        @ProcedureId,
                        @Owner,
                        @Notes
                    )
                    RETURNING id";
                var id = await db.ExecuteScalarAsync<int>(query, request);
                return await db.QueryFirstOrDefaultAsync<AuditScopeItem>($"{ScopeItemSelect} WHERE si.id = @Id", new { Id = id });
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in CreateScopeItemAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<AuditScopeItem> UpdateScopeItemAsync(UpdateAuditScopeItemRequest request)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();
                var query = @"
                    UPDATE audit_scope_items
                    SET
                        business_unit = @BusinessUnit,
                        process_name = @ProcessName,
                        subprocess_name = @SubProcessName,
                        fsli = @Fsli,
                        assertions = @Assertions,
                        scoping_rationale = @ScopingRationale,
                        scope_status = @ScopeStatus,
                        include_in_scope = @IncludeInScope,
                        risk_reference = @RiskReference,
                        control_reference = @ControlReference,
                        procedure_id = @ProcedureId,
                        owner = @Owner,
                        notes = @Notes
                    WHERE id = @Id";
                await db.ExecuteAsync(query, request);
                return await db.QueryFirstOrDefaultAsync<AuditScopeItem>($"{ScopeItemSelect} WHERE si.id = @Id", new { Id = request.Id });
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in UpdateScopeItemAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<bool> DeleteScopeItemAsync(int id)
        {
            using IDbConnection db = new NpgsqlConnection(_connectionString);
            db.Open();
            return await db.ExecuteAsync("DELETE FROM audit_scope_items WHERE id = @Id", new { Id = id }) > 0;
        }

        public async Task<List<RiskControlMatrixEntry>> GetRiskControlMatrixByReferenceAsync(int referenceId)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();
                var query = $@"
                    {RcmSelect}
                    WHERE rcm.reference_id = @ReferenceId
                    ORDER BY rcm.id DESC";
                var result = await db.QueryAsync<RiskControlMatrixEntry>(query, new { ReferenceId = referenceId });
                return result.ToList();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in GetRiskControlMatrixByReferenceAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<RiskControlMatrixEntry> CreateRiskControlMatrixEntryAsync(CreateRiskControlMatrixEntryRequest request)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();
                var query = @"
                    INSERT INTO audit_risk_control_matrix
                    (
                        reference_id,
                        scope_item_id,
                        procedure_id,
                        risk_title,
                        risk_description,
                        control_name,
                        control_description,
                        control_adequacy,
                        control_effectiveness,
                        control_classification_id,
                        control_type_id,
                        control_frequency_id,
                        control_owner,
                        notes
                    )
                    VALUES
                    (
                        @ReferenceId,
                        @ScopeItemId,
                        @ProcedureId,
                        @RiskTitle,
                        @RiskDescription,
                        @ControlName,
                        @ControlDescription,
                        @ControlAdequacy,
                        @ControlEffectiveness,
                        @ControlClassificationId,
                        @ControlTypeId,
                        @ControlFrequencyId,
                        @ControlOwner,
                        @Notes
                    )
                    RETURNING id";
                var id = await db.ExecuteScalarAsync<int>(query, request);
                return await db.QueryFirstOrDefaultAsync<RiskControlMatrixEntry>($"{RcmSelect} WHERE rcm.id = @Id", new { Id = id });
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in CreateRiskControlMatrixEntryAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<RiskControlMatrixEntry> UpdateRiskControlMatrixEntryAsync(UpdateRiskControlMatrixEntryRequest request)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();
                var query = @"
                    UPDATE audit_risk_control_matrix
                    SET
                        scope_item_id = @ScopeItemId,
                        procedure_id = @ProcedureId,
                        risk_title = @RiskTitle,
                        risk_description = @RiskDescription,
                        control_name = @ControlName,
                        control_description = @ControlDescription,
                        control_adequacy = @ControlAdequacy,
                        control_effectiveness = @ControlEffectiveness,
                        control_classification_id = @ControlClassificationId,
                        control_type_id = @ControlTypeId,
                        control_frequency_id = @ControlFrequencyId,
                        control_owner = @ControlOwner,
                        notes = @Notes
                    WHERE id = @Id";
                await db.ExecuteAsync(query, request);
                return await db.QueryFirstOrDefaultAsync<RiskControlMatrixEntry>($"{RcmSelect} WHERE rcm.id = @Id", new { Id = request.Id });
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in UpdateRiskControlMatrixEntryAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<bool> DeleteRiskControlMatrixEntryAsync(int id)
        {
            using IDbConnection db = new NpgsqlConnection(_connectionString);
            db.Open();
            return await db.ExecuteAsync("DELETE FROM audit_risk_control_matrix WHERE id = @Id", new { Id = id }) > 0;
        }

        public async Task<List<ControlClassificationOption>> GetControlClassificationsAsync()
        {
            return await GetLookupAsync<ControlClassificationOption>("ra_control_classification");
        }

        public async Task<List<ControlTypeOption>> GetControlTypesAsync()
        {
            return await GetLookupAsync<ControlTypeOption>("ra_control_type");
        }

        public async Task<List<ControlFrequencyOption>> GetControlFrequenciesAsync()
        {
            return await GetLookupAsync<ControlFrequencyOption>("ra_control_frequency");
        }

        public async Task<List<AuditWalkthrough>> GetWalkthroughsByReferenceAsync(int referenceId)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();
                var query = $@"
                    {WalkthroughSelect}
                    WHERE w.reference_id = @ReferenceId
                    ORDER BY COALESCE(w.walkthrough_date, w.created_at) DESC, w.process_name";
                var result = (await db.QueryAsync<AuditWalkthrough>(query, new { ReferenceId = referenceId })).ToList();
                foreach (var walkthrough in result)
                {
                    walkthrough.Exceptions = await GetWalkthroughExceptionsAsync(db, walkthrough.Id);
                }
                return result;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in GetWalkthroughsByReferenceAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<AuditWalkthrough> CreateWalkthroughAsync(CreateAuditWalkthroughRequest request)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();
                var query = @"
                    INSERT INTO audit_walkthroughs
                    (
                        reference_id,
                        scope_item_id,
                        procedure_id,
                        risk_control_matrix_id,
                        process_name,
                        walkthrough_date,
                        participants,
                        process_narrative,
                        evidence_summary,
                        control_design_conclusion,
                        notes
                    )
                    VALUES
                    (
                        @ReferenceId,
                        @ScopeItemId,
                        @ProcedureId,
                        @RiskControlMatrixId,
                        @ProcessName,
                        @WalkthroughDate,
                        @Participants,
                        @ProcessNarrative,
                        @EvidenceSummary,
                        @ControlDesignConclusion,
                        @Notes
                    )
                    RETURNING id";
                var id = await db.ExecuteScalarAsync<int>(query, request);
                return await GetWalkthroughAsync(id);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in CreateWalkthroughAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<AuditWalkthrough> UpdateWalkthroughAsync(UpdateAuditWalkthroughRequest request)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();
                var query = @"
                    UPDATE audit_walkthroughs
                    SET
                        scope_item_id = @ScopeItemId,
                        procedure_id = @ProcedureId,
                        risk_control_matrix_id = @RiskControlMatrixId,
                        process_name = @ProcessName,
                        walkthrough_date = @WalkthroughDate,
                        participants = @Participants,
                        process_narrative = @ProcessNarrative,
                        evidence_summary = @EvidenceSummary,
                        control_design_conclusion = @ControlDesignConclusion,
                        notes = @Notes
                    WHERE id = @Id";
                await db.ExecuteAsync(query, request);
                return await GetWalkthroughAsync(request.Id);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in UpdateWalkthroughAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<bool> DeleteWalkthroughAsync(int id)
        {
            using IDbConnection db = new NpgsqlConnection(_connectionString);
            db.Open();
            return await db.ExecuteAsync("DELETE FROM audit_walkthroughs WHERE id = @Id", new { Id = id }) > 0;
        }

        public async Task<AuditWalkthroughException> AddWalkthroughExceptionAsync(AddWalkthroughExceptionRequest request)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();
                var query = @"
                    INSERT INTO audit_walkthrough_exceptions
                    (
                        walkthrough_id,
                        exception_title,
                        exception_description,
                        severity,
                        linked_finding_id,
                        is_resolved
                    )
                    VALUES
                    (
                        @WalkthroughId,
                        @ExceptionTitle,
                        @ExceptionDescription,
                        @Severity,
                        @LinkedFindingId,
                        @IsResolved
                    )
                    RETURNING id";
                var id = await db.ExecuteScalarAsync<int>(query, request);
                return await GetWalkthroughExceptionAsync(id);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in AddWalkthroughExceptionAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<List<AuditManagementAction>> GetManagementActionsByReferenceAsync(int referenceId)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();
                var query = $@"
                    {ManagementActionSelect}
                    WHERE ma.reference_id = @ReferenceId
                    ORDER BY
                        CASE
                            WHEN ma.due_date IS NULL THEN 1
                            ELSE 0
                        END,
                        ma.due_date,
                        ma.id DESC";
                var result = await db.QueryAsync<AuditManagementAction>(query, new { ReferenceId = referenceId });
                return result.ToList();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in GetManagementActionsByReferenceAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<AuditManagementAction> CreateManagementActionAsync(CreateAuditManagementActionRequest request)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();
                var query = @"
                    INSERT INTO audit_management_actions
                    (
                        reference_id,
                        finding_id,
                        recommendation_id,
                        action_title,
                        action_description,
                        owner_name,
                        owner_user_id,
                        due_date,
                        status,
                        progress_percent,
                        management_response,
                        closure_notes,
                        validated_by_name,
                        validated_by_user_id,
                        validated_at
                    )
                    VALUES
                    (
                        @ReferenceId,
                        @FindingId,
                        @RecommendationId,
                        @ActionTitle,
                        @ActionDescription,
                        @OwnerName,
                        @OwnerUserId,
                        @DueDate,
                        COALESCE(@Status, 'Open'),
                        COALESCE(@ProgressPercent, 0),
                        @ManagementResponse,
                        @ClosureNotes,
                        @ValidatedByName,
                        @ValidatedByUserId,
                        @ValidatedAt
                    )
                    RETURNING id";
                var id = await db.ExecuteScalarAsync<int>(query, request);
                return await GetManagementActionAsync(id);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in CreateManagementActionAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<AuditManagementAction> UpdateManagementActionAsync(UpdateAuditManagementActionRequest request)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();
                var query = @"
                    UPDATE audit_management_actions
                    SET
                        finding_id = @FindingId,
                        recommendation_id = @RecommendationId,
                        action_title = @ActionTitle,
                        action_description = @ActionDescription,
                        owner_name = @OwnerName,
                        owner_user_id = @OwnerUserId,
                        due_date = @DueDate,
                        status = COALESCE(@Status, status),
                        progress_percent = COALESCE(@ProgressPercent, progress_percent),
                        management_response = @ManagementResponse,
                        closure_notes = @ClosureNotes,
                        validated_by_name = @ValidatedByName,
                        validated_by_user_id = @ValidatedByUserId,
                        validated_at = @ValidatedAt,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = @Id";
                await db.ExecuteAsync(query, request);
                return await GetManagementActionAsync(request.Id);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in UpdateManagementActionAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<bool> DeleteManagementActionAsync(int id)
        {
            using IDbConnection db = new NpgsqlConnection(_connectionString);
            db.Open();
            return await db.ExecuteAsync("DELETE FROM audit_management_actions WHERE id = @Id", new { Id = id }) > 0;
        }

        private async Task<AuditWalkthrough> GetWalkthroughAsync(int id)
        {
            using IDbConnection db = new NpgsqlConnection(_connectionString);
            db.Open();
            var walkthrough = await db.QueryFirstOrDefaultAsync<AuditWalkthrough>($"{WalkthroughSelect} WHERE w.id = @Id", new { Id = id });
            if (walkthrough != null)
            {
                walkthrough.Exceptions = await GetWalkthroughExceptionsAsync(db, id);
            }
            return walkthrough;
        }

        private async Task<AuditWalkthroughException> GetWalkthroughExceptionAsync(int id)
        {
            using IDbConnection db = new NpgsqlConnection(_connectionString);
            db.Open();
            return await db.QueryFirstOrDefaultAsync<AuditWalkthroughException>(@"
                SELECT
                    ex.id AS Id,
                    ex.walkthrough_id AS WalkthroughId,
                    ex.exception_title AS ExceptionTitle,
                    ex.exception_description AS ExceptionDescription,
                    ex.severity AS Severity,
                    ex.linked_finding_id AS LinkedFindingId,
                    f.finding_number AS LinkedFindingNumber,
                    ex.is_resolved AS IsResolved,
                    ex.created_at AS CreatedAt
                FROM audit_walkthrough_exceptions ex
                LEFT JOIN audit_findings f ON ex.linked_finding_id = f.id
                WHERE ex.id = @Id", new { Id = id });
        }

        private async Task<AuditManagementAction> GetManagementActionAsync(int id)
        {
            using IDbConnection db = new NpgsqlConnection(_connectionString);
            db.Open();
            return await db.QueryFirstOrDefaultAsync<AuditManagementAction>(
                $"{ManagementActionSelect} WHERE ma.id = @Id",
                new { Id = id }
            );
        }

        private async Task<List<AuditWalkthroughException>> GetWalkthroughExceptionsAsync(IDbConnection db, int walkthroughId)
        {
            var query = @"
                SELECT
                    ex.id AS Id,
                    ex.walkthrough_id AS WalkthroughId,
                    ex.exception_title AS ExceptionTitle,
                    ex.exception_description AS ExceptionDescription,
                    ex.severity AS Severity,
                    ex.linked_finding_id AS LinkedFindingId,
                    f.finding_number AS LinkedFindingNumber,
                    ex.is_resolved AS IsResolved,
                    ex.created_at AS CreatedAt
                FROM audit_walkthrough_exceptions ex
                LEFT JOIN audit_findings f ON ex.linked_finding_id = f.id
                WHERE ex.walkthrough_id = @WalkthroughId
                ORDER BY ex.id DESC";
            var result = await db.QueryAsync<AuditWalkthroughException>(query, new { WalkthroughId = walkthroughId });
            return result.ToList();
        }

        private async Task<List<T>> GetLookupAsync<T>(string tableName)
        {
            using IDbConnection db = new NpgsqlConnection(_connectionString);
            db.Open();
            var query = $@"
                SELECT
                    id AS Id,
                    name AS Name,
                    description AS Description,
                    sort_order AS SortOrder,
                    is_active AS IsActive
                FROM {tableName}
                WHERE is_active = true
                ORDER BY sort_order, name";
            var result = await db.QueryAsync<T>(query);
            return result.ToList();
        }
    }
}
