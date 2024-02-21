using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Affine.Engine.Model.Auditing.Assessment
{
    public class Risks_Assessment
    {

        public string KeyRiskAndFactors { get; set; }
        public List<string> RiskLikelihood { get; set; }
        public List<string> RiskImpact { get; set; }
        public List<string> KeyOrSecondary { get; set; }

        public List<string> RiskCategory { get; set; }
    }
}
