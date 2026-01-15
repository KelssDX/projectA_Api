using Affine.Engine.Model.Auditing.HeatMap;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Affine.Engine.Repository.Auditing
{
    public interface IRiskHeatMapRepository
    {
        Task<RiskHeatmapResponse> GetRiskHeatmapAsync(int referenceId, int? departmentId = null);
        Task<AnalyticalReportResponse> GetAnalyticalReportAsync(int referenceId);
    }
}
