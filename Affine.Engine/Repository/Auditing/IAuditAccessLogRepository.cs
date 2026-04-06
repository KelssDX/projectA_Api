using Affine.Engine.Model.Auditing.AuditUniverse;

namespace Affine.Engine.Repository.Auditing
{
    public interface IAuditAccessLogRepository
    {
        Task LogDocumentAccessAsync(AuditDocumentAccessLogEntry entry);
        Task<IReadOnlyList<AuditDocumentAccessLogRecord>> GetDocumentAccessLogsByReferenceAsync(int referenceId, int? documentId = null, int limit = 100);
        Task LogLoginEventAsync(AuditLoginEventEntry entry);
    }
}
