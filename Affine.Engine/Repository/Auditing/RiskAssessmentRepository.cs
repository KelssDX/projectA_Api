using Affine.Engine.Model.Auditing.Assessment;
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
    public class RiskAssessmentRepository
    {
        private readonly string _connectionString;

        public RiskAssessmentRepository(string connectionString)
        {
            _connectionString = connectionString;
        }

        #region #DropDowns
        public Risks_Assessment GetRisks(string email, string password)
        {
            using IDbConnection dbConnection = new NpgsqlConnection(_connectionString);
            dbConnection.Open();

            string query = @"
        SELECT 
    NULL AS KeyRiskAndFactors,
    (SELECT ARRAY_AGG(description) FROM RA_RiskLikelihood) AS RiskLikelihood,
    (SELECT ARRAY_AGG(description) FROM RA_Riskimpact) AS RiskImpact,
    (SELECT ARRAY_AGG(description) FROM RA_KeySecondary) AS KeyOrSecondary,
    (SELECT ARRAY_AGG(description) FROM RS_RiskCategory) AS RiskCategory;";

            return dbConnection.QueryFirstOrDefault<Risks_Assessment>(query);
        }




        public Controls_Assessment GetControls(string email, string password)
        {
            using IDbConnection dbConnection = new NpgsqlConnection(_connectionString);
            dbConnection.Open();

            string query = @"
       SELECT 
    NULL AS MitigatingControls,
    NULL AS Responsibility,
    (SELECT ARRAY_AGG(description) FROM RA_DataFrequency) AS DataFrequency,
    (SELECT ARRAY_AGG(description) FROM RA_Nature) AS Nature,
    (SELECT ARRAY_AGG(description) FROM RA_Frequency) AS Frequency;
";

            return dbConnection.QueryFirstOrDefault<Controls_Assessment>(query, new { Email = email, Password = password });
        }

      
        public Outcome_Assessment GetOutcomes(string email, string password)
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
    (SELECT ARRAY_AGG(description) FROM RA_OutcomeLkelihood) AS OutcomeLikelihood,
    (SELECT ARRAY_AGG(description) FROM RA_Impact) AS Impact;";

            return dbConnection.QueryFirstOrDefault<Outcome_Assessment>(query, new { Email = email, Password = password });
        }




        #endregion Dropdowns


        public RiskAssessment_Assessment GetRiskAssessment(int RiskAssessmentRefID)
        {
            using IDbConnection dbConnection = new NpgsqlConnection(_connectionString);
            dbConnection.Open();

            string query = @"
        SELECT 
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
LEFT JOIN 
    RA_RiskLikelihood rl ON ra.id = rl.assessment_id
LEFT JOIN 
    RA_RiskImpact ri ON ra.id = ri.assessment_id
LEFT JOIN 
    RA_KeySecondary ks ON ra.id = ks.assessment_id
LEFT JOIN 
    RS_RiskCategory rc ON ra.id = rc.assessment_id
LEFT JOIN 
    RA_DataFrequency df ON ra.id = df.assessment_id
LEFT JOIN 
    RA_Frequency f ON ra.id = f.assessment_id
LEFT JOIN 
    RA_OutcomeEvidence e ON ra.id = e.assessment_id
LEFT JOIN 
    RA_OutcomeLikelihood ol ON ra.id = ol.assessment_id
LEFT JOIN 
    RA_OutcomeImpact i ON ra.id = i.assessment_id
WHERE 
    ra.RiskAssessment_RefID = @RiskAssessmentID; 
     ";

            return dbConnection.QueryFirstOrDefault<RiskAssessment_Assessment>(query, new { RiskAssessmentID = RiskAssessmentRefID });
        }


        public bool AddRiskAssessment(RiskAssessmentCreateRequest RiskAssessmentCreate)
        {
            using IDbConnection dbConnection = new NpgsqlConnection(_connectionString);
            dbConnection.Open();

            // Check if the RiskAssessment already exists
            string checkQuery = "SELECT id FROM RiskAssessment WHERE RiskAssessment_RefID = @RiskAssessment_RefID";
            var existingId = dbConnection.QueryFirstOrDefault<int?>(checkQuery, new { RiskAssessment_RefID = RiskAssessmentCreate.RiskAssessment_RefID });

            if (existingId != null)
            {
                // RiskAssessment already exists, return false (not added)
                return false;
            }

            // If not exists, insert the RiskAssessment
            string insertQuery = @"
        INSERT INTO RiskAssessment (
            RiskAssessment_RefID,
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
            @RiskAssessment_RefID,
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
        ) RETURNING id";

            // Execute the insert query
            int insertedRiskAssessmentId = dbConnection.ExecuteScalar<int>(insertQuery, new
            {
                RiskAssessment_RefID = RiskAssessmentCreate.RiskAssessment_RefID,
                BusinessObjectives = RiskAssessmentCreate.BusinessObjectives,
                MainProcess = RiskAssessmentCreate.MainProcess,
                SubProcess = RiskAssessmentCreate.SubProcess,
                KeyRiskAndFactors = RiskAssessmentCreate.KeyRiskAndFactors,
                MitigatingControls = RiskAssessmentCreate.MitigatingControls,
                Responsibility = RiskAssessmentCreate.Responsibility,
                Authoriser = RiskAssessmentCreate.Authoriser,
                AuditorsRecommendedActionPlan = RiskAssessmentCreate.AuditorsRecommendedActionPlan,
                ResponsiblePerson = RiskAssessmentCreate.ResponsiblePerson,
                AgreedDate = RiskAssessmentCreate.AgreedDate,
                RiskLikelihoodId = RiskAssessmentCreate.RiskLikelihoodId,
                RiskImpactId = RiskAssessmentCreate.RiskImpactId,
                KeySecondaryId = RiskAssessmentCreate.KeySecondaryId,
                RiskCategoryId = RiskAssessmentCreate.RiskCategoryId,
                DataFrequencyId = RiskAssessmentCreate.DataFrequencyId,
                FrequencyId = RiskAssessmentCreate.FrequencyId,
                EvidenceId = RiskAssessmentCreate.EvidenceId,
                OutcomeLikelihoodId = RiskAssessmentCreate.OutcomeLikelihoodId,
                ImpactId = RiskAssessmentCreate.ImpactId
            });

            // Return true (added successfully)
            return true;
        }



    }
}
