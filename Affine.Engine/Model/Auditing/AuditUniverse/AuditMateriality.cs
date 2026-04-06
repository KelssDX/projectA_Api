using System;
using System.Collections.Generic;

namespace Affine.Engine.Model.Auditing.AuditUniverse
{
    public class AuditMaterialityWorkspace
    {
        public int ReferenceId { get; set; }
        public string EngagementTitle { get; set; }
        public int? EngagementTypeId { get; set; }
        public string EngagementTypeName { get; set; }
        public int? PlanYear { get; set; }
        public string PlanningMateriality { get; set; }
        public string PlanningMaterialityBasis { get; set; }
        public decimal? PlanningOverallMateriality { get; set; }
        public decimal? PlanningPerformanceMateriality { get; set; }
        public decimal? PlanningClearlyTrivialThreshold { get; set; }
        public int? SelectedBenchmarkProfileId { get; set; }
        public string SelectedBenchmarkProfileName { get; set; }
        public string MaterialityEntityType { get; set; }
        public string MaterialityIndustryName { get; set; }
        public string MaterialityBenchmarkSelectionRationale { get; set; }
        public bool HasTrialBalanceData { get; set; }
        public int? LatestTrialBalanceYear { get; set; }
        public int TrialBalanceAccountCount { get; set; }
        public decimal TrialBalanceAbsoluteBalance { get; set; }
        public bool HasJournalData { get; set; }
        public int? LatestJournalYear { get; set; }
        public int JournalEntryCount { get; set; }
        public DateTime? LatestAnalyticsImportAt { get; set; }
        public AuditMaterialityCalculation ActiveCalculation { get; set; }
        public AuditMaterialityApplicationSummary ApplicationSummary { get; set; }
        public AuditMaterialityMisstatementSummary MisstatementSummary { get; set; }
        public List<AuditMaterialityScopeLink> ScopeLinks { get; set; } = new List<AuditMaterialityScopeLink>();
        public List<AuditMisstatement> Misstatements { get; set; } = new List<AuditMisstatement>();
        public List<AuditMaterialityCalculation> Calculations { get; set; } = new List<AuditMaterialityCalculation>();
        public List<AuditMaterialityCandidate> BenchmarkCandidates { get; set; } = new List<AuditMaterialityCandidate>();
        public List<AuditMaterialityBenchmarkProfile> BenchmarkProfiles { get; set; } = new List<AuditMaterialityBenchmarkProfile>();
        public List<AuditMaterialityApprovalHistoryEntry> ApprovalHistory { get; set; } = new List<AuditMaterialityApprovalHistoryEntry>();
    }

    public class AuditMaterialityApplicationSummary
    {
        public int ReferenceId { get; set; }
        public string ThresholdSource { get; set; }
        public string ActiveBenchmarkSummary { get; set; }
        public decimal OverallMateriality { get; set; }
        public decimal PerformanceMateriality { get; set; }
        public decimal ClearlyTrivialThreshold { get; set; }
        public string PopulationSource { get; set; }
        public int? PopulationFiscalYear { get; set; }
        public int PopulationItemCount { get; set; }
        public decimal PopulationAmount { get; set; }
        public int KeyItemCount { get; set; }
        public decimal KeyItemAmount { get; set; }
        public int SamplePoolCount { get; set; }
        public decimal SamplePoolAmount { get; set; }
        public int ScopeCandidateCount { get; set; }
        public decimal ScopeCandidateBalance { get; set; }
        public string Guidance { get; set; }
        public List<AuditMaterialityPopulationItem> KeyItems { get; set; } = new List<AuditMaterialityPopulationItem>();
        public List<AuditMaterialityPopulationItem> SamplePoolItems { get; set; } = new List<AuditMaterialityPopulationItem>();
        public List<AuditMaterialityPopulationItem> ScopeCandidates { get; set; } = new List<AuditMaterialityPopulationItem>();
    }

    public class AuditMaterialityPopulationItem
    {
        public string ItemIdentifier { get; set; }
        public DateTime? ItemDate { get; set; }
        public int? FiscalYear { get; set; }
        public string AccountNumber { get; set; }
        public string AccountName { get; set; }
        public string Fsli { get; set; }
        public string BusinessUnit { get; set; }
        public string Description { get; set; }
        public decimal BasisAmount { get; set; }
        public string Classification { get; set; }
        public string RecommendedAction { get; set; }
        public string SourceDataset { get; set; }
    }

    public class AuditMaterialityMisstatementSummary
    {
        public int ReferenceId { get; set; }
        public string ThresholdSource { get; set; }
        public decimal OverallMateriality { get; set; }
        public decimal PerformanceMateriality { get; set; }
        public decimal ClearlyTrivialThreshold { get; set; }
        public int TotalRecordedMisstatements { get; set; }
        public decimal TotalActualAmount { get; set; }
        public decimal TotalProjectedAmount { get; set; }
        public int AboveClearlyTrivialCount { get; set; }
        public int AbovePerformanceMaterialityCount { get; set; }
        public int AboveOverallMaterialityCount { get; set; }
        public string EvaluationConclusion { get; set; }
    }

    public class AuditMaterialityScopeLink
    {
        public long Id { get; set; }
        public int ReferenceId { get; set; }
        public long MaterialityCalculationId { get; set; }
        public string CalculationSummary { get; set; }
        public int? ScopeItemId { get; set; }
        public string ScopeItemLabel { get; set; }
        public string Fsli { get; set; }
        public string BenchmarkRelevance { get; set; }
        public string InclusionReason { get; set; }
        public bool IsAboveThreshold { get; set; }
        public decimal? CoveragePercent { get; set; }
        public DateTime? CreatedAt { get; set; }
    }

    public class AuditMisstatement
    {
        public long Id { get; set; }
        public int ReferenceId { get; set; }
        public int? FindingId { get; set; }
        public string FindingTitle { get; set; }
        public long? MaterialityCalculationId { get; set; }
        public string CalculationSummary { get; set; }
        public string Fsli { get; set; }
        public string AccountNumber { get; set; }
        public string TransactionIdentifier { get; set; }
        public string Description { get; set; }
        public decimal ActualAmount { get; set; }
        public decimal? ProjectedAmount { get; set; }
        public string EvaluationBasis { get; set; }
        public bool ExceedsClearlyTrivial { get; set; }
        public bool ExceedsPerformanceMateriality { get; set; }
        public bool ExceedsOverallMateriality { get; set; }
        public string Status { get; set; }
        public int? CreatedByUserId { get; set; }
        public string CreatedByName { get; set; }
        public DateTime? CreatedAt { get; set; }
        public DateTime? UpdatedAt { get; set; }
    }

    public class AuditMaterialityCalculation
    {
        public long Id { get; set; }
        public int ReferenceId { get; set; }
        public int? FiscalYear { get; set; }
        public long? CandidateId { get; set; }
        public int? BenchmarkProfileId { get; set; }
        public string BenchmarkProfileName { get; set; }
        public string BenchmarkProfileValidationStatus { get; set; }
        public string BenchmarkCode { get; set; }
        public string BenchmarkName { get; set; }
        public string BenchmarkSource { get; set; }
        public string SourceTable { get; set; }
        public decimal BenchmarkAmount { get; set; }
        public decimal PercentageApplied { get; set; }
        public decimal OverallMateriality { get; set; }
        public decimal PerformancePercentageApplied { get; set; }
        public decimal PerformanceMateriality { get; set; }
        public decimal ClearlyTrivialPercentageApplied { get; set; }
        public decimal ClearlyTrivialThreshold { get; set; }
        public string CalculationSummary { get; set; }
        public string Rationale { get; set; }
        public string EntityType { get; set; }
        public string IndustryName { get; set; }
        public string BenchmarkSelectionRationale { get; set; }
        public bool IsActive { get; set; }
        public bool IsManualOverride { get; set; }
        public int? ApprovedByUserId { get; set; }
        public string ApprovedByName { get; set; }
        public DateTime? ApprovedAt { get; set; }
        public int? CreatedByUserId { get; set; }
        public string CreatedByName { get; set; }
        public DateTime? CreatedAt { get; set; }
        public DateTime? UpdatedAt { get; set; }
    }

    public class AuditMaterialityCandidate
    {
        public long Id { get; set; }
        public int ReferenceId { get; set; }
        public int? FiscalYear { get; set; }
        public int? BenchmarkProfileId { get; set; }
        public string BenchmarkProfileName { get; set; }
        public string BenchmarkProfileValidationStatus { get; set; }
        public string CandidateCode { get; set; }
        public string CandidateName { get; set; }
        public string BenchmarkSource { get; set; }
        public string SourceTable { get; set; }
        public string SourceMetricLabel { get; set; }
        public decimal BenchmarkAmount { get; set; }
        public decimal RecommendedPercentage { get; set; }
        public decimal RecommendedOverallMateriality { get; set; }
        public decimal RecommendedPerformancePercentage { get; set; }
        public decimal RecommendedPerformanceMateriality { get; set; }
        public decimal RecommendedClearlyTrivialPercentage { get; set; }
        public decimal RecommendedClearlyTrivialThreshold { get; set; }
        public string Notes { get; set; }
        public string EntityType { get; set; }
        public string IndustryName { get; set; }
        public bool IsSelected { get; set; }
        public long? SelectedCalculationId { get; set; }
        public int? GeneratedByUserId { get; set; }
        public string GeneratedByName { get; set; }
        public DateTime? GeneratedAt { get; set; }
    }

    public class AuditMaterialityBenchmarkProfile
    {
        public int Id { get; set; }
        public string ProfileCode { get; set; }
        public string ProfileName { get; set; }
        public int? EngagementTypeId { get; set; }
        public string EngagementTypeName { get; set; }
        public string EntityType { get; set; }
        public string IndustryName { get; set; }
        public decimal ProfitBeforeTaxPercentage { get; set; }
        public decimal RevenuePercentage { get; set; }
        public decimal TotalAssetsPercentage { get; set; }
        public decimal ExpensesPercentage { get; set; }
        public decimal PerformancePercentage { get; set; }
        public decimal ClearlyTrivialPercentage { get; set; }
        public string BenchmarkRationale { get; set; }
        public string ValidationStatus { get; set; }
        public string ValidationNotes { get; set; }
        public string ApprovedByName { get; set; }
        public DateTime? ApprovedAt { get; set; }
        public bool IsDefault { get; set; }
        public int SortOrder { get; set; }
        public bool IsActive { get; set; }
    }

    public class AuditMaterialityApprovalHistoryEntry
    {
        public long Id { get; set; }
        public int ReferenceId { get; set; }
        public long? PreviousCalculationId { get; set; }
        public string PreviousCalculationSummary { get; set; }
        public long CalculationId { get; set; }
        public int? BenchmarkProfileId { get; set; }
        public string BenchmarkProfileName { get; set; }
        public string ActionType { get; set; }
        public string ActionLabel { get; set; }
        public string BenchmarkCode { get; set; }
        public string BenchmarkName { get; set; }
        public decimal PercentageApplied { get; set; }
        public decimal PerformancePercentageApplied { get; set; }
        public decimal ClearlyTrivialPercentageApplied { get; set; }
        public decimal OverallMateriality { get; set; }
        public decimal PerformanceMateriality { get; set; }
        public decimal ClearlyTrivialThreshold { get; set; }
        public string EntityType { get; set; }
        public string IndustryName { get; set; }
        public string BenchmarkSelectionRationale { get; set; }
        public string OverrideReason { get; set; }
        public int? ApprovedByUserId { get; set; }
        public string ApprovedByName { get; set; }
        public DateTime? ApprovedAt { get; set; }
        public DateTime? CreatedAt { get; set; }
    }
}
