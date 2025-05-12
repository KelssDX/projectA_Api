using System;
using System.Linq;
using System.Threading.Tasks;
using Affine.Engine.Model.Auditing.Assessment;
using Affine.Engine.Repository.Auditing;
using Affine.Tests.Helpers;
using Xunit;

namespace Affine.Tests.Repositories
{
    public class RiskHeatMapRepositoryTests : IClassFixture<PostgresTestDbHelper>, IAsyncLifetime
    {
        private readonly PostgresTestDbHelper _dbHelper;
        private IRiskHeatMapRepository _repository;
        private IRiskAssessmentRepository _assessmentRepository;
        private string _connectionString;

        public RiskHeatMapRepositoryTests(PostgresTestDbHelper dbHelper)
        {
            _dbHelper = dbHelper;
        }

        public async Task InitializeAsync()
        {
            await _dbHelper.InitializeAsync();
            _connectionString = _dbHelper.GetConnectionString();
            _repository = new RiskHeatMapRepository(_connectionString);
            _assessmentRepository = new RiskAssessmentRepository(_connectionString);
            
            // Create sample data for heat map tests
            await CreateSampleData();
        }

        public async Task DisposeAsync()
        {
            await _dbHelper.DisposeAsync();
        }

        [Fact]
        public async Task GetHeatMapAsync_ShouldReturnHeatMapData()
        {
            // Arrange
            int referenceId = 1; // From sample data

            // Act
            var result = await _repository.GetHeatMapAsync(referenceId);

            // Assert
            Assert.NotNull(result);
            Assert.NotNull(result.heatMap);
            Assert.NotNull(result.impactList);
            Assert.NotNull(result.likelihoodList);
            
            // Verify impact and likelihood lists
            Assert.Equal(3, result.impactList.Count);
            Assert.Equal(3, result.likelihoodList.Count);
            
            // Verify heat map data based on sample data
            Assert.True(result.heatMap.Any(h => h.likelihoodId == 1 && h.impactId == 1));
            Assert.True(result.heatMap.Any(h => h.likelihoodId == 2 && h.impactId == 2));
        }

        [Fact]
        public async Task GetHeatMapAsync_WithInvalidReferenceId_ShouldReturnEmptyHeatMap()
        {
            // Arrange
            int invalidReferenceId = 999;

            // Act
            var result = await _repository.GetHeatMapAsync(invalidReferenceId);

            // Assert
            Assert.NotNull(result);
            Assert.Empty(result.heatMap);
            Assert.NotEmpty(result.impactList);
            Assert.NotEmpty(result.likelihoodList);
        }

        [Fact]
        public async Task GetRiskGraphAsync_ShouldReturnRiskCategoryData()
        {
            // Arrange
            int referenceId = 1; // From sample data

            // Act
            var result = await _repository.GetRiskGraphAsync(referenceId);

            // Assert
            Assert.NotNull(result);
            Assert.NotEmpty(result);
            
            // Verify risk categories in the result based on sample data
            var riskCategories = result.Select(r => r.category).ToList();
            Assert.Contains("Test Category", riskCategories);
        }

        [Fact]
        public async Task GetRiskGraphAsync_WithInvalidReferenceId_ShouldReturnEmptyList()
        {
            // Arrange
            int invalidReferenceId = 999;

            // Act
            var result = await _repository.GetRiskGraphAsync(invalidReferenceId);

            // Assert
            Assert.NotNull(result);
            Assert.Empty(result);
        }

        private async Task CreateSampleData()
        {
            // Create a risk assessment reference
            var reference = new RiskAssessmentReference
            {
                Client = "Heat Map Test Client",
                Assessor = "Heat Map Test Assessor",
                ApprovedBy = "Heat Map Test Approver",
                AssessmentStartDate = DateTime.Now.AddDays(-30),
                AssessmentEndDate = DateTime.Now
            };

            var referenceId = await _assessmentRepository.AddRiskAssessmentReferenceAsync(reference);

            // Create risk assessments with different likelihood and impact combinations
            var assessments = new System.Collections.Generic.List<RiskAssessmentCreateRequest>
            {
                new RiskAssessmentCreateRequest
                {
                    BusinessObjectives = "Business Objectives 1",
                    MainProcess = "Main Process 1",
                    SubProcess = "Sub Process 1",
                    KeyRiskAndFactors = "Key Risk 1",
                    MitigatingControls = "Mitigating Controls 1",
                    Responsibility = "Responsibility 1",
                    Authoriser = "Authoriser 1",
                    AuditorsRecommendedActionPlan = "Action Plan 1",
                    ResponsiblePerson = "Person 1",
                    AgreedDate = DateTime.Now,
                    RiskLikelihoodId = 1, // Low
                    RiskImpactId = 1, // Low
                    KeySecondaryId = 1,
                    RiskCategoryId = 1, // Test Category
                    DataFrequencyId = 1,
                    FrequencyId = 1,
                    EvidenceId = 1,
                    OutcomeLikelihoodId = 1,
                    ImpactId = 1
                },
                new RiskAssessmentCreateRequest
                {
                    BusinessObjectives = "Business Objectives 2",
                    MainProcess = "Main Process 2",
                    SubProcess = "Sub Process 2",
                    KeyRiskAndFactors = "Key Risk 2",
                    MitigatingControls = "Mitigating Controls 2",
                    Responsibility = "Responsibility 2",
                    Authoriser = "Authoriser 2",
                    AuditorsRecommendedActionPlan = "Action Plan 2",
                    ResponsiblePerson = "Person 2",
                    AgreedDate = DateTime.Now,
                    RiskLikelihoodId = 2, // Medium
                    RiskImpactId = 2, // Medium
                    KeySecondaryId = 1,
                    RiskCategoryId = 1, // Test Category
                    DataFrequencyId = 1,
                    FrequencyId = 1,
                    EvidenceId = 1,
                    OutcomeLikelihoodId = 1,
                    ImpactId = 1
                },
                new RiskAssessmentCreateRequest
                {
                    BusinessObjectives = "Business Objectives 3",
                    MainProcess = "Main Process 3",
                    SubProcess = "Sub Process 3",
                    KeyRiskAndFactors = "Key Risk 3",
                    MitigatingControls = "Mitigating Controls 3",
                    Responsibility = "Responsibility 3",
                    Authoriser = "Authoriser 3",
                    AuditorsRecommendedActionPlan = "Action Plan 3",
                    ResponsiblePerson = "Person 3",
                    AgreedDate = DateTime.Now,
                    RiskLikelihoodId = 2, // Medium
                    RiskImpactId = 2, // Medium (duplicate to test count)
                    KeySecondaryId = 1,
                    RiskCategoryId = 2, // Another category
                    DataFrequencyId = 1,
                    FrequencyId = 1,
                    EvidenceId = 1,
                    OutcomeLikelihoodId = 1,
                    ImpactId = 1
                }
            };

            // Add the assessments
            await _assessmentRepository.AddRiskAssessmentAsync(assessments, reference, referenceId);
        }
    }
} 