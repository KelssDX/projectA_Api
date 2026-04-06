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
                        title AS Title,
                        description AS Description,
                        assessment_start_date as AssessmentStartDate,
                        assessment_end_date as AssessmentEndDate,
                        assessor as Assessor,
                        approved_by as ApprovedBy,
                        status_id AS StatusId,
                        rs.name AS StatusName,
                        COALESCE(is_archived, false) AS IsArchived,
                        (
                            COALESCE(is_archived, false)
                            OR COALESCE(NULLIF(TRIM(approved_by), ''), '') <> ''
                            OR LOWER(COALESCE(rs.name, '')) IN ('approved', 'archived', 'completed', 'cancelled')
                        ) AS IsLockedForEdit
                    FROM 
                        riskassessmentreference
                    LEFT JOIN ra_referencestatus rs ON riskassessmentreference.status_id = rs.id
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
                        ra.BusinessObjectiveDescription AS ProcessObjectivesAssessment_Description,
                        ra.KeyRiskAndFactors AS RisksAssessment_KeyRiskAndFactors,
                        ra.RiskDescription AS RisksAssessment_Description,
                        rl.description AS RisksAssessment_RiskLikelihood,
                        ri.description AS RisksAssessment_RiskImpact,
                        ks.description AS RisksAssessment_KeyOrSecondary,
                        rc.description AS RisksAssessment_RiskCategory,
                        ra.MitigatingControls AS ControlsAssessment_MitigatingControls,
                        ra.ControlDescription AS ControlsAssessment_Description,
                        ra.Responsibility AS ControlsAssessment_Responsibility,
                        df.description AS ControlsAssessment_DataFrequency,
                        f.description AS ControlsAssessment_Frequency,
                        ra.status_id AS StatusId,
                        ast.name AS StatusName,
                        e.description AS OutcomeAssessment_Evidence,
                        ra.Authoriser AS OutcomeAssessment_Authoriser,
                        ra.AuditorsRecommendedActionPlan AS OutcomeAssessment_AuditorsRecommendedActionPlan,
                        ra.OutcomeDescription AS OutcomeAssessment_Description,
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
                        ra_assessmentstatus ast ON ra.status_id = ast.id
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
                            await EnsureReferenceEditableAsync(dbConnection, refId, "add risk assessment items", transaction);
                        }
                        else if (reference != null)
                        {
                            // Reference doesn't exist but we have reference data, create a new one
                            var resolvedStatusId = await ResolveReferenceStatusIdAsync(
                                dbConnection,
                                reference.StatusId,
                                reference.StatusName,
                                transaction);

                            string insertRefQuery = @"
                                INSERT INTO riskassessmentreference (
                                    client, 
                                    assessment_start_date, 
                                    assessment_end_date, 
                                    assessor, 
                                    approved_by,
                                    department_id,
                                    project_id,
                                    title,
                                    description,
                                    status_id
                                ) VALUES (
                                    @Client, 
                                    @AssessmentStartDate, 
                                    @AssessmentEndDate, 
                                    @Assessor, 
                                    @ApprovedBy,
                                    @DepartmentId,
                                    @ProjectId,
                                    @Title,
                                    @Description,
                                    @StatusId
                                ) RETURNING reference_id";
                            
                            refId = await dbConnection.ExecuteScalarAsync<int>(insertRefQuery, new
                            {
                                reference.Client,
                                reference.AssessmentStartDate,
                                reference.AssessmentEndDate,
                                reference.Assessor,
                                reference.ApprovedBy,
                                reference.DepartmentId,
                                reference.ProjectId,
                                reference.Title,
                                reference.Description,
                                StatusId = resolvedStatusId
                            }, transaction);
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
                        var resolvedStatusId = await ResolveReferenceStatusIdAsync(
                            dbConnection,
                            reference.StatusId,
                            reference.StatusName,
                            transaction);

                        string insertRefQuery = @"
                            INSERT INTO riskassessmentreference (
                                client, 
                                assessment_start_date, 
                                assessment_end_date, 
                                assessor, 
                                approved_by,
                                department_id,
                                project_id,
                                title,
                                description,
                                status_id
                            ) VALUES (
                                @Client, 
                                @AssessmentStartDate, 
                                @AssessmentEndDate, 
                                @Assessor, 
                                @ApprovedBy,
                                @DepartmentId,
                                @ProjectId,
                                @Title,
                                @Description,
                                @StatusId
                            ) RETURNING reference_id";
                        
                        refId = await dbConnection.ExecuteScalarAsync<int>(insertRefQuery, new
                        {
                            reference.Client,
                            reference.AssessmentStartDate,
                            reference.AssessmentEndDate,
                            reference.Assessor,
                            reference.ApprovedBy,
                            reference.DepartmentId,
                            reference.ProjectId,
                            reference.Title,
                            reference.Description,
                            StatusId = resolvedStatusId
                        }, transaction);
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
                            BusinessObjectiveDescription,
                            KeyRiskAndFactors,
                            RiskDescription,
                            MitigatingControls,
                            ControlDescription,
                            Responsibility,
                            Authoriser,
                            AuditorsRecommendedActionPlan,
                            OutcomeDescription,
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
                            ImpactId,
                            StatusId
                        ) VALUES (
                            @ReferenceId,
                            @BusinessObjectives,
                            @MainProcess,
                            @SubProcess,
                            @BusinessObjectiveDescription,
                            @KeyRiskAndFactors,
                            @RiskDescription,
                            @MitigatingControls,
                            @ControlDescription,
                            @Responsibility,
                            @Authoriser,
                            @AuditorsRecommendedActionPlan,
                            @OutcomeDescription,
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
                            @ImpactId,
                            COALESCE(@StatusId, 1)
                        )";
                    
                    foreach (var request in requests)
                    {
                        var parameters = new
                        {
                            ReferenceId = refId,
                            request.BusinessObjectives,
                            request.MainProcess,
                            request.SubProcess,
                            request.BusinessObjectiveDescription,
                            request.KeyRiskAndFactors,
                            request.RiskDescription,
                            request.MitigatingControls,
                            request.ControlDescription,
                            request.Responsibility,
                            request.Authoriser,
                            request.AuditorsRecommendedActionPlan,
                            request.OutcomeDescription,
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
                            request.ImpactId,
                            request.StatusId
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

                    await EnsureReferenceEditableAsync(dbConnection, referenceId, "update risk assessment items", transaction);
                    
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
                        AddUpdateField(updateFields, parameters, "BusinessObjectiveDescription", update.BusinessObjectiveDescription);
                        AddUpdateField(updateFields, parameters, "KeyRiskAndFactors", update.KeyRiskAndFactors);
                        AddUpdateField(updateFields, parameters, "RiskDescription", update.RiskDescription);
                        AddUpdateField(updateFields, parameters, "MitigatingControls", update.MitigatingControls);
                        AddUpdateField(updateFields, parameters, "ControlDescription", update.ControlDescription);
                        AddUpdateField(updateFields, parameters, "Responsibility", update.Responsibility);
                        AddUpdateField(updateFields, parameters, "Authoriser", update.Authoriser);
                        AddUpdateField(updateFields, parameters, "AuditorsRecommendedActionPlan", update.AuditorsRecommendedActionPlan);
                        AddUpdateField(updateFields, parameters, "OutcomeDescription", update.OutcomeDescription);
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
                        AddUpdateField(updateFields, parameters, "StatusId", update.StatusId);
                        
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

        private sealed class ReferenceEditState
        {
            public int ReferenceId { get; set; }
            public string ApprovedBy { get; set; }
            public string StatusName { get; set; }
            public bool IsArchived { get; set; }
        }

        private async Task<ReferenceEditState> GetReferenceEditStateAsync(IDbConnection dbConnection, int referenceId, IDbTransaction transaction = null)
        {
            const string query = @"
                SELECT
                    ref.reference_id AS ReferenceId,
                    ref.approved_by AS ApprovedBy,
                    rs.name AS StatusName,
                    COALESCE(ref.is_archived, false) AS IsArchived
                FROM riskassessmentreference ref
                LEFT JOIN ra_referencestatus rs ON ref.status_id = rs.id
                WHERE ref.reference_id = @ReferenceId";

            return await dbConnection.QueryFirstOrDefaultAsync<ReferenceEditState>(
                query,
                new { ReferenceId = referenceId },
                transaction);
        }

        private static bool IsReferenceLockedForEdit(ReferenceEditState state)
        {
            if (state == null)
            {
                return false;
            }

            if (state.IsArchived)
            {
                return true;
            }

            if (!string.IsNullOrWhiteSpace(state.ApprovedBy))
            {
                return true;
            }

            var normalizedStatus = (state.StatusName ?? string.Empty).Trim().ToLowerInvariant();
            return normalizedStatus is "approved" or "archived" or "completed" or "cancelled";
        }

        private async Task EnsureReferenceEditableAsync(IDbConnection dbConnection, int referenceId, string actionLabel, IDbTransaction transaction = null)
        {
            var state = await GetReferenceEditStateAsync(dbConnection, referenceId, transaction);
            if (state == null)
            {
                return;
            }

            if (IsReferenceLockedForEdit(state))
            {
                throw new InvalidOperationException($"Audit file {referenceId} is locked for edits and cannot be used to {actionLabel}.");
            }
        }

        private async Task<int?> ResolveReferenceStatusIdAsync(
            IDbConnection dbConnection,
            int? requestedStatusId,
            string requestedStatusName,
            IDbTransaction transaction = null)
        {
            if (requestedStatusId.HasValue && requestedStatusId.Value > 0)
            {
                return requestedStatusId.Value;
            }

            string[] candidateNames = string.IsNullOrWhiteSpace(requestedStatusName)
                ? new[] { "Draft", "Reference is currently active" }
                : new[] { requestedStatusName.Trim() };

            foreach (var candidate in candidateNames)
            {
                const string query = @"
                    SELECT id
                    FROM ra_referencestatus
                    WHERE LOWER(name) = LOWER(@Name)
                    LIMIT 1;";

                var resolved = await dbConnection.ExecuteScalarAsync<int?>(query, new { Name = candidate }, transaction);
                if (resolved.HasValue && resolved.Value > 0)
                {
                    return resolved.Value;
                }
            }

            return requestedStatusId;
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

                await EnsureReferenceEditableAsync(dbConnection, referenceId, "delete risk assessment items");

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
                        (
                            SELECT COUNT(*)
                            FROM audit_project_collaborators apc
                            WHERE apc.project_id = projects.id
                        ) AS CollaboratorCount,
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

        public async Task<List<Affine.Engine.Model.Auditing.AuditCollaboratorRoleOption>> GetCollaboratorRolesAsync()
        {
            try
            {
                using IDbConnection dbConnection = new NpgsqlConnection(_connectionString);
                dbConnection.Open();

                const string query = @"
                    SELECT
                        id AS Id,
                        name AS Name,
                        description AS Description,
                        color AS Color,
                        is_client_role AS IsClientRole,
                        sort_order AS SortOrder,
                        is_active AS IsActive
                    FROM ra_audit_collaborator_role
                    WHERE is_active = true
                    ORDER BY sort_order, name;";

                var result = await dbConnection.QueryAsync<Affine.Engine.Model.Auditing.AuditCollaboratorRoleOption>(query);
                return result.ToList();
            }
            catch (Exception ex)
            {
                throw new InvalidOperationException($"Failed to retrieve collaborator roles. Error: {ex.Message}", ex);
            }
        }

        public async Task<List<Affine.Engine.Model.Auditing.AuditCollaboratorAssignment>> GetProjectCollaboratorsAsync(int projectId)
        {
            if (projectId <= 0)
                throw new ArgumentException("Project ID must be greater than zero.", nameof(projectId));

            try
            {
                using IDbConnection dbConnection = new NpgsqlConnection(_connectionString);
                dbConnection.Open();
                return await GetProjectCollaboratorsInternalAsync(dbConnection, projectId);
            }
            catch (Exception ex)
            {
                throw new InvalidOperationException($"Failed to retrieve project collaborators. Error: {ex.Message}", ex);
            }
        }

        public async Task<List<Affine.Engine.Model.Auditing.AuditCollaboratorAssignment>> SaveProjectCollaboratorsAsync(
            int projectId,
            Affine.Engine.Model.Auditing.SaveAuditCollaboratorsRequest request,
            int? assignedByUserId,
            string assignedByName)
        {
            if (projectId <= 0)
                throw new ArgumentException("Project ID must be greater than zero.", nameof(projectId));

            try
            {
                await using var dbConnection = new NpgsqlConnection(_connectionString);
                await dbConnection.OpenAsync();
                await using var transaction = await dbConnection.BeginTransactionAsync();

                await dbConnection.ExecuteAsync(
                    "DELETE FROM audit_project_collaborators WHERE project_id = @ProjectId;",
                    new { ProjectId = projectId },
                    transaction);

                const string insertQuery = @"
                    INSERT INTO audit_project_collaborators
                    (
                        project_id,
                        user_id,
                        collaborator_role_id,
                        can_edit,
                        can_review,
                        can_upload_evidence,
                        can_manage_access,
                        notes,
                        assigned_by_user_id,
                        assigned_by_name
                    )
                    VALUES
                    (
                        @ProjectId,
                        @UserId,
                        @CollaboratorRoleId,
                        @CanEdit,
                        @CanReview,
                        @CanUploadEvidence,
                        @CanManageAccess,
                        @Notes,
                        @AssignedByUserId,
                        @AssignedByName
                    );";

                foreach (var collaborator in (request?.Collaborators ?? new List<Affine.Engine.Model.Auditing.AuditCollaboratorAssignmentInput>())
                    .Where(item => item != null && item.UserId > 0)
                    .GroupBy(item => item.UserId)
                    .Select(group => group.First()))
                {
                    await dbConnection.ExecuteAsync(insertQuery, new
                    {
                        ProjectId = projectId,
                        collaborator.UserId,
                        collaborator.CollaboratorRoleId,
                        collaborator.CanEdit,
                        collaborator.CanReview,
                        collaborator.CanUploadEvidence,
                        collaborator.CanManageAccess,
                        collaborator.Notes,
                        AssignedByUserId = assignedByUserId,
                        AssignedByName = assignedByName
                    }, transaction);
                }

                await transaction.CommitAsync();
                return await GetProjectCollaboratorsAsync(projectId);
            }
            catch (Exception ex)
            {
                throw new InvalidOperationException($"Failed to save project collaborators. Error: {ex.Message}", ex);
            }
        }

        public async Task<List<Affine.Engine.Model.Auditing.AuditCollaboratorAssignment>> GetReferenceCollaboratorsAsync(int referenceId)
        {
            if (referenceId <= 0)
                throw new ArgumentException("Reference ID must be greater than zero.", nameof(referenceId));

            try
            {
                using IDbConnection dbConnection = new NpgsqlConnection(_connectionString);
                dbConnection.Open();
                return await GetReferenceCollaboratorsInternalAsync(dbConnection, referenceId);
            }
            catch (Exception ex)
            {
                throw new InvalidOperationException($"Failed to retrieve audit file collaborators. Error: {ex.Message}", ex);
            }
        }

        public async Task<List<Affine.Engine.Model.Auditing.AuditCollaboratorAssignment>> SaveReferenceCollaboratorsAsync(
            int referenceId,
            Affine.Engine.Model.Auditing.SaveAuditCollaboratorsRequest request,
            int? assignedByUserId,
            string assignedByName)
        {
            if (referenceId <= 0)
                throw new ArgumentException("Reference ID must be greater than zero.", nameof(referenceId));

            try
            {
                await using var dbConnection = new NpgsqlConnection(_connectionString);
                await dbConnection.OpenAsync();
                await using var transaction = await dbConnection.BeginTransactionAsync();

                await dbConnection.ExecuteAsync(
                    "DELETE FROM audit_reference_collaborators WHERE reference_id = @ReferenceId;",
                    new { ReferenceId = referenceId },
                    transaction);

                const string insertQuery = @"
                    INSERT INTO audit_reference_collaborators
                    (
                        reference_id,
                        user_id,
                        collaborator_role_id,
                        can_edit,
                        can_review,
                        can_upload_evidence,
                        can_manage_access,
                        notes,
                        assigned_by_user_id,
                        assigned_by_name
                    )
                    VALUES
                    (
                        @ReferenceId,
                        @UserId,
                        @CollaboratorRoleId,
                        @CanEdit,
                        @CanReview,
                        @CanUploadEvidence,
                        @CanManageAccess,
                        @Notes,
                        @AssignedByUserId,
                        @AssignedByName
                    );";

                foreach (var collaborator in (request?.Collaborators ?? new List<Affine.Engine.Model.Auditing.AuditCollaboratorAssignmentInput>())
                    .Where(item => item != null && item.UserId > 0)
                    .GroupBy(item => item.UserId)
                    .Select(group => group.First()))
                {
                    await dbConnection.ExecuteAsync(insertQuery, new
                    {
                        ReferenceId = referenceId,
                        collaborator.UserId,
                        collaborator.CollaboratorRoleId,
                        collaborator.CanEdit,
                        collaborator.CanReview,
                        collaborator.CanUploadEvidence,
                        collaborator.CanManageAccess,
                        collaborator.Notes,
                        AssignedByUserId = assignedByUserId,
                        AssignedByName = assignedByName
                    }, transaction);
                }

                await transaction.CommitAsync();
                return await GetReferenceCollaboratorsAsync(referenceId);
            }
            catch (Exception ex)
            {
                throw new InvalidOperationException($"Failed to save audit file collaborators. Error: {ex.Message}", ex);
            }
        }

        public async Task<Affine.Engine.Model.Auditing.Department> CreateDepartmentAsync(Affine.Engine.Model.Auditing.Department department)
        {
            if (department == null)
                throw new ArgumentNullException(nameof(department));

            try
            {
                using IDbConnection dbConnection = new NpgsqlConnection(_connectionString);
                dbConnection.Open();

                const string query = @"
                    INSERT INTO departments (name, head, risk_level_id, assessments, created_at, updated_at)
                    VALUES (@Name, @Head, @RiskLevelId, COALESCE(@Assessments, 0), NOW(), NOW())
                    RETURNING 
                        id, 
                        name, 
                        head, 
                        risk_level_id AS RiskLevelId, 
                        assessments, 
                        created_at AS CreatedAt, 
                        updated_at AS UpdatedAt;";

                var created = await dbConnection.QueryFirstOrDefaultAsync<Affine.Engine.Model.Auditing.Department>(query, department);
                return created;
            }
            catch (Exception ex)
            {
                throw new InvalidOperationException($"Failed to create department. Error: {ex.Message}", ex);
            }
        }

        public async Task<Affine.Engine.Model.Auditing.Department> UpdateDepartmentAsync(Affine.Engine.Model.Auditing.Department department)
        {
            if (department == null)
                throw new ArgumentNullException(nameof(department));

            if (department.Id <= 0)
                throw new ArgumentException("Department ID must be greater than zero.", nameof(department.Id));

            try
            {
                using IDbConnection dbConnection = new NpgsqlConnection(_connectionString);
                dbConnection.Open();

                const string query = @"
                    UPDATE departments
                    SET 
                        name = @Name,
                        head = @Head,
                        risk_level_id = @RiskLevelId,
                        updated_at = NOW()
                    WHERE id = @Id
                    RETURNING 
                        id, 
                        name, 
                        head, 
                        risk_level_id AS RiskLevelId, 
                        assessments, 
                        created_at AS CreatedAt, 
                        updated_at AS UpdatedAt;";

                var updated = await dbConnection.QueryFirstOrDefaultAsync<Affine.Engine.Model.Auditing.Department>(query, department);
                return updated;
            }
            catch (Exception ex)
            {
                throw new InvalidOperationException($"Failed to update department. Error: {ex.Message}", ex);
            }
        }

        public async Task<bool> DeleteDepartmentAsync(int departmentId)
        {
            if (departmentId <= 0)
                throw new ArgumentException("Department ID must be greater than zero.", nameof(departmentId));

            try
            {
                using IDbConnection dbConnection = new NpgsqlConnection(_connectionString);
                dbConnection.Open();

                const string query = @"DELETE FROM departments WHERE id = @Id;";
                var affected = await dbConnection.ExecuteAsync(query, new { Id = departmentId });
                return affected > 0;
            }
            catch (Exception ex)
            {
                throw new InvalidOperationException($"Failed to delete department. Error: {ex.Message}", ex);
            }
        }

        public async Task<Affine.Engine.Model.Auditing.Project> CreateProjectAsync(Affine.Engine.Model.Auditing.Project project)
        {
            if (project == null)
                throw new ArgumentNullException(nameof(project));

            try
            {
                using IDbConnection dbConnection = new NpgsqlConnection(_connectionString);
                dbConnection.Open();

                const string query = @"
                    INSERT INTO projects (
                        name,
                        description,
                        status_id,
                        department_id,
                        start_date,
                        end_date,
                        budget,
                        risk_level_id,
                        manager,
                        created_at,
                        updated_at
                    )
                    VALUES (
                        @Name,
                        @Description,
                        @StatusId,
                        @DepartmentId,
                        @StartDate,
                        @EndDate,
                        @Budget,
                        @RiskLevelId,
                        @Manager,
                        NOW(),
                        NOW()
                    )
                    RETURNING
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
                        0 AS CollaboratorCount,
                        created_at AS CreatedAt,
                        updated_at AS UpdatedAt;";

                var created = await dbConnection.QueryFirstOrDefaultAsync<Affine.Engine.Model.Auditing.Project>(query, project);
                return created;
            }
            catch (Exception ex)
            {
                throw new InvalidOperationException($"Failed to create project. Error: {ex.Message}", ex);
            }
        }

        public async Task<Affine.Engine.Model.Auditing.Project> UpdateProjectAsync(Affine.Engine.Model.Auditing.Project project)
        {
            if (project == null)
                throw new ArgumentNullException(nameof(project));

            if (project.Id <= 0)
                throw new ArgumentException("Project ID must be greater than zero.", nameof(project.Id));

            try
            {
                using IDbConnection dbConnection = new NpgsqlConnection(_connectionString);
                dbConnection.Open();

                const string query = @"
                    UPDATE projects
                    SET
                        name = @Name,
                        description = @Description,
                        status_id = @StatusId,
                        department_id = @DepartmentId,
                        start_date = @StartDate,
                        end_date = @EndDate,
                        budget = @Budget,
                        risk_level_id = @RiskLevelId,
                        manager = @Manager,
                        updated_at = NOW()
                    WHERE id = @Id
                    RETURNING
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
                        (
                            SELECT COUNT(*)
                            FROM audit_project_collaborators apc
                            WHERE apc.project_id = projects.id
                        ) AS CollaboratorCount,
                        created_at AS CreatedAt,
                        updated_at AS UpdatedAt;";

                var updated = await dbConnection.QueryFirstOrDefaultAsync<Affine.Engine.Model.Auditing.Project>(query, project);
                return updated;
            }
            catch (Exception ex)
            {
                throw new InvalidOperationException($"Failed to update project. Error: {ex.Message}", ex);
            }
        }

        public async Task<bool> DeleteProjectAsync(int projectId)
        {
            if (projectId <= 0)
                throw new ArgumentException("Project ID must be greater than zero.", nameof(projectId));

            try
            {
                using IDbConnection dbConnection = new NpgsqlConnection(_connectionString);
                dbConnection.Open();

                const string query = @"DELETE FROM projects WHERE id = @Id;";
                var affected = await dbConnection.ExecuteAsync(query, new { Id = projectId });
                return affected > 0;
            }
            catch (Exception ex)
            {
                throw new InvalidOperationException($"Failed to delete project. Error: {ex.Message}", ex);
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
                        COALESCE(NULLIF(ref.title, ''), ref.client) AS title,
                        ref.department_id,
                        dept.name AS department,
                        ref.project_id,
                        proj.name AS project,
                        ref.assessor AS auditor,
                        ref.assessment_start_date AS assessment_date,
                        ref.approved_by,
                        plan.engagement_type_id,
                        et.name AS engagement_type_name,
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
                    LEFT JOIN departments dept ON ref.department_id = dept.id
                    LEFT JOIN projects proj ON ref.project_id = proj.id
                    LEFT JOIN audit_engagement_plans plan ON ref.reference_id = plan.reference_id
                    LEFT JOIN ra_engagement_type et ON plan.engagement_type_id = et.id
                    LEFT JOIN riskassessment ra ON ref.reference_id = ra.reference_id
                    WHERE COALESCE(ref.is_archived, false) = false
                    GROUP BY ref.reference_id, ref.client, ref.title, ref.department_id, dept.name,
                             ref.project_id, proj.name, ref.assessor, ref.assessment_start_date,
                             ref.approved_by, plan.engagement_type_id, et.name, ref.created_date, ref.updated_at
                    ORDER BY ref.assessment_start_date DESC";

                var queryResult = await dbConnection.QueryAsync(query);
                var resultList = queryResult.ToList();
                Console.WriteLine($"DEBUG: [RiskAssessmentRepository] GetAssessmentsAsync found {resultList.Count} assessments.");
                return resultList ?? Enumerable.Empty<object>();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"DEBUG: [RiskAssessmentRepository] GetAssessmentsAsync ERROR: {ex.Message}");
                throw new InvalidOperationException($"Failed to retrieve assessments. Error: {ex.Message}", ex);
            }
        }

        private async Task<List<Affine.Engine.Model.Auditing.AuditCollaboratorAssignment>> GetProjectCollaboratorsInternalAsync(IDbConnection dbConnection, int projectId)
        {
            const string query = @"
                SELECT
                    apc.id AS Id,
                    apc.project_id AS ProjectId,
                    NULL::INTEGER AS ReferenceId,
                    apc.user_id AS UserId,
                    COALESCE(NULLIF(uv.name, ''), NULLIF(uv.username, ''), 'User ' || apc.user_id::text) AS UserName,
                    uv.email AS UserEmail,
                    uv.role AS UserSystemRole,
                    apc.collaborator_role_id AS CollaboratorRoleId,
                    role.name AS CollaboratorRoleName,
                    role.color AS CollaboratorRoleColor,
                    apc.can_edit AS CanEdit,
                    apc.can_review AS CanReview,
                    apc.can_upload_evidence AS CanUploadEvidence,
                    apc.can_manage_access AS CanManageAccess,
                    apc.notes AS Notes,
                    apc.assigned_by_user_id AS AssignedByUserId,
                    COALESCE(NULLIF(apc.assigned_by_name, ''), NULLIF(assigner.name, ''), assigner.username) AS AssignedByName,
                    apc.created_at AS CreatedAt,
                    apc.updated_at AS UpdatedAt,
                    false AS IsInheritedFromProject
                FROM audit_project_collaborators apc
                LEFT JOIN user_view uv ON apc.user_id = uv.id
                LEFT JOIN ra_audit_collaborator_role role ON apc.collaborator_role_id = role.id
                LEFT JOIN user_view assigner ON apc.assigned_by_user_id = assigner.id
                WHERE apc.project_id = @ProjectId
                ORDER BY COALESCE(role.sort_order, 999), COALESCE(NULLIF(uv.name, ''), NULLIF(uv.username, ''), apc.user_id::text);";

            var result = await dbConnection.QueryAsync<Affine.Engine.Model.Auditing.AuditCollaboratorAssignment>(query, new { ProjectId = projectId });
            return result.ToList();
        }

        private async Task<List<Affine.Engine.Model.Auditing.AuditCollaboratorAssignment>> GetReferenceCollaboratorsInternalAsync(IDbConnection dbConnection, int referenceId)
        {
            const string query = @"
                WITH reference_info AS (
                    SELECT reference_id, project_id
                    FROM riskassessmentreference
                    WHERE reference_id = @ReferenceId
                ),
                explicit_assignments AS (
                    SELECT
                        arc.id AS Id,
                        ri.project_id AS ProjectId,
                        arc.reference_id AS ReferenceId,
                        arc.user_id AS UserId,
                        COALESCE(NULLIF(uv.name, ''), NULLIF(uv.username, ''), 'User ' || arc.user_id::text) AS UserName,
                        uv.email AS UserEmail,
                        uv.role AS UserSystemRole,
                        arc.collaborator_role_id AS CollaboratorRoleId,
                        role.name AS CollaboratorRoleName,
                        role.color AS CollaboratorRoleColor,
                        arc.can_edit AS CanEdit,
                        arc.can_review AS CanReview,
                        arc.can_upload_evidence AS CanUploadEvidence,
                        arc.can_manage_access AS CanManageAccess,
                        arc.notes AS Notes,
                        arc.assigned_by_user_id AS AssignedByUserId,
                        COALESCE(NULLIF(arc.assigned_by_name, ''), NULLIF(assigner.name, ''), assigner.username) AS AssignedByName,
                        arc.created_at AS CreatedAt,
                        arc.updated_at AS UpdatedAt,
                        false AS IsInheritedFromProject,
                        COALESCE(role.sort_order, 999) AS RoleSortOrder
                    FROM audit_reference_collaborators arc
                    INNER JOIN reference_info ri ON ri.reference_id = arc.reference_id
                    LEFT JOIN user_view uv ON arc.user_id = uv.id
                    LEFT JOIN ra_audit_collaborator_role role ON arc.collaborator_role_id = role.id
                    LEFT JOIN user_view assigner ON arc.assigned_by_user_id = assigner.id
                ),
                inherited_project_assignments AS (
                    SELECT
                        NULL::INTEGER AS Id,
                        ri.project_id AS ProjectId,
                        ri.reference_id AS ReferenceId,
                        apc.user_id AS UserId,
                        COALESCE(NULLIF(uv.name, ''), NULLIF(uv.username, ''), 'User ' || apc.user_id::text) AS UserName,
                        uv.email AS UserEmail,
                        uv.role AS UserSystemRole,
                        apc.collaborator_role_id AS CollaboratorRoleId,
                        role.name AS CollaboratorRoleName,
                        role.color AS CollaboratorRoleColor,
                        apc.can_edit AS CanEdit,
                        apc.can_review AS CanReview,
                        apc.can_upload_evidence AS CanUploadEvidence,
                        apc.can_manage_access AS CanManageAccess,
                        apc.notes AS Notes,
                        apc.assigned_by_user_id AS AssignedByUserId,
                        COALESCE(NULLIF(apc.assigned_by_name, ''), NULLIF(assigner.name, ''), assigner.username) AS AssignedByName,
                        apc.created_at AS CreatedAt,
                        apc.updated_at AS UpdatedAt,
                        true AS IsInheritedFromProject,
                        COALESCE(role.sort_order, 999) AS RoleSortOrder
                    FROM reference_info ri
                    INNER JOIN audit_project_collaborators apc ON apc.project_id = ri.project_id
                    LEFT JOIN audit_reference_collaborators arc ON arc.reference_id = ri.reference_id AND arc.user_id = apc.user_id
                    LEFT JOIN user_view uv ON apc.user_id = uv.id
                    LEFT JOIN ra_audit_collaborator_role role ON apc.collaborator_role_id = role.id
                    LEFT JOIN user_view assigner ON apc.assigned_by_user_id = assigner.id
                    WHERE ri.project_id IS NOT NULL
                      AND arc.id IS NULL
                )
                SELECT
                    combined.Id,
                    combined.ProjectId,
                    combined.ReferenceId,
                    combined.UserId,
                    combined.UserName,
                    combined.UserEmail,
                    combined.UserSystemRole,
                    combined.CollaboratorRoleId,
                    combined.CollaboratorRoleName,
                    combined.CollaboratorRoleColor,
                    combined.CanEdit,
                    combined.CanReview,
                    combined.CanUploadEvidence,
                    combined.CanManageAccess,
                    combined.Notes,
                    combined.AssignedByUserId,
                    combined.AssignedByName,
                    combined.CreatedAt,
                    combined.UpdatedAt,
                    combined.IsInheritedFromProject
                FROM (
                    SELECT * FROM explicit_assignments
                    UNION ALL
                    SELECT * FROM inherited_project_assignments
                ) combined
                ORDER BY combined.IsInheritedFromProject, combined.RoleSortOrder, combined.UserName;";

            var result = await dbConnection.QueryAsync<Affine.Engine.Model.Auditing.AuditCollaboratorAssignment>(query, new { ReferenceId = referenceId });
            return result.ToList();
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

                var resolvedStatusId = await ResolveReferenceStatusIdAsync(
                    dbConnection,
                    reference.StatusId,
                    reference.StatusName);

                string query = @"
                    INSERT INTO riskassessmentreference (
                        client, 
                        assessment_start_date, 
                        assessment_end_date, 
                        assessor, 
                        approved_by,
                        department_id,
                        project_id,
                        title,
                        description,
                        status_id
                    ) VALUES (
                        @Client, 
                        @AssessmentStartDate, 
                        @AssessmentEndDate, 
                        @Assessor, 
                        @ApprovedBy,
                        @DepartmentId,
                        @ProjectId,
                        @Title,
                        @Description,
                        COALESCE(@StatusId, 1)
                    ) RETURNING reference_id";

                var referenceId = await dbConnection.ExecuteScalarAsync<int>(query, new
                {
                    reference.Client,
                    reference.AssessmentStartDate,
                    reference.AssessmentEndDate,
                    reference.Assessor,
                    reference.ApprovedBy,
                    reference.DepartmentId,
                    reference.ProjectId,
                    reference.Title,
                    reference.Description,
                    StatusId = resolvedStatusId
                });
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

                await EnsureReferenceEditableAsync(dbConnection, referenceId, "update audit file header");
                var resolvedStatusId = await ResolveReferenceStatusIdAsync(
                    dbConnection,
                    reference.StatusId,
                    reference.StatusName);

                string query = @"
                    UPDATE riskassessmentreference SET
                        client = @Client, 
                        assessment_start_date = @AssessmentStartDate, 
                        assessment_end_date = @AssessmentEndDate, 
                        assessor = @Assessor, 
                        approved_by = @ApprovedBy,
                        department_id = @DepartmentId,
                        project_id = @ProjectId,
                        title = @Title,
                        description = @Description,
                        status_id = COALESCE(@StatusId, status_id),
                        updated_at = NOW()
                    WHERE reference_id = @ReferenceId";

                var parameters = new
                {
                    ReferenceId = referenceId,
                    reference.Client,
                    reference.AssessmentStartDate,
                    reference.AssessmentEndDate,
                    reference.Assessor,
                    reference.ApprovedBy,
                    reference.DepartmentId,
                    reference.ProjectId,
                    reference.Title,
                    reference.Description,
                    StatusId = resolvedStatusId
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
