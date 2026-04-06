using Affine.Engine.Model.Auditing.AuditUniverse;
using Affine.Engine.Repository.Auditing;
using Microsoft.Extensions.Configuration;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Net.Http.Headers;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using System.Text.RegularExpressions;
using System.Threading.Tasks;

namespace Affine.Engine.Services
{
    public interface IAuditWorkflowService
    {
        Task<WorkflowLaunchResult> StartWorkflowAsync(StartAuditWorkflowRequest request);
        Task<AuditWorkflowInstance> GetWorkflowInstanceAsync(string workflowInstanceId);
        Task<AuditWorkflowInstance> UpdateWorkflowStatusAsync(UpdateAuditWorkflowInstanceStatusRequest request);
        Task<List<AuditWorkflowInstance>> GetWorkflowInstancesByReferenceAsync(int referenceId);
        Task<List<AuditWorkflowInstance>> GetWorkflowInstancesAsync(bool activeOnly = false);
        Task<List<AuditWorkflowEvent>> GetWorkflowTimelineByReferenceAsync(int referenceId, int limit = 100);
        Task<AuditWorkflowSyncResult> SyncWorkflowStateAsync(SyncAuditWorkflowStateRequest request);
        Task<AuditWorkflowReminderSweepResult> RunReminderSweepAsync();
        Task<AuditWorkflowTask> CreateWorkflowTaskAsync(CreateAuditWorkflowTaskRequest request);
        Task<AuditWorkflowTask> CompleteWorkflowTaskAsync(CompleteAuditWorkflowTaskRequest request);
        Task<List<AuditWorkflowTask>> GetWorkflowTasksByUserAsync(int? userId, bool pendingOnly = false);
        Task<AuditNotification> CreateNotificationAsync(CreateAuditNotificationRequest request);
        Task<List<AuditNotification>> GetNotificationsByUserAsync(int? userId, bool unreadOnly = false);
        Task<bool> MarkNotificationReadAsync(MarkAuditNotificationReadRequest request);
        Task<AuditWorkflowInbox> GetInboxAsync(int? userId);
    }

    public class AuditWorkflowService : IAuditWorkflowService
    {
        private const string DefaultWorkflowServiceApiKey = "00000000-0000-0000-0000-000000000000";
        private const string ElsaRunTaskSource = "RunTask";
        private readonly HttpClient _httpClient;
        private readonly IConfiguration _configuration;
        private readonly IAuditWorkflowRepository _workflowRepository;

        public AuditWorkflowService(
            HttpClient httpClient,
            IConfiguration configuration,
            IAuditWorkflowRepository workflowRepository)
        {
            _httpClient = httpClient ?? throw new ArgumentNullException(nameof(httpClient));
            _configuration = configuration ?? throw new ArgumentNullException(nameof(configuration));
            _workflowRepository = workflowRepository ?? throw new ArgumentNullException(nameof(workflowRepository));
        }

        public async Task<WorkflowLaunchResult> StartWorkflowAsync(StartAuditWorkflowRequest request)
        {
            if (request == null)
                throw new ArgumentNullException(nameof(request));

            var workflowServiceUrl = GetWorkflowServiceUrl();
            var dispatchRequest = new
            {
                workflowDefinitionId = request.WorkflowDefinitionId,
                activityId = request.ActivityId,
                input = request.Input ?? new Dictionary<string, object>()
            };

            using var response = await SendWorkflowServiceRequestAsync(
                HttpMethod.Post,
                $"{workflowServiceUrl}/elsa/api/workflow-definitions/{Uri.EscapeDataString(request.WorkflowDefinitionId)}/dispatch",
                new StringContent(JsonSerializer.Serialize(dispatchRequest), Encoding.UTF8, "application/json"));

            var responseContent = await response.Content.ReadAsStringAsync();
            if (!response.IsSuccessStatusCode)
            {
                return new WorkflowLaunchResult
                {
                    Success = false,
                    Status = "Failed",
                    Message = $"Failed to start workflow: {response.ReasonPhrase}"
                };
            }

            var workflowInstanceId = ExtractWorkflowInstanceId(responseContent);
            if (string.IsNullOrWhiteSpace(workflowInstanceId))
            {
                return new WorkflowLaunchResult
                {
                    Success = false,
                    Status = "Failed",
                    Message = "Workflow service did not return a workflow instance ID."
                };
            }

            var currentActivityName = HumanizeIdentifier(request.ActivityId);
            var workflow = await _workflowRepository.CreateWorkflowInstanceAsync(new CreateAuditWorkflowInstanceRequest
            {
                ReferenceId = request.ReferenceId,
                EntityType = request.EntityType ?? "Assessment",
                EntityId = request.EntityId,
                WorkflowDefinitionId = request.WorkflowDefinitionId,
                WorkflowDisplayName = string.IsNullOrWhiteSpace(request.WorkflowDisplayName)
                    ? HumanizeIdentifier(request.WorkflowDefinitionId)
                    : request.WorkflowDisplayName,
                WorkflowInstanceId = workflowInstanceId,
                Status = BuildInitialStatus(request.WorkflowDisplayName, currentActivityName),
                CurrentActivityId = request.ActivityId,
                CurrentActivityName = currentActivityName,
                StartedByUserId = request.InitiatedByUserId,
                StartedByName = request.InitiatedByName,
                IsActive = true,
                MetadataJson = JsonSerializer.Serialize(new
                {
                    request.ReferenceId,
                    request.EntityType,
                    request.EntityId,
                    request.WorkflowDefinitionId,
                    request.WorkflowDisplayName,
                    request.ActivityId,
                    request.Input,
                    ElsaResponse = responseContent,
                    StartedAt = DateTime.UtcNow
                })
            });

            var eventsCreated = 0;
            if (workflow != null)
            {
                await AppendWorkflowEventAsync(new CreateAuditWorkflowEventRequest
                {
                    WorkflowInstanceId = workflow.WorkflowInstanceId,
                    ReferenceId = workflow.ReferenceId,
                    EntityType = workflow.EntityType,
                    EntityId = workflow.EntityId,
                    EventType = "WorkflowStarted",
                    Title = $"{workflow.WorkflowDisplayName} started",
                    Description = string.IsNullOrWhiteSpace(request.TaskDescription)
                        ? $"{workflow.WorkflowDisplayName} was dispatched to Elsa."
                        : request.TaskDescription,
                    ActorUserId = request.InitiatedByUserId,
                    ActorName = request.InitiatedByName,
                    MetadataJson = JsonSerializer.Serialize(new
                    {
                        workflow.WorkflowDefinitionId,
                        workflow.CurrentActivityId,
                        workflow.CurrentActivityName
                    })
                });
                eventsCreated++;
            }

            if (!string.IsNullOrWhiteSpace(request.TaskTitle))
            {
                var externalTaskId = await ResolveElsaTaskIdAsync(workflow.WorkflowInstanceId);
                var createdTask = await _workflowRepository.CreateWorkflowTaskAsync(new CreateAuditWorkflowTaskRequest
                {
                    WorkflowInstanceId = workflow.WorkflowInstanceId,
                    ExternalTaskId = externalTaskId,
                    ExternalTaskSource = string.IsNullOrWhiteSpace(externalTaskId) ? null : ElsaRunTaskSource,
                    ReferenceId = request.ReferenceId,
                    EntityType = request.EntityType ?? "Assessment",
                    EntityId = request.EntityId,
                    TaskTitle = request.TaskTitle,
                    TaskDescription = request.TaskDescription,
                    AssigneeUserId = request.AssigneeUserId,
                    AssigneeName = request.AssigneeName,
                    Status = "Pending",
                    Priority = string.IsNullOrWhiteSpace(request.Priority) ? "Medium" : request.Priority,
                    DueDate = request.DueDate,
                    ActionUrl = request.ActionUrl
                });

                if (createdTask != null)
                {
                    await AppendWorkflowEventAsync(new CreateAuditWorkflowEventRequest
                    {
                        WorkflowInstanceId = workflow.WorkflowInstanceId,
                        ReferenceId = request.ReferenceId,
                        EntityType = request.EntityType ?? "Assessment",
                        EntityId = request.EntityId,
                        EventType = "TaskAssigned",
                        Title = createdTask.TaskTitle,
                        Description = string.IsNullOrWhiteSpace(createdTask.TaskDescription)
                            ? "A workflow task was assigned."
                            : createdTask.TaskDescription,
                        ActorUserId = request.InitiatedByUserId,
                        ActorName = request.InitiatedByName,
                        MetadataJson = JsonSerializer.Serialize(new
                        {
                            createdTask.AssigneeUserId,
                            createdTask.AssigneeName,
                            createdTask.Priority,
                            createdTask.DueDate
                        })
                    });
                    eventsCreated++;
                    await CreateReviewReadyNotificationIfApplicableAsync(workflow, createdTask);
                }
            }

            if (!string.IsNullOrWhiteSpace(request.NotificationTitle) || !string.IsNullOrWhiteSpace(request.NotificationMessage))
            {
                await CreateNotificationIfMissingAsync(new CreateAuditNotificationRequest
                {
                    ReferenceId = request.ReferenceId,
                    EntityType = request.EntityType ?? "Assessment",
                    EntityId = request.EntityId,
                    WorkflowInstanceId = workflow.WorkflowInstanceId,
                    NotificationType = string.IsNullOrWhiteSpace(request.NotificationType) ? "Workflow" : request.NotificationType,
                    Severity = string.IsNullOrWhiteSpace(request.Severity) ? "Info" : request.Severity,
                    Title = string.IsNullOrWhiteSpace(request.NotificationTitle)
                        ? $"{workflow.WorkflowDisplayName} started"
                        : request.NotificationTitle,
                    Message = request.NotificationMessage,
                    RecipientUserId = request.AssigneeUserId,
                    RecipientName = request.AssigneeName,
                    ActionUrl = request.ActionUrl
                });
            }

            return new WorkflowLaunchResult
            {
                Success = true,
                WorkflowInstanceId = workflow.WorkflowInstanceId,
                Status = workflow.Status,
                Message = eventsCreated > 0
                    ? "Workflow started successfully"
                    : "Workflow started successfully with no workflow events recorded",
                Workflow = workflow
            };
        }

        public Task<AuditWorkflowInstance> GetWorkflowInstanceAsync(string workflowInstanceId)
            => _workflowRepository.GetWorkflowInstanceAsync(workflowInstanceId);

        public Task<AuditWorkflowInstance> UpdateWorkflowStatusAsync(UpdateAuditWorkflowInstanceStatusRequest request)
            => _workflowRepository.UpdateWorkflowInstanceStatusAsync(request);

        public Task<List<AuditWorkflowInstance>> GetWorkflowInstancesByReferenceAsync(int referenceId)
            => _workflowRepository.GetWorkflowInstancesByReferenceAsync(referenceId);

        public Task<List<AuditWorkflowInstance>> GetWorkflowInstancesAsync(bool activeOnly = false)
            => _workflowRepository.GetWorkflowInstancesAsync(activeOnly);

        public Task<List<AuditWorkflowEvent>> GetWorkflowTimelineByReferenceAsync(int referenceId, int limit = 100)
            => _workflowRepository.GetWorkflowEventsByReferenceAsync(referenceId, limit);

        public async Task<AuditWorkflowSyncResult> SyncWorkflowStateAsync(SyncAuditWorkflowStateRequest request)
        {
            if (request == null)
                throw new ArgumentNullException(nameof(request));
            if (string.IsNullOrWhiteSpace(request.WorkflowInstanceId))
                throw new ArgumentException("Workflow instance ID is required", nameof(request));

            var existingWorkflow = await _workflowRepository.GetWorkflowInstanceAsync(request.WorkflowInstanceId);
            if (existingWorkflow == null)
            {
                return new AuditWorkflowSyncResult
                {
                    Success = false,
                    WorkflowInstanceId = request.WorkflowInstanceId,
                    Message = "Workflow instance was not found"
                };
            }

            var terminalStatus = IsTerminalStatus(request.Status);
            var workflow = await _workflowRepository.UpdateWorkflowInstanceStatusAsync(new UpdateAuditWorkflowInstanceStatusRequest
            {
                WorkflowInstanceId = request.WorkflowInstanceId,
                Status = string.IsNullOrWhiteSpace(request.Status) ? existingWorkflow.Status : request.Status,
                CurrentActivityId = string.IsNullOrWhiteSpace(request.CurrentActivityId) ? existingWorkflow.CurrentActivityId : request.CurrentActivityId,
                CurrentActivityName = string.IsNullOrWhiteSpace(request.CurrentActivityName) ? existingWorkflow.CurrentActivityName : request.CurrentActivityName,
                IsActive = request.IsActive ?? !terminalStatus,
                CompletedAt = request.CompletedAt ?? (terminalStatus ? DateTime.UtcNow : existingWorkflow.CompletedAt)
            });

            var tasksCompleted = 0;
            if ((request.AutoCompleteOpenTasks ?? terminalStatus) && workflow != null)
            {
                tasksCompleted = await _workflowRepository.CompleteOpenTasksForWorkflowInstanceAsync(
                    workflow.WorkflowInstanceId,
                    request.ActorUserId,
                    request.EventDescription ?? $"Workflow status synchronized to {workflow.Status}.");
            }

            var workflowEvent = await AppendWorkflowEventAsync(new CreateAuditWorkflowEventRequest
            {
                WorkflowInstanceId = request.WorkflowInstanceId,
                ReferenceId = existingWorkflow.ReferenceId,
                EntityType = existingWorkflow.EntityType,
                EntityId = existingWorkflow.EntityId,
                EventType = string.IsNullOrWhiteSpace(request.EventType) ? "WorkflowSynchronized" : request.EventType,
                Title = string.IsNullOrWhiteSpace(request.EventTitle)
                    ? $"{existingWorkflow.WorkflowDisplayName} updated to {workflow?.Status ?? request.Status}"
                    : request.EventTitle,
                Description = string.IsNullOrWhiteSpace(request.EventDescription)
                    ? $"Elsa synchronized workflow state to {workflow?.Status ?? request.Status}."
                    : request.EventDescription,
                ActorUserId = request.ActorUserId,
                ActorName = request.ActorName,
                MetadataJson = JsonSerializer.Serialize(new
                {
                    request.CurrentActivityId,
                    request.CurrentActivityName,
                    request.Status,
                    request.CompletedAt,
                    AutoCompletedTasks = tasksCompleted
                })
            });

            var notificationsCreated = 0;
            var notificationTitle = request.NotificationTitle;
            var notificationMessage = request.NotificationMessage;

            if (terminalStatus && string.IsNullOrWhiteSpace(notificationTitle))
            {
                notificationTitle = $"{existingWorkflow.WorkflowDisplayName} completed";
                notificationMessage ??= $"Workflow status changed to {workflow?.Status ?? request.Status}.";
            }

            if (!string.IsNullOrWhiteSpace(notificationTitle) || !string.IsNullOrWhiteSpace(notificationMessage))
            {
                notificationsCreated += await CreateNotificationIfMissingAsync(new CreateAuditNotificationRequest
                {
                    ReferenceId = existingWorkflow.ReferenceId,
                    EntityType = existingWorkflow.EntityType,
                    EntityId = existingWorkflow.EntityId,
                    WorkflowInstanceId = existingWorkflow.WorkflowInstanceId,
                    NotificationType = string.IsNullOrWhiteSpace(request.NotificationType) ? "WorkflowStatus" : request.NotificationType,
                    Severity = string.IsNullOrWhiteSpace(request.NotificationSeverity)
                        ? (terminalStatus ? "Success" : "Info")
                        : request.NotificationSeverity,
                    Title = notificationTitle,
                    Message = notificationMessage,
                    RecipientUserId = request.NotificationRecipientUserId ?? existingWorkflow.StartedByUserId,
                    RecipientName = request.NotificationRecipientName ?? existingWorkflow.StartedByName,
                    ActionUrl = string.IsNullOrWhiteSpace(request.ActionUrl)
                        ? $"/assessments/{existingWorkflow.ReferenceId}"
                        : request.ActionUrl
                });
            }

            return new AuditWorkflowSyncResult
            {
                Success = workflow != null,
                WorkflowInstanceId = request.WorkflowInstanceId,
                Status = workflow?.Status ?? request.Status,
                TasksCompleted = tasksCompleted,
                NotificationsCreated = notificationsCreated,
                Workflow = workflow,
                Event = workflowEvent,
                Message = workflow != null
                    ? "Workflow state synchronized successfully"
                    : "Workflow state synchronization did not return an updated workflow"
            };
        }

        public async Task<AuditWorkflowReminderSweepResult> RunReminderSweepAsync()
        {
            var dueSoonHours = ParseIntConfig("WorkflowReminders:DueSoonHours", 24);
            var escalationHours = ParseIntConfig("WorkflowReminders:EscalationHours", 72);
            var now = DateTime.UtcNow;

            var tasks = await _workflowRepository.GetWorkflowTasksByUserAsync(null, pendingOnly: true);
            var workflows = await _workflowRepository.GetWorkflowInstancesAsync(activeOnly: false);
            var workflowLookup = workflows
                .Where(x => !string.IsNullOrWhiteSpace(x.WorkflowInstanceId))
                .GroupBy(x => x.WorkflowInstanceId)
                .ToDictionary(g => g.Key, g => g.First());

            var result = new AuditWorkflowReminderSweepResult
            {
                Success = true,
                TasksEvaluated = tasks.Count,
                Message = "Reminder sweep completed"
            };

            foreach (var task in tasks)
            {
                if (task == null || string.IsNullOrWhiteSpace(task.WorkflowInstanceId))
                    continue;

                workflowLookup.TryGetValue(task.WorkflowInstanceId, out var workflow);
                var dueDate = task.DueDate?.ToUniversalTime();
                var isReviewTask = IsReviewTask(task);

                if (isReviewTask)
                {
                    result.ReviewReadyNotificationsCreated += await CreateNotificationIfMissingAsync(new CreateAuditNotificationRequest
                    {
                        ReferenceId = task.ReferenceId,
                        EntityType = task.EntityType,
                        EntityId = task.EntityId,
                        WorkflowInstanceId = task.WorkflowInstanceId,
                        NotificationType = "ReviewReady",
                        Severity = "Info",
                        Title = $"Review-ready: {task.TaskTitle}",
                        Message = $"Task '{task.TaskTitle}' is waiting for review or approval.",
                        RecipientUserId = task.AssigneeUserId,
                        RecipientName = task.AssigneeName,
                        ActionUrl = task.ActionUrl
                    });
                }

                if (!dueDate.HasValue)
                    continue;

                var hoursUntilDue = (dueDate.Value - now).TotalHours;
                var hoursOverdue = (now - dueDate.Value).TotalHours;

                if (hoursUntilDue >= 0 && hoursUntilDue <= dueSoonHours)
                {
                    result.DueSoonRemindersCreated += await CreateNotificationIfMissingAsync(new CreateAuditNotificationRequest
                    {
                        ReferenceId = task.ReferenceId,
                        EntityType = task.EntityType,
                        EntityId = task.EntityId,
                        WorkflowInstanceId = task.WorkflowInstanceId,
                        NotificationType = "DueSoonReminder",
                        Severity = "Warning",
                        Title = $"Due soon: {task.TaskTitle}",
                        Message = $"Task '{task.TaskTitle}' is due on {dueDate.Value:yyyy-MM-dd HH:mm} UTC.",
                        RecipientUserId = task.AssigneeUserId,
                        RecipientName = task.AssigneeName,
                        ActionUrl = task.ActionUrl
                    });
                }

                if (hoursOverdue <= 0)
                    continue;

                var overdueType = string.Equals(task.EntityType, "Finding", StringComparison.OrdinalIgnoreCase)
                    || string.Equals(task.EntityType, "Recommendation", StringComparison.OrdinalIgnoreCase)
                    ? "OverdueFindingReminder"
                    : "OverdueReminder";

                var overdueTitle = overdueType == "OverdueFindingReminder"
                    ? $"Overdue finding follow-up: {task.TaskTitle}"
                    : $"Overdue workflow task: {task.TaskTitle}";

                var createdOverdue = await CreateNotificationIfMissingAsync(new CreateAuditNotificationRequest
                {
                    ReferenceId = task.ReferenceId,
                    EntityType = task.EntityType,
                    EntityId = task.EntityId,
                    WorkflowInstanceId = task.WorkflowInstanceId,
                    NotificationType = overdueType,
                    Severity = "Danger",
                    Title = overdueTitle,
                    Message = $"Task '{task.TaskTitle}' is overdue since {dueDate.Value:yyyy-MM-dd HH:mm} UTC.",
                    RecipientUserId = task.AssigneeUserId,
                    RecipientName = task.AssigneeName,
                    ActionUrl = task.ActionUrl
                });
                result.OverdueRemindersCreated += createdOverdue;

                if (createdOverdue > 0)
                {
                    await AppendWorkflowEventAsync(new CreateAuditWorkflowEventRequest
                    {
                        WorkflowInstanceId = task.WorkflowInstanceId,
                        ReferenceId = task.ReferenceId,
                        EntityType = task.EntityType,
                        EntityId = task.EntityId,
                        EventType = overdueType,
                        Title = overdueTitle,
                        Description = $"Reminder generated for overdue task '{task.TaskTitle}'.",
                        ActorName = "Workflow Reminder Service",
                        MetadataJson = JsonSerializer.Serialize(new { task.DueDate, task.Priority, task.AssigneeUserId })
                    });
                    result.WorkflowEventsCreated++;
                }

                if (hoursOverdue < escalationHours)
                    continue;

                result.EscalationsCreated += await CreateNotificationIfMissingAsync(new CreateAuditNotificationRequest
                {
                    ReferenceId = task.ReferenceId,
                    EntityType = task.EntityType,
                    EntityId = task.EntityId,
                    WorkflowInstanceId = task.WorkflowInstanceId,
                    NotificationType = "Escalation",
                    Severity = "Danger",
                    Title = $"Escalation: {task.TaskTitle}",
                    Message = $"Task '{task.TaskTitle}' remains overdue and requires escalation.",
                    RecipientUserId = workflow?.StartedByUserId ?? task.AssigneeUserId,
                    RecipientName = workflow?.StartedByName ?? task.AssigneeName,
                    ActionUrl = task.ActionUrl
                });
            }

            return result;
        }

        public async Task<AuditWorkflowTask> CreateWorkflowTaskAsync(CreateAuditWorkflowTaskRequest request)
        {
            var task = await _workflowRepository.CreateWorkflowTaskAsync(request);
            if (task == null)
                return null;

            await AppendWorkflowEventAsync(new CreateAuditWorkflowEventRequest
            {
                WorkflowInstanceId = task.WorkflowInstanceId,
                ReferenceId = task.ReferenceId,
                EntityType = task.EntityType,
                EntityId = task.EntityId,
                EventType = "TaskAssigned",
                Title = task.TaskTitle,
                Description = string.IsNullOrWhiteSpace(task.TaskDescription) ? "A workflow task was assigned." : task.TaskDescription,
                ActorUserId = request.AssigneeUserId,
                ActorName = request.AssigneeName,
                MetadataJson = JsonSerializer.Serialize(new { task.Priority, task.DueDate, task.Status })
            });

            var workflow = await _workflowRepository.GetWorkflowInstanceAsync(task.WorkflowInstanceId);
            if (workflow != null)
            {
                await CreateReviewReadyNotificationIfApplicableAsync(workflow, task);
            }

            return task;
        }

        public async Task<AuditWorkflowTask> CompleteWorkflowTaskAsync(CompleteAuditWorkflowTaskRequest request)
        {
            var task = await _workflowRepository.CompleteWorkflowTaskAsync(request);
            if (task == null)
                return null;

            await AppendWorkflowEventAsync(new CreateAuditWorkflowEventRequest
            {
                WorkflowInstanceId = task.WorkflowInstanceId,
                ReferenceId = task.ReferenceId,
                EntityType = task.EntityType,
                EntityId = task.EntityId,
                EventType = "TaskCompleted",
                Title = task.TaskTitle,
                Description = string.IsNullOrWhiteSpace(request?.CompletionNotes)
                    ? "Workflow task completed."
                    : request.CompletionNotes,
                ActorUserId = request?.CompletedByUserId,
                ActorName = "Workflow User",
                MetadataJson = JsonSerializer.Serialize(new { task.CompletedAt, task.Status })
            });

            try
            {
                await NotifyElsaWorkflowCompletedAsync(task);
            }
            catch (Exception ex)
            {
                await AppendWorkflowEventAsync(new CreateAuditWorkflowEventRequest
                {
                    WorkflowInstanceId = task.WorkflowInstanceId,
                    ReferenceId = task.ReferenceId,
                    EntityType = task.EntityType,
                    EntityId = task.EntityId,
                    EventType = "ElsaCallbackFailed",
                    Title = $"Elsa callback failed for {task.TaskTitle}",
                    Description = $"Task completion was saved, but the Elsa workflow callback failed: {ex.Message}",
                    ActorUserId = request?.CompletedByUserId,
                    ActorName = "Workflow User",
                    MetadataJson = JsonSerializer.Serialize(new
                    {
                        task.CompletedAt,
                        task.Status,
                        task.WorkflowInstanceId
                    })
                });
            }

            return task;
        }

        public Task<List<AuditWorkflowTask>> GetWorkflowTasksByUserAsync(int? userId, bool pendingOnly = false)
            => _workflowRepository.GetWorkflowTasksByUserAsync(userId, pendingOnly);

        public Task<AuditNotification> CreateNotificationAsync(CreateAuditNotificationRequest request)
            => _workflowRepository.CreateNotificationAsync(request);

        public Task<List<AuditNotification>> GetNotificationsByUserAsync(int? userId, bool unreadOnly = false)
            => _workflowRepository.GetNotificationsByUserAsync(userId, unreadOnly);

        public Task<bool> MarkNotificationReadAsync(MarkAuditNotificationReadRequest request)
            => _workflowRepository.MarkNotificationReadAsync(request);

        public Task<AuditWorkflowInbox> GetInboxAsync(int? userId)
            => _workflowRepository.GetInboxAsync(userId);

        private static string ExtractWorkflowInstanceId(string responseContent)
        {
            if (string.IsNullOrWhiteSpace(responseContent))
                return null;

            try
            {
                using var document = JsonDocument.Parse(responseContent);
                var root = document.RootElement;

                if (root.ValueKind == JsonValueKind.Object)
                {
                    if (root.TryGetProperty("workflowInstanceId", out var workflowInstanceIdProperty))
                    {
                        return workflowInstanceIdProperty.GetString();
                    }

                    if (root.TryGetProperty("id", out var idProperty))
                    {
                        return idProperty.GetString();
                    }
                }
            }
            catch
            {
                return null;
            }

            return null;
        }

        private static string HumanizeIdentifier(string identifier)
        {
            if (string.IsNullOrWhiteSpace(identifier))
                return "Workflow Activity";

            var spaced = Regex.Replace(identifier, "([a-z0-9])([A-Z])", "$1 $2");
            spaced = spaced.Replace("_", " ").Replace("-", " ").Trim();
            return string.IsNullOrWhiteSpace(spaced) ? identifier : spaced;
        }

        private static string BuildInitialStatus(string workflowDisplayName, string currentActivityName)
        {
            if (!string.IsNullOrWhiteSpace(currentActivityName))
            {
                return $"{currentActivityName} In Progress";
            }

            if (!string.IsNullOrWhiteSpace(workflowDisplayName))
            {
                return $"{workflowDisplayName} In Progress";
            }

            return "Workflow In Progress";
        }

        private async Task<AuditWorkflowEvent> AppendWorkflowEventAsync(CreateAuditWorkflowEventRequest request)
        {
            if (request == null || string.IsNullOrWhiteSpace(request.WorkflowInstanceId) || string.IsNullOrWhiteSpace(request.Title))
                return null;

            return await _workflowRepository.CreateWorkflowEventAsync(request);
        }

        private async Task<int> CreateNotificationIfMissingAsync(CreateAuditNotificationRequest request)
        {
            if (request == null || string.IsNullOrWhiteSpace(request.Title))
                return 0;

            var exists = await _workflowRepository.NotificationExistsAsync(
                request.NotificationType ?? "Workflow",
                request.Title,
                request.RecipientUserId,
                request.WorkflowInstanceId);

            if (exists)
                return 0;

            await _workflowRepository.CreateNotificationAsync(request);
            return 1;
        }

        private async Task CreateReviewReadyNotificationIfApplicableAsync(AuditWorkflowInstance workflow, AuditWorkflowTask task)
        {
            if (workflow == null || task == null || !IsReviewTask(task))
                return;

            await CreateNotificationIfMissingAsync(new CreateAuditNotificationRequest
            {
                ReferenceId = workflow.ReferenceId,
                EntityType = task.EntityType,
                EntityId = task.EntityId,
                WorkflowInstanceId = workflow.WorkflowInstanceId,
                NotificationType = "ReviewReady",
                Severity = "Info",
                Title = $"Review-ready: {task.TaskTitle}",
                Message = $"Task '{task.TaskTitle}' is ready for reviewer action.",
                RecipientUserId = task.AssigneeUserId,
                RecipientName = task.AssigneeName,
                ActionUrl = task.ActionUrl
            });
        }

        private async Task NotifyElsaWorkflowCompletedAsync(AuditWorkflowTask task)
        {
            if (task == null || string.IsNullOrWhiteSpace(task.WorkflowInstanceId))
                return;

            var externalTaskId = task.ExternalTaskId;
            if (string.IsNullOrWhiteSpace(externalTaskId))
            {
                externalTaskId = await ResolveElsaTaskIdAsync(task.WorkflowInstanceId);
            }

            if (string.IsNullOrWhiteSpace(externalTaskId))
            {
                throw new InvalidOperationException($"Could not resolve an Elsa task ID for workflow instance {task.WorkflowInstanceId}.");
            }

            var workflowServiceUrl = GetWorkflowServiceUrl();
            var callbackUrl = $"{workflowServiceUrl}/elsa/api/tasks/{Uri.EscapeDataString(externalTaskId)}/complete";
            using var response = await SendWorkflowServiceRequestAsync(
                HttpMethod.Post,
                callbackUrl,
                new StringContent("{}", Encoding.UTF8, "application/json"));

            if (response.IsSuccessStatusCode)
                return;

            var responseContent = await response.Content.ReadAsStringAsync();
            throw new InvalidOperationException(
                $"Workflow callback endpoint returned {(int)response.StatusCode} {response.ReasonPhrase}: {responseContent}");
        }

        private async Task<string> ResolveElsaTaskIdAsync(string workflowInstanceId)
        {
            if (string.IsNullOrWhiteSpace(workflowInstanceId))
                return null;

            for (var attempt = 0; attempt < 8; attempt++)
            {
                var taskId = await _workflowRepository.GetLatestExternalTaskIdAsync(workflowInstanceId, ElsaRunTaskSource);
                if (!string.IsNullOrWhiteSpace(taskId))
                {
                    return taskId;
                }

                await Task.Delay(250);
            }

            return null;
        }

        private string GetWorkflowServiceUrl()
            => (_configuration["WorkflowServiceUrl"] ?? "https://localhost:5001").TrimEnd('/');

        private string GetWorkflowServiceApiKey()
            => string.IsNullOrWhiteSpace(_configuration["WorkflowServiceApiKey"])
                ? DefaultWorkflowServiceApiKey
                : _configuration["WorkflowServiceApiKey"]!.Trim();

        private async Task<HttpResponseMessage> SendWorkflowServiceRequestAsync(HttpMethod method, string url, HttpContent? content = null)
        {
            using var request = new HttpRequestMessage(method, url)
            {
                Content = content
            };
            request.Headers.Authorization = new AuthenticationHeaderValue("ApiKey", GetWorkflowServiceApiKey());

            return await _httpClient.SendAsync(request);
        }

        private static bool IsReviewTask(AuditWorkflowTask task)
        {
            var text = $"{task?.TaskTitle} {task?.TaskDescription}".ToLowerInvariant();
            return text.Contains("review") || text.Contains("approve") || text.Contains("sign off") || text.Contains("sign-off");
        }

        private static bool IsTerminalStatus(string status)
        {
            var normalized = (status ?? string.Empty).Trim().ToLowerInvariant();
            return normalized is "completed" or "complete" or "approved" or "closed" or "cancelled" or "canceled" or "rejected" or "done";
        }

        private int ParseIntConfig(string key, int fallback)
        {
            var raw = _configuration[key];
            return int.TryParse(raw, out var value) ? value : fallback;
        }
    }
}
