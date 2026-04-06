using Affine.Engine.Model.Auditing.AuditUniverse;
using Affine.Engine.Repository.Auditing;
using Microsoft.AspNetCore.Mvc;

namespace Affine.Auditing.API.Controllers
{
    [ApiController]
    [Route("api/v1/[controller]")]
    public class AuditProceduresController : ControllerBase
    {
        private readonly IAuditProceduresRepository _proceduresRepository;

        public AuditProceduresController(IAuditProceduresRepository proceduresRepository)
        {
            _proceduresRepository = proceduresRepository;
        }

        [HttpGet]
        [Route("GetProcedure/{id}")]
        public async Task<IActionResult> GetProcedure(int id)
        {
            try
            {
                var procedure = await _proceduresRepository.GetProcedureAsync(id);
                if (procedure == null)
                {
                    return NotFound($"Procedure with ID {id} not found");
                }
                return Ok(procedure);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpGet]
        [Route("GetByReference/{referenceId}")]
        public async Task<IActionResult> GetByReference(int referenceId)
        {
            try
            {
                var procedures = await _proceduresRepository.GetProceduresByReferenceAsync(referenceId);
                return Ok(procedures);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpGet]
        [Route("GetLibrary")]
        public async Task<IActionResult> GetLibrary([FromQuery] string? search = null, [FromQuery] int? engagementTypeId = null)
        {
            try
            {
                var procedures = await _proceduresRepository.GetLibraryProceduresAsync(search, engagementTypeId);
                return Ok(procedures);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpPost]
        [Route("CreateProcedure")]
        public async Task<IActionResult> CreateProcedure([FromBody] CreateAuditProcedureRequest request)
        {
            if (string.IsNullOrWhiteSpace(request.ProcedureTitle))
            {
                return BadRequest("Procedure title is required");
            }

            try
            {
                var procedure = await _proceduresRepository.CreateProcedureAsync(request);
                return CreatedAtAction(nameof(GetProcedure), new { id = procedure.Id }, procedure);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpPut]
        [Route("UpdateProcedure/{id}")]
        public async Task<IActionResult> UpdateProcedure(int id, [FromBody] UpdateAuditProcedureRequest request)
        {
            if (id != request.Id)
            {
                return BadRequest("ID mismatch");
            }
            if (string.IsNullOrWhiteSpace(request.ProcedureTitle))
            {
                return BadRequest("Procedure title is required");
            }

            try
            {
                var procedure = await _proceduresRepository.UpdateProcedureAsync(request);
                return Ok(procedure);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpPost]
        [Route("CreateFromTemplate")]
        public async Task<IActionResult> CreateFromTemplate([FromBody] CreateProcedureFromTemplateRequest request)
        {
            if (request.TemplateId <= 0 || request.ReferenceId <= 0)
            {
                return BadRequest("Template ID and reference ID are required");
            }

            try
            {
                var procedure = await _proceduresRepository.CreateProcedureFromTemplateAsync(request);
                return CreatedAtAction(nameof(GetProcedure), new { id = procedure.Id }, procedure);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpDelete]
        [Route("DeleteProcedure/{id}")]
        public async Task<IActionResult> DeleteProcedure(int id)
        {
            try
            {
                var result = await _proceduresRepository.DeleteProcedureAsync(id);
                if (!result)
                {
                    return NotFound($"Procedure with ID {id} not found");
                }
                return Ok(new { message = "Procedure deleted successfully", id });
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpGet]
        [Route("GetTypes")]
        public async Task<IActionResult> GetTypes()
        {
            try
            {
                var types = await _proceduresRepository.GetProcedureTypesAsync();
                return Ok(types);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpGet]
        [Route("GetStatuses")]
        public async Task<IActionResult> GetStatuses()
        {
            try
            {
                var statuses = await _proceduresRepository.GetProcedureStatusesAsync();
                return Ok(statuses);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }
    }
}
