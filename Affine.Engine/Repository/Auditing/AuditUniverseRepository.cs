using Affine.Engine.Model.Auditing.AuditUniverse;
using Dapper;
using Npgsql;
using System;
using System.Collections.Generic;
using System.Data;
using System.Linq;
using System.Threading.Tasks;

namespace Affine.Engine.Repository.Auditing
{
    public class AuditUniverseRepository : IAuditUniverseRepository
    {
        private readonly string _connectionString;

        public AuditUniverseRepository(string connectionString)
        {
            _connectionString = connectionString ?? throw new ArgumentNullException(nameof(connectionString));
        }

        #region Hierarchy Operations

        public async Task<AuditUniverseHierarchyResponse> GetHierarchyAsync()
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();

                // Get all nodes
                var nodesQuery = @"
                    SELECT
                        au.id AS Id,
                        au.name AS Name,
                        au.code AS Code,
                        au.parent_id AS ParentId,
                        au.level AS Level,
                        au.level_name AS LevelName,
                        au.description AS Description,
                        au.risk_rating AS RiskRating,
                        au.last_audit_date AS LastAuditDate,
                        au.next_audit_date AS NextAuditDate,
                        au.audit_frequency_months AS AuditFrequencyMonths,
                        au.owner AS Owner,
                        au.is_active AS IsActive,
                        au.created_at AS CreatedAt,
                        au.updated_at AS UpdatedAt,
                        p.name AS ParentName,
                        (SELECT COUNT(*) FROM audit_universe c WHERE c.parent_id = au.id) AS ChildCount,
                        (SELECT COUNT(*) FROM audit_findings f WHERE f.audit_universe_id = au.id) AS FindingsCount,
                        (SELECT COUNT(*) FROM audit_findings f WHERE f.audit_universe_id = au.id
                         AND f.status_id IN (SELECT id FROM ra_finding_status WHERE is_closed = false)) AS OpenFindingsCount
                    FROM audit_universe au
                    LEFT JOIN audit_universe p ON au.parent_id = p.id
                    WHERE au.is_active = true
                    ORDER BY au.level, au.name";

                var allNodes = (await db.QueryAsync<AuditUniverseNode>(nodesQuery)).ToList();

                // Get levels
                var levels = await GetLevelsAsync();

                // Build hierarchy tree
                var nodeDict = allNodes.ToDictionary(n => n.Id);
                var rootNodes = new List<AuditUniverseNode>();

                foreach (var node in allNodes)
                {
                    if (node.ParentId.HasValue && nodeDict.ContainsKey(node.ParentId.Value))
                    {
                        nodeDict[node.ParentId.Value].Children.Add(node);
                    }
                    else
                    {
                        rootNodes.Add(node);
                    }
                }

                // Calculate total descendants
                foreach (var root in rootNodes)
                {
                    CalculateTotalDescendants(root);
                }

                return new AuditUniverseHierarchyResponse
                {
                    RootNodes = rootNodes,
                    TotalNodes = allNodes.Count,
                    MaxDepth = allNodes.Any() ? allNodes.Max(n => n.Level) : 0,
                    Levels = levels
                };
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in GetHierarchyAsync: {ex.Message}");
                throw;
            }
        }

        private void CalculateTotalDescendants(AuditUniverseNode node)
        {
            int total = node.Children.Count;
            foreach (var child in node.Children)
            {
                CalculateTotalDescendants(child);
                total += child.TotalDescendantCount;
            }
            node.TotalDescendantCount = total;
        }

        public async Task<List<AuditUniverseFlatNode>> GetFlatHierarchyAsync()
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();

                // Use recursive CTE to get full path
                var query = @"
                    WITH RECURSIVE hierarchy AS (
                        -- Base case: root nodes
                        SELECT
                            id, name, code, parent_id, level, level_name,
                            risk_rating, owner, last_audit_date, next_audit_date, is_active,
                            name::text AS full_path,
                            ARRAY[id] AS ancestor_ids,
                            1 AS depth
                        FROM audit_universe
                        WHERE parent_id IS NULL AND is_active = true

                        UNION ALL

                        -- Recursive case
                        SELECT
                            au.id, au.name, au.code, au.parent_id, au.level, au.level_name,
                            au.risk_rating, au.owner, au.last_audit_date, au.next_audit_date, au.is_active,
                            h.full_path || ' > ' || au.name,
                            h.ancestor_ids || au.id,
                            h.depth + 1
                        FROM audit_universe au
                        INNER JOIN hierarchy h ON au.parent_id = h.id
                        WHERE au.is_active = true
                    )
                    SELECT
                        h.id AS Id,
                        h.name AS Name,
                        h.code AS Code,
                        h.parent_id AS ParentId,
                        h.level AS Level,
                        h.level_name AS LevelName,
                        h.risk_rating AS RiskRating,
                        h.owner AS Owner,
                        h.last_audit_date AS LastAuditDate,
                        h.next_audit_date AS NextAuditDate,
                        h.is_active AS IsActive,
                        h.full_path AS FullPath,
                        h.depth AS Depth,
                        EXISTS(SELECT 1 FROM audit_universe c WHERE c.parent_id = h.id AND c.is_active = true) AS HasChildren
                    FROM hierarchy h
                    ORDER BY h.full_path";

                var result = await db.QueryAsync<AuditUniverseFlatNode>(query);
                return result.ToList();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in GetFlatHierarchyAsync: {ex.Message}");
                throw;
            }
        }

        #endregion

        #region Node CRUD Operations

        public async Task<AuditUniverseNode> GetNodeAsync(int id)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();

                var query = @"
                    SELECT
                        au.id AS Id,
                        au.name AS Name,
                        au.code AS Code,
                        au.parent_id AS ParentId,
                        au.level AS Level,
                        au.level_name AS LevelName,
                        au.description AS Description,
                        au.risk_rating AS RiskRating,
                        au.last_audit_date AS LastAuditDate,
                        au.next_audit_date AS NextAuditDate,
                        au.audit_frequency_months AS AuditFrequencyMonths,
                        au.owner AS Owner,
                        au.is_active AS IsActive,
                        au.created_at AS CreatedAt,
                        au.updated_at AS UpdatedAt,
                        p.name AS ParentName
                    FROM audit_universe au
                    LEFT JOIN audit_universe p ON au.parent_id = p.id
                    WHERE au.id = @Id";

                var node = await db.QueryFirstOrDefaultAsync<AuditUniverseNode>(query, new { Id = id });

                if (node != null)
                {
                    // Get linked department IDs
                    var deptQuery = @"SELECT department_id FROM audit_universe_department_link WHERE audit_universe_id = @Id";
                    var deptIds = await db.QueryAsync<int>(deptQuery, new { Id = id });
                    node.LinkedDepartmentIds = deptIds.ToList();
                }

                return node;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in GetNodeAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<AuditUniverseNode> GetNodeWithChildrenAsync(int id)
        {
            try
            {
                var node = await GetNodeAsync(id);
                if (node == null) return null;

                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();

                var childrenQuery = @"
                    SELECT
                        id AS Id, name AS Name, code AS Code, parent_id AS ParentId,
                        level AS Level, level_name AS LevelName, description AS Description,
                        risk_rating AS RiskRating, owner AS Owner, is_active AS IsActive,
                        (SELECT COUNT(*) FROM audit_universe c WHERE c.parent_id = au.id) AS ChildCount
                    FROM audit_universe au
                    WHERE parent_id = @ParentId AND is_active = true
                    ORDER BY name";

                var children = await db.QueryAsync<AuditUniverseNode>(childrenQuery, new { ParentId = id });
                node.Children = children.ToList();

                return node;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in GetNodeWithChildrenAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<AuditUniverseNode> CreateNodeAsync(CreateAuditUniverseNodeRequest request)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();

                // Determine level based on parent
                int level = 1;
                string levelName = "Entity";
                if (request.ParentId.HasValue)
                {
                    var parent = await GetNodeAsync(request.ParentId.Value);
                    if (parent != null)
                    {
                        level = parent.Level + 1;
                        var levels = await GetLevelsAsync();
                        levelName = levels.FirstOrDefault(l => l.Level == level)?.Name ?? $"Level {level}";
                    }
                }

                var insertQuery = @"
                    INSERT INTO audit_universe
                        (name, code, parent_id, level, level_name, description, risk_rating,
                         last_audit_date, next_audit_date, audit_frequency_months, owner, is_active)
                    VALUES
                        (@Name, @Code, @ParentId, @Level, @LevelName, @Description, @RiskRating,
                         @LastAuditDate, @NextAuditDate, @AuditFrequencyMonths, @Owner, true)
                    RETURNING id";

                var newId = await db.ExecuteScalarAsync<int>(insertQuery, new
                {
                    request.Name,
                    request.Code,
                    request.ParentId,
                    Level = level,
                    LevelName = request.LevelName ?? levelName,
                    request.Description,
                    RiskRating = request.RiskRating ?? "Medium",
                    request.LastAuditDate,
                    request.NextAuditDate,
                    AuditFrequencyMonths = request.AuditFrequencyMonths ?? 12,
                    request.Owner
                });

                // Link departments if provided
                if (request.DepartmentIds?.Any() == true)
                {
                    await BulkLinkDepartmentsAsync(newId, request.DepartmentIds);
                }

                return await GetNodeAsync(newId);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in CreateNodeAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<AuditUniverseNode> UpdateNodeAsync(UpdateAuditUniverseNodeRequest request)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();

                var updateQuery = @"
                    UPDATE audit_universe SET
                        name = @Name,
                        code = @Code,
                        parent_id = @ParentId,
                        level = @Level,
                        level_name = @LevelName,
                        description = @Description,
                        risk_rating = @RiskRating,
                        last_audit_date = @LastAuditDate,
                        next_audit_date = @NextAuditDate,
                        audit_frequency_months = @AuditFrequencyMonths,
                        owner = @Owner,
                        is_active = @IsActive,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = @Id";

                await db.ExecuteAsync(updateQuery, request);

                return await GetNodeAsync(request.Id);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in UpdateNodeAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<bool> DeleteNodeAsync(int id)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();

                // Soft delete - set is_active to false
                // Children will be reparented to the deleted node's parent
                var node = await GetNodeAsync(id);
                if (node == null) return false;

                using var transaction = db.BeginTransaction();
                try
                {
                    // Reparent children
                    var reparentQuery = @"
                        UPDATE audit_universe
                        SET parent_id = @NewParentId, updated_at = CURRENT_TIMESTAMP
                        WHERE parent_id = @Id";
                    await db.ExecuteAsync(reparentQuery, new { NewParentId = node.ParentId, Id = id }, transaction);

                    // Soft delete the node
                    var deleteQuery = @"
                        UPDATE audit_universe
                        SET is_active = false, updated_at = CURRENT_TIMESTAMP
                        WHERE id = @Id";
                    await db.ExecuteAsync(deleteQuery, new { Id = id }, transaction);

                    transaction.Commit();
                    return true;
                }
                catch
                {
                    transaction.Rollback();
                    throw;
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in DeleteNodeAsync: {ex.Message}");
                throw;
            }
        }

        #endregion

        #region Department Linking

        public async Task<bool> LinkDepartmentAsync(int auditUniverseId, int departmentId)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();

                var query = @"
                    INSERT INTO audit_universe_department_link (audit_universe_id, department_id)
                    VALUES (@AuditUniverseId, @DepartmentId)
                    ON CONFLICT (audit_universe_id, department_id) DO NOTHING";

                await db.ExecuteAsync(query, new { AuditUniverseId = auditUniverseId, DepartmentId = departmentId });
                return true;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in LinkDepartmentAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<bool> UnlinkDepartmentAsync(int auditUniverseId, int departmentId)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();

                var query = @"
                    DELETE FROM audit_universe_department_link
                    WHERE audit_universe_id = @AuditUniverseId AND department_id = @DepartmentId";

                await db.ExecuteAsync(query, new { AuditUniverseId = auditUniverseId, DepartmentId = departmentId });
                return true;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in UnlinkDepartmentAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<bool> BulkLinkDepartmentsAsync(int auditUniverseId, List<int> departmentIds)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();

                // Remove existing links
                await db.ExecuteAsync(
                    "DELETE FROM audit_universe_department_link WHERE audit_universe_id = @Id",
                    new { Id = auditUniverseId });

                // Add new links
                foreach (var deptId in departmentIds)
                {
                    await LinkDepartmentAsync(auditUniverseId, deptId);
                }

                return true;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in BulkLinkDepartmentsAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<List<AuditUniverseDepartmentLink>> GetLinkedDepartmentsAsync(int auditUniverseId)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();

                var query = @"
                    SELECT
                        l.id AS Id,
                        l.audit_universe_id AS AuditUniverseId,
                        l.department_id AS DepartmentId,
                        l.created_at AS CreatedAt,
                        d.name AS DepartmentName,
                        au.name AS AuditUniverseName
                    FROM audit_universe_department_link l
                    INNER JOIN departments d ON l.department_id = d.id
                    INNER JOIN audit_universe au ON l.audit_universe_id = au.id
                    WHERE l.audit_universe_id = @AuditUniverseId";

                var result = await db.QueryAsync<AuditUniverseDepartmentLink>(query, new { AuditUniverseId = auditUniverseId });
                return result.ToList();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in GetLinkedDepartmentsAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<List<AuditUniverseNode>> GetNodesByDepartmentAsync(int departmentId)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();

                var query = @"
                    SELECT
                        au.id AS Id, au.name AS Name, au.code AS Code, au.parent_id AS ParentId,
                        au.level AS Level, au.level_name AS LevelName, au.risk_rating AS RiskRating,
                        au.owner AS Owner
                    FROM audit_universe au
                    INNER JOIN audit_universe_department_link l ON au.id = l.audit_universe_id
                    WHERE l.department_id = @DepartmentId AND au.is_active = true
                    ORDER BY au.level, au.name";

                var result = await db.QueryAsync<AuditUniverseNode>(query, new { DepartmentId = departmentId });
                return result.ToList();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in GetNodesByDepartmentAsync: {ex.Message}");
                throw;
            }
        }

        #endregion

        #region Levels

        public async Task<List<AuditUniverseLevel>> GetLevelsAsync()
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();

                var query = @"
                    SELECT
                        id AS Id, level AS Level, name AS Name, description AS Description,
                        icon AS Icon, sort_order AS SortOrder, is_active AS IsActive
                    FROM ra_audit_universe_levels
                    WHERE is_active = true
                    ORDER BY level";

                var result = await db.QueryAsync<AuditUniverseLevel>(query);
                return result.ToList();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in GetLevelsAsync: {ex.Message}");
                throw;
            }
        }

        #endregion

        #region Search and Filter

        public async Task<List<AuditUniverseNode>> SearchNodesAsync(string searchText)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();

                var query = @"
                    SELECT
                        id AS Id, name AS Name, code AS Code, parent_id AS ParentId,
                        level AS Level, level_name AS LevelName, description AS Description,
                        risk_rating AS RiskRating, owner AS Owner, is_active AS IsActive
                    FROM audit_universe
                    WHERE is_active = true
                      AND (LOWER(name) LIKE LOWER(@Search)
                           OR LOWER(code) LIKE LOWER(@Search)
                           OR LOWER(description) LIKE LOWER(@Search))
                    ORDER BY level, name
                    LIMIT 50";

                var result = await db.QueryAsync<AuditUniverseNode>(query, new { Search = $"%{searchText}%" });
                return result.ToList();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in SearchNodesAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<List<AuditUniverseNode>> GetNodesByLevelAsync(int level)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();

                var query = @"
                    SELECT
                        id AS Id, name AS Name, code AS Code, parent_id AS ParentId,
                        level AS Level, level_name AS LevelName, risk_rating AS RiskRating,
                        owner AS Owner, is_active AS IsActive
                    FROM audit_universe
                    WHERE level = @Level AND is_active = true
                    ORDER BY name";

                var result = await db.QueryAsync<AuditUniverseNode>(query, new { Level = level });
                return result.ToList();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in GetNodesByLevelAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<List<AuditUniverseNode>> GetNodesByRiskRatingAsync(string riskRating)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();

                var query = @"
                    SELECT
                        id AS Id, name AS Name, code AS Code, parent_id AS ParentId,
                        level AS Level, level_name AS LevelName, risk_rating AS RiskRating,
                        owner AS Owner, is_active AS IsActive
                    FROM audit_universe
                    WHERE risk_rating = @RiskRating AND is_active = true
                    ORDER BY level, name";

                var result = await db.QueryAsync<AuditUniverseNode>(query, new { RiskRating = riskRating });
                return result.ToList();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in GetNodesByRiskRatingAsync: {ex.Message}");
                throw;
            }
        }

        #endregion
    }
}
