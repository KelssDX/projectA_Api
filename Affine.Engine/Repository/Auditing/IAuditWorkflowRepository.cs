using Affine.Engine.Model.Auditing.AuditUniverse;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace Affine.Engine.Repository.Auditing
{
    public interface IAuditWorkflowRepository
    {
        Task<AuditWorkflowInstance> CreateWorkflowInstanceAsync(CreateAuditWorkflowInstanceRequest request);
        Task<AuditWorkflowInstance> GetWorkflowInstanceAsync(string workflowInstanceId);
        Task<AuditWorkflowInstance> UpdateWorkflowInstanceStatusAsync(UpdateAuditWorkflowInstanceStatusRequest request);
        Task<List<AuditWorkflowInstance>> GetWorkflowInstancesByReferenceAsync(int referenceId);
        Task<List<AuditWorkflowInstance>> GetWorkflowInstancesAsync(bool activeOnly = false);

        Task<AuditWorkflowTask> CreateWorkflowTaskAsync(CreateAuditWorkflowTaskRequest request);
        Task<AuditWorkflowTask> CompleteWorkflowTaskAsync(CompleteAuditWorkflowTaskRequest request);
        Task<int> CompleteOpenTasksForWorkflowInstanceAsync(string workflowInstanceId, int? completedByUserId, string completionNotes);
        Task<List<AuditWorkflowTask>> GetWorkflowTasksByUserAsync(int? userId, bool pendingOnly = false);
        Task<string> GetLatestExternalTaskIdAsync(string workflowInstanceId, string externalTaskSource = null);

        Task<AuditNotification> CreateNotificationAsync(CreateAuditNotificationRequest request);
        Task<bool> NotificationExistsAsync(string notificationType, string title, int? recipientUserId, string workflowInstanceId);
        Task<List<AuditNotification>> GetNotificationsByUserAsync(int? userId, bool unreadOnly = false);
        Task<bool> MarkNotificationReadAsync(MarkAuditNotificationReadRequest request);

        Task<AuditWorkflowEvent> CreateWorkflowEventAsync(CreateAuditWorkflowEventRequest request);
        Task<List<AuditWorkflowEvent>> GetWorkflowEventsByReferenceAsync(int referenceId, int limit = 100);

        Task<AuditWorkflowInbox> GetInboxAsync(int? userId);
    }
}
