using Affine.Engine.Model.Auditing.Assessment;
using Dapper;
using Npgsql;
using System.Collections.Generic;
using System.Data;
using System.Threading.Tasks;
using System.Linq;
using System;

namespace Affine.Engine.Repository.Auditing
{
    public class RiskAssessmentRepository: IRiskAssessmentRepository
    {
        private readonly string _connectionString;

        public RiskAssessmentRepository(string connectionString)
        {
            _connectionString = connectionString ?? throw new ArgumentNullException(nameof(connectionString));
        }

        #region #DropDowns

        public async Task<Risks_Assessment> GetRisksAsync(string email, string password)
        {
            try
            {
                using IDbConnection dbConnection = new NpgsqlConnection(_connectionString);
                dbConnection.Open();

                string query = @"
                    SELECT 
                        NULL AS KeyRiskAndFactors,
                        (SELECT ARRAY_AGG(description) FROM ra_risklikelihood) AS RiskLikelihood,
                        (SELECT ARRAY_AGG(description) FROM ra_riskimpact) AS RiskImpact,
                        (SELECT ARRAY_AGG(description) FROM ra_keysecondary) AS KeyOrSecondary,
                        (SELECT ARRAY_AGG(description) FROM ra_riskcategory) AS RiskCategory;";

                var result = await dbConnection.QueryFirstOrDefaultAsync<Risks_Assessment>(query);
                return result ?? new Risks_Assessment();
            }
            catch (Exception ex)
            {
                throw new InvalidOperationException($"Failed to retrieve risks. Error: {ex.Message}", ex);
            }
        }

        public async Task<Controls_Assessment> GetControlsAsync(string email, string password)
        {
            try
            {
                using IDbConnection dbConnection = new NpgsqlConnection(_connectionString);
                dbConnection.Open();

                string query = @"
                    SELECT 
                        NULL AS MitigatingControls,
                        NULL AS Responsibility,
                        (SELECT ARRAY_AGG(description) FROM ra_datafrequency) AS DataFrequency,
                        (SELECT ARRAY_AGG(description) FROM ra_nature) AS Nature,
                        (SELECT ARRAY_AGG(description) FROM ra_frequency) AS Frequency;";

                var result = await dbConnection.QueryFirstOrDefaultAsync<Controls_Assessment>(query, new { Email = email, Password = password });
                return result ?? new Controls_Assessment();
            }
            catch (Exception ex)
            {
                throw new InvalidOperationException($"Failed to retrieve controls. Error: {ex.Message}", ex);
            }
        }

        public async Task<Outcome_Assessment> GetOutcomesAsync(string email, string password)
        {
            try
            {
                using IDbConnection dbConnection = new NpgsqlConnection(_connectionString);
                dbConnection.Open();

                string query = @"
                    SELECT 
                        (SELECT ARRAY_AGG(description) FROM ra_evidence) AS Evidence,
                        NULL AS Authoriser,
                        NULL AS AuditorsRecommendedActionPlan,
                        NULL AS ResponsiblePerson,
                        NULL AS AgreedDate,
                        (SELECT ARRAY_AGG(description) FROM ra_outcomelikelihood) AS OutcomeLikelihood,
                        (SELECT ARRAY_AGG(description) FROM ra_impact) AS Impact;";

                var result = await dbConnection.QueryFirstOrDefaultAsync<Outcome_Assessment>(query, new { Email = email, Password = password });
                return result ?? new Outcome_Assessment();
            }
            catch (Exception ex)
            {
                throw new InvalidOperationException($"Failed to retrieve outcomes. Error: {ex.Message}", ex);
            }
        }

        #endregion

        #region RiskAssessment

        public async Task<RiskAssessment_Assessment> GetRiskAssessmentAsync(int RiskAssessmentRefID)
        {
            if (RiskAssessmentRefID <= 0)
            {
                throw new ArgumentException("Reference ID must be greater than zero.", nameof(RiskAssessmentRefID));
            }

            try
            {
                using IDbConnection dbConnection = new NpgsqlConnection(_connectionString);
                dbConnection.Open();

                // First, get the reference (parent) data
                string referenceQuery = @"
                    SELECT 
                        reference_id as ReferenceId,
                        client as Client,
                        assessment_start_date as AssessmentStartDate,
                        assessment_end_date as AssessmentEndDate,
                        assessor as Assessor,
                        approved_by as ApprovedBy
                    FROM 
                        riskassessmentreference
                    WHERE 
                        reference_id = @ReferenceId";

                var parent = await dbConnection.QueryFirstOrDefaultAsync<RiskAssessment_Assessment>(
                    referenceQuery, 
                    new { ReferenceId = RiskAssessmentRefID });

                if (parent == null)
                {
                    return null;
                }

                // Then, get all risk assessments (children) for this reference
                string assessmentsQuery = @"
                    SELECT 
                        ra.RiskAssessment_RefID,
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
                        riskassessment ra
                    LEFT JOIN 
                        ra_risklikelihood rl ON ra.RiskLikelihoodId = rl.id
                    LEFT JOIN 
                        ra_riskimpact ri ON ra.RiskImpactId = ri.id
                    LEFT JOIN 
                        ra_keysecondary ks ON ra.KeySecondaryId = ks.id
                    LEFT JOIN 
                        ra_riskcategory rc ON ra.RiskCategoryId = rc.id
                    LEFT JOIN 
                        ra_datafrequency df ON ra.DataFrequencyId = df.id
                    LEFT JOIN 
                        ra_frequency f ON ra.FrequencyId = f.id
                    LEFT JOIN 
                        ra_evidence e ON ra.EvidenceId = e.id
                    LEFT JOIN 
                        ra_outcomelikelihood ol ON ra.OutcomeLikelihoodId = ol.id
                    LEFT JOIN 
                        ra_impact i ON ra.ImpactId = i.id
                    WHERE 
                        ra.reference_id = @ReferenceId
                    ORDER BY
                        ra.RiskAssessment_RefID ASC";

                var children = await dbConnection.QueryAsync<RiskAssessmentDetail>(
                    assessmentsQuery,
                    new { ReferenceId = RiskAssessmentRefID });

                // Add children to parent
                parent.RiskAssessments = children.ToList();

                return parent;
            }
            catch (Exception ex)
            {
                throw new InvalidOperationException($"Failed to retrieve risk assessments. Error: {ex.Message}", ex);
            }
        }

        public async Task<bool> AddRiskAssessmentAsync(List<RiskAssessmentCreateRequest> requests, RiskAssessmentReferenceInput reference, int? referenceId = null)
        {
            if (requests == null || !requests.Any())
            {
                throw new ArgumentException("Risk assessment requests cannot be null or empty.", nameof(requests));
            }

            if (reference == null && !referenceId.HasValue)
            {
                throw new ArgumentNullException(nameof(reference), "Risk assessment reference information is required when not using an existing reference.");
            }

            try
            {
                using IDbConnection dbConnection = new NpgsqlConnection(_connectionString);
                dbConnection.Open();
                
                // Begin transaction to ensure all inserts succeed or fail together
                using var transaction = dbConnection.BeginTransaction();
                
                try
                {
                    int refId;
                    
                    // Check if a reference ID was provided and if it exists
                    if (referenceId.HasValue && referenceId.Value > 0)
                    {
                        // Verify the reference ID exists
                        string checkReferenceQuery = @"
                            SELECT COUNT(*) 
                            FROM riskassessmentreference 
                            WHERE reference_id = @ReferenceId";
                        
                        var referenceExists = await dbConnection.ExecuteScalarAsync<int>(
                            checkReferenceQuery, 
                            new { ReferenceId = referenceId.Value }, 
                            transaction);
                        
                        if (referenceExists > 0)
                        {
                            // Reference exists, use the provided ID
                            refId = referenceId.Value;
                        }
                        else if (reference != null)
                        {
                            // Reference doesn't exist but we have reference data, create a new one
                            string insertRefQuery = @"
                                INSERT INTO riskassessmentreference (
                                    client, 
                                    assessment_start_date, 
                                    assessment_end_date, 
                                    assessor, 
                                    approved_by
                                ) VALUES (
                                    @Client, 
                                    @AssessmentStartDate, 
                                    @AssessmentEndDate, 
                                    @Assessor, 
                                    @ApprovedBy
                                ) RETURNING reference_id";
                            
                            refId = await dbConnection.ExecuteScalarAsync<int>(insertRefQuery, reference, transaction);
                        }
                        else
                        {
                            // Neither a valid reference ID nor reference data was provided
                            throw new ArgumentException("Invalid reference ID and no reference data provided.");
                        }
                    }
                    else if (reference != null)
                    {
                        // No reference ID provided but we have reference data, create a new one
                        string insertRefQuery = @"
                            INSERT INTO riskassessmentreference (
                                client, 
                                assessment_start_date, 
                                assessment_end_date, 
                                assessor, 
                                approved_by
                            ) VALUES (
                                @Client, 
                                @AssessmentStartDate, 
                                @AssessmentEndDate, 
                                @Assessor, 
                                @ApprovedBy
                            ) RETURNING reference_id";
                        
                        refId = await dbConnection.ExecuteScalarAsync<int>(insertRefQuery, reference, transaction);
                    }
                    else
                    {
                        // Neither a reference ID nor reference data was provided
                        throw new ArgumentException("Either a reference ID or reference data must be provided.");
                    }
                    
                    // Insert each risk assessment with the reference ID
                    string insertQuery = @"
                        INSERT INTO riskassessment (
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
                        var parameters = new
                        {
                            ReferenceId = refId,
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
                    
                    // Commit the transaction
                    transaction.Commit();
                    return true;
                }
                catch
                {
                    // If any error occurs, roll back the transaction
                    transaction.Rollback();
                    throw;
                }
            }
            catch (Exception ex)
            {
                throw new InvalidOperationException($"Failed to add risk assessment. Error: {ex.Message}", ex);
            }
        }

        public async Task<bool> UpdateRiskAssessmentsAsync(List<RiskAssessmentUpdateRequest> updates, int referenceId)
        {
            if (updates == null || !updates.Any())
            {
                throw new ArgumentException("Updates cannot be null or empty.", nameof(updates));
            }

            if (referenceId <= 0)
            {
                throw new ArgumentException("Reference ID must be greater than zero.", nameof(referenceId));
            }

            try
            {
                using IDbConnection dbConnection = new NpgsqlConnection(_connectionString);
                dbConnection.Open();
                
                // Begin transaction to ensure all updates succeed or fail together
                using var transaction = dbConnection.BeginTransaction();
                
                try
                {
                    // Check if reference exists
                    string checkReferenceQuery = @"
                        SELECT COUNT(*) 
                        FROM riskassessmentreference 
                        WHERE reference_id = @ReferenceId";
                    
                    var referenceExists = await dbConnection.ExecuteScalarAsync<int>(
                        checkReferenceQuery, 
                        new { ReferenceId = referenceId }, 
                        transaction);
                    
                    if (referenceExists == 0)
                    {
                        // Reference ID doesn't exist
                        transaction.Rollback();
                        return false;
                    }
                    
                    // Update each risk assessment individually with only the specified fields
                    foreach (var update in updates)
                    {
                        if (update.RiskAssessmentRefId <= 0)
                        {
                            continue; // Skip invalid IDs
                        }
                        
                        // Check if this specific risk assessment exists and belongs to the reference
                        string checkRiskAssessmentQuery = @"
                            SELECT COUNT(*) 
                            FROM riskassessment 
                            WHERE RiskAssessment_RefID = @RiskAssessmentRefId 
                            AND reference_id = @ReferenceId";
                        
                        var riskAssessmentExists = await dbConnection.ExecuteScalarAsync<int>(
                            checkRiskAssessmentQuery, 
                            new { 
                                RiskAssessmentRefId = update.RiskAssessmentRefId,
                                ReferenceId = referenceId
                            }, 
                            transaction);
                        
                        if (riskAssessmentExists == 0)
                        {
                            continue; // Skip updates for non-existent risk assessments
                        }
                        
                        // Build parameters and update fields more efficiently
                        var parameters = new DynamicParameters();
                        parameters.Add("RiskAssessmentRefId", update.RiskAssessmentRefId);
                        
                        var updateFields = new List<string>();
                        
                        // More concise approach to adding fields for update
                        AddUpdateField(updateFields, parameters, "BusinessObjectives", update.BusinessObjectives);
                        AddUpdateField(updateFields, parameters, "MainProcess", update.MainProcess);
                        AddUpdateField(updateFields, parameters, "SubProcess", update.SubProcess);
                        AddUpdateField(updateFields, parameters, "KeyRiskAndFactors", update.KeyRiskAndFactors);
                        AddUpdateField(updateFields, parameters, "MitigatingControls", update.MitigatingControls);
                        AddUpdateField(updateFields, parameters, "Responsibility", update.Responsibility);
                        AddUpdateField(updateFields, parameters, "Authoriser", update.Authoriser);
                        AddUpdateField(updateFields, parameters, "AuditorsRecommendedActionPlan", update.AuditorsRecommendedActionPlan);
                        AddUpdateField(updateFields, parameters, "ResponsiblePerson", update.ResponsiblePerson);
                        AddUpdateField(updateFields, parameters, "AgreedDate", update.AgreedDate);
                        AddUpdateField(updateFields, parameters, "RiskLikelihoodId", update.RiskLikelihoodId);
                        AddUpdateField(updateFields, parameters, "RiskImpactId", update.RiskImpactId);
                        AddUpdateField(updateFields, parameters, "KeySecondaryId", update.KeySecondaryId);
                        AddUpdateField(updateFields, parameters, "RiskCategoryId", update.RiskCategoryId);
                        AddUpdateField(updateFields, parameters, "DataFrequencyId", update.DataFrequencyId);
                        AddUpdateField(updateFields, parameters, "FrequencyId", update.FrequencyId);
                        AddUpdateField(updateFields, parameters, "EvidenceId", update.EvidenceId);
                        AddUpdateField(updateFields, parameters, "OutcomeLikelihoodId", update.OutcomeLikelihoodId);
                        AddUpdateField(updateFields, parameters, "ImpactId", update.ImpactId);
                        
                        // Skip if no fields to update
                        if (updateFields.Count == 0)
                        {
                            continue;
                        }
                        
                        // Build and execute the update query
                        string updateQuery = $@"
                            UPDATE riskassessment 
                            SET {string.Join(", ", updateFields)}
                            WHERE RiskAssessment_RefID = @RiskAssessmentRefId";
                        
                        await dbConnection.ExecuteAsync(updateQuery, parameters, transaction);
                    }
                    
                    // Commit the transaction
                    transaction.Commit();
                    return true;
                }
                catch
                {
                    // If any error occurs, roll back the transaction
                    transaction.Rollback();
                    throw;
                }
            }
            catch (Exception ex)
            {
                throw new InvalidOperationException($"Failed to update risk assessments. Error: {ex.Message}", ex);
            }
        }

        // Helper method to add a field to the update if it's not null
        private void AddUpdateField<T>(List<string> updateFields, DynamicParameters parameters, string fieldName, T value)
        {
            if (value != null)
            {
                updateFields.Add($"{fieldName} = @{fieldName}");
                parameters.Add(fieldName, value);
            }
        }

        public async Task<bool> DeleteRiskAssessmentAsync(int riskAssessmentId, int referenceId)
        {
            if (riskAssessmentId <= 0)
            {
                throw new ArgumentException("Risk Assessment ID must be greater than zero.", nameof(riskAssessmentId));
            }

            if (referenceId <= 0)
            {
                throw new ArgumentException("Reference ID must be greater than zero.", nameof(referenceId));
            }

            try
            {
                using IDbConnection dbConnection = new NpgsqlConnection(_connectionString);
                dbConnection.Open();

                string deleteQuery = @"
                    DELETE FROM riskassessment 
                    WHERE RiskAssessment_RefID = @RiskAssessmentId 
                    AND reference_id = @ReferenceId";

                var rowsAffected = await dbConnection.ExecuteAsync(deleteQuery, new 
                { 
                    RiskAssessmentId = riskAssessmentId, 
                    ReferenceId = referenceId 
                });

                return rowsAffected > 0;
            }
            catch (Exception ex)
            {
                throw new InvalidOperationException($"Failed to delete risk assessment. Error: {ex.Message}", ex);
            }
        }

        #endregion

        #region RA_Tables

        public async Task<IEnumerable<RiskLikelihood>> GetRiskLikelihoodsAsync()
        {
            try
            {
                using IDbConnection dbConnection = new NpgsqlConnection(_connectionString);
                dbConnection.Open();

                string query = "SELECT id, description FROM ra_risklikelihood ORDER BY position";
                var result = await dbConnection.QueryAsync<RiskLikelihood>(query);
                return result ?? Enumerable.Empty<RiskLikelihood>();
            }
            catch (Exception ex)
            {
                throw new InvalidOperationException($"Failed to retrieve risk likelihoods. Error: {ex.Message}", ex);
            }
        }

        public async Task<IEnumerable<Impact>> GetImpactsAsync()
        {
            try
            {
                using IDbConnection dbConnection = new NpgsqlConnection(_connectionString);
                dbConnection.Open();

                string query = "SELECT id, description FROM ra_impact ORDER BY position";
                var result = await dbConnection.QueryAsync<Impact>(query);
                return result ?? Enumerable.Empty<Impact>();
            }
            catch (Exception ex)
            {
                throw new InvalidOperationException($"Failed to retrieve impacts. Error: {ex.Message}", ex);
            }
        }

        public async Task<IEnumerable<KeySecondary>> GetKeySecondaryRisksAsync()
        {
            try
            {
                using IDbConnection dbConnection = new NpgsqlConnection(_connectionString);
                dbConnection.Open();

                string query = "SELECT id, description FROM ra_keysecondary ORDER BY position";
                var result = await dbConnection.QueryAsync<KeySecondary>(query);
                return result ?? Enumerable.Empty<KeySecondary>();
            }
            catch (Exception ex)
            {
                throw new InvalidOperationException($"Failed to retrieve key secondary risks. Error: {ex.Message}", ex);
            }
        }

        public async Task<IEnumerable<RiskCategory>> GetRiskCategoriesAsync()
        {
            try
            {
                using IDbConnection dbConnection = new NpgsqlConnection(_connectionString);
                dbConnection.Open();

                string query = "SELECT id, description FROM ra_riskcategory ORDER BY position";
                var result = await dbConnection.QueryAsync<RiskCategory>(query);
                return result ?? Enumerable.Empty<RiskCategory>();
            }
            catch (Exception ex)
            {
                throw new InvalidOperationException($"Failed to retrieve risk categories. Error: {ex.Message}", ex);
            }
        }

        public async Task<IEnumerable<DataFrequency>> GetDataFrequenciesAsync()
        {
            try
            {
                using IDbConnection dbConnection = new NpgsqlConnection(_connectionString);
                dbConnection.Open();

                string query = "SELECT id, description FROM ra_datafrequency ORDER BY position";
                var result = await dbConnection.QueryAsync<DataFrequency>(query);
                return result ?? Enumerable.Empty<DataFrequency>();
            }
            catch (Exception ex)
            {
                throw new InvalidOperationException($"Failed to retrieve data frequencies. Error: {ex.Message}", ex);
            }
        }

        public async Task<IEnumerable<OutcomeLikelihood>> GetOutcomeLikelihoodsAsync()
        {
            try
            {
                using IDbConnection dbConnection = new NpgsqlConnection(_connectionString);
                dbConnection.Open();

                string query = "SELECT id, description FROM ra_outcomelikelihood ORDER BY position";
                var result = await dbConnection.QueryAsync<OutcomeLikelihood>(query);
                return result ?? Enumerable.Empty<OutcomeLikelihood>();
            }
            catch (Exception ex)
            {
                throw new InvalidOperationException($"Failed to retrieve outcome likelihoods. Error: {ex.Message}", ex);
            }
        }

        public async Task<IEnumerable<Evidence>> GetEvidenceAsync()
        {
            try
            {
                using IDbConnection dbConnection = new NpgsqlConnection(_connectionString);
                dbConnection.Open();

                string query = "SELECT id, description FROM ra_evidence ORDER BY position";
                var result = await dbConnection.QueryAsync<Evidence>(query);
                return result ?? Enumerable.Empty<Evidence>();
            }
            catch (Exception ex)
            {
                throw new InvalidOperationException($"Failed to retrieve evidence. Error: {ex.Message}", ex);
            }
        }

        #endregion

        public async Task<IEnumerable<Affine.Engine.Model.Auditing.Department>> GetDepartmentsAsync()
        {
            try
            {
                using IDbConnection dbConnection = new NpgsqlConnection(_connectionString);
                dbConnection.Open();

                // Follow repository pattern: no schema prefixes (connection default schema handles it)
                const string query = @"SELECT id, name, head, risk_level_id AS RiskLevelId, assessments, created_at AS CreatedAt, updated_at AS UpdatedAt FROM departments ORDER BY name";

                var result = await dbConnection.QueryAsync<Affine.Engine.Model.Auditing.Department>(query);
                return result ?? Enumerable.Empty<Affine.Engine.Model.Auditing.Department>();
            }
            catch (Exception ex)
            {
                throw new InvalidOperationException($"Failed to retrieve departments. Error: {ex.Message}", ex);
            }
        }

        public async Task<IEnumerable<Affine.Engine.Model.Auditing.Project>> GetProjectsAsync()
        {
            try
            {
                using IDbConnection dbConnection = new NpgsqlConnection(_connectionString);
                dbConnection.Open();

                const string query = @"
                    SELECT 
                        id, 
                        name, 
                        description, 
                        status_id AS StatusId,
                        department_id AS DepartmentId,
                        start_date AS StartDate,
                        end_date AS EndDate,
                        budget,
                        risk_level_id AS RiskLevelId,
                        manager,
                        created_at AS CreatedAt, 
                        updated_at AS UpdatedAt 
                    FROM projects 
                    ORDER BY name";

                var result = await dbConnection.QueryAsync<Affine.Engine.Model.Auditing.Project>(query);
                return result ?? Enumerable.Empty<Affine.Engine.Model.Auditing.Project>();
            }
            catch (Exception ex)
            {
                throw new InvalidOperationException($"Failed to retrieve projects. Error: {ex.Message}", ex);
            }
        }

        public async Task<IEnumerable<object>> GetAssessmentsAsync()
        {
            try
            {
                using IDbConnection dbConnection = new NpgsqlConnection(_connectionString);
                dbConnection.Open();

                const string query = @"
                    SELECT 
                        ref.reference_id AS id,
                        ref.client AS title,
                        ref.assessor AS auditor,
                        ref.assessment_start_date AS assessment_date,
                        ref.approved_by,
                        COALESCE(AVG(COALESCE(ra.risklikelihoodid, 0) * COALESCE(ra.riskimpactid, 0)), 0) AS risk_score,
                        CASE 
                            WHEN COALESCE(AVG(COALESCE(ra.risklikelihoodid, 0) * COALESCE(ra.riskimpactid, 0)), 0) >= 16 THEN 'High'
                            WHEN COALESCE(AVG(COALESCE(ra.risklikelihoodid, 0) * COALESCE(ra.riskimpactid, 0)), 0) >= 8 THEN 'Medium'
                            ELSE 'Low'
                        END AS risk_level,
                        COUNT(ra.riskassessment_refid) AS total_assessments,
                        ref.created_date AS created_at,
                        ref.updated_at
                    FROM riskassessmentreference ref
                    LEFT JOIN riskassessment ra ON ref.reference_id = ra.reference_id
                    GROUP BY ref.reference_id, ref.client, ref.assessor, ref.assessment_start_date, 
                             ref.approved_by, ref.created_date, ref.updated_at
                    ORDER BY ref.assessment_start_date DESC";

                var result = await dbConnection.QueryAsync(query);
                return result ?? Enumerable.Empty<object>();
            }
            catch (Exception ex)
            {
                throw new InvalidOperationException($"Failed to retrieve assessments. Error: {ex.Message}", ex);
            }
        }

        public async Task<int> AddRiskAssessmentReferenceAsync(RiskAssessmentReferenceInput reference)
        {
            if (reference == null)
            {
                throw new ArgumentNullException(nameof(reference), "Risk assessment reference cannot be null.");
            }

            try
            {
                using IDbConnection dbConnection = new NpgsqlConnection(_connectionString);
                dbConnection.Open();

                string query = @"
                    INSERT INTO riskassessmentreference (
                        client, 
                        assessment_start_date, 
                        assessment_end_date, 
                        assessor, 
                        approved_by
                    ) VALUES (
                        @Client, 
                        @AssessmentStartDate, 
                        @AssessmentEndDate, 
                        @Assessor, 
                        @ApprovedBy
                    ) RETURNING reference_id";

                var referenceId = await dbConnection.ExecuteScalarAsync<int>(query, reference);
                return referenceId;
            }
            catch (Exception ex)
            {
                throw new InvalidOperationException($"Failed to add risk assessment reference. Error: {ex.Message}", ex);
            }
        }

        public async Task<bool> UpdateRiskAssessmentReferenceAsync(int referenceId, RiskAssessmentReferenceInput reference)
        {
            if (reference == null)
            {
                throw new ArgumentNullException(nameof(reference), "Risk assessment reference cannot be null.");
            }

            if (referenceId <= 0)
            {
                throw new ArgumentException("Reference ID must be greater than zero.", nameof(referenceId));
            }

            try
            {
                using IDbConnection dbConnection = new NpgsqlConnection(_connectionString);
                dbConnection.Open();

                string query = @"
                    UPDATE riskassessmentreference SET
                        client = @Client, 
                        assessment_start_date = @AssessmentStartDate, 
                        assessment_end_date = @AssessmentEndDate, 
                        assessor = @Assessor, 
                        approved_by = @ApprovedBy
                    WHERE reference_id = @ReferenceId";

                var parameters = new
                {
                    ReferenceId = referenceId,
                    reference.Client,
                    reference.AssessmentStartDate,
                    reference.AssessmentEndDate,
                    reference.Assessor,
                    reference.ApprovedBy
                };

                var rowsAffected = await dbConnection.ExecuteAsync(query, parameters);
                return rowsAffected > 0;
            }
            catch (Exception ex)
            {
                throw new InvalidOperationException($"Failed to update risk assessment reference. Error: {ex.Message}", ex);
            }
        }
    }
}
