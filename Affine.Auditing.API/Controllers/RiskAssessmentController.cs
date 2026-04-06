using Affine.Engine.Model.Auditing.Assessment;
using Affine.Engine.Repository.Auditing;
using Affine.Engine.Services;
using Microsoft.AspNetCore.Mvc;
using Affine.Auditing.API.Security;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Affina.Auditing.API.Controllers
{
    [ApiController]
    [Route("api/v1/[controller]")]
    public class RiskAssessmentController : ControllerBase
    {
        private readonly IRiskAssessmentRepository _riskAssessmentRepository;
        private readonly IAuditWorkflowService _workflowService;
        private readonly IAuditTrailService _auditTrailService;
        private readonly IAuditPlatformRepository _platformRepository;

        public RiskAssessmentController(
            IRiskAssessmentRepository riskAssessmentRepository,
            IAuditWorkflowService workflowService,
            IAuditTrailService auditTrailService,
            IAuditPlatformRepository platformRepository)
        {
            _riskAssessmentRepository = riskAssessmentRepository ?? throw new ArgumentNullException(nameof(riskAssessmentRepository));
            _workflowService = workflowService ?? throw new ArgumentNullException(nameof(workflowService));
            _auditTrailService = auditTrailService ?? throw new ArgumentNullException(nameof(auditTrailService));
            _platformRepository = platformRepository ?? throw new ArgumentNullException(nameof(platformRepository));
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
        [Route("GetCollaboratorRoles")]
        public async Task<IActionResult> GetCollaboratorRoles()
        {
            try
            {
                var roles = await _riskAssessmentRepository.GetCollaboratorRolesAsync();
                return Ok(roles);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"An unexpected error occurred while retrieving collaborator roles: {ex.Message}");
            }
        }

        [HttpGet]
        [Route("GetProjectCollaborators/{projectId}")]
        public async Task<IActionResult> GetProjectCollaborators(int projectId)
        {
            if (projectId <= 0)
                return BadRequest("Project ID must be greater than zero.");

            var userContext = AuditApiUserContext.FromHttpContext(HttpContext);
            if (!userContext.HasUserContext || !userContext.UserId.HasValue)
                return Unauthorized("User context headers are required.");

            if (!userContext.CanReviewAuditContent() && !userContext.CanSubmitEvidence())
                return StatusCode(403, "You do not have permission to view project collaborators.");

            try
            {
                var collaborators = await _riskAssessmentRepository.GetProjectCollaboratorsAsync(projectId);
                return Ok(collaborators);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"An unexpected error occurred while retrieving project collaborators: {ex.Message}");
            }
        }

        [HttpPost]
        [Route("SaveProjectCollaborators/{projectId}")]
        public async Task<IActionResult> SaveProjectCollaborators(int projectId, [FromBody] Affine.Engine.Model.Auditing.SaveAuditCollaboratorsRequest request)
        {
            if (projectId <= 0)
                return BadRequest("Project ID must be greater than zero.");

            if (request == null)
                return BadRequest("Collaborator assignment data is required.");

            var userContext = AuditApiUserContext.FromHttpContext(HttpContext);
            if (!userContext.HasUserContext || !userContext.UserId.HasValue)
                return Unauthorized("User context headers are required.");

            if (!userContext.CanManageAuditContent() && !userContext.CanManageDocumentSecurity())
                return StatusCode(403, "You do not have permission to manage project collaborators.");

            try
            {
                var collaborators = await _riskAssessmentRepository.SaveProjectCollaboratorsAsync(
                    projectId,
                    request,
                    userContext.UserId,
                    userContext.GetDisplayName());

                return Ok(collaborators);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"An unexpected error occurred while saving project collaborators: {ex.Message}");
            }
        }

        [HttpGet]
        [Route("GetReferenceCollaborators/{referenceId}")]
        public async Task<IActionResult> GetReferenceCollaborators(int referenceId)
        {
            if (referenceId <= 0)
                return BadRequest("Reference ID must be greater than zero.");

            var userContext = AuditApiUserContext.FromHttpContext(HttpContext);
            if (!userContext.HasUserContext || !userContext.UserId.HasValue)
                return Unauthorized("User context headers are required.");

            if (!userContext.CanReviewAuditContent() && !userContext.CanSubmitEvidence())
                return StatusCode(403, "You do not have permission to view audit file collaborators.");

            try
            {
                var collaborators = await _riskAssessmentRepository.GetReferenceCollaboratorsAsync(referenceId);
                return Ok(collaborators);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"An unexpected error occurred while retrieving audit file collaborators: {ex.Message}");
            }
        }

        [HttpPost]
        [Route("SaveReferenceCollaborators/{referenceId}")]
        public async Task<IActionResult> SaveReferenceCollaborators(int referenceId, [FromBody] Affine.Engine.Model.Auditing.SaveAuditCollaboratorsRequest request)
        {
            if (referenceId <= 0)
                return BadRequest("Reference ID must be greater than zero.");

            if (request == null)
                return BadRequest("Collaborator assignment data is required.");

            var userContext = AuditApiUserContext.FromHttpContext(HttpContext);
            if (!userContext.HasUserContext || !userContext.UserId.HasValue)
                return Unauthorized("User context headers are required.");

            if (!userContext.CanManageAuditContent() && !userContext.CanManageDocumentSecurity())
                return StatusCode(403, "You do not have permission to manage audit file collaborators.");

            try
            {
                var collaborators = await _riskAssessmentRepository.SaveReferenceCollaboratorsAsync(
                    referenceId,
                    request,
                    userContext.UserId,
                    userContext.GetDisplayName());

                return Ok(collaborators);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"An unexpected error occurred while saving audit file collaborators: {ex.Message}");
            }
        }

        [HttpPost]
        [Route("CreateDepartment")]
        public async Task<IActionResult> CreateDepartment([FromBody] Affine.Engine.Model.Auditing.Department department)
        {
            if (department == null)
                return BadRequest("Department data is required.");

            if (string.IsNullOrWhiteSpace(department.Name))
                return BadRequest("Department name is required.");

            try
            {
                var created = await _riskAssessmentRepository.CreateDepartmentAsync(department);
                return Ok(created);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"An unexpected error occurred while creating department: {ex.Message}");
            }
        }

        [HttpPut]
        [Route("UpdateDepartment/{id}")]
        public async Task<IActionResult> UpdateDepartment(int id, [FromBody] Affine.Engine.Model.Auditing.Department department)
        {
            if (id <= 0)
                return BadRequest("Department ID must be greater than zero.");

            if (department == null)
                return BadRequest("Department data is required.");

            if (string.IsNullOrWhiteSpace(department.Name))
                return BadRequest("Department name is required.");

            try
            {
                department.Id = id;
                var updated = await _riskAssessmentRepository.UpdateDepartmentAsync(department);
                if (updated == null)
                    return NotFound($"Department with ID {id} not found.");
                return Ok(updated);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"An unexpected error occurred while updating department: {ex.Message}");
            }
        }

        [HttpDelete]
        [Route("DeleteDepartment/{id}")]
        public async Task<IActionResult> DeleteDepartment(int id)
        {
            if (id <= 0)
                return BadRequest("Department ID must be greater than zero.");

            try
            {
                var deleted = await _riskAssessmentRepository.DeleteDepartmentAsync(id);
                if (!deleted)
                    return NotFound($"Department with ID {id} not found.");
                return Ok(new { Success = true });
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"An unexpected error occurred while deleting department: {ex.Message}");
            }
        }

        [HttpPost]
        [Route("CreateProject")]
        public async Task<IActionResult> CreateProject([FromBody] Affine.Engine.Model.Auditing.Project project)
        {
            if (project == null)
                return BadRequest("Project data is required.");

            if (string.IsNullOrWhiteSpace(project.Name))
                return BadRequest("Project name is required.");

            if (!project.StatusId.HasValue || project.StatusId.Value <= 0)
                return BadRequest("StatusId is required.");

            try
            {
                var created = await _riskAssessmentRepository.CreateProjectAsync(project);
                return Ok(created);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"An unexpected error occurred while creating project: {ex.Message}");
            }
        }

        [HttpPut]
        [Route("UpdateProject/{id}")]
        public async Task<IActionResult> UpdateProject(int id, [FromBody] Affine.Engine.Model.Auditing.Project project)
        {
            if (id <= 0)
                return BadRequest("Project ID must be greater than zero.");

            if (project == null)
                return BadRequest("Project data is required.");

            if (string.IsNullOrWhiteSpace(project.Name))
                return BadRequest("Project name is required.");

            if (!project.StatusId.HasValue || project.StatusId.Value <= 0)
                return BadRequest("StatusId is required.");

            try
            {
                project.Id = id;
                var updated = await _riskAssessmentRepository.UpdateProjectAsync(project);
                if (updated == null)
                    return NotFound($"Project with ID {id} not found.");
                return Ok(updated);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"An unexpected error occurred while updating project: {ex.Message}");
            }
        }

        [HttpDelete]
        [Route("DeleteProject/{id}")]
        public async Task<IActionResult> DeleteProject(int id)
        {
            if (id <= 0)
                return BadRequest("Project ID must be greater than zero.");

            try
            {
                var deleted = await _riskAssessmentRepository.DeleteProjectAsync(id);
                if (!deleted)
                    return NotFound($"Project with ID {id} not found.");
                return Ok(new { Success = true });
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"An unexpected error occurred while deleting project: {ex.Message}");
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
                if (ex.Message.Contains("locked for edits", StringComparison.OrdinalIgnoreCase))
                    return Conflict(ex.Message);
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
                if (ex.Message.Contains("locked for edits", StringComparison.OrdinalIgnoreCase))
                    return Conflict(ex.Message);
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
                if (ex.Message.Contains("locked for edits", StringComparison.OrdinalIgnoreCase))
                    return Conflict(ex.Message);
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
            var userContext = AuditApiUserContext.FromHttpContext(HttpContext);
            if (!userContext.HasUserContext || !userContext.UserId.HasValue)
                return Unauthorized("User context headers are required.");

            if (!userContext.CanStartWorkflows())
                return StatusCode(403, "You do not have permission to start control testing workflows.");

            if (referenceId <= 0)
                return BadRequest("Reference ID must be greater than zero.");

            if (request == null)
                return BadRequest("Control testing request data is required.");

            request.TesterId = userContext.UserId.Value.ToString();
                
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

                var parsedTesterId = userContext.UserId;
                var testerName = userContext.GetDisplayName($"User {request.TesterId}");

                var workflowResult = await _workflowService.StartWorkflowAsync(new Affine.Engine.Model.Auditing.AuditUniverse.StartAuditWorkflowRequest
                {
                    ReferenceId = referenceId,
                    EntityType = "Assessment",
                    EntityId = referenceId,
                    WorkflowDefinitionId = "Audit.Execution.ControlTesting.v1",
                    WorkflowDisplayName = "Control Testing Workflow",
                    ActivityId = "ControlTestingActivity",
                    Input = new Dictionary<string, object>
                    {
                        ["ControlId"] = request.ControlId,
                        ["RiskAssessmentId"] = referenceId.ToString(),
                        ["TesterName"] = testerName,
                        ["TesterId"] = request.TesterId,
                        ["TestFrequency"] = request.TestFrequency ?? "Not specified",
                        ["TestResult"] = "Pending"
                    },
                    InitiatedByUserId = parsedTesterId,
                    InitiatedByName = testerName,
                    AssigneeUserId = parsedTesterId,
                    AssigneeName = testerName,
                    TaskTitle = $"Perform control testing for {request.ControlId}",
                    TaskDescription = $"Execute control testing for control {request.ControlId} on assessment {referenceId}. Frequency: {request.TestFrequency ?? "Not specified"}.",
                    Priority = "High",
                    DueDate = DateTime.UtcNow.AddDays(5),
                    NotificationType = "Workflow",
                    NotificationTitle = $"Control testing started for {request.ControlId}",
                    NotificationMessage = $"A control testing workflow has started for assessment {referenceId}.",
                    Severity = "Info",
                    ActionUrl = $"/assessments/{referenceId}"
                });

                if (!workflowResult.Success)
                {
                    return StatusCode(502, workflowResult);
                }

                if (workflowResult.Workflow != null)
                {
                    try
                    {
                        await _platformRepository.RecordUsageEventAsync(new Affine.Engine.Model.Auditing.AuditUniverse.RecordAuditUsageEventRequest
                        {
                            ModuleName = "assessments",
                            FeatureName = "control_testing",
                            EventName = "started",
                            ReferenceId = referenceId,
                            PerformedByUserId = parsedTesterId,
                            PerformedByName = testerName,
                            RoleName = userContext.Role,
                            Source = "RiskAssessmentController",
                            MetadataJson = System.Text.Json.JsonSerializer.Serialize(new
                            {
                                request.ControlId,
                                workflowResult.Workflow.WorkflowInstanceId
                            })
                        });
                    }
                    catch (Exception telemetryEx)
                    {
                        Console.WriteLine($"Telemetry write failed during control testing start: {telemetryEx.Message}");
                    }
                    await _auditTrailService.RecordEventAsync(new Affine.Engine.Model.Auditing.AuditUniverse.CreateAuditTrailEventRequest
                    {
                        ReferenceId = referenceId,
                        EntityType = "Assessment",
                        EntityId = referenceId.ToString(),
                        Category = "Workflow",
                        Action = "Start",
                        Summary = $"Started control testing workflow for {request.ControlId}",
                        PerformedByUserId = parsedTesterId,
                        PerformedByName = testerName,
                        WorkflowInstanceId = workflowResult.Workflow.WorkflowInstanceId,
                        CorrelationId = request.ControlId,
                        Source = "Assessment",
                        DetailsJson = System.Text.Json.JsonSerializer.Serialize(new
                        {
                            request.ControlId,
                            request.TestFrequency,
                            workflowResult.Workflow.WorkflowDefinitionId,
                            workflowResult.Workflow.WorkflowInstanceId
                        })
                    });
                }

                return Ok(new
                {
                    Success = true,
                    Message = "Control testing workflow started successfully",
                    WorkflowInstanceId = workflowResult.WorkflowInstanceId,
                    Workflow = workflowResult.Workflow
                });
            }
            catch (InvalidOperationException ex)
            {
                if (ex.Message.Contains("locked for edits", StringComparison.OrdinalIgnoreCase))
                    return Conflict(ex.Message);
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
                if (ex.Message.Contains("locked for edits", StringComparison.OrdinalIgnoreCase))
                    return Conflict(ex.Message);
                return StatusCode(500, $"Database operation failed: {ex.Message}");
            }
            catch (Exception ex)
            {
                return StatusCode(500, "An unexpected error occurred while creating reference data.");
            }
        }

        [HttpPut]
        [Route("UpdateReference/{referenceId}")]
        public async Task<IActionResult> UpdateReference(int referenceId, [FromBody] RiskAssessmentReferenceInput request)
        {
            if (referenceId <= 0)
                return BadRequest("Reference ID must be greater than zero.");

            if (!ModelState.IsValid)
                return BadRequest(ModelState);

            if (request == null)
                return BadRequest("Reference data is required.");

            try
            {
                var result = await _riskAssessmentRepository.UpdateRiskAssessmentReferenceAsync(referenceId, request);
                
                if (!result)
                    return NotFound($"Risk Assessment Reference with ID {referenceId} not found.");

                return Ok(new { 
                    Success = true, 
                    ReferenceId = referenceId, 
                    Message = "Reference updated successfully." 
                });
            }
            catch (InvalidOperationException ex)
            {
                return StatusCode(500, $"Database operation failed: {ex.Message}");
            }
            catch (Exception ex)
            {
                return StatusCode(500, "An unexpected error occurred while updating reference data.");
            }
        }

        [HttpDelete]
        [Route("DeleteRiskAssessment/{referenceId}/{assessmentId}")]
        public async Task<IActionResult> DeleteRiskAssessment(int referenceId, int assessmentId)
        {
            if (referenceId <= 0)
                return BadRequest("Reference ID must be greater than zero.");

            if (assessmentId <= 0)
                return BadRequest("Assessment ID must be greater than zero.");

            try
            {
                var result = await _riskAssessmentRepository.DeleteRiskAssessmentAsync(assessmentId, referenceId);

                if (!result)
                    return NotFound($"Risk Assessment with ID {assessmentId} not found for Reference ID {referenceId}.");

                return Ok(new { 
                    Success = true, 
                    Message = "Risk assessment deleted successfully.",
                    ReferenceId = referenceId,
                    AssessmentId = assessmentId
                });
            }
            catch (InvalidOperationException ex)
            {
                return StatusCode(500, $"Database operation failed: {ex.Message}");
            }
            catch (Exception ex)
            {
                return StatusCode(500, "An unexpected error occurred while deleting risk assessment data.");
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
