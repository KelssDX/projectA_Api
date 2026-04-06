using System;
using System.Collections.Generic;

namespace Affine.Engine.Model.Auditing.AuditUniverse
{
    public class AuditTrailEvent
    {
        public long Id { get; set; }
        public int? ReferenceId { get; set; }
        public string EntityType { get; set; }
        public string EntityId { get; set; }
        public string Category { get; set; }
        public string Action { get; set; }
        public string Summary { get; set; }
        public int? PerformedByUserId { get; set; }
        public string PerformedByName { get; set; }
        public string Icon { get; set; }
        public string Color { get; set; }
        public string WorkflowInstanceId { get; set; }
        public string CorrelationId { get; set; }
        public string Source { get; set; }
        public string DetailsJson { get; set; }
        public DateTime? EventTime { get; set; }
        public List<AuditTrailChange> Changes { get; set; } = new List<AuditTrailChange>();
    }

    public class AuditTrailChange
    {
        public long Id { get; set; }
        public long AuditTrailEventId { get; set; }
        public string FieldName { get; set; }
        public string OldValue { get; set; }
        public string NewValue { get; set; }
    }

    public class AuditTrailCategoryCount
    {
        public string Category { get; set; }
        public int EventCount { get; set; }
    }

    public class AuditTrailDashboard
    {
        public int? ReferenceId { get; set; }
        public int TotalEvents { get; set; }
        public int ChangeRecords { get; set; }
        public List<AuditTrailCategoryCount> Categories { get; set; } = new List<AuditTrailCategoryCount>();
        public List<AuditTrailEvent> RecentEvents { get; set; } = new List<AuditTrailEvent>();
    }

    public class CreateAuditTrailEventRequest
    {
        public int? ReferenceId { get; set; }
        public string EntityType { get; set; } = string.Empty;
        public string EntityId { get; set; } = string.Empty;
        public string Category { get; set; } = string.Empty;
        public string Action { get; set; } = string.Empty;
        public string Summary { get; set; } = string.Empty;
        public int? PerformedByUserId { get; set; }
        public string PerformedByName { get; set; } = string.Empty;
        public string Icon { get; set; } = string.Empty;
        public string Color { get; set; } = string.Empty;
        public string WorkflowInstanceId { get; set; } = string.Empty;
        public string CorrelationId { get; set; } = string.Empty;
        public string Source { get; set; } = string.Empty;
        public string DetailsJson { get; set; } = string.Empty;
        public List<CreateAuditTrailChangeRequest> Changes { get; set; } = new List<CreateAuditTrailChangeRequest>();
    }

    public class CreateAuditTrailChangeRequest
    {
        public string FieldName { get; set; } = string.Empty;
        public string OldValue { get; set; } = string.Empty;
        public string NewValue { get; set; } = string.Empty;
    }
}
