using System;
using System.Collections.Generic;

namespace Affine.Engine.Model.Auditing.AuditUniverse
{
    /// <summary>
    /// Represents a working paper tied to an audit engagement or stored as a reusable template.
    /// </summary>
    public class AuditWorkingPaper
    {
        public int Id { get; set; }
        public int? ReferenceId { get; set; }
        public int? AuditUniverseId { get; set; }
        public int? ProcedureId { get; set; }
        public string WorkingPaperCode { get; set; }
        public string Title { get; set; }
        public string Objective { get; set; }
        public string Description { get; set; }
        public int? StatusId { get; set; }
        public string PreparedBy { get; set; }
        public int? PreparedByUserId { get; set; }
        public string ReviewerName { get; set; }
        public int? ReviewerUserId { get; set; }
        public string Conclusion { get; set; }
        public string Notes { get; set; }
        public DateTime? PreparedDate { get; set; }
        public DateTime? ReviewedDate { get; set; }
        public bool IsTemplate { get; set; }
        public int? SourceTemplateId { get; set; }
        public int? ApplicableEngagementTypeId { get; set; }
        public string ApplicableEngagementTypeName { get; set; }
        public string TemplatePack { get; set; }
        public string TemplateTags { get; set; }
        public bool IsActive { get; set; } = true;
        public DateTime? CreatedAt { get; set; }
        public DateTime? UpdatedAt { get; set; }

        // Display fields
        public string StatusName { get; set; }
        public string StatusColor { get; set; }
        public string ProcedureTitle { get; set; }
        public string AuditUniverseName { get; set; }

        // Computed
        public int SignOffCount { get; set; }
        public int ReferenceCount { get; set; }

        public List<WorkingPaperSignoff> SignOffHistory { get; set; } = new List<WorkingPaperSignoff>();
        public List<WorkingPaperReferenceLink> CrossReferences { get; set; } = new List<WorkingPaperReferenceLink>();
    }

    public class WorkingPaperStatus
    {
        public int Id { get; set; }
        public string Name { get; set; }
        public string Description { get; set; }
        public string Color { get; set; }
        public bool IsClosed { get; set; }
        public int? SortOrder { get; set; }
        public bool IsActive { get; set; } = true;
    }

    public class WorkingPaperSignoff
    {
        public int Id { get; set; }
        public int WorkingPaperId { get; set; }
        public string ActionType { get; set; }
        public int? SignedByUserId { get; set; }
        public string SignedByName { get; set; }
        public string Comment { get; set; }
        public DateTime SignedAt { get; set; }
    }

    public class WorkingPaperReferenceLink
    {
        public int Id { get; set; }
        public int FromWorkingPaperId { get; set; }
        public int ToWorkingPaperId { get; set; }
        public string ReferenceType { get; set; }
        public string Notes { get; set; }
        public string TargetWorkingPaperCode { get; set; }
        public string TargetWorkingPaperTitle { get; set; }
        public DateTime CreatedAt { get; set; }
    }
}
