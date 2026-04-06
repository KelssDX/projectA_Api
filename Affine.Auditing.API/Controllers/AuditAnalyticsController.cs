using Affine.Engine.Repository.Auditing;
using Microsoft.AspNetCore.Mvc;
using Affine.Engine.Model.Auditing.AuditUniverse;
using Affine.Auditing.API.Security;

namespace Affine.Auditing.API.Controllers
{
    [ApiController]
    [Route("api/v1/[controller]")]
    public class AuditAnalyticsController : ControllerBase
    {
        private readonly IAuditAnalyticsRepository _analyticsRepository;
        private readonly IAuditPlatformRepository _platformRepository;

        public AuditAnalyticsController(IAuditAnalyticsRepository analyticsRepository, IAuditPlatformRepository platformRepository)
        {
            _analyticsRepository = analyticsRepository;
            _platformRepository = platformRepository;
        }

        [HttpGet("GetManagementOverrideAnalytics")]
        public async Task<IActionResult> GetManagementOverrideAnalytics([FromQuery] int? referenceId, [FromQuery] int? year, [FromQuery] int? period)
        {
            try
            {
                return Ok(await _analyticsRepository.GetManagementOverrideAnalyticsAsync(referenceId, year, period));
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpGet("GetJournalExceptionAnalytics")]
        public async Task<IActionResult> GetJournalExceptionAnalytics([FromQuery] int? referenceId, [FromQuery] int? year, [FromQuery] int? period)
        {
            try
            {
                return Ok(await _analyticsRepository.GetJournalExceptionAnalyticsAsync(referenceId, year, period));
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpGet("GetUserPostingConcentration")]
        public async Task<IActionResult> GetUserPostingConcentration([FromQuery] int? referenceId, [FromQuery] int? year, [FromQuery] int? period, [FromQuery] int topUsers = 5)
        {
            try
            {
                return Ok(await _analyticsRepository.GetUserPostingConcentrationAsync(referenceId, year, period, topUsers));
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpGet("GetTrialBalanceMovement")]
        public async Task<IActionResult> GetTrialBalanceMovement([FromQuery] int? referenceId, [FromQuery] int? currentYear, [FromQuery] int? priorYear, [FromQuery] int topAccounts = 10)
        {
            try
            {
                return Ok(await _analyticsRepository.GetTrialBalanceMovementAsync(referenceId, currentYear, priorYear, topAccounts));
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpGet("GetIndustryBenchmarkAnalytics")]
        public async Task<IActionResult> GetIndustryBenchmarkAnalytics([FromQuery] int? referenceId, [FromQuery] int? year, [FromQuery] int topMetrics = 6)
        {
            try
            {
                return Ok(await _analyticsRepository.GetIndustryBenchmarkAnalyticsAsync(referenceId, year, topMetrics));
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpGet("GetReasonabilityForecastAnalytics")]
        public async Task<IActionResult> GetReasonabilityForecastAnalytics([FromQuery] int? referenceId, [FromQuery] int? year, [FromQuery] int topItems = 6)
        {
            try
            {
                return Ok(await _analyticsRepository.GetReasonabilityForecastAnalyticsAsync(referenceId, year, topItems));
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpGet("GetImportBatches")]
        public async Task<IActionResult> GetImportBatches([FromQuery] int? referenceId, [FromQuery] string? datasetType, [FromQuery] int limit = 20)
        {
            try
            {
                return Ok(await _analyticsRepository.GetAnalyticsImportBatchesAsync(referenceId, datasetType, limit));
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpPost("ImportCsv")]
        public async Task<IActionResult> ImportCsv([FromForm] AuditAnalyticsImportRequest request, IFormFile file)
        {
            var userContext = AuditApiUserContext.FromHttpContext(HttpContext);
            if (!userContext.HasUserContext || !userContext.UserId.HasValue)
            {
                return Unauthorized("User context headers are required.");
            }

            if (!userContext.CanImportAnalytics())
            {
                return StatusCode(403, "You do not have permission to import analytics data.");
            }

            if (file == null || file.Length == 0)
                return BadRequest("No file uploaded.");

            if (string.IsNullOrWhiteSpace(request.DatasetType))
                return BadRequest("DatasetType is required.");

            try
            {
                request.ImportedByUserId = userContext.UserId;
                request.ImportedByName = userContext.GetDisplayName(request.ImportedByName ?? "Audit User");
                using var stream = file.OpenReadStream();
                var result = await _analyticsRepository.ImportAnalyticsCsvAsync(stream, request, file.FileName);
                try
                {
                    await _platformRepository.RecordUsageEventAsync(new RecordAuditUsageEventRequest
                    {
                        ModuleName = "analytics",
                        FeatureName = "import_csv",
                        EventName = "completed",
                        ReferenceId = request.ReferenceId,
                        PerformedByUserId = userContext.UserId,
                        PerformedByName = userContext.GetDisplayName(request.ImportedByName ?? "Audit User"),
                        RoleName = userContext.Role,
                        Source = "AuditAnalyticsController",
                        MetadataJson = System.Text.Json.JsonSerializer.Serialize(new
                        {
                            request.DatasetType,
                            result.RowCount,
                            file.FileName
                        })
                    });
                }
                catch (Exception telemetryEx)
                {
                    Console.WriteLine($"Telemetry write failed during analytics import: {telemetryEx.Message}");
                }
                return Ok(result);
            }
            catch (InvalidOperationException ex)
            {
                return BadRequest(ex.Message);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }
    }
}
