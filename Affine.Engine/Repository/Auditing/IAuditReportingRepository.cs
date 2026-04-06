using Affine.Engine.Model.Auditing.AuditUniverse;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace Affine.Engine.Repository.Auditing
{
    public interface IAuditReportingRepository
    {
        Task<PowerBIReconciliationResponse> GetPowerBIReconciliationAsync(int? referenceId);
        Task<AuditFinanceAuditWorkspace> GetFinanceAuditWorkspaceAsync(int referenceId);
        Task<List<AuditFinancialStatementMappingItem>> GenerateTrialBalanceMappingsAsync(GenerateTrialBalanceMappingsRequest request);
        Task<AuditFinancialStatementMappingItem> SaveTrialBalanceMappingAsync(SaveTrialBalanceMappingRequest request);
        Task<AuditFinancialStatementMappingProfile> SaveMappingProfileFromCurrentAsync(SaveAuditMappingProfileRequest request);
        Task<List<AuditDraftFinancialStatement>> GenerateDraftFinancialStatementsAsync(GenerateDraftFinancialStatementsRequest request);
        Task<List<AuditSubstantiveSupportRequest>> GenerateSupportQueueAsync(GenerateAuditSupportQueueRequest request);
        Task<AuditSubstantiveSupportRequest> UpdateSupportRequestAsync(UpdateAuditSupportRequestRequest request);
        Task<AuditFinanceFinalizationRecord> UpsertFinanceFinalizationAsync(UpsertAuditFinanceFinalizationRequest request);
    }
}
