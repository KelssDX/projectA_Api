using System;
using System.Collections.Generic;

namespace Affine.Engine.Model.Auditing.AuditUniverse
{
    /// <summary>
    /// Represents audit coverage metrics for a universe node
    /// </summary>
    public class AuditCoverage
    {
        public int Id { get; set; }
        public int AuditUniverseId { get; set; }
        public int PeriodYear { get; set; }
        public int? PeriodQuarter { get; set; }
        public int PlannedAudits { get; set; }
        public int CompletedAudits { get; set; }
        public decimal CoveragePercentage { get; set; } // Auto-calculated in DB
        public int TotalFindings { get; set; }
        public int CriticalFindings { get; set; }
        public int HighFindings { get; set; }
        public string Notes { get; set; }
        public DateTime? CreatedAt { get; set; }
        public DateTime? UpdatedAt { get; set; }

        // Navigation
        public string AuditUniverseName { get; set; }
        public string AuditUniverseCode { get; set; }
    }

    /// <summary>
    /// Response for audit coverage map visualization
    /// </summary>
    public class AuditCoverageMapResponse
    {
        public int Year { get; set; }
        public int? Quarter { get; set; }
        public List<AuditCoverageMapNode> Nodes { get; set; } = new List<AuditCoverageMapNode>();
        public AuditCoverageMapSummary Summary { get; set; } = new AuditCoverageMapSummary();
    }

    /// <summary>
    /// Node in the audit coverage map (for treemap/sunburst visualization)
    /// </summary>
    public class AuditCoverageMapNode
    {
        public int Id { get; set; }
        public string Name { get; set; }
        public string Code { get; set; }
        public int? ParentId { get; set; }
        public int Level { get; set; }
        public string RiskRating { get; set; }

        // Coverage metrics
        public int PlannedAudits { get; set; }
        public int CompletedAudits { get; set; }
        public decimal CoveragePercentage { get; set; }

        // Findings metrics
        public int TotalFindings { get; set; }
        public int OpenFindings { get; set; }
        public int CriticalFindings { get; set; }
        public int HighFindings { get; set; }

        // Visual properties
        public string CoverageColor { get; set; } // Based on percentage (red/yellow/green)
        public int Size { get; set; } // For treemap sizing

        // Children for hierarchical visualization
        public List<AuditCoverageMapNode> Children { get; set; } = new List<AuditCoverageMapNode>();
    }

    public class AuditCoverageMapSummary
    {
        public int TotalNodes { get; set; }
        public int NodesAudited { get; set; }
        public decimal OverallCoverage { get; set; }
        public int TotalPlannedAudits { get; set; }
        public int TotalCompletedAudits { get; set; }
        public int NodesBelowTarget { get; set; } // Nodes with coverage < 80%
        public int NodesAtRisk { get; set; } // Nodes with coverage < 50%
    }

    /// <summary>
    /// Risk trend history snapshot
    /// </summary>
    public class RiskTrendSnapshot
    {
        public int Id { get; set; }
        public int? ReferenceId { get; set; }
        public int? AuditUniverseId { get; set; }
        public DateTime SnapshotDate { get; set; }
        public string PeriodType { get; set; } // daily, weekly, monthly, quarterly
        public int CriticalCount { get; set; }
        public int HighCount { get; set; }
        public int MediumCount { get; set; }
        public int LowCount { get; set; }
        public int VeryLowCount { get; set; }
        public decimal TotalInherentScore { get; set; }
        public decimal TotalResidualScore { get; set; }
        public int AssessmentCount { get; set; }
        public DateTime? CreatedAt { get; set; }
    }

    /// <summary>
    /// Response for risk trend analysis
    /// </summary>
    public class RiskTrendResponse
    {
        public int? ReferenceId { get; set; }
        public int? AuditUniverseId { get; set; }
        public string PeriodType { get; set; }
        public List<RiskTrendDataPoint> DataPoints { get; set; } = new List<RiskTrendDataPoint>();
        public RiskTrendSummary Summary { get; set; } = new RiskTrendSummary();
    }

    public class RiskTrendDataPoint
    {
        public DateTime Date { get; set; }
        public string PeriodLabel { get; set; } // e.g., "Jan 2026", "Q1 2026"
        public int CriticalCount { get; set; }
        public int HighCount { get; set; }
        public int MediumCount { get; set; }
        public int LowCount { get; set; }
        public int TotalCount { get; set; }
        public decimal AverageResidualScore { get; set; }
    }

    public class RiskTrendSummary
    {
        public int CurrentTotal { get; set; }
        public int PreviousTotal { get; set; }
        public int ChangeCount { get; set; }
        public decimal ChangePercentage { get; set; }
        public string TrendDirection { get; set; } // "improving", "worsening", "stable"
        public int CriticalChange { get; set; }
        public int HighChange { get; set; }
    }

    /// <summary>
    /// Response for risk velocity meter
    /// </summary>
    public class RiskVelocityResponse
    {
        public int? ReferenceId { get; set; }
        public int? AuditUniverseId { get; set; }
        public DateTime PeriodStart { get; set; }
        public DateTime PeriodEnd { get; set; }

        // Velocity metrics
        public int RisksAdded { get; set; }
        public int RisksClosed { get; set; }
        public int RisksEscalated { get; set; } // Moved to higher severity
        public int RisksDeescalated { get; set; } // Moved to lower severity
        public int NetChange { get; set; }

        // Velocity score (-100 to +100, negative is improving)
        public int VelocityScore { get; set; }
        public string VelocityDirection { get; set; } // "accelerating", "decelerating", "stable"
        public string TrendIndicator { get; set; } // "improving", "worsening", "stable"

        // Previous period comparison
        public int PreviousPeriodNetChange { get; set; }
        public string ComparisonText { get; set; } // e.g., "Better than last period"
    }
}
