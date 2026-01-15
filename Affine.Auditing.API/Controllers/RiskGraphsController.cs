using Microsoft.AspNetCore.Mvc;
using Affine.Engine.Repository.Auditing;
using Affine.Engine.Model.Auditing.HeatMap;
using Affine.Engine.Repository.Analytics;

namespace Affine.Auditing.API.Controllers
{
    [ApiController]
    [Route("api/v1/[controller]")]
    public class RiskGraphsController : ControllerBase
    {
        private readonly IRiskHeatMapRepository _riskHeatMapRepository;
        private readonly IAnalyticsRepository _analyticsRepository;

        // Use the interface for dependency injection consistency
        public RiskGraphsController(IRiskHeatMapRepository riskHeatMapRepository, IAnalyticsRepository analyticsRepository)
        {
            _riskHeatMapRepository = riskHeatMapRepository;
            _analyticsRepository = analyticsRepository;
        }

        [HttpGet]
        [Route("GetHeatmap")]
        public async Task<IActionResult> GetHeatmap(int referenceId, int? departmentId = null)
        {
            var heatmap = await _riskHeatMapRepository.GetRiskHeatmapAsync(referenceId, departmentId);

            if (heatmap == null)
            {
                return NotFound("Heatmap not found");
            }

            return Ok(heatmap);
        }
        [HttpGet]
        [Route("GetAnalyticalReport")]
        public async Task<IActionResult> GetAnalyticalReport(int referenceId)
        {
            if (referenceId <= 0) return BadRequest("Invalid Reference ID");

            try
            {
                var baseReport = await _riskHeatMapRepository.GetAnalyticalReportAsync(referenceId);
                var riskProfile = await _analyticsRepository.GetRiskProfileAsync(referenceId);
                var controlStats = await _analyticsRepository.GetControlCoverageAsync();

                var result = new
                {
                    baseReport,
                    riskProfile,
                    controlStats = new[] { controlStats }
                };

                return Ok(result);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpGet("GetMarketInsights")]
        public async Task<IActionResult> GetMarketInsights(string symbol = "IBM")
        {
            var data = await _analyticsRepository.GetMarketVolatilityAsync(symbol);
            return Ok(data);
        }

        [HttpGet("GetTopRisks")]
        public async Task<IActionResult> GetTopRisks(int count = 10)
        {
            var data = await _analyticsRepository.GetTopRisksAsync(count);
            return Ok(data);
        }

        [HttpGet("GetCorrelationMatrix")]
        public async Task<IActionResult> GetCorrelationMatrix()
        {
            var data = await _analyticsRepository.GetCorrelationMatrixAsync();
            return Ok(data);
        }
    }
}
