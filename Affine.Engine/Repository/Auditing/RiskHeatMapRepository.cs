using Affine.Engine.Model.Auditing.HeatMap;
using Dapper;
using Npgsql;
using System;
using System.Collections.Generic;
using System.Data;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Affine.Engine.Repository.Auditing
{
    public class RiskHeatMapRepository: IRiskHeatMapRepository
    {

        private readonly string _connectionString;

        public RiskHeatMapRepository(string connectionString)
        {
            _connectionString = connectionString;
        }
        public async Task<RiskHeatmapResponse> GetRiskHeatmapAsync(int referenceId, int? departmentId = null)
{
    using IDbConnection dbConnection = new NpgsqlConnection(_connectionString);
    dbConnection.Open();

    try
    {
        // Query to aggregate risks by likelihood and impact
                var heatmapQuery = new StringBuilder();
                // Align with actual table names used by the RA schema (RA_RiskLikelihood/RA_RiskImpact)
                heatmapQuery.Append(@"SELECT rl.description AS Likelihood, ri.description AS Impact, COUNT(*) AS Count
                                     FROM RiskAssessment ra
                                     INNER JOIN RA_RiskLikelihood rl ON ra.RiskLikelihoodId = rl.Id
                                     INNER JOIN RA_RiskImpact ri ON ra.RiskImpactId = ri.Id
                                     WHERE ra.ReferenceId = @ReferenceId");
                if (departmentId.HasValue)
                {
                    heatmapQuery.Append(" AND ra.DepartmentId = @DepartmentId");
                }
                heatmapQuery.Append(" GROUP BY rl.Name, ri.Name");

                var heatmapData = await dbConnection.QueryAsync<HeatmapData>(heatmapQuery.ToString(), new { ReferenceId = referenceId, DepartmentId = departmentId });

        // Transform the data into a heatmap grid
        var grid = new Dictionary<string, Dictionary<string, int>>();

        foreach (var data in heatmapData)
        {
            if (!grid.ContainsKey(data.Impact))
                grid[data.Impact] = new Dictionary<string, int>();

            grid[data.Impact][data.Likelihood] = data.Count;
        }

        return new RiskHeatmapResponse
        {
            ReferenceId = referenceId,
            HeatmapGrid = grid
        };
    }
    catch
    {
        throw; // Re-throw for proper error handling
    }
}

    }
}
