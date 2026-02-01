using Microsoft.AspNetCore.Mvc;
using Affine.Engine.Repository.Auditing;
using Affine.Engine.Model.Auditing.AuditUniverse;

namespace Affine.Auditing.API.Controllers
{
    [ApiController]
    [Route("api/v1/[controller]")]
    public class AuditUniverseController : ControllerBase
    {
        private readonly IAuditUniverseRepository _auditUniverseRepository;

        public AuditUniverseController(IAuditUniverseRepository auditUniverseRepository)
        {
            _auditUniverseRepository = auditUniverseRepository;
        }

        #region Hierarchy Operations

        /// <summary>
        /// Get the full audit universe hierarchy as a tree structure
        /// </summary>
        [HttpGet]
        [Route("GetHierarchy")]
        public async Task<IActionResult> GetHierarchy()
        {
            try
            {
                var hierarchy = await _auditUniverseRepository.GetHierarchyAsync();
                return Ok(hierarchy);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        /// <summary>
        /// Get the audit universe as a flat list with path information
        /// </summary>
        [HttpGet]
        [Route("GetFlatHierarchy")]
        public async Task<IActionResult> GetFlatHierarchy()
        {
            try
            {
                var nodes = await _auditUniverseRepository.GetFlatHierarchyAsync();
                return Ok(nodes);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        #endregion

        #region Node CRUD

        /// <summary>
        /// Get a single audit universe node by ID
        /// </summary>
        [HttpGet]
        [Route("GetNode/{id}")]
        public async Task<IActionResult> GetNode(int id)
        {
            try
            {
                var node = await _auditUniverseRepository.GetNodeAsync(id);
                if (node == null)
                {
                    return NotFound($"Node with ID {id} not found");
                }
                return Ok(node);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        /// <summary>
        /// Get a node with its immediate children
        /// </summary>
        [HttpGet]
        [Route("GetNodeWithChildren/{id}")]
        public async Task<IActionResult> GetNodeWithChildren(int id)
        {
            try
            {
                var node = await _auditUniverseRepository.GetNodeWithChildrenAsync(id);
                if (node == null)
                {
                    return NotFound($"Node with ID {id} not found");
                }
                return Ok(node);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        /// <summary>
        /// Create a new audit universe node
        /// </summary>
        [HttpPost]
        [Route("CreateNode")]
        public async Task<IActionResult> CreateNode([FromBody] CreateAuditUniverseNodeRequest request)
        {
            if (string.IsNullOrEmpty(request.Name))
            {
                return BadRequest("Node name is required");
            }
            if (string.IsNullOrEmpty(request.Code))
            {
                return BadRequest("Node code is required");
            }

            try
            {
                var node = await _auditUniverseRepository.CreateNodeAsync(request);
                return CreatedAtAction(nameof(GetNode), new { id = node.Id }, node);
            }
            catch (Exception ex)
            {
                if (ex.Message.Contains("duplicate") || ex.Message.Contains("unique"))
                {
                    return Conflict($"A node with code '{request.Code}' already exists");
                }
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        /// <summary>
        /// Update an existing audit universe node
        /// </summary>
        [HttpPut]
        [Route("UpdateNode/{id}")]
        public async Task<IActionResult> UpdateNode(int id, [FromBody] UpdateAuditUniverseNodeRequest request)
        {
            if (id != request.Id)
            {
                return BadRequest("ID mismatch");
            }

            try
            {
                var node = await _auditUniverseRepository.UpdateNodeAsync(request);
                if (node == null)
                {
                    return NotFound($"Node with ID {id} not found");
                }
                return Ok(node);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        /// <summary>
        /// Delete an audit universe node (soft delete, children are reparented)
        /// </summary>
        [HttpDelete]
        [Route("DeleteNode/{id}")]
        public async Task<IActionResult> DeleteNode(int id)
        {
            try
            {
                var result = await _auditUniverseRepository.DeleteNodeAsync(id);
                if (!result)
                {
                    return NotFound($"Node with ID {id} not found");
                }
                return Ok(new { message = "Node deleted successfully", id });
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        #endregion

        #region Department Linking

        /// <summary>
        /// Link a department to an audit universe node
        /// </summary>
        [HttpPost]
        [Route("LinkDepartment")]
        public async Task<IActionResult> LinkDepartment([FromBody] LinkDepartmentRequest request)
        {
            try
            {
                await _auditUniverseRepository.LinkDepartmentAsync(request.AuditUniverseId, request.DepartmentId);
                return Ok(new { message = "Department linked successfully" });
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        /// <summary>
        /// Unlink a department from an audit universe node
        /// </summary>
        [HttpDelete]
        [Route("UnlinkDepartment")]
        public async Task<IActionResult> UnlinkDepartment([FromQuery] int auditUniverseId, [FromQuery] int departmentId)
        {
            try
            {
                await _auditUniverseRepository.UnlinkDepartmentAsync(auditUniverseId, departmentId);
                return Ok(new { message = "Department unlinked successfully" });
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        /// <summary>
        /// Bulk link multiple departments to a node
        /// </summary>
        [HttpPost]
        [Route("BulkLinkDepartments")]
        public async Task<IActionResult> BulkLinkDepartments([FromBody] BulkLinkDepartmentsRequest request)
        {
            try
            {
                await _auditUniverseRepository.BulkLinkDepartmentsAsync(request.AuditUniverseId, request.DepartmentIds);
                return Ok(new { message = "Departments linked successfully" });
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        /// <summary>
        /// Get all departments linked to a node
        /// </summary>
        [HttpGet]
        [Route("GetLinkedDepartments/{nodeId}")]
        public async Task<IActionResult> GetLinkedDepartments(int nodeId)
        {
            try
            {
                var links = await _auditUniverseRepository.GetLinkedDepartmentsAsync(nodeId);
                return Ok(links);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        /// <summary>
        /// Get all audit universe nodes linked to a department
        /// </summary>
        [HttpGet]
        [Route("GetNodesByDepartment/{departmentId}")]
        public async Task<IActionResult> GetNodesByDepartment(int departmentId)
        {
            try
            {
                var nodes = await _auditUniverseRepository.GetNodesByDepartmentAsync(departmentId);
                return Ok(nodes);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        #endregion

        #region Lookups and Search

        /// <summary>
        /// Get all level definitions
        /// </summary>
        [HttpGet]
        [Route("GetLevels")]
        public async Task<IActionResult> GetLevels()
        {
            try
            {
                var levels = await _auditUniverseRepository.GetLevelsAsync();
                return Ok(levels);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        /// <summary>
        /// Search nodes by name, code, or description
        /// </summary>
        [HttpGet]
        [Route("Search")]
        public async Task<IActionResult> Search([FromQuery] string query)
        {
            if (string.IsNullOrWhiteSpace(query))
            {
                return BadRequest("Search query is required");
            }

            try
            {
                var nodes = await _auditUniverseRepository.SearchNodesAsync(query);
                return Ok(nodes);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        /// <summary>
        /// Get all nodes at a specific level
        /// </summary>
        [HttpGet]
        [Route("GetNodesByLevel/{level}")]
        public async Task<IActionResult> GetNodesByLevel(int level)
        {
            try
            {
                var nodes = await _auditUniverseRepository.GetNodesByLevelAsync(level);
                return Ok(nodes);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        /// <summary>
        /// Get all nodes with a specific risk rating
        /// </summary>
        [HttpGet]
        [Route("GetNodesByRiskRating")]
        public async Task<IActionResult> GetNodesByRiskRating([FromQuery] string riskRating)
        {
            try
            {
                var nodes = await _auditUniverseRepository.GetNodesByRiskRatingAsync(riskRating);
                return Ok(nodes);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        #endregion
    }
}
