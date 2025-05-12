using System;
using System.Collections.Generic;
using System.Net;
using System.Net.Http;
using System.Net.Http.Json;
using System.Threading.Tasks;
using Affine.Engine.Model.Auditing.Assessment;
using Affine.Tests.Helpers;
using Xunit;

namespace Affine.Tests.Integration
{
    public class RiskGraphsApiTests : IntegrationTestBase
    {
        public RiskGraphsApiTests(AffineApiFactory factory) : base(factory)
        {
        }

        [Fact]
        public async Task GetRiskGraph_ReturnsNotFound_WhenIdDoesNotExist()
        {
            // Arrange
            int nonExistentId = 9999;

            // Act
            var response = await Client.GetAsync($"/api/riskgraphs/{nonExistentId}");

            // Assert
            Assert.Equal(HttpStatusCode.NotFound, response.StatusCode);
        }

        [Fact]
        public async Task GetRiskGraphData_ReturnsNotFound_WhenIdDoesNotExist()
        {
            // Arrange
            int nonExistentId = 9999;

            // Act
            var response = await Client.GetAsync($"/api/riskgraphs/{nonExistentId}/data");

            // Assert
            Assert.Equal(HttpStatusCode.NotFound, response.StatusCode);
        }

        [Fact]
        public async Task CreateRiskAssessmentAndGetRiskGraph_Success()
        {
            // Arrange - Create Risk Assessment
            var createRequest = new RiskAssessmentPostRequest
            {
                Reference = new RiskAssessmentReference
                {
                    Client = "Graph Test Client",
                    Assessor = "Graph Test Assessor",
                    ApprovedBy = "Graph Test Approver",
                    AssessmentStartDate = DateTime.Now.AddDays(-30),
                    AssessmentEndDate = DateTime.Now
                },
                Assessments = new List<RiskAssessmentCreateRequest>
                {
                    new RiskAssessmentCreateRequest
                    {
                        BusinessObjectives = "Graph Test Business Objectives 1",
                        MainProcess = "Graph Test Main Process 1",
                        SubProcess = "Graph Test Sub Process 1",
                        KeyRiskAndFactors = "Graph Test Key Risk Factors 1",
                        MitigatingControls = "Graph Test Mitigating Controls 1",
                        Responsibility = "Graph Test Responsibility 1",
                        Authoriser = "Graph Test Authoriser 1",
                        AuditorsRecommendedActionPlan = "Graph Test Action Plan 1",
                        ResponsiblePerson = "Graph Test Person 1",
                        AgreedDate = DateTime.Now,
                        RiskLikelihoodId = 1, // Low
                        RiskImpactId = 1, // Low
                        KeySecondaryId = 1,
                        RiskCategoryId = 1, // First category
                        DataFrequencyId = 1,
                        FrequencyId = 1,
                        EvidenceId = 1,
                        OutcomeLikelihoodId = 1,
                        ImpactId = 1
                    },
                    new RiskAssessmentCreateRequest
                    {
                        BusinessObjectives = "Graph Test Business Objectives 2",
                        MainProcess = "Graph Test Main Process 2",
                        SubProcess = "Graph Test Sub Process 2",
                        KeyRiskAndFactors = "Graph Test Key Risk Factors 2",
                        MitigatingControls = "Graph Test Mitigating Controls 2",
                        Responsibility = "Graph Test Responsibility 2",
                        Authoriser = "Graph Test Authoriser 2",
                        AuditorsRecommendedActionPlan = "Graph Test Action Plan 2",
                        ResponsiblePerson = "Graph Test Person 2",
                        AgreedDate = DateTime.Now,
                        RiskLikelihoodId = 2, // Medium
                        RiskImpactId = 2, // Medium
                        KeySecondaryId = 1,
                        RiskCategoryId = 2, // Second category
                        DataFrequencyId = 1,
                        FrequencyId = 1,
                        EvidenceId = 1,
                        OutcomeLikelihoodId = 1,
                        ImpactId = 1
                    }
                }
            };

            var jsonContent = JsonContent.Create(createRequest);

            // Act - Create Risk Assessment
            var createResponse = await Client.PostAsync("/api/riskassessment", jsonContent);
            
            // Get the ID from the Location header
            var location = createResponse.Headers.Location.ToString();
            var referenceId = int.Parse(location.Substring(location.LastIndexOf('/') + 1));
            
            // Act - Get Heat Map
            var heatMapResponse = await Client.GetAsync($"/api/riskgraphs/{referenceId}");
            
            // Assert - Heat Map
            Assert.Equal(HttpStatusCode.OK, heatMapResponse.StatusCode);
            
            var heatMap = await heatMapResponse.Content.ReadFromJsonAsync<HeatMapResultDto>();
            Assert.NotNull(heatMap);
            Assert.NotEmpty(heatMap.heatMap);
            Assert.NotEmpty(heatMap.impactList);
            Assert.NotEmpty(heatMap.likelihoodList);
            
            // Verify heat map entries
            Assert.Contains(heatMap.heatMap, h => h.likelihoodId == 1 && h.impactId == 1);
            Assert.Contains(heatMap.heatMap, h => h.likelihoodId == 2 && h.impactId == 2);
            
            // Act - Get Risk Graph Data
            var graphDataResponse = await Client.GetAsync($"/api/riskgraphs/{referenceId}/data");
            
            // Assert - Risk Graph Data
            Assert.Equal(HttpStatusCode.OK, graphDataResponse.StatusCode);
            
            var graphData = await graphDataResponse.Content.ReadFromJsonAsync<List<RiskGraphDto>>();
            Assert.NotNull(graphData);
            Assert.NotEmpty(graphData);
            
            // Verify risk categories
            var categoryIds = new HashSet<string>(graphData.Select(g => g.category));
            Assert.Equal(2, categoryIds.Count);
        }
    }
} 