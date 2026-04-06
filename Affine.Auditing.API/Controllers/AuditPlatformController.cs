using Affine.Auditing.API.Security;
using Affine.Engine.Model.Auditing.AuditUniverse;
using Affine.Engine.Repository.Auditing;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Configuration;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace Affine.Auditing.API.Controllers
{
    [ApiController]
    [Route("api/v1/[controller]")]
    public class AuditPlatformController : ControllerBase
    {
        private readonly IConfiguration _configuration;
        private readonly IAuditPlatformRepository _platformRepository;

        public AuditPlatformController(IConfiguration configuration, IAuditPlatformRepository platformRepository)
        {
            _configuration = configuration;
            _platformRepository = platformRepository;
        }

        [HttpGet("GetClientConfiguration")]
        public async Task<IActionResult> GetClientConfiguration()
        {
            try
            {
                var featureFlags = _configuration.GetSection("FeatureFlags").Get<AuditFeatureFlags>() ?? new AuditFeatureFlags();
                var powerBi = _configuration.GetSection("PowerBI").Get<PowerBIEnvironmentConfig>() ?? new PowerBIEnvironmentConfig();
                var telemetryEnabled = _configuration.GetValue("Telemetry:Enabled", true);
                var telemetryRetentionDays = _configuration.GetValue("Telemetry:RetentionDays", 365);
                var retentionPolicies = await _platformRepository.GetRetentionPoliciesAsync();

                return Ok(new AuditPlatformConfiguration
                {
                    FeatureFlags = featureFlags,
                    PowerBI = powerBi,
                    TelemetryEnabled = telemetryEnabled,
                    TelemetryRetentionDays = telemetryRetentionDays,
                    RetentionPolicies = retentionPolicies
                });
            }
            catch (System.Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpGet("GetRetentionPolicies")]
        public async Task<IActionResult> GetRetentionPolicies()
        {
            var userContext = AuditApiUserContext.FromHttpContext(HttpContext);
            if (!userContext.HasUserContext || !userContext.UserId.HasValue)
            {
                return Unauthorized("User context headers are required.");
            }

            if (!userContext.CanStartWorkflows())
            {
                return StatusCode(403, "You do not have permission to view retention policies.");
            }

            try
            {
                return Ok(await _platformRepository.GetRetentionPoliciesAsync());
            }
            catch (System.Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpGet("GetUsageSummary")]
        public async Task<IActionResult> GetUsageSummary([FromQuery] int days = 30)
        {
            var userContext = AuditApiUserContext.FromHttpContext(HttpContext);
            if (!userContext.HasUserContext || !userContext.UserId.HasValue)
            {
                return Unauthorized("User context headers are required.");
            }

            if (!userContext.CanRunWorkflowAdminActions())
            {
                return StatusCode(403, "You do not have permission to view platform telemetry.");
            }

            try
            {
                return Ok(await _platformRepository.GetUsageSummaryAsync(days));
            }
            catch (System.Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpPost("RecordUsageEvent")]
        public async Task<IActionResult> RecordUsageEvent([FromBody] RecordAuditUsageEventRequest request)
        {
            var userContext = AuditApiUserContext.FromHttpContext(HttpContext);
            if (!userContext.HasUserContext || !userContext.UserId.HasValue)
            {
                return Unauthorized("User context headers are required.");
            }

            if (request == null || string.IsNullOrWhiteSpace(request.ModuleName) || string.IsNullOrWhiteSpace(request.EventName))
            {
                return BadRequest("ModuleName and EventName are required.");
            }

            try
            {
                request.PerformedByUserId = userContext.UserId;
                request.PerformedByName = userContext.GetDisplayName(request.PerformedByName ?? "Audit User");
                request.RoleName = userContext.Role;
                return Ok(await _platformRepository.RecordUsageEventAsync(request));
            }
            catch (System.Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpPost("ArchiveAssessment/{referenceId}")]
        public async Task<IActionResult> ArchiveAssessment(int referenceId, [FromBody] ArchiveAssessmentRequest request)
        {
            var userContext = AuditApiUserContext.FromHttpContext(HttpContext);
            if (!userContext.HasUserContext || !userContext.UserId.HasValue)
            {
                return Unauthorized("User context headers are required.");
            }

            if (!userContext.CanStartWorkflows())
            {
                return StatusCode(403, "You do not have permission to archive audit assessments.");
            }

            if (referenceId <= 0)
            {
                return BadRequest("Reference ID is required.");
            }

            request ??= new ArchiveAssessmentRequest();
            request.ReferenceId = referenceId;
            request.ArchivedByUserId = userContext.UserId;
            request.ArchivedByName = userContext.GetDisplayName(request.ArchivedByName ?? "Audit User");

            try
            {
                var result = await _platformRepository.ArchiveAssessmentAsync(request);
                if (!result.Success)
                {
                    return NotFound(result);
                }

                return Ok(result);
            }
            catch (System.Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }
    }
}
