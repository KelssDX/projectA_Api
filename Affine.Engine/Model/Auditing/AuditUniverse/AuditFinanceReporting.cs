using System;
using System.Collections.Generic;

namespace Affine.Engine.Model.Auditing.AuditUniverse
{
    public class AuditFinanceAuditWorkspace
    {
        public int ReferenceId { get; set; }
        public string EngagementTitle { get; set; }
        public int? PlanYear { get; set; }
        public bool HasTrialBalanceData { get; set; }
        public int? LatestTrialBalanceYear { get; set; }
        public int TrialBalanceAccountCount { get; set; }
        public bool HasJournalData { get; set; }
        public int? LatestJournalYear { get; set; }
        public int JournalEntryCount { get; set; }
        public string RulePackageCode { get; set; }
        public string RulePackageName { get; set; }
        public int? ActiveMappingProfileId { get; set; }
        public string ActiveMappingProfileName { get; set; }
        public int MappingCount { get; set; }
        public int UnmappedAccountCount { get; set; }
        public int SupportRequestCount { get; set; }
        public int OpenSupportRequestCount { get; set; }
        public List<AuditRulePackage> RulePackages { get; set; } = new List<AuditRulePackage>();
        public List<AuditFinancialStatementMappingProfile> MappingProfiles { get; set; } = new List<AuditFinancialStatementMappingProfile>();
        public List<AuditFinancialStatementMappingItem> TrialBalanceMappings { get; set; } = new List<AuditFinancialStatementMappingItem>();
        public List<AuditDraftFinancialStatement> DraftStatements { get; set; } = new List<AuditDraftFinancialStatement>();
        public List<AuditSubstantiveSupportRequest> SupportRequests { get; set; } = new List<AuditSubstantiveSupportRequest>();
        public AuditFinanceFinalizationRecord Finalization { get; set; } = new AuditFinanceFinalizationRecord();
    }

    public class AuditRulePackage
    {
        public int Id { get; set; }
        public string PackageCode { get; set; }
        public string PackageName { get; set; }
        public string DomainCode { get; set; }
        public string Description { get; set; }
        public bool IsDefault { get; set; }
        public bool IsActive { get; set; }
    }

    public class AuditFinancialStatementMappingProfile
    {
        public int Id { get; set; }
        public int? ReferenceId { get; set; }
        public int? EngagementTypeId { get; set; }
        public string EngagementTypeName { get; set; }
        public int? RulePackageId { get; set; }
        public string PackageCode { get; set; }
        public string PackageName { get; set; }
        public string ProfileCode { get; set; }
        public string ProfileName { get; set; }
        public string EntityType { get; set; }
        public string IndustryName { get; set; }
        public string Notes { get; set; }
        public bool IsReusable { get; set; }
        public bool IsDefault { get; set; }
        public bool IsActive { get; set; }
        public int RuleCount { get; set; }
        public string CreatedByName { get; set; }
        public DateTime? CreatedAt { get; set; }
    }

    public class AuditFinancialStatementMappingItem
    {
        public long Id { get; set; }
        public int ReferenceId { get; set; }
        public int FiscalYear { get; set; }
        public int? MappingProfileId { get; set; }
        public string MappingProfileName { get; set; }
        public string AccountNumber { get; set; }
        public string AccountName { get; set; }
        public string Fsli { get; set; }
        public string BusinessUnit { get; set; }
        public decimal CurrentBalance { get; set; }
        public string StatementType { get; set; }
        public string SectionName { get; set; }
        public string LineName { get; set; }
        public string Classification { get; set; }
        public int DisplayOrder { get; set; }
        public string Notes { get; set; }
        public bool IsAutoMapped { get; set; }
        public bool IsReviewed { get; set; }
        public DateTime? UpdatedAt { get; set; }
    }

    public class AuditDraftFinancialStatement
    {
        public string StatementType { get; set; }
        public int FiscalYear { get; set; }
        public decimal TotalAmount { get; set; }
        public List<AuditDraftFinancialStatementLine> Lines { get; set; } = new List<AuditDraftFinancialStatementLine>();
    }

    public class AuditDraftFinancialStatementLine
    {
        public string StatementType { get; set; }
        public string SectionName { get; set; }
        public string LineName { get; set; }
        public decimal Amount { get; set; }
        public int AccountCount { get; set; }
    }

    public class AuditSubstantiveSupportRequest
    {
        public long Id { get; set; }
        public int ReferenceId { get; set; }
        public int FiscalYear { get; set; }
        public string SourceType { get; set; }
        public long? SourceRecordId { get; set; }
        public string SourceKey { get; set; }
        public string TransactionIdentifier { get; set; }
        public string JournalNumber { get; set; }
        public DateTime? PostingDate { get; set; }
        public string AccountNumber { get; set; }
        public string AccountName { get; set; }
        public string Fsli { get; set; }
        public decimal Amount { get; set; }
        public string Description { get; set; }
        public string TriageReason { get; set; }
        public string RiskFlags { get; set; }
        public string SupportStatus { get; set; }
        public string SupportSummary { get; set; }
        public int? LinkedProcedureId { get; set; }
        public string LinkedProcedureTitle { get; set; }
        public int? LinkedWalkthroughId { get; set; }
        public string LinkedWalkthroughTitle { get; set; }
        public int? LinkedControlId { get; set; }
        public string LinkedControlName { get; set; }
        public int? LinkedFindingId { get; set; }
        public string LinkedFindingTitle { get; set; }
        public string Notes { get; set; }
        public DateTime? RequestedAt { get; set; }
        public DateTime? UpdatedAt { get; set; }
    }

    public class AuditFinanceFinalizationRecord
    {
        public long Id { get; set; }
        public int ReferenceId { get; set; }
        public int? ActiveMappingProfileId { get; set; }
        public string ActiveMappingProfileName { get; set; }
        public int? ActiveRulePackageId { get; set; }
        public string ActiveRulePackageCode { get; set; }
        public string ActiveRulePackageName { get; set; }
        public string OverallConclusion { get; set; }
        public string RecommendationSummary { get; set; }
        public string ReleaseReadinessStatus { get; set; }
        public string DraftStatementStatus { get; set; }
        public string OutstandingItems { get; set; }
        public string ReviewerNotes { get; set; }
        public bool ReadyForRelease { get; set; }
        public int? LastGeneratedStatementYear { get; set; }
        public DateTime? LastGeneratedAt { get; set; }
        public int? UpdatedByUserId { get; set; }
        public string UpdatedByName { get; set; }
        public DateTime? UpdatedAt { get; set; }
    }
}
