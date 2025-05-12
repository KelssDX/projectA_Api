using System;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.AspNetCore.TestHost;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Affine.Auditing.API;
using Affine.Engine.Repository.Auditing;

namespace Affine.Tests.Helpers
{
    public class AffineApiFactory : WebApplicationFactory<Program>
    {
        private readonly PostgresTestDbHelper _postgresTestDbHelper;

        public AffineApiFactory()
        {
            _postgresTestDbHelper = new PostgresTestDbHelper();
            _postgresTestDbHelper.InitializeAsync().GetAwaiter().GetResult();
        }

        protected override void ConfigureWebHost(IWebHostBuilder builder)
        {
            builder.ConfigureAppConfiguration((context, config) =>
            {
                // Add test-specific configuration
                var configValues = new[]
                {
                    KeyValuePair.Create("ConnectionStrings:RiskAssessment", _postgresTestDbHelper.GetConnectionString())
                };

                config.AddInMemoryCollection(configValues);
            });

            builder.ConfigureTestServices(services =>
            {
                // Replace services for testing if needed
                // Example: services.AddScoped<IRiskAssessmentRepository, TestRiskAssessmentRepository>();
            });
        }

        public string GetConnectionString()
        {
            return _postgresTestDbHelper.GetConnectionString();
        }

        protected override void Dispose(bool disposing)
        {
            if (disposing)
            {
                _postgresTestDbHelper.DisposeAsync().GetAwaiter().GetResult();
            }

            base.Dispose(disposing);
        }
    }
} 