using System;
using System.Net.Http.Json;
using Elsa.Workflows;
using Elsa.Workflows.Models;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;

namespace Affine.Auditing.Workflows.Server.Activities;

public class SyncAuditWorkflowStateActivity : CodeActivity
{
    public Input<string> Status { get; set; } = new("In Progress", "workflow-status");
    public Input<string> CurrentActivityId { get; set; } = new("WorkflowActivity", "current-activity-id");
    public Input<string> CurrentActivityName { get; set; } = new("Workflow activity", "current-activity-name");
    public Input<string> EventType { get; set; } = new("WorkflowSynchronized", "event-type");
    public Input<string> EventTitle { get; set; } = new("Workflow synchronized", "event-title");
    public Input<string> EventDescription { get; set; } = new("Workflow state was synchronized from Elsa.", "event-description");
    public Input<string> ActorName { get; set; } = new("Elsa Workflow Engine", "actor-name");
    public Input<string> NotificationType { get; set; } = new("", "notification-type");
    public Input<string> NotificationTitle { get; set; } = new("", "notification-title");
    public Input<string> NotificationMessage { get; set; } = new("", "notification-message");
    public Input<string> NotificationSeverity { get; set; } = new("", "notification-severity");
    public Input<string> NotificationRecipientName { get; set; } = new("", "notification-recipient-name");
    public Input<string> ActionUrl { get; set; } = new("", "action-url");
    public Input<bool> AutoCompleteOpenTasks { get; set; } = new(false, "auto-complete-open-tasks");
    public Input<bool> IsActive { get; set; } = new(true, "is-active");

    protected override void Execute(ActivityExecutionContext context)
    {
        var workflowExecutionContext = context.WorkflowExecutionContext;
        var configuration = context.GetRequiredService<IConfiguration>();
        var httpClientFactory = context.GetRequiredService<IHttpClientFactory>();
        var logger = context.GetService<ILogger<SyncAuditWorkflowStateActivity>>();

        var auditApiBaseUrl = (configuration["AuditApi:BaseUrl"] ?? "http://localhost:5023").TrimEnd('/');
        var request = new
        {
            WorkflowInstanceId = workflowExecutionContext.Id,
            Status = ReadString(context, Status, "In Progress"),
            CurrentActivityId = ReadString(context, CurrentActivityId, "WorkflowActivity"),
            CurrentActivityName = ReadString(context, CurrentActivityName, "Workflow activity"),
            IsActive = Read(context, IsActive),
            AutoCompleteOpenTasks = Read(context, AutoCompleteOpenTasks),
            ActorName = ReadString(context, ActorName, "Elsa Workflow Engine"),
            EventType = ReadString(context, EventType, "WorkflowSynchronized"),
            EventTitle = ReadString(context, EventTitle, "Workflow synchronized"),
            EventDescription = ReadString(context, EventDescription, "Workflow state was synchronized from Elsa."),
            NotificationType = ReadString(context, NotificationType),
            NotificationTitle = ReadString(context, NotificationTitle),
            NotificationMessage = ReadString(context, NotificationMessage),
            NotificationSeverity = ReadString(context, NotificationSeverity, "Info"),
            NotificationRecipientName = ReadString(context, NotificationRecipientName),
            ActionUrl = ReadString(context, ActionUrl)
        };

        try
        {
            var client = httpClientFactory.CreateClient();
            var response = client
                .PostAsJsonAsync($"{auditApiBaseUrl}/api/v1/AuditWorkflow/SyncElsaState", request, context.CancellationToken)
                .GetAwaiter()
                .GetResult();

            if (!response.IsSuccessStatusCode)
            {
                var responseContent = response.Content
                    .ReadAsStringAsync(context.CancellationToken)
                    .GetAwaiter()
                    .GetResult();

                throw new InvalidOperationException(
                    $"Audit workflow sync failed with status code {(int)response.StatusCode}: {responseContent}");
            }

            context.AddExecutionLogEntry(
                "AuditWorkflowSync",
                $"Synchronized workflow {workflowExecutionContext.Id} to status '{request.Status}'.",
                nameof(SyncAuditWorkflowStateActivity),
                request);
        }
        catch (Exception ex)
        {
            logger?.LogError(ex, "Failed to synchronize Elsa workflow state for workflow instance {WorkflowInstanceId}", workflowExecutionContext.Id);
            throw;
        }
    }

    private static T Read<T>(ActivityExecutionContext context, Input<T> input) => context.Get(input)!;
    private static string ReadString(ActivityExecutionContext context, Input<string> input, string fallback = "")
    {
        var value = context.Get(input);
        return value ?? fallback;
    }
}
