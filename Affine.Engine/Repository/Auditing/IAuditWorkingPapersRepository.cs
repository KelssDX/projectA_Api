using Affine.Engine.Model.Auditing.AuditUniverse;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace Affine.Engine.Repository.Auditing
{
    public interface IAuditWorkingPapersRepository
    {
        Task<AuditWorkingPaper> GetWorkingPaperAsync(int id);
        Task<List<AuditWorkingPaper>> GetWorkingPapersByReferenceAsync(int referenceId);
        Task<List<AuditWorkingPaper>> GetWorkingPaperTemplatesAsync(string? searchText = null, int? engagementTypeId = null);
        Task<AuditWorkingPaper> CreateWorkingPaperAsync(CreateAuditWorkingPaperRequest request);
        Task<AuditWorkingPaper> UpdateWorkingPaperAsync(UpdateAuditWorkingPaperRequest request);
        Task<AuditWorkingPaper> CreateWorkingPaperFromTemplateAsync(CreateWorkingPaperFromTemplateRequest request);
        Task<bool> DeleteWorkingPaperAsync(int id);
        Task<List<WorkingPaperStatus>> GetWorkingPaperStatusesAsync();
        Task<List<WorkingPaperSignoff>> GetSignoffsAsync(int workingPaperId);
        Task<WorkingPaperSignoff> AddSignoffAsync(AddWorkingPaperSignoffRequest request);
        Task<List<WorkingPaperReferenceLink>> GetReferencesAsync(int workingPaperId);
        Task<WorkingPaperReferenceLink> AddReferenceAsync(AddWorkingPaperReferenceRequest request);
    }
}
