using Affine.Engine.Model.Auditing.Assessment;
using Affine.Engine.Repository.Auditing;
using Microsoft.AspNetCore.Mvc;

namespace Affina.Auditing.API.Controllers
{
    [ApiController]
    [Route("api/v1/[controller]")]
    public class RiskAssessmentController : ControllerBase
    {
        private readonly IRiskAssessmentRepository _riskAssessmentRepository;

        public RiskAssessmentController(IRiskAssessmentRepository riskAssessmentRepository)
        {
            _riskAssessmentRepository = riskAssessmentRepository;
        }

        // Original Risk Assessment Logic
        [HttpGet]
        [Route("GetRiskAssessment")]
        public async Task<IActionResult> GetRiskAssessment(int referenceId)
        {
            var assessment = await _riskAssessmentRepository.GetRiskAssessmentAsync(referenceId);

            if (assessment == null)
            {
                return NotFound("Risk Assessment not found");
            }

            return Ok(assessment);
        }

        [HttpPost]
        [Route("CreateRiskAssessment")]
        public async Task<IActionResult> CreateRiskAssessment([FromBody] List<RiskAssessmentCreateRequest> request)
        {
            if (!ModelState.IsValid)
                return BadRequest(ModelState);

            var result = await _riskAssessmentRepository.AddRiskAssessmentAsync(request);
            
            if (!result)
                return BadRequest("Failed to create risk assessment");

            return Ok("Risk assessment created successfully");
        }

        [HttpPut]
        [Route("UpdateRiskAssessment/{referenceId}")]
        public async Task<IActionResult> UpdateRiskAssessment(int referenceId, [FromBody] RiskAssessmentUpdateRequest request)
        {
            if (!ModelState.IsValid)
                return BadRequest(ModelState);

            var result = await _riskAssessmentRepository.UpdateRiskAssessmentAsync(referenceId, request);
            
            if (!result)
                return BadRequest("Failed to update risk assessment");

            return Ok("Risk assessment updated successfully");
        }

        [HttpGet]
        [Route("GetRisks")]
        public async Task<IActionResult> GetRisks()
        {
            // var risks = await _riskAssessmentRepository.GetRisksAsync();
            //  return Ok(risks);
            return null;
        }

        [HttpGet]
        [Route("GetControls")]
        public async Task<IActionResult> GetControls()
        {
            // var controls = await _riskAssessmentRepository.GetControlsAsync();
            // return Ok(controls);
            return null;
        }
        

        [HttpGet]
        [Route("GetOutcomes")]
        public async Task<IActionResult> GetOutcomes()
        {
            // var outcomes = await _riskAssessmentRepository.GetOutcomesAsync();
            // return Ok(outcomes);
            return null;
        }
    

        //New Endpoints for ra_* Tables
        [HttpGet]
        [Route("GetRiskLikelihoods")]
        public async Task<IActionResult> GetRiskLikelihoods()
        {
            var likelihoods = await _riskAssessmentRepository.GetRiskLikelihoodsAsync();
            return Ok(likelihoods);
        }

        [HttpGet]
        [Route("GetImpacts")]
        public async Task<IActionResult> GetImpacts()
        {
            var impacts = await _riskAssessmentRepository.GetImpactsAsync();
            return Ok(impacts);
        }

        [HttpGet]
        [Route("GetKeySecondaryRisks")]
        public async Task<IActionResult> GetKeySecondaryRisks()
        {
            var keySecondaryRisks = await _riskAssessmentRepository.GetKeySecondaryRisksAsync();
            return Ok(keySecondaryRisks);
        }

        [HttpGet]
        [Route("GetRiskCategories")]
        public async Task<IActionResult> GetRiskCategories()
        {
            var categories = await _riskAssessmentRepository.GetRiskCategoriesAsync();
            return Ok(categories);
        }

        [HttpGet]
        [Route("GetDataFrequencies")]
        public async Task<IActionResult> GetDataFrequencies()
        {
            var frequencies = await _riskAssessmentRepository.GetDataFrequenciesAsync();
            return Ok(frequencies);
        }

        [HttpGet]
        [Route("GetOutcomeLikelihoods")]
        public async Task<IActionResult> GetOutcomeLikelihoods()
        {
            var outcomeLikelihoods = await _riskAssessmentRepository.GetOutcomeLikelihoodsAsync();
            return Ok(outcomeLikelihoods);
        }

        [HttpGet]
        [Route("GetEvidence")]
        public async Task<IActionResult> GetEvidence()
        {
            var evidence = await _riskAssessmentRepository.GetEvidenceAsync();
            return Ok(evidence);
        }
    }
}
