using System;

namespace Affine.Engine.Model.Auditing.AuditUniverse
{
    /// <summary>
    /// Represents a recommendation/action plan for an audit finding
    /// </summary>
    public class AuditRecommendation
    {
        public int Id { get; set; }
        public int FindingId { get; set; }
        public string RecommendationNumber { get; set; }
        public string Recommendation { get; set; }
        public int Priority { get; set; } = 2; // 1=High, 2=Medium, 3=Low
        public string ManagementResponse { get; set; }
        public DateTime? AgreedDate { get; set; }
        public DateTime? TargetDate { get; set; }
        public DateTime? ImplementationDate { get; set; }
        public string ResponsiblePerson { get; set; }
        public int? ResponsibleUserId { get; set; }
        public int? StatusId { get; set; }
        public string VerificationNotes { get; set; }
        public int? VerifiedByUserId { get; set; }
        public DateTime? VerifiedDate { get; set; }
        public DateTime? CreatedAt { get; set; }
        public DateTime? UpdatedAt { get; set; }

        // Navigation/Display properties
        public string StatusName { get; set; }
        public string StatusColor { get; set; }
        public string PriorityName { get; set; }
        public string ResponsibleUserName { get; set; }
        public string VerifiedByUserName { get; set; }
        public string FindingTitle { get; set; }
        public string FindingNumber { get; set; }

        // Computed
        public int? DaysUntilTarget { get; set; }
        public bool IsOverdue { get; set; }
    }

    /// <summary>
    /// Lookup for recommendation status values
    /// </summary>
    public class RecommendationStatus
    {
        public int Id { get; set; }
        public string Name { get; set; }
        public string Description { get; set; }
        public string Color { get; set; }
        public int? SortOrder { get; set; }
        public bool IsActive { get; set; } = true;
    }

    /// <summary>
    /// Summary of recommendations for dashboard display
    /// </summary>
    public class RecommendationSummary
    {
        public int TotalCount { get; set; }
        public int PendingCount { get; set; }
        public int AgreedCount { get; set; }
        public int InProgressCount { get; set; }
        public int ImplementedCount { get; set; }
        public int RejectedCount { get; set; }
        public int DeferredCount { get; set; }
        public int OverdueCount { get; set; }
        public double ImplementationRate { get; set; } // Percentage implemented
    }
}
