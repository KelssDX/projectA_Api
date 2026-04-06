using Affine.Engine.Model.Auditing.AuditUniverse;
using Affine.Engine.Repository.Auditing;
using Microsoft.AspNetCore.Mvc;

namespace Affine.Auditing.API.Controllers
{
    [ApiController]
    [Route("api/v1/[controller]")]
    public class AuditMaterialityController : ControllerBase
    {
        private readonly IAuditMaterialityRepository _materialityRepository;

        public AuditMaterialityController(IAuditMaterialityRepository materialityRepository)
        {
            _materialityRepository = materialityRepository;
        }

        [HttpGet("GetWorkspace/{referenceId}")]
        public async Task<IActionResult> GetWorkspace(int referenceId)
        {
            try
            {
                return Ok(await _materialityRepository.GetWorkspaceAsync(referenceId));
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpPost("GenerateCandidates")]
        public async Task<IActionResult> GenerateCandidates([FromBody] GenerateAuditMaterialityCandidatesRequest request)
        {
            if (request.ReferenceId <= 0)
            {
                return BadRequest("Reference ID is required.");
            }

            try
            {
                return Ok(await _materialityRepository.GenerateCandidatesAsync(request));
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

        [HttpGet("GetApplicationSummary/{referenceId}")]
        public async Task<IActionResult> GetApplicationSummary(int referenceId)
        {
            try
            {
                return Ok(await _materialityRepository.GetApplicationSummaryAsync(referenceId));
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

        [HttpGet("GetCalculationsByReference/{referenceId}")]
        public async Task<IActionResult> GetCalculationsByReference(int referenceId)
        {
            try
            {
                return Ok(await _materialityRepository.GetCalculationsByReferenceAsync(referenceId));
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpPost("CreateCalculation")]
        public async Task<IActionResult> CreateCalculation([FromBody] CreateAuditMaterialityCalculationRequest request)
        {
            if (request.ReferenceId <= 0)
            {
                return BadRequest("Reference ID is required.");
            }

            try
            {
                return Ok(await _materialityRepository.CreateCalculationAsync(request));
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

        [HttpPost("SetActiveCalculation")]
        public async Task<IActionResult> SetActiveCalculation([FromBody] SetActiveAuditMaterialityRequest request)
        {
            if (request.ReferenceId <= 0 || request.CalculationId <= 0)
            {
                return BadRequest("Reference ID and calculation ID are required.");
            }

            try
            {
                return Ok(await _materialityRepository.SetActiveCalculationAsync(request));
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

        [HttpPost("CreateScopeLink")]
        public async Task<IActionResult> CreateScopeLink([FromBody] UpsertAuditMaterialityScopeLinkRequest request)
        {
            if (request.ReferenceId <= 0)
            {
                return BadRequest("Reference ID is required.");
            }

            try
            {
                return Ok(await _materialityRepository.CreateScopeLinkAsync(request));
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

        [HttpPut("UpdateScopeLink/{id}")]
        public async Task<IActionResult> UpdateScopeLink(long id, [FromBody] UpsertAuditMaterialityScopeLinkRequest request)
        {
            if (id <= 0 || request.ReferenceId <= 0)
            {
                return BadRequest("Scope link ID and reference ID are required.");
            }

            request.Id = id;

            try
            {
                return Ok(await _materialityRepository.UpdateScopeLinkAsync(request));
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

        [HttpDelete("DeleteScopeLink/{id}")]
        public async Task<IActionResult> DeleteScopeLink(long id)
        {
            try
            {
                return Ok(new { deleted = await _materialityRepository.DeleteScopeLinkAsync(id), id });
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpPost("CreateMisstatement")]
        public async Task<IActionResult> CreateMisstatement([FromBody] UpsertAuditMisstatementRequest request)
        {
            if (request.ReferenceId <= 0)
            {
                return BadRequest("Reference ID is required.");
            }

            try
            {
                return Ok(await _materialityRepository.CreateMisstatementAsync(request));
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

        [HttpPut("UpdateMisstatement/{id}")]
        public async Task<IActionResult> UpdateMisstatement(long id, [FromBody] UpsertAuditMisstatementRequest request)
        {
            if (id <= 0 || request.ReferenceId <= 0)
            {
                return BadRequest("Misstatement ID and reference ID are required.");
            }

            request.Id = id;

            try
            {
                return Ok(await _materialityRepository.UpdateMisstatementAsync(request));
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

        [HttpDelete("DeleteMisstatement/{id}")]
        public async Task<IActionResult> DeleteMisstatement(long id)
        {
            try
            {
                return Ok(new { deleted = await _materialityRepository.DeleteMisstatementAsync(id), id });
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }
    }
}
