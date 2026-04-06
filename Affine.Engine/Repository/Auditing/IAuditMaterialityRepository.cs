using Affine.Engine.Model.Auditing.AuditUniverse;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace Affine.Engine.Repository.Auditing
{
    public interface IAuditMaterialityRepository
    {
        Task<AuditMaterialityWorkspace> GetWorkspaceAsync(int referenceId);
        Task<AuditMaterialityApplicationSummary> GetApplicationSummaryAsync(int referenceId);
        Task<List<AuditMaterialityCandidate>> GenerateCandidatesAsync(GenerateAuditMaterialityCandidatesRequest request);
        Task<List<AuditMaterialityCalculation>> GetCalculationsByReferenceAsync(int referenceId);
        Task<AuditMaterialityCalculation> CreateCalculationAsync(CreateAuditMaterialityCalculationRequest request);
        Task<AuditMaterialityCalculation> SetActiveCalculationAsync(SetActiveAuditMaterialityRequest request);
        Task<AuditMaterialityScopeLink> CreateScopeLinkAsync(UpsertAuditMaterialityScopeLinkRequest request);
        Task<AuditMaterialityScopeLink> UpdateScopeLinkAsync(UpsertAuditMaterialityScopeLinkRequest request);
        Task<bool> DeleteScopeLinkAsync(long id);
        Task<AuditMisstatement> CreateMisstatementAsync(UpsertAuditMisstatementRequest request);
        Task<AuditMisstatement> UpdateMisstatementAsync(UpsertAuditMisstatementRequest request);
        Task<bool> DeleteMisstatementAsync(long id);
    }
}
