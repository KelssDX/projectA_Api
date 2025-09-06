# Elsa Workflows for Risk Assessment

This module implements workflow automation for risk assessment approval processes using Elsa Workflows.

## Projects

- **Affine.Auditing.Workflows.Server**: API server that hosts the Elsa workflow engine
- **Affine.Auditing.Workflows.Studio**: Web interface for designing and managing workflows

## Features

- Risk assessment approval workflows
- Email notifications for approvers
- Tracking of approval status and comments
- Visual workflow designer

## Workflow Components

### Activities

- **RiskAssessmentApprovalActivity**: Custom activity that assigns a risk assessment for approval and waits for an approval decision.

### Workflows

- **RiskAssessmentApprovalWorkflow**: Example workflow that sends notifications, waits for approval, and processes the result.

### API Endpoints

- **POST /api/workflows/risk-assessment/start/{riskAssessmentId}**: Start an approval workflow for a risk assessment
- **POST /api/workflows/risk-assessment/approval/{riskAssessmentId}**: Submit an approval decision for a risk assessment

## Integration with Existing System

The workflow server integrates with the existing risk assessment system by:

1. Using PostgreSQL as the workflow state persistence layer
2. Exposing REST APIs for initiating and interacting with workflows
3. Providing webhook capabilities for external system integration

## Getting Started

1. Configure the database connection string in `appsettings.json`
2. Run the Workflow Server
3. Run the Studio application to design and deploy workflows
4. Use the API endpoints to initiate workflows for risk assessments

## Example API Usage

```csharp
// Start an approval workflow
var client = new HttpClient();
var startRequest = new StartApprovalRequest
{
    WorkflowDefinitionId = "RiskAssessmentApprovalWorkflow",
    ApproverId = "user@example.com",
    ApprovalDeadline = DateTime.UtcNow.AddDays(3)
};

await client.PostAsJsonAsync($"api/workflows/risk-assessment/start/{riskAssessmentId}", startRequest);

// Submit an approval decision
var approvalRequest = new ApprovalSubmissionRequest
{
    IsApproved = true,
    Comments = "Looks good, approved!"
};

await client.PostAsJsonAsync($"api/workflows/risk-assessment/approval/{riskAssessmentId}", approvalRequest);
``` 