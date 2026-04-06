using System;

namespace Affine.Engine.Model.Auditing.AuditUniverse
{
    public class CreateAuditWorkingPaperRequest
    {
        public int? ReferenceId { get; set; }
        public int? AuditUniverseId { get; set; }
        public int? ProcedureId { get; set; }
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
        public int? ApplicableEngagementTypeId { get; set; }
        public string TemplatePack { get; set; }
        public string TemplateTags { get; set; }
    }

    public class UpdateAuditWorkingPaperRequest
    {
        public int Id { get; set; }
        public int? ProcedureId { get; set; }
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
        public int? ApplicableEngagementTypeId { get; set; }
        public string TemplatePack { get; set; }
        public string TemplateTags { get; set; }
        public bool IsActive { get; set; } = true;
    }

    public class CreateWorkingPaperFromTemplateRequest
    {
        public int TemplateId { get; set; }
        public int ReferenceId { get; set; }
        public int? AuditUniverseId { get; set; }
        public int? ProcedureId { get; set; }
        public string PreparedBy { get; set; }
        public int? PreparedByUserId { get; set; }
    }

    public class AddWorkingPaperSignoffRequest
    {
        public int WorkingPaperId { get; set; }
        public string ActionType { get; set; }
        public int? SignedByUserId { get; set; }
        public string SignedByName { get; set; }
        public string Comment { get; set; }
    }

    public class AddWorkingPaperReferenceRequest
    {
        public int FromWorkingPaperId { get; set; }
        public int ToWorkingPaperId { get; set; }
        public string ReferenceType { get; set; }
        public string Notes { get; set; }
    }
}
