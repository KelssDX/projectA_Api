using Affine.Engine.Repository.Auditing;
using Affine.Engine.Repository.Identity;
using Affine.Engine.Repository.Market;
using Affine.Engine.Repository.Operational;
using Affine.Engine.Services;
using Affine.Auditing.API.Services;
using Microsoft.OpenApi.Models;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container.
builder.Logging.ClearProviders();
builder.Logging.AddConsole();
builder.Logging.AddDebug();

// Add Swagger generation with a Swagger document for the API
builder.Services.AddSwaggerGen(c =>
{
    c.SwaggerDoc("v1", new OpenApiInfo { Title = "Your API", Version = "v1" });
});

// Add HttpClient for workflow service integration
builder.Services.AddHttpClient();

//Add scoped dependency injection 
builder.Services.AddScoped<IUserRepository, UserRepository>(provider =>
    new UserRepository(builder.Configuration.GetConnectionString("RiskAssessment")));

builder.Services.AddScoped<IRiskAssessmentRepository, RiskAssessmentRepository>(provider =>
    new RiskAssessmentRepository(builder.Configuration.GetConnectionString("RiskAssessment")));


builder.Services.AddScoped<IRiskHeatMapRepository, RiskHeatMapRepository>(provider =>
    new RiskHeatMapRepository (builder.Configuration.GetConnectionString("RiskAssessment")));

// New Risk Services
builder.Services.AddScoped<IMarketDataRepository, MarketDataRepository>(provider =>
    new MarketDataRepository(builder.Configuration.GetConnectionString("RiskAssessment")));

builder.Services.AddScoped<IOperationalRiskRepository, OperationalRiskRepository>(provider =>
    new OperationalRiskRepository(builder.Configuration.GetConnectionString("RiskAssessment")));

builder.Services.AddHttpClient<IAlphaVantageService, AlphaVantageService>();

builder.Services.AddScoped<Affine.Engine.Repository.Analytics.IAnalyticsRepository, Affine.Engine.Repository.Analytics.AnalyticsRepository>(provider =>
    new Affine.Engine.Repository.Analytics.AnalyticsRepository(builder.Configuration.GetConnectionString("RiskAssessment")));

// Audit Universe and Findings Repositories
builder.Services.AddScoped<IAuditUniverseRepository, AuditUniverseRepository>(provider =>
    new AuditUniverseRepository(builder.Configuration.GetConnectionString("RiskAssessment")));

builder.Services.AddScoped<IAuditFindingsRepository, AuditFindingsRepository>(provider =>
    new AuditFindingsRepository(builder.Configuration.GetConnectionString("RiskAssessment")));

builder.Services.AddScoped<IAuditProceduresRepository, AuditProceduresRepository>(provider =>
    new AuditProceduresRepository(builder.Configuration.GetConnectionString("RiskAssessment")));

builder.Services.AddScoped<IAuditWorkingPapersRepository, AuditWorkingPapersRepository>(provider =>
    new AuditWorkingPapersRepository(builder.Configuration.GetConnectionString("RiskAssessment")));

builder.Services.AddScoped<IAuditDocumentsRepository, AuditDocumentsRepository>(provider =>
    new AuditDocumentsRepository(builder.Configuration.GetConnectionString("RiskAssessment")));

builder.Services.AddScoped<IAuditExecutionRepository, AuditExecutionRepository>(provider =>
    new AuditExecutionRepository(builder.Configuration.GetConnectionString("RiskAssessment")));

builder.Services.AddScoped<IAuditWorkflowRepository, AuditWorkflowRepository>(provider =>
    new AuditWorkflowRepository(builder.Configuration.GetConnectionString("RiskAssessment")));

builder.Services.AddScoped<IAuditAnalyticsRepository, AuditAnalyticsRepository>(provider =>
    new AuditAnalyticsRepository(builder.Configuration.GetConnectionString("RiskAssessment")));

builder.Services.AddScoped<IAuditMaterialityRepository, AuditMaterialityRepository>(provider =>
    new AuditMaterialityRepository(builder.Configuration.GetConnectionString("RiskAssessment")));

builder.Services.AddScoped<IAuditReportingRepository, AuditReportingRepository>(provider =>
    new AuditReportingRepository(builder.Configuration.GetConnectionString("RiskAssessment")));

builder.Services.AddScoped<IAuditTrailRepository, AuditTrailRepository>(provider =>
    new AuditTrailRepository(builder.Configuration.GetConnectionString("RiskAssessment")));

builder.Services.AddScoped<IAuditPlatformRepository, AuditPlatformRepository>(provider =>
    new AuditPlatformRepository(builder.Configuration.GetConnectionString("RiskAssessment")));

builder.Services.AddScoped<IAuditReviewsRepository, AuditReviewsRepository>(provider =>
    new AuditReviewsRepository(builder.Configuration.GetConnectionString("RiskAssessment")));

builder.Services.AddScoped<IAuditAccessLogRepository, AuditAccessLogRepository>(provider =>
    new AuditAccessLogRepository(builder.Configuration.GetConnectionString("RiskAssessment")));

builder.Services.AddHttpClient<IAuditWorkflowService, AuditWorkflowService>();
builder.Services.AddScoped<IAuditTrailService, AuditTrailService>();
builder.Services.AddHostedService<AuditWorkflowReminderHostedService>();

builder.Services.AddControllers();

// Add configuration for workflow service
builder.Configuration.AddJsonFile("appsettings.json", optional: false, reloadOnChange: true);
builder.Configuration.AddJsonFile($"appsettings.{builder.Environment.EnvironmentName}.json", optional: true);
builder.Configuration.AddEnvironmentVariables();

var app = builder.Build();

// Configure the HTTP request pipeline.

if (app.Environment.IsDevelopment())
{
    // Enable middleware to serve generated Swagger as a JSON endpoint.
    app.UseSwagger();
    // Enable middleware to serve swagger-ui (HTML, JS, CSS, etc.),
    // specifying the Swagger JSON endpoint.
    app.UseSwaggerUI(c => c.SwaggerEndpoint("/swagger/v1/swagger.json", "Your API V1"));
}

app.UseHttpsRedirection();

app.UseRouting();

app.UseAuthorization();

app.MapControllers();

app.Run();
