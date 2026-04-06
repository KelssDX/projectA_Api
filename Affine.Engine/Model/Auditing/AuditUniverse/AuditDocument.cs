using System;
using System.Collections.Generic;

namespace Affine.Engine.Model.Auditing.AuditUniverse
{
    /// <summary>
    /// Represents a document or evidence item uploaded for an audit engagement.
    /// </summary>
    public class AuditDocument
    {
        public int Id { get; set; }
        public int? ReferenceId { get; set; }
        public int? AuditUniverseId { get; set; }
        public int? ProcedureId { get; set; }
        public int? WorkingPaperId { get; set; }
        public int? FindingId { get; set; }
        public int? RecommendationId { get; set; }
        public string DocumentCode { get; set; }
        public string Title { get; set; }
        public string OriginalFileName { get; set; }
        public string StoredFileName { get; set; }
        public string StoredRelativePath { get; set; }
        public string ContentType { get; set; }
        public string FileExtension { get; set; }
        public long? FileSize { get; set; }
        public int? CategoryId { get; set; }
        public int? VisibilityLevelId { get; set; }
        public string SourceType { get; set; }
        public string Tags { get; set; }
        public string Notes { get; set; }
        public string ConfidentialityLabel { get; set; }
        public string ConfidentialityReason { get; set; }
        public bool SecurityReviewRequired { get; set; }
        public string SecurityReviewStatus { get; set; }
        public DateTime? SecurityReviewRequestedAt { get; set; }
        public int? SecurityReviewRequestedByUserId { get; set; }
        public string SecurityReviewRequestedByName { get; set; }
        public DateTime? SecurityReviewedAt { get; set; }
        public int? SecurityReviewedByUserId { get; set; }
        public string SecurityReviewedByName { get; set; }
        public string SecurityReviewNotes { get; set; }
        public string UploadedByName { get; set; }
        public int? UploadedByUserId { get; set; }
        public DateTime? UploadedAt { get; set; }
        public bool IsActive { get; set; } = true;

        // Display fields
        public string CategoryName { get; set; }
        public string CategoryColor { get; set; }
        public bool IsSensitiveCategory { get; set; }
        public string VisibilityLevelName { get; set; }
        public string VisibilityLevelColor { get; set; }
        public bool VisibilityIsRestricted { get; set; }
        public string AccessSummary { get; set; }
        public string ProcedureTitle { get; set; }
        public string WorkingPaperCode { get; set; }
        public string WorkingPaperTitle { get; set; }
        public string FindingNumber { get; set; }
        public string FindingTitle { get; set; }
        public string RecommendationNumber { get; set; }
        public string RecommendationText { get; set; }
        public List<AuditDocumentAccessGrant> AccessGrants { get; set; } = new List<AuditDocumentAccessGrant>();
    }

    public class AuditDocumentCategory
    {
        public int Id { get; set; }
        public string Name { get; set; }
        public string Description { get; set; }
        public string Color { get; set; }
        public int? SortOrder { get; set; }
        public bool IsSensitive { get; set; }
        public int? DefaultVisibilityLevelId { get; set; }
        public bool RequiresSecurityApproval { get; set; }
        public string DefaultConfidentialityLabel { get; set; }
        public bool IsActive { get; set; } = true;
    }

    public class AuditDocumentVisibilityOption
    {
        public int Id { get; set; }
        public string Name { get; set; }
        public string Description { get; set; }
        public string Color { get; set; }
        public bool IsRestricted { get; set; }
        public int? SortOrder { get; set; }
        public bool IsActive { get; set; } = true;
    }

    public class AuditDocumentAccessGrant
    {
        public int Id { get; set; }
        public int DocumentId { get; set; }
        public int? GranteeUserId { get; set; }
        public string GrantedUserName { get; set; }
        public string GranteeRoleName { get; set; }
        public string PermissionLevel { get; set; }
        public bool CanDownload { get; set; } = true;
        public int? GrantedByUserId { get; set; }
        public string GrantedByName { get; set; }
        public string Notes { get; set; }
        public DateTime? GrantedAt { get; set; }
        public DateTime? ExpiresAt { get; set; }
    }

    public class AuditEvidenceRequest
    {
        public int Id { get; set; }
        public int? ReferenceId { get; set; }
        public int? AuditUniverseId { get; set; }
        public string RequestNumber { get; set; }
        public string Title { get; set; }
        public string RequestDescription { get; set; }
        public string RequestedFrom { get; set; }
        public string RequestedToEmail { get; set; }
        public int Priority { get; set; } = 2;
        public DateTime? DueDate { get; set; }
        public int? StatusId { get; set; }
        public int? RequestedByUserId { get; set; }
        public string RequestedByName { get; set; }
        public string WorkflowInstanceId { get; set; }
        public string Notes { get; set; }
        public DateTime? CreatedAt { get; set; }
        public DateTime? UpdatedAt { get; set; }

        // Display fields
        public string StatusName { get; set; }
        public string StatusColor { get; set; }
        public int TotalItems { get; set; }
        public int FulfilledItems { get; set; }
        public List<AuditEvidenceRequestItem> Items { get; set; } = new List<AuditEvidenceRequestItem>();
    }

    public class AuditEvidenceRequestItem
    {
        public int Id { get; set; }
        public int RequestId { get; set; }
        public string ItemDescription { get; set; }
        public string ExpectedDocumentType { get; set; }
        public bool IsRequired { get; set; } = true;
        public int? FulfilledDocumentId { get; set; }
        public DateTime? SubmittedAt { get; set; }
        public string ReviewerNotes { get; set; }
        public int? ReviewedByUserId { get; set; }
        public DateTime? ReviewedAt { get; set; }
        public bool? IsAccepted { get; set; }
        public DateTime? CreatedAt { get; set; }

        // Display fields
        public string FulfilledDocumentCode { get; set; }
        public string FulfilledDocumentTitle { get; set; }
    }

    public class EvidenceRequestStatus
    {
        public int Id { get; set; }
        public string Name { get; set; }
        public string Description { get; set; }
        public string Color { get; set; }
        public bool IsClosed { get; set; }
        public int? SortOrder { get; set; }
        public bool IsActive { get; set; } = true;
    }
}
