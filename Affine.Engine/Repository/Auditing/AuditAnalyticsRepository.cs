using Affine.Engine.Model.Auditing.AuditUniverse;
using Dapper;
using Microsoft.VisualBasic.FileIO;
using Npgsql;
using System;
using System.Collections.Generic;
using System.Data;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Threading.Tasks;

namespace Affine.Engine.Repository.Auditing
{
    public class AuditAnalyticsRepository : IAuditAnalyticsRepository
    {
        private readonly string _connectionString;

        public AuditAnalyticsRepository(string connectionString)
        {
            _connectionString = connectionString ?? throw new ArgumentNullException(nameof(connectionString));
        }

        private async Task<MaterialityContextRow> ResolveMaterialityContextAsync(IDbConnection db, int? referenceId)
        {
            return await db.QueryFirstOrDefaultAsync<MaterialityContextRow>(@"
                WITH active_calculation AS (
                    SELECT
                        GREATEST(COALESCE(overall_materiality, 0), COALESCE(performance_materiality, 0)) AS threshold_value,
                        calculation_summary,
                        benchmark_name
                    FROM audit_materiality_calculations
                    WHERE is_active = TRUE
                      AND (@ReferenceId IS NULL OR reference_id = @ReferenceId)
                    ORDER BY COALESCE(approved_at, created_at) DESC, id DESC
                    LIMIT 1
                ),
                planning AS (
                    SELECT
                        GREATEST(COALESCE(overall_materiality, 0), COALESCE(performance_materiality, 0)) AS threshold_value,
                        materiality_basis,
                        selected_materiality_benchmark
                    FROM audit_engagement_plans
                    WHERE (@ReferenceId IS NULL OR reference_id = @ReferenceId)
                    ORDER BY updated_at DESC NULLS LAST, created_at DESC NULLS LAST, reference_id DESC
                    LIMIT 1
                )
                SELECT
                    COALESCE(
                        (SELECT threshold_value FROM active_calculation),
                        (SELECT threshold_value FROM planning),
                        0
                    ) AS Threshold,
                    CASE
                        WHEN EXISTS (SELECT 1 FROM active_calculation) THEN 'Calculated'
                        WHEN EXISTS (SELECT 1 FROM planning) THEN 'Manual Planning'
                        ELSE 'Not Set'
                    END AS ThresholdSource,
                    COALESCE(
                        (SELECT calculation_summary FROM active_calculation),
                        (SELECT COALESCE(selected_materiality_benchmark, materiality_basis) FROM planning),
                        'No active materiality threshold'
                    ) AS BenchmarkSummary;",
                new { ReferenceId = referenceId }) ?? new MaterialityContextRow();
        }

        private async Task<decimal> ResolveMaterialityThresholdAsync(IDbConnection db, int? referenceId)
        {
            var context = await ResolveMaterialityContextAsync(db, referenceId);
            return context?.Threshold ?? 0;
        }

        public Task<JournalExceptionAnalyticsResponse> GetManagementOverrideAnalyticsAsync(int? referenceId, int? year, int? period)
            => GetJournalAnalyticsInternalAsync(referenceId, year, period);

        public Task<JournalExceptionAnalyticsResponse> GetJournalExceptionAnalyticsAsync(int? referenceId, int? year, int? period)
            => GetJournalAnalyticsInternalAsync(referenceId, year, period);

        public async Task<UserPostingConcentrationResponse> GetUserPostingConcentrationAsync(int? referenceId, int? year, int? period, int topUsers)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();

                var resolvedYear = await ResolveJournalYearAsync(db, referenceId, year);
                var parameters = new DynamicParameters();
                parameters.Add("ReferenceId", referenceId);
                parameters.Add("Year", resolvedYear);
                parameters.Add("Period", period);
                parameters.Add("TopUsers", topUsers <= 0 ? 5 : topUsers);

                var totalQuery = @"
                    WITH filtered AS (
                        SELECT
                            COALESCE(NULLIF(TRIM(user_name), ''), NULLIF(TRIM(user_id), ''), 'Unassigned') AS user_name,
                            ABS(COALESCE(amount, COALESCE(debit_amount, 0) - COALESCE(credit_amount, 0))) AS abs_amount
                        FROM audit_gl_journal_entries
                        WHERE (@ReferenceId IS NULL OR reference_id = @ReferenceId)
                          AND fiscal_year = @Year
                          AND (@Period IS NULL OR fiscal_period = @Period)
                    )
                    SELECT
                        COUNT(*) AS TotalEntries,
                        COALESCE(SUM(abs_amount), 0) AS TotalPostedAmount
                    FROM filtered;";

                var totals = await db.QueryFirstOrDefaultAsync<UserPostingConcentrationResponse>(totalQuery, parameters)
                    ?? new UserPostingConcentrationResponse();

                var userQuery = @"
                    WITH filtered AS (
                        SELECT
                            COALESCE(NULLIF(TRIM(user_name), ''), NULLIF(TRIM(user_id), ''), 'Unassigned') AS user_name,
                            ABS(COALESCE(amount, COALESCE(debit_amount, 0) - COALESCE(credit_amount, 0))) AS abs_amount
                        FROM audit_gl_journal_entries
                        WHERE (@ReferenceId IS NULL OR reference_id = @ReferenceId)
                          AND fiscal_year = @Year
                          AND (@Period IS NULL OR fiscal_period = @Period)
                    )
                    SELECT
                        user_name AS UserName,
                        COUNT(*) AS EntryCount,
                        COALESCE(SUM(abs_amount), 0) AS TotalAmount
                    FROM filtered
                    GROUP BY user_name
                    ORDER BY COUNT(*) DESC, COALESCE(SUM(abs_amount), 0) DESC
                    LIMIT @TopUsers;";

                var users = (await db.QueryAsync<UserPostingConcentrationItem>(userQuery, parameters)).ToList();
                foreach (var user in users)
                {
                    user.PercentageOfEntries = totals.TotalEntries > 0
                        ? Math.Round((decimal)user.EntryCount / totals.TotalEntries * 100, 1)
                        : 0;
                    user.PercentageOfValue = totals.TotalPostedAmount > 0
                        ? Math.Round(user.TotalAmount / totals.TotalPostedAmount * 100, 1)
                        : 0;
                }

                return new UserPostingConcentrationResponse
                {
                    ReferenceId = referenceId,
                    Year = resolvedYear,
                    Period = period,
                    TotalEntries = totals.TotalEntries,
                    TotalPostedAmount = totals.TotalPostedAmount,
                    TopUserConcentrationRate = users.FirstOrDefault()?.PercentageOfEntries ?? 0,
                    Users = users
                };
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in GetUserPostingConcentrationAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<TrialBalanceMovementResponse> GetTrialBalanceMovementAsync(int? referenceId, int? currentYear, int? priorYear, int topAccounts)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();

                var resolvedCurrentYear = await ResolveTrialBalanceYearAsync(db, referenceId, currentYear);
                var resolvedPriorYear = priorYear ?? (resolvedCurrentYear - 1);

                var parameters = new DynamicParameters();
                parameters.Add("ReferenceId", referenceId);
                parameters.Add("CurrentYear", resolvedCurrentYear);
                parameters.Add("PriorYear", resolvedPriorYear);
                parameters.Add("TopAccounts", topAccounts <= 0 ? 10 : topAccounts);
                var materialityContext = await ResolveMaterialityContextAsync(db, referenceId);
                parameters.Add("MaterialityThreshold", materialityContext.Threshold);

                var query = @"
                    WITH materiality AS (
                        SELECT @MaterialityThreshold AS threshold
                    ),
                    current_year AS (
                        SELECT
                            account_number,
                            MAX(account_name) AS account_name,
                            MAX(fsli) AS fsli,
                            COALESCE(SUM(current_balance), 0) AS current_year_balance
                        FROM audit_trial_balance_snapshots
                        WHERE (@ReferenceId IS NULL OR reference_id = @ReferenceId)
                          AND fiscal_year = @CurrentYear
                        GROUP BY account_number
                    ),
                    prior_year AS (
                        SELECT
                            account_number,
                            MAX(account_name) AS account_name,
                            MAX(fsli) AS fsli,
                            COALESCE(SUM(current_balance), 0) AS prior_year_balance
                        FROM audit_trial_balance_snapshots
                        WHERE (@ReferenceId IS NULL OR reference_id = @ReferenceId)
                          AND fiscal_year = @PriorYear
                        GROUP BY account_number
                    )
                    SELECT
                        COALESCE(c.account_number, p.account_number) AS AccountNumber,
                        COALESCE(c.account_name, p.account_name, 'Unmapped Account') AS AccountName,
                        COALESCE(c.fsli, p.fsli, 'Unmapped FSLI') AS Fsli,
                        COALESCE(p.prior_year_balance, 0) AS PriorYearBalance,
                        COALESCE(c.current_year_balance, 0) AS CurrentYearBalance,
                        COALESCE(c.current_year_balance, 0) - COALESCE(p.prior_year_balance, 0) AS MovementAmount,
                        CASE
                            WHEN NULLIF(ABS(COALESCE(p.prior_year_balance, 0)), 0) IS NULL THEN NULL
                            ELSE ROUND(
                                (
                                    (COALESCE(c.current_year_balance, 0) - COALESCE(p.prior_year_balance, 0))
                                    / NULLIF(ABS(COALESCE(p.prior_year_balance, 0)), 0)
                                ) * 100, 1
                            )
                        END AS MovementPercent,
                        (
                            COALESCE(m.threshold, 0) > 0
                            AND ABS(COALESCE(c.current_year_balance, 0) - COALESCE(p.prior_year_balance, 0)) >= COALESCE(m.threshold, 0)
                        ) AS IsAboveMateriality
                    FROM current_year c
                    FULL OUTER JOIN prior_year p ON c.account_number = p.account_number
                    CROSS JOIN materiality m
                    WHERE COALESCE(c.current_year_balance, 0) <> 0 OR COALESCE(p.prior_year_balance, 0) <> 0
                    ORDER BY ABS(COALESCE(c.current_year_balance, 0) - COALESCE(p.prior_year_balance, 0)) DESC
                    LIMIT @TopAccounts;";

                var accounts = (await db.QueryAsync<TrialBalanceMovementItem>(query, parameters)).ToList();

                return new TrialBalanceMovementResponse
                {
                    ReferenceId = referenceId,
                    CurrentYear = resolvedCurrentYear,
                    PriorYear = resolvedPriorYear,
                    MaterialityThreshold = materialityContext.Threshold,
                    MaterialityThresholdSource = materialityContext.ThresholdSource,
                    MaterialityBenchmarkSummary = materialityContext.BenchmarkSummary,
                    TotalAccountsCompared = accounts.Count,
                    SignificantMovementsCount = accounts.Count(a => a.IsAboveMateriality),
                    LargestMovementAmount = accounts.Any() ? accounts.Max(a => Math.Abs(a.MovementAmount)) : 0,
                    Accounts = accounts
                };
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in GetTrialBalanceMovementAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<IndustryBenchmarkAnalyticsResponse> GetIndustryBenchmarkAnalyticsAsync(int? referenceId, int? year, int topMetrics)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();

                var resolvedYear = await ResolveIndustryBenchmarkYearAsync(db, referenceId, year);
                var requestedMetrics = topMetrics <= 0 ? 6 : topMetrics;
                var parameters = new DynamicParameters();
                parameters.Add("ReferenceId", referenceId);
                parameters.Add("Year", resolvedYear);

                var query = @"
                    WITH ranked AS (
                        SELECT
                            industry_code,
                            industry_name,
                            metric_name,
                            unit_of_measure,
                            company_value,
                            benchmark_median,
                            benchmark_lower_quartile,
                            benchmark_upper_quartile,
                            benchmark_source,
                            ROW_NUMBER() OVER (
                                PARTITION BY metric_name
                                ORDER BY
                                    CASE
                                        WHEN @ReferenceId IS NOT NULL AND reference_id = @ReferenceId THEN 0
                                        WHEN reference_id IS NULL THEN 1
                                        ELSE 2
                                    END,
                                    id DESC
                            ) AS rn
                        FROM audit_industry_benchmarks
                        WHERE fiscal_year = @Year
                          AND (
                                (@ReferenceId IS NULL AND reference_id IS NULL)
                                OR (@ReferenceId IS NOT NULL AND (reference_id = @ReferenceId OR reference_id IS NULL))
                              )
                    )
                    SELECT
                        COALESCE(industry_code, 'General') AS IndustryCode,
                        COALESCE(industry_name, 'Industry Benchmark') AS IndustryName,
                        metric_name AS MetricName,
                        COALESCE(unit_of_measure, 'ratio') AS UnitOfMeasure,
                        COALESCE(company_value, 0) AS CompanyValue,
                        COALESCE(benchmark_median, 0) AS BenchmarkMedian,
                        benchmark_lower_quartile AS BenchmarkLowerQuartile,
                        benchmark_upper_quartile AS BenchmarkUpperQuartile,
                        CASE
                            WHEN NULLIF(ABS(COALESCE(benchmark_median, 0)), 0) IS NULL THEN 0
                            ELSE ROUND(
                                (
                                    (COALESCE(company_value, 0) - COALESCE(benchmark_median, 0))
                                    / NULLIF(ABS(COALESCE(benchmark_median, 0)), 0)
                                ) * 100, 1
                            )
                        END AS VariancePercent,
                        CASE
                            WHEN benchmark_lower_quartile IS NOT NULL AND COALESCE(company_value, 0) < benchmark_lower_quartile THEN TRUE
                            WHEN benchmark_upper_quartile IS NOT NULL AND COALESCE(company_value, 0) > benchmark_upper_quartile THEN TRUE
                            ELSE FALSE
                        END AS IsOutsideBenchmarkRange,
                        COALESCE(benchmark_source, 'Benchmark dataset') AS BenchmarkSource
                    FROM ranked
                    WHERE rn = 1
                    ORDER BY
                        CASE
                            WHEN (
                                (benchmark_lower_quartile IS NOT NULL AND COALESCE(company_value, 0) < benchmark_lower_quartile)
                                OR (benchmark_upper_quartile IS NOT NULL AND COALESCE(company_value, 0) > benchmark_upper_quartile)
                            ) THEN 0
                            ELSE 1
                        END,
                        ABS(
                            CASE
                                WHEN NULLIF(ABS(COALESCE(benchmark_median, 0)), 0) IS NULL THEN 0
                                ELSE (
                                    (COALESCE(company_value, 0) - COALESCE(benchmark_median, 0))
                                    / NULLIF(ABS(COALESCE(benchmark_median, 0)), 0)
                                ) * 100
                            END
                        ) DESC,
                        metric_name;";

                var metrics = (await db.QueryAsync<IndustryBenchmarkMetricItem>(query, parameters)).ToList();

                return new IndustryBenchmarkAnalyticsResponse
                {
                    ReferenceId = referenceId,
                    Year = resolvedYear,
                    IndustryCode = metrics.FirstOrDefault()?.IndustryCode,
                    IndustryName = metrics.FirstOrDefault()?.IndustryName,
                    MetricsCompared = metrics.Count,
                    OutsideBenchmarkCount = metrics.Count(metric => metric.IsOutsideBenchmarkRange),
                    LargestVariancePercent = metrics.Any() ? metrics.Max(metric => Math.Abs(metric.VariancePercent)) : 0,
                    Metrics = metrics.Take(requestedMetrics).ToList()
                };
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in GetIndustryBenchmarkAnalyticsAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<ReasonabilityForecastAnalyticsResponse> GetReasonabilityForecastAnalyticsAsync(int? referenceId, int? year, int topItems)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();

                var resolvedYear = await ResolveReasonabilityForecastYearAsync(db, referenceId, year);
                var requestedItems = topItems <= 0 ? 6 : topItems;
                var parameters = new DynamicParameters();
                parameters.Add("ReferenceId", referenceId);
                parameters.Add("Year", resolvedYear);
                var materialityContext = await ResolveMaterialityContextAsync(db, referenceId);
                parameters.Add("MaterialityThreshold", materialityContext.Threshold);

                var query = @"
                    WITH materiality AS (
                        SELECT @MaterialityThreshold AS threshold
                    )
                    SELECT
                        metric_name AS MetricName,
                        COALESCE(metric_category, 'General') AS MetricCategory,
                        COALESCE(actual_value, 0) AS ActualValue,
                        COALESCE(expected_value, 0) AS ExpectedValue,
                        budget_value AS BudgetValue,
                        prior_year_value AS PriorYearValue,
                        COALESCE(actual_value, 0) - COALESCE(expected_value, 0) AS VarianceAmount,
                        CASE
                            WHEN NULLIF(ABS(COALESCE(expected_value, 0)), 0) IS NULL THEN NULL
                            ELSE ROUND(
                                (
                                    (COALESCE(actual_value, 0) - COALESCE(expected_value, 0))
                                    / NULLIF(ABS(COALESCE(expected_value, 0)), 0)
                                ) * 100, 1
                            )
                        END AS VariancePercent,
                        CASE
                            WHEN GREATEST(COALESCE(rf.threshold_amount, 0), COALESCE(m.threshold, 0)) > 0
                                 AND ABS(COALESCE(actual_value, 0) - COALESCE(expected_value, 0)) >= GREATEST(COALESCE(rf.threshold_amount, 0), COALESCE(m.threshold, 0))
                                THEN TRUE
                            WHEN COALESCE(rf.threshold_percent, 0) > 0
                                 AND NULLIF(ABS(COALESCE(expected_value, 0)), 0) IS NOT NULL
                                 AND ABS(
                                        (
                                            (COALESCE(actual_value, 0) - COALESCE(expected_value, 0))
                                            / NULLIF(ABS(COALESCE(expected_value, 0)), 0)
                                        ) * 100
                                     ) >= COALESCE(rf.threshold_percent, 0)
                                THEN TRUE
                            ELSE FALSE
                        END AS IsAboveThreshold,
                        COALESCE(rf.forecast_basis, 'Reasonability') AS ForecastBasis,
                        COALESCE(rf.explanation, '') AS Explanation
                    FROM audit_reasonability_forecasts rf
                    CROSS JOIN materiality m
                    WHERE (@ReferenceId IS NULL OR rf.reference_id = @ReferenceId)
                      AND rf.fiscal_year = @Year
                    ORDER BY
                        CASE
                            WHEN
                                (
                                    GREATEST(COALESCE(rf.threshold_amount, 0), COALESCE(m.threshold, 0)) > 0
                                    AND ABS(COALESCE(actual_value, 0) - COALESCE(expected_value, 0)) >= GREATEST(COALESCE(rf.threshold_amount, 0), COALESCE(m.threshold, 0))
                                )
                                OR
                                (
                                    COALESCE(rf.threshold_percent, 0) > 0
                                    AND NULLIF(ABS(COALESCE(expected_value, 0)), 0) IS NOT NULL
                                    AND ABS(
                                            (
                                                (COALESCE(actual_value, 0) - COALESCE(expected_value, 0))
                                                / NULLIF(ABS(COALESCE(expected_value, 0)), 0)
                                            ) * 100
                                        ) >= COALESCE(rf.threshold_percent, 0)
                                )
                            THEN 0
                            ELSE 1
                        END,
                        ABS(COALESCE(actual_value, 0) - COALESCE(expected_value, 0)) DESC,
                        metric_name;";

                var items = (await db.QueryAsync<ReasonabilityForecastItem>(query, parameters)).ToList();
                var forecastBases = items
                    .Select(item => item.ForecastBasis)
                    .Where(value => !string.IsNullOrWhiteSpace(value))
                    .Distinct(StringComparer.OrdinalIgnoreCase)
                    .ToList();

                return new ReasonabilityForecastAnalyticsResponse
                {
                    ReferenceId = referenceId,
                    Year = resolvedYear,
                    ForecastBasis = forecastBases.Count == 0 ? "Reasonability" : forecastBases.Count == 1 ? forecastBases[0] : "Mixed",
                    MaterialityThreshold = materialityContext.Threshold,
                    MaterialityThresholdSource = materialityContext.ThresholdSource,
                    MaterialityBenchmarkSummary = materialityContext.BenchmarkSummary,
                    MetricsEvaluated = items.Count,
                    SignificantVarianceCount = items.Count(item => item.IsAboveThreshold),
                    LargestVarianceAmount = items.Any() ? items.Max(item => Math.Abs(item.VarianceAmount)) : 0,
                    Items = items.Take(requestedItems).ToList()
                };
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in GetReasonabilityForecastAnalyticsAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<AuditAnalyticsImportResult> ImportAnalyticsCsvAsync(Stream stream, AuditAnalyticsImportRequest request, string sourceFileName)
        {
            if (stream == null)
                throw new ArgumentNullException(nameof(stream));
            if (request == null)
                throw new ArgumentNullException(nameof(request));

            var datasetType = NormalizeDatasetType(request.DatasetType);
            if (string.IsNullOrWhiteSpace(datasetType))
                throw new ArgumentException("Dataset type is required.", nameof(request.DatasetType));

            var rows = ReadCsvRows(stream);
            if (rows.Count == 0)
                throw new InvalidOperationException("The uploaded CSV does not contain any data rows.");

            var missingColumns = GetRequiredColumns(datasetType)
                .Where(required => !rows[0].ContainsKey(required))
                .ToList();

            if (missingColumns.Count > 0)
                throw new InvalidOperationException($"Missing required columns for {datasetType}: {string.Join(", ", missingColumns)}");

            using IDbConnection db = new NpgsqlConnection(_connectionString);
            db.Open();
            using var transaction = db.BeginTransaction();

            try
            {
                var batchId = await db.ExecuteScalarAsync<int>(@"
                    INSERT INTO audit_analytics_import_batches
                    (
                        reference_id,
                        dataset_type,
                        batch_name,
                        source_system,
                        source_file_name,
                        row_count,
                        imported_by_user_id,
                        imported_by_name,
                        notes
                    )
                    VALUES
                    (
                        @ReferenceId,
                        @DatasetType,
                        @BatchName,
                        @SourceSystem,
                        @SourceFileName,
                        0,
                        @ImportedByUserId,
                        @ImportedByName,
                        @Notes
                    )
                    RETURNING id;",
                    new
                    {
                        request.ReferenceId,
                        DatasetType = datasetType,
                        BatchName = string.IsNullOrWhiteSpace(request.BatchName) ? Path.GetFileNameWithoutExtension(sourceFileName) : request.BatchName,
                        SourceSystem = request.SourceSystem,
                        SourceFileName = sourceFileName,
                        request.ImportedByUserId,
                        request.ImportedByName,
                        request.Notes
                    },
                    transaction);

                var validationErrors = new List<string>();
                var insertedRows = 0;

                for (var index = 0; index < rows.Count; index++)
                {
                    var rowNumber = index + 2;
                    try
                    {
                        switch (datasetType)
                        {
                            case "journal_entries":
                                insertedRows += await InsertJournalEntryAsync(db, transaction, batchId, request, rows[index]);
                                break;
                            case "trial_balance":
                                insertedRows += await InsertTrialBalanceAsync(db, transaction, batchId, request, rows[index]);
                                break;
                            case "industry_benchmarks":
                                insertedRows += await InsertIndustryBenchmarkAsync(db, transaction, batchId, request, rows[index]);
                                break;
                            case "reasonability_forecasts":
                                insertedRows += await InsertReasonabilityForecastAsync(db, transaction, batchId, request, rows[index]);
                                break;
                            default:
                                throw new InvalidOperationException($"Unsupported dataset type: {datasetType}");
                        }
                    }
                    catch (Exception ex)
                    {
                        validationErrors.Add($"Row {rowNumber}: {ex.Message}");
                        if (validationErrors.Count >= 10)
                            break;
                    }
                }

                if (validationErrors.Count > 0)
                    throw new InvalidOperationException(string.Join(" | ", validationErrors));

                await db.ExecuteAsync(
                    "UPDATE audit_analytics_import_batches SET row_count = @RowCount WHERE id = @BatchId;",
                    new { RowCount = insertedRows, BatchId = batchId },
                    transaction);

                transaction.Commit();

                return new AuditAnalyticsImportResult
                {
                    BatchId = batchId,
                    ReferenceId = request.ReferenceId,
                    DatasetType = datasetType,
                    SourceFileName = sourceFileName,
                    RowCount = insertedRows,
                    ImportedAt = DateTime.UtcNow,
                    Status = "Imported"
                };
            }
            catch
            {
                transaction.Rollback();
                throw;
            }
        }

        public async Task<List<AuditAnalyticsImportBatchSummary>> GetAnalyticsImportBatchesAsync(int? referenceId, string? datasetType, int limit)
        {
            using IDbConnection db = new NpgsqlConnection(_connectionString);
            db.Open();

            var normalizedDatasetType = NormalizeDatasetType(datasetType);
            var resolvedLimit = limit <= 0 ? 20 : limit;

            var query = @"
                SELECT
                    id,
                    reference_id AS ReferenceId,
                    dataset_type AS DatasetType,
                    batch_name AS BatchName,
                    source_system AS SourceSystem,
                    source_file_name AS SourceFileName,
                    row_count AS RowCount,
                    imported_by_user_id AS ImportedByUserId,
                    imported_by_name AS ImportedByName,
                    imported_at AS ImportedAt,
                    notes
                FROM audit_analytics_import_batches
                WHERE (@ReferenceId IS NULL OR reference_id = @ReferenceId)
                  AND (@DatasetType IS NULL OR dataset_type = @DatasetType)
                ORDER BY imported_at DESC, id DESC
                LIMIT @Limit;";

            var batches = await db.QueryAsync<AuditAnalyticsImportBatchSummary>(
                query,
                new { ReferenceId = referenceId, DatasetType = normalizedDatasetType, Limit = resolvedLimit });

            return batches.ToList();
        }

        private async Task<JournalExceptionAnalyticsResponse> GetJournalAnalyticsInternalAsync(int? referenceId, int? year, int? period)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();

                var resolvedYear = await ResolveJournalYearAsync(db, referenceId, year);
                var parameters = new DynamicParameters();
                parameters.Add("ReferenceId", referenceId);
                parameters.Add("Year", resolvedYear);
                parameters.Add("Period", period);
                var materialityContext = await ResolveMaterialityContextAsync(db, referenceId);
                parameters.Add("MaterialityThreshold", materialityContext.Threshold);

                var query = @"
                    WITH materiality AS (
                        SELECT @MaterialityThreshold AS threshold
                    ),
                    filtered AS (
                        SELECT
                            entry_id.id,
                            entry_id.posting_date,
                            entry_id.fiscal_period,
                            entry_id.is_manual,
                            entry_id.is_period_end,
                            COALESCE(NULLIF(TRIM(entry_id.user_name), ''), NULLIF(TRIM(entry_id.user_id), ''), 'Unassigned') AS posting_user,
                            ABS(COALESCE(entry_id.amount, COALESCE(entry_id.debit_amount, 0) - COALESCE(entry_id.credit_amount, 0))) AS abs_amount
                        FROM audit_gl_journal_entries entry_id
                        WHERE (@ReferenceId IS NULL OR entry_id.reference_id = @ReferenceId)
                          AND entry_id.fiscal_year = @Year
                          AND (@Period IS NULL OR entry_id.fiscal_period = @Period)
                    )
                    SELECT
                        COUNT(*) AS TotalEntries,
                        COUNT(*) FILTER (WHERE COALESCE(is_manual, false)) AS ManualEntries,
                        COUNT(*) FILTER (WHERE MOD(abs_amount, 1000) = 0 AND abs_amount >= 1000) AS RoundAmountEntries,
                        COUNT(*) FILTER (WHERE EXTRACT(ISODOW FROM posting_date) IN (6, 7)) AS WeekendEntries,
                        COUNT(*) FILTER (WHERE hc.id IS NOT NULL) AS HolidayEntries,
                        COUNT(*) FILTER (WHERE EXTRACT(ISODOW FROM posting_date) IN (6, 7) OR hc.id IS NOT NULL) AS WeekendOrHolidayEntries,
                        COUNT(*) FILTER (
                            WHERE COALESCE(is_period_end, false)
                               OR EXTRACT(DAY FROM posting_date) >= 28
                        ) AS PeriodEndEntries,
                        COUNT(*) FILTER (
                            WHERE COALESCE(m.threshold, 0) > 0
                              AND abs_amount >= COALESCE(m.threshold, 0)
                        ) AS MaterialityBreaches,
                        COUNT(DISTINCT posting_user) AS UniqueUsers,
                        COALESCE(SUM(abs_amount), 0) AS TotalPostedAmount,
                        COALESCE(MAX(abs_amount), 0) AS MaxEntryAmount,
                        COALESCE(m.threshold, 0) AS MaterialityThreshold
                    FROM filtered f
                    CROSS JOIN materiality m
                    LEFT JOIN audit_holiday_calendar hc
                      ON f.posting_date = hc.holiday_date
                     AND hc.is_active = true;";

                var response = await db.QueryFirstOrDefaultAsync<JournalExceptionAnalyticsResponse>(query, parameters)
                    ?? new JournalExceptionAnalyticsResponse();

                var topUserEntryCount = await db.ExecuteScalarAsync<int>(@"
                    WITH filtered AS (
                        SELECT
                            COALESCE(NULLIF(TRIM(user_name), ''), NULLIF(TRIM(user_id), ''), 'Unassigned') AS posting_user
                        FROM audit_gl_journal_entries
                        WHERE (@ReferenceId IS NULL OR reference_id = @ReferenceId)
                          AND fiscal_year = @Year
                          AND (@Period IS NULL OR fiscal_period = @Period)
                    )
                    SELECT COALESCE(MAX(entry_count), 0)
                    FROM (
                        SELECT COUNT(*) AS entry_count
                        FROM filtered
                        GROUP BY posting_user
                    ) users;", parameters);

                response.ReferenceId = referenceId;
                response.Year = resolvedYear;
                response.Period = period;
                response.MaterialityThresholdSource = materialityContext.ThresholdSource;
                response.MaterialityBenchmarkSummary = materialityContext.BenchmarkSummary;
                response.ManualEntryRate = response.TotalEntries > 0
                    ? Math.Round((decimal)response.ManualEntries / response.TotalEntries * 100, 1)
                    : 0;
                response.WeekendHolidayRate = response.TotalEntries > 0
                    ? Math.Round((decimal)response.WeekendOrHolidayEntries / response.TotalEntries * 100, 1)
                    : 0;
                response.TopUserConcentrationRate = response.TotalEntries > 0
                    ? Math.Round((decimal)topUserEntryCount / response.TotalEntries * 100, 1)
                    : 0;

                return response;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in GetJournalAnalyticsInternalAsync: {ex.Message}");
                throw;
            }
        }

        private static List<Dictionary<string, string>> ReadCsvRows(Stream stream)
        {
            if (stream.CanSeek)
                stream.Position = 0;

            using var parser = new TextFieldParser(stream)
            {
                TextFieldType = FieldType.Delimited,
                HasFieldsEnclosedInQuotes = true,
                TrimWhiteSpace = true
            };
            parser.SetDelimiters(",");

            if (parser.EndOfData)
                return new List<Dictionary<string, string>>();

            var headerFields = parser.ReadFields() ?? Array.Empty<string>();
            var normalizedHeaders = headerFields
                .Select(NormalizeColumnName)
                .ToList();

            var rows = new List<Dictionary<string, string>>();
            while (!parser.EndOfData)
            {
                var fields = parser.ReadFields();
                if (fields == null || fields.All(string.IsNullOrWhiteSpace))
                    continue;

                var row = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
                for (var index = 0; index < normalizedHeaders.Count; index++)
                {
                    var header = normalizedHeaders[index];
                    if (string.IsNullOrWhiteSpace(header))
                        continue;
                    row[header] = index < fields.Length ? fields[index]?.Trim() ?? string.Empty : string.Empty;
                }

                rows.Add(row);
            }

            return rows;
        }

        private static string NormalizeDatasetType(string? datasetType)
        {
            var value = (datasetType ?? string.Empty).Trim().ToLowerInvariant();
            return value switch
            {
                "journal" or "journal_entry" or "journal_entries" => "journal_entries",
                "trial_balance" or "trialbalance" or "tb" => "trial_balance",
                "industry_benchmarks" or "industry_benchmark" or "benchmarks" => "industry_benchmarks",
                "reasonability_forecasts" or "reasonability_forecast" or "forecasts" => "reasonability_forecasts",
                _ => value
            };
        }

        private static IReadOnlyCollection<string> GetRequiredColumns(string datasetType)
        {
            return datasetType switch
            {
                "journal_entries" => new[] { "fiscal_year", "posting_date", "journal_number" },
                "trial_balance" => new[] { "fiscal_year", "account_number", "current_balance" },
                "industry_benchmarks" => new[] { "fiscal_year", "metric_name", "company_value", "benchmark_median" },
                "reasonability_forecasts" => new[] { "fiscal_year", "metric_name", "actual_value", "expected_value" },
                _ => Array.Empty<string>()
            };
        }

        private static string NormalizeColumnName(string? value)
        {
            if (string.IsNullOrWhiteSpace(value))
                return string.Empty;

            var normalized = new string(value.Trim().ToLowerInvariant()
                .Select(ch => char.IsLetterOrDigit(ch) ? ch : '_')
                .ToArray());

            while (normalized.Contains("__", StringComparison.Ordinal))
                normalized = normalized.Replace("__", "_", StringComparison.Ordinal);

            return normalized.Trim('_');
        }

        private static string? GetStringValue(IReadOnlyDictionary<string, string> row, params string[] aliases)
        {
            foreach (var alias in aliases.Select(NormalizeColumnName))
            {
                if (row.TryGetValue(alias, out var value) && !string.IsNullOrWhiteSpace(value))
                    return value.Trim();
            }

            return null;
        }

        private static int GetRequiredInt(IReadOnlyDictionary<string, string> row, params string[] aliases)
        {
            var value = GetStringValue(row, aliases)
                ?? throw new InvalidOperationException($"Required integer field missing: {aliases[0]}");
            return ParseInt(value, aliases[0]);
        }

        private static int? GetOptionalInt(IReadOnlyDictionary<string, string> row, params string[] aliases)
        {
            var value = GetStringValue(row, aliases);
            return string.IsNullOrWhiteSpace(value) ? null : ParseInt(value, aliases[0]);
        }

        private static decimal GetRequiredDecimal(IReadOnlyDictionary<string, string> row, params string[] aliases)
        {
            var value = GetStringValue(row, aliases)
                ?? throw new InvalidOperationException($"Required numeric field missing: {aliases[0]}");
            return ParseDecimal(value, aliases[0]);
        }

        private static decimal? GetOptionalDecimal(IReadOnlyDictionary<string, string> row, params string[] aliases)
        {
            var value = GetStringValue(row, aliases);
            return string.IsNullOrWhiteSpace(value) ? null : ParseDecimal(value, aliases[0]);
        }

        private static DateTime GetRequiredDate(IReadOnlyDictionary<string, string> row, params string[] aliases)
        {
            var value = GetStringValue(row, aliases)
                ?? throw new InvalidOperationException($"Required date field missing: {aliases[0]}");
            return ParseDate(value, aliases[0]);
        }

        private static DateTime? GetOptionalDate(IReadOnlyDictionary<string, string> row, params string[] aliases)
        {
            var value = GetStringValue(row, aliases);
            return string.IsNullOrWhiteSpace(value) ? null : ParseDate(value, aliases[0]);
        }

        private static bool GetOptionalBool(IReadOnlyDictionary<string, string> row, params string[] aliases)
        {
            var value = GetStringValue(row, aliases);
            if (string.IsNullOrWhiteSpace(value))
                return false;

            var normalized = value.Trim().ToLowerInvariant();
            return normalized is "true" or "1" or "yes" or "y";
        }

        private static int ParseInt(string value, string fieldName)
        {
            if (int.TryParse(value, NumberStyles.Integer, CultureInfo.InvariantCulture, out var parsed))
                return parsed;
            throw new InvalidOperationException($"Invalid integer value for {fieldName}: {value}");
        }

        private static decimal ParseDecimal(string value, string fieldName)
        {
            var sanitized = value.Replace(" ", string.Empty).Replace(",", string.Empty);
            if (decimal.TryParse(sanitized, NumberStyles.Any, CultureInfo.InvariantCulture, out var parsed))
                return parsed;
            throw new InvalidOperationException($"Invalid numeric value for {fieldName}: {value}");
        }

        private static DateTime ParseDate(string value, string fieldName)
        {
            if (DateTime.TryParse(value, CultureInfo.InvariantCulture, DateTimeStyles.AssumeLocal, out var parsed))
                return parsed.Date;
            throw new InvalidOperationException($"Invalid date value for {fieldName}: {value}");
        }

        private static async Task<int> InsertJournalEntryAsync(
            IDbConnection db,
            IDbTransaction transaction,
            int batchId,
            AuditAnalyticsImportRequest request,
            IReadOnlyDictionary<string, string> row)
        {
            var sql = @"
                INSERT INTO audit_gl_journal_entries
                (
                    import_batch_id,
                    reference_id,
                    company_code,
                    fiscal_year,
                    fiscal_period,
                    posting_date,
                    document_date,
                    journal_number,
                    line_number,
                    account_number,
                    account_name,
                    fsli,
                    business_unit,
                    cost_center,
                    user_id,
                    user_name,
                    description,
                    amount,
                    debit_amount,
                    credit_amount,
                    currency_code,
                    source_system,
                    source_document_number,
                    is_manual,
                    is_period_end
                )
                VALUES
                (
                    @ImportBatchId,
                    @ReferenceId,
                    @CompanyCode,
                    @FiscalYear,
                    @FiscalPeriod,
                    @PostingDate,
                    @DocumentDate,
                    @JournalNumber,
                    @LineNumber,
                    @AccountNumber,
                    @AccountName,
                    @Fsli,
                    @BusinessUnit,
                    @CostCenter,
                    @UserId,
                    @UserName,
                    @Description,
                    @Amount,
                    @DebitAmount,
                    @CreditAmount,
                    @CurrencyCode,
                    @SourceSystem,
                    @SourceDocumentNumber,
                    @IsManual,
                    @IsPeriodEnd
                );";

            await db.ExecuteAsync(sql, new
            {
                ImportBatchId = batchId,
                request.ReferenceId,
                CompanyCode = GetStringValue(row, "company_code"),
                FiscalYear = GetRequiredInt(row, "fiscal_year"),
                FiscalPeriod = GetOptionalInt(row, "fiscal_period", "period"),
                PostingDate = GetRequiredDate(row, "posting_date"),
                DocumentDate = GetOptionalDate(row, "document_date"),
                JournalNumber = GetStringValue(row, "journal_number", "document_number")
                    ?? throw new InvalidOperationException("Required field missing: journal_number"),
                LineNumber = GetOptionalInt(row, "line_number") ?? 1,
                AccountNumber = GetStringValue(row, "account_number", "gl_account"),
                AccountName = GetStringValue(row, "account_name"),
                Fsli = GetStringValue(row, "fsli"),
                BusinessUnit = GetStringValue(row, "business_unit"),
                CostCenter = GetStringValue(row, "cost_center"),
                UserId = GetStringValue(row, "user_id"),
                UserName = GetStringValue(row, "user_name"),
                Description = GetStringValue(row, "description", "line_description"),
                Amount = GetRequiredDecimal(row, "amount"),
                DebitAmount = GetOptionalDecimal(row, "debit_amount"),
                CreditAmount = GetOptionalDecimal(row, "credit_amount"),
                CurrencyCode = GetStringValue(row, "currency_code", "currency"),
                SourceSystem = GetStringValue(row, "source_system") ?? request.SourceSystem,
                SourceDocumentNumber = GetStringValue(row, "source_document_number"),
                IsManual = GetOptionalBool(row, "is_manual", "manual"),
                IsPeriodEnd = GetOptionalBool(row, "is_period_end", "period_end")
            }, transaction);

            return 1;
        }

        private static async Task<int> InsertTrialBalanceAsync(
            IDbConnection db,
            IDbTransaction transaction,
            int batchId,
            AuditAnalyticsImportRequest request,
            IReadOnlyDictionary<string, string> row)
        {
            var sql = @"
                INSERT INTO audit_trial_balance_snapshots
                (
                    import_batch_id,
                    reference_id,
                    fiscal_year,
                    period_label,
                    as_of_date,
                    account_number,
                    account_name,
                    fsli,
                    business_unit,
                    current_balance,
                    currency_code
                )
                VALUES
                (
                    @ImportBatchId,
                    @ReferenceId,
                    @FiscalYear,
                    @PeriodLabel,
                    @AsOfDate,
                    @AccountNumber,
                    @AccountName,
                    @Fsli,
                    @BusinessUnit,
                    @CurrentBalance,
                    @CurrencyCode
                );";

            await db.ExecuteAsync(sql, new
            {
                ImportBatchId = batchId,
                request.ReferenceId,
                FiscalYear = GetRequiredInt(row, "fiscal_year"),
                PeriodLabel = GetStringValue(row, "period_label", "period"),
                AsOfDate = GetOptionalDate(row, "as_of_date"),
                AccountNumber = GetStringValue(row, "account_number", "gl_account")
                    ?? throw new InvalidOperationException("Required field missing: account_number"),
                AccountName = GetStringValue(row, "account_name"),
                Fsli = GetStringValue(row, "fsli"),
                BusinessUnit = GetStringValue(row, "business_unit"),
                CurrentBalance = GetRequiredDecimal(row, "current_balance", "balance"),
                CurrencyCode = GetStringValue(row, "currency_code", "currency")
            }, transaction);

            return 1;
        }

        private static async Task<int> InsertIndustryBenchmarkAsync(
            IDbConnection db,
            IDbTransaction transaction,
            int batchId,
            AuditAnalyticsImportRequest request,
            IReadOnlyDictionary<string, string> row)
        {
            var sql = @"
                INSERT INTO audit_industry_benchmarks
                (
                    import_batch_id,
                    reference_id,
                    fiscal_year,
                    industry_code,
                    industry_name,
                    metric_name,
                    unit_of_measure,
                    company_value,
                    benchmark_median,
                    benchmark_lower_quartile,
                    benchmark_upper_quartile,
                    benchmark_source,
                    notes
                )
                VALUES
                (
                    @ImportBatchId,
                    @ReferenceId,
                    @FiscalYear,
                    @IndustryCode,
                    @IndustryName,
                    @MetricName,
                    @UnitOfMeasure,
                    @CompanyValue,
                    @BenchmarkMedian,
                    @BenchmarkLowerQuartile,
                    @BenchmarkUpperQuartile,
                    @BenchmarkSource,
                    @Notes
                );";

            await db.ExecuteAsync(sql, new
            {
                ImportBatchId = batchId,
                request.ReferenceId,
                FiscalYear = GetRequiredInt(row, "fiscal_year"),
                IndustryCode = GetStringValue(row, "industry_code"),
                IndustryName = GetStringValue(row, "industry_name"),
                MetricName = GetStringValue(row, "metric_name")
                    ?? throw new InvalidOperationException("Required field missing: metric_name"),
                UnitOfMeasure = GetStringValue(row, "unit_of_measure", "unit"),
                CompanyValue = GetRequiredDecimal(row, "company_value"),
                BenchmarkMedian = GetRequiredDecimal(row, "benchmark_median"),
                BenchmarkLowerQuartile = GetOptionalDecimal(row, "benchmark_lower_quartile"),
                BenchmarkUpperQuartile = GetOptionalDecimal(row, "benchmark_upper_quartile"),
                BenchmarkSource = GetStringValue(row, "benchmark_source", "source"),
                Notes = GetStringValue(row, "notes")
            }, transaction);

            return 1;
        }

        private static async Task<int> InsertReasonabilityForecastAsync(
            IDbConnection db,
            IDbTransaction transaction,
            int batchId,
            AuditAnalyticsImportRequest request,
            IReadOnlyDictionary<string, string> row)
        {
            var sql = @"
                INSERT INTO audit_reasonability_forecasts
                (
                    import_batch_id,
                    reference_id,
                    fiscal_year,
                    fiscal_period,
                    metric_name,
                    metric_category,
                    forecast_basis,
                    actual_value,
                    expected_value,
                    budget_value,
                    prior_year_value,
                    threshold_amount,
                    threshold_percent,
                    explanation
                )
                VALUES
                (
                    @ImportBatchId,
                    @ReferenceId,
                    @FiscalYear,
                    @FiscalPeriod,
                    @MetricName,
                    @MetricCategory,
                    @ForecastBasis,
                    @ActualValue,
                    @ExpectedValue,
                    @BudgetValue,
                    @PriorYearValue,
                    @ThresholdAmount,
                    @ThresholdPercent,
                    @Explanation
                );";

            await db.ExecuteAsync(sql, new
            {
                ImportBatchId = batchId,
                request.ReferenceId,
                FiscalYear = GetRequiredInt(row, "fiscal_year"),
                FiscalPeriod = GetOptionalInt(row, "fiscal_period", "period"),
                MetricName = GetStringValue(row, "metric_name")
                    ?? throw new InvalidOperationException("Required field missing: metric_name"),
                MetricCategory = GetStringValue(row, "metric_category"),
                ForecastBasis = GetStringValue(row, "forecast_basis"),
                ActualValue = GetRequiredDecimal(row, "actual_value"),
                ExpectedValue = GetRequiredDecimal(row, "expected_value"),
                BudgetValue = GetOptionalDecimal(row, "budget_value"),
                PriorYearValue = GetOptionalDecimal(row, "prior_year_value"),
                ThresholdAmount = GetOptionalDecimal(row, "threshold_amount"),
                ThresholdPercent = GetOptionalDecimal(row, "threshold_percent"),
                Explanation = GetStringValue(row, "explanation", "notes")
            }, transaction);

            return 1;
        }

        private async Task<int> ResolveJournalYearAsync(IDbConnection db, int? referenceId, int? year)
        {
            if (year.HasValue)
                return year.Value;

            var resolved = await db.ExecuteScalarAsync<int?>(@"
                SELECT MAX(fiscal_year)
                FROM audit_gl_journal_entries
                WHERE (@ReferenceId IS NULL OR reference_id = @ReferenceId);",
                new { ReferenceId = referenceId });

            return resolved ?? DateTime.UtcNow.Year;
        }

        private async Task<int> ResolveTrialBalanceYearAsync(IDbConnection db, int? referenceId, int? year)
        {
            if (year.HasValue)
                return year.Value;

            var resolved = await db.ExecuteScalarAsync<int?>(@"
                SELECT MAX(fiscal_year)
                FROM audit_trial_balance_snapshots
                WHERE (@ReferenceId IS NULL OR reference_id = @ReferenceId);",
                new { ReferenceId = referenceId });

            return resolved ?? DateTime.UtcNow.Year;
        }

        private async Task<int> ResolveIndustryBenchmarkYearAsync(IDbConnection db, int? referenceId, int? year)
        {
            if (year.HasValue)
                return year.Value;

            var resolved = await db.ExecuteScalarAsync<int?>(@"
                SELECT MAX(fiscal_year)
                FROM audit_industry_benchmarks
                WHERE
                    (
                        (@ReferenceId IS NULL AND reference_id IS NULL)
                        OR (@ReferenceId IS NOT NULL AND (reference_id = @ReferenceId OR reference_id IS NULL))
                    );",
                new { ReferenceId = referenceId });

            return resolved ?? DateTime.UtcNow.Year;
        }

        private async Task<int> ResolveReasonabilityForecastYearAsync(IDbConnection db, int? referenceId, int? year)
        {
            if (year.HasValue)
                return year.Value;

            var resolved = await db.ExecuteScalarAsync<int?>(@"
                SELECT MAX(fiscal_year)
                FROM audit_reasonability_forecasts
                WHERE (@ReferenceId IS NULL OR reference_id = @ReferenceId);",
                new { ReferenceId = referenceId });

            return resolved ?? DateTime.UtcNow.Year;
        }

        private sealed class MaterialityContextRow
        {
            public decimal Threshold { get; set; }
            public string ThresholdSource { get; set; }
            public string BenchmarkSummary { get; set; }
        }
    }
}
