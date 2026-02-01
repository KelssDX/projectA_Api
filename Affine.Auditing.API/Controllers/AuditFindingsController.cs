using Microsoft.AspNetCore.Mvc;
using Affine.Engine.Repository.Auditing;
using Affine.Engine.Model.Auditing.AuditUniverse;

namespace Affine.Auditing.API.Controllers
{
    [ApiController]
    [Route("api/v1/[controller]")]
    public class AuditFindingsController : ControllerBase
    {
        private readonly IAuditFindingsRepository _findingsRepository;

        public AuditFindingsController(IAuditFindingsRepository findingsRepository)
        {
            _findingsRepository = findingsRepository;
        }

        #region Findings CRUD

        /// <summary>
        /// Get a single finding by ID with all details
        /// </summary>
        [HttpGet]
        [Route("GetFinding/{id}")]
        public async Task<IActionResult> GetFinding(int id)
        {
            try
            {
                var finding = await _findingsRepository.GetFindingAsync(id);
                if (finding == null)
                {
                    return NotFound($"Finding with ID {id} not found");
                }
                return Ok(finding);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        /// <summary>
        /// Get all findings for a reference ID
        /// </summary>
        [HttpGet]
        [Route("GetByReference/{referenceId}")]
        public async Task<IActionResult> GetByReference(int referenceId)
        {
            try
            {
                var findings = await _findingsRepository.GetFindingsByReferenceAsync(referenceId);
                return Ok(findings);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        /// <summary>
        /// Get all findings for an audit universe node
        /// </summary>
        [HttpGet]
        [Route("GetByUniverseNode/{auditUniverseId}")]
        public async Task<IActionResult> GetByUniverseNode(int auditUniverseId)
        {
            try
            {
                var findings = await _findingsRepository.GetFindingsByUniverseNodeAsync(auditUniverseId);
                return Ok(findings);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        /// <summary>
        /// Get paginated findings with filters
        /// </summary>
        [HttpPost]
        [Route("GetFindings")]
        public async Task<IActionResult> GetFindings([FromBody] FindingsFilterRequest filter)
        {
            try
            {
                var result = await _findingsRepository.GetFindingsAsync(filter);
                return Ok(result);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        /// <summary>
        /// Create a new audit finding
        /// </summary>
        [HttpPost]
        [Route("CreateFinding")]
        public async Task<IActionResult> CreateFinding([FromBody] CreateAuditFindingRequest request)
        {
            if (string.IsNullOrEmpty(request.FindingTitle))
            {
                return BadRequest("Finding title is required");
            }

            try
            {
                var finding = await _findingsRepository.CreateFindingAsync(request);
                return CreatedAtAction(nameof(GetFinding), new { id = finding.Id }, finding);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        /// <summary>
        /// Update an existing finding
        /// </summary>
        [HttpPut]
        [Route("UpdateFinding/{id}")]
        public async Task<IActionResult> UpdateFinding(int id, [FromBody] UpdateAuditFindingRequest request)
        {
            if (id != request.Id)
            {
                return BadRequest("ID mismatch");
            }

            try
            {
                var finding = await _findingsRepository.UpdateFindingAsync(request);
                return Ok(finding);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        /// <summary>
        /// Delete a finding
        /// </summary>
        [HttpDelete]
        [Route("DeleteFinding/{id}")]
        public async Task<IActionResult> DeleteFinding(int id)
        {
            try
            {
                var result = await _findingsRepository.DeleteFindingAsync(id);
                if (!result)
                {
                    return NotFound($"Finding with ID {id} not found");
                }
                return Ok(new { message = "Finding deleted successfully", id });
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        #endregion

        #region Recommendations CRUD

        /// <summary>
        /// Get a recommendation by ID
        /// </summary>
        [HttpGet]
        [Route("GetRecommendation/{id}")]
        public async Task<IActionResult> GetRecommendation(int id)
        {
            try
            {
                var rec = await _findingsRepository.GetRecommendationAsync(id);
                if (rec == null)
                {
                    return NotFound($"Recommendation with ID {id} not found");
                }
                return Ok(rec);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        /// <summary>
        /// Get all recommendations for a finding
        /// </summary>
        [HttpGet]
        [Route("GetRecommendationsByFinding/{findingId}")]
        public async Task<IActionResult> GetRecommendationsByFinding(int findingId)
        {
            try
            {
                var recommendations = await _findingsRepository.GetRecommendationsByFindingAsync(findingId);
                return Ok(recommendations);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        /// <summary>
        /// Create a new recommendation
        /// </summary>
        [HttpPost]
        [Route("CreateRecommendation")]
        public async Task<IActionResult> CreateRecommendation([FromBody] CreateRecommendationRequest request)
        {
            if (string.IsNullOrEmpty(request.Recommendation))
            {
                return BadRequest("Recommendation text is required");
            }
            if (request.FindingId <= 0)
            {
                return BadRequest("Valid finding ID is required");
            }

            try
            {
                var rec = await _findingsRepository.CreateRecommendationAsync(request);
                return CreatedAtAction(nameof(GetRecommendation), new { id = rec.Id }, rec);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        /// <summary>
        /// Update a recommendation
        /// </summary>
        [HttpPut]
        [Route("UpdateRecommendation/{id}")]
        public async Task<IActionResult> UpdateRecommendation(int id, [FromBody] UpdateRecommendationRequest request)
        {
            if (id != request.Id)
            {
                return BadRequest("ID mismatch");
            }

            try
            {
                var rec = await _findingsRepository.UpdateRecommendationAsync(request);
                return Ok(rec);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        /// <summary>
        /// Delete a recommendation
        /// </summary>
        [HttpDelete]
        [Route("DeleteRecommendation/{id}")]
        public async Task<IActionResult> DeleteRecommendation(int id)
        {
            try
            {
                var result = await _findingsRepository.DeleteRecommendationAsync(id);
                if (!result)
                {
                    return NotFound($"Recommendation with ID {id} not found");
                }
                return Ok(new { message = "Recommendation deleted successfully", id });
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        #endregion

        #region Lookups

        /// <summary>
        /// Get all finding severity levels
        /// </summary>
        [HttpGet]
        [Route("GetSeverities")]
        public async Task<IActionResult> GetSeverities()
        {
            try
            {
                var severities = await _findingsRepository.GetSeveritiesAsync();
                return Ok(severities);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        /// <summary>
        /// Get all finding status values
        /// </summary>
        [HttpGet]
        [Route("GetFindingStatuses")]
        public async Task<IActionResult> GetFindingStatuses()
        {
            try
            {
                var statuses = await _findingsRepository.GetFindingStatusesAsync();
                return Ok(statuses);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        /// <summary>
        /// Get all recommendation status values
        /// </summary>
        [HttpGet]
        [Route("GetRecommendationStatuses")]
        public async Task<IActionResult> GetRecommendationStatuses()
        {
            try
            {
                var statuses = await _findingsRepository.GetRecommendationStatusesAsync();
                return Ok(statuses);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        #endregion

        #region Analytics

        /// <summary>
        /// Get findings aging analysis (for aging widget)
        /// </summary>
        [HttpGet]
        [Route("GetFindingsAging")]
        public async Task<IActionResult> GetFindingsAging([FromQuery] int? referenceId, [FromQuery] int? auditUniverseId)
        {
            try
            {
                var aging = await _findingsRepository.GetFindingsAgingAsync(referenceId, auditUniverseId);
                return Ok(aging);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        /// <summary>
        /// Get recommendation summary statistics
        /// </summary>
        [HttpGet]
        [Route("GetRecommendationSummary")]
        public async Task<IActionResult> GetRecommendationSummary([FromQuery] int? referenceId, [FromQuery] int? auditUniverseId)
        {
            try
            {
                var summary = await _findingsRepository.GetRecommendationSummaryAsync(referenceId, auditUniverseId);
                return Ok(summary);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        #endregion

        #region Audit Coverage

        /// <summary>
        /// Get audit coverage for a universe node
        /// </summary>
        [HttpGet]
        [Route("GetAuditCoverage/{auditUniverseId}")]
        public async Task<IActionResult> GetAuditCoverage(int auditUniverseId, [FromQuery] int? year)
        {
            try
            {
                var coverage = await _findingsRepository.GetAuditCoverageAsync(auditUniverseId, year);
                return Ok(coverage);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        /// <summary>
        /// Get audit coverage map (for treemap widget)
        /// </summary>
        [HttpGet]
        [Route("GetAuditCoverageMap")]
        public async Task<IActionResult> GetAuditCoverageMap([FromQuery] int year, [FromQuery] int? quarter)
        {
            try
            {
                var map = await _findingsRepository.GetAuditCoverageMapAsync(year, quarter);
                return Ok(map);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        /// <summary>
        /// Update audit coverage data
        /// </summary>
        [HttpPost]
        [Route("UpdateAuditCoverage")]
        public async Task<IActionResult> UpdateAuditCoverage([FromBody] UpdateAuditCoverageRequest request)
        {
            try
            {
                await _findingsRepository.UpdateAuditCoverageAsync(request);
                return Ok(new { message = "Audit coverage updated successfully" });
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        #endregion

        #region Risk Trends

        /// <summary>
        /// Get risk trend data over time
        /// </summary>
        [HttpGet]
        [Route("GetRiskTrend")]
        public async Task<IActionResult> GetRiskTrend([FromQuery] int? referenceId, [FromQuery] int? auditUniverseId, [FromQuery] int months = 12)
        {
            try
            {
                var trend = await _findingsRepository.GetRiskTrendAsync(referenceId, auditUniverseId, months);
                return Ok(trend);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        /// <summary>
        /// Get risk velocity metrics
        /// </summary>
        [HttpGet]
        [Route("GetRiskVelocity")]
        public async Task<IActionResult> GetRiskVelocity([FromQuery] int? referenceId, [FromQuery] int? auditUniverseId)
        {
            try
            {
                var velocity = await _findingsRepository.GetRiskVelocityAsync(referenceId, auditUniverseId);
                return Ok(velocity);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        /// <summary>
        /// Create a risk trend snapshot (for scheduled jobs)
        /// </summary>
        [HttpPost]
        [Route("CreateRiskTrendSnapshot")]
        public async Task<IActionResult> CreateRiskTrendSnapshot([FromQuery] int? referenceId, [FromQuery] int? auditUniverseId)
        {
            try
            {
                await _findingsRepository.CreateRiskTrendSnapshotAsync(referenceId, auditUniverseId);
                return Ok(new { message = "Risk trend snapshot created successfully" });
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        #endregion
    }
}
