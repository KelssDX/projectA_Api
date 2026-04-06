using Affine.Engine.Model.Auditing.AuditUniverse;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace Affine.Engine.Repository.Auditing
{
    public interface IAuditReviewsRepository
    {
        Task<AuditReviewWorkspace> GetWorkspaceAsync(int? userId);
        Task<List<AuditReview>> GetReviewsByReferenceAsync(int referenceId);
        Task<List<AuditReviewNote>> GetReviewNotesAsync(int reviewId);
        Task<List<AuditSignoff>> GetSignoffsByReferenceAsync(int referenceId, int limit = 100);

        Task<AuditTask> CreateTaskAsync(CreateAuditTaskRequest request);
        Task<int> CompleteOpenTasksByWorkflowInstanceAsync(CompleteAuditTaskRequest request);

        Task<AuditReview> CreateReviewAsync(CreateAuditReviewRequest request);
        Task<AuditReview?> GetReviewByWorkflowInstanceAsync(string workflowInstanceId);
        Task<AuditReview?> CompleteReviewByWorkflowInstanceAsync(CompleteAuditReviewRequest request);

        Task<AuditReviewNote> AddReviewNoteAsync(CreateAuditReviewNoteRequest request);
        Task<AuditSignoff> AddSignoffAsync(CreateAuditSignoffRequest request);
    }
}
