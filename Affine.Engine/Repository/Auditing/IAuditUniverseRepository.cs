using Affine.Engine.Model.Auditing.AuditUniverse;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace Affine.Engine.Repository.Auditing
{
    public interface IAuditUniverseRepository
    {
        // Audit Universe Node Operations
        Task<AuditUniverseHierarchyResponse> GetHierarchyAsync();
        Task<List<AuditUniverseFlatNode>> GetFlatHierarchyAsync();
        Task<AuditUniverseNode> GetNodeAsync(int id);
        Task<AuditUniverseNode> GetNodeWithChildrenAsync(int id);
        Task<AuditUniverseNode> CreateNodeAsync(CreateAuditUniverseNodeRequest request);
        Task<AuditUniverseNode> UpdateNodeAsync(UpdateAuditUniverseNodeRequest request);
        Task<bool> DeleteNodeAsync(int id);

        // Department Linking
        Task<bool> LinkDepartmentAsync(int auditUniverseId, int departmentId);
        Task<bool> UnlinkDepartmentAsync(int auditUniverseId, int departmentId);
        Task<bool> BulkLinkDepartmentsAsync(int auditUniverseId, List<int> departmentIds);
        Task<List<AuditUniverseDepartmentLink>> GetLinkedDepartmentsAsync(int auditUniverseId);
        Task<List<AuditUniverseNode>> GetNodesByDepartmentAsync(int departmentId);

        // Level Definitions
        Task<List<AuditUniverseLevel>> GetLevelsAsync();

        // Search and Filter
        Task<List<AuditUniverseNode>> SearchNodesAsync(string searchText);
        Task<List<AuditUniverseNode>> GetNodesByLevelAsync(int level);
        Task<List<AuditUniverseNode>> GetNodesByRiskRatingAsync(string riskRating);
    }
}
