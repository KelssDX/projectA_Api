using System;
using System.Collections.Generic;
using System.Net;
using System.Net.Http;
using System.Net.Http.Json;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;
using Affine.Engine.Model.Auditing.Assessment;
using Affine.Tests.Helpers;
using Microsoft.AspNetCore.Mvc.Testing;
using Xunit;

namespace Affine.Tests.Integration
{
    public class RiskAssessmentApiTests : IntegrationTestBase
    {
        public RiskAssessmentApiTests(AffineApiFactory factory) : base(factory)
        {
        }

        [Fact]
        public async Task GetRiskAssessment_ReturnsNotFound_WhenIdDoesNotExist()
        {
            // Arrange
            int nonExistentId = 9999;

            // Act
            var response = await Client.GetAsync($"/api/riskassessment/{nonExistentId}");

            // Assert
            Assert.Equal(HttpStatusCode.NotFound, response.StatusCode);
        }

        [Fact]
        public async Task CreateAndGetRiskAssessment_Success()
        {
            // Arrange
            var request = new RiskAssessmentPostRequest
            {
                Reference = new RiskAssessmentReference
                {
                    Client = "Integration Test Client",
                    Assessor = "Integration Test Assessor",
                    ApprovedBy = "Integration Test Approver",
                    AssessmentStartDate = DateTime.Now.AddDays(-30),
                    AssessmentEndDate = DateTime.Now
                },
                Assessments = new List<RiskAssessmentCreateRequest>
                {
                    new RiskAssessmentCreateRequest
                    {
                        BusinessObjectives = "Integration Test Business Objectives",
                        MainProcess = "Integration Test Main Process",
                        SubProcess = "Integration Test Sub Process",
                        KeyRiskAndFactors = "Integration Test Key Risk Factors",
                        MitigatingControls = "Integration Test Mitigating Controls",
                        Responsibility = "Integration Test Responsibility",
                        Authoriser = "Integration Test Authoriser",
                        AuditorsRecommendedActionPlan = "Integration Test Action Plan",
                        ResponsiblePerson = "Integration Test Person",
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
                }
            };

            var jsonContent = JsonContent.Create(request);

            // Act - Create
            var createResponse = await Client.PostAsync("/api/riskassessment", jsonContent);

            // Assert - Create
            Assert.Equal(HttpStatusCode.Created, createResponse.StatusCode);
            
            // Get the ID from the Location header
            var location = createResponse.Headers.Location.ToString();
            var id = int.Parse(location.Substring(location.LastIndexOf('/') + 1));
            
            // Act - Get
            var getResponse = await Client.GetAsync($"/api/riskassessment/{id}");
            
            // Assert - Get
            Assert.Equal(HttpStatusCode.OK, getResponse.StatusCode);
            
            var assessment = await getResponse.Content.ReadFromJsonAsync<RiskAssessmentViewModel>();
            Assert.NotNull(assessment);
            Assert.Equal("Integration Test Client", assessment.Client);
            Assert.Equal("Integration Test Assessor", assessment.Assessor);
            Assert.Single(assessment.RiskAssessments);
            Assert.Equal("Integration Test Business Objectives", 
                assessment.RiskAssessments[0].ProcessObjectivesAssessment_BusinessObjectives);
        }

        [Fact]
        public async Task GetRiskLikelihoods_ReturnsData()
        {
            // Act
            var response = await Client.GetAsync("/api/riskassessment/likelihoods");
            
            // Assert
            Assert.Equal(HttpStatusCode.OK, response.StatusCode);
            
            var likelihoods = await response.Content.ReadFromJsonAsync<List<dynamic>>();
            Assert.NotNull(likelihoods);
            Assert.NotEmpty(likelihoods);
        }

        [Fact]
        public async Task GetImpacts_ReturnsData()
        {
            // Act
            var response = await Client.GetAsync("/api/riskassessment/impacts");
            
            // Assert
            Assert.Equal(HttpStatusCode.OK, response.StatusCode);
            
            var impacts = await response.Content.ReadFromJsonAsync<List<dynamic>>();
            Assert.NotNull(impacts);
            Assert.NotEmpty(impacts);
        }

        [Fact]
        public async Task GetEvidence_ReturnsData()
        {
            // Act
            var response = await Client.GetAsync("/api/riskassessment/evidence");
            
            // Assert
            Assert.Equal(HttpStatusCode.OK, response.StatusCode);
            
            var evidence = await response.Content.ReadFromJsonAsync<List<dynamic>>();
            Assert.NotNull(evidence);
            Assert.NotEmpty(evidence);
        }

        [Fact]
        public async Task CreateUpdateAndGetRiskAssessment_Success()
        {
            // Arrange - Create
            var createRequest = new RiskAssessmentPostRequest
            {
                Reference = new RiskAssessmentReference
                {
                    Client = "Update Test Client",
                    Assessor = "Update Test Assessor",
                    ApprovedBy = "Update Test Approver",
                    AssessmentStartDate = DateTime.Now.AddDays(-30),
                    AssessmentEndDate = DateTime.Now
                },
                Assessments = new List<RiskAssessmentCreateRequest>
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
                }
            };

            var createJsonContent = JsonContent.Create(createRequest);

            // Act - Create
            var createResponse = await Client.PostAsync("/api/riskassessment", createJsonContent);
            
            // Get the ID from the Location header
            var location = createResponse.Headers.Location.ToString();
            var referenceId = int.Parse(location.Substring(location.LastIndexOf('/') + 1));
            
            // Get the assessment to retrieve assessment ref ID
            var getResponse = await Client.GetAsync($"/api/riskassessment/{referenceId}");
            var assessment = await getResponse.Content.ReadFromJsonAsync<RiskAssessmentViewModel>();
            var assessmentRefId = assessment.RiskAssessments[0].RiskAssessment_RefID;
            
            // Arrange - Update
            var updateRequest = new List<RiskAssessmentUpdateRequest>
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
            
            var updateJsonContent = JsonContent.Create(updateRequest);
            
            // Act - Update
            var updateResponse = await Client.PutAsync($"/api/riskassessment/{referenceId}", updateJsonContent);
            
            // Assert - Update
            Assert.Equal(HttpStatusCode.OK, updateResponse.StatusCode);
            
            // Act - Get Updated
            var getUpdatedResponse = await Client.GetAsync($"/api/riskassessment/{referenceId}");
            var updatedAssessment = await getUpdatedResponse.Content.ReadFromJsonAsync<RiskAssessmentViewModel>();
            
            // Assert - Get Updated
            Assert.Equal("Updated Business Objectives", 
                updatedAssessment.RiskAssessments[0].ProcessObjectivesAssessment_BusinessObjectives);
            Assert.Equal("Updated Main Process", 
                updatedAssessment.RiskAssessments[0].ProcessObjectivesAssessment_MainProcess);
            Assert.Equal("Updated Key Risk Factors", 
                updatedAssessment.RiskAssessments[0].RisksAssessment_KeyRiskAndFactors);
        }
    }
}