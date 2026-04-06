using Affine.Engine.Model.Auditing.AuditUniverse;
using Affine.Engine.Repository.Auditing;
using Affine.Engine.Services;
using Microsoft.AspNetCore.Mvc;
using Affine.Auditing.API.Security;
using System.Linq;

namespace Affine.Auditing.API.Controllers
{
    [ApiController]
    [Route("api/v1/[controller]")]
    public class AuditWorkflowController : ControllerBase
    {
        private readonly IAuditWorkflowService _workflowService;
        private readonly IAuditTrailService _auditTrailService;
        private readonly IAuditPlatformRepository _platformRepository;
        private readonly IAuditReviewsRepository _reviewsRepository;

        public AuditWorkflowController(
            IAuditWorkflowService workflowService,
            IAuditTrailService auditTrailService,
            IAuditPlatformRepository platformRepository,
            IAuditReviewsRepository reviewsRepository)
        {
            _workflowService = workflowService;
            _auditTrailService = auditTrailService;
            _platformRepository = platformRepository;
            _reviewsRepository = reviewsRepository;
        }

        [HttpPost("StartPlanningApproval")]
        public async Task<IActionResult> StartPlanningApproval([FromBody] StartPlanningApprovalWorkflowRequest request)
        {
            var userContext = GetUserContext();
            var permissionResult = RequireWorkflowStarter(userContext);
            if (permissionResult != null)
            {
                return permissionResult;
            }

            if (request == null || request.ReferenceId <= 0)
            {
                return BadRequest("Reference ID is required");
            }

            return await StartDomainWorkflowAsync(new StartAuditWorkflowRequest
            {
                ReferenceId = request.ReferenceId,
                EntityType = "Planning",
                EntityId = request.ReferenceId,
                WorkflowDefinitionId = "Audit.Planning.PlanningApproval.v1",
                WorkflowDisplayName = "Planning Approval Workflow",
                ActivityId = "PlanningApprovalActivity",
                Input = new Dictionary<string, object>
                {
                    ["ReferenceId"] = request.ReferenceId,
                    ["EngagementTitle"] = request.EngagementTitle ?? $"Assessment {request.ReferenceId}",
                    ["Notes"] = request.Notes ?? ""
                },
                InitiatedByUserId = userContext.UserId,
                InitiatedByName = userContext.GetDisplayName(request.RequestedByName ?? "Audit User"),
                AssigneeUserId = request.ApproverUserId,
                AssigneeName = request.ApproverName,
                TaskTitle = $"Approve planning scope for {request.EngagementTitle ?? $"assessment {request.ReferenceId}"}",
                TaskDescription = "Review planning, scope, and engagement setup before fieldwork begins.",
                Priority = "High",
                DueDate = request.DueDate ?? DateTime.UtcNow.AddDays(3),
                NotificationType = "Approval",
                NotificationTitle = $"Planning approval requested for assessment {request.ReferenceId}",
                NotificationMessage = "A planning approval workflow has been started and is awaiting review.",
                Severity = "Info",
                ActionUrl = $"/assessments/{request.ReferenceId}"
            });
        }

        [HttpPost("StartAnnualAuditPlanApproval")]
        public async Task<IActionResult> StartAnnualAuditPlanApproval([FromBody] StartAnnualAuditPlanApprovalWorkflowRequest request)
        {
            var userContext = GetUserContext();
            var permissionResult = RequireWorkflowStarter(userContext);
            if (permissionResult != null)
            {
                return permissionResult;
            }

            if (request == null || request.ReferenceId <= 0)
            {
                return BadRequest("Reference ID is required");
            }

            var planLabel = string.IsNullOrWhiteSpace(request.AnnualPlanName)
                ? $"Annual audit plan {request.PlanYear ?? DateTime.UtcNow.Year}"
                : request.AnnualPlanName;

            return await StartDomainWorkflowAsync(new StartAuditWorkflowRequest
            {
                ReferenceId = request.ReferenceId,
                EntityType = "AnnualPlan",
                EntityId = request.ReferenceId,
                WorkflowDefinitionId = "Audit.Planning.AnnualPlanApproval.v1",
                WorkflowDisplayName = "Annual Audit Plan Approval Workflow",
                ActivityId = "AnnualPlanApprovalActivity",
                Input = new Dictionary<string, object>
                {
                    ["ReferenceId"] = request.ReferenceId,
                    ["AnnualPlanName"] = request.AnnualPlanName ?? "",
                    ["PlanYear"] = request.PlanYear,
                    ["Notes"] = request.Notes ?? ""
                },
                InitiatedByUserId = userContext.UserId,
                InitiatedByName = userContext.GetDisplayName(request.RequestedByName ?? "Audit User"),
                AssigneeUserId = request.ApproverUserId,
                AssigneeName = request.ApproverName,
                TaskTitle = $"Approve annual audit plan: {planLabel}",
                TaskDescription = "Review annual audit coverage priorities, planned engagements, and risk universe focus areas.",
                Priority = "High",
                DueDate = request.DueDate ?? DateTime.UtcNow.AddDays(5),
                NotificationType = "Approval",
                NotificationTitle = $"Annual audit plan approval requested for assessment {request.ReferenceId}",
                NotificationMessage = "An annual audit plan approval workflow has been started and is awaiting review.",
                Severity = "Info",
                ActionUrl = $"/assessments/{request.ReferenceId}"
            });
        }

        [HttpPost("StartScopeApproval")]
        public async Task<IActionResult> StartScopeApproval([FromBody] StartScopeApprovalWorkflowRequest request)
        {
            var userContext = GetUserContext();
            var permissionResult = RequireWorkflowStarter(userContext);
            if (permissionResult != null)
            {
                return permissionResult;
            }

            if (request == null || request.ReferenceId <= 0)
            {
                return BadRequest("Reference ID is required");
            }

            return await StartDomainWorkflowAsync(new StartAuditWorkflowRequest
            {
                ReferenceId = request.ReferenceId,
                EntityType = "Scope",
                EntityId = request.ReferenceId,
                WorkflowDefinitionId = "Audit.Planning.ScopeApproval.v1",
                WorkflowDisplayName = "Scope Approval Workflow",
                ActivityId = "ScopeApprovalActivity",
                Input = new Dictionary<string, object>
                {
                    ["ReferenceId"] = request.ReferenceId,
                    ["ScopeSummary"] = request.ScopeSummary ?? $"Scope for assessment {request.ReferenceId}",
                    ["Notes"] = request.Notes ?? ""
                },
                InitiatedByUserId = userContext.UserId,
                InitiatedByName = userContext.GetDisplayName(request.RequestedByName ?? "Audit User"),
                AssigneeUserId = request.ApproverUserId,
                AssigneeName = request.ApproverName,
                TaskTitle = $"Approve scope for assessment {request.ReferenceId}",
                TaskDescription = "Review scope items, boundaries, and linked business processes.",
                Priority = "High",
                DueDate = request.DueDate ?? DateTime.UtcNow.AddDays(2),
                NotificationType = "Approval",
                NotificationTitle = $"Scope approval requested for assessment {request.ReferenceId}",
                NotificationMessage = "A scope approval workflow has been started and is awaiting review.",
                Severity = "Info",
                ActionUrl = $"/assessments/{request.ReferenceId}"
            });
        }

        [HttpPost("StartWalkthrough")]
        public async Task<IActionResult> StartWalkthrough([FromBody] StartWalkthroughWorkflowRequest request)
        {
            var userContext = GetUserContext();
            var permissionResult = RequireWorkflowStarter(userContext);
            if (permissionResult != null)
            {
                return permissionResult;
            }

            if (request == null || request.ReferenceId <= 0 || request.WalkthroughId <= 0)
            {
                return BadRequest("Reference ID and walkthrough ID are required");
            }

            var processLabel = string.IsNullOrWhiteSpace(request.ProcessName)
                ? $"walkthrough {request.WalkthroughId}"
                : request.ProcessName;

            return await StartDomainWorkflowAsync(new StartAuditWorkflowRequest
            {
                ReferenceId = request.ReferenceId,
                EntityType = "Walkthrough",
                EntityId = request.WalkthroughId,
                WorkflowDefinitionId = "Audit.Execution.WalkthroughReview.v1",
                WorkflowDisplayName = "Walkthrough Review Workflow",
                ActivityId = "WalkthroughReviewActivity",
                Input = new Dictionary<string, object>
                {
                    ["ReferenceId"] = request.ReferenceId,
                    ["WalkthroughId"] = request.WalkthroughId,
                    ["ProcessName"] = request.ProcessName ?? "",
                    ["Notes"] = request.Notes ?? ""
                },
                InitiatedByUserId = userContext.UserId,
                InitiatedByName = userContext.GetDisplayName(request.RequestedByName ?? "Audit User"),
                AssigneeUserId = request.ReviewerUserId,
                AssigneeName = request.ReviewerName,
                TaskTitle = $"Review walkthrough: {processLabel}",
                TaskDescription = $"Review walkthrough narrative, participants, and exceptions for {processLabel}.",
                Priority = "Medium",
                DueDate = request.DueDate ?? DateTime.UtcNow.AddDays(3),
                NotificationType = "Review",
                NotificationTitle = $"Walkthrough review requested for {processLabel}",
                NotificationMessage = "A walkthrough review workflow has been started.",
                Severity = "Info",
                ActionUrl = $"/assessments/{request.ReferenceId}"
            });
        }

        [HttpPost("StartWorkingPaperReview")]
        public async Task<IActionResult> StartWorkingPaperReview([FromBody] StartWorkingPaperReviewWorkflowRequest request)
        {
            var userContext = GetUserContext();
            var permissionResult = RequireWorkflowStarter(userContext);
            if (permissionResult != null)
            {
                return permissionResult;
            }

            if (request == null || request.ReferenceId <= 0 || request.WorkingPaperId <= 0)
            {
                return BadRequest("Reference ID and working paper ID are required");
            }

            var workingPaperLabel = string.IsNullOrWhiteSpace(request.WorkingPaperCode)
                ? request.WorkingPaperTitle ?? $"working paper {request.WorkingPaperId}"
                : request.WorkingPaperCode;

            return await StartDomainWorkflowAsync(new StartAuditWorkflowRequest
            {
                ReferenceId = request.ReferenceId,
                EntityType = "WorkingPaper",
                EntityId = request.WorkingPaperId,
                WorkflowDefinitionId = "Audit.Execution.WorkpaperReview.v1",
                WorkflowDisplayName = "Working Paper Review Workflow",
                ActivityId = "WorkpaperReviewActivity",
                Input = new Dictionary<string, object>
                {
                    ["ReferenceId"] = request.ReferenceId,
                    ["WorkingPaperId"] = request.WorkingPaperId,
                    ["WorkingPaperCode"] = request.WorkingPaperCode ?? "",
                    ["WorkingPaperTitle"] = request.WorkingPaperTitle ?? "",
                    ["Notes"] = request.Notes ?? ""
                },
                InitiatedByUserId = userContext.UserId,
                InitiatedByName = userContext.GetDisplayName(request.RequestedByName ?? "Audit User"),
                AssigneeUserId = request.ReviewerUserId,
                AssigneeName = request.ReviewerName,
                TaskTitle = $"Review working paper {workingPaperLabel}",
                TaskDescription = $"Review and sign off working paper {request.WorkingPaperTitle ?? workingPaperLabel}.",
                Priority = "High",
                DueDate = request.DueDate ?? DateTime.UtcNow.AddDays(4),
                NotificationType = "Review",
                NotificationTitle = $"Working paper review requested for {workingPaperLabel}",
                NotificationMessage = "A working paper review workflow has been started.",
                Severity = "Info",
                ActionUrl = $"/assessments/{request.ReferenceId}"
            });
        }

        [HttpPost("StartFindingReview")]
        public async Task<IActionResult> StartFindingReview([FromBody] StartFindingReviewWorkflowRequest request)
        {
            var userContext = GetUserContext();
            var permissionResult = RequireWorkflowStarter(userContext);
            if (permissionResult != null)
            {
                return permissionResult;
            }

            if (request == null || request.ReferenceId <= 0)
            {
                return BadRequest("Reference ID is required");
            }

            var findingLabel = request.FindingNumber
                ?? request.FindingTitle
                ?? (request.FindingId.HasValue ? $"finding {request.FindingId}" : $"assessment {request.ReferenceId} findings");

            return await StartDomainWorkflowAsync(new StartAuditWorkflowRequest
            {
                ReferenceId = request.ReferenceId,
                EntityType = "Finding",
                EntityId = request.FindingId,
                WorkflowDefinitionId = "Audit.Reporting.FindingApproval.v1",
                WorkflowDisplayName = "Finding Review Workflow",
                ActivityId = "FindingApprovalActivity",
                Input = new Dictionary<string, object>
                {
                    ["ReferenceId"] = request.ReferenceId,
                    ["FindingId"] = request.FindingId,
                    ["FindingNumber"] = request.FindingNumber ?? "",
                    ["FindingTitle"] = request.FindingTitle ?? "",
                    ["Notes"] = request.Notes ?? ""
                },
                InitiatedByUserId = userContext.UserId,
                InitiatedByName = userContext.GetDisplayName(request.RequestedByName ?? "Audit User"),
                AssigneeUserId = request.ReviewerUserId,
                AssigneeName = request.ReviewerName,
                TaskTitle = $"Review finding {findingLabel}",
                TaskDescription = "Review findings and recommendations before reporting.",
                Priority = "High",
                DueDate = request.DueDate ?? DateTime.UtcNow.AddDays(3),
                NotificationType = "Review",
                NotificationTitle = $"Finding review requested for assessment {request.ReferenceId}",
                NotificationMessage = "A finding review workflow has been started.",
                Severity = "Info",
                ActionUrl = $"/assessments/{request.ReferenceId}"
            });
        }

        [HttpPost("StartManagementResponse")]
        public async Task<IActionResult> StartManagementResponse([FromBody] StartManagementResponseWorkflowRequest request)
        {
            var userContext = GetUserContext();
            var permissionResult = RequireWorkflowStarter(userContext);
            if (permissionResult != null)
            {
                return permissionResult;
            }

            if (request == null || request.ReferenceId <= 0 || request.RecommendationId <= 0)
            {
                return BadRequest("Reference ID and recommendation ID are required");
            }

            var recommendationLabel = request.RecommendationNumber
                ?? request.RecommendationTitle
                ?? $"recommendation {request.RecommendationId}";

            return await StartDomainWorkflowAsync(new StartAuditWorkflowRequest
            {
                ReferenceId = request.ReferenceId,
                EntityType = "Recommendation",
                EntityId = request.RecommendationId,
                WorkflowDefinitionId = "Audit.Reporting.ManagementResponse.v1",
                WorkflowDisplayName = "Management Response Workflow",
                ActivityId = "ManagementResponseActivity",
                Input = new Dictionary<string, object>
                {
                    ["ReferenceId"] = request.ReferenceId,
                    ["RecommendationId"] = request.RecommendationId,
                    ["RecommendationNumber"] = request.RecommendationNumber ?? "",
                    ["RecommendationTitle"] = request.RecommendationTitle ?? "",
                    ["Notes"] = request.Notes ?? ""
                },
                InitiatedByUserId = userContext.UserId,
                InitiatedByName = userContext.GetDisplayName(request.RequestedByName ?? "Audit User"),
                AssigneeUserId = request.ResponsibleUserId,
                AssigneeName = request.ResponsibleName,
                TaskTitle = $"Provide management response for {recommendationLabel}",
                TaskDescription = "Capture management response, action plan, and agreed target date.",
                Priority = "High",
                DueDate = request.DueDate ?? DateTime.UtcNow.AddDays(5),
                NotificationType = "Response",
                NotificationTitle = $"Management response requested for {recommendationLabel}",
                NotificationMessage = "A management response workflow has been started.",
                Severity = "Info",
                ActionUrl = $"/assessments/{request.ReferenceId}"
            });
        }

        [HttpPost("StartRemediationFollowUp")]
        public async Task<IActionResult> StartRemediationFollowUp([FromBody] StartRemediationFollowUpWorkflowRequest request)
        {
            var userContext = GetUserContext();
            var permissionResult = RequireWorkflowStarter(userContext);
            if (permissionResult != null)
            {
                return permissionResult;
            }

            if (request == null || request.ReferenceId <= 0 || request.RecommendationId <= 0)
            {
                return BadRequest("Reference ID and recommendation ID are required");
            }

            var recommendationLabel = request.RecommendationNumber
                ?? request.RecommendationTitle
                ?? $"recommendation {request.RecommendationId}";

            return await StartDomainWorkflowAsync(new StartAuditWorkflowRequest
            {
                ReferenceId = request.ReferenceId,
                EntityType = "Recommendation",
                EntityId = request.RecommendationId,
                WorkflowDefinitionId = "Audit.FollowUp.RemediationReview.v1",
                WorkflowDisplayName = "Remediation Follow-Up Workflow",
                ActivityId = "RemediationFollowUpActivity",
                Input = new Dictionary<string, object>
                {
                    ["ReferenceId"] = request.ReferenceId,
                    ["RecommendationId"] = request.RecommendationId,
                    ["RecommendationNumber"] = request.RecommendationNumber ?? "",
                    ["RecommendationTitle"] = request.RecommendationTitle ?? "",
                    ["Notes"] = request.Notes ?? ""
                },
                InitiatedByUserId = userContext.UserId,
                InitiatedByName = userContext.GetDisplayName(request.RequestedByName ?? "Audit User"),
                AssigneeUserId = request.ReviewerUserId,
                AssigneeName = request.ReviewerName,
                TaskTitle = $"Perform remediation follow-up for {recommendationLabel}",
                TaskDescription = "Verify management action implementation and close the follow-up loop.",
                Priority = "High",
                DueDate = request.DueDate ?? DateTime.UtcNow.AddDays(10),
                NotificationType = "FollowUp",
                NotificationTitle = $"Remediation follow-up requested for {recommendationLabel}",
                NotificationMessage = "A remediation follow-up workflow has been started.",
                Severity = "Info",
                ActionUrl = $"/assessments/{request.ReferenceId}"
            });
        }

        [HttpPost("StartFinalReportSignOff")]
        public async Task<IActionResult> StartFinalReportSignOff([FromBody] StartFinalReportSignOffWorkflowRequest request)
        {
            var userContext = GetUserContext();
            var permissionResult = RequireWorkflowStarter(userContext);
            if (permissionResult != null)
            {
                return permissionResult;
            }

            if (request == null || request.ReferenceId <= 0)
            {
                return BadRequest("Reference ID is required");
            }

            return await StartDomainWorkflowAsync(new StartAuditWorkflowRequest
            {
                ReferenceId = request.ReferenceId,
                EntityType = "Assessment",
                EntityId = request.ReferenceId,
                WorkflowDefinitionId = "Audit.Reporting.FinalSignOff.v1",
                WorkflowDisplayName = "Final Report Sign-Off Workflow",
                ActivityId = "FinalSignOffActivity",
                Input = new Dictionary<string, object>
                {
                    ["ReferenceId"] = request.ReferenceId,
                    ["ReportTitle"] = request.ReportTitle ?? $"Audit report {request.ReferenceId}",
                    ["Notes"] = request.Notes ?? ""
                },
                InitiatedByUserId = userContext.UserId,
                InitiatedByName = userContext.GetDisplayName(request.RequestedByName ?? "Audit User"),
                AssigneeUserId = request.ApproverUserId,
                AssigneeName = request.ApproverName,
                TaskTitle = $"Sign off final report for assessment {request.ReferenceId}",
                TaskDescription = "Review the final audit pack and provide final sign-off.",
                Priority = "High",
                DueDate = request.DueDate ?? DateTime.UtcNow.AddDays(5),
                NotificationType = "Approval",
                NotificationTitle = $"Final report sign-off requested for assessment {request.ReferenceId}",
                NotificationMessage = "A final report sign-off workflow has been started.",
                Severity = "Info",
                ActionUrl = $"/assessments/{request.ReferenceId}"
            });
        }

        [HttpPost("Start")]
        public async Task<IActionResult> Start([FromBody] StartAuditWorkflowRequest request)
        {
            var userContext = GetUserContext();
            var permissionResult = RequireWorkflowStarter(userContext);
            if (permissionResult != null)
            {
                return permissionResult;
            }

            if (request == null || string.IsNullOrWhiteSpace(request.WorkflowDefinitionId))
            {
                return BadRequest("Workflow definition is required");
            }

            request.InitiatedByUserId = userContext.UserId;
            request.InitiatedByName = userContext.GetDisplayName(request.InitiatedByName ?? "Audit User");
            return await StartDomainWorkflowAsync(request);
        }

        [HttpGet("GetWorkflowInstance/{workflowInstanceId}")]
        public async Task<IActionResult> GetWorkflowInstance(string workflowInstanceId)
        {
            try
            {
                return Ok(await _workflowService.GetWorkflowInstanceAsync(workflowInstanceId));
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpGet("GetWorkflowInstances")]
        public async Task<IActionResult> GetWorkflowInstances([FromQuery] bool activeOnly = false)
        {
            try
            {
                return Ok(await _workflowService.GetWorkflowInstancesAsync(activeOnly));
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpGet("GetWorkflowInstancesByReference/{referenceId}")]
        public async Task<IActionResult> GetWorkflowInstancesByReference(int referenceId)
        {
            try
            {
                return Ok(await _workflowService.GetWorkflowInstancesByReferenceAsync(referenceId));
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpGet("GetTimeline/{referenceId}")]
        public async Task<IActionResult> GetTimeline(int referenceId, [FromQuery] int limit = 100)
        {
            try
            {
                return Ok(await _workflowService.GetWorkflowTimelineByReferenceAsync(referenceId, limit));
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpPut("UpdateWorkflowStatus/{workflowInstanceId}")]
        public async Task<IActionResult> UpdateWorkflowStatus(string workflowInstanceId, [FromBody] UpdateAuditWorkflowInstanceStatusRequest request)
        {
            if (request == null)
            {
                return BadRequest("Workflow status update data is required");
            }

            if (!string.IsNullOrWhiteSpace(request.WorkflowInstanceId) && request.WorkflowInstanceId != workflowInstanceId)
            {
                return BadRequest("Workflow instance mismatch");
            }

            try
            {
                request.WorkflowInstanceId = workflowInstanceId;
                return Ok(await _workflowService.UpdateWorkflowStatusAsync(request));
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpPost("SyncElsaState")]
        public async Task<IActionResult> SyncElsaState([FromBody] SyncAuditWorkflowStateRequest request)
        {
            if (request == null || string.IsNullOrWhiteSpace(request.WorkflowInstanceId))
            {
                return BadRequest("Workflow instance ID is required");
            }

            try
            {
                var result = await _workflowService.SyncWorkflowStateAsync(request);
                if (!result.Success)
                {
                    return NotFound(result);
                }

                return Ok(result);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpGet("GetInbox")]
        public async Task<IActionResult> GetInbox([FromQuery] int? userId)
        {
            var userContext = GetUserContext();
            var scopedUser = ResolveScopedUserId(userContext, userId);
            if (scopedUser.Error != null)
            {
                return scopedUser.Error;
            }

            try
            {
                return Ok(await _workflowService.GetInboxAsync(scopedUser.UserId));
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpGet("GetTasks")]
        public async Task<IActionResult> GetTasks([FromQuery] int? userId, [FromQuery] bool pendingOnly = false)
        {
            var userContext = GetUserContext();
            var scopedUser = ResolveScopedUserId(userContext, userId);
            if (scopedUser.Error != null)
            {
                return scopedUser.Error;
            }

            try
            {
                return Ok(await _workflowService.GetWorkflowTasksByUserAsync(scopedUser.UserId, pendingOnly));
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpPost("CreateTask")]
        public async Task<IActionResult> CreateTask([FromBody] CreateAuditWorkflowTaskRequest request)
        {
            var userContext = GetUserContext();
            var permissionResult = RequireWorkflowStarter(userContext);
            if (permissionResult != null)
            {
                return permissionResult;
            }

            if (request == null || string.IsNullOrWhiteSpace(request.WorkflowInstanceId) || string.IsNullOrWhiteSpace(request.TaskTitle))
            {
                return BadRequest("Workflow instance and task title are required");
            }

            try
            {
                return Ok(await _workflowService.CreateWorkflowTaskAsync(request));
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpPut("CompleteTask/{taskId}")]
        public async Task<IActionResult> CompleteTask(int taskId, [FromBody] CompleteAuditWorkflowTaskRequest request)
        {
            var userContext = GetUserContext();
            var userContextResult = RequireUserContext(userContext);
            if (userContextResult != null)
            {
                return userContextResult;
            }

            request ??= new CompleteAuditWorkflowTaskRequest();

            try
            {
                if (!userContext.CanCompleteAnyWorkflowTask())
                {
                    var userTasks = await _workflowService.GetWorkflowTasksByUserAsync(userContext.UserId, pendingOnly: false);
                    var matchingTask = userTasks.FirstOrDefault(task => task.Id == taskId);
                    if (!userContext.CanCompleteTask(matchingTask))
                    {
                        return StatusCode(403, "You do not have permission to complete this workflow task.");
                    }
                }

                request.TaskId = taskId;
                request.CompletedByUserId = userContext.UserId;
                var task = await _workflowService.CompleteWorkflowTaskAsync(request);
                if (task != null)
                {
                    await _reviewsRepository.CompleteOpenTasksByWorkflowInstanceAsync(new CompleteAuditTaskRequest
                    {
                        WorkflowInstanceId = task.WorkflowInstanceId,
                        CompletedByUserId = request.CompletedByUserId,
                        CompletionNotes = request.CompletionNotes
                    });

                    var completedReview = await _reviewsRepository.CompleteReviewByWorkflowInstanceAsync(new CompleteAuditReviewRequest
                    {
                        WorkflowInstanceId = task.WorkflowInstanceId,
                        Status = "Completed",
                        CompletedByUserId = request.CompletedByUserId,
                        Summary = string.IsNullOrWhiteSpace(request.CompletionNotes)
                            ? $"Completed review task: {task.TaskTitle}"
                            : request.CompletionNotes
                    });

                    if (completedReview != null)
                    {
                        await _reviewsRepository.AddSignoffAsync(new CreateAuditSignoffRequest
                        {
                            ReferenceId = completedReview.ReferenceId,
                            EntityType = string.IsNullOrWhiteSpace(completedReview.EntityType) ? "Review" : completedReview.EntityType,
                            EntityId = completedReview.EntityId,
                            ReviewId = completedReview.Id,
                            WorkflowInstanceId = completedReview.WorkflowInstanceId,
                            SignoffType = string.IsNullOrWhiteSpace(completedReview.ReviewType) ? "Review Completion" : completedReview.ReviewType,
                            SignoffLevel = completedReview.EntityType,
                            Status = "Signed",
                            SignedByUserId = request.CompletedByUserId,
                            SignedByName = userContext.GetDisplayName(task.AssigneeName ?? "Workflow User"),
                            Comment = request.CompletionNotes
                        });
                    }

                    try
                    {
                        await _platformRepository.RecordUsageEventAsync(new RecordAuditUsageEventRequest
                        {
                            ModuleName = "workflows",
                            FeatureName = "task_completion",
                            EventName = "completed",
                            ReferenceId = task.ReferenceId,
                            PerformedByUserId = request.CompletedByUserId,
                            PerformedByName = userContext.GetDisplayName(task.AssigneeName ?? "Workflow User"),
                            RoleName = userContext.Role,
                            Source = "AuditWorkflowController",
                            MetadataJson = System.Text.Json.JsonSerializer.Serialize(new
                            {
                                task.Id,
                                task.TaskTitle,
                                task.WorkflowInstanceId
                            })
                        });
                    }
                    catch (Exception telemetryEx)
                    {
                        Console.WriteLine($"Telemetry write failed during workflow task completion: {telemetryEx.Message}");
                    }
                    await _auditTrailService.RecordEventAsync(new CreateAuditTrailEventRequest
                    {
                        ReferenceId = task.ReferenceId,
                        EntityType = string.IsNullOrWhiteSpace(task.EntityType) ? "WorkflowTask" : task.EntityType,
                        EntityId = task.EntityId?.ToString(),
                        Category = "Workflow",
                        Action = "Complete",
                        Summary = $"Completed workflow task: {task.TaskTitle}",
                        PerformedByUserId = request.CompletedByUserId,
                        PerformedByName = userContext.GetDisplayName(task.AssigneeName ?? "Workflow User"),
                        WorkflowInstanceId = task.WorkflowInstanceId,
                        Source = "WorkflowInbox",
                        DetailsJson = System.Text.Json.JsonSerializer.Serialize(new
                        {
                            task.Id,
                            task.TaskTitle,
                            task.Status,
                            task.CompletedAt,
                            request.CompletionNotes
                        })
                    });
                }

                return Ok(task);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpGet("GetNotifications")]
        public async Task<IActionResult> GetNotifications([FromQuery] int? userId, [FromQuery] bool unreadOnly = false)
        {
            var userContext = GetUserContext();
            var scopedUser = ResolveScopedUserId(userContext, userId);
            if (scopedUser.Error != null)
            {
                return scopedUser.Error;
            }

            try
            {
                return Ok(await _workflowService.GetNotificationsByUserAsync(scopedUser.UserId, unreadOnly));
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpPost("CreateNotification")]
        public async Task<IActionResult> CreateNotification([FromBody] CreateAuditNotificationRequest request)
        {
            var userContext = GetUserContext();
            var permissionResult = RequireWorkflowAdmin(userContext);
            if (permissionResult != null)
            {
                return permissionResult;
            }

            if (request == null || string.IsNullOrWhiteSpace(request.Title))
            {
                return BadRequest("Notification title is required");
            }

            try
            {
                return Ok(await _workflowService.CreateNotificationAsync(request));
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpPut("MarkNotificationRead/{notificationId}")]
        public async Task<IActionResult> MarkNotificationRead(int notificationId, [FromBody] MarkAuditNotificationReadRequest request)
        {
            var userContext = GetUserContext();
            var userContextResult = RequireUserContext(userContext);
            if (userContextResult != null)
            {
                return userContextResult;
            }

            request ??= new MarkAuditNotificationReadRequest();

            try
            {
                request.NotificationId = notificationId;
                request.ReadByUserId = userContext.UserId;
                return Ok(new { success = await _workflowService.MarkNotificationReadAsync(request), notificationId });
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpPost("RunReminderSweep")]
        public async Task<IActionResult> RunReminderSweep()
        {
            var userContext = GetUserContext();
            var permissionResult = RequireWorkflowAdmin(userContext);
            if (permissionResult != null)
            {
                return permissionResult;
            }

            try
            {
                var result = await _workflowService.RunReminderSweepAsync();
                try
                {
                    await _platformRepository.RecordUsageEventAsync(new RecordAuditUsageEventRequest
                    {
                        ModuleName = "workflows",
                        FeatureName = "reminder_sweep",
                        EventName = "completed",
                        PerformedByUserId = userContext.UserId,
                        PerformedByName = userContext.GetDisplayName("Audit User"),
                        RoleName = userContext.Role,
                        Source = "AuditWorkflowController",
                        MetadataJson = System.Text.Json.JsonSerializer.Serialize(result)
                    });
                }
                catch (Exception telemetryEx)
                {
                    Console.WriteLine($"Telemetry write failed during reminder sweep: {telemetryEx.Message}");
                }
                return Ok(result);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        private AuditApiUserContext GetUserContext()
            => AuditApiUserContext.FromHttpContext(HttpContext);

        private IActionResult? RequireUserContext(AuditApiUserContext userContext)
        {
            if (!userContext.HasUserContext || !userContext.UserId.HasValue)
            {
                return Unauthorized("User context headers are required.");
            }

            return null;
        }

        private IActionResult? RequireWorkflowStarter(AuditApiUserContext userContext)
        {
            var userContextResult = RequireUserContext(userContext);
            if (userContextResult != null)
            {
                return userContextResult;
            }

            if (!userContext.CanStartWorkflows())
            {
                return StatusCode(403, "You do not have permission to start audit workflows.");
            }

            return null;
        }

        private IActionResult? RequireWorkflowAdmin(AuditApiUserContext userContext)
        {
            var userContextResult = RequireUserContext(userContext);
            if (userContextResult != null)
            {
                return userContextResult;
            }

            if (!userContext.CanRunWorkflowAdminActions())
            {
                return StatusCode(403, "You do not have permission to run workflow administration actions.");
            }

            return null;
        }

        private (int? UserId, IActionResult? Error) ResolveScopedUserId(AuditApiUserContext userContext, int? requestedUserId)
        {
            var userContextResult = RequireUserContext(userContext);
            if (userContextResult != null)
            {
                return (null, userContextResult);
            }

            if (!userContext.CanAccessUserScope(requestedUserId))
            {
                return (null, StatusCode(403, "You do not have permission to access workflow data for that user."));
            }

            if (!requestedUserId.HasValue && userContext.CanRunWorkflowAdminActions())
            {
                return (null, null);
            }

            return (requestedUserId ?? userContext.UserId, null);
        }

        private async Task<IActionResult> StartDomainWorkflowAsync(StartAuditWorkflowRequest request)
        {
            try
            {
                var result = await _workflowService.StartWorkflowAsync(request);
                if (!result.Success)
                {
                    return StatusCode(502, result);
                }

                if (result.Workflow != null)
                {
                    var genericTask = await _reviewsRepository.CreateTaskAsync(new CreateAuditTaskRequest
                    {
                        ReferenceId = result.Workflow.ReferenceId,
                        EntityType = string.IsNullOrWhiteSpace(result.Workflow.EntityType) ? "Workflow" : result.Workflow.EntityType,
                        EntityId = result.Workflow.EntityId,
                        WorkflowInstanceId = result.Workflow.WorkflowInstanceId,
                        TaskType = DetermineGenericTaskType(request),
                        Title = request.TaskTitle ?? $"{result.Workflow.WorkflowDisplayName} action",
                        Description = request.TaskDescription,
                        AssignedToUserId = request.AssigneeUserId,
                        AssignedToName = request.AssigneeName,
                        AssignedByUserId = request.InitiatedByUserId,
                        AssignedByName = request.InitiatedByName,
                        Status = "Open",
                        Priority = string.IsNullOrWhiteSpace(request.Priority) ? "Medium" : request.Priority,
                        DueDate = request.DueDate,
                        Source = "Workflow"
                    });

                    if (ShouldCreateGenericReview(request, result.Workflow))
                    {
                        await _reviewsRepository.CreateReviewAsync(new CreateAuditReviewRequest
                        {
                            ReferenceId = result.Workflow.ReferenceId,
                            EntityType = string.IsNullOrWhiteSpace(result.Workflow.EntityType) ? "Workflow" : result.Workflow.EntityType,
                            EntityId = result.Workflow.EntityId ?? result.Workflow.ReferenceId ?? 0,
                            ReviewType = DetermineReviewType(request, result.Workflow),
                            Status = "Pending",
                            TaskId = genericTask?.Id,
                            WorkflowInstanceId = result.Workflow.WorkflowInstanceId,
                            AssignedReviewerUserId = request.AssigneeUserId,
                            AssignedReviewerName = request.AssigneeName,
                            RequestedByUserId = request.InitiatedByUserId,
                            RequestedByName = request.InitiatedByName,
                            DueDate = request.DueDate,
                            Summary = request.TaskDescription
                        });
                    }

                    try
                    {
                        await _platformRepository.RecordUsageEventAsync(new RecordAuditUsageEventRequest
                        {
                            ModuleName = "workflows",
                            FeatureName = "workflow_start",
                            EventName = "started",
                            ReferenceId = result.Workflow.ReferenceId,
                            PerformedByUserId = request.InitiatedByUserId,
                            PerformedByName = request.InitiatedByName ?? "Audit User",
                            Source = "AuditWorkflowController",
                            MetadataJson = System.Text.Json.JsonSerializer.Serialize(new
                            {
                                result.Workflow.WorkflowDefinitionId,
                                result.Workflow.WorkflowDisplayName,
                                result.Workflow.WorkflowInstanceId
                            })
                        });
                    }
                    catch (Exception telemetryEx)
                    {
                        Console.WriteLine($"Telemetry write failed during workflow start: {telemetryEx.Message}");
                    }
                    await _auditTrailService.RecordEventAsync(new CreateAuditTrailEventRequest
                    {
                        ReferenceId = result.Workflow.ReferenceId,
                        EntityType = string.IsNullOrWhiteSpace(result.Workflow.EntityType) ? "Workflow" : result.Workflow.EntityType,
                        EntityId = result.Workflow.EntityId?.ToString(),
                        Category = "Workflow",
                        Action = "Start",
                        Summary = $"Started workflow: {result.Workflow.WorkflowDisplayName}",
                        PerformedByUserId = request.InitiatedByUserId,
                        PerformedByName = request.InitiatedByName,
                        WorkflowInstanceId = result.Workflow.WorkflowInstanceId,
                        CorrelationId = result.Workflow.WorkflowDefinitionId,
                        Source = "WorkflowLaunch",
                        DetailsJson = System.Text.Json.JsonSerializer.Serialize(new
                        {
                            result.Workflow.WorkflowDefinitionId,
                            result.Workflow.WorkflowInstanceId,
                            result.Workflow.Status,
                            request.TaskTitle,
                            request.TaskDescription
                        })
                    });
                }

                return Ok(result);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        private static bool ShouldCreateGenericReview(StartAuditWorkflowRequest request, AuditWorkflowInstance workflow)
        {
            var normalized = $"{request?.WorkflowDisplayName} {workflow?.WorkflowDisplayName} {request?.WorkflowDefinitionId}".ToLowerInvariant();
            return normalized.Contains("review")
                || normalized.Contains("approval")
                || normalized.Contains("sign-off")
                || normalized.Contains("signoff")
                || normalized.Contains("response")
                || normalized.Contains("follow-up")
                || normalized.Contains("followup");
        }

        private static string DetermineReviewType(StartAuditWorkflowRequest request, AuditWorkflowInstance workflow)
        {
            var label = request?.WorkflowDisplayName ?? workflow?.WorkflowDisplayName ?? "Audit Review";
            return label.Replace("Workflow", string.Empty).Trim();
        }

        private static string DetermineGenericTaskType(StartAuditWorkflowRequest request)
        {
            var normalized = $"{request?.WorkflowDisplayName} {request?.WorkflowDefinitionId}".ToLowerInvariant();
            if (normalized.Contains("sign-off") || normalized.Contains("signoff"))
            {
                return "Sign-Off";
            }
            if (normalized.Contains("approval"))
            {
                return "Approval";
            }
            if (normalized.Contains("review") || normalized.Contains("response") || normalized.Contains("follow-up") || normalized.Contains("followup"))
            {
                return "Review";
            }
            return "Action";
        }
    }
}
