using Affine.Engine.Repository.Auditing;
using Affine.Engine.Repository.Identity;
using Microsoft.OpenApi.Models;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container.

// Add Swagger generation with a Swagger document for the API
builder.Services.AddSwaggerGen(c =>
{
    c.SwaggerDoc("v1", new OpenApiInfo { Title = "Your API", Version = "v1" });
});

//Add scoped dependency injection 
builder.Services.AddScoped<IUserRepository, UserRepository>(provider =>
    new UserRepository(builder.Configuration.GetConnectionString("RiskAssessment")));

builder.Services.AddScoped<IRiskAssessmentRepository, RiskAssessmentRepository>(provider =>
    new RiskAssessmentRepository(builder.Configuration.GetConnectionString("RiskAssessment")));


builder.Services.AddScoped<IRiskHeatMapRepository, RiskHeatMapRepository>(provider =>
    new RiskHeatMapRepository (builder.Configuration.GetConnectionString("RiskAssessment")));

builder.Services.AddControllers();

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