using Affine.Engine.Model.Auditing.AuditUniverse;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace Affine.Engine.Repository.Auditing
{
    public interface IAuditPlatformRepository
    {
        Task<List<AuditRetentionPolicy>> GetRetentionPoliciesAsync();
        Task<ArchiveAssessmentResult> ArchiveAssessmentAsync(ArchiveAssessmentRequest request);
        Task<AuditUsageEvent> RecordUsageEventAsync(RecordAuditUsageEventRequest request);
        Task<List<AuditUsageSummary>> GetUsageSummaryAsync(int days = 30);
    }
}
