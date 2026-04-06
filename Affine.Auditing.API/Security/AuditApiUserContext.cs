using Affine.Engine.Model.Auditing.AuditUniverse;
using Microsoft.AspNetCore.Http;
using System.Collections.Generic;
using System.Linq;

namespace Affine.Auditing.API.Security
{
    public sealed class AuditApiUserContext
    {
        public const string UserIdHeader = "X-Audit-User-Id";
        public const string UserRoleHeader = "X-Audit-User-Role";
        public const string UserNameHeader = "X-Audit-User-Name";
        public const string UserEmailHeader = "X-Audit-User-Email";

        private static readonly HashSet<string> AdminRoles = new(new[]
        {
            "admin",
            "administrator",
            "superadmin"
        });

        private static readonly HashSet<string> AuditEditorRoles = new(new[]
        {
            "admin",
            "administrator",
            "superadmin",
            "auditor",
            "senior_auditor",
            "internal_auditor",
            "external_auditor",
            "audit_manager",
            "manager"
        });

        private static readonly HashSet<string> AuditReviewRoles = new(new[]
        {
            "admin",
            "administrator",
            "superadmin",
            "reviewer",
            "audit_reviewer",
            "audit_manager",
            "manager",
            "partner",
            "director"
        });

        private static readonly HashSet<string> ClientContributorRoles = new(new[]
        {
            "client_owner",
            "owner",
            "management",
            "process_owner",
            "information_owner"
        });

        public int? UserId { get; }
        public string Role { get; }
        public string UserName { get; }
        public string UserEmail { get; }

        public bool HasUserContext =>
            UserId.HasValue
            || !string.IsNullOrWhiteSpace(Role)
            || !string.IsNullOrWhiteSpace(UserName)
            || !string.IsNullOrWhiteSpace(UserEmail);

        private AuditApiUserContext(int? userId, string role, string userName, string userEmail)
        {
            UserId = userId;
            Role = NormalizeRole(role);
            UserName = userName?.Trim() ?? string.Empty;
            UserEmail = userEmail?.Trim() ?? string.Empty;
        }

        public static AuditApiUserContext FromHttpContext(HttpContext httpContext)
        {
            var headers = httpContext?.Request?.Headers;
            return new AuditApiUserContext(
                ParseNullableInt(headers?[UserIdHeader].FirstOrDefault()),
                headers?[UserRoleHeader].FirstOrDefault() ?? string.Empty,
                headers?[UserNameHeader].FirstOrDefault() ?? string.Empty,
                headers?[UserEmailHeader].FirstOrDefault() ?? string.Empty);
        }

        public bool CanImportAnalytics()
            => HasAnyRole(AuditEditorRoles) || HasAnyRole(AuditReviewRoles);

        public bool CanReviewAuditContent()
            => HasAnyRole(AuditEditorRoles) || HasAnyRole(AuditReviewRoles);

        public bool CanManageAuditContent()
            => HasAnyRole(AuditEditorRoles);

        public bool CanStartWorkflows()
            => HasAnyRole(AuditEditorRoles) || HasAnyRole(AuditReviewRoles);

        public bool CanRunWorkflowAdminActions()
            => HasAnyRole(AdminRoles) || HasRole("audit_manager") || HasRole("manager");

        public bool CanCompleteAnyWorkflowTask()
            => HasAnyRole(AuditEditorRoles) || HasAnyRole(AuditReviewRoles);

        public bool CanSubmitEvidence()
            => HasAnyRole(ClientContributorRoles) || CanManageAuditContent() || CanReviewAuditContent();

        public bool IsAuditTeamMember()
            => CanManageAuditContent() || CanReviewAuditContent();

        public bool CanAccessManagerReviewOnlyContent()
            => HasAnyRole(AuditReviewRoles) || CanManageDocumentSecurity();

        public bool CanManageDocumentSecurity()
            => HasAnyRole(AdminRoles)
               || HasRole("audit_manager")
               || HasRole("manager")
               || HasRole("partner")
               || HasRole("director");

        public bool HasNormalizedRole(string role)
            => HasRole(role);

        public bool CanCompleteTask(AuditWorkflowTask? task)
        {
            if (task == null)
            {
                return false;
            }

            if (CanCompleteAnyWorkflowTask())
            {
                return true;
            }

            return UserId.HasValue && task.AssigneeUserId.HasValue && task.AssigneeUserId.Value == UserId.Value;
        }

        public bool CanAccessUserScope(int? requestedUserId)
        {
            if (CanRunWorkflowAdminActions())
            {
                return true;
            }

            if (!UserId.HasValue)
            {
                return false;
            }

            return !requestedUserId.HasValue || requestedUserId.Value == UserId.Value;
        }

        public string GetDisplayName(string fallback = "Audit User")
            => !string.IsNullOrWhiteSpace(UserName) ? UserName : fallback;

        private bool HasAnyRole(IEnumerable<string> roles)
            => roles.Any(HasRole);

        private bool HasRole(string role)
            => Role == NormalizeRole(role);

        private static string NormalizeRole(string role)
            => (role ?? string.Empty).Trim().ToLowerInvariant().Replace("-", "_").Replace(" ", "_");

        private static int? ParseNullableInt(string? value)
        {
            return int.TryParse(value, out var parsed) ? parsed : null;
        }
    }
}
