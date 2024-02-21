using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Affine.Engine.Model.Auditing.Assessment
{
    public class Outcome_Assessment
    {
        public List<string> Evidence { get; set; }
        public string Authoriser { get; set; }
        public string AuditorsRecommendedActionPlan { get; set; }   
        public string ResponsiblePerson  { get; set; }
        public DateTime? AgreedDate { get; set; }   
        public List<string> OutcomeLikelihood { get; set; }
        public List<string> Impact { get; set; }
    }
}
