using Affine.Engine.Model.Auditing.AuditUniverse;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace Affine.Engine.Repository.Auditing
{
    public interface IAuditExecutionRepository
    {
        Task<AuditEngagementPlan> GetPlanningByReferenceAsync(int referenceId);
        Task<AuditEngagementPlan> UpsertPlanningAsync(UpsertAuditEngagementPlanRequest request);
        Task<List<EngagementTypeOption>> GetEngagementTypesAsync();
        Task<List<PlanningStatusOption>> GetPlanningStatusesAsync();

        Task<List<AuditScopeItem>> GetScopeItemsByReferenceAsync(int referenceId);
        Task<AuditScopeItem> CreateScopeItemAsync(CreateAuditScopeItemRequest request);
        Task<AuditScopeItem> UpdateScopeItemAsync(UpdateAuditScopeItemRequest request);
        Task<bool> DeleteScopeItemAsync(int id);

        Task<List<RiskControlMatrixEntry>> GetRiskControlMatrixByReferenceAsync(int referenceId);
        Task<RiskControlMatrixEntry> CreateRiskControlMatrixEntryAsync(CreateRiskControlMatrixEntryRequest request);
        Task<RiskControlMatrixEntry> UpdateRiskControlMatrixEntryAsync(UpdateRiskControlMatrixEntryRequest request);
        Task<bool> DeleteRiskControlMatrixEntryAsync(int id);
        Task<List<ControlClassificationOption>> GetControlClassificationsAsync();
        Task<List<ControlTypeOption>> GetControlTypesAsync();
        Task<List<ControlFrequencyOption>> GetControlFrequenciesAsync();

        Task<List<AuditWalkthrough>> GetWalkthroughsByReferenceAsync(int referenceId);
        Task<AuditWalkthrough> CreateWalkthroughAsync(CreateAuditWalkthroughRequest request);
        Task<AuditWalkthrough> UpdateWalkthroughAsync(UpdateAuditWalkthroughRequest request);
        Task<bool> DeleteWalkthroughAsync(int id);
        Task<AuditWalkthroughException> AddWalkthroughExceptionAsync(AddWalkthroughExceptionRequest request);

        Task<List<AuditManagementAction>> GetManagementActionsByReferenceAsync(int referenceId);
        Task<AuditManagementAction> CreateManagementActionAsync(CreateAuditManagementActionRequest request);
        Task<AuditManagementAction> UpdateManagementActionAsync(UpdateAuditManagementActionRequest request);
        Task<bool> DeleteManagementActionAsync(int id);
    }
}
