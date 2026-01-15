using Dapper;
using Npgsql;
using System.Collections.Generic;
using System.Data;
using System.Threading.Tasks;
using Affine.Engine.Model.Auditing.Operational;

namespace Affine.Engine.Repository.Operational
{
    public interface IOperationalRiskRepository
    {
        Task<IEnumerable<OperationalRiskAssessmentDto>> GetOperationalRisksAsync(int referenceId);
    }

    public class OperationalRiskRepository : IOperationalRiskRepository
    {
        private readonly string _connectionString;

        public OperationalRiskRepository(string connectionString)
        {
            _connectionString = connectionString;
        }

        public async Task<IEnumerable<OperationalRiskAssessmentDto>> GetOperationalRisksAsync(int referenceId)
        {
            using IDbConnection db = new NpgsqlConnection(_connectionString);
            string sql = @"
                SELECT * 
                FROM ""Risk_Assess_Framework"".""OperationalRiskAssessment"" 
                WHERE ""ReferenceId"" = @ReferenceId";

            return await db.QueryAsync<OperationalRiskAssessmentDto>(sql, new { ReferenceId = referenceId });
        }
    }
}
