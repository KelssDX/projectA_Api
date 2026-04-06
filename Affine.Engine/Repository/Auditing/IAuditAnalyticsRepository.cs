using Affine.Engine.Model.Auditing.AuditUniverse;
using System.Threading.Tasks;
using System.Collections.Generic;
using System.IO;

namespace Affine.Engine.Repository.Auditing
{
    public interface IAuditAnalyticsRepository
    {
        Task<JournalExceptionAnalyticsResponse> GetManagementOverrideAnalyticsAsync(int? referenceId, int? year, int? period);
        Task<JournalExceptionAnalyticsResponse> GetJournalExceptionAnalyticsAsync(int? referenceId, int? year, int? period);
        Task<UserPostingConcentrationResponse> GetUserPostingConcentrationAsync(int? referenceId, int? year, int? period, int topUsers);
        Task<TrialBalanceMovementResponse> GetTrialBalanceMovementAsync(int? referenceId, int? currentYear, int? priorYear, int topAccounts);
        Task<IndustryBenchmarkAnalyticsResponse> GetIndustryBenchmarkAnalyticsAsync(int? referenceId, int? year, int topMetrics);
        Task<ReasonabilityForecastAnalyticsResponse> GetReasonabilityForecastAnalyticsAsync(int? referenceId, int? year, int topItems);
        Task<AuditAnalyticsImportResult> ImportAnalyticsCsvAsync(Stream stream, AuditAnalyticsImportRequest request, string sourceFileName);
        Task<List<AuditAnalyticsImportBatchSummary>> GetAnalyticsImportBatchesAsync(int? referenceId, string? datasetType, int limit);
    }
}
