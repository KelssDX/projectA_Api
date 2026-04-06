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
    public class AuditMaterialityRepository : IAuditMaterialityRepository
    {
        private readonly string _connectionString;

        private const string CalculationSelect = @"
            SELECT
                calc.id AS Id,
                calc.reference_id AS ReferenceId,
                calc.fiscal_year AS FiscalYear,
                calc.candidate_id AS CandidateId,
                calc.benchmark_profile_id AS BenchmarkProfileId,
                profile.profile_name AS BenchmarkProfileName,
                profile.validation_status AS BenchmarkProfileValidationStatus,
                calc.benchmark_code AS BenchmarkCode,
                calc.benchmark_name AS BenchmarkName,
                calc.benchmark_source AS BenchmarkSource,
                calc.source_table AS SourceTable,
                calc.benchmark_amount AS BenchmarkAmount,
                calc.percentage_applied AS PercentageApplied,
                calc.overall_materiality AS OverallMateriality,
                calc.performance_percentage_applied AS PerformancePercentageApplied,
                calc.performance_materiality AS PerformanceMateriality,
                calc.clearly_trivial_percentage_applied AS ClearlyTrivialPercentageApplied,
                calc.clearly_trivial_threshold AS ClearlyTrivialThreshold,
                calc.calculation_summary AS CalculationSummary,
                calc.rationale AS Rationale,
                calc.entity_type AS EntityType,
                calc.industry_name AS IndustryName,
                calc.benchmark_selection_rationale AS BenchmarkSelectionRationale,
                calc.is_active AS IsActive,
                calc.is_manual_override AS IsManualOverride,
                calc.approved_by_user_id AS ApprovedByUserId,
                calc.approved_by_name AS ApprovedByName,
                calc.approved_at AS ApprovedAt,
                calc.created_by_user_id AS CreatedByUserId,
                calc.created_by_name AS CreatedByName,
                calc.created_at AS CreatedAt,
                calc.updated_at AS UpdatedAt
            FROM audit_materiality_calculations calc
            LEFT JOIN audit_materiality_benchmark_profiles profile ON calc.benchmark_profile_id = profile.id";

        private const string CandidateSelect = @"
            SELECT
                cand.id AS Id,
                cand.reference_id AS ReferenceId,
                cand.fiscal_year AS FiscalYear,
                cand.benchmark_profile_id AS BenchmarkProfileId,
                profile.profile_name AS BenchmarkProfileName,
                profile.validation_status AS BenchmarkProfileValidationStatus,
                cand.candidate_code AS CandidateCode,
                cand.candidate_name AS CandidateName,
                cand.benchmark_source AS BenchmarkSource,
                cand.source_table AS SourceTable,
                cand.source_metric_label AS SourceMetricLabel,
                cand.benchmark_amount AS BenchmarkAmount,
                cand.recommended_percentage AS RecommendedPercentage,
                cand.recommended_overall_materiality AS RecommendedOverallMateriality,
                cand.recommended_performance_percentage AS RecommendedPerformancePercentage,
                cand.recommended_performance_materiality AS RecommendedPerformanceMateriality,
                cand.recommended_clearly_trivial_percentage AS RecommendedClearlyTrivialPercentage,
                cand.recommended_clearly_trivial_threshold AS RecommendedClearlyTrivialThreshold,
                cand.notes AS Notes,
                cand.entity_type AS EntityType,
                cand.industry_name AS IndustryName,
                cand.is_selected AS IsSelected,
                cand.selected_calculation_id AS SelectedCalculationId,
                cand.generated_by_user_id AS GeneratedByUserId,
                cand.generated_by_name AS GeneratedByName,
                cand.generated_at AS GeneratedAt
            FROM audit_materiality_candidates cand
            LEFT JOIN audit_materiality_benchmark_profiles profile ON cand.benchmark_profile_id = profile.id";

        private const string BenchmarkProfileSelect = @"
            SELECT
                profile.id AS Id,
                profile.profile_code AS ProfileCode,
                profile.profile_name AS ProfileName,
                profile.engagement_type_id AS EngagementTypeId,
                et.name AS EngagementTypeName,
                profile.entity_type AS EntityType,
                profile.industry_name AS IndustryName,
                profile.profit_before_tax_percentage AS ProfitBeforeTaxPercentage,
                profile.revenue_percentage AS RevenuePercentage,
                profile.total_assets_percentage AS TotalAssetsPercentage,
                profile.expenses_percentage AS ExpensesPercentage,
                profile.performance_percentage AS PerformancePercentage,
                profile.clearly_trivial_percentage AS ClearlyTrivialPercentage,
                profile.benchmark_rationale AS BenchmarkRationale,
                profile.validation_status AS ValidationStatus,
                profile.validation_notes AS ValidationNotes,
                profile.approved_by_name AS ApprovedByName,
                profile.approved_at AS ApprovedAt,
                profile.is_default AS IsDefault,
                profile.sort_order AS SortOrder,
                profile.is_active AS IsActive
            FROM audit_materiality_benchmark_profiles profile
            LEFT JOIN ra_engagement_type et ON profile.engagement_type_id = et.id";

        private const string ApprovalHistorySelect = @"
            SELECT
                history.id AS Id,
                history.reference_id AS ReferenceId,
                history.previous_calculation_id AS PreviousCalculationId,
                previous_calc.calculation_summary AS PreviousCalculationSummary,
                history.calculation_id AS CalculationId,
                history.benchmark_profile_id AS BenchmarkProfileId,
                profile.profile_name AS BenchmarkProfileName,
                history.action_type AS ActionType,
                history.action_label AS ActionLabel,
                history.benchmark_code AS BenchmarkCode,
                history.benchmark_name AS BenchmarkName,
                history.percentage_applied AS PercentageApplied,
                history.performance_percentage_applied AS PerformancePercentageApplied,
                history.clearly_trivial_percentage_applied AS ClearlyTrivialPercentageApplied,
                history.overall_materiality AS OverallMateriality,
                history.performance_materiality AS PerformanceMateriality,
                history.clearly_trivial_threshold AS ClearlyTrivialThreshold,
                history.entity_type AS EntityType,
                history.industry_name AS IndustryName,
                history.benchmark_selection_rationale AS BenchmarkSelectionRationale,
                history.override_reason AS OverrideReason,
                history.approved_by_user_id AS ApprovedByUserId,
                history.approved_by_name AS ApprovedByName,
                history.approved_at AS ApprovedAt,
                history.created_at AS CreatedAt
            FROM audit_materiality_approval_history history
            LEFT JOIN audit_materiality_calculations previous_calc ON history.previous_calculation_id = previous_calc.id
            LEFT JOIN audit_materiality_benchmark_profiles profile ON history.benchmark_profile_id = profile.id";

        private const string ScopeLinkSelect = @"
            SELECT
                link.id AS Id,
                link.reference_id AS ReferenceId,
                link.materiality_calculation_id AS MaterialityCalculationId,
                calc.calculation_summary AS CalculationSummary,
                link.scope_item_id AS ScopeItemId,
                COALESCE(NULLIF(si.fsli, ''), NULLIF(TRIM(CONCAT_WS(' / ', si.business_unit, si.process_name, si.subprocess_name)), ''), CONCAT('Scope item ', link.scope_item_id)) AS ScopeItemLabel,
                link.fsli AS Fsli,
                link.benchmark_relevance AS BenchmarkRelevance,
                link.inclusion_reason AS InclusionReason,
                link.is_above_threshold AS IsAboveThreshold,
                link.coverage_percent AS CoveragePercent,
                link.created_at AS CreatedAt
            FROM audit_materiality_scope_links link
            LEFT JOIN audit_materiality_calculations calc ON link.materiality_calculation_id = calc.id
            LEFT JOIN audit_scope_items si ON link.scope_item_id = si.id";

        private const string MisstatementSelect = @"
            SELECT
                mis.id AS Id,
                mis.reference_id AS ReferenceId,
                mis.finding_id AS FindingId,
                f.finding_title AS FindingTitle,
                mis.materiality_calculation_id AS MaterialityCalculationId,
                calc.calculation_summary AS CalculationSummary,
                mis.fsli AS Fsli,
                mis.account_number AS AccountNumber,
                mis.transaction_identifier AS TransactionIdentifier,
                mis.description AS Description,
                mis.actual_amount AS ActualAmount,
                mis.projected_amount AS ProjectedAmount,
                mis.evaluation_basis AS EvaluationBasis,
                mis.exceeds_clearly_trivial AS ExceedsClearlyTrivial,
                mis.exceeds_performance_materiality AS ExceedsPerformanceMateriality,
                mis.exceeds_overall_materiality AS ExceedsOverallMateriality,
                mis.status AS Status,
                mis.created_by_user_id AS CreatedByUserId,
                mis.created_by_name AS CreatedByName,
                mis.created_at AS CreatedAt,
                mis.updated_at AS UpdatedAt
            FROM audit_misstatements mis
            LEFT JOIN audit_materiality_calculations calc ON mis.materiality_calculation_id = calc.id
            LEFT JOIN audit_findings f ON mis.finding_id = f.id";

        public AuditMaterialityRepository(string connectionString)
        {
            _connectionString = connectionString ?? throw new ArgumentNullException(nameof(connectionString));
        }

        public async Task<AuditMaterialityWorkspace> GetWorkspaceAsync(int referenceId)
        {
            using IDbConnection db = new NpgsqlConnection(_connectionString);
            db.Open();

            var workspaceQuery = @"
                SELECT
                    ref.reference_id AS ReferenceId,
                    COALESCE(plan.engagement_title, NULLIF(ref.title, ''), ref.client, CONCAT('Audit File ', ref.reference_id)) AS EngagementTitle,
                    plan.engagement_type_id AS EngagementTypeId,
                    et.name AS EngagementTypeName,
                    plan.plan_year AS PlanYear,
                    plan.materiality AS PlanningMateriality,
                    plan.materiality_basis AS PlanningMaterialityBasis,
                    plan.overall_materiality AS PlanningOverallMateriality,
                    plan.performance_materiality AS PlanningPerformanceMateriality,
                    plan.clearly_trivial_threshold AS PlanningClearlyTrivialThreshold,
                    plan.materiality_benchmark_profile_id AS SelectedBenchmarkProfileId,
                    profile.profile_name AS SelectedBenchmarkProfileName,
                    plan.materiality_entity_type AS MaterialityEntityType,
                    plan.materiality_industry_name AS MaterialityIndustryName,
                    plan.materiality_benchmark_selection_rationale AS MaterialityBenchmarkSelectionRationale
                FROM riskassessmentreference ref
                LEFT JOIN audit_engagement_plans plan ON ref.reference_id = plan.reference_id
                LEFT JOIN ra_engagement_type et ON plan.engagement_type_id = et.id
                LEFT JOIN audit_materiality_benchmark_profiles profile ON plan.materiality_benchmark_profile_id = profile.id
                WHERE ref.reference_id = @ReferenceId;";

            var availabilityQuery = @"
                WITH latest_tb AS (
                    SELECT MAX(fiscal_year) AS latest_year
                    FROM audit_trial_balance_snapshots
                    WHERE reference_id = @ReferenceId
                ),
                latest_journal AS (
                    SELECT MAX(fiscal_year) AS latest_year
                    FROM audit_gl_journal_entries
                    WHERE reference_id = @ReferenceId
                )
                SELECT
                    EXISTS(
                        SELECT 1
                        FROM audit_trial_balance_snapshots
                        WHERE reference_id = @ReferenceId
                    ) AS HasTrialBalanceData,
                    (SELECT latest_year FROM latest_tb) AS LatestTrialBalanceYear,
                    COALESCE((
                        SELECT COUNT(*)
                        FROM audit_trial_balance_snapshots tb
                        WHERE tb.reference_id = @ReferenceId
                          AND tb.fiscal_year = (SELECT latest_year FROM latest_tb)
                    ), 0) AS TrialBalanceAccountCount,
                    COALESCE((
                        SELECT SUM(ABS(COALESCE(tb.current_balance, 0)))
                        FROM audit_trial_balance_snapshots tb
                        WHERE tb.reference_id = @ReferenceId
                          AND tb.fiscal_year = (SELECT latest_year FROM latest_tb)
                    ), 0) AS TrialBalanceAbsoluteBalance,
                    EXISTS(
                        SELECT 1
                        FROM audit_gl_journal_entries
                        WHERE reference_id = @ReferenceId
                    ) AS HasJournalData,
                    (SELECT latest_year FROM latest_journal) AS LatestJournalYear,
                    COALESCE((
                        SELECT COUNT(*)
                        FROM audit_gl_journal_entries je
                        WHERE je.reference_id = @ReferenceId
                          AND je.fiscal_year = (SELECT latest_year FROM latest_journal)
                    ), 0) AS JournalEntryCount,
                    (
                        SELECT MAX(imported_at)
                        FROM audit_analytics_import_batches
                        WHERE reference_id = @ReferenceId
                    ) AS LatestAnalyticsImportAt;";

            var workspace = await db.QueryFirstOrDefaultAsync<AuditMaterialityWorkspace>(
                workspaceQuery,
                new { ReferenceId = referenceId })
                ?? new AuditMaterialityWorkspace { ReferenceId = referenceId };

            var availability = await db.QueryFirstOrDefaultAsync<MaterialityAvailabilityRow>(
                availabilityQuery,
                new { ReferenceId = referenceId });

            if (availability != null)
            {
                workspace.HasTrialBalanceData = availability.HasTrialBalanceData;
                workspace.LatestTrialBalanceYear = availability.LatestTrialBalanceYear;
                workspace.TrialBalanceAccountCount = availability.TrialBalanceAccountCount;
                workspace.TrialBalanceAbsoluteBalance = availability.TrialBalanceAbsoluteBalance;
                workspace.HasJournalData = availability.HasJournalData;
                workspace.LatestJournalYear = availability.LatestJournalYear;
                workspace.JournalEntryCount = availability.JournalEntryCount;
                workspace.LatestAnalyticsImportAt = availability.LatestAnalyticsImportAt;
            }

            workspace.ActiveCalculation = await GetActiveCalculationInternalAsync(db, referenceId);
            workspace.Calculations = await GetCalculationsInternalAsync(db, referenceId);
            workspace.BenchmarkCandidates = await GetLatestCandidatesInternalAsync(db, referenceId);
            workspace.BenchmarkProfiles = await GetBenchmarkProfilesInternalAsync(db, workspace.EngagementTypeId);
            workspace.ApprovalHistory = await GetApprovalHistoryInternalAsync(db, referenceId);
            workspace.ApplicationSummary = await GetApplicationSummaryInternalAsync(db, workspace);
            workspace.MisstatementSummary = await GetMisstatementSummaryInternalAsync(db, workspace);
            workspace.ScopeLinks = await GetScopeLinksInternalAsync(db, referenceId);
            workspace.Misstatements = await GetMisstatementsInternalAsync(db, referenceId);
            return workspace;
        }

        public async Task<AuditMaterialityApplicationSummary> GetApplicationSummaryAsync(int referenceId)
        {
            var workspace = await GetWorkspaceAsync(referenceId);
            return workspace.ApplicationSummary ?? new AuditMaterialityApplicationSummary { ReferenceId = referenceId };
        }

        public async Task<List<AuditMaterialityCandidate>> GenerateCandidatesAsync(GenerateAuditMaterialityCandidatesRequest request)
        {
            if (request == null)
                throw new ArgumentNullException(nameof(request));
            if (request.ReferenceId <= 0)
                throw new InvalidOperationException("Reference ID is required.");

            using IDbConnection db = new NpgsqlConnection(_connectionString);
            db.Open();

            var fiscalYear = await ResolveTrialBalanceYearAsync(db, request.ReferenceId, request.FiscalYear);
            if (!fiscalYear.HasValue)
                throw new InvalidOperationException("No imported trial balance data is available for this audit file.");

            var benchmarkProfile = await ResolveBenchmarkProfileAsync(db, request.ReferenceId, request.BenchmarkProfileId);
            var effectiveRequest = ApplyBenchmarkProfileDefaults(request, benchmarkProfile);

            var rows = (await db.QueryAsync<TrialBalanceMetricRow>(@"
                SELECT
                    COALESCE(account_name, '') AS AccountName,
                    COALESCE(fsli, '') AS Fsli,
                    COALESCE(current_balance, 0) AS CurrentBalance
                FROM audit_trial_balance_snapshots
                WHERE reference_id = @ReferenceId
                  AND fiscal_year = @FiscalYear;",
                new { request.ReferenceId, FiscalYear = fiscalYear.Value })).ToList();

            if (!rows.Any())
                throw new InvalidOperationException("The selected audit file has no trial balance rows for candidate generation.");

            var generatedAt = DateTime.UtcNow;
            var candidates = BuildCandidateRows(rows, request.ReferenceId, fiscalYear.Value, effectiveRequest, benchmarkProfile, generatedAt);
            if (!candidates.Any())
                throw new InvalidOperationException("Imported financial data exists, but benchmark candidates could not be derived from the current trial balance labels.");

            const string insertQuery = @"
                INSERT INTO audit_materiality_candidates
                (
                    reference_id,
                    fiscal_year,
                    benchmark_profile_id,
                    candidate_code,
                    candidate_name,
                    benchmark_source,
                    source_table,
                    source_metric_label,
                    benchmark_amount,
                    recommended_percentage,
                    recommended_overall_materiality,
                    recommended_performance_percentage,
                    recommended_performance_materiality,
                    recommended_clearly_trivial_percentage,
                    recommended_clearly_trivial_threshold,
                    notes,
                    entity_type,
                    industry_name,
                    is_selected,
                    selected_calculation_id,
                    generated_by_user_id,
                    generated_by_name,
                    generated_at
                )
                VALUES
                (
                    @ReferenceId,
                    @FiscalYear,
                    @BenchmarkProfileId,
                    @CandidateCode,
                    @CandidateName,
                    @BenchmarkSource,
                    @SourceTable,
                    @SourceMetricLabel,
                    @BenchmarkAmount,
                    @RecommendedPercentage,
                    @RecommendedOverallMateriality,
                    @RecommendedPerformancePercentage,
                    @RecommendedPerformanceMateriality,
                    @RecommendedClearlyTrivialPercentage,
                    @RecommendedClearlyTrivialThreshold,
                    @Notes,
                    @EntityType,
                    @IndustryName,
                    @IsSelected,
                    @SelectedCalculationId,
                    @GeneratedByUserId,
                    @GeneratedByName,
                    @GeneratedAt
                )
                RETURNING id;";

            foreach (var candidate in candidates)
            {
                candidate.Id = await db.ExecuteScalarAsync<long>(insertQuery, candidate);
            }

            return candidates;
        }

        public async Task<List<AuditMaterialityCalculation>> GetCalculationsByReferenceAsync(int referenceId)
        {
            using IDbConnection db = new NpgsqlConnection(_connectionString);
            db.Open();
            return await GetCalculationsInternalAsync(db, referenceId);
        }

        public async Task<AuditMaterialityCalculation> CreateCalculationAsync(CreateAuditMaterialityCalculationRequest request)
        {
            if (request == null)
                throw new ArgumentNullException(nameof(request));
            if (request.ReferenceId <= 0)
                throw new InvalidOperationException("Reference ID is required.");

            using IDbConnection db = new NpgsqlConnection(_connectionString);
            db.Open();

            AuditMaterialityCandidate sourceCandidate = null;
            if (request.CandidateId.HasValue)
            {
                sourceCandidate = await db.QueryFirstOrDefaultAsync<AuditMaterialityCandidate>(
                    $"{CandidateSelect} WHERE cand.id = @Id AND cand.reference_id = @ReferenceId",
                    new { Id = request.CandidateId.Value, request.ReferenceId });

                if (sourceCandidate == null)
                    throw new InvalidOperationException("The selected materiality candidate could not be found.");

                request.FiscalYear ??= sourceCandidate.FiscalYear;
                request.BenchmarkProfileId ??= sourceCandidate.BenchmarkProfileId;
                request.BenchmarkCode ??= sourceCandidate.CandidateCode;
                request.BenchmarkName ??= sourceCandidate.CandidateName;
                request.BenchmarkSource = string.IsNullOrWhiteSpace(request.BenchmarkSource) ? sourceCandidate.BenchmarkSource : request.BenchmarkSource;
                request.SourceTable = string.IsNullOrWhiteSpace(request.SourceTable) ? sourceCandidate.SourceTable : request.SourceTable;
                request.EntityType = string.IsNullOrWhiteSpace(request.EntityType) ? sourceCandidate.EntityType : request.EntityType;
                request.IndustryName = string.IsNullOrWhiteSpace(request.IndustryName) ? sourceCandidate.IndustryName : request.IndustryName;
                if (request.BenchmarkAmount <= 0)
                    request.BenchmarkAmount = sourceCandidate.BenchmarkAmount;
                if (request.PercentageApplied <= 0)
                    request.PercentageApplied = sourceCandidate.RecommendedPercentage;
                if (!request.PerformancePercentageApplied.HasValue || request.PerformancePercentageApplied <= 0)
                    request.PerformancePercentageApplied = sourceCandidate.RecommendedPerformancePercentage;
                if (!request.ClearlyTrivialPercentageApplied.HasValue || request.ClearlyTrivialPercentageApplied <= 0)
                    request.ClearlyTrivialPercentageApplied = sourceCandidate.RecommendedClearlyTrivialPercentage;
            }

            var benchmarkProfile = await ResolveBenchmarkProfileAsync(db, request.ReferenceId, request.BenchmarkProfileId);
            request.EntityType = NormalizeOptionalText(request.EntityType) ?? benchmarkProfile?.EntityType;
            request.IndustryName = NormalizeOptionalText(request.IndustryName) ?? benchmarkProfile?.IndustryName;
            request.BenchmarkSelectionRationale = NormalizeOptionalText(request.BenchmarkSelectionRationale);

            if (request.BenchmarkAmount <= 0)
                throw new InvalidOperationException("Benchmark amount must be greater than zero.");
            if (request.PercentageApplied <= 0)
                throw new InvalidOperationException("Benchmark percentage must be greater than zero.");
            if (string.IsNullOrWhiteSpace(request.BenchmarkName))
                throw new InvalidOperationException("Benchmark name is required.");

            var overallMateriality = CalculateAmount(request.BenchmarkAmount, request.PercentageApplied);
            var performancePercent = request.PerformancePercentageApplied ?? 75m;
            var clearlyTrivialPercent = request.ClearlyTrivialPercentageApplied ?? 5m;
            var performanceMateriality = CalculateAmount(overallMateriality, performancePercent);
            var clearlyTrivial = CalculateAmount(overallMateriality, clearlyTrivialPercent);
            var calculationSummary = $"{request.BenchmarkName} @ {request.PercentageApplied:0.####}%";

            const string insertQuery = @"
                INSERT INTO audit_materiality_calculations
                (
                    reference_id,
                    fiscal_year,
                    candidate_id,
                    benchmark_profile_id,
                    benchmark_code,
                    benchmark_name,
                    benchmark_source,
                    source_table,
                    benchmark_amount,
                    percentage_applied,
                    overall_materiality,
                    performance_percentage_applied,
                    performance_materiality,
                    clearly_trivial_percentage_applied,
                    clearly_trivial_threshold,
                    calculation_summary,
                    rationale,
                    entity_type,
                    industry_name,
                    benchmark_selection_rationale,
                    is_active,
                    is_manual_override,
                    created_by_user_id,
                    created_by_name
                )
                VALUES
                (
                    @ReferenceId,
                    @FiscalYear,
                    @CandidateId,
                    @BenchmarkProfileId,
                    @BenchmarkCode,
                    @BenchmarkName,
                    @BenchmarkSource,
                    @SourceTable,
                    @BenchmarkAmount,
                    @PercentageApplied,
                    @OverallMateriality,
                    @PerformancePercentageApplied,
                    @PerformanceMateriality,
                    @ClearlyTrivialPercentageApplied,
                    @ClearlyTrivialThreshold,
                    @CalculationSummary,
                    @Rationale,
                    @EntityType,
                    @IndustryName,
                    @BenchmarkSelectionRationale,
                    FALSE,
                    @IsManualOverride,
                    @CreatedByUserId,
                    @CreatedByName
                )
                RETURNING id;";

            var id = await db.ExecuteScalarAsync<long>(insertQuery, new
            {
                request.ReferenceId,
                request.FiscalYear,
                request.CandidateId,
                BenchmarkProfileId = benchmarkProfile?.Id,
                request.BenchmarkCode,
                request.BenchmarkName,
                request.BenchmarkSource,
                request.SourceTable,
                request.BenchmarkAmount,
                request.PercentageApplied,
                OverallMateriality = overallMateriality,
                PerformancePercentageApplied = performancePercent,
                PerformanceMateriality = performanceMateriality,
                ClearlyTrivialPercentageApplied = clearlyTrivialPercent,
                ClearlyTrivialThreshold = clearlyTrivial,
                CalculationSummary = calculationSummary,
                request.Rationale,
                request.EntityType,
                request.IndustryName,
                request.BenchmarkSelectionRationale,
                request.IsManualOverride,
                request.CreatedByUserId,
                request.CreatedByName
            });

            if (request.CandidateId.HasValue)
            {
                await db.ExecuteAsync(@"
                    UPDATE audit_materiality_candidates
                    SET selected_calculation_id = @CalculationId
                    WHERE id = @CandidateId;",
                    new { CalculationId = id, CandidateId = request.CandidateId.Value });
            }

            if (request.SetAsActive)
            {
                return await SetActiveCalculationAsync(new SetActiveAuditMaterialityRequest
                {
                    ReferenceId = request.ReferenceId,
                    CalculationId = id,
                    ApprovedByUserId = request.CreatedByUserId,
                    ApprovedByName = request.CreatedByName,
                    ApprovedAt = DateTime.UtcNow,
                    MaterialityOverrideReason = request.IsManualOverride ? request.Rationale : null
                });
            }

            return await db.QueryFirstOrDefaultAsync<AuditMaterialityCalculation>(
                $"{CalculationSelect} WHERE calc.id = @Id",
                new { Id = id });
        }

        public async Task<AuditMaterialityCalculation> SetActiveCalculationAsync(SetActiveAuditMaterialityRequest request)
        {
            if (request == null)
                throw new ArgumentNullException(nameof(request));

            await using var db = new NpgsqlConnection(_connectionString);
            await db.OpenAsync();
            await using var transaction = await db.BeginTransactionAsync();

            var calculation = await db.QueryFirstOrDefaultAsync<AuditMaterialityCalculation>(
                $"{CalculationSelect} WHERE calc.id = @CalculationId AND calc.reference_id = @ReferenceId",
                new { request.CalculationId, request.ReferenceId },
                transaction);

            if (calculation == null)
                throw new InvalidOperationException("The selected materiality calculation could not be found.");

            var previousActiveCalculation = await db.QueryFirstOrDefaultAsync<AuditMaterialityCalculation>(
                $@"{CalculationSelect}
                   WHERE calc.reference_id = @ReferenceId
                     AND calc.is_active = TRUE
                     AND calc.id <> @CalculationId
                   ORDER BY COALESCE(calc.approved_at, calc.created_at) DESC, calc.id DESC
                   LIMIT 1;",
                new
                {
                    request.ReferenceId,
                    request.CalculationId
                },
                transaction);

            await db.ExecuteAsync(
                "UPDATE audit_materiality_calculations SET is_active = FALSE WHERE reference_id = @ReferenceId;",
                new { request.ReferenceId },
                transaction);

            var approvedAt = request.ApprovedAt ?? DateTime.UtcNow;

            await db.ExecuteAsync(@"
                UPDATE audit_materiality_calculations
                SET
                    is_active = TRUE,
                    approved_by_user_id = @ApprovedByUserId,
                    approved_by_name = @ApprovedByName,
                    approved_at = @ApprovedAt,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = @CalculationId;",
                new
                {
                    request.CalculationId,
                    request.ApprovedByUserId,
                    request.ApprovedByName,
                    ApprovedAt = approvedAt
                },
                transaction);

            await db.ExecuteAsync(@"
                UPDATE audit_materiality_candidates
                SET
                    is_selected = CASE WHEN id = @CandidateId THEN TRUE ELSE FALSE END,
                    selected_calculation_id = CASE WHEN id = @CandidateId THEN @CalculationId ELSE selected_calculation_id END
                WHERE reference_id = @ReferenceId;",
                new
                {
                    request.ReferenceId,
                    request.CalculationId,
                    CandidateId = calculation.CandidateId
                },
                transaction);

            await db.ExecuteAsync(@"
                INSERT INTO audit_engagement_plans
                (
                    reference_id,
                    engagement_title,
                    planning_status_id,
                    materiality,
                    materiality_basis,
                    overall_materiality,
                    performance_materiality,
                    clearly_trivial_threshold,
                    materiality_source,
                    active_materiality_calculation_id,
                    materiality_last_calculated_at,
                    materiality_override_reason,
                    selected_materiality_benchmark,
                    selected_materiality_benchmark_amount,
                    selected_materiality_benchmark_percentage,
                    materiality_benchmark_profile_id,
                    materiality_entity_type,
                    materiality_industry_name,
                    materiality_benchmark_selection_rationale
                )
                VALUES
                (
                    @ReferenceId,
                    COALESCE(
                        (SELECT engagement_title FROM audit_engagement_plans WHERE reference_id = @ReferenceId),
                        (SELECT COALESCE(NULLIF(title, ''), client, CONCAT('Audit File ', reference_id)) FROM riskassessmentreference WHERE reference_id = @ReferenceId)
                    ),
                    COALESCE((SELECT planning_status_id FROM audit_engagement_plans WHERE reference_id = @ReferenceId), 1),
                    @MaterialityNote,
                    @MaterialityBasis,
                    @OverallMateriality,
                    @PerformanceMateriality,
                    @ClearlyTrivialThreshold,
                    'Calculated',
                    @CalculationId,
                    @ApprovedAt,
                    @OverrideReason,
                    @BenchmarkName,
                    @BenchmarkAmount,
                    @BenchmarkPercentage,
                    @BenchmarkProfileId,
                    @EntityType,
                    @IndustryName,
                    @BenchmarkSelectionRationale
                )
                ON CONFLICT (reference_id)
                DO UPDATE SET
                    materiality = EXCLUDED.materiality,
                    materiality_basis = EXCLUDED.materiality_basis,
                    overall_materiality = EXCLUDED.overall_materiality,
                    performance_materiality = EXCLUDED.performance_materiality,
                    clearly_trivial_threshold = EXCLUDED.clearly_trivial_threshold,
                    materiality_source = EXCLUDED.materiality_source,
                    active_materiality_calculation_id = EXCLUDED.active_materiality_calculation_id,
                    materiality_last_calculated_at = EXCLUDED.materiality_last_calculated_at,
                    materiality_override_reason = EXCLUDED.materiality_override_reason,
                    selected_materiality_benchmark = EXCLUDED.selected_materiality_benchmark,
                    selected_materiality_benchmark_amount = EXCLUDED.selected_materiality_benchmark_amount,
                    selected_materiality_benchmark_percentage = EXCLUDED.selected_materiality_benchmark_percentage,
                    materiality_benchmark_profile_id = EXCLUDED.materiality_benchmark_profile_id,
                    materiality_entity_type = EXCLUDED.materiality_entity_type,
                    materiality_industry_name = EXCLUDED.materiality_industry_name,
                    materiality_benchmark_selection_rationale = EXCLUDED.materiality_benchmark_selection_rationale,
                    updated_at = CURRENT_TIMESTAMP;",
                new
                {
                    request.ReferenceId,
                    request.CalculationId,
                    ApprovedAt = approvedAt,
                    OverrideReason = request.MaterialityOverrideReason,
                    MaterialityNote = $"Calculated from {calculation.BenchmarkName} using imported financial data.",
                    MaterialityBasis = calculation.CalculationSummary,
                    calculation.OverallMateriality,
                    calculation.PerformanceMateriality,
                    calculation.ClearlyTrivialThreshold,
                    calculation.BenchmarkName,
                    calculation.BenchmarkAmount,
                    BenchmarkPercentage = calculation.PercentageApplied,
                    calculation.BenchmarkProfileId,
                    calculation.EntityType,
                    calculation.IndustryName,
                    calculation.BenchmarkSelectionRationale
                },
                transaction);

            await db.ExecuteAsync(@"
                INSERT INTO audit_materiality_approval_history
                (
                    reference_id,
                    previous_calculation_id,
                    calculation_id,
                    benchmark_profile_id,
                    action_type,
                    action_label,
                    benchmark_code,
                    benchmark_name,
                    percentage_applied,
                    performance_percentage_applied,
                    clearly_trivial_percentage_applied,
                    overall_materiality,
                    performance_materiality,
                    clearly_trivial_threshold,
                    entity_type,
                    industry_name,
                    benchmark_selection_rationale,
                    override_reason,
                    approved_by_user_id,
                    approved_by_name,
                    approved_at
                )
                VALUES
                (
                    @ReferenceId,
                    @PreviousCalculationId,
                    @CalculationId,
                    @BenchmarkProfileId,
                    @ActionType,
                    @ActionLabel,
                    @BenchmarkCode,
                    @BenchmarkName,
                    @PercentageApplied,
                    @PerformancePercentageApplied,
                    @ClearlyTrivialPercentageApplied,
                    @OverallMateriality,
                    @PerformanceMateriality,
                    @ClearlyTrivialThreshold,
                    @EntityType,
                    @IndustryName,
                    @BenchmarkSelectionRationale,
                    @OverrideReason,
                    @ApprovedByUserId,
                    @ApprovedByName,
                    @ApprovedAt
                );",
                new
                {
                    request.ReferenceId,
                    PreviousCalculationId = previousActiveCalculation?.Id,
                    request.CalculationId,
                    calculation.BenchmarkProfileId,
                    ActionType = calculation.IsManualOverride ? "manual_override_activated" : "calculation_activated",
                    ActionLabel = calculation.IsManualOverride ? "Manual materiality override activated" : "Calculated materiality activated",
                    calculation.BenchmarkCode,
                    calculation.BenchmarkName,
                    calculation.PercentageApplied,
                    calculation.PerformancePercentageApplied,
                    calculation.ClearlyTrivialPercentageApplied,
                    calculation.OverallMateriality,
                    calculation.PerformanceMateriality,
                    calculation.ClearlyTrivialThreshold,
                    calculation.EntityType,
                    calculation.IndustryName,
                    calculation.BenchmarkSelectionRationale,
                    OverrideReason = request.MaterialityOverrideReason,
                    request.ApprovedByUserId,
                    request.ApprovedByName,
                    ApprovedAt = approvedAt
                },
                transaction);

            await transaction.CommitAsync();

            return await db.QueryFirstOrDefaultAsync<AuditMaterialityCalculation>(
                $"{CalculationSelect} WHERE calc.id = @Id",
                new { Id = request.CalculationId });
        }

        public async Task<AuditMaterialityScopeLink> CreateScopeLinkAsync(UpsertAuditMaterialityScopeLinkRequest request)
        {
            if (request == null)
                throw new ArgumentNullException(nameof(request));
            if (request.ReferenceId <= 0)
                throw new InvalidOperationException("Reference ID is required.");

            using IDbConnection db = new NpgsqlConnection(_connectionString);
            db.Open();

            var calculationId = await ResolveMaterialityCalculationIdAsync(db, request.ReferenceId, request.MaterialityCalculationId);
            if (!calculationId.HasValue)
                throw new InvalidOperationException("Activate a materiality calculation before recording a scope decision.");

            var normalized = await NormalizeScopeLinkRequestAsync(db, request, calculationId.Value);

            const string insertQuery = @"
                INSERT INTO audit_materiality_scope_links
                (
                    reference_id,
                    materiality_calculation_id,
                    scope_item_id,
                    fsli,
                    benchmark_relevance,
                    inclusion_reason,
                    is_above_threshold,
                    coverage_percent
                )
                VALUES
                (
                    @ReferenceId,
                    @MaterialityCalculationId,
                    @ScopeItemId,
                    @Fsli,
                    @BenchmarkRelevance,
                    @InclusionReason,
                    @IsAboveThreshold,
                    @CoveragePercent
                )
                RETURNING id;";

            var id = await db.ExecuteScalarAsync<long>(insertQuery, normalized);
            return await db.QueryFirstOrDefaultAsync<AuditMaterialityScopeLink>(
                $"{ScopeLinkSelect} WHERE link.id = @Id",
                new { Id = id });
        }

        public async Task<AuditMaterialityScopeLink> UpdateScopeLinkAsync(UpsertAuditMaterialityScopeLinkRequest request)
        {
            if (request == null)
                throw new ArgumentNullException(nameof(request));
            if (!request.Id.HasValue || request.Id.Value <= 0)
                throw new InvalidOperationException("Scope link ID is required.");
            if (request.ReferenceId <= 0)
                throw new InvalidOperationException("Reference ID is required.");

            using IDbConnection db = new NpgsqlConnection(_connectionString);
            db.Open();

            var calculationId = await ResolveMaterialityCalculationIdAsync(db, request.ReferenceId, request.MaterialityCalculationId);
            if (!calculationId.HasValue)
                throw new InvalidOperationException("Activate a materiality calculation before recording a scope decision.");

            var normalized = await NormalizeScopeLinkRequestAsync(db, request, calculationId.Value);

            await db.ExecuteAsync(@"
                UPDATE audit_materiality_scope_links
                SET
                    materiality_calculation_id = @MaterialityCalculationId,
                    scope_item_id = @ScopeItemId,
                    fsli = @Fsli,
                    benchmark_relevance = @BenchmarkRelevance,
                    inclusion_reason = @InclusionReason,
                    is_above_threshold = @IsAboveThreshold,
                    coverage_percent = @CoveragePercent
                WHERE id = @Id
                  AND reference_id = @ReferenceId;",
                new
                {
                    Id = request.Id.Value,
                    normalized.ReferenceId,
                    normalized.MaterialityCalculationId,
                    normalized.ScopeItemId,
                    normalized.Fsli,
                    normalized.BenchmarkRelevance,
                    normalized.InclusionReason,
                    normalized.IsAboveThreshold,
                    normalized.CoveragePercent
                });

            return await db.QueryFirstOrDefaultAsync<AuditMaterialityScopeLink>(
                $"{ScopeLinkSelect} WHERE link.id = @Id",
                new { Id = request.Id.Value });
        }

        public async Task<bool> DeleteScopeLinkAsync(long id)
        {
            using IDbConnection db = new NpgsqlConnection(_connectionString);
            db.Open();
            return await db.ExecuteAsync("DELETE FROM audit_materiality_scope_links WHERE id = @Id", new { Id = id }) > 0;
        }

        public async Task<AuditMisstatement> CreateMisstatementAsync(UpsertAuditMisstatementRequest request)
        {
            if (request == null)
                throw new ArgumentNullException(nameof(request));
            if (request.ReferenceId <= 0)
                throw new InvalidOperationException("Reference ID is required.");
            if (string.IsNullOrWhiteSpace(request.Description))
                throw new InvalidOperationException("Misstatement description is required.");

            using IDbConnection db = new NpgsqlConnection(_connectionString);
            db.Open();

            var normalized = await NormalizeMisstatementRequestAsync(db, request);

            const string insertQuery = @"
                INSERT INTO audit_misstatements
                (
                    reference_id,
                    finding_id,
                    materiality_calculation_id,
                    fsli,
                    account_number,
                    transaction_identifier,
                    description,
                    actual_amount,
                    projected_amount,
                    evaluation_basis,
                    exceeds_clearly_trivial,
                    exceeds_performance_materiality,
                    exceeds_overall_materiality,
                    status,
                    created_by_user_id,
                    created_by_name
                )
                VALUES
                (
                    @ReferenceId,
                    @FindingId,
                    @MaterialityCalculationId,
                    @Fsli,
                    @AccountNumber,
                    @TransactionIdentifier,
                    @Description,
                    @ActualAmount,
                    @ProjectedAmount,
                    @EvaluationBasis,
                    @ExceedsClearlyTrivial,
                    @ExceedsPerformanceMateriality,
                    @ExceedsOverallMateriality,
                    @Status,
                    @CreatedByUserId,
                    @CreatedByName
                )
                RETURNING id;";

            var id = await db.ExecuteScalarAsync<long>(insertQuery, normalized);
            return await db.QueryFirstOrDefaultAsync<AuditMisstatement>(
                $"{MisstatementSelect} WHERE mis.id = @Id",
                new { Id = id });
        }

        public async Task<AuditMisstatement> UpdateMisstatementAsync(UpsertAuditMisstatementRequest request)
        {
            if (request == null)
                throw new ArgumentNullException(nameof(request));
            if (!request.Id.HasValue || request.Id.Value <= 0)
                throw new InvalidOperationException("Misstatement ID is required.");
            if (request.ReferenceId <= 0)
                throw new InvalidOperationException("Reference ID is required.");
            if (string.IsNullOrWhiteSpace(request.Description))
                throw new InvalidOperationException("Misstatement description is required.");

            using IDbConnection db = new NpgsqlConnection(_connectionString);
            db.Open();

            var normalized = await NormalizeMisstatementRequestAsync(db, request);

            await db.ExecuteAsync(@"
                UPDATE audit_misstatements
                SET
                    finding_id = @FindingId,
                    materiality_calculation_id = @MaterialityCalculationId,
                    fsli = @Fsli,
                    account_number = @AccountNumber,
                    transaction_identifier = @TransactionIdentifier,
                    description = @Description,
                    actual_amount = @ActualAmount,
                    projected_amount = @ProjectedAmount,
                    evaluation_basis = @EvaluationBasis,
                    exceeds_clearly_trivial = @ExceedsClearlyTrivial,
                    exceeds_performance_materiality = @ExceedsPerformanceMateriality,
                    exceeds_overall_materiality = @ExceedsOverallMateriality,
                    status = @Status,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = @Id
                  AND reference_id = @ReferenceId;",
                new
                {
                    Id = request.Id.Value,
                    normalized.ReferenceId,
                    normalized.FindingId,
                    normalized.MaterialityCalculationId,
                    normalized.Fsli,
                    normalized.AccountNumber,
                    normalized.TransactionIdentifier,
                    normalized.Description,
                    normalized.ActualAmount,
                    normalized.ProjectedAmount,
                    normalized.EvaluationBasis,
                    normalized.ExceedsClearlyTrivial,
                    normalized.ExceedsPerformanceMateriality,
                    normalized.ExceedsOverallMateriality,
                    normalized.Status
                });

            return await db.QueryFirstOrDefaultAsync<AuditMisstatement>(
                $"{MisstatementSelect} WHERE mis.id = @Id",
                new { Id = request.Id.Value });
        }

        public async Task<bool> DeleteMisstatementAsync(long id)
        {
            using IDbConnection db = new NpgsqlConnection(_connectionString);
            db.Open();
            return await db.ExecuteAsync("DELETE FROM audit_misstatements WHERE id = @Id", new { Id = id }) > 0;
        }

        private async Task<List<AuditMaterialityCalculation>> GetCalculationsInternalAsync(IDbConnection db, int referenceId)
        {
            return (await db.QueryAsync<AuditMaterialityCalculation>(
                $@"{CalculationSelect}
                   WHERE calc.reference_id = @ReferenceId
                   ORDER BY
                        CASE WHEN calc.is_active THEN 0 ELSE 1 END,
                        COALESCE(calc.approved_at, calc.created_at) DESC,
                        calc.id DESC;",
                new { ReferenceId = referenceId })).ToList();
        }

        private async Task<AuditMaterialityCalculation> GetActiveCalculationInternalAsync(IDbConnection db, int referenceId)
        {
            return await db.QueryFirstOrDefaultAsync<AuditMaterialityCalculation>(
                $@"{CalculationSelect}
                   WHERE calc.reference_id = @ReferenceId
                     AND calc.is_active = TRUE
                   ORDER BY COALESCE(calc.approved_at, calc.created_at) DESC, calc.id DESC
                   LIMIT 1;",
                new { ReferenceId = referenceId });
        }

        private async Task<List<AuditMaterialityCandidate>> GetLatestCandidatesInternalAsync(IDbConnection db, int referenceId)
        {
            var query = $@"
                WITH latest_generation AS (
                    SELECT MAX(generated_at) AS generated_at
                    FROM audit_materiality_candidates
                    WHERE reference_id = @ReferenceId
                )
                {CandidateSelect}
                WHERE cand.reference_id = @ReferenceId
                  AND cand.generated_at = (SELECT generated_at FROM latest_generation)
                ORDER BY cand.recommended_overall_materiality DESC, cand.id DESC;";

            return (await db.QueryAsync<AuditMaterialityCandidate>(query, new { ReferenceId = referenceId })).ToList();
        }

        private async Task<List<AuditMaterialityBenchmarkProfile>> GetBenchmarkProfilesInternalAsync(IDbConnection db, int? engagementTypeId)
        {
            return (await db.QueryAsync<AuditMaterialityBenchmarkProfile>(
                $@"{BenchmarkProfileSelect}
                   WHERE profile.is_active = TRUE
                     AND (profile.engagement_type_id IS NULL OR profile.engagement_type_id = @EngagementTypeId)
                   ORDER BY
                        CASE WHEN profile.is_default THEN 0 ELSE 1 END,
                        profile.sort_order,
                        profile.profile_name;",
                new { EngagementTypeId = engagementTypeId })).ToList();
        }

        private async Task<List<AuditMaterialityApprovalHistoryEntry>> GetApprovalHistoryInternalAsync(IDbConnection db, int referenceId)
        {
            return (await db.QueryAsync<AuditMaterialityApprovalHistoryEntry>(
                $@"{ApprovalHistorySelect}
                   WHERE history.reference_id = @ReferenceId
                   ORDER BY COALESCE(history.approved_at, history.created_at) DESC, history.id DESC;",
                new { ReferenceId = referenceId })).ToList();
        }

        private async Task<AuditMaterialityBenchmarkProfile> ResolveBenchmarkProfileAsync(IDbConnection db, int referenceId, int? requestedProfileId)
        {
            if (requestedProfileId.HasValue && requestedProfileId.Value > 0)
            {
                var requestedProfile = await db.QueryFirstOrDefaultAsync<AuditMaterialityBenchmarkProfile>(
                    $@"{BenchmarkProfileSelect}
                       WHERE profile.id = @ProfileId
                         AND profile.is_active = TRUE;",
                    new { ProfileId = requestedProfileId.Value });

                if (requestedProfile == null)
                    throw new InvalidOperationException("The selected materiality benchmark profile could not be found.");

                return requestedProfile;
            }

            return await db.QueryFirstOrDefaultAsync<AuditMaterialityBenchmarkProfile>(
                $@"{BenchmarkProfileSelect}
                   WHERE profile.is_active = TRUE
                     AND (
                            profile.id = (
                                SELECT materiality_benchmark_profile_id
                                FROM audit_engagement_plans
                                WHERE reference_id = @ReferenceId
                            )
                         OR profile.is_default = TRUE
                      )
                   ORDER BY
                        CASE WHEN profile.id = (
                                SELECT materiality_benchmark_profile_id
                                FROM audit_engagement_plans
                                WHERE reference_id = @ReferenceId
                            ) THEN 0 ELSE 1 END,
                        CASE WHEN profile.is_default THEN 0 ELSE 1 END,
                        profile.sort_order,
                        profile.profile_name
                   LIMIT 1;",
                new { ReferenceId = referenceId });
        }

        private static GenerateAuditMaterialityCandidatesRequest ApplyBenchmarkProfileDefaults(
            GenerateAuditMaterialityCandidatesRequest request,
            AuditMaterialityBenchmarkProfile benchmarkProfile)
        {
            return new GenerateAuditMaterialityCandidatesRequest
            {
                ReferenceId = request.ReferenceId,
                FiscalYear = request.FiscalYear,
                BenchmarkProfileId = benchmarkProfile?.Id ?? request.BenchmarkProfileId,
                EntityType = NormalizeOptionalText(request.EntityType) ?? benchmarkProfile?.EntityType,
                IndustryName = NormalizeOptionalText(request.IndustryName) ?? benchmarkProfile?.IndustryName,
                ProfitBeforeTaxPercentage = request.ProfitBeforeTaxPercentage ?? benchmarkProfile?.ProfitBeforeTaxPercentage ?? 5m,
                RevenuePercentage = request.RevenuePercentage ?? benchmarkProfile?.RevenuePercentage ?? 1m,
                TotalAssetsPercentage = request.TotalAssetsPercentage ?? benchmarkProfile?.TotalAssetsPercentage ?? 1m,
                ExpensesPercentage = request.ExpensesPercentage ?? benchmarkProfile?.ExpensesPercentage ?? 1m,
                PerformancePercentage = request.PerformancePercentage ?? benchmarkProfile?.PerformancePercentage ?? 75m,
                ClearlyTrivialPercentage = request.ClearlyTrivialPercentage ?? benchmarkProfile?.ClearlyTrivialPercentage ?? 5m,
                GeneratedByUserId = request.GeneratedByUserId,
                GeneratedByName = request.GeneratedByName
            };
        }

        private async Task<AuditMaterialityApplicationSummary> GetApplicationSummaryInternalAsync(IDbConnection db, AuditMaterialityWorkspace workspace)
        {
            var summary = new AuditMaterialityApplicationSummary
            {
                ReferenceId = workspace.ReferenceId,
                ThresholdSource = workspace.ActiveCalculation != null ? "Calculated" :
                    (!string.IsNullOrWhiteSpace(workspace.PlanningMaterialityBasis) ? "Manual Planning" : "Not Set"),
                ActiveBenchmarkSummary = workspace.ActiveCalculation?.CalculationSummary ??
                    (!string.IsNullOrWhiteSpace(workspace.PlanningMaterialityBasis) ? workspace.PlanningMaterialityBasis : "No active calculation"),
                OverallMateriality = workspace.ActiveCalculation?.OverallMateriality ?? workspace.PlanningOverallMateriality ?? 0,
                PerformanceMateriality = workspace.ActiveCalculation?.PerformanceMateriality ?? workspace.PlanningPerformanceMateriality ?? 0,
                ClearlyTrivialThreshold = workspace.ActiveCalculation?.ClearlyTrivialThreshold ?? workspace.PlanningClearlyTrivialThreshold ?? 0
            };

            if (summary.PerformanceMateriality <= 0)
            {
                summary.Guidance = "Create or activate a materiality calculation before applying thresholds to imported populations.";
                return summary;
            }

            var journalYear = await ResolvePopulationYearAsync(
                db,
                "audit_gl_journal_entries",
                workspace.ReferenceId,
                workspace.ActiveCalculation?.FiscalYear,
                workspace.LatestJournalYear);
            var trialBalanceYear = await ResolvePopulationYearAsync(
                db,
                "audit_trial_balance_snapshots",
                workspace.ReferenceId,
                workspace.ActiveCalculation?.FiscalYear,
                workspace.LatestTrialBalanceYear);

            if (journalYear.HasValue)
            {
                summary.PopulationSource = "Journal Entries";
                summary.PopulationFiscalYear = journalYear.Value;

                var journalAggregate = await db.QueryFirstOrDefaultAsync<PopulationAggregateRow>(@"
                    WITH population AS (
                        SELECT ABS(COALESCE(amount, COALESCE(debit_amount, 0) - COALESCE(credit_amount, 0))) AS basis_amount
                        FROM audit_gl_journal_entries
                        WHERE reference_id = @ReferenceId
                          AND fiscal_year = @FiscalYear
                    )
                    SELECT
                        COUNT(*) AS PopulationItemCount,
                        COALESCE(SUM(basis_amount), 0) AS PopulationAmount,
                        COUNT(*) FILTER (WHERE basis_amount >= @PerformanceMateriality) AS KeyItemCount,
                        COALESCE(SUM(basis_amount) FILTER (WHERE basis_amount >= @PerformanceMateriality), 0) AS KeyItemAmount,
                        COUNT(*) FILTER (WHERE basis_amount < @PerformanceMateriality) AS SamplePoolCount,
                        COALESCE(SUM(basis_amount) FILTER (WHERE basis_amount < @PerformanceMateriality), 0) AS SamplePoolAmount
                    FROM population;",
                    new
                    {
                        ReferenceId = workspace.ReferenceId,
                        FiscalYear = journalYear.Value,
                        summary.PerformanceMateriality
                    });

                if (journalAggregate != null)
                {
                    summary.PopulationItemCount = journalAggregate.PopulationItemCount;
                    summary.PopulationAmount = journalAggregate.PopulationAmount;
                    summary.KeyItemCount = journalAggregate.KeyItemCount;
                    summary.KeyItemAmount = journalAggregate.KeyItemAmount;
                    summary.SamplePoolCount = journalAggregate.SamplePoolCount;
                    summary.SamplePoolAmount = journalAggregate.SamplePoolAmount;
                }

                summary.KeyItems = (await db.QueryAsync<AuditMaterialityPopulationItem>(@"
                    SELECT
                        CONCAT(journal_number, '-', line_number) AS ItemIdentifier,
                        posting_date AS ItemDate,
                        fiscal_year AS FiscalYear,
                        account_number AS AccountNumber,
                        account_name AS AccountName,
                        fsli AS Fsli,
                        business_unit AS BusinessUnit,
                        COALESCE(description, 'Journal line') AS Description,
                        ABS(COALESCE(amount, COALESCE(debit_amount, 0) - COALESCE(credit_amount, 0))) AS BasisAmount,
                        'Key Item' AS Classification,
                        '100% test / vouch this item' AS RecommendedAction,
                        'Journal Entries' AS SourceDataset
                    FROM audit_gl_journal_entries
                    WHERE reference_id = @ReferenceId
                      AND fiscal_year = @FiscalYear
                      AND ABS(COALESCE(amount, COALESCE(debit_amount, 0) - COALESCE(credit_amount, 0))) >= @PerformanceMateriality
                    ORDER BY ABS(COALESCE(amount, COALESCE(debit_amount, 0) - COALESCE(credit_amount, 0))) DESC, posting_date DESC
                    LIMIT 6;",
                    new
                    {
                        ReferenceId = workspace.ReferenceId,
                        FiscalYear = journalYear.Value,
                        summary.PerformanceMateriality
                    })).ToList();

                summary.SamplePoolItems = (await db.QueryAsync<AuditMaterialityPopulationItem>(@"
                    SELECT
                        CONCAT(journal_number, '-', line_number) AS ItemIdentifier,
                        posting_date AS ItemDate,
                        fiscal_year AS FiscalYear,
                        account_number AS AccountNumber,
                        account_name AS AccountName,
                        fsli AS Fsli,
                        business_unit AS BusinessUnit,
                        COALESCE(description, 'Journal line') AS Description,
                        ABS(COALESCE(amount, COALESCE(debit_amount, 0) - COALESCE(credit_amount, 0))) AS BasisAmount,
                        'Sample Pool' AS Classification,
                        'Consider statistical or risk-based sampling' AS RecommendedAction,
                        'Journal Entries' AS SourceDataset
                    FROM audit_gl_journal_entries
                    WHERE reference_id = @ReferenceId
                      AND fiscal_year = @FiscalYear
                      AND ABS(COALESCE(amount, COALESCE(debit_amount, 0) - COALESCE(credit_amount, 0))) < @PerformanceMateriality
                    ORDER BY ABS(COALESCE(amount, COALESCE(debit_amount, 0) - COALESCE(credit_amount, 0))) DESC, posting_date DESC
                    LIMIT 6;",
                    new
                    {
                        ReferenceId = workspace.ReferenceId,
                        FiscalYear = journalYear.Value,
                        summary.PerformanceMateriality
                    })).ToList();
            }
            else if (trialBalanceYear.HasValue)
            {
                summary.PopulationSource = "Trial Balance";
                summary.PopulationFiscalYear = trialBalanceYear.Value;

                var tbAggregate = await db.QueryFirstOrDefaultAsync<PopulationAggregateRow>(@"
                    WITH population AS (
                        SELECT ABS(COALESCE(current_balance, 0)) AS basis_amount
                        FROM audit_trial_balance_snapshots
                        WHERE reference_id = @ReferenceId
                          AND fiscal_year = @FiscalYear
                    )
                    SELECT
                        COUNT(*) AS PopulationItemCount,
                        COALESCE(SUM(basis_amount), 0) AS PopulationAmount,
                        COUNT(*) FILTER (WHERE basis_amount >= @PerformanceMateriality) AS KeyItemCount,
                        COALESCE(SUM(basis_amount) FILTER (WHERE basis_amount >= @PerformanceMateriality), 0) AS KeyItemAmount,
                        COUNT(*) FILTER (WHERE basis_amount < @PerformanceMateriality) AS SamplePoolCount,
                        COALESCE(SUM(basis_amount) FILTER (WHERE basis_amount < @PerformanceMateriality), 0) AS SamplePoolAmount
                    FROM population;",
                    new
                    {
                        ReferenceId = workspace.ReferenceId,
                        FiscalYear = trialBalanceYear.Value,
                        summary.PerformanceMateriality
                    });

                if (tbAggregate != null)
                {
                    summary.PopulationItemCount = tbAggregate.PopulationItemCount;
                    summary.PopulationAmount = tbAggregate.PopulationAmount;
                    summary.KeyItemCount = tbAggregate.KeyItemCount;
                    summary.KeyItemAmount = tbAggregate.KeyItemAmount;
                    summary.SamplePoolCount = tbAggregate.SamplePoolCount;
                    summary.SamplePoolAmount = tbAggregate.SamplePoolAmount;
                }

                summary.KeyItems = (await db.QueryAsync<AuditMaterialityPopulationItem>(@"
                    SELECT
                        account_number AS ItemIdentifier,
                        as_of_date AS ItemDate,
                        fiscal_year AS FiscalYear,
                        account_number AS AccountNumber,
                        account_name AS AccountName,
                        fsli AS Fsli,
                        business_unit AS BusinessUnit,
                        COALESCE(account_name, fsli, 'Trial balance line') AS Description,
                        ABS(COALESCE(current_balance, 0)) AS BasisAmount,
                        'Key Balance' AS Classification,
                        'Treat as a material balance / high-priority account' AS RecommendedAction,
                        'Trial Balance' AS SourceDataset
                    FROM audit_trial_balance_snapshots
                    WHERE reference_id = @ReferenceId
                      AND fiscal_year = @FiscalYear
                      AND ABS(COALESCE(current_balance, 0)) >= @PerformanceMateriality
                    ORDER BY ABS(COALESCE(current_balance, 0)) DESC, account_number
                    LIMIT 6;",
                    new
                    {
                        ReferenceId = workspace.ReferenceId,
                        FiscalYear = trialBalanceYear.Value,
                        summary.PerformanceMateriality
                    })).ToList();

                summary.SamplePoolItems = (await db.QueryAsync<AuditMaterialityPopulationItem>(@"
                    SELECT
                        account_number AS ItemIdentifier,
                        as_of_date AS ItemDate,
                        fiscal_year AS FiscalYear,
                        account_number AS AccountNumber,
                        account_name AS AccountName,
                        fsli AS Fsli,
                        business_unit AS BusinessUnit,
                        COALESCE(account_name, fsli, 'Trial balance line') AS Description,
                        ABS(COALESCE(current_balance, 0)) AS BasisAmount,
                        'Below PM' AS Classification,
                        'Still evaluate qualitatively or sample where relevant' AS RecommendedAction,
                        'Trial Balance' AS SourceDataset
                    FROM audit_trial_balance_snapshots
                    WHERE reference_id = @ReferenceId
                      AND fiscal_year = @FiscalYear
                      AND ABS(COALESCE(current_balance, 0)) < @PerformanceMateriality
                    ORDER BY ABS(COALESCE(current_balance, 0)) DESC, account_number
                    LIMIT 6;",
                    new
                    {
                        ReferenceId = workspace.ReferenceId,
                        FiscalYear = trialBalanceYear.Value,
                        summary.PerformanceMateriality
                    })).ToList();
            }

            if (trialBalanceYear.HasValue && summary.OverallMateriality > 0)
            {
                var scopeAggregate = await db.QueryFirstOrDefaultAsync<ScopeCandidateAggregateRow>(@"
                    SELECT
                        COUNT(*) AS ScopeCandidateCount,
                        COALESCE(SUM(ABS(COALESCE(current_balance, 0))), 0) AS ScopeCandidateBalance
                    FROM audit_trial_balance_snapshots
                    WHERE reference_id = @ReferenceId
                      AND fiscal_year = @FiscalYear
                      AND ABS(COALESCE(current_balance, 0)) >= @OverallMateriality;",
                    new
                    {
                        ReferenceId = workspace.ReferenceId,
                        FiscalYear = trialBalanceYear.Value,
                        summary.OverallMateriality
                    });

                if (scopeAggregate != null)
                {
                    summary.ScopeCandidateCount = scopeAggregate.ScopeCandidateCount;
                    summary.ScopeCandidateBalance = scopeAggregate.ScopeCandidateBalance;
                }

                summary.ScopeCandidates = (await db.QueryAsync<AuditMaterialityPopulationItem>(@"
                    SELECT
                        account_number AS ItemIdentifier,
                        as_of_date AS ItemDate,
                        fiscal_year AS FiscalYear,
                        account_number AS AccountNumber,
                        account_name AS AccountName,
                        fsli AS Fsli,
                        business_unit AS BusinessUnit,
                        COALESCE(account_name, fsli, 'Trial balance line') AS Description,
                        ABS(COALESCE(current_balance, 0)) AS BasisAmount,
                        'Scope Candidate' AS Classification,
                        'Consider scoping this FSLI or balance into the engagement' AS RecommendedAction,
                        'Trial Balance' AS SourceDataset
                    FROM audit_trial_balance_snapshots
                    WHERE reference_id = @ReferenceId
                      AND fiscal_year = @FiscalYear
                      AND ABS(COALESCE(current_balance, 0)) >= @OverallMateriality
                    ORDER BY ABS(COALESCE(current_balance, 0)) DESC, account_number
                    LIMIT 6;",
                    new
                    {
                        ReferenceId = workspace.ReferenceId,
                        FiscalYear = trialBalanceYear.Value,
                        summary.OverallMateriality
                    })).ToList();
            }

            if (summary.PopulationItemCount == 0)
            {
                summary.Guidance = "Import journal entries or trial balance data for this audit file to apply performance materiality to a testing population.";
            }
            else if (summary.KeyItemCount > 0)
            {
                summary.Guidance = $"{summary.KeyItemCount} items exceed performance materiality and should be treated as key items for focused testing.";
            }
            else
            {
                summary.Guidance = "No individual imported items exceed performance materiality. Sampling and qualitative risk review still apply.";
            }

            return summary;
        }

        private async Task<AuditMaterialityMisstatementSummary> GetMisstatementSummaryInternalAsync(IDbConnection db, AuditMaterialityWorkspace workspace)
        {
            var summary = new AuditMaterialityMisstatementSummary
            {
                ReferenceId = workspace.ReferenceId,
                ThresholdSource = workspace.ActiveCalculation != null ? "Calculated" :
                    (!string.IsNullOrWhiteSpace(workspace.PlanningMaterialityBasis) ? "Manual Planning" : "Not Set"),
                OverallMateriality = workspace.ActiveCalculation?.OverallMateriality ?? workspace.PlanningOverallMateriality ?? 0,
                PerformanceMateriality = workspace.ActiveCalculation?.PerformanceMateriality ?? workspace.PlanningPerformanceMateriality ?? 0,
                ClearlyTrivialThreshold = workspace.ActiveCalculation?.ClearlyTrivialThreshold ?? workspace.PlanningClearlyTrivialThreshold ?? 0,
            };

            var aggregate = await db.QueryFirstOrDefaultAsync<MisstatementAggregateRow>(@"
                SELECT
                    COUNT(*) AS TotalRecordedMisstatements,
                    COALESCE(SUM(ABS(COALESCE(actual_amount, 0))), 0) AS TotalActualAmount,
                    COALESCE(SUM(ABS(COALESCE(projected_amount, actual_amount, 0))), 0) AS TotalProjectedAmount,
                    COUNT(*) FILTER (WHERE COALESCE(exceeds_clearly_trivial, FALSE)) AS AboveClearlyTrivialCount,
                    COUNT(*) FILTER (WHERE COALESCE(exceeds_performance_materiality, FALSE)) AS AbovePerformanceMaterialityCount,
                    COUNT(*) FILTER (WHERE COALESCE(exceeds_overall_materiality, FALSE)) AS AboveOverallMaterialityCount
                FROM audit_misstatements
                WHERE reference_id = @ReferenceId;",
                new { workspace.ReferenceId });

            if (aggregate != null)
            {
                summary.TotalRecordedMisstatements = aggregate.TotalRecordedMisstatements;
                summary.TotalActualAmount = aggregate.TotalActualAmount;
                summary.TotalProjectedAmount = aggregate.TotalProjectedAmount;
                summary.AboveClearlyTrivialCount = aggregate.AboveClearlyTrivialCount;
                summary.AbovePerformanceMaterialityCount = aggregate.AbovePerformanceMaterialityCount;
                summary.AboveOverallMaterialityCount = aggregate.AboveOverallMaterialityCount;
            }

            if (summary.TotalRecordedMisstatements == 0)
            {
                summary.EvaluationConclusion = "No recorded misstatements yet. Summary of audit differences is still clear.";
            }
            else if (summary.OverallMateriality > 0 && summary.TotalProjectedAmount >= summary.OverallMateriality)
            {
                summary.EvaluationConclusion = "Recorded misstatements exceed overall materiality. Management adjustment or reporting impact is likely required.";
            }
            else if (summary.PerformanceMateriality > 0 && summary.TotalProjectedAmount >= summary.PerformanceMateriality)
            {
                summary.EvaluationConclusion = "Recorded misstatements exceed performance materiality. Further evaluation and extension of testing are likely required.";
            }
            else if (summary.ClearlyTrivialThreshold > 0 && summary.TotalProjectedAmount < summary.ClearlyTrivialThreshold)
            {
                summary.EvaluationConclusion = "Recorded misstatements remain below the clearly trivial threshold in aggregate.";
            }
            else
            {
                summary.EvaluationConclusion = "Recorded misstatements are below overall materiality but still require aggregation and client follow-up.";
            }

            return summary;
        }

        private async Task<List<AuditMaterialityScopeLink>> GetScopeLinksInternalAsync(IDbConnection db, int referenceId)
        {
            return (await db.QueryAsync<AuditMaterialityScopeLink>(
                $@"{ScopeLinkSelect}
                   WHERE link.reference_id = @ReferenceId
                   ORDER BY link.created_at DESC, link.id DESC;",
                new { ReferenceId = referenceId })).ToList();
        }

        private async Task<List<AuditMisstatement>> GetMisstatementsInternalAsync(IDbConnection db, int referenceId)
        {
            return (await db.QueryAsync<AuditMisstatement>(
                $@"{MisstatementSelect}
                   WHERE mis.reference_id = @ReferenceId
                   ORDER BY mis.created_at DESC, mis.id DESC;",
                new { ReferenceId = referenceId })).ToList();
        }

        private async Task<long?> ResolveMaterialityCalculationIdAsync(IDbConnection db, int referenceId, long? requestedCalculationId)
        {
            if (requestedCalculationId.HasValue && requestedCalculationId.Value > 0)
            {
                return await db.ExecuteScalarAsync<long?>(@"
                    SELECT id
                    FROM audit_materiality_calculations
                    WHERE id = @CalculationId
                      AND reference_id = @ReferenceId;",
                    new
                    {
                        ReferenceId = referenceId,
                        CalculationId = requestedCalculationId.Value
                    });
            }

            return await db.ExecuteScalarAsync<long?>(@"
                SELECT id
                FROM audit_materiality_calculations
                WHERE reference_id = @ReferenceId
                  AND is_active = TRUE
                ORDER BY COALESCE(approved_at, created_at) DESC, id DESC
                LIMIT 1;",
                new { ReferenceId = referenceId });
        }

        private async Task<NormalizedScopeLinkRow> NormalizeScopeLinkRequestAsync(
            IDbConnection db,
            UpsertAuditMaterialityScopeLinkRequest request,
            long materialityCalculationId)
        {
            var normalized = new NormalizedScopeLinkRow
            {
                ReferenceId = request.ReferenceId,
                MaterialityCalculationId = materialityCalculationId,
                ScopeItemId = request.ScopeItemId,
                Fsli = request.Fsli?.Trim(),
                BenchmarkRelevance = string.IsNullOrWhiteSpace(request.BenchmarkRelevance)
                    ? "Above overall materiality"
                    : request.BenchmarkRelevance.Trim(),
                InclusionReason = request.InclusionReason?.Trim(),
                IsAboveThreshold = request.IsAboveThreshold,
                CoveragePercent = request.CoveragePercent
            };

            if (request.ScopeItemId.HasValue)
            {
                var scopeItem = await db.QueryFirstOrDefaultAsync<AuditScopeItem>(@"
                    SELECT
                        id AS Id,
                        reference_id AS ReferenceId,
                        business_unit AS BusinessUnit,
                        process_name AS ProcessName,
                        subprocess_name AS SubProcessName,
                        fsli AS Fsli
                    FROM audit_scope_items
                    WHERE id = @Id
                      AND reference_id = @ReferenceId;",
                    new
                    {
                        Id = request.ScopeItemId.Value,
                        ReferenceId = request.ReferenceId
                    });

                if (scopeItem == null)
                    throw new InvalidOperationException("The selected scope item could not be found for this audit file.");

                if (string.IsNullOrWhiteSpace(normalized.Fsli))
                    normalized.Fsli = scopeItem.Fsli?.Trim();
            }

            if (string.IsNullOrWhiteSpace(normalized.Fsli))
                throw new InvalidOperationException("FSLI is required to record a materiality scope decision.");

            return normalized;
        }

        private async Task<NormalizedMisstatementRow> NormalizeMisstatementRequestAsync(
            IDbConnection db,
            UpsertAuditMisstatementRequest request)
        {
            var thresholds = await GetThresholdRowAsync(db, request.ReferenceId, request.MaterialityCalculationId);
            var projectedAmount = request.ProjectedAmount ?? request.ActualAmount;
            var evaluationAmount = Math.Abs(projectedAmount);

            return new NormalizedMisstatementRow
            {
                ReferenceId = request.ReferenceId,
                FindingId = request.FindingId,
                MaterialityCalculationId = thresholds.MaterialityCalculationId,
                Fsli = request.Fsli?.Trim(),
                AccountNumber = request.AccountNumber?.Trim(),
                TransactionIdentifier = request.TransactionIdentifier?.Trim(),
                Description = request.Description?.Trim(),
                ActualAmount = request.ActualAmount,
                ProjectedAmount = request.ProjectedAmount,
                EvaluationBasis = string.IsNullOrWhiteSpace(request.EvaluationBasis)
                    ? "Projected amount against active thresholds"
                    : request.EvaluationBasis.Trim(),
                ExceedsClearlyTrivial = thresholds.ClearlyTrivialThreshold > 0 && evaluationAmount >= thresholds.ClearlyTrivialThreshold,
                ExceedsPerformanceMateriality = thresholds.PerformanceMateriality > 0 && evaluationAmount >= thresholds.PerformanceMateriality,
                ExceedsOverallMateriality = thresholds.OverallMateriality > 0 && evaluationAmount >= thresholds.OverallMateriality,
                Status = string.IsNullOrWhiteSpace(request.Status) ? "Open" : request.Status.Trim(),
                CreatedByUserId = request.CreatedByUserId,
                CreatedByName = request.CreatedByName
            };
        }

        private async Task<MaterialityThresholdRow> GetThresholdRowAsync(IDbConnection db, int referenceId, long? requestedCalculationId)
        {
            return await db.QueryFirstOrDefaultAsync<MaterialityThresholdRow>(@"
                WITH selected_calculation AS (
                    SELECT id, overall_materiality, performance_materiality, clearly_trivial_threshold
                    FROM audit_materiality_calculations
                    WHERE reference_id = @ReferenceId
                      AND (
                            (@CalculationId IS NOT NULL AND id = @CalculationId)
                         OR (@CalculationId IS NULL AND is_active = TRUE)
                      )
                    ORDER BY COALESCE(approved_at, created_at) DESC, id DESC
                    LIMIT 1
                )
                SELECT
                    sc.id AS MaterialityCalculationId,
                    COALESCE(sc.overall_materiality, plan.overall_materiality, 0) AS OverallMateriality,
                    COALESCE(sc.performance_materiality, plan.performance_materiality, 0) AS PerformanceMateriality,
                    COALESCE(sc.clearly_trivial_threshold, plan.clearly_trivial_threshold, 0) AS ClearlyTrivialThreshold
                FROM riskassessmentreference ref
                LEFT JOIN audit_engagement_plans plan ON plan.reference_id = ref.reference_id
                LEFT JOIN selected_calculation sc ON TRUE
                WHERE ref.reference_id = @ReferenceId;",
                new
                {
                    ReferenceId = referenceId,
                    CalculationId = requestedCalculationId
                }) ?? new MaterialityThresholdRow();
        }

        private async Task<int?> ResolveTrialBalanceYearAsync(IDbConnection db, int referenceId, int? fiscalYear)
        {
            return await db.ExecuteScalarAsync<int?>(@"
                SELECT COALESCE(@FiscalYear, MAX(fiscal_year))
                FROM audit_trial_balance_snapshots
                WHERE reference_id = @ReferenceId;",
                new { ReferenceId = referenceId, FiscalYear = fiscalYear });
        }

        private async Task<int?> ResolvePopulationYearAsync(
            IDbConnection db,
            string tableName,
            int referenceId,
            int? preferredYear,
            int? fallbackYear)
        {
            if (preferredYear.HasValue)
            {
                var exists = await db.ExecuteScalarAsync<bool>($@"
                    SELECT EXISTS(
                        SELECT 1
                        FROM {tableName}
                        WHERE reference_id = @ReferenceId
                          AND fiscal_year = @FiscalYear
                    );",
                    new { ReferenceId = referenceId, FiscalYear = preferredYear.Value });
                if (exists)
                    return preferredYear.Value;
            }

            return fallbackYear;
        }

        private static List<AuditMaterialityCandidate> BuildCandidateRows(
            IEnumerable<TrialBalanceMetricRow> rows,
            int referenceId,
            int fiscalYear,
            GenerateAuditMaterialityCandidatesRequest request,
            AuditMaterialityBenchmarkProfile benchmarkProfile,
            DateTime generatedAt)
        {
            var rowList = rows.ToList();
            var profileLabel = benchmarkProfile?.ProfileName;
            var validationStatus = benchmarkProfile?.ValidationStatus;

            var revenueAmount = Math.Abs(rowList.Where(IsRevenueRow).Sum(row => row.CurrentBalance));
            var expensesAmount = Math.Abs(rowList.Where(IsExpenseRow).Sum(row => row.CurrentBalance));
            var assetsAmount = rowList.Where(IsAssetRow).Sum(row => Math.Abs(row.CurrentBalance));
            var directProfitBeforeTaxAmount = Math.Abs(rowList.Where(IsProfitBeforeTaxRow).Sum(row => row.CurrentBalance));
            var derivedProfitBeforeTax = directProfitBeforeTaxAmount > 0
                ? directProfitBeforeTaxAmount
                : Math.Max(revenueAmount - expensesAmount, 0);

            var candidates = new List<AuditMaterialityCandidate>();
            AddCandidate(candidates, referenceId, fiscalYear, request, benchmarkProfile, generatedAt, "profit_before_tax", "Profit Before Tax", derivedProfitBeforeTax, request.ProfitBeforeTaxPercentage ?? 5m, request.PerformancePercentage ?? 75m, request.ClearlyTrivialPercentage ?? 5m,
                directProfitBeforeTaxAmount > 0
                    ? "Derived from trial balance lines matching profit-before-tax labels."
                    : "Derived as revenue less expenses because no direct profit-before-tax line was found.",
                profileLabel,
                validationStatus);
            AddCandidate(candidates, referenceId, fiscalYear, request, benchmarkProfile, generatedAt, "revenue", "Revenue", revenueAmount, request.RevenuePercentage ?? 1m, request.PerformancePercentage ?? 75m, request.ClearlyTrivialPercentage ?? 5m,
                "Derived from trial balance lines matching revenue, sales, turnover, or income labels.",
                profileLabel,
                validationStatus);
            AddCandidate(candidates, referenceId, fiscalYear, request, benchmarkProfile, generatedAt, "total_assets", "Total Assets", assetsAmount, request.TotalAssetsPercentage ?? 1m, request.PerformancePercentage ?? 75m, request.ClearlyTrivialPercentage ?? 5m,
                "Derived from trial balance lines matching asset-style FSLI or account labels.",
                profileLabel,
                validationStatus);
            AddCandidate(candidates, referenceId, fiscalYear, request, benchmarkProfile, generatedAt, "expenses", "Expenses", expensesAmount, request.ExpensesPercentage ?? 1m, request.PerformancePercentage ?? 75m, request.ClearlyTrivialPercentage ?? 5m,
                "Derived from trial balance lines matching expense and cost labels.",
                profileLabel,
                validationStatus);

            return candidates
                .Where(candidate => candidate.BenchmarkAmount > 0 && candidate.RecommendedOverallMateriality > 0)
                .OrderByDescending(candidate => candidate.RecommendedOverallMateriality)
                .ToList();
        }

        private static void AddCandidate(
            ICollection<AuditMaterialityCandidate> candidates,
            int referenceId,
            int fiscalYear,
            GenerateAuditMaterialityCandidatesRequest request,
            AuditMaterialityBenchmarkProfile benchmarkProfile,
            DateTime generatedAt,
            string candidateCode,
            string candidateName,
            decimal benchmarkAmount,
            decimal recommendedPercentage,
            decimal performancePercentage,
            decimal clearlyTrivialPercentage,
            string notes,
            string profileLabel,
            string validationStatus)
        {
            if (benchmarkAmount <= 0 || recommendedPercentage <= 0)
                return;

            var overallMateriality = CalculateAmount(benchmarkAmount, recommendedPercentage);
            var performanceMateriality = CalculateAmount(overallMateriality, performancePercentage);
            var clearlyTrivialThreshold = CalculateAmount(overallMateriality, clearlyTrivialPercentage);
            var noteSegments = new List<string> { notes };
            if (!string.IsNullOrWhiteSpace(profileLabel))
            {
                noteSegments.Add($"Profile: {profileLabel}");
            }
            if (!string.IsNullOrWhiteSpace(validationStatus))
            {
                noteSegments.Add($"Validation: {validationStatus}");
            }

            candidates.Add(new AuditMaterialityCandidate
            {
                ReferenceId = referenceId,
                FiscalYear = fiscalYear,
                BenchmarkProfileId = benchmarkProfile?.Id,
                BenchmarkProfileName = benchmarkProfile?.ProfileName,
                BenchmarkProfileValidationStatus = benchmarkProfile?.ValidationStatus,
                CandidateCode = candidateCode,
                CandidateName = candidateName,
                BenchmarkSource = "trial_balance",
                SourceTable = "audit_trial_balance_snapshots",
                SourceMetricLabel = $"{candidateName} benchmark from fiscal year {fiscalYear}",
                BenchmarkAmount = Math.Round(benchmarkAmount, 2),
                RecommendedPercentage = recommendedPercentage,
                RecommendedOverallMateriality = overallMateriality,
                RecommendedPerformancePercentage = performancePercentage,
                RecommendedPerformanceMateriality = performanceMateriality,
                RecommendedClearlyTrivialPercentage = clearlyTrivialPercentage,
                RecommendedClearlyTrivialThreshold = clearlyTrivialThreshold,
                Notes = string.Join(" ", noteSegments.Where(segment => !string.IsNullOrWhiteSpace(segment))),
                EntityType = NormalizeOptionalText(request.EntityType) ?? benchmarkProfile?.EntityType,
                IndustryName = NormalizeOptionalText(request.IndustryName) ?? benchmarkProfile?.IndustryName,
                IsSelected = false,
                SelectedCalculationId = null,
                GeneratedByUserId = request.GeneratedByUserId,
                GeneratedByName = request.GeneratedByName,
                GeneratedAt = generatedAt
            });
        }

        private static string NormalizeOptionalText(string value)
        {
            var normalized = value?.Trim();
            return string.IsNullOrWhiteSpace(normalized) ? null : normalized;
        }

        private static decimal CalculateAmount(decimal basisAmount, decimal percentage)
            => Math.Round(basisAmount * (percentage / 100m), 2);

        private static bool IsRevenueRow(TrialBalanceMetricRow row)
        {
            var label = GetLabel(row);
            return ContainsAny(label, "revenue", "sales", "turnover", "income");
        }

        private static bool IsExpenseRow(TrialBalanceMetricRow row)
        {
            var label = GetLabel(row);
            return ContainsAny(label, "expense", "cost of sales", "cost of goods", "operating cost", "operating expense", "administrative expense", "selling expense", "payroll", "salary", "depreciation");
        }

        private static bool IsAssetRow(TrialBalanceMetricRow row)
        {
            var label = GetLabel(row);
            return ContainsAny(label, "asset", "cash", "bank", "receivable", "inventory", "property", "plant", "equipment", "ppe", "intangible", "investment");
        }

        private static bool IsProfitBeforeTaxRow(TrialBalanceMetricRow row)
        {
            var label = GetLabel(row);
            return ContainsAny(label, "profit before tax", "income before tax", "pbt", "profit bt");
        }

        private static string GetLabel(TrialBalanceMetricRow row)
            => $"{row.AccountName} {row.Fsli}".Trim().ToLowerInvariant();

        private static bool ContainsAny(string text, params string[] tokens)
            => tokens.Any(token => text.Contains(token, StringComparison.OrdinalIgnoreCase));

        private sealed class TrialBalanceMetricRow
        {
            public string AccountName { get; set; }
            public string Fsli { get; set; }
            public decimal CurrentBalance { get; set; }
        }

        private sealed class MaterialityAvailabilityRow
        {
            public bool HasTrialBalanceData { get; set; }
            public int? LatestTrialBalanceYear { get; set; }
            public int TrialBalanceAccountCount { get; set; }
            public decimal TrialBalanceAbsoluteBalance { get; set; }
            public bool HasJournalData { get; set; }
            public int? LatestJournalYear { get; set; }
            public int JournalEntryCount { get; set; }
            public DateTime? LatestAnalyticsImportAt { get; set; }
        }

        private sealed class PopulationAggregateRow
        {
            public int PopulationItemCount { get; set; }
            public decimal PopulationAmount { get; set; }
            public int KeyItemCount { get; set; }
            public decimal KeyItemAmount { get; set; }
            public int SamplePoolCount { get; set; }
            public decimal SamplePoolAmount { get; set; }
        }

        private sealed class ScopeCandidateAggregateRow
        {
            public int ScopeCandidateCount { get; set; }
            public decimal ScopeCandidateBalance { get; set; }
        }

        private sealed class MisstatementAggregateRow
        {
            public int TotalRecordedMisstatements { get; set; }
            public decimal TotalActualAmount { get; set; }
            public decimal TotalProjectedAmount { get; set; }
            public int AboveClearlyTrivialCount { get; set; }
            public int AbovePerformanceMaterialityCount { get; set; }
            public int AboveOverallMaterialityCount { get; set; }
        }

        private sealed class MaterialityThresholdRow
        {
            public long? MaterialityCalculationId { get; set; }
            public decimal OverallMateriality { get; set; }
            public decimal PerformanceMateriality { get; set; }
            public decimal ClearlyTrivialThreshold { get; set; }
        }

        private sealed class NormalizedScopeLinkRow
        {
            public int ReferenceId { get; set; }
            public long MaterialityCalculationId { get; set; }
            public int? ScopeItemId { get; set; }
            public string Fsli { get; set; }
            public string BenchmarkRelevance { get; set; }
            public string InclusionReason { get; set; }
            public bool IsAboveThreshold { get; set; }
            public decimal? CoveragePercent { get; set; }
        }

        private sealed class NormalizedMisstatementRow
        {
            public int ReferenceId { get; set; }
            public int? FindingId { get; set; }
            public long? MaterialityCalculationId { get; set; }
            public string Fsli { get; set; }
            public string AccountNumber { get; set; }
            public string TransactionIdentifier { get; set; }
            public string Description { get; set; }
            public decimal ActualAmount { get; set; }
            public decimal? ProjectedAmount { get; set; }
            public string EvaluationBasis { get; set; }
            public bool ExceedsClearlyTrivial { get; set; }
            public bool ExceedsPerformanceMateriality { get; set; }
            public bool ExceedsOverallMateriality { get; set; }
            public string Status { get; set; }
            public int? CreatedByUserId { get; set; }
            public string CreatedByName { get; set; }
        }
    }
}
