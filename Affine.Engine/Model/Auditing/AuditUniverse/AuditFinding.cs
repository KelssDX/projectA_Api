using System;
using System.Collections.Generic;

namespace Affine.Engine.Model.Auditing.AuditUniverse
{
    /// <summary>
    /// Represents an audit finding identified during a risk assessment
    /// </summary>
    public class AuditFinding
    {
        public int Id { get; set; }
        public int? ReferenceId { get; set; }
        public int? AuditUniverseId { get; set; }
        public string FindingNumber { get; set; }
        public string FindingTitle { get; set; }
        public string FindingDescription { get; set; }
        public int? SeverityId { get; set; }
        public int? StatusId { get; set; }
        public DateTime IdentifiedDate { get; set; } = DateTime.Today;
        public DateTime? DueDate { get; set; }
        public DateTime? ClosedDate { get; set; }
        public string AssignedTo { get; set; }
        public int? AssignedToUserId { get; set; }
        public string RootCause { get; set; }
        public string BusinessImpact { get; set; }
        public int? CreatedByUserId { get; set; }
        public DateTime? CreatedAt { get; set; }
        public DateTime? UpdatedAt { get; set; }

        // Navigation/Display properties
        public string SeverityName { get; set; }
        public string SeverityColor { get; set; }
        public string StatusName { get; set; }
        public string StatusColor { get; set; }
        public string AuditUniverseName { get; set; }
        public string AssignedToUserName { get; set; }
        public string CreatedByUserName { get; set; }

        // Computed
        public int DaysOpen { get; set; }
        public int? DaysOverdue { get; set; }
        public bool IsOverdue { get; set; }
        public int RecommendationCount { get; set; }

        // Related data
        public List<AuditRecommendation> Recommendations { get; set; } = new List<AuditRecommendation>();
    }

    /// <summary>
    /// Lookup for finding severity levels
    /// </summary>
    public class FindingSeverity
    {
        public int Id { get; set; }
        public string Name { get; set; }
        public string Description { get; set; }
        public string Color { get; set; }
        public int? SortOrder { get; set; }
        public bool IsActive { get; set; } = true;
    }

    /// <summary>
    /// Lookup for finding status values
    /// </summary>
    public class FindingStatus
    {
        public int Id { get; set; }
        public string Name { get; set; }
        public string Description { get; set; }
        public string Color { get; set; }
        public bool IsClosed { get; set; }
        public int? SortOrder { get; set; }
        public bool IsActive { get; set; } = true;
    }

    /// <summary>
    /// Response for findings aging analysis
    /// </summary>
    public class FindingsAgingResponse
    {
        public int ReferenceId { get; set; }
        public int? AuditUniverseId { get; set; }
        public List<FindingsAgingBucket> AgingBuckets { get; set; } = new List<FindingsAgingBucket>();
        public FindingsAgingSummary Summary { get; set; } = new FindingsAgingSummary();
    }

    public class FindingsAgingBucket
    {
        public string Severity { get; set; } // Critical, High, Medium, Low
        public string SeverityColor { get; set; }
        public int Days0To30 { get; set; }
        public int Days31To60 { get; set; }
        public int Days61To90 { get; set; }
        public int Days90Plus { get; set; }
        public int TotalOpen { get; set; }
    }

    public class FindingsAgingSummary
    {
        public int TotalOpen { get; set; }
        public int TotalOverdue { get; set; }
        public int ClosedThisPeriod { get; set; }
        public double AverageAgeInDays { get; set; }
        public int OldestOpenDays { get; set; }
    }

    /// <summary>
    /// Simple finding item for lists
    /// </summary>
    public class FindingListItem
    {
        public int Id { get; set; }
        public string FindingNumber { get; set; }
        public string FindingTitle { get; set; }
        public string Severity { get; set; }
        public string SeverityColor { get; set; }
        public string Status { get; set; }
        public string StatusColor { get; set; }
        public DateTime IdentifiedDate { get; set; }
        public DateTime? DueDate { get; set; }
        public string AssignedTo { get; set; }
        public int DaysOpen { get; set; }
        public bool IsOverdue { get; set; }
    }
}
