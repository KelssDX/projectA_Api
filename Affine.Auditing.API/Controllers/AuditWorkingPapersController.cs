using Affine.Engine.Model.Auditing.AuditUniverse;
using Affine.Engine.Repository.Auditing;
using Microsoft.AspNetCore.Mvc;

namespace Affine.Auditing.API.Controllers
{
    [ApiController]
    [Route("api/v1/[controller]")]
    public class AuditWorkingPapersController : ControllerBase
    {
        private readonly IAuditWorkingPapersRepository _workingPapersRepository;

        public AuditWorkingPapersController(IAuditWorkingPapersRepository workingPapersRepository)
        {
            _workingPapersRepository = workingPapersRepository;
        }

        [HttpGet]
        [Route("GetWorkingPaper/{id}")]
        public async Task<IActionResult> GetWorkingPaper(int id)
        {
            try
            {
                var workingPaper = await _workingPapersRepository.GetWorkingPaperAsync(id);
                if (workingPaper == null)
                {
                    return NotFound($"Working paper with ID {id} not found");
                }
                return Ok(workingPaper);
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
                var workingPapers = await _workingPapersRepository.GetWorkingPapersByReferenceAsync(referenceId);
                return Ok(workingPapers);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpGet]
        [Route("GetTemplates")]
        public async Task<IActionResult> GetTemplates([FromQuery] string? search = null, [FromQuery] int? engagementTypeId = null)
        {
            try
            {
                var workingPapers = await _workingPapersRepository.GetWorkingPaperTemplatesAsync(search, engagementTypeId);
                return Ok(workingPapers);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpPost]
        [Route("CreateWorkingPaper")]
        public async Task<IActionResult> CreateWorkingPaper([FromBody] CreateAuditWorkingPaperRequest request)
        {
            if (string.IsNullOrWhiteSpace(request.Title))
            {
                return BadRequest("Working paper title is required");
            }

            try
            {
                var workingPaper = await _workingPapersRepository.CreateWorkingPaperAsync(request);
                return CreatedAtAction(nameof(GetWorkingPaper), new { id = workingPaper.Id }, workingPaper);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpPut]
        [Route("UpdateWorkingPaper/{id}")]
        public async Task<IActionResult> UpdateWorkingPaper(int id, [FromBody] UpdateAuditWorkingPaperRequest request)
        {
            if (id != request.Id)
            {
                return BadRequest("ID mismatch");
            }
            if (string.IsNullOrWhiteSpace(request.Title))
            {
                return BadRequest("Working paper title is required");
            }

            try
            {
                var workingPaper = await _workingPapersRepository.UpdateWorkingPaperAsync(request);
                return Ok(workingPaper);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpPost]
        [Route("CreateFromTemplate")]
        public async Task<IActionResult> CreateFromTemplate([FromBody] CreateWorkingPaperFromTemplateRequest request)
        {
            if (request.TemplateId <= 0 || request.ReferenceId <= 0)
            {
                return BadRequest("Template ID and reference ID are required");
            }

            try
            {
                var workingPaper = await _workingPapersRepository.CreateWorkingPaperFromTemplateAsync(request);
                return CreatedAtAction(nameof(GetWorkingPaper), new { id = workingPaper.Id }, workingPaper);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpDelete]
        [Route("DeleteWorkingPaper/{id}")]
        public async Task<IActionResult> DeleteWorkingPaper(int id)
        {
            try
            {
                var result = await _workingPapersRepository.DeleteWorkingPaperAsync(id);
                if (!result)
                {
                    return NotFound($"Working paper with ID {id} not found");
                }
                return Ok(new { message = "Working paper deleted successfully", id });
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
                var statuses = await _workingPapersRepository.GetWorkingPaperStatusesAsync();
                return Ok(statuses);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpGet]
        [Route("GetSignoffs/{workingPaperId}")]
        public async Task<IActionResult> GetSignoffs(int workingPaperId)
        {
            try
            {
                var signoffs = await _workingPapersRepository.GetSignoffsAsync(workingPaperId);
                return Ok(signoffs);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpPost]
        [Route("AddSignoff")]
        public async Task<IActionResult> AddSignoff([FromBody] AddWorkingPaperSignoffRequest request)
        {
            if (request.WorkingPaperId <= 0 || string.IsNullOrWhiteSpace(request.ActionType))
            {
                return BadRequest("Working paper and sign-off action are required");
            }

            try
            {
                var signoff = await _workingPapersRepository.AddSignoffAsync(request);
                return Ok(signoff);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpGet]
        [Route("GetReferences/{workingPaperId}")]
        public async Task<IActionResult> GetReferences(int workingPaperId)
        {
            try
            {
                var references = await _workingPapersRepository.GetReferencesAsync(workingPaperId);
                return Ok(references);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpPost]
        [Route("AddReference")]
        public async Task<IActionResult> AddReference([FromBody] AddWorkingPaperReferenceRequest request)
        {
            if (request.FromWorkingPaperId <= 0 || request.ToWorkingPaperId <= 0)
            {
                return BadRequest("Source and target working paper IDs are required");
            }
            if (request.FromWorkingPaperId == request.ToWorkingPaperId)
            {
                return BadRequest("A working paper cannot reference itself");
            }

            try
            {
                var reference = await _workingPapersRepository.AddReferenceAsync(request);
                return Ok(reference);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }
    }
}
