using System;

namespace Affine.Engine.Model.Auditing.Assessment
{
    public class RiskAssessment_Assessment
    {
        // Reference Information
        public int ReferenceId { get; set; }
        public string Client { get; set; }
        public string AssessmentPeriod { get; set; }
        public string Assessor { get; set; }
        public string ApprovedBy { get; set; }

        // Process Objectives Assessment
        public string ProcessObjectivesAssessment_BusinessObjectives { get; set; }
        public string ProcessObjectivesAssessment_MainProcess { get; set; }
        public string ProcessObjectivesAssessment_SubProcess { get; set; }

        // Risks Assessment
        public string RisksAssessment_KeyRiskAndFactors { get; set; }
        public string RisksAssessment_RiskLikelihood { get; set; }
        public string RisksAssessment_RiskImpact { get; set; }
        public string RisksAssessment_KeyOrSecondary { get; set; }
        public string RisksAssessment_RiskCategory { get; set; }

        // Controls Assessment
        public string ControlsAssessment_MitigatingControls { get; set; }
        public string ControlsAssessment_Responsibility { get; set; }
        public string ControlsAssessment_DataFrequency { get; set; }
        public string ControlsAssessment_Frequency { get; set; }

        // Outcome Assessment
        public string OutcomeAssessment_Evidence { get; set; }
        public string OutcomeAssessment_Authoriser { get; set; }
        public string OutcomeAssessment_AuditorsRecommendedActionPlan { get; set; }
        public string OutcomeAssessment_ResponsiblePerson { get; set; }
        public DateTime? OutcomeAssessment_AgreedDate { get; set; }
        public string OutcomeAssessment_OutcomeLikelihood { get; set; }
        public string OutcomeAssessment_Impact { get; set; }
    }
}
