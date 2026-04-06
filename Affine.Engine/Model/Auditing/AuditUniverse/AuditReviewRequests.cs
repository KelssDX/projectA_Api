using System;

namespace Affine.Engine.Model.Auditing.AuditUniverse
{
    public class CreateAuditTaskRequest
    {
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
        public string Status { get; set; } = "Open";
        public string Priority { get; set; } = "Medium";
        public DateTime? DueDate { get; set; }
        public string Source { get; set; } = "Manual";
    }

    public class CompleteAuditTaskRequest
    {
        public string WorkflowInstanceId { get; set; }
        public int? CompletedByUserId { get; set; }
        public string CompletionNotes { get; set; }
    }

    public class CreateAuditReviewRequest
    {
        public int? ReferenceId { get; set; }
        public string EntityType { get; set; }
        public int EntityId { get; set; }
        public string ReviewType { get; set; }
        public string Status { get; set; } = "Pending";
        public int? TaskId { get; set; }
        public string WorkflowInstanceId { get; set; }
        public int? AssignedReviewerUserId { get; set; }
        public string AssignedReviewerName { get; set; }
        public int? RequestedByUserId { get; set; }
        public string RequestedByName { get; set; }
        public DateTime? DueDate { get; set; }
        public string Summary { get; set; }
    }

    public class CompleteAuditReviewRequest
    {
        public string WorkflowInstanceId { get; set; }
        public string Status { get; set; } = "Completed";
        public int? CompletedByUserId { get; set; }
        public string Summary { get; set; }
    }

    public class CreateAuditReviewNoteRequest
    {
        public int ReviewId { get; set; }
        public int? WorkingPaperSectionId { get; set; }
        public string NoteType { get; set; } = "Review Note";
        public string Severity { get; set; } = "Medium";
        public string Status { get; set; } = "Open";
        public string NoteText { get; set; }
        public string ResponseText { get; set; }
        public int? RaisedByUserId { get; set; }
        public string RaisedByName { get; set; }
    }

    public class CreateAuditSignoffRequest
    {
        public int? ReferenceId { get; set; }
        public string EntityType { get; set; }
        public int EntityId { get; set; }
        public int? ReviewId { get; set; }
        public string WorkflowInstanceId { get; set; }
        public string SignoffType { get; set; }
        public string SignoffLevel { get; set; }
        public string Status { get; set; } = "Signed";
        public int? SignedByUserId { get; set; }
        public string SignedByName { get; set; }
        public string Comment { get; set; }
    }
}
