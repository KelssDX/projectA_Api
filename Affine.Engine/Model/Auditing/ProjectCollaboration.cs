using System;
using System.Collections.Generic;

namespace Affine.Engine.Model.Auditing
{
    public class AuditCollaboratorRoleOption
    {
        public int Id { get; set; }
        public string Name { get; set; }
        public string Description { get; set; }
        public string Color { get; set; }
        public bool IsClientRole { get; set; }
        public int? SortOrder { get; set; }
        public bool IsActive { get; set; } = true;
    }

    public class AuditCollaboratorAssignment
    {
        public int? Id { get; set; }
        public int? ProjectId { get; set; }
        public int? ReferenceId { get; set; }
        public int UserId { get; set; }
        public string UserName { get; set; }
        public string UserEmail { get; set; }
        public string UserSystemRole { get; set; }
        public int? CollaboratorRoleId { get; set; }
        public string CollaboratorRoleName { get; set; }
        public string CollaboratorRoleColor { get; set; }
        public bool CanEdit { get; set; } = true;
        public bool CanReview { get; set; }
        public bool CanUploadEvidence { get; set; } = true;
        public bool CanManageAccess { get; set; }
        public string Notes { get; set; }
        public int? AssignedByUserId { get; set; }
        public string AssignedByName { get; set; }
        public DateTime? CreatedAt { get; set; }
        public DateTime? UpdatedAt { get; set; }
        public bool IsInheritedFromProject { get; set; }
    }

    public class SaveAuditCollaboratorsRequest
    {
        public List<AuditCollaboratorAssignmentInput> Collaborators { get; set; } = new List<AuditCollaboratorAssignmentInput>();
    }

    public class AuditCollaboratorAssignmentInput
    {
        public int UserId { get; set; }
        public int? CollaboratorRoleId { get; set; }
        public bool CanEdit { get; set; } = true;
        public bool CanReview { get; set; }
        public bool CanUploadEvidence { get; set; } = true;
        public bool CanManageAccess { get; set; }
        public string Notes { get; set; }
    }
}
