using Elsa.EntityFrameworkCore.Extensions;
using Elsa.EntityFrameworkCore.Modules.Management;
using Elsa.EntityFrameworkCore.Modules.Runtime;
using Elsa.Extensions;
using Affine.Auditing.Workflows.Server.Activities;
using Affine.Auditing.Workflows.Server.Workflows;

var builder = WebApplication.CreateBuilder(args);

builder.Logging.ClearProviders();
builder.Logging.AddConsole();
builder.Logging.AddDebug();

builder.Services.AddHttpClient();

// Add services to the container.
builder.Services.AddElsa(elsa =>
{
    elsa.UseWorkflowManagement(management =>
    {
        management.UseEntityFrameworkCore(ef => ef.UsePostgreSql(builder.Configuration.GetConnectionString("RiskWorkflow") ?? ""));
    });

    elsa.UseWorkflowRuntime(runtime =>
    {
        runtime.UseEntityFrameworkCore(ef => ef.UsePostgreSql(builder.Configuration.GetConnectionString("RiskWorkflow") ?? ""));
    });

    elsa.UseIdentity(identity =>
    {
        identity.TokenOptions = options => options.SigningKey = "sufficiently-large-secret-signing-key"; // This key needs to be at least 256 bits.
        identity.UseAdminUserProvider();
    });

    elsa.UseDefaultAuthentication(auth => auth.UseAdminApiKey());
    elsa.UseWorkflowsApi();
    elsa.UseScheduling();
    elsa.UseHttp();
    elsa.UseJavaScript();
    elsa.UseLiquid();
    elsa.UseCSharp();

    elsa.AddActivity<SyncAuditWorkflowStateActivity>();
    elsa.AddWorkflow<PlanningApprovalWorkflow>();
    elsa.AddWorkflow<AnnualPlanApprovalWorkflow>();
    elsa.AddWorkflow<ScopeApprovalWorkflow>();
    elsa.AddWorkflow<ControlTestingWorkflow>();
    elsa.AddWorkflow<WalkthroughReviewWorkflow>();
    elsa.AddWorkflow<WorkingPaperReviewWorkflow>();
    elsa.AddWorkflow<FindingApprovalWorkflow>();
    elsa.AddWorkflow<ManagementResponseWorkflow>();
    elsa.AddWorkflow<RemediationReviewWorkflow>();
    elsa.AddWorkflow<FinalReportSignOffWorkflow>();
});

// Add CORS
builder.Services.AddCors(options =>
{
    options.AddDefaultPolicy(policy =>
    {
        policy.AllowAnyOrigin()
              .AllowAnyHeader()
              .AllowAnyMethod();
    });
});

// Add Razor Pages
builder.Services.AddRazorPages();

var app = builder.Build();

// Configure the HTTP request pipeline.
if (!app.Environment.IsDevelopment())
{
    app.UseExceptionHandler("/Error");
    app.UseHsts();
}

app.UseHttpsRedirection();
app.UseStaticFiles();

// Use CORS before routing
app.UseCors();

app.UseAuthentication();
app.UseAuthorization();
app.UseWorkflowsApi();
app.UseWorkflows();

app.MapRazorPages();

app.Run(); 
