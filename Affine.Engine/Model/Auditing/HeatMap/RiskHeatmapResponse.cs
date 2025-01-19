using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Affine.Engine.Model.Auditing.HeatMap
{
    public class RiskHeatmapResponse
    {
        public int ReferenceId { get; set; }
        public Dictionary<string, Dictionary<string, int>> HeatmapGrid { get; set; }
    }
}
