using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Affine.Engine.Model.Auditing.Assessment;
using Affine.Engine.Repository.Auditing;
using Affine.Tests.Helpers;
using Xunit;

namespace Affine.Tests.Repositories
{
    public class RiskAssessmentRepositoryTests : IClassFixture<PostgresTestDbHelper>, IAsyncLifetime
    {
        private readonly PostgresTestDbHelper _dbHelper;
        private IRiskAssessmentRepository _repository;
        private string _connectionString;

        public RiskAssessmentRepositoryTests(PostgresTestDbHelper dbHelper)
        {
            _dbHelper = dbHelper;
        }

        public async Task InitializeAsync()
        {
            await _dbHelper.InitializeAsync();
            _connectionString = _dbHelper.GetConnectionString();
            _repository = new RiskAssessmentRepository(_connectionString);
        }

        public async Task DisposeAsync()
        {
            await _dbHelper.DisposeAsync();
        }

        [Fact]
        public async Task GetRiskAssessmentAsync_ShouldReturnSingleRiskAssessment()
        {
            // Arrange
            int referenceId = 1; // From test data in PostgresTestDbHelper

            // Act
            var result = await _repository.GetRiskAssessmentAsync(referenceId);

            // Assert
            Assert.NotNull(result);
            Assert.Equal(referenceId, result.ReferenceId);
            Assert.Equal("Test Client", result.Client);
            Assert.NotEmpty(result.RiskAssessments);
        }

        [Fact]
        public async Task GetRiskLikelihoodsAsync_ShouldReturnAllRiskLikelihoods()
        {
            // Act
            var result = await _repository.GetRiskLikelihoodsAsync();

            // Assert
            Assert.NotNull(result);
            Assert.Equal(3, result.Count());
            Assert.Contains(result, r => r.Description == "Low");
            Assert.Contains(result, r => r.Description == "Medium");
            Assert.Contains(result, r => r.Description == "High");
        }

        [Fact]
        public async Task GetImpactsAsync_ShouldReturnAllImpacts()
        {
            // Act
            var result = await _repository.GetImpactsAsync();

            // Assert
            Assert.NotNull(result);
            Assert.Equal(3, result.Count());
        }

        [Fact]
        public async Task GetEvidenceAsync_ShouldReturnAllEvidence()
        {
            // Act
            var result = await _repository.GetEvidenceAsync();

            // Assert
            Assert.NotNull(result);
            Assert.Equal(3, result.Count());
        }

        [Fact]
        public async Task AddRiskAssessmentReferenceAsync_ShouldAddReferenceAndReturnId()
        {
            // Arrange
            var reference = new RiskAssessmentReferenceInput
            {
                Client = "Test Reference Client",
                Assessor = "Test Assessor",
                ApprovedBy = "Test Approver",
                AssessmentStartDate = DateTime.Now.AddDays(-10),
                AssessmentEndDate = DateTime.Now
            };

            // Act
            var result = await _repository.AddRiskAssessmentReferenceAsync(reference);

            // Assert
            Assert.True(result > 0);
        }

        [Fact]
        public async Task AddRiskAssessmentAsync_ShouldAddRiskAssessment()
        {
            // Arrange
            var reference = new RiskAssessmentReferenceInput
            {
                Client = "Add Test Client",
                Assessor = "Add Test Assessor",
                ApprovedBy = "Add Test Approver",
                AssessmentStartDate = DateTime.Now.AddDays(-30),
                AssessmentEndDate = DateTime.Now
            };

            var requests = new List<RiskAssessmentCreateRequest>
            {
                new RiskAssessmentCreateRequest
                {
                    BusinessObjectives = "Test Business Objectives",
                    MainProcess = "Test Main Process",
                    SubProcess = "Test Sub Process",
                    KeyRiskAndFactors = "Test Key Risk Factors",
                    MitigatingControls = "Test Mitigating Controls",
                    Responsibility = "Test Responsibility",
                    Authoriser = "Test Authoriser",
                    AuditorsRecommendedActionPlan = "Test Action Plan",
                    ResponsiblePerson = "Test Person",
                    AgreedDate = DateTime.Now,
                    RiskLikelihoodId = 1,
                    RiskImpactId = 2,
                    KeySecondaryId = 1,
                    RiskCategoryId = 1,
                    DataFrequencyId = 1,
                    FrequencyId = 1,
                    EvidenceId = 1,
                    OutcomeLikelihoodId = 1,
                    ImpactId = 1
                }
            };

            // Act
            var result = await _repository.AddRiskAssessmentAsync(requests, reference);

            // Assert
            Assert.True(result);

            // Verify
            var assessments = await _repository.GetRiskAssessmentAsync(1); // Get the first assessment
            Assert.NotNull(assessments);
            Assert.Equal("Add Test Client", assessments.Client);
            Assert.Single(assessments.RiskAssessments);
        }

        [Fact]
        public async Task UpdateRiskAssessmentsAsync_ShouldUpdateRiskAssessment()
        {
            // Arrange
            var reference = new RiskAssessmentReferenceInput
            {
                Client = "Update Test Client",
                Assessor = "Update Test Assessor",
                ApprovedBy = "Update Test Approver",
                AssessmentStartDate = DateTime.Now.AddDays(-30),
                AssessmentEndDate = DateTime.Now
            };

            var referenceId = await _repository.AddRiskAssessmentReferenceAsync(reference);

            var requests = new List<RiskAssessmentCreateRequest>
            {
                new RiskAssessmentCreateRequest
                {
                    BusinessObjectives = "Original Business Objectives",
                    MainProcess = "Original Main Process",
                    SubProcess = "Original Sub Process",
                    KeyRiskAndFactors = "Original Key Risk Factors",
                    MitigatingControls = "Original Mitigating Controls",
                    Responsibility = "Original Responsibility",
                    Authoriser = "Original Authoriser",
                    AuditorsRecommendedActionPlan = "Original Action Plan",
                    ResponsiblePerson = "Original Person",
                    AgreedDate = DateTime.Now,
                    RiskLikelihoodId = 1,
                    RiskImpactId = 2,
                    KeySecondaryId = 1,
                    RiskCategoryId = 1,
                    DataFrequencyId = 1,
                    FrequencyId = 1,
                    EvidenceId = 1,
                    OutcomeLikelihoodId = 1,
                    ImpactId = 1
                }
            };

            await _repository.AddRiskAssessmentAsync(requests, reference, referenceId);

            // Get the created assessment to retrieve its ID
            var assessments = await _repository.GetRiskAssessmentAsync(referenceId);
            var assessmentRefId = assessments.RiskAssessments.First().RiskAssessment_RefID;

            var updates = new List<RiskAssessmentUpdateRequest>
            {
                new RiskAssessmentUpdateRequest
                {
                    RiskAssessmentRefId = assessmentRefId,
                    BusinessObjectives = "Updated Business Objectives",
                    MainProcess = "Updated Main Process",
                    SubProcess = "Updated Sub Process",
                    KeyRiskAndFactors = "Updated Key Risk Factors",
                    MitigatingControls = "Updated Mitigating Controls",
                    Responsibility = "Updated Responsibility",
                    Authoriser = "Updated Authoriser",
                    AuditorsRecommendedActionPlan = "Updated Action Plan",
                    ResponsiblePerson = "Updated Person",
                    AgreedDate = DateTime.Now.AddDays(1),
                    RiskLikelihoodId = 2,
                    RiskImpactId = 3,
                    KeySecondaryId = 2,
                    RiskCategoryId = 2,
                    DataFrequencyId = 2,
                    FrequencyId = 2,
                    EvidenceId = 2,
                    OutcomeLikelihoodId = 2,
                    ImpactId = 2
                }
            };

            // Act
            var result = await _repository.UpdateRiskAssessmentsAsync(updates, referenceId);

            // Assert
            Assert.True(result);

            // Verify
            var updatedAssessments = await _repository.GetRiskAssessmentAsync(referenceId);
            var updatedAssessment = updatedAssessments.RiskAssessments.First();
            Assert.Equal("Updated Business Objectives", updatedAssessment.ProcessObjectivesAssessment_BusinessObjectives);
            Assert.Equal("Updated Main Process", updatedAssessment.ProcessObjectivesAssessment_MainProcess);
            Assert.Equal("Updated Sub Process", updatedAssessment.ProcessObjectivesAssessment_SubProcess);
            Assert.Equal("Updated Key Risk Factors", updatedAssessment.RisksAssessment_KeyRiskAndFactors);
            Assert.Equal("Medium", updatedAssessment.RisksAssessment_RiskLikelihood); // ID 2 = Medium
        }
    }
} 