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
                // Use correct schema and column names (snake_case as per database)
                heatmapQuery.Append(@"SELECT rl.description AS Likelihood, ri.description AS Impact, COUNT(*) AS Count
                                     FROM ""Risk_Assess_Framework"".riskassessment ra
                                     INNER JOIN public.ra_risklikelihood rl ON ra.risklikelihoodid = rl.id
                                     INNER JOIN ""Risk_Assess_Framework"".ra_riskimpact ri ON ra.riskimpactid = ri.id
                                     WHERE ra.reference_id = @ReferenceId");
                if (departmentId.HasValue)
                {
                    heatmapQuery.Append(" AND ra.department_id = @DepartmentId");
                }
                heatmapQuery.Append(" GROUP BY rl.description, ri.description");

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

        public async Task<AnalyticalReportResponse> GetAnalyticalReportAsync(int referenceId)
        {
            using IDbConnection dbConnection = new NpgsqlConnection(_connectionString);
            dbConnection.Open();

            try
            {
                System.Console.WriteLine($"DEBUG: Querying Risks for RefId: {referenceId} on DB: {dbConnection.Database}");
                var sql = @"
                    SELECT 
                        ra.riskassessment_refid as ""RiskId"",
                        ra.keyriskandfactors as ""Title"",
                        rc.description as ""Category"",
                        ril.description as ""InherentLikelihood"",
                        rii.description as ""InherentImpact"",
                        rol.description as ""ResidualLikelihood"",
                        roi.description as ""ResidualImpact"",
                        ra.mitigatingcontrols as ""Controls""
                    FROM ""Risk_Assess_Framework"".riskassessment ra
                    LEFT JOIN public.ra_risklikelihood ril ON ra.risklikelihoodid = ril.id
                    LEFT JOIN ""Risk_Assess_Framework"".ra_riskimpact rii ON ra.riskimpactid = rii.id
                    LEFT JOIN ""Risk_Assess_Framework"".ra_outcomelikelihood rol ON ra.outcomelikelihoodid = rol.id
                    LEFT JOIN ""Risk_Assess_Framework"".ra_impact roi ON ra.impactid = roi.id
                    LEFT JOIN ""Risk_Assess_Framework"".ra_riskcategory rc ON ra.riskcategoryid = rc.id
                    WHERE ra.reference_id = @ReferenceId";

                var queryResult = await dbConnection.QueryAsync(sql, new { ReferenceId = referenceId });
                var risks = queryResult.Select(x => (IDictionary<string, object>)x).ToList();
                Console.WriteLine($"DEBUG: [RiskHeatMapRepository] Risks Found for RefId {referenceId}: {risks.Count}");

                var response = new AnalyticalReportResponse { ReferenceId = referenceId };
                
                int totalRisks = 0;
                int withControls = 0;
                var inherentCounts = new Dictionary<string, int> { {"Critical",0}, {"High",0}, {"Medium",0}, {"Low",0}, {"Very Low",0}, {"Unknown",0} };
                var residualCounts = new Dictionary<string, int> { {"Critical",0}, {"High",0}, {"Medium",0}, {"Low",0}, {"Very Low",0}, {"Unknown",0} };
                var categories = new Dictionary<string, (int Count, int TotalScore)>();
                var topRisks = new List<TopRiskItem>();
                
                (int Score, string Level) CalculateRisk(string likelihood, string impact)
                {
                    Console.WriteLine($"DEBUG: [RiskHeatMapRepository] CalculateRisk input: L='{likelihood}', I='{impact}'");
                if (string.IsNullOrWhiteSpace(likelihood) || string.IsNullOrWhiteSpace(impact)) 
                {
                    Console.WriteLine("DEBUG: [RiskHeatMapRepository] CalculateRisk: Null/Empty input, returning (1, 'Very Low')");
                    return (1, "Very Low");
                }

                try
                {
                    var l_norm = likelihood.Trim().ToLowerInvariant();
                    var i_norm = impact.Trim().ToLowerInvariant();

                    int l = l_norm switch {
                        var s when s.Contains("rare") || s.Contains("very low") => 1,
                        var s when s.Contains("unlikely") || s.Contains("low") => 2,
                        var s when s.Contains("possible") || s.Contains("medium") => 3,
                        var s when s.Contains("probable") || s.Contains("high") => 4,
                        var s when s.Contains("certain") || s.Contains("very high") => 5,
                        _ => 1
                    };
                    int i = i_norm switch {
                        var s when s.Contains("negligible") || s.Contains("lower") => 1,
                        var s when s.Contains("minor") || s.Contains("low") => 2,
                        var s when s.Contains("moderate") || s.Contains("medium") => 3,
                        var s when s.Contains("major") || s.Contains("high") || s.Contains("significant") => 4,
                        var s when s.Contains("catastrophic") || s.Contains("extreme") || s.Contains("very high") => 5,
                        _ => 1
                    };

                    int score = l * i;
                    string level = score switch {
                        >= 20 => "Critical",
                        >= 12 => "High",
                        >= 8 => "Medium",
                        >= 4 => "Low",
                        _ => "Very Low"
                    };
                    Console.WriteLine($"DEBUG: [RiskHeatMapRepository] CalculateRisk: L_val={l}, I_val={i}, Score={score} -> {level}");
                    return (score, level);
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"DEBUG: [RiskHeatMapRepository] CalculateRisk ERROR: {ex.Message}");
                    return (1, "Unknown"); // Return a default low score and "Unknown" level on error
                }
                }

                foreach (var dict in risks)
                {
                    totalRisks++;
                    
                    string GetProp(string name) {
                       var key = dict.Keys.FirstOrDefault(k => k.Equals(name, StringComparison.OrdinalIgnoreCase));
                       return key != null ? dict[key]?.ToString() : null;
                    }

                    string title = GetProp("Title") ?? "Untitled";
                    string cat = GetProp("Category") ?? "Uncategorized";
                    string controls = GetProp("Controls") ?? "";
                    
                    string iLikelihood = GetProp("InherentLikelihood") ?? "";
                    string iImpact = GetProp("InherentImpact") ?? "";
                    string rLikelihood = GetProp("ResidualLikelihood") ?? "";
                    string rImpact = GetProp("ResidualImpact") ?? "";

                    var (iScore, iLevel) = CalculateRisk(iLikelihood, iImpact);
                    var (rScore, rLevel) = CalculateRisk(rLikelihood, rImpact);
                    
                    if (!string.IsNullOrWhiteSpace(controls)) withControls++;
                    
                    if (inherentCounts.ContainsKey(iLevel)) inherentCounts[iLevel]++;
                    else inherentCounts["Unknown"]++;

                    if (residualCounts.ContainsKey(rLevel)) residualCounts[rLevel]++;
                    else residualCounts["Unknown"]++;

                    if (!categories.ContainsKey(cat)) categories[cat] = (0, 0);
                    categories[cat] = (categories[cat].Count + 1, categories[cat].TotalScore + rScore);

                    int rId = 0;
                    var rIdStr = GetProp("RiskId");
                    if (rIdStr != null) int.TryParse(rIdStr, out rId);

                    topRisks.Add(new TopRiskItem
                    {
                        RiskId = rId,
                        Title = title,
                        InherentScore = iScore,
                        ResidualScore = rScore,
                        Category = cat,
                        RiskLevel = rLevel
                    });
                }

                var levels = new[] { "Critical", "High", "Medium", "Low", "Very Low" };
                int sort = 1;
                foreach (var lvl in levels)
                {
                    response.RiskReduction.Add(new RiskLevelComparison
                    {
                        Level = lvl,
                        InherentCount = inherentCounts[lvl],
                        ResidualCount = residualCounts[lvl],
                        SortOrder = sort++
                    });
                }

                foreach (var kvp in categories)
                {
                    response.CategoryDistribution.Add(new CategoryDatum
                    {
                        CategoryName = kvp.Key,
                        Count = kvp.Value.Count,
                        AverageScore = (double)kvp.Value.TotalScore / kvp.Value.Count
                    });
                }
                
                response.ControlStats.Add(new ControlStat 
                { 
                    StatType = "Coverage", 
                    Value = totalRisks > 0 ? $"{(float)withControls/totalRisks*100:0}%" : "0%", 
                    Description = "Risks with Mitigating Controls",
                    ColorCode = "#2ecc71"
                });

                response.TopResidualRisks = topRisks.OrderByDescending(x => x.ResidualScore).Take(10).ToList();

                return response;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"ERROR: [RiskHeatMapRepository] GetAnalyticalReport: {ex.Message}");
                throw;
            }
        }

    }
}
