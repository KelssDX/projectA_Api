using System;
using System.Collections.Generic;

namespace Affine.Engine.Model.Auditing.Analytics
{
    /// <summary>
    /// Context object for drill-down navigation in analytics
    /// </summary>
    public class DrillDownContext
    {
        public string ChartType { get; set; } // e.g., "heatmap", "category", "severity"
        public string SourceWidget { get; set; }
        public int? ReferenceId { get; set; }
        public int? AuditUniverseId { get; set; }
        public int? DepartmentId { get; set; }

        // Filter context
        public string RiskLevel { get; set; } // Critical, High, Medium, Low
        public string Category { get; set; }
        public int? Likelihood { get; set; }
        public int? Impact { get; set; }
        public string Status { get; set; }
        public DateTime? DateFrom { get; set; }
        public DateTime? DateTo { get; set; }

        // Breadcrumb trail
        public List<BreadcrumbItem> Breadcrumbs { get; set; } = new List<BreadcrumbItem>();
    }

    /// <summary>
    /// Breadcrumb item for navigation trail
    /// </summary>
    public class BreadcrumbItem
    {
        public string Label { get; set; }
        public string NavigationType { get; set; } // "dashboard", "widget", "filter", "detail"
        public DrillDownContext Context { get; set; }
    }

    /// <summary>
    /// Request for drill-down data
    /// </summary>
    public class DrillDownRequest
    {
        public string ChartType { get; set; }
        public int? ReferenceId { get; set; }
        public int? AuditUniverseId { get; set; }
        public string FilterJson { get; set; } // JSON string of filter parameters
    }

    /// <summary>
    /// Response for drill-down data
    /// </summary>
    public class DrillDownResponse
    {
        public DrillDownContext Context { get; set; }
        public string DataType { get; set; } // "assessments", "findings", "recommendations"
        public List<DrillDownDataItem> Items { get; set; } = new List<DrillDownDataItem>();
        public int TotalCount { get; set; }
        public bool HasMore { get; set; }
        public DrillDownSummary Summary { get; set; }
    }

    /// <summary>
    /// Generic drill-down data item
    /// </summary>
    public class DrillDownDataItem
    {
        public int Id { get; set; }
        public string Title { get; set; }
        public string Description { get; set; }
        public string Type { get; set; } // "assessment", "finding", "recommendation"
        public string Status { get; set; }
        public string StatusColor { get; set; }
        public string Severity { get; set; }
        public string SeverityColor { get; set; }
        public string Category { get; set; }
        public int? Score { get; set; }
        public DateTime? Date { get; set; }
        public string AssignedTo { get; set; }
        public Dictionary<string, object> AdditionalData { get; set; } = new Dictionary<string, object>();
    }

    /// <summary>
    /// Summary statistics for drill-down view
    /// </summary>
    public class DrillDownSummary
    {
        public int TotalItems { get; set; }
        public int CriticalCount { get; set; }
        public int HighCount { get; set; }
        public int MediumCount { get; set; }
        public int LowCount { get; set; }
        public decimal AverageScore { get; set; }
        public Dictionary<string, int> StatusBreakdown { get; set; } = new Dictionary<string, int>();
    }

    /// <summary>
    /// Department comparison data for analytics
    /// </summary>
    public class DepartmentComparisonResponse
    {
        public int? ReferenceId { get; set; }
        public List<DepartmentComparisonItem> Departments { get; set; } = new List<DepartmentComparisonItem>();
        public DepartmentComparisonSummary Summary { get; set; }
    }

    public class DepartmentComparisonItem
    {
        public int DepartmentId { get; set; }
        public string DepartmentName { get; set; }
        public string DepartmentHead { get; set; }

        // Risk metrics
        public int TotalRisks { get; set; }
        public int CriticalRisks { get; set; }
        public int HighRisks { get; set; }
        public int MediumRisks { get; set; }
        public int LowRisks { get; set; }
        public decimal AverageInherentScore { get; set; }
        public decimal AverageResidualScore { get; set; }
        public decimal RiskReduction { get; set; } // Percentage

        // Control metrics
        public int TotalControls { get; set; }
        public int EffectiveControls { get; set; }
        public decimal ControlEffectiveness { get; set; }

        // Findings metrics
        public int OpenFindings { get; set; }
        public int OverdueFindings { get; set; }

        // Radar chart dimensions (normalized 0-100)
        public int RiskScore { get; set; }
        public int ControlScore { get; set; }
        public int ComplianceScore { get; set; }
        public int FindingsScore { get; set; }
        public int CoverageScore { get; set; }
    }

    public class DepartmentComparisonSummary
    {
        public int TotalDepartments { get; set; }
        public string HighestRiskDepartment { get; set; }
        public string LowestRiskDepartment { get; set; }
        public decimal AverageRiskScore { get; set; }
        public decimal AverageControlEffectiveness { get; set; }
    }

    /// <summary>
    /// Control effectiveness data for analytics
    /// </summary>
    public class ControlEffectivenessResponse
    {
        public int? ReferenceId { get; set; }
        public int? AuditUniverseId { get; set; }

        // Pie chart data
        public List<ControlEffectivenessCategory> Categories { get; set; } = new List<ControlEffectivenessCategory>();

        // Timeline data
        public List<ControlTestingTimelineItem> Timeline { get; set; } = new List<ControlTestingTimelineItem>();

        // Gap analysis
        public List<ControlGapItem> Gaps { get; set; } = new List<ControlGapItem>();

        // Summary
        public ControlEffectivenessSummary Summary { get; set; }
    }

    public class ControlEffectivenessCategory
    {
        public string Category { get; set; } // "Effective", "Partially Effective", "Not Effective", "Not Tested"
        public int Count { get; set; }
        public decimal Percentage { get; set; }
        public string Color { get; set; }
    }

    public class ControlTestingTimelineItem
    {
        public DateTime Date { get; set; }
        public string PeriodLabel { get; set; }
        public int ControlsTested { get; set; }
        public int Effective { get; set; }
        public int PartiallyEffective { get; set; }
        public int NotEffective { get; set; }
    }

    public class ControlGapItem
    {
        public int ControlId { get; set; }
        public string ControlName { get; set; }
        public string RiskArea { get; set; }
        public string GapDescription { get; set; }
        public string GapSeverity { get; set; }
        public string RecommendedAction { get; set; }
    }

    public class ControlEffectivenessSummary
    {
        public int TotalControls { get; set; }
        public int TestedControls { get; set; }
        public decimal TestingCoverage { get; set; }
        public decimal OverallEffectiveness { get; set; }
        public int ControlGaps { get; set; }
        public DateTime? LastTestDate { get; set; }
    }
}
