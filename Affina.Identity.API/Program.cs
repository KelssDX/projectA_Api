using Affine.Engine.Repository.Identity;
using Microsoft.OpenApi.Models;
using Npgsql;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container.

// Add Swagger generation with a Swagger document for the API
builder.Services.AddSwaggerGen(c =>
{
    c.SwaggerDoc("v1", new OpenApiInfo { Title = "Your API", Version = "v1" });
});

// Create a NpgsqlConnectionStringBuilder to construct the connection string
var connectionStringBuilder = new NpgsqlConnectionStringBuilder(builder.Configuration.GetConnectionString("RiskAssessment"));

// Add the schema or search path settings directly to the connection string
connectionStringBuilder.SearchPath = "\"Risk_Assess_Framework\",public,\"$user\"";

// Add scoped dependency injection for IUserRepository and UserRepository with the modified connection string
builder.Services.AddScoped<IUserRepository, UserRepository>(provider =>
    new UserRepository(connectionStringBuilder.ToString()));

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
