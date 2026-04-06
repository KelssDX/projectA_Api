using Affine.Engine.Model.Auditing.AuditUniverse;
using Affine.Engine.Repository.Auditing;
using Microsoft.AspNetCore.Mvc;

namespace Affine.Auditing.API.Controllers
{
    [ApiController]
    [Route("api/v1/[controller]")]
    public class AuditExecutionController : ControllerBase
    {
        private readonly IAuditExecutionRepository _executionRepository;

        public AuditExecutionController(IAuditExecutionRepository executionRepository)
        {
            _executionRepository = executionRepository;
        }

        [HttpGet("GetPlanningByReference/{referenceId}")]
        public async Task<IActionResult> GetPlanningByReference(int referenceId)
        {
            try
            {
                return Ok(await _executionRepository.GetPlanningByReferenceAsync(referenceId));
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpPost("UpsertPlanning")]
        public async Task<IActionResult> UpsertPlanning([FromBody] UpsertAuditEngagementPlanRequest request)
        {
            if (request.ReferenceId <= 0 || string.IsNullOrWhiteSpace(request.EngagementTitle))
            {
                return BadRequest("Reference ID and engagement title are required");
            }

            try
            {
                return Ok(await _executionRepository.UpsertPlanningAsync(request));
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpGet("GetEngagementTypes")]
        public async Task<IActionResult> GetEngagementTypes()
        {
            try
            {
                return Ok(await _executionRepository.GetEngagementTypesAsync());
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpGet("GetPlanningStatuses")]
        public async Task<IActionResult> GetPlanningStatuses()
        {
            try
            {
                return Ok(await _executionRepository.GetPlanningStatusesAsync());
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpGet("GetScopeItemsByReference/{referenceId}")]
        public async Task<IActionResult> GetScopeItemsByReference(int referenceId)
        {
            try
            {
                return Ok(await _executionRepository.GetScopeItemsByReferenceAsync(referenceId));
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpPost("CreateScopeItem")]
        public async Task<IActionResult> CreateScopeItem([FromBody] CreateAuditScopeItemRequest request)
        {
            if (request.PlanId <= 0 || request.ReferenceId <= 0 || string.IsNullOrWhiteSpace(request.ProcessName))
            {
                return BadRequest("Plan, reference, and process name are required");
            }

            try
            {
                return Ok(await _executionRepository.CreateScopeItemAsync(request));
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpPut("UpdateScopeItem/{id}")]
        public async Task<IActionResult> UpdateScopeItem(int id, [FromBody] UpdateAuditScopeItemRequest request)
        {
            if (id != request.Id)
            {
                return BadRequest("ID mismatch");
            }

            try
            {
                return Ok(await _executionRepository.UpdateScopeItemAsync(request));
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpDelete("DeleteScopeItem/{id}")]
        public async Task<IActionResult> DeleteScopeItem(int id)
        {
            try
            {
                return Ok(new { deleted = await _executionRepository.DeleteScopeItemAsync(id), id });
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpGet("GetRiskControlMatrixByReference/{referenceId}")]
        public async Task<IActionResult> GetRiskControlMatrixByReference(int referenceId)
        {
            try
            {
                return Ok(await _executionRepository.GetRiskControlMatrixByReferenceAsync(referenceId));
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpPost("CreateRiskControlMatrixEntry")]
        public async Task<IActionResult> CreateRiskControlMatrixEntry([FromBody] CreateRiskControlMatrixEntryRequest request)
        {
            if (request.ReferenceId <= 0 || string.IsNullOrWhiteSpace(request.RiskTitle) || string.IsNullOrWhiteSpace(request.ControlName))
            {
                return BadRequest("Reference, risk title, and control name are required");
            }

            try
            {
                return Ok(await _executionRepository.CreateRiskControlMatrixEntryAsync(request));
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpPut("UpdateRiskControlMatrixEntry/{id}")]
        public async Task<IActionResult> UpdateRiskControlMatrixEntry(int id, [FromBody] UpdateRiskControlMatrixEntryRequest request)
        {
            if (id != request.Id)
            {
                return BadRequest("ID mismatch");
            }

            try
            {
                return Ok(await _executionRepository.UpdateRiskControlMatrixEntryAsync(request));
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpDelete("DeleteRiskControlMatrixEntry/{id}")]
        public async Task<IActionResult> DeleteRiskControlMatrixEntry(int id)
        {
            try
            {
                return Ok(new { deleted = await _executionRepository.DeleteRiskControlMatrixEntryAsync(id), id });
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpGet("GetControlClassifications")]
        public async Task<IActionResult> GetControlClassifications()
        {
            try
            {
                return Ok(await _executionRepository.GetControlClassificationsAsync());
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpGet("GetControlTypes")]
        public async Task<IActionResult> GetControlTypes()
        {
            try
            {
                return Ok(await _executionRepository.GetControlTypesAsync());
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpGet("GetControlFrequencies")]
        public async Task<IActionResult> GetControlFrequencies()
        {
            try
            {
                return Ok(await _executionRepository.GetControlFrequenciesAsync());
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpGet("GetWalkthroughsByReference/{referenceId}")]
        public async Task<IActionResult> GetWalkthroughsByReference(int referenceId)
        {
            try
            {
                return Ok(await _executionRepository.GetWalkthroughsByReferenceAsync(referenceId));
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpPost("CreateWalkthrough")]
        public async Task<IActionResult> CreateWalkthrough([FromBody] CreateAuditWalkthroughRequest request)
        {
            if (request.ReferenceId <= 0 || string.IsNullOrWhiteSpace(request.ProcessName))
            {
                return BadRequest("Reference and process name are required");
            }

            try
            {
                return Ok(await _executionRepository.CreateWalkthroughAsync(request));
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpPut("UpdateWalkthrough/{id}")]
        public async Task<IActionResult> UpdateWalkthrough(int id, [FromBody] UpdateAuditWalkthroughRequest request)
        {
            if (id != request.Id)
            {
                return BadRequest("ID mismatch");
            }

            try
            {
                return Ok(await _executionRepository.UpdateWalkthroughAsync(request));
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpDelete("DeleteWalkthrough/{id}")]
        public async Task<IActionResult> DeleteWalkthrough(int id)
        {
            try
            {
                return Ok(new { deleted = await _executionRepository.DeleteWalkthroughAsync(id), id });
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpPost("AddWalkthroughException")]
        public async Task<IActionResult> AddWalkthroughException([FromBody] AddWalkthroughExceptionRequest request)
        {
            if (request.WalkthroughId <= 0 || string.IsNullOrWhiteSpace(request.ExceptionTitle))
            {
                return BadRequest("Walkthrough and exception title are required");
            }

            try
            {
                return Ok(await _executionRepository.AddWalkthroughExceptionAsync(request));
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpGet("GetManagementActionsByReference/{referenceId}")]
        public async Task<IActionResult> GetManagementActionsByReference(int referenceId)
        {
            try
            {
                return Ok(await _executionRepository.GetManagementActionsByReferenceAsync(referenceId));
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpPost("CreateManagementAction")]
        public async Task<IActionResult> CreateManagementAction([FromBody] CreateAuditManagementActionRequest request)
        {
            if (request.ReferenceId <= 0 || string.IsNullOrWhiteSpace(request.ActionTitle))
            {
                return BadRequest("Reference and action title are required");
            }

            try
            {
                return Ok(await _executionRepository.CreateManagementActionAsync(request));
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpPut("UpdateManagementAction/{id}")]
        public async Task<IActionResult> UpdateManagementAction(int id, [FromBody] UpdateAuditManagementActionRequest request)
        {
            if (id != request.Id)
            {
                return BadRequest("ID mismatch");
            }

            try
            {
                return Ok(await _executionRepository.UpdateManagementActionAsync(request));
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpDelete("DeleteManagementAction/{id}")]
        public async Task<IActionResult> DeleteManagementAction(int id)
        {
            try
            {
                return Ok(new { deleted = await _executionRepository.DeleteManagementActionAsync(id), id });
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }
    }
}
