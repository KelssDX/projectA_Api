using Affine.Engine.Model.Auditing.AuditUniverse;
using Affine.Engine.Services;
using Microsoft.AspNetCore.Mvc;

namespace Affine.Auditing.API.Controllers
{
    [ApiController]
    [Route("api/v1/[controller]")]
    public class AuditTrailController : ControllerBase
    {
        private readonly IAuditTrailService _auditTrailService;

        public AuditTrailController(IAuditTrailService auditTrailService)
        {
            _auditTrailService = auditTrailService;
        }

        [HttpPost("RecordEvent")]
        public async Task<IActionResult> RecordEvent([FromBody] CreateAuditTrailEventRequest request)
        {
            if (request == null || string.IsNullOrWhiteSpace(request.Summary))
            {
                return BadRequest("Audit trail summary is required");
            }

            try
            {
                return Ok(await _auditTrailService.RecordEventAsync(request));
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpGet("GetByReference/{referenceId}")]
        public async Task<IActionResult> GetByReference(int referenceId, [FromQuery] int limit = 100)
        {
            try
            {
                return Ok(await _auditTrailService.GetEventsByReferenceAsync(referenceId, limit));
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpGet("GetDashboard/{referenceId}")]
        public async Task<IActionResult> GetDashboard(int referenceId, [FromQuery] int limit = 50)
        {
            try
            {
                return Ok(await _auditTrailService.GetDashboardByReferenceAsync(referenceId, limit));
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }
    }
}
