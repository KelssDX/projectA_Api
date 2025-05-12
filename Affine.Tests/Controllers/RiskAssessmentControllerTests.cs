using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Affine.Auditing.API.Controllers;
using Affine.Engine.Model.Auditing.Assessment;
using Affine.Engine.Repository.Auditing;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;
using Moq;
using Xunit;

namespace Affine.Tests.Controllers
{
    public class RiskAssessmentControllerTests
    {
        private readonly Mock<IRiskAssessmentRepository> _mockRepository;
        private readonly Mock<ILogger<RiskAssessmentController>> _mockLogger;
        private readonly RiskAssessmentController _controller;

        public RiskAssessmentControllerTests()
        {
            _mockRepository = new Mock<IRiskAssessmentRepository>();
            _mockLogger = new Mock<ILogger<RiskAssessmentController>>();
            _controller = new RiskAssessmentController(_mockRepository.Object, _mockLogger.Object);
        }

        [Fact]
        public async Task GetRiskAssessment_WhenValidId_ReturnsOkResult()
        {
            // Arrange
            int referenceId = 1;
            var riskAssessment = GetSampleRiskAssessment(referenceId);
            _mockRepository.Setup(repo => repo.GetRiskAssessmentAsync(referenceId))
                .ReturnsAsync(riskAssessment);

            // Act
            var result = await _controller.GetRiskAssessment(referenceId);

            // Assert
            var okResult = Assert.IsType<OkObjectResult>(result);
            var returnValue = Assert.IsType<RiskAssessmentViewModel>(okResult.Value);
            Assert.Equal(referenceId, returnValue.ReferenceId);
            Assert.Equal("Test Client", returnValue.Client);
            Assert.Equal(2, returnValue.RiskAssessments.Count);
        }

        [Fact]
        public async Task GetRiskAssessment_WhenInvalidId_ReturnsNotFound()
        {
            // Arrange
            int referenceId = 999;
            _mockRepository.Setup(repo => repo.GetRiskAssessmentAsync(referenceId))
                .ReturnsAsync((RiskAssessmentViewModel)null);

            // Act
            var result = await _controller.GetRiskAssessment(referenceId);

            // Assert
            Assert.IsType<NotFoundResult>(result);
        }

        [Fact]
        public async Task GetRiskLikelihoods_ReturnsOkResult()
        {
            // Arrange
            var likelihoods = new List<(int id, string description)>
            {
                (1, "Low"),
                (2, "Medium"),
                (3, "High")
            };
            
            _mockRepository.Setup(repo => repo.GetRiskLikelihoodsAsync())
                .ReturnsAsync(likelihoods);

            // Act
            var result = await _controller.GetRiskLikelihoods();

            // Assert
            var okResult = Assert.IsType<OkObjectResult>(result);
            var returnValue = Assert.IsAssignableFrom<IEnumerable<(int id, string description)>>(okResult.Value);
            Assert.Equal(3, returnValue.Count());
        }

        [Fact]
        public async Task GetImpacts_ReturnsOkResult()
        {
            // Arrange
            var impacts = new List<(int id, string description)>
            {
                (1, "Low"),
                (2, "Medium"),
                (3, "High")
            };
            
            _mockRepository.Setup(repo => repo.GetImpactsAsync())
                .ReturnsAsync(impacts);

            // Act
            var result = await _controller.GetImpacts();

            // Assert
            var okResult = Assert.IsType<OkObjectResult>(result);
            var returnValue = Assert.IsAssignableFrom<IEnumerable<(int id, string description)>>(okResult.Value);
            Assert.Equal(3, returnValue.Count());
        }

        [Fact]
        public async Task GetEvidence_ReturnsOkResult()
        {
            // Arrange
            var evidence = new List<(int id, string description)>
            {
                (1, "Low"),
                (2, "Medium"),
                (3, "High")
            };
            
            _mockRepository.Setup(repo => repo.GetEvidenceAsync())
                .ReturnsAsync(evidence);

            // Act
            var result = await _controller.GetEvidence();

            // Assert
            var okResult = Assert.IsType<OkObjectResult>(result);
            var returnValue = Assert.IsAssignableFrom<IEnumerable<(int id, string description)>>(okResult.Value);
            Assert.Equal(3, returnValue.Count());
        }

        [Fact]
        public async Task AddRiskAssessment_WhenValidRequest_ReturnsCreatedAtAction()
        {
            // Arrange
            var request = new RiskAssessmentPostRequest
            {
                Reference = new RiskAssessmentReference
                {
                    Client = "Test Client",
                    Assessor = "Test Assessor",
                    ApprovedBy = "Test Approver",
                    AssessmentStartDate = DateTime.Now.AddDays(-30),
                    AssessmentEndDate = DateTime.Now
                },
                Assessments = new List<RiskAssessmentCreateRequest>
                {
                    new RiskAssessmentCreateRequest
                    {
                        BusinessObjectives = "Test Business Objectives",
                        MainProcess = "Test Main Process",
                        SubProcess = "Test Sub Process",
                        KeyRiskAndFactors = "Test Key Risk Factors"
                    }
                }
            };

            int referenceId = 1;
            _mockRepository.Setup(repo => repo.AddRiskAssessmentReferenceAsync(It.IsAny<RiskAssessmentReference>()))
                .ReturnsAsync(referenceId);
            _mockRepository.Setup(repo => repo.AddRiskAssessmentAsync(
                    It.IsAny<List<RiskAssessmentCreateRequest>>(), 
                    It.IsAny<RiskAssessmentReference>(), 
                    referenceId))
                .ReturnsAsync(true);

            // Act
            var result = await _controller.AddRiskAssessment(request);

            // Assert
            var createdAtActionResult = Assert.IsType<CreatedAtActionResult>(result);
            Assert.Equal("GetRiskAssessment", createdAtActionResult.ActionName);
            Assert.Equal(referenceId, createdAtActionResult.RouteValues["id"]);
        }

        [Fact]
        public async Task AddRiskAssessment_WhenReferenceAddFails_ReturnsBadRequest()
        {
            // Arrange
            var request = new RiskAssessmentPostRequest
            {
                Reference = new RiskAssessmentReference
                {
                    Client = "Test Client"
                },
                Assessments = new List<RiskAssessmentCreateRequest>
                {
                    new RiskAssessmentCreateRequest
                    {
                        BusinessObjectives = "Test Business Objectives"
                    }
                }
            };

            _mockRepository.Setup(repo => repo.AddRiskAssessmentReferenceAsync(It.IsAny<RiskAssessmentReference>()))
                .ReturnsAsync(0);

            // Act
            var result = await _controller.AddRiskAssessment(request);

            // Assert
            var badRequestResult = Assert.IsType<BadRequestObjectResult>(result);
            Assert.Equal("Failed to add risk assessment reference", badRequestResult.Value);
        }

        [Fact]
        public async Task AddRiskAssessment_WhenAssessmentAddFails_ReturnsBadRequest()
        {
            // Arrange
            var request = new RiskAssessmentPostRequest
            {
                Reference = new RiskAssessmentReference
                {
                    Client = "Test Client"
                },
                Assessments = new List<RiskAssessmentCreateRequest>
                {
                    new RiskAssessmentCreateRequest
                    {
                        BusinessObjectives = "Test Business Objectives"
                    }
                }
            };

            int referenceId = 1;
            _mockRepository.Setup(repo => repo.AddRiskAssessmentReferenceAsync(It.IsAny<RiskAssessmentReference>()))
                .ReturnsAsync(referenceId);
            _mockRepository.Setup(repo => repo.AddRiskAssessmentAsync(
                    It.IsAny<List<RiskAssessmentCreateRequest>>(), 
                    It.IsAny<RiskAssessmentReference>(), 
                    referenceId))
                .ReturnsAsync(false);

            // Act
            var result = await _controller.AddRiskAssessment(request);

            // Assert
            var badRequestResult = Assert.IsType<BadRequestObjectResult>(result);
            Assert.Equal("Failed to add risk assessments", badRequestResult.Value);
        }

        [Fact]
        public async Task UpdateRiskAssessment_WhenValidRequest_ReturnsOkResult()
        {
            // Arrange
            int referenceId = 1;
            var updateRequests = new List<RiskAssessmentUpdateRequest>
            {
                new RiskAssessmentUpdateRequest
                {
                    RiskAssessmentRefId = 1,
                    BusinessObjectives = "Updated Business Objectives",
                    MainProcess = "Updated Main Process"
                }
            };

            _mockRepository.Setup(repo => repo.UpdateRiskAssessmentsAsync(updateRequests, referenceId))
                .ReturnsAsync(true);

            // Act
            var result = await _controller.UpdateRiskAssessment(referenceId, updateRequests);

            // Assert
            Assert.IsType<OkResult>(result);
        }

        [Fact]
        public async Task UpdateRiskAssessment_WhenUpdateFails_ReturnsBadRequest()
        {
            // Arrange
            int referenceId = 1;
            var updateRequests = new List<RiskAssessmentUpdateRequest>
            {
                new RiskAssessmentUpdateRequest
                {
                    RiskAssessmentRefId = 1,
                    BusinessObjectives = "Updated Business Objectives"
                }
            };

            _mockRepository.Setup(repo => repo.UpdateRiskAssessmentsAsync(updateRequests, referenceId))
                .ReturnsAsync(false);

            // Act
            var result = await _controller.UpdateRiskAssessment(referenceId, updateRequests);

            // Assert
            var badRequestResult = Assert.IsType<BadRequestObjectResult>(result);
            Assert.Equal("Failed to update risk assessments", badRequestResult.Value);
        }

        private RiskAssessmentViewModel GetSampleRiskAssessment(int referenceId)
        {
            return new RiskAssessmentViewModel
            {
                ReferenceId = referenceId,
                Client = "Test Client",
                Assessor = "Test Assessor",
                ApprovedBy = "Test Approver",
                AssessmentStartDate = DateTime.Now.AddDays(-30),
                AssessmentEndDate = DateTime.Now,
                RiskAssessments = new List<RiskAssessmentData>
                {
                    new RiskAssessmentData
                    {
                        RiskAssessment_RefID = 1,
                        ProcessObjectivesAssessment_BusinessObjectives = "Business Objectives 1",
                        ProcessObjectivesAssessment_MainProcess = "Main Process 1",
                        ProcessObjectivesAssessment_SubProcess = "Sub Process 1",
                        RisksAssessment_KeyRiskAndFactors = "Key Risk 1",
                        RisksAssessment_MitigatingControls = "Mitigating Controls 1",
                        RisksAssessment_RiskLikelihood = "Low",
                        RisksAssessment_RiskImpact = "Medium"
                    },
                    new RiskAssessmentData
                    {
                        RiskAssessment_RefID = 2,
                        ProcessObjectivesAssessment_BusinessObjectives = "Business Objectives 2",
                        ProcessObjectivesAssessment_MainProcess = "Main Process 2",
                        ProcessObjectivesAssessment_SubProcess = "Sub Process 2",
                        RisksAssessment_KeyRiskAndFactors = "Key Risk 2",
                        RisksAssessment_MitigatingControls = "Mitigating Controls 2",
                        RisksAssessment_RiskLikelihood = "Medium",
                        RisksAssessment_RiskImpact = "High"
                    }
                }
            };
        }
    }
}