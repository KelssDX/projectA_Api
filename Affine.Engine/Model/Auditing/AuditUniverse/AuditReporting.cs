using System;
using System.Collections.Generic;

namespace Affine.Engine.Model.Auditing.AuditUniverse
{
    public class PowerBIReconciliationMetric
    {
        public string MetricKey { get; set; }
        public string MetricName { get; set; }
        public string Category { get; set; }
        public decimal NativeValue { get; set; }
        public decimal ReportingValue { get; set; }
        public decimal Variance { get; set; }
        public bool IsMatched { get; set; }
    }

    public class PowerBIReconciliationResponse
    {
        public int? ReferenceId { get; set; }
        public string DataMartStatus { get; set; }
        public DateTime GeneratedAt { get; set; }
        public int MatchedMetrics { get; set; }
        public int MismatchedMetrics { get; set; }
        public List<PowerBIReconciliationMetric> Metrics { get; set; } = new List<PowerBIReconciliationMetric>();
    }
}
