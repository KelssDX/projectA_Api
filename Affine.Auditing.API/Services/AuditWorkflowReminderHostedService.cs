using Affine.Engine.Services;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;

namespace Affine.Auditing.API.Services
{
    public class AuditWorkflowReminderHostedService : BackgroundService
    {
        private readonly IServiceProvider _serviceProvider;
        private readonly IConfiguration _configuration;
        private readonly ILogger<AuditWorkflowReminderHostedService> _logger;

        public AuditWorkflowReminderHostedService(
            IServiceProvider serviceProvider,
            IConfiguration configuration,
            ILogger<AuditWorkflowReminderHostedService> logger)
        {
            _serviceProvider = serviceProvider;
            _configuration = configuration;
            _logger = logger;
        }

        protected override async Task ExecuteAsync(CancellationToken stoppingToken)
        {
            if (!IsEnabled())
            {
                _logger.LogInformation("Workflow reminder hosted service is disabled.");
                return;
            }

            var intervalMinutes = GetIntervalMinutes();
            _logger.LogInformation("Workflow reminder hosted service started with {IntervalMinutes} minute interval.", intervalMinutes);

            while (!stoppingToken.IsCancellationRequested)
            {
                try
                {
                    using var scope = _serviceProvider.CreateScope();
                    var workflowService = scope.ServiceProvider.GetRequiredService<IAuditWorkflowService>();
                    var result = await workflowService.RunReminderSweepAsync();
                    _logger.LogInformation(
                        "Workflow reminder sweep completed. Tasks={TasksEvaluated}, DueSoon={DueSoon}, ReviewReady={ReviewReady}, Overdue={Overdue}, Escalations={Escalations}",
                        result.TasksEvaluated,
                        result.DueSoonRemindersCreated,
                        result.ReviewReadyNotificationsCreated,
                        result.OverdueRemindersCreated,
                        result.EscalationsCreated);
                }
                catch (Exception ex)
                {
                    _logger.LogError(ex, "Workflow reminder sweep failed.");
                }

                await Task.Delay(TimeSpan.FromMinutes(intervalMinutes), stoppingToken);
            }
        }

        private bool IsEnabled()
        {
            var raw = _configuration["WorkflowReminders:Enabled"];
            return string.IsNullOrWhiteSpace(raw) || !raw.Equals("false", StringComparison.OrdinalIgnoreCase);
        }

        private int GetIntervalMinutes()
        {
            var raw = _configuration["WorkflowReminders:IntervalMinutes"];
            return int.TryParse(raw, out var value) && value > 0 ? value : 15;
        }
    }
}
