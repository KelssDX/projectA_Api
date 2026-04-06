using System;
using System.Collections.Generic;

namespace Affine.Engine.Model.Auditing.AuditUniverse
{
    public class AuditWorkflowInstance
    {
        public int Id { get; set; }
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
        public DateTime? StartedAt { get; set; }
        public DateTime? LastSyncedAt { get; set; }
        public DateTime? CompletedAt { get; set; }
        public bool IsActive { get; set; }
        public string MetadataJson { get; set; }
    }

    public class AuditWorkflowTask
    {
        public int Id { get; set; }
        public string WorkflowInstanceId { get; set; }
        public string ExternalTaskId { get; set; }
        public string ExternalTaskSource { get; set; }
        public int? ReferenceId { get; set; }
        public string EntityType { get; set; }
        public int? EntityId { get; set; }
        public string WorkflowDisplayName { get; set; }
        public string TaskTitle { get; set; }
        public string TaskDescription { get; set; }
        public int? AssigneeUserId { get; set; }
        public string AssigneeName { get; set; }
        public string Status { get; set; }
        public string Priority { get; set; }
        public DateTime? DueDate { get; set; }
        public string ActionUrl { get; set; }
        public DateTime? CreatedAt { get; set; }
        public DateTime? CompletedAt { get; set; }
        public int? CompletedByUserId { get; set; }
        public string CompletionNotes { get; set; }
    }

    public class AuditNotification
    {
        public int Id { get; set; }
        public int? ReferenceId { get; set; }
        public string EntityType { get; set; }
        public int? EntityId { get; set; }
        public string WorkflowInstanceId { get; set; }
        public string WorkflowDisplayName { get; set; }
        public string NotificationType { get; set; }
        public string Severity { get; set; }
        public string Title { get; set; }
        public string Message { get; set; }
        public int? RecipientUserId { get; set; }
        public string RecipientName { get; set; }
        public bool IsRead { get; set; }
        public DateTime? ReadAt { get; set; }
        public string ActionUrl { get; set; }
        public DateTime? CreatedAt { get; set; }
    }

    public class AuditWorkflowEvent
    {
        public int Id { get; set; }
        public string WorkflowInstanceId { get; set; }
        public int? ReferenceId { get; set; }
        public string EntityType { get; set; }
        public int? EntityId { get; set; }
        public string WorkflowDisplayName { get; set; }
        public string EventType { get; set; }
        public string Title { get; set; }
        public string Description { get; set; }
        public int? ActorUserId { get; set; }
        public string ActorName { get; set; }
        public DateTime? EventTime { get; set; }
        public string MetadataJson { get; set; }
    }

    public class AuditWorkflowInbox
    {
        public List<AuditWorkflowInstance> Workflows { get; set; } = new List<AuditWorkflowInstance>();
        public List<AuditWorkflowTask> Tasks { get; set; } = new List<AuditWorkflowTask>();
        public List<AuditNotification> Notifications { get; set; } = new List<AuditNotification>();
        public List<AuditWorkflowEvent> Events { get; set; } = new List<AuditWorkflowEvent>();
    }

    public class WorkflowLaunchResult
    {
        public bool Success { get; set; }
        public string WorkflowInstanceId { get; set; }
        public string Status { get; set; }
        public string Message { get; set; }
        public AuditWorkflowInstance Workflow { get; set; }
    }

    public class AuditWorkflowSyncResult
    {
        public bool Success { get; set; }
        public string WorkflowInstanceId { get; set; }
        public string Status { get; set; }
        public int TasksCompleted { get; set; }
        public int NotificationsCreated { get; set; }
        public AuditWorkflowInstance Workflow { get; set; }
        public AuditWorkflowEvent Event { get; set; }
        public string Message { get; set; }
    }

    public class AuditWorkflowReminderSweepResult
    {
        public bool Success { get; set; }
        public int DueSoonRemindersCreated { get; set; }
        public int ReviewReadyNotificationsCreated { get; set; }
        public int OverdueRemindersCreated { get; set; }
        public int EscalationsCreated { get; set; }
        public int WorkflowEventsCreated { get; set; }
        public int TasksEvaluated { get; set; }
        public string Message { get; set; }
    }
}
