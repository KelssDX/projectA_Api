using System;

namespace Affine.Engine.Model.Auditing
{
    public class Department
    {
        public int Id { get; set; }
        public string Name { get; set; }
        public string Head { get; set; }
        public int? RiskLevelId { get; set; }
        public int? Assessments { get; set; }
        public DateTime? CreatedAt { get; set; }
        public DateTime? UpdatedAt { get; set; }
    }
}


