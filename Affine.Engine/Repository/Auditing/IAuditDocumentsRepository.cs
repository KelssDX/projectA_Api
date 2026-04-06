using Affine.Engine.Model.Auditing.AuditUniverse;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace Affine.Engine.Repository.Auditing
{
    public interface IAuditDocumentsRepository
    {
        Task<AuditDocument> GetDocumentAsync(int id);
        Task<List<AuditDocument>> GetDocumentsByReferenceAsync(int referenceId);
        Task<List<AuditDocumentCategory>> GetDocumentCategoriesAsync();
        Task<List<AuditDocumentVisibilityOption>> GetDocumentVisibilityOptionsAsync();
        Task<AuditDocument> CreateDocumentAsync(CreateAuditDocumentRequest request);
        Task<AuditDocument> UpdateDocumentSecurityAsync(int id, UpdateAuditDocumentSecurityRequest request);
        Task<bool> DeleteDocumentAsync(int id);
        Task<List<AuditEvidenceRequest>> GetEvidenceRequestsByReferenceAsync(int referenceId);
        Task<List<EvidenceRequestStatus>> GetEvidenceRequestStatusesAsync();
        Task<AuditEvidenceRequest> CreateEvidenceRequestAsync(CreateAuditEvidenceRequestRequest request);
        Task<bool> FulfillEvidenceRequestItemAsync(int requestItemId, int documentId);
        Task<AuditEvidenceRequestItem> ReviewEvidenceRequestItemAsync(ReviewEvidenceRequestItemRequest request);
        Task<AuditEvidenceRequestAssignmentContext> GetEvidenceRequestAssignmentContextByItemAsync(int requestItemId);
        Task<AuditDocument> ReviewDocumentSecurityAsync(int id, ReviewAuditDocumentSecurityRequest request);
    }
}
