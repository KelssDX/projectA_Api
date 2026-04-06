using Affine.Engine.Model.Auditing.AuditUniverse;
using Dapper;
using Npgsql;
using System;
using System.Collections.Generic;
using System.Data;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Affine.Engine.Repository.Auditing
{
    public class AuditReportingRepository : IAuditReportingRepository
    {
        private readonly string _connectionString;

        private const string RulePackageSelect = @"
            SELECT
                id AS Id,
                package_code AS PackageCode,
                package_name AS PackageName,
                domain_code AS DomainCode,
                description AS Description,
                is_default AS IsDefault,
                is_active AS IsActive
            FROM audit_domain_rule_packages";

        private const string MappingProfileSelect = @"
            SELECT
                profile.id AS Id,
                profile.reference_id AS ReferenceId,
                profile.engagement_type_id AS EngagementTypeId,
                et.name AS EngagementTypeName,
                profile.rule_package_id AS RulePackageId,
                pkg.package_code AS PackageCode,
                pkg.package_name AS PackageName,
                profile.profile_code AS ProfileCode,
                profile.profile_name AS ProfileName,
                profile.entity_type AS EntityType,
                profile.industry_name AS IndustryName,
                profile.notes AS Notes,
                profile.is_reusable AS IsReusable,
                profile.is_default AS IsDefault,
                profile.is_active AS IsActive,
                COALESCE(rule_counts.rule_count, 0) AS RuleCount,
                profile.created_by_name AS CreatedByName,
                profile.created_at AS CreatedAt
            FROM audit_financial_statement_mapping_profiles profile
            LEFT JOIN audit_domain_rule_packages pkg ON profile.rule_package_id = pkg.id
            LEFT JOIN ra_engagement_type et ON profile.engagement_type_id = et.id
            LEFT JOIN (
                SELECT mapping_profile_id, COUNT(*) AS rule_count
                FROM audit_financial_statement_profile_rules
                GROUP BY mapping_profile_id
            ) rule_counts ON profile.id = rule_counts.mapping_profile_id";

        private const string MappingSelect = @"
            WITH tb AS (
                SELECT
                    reference_id,
                    fiscal_year,
                    account_number,
                    MAX(account_name) AS account_name,
                    MAX(fsli) AS fsli,
                    MAX(business_unit) AS business_unit,
                    SUM(COALESCE(current_balance, 0)) AS current_balance
                FROM audit_trial_balance_snapshots
                WHERE reference_id = @ReferenceId
                  AND fiscal_year = @FiscalYear
                GROUP BY reference_id, fiscal_year, account_number
            )
            SELECT
                COALESCE(map.id, 0) AS Id,
                tb.reference_id AS ReferenceId,
                tb.fiscal_year AS FiscalYear,
                map.mapping_profile_id AS MappingProfileId,
                profile.profile_name AS MappingProfileName,
                tb.account_number AS AccountNumber,
                tb.account_name AS AccountName,
                tb.fsli AS Fsli,
                tb.business_unit AS BusinessUnit,
                tb.current_balance AS CurrentBalance,
                map.statement_type AS StatementType,
                map.section_name AS SectionName,
                map.line_name AS LineName,
                map.classification AS Classification,
                COALESCE(map.display_order, 100) AS DisplayOrder,
                map.notes AS Notes,
                COALESCE(map.is_auto_mapped, TRUE) AS IsAutoMapped,
                COALESCE(map.is_reviewed, FALSE) AS IsReviewed,
                map.updated_at AS UpdatedAt
            FROM tb
            LEFT JOIN audit_financial_statement_mappings map
                ON map.reference_id = tb.reference_id
               AND map.fiscal_year = tb.fiscal_year
               AND map.account_number = tb.account_number
            LEFT JOIN audit_financial_statement_mapping_profiles profile
                ON map.mapping_profile_id = profile.id";

        private const string SupportRequestSelect = @"
            SELECT
                request.id AS Id,
                request.reference_id AS ReferenceId,
                request.fiscal_year AS FiscalYear,
                request.source_type AS SourceType,
                request.source_record_id AS SourceRecordId,
                request.source_key AS SourceKey,
                request.transaction_identifier AS TransactionIdentifier,
                request.journal_number AS JournalNumber,
                request.posting_date AS PostingDate,
                request.account_number AS AccountNumber,
                request.account_name AS AccountName,
                request.fsli AS Fsli,
                request.amount AS Amount,
                request.description AS Description,
                request.triage_reason AS TriageReason,
                request.risk_flags AS RiskFlags,
                request.support_status AS SupportStatus,
                request.support_summary AS SupportSummary,
                request.linked_procedure_id AS LinkedProcedureId,
                procedure.procedure_title AS LinkedProcedureTitle,
                request.linked_walkthrough_id AS LinkedWalkthroughId,
                walkthrough.process_name AS LinkedWalkthroughTitle,
                request.linked_control_id AS LinkedControlId,
                control.control_name AS LinkedControlName,
                request.linked_finding_id AS LinkedFindingId,
                finding.finding_title AS LinkedFindingTitle,
                request.notes AS Notes,
                request.requested_at AS RequestedAt,
                request.updated_at AS UpdatedAt
            FROM audit_substantive_support_requests request
            LEFT JOIN audit_procedures procedure ON request.linked_procedure_id = procedure.id
            LEFT JOIN audit_walkthroughs walkthrough ON request.linked_walkthrough_id = walkthrough.id
            LEFT JOIN audit_risk_control_matrix control ON request.linked_control_id = control.id
            LEFT JOIN audit_findings finding ON request.linked_finding_id = finding.id";

        private const string FinalizationSelect = @"
            SELECT
                finalization.id AS Id,
                finalization.reference_id AS ReferenceId,
                finalization.active_mapping_profile_id AS ActiveMappingProfileId,
                profile.profile_name AS ActiveMappingProfileName,
                finalization.active_rule_package_id AS ActiveRulePackageId,
                package.package_code AS ActiveRulePackageCode,
                package.package_name AS ActiveRulePackageName,
                finalization.overall_conclusion AS OverallConclusion,
                finalization.recommendation_summary AS RecommendationSummary,
                finalization.release_readiness_status AS ReleaseReadinessStatus,
                finalization.draft_statement_status AS DraftStatementStatus,
                finalization.outstanding_items AS OutstandingItems,
                finalization.reviewer_notes AS ReviewerNotes,
                finalization.ready_for_release AS ReadyForRelease,
                finalization.last_generated_statement_year AS LastGeneratedStatementYear,
                finalization.last_generated_at AS LastGeneratedAt,
                finalization.updated_by_user_id AS UpdatedByUserId,
                finalization.updated_by_name AS UpdatedByName,
                finalization.updated_at AS UpdatedAt
            FROM audit_finance_finalization finalization
            LEFT JOIN audit_financial_statement_mapping_profiles profile ON finalization.active_mapping_profile_id = profile.id
            LEFT JOIN audit_domain_rule_packages package ON finalization.active_rule_package_id = package.id";

        public AuditReportingRepository(string connectionString)
        {
            _connectionString = connectionString ?? throw new ArgumentNullException(nameof(connectionString));
        }

        public async Task<PowerBIReconciliationResponse> GetPowerBIReconciliationAsync(int? referenceId)
        {
            using IDbConnection db = new NpgsqlConnection(_connectionString);
            db.Open();

            var reporting = await db.QueryFirstOrDefaultAsync<ReportingAggregateRow>(@"
                SELECT
                    COALESCE(f.total_findings, 0) AS TotalFindings,
                    COALESCE(f.open_findings, 0) AS OpenFindings,
                    COALESCE(f.total_recommendations, 0) AS TotalRecommendations,
                    COALESCE(f.open_recommendations, 0) AS OpenRecommendations,
                    COALESCE(f.overdue_management_actions, 0) AS OverdueManagementActions,
                    COALESCE(e.total_working_papers, 0) AS TotalWorkingPapers,
                    COALESCE(e.signed_off_working_papers, 0) AS SignedOffWorkingPapers,
                    COALESCE(e.total_documents, 0) AS TotalDocuments,
                    COALESCE(e.open_evidence_requests, 0) AS OpenEvidenceRequests,
                    COALESCE(e.active_workflows, 0) AS ActiveWorkflows,
                    COALESCE(e.pending_workflow_tasks, 0) AS PendingWorkflowTasks,
                    COALESCE(a.journal_entry_rows, 0) AS JournalEntryRows,
                    COALESCE(a.trial_balance_accounts, 0) AS TrialBalanceAccounts,
                    COALESCE(a.industry_benchmark_metrics, 0) AS IndustryBenchmarkMetrics,
                    COALESCE(a.reasonability_forecast_metrics, 0) AS ReasonabilityForecastMetrics
                FROM (SELECT 1 AS stub) seed
                LEFT JOIN (
                    SELECT
                        COALESCE(SUM(total_findings), 0) AS total_findings,
                        COALESCE(SUM(open_findings), 0) AS open_findings,
                        COALESCE(SUM(total_recommendations), 0) AS total_recommendations,
                        COALESCE(SUM(open_recommendations), 0) AS open_recommendations,
                        COALESCE(SUM(overdue_management_actions), 0) AS overdue_management_actions
                    FROM vw_audit_reporting_findings_summary
                    WHERE (@ReferenceId IS NULL OR reference_id = @ReferenceId)
                ) f ON TRUE
                LEFT JOIN (
                    SELECT
                        COALESCE(SUM(total_working_papers), 0) AS total_working_papers,
                        COALESCE(SUM(signed_off_working_papers), 0) AS signed_off_working_papers,
                        COALESCE(SUM(total_documents), 0) AS total_documents,
                        COALESCE(SUM(open_evidence_requests), 0) AS open_evidence_requests,
                        COALESCE(SUM(active_workflows), 0) AS active_workflows,
                        COALESCE(SUM(pending_workflow_tasks), 0) AS pending_workflow_tasks
                    FROM vw_audit_reporting_execution_summary
                    WHERE (@ReferenceId IS NULL OR reference_id = @ReferenceId)
                ) e ON TRUE
                LEFT JOIN (
                    SELECT
                        COALESCE(SUM(journal_entry_rows), 0) AS journal_entry_rows,
                        COALESCE(SUM(trial_balance_accounts), 0) AS trial_balance_accounts,
                        COALESCE(SUM(industry_benchmark_metrics), 0) AS industry_benchmark_metrics,
                        COALESCE(SUM(reasonability_forecast_metrics), 0) AS reasonability_forecast_metrics
                    FROM vw_audit_reporting_analytics_summary
                    WHERE (@ReferenceId IS NULL OR reference_id = @ReferenceId)
                ) a ON TRUE;",
                new { ReferenceId = referenceId }) ?? new ReportingAggregateRow();

            var native = await db.QueryFirstOrDefaultAsync<ReportingAggregateRow>(@"
                WITH finding_summary AS (
                    SELECT
                        COUNT(*) AS total_findings,
                        COUNT(*) FILTER (WHERE COALESCE(fs.is_closed, FALSE) = FALSE) AS open_findings
                    FROM audit_findings f
                    LEFT JOIN ra_finding_status fs ON fs.id = f.status_id
                    WHERE (@ReferenceId IS NULL OR f.reference_id = @ReferenceId)
                ),
                recommendation_summary AS (
                    SELECT
                        COUNT(*) AS total_recommendations,
                        COUNT(*) FILTER (
                            WHERE COALESCE(rs.name, 'Pending') NOT IN ('Implemented', 'Rejected', 'Deferred')
                        ) AS open_recommendations
                    FROM audit_recommendations r
                    INNER JOIN audit_findings f ON f.id = r.finding_id
                    LEFT JOIN ra_recommendation_status rs ON rs.id = r.status_id
                    WHERE (@ReferenceId IS NULL OR f.reference_id = @ReferenceId)
                ),
                management_action_summary AS (
                    SELECT
                        COUNT(*) FILTER (
                            WHERE due_date < CURRENT_DATE
                              AND LOWER(COALESCE(status, 'open')) NOT IN ('closed', 'completed', 'validated', 'cancelled', 'canceled')
                        ) AS overdue_management_actions
                    FROM audit_management_actions
                    WHERE (@ReferenceId IS NULL OR reference_id = @ReferenceId)
                ),
                working_paper_summary AS (
                    SELECT
                        COUNT(*) FILTER (WHERE COALESCE(wp.is_template, FALSE) = FALSE AND COALESCE(wp.is_active, TRUE) = TRUE) AS total_working_papers,
                        COUNT(DISTINCT CASE WHEN s.id IS NOT NULL THEN wp.id END) FILTER (WHERE COALESCE(wp.is_template, FALSE) = FALSE AND COALESCE(wp.is_active, TRUE) = TRUE) AS signed_off_working_papers
                    FROM audit_working_papers wp
                    LEFT JOIN audit_working_paper_signoffs s ON s.working_paper_id = wp.id
                    WHERE (@ReferenceId IS NULL OR wp.reference_id = @ReferenceId)
                ),
                document_summary AS (
                    SELECT COUNT(*) FILTER (WHERE COALESCE(is_active, TRUE) = TRUE) AS total_documents
                    FROM audit_documents
                    WHERE (@ReferenceId IS NULL OR reference_id = @ReferenceId)
                ),
                evidence_summary AS (
                    SELECT COUNT(*) FILTER (WHERE COALESCE(es.is_closed, FALSE) = FALSE) AS open_evidence_requests
                    FROM audit_evidence_requests er
                    LEFT JOIN ra_evidence_request_status es ON es.id = er.status_id
                    WHERE (@ReferenceId IS NULL OR er.reference_id = @ReferenceId)
                ),
                workflow_summary AS (
                    SELECT COUNT(*) FILTER (WHERE COALESCE(is_active, FALSE) = TRUE) AS active_workflows
                    FROM audit_workflow_instances
                    WHERE (@ReferenceId IS NULL OR reference_id = @ReferenceId)
                ),
                task_summary AS (
                    SELECT COUNT(*) FILTER (WHERE LOWER(COALESCE(status, 'pending')) = 'pending') AS pending_workflow_tasks
                    FROM audit_workflow_tasks
                    WHERE (@ReferenceId IS NULL OR reference_id = @ReferenceId)
                ),
                analytics_summary AS (
                    SELECT
                        (SELECT COUNT(*) FROM audit_gl_journal_entries WHERE (@ReferenceId IS NULL OR reference_id = @ReferenceId)) AS journal_entry_rows,
                        (SELECT COUNT(*) FROM audit_trial_balance_snapshots WHERE (@ReferenceId IS NULL OR reference_id = @ReferenceId)) AS trial_balance_accounts,
                        (SELECT COUNT(*) FROM audit_industry_benchmarks WHERE (@ReferenceId IS NULL OR reference_id = @ReferenceId)) AS industry_benchmark_metrics,
                        (SELECT COUNT(*) FROM audit_reasonability_forecasts WHERE (@ReferenceId IS NULL OR reference_id = @ReferenceId)) AS reasonability_forecast_metrics
                )
                SELECT
                    COALESCE(finding_summary.total_findings, 0) AS TotalFindings,
                    COALESCE(finding_summary.open_findings, 0) AS OpenFindings,
                    COALESCE(recommendation_summary.total_recommendations, 0) AS TotalRecommendations,
                    COALESCE(recommendation_summary.open_recommendations, 0) AS OpenRecommendations,
                    COALESCE(management_action_summary.overdue_management_actions, 0) AS OverdueManagementActions,
                    COALESCE(working_paper_summary.total_working_papers, 0) AS TotalWorkingPapers,
                    COALESCE(working_paper_summary.signed_off_working_papers, 0) AS SignedOffWorkingPapers,
                    COALESCE(document_summary.total_documents, 0) AS TotalDocuments,
                    COALESCE(evidence_summary.open_evidence_requests, 0) AS OpenEvidenceRequests,
                    COALESCE(workflow_summary.active_workflows, 0) AS ActiveWorkflows,
                    COALESCE(task_summary.pending_workflow_tasks, 0) AS PendingWorkflowTasks,
                    COALESCE(analytics_summary.journal_entry_rows, 0) AS JournalEntryRows,
                    COALESCE(analytics_summary.trial_balance_accounts, 0) AS TrialBalanceAccounts,
                    COALESCE(analytics_summary.industry_benchmark_metrics, 0) AS IndustryBenchmarkMetrics,
                    COALESCE(analytics_summary.reasonability_forecast_metrics, 0) AS ReasonabilityForecastMetrics
                FROM finding_summary
                CROSS JOIN recommendation_summary
                CROSS JOIN management_action_summary
                CROSS JOIN working_paper_summary
                CROSS JOIN document_summary
                CROSS JOIN evidence_summary
                CROSS JOIN workflow_summary
                CROSS JOIN task_summary
                CROSS JOIN analytics_summary;",
                new { ReferenceId = referenceId }) ?? new ReportingAggregateRow();

            var metrics = BuildMetrics(native, reporting);

            return new PowerBIReconciliationResponse
            {
                ReferenceId = referenceId,
                DataMartStatus = "Ready",
                GeneratedAt = DateTime.UtcNow,
                MatchedMetrics = metrics.Count(metric => metric.IsMatched),
                MismatchedMetrics = metrics.Count(metric => !metric.IsMatched),
                Metrics = metrics
            };
        }

        public async Task<AuditFinanceAuditWorkspace> GetFinanceAuditWorkspaceAsync(int referenceId)
        {
            if (referenceId <= 0)
                throw new InvalidOperationException("Reference ID is required.");

            await using var db = new NpgsqlConnection(_connectionString);
            await db.OpenAsync();

            var workspace = await db.QueryFirstOrDefaultAsync<AuditFinanceAuditWorkspace>(@"
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
                    ref.reference_id AS ReferenceId,
                    COALESCE(plan.engagement_title, NULLIF(ref.title, ''), ref.client, CONCAT('Audit File ', ref.reference_id)) AS EngagementTitle,
                    plan.plan_year AS PlanYear,
                    EXISTS(SELECT 1 FROM audit_trial_balance_snapshots tb WHERE tb.reference_id = @ReferenceId) AS HasTrialBalanceData,
                    (SELECT latest_year FROM latest_tb) AS LatestTrialBalanceYear,
                    COALESCE((
                        SELECT COUNT(*)
                        FROM audit_trial_balance_snapshots tb
                        WHERE tb.reference_id = @ReferenceId
                          AND tb.fiscal_year = (SELECT latest_year FROM latest_tb)
                    ), 0) AS TrialBalanceAccountCount,
                    EXISTS(SELECT 1 FROM audit_gl_journal_entries je WHERE je.reference_id = @ReferenceId) AS HasJournalData,
                    (SELECT latest_year FROM latest_journal) AS LatestJournalYear,
                    COALESCE((
                        SELECT COUNT(*)
                        FROM audit_gl_journal_entries je
                        WHERE je.reference_id = @ReferenceId
                          AND je.fiscal_year = (SELECT latest_year FROM latest_journal)
                    ), 0) AS JournalEntryCount
                FROM riskassessmentreference ref
                LEFT JOIN audit_engagement_plans plan ON plan.reference_id = ref.reference_id
                WHERE ref.reference_id = @ReferenceId;",
                new { ReferenceId = referenceId }) ?? new AuditFinanceAuditWorkspace { ReferenceId = referenceId };

            workspace.RulePackages = await GetRulePackagesInternalAsync(db);
            workspace.Finalization = await GetFinalizationInternalAsync(db, referenceId);
            workspace.MappingProfiles = await GetMappingProfilesInternalAsync(db, referenceId);

            var financePackage = workspace.RulePackages.FirstOrDefault(pkg => pkg.Id == workspace.Finalization.ActiveRulePackageId)
                ?? workspace.RulePackages.FirstOrDefault(pkg => pkg.IsDefault)
                ?? workspace.RulePackages.FirstOrDefault();
            if (financePackage != null)
            {
                workspace.RulePackageCode = financePackage.PackageCode;
                workspace.RulePackageName = financePackage.PackageName;
            }

            var activeProfile = workspace.MappingProfiles.FirstOrDefault(profile => profile.Id == workspace.Finalization.ActiveMappingProfileId)
                ?? workspace.MappingProfiles.FirstOrDefault(profile => profile.IsDefault)
                ?? workspace.MappingProfiles.FirstOrDefault();
            if (activeProfile != null)
            {
                workspace.ActiveMappingProfileId = activeProfile.Id;
                workspace.ActiveMappingProfileName = activeProfile.ProfileName;
            }

            if (workspace.LatestTrialBalanceYear.HasValue)
            {
                workspace.TrialBalanceMappings = await GetMappingsInternalAsync(db, referenceId, workspace.LatestTrialBalanceYear.Value);
                workspace.MappingCount = workspace.TrialBalanceMappings.Count(item =>
                    !string.IsNullOrWhiteSpace(item.StatementType)
                    && !string.IsNullOrWhiteSpace(item.SectionName)
                    && !string.IsNullOrWhiteSpace(item.LineName));
                workspace.UnmappedAccountCount = workspace.TrialBalanceMappings.Count(item => string.IsNullOrWhiteSpace(item.StatementType));
                workspace.DraftStatements = await BuildDraftStatementsInternalAsync(db, referenceId, workspace.LatestTrialBalanceYear.Value);
            }

            if (workspace.LatestJournalYear.HasValue)
            {
                workspace.SupportRequests = await GetSupportRequestsInternalAsync(db, referenceId, workspace.LatestJournalYear.Value);
                workspace.SupportRequestCount = workspace.SupportRequests.Count;
                workspace.OpenSupportRequestCount = workspace.SupportRequests.Count(item =>
                    !string.Equals(item.SupportStatus, "Cleared", StringComparison.OrdinalIgnoreCase)
                    && !string.Equals(item.SupportStatus, "Received", StringComparison.OrdinalIgnoreCase));
            }

            return workspace;
        }

        public async Task<List<AuditFinancialStatementMappingItem>> GenerateTrialBalanceMappingsAsync(GenerateTrialBalanceMappingsRequest request)
        {
            if (request == null)
                throw new ArgumentNullException(nameof(request));
            if (request.ReferenceId <= 0)
                throw new InvalidOperationException("Reference ID is required.");

            await using var db = new NpgsqlConnection(_connectionString);
            await db.OpenAsync();

            var fiscalYear = await ResolveLatestTrialBalanceYearAsync(db, request.ReferenceId, request.FiscalYear);
            if (!fiscalYear.HasValue)
                throw new InvalidOperationException("Import a trial balance before generating mappings.");

            var selectedProfileId = await ResolvePreferredMappingProfileAsync(db, request.ReferenceId, request.MappingProfileId);
            var profileRules = await GetProfileRulesInternalAsync(db, selectedProfileId);
            var ruleLookup = profileRules
                .Where(rule => !string.IsNullOrWhiteSpace(rule.AccountNumber))
                .GroupBy(rule => rule.AccountNumber, StringComparer.OrdinalIgnoreCase)
                .ToDictionary(group => group.Key, group => group.First(), StringComparer.OrdinalIgnoreCase);

            var existingMappings = await GetMappingsInternalAsync(db, request.ReferenceId, fiscalYear.Value);
            var existingByAccount = existingMappings
                .Where(item => !string.IsNullOrWhiteSpace(item.AccountNumber))
                .GroupBy(item => item.AccountNumber, StringComparer.OrdinalIgnoreCase)
                .ToDictionary(group => group.Key, group => group.First(), StringComparer.OrdinalIgnoreCase);

            var trialBalanceRows = (await db.QueryAsync<TrialBalanceSourceRow>(@"
                WITH normalized AS (
                    SELECT
                        reference_id,
                        fiscal_year,
                        COALESCE(NULLIF(TRIM(account_number), ''), NULLIF(TRIM(account_name), ''), CONCAT('TB-', id)) AS account_number,
                        account_name,
                        fsli,
                        business_unit,
                        COALESCE(current_balance, 0) AS current_balance
                    FROM audit_trial_balance_snapshots
                    WHERE reference_id = @ReferenceId
                      AND fiscal_year = @FiscalYear
                )
                SELECT
                    reference_id AS ReferenceId,
                    fiscal_year AS FiscalYear,
                    account_number AS AccountNumber,
                    MAX(account_name) AS AccountName,
                    MAX(fsli) AS Fsli,
                    MAX(business_unit) AS BusinessUnit,
                    SUM(current_balance) AS CurrentBalance
                FROM normalized
                GROUP BY reference_id, fiscal_year, account_number;",
                new { request.ReferenceId, FiscalYear = fiscalYear.Value })).ToList();

            if (!trialBalanceRows.Any())
                throw new InvalidOperationException("The selected audit file has no trial balance rows to map.");

            var defaultRulePackageId = await ResolveDefaultRulePackageIdAsync(db);
            await using var transaction = await db.BeginTransactionAsync();

            const string upsertMappingSql = @"
                INSERT INTO audit_financial_statement_mappings
                (
                    reference_id,
                    fiscal_year,
                    mapping_profile_id,
                    account_number,
                    account_name,
                    fsli,
                    business_unit,
                    current_balance,
                    statement_type,
                    section_name,
                    line_name,
                    classification,
                    display_order,
                    notes,
                    is_auto_mapped,
                    is_reviewed
                )
                VALUES
                (
                    @ReferenceId,
                    @FiscalYear,
                    @MappingProfileId,
                    @AccountNumber,
                    @AccountName,
                    @Fsli,
                    @BusinessUnit,
                    @CurrentBalance,
                    @StatementType,
                    @SectionName,
                    @LineName,
                    @Classification,
                    @DisplayOrder,
                    @Notes,
                    @IsAutoMapped,
                    @IsReviewed
                )
                ON CONFLICT (reference_id, fiscal_year, account_number)
                DO UPDATE SET
                    mapping_profile_id = EXCLUDED.mapping_profile_id,
                    account_name = EXCLUDED.account_name,
                    fsli = EXCLUDED.fsli,
                    business_unit = EXCLUDED.business_unit,
                    current_balance = EXCLUDED.current_balance,
                    statement_type = EXCLUDED.statement_type,
                    section_name = EXCLUDED.section_name,
                    line_name = EXCLUDED.line_name,
                    classification = EXCLUDED.classification,
                    display_order = EXCLUDED.display_order,
                    notes = EXCLUDED.notes,
                    is_auto_mapped = EXCLUDED.is_auto_mapped,
                    is_reviewed = EXCLUDED.is_reviewed;";

            foreach (var row in trialBalanceRows)
            {
                existingByAccount.TryGetValue(row.AccountNumber ?? string.Empty, out var existing);
                var preserveReviewed = existing != null && existing.IsReviewed && !request.OverwriteReviewedMappings;
                var suggestion = preserveReviewed
                    ? MappingSuggestion.FromExisting(existing)
                    : DetermineSuggestedMapping(row, ruleLookup, selectedProfileId);

                await db.ExecuteAsync(
                    upsertMappingSql,
                    new
                    {
                        ReferenceId = request.ReferenceId,
                        FiscalYear = fiscalYear.Value,
                        MappingProfileId = preserveReviewed ? existing.MappingProfileId : suggestion?.MappingProfileId,
                        AccountNumber = row.AccountNumber,
                        AccountName = row.AccountName,
                        Fsli = row.Fsli,
                        BusinessUnit = row.BusinessUnit,
                        CurrentBalance = row.CurrentBalance,
                        StatementType = suggestion?.StatementType,
                        SectionName = suggestion?.SectionName,
                        LineName = suggestion?.LineName,
                        Classification = suggestion?.Classification,
                        DisplayOrder = suggestion?.DisplayOrder ?? 999,
                        Notes = preserveReviewed
                            ? NormalizeOptionalText(existing.Notes)
                            : NormalizeOptionalText(suggestion?.Notes) ?? "Awaiting reviewer confirmation.",
                        IsAutoMapped = preserveReviewed ? existing.IsAutoMapped : suggestion != null,
                        IsReviewed = preserveReviewed && existing.IsReviewed
                    },
                    transaction);
            }

            await EnsureFinanceFinalizationAsync(
                db,
                request.ReferenceId,
                selectedProfileId,
                defaultRulePackageId,
                request.GeneratedByUserId,
                NormalizeOptionalText(request.GeneratedByName),
                transaction);

            await transaction.CommitAsync();
            return await GetMappingsInternalAsync(db, request.ReferenceId, fiscalYear.Value);
        }

        public async Task<AuditFinancialStatementMappingItem> SaveTrialBalanceMappingAsync(SaveTrialBalanceMappingRequest request)
        {
            if (request == null)
                throw new ArgumentNullException(nameof(request));
            if (request.ReferenceId <= 0)
                throw new InvalidOperationException("Reference ID is required.");
            if (request.FiscalYear <= 0)
                throw new InvalidOperationException("Fiscal year is required.");
            if (string.IsNullOrWhiteSpace(request.AccountNumber))
                throw new InvalidOperationException("Account number is required.");

            await using var db = new NpgsqlConnection(_connectionString);
            await db.OpenAsync();

            var mappingProfileId = request.MappingProfileId ?? await ResolvePreferredMappingProfileAsync(db, request.ReferenceId, null);
            var defaultRulePackageId = await ResolveDefaultRulePackageIdAsync(db);
            await using var transaction = await db.BeginTransactionAsync();

            await db.ExecuteAsync(@"
                INSERT INTO audit_financial_statement_mappings
                (
                    reference_id,
                    fiscal_year,
                    mapping_profile_id,
                    account_number,
                    account_name,
                    fsli,
                    business_unit,
                    current_balance,
                    statement_type,
                    section_name,
                    line_name,
                    classification,
                    display_order,
                    notes,
                    is_auto_mapped,
                    is_reviewed
                )
                VALUES
                (
                    @ReferenceId,
                    @FiscalYear,
                    @MappingProfileId,
                    @AccountNumber,
                    @AccountName,
                    @Fsli,
                    @BusinessUnit,
                    @CurrentBalance,
                    @StatementType,
                    @SectionName,
                    @LineName,
                    @Classification,
                    @DisplayOrder,
                    @Notes,
                    @IsAutoMapped,
                    @IsReviewed
                )
                ON CONFLICT (reference_id, fiscal_year, account_number)
                DO UPDATE SET
                    mapping_profile_id = EXCLUDED.mapping_profile_id,
                    account_name = EXCLUDED.account_name,
                    fsli = EXCLUDED.fsli,
                    business_unit = EXCLUDED.business_unit,
                    current_balance = EXCLUDED.current_balance,
                    statement_type = EXCLUDED.statement_type,
                    section_name = EXCLUDED.section_name,
                    line_name = EXCLUDED.line_name,
                    classification = EXCLUDED.classification,
                    display_order = EXCLUDED.display_order,
                    notes = EXCLUDED.notes,
                    is_auto_mapped = EXCLUDED.is_auto_mapped,
                    is_reviewed = EXCLUDED.is_reviewed;",
                new
                {
                    request.ReferenceId,
                    request.FiscalYear,
                    MappingProfileId = mappingProfileId,
                    AccountNumber = NormalizeOptionalText(request.AccountNumber),
                    AccountName = NormalizeOptionalText(request.AccountName),
                    Fsli = NormalizeOptionalText(request.Fsli),
                    BusinessUnit = NormalizeOptionalText(request.BusinessUnit),
                    request.CurrentBalance,
                    StatementType = NormalizeOptionalText(request.StatementType),
                    SectionName = NormalizeOptionalText(request.SectionName),
                    LineName = NormalizeOptionalText(request.LineName),
                    Classification = NormalizeOptionalText(request.Classification),
                    request.DisplayOrder,
                    Notes = NormalizeOptionalText(request.Notes),
                    request.IsAutoMapped,
                    request.IsReviewed
                },
                transaction);

            await EnsureFinanceFinalizationAsync(
                db,
                request.ReferenceId,
                mappingProfileId,
                defaultRulePackageId,
                null,
                null,
                transaction);

            await transaction.CommitAsync();
            var mappings = await GetMappingsInternalAsync(db, request.ReferenceId, request.FiscalYear);
            return mappings.FirstOrDefault(item =>
                string.Equals(item.AccountNumber, request.AccountNumber, StringComparison.OrdinalIgnoreCase));
        }

        public async Task<AuditFinancialStatementMappingProfile> SaveMappingProfileFromCurrentAsync(SaveAuditMappingProfileRequest request)
        {
            if (request == null)
                throw new ArgumentNullException(nameof(request));
            if (request.ReferenceId <= 0)
                throw new InvalidOperationException("Reference ID is required.");
            if (string.IsNullOrWhiteSpace(request.ProfileName))
                throw new InvalidOperationException("Profile name is required.");

            await using var db = new NpgsqlConnection(_connectionString);
            await db.OpenAsync();

            var fiscalYear = await ResolveLatestTrialBalanceYearAsync(db, request.ReferenceId, request.FiscalYear);
            if (!fiscalYear.HasValue)
                throw new InvalidOperationException("Import and classify a trial balance before saving a mapping profile.");

            var currentMappings = (await GetMappingsInternalAsync(db, request.ReferenceId, fiscalYear.Value))
                .Where(item =>
                    !string.IsNullOrWhiteSpace(item.StatementType)
                    && !string.IsNullOrWhiteSpace(item.SectionName)
                    && !string.IsNullOrWhiteSpace(item.LineName))
                .ToList();

            if (!currentMappings.Any())
                throw new InvalidOperationException("Generate or review trial balance mappings before saving a profile.");

            var engagementTypeId = await db.ExecuteScalarAsync<int?>(@"
                SELECT engagement_type_id
                FROM audit_engagement_plans
                WHERE reference_id = @ReferenceId;",
                new { request.ReferenceId });
            var rulePackageId = request.RulePackageId ?? await ResolveDefaultRulePackageIdAsync(db);
            var profileCode = await BuildUniqueProfileCodeAsync(db, request.ProfileName);
            var profileReferenceId = request.IsReusable ? (int?)null : request.ReferenceId;

            await using var transaction = await db.BeginTransactionAsync();

            var profileId = await db.ExecuteScalarAsync<int>(@"
                INSERT INTO audit_financial_statement_mapping_profiles
                (
                    reference_id,
                    engagement_type_id,
                    rule_package_id,
                    profile_code,
                    profile_name,
                    entity_type,
                    industry_name,
                    notes,
                    is_reusable,
                    is_default,
                    is_active,
                    created_by_user_id,
                    created_by_name
                )
                VALUES
                (
                    @ReferenceId,
                    @EngagementTypeId,
                    @RulePackageId,
                    @ProfileCode,
                    @ProfileName,
                    @EntityType,
                    @IndustryName,
                    @Notes,
                    @IsReusable,
                    FALSE,
                    TRUE,
                    @CreatedByUserId,
                    @CreatedByName
                )
                RETURNING id;",
                new
                {
                    ReferenceId = profileReferenceId,
                    EngagementTypeId = engagementTypeId,
                    RulePackageId = rulePackageId,
                    ProfileCode = profileCode,
                    ProfileName = NormalizeOptionalText(request.ProfileName),
                    EntityType = NormalizeOptionalText(request.EntityType),
                    IndustryName = NormalizeOptionalText(request.IndustryName),
                    Notes = NormalizeOptionalText(request.Notes),
                    request.IsReusable,
                    request.CreatedByUserId,
                    CreatedByName = NormalizeOptionalText(request.CreatedByName)
                },
                transaction);

            const string insertRuleSql = @"
                INSERT INTO audit_financial_statement_profile_rules
                (
                    mapping_profile_id,
                    account_number,
                    account_name,
                    fsli,
                    statement_type,
                    section_name,
                    line_name,
                    classification,
                    display_order,
                    notes
                )
                VALUES
                (
                    @MappingProfileId,
                    @AccountNumber,
                    @AccountName,
                    @Fsli,
                    @StatementType,
                    @SectionName,
                    @LineName,
                    @Classification,
                    @DisplayOrder,
                    @Notes
                );";

            foreach (var mapping in currentMappings)
            {
                await db.ExecuteAsync(
                    insertRuleSql,
                    new
                    {
                        MappingProfileId = profileId,
                        AccountNumber = NormalizeOptionalText(mapping.AccountNumber),
                        AccountName = NormalizeOptionalText(mapping.AccountName),
                        Fsli = NormalizeOptionalText(mapping.Fsli),
                        StatementType = NormalizeOptionalText(mapping.StatementType),
                        SectionName = NormalizeOptionalText(mapping.SectionName),
                        LineName = NormalizeOptionalText(mapping.LineName),
                        Classification = NormalizeOptionalText(mapping.Classification),
                        mapping.DisplayOrder,
                        Notes = NormalizeOptionalText(mapping.Notes)
                    },
                    transaction);
            }

            if (request.SetAsActive)
            {
                await EnsureFinanceFinalizationAsync(
                    db,
                    request.ReferenceId,
                    profileId,
                    rulePackageId,
                    request.CreatedByUserId,
                    NormalizeOptionalText(request.CreatedByName),
                    transaction);
            }

            await transaction.CommitAsync();
            return await GetMappingProfileByIdAsync(db, profileId);
        }

        public async Task<List<AuditDraftFinancialStatement>> GenerateDraftFinancialStatementsAsync(GenerateDraftFinancialStatementsRequest request)
        {
            if (request == null)
                throw new ArgumentNullException(nameof(request));
            if (request.ReferenceId <= 0)
                throw new InvalidOperationException("Reference ID is required.");

            await using var db = new NpgsqlConnection(_connectionString);
            await db.OpenAsync();

            var fiscalYear = await ResolveLatestTrialBalanceYearAsync(db, request.ReferenceId, request.FiscalYear);
            if (!fiscalYear.HasValue)
                throw new InvalidOperationException("Import and map a trial balance before generating draft financial statements.");

            var statements = await BuildDraftStatementsInternalAsync(db, request.ReferenceId, fiscalYear.Value);
            if (!statements.Any())
                throw new InvalidOperationException("No classified trial balance mappings are available for draft statement generation.");

            var activeProfileId = request.MappingProfileId ?? await ResolvePreferredMappingProfileAsync(db, request.ReferenceId, null);
            var defaultRulePackageId = await ResolveDefaultRulePackageIdAsync(db);
            await using var transaction = await db.BeginTransactionAsync();

            await EnsureFinanceFinalizationAsync(
                db,
                request.ReferenceId,
                activeProfileId,
                defaultRulePackageId,
                request.GeneratedByUserId,
                NormalizeOptionalText(request.GeneratedByName),
                transaction);

            await db.ExecuteAsync(@"
                UPDATE audit_finance_finalization
                SET
                    active_mapping_profile_id = COALESCE(@ActiveMappingProfileId, active_mapping_profile_id),
                    active_rule_package_id = COALESCE(@ActiveRulePackageId, active_rule_package_id),
                    draft_statement_status = 'Generated',
                    last_generated_statement_year = @FiscalYear,
                    last_generated_at = CURRENT_TIMESTAMP,
                    updated_by_user_id = COALESCE(@UpdatedByUserId, updated_by_user_id),
                    updated_by_name = COALESCE(@UpdatedByName, updated_by_name)
                WHERE reference_id = @ReferenceId;",
                new
                {
                    request.ReferenceId,
                    FiscalYear = fiscalYear.Value,
                    ActiveMappingProfileId = activeProfileId,
                    ActiveRulePackageId = defaultRulePackageId,
                    UpdatedByUserId = request.GeneratedByUserId,
                    UpdatedByName = NormalizeOptionalText(request.GeneratedByName)
                },
                transaction);

            await transaction.CommitAsync();
            return statements;
        }

        public async Task<List<AuditSubstantiveSupportRequest>> GenerateSupportQueueAsync(GenerateAuditSupportQueueRequest request)
        {
            if (request == null)
                throw new ArgumentNullException(nameof(request));
            if (request.ReferenceId <= 0)
                throw new InvalidOperationException("Reference ID is required.");

            await using var db = new NpgsqlConnection(_connectionString);
            await db.OpenAsync();

            var fiscalYear = await ResolveLatestJournalYearAsync(db, request.ReferenceId, request.FiscalYear);
            if (!fiscalYear.HasValue)
                throw new InvalidOperationException("Import journal entries before generating the support queue.");

            var threshold = await ResolveMaterialityThresholdAsync(db, request.ReferenceId);
            var holidayDates = (await db.QueryAsync<DateTime>(@"
                SELECT holiday_date
                FROM audit_holiday_calendar
                WHERE is_active = TRUE;"))
                .Select(date => date.Date)
                .ToHashSet();

            var journalRows = (await db.QueryAsync<JournalSelectionRow>(@"
                SELECT
                    id AS Id,
                    reference_id AS ReferenceId,
                    fiscal_year AS FiscalYear,
                    posting_date AS PostingDate,
                    fiscal_period AS FiscalPeriod,
                    journal_number AS JournalNumber,
                    line_number AS LineNumber,
                    account_number AS AccountNumber,
                    account_name AS AccountName,
                    fsli AS Fsli,
                    description AS Description,
                    COALESCE(amount, COALESCE(debit_amount, 0) - COALESCE(credit_amount, 0)) AS Amount,
                    COALESCE(is_manual, FALSE) AS IsManual,
                    COALESCE(is_period_end, FALSE) AS IsPeriodEnd
                FROM audit_gl_journal_entries
                WHERE reference_id = @ReferenceId
                  AND fiscal_year = @FiscalYear;",
                new { request.ReferenceId, FiscalYear = fiscalYear.Value })).ToList();

            if (!journalRows.Any())
                throw new InvalidOperationException("The selected audit file has no journal-entry data for support queue generation.");

            await using var transaction = await db.BeginTransactionAsync();
            const string upsertSupportRequestSql = @"
                INSERT INTO audit_substantive_support_requests
                (
                    reference_id,
                    fiscal_year,
                    source_type,
                    source_record_id,
                    source_key,
                    transaction_identifier,
                    journal_number,
                    posting_date,
                    account_number,
                    account_name,
                    fsli,
                    amount,
                    description,
                    triage_reason,
                    risk_flags
                )
                VALUES
                (
                    @ReferenceId,
                    @FiscalYear,
                    @SourceType,
                    @SourceRecordId,
                    @SourceKey,
                    @TransactionIdentifier,
                    @JournalNumber,
                    @PostingDate,
                    @AccountNumber,
                    @AccountName,
                    @Fsli,
                    @Amount,
                    @Description,
                    @TriageReason,
                    @RiskFlags
                )
                ON CONFLICT (reference_id, source_key, triage_reason)
                DO UPDATE SET
                    fiscal_year = EXCLUDED.fiscal_year,
                    source_type = EXCLUDED.source_type,
                    source_record_id = EXCLUDED.source_record_id,
                    transaction_identifier = EXCLUDED.transaction_identifier,
                    journal_number = EXCLUDED.journal_number,
                    posting_date = EXCLUDED.posting_date,
                    account_number = EXCLUDED.account_number,
                    account_name = EXCLUDED.account_name,
                    fsli = EXCLUDED.fsli,
                    amount = EXCLUDED.amount,
                    description = EXCLUDED.description,
                    risk_flags = EXCLUDED.risk_flags,
                    updated_at = CURRENT_TIMESTAMP;";

            foreach (var row in journalRows)
            {
                var selections = DetermineSupportSelections(row, threshold, request, holidayDates);
                if (!selections.Any())
                    continue;

                var riskFlags = string.Join(", ", selections.Select(selection => selection.Code).Distinct(StringComparer.OrdinalIgnoreCase));
                foreach (var selection in selections)
                {
                    await db.ExecuteAsync(
                        upsertSupportRequestSql,
                        new
                        {
                            ReferenceId = request.ReferenceId,
                            FiscalYear = fiscalYear.Value,
                            SourceType = "journal_entry",
                            SourceRecordId = row.Id,
                            SourceKey = $"{row.Id}:{selection.Code}",
                            TransactionIdentifier = BuildTransactionIdentifier(row),
                            row.JournalNumber,
                            PostingDate = row.PostingDate?.Date,
                            AccountNumber = NormalizeOptionalText(row.AccountNumber),
                            AccountName = NormalizeOptionalText(row.AccountName),
                            Fsli = NormalizeOptionalText(row.Fsli),
                            Amount = row.Amount,
                            Description = NormalizeOptionalText(row.Description),
                            TriageReason = selection.Label,
                            RiskFlags = riskFlags
                        },
                        transaction);
                }
            }

            await transaction.CommitAsync();
            return await GetSupportRequestsInternalAsync(db, request.ReferenceId, fiscalYear.Value);
        }

        public async Task<AuditSubstantiveSupportRequest> UpdateSupportRequestAsync(UpdateAuditSupportRequestRequest request)
        {
            if (request == null)
                throw new ArgumentNullException(nameof(request));
            if (request.Id <= 0)
                throw new InvalidOperationException("Support request ID is required.");
            if (request.ReferenceId <= 0)
                throw new InvalidOperationException("Reference ID is required.");

            await using var db = new NpgsqlConnection(_connectionString);
            await db.OpenAsync();

            var affected = await db.ExecuteAsync(@"
                UPDATE audit_substantive_support_requests
                SET
                    support_status = COALESCE(@SupportStatus, support_status),
                    support_summary = @SupportSummary,
                    linked_procedure_id = @LinkedProcedureId,
                    linked_walkthrough_id = @LinkedWalkthroughId,
                    linked_control_id = @LinkedControlId,
                    linked_finding_id = @LinkedFindingId,
                    notes = @Notes,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = @Id
                  AND reference_id = @ReferenceId;",
                new
                {
                    request.Id,
                    request.ReferenceId,
                    SupportStatus = NormalizeOptionalText(request.SupportStatus) ?? "Requested",
                    SupportSummary = NormalizeOptionalText(request.SupportSummary),
                    request.LinkedProcedureId,
                    request.LinkedWalkthroughId,
                    request.LinkedControlId,
                    request.LinkedFindingId,
                    Notes = NormalizeOptionalText(request.Notes)
                });

            if (affected <= 0)
                throw new InvalidOperationException("The selected support request could not be found.");

            return await GetSupportRequestByIdAsync(db, request.ReferenceId, request.Id);
        }

        public async Task<AuditFinanceFinalizationRecord> UpsertFinanceFinalizationAsync(UpsertAuditFinanceFinalizationRequest request)
        {
            if (request == null)
                throw new ArgumentNullException(nameof(request));
            if (request.ReferenceId <= 0)
                throw new InvalidOperationException("Reference ID is required.");

            await using var db = new NpgsqlConnection(_connectionString);
            await db.OpenAsync();

            var defaultRulePackageId = await ResolveDefaultRulePackageIdAsync(db);
            var activeRulePackageId = request.ActiveRulePackageId ?? defaultRulePackageId;
            await using var transaction = await db.BeginTransactionAsync();

            await EnsureFinanceFinalizationAsync(
                db,
                request.ReferenceId,
                request.ActiveMappingProfileId,
                activeRulePackageId,
                request.UpdatedByUserId,
                NormalizeOptionalText(request.UpdatedByName),
                transaction);

            await db.ExecuteAsync(@"
                UPDATE audit_finance_finalization
                SET
                    active_mapping_profile_id = COALESCE(@ActiveMappingProfileId, active_mapping_profile_id),
                    active_rule_package_id = COALESCE(@ActiveRulePackageId, active_rule_package_id),
                    overall_conclusion = @OverallConclusion,
                    recommendation_summary = @RecommendationSummary,
                    release_readiness_status = COALESCE(@ReleaseReadinessStatus, release_readiness_status),
                    draft_statement_status = COALESCE(@DraftStatementStatus, draft_statement_status),
                    outstanding_items = @OutstandingItems,
                    reviewer_notes = @ReviewerNotes,
                    ready_for_release = @ReadyForRelease,
                    updated_by_user_id = @UpdatedByUserId,
                    updated_by_name = @UpdatedByName,
                    updated_at = CURRENT_TIMESTAMP
                WHERE reference_id = @ReferenceId;",
                new
                {
                    request.ReferenceId,
                    request.ActiveMappingProfileId,
                    ActiveRulePackageId = activeRulePackageId,
                    OverallConclusion = NormalizeOptionalText(request.OverallConclusion),
                    RecommendationSummary = NormalizeOptionalText(request.RecommendationSummary),
                    ReleaseReadinessStatus = NormalizeOptionalText(request.ReleaseReadinessStatus) ?? "In Preparation",
                    DraftStatementStatus = NormalizeOptionalText(request.DraftStatementStatus) ?? "Not Generated",
                    OutstandingItems = NormalizeOptionalText(request.OutstandingItems),
                    ReviewerNotes = NormalizeOptionalText(request.ReviewerNotes),
                    request.ReadyForRelease,
                    request.UpdatedByUserId,
                    UpdatedByName = NormalizeOptionalText(request.UpdatedByName)
                },
                transaction);

            await transaction.CommitAsync();
            return await GetFinalizationInternalAsync(db, request.ReferenceId);
        }

        private static List<PowerBIReconciliationMetric> BuildMetrics(ReportingAggregateRow native, ReportingAggregateRow reporting)
        {
            return new List<PowerBIReconciliationMetric>
            {
                CreateMetric("total_findings", "Total Findings", "Findings", native.TotalFindings, reporting.TotalFindings),
                CreateMetric("open_findings", "Open Findings", "Findings", native.OpenFindings, reporting.OpenFindings),
                CreateMetric("total_recommendations", "Total Recommendations", "Findings", native.TotalRecommendations, reporting.TotalRecommendations),
                CreateMetric("open_recommendations", "Open Recommendations", "Findings", native.OpenRecommendations, reporting.OpenRecommendations),
                CreateMetric("overdue_management_actions", "Overdue Management Actions", "Execution", native.OverdueManagementActions, reporting.OverdueManagementActions),
                CreateMetric("total_working_papers", "Total Working Papers", "Execution", native.TotalWorkingPapers, reporting.TotalWorkingPapers),
                CreateMetric("signed_off_working_papers", "Signed-Off Working Papers", "Execution", native.SignedOffWorkingPapers, reporting.SignedOffWorkingPapers),
                CreateMetric("total_documents", "Total Documents", "Execution", native.TotalDocuments, reporting.TotalDocuments),
                CreateMetric("open_evidence_requests", "Open Evidence Requests", "Execution", native.OpenEvidenceRequests, reporting.OpenEvidenceRequests),
                CreateMetric("active_workflows", "Active Workflows", "Execution", native.ActiveWorkflows, reporting.ActiveWorkflows),
                CreateMetric("pending_workflow_tasks", "Pending Workflow Tasks", "Execution", native.PendingWorkflowTasks, reporting.PendingWorkflowTasks),
                CreateMetric("journal_entry_rows", "Journal Entry Rows", "Analytics", native.JournalEntryRows, reporting.JournalEntryRows),
                CreateMetric("trial_balance_accounts", "Trial Balance Accounts", "Analytics", native.TrialBalanceAccounts, reporting.TrialBalanceAccounts),
                CreateMetric("industry_benchmark_metrics", "Industry Benchmark Metrics", "Analytics", native.IndustryBenchmarkMetrics, reporting.IndustryBenchmarkMetrics),
                CreateMetric("reasonability_forecast_metrics", "Reasonability Forecast Metrics", "Analytics", native.ReasonabilityForecastMetrics, reporting.ReasonabilityForecastMetrics)
            };
        }

        private static PowerBIReconciliationMetric CreateMetric(string key, string name, string category, decimal nativeValue, decimal reportingValue)
        {
            return new PowerBIReconciliationMetric
            {
                MetricKey = key,
                MetricName = name,
                Category = category,
                NativeValue = nativeValue,
                ReportingValue = reportingValue,
                Variance = reportingValue - nativeValue,
                IsMatched = nativeValue == reportingValue
            };
        }

        private async Task<List<AuditRulePackage>> GetRulePackagesInternalAsync(NpgsqlConnection db, IDbTransaction transaction = null)
        {
            var query = $"{RulePackageSelect} WHERE is_active = TRUE ORDER BY CASE WHEN package_code = 'finance_audit_core' THEN 0 WHEN is_default THEN 1 ELSE 2 END, package_name;";
            var rows = await db.QueryAsync<AuditRulePackage>(query, transaction: transaction);
            return rows.ToList();
        }

        private async Task<List<AuditFinancialStatementMappingProfile>> GetMappingProfilesInternalAsync(NpgsqlConnection db, int referenceId, IDbTransaction transaction = null)
        {
            var query = $@"
                {MappingProfileSelect}
                WHERE profile.is_active = TRUE
                  AND (
                        profile.reference_id = @ReferenceId
                        OR profile.reference_id IS NULL
                        OR profile.is_reusable = TRUE
                      )
                ORDER BY
                    CASE
                        WHEN profile.reference_id = @ReferenceId THEN 0
                        WHEN profile.is_default THEN 1
                        WHEN profile.is_reusable THEN 2
                        ELSE 3
                    END,
                    profile.profile_name;";

            var rows = await db.QueryAsync<AuditFinancialStatementMappingProfile>(
                query,
                new { ReferenceId = referenceId },
                transaction);
            return rows.ToList();
        }

        private async Task<AuditFinancialStatementMappingProfile> GetMappingProfileByIdAsync(NpgsqlConnection db, int profileId, IDbTransaction transaction = null)
        {
            var query = $@"
                {MappingProfileSelect}
                WHERE profile.id = @ProfileId;";

            return await db.QueryFirstOrDefaultAsync<AuditFinancialStatementMappingProfile>(
                query,
                new { ProfileId = profileId },
                transaction);
        }

        private async Task<List<AuditFinancialStatementMappingItem>> GetMappingsInternalAsync(NpgsqlConnection db, int referenceId, int fiscalYear, IDbTransaction transaction = null)
        {
            var query = $@"
                {MappingSelect}
                ORDER BY
                    COALESCE(map.display_order, 999),
                    COALESCE(map.section_name, 'ZZZ'),
                    COALESCE(map.line_name, 'ZZZ'),
                    tb.account_number;";

            var rows = await db.QueryAsync<AuditFinancialStatementMappingItem>(
                query,
                new { ReferenceId = referenceId, FiscalYear = fiscalYear },
                transaction);
            return rows.ToList();
        }

        private async Task<List<AuditSubstantiveSupportRequest>> GetSupportRequestsInternalAsync(NpgsqlConnection db, int referenceId, int fiscalYear, IDbTransaction transaction = null)
        {
            var query = $@"
                {SupportRequestSelect}
                WHERE request.reference_id = @ReferenceId
                  AND request.fiscal_year = @FiscalYear
                ORDER BY request.requested_at DESC, ABS(COALESCE(request.amount, 0)) DESC, request.id DESC;";

            var rows = await db.QueryAsync<AuditSubstantiveSupportRequest>(
                query,
                new { ReferenceId = referenceId, FiscalYear = fiscalYear },
                transaction);
            return rows.ToList();
        }

        private async Task<AuditSubstantiveSupportRequest> GetSupportRequestByIdAsync(NpgsqlConnection db, int referenceId, long id, IDbTransaction transaction = null)
        {
            var query = $@"
                {SupportRequestSelect}
                WHERE request.reference_id = @ReferenceId
                  AND request.id = @Id;";

            return await db.QueryFirstOrDefaultAsync<AuditSubstantiveSupportRequest>(
                query,
                new { ReferenceId = referenceId, Id = id },
                transaction);
        }

        private async Task<AuditFinanceFinalizationRecord> GetFinalizationInternalAsync(NpgsqlConnection db, int referenceId, IDbTransaction transaction = null)
        {
            var query = $@"
                {FinalizationSelect}
                WHERE finalization.reference_id = @ReferenceId;";

            var record = await db.QueryFirstOrDefaultAsync<AuditFinanceFinalizationRecord>(
                query,
                new { ReferenceId = referenceId },
                transaction);

            if (record != null)
                return record;

            var defaultPackage = (await GetRulePackagesInternalAsync(db, transaction)).FirstOrDefault();
            return new AuditFinanceFinalizationRecord
            {
                ReferenceId = referenceId,
                ActiveRulePackageId = defaultPackage?.Id,
                ActiveRulePackageCode = defaultPackage?.PackageCode,
                ActiveRulePackageName = defaultPackage?.PackageName,
                ReleaseReadinessStatus = "In Preparation",
                DraftStatementStatus = "Not Generated",
                ReadyForRelease = false
            };
        }

        private async Task<List<AuditDraftFinancialStatement>> BuildDraftStatementsInternalAsync(NpgsqlConnection db, int referenceId, int fiscalYear, IDbTransaction transaction = null)
        {
            var mappings = (await GetMappingsInternalAsync(db, referenceId, fiscalYear, transaction))
                .Where(item =>
                    !string.IsNullOrWhiteSpace(item.StatementType)
                    && !string.IsNullOrWhiteSpace(item.SectionName)
                    && !string.IsNullOrWhiteSpace(item.LineName))
                .OrderBy(item => GetStatementSortKey(item.StatementType))
                .ThenBy(item => item.DisplayOrder)
                .ThenBy(item => item.AccountNumber)
                .ToList();

            return mappings
                .GroupBy(item => item.StatementType)
                .OrderBy(group => GetStatementSortKey(group.Key))
                .Select(group => new AuditDraftFinancialStatement
                {
                    StatementType = group.Key,
                    FiscalYear = fiscalYear,
                    TotalAmount = group.Sum(item => item.CurrentBalance),
                    Lines = group
                        .GroupBy(item => new { item.StatementType, item.SectionName, item.LineName })
                        .OrderBy(lineGroup => lineGroup.Min(item => item.DisplayOrder))
                        .ThenBy(lineGroup => lineGroup.Key.SectionName)
                        .ThenBy(lineGroup => lineGroup.Key.LineName)
                        .Select(lineGroup => new AuditDraftFinancialStatementLine
                        {
                            StatementType = lineGroup.Key.StatementType,
                            SectionName = lineGroup.Key.SectionName,
                            LineName = lineGroup.Key.LineName,
                            Amount = lineGroup.Sum(item => item.CurrentBalance),
                            AccountCount = lineGroup.Count()
                        })
                        .ToList()
                })
                .ToList();
        }

        private async Task<List<ProfileRuleRow>> GetProfileRulesInternalAsync(NpgsqlConnection db, int? mappingProfileId, IDbTransaction transaction = null)
        {
            if (!mappingProfileId.HasValue)
                return new List<ProfileRuleRow>();

            var rows = await db.QueryAsync<ProfileRuleRow>(@"
                SELECT
                    account_number AS AccountNumber,
                    account_name AS AccountName,
                    fsli AS Fsli,
                    statement_type AS StatementType,
                    section_name AS SectionName,
                    line_name AS LineName,
                    classification AS Classification,
                    display_order AS DisplayOrder,
                    notes AS Notes
                FROM audit_financial_statement_profile_rules
                WHERE mapping_profile_id = @MappingProfileId;",
                new { MappingProfileId = mappingProfileId.Value },
                transaction);

            return rows.ToList();
        }

        private async Task<int?> ResolveLatestTrialBalanceYearAsync(NpgsqlConnection db, int referenceId, int? fiscalYear, IDbTransaction transaction = null)
        {
            if (fiscalYear.HasValue && fiscalYear.Value > 0)
                return fiscalYear.Value;

            return await db.ExecuteScalarAsync<int?>(@"
                SELECT MAX(fiscal_year)
                FROM audit_trial_balance_snapshots
                WHERE reference_id = @ReferenceId;",
                new { ReferenceId = referenceId },
                transaction);
        }

        private async Task<int?> ResolveLatestJournalYearAsync(NpgsqlConnection db, int referenceId, int? fiscalYear, IDbTransaction transaction = null)
        {
            if (fiscalYear.HasValue && fiscalYear.Value > 0)
                return fiscalYear.Value;

            return await db.ExecuteScalarAsync<int?>(@"
                SELECT MAX(fiscal_year)
                FROM audit_gl_journal_entries
                WHERE reference_id = @ReferenceId;",
                new { ReferenceId = referenceId },
                transaction);
        }

        private async Task<int?> ResolveDefaultRulePackageIdAsync(NpgsqlConnection db, IDbTransaction transaction = null)
        {
            return await db.ExecuteScalarAsync<int?>(@"
                SELECT id
                FROM audit_domain_rule_packages
                WHERE is_active = TRUE
                ORDER BY
                    CASE
                        WHEN package_code = 'finance_audit_core' THEN 0
                        WHEN is_default THEN 1
                        ELSE 2
                    END,
                    id
                LIMIT 1;",
                transaction: transaction);
        }

        private async Task<int?> ResolvePreferredMappingProfileAsync(NpgsqlConnection db, int referenceId, int? requestedProfileId, IDbTransaction transaction = null)
        {
            if (requestedProfileId.HasValue)
            {
                var explicitProfileId = await db.ExecuteScalarAsync<int?>(@"
                    SELECT id
                    FROM audit_financial_statement_mapping_profiles
                    WHERE id = @ProfileId
                      AND is_active = TRUE;",
                    new { ProfileId = requestedProfileId.Value },
                    transaction);
                if (explicitProfileId.HasValue)
                    return explicitProfileId.Value;
            }

            var finalizationProfileId = await db.ExecuteScalarAsync<int?>(@"
                SELECT active_mapping_profile_id
                FROM audit_finance_finalization
                WHERE reference_id = @ReferenceId;",
                new { ReferenceId = referenceId },
                transaction);
            if (finalizationProfileId.HasValue)
                return finalizationProfileId.Value;

            return await db.ExecuteScalarAsync<int?>(@"
                SELECT id
                FROM audit_financial_statement_mapping_profiles
                WHERE is_active = TRUE
                  AND (
                        reference_id = @ReferenceId
                        OR reference_id IS NULL
                        OR is_reusable = TRUE
                      )
                ORDER BY
                    CASE
                        WHEN reference_id = @ReferenceId THEN 0
                        WHEN is_default THEN 1
                        WHEN is_reusable THEN 2
                        ELSE 3
                    END,
                    created_at DESC
                LIMIT 1;",
                new { ReferenceId = referenceId },
                transaction);
        }

        private async Task EnsureFinanceFinalizationAsync(
            NpgsqlConnection db,
            int referenceId,
            int? activeMappingProfileId,
            int? activeRulePackageId,
            int? updatedByUserId,
            string updatedByName,
            IDbTransaction transaction = null)
        {
            var resolvedRulePackageId = activeRulePackageId ?? await ResolveDefaultRulePackageIdAsync(db, transaction);
            await db.ExecuteAsync(@"
                INSERT INTO audit_finance_finalization
                (
                    reference_id,
                    active_mapping_profile_id,
                    active_rule_package_id,
                    release_readiness_status,
                    draft_statement_status,
                    updated_by_user_id,
                    updated_by_name
                )
                VALUES
                (
                    @ReferenceId,
                    @ActiveMappingProfileId,
                    @ActiveRulePackageId,
                    'In Preparation',
                    'Not Generated',
                    @UpdatedByUserId,
                    @UpdatedByName
                )
                ON CONFLICT (reference_id)
                DO UPDATE SET
                    active_mapping_profile_id = COALESCE(EXCLUDED.active_mapping_profile_id, audit_finance_finalization.active_mapping_profile_id),
                    active_rule_package_id = COALESCE(EXCLUDED.active_rule_package_id, audit_finance_finalization.active_rule_package_id),
                    updated_by_user_id = COALESCE(EXCLUDED.updated_by_user_id, audit_finance_finalization.updated_by_user_id),
                    updated_by_name = COALESCE(EXCLUDED.updated_by_name, audit_finance_finalization.updated_by_name),
                    updated_at = CURRENT_TIMESTAMP;",
                new
                {
                    ReferenceId = referenceId,
                    ActiveMappingProfileId = activeMappingProfileId,
                    ActiveRulePackageId = resolvedRulePackageId,
                    UpdatedByUserId = updatedByUserId,
                    UpdatedByName = NormalizeOptionalText(updatedByName)
                },
                transaction);
        }

        private async Task<FinanceMaterialityThresholdRow> ResolveMaterialityThresholdAsync(NpgsqlConnection db, int referenceId, IDbTransaction transaction = null)
        {
            return await db.QueryFirstOrDefaultAsync<FinanceMaterialityThresholdRow>(@"
                SELECT
                    COALESCE(active_calc.performance_materiality, active_calc.overall_materiality, plan.performance_materiality, plan.overall_materiality, 0) AS Threshold,
                    CASE
                        WHEN active_calc.performance_materiality IS NOT NULL AND active_calc.performance_materiality > 0 THEN 'Active performance materiality'
                        WHEN active_calc.overall_materiality IS NOT NULL AND active_calc.overall_materiality > 0 THEN 'Active overall materiality'
                        WHEN plan.performance_materiality IS NOT NULL AND plan.performance_materiality > 0 THEN 'Planning performance materiality'
                        WHEN plan.overall_materiality IS NOT NULL AND plan.overall_materiality > 0 THEN 'Planning overall materiality'
                        ELSE 'No materiality threshold'
                    END AS ThresholdSource
                FROM riskassessmentreference ref
                LEFT JOIN audit_engagement_plans plan ON plan.reference_id = ref.reference_id
                LEFT JOIN audit_materiality_calculations active_calc
                    ON active_calc.id = plan.active_materiality_calculation_id
                WHERE ref.reference_id = @ReferenceId;",
                new { ReferenceId = referenceId },
                transaction) ?? new FinanceMaterialityThresholdRow();
        }

        private static MappingSuggestion DetermineSuggestedMapping(
            TrialBalanceSourceRow source,
            IReadOnlyDictionary<string, ProfileRuleRow> ruleLookup,
            int? mappingProfileId)
        {
            if (source == null)
                return null;

            if (!string.IsNullOrWhiteSpace(source.AccountNumber)
                && ruleLookup != null
                && ruleLookup.TryGetValue(source.AccountNumber, out var explicitRule))
            {
                return new MappingSuggestion
                {
                    MappingProfileId = mappingProfileId,
                    StatementType = explicitRule.StatementType,
                    SectionName = explicitRule.SectionName,
                    LineName = explicitRule.LineName,
                    Classification = explicitRule.Classification,
                    DisplayOrder = explicitRule.DisplayOrder > 0 ? explicitRule.DisplayOrder : 100,
                    Notes = NormalizeOptionalText(explicitRule.Notes) ?? "Matched reusable mapping profile rule."
                };
            }

            var normalized = $"{source.AccountName} {source.Fsli}".Trim().ToLowerInvariant();
            if (string.IsNullOrWhiteSpace(normalized))
                return null;

            if (ContainsAny(normalized, "revenue", "sales", "turnover"))
                return MappingSuggestion.Create(mappingProfileId, "Income Statement", "Revenue", "Revenue", "Revenue", 10, "Auto-mapped from revenue keywords.");
            if (ContainsAny(normalized, "cost of sales", "cost of goods", "cost of sale", "cogs"))
                return MappingSuggestion.Create(mappingProfileId, "Income Statement", "Cost of Sales", "Cost of Sales", "Expense", 20, "Auto-mapped from cost-of-sales keywords.");
            if (ContainsAny(normalized, "finance income", "interest received", "investment income"))
                return MappingSuggestion.Create(mappingProfileId, "Income Statement", "Other Income", "Finance Income", "Income", 60, "Auto-mapped from finance-income keywords.");
            if (ContainsAny(normalized, "finance cost", "interest expense", "borrowing cost"))
                return MappingSuggestion.Create(mappingProfileId, "Income Statement", "Finance Costs", "Finance Costs", "Expense", 70, "Auto-mapped from finance-cost keywords.");
            if (ContainsAny(normalized, "tax", "income tax", "taxation", "deferred tax"))
                return MappingSuggestion.Create(mappingProfileId, "Income Statement", "Taxation", "Tax Expense", "Tax", 80, "Auto-mapped from tax keywords.");
            if (ContainsAny(normalized, "expense", "salary", "wage", "payroll", "rent", "utility", "travel", "marketing", "professional", "depreciation", "amortisation", "amortization", "admin"))
            {
                return MappingSuggestion.Create(
                    mappingProfileId,
                    "Income Statement",
                    "Operating Expenses",
                    NormalizeOptionalText(source.AccountName) ?? "Operating Expense",
                    "Expense",
                    50,
                    "Auto-mapped from operating-expense keywords.");
            }

            if (ContainsAny(normalized, "cash", "bank"))
                return MappingSuggestion.Create(mappingProfileId, "Balance Sheet", "Current Assets", "Cash and Cash Equivalents", "Asset", 10, "Auto-mapped from cash keywords.");
            if (ContainsAny(normalized, "receivable", "debtor", "accounts receivable", "trade receivable"))
                return MappingSuggestion.Create(mappingProfileId, "Balance Sheet", "Current Assets", "Trade and Other Receivables", "Asset", 12, "Auto-mapped from receivable keywords.");
            if (ContainsAny(normalized, "inventory", "stock"))
                return MappingSuggestion.Create(mappingProfileId, "Balance Sheet", "Current Assets", "Inventory", "Asset", 14, "Auto-mapped from inventory keywords.");
            if (ContainsAny(normalized, "prepaid", "prepayment"))
                return MappingSuggestion.Create(mappingProfileId, "Balance Sheet", "Current Assets", "Prepayments", "Asset", 16, "Auto-mapped from prepayment keywords.");
            if (ContainsAny(normalized, "property", "plant", "equipment", "ppe", "fixed asset", "motor vehicle", "furniture"))
                return MappingSuggestion.Create(mappingProfileId, "Balance Sheet", "Non-Current Assets", "Property, Plant and Equipment", "Asset", 20, "Auto-mapped from PPE keywords.");
            if (ContainsAny(normalized, "intangible", "goodwill", "software"))
                return MappingSuggestion.Create(mappingProfileId, "Balance Sheet", "Non-Current Assets", "Intangible Assets", "Asset", 22, "Auto-mapped from intangible-asset keywords.");
            if (ContainsAny(normalized, "investment"))
                return MappingSuggestion.Create(mappingProfileId, "Balance Sheet", "Non-Current Assets", "Investments", "Asset", 24, "Auto-mapped from investment keywords.");
            if (ContainsAny(normalized, "payable", "creditor", "accounts payable", "trade payable"))
                return MappingSuggestion.Create(mappingProfileId, "Balance Sheet", "Current Liabilities", "Trade and Other Payables", "Liability", 30, "Auto-mapped from payable keywords.");
            if (ContainsAny(normalized, "accrual"))
                return MappingSuggestion.Create(mappingProfileId, "Balance Sheet", "Current Liabilities", "Accruals", "Liability", 32, "Auto-mapped from accrual keywords.");
            if (ContainsAny(normalized, "vat payable", "tax payable"))
                return MappingSuggestion.Create(mappingProfileId, "Balance Sheet", "Current Liabilities", "Tax Payables", "Liability", 34, "Auto-mapped from payable-tax keywords.");
            if (ContainsAny(normalized, "loan", "borrowing", "lease liability", "mortgage", "debt"))
                return MappingSuggestion.Create(mappingProfileId, "Balance Sheet", "Non-Current Liabilities", "Borrowings", "Liability", 40, "Auto-mapped from borrowing keywords.");
            if (ContainsAny(normalized, "share capital", "capital", "equity"))
                return MappingSuggestion.Create(mappingProfileId, "Balance Sheet", "Equity", "Share Capital", "Equity", 50, "Auto-mapped from equity keywords.");
            if (ContainsAny(normalized, "retained earnings", "reserve", "accumulated profit"))
                return MappingSuggestion.Create(mappingProfileId, "Balance Sheet", "Equity", "Retained Earnings and Reserves", "Equity", 52, "Auto-mapped from retained-earnings keywords.");

            return null;
        }

        private static List<SupportSelection> DetermineSupportSelections(
            JournalSelectionRow row,
            FinanceMaterialityThresholdRow threshold,
            GenerateAuditSupportQueueRequest request,
            ISet<DateTime> holidayDates)
        {
            var selections = new List<SupportSelection>();
            var absoluteAmount = Math.Abs(row?.Amount ?? 0);
            var postingDate = row?.PostingDate?.Date;
            var normalizedText = $"{row?.AccountName} {row?.Fsli} {row?.Description}".ToLowerInvariant();

            if (request.IncludeMaterialitySelections && threshold != null && threshold.Threshold > 0 && absoluteAmount >= threshold.Threshold)
                selections.Add(new SupportSelection("materiality", $"Above {threshold.ThresholdSource}".Trim()));
            if (request.IncludeJournalRiskSelections && row != null && row.IsManual)
                selections.Add(new SupportSelection("manual_journal", "Manual journal entry"));
            if (request.IncludeJournalRiskSelections && row != null && (row.IsPeriodEnd || (postingDate.HasValue && postingDate.Value.Day >= 28)))
                selections.Add(new SupportSelection("period_end_journal", "Period-end journal"));
            if (request.IncludeJournalRiskSelections && postingDate.HasValue && (postingDate.Value.DayOfWeek == DayOfWeek.Saturday || postingDate.Value.DayOfWeek == DayOfWeek.Sunday || holidayDates.Contains(postingDate.Value)))
                selections.Add(new SupportSelection("weekend_holiday_journal", "Weekend or holiday journal"));
            if (request.IncludeJournalRiskSelections && absoluteAmount >= 1000 && absoluteAmount % 1000 == 0)
                selections.Add(new SupportSelection("round_amount_journal", "Round amount journal"));
            if (request.IncludeRevenueRiskSelections && ContainsAny(normalizedText, "revenue", "sales", "turnover", "invoice", "credit note"))
                selections.Add(new SupportSelection("revenue_risk", "Revenue risk selection"));

            return selections
                .GroupBy(selection => selection.Code, StringComparer.OrdinalIgnoreCase)
                .Select(group => group.First())
                .ToList();
        }

        private static string BuildTransactionIdentifier(JournalSelectionRow row)
        {
            if (!string.IsNullOrWhiteSpace(row.JournalNumber))
                return row.LineNumber.HasValue ? $"{row.JournalNumber}-{row.LineNumber.Value}" : row.JournalNumber;

            return $"JE-{row.Id}";
        }

        private async Task<string> BuildUniqueProfileCodeAsync(NpgsqlConnection db, string profileName, IDbTransaction transaction = null)
        {
            var slug = Slugify(profileName);
            var baseCandidate = string.IsNullOrWhiteSpace(slug) ? "finance-mapping-profile" : slug;
            var candidate = baseCandidate;
            var suffix = 2;

            while (await db.ExecuteScalarAsync<int>(@"
                SELECT COUNT(*)
                FROM audit_financial_statement_mapping_profiles
                WHERE profile_code = @ProfileCode;",
                new { ProfileCode = candidate },
                transaction) > 0)
            {
                candidate = $"{baseCandidate}-{suffix}";
                suffix++;
            }

            return candidate;
        }

        private static int GetStatementSortKey(string statementType)
        {
            return string.Equals(statementType, "Income Statement", StringComparison.OrdinalIgnoreCase) ? 0 : 1;
        }

        private static bool ContainsAny(string input, params string[] values)
        {
            if (string.IsNullOrWhiteSpace(input) || values == null || values.Length == 0)
                return false;

            foreach (var value in values)
            {
                if (!string.IsNullOrWhiteSpace(value) && input.Contains(value, StringComparison.OrdinalIgnoreCase))
                    return true;
            }

            return false;
        }

        private static string NormalizeOptionalText(string value)
        {
            return string.IsNullOrWhiteSpace(value) ? null : value.Trim();
        }

        private static string Slugify(string value)
        {
            if (string.IsNullOrWhiteSpace(value))
                return "finance-mapping-profile";

            var builder = new StringBuilder();
            var lastWasSeparator = false;

            foreach (var character in value.Trim().ToLowerInvariant())
            {
                if (char.IsLetterOrDigit(character))
                {
                    builder.Append(character);
                    lastWasSeparator = false;
                }
                else if (!lastWasSeparator)
                {
                    builder.Append('-');
                    lastWasSeparator = true;
                }
            }

            return builder.ToString().Trim('-');
        }

        private sealed class ReportingAggregateRow
        {
            public decimal TotalFindings { get; set; }
            public decimal OpenFindings { get; set; }
            public decimal TotalRecommendations { get; set; }
            public decimal OpenRecommendations { get; set; }
            public decimal OverdueManagementActions { get; set; }
            public decimal TotalWorkingPapers { get; set; }
            public decimal SignedOffWorkingPapers { get; set; }
            public decimal TotalDocuments { get; set; }
            public decimal OpenEvidenceRequests { get; set; }
            public decimal ActiveWorkflows { get; set; }
            public decimal PendingWorkflowTasks { get; set; }
            public decimal JournalEntryRows { get; set; }
            public decimal TrialBalanceAccounts { get; set; }
            public decimal IndustryBenchmarkMetrics { get; set; }
            public decimal ReasonabilityForecastMetrics { get; set; }
        }

        private sealed class ProfileRuleRow
        {
            public string AccountNumber { get; set; }
            public string AccountName { get; set; }
            public string Fsli { get; set; }
            public string StatementType { get; set; }
            public string SectionName { get; set; }
            public string LineName { get; set; }
            public string Classification { get; set; }
            public int DisplayOrder { get; set; }
            public string Notes { get; set; }
        }

        private sealed class TrialBalanceSourceRow
        {
            public int ReferenceId { get; set; }
            public int FiscalYear { get; set; }
            public string AccountNumber { get; set; }
            public string AccountName { get; set; }
            public string Fsli { get; set; }
            public string BusinessUnit { get; set; }
            public decimal CurrentBalance { get; set; }
        }

        private sealed class MappingSuggestion
        {
            public int? MappingProfileId { get; set; }
            public string StatementType { get; set; }
            public string SectionName { get; set; }
            public string LineName { get; set; }
            public string Classification { get; set; }
            public int DisplayOrder { get; set; }
            public string Notes { get; set; }

            public static MappingSuggestion Create(int? mappingProfileId, string statementType, string sectionName, string lineName, string classification, int displayOrder, string notes)
            {
                return new MappingSuggestion
                {
                    MappingProfileId = mappingProfileId,
                    StatementType = statementType,
                    SectionName = sectionName,
                    LineName = lineName,
                    Classification = classification,
                    DisplayOrder = displayOrder,
                    Notes = notes
                };
            }

            public static MappingSuggestion FromExisting(AuditFinancialStatementMappingItem mapping)
            {
                if (mapping == null)
                    return null;

                return new MappingSuggestion
                {
                    MappingProfileId = mapping.MappingProfileId,
                    StatementType = mapping.StatementType,
                    SectionName = mapping.SectionName,
                    LineName = mapping.LineName,
                    Classification = mapping.Classification,
                    DisplayOrder = mapping.DisplayOrder > 0 ? mapping.DisplayOrder : 100,
                    Notes = mapping.Notes
                };
            }
        }

        private sealed class FinanceMaterialityThresholdRow
        {
            public decimal Threshold { get; set; }
            public string ThresholdSource { get; set; }
        }

        private sealed class JournalSelectionRow
        {
            public long Id { get; set; }
            public int ReferenceId { get; set; }
            public int FiscalYear { get; set; }
            public DateTime? PostingDate { get; set; }
            public int? FiscalPeriod { get; set; }
            public string JournalNumber { get; set; }
            public int? LineNumber { get; set; }
            public string AccountNumber { get; set; }
            public string AccountName { get; set; }
            public string Fsli { get; set; }
            public string Description { get; set; }
            public decimal Amount { get; set; }
            public bool IsManual { get; set; }
            public bool IsPeriodEnd { get; set; }
        }

        private sealed class SupportSelection
        {
            public SupportSelection(string code, string label)
            {
                Code = code;
                Label = label;
            }

            public string Code { get; }
            public string Label { get; }
        }
    }
}
