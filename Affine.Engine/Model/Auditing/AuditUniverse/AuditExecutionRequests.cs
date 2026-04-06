using System;

namespace Affine.Engine.Model.Auditing.AuditUniverse
{
    public class UpsertAuditEngagementPlanRequest
    {
        public int? Id { get; set; }
        public int ReferenceId { get; set; }
        public string EngagementTitle { get; set; }
        public int? EngagementTypeId { get; set; }
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
        public int? ScopeLetterDocumentId { get; set; }
        public bool IsSignedOff { get; set; }
        public string SignedOffByName { get; set; }
        public int? SignedOffByUserId { get; set; }
        public DateTime? SignedOffAt { get; set; }
        public string Notes { get; set; }
    }

    public class CreateAuditScopeItemRequest
    {
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
        public string Owner { get; set; }
        public string Notes { get; set; }
    }

    public class UpdateAuditScopeItemRequest : CreateAuditScopeItemRequest
    {
        public int Id { get; set; }
    }

    public class CreateRiskControlMatrixEntryRequest
    {
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
        public int? ControlTypeId { get; set; }
        public int? ControlFrequencyId { get; set; }
        public string ControlOwner { get; set; }
        public string Notes { get; set; }
    }

    public class UpdateRiskControlMatrixEntryRequest : CreateRiskControlMatrixEntryRequest
    {
        public int Id { get; set; }
    }

    public class CreateAuditWalkthroughRequest
    {
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
    }

    public class UpdateAuditWalkthroughRequest : CreateAuditWalkthroughRequest
    {
        public int Id { get; set; }
    }

    public class AddWalkthroughExceptionRequest
    {
        public int WalkthroughId { get; set; }
        public string ExceptionTitle { get; set; }
        public string ExceptionDescription { get; set; }
        public string Severity { get; set; }
        public int? LinkedFindingId { get; set; }
        public bool IsResolved { get; set; }
    }

    public class ReviewEvidenceRequestItemRequest
    {
        public int RequestItemId { get; set; }
        public bool IsAccepted { get; set; }
        public string ReviewerNotes { get; set; }
        public int? ReviewedByUserId { get; set; }
    }

    public class CreateAuditManagementActionRequest
    {
        public int ReferenceId { get; set; }
        public int? FindingId { get; set; }
        public int? RecommendationId { get; set; }
        public string ActionTitle { get; set; }
        public string ActionDescription { get; set; }
        public string OwnerName { get; set; }
        public int? OwnerUserId { get; set; }
        public DateTime? DueDate { get; set; }
        public string Status { get; set; }
        public int? ProgressPercent { get; set; }
        public string ManagementResponse { get; set; }
        public string ClosureNotes { get; set; }
        public string ValidatedByName { get; set; }
        public int? ValidatedByUserId { get; set; }
        public DateTime? ValidatedAt { get; set; }
    }

    public class UpdateAuditManagementActionRequest : CreateAuditManagementActionRequest
    {
        public int Id { get; set; }
    }
}
