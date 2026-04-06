using System;

namespace Affine.Engine.Model.Auditing.AuditUniverse
{
    /// <summary>
    /// Represents an audit procedure that can be executed against an engagement
    /// or stored as a reusable library template.
    /// </summary>
    public class AuditProcedure
    {
        public int Id { get; set; }
        public int? ReferenceId { get; set; }
        public int? AuditUniverseId { get; set; }
        public string ProcedureCode { get; set; }
        public string ProcedureTitle { get; set; }
        public string Objective { get; set; }
        public string ProcedureDescription { get; set; }
        public int? ProcedureTypeId { get; set; }
        public int? StatusId { get; set; }
        public int? SampleSize { get; set; }
        public string ExpectedEvidence { get; set; }
        public string WorkingPaperRef { get; set; }
        public string Owner { get; set; }
        public int? PerformerUserId { get; set; }
        public int? ReviewerUserId { get; set; }
        public DateTime? PlannedDate { get; set; }
        public DateTime? PerformedDate { get; set; }
        public DateTime? ReviewedDate { get; set; }
        public string Conclusion { get; set; }
        public string Notes { get; set; }
        public bool IsTemplate { get; set; }
        public int? SourceTemplateId { get; set; }
        public int? ApplicableEngagementTypeId { get; set; }
        public string ApplicableEngagementTypeName { get; set; }
        public string TemplatePack { get; set; }
        public string TemplateTags { get; set; }
        public int? CreatedByUserId { get; set; }
        public bool IsActive { get; set; } = true;
        public DateTime? CreatedAt { get; set; }
        public DateTime? UpdatedAt { get; set; }

        // Display fields
        public string ProcedureTypeName { get; set; }
        public string ProcedureTypeColor { get; set; }
        public string StatusName { get; set; }
        public string StatusColor { get; set; }
        public string AuditUniverseName { get; set; }

        // Computed indicators
        public bool IsOverdue { get; set; }
        public int? DaysPastPlanned { get; set; }
    }

    public class ProcedureType
    {
        public int Id { get; set; }
        public string Name { get; set; }
        public string Description { get; set; }
        public string Color { get; set; }
        public int? SortOrder { get; set; }
        public bool IsActive { get; set; } = true;
    }

    public class ProcedureStatus
    {
        public int Id { get; set; }
        public string Name { get; set; }
        public string Description { get; set; }
        public string Color { get; set; }
        public bool IsClosed { get; set; }
        public int? SortOrder { get; set; }
        public bool IsActive { get; set; } = true;
    }
}
