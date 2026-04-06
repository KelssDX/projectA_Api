using Affine.Engine.Model.Auditing.AuditUniverse;
using Affine.Engine.Repository.Auditing;
using System;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace Affine.Engine.Services
{
    public interface IAuditTrailService
    {
        Task<AuditTrailEvent> RecordEventAsync(CreateAuditTrailEventRequest request);
        Task<List<AuditTrailEvent>> GetEventsByReferenceAsync(int referenceId, int limit = 100);
        Task<AuditTrailDashboard> GetDashboardByReferenceAsync(int referenceId, int limit = 50);
    }

    public class AuditTrailService : IAuditTrailService
    {
        private readonly IAuditTrailRepository _auditTrailRepository;

        public AuditTrailService(IAuditTrailRepository auditTrailRepository)
        {
            _auditTrailRepository = auditTrailRepository ?? throw new ArgumentNullException(nameof(auditTrailRepository));
        }

        public async Task<AuditTrailEvent> RecordEventAsync(CreateAuditTrailEventRequest request)
        {
            if (request == null)
                throw new ArgumentNullException(nameof(request));
            if (string.IsNullOrWhiteSpace(request.Summary))
                throw new ArgumentException("Audit trail summary is required", nameof(request));

            request.Category = string.IsNullOrWhiteSpace(request.Category) ? "Business" : request.Category.Trim();
            request.Action = string.IsNullOrWhiteSpace(request.Action) ? "Updated" : request.Action.Trim();
            request.EntityType = string.IsNullOrWhiteSpace(request.EntityType) ? "Assessment" : request.EntityType.Trim();
            request.PerformedByName = string.IsNullOrWhiteSpace(request.PerformedByName) ? "System" : request.PerformedByName.Trim();
            request.Source = string.IsNullOrWhiteSpace(request.Source) ? "Application" : request.Source.Trim();
            request.Icon = string.IsNullOrWhiteSpace(request.Icon) ? InferIcon(request) : request.Icon.Trim();
            request.Color = string.IsNullOrWhiteSpace(request.Color) ? InferColor(request) : request.Color.Trim();

            return await _auditTrailRepository.CreateEventAsync(request);
        }

        public Task<List<AuditTrailEvent>> GetEventsByReferenceAsync(int referenceId, int limit = 100)
            => _auditTrailRepository.GetEventsByReferenceAsync(referenceId, limit);

        public Task<AuditTrailDashboard> GetDashboardByReferenceAsync(int referenceId, int limit = 50)
            => _auditTrailRepository.GetDashboardByReferenceAsync(referenceId, limit);

        private static string InferIcon(CreateAuditTrailEventRequest request)
        {
            var category = (request.Category ?? string.Empty).Trim().ToLowerInvariant();
            var action = (request.Action ?? string.Empty).Trim().ToLowerInvariant();

            if (category.Contains("workflow"))
                return "ROUTE";
            if (category.Contains("document"))
                return action.Contains("view") || action.Contains("download") ? "VISIBILITY" : "FOLDER_OPEN";
            if (action.Contains("delete"))
                return "DELETE";
            if (action.Contains("create") || action.Contains("add"))
                return "ADD_CIRCLE";
            if (action.Contains("approve") || action.Contains("complete") || action.Contains("sign"))
                return "CHECK_CIRCLE";
            if (action.Contains("comment"))
                return "COMMENT";
            return "INFO";
        }

        private static string InferColor(CreateAuditTrailEventRequest request)
        {
            var category = (request.Category ?? string.Empty).Trim().ToLowerInvariant();
            var action = (request.Action ?? string.Empty).Trim().ToLowerInvariant();

            if (action.Contains("delete"))
                return "#dc2626";
            if (action.Contains("approve") || action.Contains("complete") || action.Contains("sign"))
                return "#16a34a";
            if (category.Contains("workflow"))
                return "#2563eb";
            if (category.Contains("document"))
                return "#0f766e";
            if (action.Contains("comment"))
                return "#3498db";
            return "#2563eb";
        }
    }
}
