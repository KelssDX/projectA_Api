using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Affine.Engine.Model.Auditing.Assessment
{
    public class RiskAssessment_Assessment
    {
        public ProcessObjectives_Assessment ProcessObjectivesAssessment { get; set; }
        public Risks_Assessment RisksAssessment { get; set; }   
        public Controls_Assessment Controls_Assessment { get; set; }
        public  Outcome_Assessment OutcomeAssessment { get; set; }  
    }

    public class RiskAssessmentCreateRequest
    {
        public int Id { get; set; }
        public int RiskAssessment_RefID { get; set; }
        public string BusinessObjectives { get; set; }
        public string MainProcess { get; set; }
        public string SubProcess { get; set; }
        public string KeyRiskAndFactors { get; set; }
        public string MitigatingControls { get; set; }
        public string Responsibility { get; set; }
        public string Authoriser { get; set; }
        public string AuditorsRecommendedActionPlan { get; set; }
        public string ResponsiblePerson { get; set; }
        public DateTime? AgreedDate { get; set; }
        public int? RiskLikelihoodId { get; set; }
        public int? RiskImpactId { get; set; }
        public int? KeySecondaryId { get; set; }
        public int? RiskCategoryId { get; set; }
        public int? DataFrequencyId { get; set; }
        public int? FrequencyId { get; set; }
        public int? EvidenceId { get; set; }
        public int? OutcomeLikelihoodId { get; set; }
        public int? ImpactId { get; set; }
    }
}
