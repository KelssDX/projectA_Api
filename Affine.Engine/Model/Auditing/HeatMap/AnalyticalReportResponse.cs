using System;
using System.Collections.Generic;

namespace Affine.Engine.Model.Auditing.HeatMap
{
    public class AnalyticalReportResponse
    {
        public int ReferenceId { get; set; }
        public List<RiskLevelComparison> RiskReduction { get; set; } = new List<RiskLevelComparison>();
        public List<CategoryDatum> CategoryDistribution { get; set; } = new List<CategoryDatum>();
        public List<ControlStat> ControlStats { get; set; } = new List<ControlStat>();
        public List<TopRiskItem> TopResidualRisks { get; set; } = new List<TopRiskItem>();
    }

    public class RiskLevelComparison
    {
        public string Level { get; set; } // e.g., "High", "Critical"
        public int InherentCount { get; set; }
        public int ResidualCount { get; set; }
        public int SortOrder { get; set; }
    }

    public class CategoryDatum
    {
        public string CategoryName { get; set; }
        public int Count { get; set; }
        public double AverageScore { get; set; } // Average Residual Score
    }

    public class ControlStat
    {
        public string StatType { get; set; } // e.g., "With Controls", "Without Controls", "Avg Reduction"
        public string Value { get; set; }
        public string Description { get; set; }
        public string ColorCode { get; set; } // Optional hex color suggestion
    }

    public class TopRiskItem
    {
        public int RiskId { get; set; }
        public string Title { get; set; }
        public int InherentScore { get; set; }
        public int ResidualScore { get; set; }
        public string Category { get; set; }
        public string RiskLevel { get; set; } // Residual Level
    }
}
