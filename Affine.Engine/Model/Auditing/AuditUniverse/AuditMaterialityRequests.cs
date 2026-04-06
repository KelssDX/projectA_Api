using System;

namespace Affine.Engine.Model.Auditing.AuditUniverse
{
    public class GenerateAuditMaterialityCandidatesRequest
    {
        public int ReferenceId { get; set; }
        public int? FiscalYear { get; set; }
        public int? BenchmarkProfileId { get; set; }
        public string EntityType { get; set; }
        public string IndustryName { get; set; }
        public decimal? ProfitBeforeTaxPercentage { get; set; }
        public decimal? RevenuePercentage { get; set; }
        public decimal? TotalAssetsPercentage { get; set; }
        public decimal? ExpensesPercentage { get; set; }
        public decimal? PerformancePercentage { get; set; }
        public decimal? ClearlyTrivialPercentage { get; set; }
        public int? GeneratedByUserId { get; set; }
        public string GeneratedByName { get; set; }
    }

    public class CreateAuditMaterialityCalculationRequest
    {
        public int ReferenceId { get; set; }
        public int? FiscalYear { get; set; }
        public long? CandidateId { get; set; }
        public int? BenchmarkProfileId { get; set; }
        public string BenchmarkCode { get; set; }
        public string BenchmarkName { get; set; }
        public string BenchmarkSource { get; set; } = "trial_balance";
        public string SourceTable { get; set; } = "audit_trial_balance_snapshots";
        public decimal BenchmarkAmount { get; set; }
        public decimal PercentageApplied { get; set; }
        public decimal? PerformancePercentageApplied { get; set; } = 75m;
        public decimal? ClearlyTrivialPercentageApplied { get; set; } = 5m;
        public bool IsManualOverride { get; set; }
        public bool SetAsActive { get; set; }
        public string Rationale { get; set; }
        public string EntityType { get; set; }
        public string IndustryName { get; set; }
        public string BenchmarkSelectionRationale { get; set; }
        public int? CreatedByUserId { get; set; }
        public string CreatedByName { get; set; }
    }

    public class SetActiveAuditMaterialityRequest
    {
        public int ReferenceId { get; set; }
        public long CalculationId { get; set; }
        public string MaterialityOverrideReason { get; set; }
        public int? ApprovedByUserId { get; set; }
        public string ApprovedByName { get; set; }
        public DateTime? ApprovedAt { get; set; }
    }

    public class UpsertAuditMaterialityScopeLinkRequest
    {
        public long? Id { get; set; }
        public int ReferenceId { get; set; }
        public long? MaterialityCalculationId { get; set; }
        public int? ScopeItemId { get; set; }
        public string Fsli { get; set; }
        public string BenchmarkRelevance { get; set; }
        public string InclusionReason { get; set; }
        public bool IsAboveThreshold { get; set; } = true;
        public decimal? CoveragePercent { get; set; }
    }

    public class UpsertAuditMisstatementRequest
    {
        public long? Id { get; set; }
        public int ReferenceId { get; set; }
        public int? FindingId { get; set; }
        public long? MaterialityCalculationId { get; set; }
        public string Fsli { get; set; }
        public string AccountNumber { get; set; }
        public string TransactionIdentifier { get; set; }
        public string Description { get; set; }
        public decimal ActualAmount { get; set; }
        public decimal? ProjectedAmount { get; set; }
        public string EvaluationBasis { get; set; }
        public string Status { get; set; } = "Open";
        public int? CreatedByUserId { get; set; }
        public string CreatedByName { get; set; }
    }
}
