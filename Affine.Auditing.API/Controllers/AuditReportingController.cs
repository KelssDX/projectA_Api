using Affine.Engine.Repository.Auditing;
using Microsoft.AspNetCore.Mvc;
using Affine.Engine.Model.Auditing.AuditUniverse;

namespace Affine.Auditing.API.Controllers
{
    [ApiController]
    [Route("api/v1/[controller]")]
    public class AuditReportingController : ControllerBase
    {
        private readonly IAuditReportingRepository _reportingRepository;

        public AuditReportingController(IAuditReportingRepository reportingRepository)
        {
            _reportingRepository = reportingRepository;
        }

        [HttpGet("GetPowerBIReconciliation")]
        public async Task<IActionResult> GetPowerBIReconciliation([FromQuery] int? referenceId)
        {
            try
            {
                return Ok(await _reportingRepository.GetPowerBIReconciliationAsync(referenceId));
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpGet("GetFinanceAuditWorkspace/{referenceId}")]
        public async Task<IActionResult> GetFinanceAuditWorkspace(int referenceId)
        {
            try
            {
                return Ok(await _reportingRepository.GetFinanceAuditWorkspaceAsync(referenceId));
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

        [HttpPost("GenerateTrialBalanceMappings")]
        public async Task<IActionResult> GenerateTrialBalanceMappings([FromBody] GenerateTrialBalanceMappingsRequest request)
        {
            try
            {
                return Ok(await _reportingRepository.GenerateTrialBalanceMappingsAsync(request));
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

        [HttpPost("SaveTrialBalanceMapping")]
        public async Task<IActionResult> SaveTrialBalanceMapping([FromBody] SaveTrialBalanceMappingRequest request)
        {
            try
            {
                return Ok(await _reportingRepository.SaveTrialBalanceMappingAsync(request));
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

        [HttpPost("SaveMappingProfileFromCurrent")]
        public async Task<IActionResult> SaveMappingProfileFromCurrent([FromBody] SaveAuditMappingProfileRequest request)
        {
            try
            {
                return Ok(await _reportingRepository.SaveMappingProfileFromCurrentAsync(request));
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

        [HttpPost("GenerateDraftFinancialStatements")]
        public async Task<IActionResult> GenerateDraftFinancialStatements([FromBody] GenerateDraftFinancialStatementsRequest request)
        {
            try
            {
                return Ok(await _reportingRepository.GenerateDraftFinancialStatementsAsync(request));
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

        [HttpPost("GenerateSupportQueue")]
        public async Task<IActionResult> GenerateSupportQueue([FromBody] GenerateAuditSupportQueueRequest request)
        {
            try
            {
                return Ok(await _reportingRepository.GenerateSupportQueueAsync(request));
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

        [HttpPut("UpdateSupportRequest")]
        public async Task<IActionResult> UpdateSupportRequest([FromBody] UpdateAuditSupportRequestRequest request)
        {
            try
            {
                return Ok(await _reportingRepository.UpdateSupportRequestAsync(request));
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

        [HttpPost("UpsertFinanceFinalization")]
        public async Task<IActionResult> UpsertFinanceFinalization([FromBody] UpsertAuditFinanceFinalizationRequest request)
        {
            try
            {
                return Ok(await _reportingRepository.UpsertFinanceFinalizationAsync(request));
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
