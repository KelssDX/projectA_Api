using Affine.Engine.Model.Auditing.Assessment;
using Affine.Engine.Repository.Auditing;
using Microsoft.AspNetCore.Mvc;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using System.Net.Http;
using System.Text.Json;
using System.Text;

namespace Affina.Auditing.API.Controllers
{
    [ApiController]
    [Route("api/v1/[controller]")]
    public class RiskAssessmentController : ControllerBase
    {
        private readonly IRiskAssessmentRepository _riskAssessmentRepository;
        private readonly IHttpClientFactory _httpClientFactory;
        private readonly IConfiguration _configuration;

        public RiskAssessmentController(
            IRiskAssessmentRepository riskAssessmentRepository,
            IHttpClientFactory httpClientFactory,
            IConfiguration configuration)
        {
            _riskAssessmentRepository = riskAssessmentRepository ?? throw new ArgumentNullException(nameof(riskAssessmentRepository));
            _httpClientFactory = httpClientFactory ?? throw new ArgumentNullException(nameof(httpClientFactory));
            _configuration = configuration ?? throw new ArgumentNullException(nameof(configuration));
        }
        // New: Departments endpoint for frontend pickers
        [HttpGet]
        [Route("GetDepartments")]
        public async Task<IActionResult> GetDepartments()
        {
            try
            {
                var departments = await _riskAssessmentRepository.GetDepartmentsAsync();
                return Ok(departments);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"An unexpected error occurred while retrieving departments: {ex.Message}");
            }
        }

        [HttpGet]
        [Route("GetProjects")]
        public async Task<IActionResult> GetProjects()
        {
            try
            {
                var projects = await _riskAssessmentRepository.GetProjectsAsync();
                return Ok(projects);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"An unexpected error occurred while retrieving projects: {ex.Message}");
            }
        }

        [HttpGet]
        [Route("GetAssessments")]
        public async Task<IActionResult> GetAssessments()
        {
            try
            {
                var assessments = await _riskAssessmentRepository.GetAssessmentsAsync();
                return Ok(assessments);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"An unexpected error occurred while retrieving assessments: {ex.Message}");
            }
        }

        // Original Risk Assessment Logic
        [HttpGet]
        [Route("GetRiskAssessment")]
        public async Task<IActionResult> GetRiskAssessment(int referenceId)
        {
            if (referenceId <= 0)
            {
                return BadRequest("Reference ID must be greater than zero.");
            }

            try
            {
                var riskAssessment = await _riskAssessmentRepository.GetRiskAssessmentAsync(referenceId);

                if (riskAssessment == null)
                {
                    return NotFound($"Risk Assessment Reference with ID {referenceId} not found");
                }

                if (riskAssessment.RiskAssessments == null || !riskAssessment.RiskAssessments.Any())
                {
                    return NotFound($"No Risk Assessments found for Reference ID {referenceId}");
                }

                return Ok(riskAssessment);
            }
            catch (InvalidOperationException ex)
            {
                return StatusCode(500, $"Database operation failed: {ex.Message}");
            }
            catch (Exception ex)
            {
                return StatusCode(500, "An unexpected error occurred while retrieving risk assessment data.");
            }
        }

        [HttpPost]
        [Route("CreateRiskAssessment")]
        public async Task<IActionResult> CreateRiskAssessment([FromBody] RiskAssessmentCreateWrapper wrapper)
        {
            if (!ModelState.IsValid)
                return BadRequest(ModelState);

            if (wrapper == null || wrapper.Assessments == null || !wrapper.Assessments.Any())
                return BadRequest("Risk assessment data is required.");

            if (wrapper.Reference == null && !wrapper.ReferenceId.HasValue)
                return BadRequest("Either reference data or an existing reference ID is required.");

            try 
            {
                // ReferenceId is an optional parameter.
                // If provided and valid, it will link new assessments to an existing reference.
                // Otherwise, a new reference will be created from the Reference property.
                var result = await _riskAssessmentRepository.AddRiskAssessmentAsync(
                    wrapper.Assessments,
                    wrapper.Reference,
                    wrapper.ReferenceId);

                if (!result)
                    return StatusCode(500, "Failed to create risk assessment.");

                return Ok(new { Success = true, Message = "Risk assessment created successfully." });
            }
            catch (InvalidOperationException ex)
            {
                return StatusCode(500, $"Database operation failed: {ex.Message}");
            }
            catch (Exception ex)
            {
                return StatusCode(500, "An unexpected error occurred while creating risk assessment data.");
            }
        }

        [HttpPut]
        [Route("UpdateRiskAssessment/{referenceId}")]
        public async Task<IActionResult> UpdateRiskAssessment(int referenceId, [FromBody] List<RiskAssessmentUpdateRequest> request)
        {
            if (referenceId <= 0)
                return BadRequest("Reference ID must be greater than zero.");

            if (request == null || !request.Any())
                return BadRequest("Update data is required.");

            // Validate RiskAssessmentRefId in each update request
            foreach (var item in request)
            {
                if (item.RiskAssessmentRefId <= 0)
                {
                    return BadRequest($"Invalid RiskAssessmentRefId: {item.RiskAssessmentRefId}. All RiskAssessmentRefId values must be greater than zero.");
                }
            }

            try
            {
                var result = await _riskAssessmentRepository.UpdateRiskAssessmentsAsync(request, referenceId);

                if (!result)
                    return NotFound($"Risk Assessment Reference with ID {referenceId} not found or no updates were applied.");

                return Ok(new { 
                    Success = true, 
                    Message = "Risk assessment updated successfully.",
                    ReferenceId = referenceId,
                    UpdatedCount = request.Count
                });
            }
            catch (InvalidOperationException ex)
            {
                return StatusCode(500, $"Database operation failed: {ex.Message}");
            }
            catch (Exception ex)
            {
                return StatusCode(500, "An unexpected error occurred while updating risk assessment data.");
            }
        }
        
        [HttpPost]
        [Route("StartControlTesting/{referenceId}")]
        public async Task<IActionResult> StartControlTesting(int referenceId, [FromBody] ControlTestingRequest request)
        {
            if (referenceId <= 0)
                return BadRequest("Reference ID must be greater than zero.");

            if (request == null)
                return BadRequest("Control testing request data is required.");
                
            if (string.IsNullOrEmpty(request.ControlId))
                return BadRequest("Control ID is required.");
                
            if (string.IsNullOrEmpty(request.TesterId))
                return BadRequest("Tester ID is required.");

            try
            {
                // First, verify the risk assessment exists
                var riskAssessment = await _riskAssessmentRepository.GetRiskAssessmentAsync(referenceId);
                if (riskAssessment == null)
                {
                    return NotFound($"Risk Assessment Reference with ID {referenceId} not found");
                }

                // Make a request to the workflow service to start control testing
                var workflowServiceUrl = _configuration["WorkflowServiceUrl"] ?? "https://localhost:7126";
                var client = _httpClientFactory.CreateClient();
                
                // Update to match Elsa 3.3.5 API structure
                var workflowRequest = new
                {
                    workflowDefinitionId = "ControlTestingWorkflow",
                    activityId = "ControlTestingActivity",
                    input = new {
                        ControlId = request.ControlId,
                        RiskAssessmentId = referenceId.ToString(),
                        TesterName = request.TesterId,
                        TestResult = "Pending"
                    }
                };
                
                var jsonContent = JsonSerializer.Serialize(workflowRequest);
                var content = new StringContent(jsonContent, Encoding.UTF8, "application/json");
                
                // Updated endpoint for Elsa 3.3.5
                var response = await client.PostAsync($"{workflowServiceUrl}/elsa/api/workflows/dispatch", content);
                
                if (response.IsSuccessStatusCode)
                {
                    var responseContent = await response.Content.ReadAsStringAsync();
                    var responseObject = JsonSerializer.Deserialize<JsonElement>(responseContent);
                    
                    return Ok(new { 
                        Success = true, 
                        Message = "Control testing workflow started successfully",
                        WorkflowInstanceId = responseObject.GetProperty("workflowInstanceId").GetString()
                    });
                }
                else
                {
                    return StatusCode((int)response.StatusCode, $"Failed to start control testing workflow: {response.ReasonPhrase}");
                }
            }
            catch (InvalidOperationException ex)
            {
                return StatusCode(500, $"Database operation failed: {ex.Message}");
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"An unexpected error occurred: {ex.Message}");
            }
        }

        [HttpGet]
        [Route("GetRisks")]
        public async Task<IActionResult> GetRisks()
        {
            try
            {
                var risks = await _riskAssessmentRepository.GetRisksAsync(null, null);
                return Ok(risks);
            }
            catch (Exception ex)
            {
                return StatusCode(500, "An unexpected error occurred while retrieving risk data.");
            }
        }

        [HttpGet]
        [Route("GetControls")]
        public async Task<IActionResult> GetControls()
        {
            try
            {
                var controls = await _riskAssessmentRepository.GetControlsAsync(null, null);
                return Ok(controls);
            }
            catch (Exception ex)
            {
                return StatusCode(500, "An unexpected error occurred while retrieving control data.");
            }
        }

        [HttpGet]
        [Route("GetOutcomes")]
        public async Task<IActionResult> GetOutcomes()
        {
            try
            {
                var outcomes = await _riskAssessmentRepository.GetOutcomesAsync(null, null);
                return Ok(outcomes);
            }
            catch (Exception ex)
            {
                return StatusCode(500, "An unexpected error occurred while retrieving outcome data.");
            }
        }

        [HttpGet]
        [Route("GetRiskLikelihoods")]
        public async Task<IActionResult> GetRiskLikelihoods()
        {
            try
            {
                var likelihoods = await _riskAssessmentRepository.GetRiskLikelihoodsAsync();
                return Ok(likelihoods);
            }
            catch (Exception ex)
            {
                return StatusCode(500, "An unexpected error occurred while retrieving risk likelihood data.");
            }
        }

        [HttpGet]
        [Route("GetImpacts")]
        public async Task<IActionResult> GetImpacts()
        {
            try
            {
                var impacts = await _riskAssessmentRepository.GetImpactsAsync();
                return Ok(impacts);
            }
            catch (Exception ex)
            {
                return StatusCode(500, "An unexpected error occurred while retrieving impact data.");
            }
        }

        [HttpGet]
        [Route("GetKeySecondaryRisks")]
        public async Task<IActionResult> GetKeySecondaryRisks()
        {
            try
            {
                var risks = await _riskAssessmentRepository.GetKeySecondaryRisksAsync();
                return Ok(risks);
            }
            catch (Exception ex)
            {
                return StatusCode(500, "An unexpected error occurred while retrieving key secondary risk data.");
            }
        }

        [HttpGet]
        [Route("GetRiskCategories")]
        public async Task<IActionResult> GetRiskCategories()
        {
            try
            {
                var categories = await _riskAssessmentRepository.GetRiskCategoriesAsync();
                return Ok(categories);
            }
            catch (Exception ex)
            {
                return StatusCode(500, "An unexpected error occurred while retrieving risk category data.");
            }
        }

        [HttpGet]
        [Route("GetDataFrequencies")]
        public async Task<IActionResult> GetDataFrequencies()
        {
            try
            {
                var frequencies = await _riskAssessmentRepository.GetDataFrequenciesAsync();
                return Ok(frequencies);
            }
            catch (Exception ex)
            {
                return StatusCode(500, "An unexpected error occurred while retrieving data frequency information.");
            }
        }

        [HttpGet]
        [Route("GetOutcomeLikelihoods")]
        public async Task<IActionResult> GetOutcomeLikelihoods()
        {
            try
            {
                var likelihoods = await _riskAssessmentRepository.GetOutcomeLikelihoodsAsync();
                return Ok(likelihoods);
            }
            catch (Exception ex)
            {
                return StatusCode(500, "An unexpected error occurred while retrieving outcome likelihood data.");
            }
        }

        [HttpGet]
        [Route("GetEvidence")]
        public async Task<IActionResult> GetEvidence()
        {
            try
            {
                var evidence = await _riskAssessmentRepository.GetEvidenceAsync();
                return Ok(evidence);
            }
            catch (Exception ex)
            {
                return StatusCode(500, "An unexpected error occurred while retrieving evidence data.");
            }
        }

        [HttpPost]
        [Route("CreateReference")]
        public async Task<IActionResult> CreateReference([FromBody] RiskAssessmentReferenceInput request)
        {
            if (!ModelState.IsValid)
                return BadRequest(ModelState);

            if (request == null)
                return BadRequest("Reference data is required.");

            try
            {
                var referenceId = await _riskAssessmentRepository.AddRiskAssessmentReferenceAsync(request);
                
                if (referenceId <= 0)
                    return StatusCode(500, "Failed to create risk assessment reference.");

                return Ok(new { ReferenceId = referenceId, Message = "Reference created successfully." });
            }
            catch (InvalidOperationException ex)
            {
                return StatusCode(500, $"Database operation failed: {ex.Message}");
            }
            catch (Exception ex)
            {
                return StatusCode(500, "An unexpected error occurred while creating reference data.");
            }
        }
    }
    
    public class ControlTestingRequest
    {
        public string ControlId { get; set; } = default!;
        public string TesterId { get; set; } = default!;
        public string? TestFrequency { get; set; }
    }
} 