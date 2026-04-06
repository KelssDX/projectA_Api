namespace Affine.Engine.Model.Auditing.AuditUniverse
{
    public class GenerateTrialBalanceMappingsRequest
    {
        public int ReferenceId { get; set; }
        public int? FiscalYear { get; set; }
        public int? MappingProfileId { get; set; }
        public bool OverwriteReviewedMappings { get; set; }
        public int? GeneratedByUserId { get; set; }
        public string GeneratedByName { get; set; }
    }

    public class SaveTrialBalanceMappingRequest
    {
        public long? Id { get; set; }
        public int ReferenceId { get; set; }
        public int FiscalYear { get; set; }
        public int? MappingProfileId { get; set; }
        public string AccountNumber { get; set; }
        public string AccountName { get; set; }
        public string Fsli { get; set; }
        public string BusinessUnit { get; set; }
        public decimal CurrentBalance { get; set; }
        public string StatementType { get; set; }
        public string SectionName { get; set; }
        public string LineName { get; set; }
        public string Classification { get; set; }
        public int DisplayOrder { get; set; } = 100;
        public string Notes { get; set; }
        public bool IsAutoMapped { get; set; }
        public bool IsReviewed { get; set; } = true;
    }

    public class SaveAuditMappingProfileRequest
    {
        public int ReferenceId { get; set; }
        public int? FiscalYear { get; set; }
        public int? RulePackageId { get; set; }
        public string ProfileName { get; set; }
        public string EntityType { get; set; }
        public string IndustryName { get; set; }
        public string Notes { get; set; }
        public bool IsReusable { get; set; } = true;
        public bool SetAsActive { get; set; } = true;
        public int? CreatedByUserId { get; set; }
        public string CreatedByName { get; set; }
    }

    public class GenerateDraftFinancialStatementsRequest
    {
        public int ReferenceId { get; set; }
        public int? FiscalYear { get; set; }
        public int? MappingProfileId { get; set; }
        public int? GeneratedByUserId { get; set; }
        public string GeneratedByName { get; set; }
    }

    public class GenerateAuditSupportQueueRequest
    {
        public int ReferenceId { get; set; }
        public int? FiscalYear { get; set; }
        public bool IncludeMaterialitySelections { get; set; } = true;
        public bool IncludeJournalRiskSelections { get; set; } = true;
        public bool IncludeRevenueRiskSelections { get; set; } = true;
        public int? GeneratedByUserId { get; set; }
        public string GeneratedByName { get; set; }
    }

    public class UpdateAuditSupportRequestRequest
    {
        public long Id { get; set; }
        public int ReferenceId { get; set; }
        public string SupportStatus { get; set; }
        public string SupportSummary { get; set; }
        public int? LinkedProcedureId { get; set; }
        public int? LinkedWalkthroughId { get; set; }
        public int? LinkedControlId { get; set; }
        public int? LinkedFindingId { get; set; }
        public string Notes { get; set; }
    }

    public class UpsertAuditFinanceFinalizationRequest
    {
        public int ReferenceId { get; set; }
        public int? ActiveMappingProfileId { get; set; }
        public int? ActiveRulePackageId { get; set; }
        public string OverallConclusion { get; set; }
        public string RecommendationSummary { get; set; }
        public string ReleaseReadinessStatus { get; set; }
        public string DraftStatementStatus { get; set; }
        public string OutstandingItems { get; set; }
        public string ReviewerNotes { get; set; }
        public bool ReadyForRelease { get; set; }
        public int? UpdatedByUserId { get; set; }
        public string UpdatedByName { get; set; }
    }
}
