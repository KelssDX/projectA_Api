using System;
using System.Collections.Generic;

namespace Affine.Engine.Model.Auditing.AuditUniverse
{
    /// <summary>
    /// Represents a node in the audit universe hierarchy.
    /// Levels: 1=Entity, 2=Division, 3=Process, 4=Sub-Process
    /// </summary>
    public class AuditUniverseNode
    {
        public int Id { get; set; }
        public string Name { get; set; }
        public string Code { get; set; }
        public int? ParentId { get; set; }
        public int Level { get; set; } = 1;
        public string LevelName { get; set; }
        public string Description { get; set; }
        public string RiskRating { get; set; } = "Medium";
        public DateTime? LastAuditDate { get; set; }
        public DateTime? NextAuditDate { get; set; }
        public int? AuditFrequencyMonths { get; set; } = 12;
        public string Owner { get; set; }
        public bool IsActive { get; set; } = true;
        public DateTime? CreatedAt { get; set; }
        public DateTime? UpdatedAt { get; set; }

        // Navigation properties (populated for tree views)
        public string ParentName { get; set; }
        public List<AuditUniverseNode> Children { get; set; } = new List<AuditUniverseNode>();
        public List<int> LinkedDepartmentIds { get; set; } = new List<int>();

        // Computed properties for UI
        public int ChildCount { get; set; }
        public int TotalDescendantCount { get; set; }
        public int FindingsCount { get; set; }
        public int OpenFindingsCount { get; set; }
        public double? CoveragePercentage { get; set; }
    }

    /// <summary>
    /// Represents a level definition in the audit universe hierarchy
    /// </summary>
    public class AuditUniverseLevel
    {
        public int Id { get; set; }
        public int Level { get; set; }
        public string Name { get; set; }
        public string Description { get; set; }
        public string Icon { get; set; }
        public int? SortOrder { get; set; }
        public bool IsActive { get; set; } = true;
    }

    /// <summary>
    /// Link between audit universe node and department
    /// </summary>
    public class AuditUniverseDepartmentLink
    {
        public int Id { get; set; }
        public int AuditUniverseId { get; set; }
        public int DepartmentId { get; set; }
        public DateTime? CreatedAt { get; set; }

        // Navigation
        public string DepartmentName { get; set; }
        public string AuditUniverseName { get; set; }
    }

    /// <summary>
    /// Flat response for hierarchy display with path information
    /// </summary>
    public class AuditUniverseFlatNode
    {
        public int Id { get; set; }
        public string Name { get; set; }
        public string Code { get; set; }
        public int? ParentId { get; set; }
        public int Level { get; set; }
        public string LevelName { get; set; }
        public string RiskRating { get; set; }
        public string Owner { get; set; }
        public DateTime? LastAuditDate { get; set; }
        public DateTime? NextAuditDate { get; set; }
        public bool IsActive { get; set; }

        // Path information
        public string FullPath { get; set; } // e.g., "Corporate > Finance > Treasury"
        public List<int> AncestorIds { get; set; } = new List<int>();
        public int Depth { get; set; }
        public bool HasChildren { get; set; }
    }

    /// <summary>
    /// Hierarchical response for full tree view
    /// </summary>
    public class AuditUniverseHierarchyResponse
    {
        public List<AuditUniverseNode> RootNodes { get; set; } = new List<AuditUniverseNode>();
        public int TotalNodes { get; set; }
        public int MaxDepth { get; set; }
        public List<AuditUniverseLevel> Levels { get; set; } = new List<AuditUniverseLevel>();
    }
}
