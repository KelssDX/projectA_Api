using System;
using System.Collections.Generic;

namespace Affine.Engine.Model.Auditing.AuditUniverse
{
    public class StartAuditWorkflowRequest
    {
        public int? ReferenceId { get; set; }
        public string EntityType { get; set; }
        public int? EntityId { get; set; }
        public string WorkflowDefinitionId { get; set; }
        public string WorkflowDisplayName { get; set; }
        public string ActivityId { get; set; }
        public Dictionary<string, object> Input { get; set; } = new Dictionary<string, object>();
        public int? InitiatedByUserId { get; set; }
        public string InitiatedByName { get; set; }
        public int? AssigneeUserId { get; set; }
        public string AssigneeName { get; set; }
        public string TaskTitle { get; set; }
        public string TaskDescription { get; set; }
        public string Priority { get; set; }
        public DateTime? DueDate { get; set; }
        public string NotificationType { get; set; }
        public string NotificationTitle { get; set; }
        public string NotificationMessage { get; set; }
        public string Severity { get; set; }
        public string ActionUrl { get; set; }
    }

    public class CreateAuditWorkflowInstanceRequest
    {
        public int? ReferenceId { get; set; }
        public string EntityType { get; set; }
        public int? EntityId { get; set; }
        public string WorkflowDefinitionId { get; set; }
        public string WorkflowDisplayName { get; set; }
        public string WorkflowInstanceId { get; set; }
        public string Status { get; set; }
        public string CurrentActivityId { get; set; }
        public string CurrentActivityName { get; set; }
        public int? StartedByUserId { get; set; }
        public string StartedByName { get; set; }
        public bool IsActive { get; set; } = true;
        public string MetadataJson { get; set; }
    }

    public class UpdateAuditWorkflowInstanceStatusRequest
    {
        public string WorkflowInstanceId { get; set; }
        public string Status { get; set; }
        public string CurrentActivityId { get; set; }
        public string CurrentActivityName { get; set; }
        public bool IsActive { get; set; } = true;
        public DateTime? CompletedAt { get; set; }
    }

    public class CreateAuditWorkflowTaskRequest
    {
        public string WorkflowInstanceId { get; set; }
        public string ExternalTaskId { get; set; }
        public string ExternalTaskSource { get; set; }
        public int? ReferenceId { get; set; }
        public string EntityType { get; set; }
        public int? EntityId { get; set; }
        public string TaskTitle { get; set; }
        public string TaskDescription { get; set; }
        public int? AssigneeUserId { get; set; }
        public string AssigneeName { get; set; }
        public string Status { get; set; } = "Pending";
        public string Priority { get; set; } = "Medium";
        public DateTime? DueDate { get; set; }
        public string ActionUrl { get; set; }
    }

    public class CompleteAuditWorkflowTaskRequest
    {
        public int TaskId { get; set; }
        public int? CompletedByUserId { get; set; }
        public string CompletionNotes { get; set; }
    }

    public class CreateAuditNotificationRequest
    {
        public int? ReferenceId { get; set; }
        public string EntityType { get; set; }
        public int? EntityId { get; set; }
        public string WorkflowInstanceId { get; set; }
        public string NotificationType { get; set; }
        public string Severity { get; set; } = "Info";
        public string Title { get; set; }
        public string Message { get; set; }
        public int? RecipientUserId { get; set; }
        public string RecipientName { get; set; }
        public string ActionUrl { get; set; }
    }

    public class CreateAuditWorkflowEventRequest
    {
        public string WorkflowInstanceId { get; set; }
        public int? ReferenceId { get; set; }
        public string EntityType { get; set; }
        public int? EntityId { get; set; }
        public string EventType { get; set; }
        public string Title { get; set; }
        public string Description { get; set; }
        public int? ActorUserId { get; set; }
        public string ActorName { get; set; }
        public string MetadataJson { get; set; }
    }

    public class MarkAuditNotificationReadRequest
    {
        public int NotificationId { get; set; }
        public int? ReadByUserId { get; set; }
    }

    public class SyncAuditWorkflowStateRequest
    {
        public string WorkflowInstanceId { get; set; }
        public string Status { get; set; }
        public string CurrentActivityId { get; set; }
        public string CurrentActivityName { get; set; }
        public bool? IsActive { get; set; }
        public DateTime? CompletedAt { get; set; }
        public bool? AutoCompleteOpenTasks { get; set; }
        public int? ActorUserId { get; set; }
        public string ActorName { get; set; }
        public string EventType { get; set; }
        public string EventTitle { get; set; }
        public string EventDescription { get; set; }
        public string NotificationType { get; set; }
        public string NotificationTitle { get; set; }
        public string NotificationMessage { get; set; }
        public string NotificationSeverity { get; set; }
        public int? NotificationRecipientUserId { get; set; }
        public string NotificationRecipientName { get; set; }
        public string ActionUrl { get; set; }
    }

    public class StartPlanningApprovalWorkflowRequest
    {
        public int ReferenceId { get; set; }
        public string EngagementTitle { get; set; }
        public int? RequestedByUserId { get; set; }
        public string RequestedByName { get; set; }
        public int? ApproverUserId { get; set; }
        public string ApproverName { get; set; }
        public DateTime? DueDate { get; set; }
        public string Notes { get; set; }
    }

    public class StartAnnualAuditPlanApprovalWorkflowRequest
    {
        public int ReferenceId { get; set; }
        public string AnnualPlanName { get; set; }
        public int? PlanYear { get; set; }
        public int? RequestedByUserId { get; set; }
        public string RequestedByName { get; set; }
        public int? ApproverUserId { get; set; }
        public string ApproverName { get; set; }
        public DateTime? DueDate { get; set; }
        public string Notes { get; set; }
    }

    public class StartScopeApprovalWorkflowRequest
    {
        public int ReferenceId { get; set; }
        public string ScopeSummary { get; set; }
        public int? RequestedByUserId { get; set; }
        public string RequestedByName { get; set; }
        public int? ApproverUserId { get; set; }
        public string ApproverName { get; set; }
        public DateTime? DueDate { get; set; }
        public string Notes { get; set; }
    }

    public class StartWalkthroughWorkflowRequest
    {
        public int ReferenceId { get; set; }
        public int WalkthroughId { get; set; }
        public string ProcessName { get; set; }
        public int? RequestedByUserId { get; set; }
        public string RequestedByName { get; set; }
        public int? ReviewerUserId { get; set; }
        public string ReviewerName { get; set; }
        public DateTime? DueDate { get; set; }
        public string Notes { get; set; }
    }

    public class StartWorkingPaperReviewWorkflowRequest
    {
        public int ReferenceId { get; set; }
        public int WorkingPaperId { get; set; }
        public string WorkingPaperCode { get; set; }
        public string WorkingPaperTitle { get; set; }
        public int? RequestedByUserId { get; set; }
        public string RequestedByName { get; set; }
        public int? ReviewerUserId { get; set; }
        public string ReviewerName { get; set; }
        public DateTime? DueDate { get; set; }
        public string Notes { get; set; }
    }

    public class StartFindingReviewWorkflowRequest
    {
        public int ReferenceId { get; set; }
        public int? FindingId { get; set; }
        public string FindingNumber { get; set; }
        public string FindingTitle { get; set; }
        public int? RequestedByUserId { get; set; }
        public string RequestedByName { get; set; }
        public int? ReviewerUserId { get; set; }
        public string ReviewerName { get; set; }
        public DateTime? DueDate { get; set; }
        public string Notes { get; set; }
    }

    public class StartManagementResponseWorkflowRequest
    {
        public int ReferenceId { get; set; }
        public int RecommendationId { get; set; }
        public string RecommendationNumber { get; set; }
        public string RecommendationTitle { get; set; }
        public int? RequestedByUserId { get; set; }
        public string RequestedByName { get; set; }
        public int? ResponsibleUserId { get; set; }
        public string ResponsibleName { get; set; }
        public DateTime? DueDate { get; set; }
        public string Notes { get; set; }
    }

    public class StartRemediationFollowUpWorkflowRequest
    {
        public int ReferenceId { get; set; }
        public int RecommendationId { get; set; }
        public string RecommendationNumber { get; set; }
        public string RecommendationTitle { get; set; }
        public int? RequestedByUserId { get; set; }
        public string RequestedByName { get; set; }
        public int? ReviewerUserId { get; set; }
        public string ReviewerName { get; set; }
        public DateTime? DueDate { get; set; }
        public string Notes { get; set; }
    }

    public class StartFinalReportSignOffWorkflowRequest
    {
        public int ReferenceId { get; set; }
        public string ReportTitle { get; set; }
        public int? RequestedByUserId { get; set; }
        public string RequestedByName { get; set; }
        public int? ApproverUserId { get; set; }
        public string ApproverName { get; set; }
        public DateTime? DueDate { get; set; }
        public string Notes { get; set; }
    }
}
