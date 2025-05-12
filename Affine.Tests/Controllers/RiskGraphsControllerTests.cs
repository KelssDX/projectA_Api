using System;
using System.Collections.Generic;
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
    public class RiskGraphsControllerTests
    {
        private readonly Mock<IRiskHeatMapRepository> _mockRepository;
        private readonly Mock<ILogger<RiskGraphsController>> _mockLogger;
        private readonly RiskGraphsController _controller;

        public RiskGraphsControllerTests()
        {
            _mockRepository = new Mock<IRiskHeatMapRepository>();
            _mockLogger = new Mock<ILogger<RiskGraphsController>>();
            _controller = new RiskGraphsController(_mockRepository.Object, _mockLogger.Object);
        }

        [Fact]
        public async Task GetRiskGraph_WhenValidId_ReturnsOkResult()
        {
            // Arrange
            int referenceId = 1;
            var heatmap = new HeatMapResultDto
            {
                heatMap = new List<HeatMapDto>
                {
                    new HeatMapDto
                    {
                        likelihoodId = 1,
                        impactId = 1,
                        count = 5
                    },
                    new HeatMapDto
                    {
                        likelihoodId = 2,
                        impactId = 2,
                        count = 3
                    }
                },
                impactList = new List<HeatMapItemDto>
                {
                    new HeatMapItemDto { id = 1, description = "Low" },
                    new HeatMapItemDto { id = 2, description = "Medium" },
                    new HeatMapItemDto { id = 3, description = "High" }
                },
                likelihoodList = new List<HeatMapItemDto>
                {
                    new HeatMapItemDto { id = 1, description = "Low" },
                    new HeatMapItemDto { id = 2, description = "Medium" },
                    new HeatMapItemDto { id = 3, description = "High" }
                }
            };

            _mockRepository.Setup(repo => repo.GetHeatMapAsync(referenceId))
                .ReturnsAsync(heatmap);

            // Act
            var result = await _controller.GetRiskGraph(referenceId);

            // Assert
            var okResult = Assert.IsType<OkObjectResult>(result);
            var returnValue = Assert.IsType<HeatMapResultDto>(okResult.Value);
            Assert.Equal(2, returnValue.heatMap.Count);
            Assert.Equal(3, returnValue.impactList.Count);
            Assert.Equal(3, returnValue.likelihoodList.Count);
        }

        [Fact]
        public async Task GetRiskGraph_WhenInvalidId_ReturnsNotFound()
        {
            // Arrange
            int referenceId = 999;
            _mockRepository.Setup(repo => repo.GetHeatMapAsync(referenceId))
                .ReturnsAsync((HeatMapResultDto)null);

            // Act
            var result = await _controller.GetRiskGraph(referenceId);

            // Assert
            Assert.IsType<NotFoundResult>(result);
        }

        [Fact]
        public async Task GetRiskGraph_WhenRepositoryThrowsException_ReturnsBadRequest()
        {
            // Arrange
            int referenceId = 1;
            string errorMessage = "Database error";
            _mockRepository.Setup(repo => repo.GetHeatMapAsync(referenceId))
                .ThrowsAsync(new Exception(errorMessage));

            // Act
            var result = await _controller.GetRiskGraph(referenceId);

            // Assert
            var badRequestResult = Assert.IsType<BadRequestObjectResult>(result);
            Assert.Contains(errorMessage, badRequestResult.Value.ToString());
        }

        [Fact]
        public async Task GetRiskGraphData_WhenValidId_ReturnsOkResult()
        {
            // Arrange
            int referenceId = 1;
            var graphData = new List<RiskGraphDto>
            {
                new RiskGraphDto
                {
                    category = "Strategic",
                    count = 5
                },
                new RiskGraphDto
                {
                    category = "Operational",
                    count = 3
                }
            };

            _mockRepository.Setup(repo => repo.GetRiskGraphAsync(referenceId))
                .ReturnsAsync(graphData);

            // Act
            var result = await _controller.GetRiskGraphData(referenceId);

            // Assert
            var okResult = Assert.IsType<OkObjectResult>(result);
            var returnValue = Assert.IsAssignableFrom<IEnumerable<RiskGraphDto>>(okResult.Value);
            Assert.Equal(2, returnValue.Count);
        }

        [Fact]
        public async Task GetRiskGraphData_WhenInvalidId_ReturnsNotFound()
        {
            // Arrange
            int referenceId = 999;
            _mockRepository.Setup(repo => repo.GetRiskGraphAsync(referenceId))
                .ReturnsAsync((List<RiskGraphDto>)null);

            // Act
            var result = await _controller.GetRiskGraphData(referenceId);

            // Assert
            Assert.IsType<NotFoundResult>(result);
        }

        [Fact]
        public async Task GetRiskGraphData_WhenRepositoryThrowsException_ReturnsBadRequest()
        {
            // Arrange
            int referenceId = 1;
            string errorMessage = "Database error";
            _mockRepository.Setup(repo => repo.GetRiskGraphAsync(referenceId))
                .ThrowsAsync(new Exception(errorMessage));

            // Act
            var result = await _controller.GetRiskGraphData(referenceId);

            // Assert
            var badRequestResult = Assert.IsType<BadRequestObjectResult>(result);
            Assert.Contains(errorMessage, badRequestResult.Value.ToString());
        }
    }
} 