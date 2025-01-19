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
        public async Task<RiskHeatmapResponse> GetRiskHeatmapAsync(int referenceId)
{
    using IDbConnection dbConnection = new NpgsqlConnection(_connectionString);
    dbConnection.Open();

    try
    {
        // Query to aggregate risks by likelihood and impact
        string heatmapQuery = @"
            SELECT 
                rl.Name AS Likelihood,
                ri.Name AS Impact,
                COUNT(*) AS Count
            FROM RiskAssessment ra
            INNER JOIN RiskLikelihood rl ON ra.RiskLikelihoodId = rl.Id
            INNER JOIN RiskImpact ri ON ra.RiskImpactId = ri.Id
            WHERE ra.ReferenceId = @ReferenceId
            GROUP BY rl.Name, ri.Name";

        var heatmapData = await dbConnection.QueryAsync<HeatmapData>(heatmapQuery, new { ReferenceId = referenceId });

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
