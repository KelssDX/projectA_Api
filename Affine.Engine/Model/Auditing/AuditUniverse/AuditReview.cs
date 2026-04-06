using System;
using System.Collections.Generic;

namespace Affine.Engine.Model.Auditing.AuditUniverse
{
    public class AuditReview
    {
        public int Id { get; set; }
        public int? ReferenceId { get; set; }
        public string EntityType { get; set; }
        public int EntityId { get; set; }
        public string ReviewType { get; set; }
        public string Status { get; set; }
        public int? TaskId { get; set; }
        public string WorkflowInstanceId { get; set; }
        public int? AssignedReviewerUserId { get; set; }
        public string AssignedReviewerName { get; set; }
        public int? RequestedByUserId { get; set; }
        public string RequestedByName { get; set; }
        public DateTime? RequestedAt { get; set; }
        public DateTime? DueDate { get; set; }
        public DateTime? CompletedAt { get; set; }
        public int? CompletedByUserId { get; set; }
        public string Summary { get; set; }
        public DateTime? CreatedAt { get; set; }
        public DateTime? UpdatedAt { get; set; }

        public string TaskTitle { get; set; }
        public string TaskDescription { get; set; }
        public string TaskStatus { get; set; }
        public string TaskPriority { get; set; }
        public string WorkflowDisplayName { get; set; }

        public int OpenNoteCount { get; set; }
        public int TotalNoteCount { get; set; }
        public int SignoffCount { get; set; }
    }

    public class AuditReviewNote
    {
        public int Id { get; set; }
        public int ReviewId { get; set; }
        public int? WorkingPaperSectionId { get; set; }
        public string NoteType { get; set; }
        public string Severity { get; set; }
        public string Status { get; set; }
        public string NoteText { get; set; }
        public string ResponseText { get; set; }
        public int? RaisedByUserId { get; set; }
        public string RaisedByName { get; set; }
        public DateTime? RaisedAt { get; set; }
        public int? ClearedByUserId { get; set; }
        public string ClearedByName { get; set; }
        public DateTime? ClearedAt { get; set; }

        public int? ReferenceId { get; set; }
        public string EntityType { get; set; }
        public int? EntityId { get; set; }
        public string ReviewType { get; set; }
        public string AssignedReviewerName { get; set; }
    }

    public class AuditSignoff
    {
        public int Id { get; set; }
        public int? ReferenceId { get; set; }
        public string EntityType { get; set; }
        public int EntityId { get; set; }
        public int? ReviewId { get; set; }
        public string WorkflowInstanceId { get; set; }
        public string SignoffType { get; set; }
        public string SignoffLevel { get; set; }
        public string Status { get; set; }
        public int? SignedByUserId { get; set; }
        public string SignedByName { get; set; }
        public DateTime? SignedAt { get; set; }
        public string Comment { get; set; }
    }

    public class AuditTask
    {
        public int Id { get; set; }
        public int? ReferenceId { get; set; }
        public string EntityType { get; set; }
        public int? EntityId { get; set; }
        public string WorkflowInstanceId { get; set; }
        public string TaskType { get; set; }
        public string Title { get; set; }
        public string Description { get; set; }
        public int? AssignedToUserId { get; set; }
        public string AssignedToName { get; set; }
        public int? AssignedByUserId { get; set; }
        public string AssignedByName { get; set; }
        public string Status { get; set; }
        public string Priority { get; set; }
        public DateTime? DueDate { get; set; }
        public DateTime? CompletedAt { get; set; }
        public int? CompletedByUserId { get; set; }
        public string CompletionNotes { get; set; }
        public string Source { get; set; }
        public DateTime? CreatedAt { get; set; }
        public DateTime? UpdatedAt { get; set; }
    }

    public class AuditReviewWorkspace
    {
        public List<AuditReview> Reviews { get; set; } = new List<AuditReview>();
        public List<AuditReviewNote> ReviewNotes { get; set; } = new List<AuditReviewNote>();
        public List<AuditSignoff> Signoffs { get; set; } = new List<AuditSignoff>();
        public List<AuditTask> Tasks { get; set; } = new List<AuditTask>();
    }
}
