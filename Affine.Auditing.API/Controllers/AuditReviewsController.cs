using Affine.Auditing.API.Security;
using Affine.Engine.Model.Auditing.AuditUniverse;
using Affine.Engine.Repository.Auditing;
using Microsoft.AspNetCore.Mvc;

namespace Affine.Auditing.API.Controllers
{
    [ApiController]
    [Route("api/v1/[controller]")]
    public class AuditReviewsController : ControllerBase
    {
        private readonly IAuditReviewsRepository _reviewsRepository;

        public AuditReviewsController(IAuditReviewsRepository reviewsRepository)
        {
            _reviewsRepository = reviewsRepository;
        }

        [HttpGet("GetWorkspace")]
        public async Task<IActionResult> GetWorkspace([FromQuery] int? userId)
        {
            var userContext = AuditApiUserContext.FromHttpContext(HttpContext);
            if (!userContext.HasUserContext)
            {
                return StatusCode(401, "Audit user context is required.");
            }
            if (!userContext.CanReviewAuditContent())
            {
                return StatusCode(403, "You do not have permission to access the review workspace.");
            }
            if (!userContext.CanAccessUserScope(userId))
            {
                return StatusCode(403, "You do not have permission to access another user's review workspace.");
            }

            try
            {
                var scopedUserId = (!userId.HasValue && userContext.CanRunWorkflowAdminActions())
                    ? null
                    : (userContext.UserId.HasValue ? userId ?? userContext.UserId : userId);
                return Ok(await _reviewsRepository.GetWorkspaceAsync(scopedUserId));
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpGet("GetByReference/{referenceId}")]
        public async Task<IActionResult> GetByReference(int referenceId)
        {
            var userContext = AuditApiUserContext.FromHttpContext(HttpContext);
            if (!userContext.HasUserContext)
            {
                return StatusCode(401, "Audit user context is required.");
            }
            if (!userContext.CanReviewAuditContent())
            {
                return StatusCode(403, "You do not have permission to access audit reviews.");
            }

            try
            {
                return Ok(await _reviewsRepository.GetReviewsByReferenceAsync(referenceId));
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpGet("GetReviewNotes/{reviewId}")]
        public async Task<IActionResult> GetReviewNotes(int reviewId)
        {
            var userContext = AuditApiUserContext.FromHttpContext(HttpContext);
            if (!userContext.HasUserContext)
            {
                return StatusCode(401, "Audit user context is required.");
            }
            if (!userContext.CanReviewAuditContent())
            {
                return StatusCode(403, "You do not have permission to access review notes.");
            }

            try
            {
                return Ok(await _reviewsRepository.GetReviewNotesAsync(reviewId));
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpGet("GetSignoffsByReference/{referenceId}")]
        public async Task<IActionResult> GetSignoffsByReference(int referenceId, [FromQuery] int limit = 100)
        {
            var userContext = AuditApiUserContext.FromHttpContext(HttpContext);
            if (!userContext.HasUserContext)
            {
                return StatusCode(401, "Audit user context is required.");
            }
            if (!userContext.CanReviewAuditContent())
            {
                return StatusCode(403, "You do not have permission to access sign-offs.");
            }

            try
            {
                return Ok(await _reviewsRepository.GetSignoffsByReferenceAsync(referenceId, limit));
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpPost("AddReviewNote")]
        public async Task<IActionResult> AddReviewNote([FromBody] CreateAuditReviewNoteRequest request)
        {
            var userContext = AuditApiUserContext.FromHttpContext(HttpContext);
            if (!userContext.HasUserContext)
            {
                return StatusCode(401, "Audit user context is required.");
            }
            if (!userContext.CanReviewAuditContent())
            {
                return StatusCode(403, "You do not have permission to add review notes.");
            }
            if (request == null || request.ReviewId <= 0 || string.IsNullOrWhiteSpace(request.NoteText))
            {
                return BadRequest("Review ID and note text are required.");
            }

            try
            {
                request.RaisedByUserId = userContext.UserId;
                request.RaisedByName = userContext.GetDisplayName(request.RaisedByName ?? "Audit Reviewer");
                return Ok(await _reviewsRepository.AddReviewNoteAsync(request));
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }
    }
}
