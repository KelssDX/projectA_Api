namespace Affine.Engine.Model.Auditing.AuditUniverse
{
    public class AuditDocumentAccessLogEntry
    {
        public int DocumentId { get; set; }
        public int? ReferenceId { get; set; }
        public string ActionType { get; set; } = "Metadata";
        public int? AccessedByUserId { get; set; }
        public string? AccessedByName { get; set; }
        public string? IpAddress { get; set; }
        public string? ClientContext { get; set; }
        public string? CorrelationId { get; set; }
        public bool Success { get; set; } = true;
        public string? DetailsJson { get; set; }
    }

    public class AuditDocumentAccessLogRecord : AuditDocumentAccessLogEntry
    {
        public long Id { get; set; }
        public string? DocumentTitle { get; set; }
        public string? DocumentCode { get; set; }
        public DateTime? AccessedAt { get; set; }
    }

    public class AuditLoginEventEntry
    {
        public int? UserId { get; set; }
        public string? Username { get; set; }
        public string? DisplayName { get; set; }
        public string EventType { get; set; } = "Login";
        public string Status { get; set; } = "Success";
        public string? IpAddress { get; set; }
        public string? UserAgent { get; set; }
        public string? ClientContext { get; set; }
        public string? FailureReason { get; set; }
        public string? CorrelationId { get; set; }
    }
}
