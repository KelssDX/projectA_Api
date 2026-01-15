using System;

namespace Affine.Engine.Model.Auditing.Operational
{
    public class OperationalRiskAssessmentDto
    {
        public int Id { get; set; }
        public int ReferenceId { get; set; }
        public string MainProcess { get; set; }
        public string SubProcess { get; set; }
        public string Source { get; set; }
        public string LossFrequency { get; set; }
        public int LossEventCount { get; set; }
        public decimal Probability { get; set; }
        public decimal LossAmount { get; set; }
        public string RiskMeasurement { get; set; }
        public decimal VaR { get; set; } // Operational VAR
        public decimal SingleVaR { get; set; } // Single VAR (possible loss)
        public decimal CumulativeVaR { get; set; } // Severity
    }
}
