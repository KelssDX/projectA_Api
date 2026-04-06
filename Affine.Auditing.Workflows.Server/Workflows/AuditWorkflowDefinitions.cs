using System.Collections.Generic;
using Affine.Auditing.Workflows.Server.Activities;
using Elsa.Extensions;
using Elsa.Workflows;
using Elsa.Workflows.Activities;
using Elsa.Workflows.Models;
using Elsa.Workflows.Runtime.Activities;

namespace Affine.Auditing.Workflows.Server.Workflows;

public abstract class AuditCallbackWorkflowBase : WorkflowBase
{
    protected abstract string DefinitionId { get; }
    protected abstract string DisplayName { get; }
    protected abstract string PendingStatus { get; }
    protected abstract string PendingActivityId { get; }
    protected abstract string PendingActivityName { get; }
    protected abstract string CompletionNotificationType { get; }

    protected virtual string Description => $"{DisplayName} managed by Elsa for the auditing application.";

    protected override void Build(IWorkflowBuilder builder)
    {
        builder.WithDefinitionId(DefinitionId);
        builder.Name = DisplayName;
        builder.Description = Description;
        builder.AsSystemWorkflow();

        builder.WithInput("ReferenceId", typeof(int), "Assessment reference ID");
        builder.WithInput("Notes", typeof(string), "Workflow context notes");
        ConfigureInputs(builder);

        builder.Root = new Sequence
        {
            Activities = new List<IActivity>
            {
                BuildPendingSyncActivity(),
                BuildCompletionTask(),
                BuildCompletionSyncActivity()
            }
        };
    }

    protected virtual void ConfigureInputs(IWorkflowBuilder builder)
    {
    }

    private IActivity BuildPendingSyncActivity()
    {
        return new SyncAuditWorkflowStateActivity
        {
            Status = new(PendingStatus, $"{DefinitionId}-pending-status"),
            CurrentActivityId = new(PendingActivityId, $"{DefinitionId}-pending-activity-id"),
            CurrentActivityName = new(PendingActivityName, $"{DefinitionId}-pending-activity-name"),
            EventType = new("WorkflowWaiting", $"{DefinitionId}-waiting-event-type"),
            EventTitle = new($"{DisplayName} is waiting for completion", $"{DefinitionId}-waiting-title"),
            EventDescription = new(
                "Elsa registered the workflow and is waiting for the audit application to signal completion.",
                $"{DefinitionId}-waiting-description"),
            AutoCompleteOpenTasks = new(false, $"{DefinitionId}-pending-auto-complete"),
            IsActive = new(true, $"{DefinitionId}-pending-is-active")
        };
    }

    private IActivity BuildCompletionTask()
    {
        return new RunTask($"{DisplayName} task", $"{DefinitionId}-run-task");
    }

    private IActivity BuildCompletionSyncActivity()
    {
        return new SyncAuditWorkflowStateActivity
        {
            Status = new("Completed", $"{DefinitionId}-completed-status"),
            CurrentActivityId = new("Completed", $"{DefinitionId}-completed-activity-id"),
            CurrentActivityName = new("Completed", $"{DefinitionId}-completed-activity-name"),
            EventType = new("WorkflowCompleted", $"{DefinitionId}-completed-event-type"),
            EventTitle = new($"{DisplayName} completed", $"{DefinitionId}-completed-title"),
            EventDescription = new(
                "Elsa received the completion callback from the audit application and closed the workflow.",
                $"{DefinitionId}-completed-description"),
            NotificationType = new(CompletionNotificationType, $"{DefinitionId}-notification-type"),
            NotificationTitle = new($"{DisplayName} completed", $"{DefinitionId}-notification-title"),
            NotificationMessage = new(
                $"{DisplayName} completed successfully and the audit workflow record was updated.",
                $"{DefinitionId}-notification-message"),
            NotificationSeverity = new("Success", $"{DefinitionId}-notification-severity"),
            AutoCompleteOpenTasks = new(true, $"{DefinitionId}-completed-auto-complete"),
            IsActive = new(false, $"{DefinitionId}-completed-is-active")
        };
    }
}

public sealed class PlanningApprovalWorkflow : AuditCallbackWorkflowBase
{
    protected override string DefinitionId => "Audit.Planning.PlanningApproval.v1";
    protected override string DisplayName => "Planning Approval Workflow";
    protected override string PendingStatus => "Awaiting Planning Approval";
    protected override string PendingActivityId => "AwaitingPlanningApproval";
    protected override string PendingActivityName => "Awaiting planning approval";
    protected override string CompletionNotificationType => "Approval";

    protected override void ConfigureInputs(IWorkflowBuilder builder)
    {
        builder.WithInput("EngagementTitle", typeof(string), "Engagement or assessment title");
    }
}

public sealed class AnnualPlanApprovalWorkflow : AuditCallbackWorkflowBase
{
    protected override string DefinitionId => "Audit.Planning.AnnualPlanApproval.v1";
    protected override string DisplayName => "Annual Audit Plan Approval Workflow";
    protected override string PendingStatus => "Awaiting Annual Plan Approval";
    protected override string PendingActivityId => "AwaitingAnnualPlanApproval";
    protected override string PendingActivityName => "Awaiting annual audit plan approval";
    protected override string CompletionNotificationType => "Approval";

    protected override void ConfigureInputs(IWorkflowBuilder builder)
    {
        builder.WithInput("AnnualPlanName", typeof(string), "Annual audit plan name");
        builder.WithInput("PlanYear", typeof(int?), "Annual audit plan year");
    }
}

public sealed class ScopeApprovalWorkflow : AuditCallbackWorkflowBase
{
    protected override string DefinitionId => "Audit.Planning.ScopeApproval.v1";
    protected override string DisplayName => "Scope Approval Workflow";
    protected override string PendingStatus => "Awaiting Scope Approval";
    protected override string PendingActivityId => "AwaitingScopeApproval";
    protected override string PendingActivityName => "Awaiting scope approval";
    protected override string CompletionNotificationType => "Approval";

    protected override void ConfigureInputs(IWorkflowBuilder builder)
    {
        builder.WithInput("ScopeSummary", typeof(string), "Summary of the requested scope");
    }
}

public sealed class ControlTestingWorkflow : AuditCallbackWorkflowBase
{
    protected override string DefinitionId => "Audit.Execution.ControlTesting.v1";
    protected override string DisplayName => "Control Testing Workflow";
    protected override string PendingStatus => "Awaiting Control Testing Completion";
    protected override string PendingActivityId => "AwaitingControlTesting";
    protected override string PendingActivityName => "Awaiting control testing completion";
    protected override string CompletionNotificationType => "Workflow";

    protected override void ConfigureInputs(IWorkflowBuilder builder)
    {
        builder.WithInput("ControlId", typeof(string), "Control identifier");
        builder.WithInput("TesterId", typeof(string), "Assigned tester identifier");
        builder.WithInput("TesterName", typeof(string), "Assigned tester name");
        builder.WithInput("TestFrequency", typeof(string), "Control testing frequency");
        builder.WithInput("TestResult", typeof(string), "Current testing result");
    }
}

public sealed class WalkthroughReviewWorkflow : AuditCallbackWorkflowBase
{
    protected override string DefinitionId => "Audit.Execution.WalkthroughReview.v1";
    protected override string DisplayName => "Walkthrough Review Workflow";
    protected override string PendingStatus => "Awaiting Walkthrough Review";
    protected override string PendingActivityId => "AwaitingWalkthroughReview";
    protected override string PendingActivityName => "Awaiting walkthrough review";
    protected override string CompletionNotificationType => "Review";

    protected override void ConfigureInputs(IWorkflowBuilder builder)
    {
        builder.WithInput("WalkthroughId", typeof(int), "Walkthrough identifier");
        builder.WithInput("ProcessName", typeof(string), "Walkthrough process name");
    }
}

public sealed class WorkingPaperReviewWorkflow : AuditCallbackWorkflowBase
{
    protected override string DefinitionId => "Audit.Execution.WorkpaperReview.v1";
    protected override string DisplayName => "Working Paper Review Workflow";
    protected override string PendingStatus => "Awaiting Working Paper Review";
    protected override string PendingActivityId => "AwaitingWorkingPaperReview";
    protected override string PendingActivityName => "Awaiting working paper review";
    protected override string CompletionNotificationType => "Review";

    protected override void ConfigureInputs(IWorkflowBuilder builder)
    {
        builder.WithInput("WorkingPaperId", typeof(int), "Working paper identifier");
        builder.WithInput("WorkingPaperCode", typeof(string), "Working paper code");
        builder.WithInput("WorkingPaperTitle", typeof(string), "Working paper title");
    }
}

public sealed class FindingApprovalWorkflow : AuditCallbackWorkflowBase
{
    protected override string DefinitionId => "Audit.Reporting.FindingApproval.v1";
    protected override string DisplayName => "Finding Review Workflow";
    protected override string PendingStatus => "Awaiting Finding Review";
    protected override string PendingActivityId => "AwaitingFindingReview";
    protected override string PendingActivityName => "Awaiting finding review";
    protected override string CompletionNotificationType => "Review";

    protected override void ConfigureInputs(IWorkflowBuilder builder)
    {
        builder.WithInput("FindingId", typeof(int?), "Finding identifier");
        builder.WithInput("FindingNumber", typeof(string), "Finding number");
        builder.WithInput("FindingTitle", typeof(string), "Finding title");
    }
}

public sealed class ManagementResponseWorkflow : AuditCallbackWorkflowBase
{
    protected override string DefinitionId => "Audit.Reporting.ManagementResponse.v1";
    protected override string DisplayName => "Management Response Workflow";
    protected override string PendingStatus => "Awaiting Management Response";
    protected override string PendingActivityId => "AwaitingManagementResponse";
    protected override string PendingActivityName => "Awaiting management response";
    protected override string CompletionNotificationType => "Response";

    protected override void ConfigureInputs(IWorkflowBuilder builder)
    {
        builder.WithInput("RecommendationId", typeof(int), "Recommendation identifier");
        builder.WithInput("RecommendationNumber", typeof(string), "Recommendation number");
        builder.WithInput("RecommendationTitle", typeof(string), "Recommendation title");
    }
}

public sealed class RemediationReviewWorkflow : AuditCallbackWorkflowBase
{
    protected override string DefinitionId => "Audit.FollowUp.RemediationReview.v1";
    protected override string DisplayName => "Remediation Follow-Up Workflow";
    protected override string PendingStatus => "Awaiting Remediation Review";
    protected override string PendingActivityId => "AwaitingRemediationReview";
    protected override string PendingActivityName => "Awaiting remediation review";
    protected override string CompletionNotificationType => "FollowUp";

    protected override void ConfigureInputs(IWorkflowBuilder builder)
    {
        builder.WithInput("RecommendationId", typeof(int), "Recommendation identifier");
        builder.WithInput("RecommendationNumber", typeof(string), "Recommendation number");
        builder.WithInput("RecommendationTitle", typeof(string), "Recommendation title");
    }
}

public sealed class FinalReportSignOffWorkflow : AuditCallbackWorkflowBase
{
    protected override string DefinitionId => "Audit.Reporting.FinalSignOff.v1";
    protected override string DisplayName => "Final Report Sign-Off Workflow";
    protected override string PendingStatus => "Awaiting Final Report Sign-Off";
    protected override string PendingActivityId => "AwaitingFinalReportSignOff";
    protected override string PendingActivityName => "Awaiting final report sign-off";
    protected override string CompletionNotificationType => "Approval";

    protected override void ConfigureInputs(IWorkflowBuilder builder)
    {
        builder.WithInput("ReportTitle", typeof(string), "Report title");
    }
}
