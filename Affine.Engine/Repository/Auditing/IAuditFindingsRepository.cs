using Affine.Engine.Model.Auditing.AuditUniverse;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace Affine.Engine.Repository.Auditing
{
    public interface IAuditFindingsRepository
    {
        // Findings CRUD
        Task<AuditFinding> GetFindingAsync(int id);
        Task<List<AuditFinding>> GetFindingsByReferenceAsync(int referenceId);
        Task<List<AuditFinding>> GetFindingsByUniverseNodeAsync(int auditUniverseId);
        Task<PaginatedResponse<FindingListItem>> GetFindingsAsync(FindingsFilterRequest filter);
        Task<AuditFinding> CreateFindingAsync(CreateAuditFindingRequest request);
        Task<AuditFinding> UpdateFindingAsync(UpdateAuditFindingRequest request);
        Task<bool> DeleteFindingAsync(int id);

        // Recommendations CRUD
        Task<AuditRecommendation> GetRecommendationAsync(int id);
        Task<List<AuditRecommendation>> GetRecommendationsByFindingAsync(int findingId);
        Task<AuditRecommendation> CreateRecommendationAsync(CreateRecommendationRequest request);
        Task<AuditRecommendation> UpdateRecommendationAsync(UpdateRecommendationRequest request);
        Task<bool> DeleteRecommendationAsync(int id);

        // Lookups
        Task<List<FindingSeverity>> GetSeveritiesAsync();
        Task<List<FindingStatus>> GetFindingStatusesAsync();
        Task<List<RecommendationStatus>> GetRecommendationStatusesAsync();

        // Analytics
        Task<FindingsAgingResponse> GetFindingsAgingAsync(int? referenceId, int? auditUniverseId);
        Task<RecommendationSummary> GetRecommendationSummaryAsync(int? referenceId, int? auditUniverseId);

        // Audit Coverage
        Task<List<AuditCoverage>> GetAuditCoverageAsync(int auditUniverseId, int? year);
        Task<AuditCoverageMapResponse> GetAuditCoverageMapAsync(int year, int? quarter);
        Task<bool> UpdateAuditCoverageAsync(UpdateAuditCoverageRequest request);

        // Risk Trends
        Task<RiskTrendResponse> GetRiskTrendAsync(int? referenceId, int? auditUniverseId, int months);
        Task<RiskVelocityResponse> GetRiskVelocityAsync(int? referenceId, int? auditUniverseId);
        Task<bool> CreateRiskTrendSnapshotAsync(int? referenceId, int? auditUniverseId);
    }
}
