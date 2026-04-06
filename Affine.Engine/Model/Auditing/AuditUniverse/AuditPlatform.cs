using System;
using System.Collections.Generic;

namespace Affine.Engine.Model.Auditing.AuditUniverse
{
    public class AuditFeatureFlags
    {
        public bool Dashboard { get; set; } = true;
        public bool Assessments { get; set; } = true;
        public bool Heatmap { get; set; } = true;
        public bool Analytics { get; set; } = true;
        public bool AuditUniverse { get; set; } = true;
        public bool Departments { get; set; } = true;
        public bool Projects { get; set; } = true;
        public bool UsersAdmin { get; set; } = true;
        public bool WorkflowInbox { get; set; } = true;
        public bool AnalyticsImport { get; set; } = true;
        public bool PowerBiReporting { get; set; } = true;
    }

    public class PowerBIEnvironmentConfig
    {
        public bool Enabled { get; set; }
        public string Mode { get; set; } = "link";
        public string ReportUrl { get; set; } = string.Empty;
        public string WorkspaceId { get; set; } = string.Empty;
        public string ReportId { get; set; } = string.Empty;
        public string DatasetId { get; set; } = string.Empty;
    }

    public class AuditRetentionPolicy
    {
        public int Id { get; set; }
        public string PolicyName { get; set; } = string.Empty;
        public string EntityType { get; set; } = string.Empty;
        public int RetentionDays { get; set; }
        public string ArchiveAction { get; set; } = string.Empty;
        public bool IsEnabled { get; set; }
        public string Notes { get; set; } = string.Empty;
        public DateTime CreatedAt { get; set; }
        public DateTime UpdatedAt { get; set; }
    }

    public class AuditArchivalEvent
    {
        public int Id { get; set; }
        public int? ReferenceId { get; set; }
        public string EntityType { get; set; } = string.Empty;
        public string EntityId { get; set; } = string.Empty;
        public string ArchiveAction { get; set; } = string.Empty;
        public string Reason { get; set; } = string.Empty;
        public int? RetentionPolicyId { get; set; }
        public int? ArchivedByUserId { get; set; }
        public string ArchivedByName { get; set; } = string.Empty;
        public DateTime ArchivedAt { get; set; }
        public string DetailsJson { get; set; } = string.Empty;
    }

    public class AuditUsageEvent
    {
        public int Id { get; set; }
        public string ModuleName { get; set; } = string.Empty;
        public string FeatureName { get; set; } = string.Empty;
        public string EventName { get; set; } = string.Empty;
        public int? ReferenceId { get; set; }
        public int? PerformedByUserId { get; set; }
        public string PerformedByName { get; set; } = string.Empty;
        public string RoleName { get; set; } = string.Empty;
        public string SessionId { get; set; } = string.Empty;
        public string Source { get; set; } = string.Empty;
        public string MetadataJson { get; set; } = string.Empty;
        public DateTime EventTime { get; set; }
    }

    public class AuditUsageSummary
    {
        public string ModuleName { get; set; } = string.Empty;
        public string FeatureName { get; set; } = string.Empty;
        public string EventName { get; set; } = string.Empty;
        public int EventCount { get; set; }
        public DateTime? LastEventTime { get; set; }
    }

    public class AuditPlatformConfiguration
    {
        public AuditFeatureFlags FeatureFlags { get; set; } = new AuditFeatureFlags();
        public PowerBIEnvironmentConfig PowerBI { get; set; } = new PowerBIEnvironmentConfig();
        public bool TelemetryEnabled { get; set; } = true;
        public int TelemetryRetentionDays { get; set; } = 365;
        public List<AuditRetentionPolicy> RetentionPolicies { get; set; } = new List<AuditRetentionPolicy>();
    }

    public class ArchiveAssessmentRequest
    {
        public int ReferenceId { get; set; }
        public int? ArchivedByUserId { get; set; }
        public string ArchivedByName { get; set; } = string.Empty;
        public string Reason { get; set; } = string.Empty;
    }

    public class ArchiveAssessmentResult
    {
        public bool Success { get; set; }
        public int ReferenceId { get; set; }
        public bool AlreadyArchived { get; set; }
        public DateTime? ArchivedAt { get; set; }
        public AuditArchivalEvent? Event { get; set; }
        public string Message { get; set; } = string.Empty;
    }

    public class RecordAuditUsageEventRequest
    {
        public string ModuleName { get; set; } = string.Empty;
        public string FeatureName { get; set; } = string.Empty;
        public string EventName { get; set; } = string.Empty;
        public int? ReferenceId { get; set; }
        public int? PerformedByUserId { get; set; }
        public string PerformedByName { get; set; } = string.Empty;
        public string RoleName { get; set; } = string.Empty;
        public string SessionId { get; set; } = string.Empty;
        public string Source { get; set; } = string.Empty;
        public string MetadataJson { get; set; } = string.Empty;
    }
}
