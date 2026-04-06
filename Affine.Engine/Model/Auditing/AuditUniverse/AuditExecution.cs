using System;
using System.Collections.Generic;

namespace Affine.Engine.Model.Auditing.AuditUniverse
{
    public class AuditEngagementPlan
    {
        public int Id { get; set; }
        public int ReferenceId { get; set; }
        public string EngagementTitle { get; set; }
        public int? EngagementTypeId { get; set; }
        public string EngagementTypeName { get; set; }
        public int? PlanYear { get; set; }
        public string AnnualPlanName { get; set; }
        public string BusinessUnit { get; set; }
        public string ProcessArea { get; set; }
        public string SubProcessArea { get; set; }
        public string Fsli { get; set; }
        public string ScopeSummary { get; set; }
        public string Materiality { get; set; }
        public string MaterialityBasis { get; set; }
        public decimal? OverallMateriality { get; set; }
        public decimal? PerformanceMateriality { get; set; }
        public decimal? ClearlyTrivialThreshold { get; set; }
        public string RiskStrategy { get; set; }
        public int? PlanningStatusId { get; set; }
        public string PlanningStatusName { get; set; }
        public string PlanningStatusColor { get; set; }
        public int? ScopeLetterDocumentId { get; set; }
        public string ScopeLetterDocumentTitle { get; set; }
        public bool IsSignedOff { get; set; }
        public string SignedOffByName { get; set; }
        public int? SignedOffByUserId { get; set; }
        public DateTime? SignedOffAt { get; set; }
        public string Notes { get; set; }
        public DateTime? CreatedAt { get; set; }
        public DateTime? UpdatedAt { get; set; }
    }

    public class EngagementTypeOption
    {
        public int Id { get; set; }
        public string Name { get; set; }
        public string Description { get; set; }
        public int? SortOrder { get; set; }
        public bool IsActive { get; set; } = true;
    }

    public class PlanningStatusOption
    {
        public int Id { get; set; }
        public string Name { get; set; }
        public string Description { get; set; }
        public string Color { get; set; }
        public int? SortOrder { get; set; }
        public bool IsClosed { get; set; }
        public bool IsActive { get; set; } = true;
    }

    public class AuditScopeItem
    {
        public int Id { get; set; }
        public int PlanId { get; set; }
        public int ReferenceId { get; set; }
        public string BusinessUnit { get; set; }
        public string ProcessName { get; set; }
        public string SubProcessName { get; set; }
        public string Fsli { get; set; }
        public string Assertions { get; set; }
        public string ScopingRationale { get; set; }
        public string ScopeStatus { get; set; }
        public bool IncludeInScope { get; set; } = true;
        public string RiskReference { get; set; }
        public string ControlReference { get; set; }
        public int? ProcedureId { get; set; }
        public string ProcedureTitle { get; set; }
        public string Owner { get; set; }
        public string Notes { get; set; }
        public DateTime? CreatedAt { get; set; }
    }

    public class AuditManagementAction
    {
        public int Id { get; set; }
        public int ReferenceId { get; set; }
        public int? FindingId { get; set; }
        public string FindingNumber { get; set; }
        public string FindingTitle { get; set; }
        public int? RecommendationId { get; set; }
        public string RecommendationNumber { get; set; }
        public string RecommendationText { get; set; }
        public string ActionTitle { get; set; }
        public string ActionDescription { get; set; }
        public string OwnerName { get; set; }
        public int? OwnerUserId { get; set; }
        public DateTime? DueDate { get; set; }
        public string Status { get; set; }
        public int ProgressPercent { get; set; }
        public string ManagementResponse { get; set; }
        public string ClosureNotes { get; set; }
        public string ValidatedByName { get; set; }
        public int? ValidatedByUserId { get; set; }
        public DateTime? ValidatedAt { get; set; }
        public DateTime? CreatedAt { get; set; }
        public DateTime? UpdatedAt { get; set; }
        public bool IsOverdue { get; set; }
    }

    public class RiskControlMatrixEntry
    {
        public int Id { get; set; }
        public int ReferenceId { get; set; }
        public int? ScopeItemId { get; set; }
        public int? ProcedureId { get; set; }
        public string RiskTitle { get; set; }
        public string RiskDescription { get; set; }
        public string ControlName { get; set; }
        public string ControlDescription { get; set; }
        public string ControlAdequacy { get; set; }
        public string ControlEffectiveness { get; set; }
        public int? ControlClassificationId { get; set; }
        public string ControlClassificationName { get; set; }
        public int? ControlTypeId { get; set; }
        public string ControlTypeName { get; set; }
        public int? ControlFrequencyId { get; set; }
        public string ControlFrequencyName { get; set; }
        public string ControlOwner { get; set; }
        public string ScopeItemLabel { get; set; }
        public string ProcedureTitle { get; set; }
        public string Notes { get; set; }
        public DateTime? CreatedAt { get; set; }
        public DateTime? UpdatedAt { get; set; }
    }

    public class ControlClassificationOption
    {
        public int Id { get; set; }
        public string Name { get; set; }
        public string Description { get; set; }
        public int? SortOrder { get; set; }
        public bool IsActive { get; set; } = true;
    }

    public class ControlTypeOption
    {
        public int Id { get; set; }
        public string Name { get; set; }
        public string Description { get; set; }
        public int? SortOrder { get; set; }
        public bool IsActive { get; set; } = true;
    }

    public class ControlFrequencyOption
    {
        public int Id { get; set; }
        public string Name { get; set; }
        public string Description { get; set; }
        public int? SortOrder { get; set; }
        public bool IsActive { get; set; } = true;
    }

    public class AuditWalkthrough
    {
        public int Id { get; set; }
        public int ReferenceId { get; set; }
        public int? ScopeItemId { get; set; }
        public int? ProcedureId { get; set; }
        public int? RiskControlMatrixId { get; set; }
        public string ProcessName { get; set; }
        public DateTime? WalkthroughDate { get; set; }
        public string Participants { get; set; }
        public string ProcessNarrative { get; set; }
        public string EvidenceSummary { get; set; }
        public string ControlDesignConclusion { get; set; }
        public string Notes { get; set; }
        public string ScopeItemLabel { get; set; }
        public string ProcedureTitle { get; set; }
        public string RiskTitle { get; set; }
        public int ExceptionCount { get; set; }
        public DateTime? CreatedAt { get; set; }
        public List<AuditWalkthroughException> Exceptions { get; set; } = new List<AuditWalkthroughException>();
    }

    public class AuditWalkthroughException
    {
        public int Id { get; set; }
        public int WalkthroughId { get; set; }
        public string ExceptionTitle { get; set; }
        public string ExceptionDescription { get; set; }
        public string Severity { get; set; }
        public int? LinkedFindingId { get; set; }
        public string LinkedFindingNumber { get; set; }
        public bool IsResolved { get; set; }
        public DateTime? CreatedAt { get; set; }
    }
}
