using Affine.Engine.Model.Auditing.AuditUniverse;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace Affine.Engine.Repository.Auditing
{
    public interface IAuditTrailRepository
    {
        Task<AuditTrailEvent> CreateEventAsync(CreateAuditTrailEventRequest request);
        Task<List<AuditTrailEvent>> GetEventsByReferenceAsync(int referenceId, int limit = 100);
        Task<AuditTrailDashboard> GetDashboardByReferenceAsync(int referenceId, int limit = 50);
    }
}
