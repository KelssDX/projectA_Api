using Microsoft.AspNetCore.Mvc;
using Affine.Engine.Repository.Auditing;
using Affine.Engine.Model.Auditing.HeatMap;

namespace Affine.Auditing.API.Controllers
{
    [ApiController]
    [Route("api/v1/[controller]")]
    public class RiskGraphsController : ControllerBase
    {
        private readonly IRiskHeatMapRepository _riskHeatMapRepository;

        // Use the interface for dependency injection consistency
        public RiskGraphsController(IRiskHeatMapRepository riskHeatMapRepository)
        {
            _riskHeatMapRepository = riskHeatMapRepository;
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
    }
}
