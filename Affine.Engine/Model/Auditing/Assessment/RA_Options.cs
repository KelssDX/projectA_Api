using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

 namespace Affine.Engine.Model.Auditing.Assessment
    {
        public class RiskLikelihood
        {
            public int Id { get; set; }
            public string Description { get; set; }
            public int Position { get; set; }
        }

        public class Impact
        {
            public int Id { get; set; }
            public string Description { get; set; }
            public int Position { get; set; }
        }

        public class KeySecondary
        {
            public int Id { get; set; }
            public string Description { get; set; }
            public int Position { get; set; }
        }

        public class RiskCategory
        {
            public int Id { get; set; }
            public string Description { get; set; }
            public int Position { get; set; }
        }

        public class DataFrequency
        {
            public int Id { get; set; }
            public string Description { get; set; }
            public int Position { get; set; }
        }

        public class OutcomeLikelihood
        {
            public int Id { get; set; }
            public string Description { get; set; }
            public int Position { get; set; }
        }

        public class Evidence
        {
            public int Id { get; set; }
            public string Description { get; set; }
            public int Position { get; set; }
        
    }

}
