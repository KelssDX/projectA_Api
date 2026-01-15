using Affine.Engine.Model.Auditing.Operational;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace Affine.Engine.Repository.Analytics
{
    public interface IAnalyticsRepository
    {
        // Risk Profile Dashboard
        Task<Dictionary<string, object>> GetRiskProfileAsync(int? referenceId = null);
        
        // Market Analytics
        Task<Dictionary<string, object>> GetMarketVolatilityAsync(string symbol, int days = 365);
        
        // Operational Analytics
        Task<IEnumerable<OperationalRiskAssessmentDto>> GetTopRisksAsync(int count = 10);
        Task<dynamic> GetControlCoverageAsync();
        
        // Advanced Correlations
        Task<Dictionary<string, double>> GetCorrelationMatrixAsync();
    }
}
