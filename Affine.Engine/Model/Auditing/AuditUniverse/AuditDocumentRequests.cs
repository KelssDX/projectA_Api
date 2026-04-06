using System;
using System.Collections.Generic;
using System.Linq;

namespace Affine.Engine.Model.Auditing.AuditUniverse
{
    public class CreateAuditDocumentRequest
    {
        public int? ReferenceId { get; set; }
        public int? AuditUniverseId { get; set; }
        public int? ProcedureId { get; set; }
        public int? WorkingPaperId { get; set; }
        public int? FindingId { get; set; }
        public int? RecommendationId { get; set; }
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
        public int? GrantedByUserId { get; set; }
        public string GrantedByName { get; set; }
        public List<int> GrantedUserIds { get; set; } = new List<int>();
        public List<string> GrantedRoleNames { get; set; } = new List<string>();

        public bool HasExplicitGrants =>
            GrantedUserIds.Any(id => id > 0) ||
            GrantedRoleNames.Any(role => !string.IsNullOrWhiteSpace(role));
    }

    public class CreateAuditEvidenceRequestRequest
    {
        public int? ReferenceId { get; set; }
        public int? AuditUniverseId { get; set; }
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
        public List<CreateAuditEvidenceRequestItemRequest> Items { get; set; } = new List<CreateAuditEvidenceRequestItemRequest>();
    }

    public class CreateAuditEvidenceRequestItemRequest
    {
        public string ItemDescription { get; set; }
        public string ExpectedDocumentType { get; set; }
        public bool IsRequired { get; set; } = true;
    }

    public class UpdateAuditDocumentSecurityRequest
    {
        public int? VisibilityLevelId { get; set; }
        public string VisibilityLevelName { get; set; }
        public string ConfidentialityLabel { get; set; }
        public string ConfidentialityReason { get; set; }
        public int? UpdatedByUserId { get; set; }
        public string UpdatedByName { get; set; }
        public List<int> GrantedUserIds { get; set; } = new List<int>();
        public List<string> GrantedRoleNames { get; set; } = new List<string>();

        public bool HasExplicitGrants =>
            GrantedUserIds.Any(id => id > 0) ||
            GrantedRoleNames.Any(role => !string.IsNullOrWhiteSpace(role));
    }

    public class AuditEvidenceRequestAssignmentContext
    {
        public int RequestItemId { get; set; }
        public int RequestId { get; set; }
        public int? ReferenceId { get; set; }
        public string Title { get; set; }
        public string RequestedFrom { get; set; }
        public string RequestedToEmail { get; set; }
        public int? RequestedByUserId { get; set; }
        public string RequestedByName { get; set; }
        public string ItemDescription { get; set; }
        public bool IsRequired { get; set; } = true;
        public int? FulfilledDocumentId { get; set; }
    }

    public class ReviewAuditDocumentSecurityRequest
    {
        public bool IsApproved { get; set; }
        public string ReviewNotes { get; set; }
        public int? ReviewedByUserId { get; set; }
        public string ReviewedByName { get; set; }
    }
}
