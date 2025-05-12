using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Affine.Engine.Model.Auditing.Assessment
{
    public class RiskAssessmentCreateWrapper
    {
        /// <summary>
        /// List of risk assessments to create.
        /// </summary>
        public List<RiskAssessmentCreateRequest> Assessments { get; set; }
        
        /// <summary>
        /// Reference information for creating a new reference record.
        /// Required when creating assessments with a new reference.
        /// </summary>
        public RiskAssessmentReferenceInput Reference { get; set; }
        
        /// <summary>
        /// Optional ID of an existing reference record to link these assessments to.
        /// If provided and valid, new assessments will be linked to this reference,
        /// and the Reference property will be ignored.
        /// If not provided, a new reference will be created from the Reference property.
        /// </summary>
        public int? ReferenceId { get; set; }
    }
}
