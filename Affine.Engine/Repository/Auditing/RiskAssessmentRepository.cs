using Affine.Engine.Model.Auditing.Assessment;
using Dapper;
using Npgsql;
using System.Collections.Generic;
using System.Data;
using System.Threading.Tasks;

namespace Affine.Engine.Repository.Auditing
{
    public class RiskAssessmentRepository: IRiskAssessmentRepository
    {
        private readonly string _connectionString;

        public RiskAssessmentRepository(string connectionString)
        {
            _connectionString = connectionString;
        }

        #region #DropDowns

        public async Task<Risks_Assessment> GetRisksAsync(string email, string password)
        {
            using IDbConnection dbConnection = new NpgsqlConnection(_connectionString);
             dbConnection.Open();

            string query = @"
                SELECT 
                    NULL AS KeyRiskAndFactors,
                    (SELECT ARRAY_AGG(description) FROM RA_RiskLikelihood) AS RiskLikelihood,
                    (SELECT ARRAY_AGG(description) FROM RA_RiskImpact) AS RiskImpact,
                    (SELECT ARRAY_AGG(description) FROM RA_KeySecondary) AS KeyOrSecondary,
                    (SELECT ARRAY_AGG(description) FROM RA_RiskCategory) AS RiskCategory;";

            return await dbConnection.QueryFirstOrDefaultAsync<Risks_Assessment>(query);
        }

        public async Task<Controls_Assessment> GetControlsAsync(string email, string password)
        {
            using IDbConnection dbConnection = new NpgsqlConnection(_connectionString);
           dbConnection.Open();

            string query = @"
                SELECT 
                    NULL AS MitigatingControls,
                    NULL AS Responsibility,
                    (SELECT ARRAY_AGG(description) FROM RA_DataFrequency) AS DataFrequency,
                    (SELECT ARRAY_AGG(description) FROM RA_Nature) AS Nature,
                    (SELECT ARRAY_AGG(description) FROM RA_Frequency) AS Frequency;";

            return await dbConnection.QueryFirstOrDefaultAsync<Controls_Assessment>(query, new { Email = email, Password = password });
        }

        public async Task<Outcome_Assessment> GetOutcomesAsync(string email, string password)
        {
            using IDbConnection dbConnection = new NpgsqlConnection(_connectionString);
           dbConnection.Open();

            string query = @"
                SELECT 
                    (SELECT ARRAY_AGG(description) FROM RA_Evidence) AS Evidence,
                    NULL AS Authoriser,
                    NULL AS AuditorsRecommendedActionPlan,
                    NULL AS ResponsiblePerson,
                    NULL AS AgreedDate,
                    (SELECT ARRAY_AGG(description) FROM RA_OutcomeLikelihood) AS OutcomeLikelihood,
                    (SELECT ARRAY_AGG(description) FROM RA_Impact) AS Impact;";

            return await dbConnection.QueryFirstOrDefaultAsync<Outcome_Assessment>(query, new { Email = email, Password = password });
        }

        #endregion

        #region RiskAssessment

        public async Task<RiskAssessment_Assessment> GetRiskAssessmentAsync(int RiskAssessmentRefID)
        {
            using IDbConnection dbConnection = new NpgsqlConnection(_connectionString);
           dbConnection.Open();

            string query = @"
                SELECT 
                    ref.client,
                    ref.assessment_period,
                    ref.assessor,
                    ref.approved_by,
                    ra.BusinessObjectives AS ProcessObjectivesAssessment_BusinessObjectives,
                    ra.MainProcess AS ProcessObjectivesAssessment_MainProcess,
                    ra.SubProcess AS ProcessObjectivesAssessment_SubProcess,
                    ra.KeyRiskAndFactors AS RisksAssessment_KeyRiskAndFactors,
                    rl.description AS RisksAssessment_RiskLikelihood,
                    ri.description AS RisksAssessment_RiskImpact,
                    ks.description AS RisksAssessment_KeyOrSecondary,
                    rc.description AS RisksAssessment_RiskCategory,
                    ra.MitigatingControls AS ControlsAssessment_MitigatingControls,
                    ra.Responsibility AS ControlsAssessment_Responsibility,
                    df.description AS ControlsAssessment_DataFrequency,
                    f.description AS ControlsAssessment_Frequency,
                    e.description AS OutcomeAssessment_Evidence,
                    ra.Authoriser AS OutcomeAssessment_Authoriser,
                    ra.AuditorsRecommendedActionPlan AS OutcomeAssessment_AuditorsRecommendedActionPlan,
                    ra.ResponsiblePerson AS OutcomeAssessment_ResponsiblePerson,
                    ra.AgreedDate AS OutcomeAssessment_AgreedDate,
                    ol.description AS OutcomeAssessment_OutcomeLikelihood,
                    i.description AS OutcomeAssessment_Impact
                FROM 
                    RiskAssessment ra
                INNER JOIN 
                    RiskAssessmentReference ref ON ra.reference_id = ref.reference_id
                LEFT JOIN 
                    RA_RiskLikelihood rl ON ra.RiskLikelihoodId = rl.id
                LEFT JOIN 
                    RA_RiskImpact ri ON ra.RiskImpactId = ri.id
                LEFT JOIN 
                    RA_KeySecondary ks ON ra.KeySecondaryId = ks.id
                LEFT JOIN 
                    RA_RiskCategory rc ON ra.RiskCategoryId = rc.id
                LEFT JOIN 
                    RA_DataFrequency df ON ra.DataFrequencyId = df.id
                LEFT JOIN 
                    RA_Frequency f ON ra.FrequencyId = f.id
                LEFT JOIN 
                    RA_Evidence e ON ra.EvidenceId = e.id
                LEFT JOIN 
                    RA_OutcomeLikelihood ol ON ra.OutcomeLikelihoodId = ol.id
                LEFT JOIN 
                    RA_Impact i ON ra.ImpactId = i.id
                WHERE 
                    ra.RiskAssessment_RefID = @RiskAssessmentID;";

            return await dbConnection.QueryFirstOrDefaultAsync<RiskAssessment_Assessment>(query, new { RiskAssessmentID = RiskAssessmentRefID });
        }

        public async Task<bool> AddRiskAssessmentAsync(List<RiskAssessmentCreateRequest> requests)
        {
            using IDbConnection dbConnection = new NpgsqlConnection(_connectionString);
            dbConnection.Open();
            using var transaction = dbConnection.BeginTransaction();

            try
            {
                int referenceId;

                if (requests[0].ReferenceId > 0)
                {
                    // Check if reference exists
                    string checkQuery = "SELECT reference_id FROM RiskAssessmentReference WHERE reference_id = @ReferenceId";
                    var existingRefId = await dbConnection.QueryFirstOrDefaultAsync<int?>(checkQuery, new { requests[0].ReferenceId });

                    if (existingRefId == null)
                    {
                        return false; // Reference doesn't exist
                    }
                    referenceId = existingRefId.Value;
                }
                else
                {
                    // Create new reference
                    string insertRefQuery = @"
                        INSERT INTO RiskAssessmentReference (
                            client,
                            assessment_period,
                            assessor,
                            approved_by
                        ) VALUES (
                            @Client,
                            @AssessmentPeriod,
                            @Assessor,
                            @ApprovedBy
                        ) RETURNING reference_id";

                    referenceId = await dbConnection.ExecuteScalarAsync<int>(insertRefQuery, requests[0], transaction);
                }

                // Insert risk assessments
                string insertQuery = @"
                    INSERT INTO RiskAssessment (
                        reference_id,
                        BusinessObjectives,
                        MainProcess,
                        SubProcess,
                        KeyRiskAndFactors,
                        MitigatingControls,
                        Responsibility,
                        Authoriser,
                        AuditorsRecommendedActionPlan,
                        ResponsiblePerson,
                        AgreedDate,
                        RiskLikelihoodId,
                        RiskImpactId,
                        KeySecondaryId,
                        RiskCategoryId,
                        DataFrequencyId,
                        FrequencyId,
                        EvidenceId,
                        OutcomeLikelihoodId,
                        ImpactId
                    ) VALUES (
                        @ReferenceId,
                        @BusinessObjectives,
                        @MainProcess,
                        @SubProcess,
                        @KeyRiskAndFactors,
                        @MitigatingControls,
                        @Responsibility,
                        @Authoriser,
                        @AuditorsRecommendedActionPlan,
                        @ResponsiblePerson,
                        @AgreedDate,
                        @RiskLikelihoodId,
                        @RiskImpactId,
                        @KeySecondaryId,
                        @RiskCategoryId,
                        @DataFrequencyId,
                        @FrequencyId,
                        @EvidenceId,
                        @OutcomeLikelihoodId,
                        @ImpactId
                    )";

                foreach (var request in requests)
                {
                    var parameters = new {
                        ReferenceId = referenceId,
                        request.BusinessObjectives,
                        request.MainProcess,
                        request.SubProcess,
                        request.KeyRiskAndFactors,
                        request.MitigatingControls,
                        request.Responsibility,
                        request.Authoriser,
                        request.AuditorsRecommendedActionPlan,
                        request.ResponsiblePerson,
                        request.AgreedDate,
                        request.RiskLikelihoodId,
                        request.RiskImpactId,
                        request.KeySecondaryId,
                        request.RiskCategoryId,
                        request.DataFrequencyId,
                        request.FrequencyId,
                        request.EvidenceId,
                        request.OutcomeLikelihoodId,
                        request.ImpactId
                    };
                    
                    await dbConnection.ExecuteAsync(insertQuery, parameters, transaction);
                }

                transaction.Commit();
                return true;
            }
            catch
            {
                transaction.Rollback();
                throw;
            }
        }

        public async Task<bool> UpdateRiskAssessmentAsync(int riskAssessmentRefId, RiskAssessmentUpdateRequest request)
        {
            using IDbConnection dbConnection = new NpgsqlConnection(_connectionString);
            dbConnection.Open();

            string updateQuery = @"
                UPDATE RiskAssessment 
                SET 
                    BusinessObjectives = @BusinessObjectives,
                    MainProcess = @MainProcess,
                    SubProcess = @SubProcess,
                    KeyRiskAndFactors = @KeyRiskAndFactors,
                    MitigatingControls = @MitigatingControls,
                    Responsibility = @Responsibility,
                    Authoriser = @Authoriser,
                    AuditorsRecommendedActionPlan = @AuditorsRecommendedActionPlan,
                    ResponsiblePerson = @ResponsiblePerson,
                    AgreedDate = @AgreedDate,
                    RiskLikelihoodId = @RiskLikelihoodId,
                    RiskImpactId = @RiskImpactId,
                    KeySecondaryId = @KeySecondaryId,
                    RiskCategoryId = @RiskCategoryId,
                    DataFrequencyId = @DataFrequencyId,
                    FrequencyId = @FrequencyId,
                    EvidenceId = @EvidenceId,
                    OutcomeLikelihoodId = @OutcomeLikelihoodId,
                    ImpactId = @ImpactId
                WHERE RiskAssessment_RefID = @RiskAssessmentRefId";

            var parameters = new
            {
                RiskAssessmentRefId = riskAssessmentRefId,
                request.BusinessObjectives,
                request.MainProcess,
                request.SubProcess,
                request.KeyRiskAndFactors,
                request.MitigatingControls,
                request.Responsibility,
                request.Authoriser,
                request.AuditorsRecommendedActionPlan,
                request.ResponsiblePerson,
                request.AgreedDate,
                request.RiskLikelihoodId,
                request.RiskImpactId,
                request.KeySecondaryId,
                request.RiskCategoryId,
                request.DataFrequencyId,
                request.FrequencyId,
                request.EvidenceId,
                request.OutcomeLikelihoodId,
                request.ImpactId
            };

            var rowsAffected = await dbConnection.ExecuteAsync(updateQuery, parameters);
            return rowsAffected > 0;
        }

        #endregion

        #region RA_Tables

        public async Task<IEnumerable<RiskLikelihood>> GetRiskLikelihoodsAsync()
        {
            using IDbConnection dbConnection = new NpgsqlConnection(_connectionString);
            string query = "SELECT Id, Description, Position FROM ra_risklikelihood ORDER BY position";
            return await dbConnection.QueryAsync<RiskLikelihood>(query);
        }

        public async Task<IEnumerable<Impact>> GetImpactsAsync()
        {
            using IDbConnection dbConnection = new NpgsqlConnection(_connectionString);
            string query = "SELECT id, description, position FROM ra_impact ORDER BY position";
            return await dbConnection.QueryAsync<Impact>(query);
        }

        public async Task<IEnumerable<KeySecondary>> GetKeySecondaryRisksAsync()
        {
            using IDbConnection dbConnection = new NpgsqlConnection(_connectionString);
            string query = "SELECT id, description, position FROM ra_keysecondary ORDER BY position";
            return await dbConnection.QueryAsync<KeySecondary>(query);
        }

        public async Task<IEnumerable<RiskCategory>> GetRiskCategoriesAsync()
        {
            using IDbConnection dbConnection = new NpgsqlConnection(_connectionString);
            string query = "SELECT id, description, position FROM ra_riskcategory ORDER BY position";
            return await dbConnection.QueryAsync<RiskCategory>(query);
        }

        public async Task<IEnumerable<DataFrequency>> GetDataFrequenciesAsync()
        {
            using IDbConnection dbConnection = new NpgsqlConnection(_connectionString);
            string query = "SELECT id, description, position FROM ra_datafrequency ORDER BY position";
            return await dbConnection.QueryAsync<DataFrequency>(query);
        }

        public async Task<IEnumerable<OutcomeLikelihood>> GetOutcomeLikelihoodsAsync()
        {
            using IDbConnection dbConnection = new NpgsqlConnection(_connectionString);
            string query = "SELECT id, description, position FROM ra_outcomelikelihood ORDER BY position";
            return await dbConnection.QueryAsync<OutcomeLikelihood>(query);
        }

        public async Task<IEnumerable<Evidence>> GetEvidenceAsync()
        {
            using IDbConnection dbConnection = new NpgsqlConnection(_connectionString);
            string query = "SELECT id, description, position FROM ra_evidence ORDER BY position";
            return await dbConnection.QueryAsync<Evidence>(query);
        }

        #endregion
    }
}
