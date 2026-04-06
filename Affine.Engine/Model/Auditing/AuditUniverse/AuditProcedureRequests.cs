using System;

namespace Affine.Engine.Model.Auditing.AuditUniverse
{
    public class CreateAuditProcedureRequest
    {
        public int? ReferenceId { get; set; }
        public int? AuditUniverseId { get; set; }
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
        public int? ApplicableEngagementTypeId { get; set; }
        public string TemplatePack { get; set; }
        public string TemplateTags { get; set; }
        public int? CreatedByUserId { get; set; }
    }

    public class UpdateAuditProcedureRequest
    {
        public int Id { get; set; }
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
        public int? ApplicableEngagementTypeId { get; set; }
        public string TemplatePack { get; set; }
        public string TemplateTags { get; set; }
        public bool IsActive { get; set; } = true;
    }

    public class CreateProcedureFromTemplateRequest
    {
        public int TemplateId { get; set; }
        public int ReferenceId { get; set; }
        public int? AuditUniverseId { get; set; }
        public DateTime? PlannedDate { get; set; }
        public int? CreatedByUserId { get; set; }
    }
}
