using Affine.Engine.Model.Auditing.AuditUniverse;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace Affine.Engine.Repository.Auditing
{
    public interface IAuditProceduresRepository
    {
        Task<AuditProcedure> GetProcedureAsync(int id);
        Task<List<AuditProcedure>> GetProceduresByReferenceAsync(int referenceId);
        Task<List<AuditProcedure>> GetLibraryProceduresAsync(string? searchText = null, int? engagementTypeId = null);
        Task<AuditProcedure> CreateProcedureAsync(CreateAuditProcedureRequest request);
        Task<AuditProcedure> UpdateProcedureAsync(UpdateAuditProcedureRequest request);
        Task<AuditProcedure> CreateProcedureFromTemplateAsync(CreateProcedureFromTemplateRequest request);
        Task<bool> DeleteProcedureAsync(int id);
        Task<List<ProcedureType>> GetProcedureTypesAsync();
        Task<List<ProcedureStatus>> GetProcedureStatusesAsync();
    }
}
