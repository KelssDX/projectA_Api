using System;
using System.Collections.Generic;

namespace Affine.Engine.Model.Auditing.AuditUniverse
{
    /// <summary>
    /// Request to create a new audit universe node
    /// </summary>
    public class CreateAuditUniverseNodeRequest
    {
        public string Name { get; set; }
        public string Code { get; set; }
        public int? ParentId { get; set; }
        public int Level { get; set; } = 1;
        public string LevelName { get; set; }
        public string Description { get; set; }
        public string RiskRating { get; set; } = "Medium";
        public DateTime? LastAuditDate { get; set; }
        public DateTime? NextAuditDate { get; set; }
        public int? AuditFrequencyMonths { get; set; } = 12;
        public string Owner { get; set; }
        public List<int> DepartmentIds { get; set; } = new List<int>();
    }

    /// <summary>
    /// Request to update an existing audit universe node
    /// </summary>
    public class UpdateAuditUniverseNodeRequest
    {
        public int Id { get; set; }
        public string Name { get; set; }
        public string Code { get; set; }
        public int? ParentId { get; set; }
        public int Level { get; set; }
        public string LevelName { get; set; }
        public string Description { get; set; }
        public string RiskRating { get; set; }
        public DateTime? LastAuditDate { get; set; }
        public DateTime? NextAuditDate { get; set; }
        public int? AuditFrequencyMonths { get; set; }
        public string Owner { get; set; }
        public bool IsActive { get; set; } = true;
    }

    /// <summary>
    /// Request to link/unlink departments to a universe node
    /// </summary>
    public class LinkDepartmentRequest
    {
        public int AuditUniverseId { get; set; }
        public int DepartmentId { get; set; }
    }

    /// <summary>
    /// Request to bulk link multiple departments
    /// </summary>
    public class BulkLinkDepartmentsRequest
    {
        public int AuditUniverseId { get; set; }
        public List<int> DepartmentIds { get; set; } = new List<int>();
    }

    /// <summary>
    /// Request to create a new audit finding
    /// </summary>
    public class CreateAuditFindingRequest
    {
        public int? ReferenceId { get; set; }
        public int? AuditUniverseId { get; set; }
        public string FindingTitle { get; set; }
        public string FindingDescription { get; set; }
        public int? SeverityId { get; set; }
        public DateTime? DueDate { get; set; }
        public string AssignedTo { get; set; }
        public int? AssignedToUserId { get; set; }
        public string RootCause { get; set; }
        public string BusinessImpact { get; set; }
        public int? CreatedByUserId { get; set; }
    }

    /// <summary>
    /// Request to update an existing audit finding
    /// </summary>
    public class UpdateAuditFindingRequest
    {
        public int Id { get; set; }
        public string FindingTitle { get; set; }
        public string FindingDescription { get; set; }
        public int? SeverityId { get; set; }
        public int? StatusId { get; set; }
        public DateTime? DueDate { get; set; }
        public DateTime? ClosedDate { get; set; }
        public string AssignedTo { get; set; }
        public int? AssignedToUserId { get; set; }
        public string RootCause { get; set; }
        public string BusinessImpact { get; set; }
    }

    /// <summary>
    /// Request to create a recommendation for a finding
    /// </summary>
    public class CreateRecommendationRequest
    {
        public int FindingId { get; set; }
        public string Recommendation { get; set; }
        public int Priority { get; set; } = 2;
        public DateTime? TargetDate { get; set; }
        public string ResponsiblePerson { get; set; }
        public int? ResponsibleUserId { get; set; }
    }

    /// <summary>
    /// Request to update a recommendation
    /// </summary>
    public class UpdateRecommendationRequest
    {
        public int Id { get; set; }
        public string Recommendation { get; set; }
        public int Priority { get; set; }
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
    }

    /// <summary>
    /// Request to record/update audit coverage
    /// </summary>
    public class UpdateAuditCoverageRequest
    {
        public int AuditUniverseId { get; set; }
        public int PeriodYear { get; set; }
        public int? PeriodQuarter { get; set; }
        public int PlannedAudits { get; set; }
        public int CompletedAudits { get; set; }
        public int? TotalFindings { get; set; }
        public int? CriticalFindings { get; set; }
        public int? HighFindings { get; set; }
        public string Notes { get; set; }
    }

    /// <summary>
    /// Filter parameters for querying findings
    /// </summary>
    public class FindingsFilterRequest
    {
        public int? ReferenceId { get; set; }
        public int? AuditUniverseId { get; set; }
        public List<int> SeverityIds { get; set; }
        public List<int> StatusIds { get; set; }
        public DateTime? IdentifiedDateFrom { get; set; }
        public DateTime? IdentifiedDateTo { get; set; }
        public DateTime? DueDateFrom { get; set; }
        public DateTime? DueDateTo { get; set; }
        public bool? OverdueOnly { get; set; }
        public int? AssignedToUserId { get; set; }
        public string SearchText { get; set; }
        public int PageNumber { get; set; } = 1;
        public int PageSize { get; set; } = 20;
        public string SortBy { get; set; } = "identified_date";
        public bool SortDescending { get; set; } = true;
    }

    /// <summary>
    /// Paginated response wrapper
    /// </summary>
    public class PaginatedResponse<T>
    {
        public List<T> Items { get; set; } = new List<T>();
        public int TotalCount { get; set; }
        public int PageNumber { get; set; }
        public int PageSize { get; set; }
        public int TotalPages { get; set; }
        public bool HasNextPage { get; set; }
        public bool HasPreviousPage { get; set; }
    }
}
