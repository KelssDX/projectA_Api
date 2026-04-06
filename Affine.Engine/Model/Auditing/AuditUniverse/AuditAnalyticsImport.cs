using System;
using System.Collections.Generic;

namespace Affine.Engine.Model.Auditing.AuditUniverse
{
    public class AuditAnalyticsImportRequest
    {
        public int? ReferenceId { get; set; }
        public string DatasetType { get; set; } = string.Empty;
        public string? BatchName { get; set; }
        public string? SourceSystem { get; set; }
        public int? ImportedByUserId { get; set; }
        public string? ImportedByName { get; set; }
        public string? Notes { get; set; }
    }

    public class AuditAnalyticsImportBatchSummary
    {
        public int Id { get; set; }
        public int? ReferenceId { get; set; }
        public string DatasetType { get; set; } = string.Empty;
        public string? BatchName { get; set; }
        public string? SourceSystem { get; set; }
        public string? SourceFileName { get; set; }
        public int RowCount { get; set; }
        public int? ImportedByUserId { get; set; }
        public string? ImportedByName { get; set; }
        public DateTime ImportedAt { get; set; }
        public string? Notes { get; set; }
    }

    public class AuditAnalyticsImportResult
    {
        public int BatchId { get; set; }
        public int? ReferenceId { get; set; }
        public string DatasetType { get; set; } = string.Empty;
        public string? SourceFileName { get; set; }
        public int RowCount { get; set; }
        public DateTime ImportedAt { get; set; }
        public string Status { get; set; } = "Imported";
        public List<string> ValidationErrors { get; set; } = new List<string>();
    }
}
