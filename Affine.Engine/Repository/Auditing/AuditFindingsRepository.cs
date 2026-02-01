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
    public class AuditFindingsRepository : IAuditFindingsRepository
    {
        private readonly string _connectionString;

        public AuditFindingsRepository(string connectionString)
        {
            _connectionString = connectionString ?? throw new ArgumentNullException(nameof(connectionString));
        }

        #region Findings CRUD

        public async Task<AuditFinding> GetFindingAsync(int id)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();

                var query = @"
                    SELECT
                        f.id AS Id,
                        f.reference_id AS ReferenceId,
                        f.audit_universe_id AS AuditUniverseId,
                        f.finding_number AS FindingNumber,
                        f.finding_title AS FindingTitle,
                        f.finding_description AS FindingDescription,
                        f.severity_id AS SeverityId,
                        f.status_id AS StatusId,
                        f.identified_date AS IdentifiedDate,
                        f.due_date AS DueDate,
                        f.closed_date AS ClosedDate,
                        f.assigned_to AS AssignedTo,
                        f.assigned_to_user_id AS AssignedToUserId,
                        f.root_cause AS RootCause,
                        f.business_impact AS BusinessImpact,
                        f.created_by_user_id AS CreatedByUserId,
                        f.created_at AS CreatedAt,
                        f.updated_at AS UpdatedAt,
                        s.name AS SeverityName,
                        s.color AS SeverityColor,
                        st.name AS StatusName,
                        st.color AS StatusColor,
                        au.name AS AuditUniverseName,
                        EXTRACT(DAY FROM (CURRENT_DATE - f.identified_date))::int AS DaysOpen,
                        CASE WHEN f.due_date < CURRENT_DATE AND st.is_closed = false
                             THEN EXTRACT(DAY FROM (CURRENT_DATE - f.due_date))::int
                             ELSE NULL END AS DaysOverdue,
                        (f.due_date < CURRENT_DATE AND st.is_closed = false) AS IsOverdue,
                        (SELECT COUNT(*) FROM audit_recommendations r WHERE r.finding_id = f.id) AS RecommendationCount
                    FROM audit_findings f
                    LEFT JOIN ra_finding_severity s ON f.severity_id = s.id
                    LEFT JOIN ra_finding_status st ON f.status_id = st.id
                    LEFT JOIN audit_universe au ON f.audit_universe_id = au.id
                    WHERE f.id = @Id";

                var finding = await db.QueryFirstOrDefaultAsync<AuditFinding>(query, new { Id = id });

                if (finding != null)
                {
                    // Get recommendations
                    finding.Recommendations = await GetRecommendationsByFindingAsync(id);
                }

                return finding;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in GetFindingAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<List<AuditFinding>> GetFindingsByReferenceAsync(int referenceId)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();

                var query = @"
                    SELECT
                        f.id AS Id,
                        f.finding_number AS FindingNumber,
                        f.finding_title AS FindingTitle,
                        f.severity_id AS SeverityId,
                        f.status_id AS StatusId,
                        f.identified_date AS IdentifiedDate,
                        f.due_date AS DueDate,
                        s.name AS SeverityName,
                        s.color AS SeverityColor,
                        st.name AS StatusName,
                        st.color AS StatusColor,
                        EXTRACT(DAY FROM (CURRENT_DATE - f.identified_date))::int AS DaysOpen,
                        (f.due_date < CURRENT_DATE AND st.is_closed = false) AS IsOverdue
                    FROM audit_findings f
                    LEFT JOIN ra_finding_severity s ON f.severity_id = s.id
                    LEFT JOIN ra_finding_status st ON f.status_id = st.id
                    WHERE f.reference_id = @ReferenceId
                    ORDER BY s.sort_order, f.identified_date DESC";

                var result = await db.QueryAsync<AuditFinding>(query, new { ReferenceId = referenceId });
                return result.ToList();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in GetFindingsByReferenceAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<List<AuditFinding>> GetFindingsByUniverseNodeAsync(int auditUniverseId)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();

                var query = @"
                    SELECT
                        f.id AS Id,
                        f.finding_number AS FindingNumber,
                        f.finding_title AS FindingTitle,
                        f.severity_id AS SeverityId,
                        f.status_id AS StatusId,
                        f.identified_date AS IdentifiedDate,
                        f.due_date AS DueDate,
                        s.name AS SeverityName,
                        s.color AS SeverityColor,
                        st.name AS StatusName,
                        st.color AS StatusColor,
                        EXTRACT(DAY FROM (CURRENT_DATE - f.identified_date))::int AS DaysOpen,
                        (f.due_date < CURRENT_DATE AND st.is_closed = false) AS IsOverdue
                    FROM audit_findings f
                    LEFT JOIN ra_finding_severity s ON f.severity_id = s.id
                    LEFT JOIN ra_finding_status st ON f.status_id = st.id
                    WHERE f.audit_universe_id = @AuditUniverseId
                    ORDER BY s.sort_order, f.identified_date DESC";

                var result = await db.QueryAsync<AuditFinding>(query, new { AuditUniverseId = auditUniverseId });
                return result.ToList();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in GetFindingsByUniverseNodeAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<PaginatedResponse<FindingListItem>> GetFindingsAsync(FindingsFilterRequest filter)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();

                var whereClause = "WHERE 1=1";
                var parameters = new DynamicParameters();

                if (filter.ReferenceId.HasValue)
                {
                    whereClause += " AND f.reference_id = @ReferenceId";
                    parameters.Add("ReferenceId", filter.ReferenceId.Value);
                }
                if (filter.AuditUniverseId.HasValue)
                {
                    whereClause += " AND f.audit_universe_id = @AuditUniverseId";
                    parameters.Add("AuditUniverseId", filter.AuditUniverseId.Value);
                }
                if (filter.SeverityIds?.Any() == true)
                {
                    whereClause += " AND f.severity_id = ANY(@SeverityIds)";
                    parameters.Add("SeverityIds", filter.SeverityIds.ToArray());
                }
                if (filter.StatusIds?.Any() == true)
                {
                    whereClause += " AND f.status_id = ANY(@StatusIds)";
                    parameters.Add("StatusIds", filter.StatusIds.ToArray());
                }
                if (filter.OverdueOnly == true)
                {
                    whereClause += " AND f.due_date < CURRENT_DATE AND st.is_closed = false";
                }
                if (!string.IsNullOrEmpty(filter.SearchText))
                {
                    whereClause += " AND (LOWER(f.finding_title) LIKE LOWER(@Search) OR LOWER(f.finding_number) LIKE LOWER(@Search))";
                    parameters.Add("Search", $"%{filter.SearchText}%");
                }

                // Count query
                var countQuery = $@"
                    SELECT COUNT(*)
                    FROM audit_findings f
                    LEFT JOIN ra_finding_status st ON f.status_id = st.id
                    {whereClause}";

                var totalCount = await db.ExecuteScalarAsync<int>(countQuery, parameters);

                // Data query
                var offset = (filter.PageNumber - 1) * filter.PageSize;
                var orderBy = filter.SortDescending ? "DESC" : "ASC";

                var dataQuery = $@"
                    SELECT
                        f.id AS Id,
                        f.finding_number AS FindingNumber,
                        f.finding_title AS FindingTitle,
                        s.name AS Severity,
                        s.color AS SeverityColor,
                        st.name AS Status,
                        st.color AS StatusColor,
                        f.identified_date AS IdentifiedDate,
                        f.due_date AS DueDate,
                        f.assigned_to AS AssignedTo,
                        EXTRACT(DAY FROM (CURRENT_DATE - f.identified_date))::int AS DaysOpen,
                        (f.due_date < CURRENT_DATE AND st.is_closed = false) AS IsOverdue
                    FROM audit_findings f
                    LEFT JOIN ra_finding_severity s ON f.severity_id = s.id
                    LEFT JOIN ra_finding_status st ON f.status_id = st.id
                    {whereClause}
                    ORDER BY f.identified_date {orderBy}
                    OFFSET @Offset LIMIT @Limit";

                parameters.Add("Offset", offset);
                parameters.Add("Limit", filter.PageSize);

                var items = await db.QueryAsync<FindingListItem>(dataQuery, parameters);

                var totalPages = (int)Math.Ceiling((double)totalCount / filter.PageSize);

                return new PaginatedResponse<FindingListItem>
                {
                    Items = items.ToList(),
                    TotalCount = totalCount,
                    PageNumber = filter.PageNumber,
                    PageSize = filter.PageSize,
                    TotalPages = totalPages,
                    HasNextPage = filter.PageNumber < totalPages,
                    HasPreviousPage = filter.PageNumber > 1
                };
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in GetFindingsAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<AuditFinding> CreateFindingAsync(CreateAuditFindingRequest request)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();

                var query = @"
                    INSERT INTO audit_findings
                        (reference_id, audit_universe_id, finding_title, finding_description,
                         severity_id, due_date, assigned_to, assigned_to_user_id,
                         root_cause, business_impact, created_by_user_id)
                    VALUES
                        (@ReferenceId, @AuditUniverseId, @FindingTitle, @FindingDescription,
                         @SeverityId, @DueDate, @AssignedTo, @AssignedToUserId,
                         @RootCause, @BusinessImpact, @CreatedByUserId)
                    RETURNING id";

                var newId = await db.ExecuteScalarAsync<int>(query, request);
                return await GetFindingAsync(newId);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in CreateFindingAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<AuditFinding> UpdateFindingAsync(UpdateAuditFindingRequest request)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();

                var query = @"
                    UPDATE audit_findings SET
                        finding_title = @FindingTitle,
                        finding_description = @FindingDescription,
                        severity_id = @SeverityId,
                        status_id = @StatusId,
                        due_date = @DueDate,
                        closed_date = @ClosedDate,
                        assigned_to = @AssignedTo,
                        assigned_to_user_id = @AssignedToUserId,
                        root_cause = @RootCause,
                        business_impact = @BusinessImpact,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = @Id";

                await db.ExecuteAsync(query, request);
                return await GetFindingAsync(request.Id);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in UpdateFindingAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<bool> DeleteFindingAsync(int id)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();

                var query = "DELETE FROM audit_findings WHERE id = @Id";
                var affected = await db.ExecuteAsync(query, new { Id = id });
                return affected > 0;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in DeleteFindingAsync: {ex.Message}");
                throw;
            }
        }

        #endregion

        #region Recommendations CRUD

        public async Task<AuditRecommendation> GetRecommendationAsync(int id)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();

                var query = @"
                    SELECT
                        r.id AS Id,
                        r.finding_id AS FindingId,
                        r.recommendation_number AS RecommendationNumber,
                        r.recommendation AS Recommendation,
                        r.priority AS Priority,
                        r.management_response AS ManagementResponse,
                        r.agreed_date AS AgreedDate,
                        r.target_date AS TargetDate,
                        r.implementation_date AS ImplementationDate,
                        r.responsible_person AS ResponsiblePerson,
                        r.responsible_user_id AS ResponsibleUserId,
                        r.status_id AS StatusId,
                        r.verification_notes AS VerificationNotes,
                        r.verified_by_user_id AS VerifiedByUserId,
                        r.verified_date AS VerifiedDate,
                        r.created_at AS CreatedAt,
                        r.updated_at AS UpdatedAt,
                        s.name AS StatusName,
                        s.color AS StatusColor,
                        f.finding_title AS FindingTitle,
                        f.finding_number AS FindingNumber,
                        CASE r.priority WHEN 1 THEN 'High' WHEN 2 THEN 'Medium' ELSE 'Low' END AS PriorityName
                    FROM audit_recommendations r
                    LEFT JOIN ra_recommendation_status s ON r.status_id = s.id
                    LEFT JOIN audit_findings f ON r.finding_id = f.id
                    WHERE r.id = @Id";

                return await db.QueryFirstOrDefaultAsync<AuditRecommendation>(query, new { Id = id });
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in GetRecommendationAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<List<AuditRecommendation>> GetRecommendationsByFindingAsync(int findingId)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();

                var query = @"
                    SELECT
                        r.id AS Id,
                        r.finding_id AS FindingId,
                        r.recommendation_number AS RecommendationNumber,
                        r.recommendation AS Recommendation,
                        r.priority AS Priority,
                        r.management_response AS ManagementResponse,
                        r.target_date AS TargetDate,
                        r.status_id AS StatusId,
                        r.responsible_person AS ResponsiblePerson,
                        s.name AS StatusName,
                        s.color AS StatusColor,
                        CASE r.priority WHEN 1 THEN 'High' WHEN 2 THEN 'Medium' ELSE 'Low' END AS PriorityName,
                        EXTRACT(DAY FROM (r.target_date - CURRENT_DATE))::int AS DaysUntilTarget,
                        (r.target_date < CURRENT_DATE AND s.name NOT IN ('Implemented', 'Rejected')) AS IsOverdue
                    FROM audit_recommendations r
                    LEFT JOIN ra_recommendation_status s ON r.status_id = s.id
                    WHERE r.finding_id = @FindingId
                    ORDER BY r.priority, r.target_date";

                var result = await db.QueryAsync<AuditRecommendation>(query, new { FindingId = findingId });
                return result.ToList();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in GetRecommendationsByFindingAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<AuditRecommendation> CreateRecommendationAsync(CreateRecommendationRequest request)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();

                var query = @"
                    INSERT INTO audit_recommendations
                        (finding_id, recommendation, priority, target_date, responsible_person, responsible_user_id)
                    VALUES
                        (@FindingId, @Recommendation, @Priority, @TargetDate, @ResponsiblePerson, @ResponsibleUserId)
                    RETURNING id";

                var newId = await db.ExecuteScalarAsync<int>(query, request);
                return await GetRecommendationAsync(newId);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in CreateRecommendationAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<AuditRecommendation> UpdateRecommendationAsync(UpdateRecommendationRequest request)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();

                var query = @"
                    UPDATE audit_recommendations SET
                        recommendation = @Recommendation,
                        priority = @Priority,
                        management_response = @ManagementResponse,
                        agreed_date = @AgreedDate,
                        target_date = @TargetDate,
                        implementation_date = @ImplementationDate,
                        responsible_person = @ResponsiblePerson,
                        responsible_user_id = @ResponsibleUserId,
                        status_id = @StatusId,
                        verification_notes = @VerificationNotes,
                        verified_by_user_id = @VerifiedByUserId,
                        verified_date = @VerifiedDate,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = @Id";

                await db.ExecuteAsync(query, request);
                return await GetRecommendationAsync(request.Id);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in UpdateRecommendationAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<bool> DeleteRecommendationAsync(int id)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();

                var query = "DELETE FROM audit_recommendations WHERE id = @Id";
                var affected = await db.ExecuteAsync(query, new { Id = id });
                return affected > 0;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in DeleteRecommendationAsync: {ex.Message}");
                throw;
            }
        }

        #endregion

        #region Lookups

        public async Task<List<FindingSeverity>> GetSeveritiesAsync()
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();

                var query = @"
                    SELECT id AS Id, name AS Name, description AS Description,
                           color AS Color, sort_order AS SortOrder, is_active AS IsActive
                    FROM ra_finding_severity
                    WHERE is_active = true
                    ORDER BY sort_order";

                var result = await db.QueryAsync<FindingSeverity>(query);
                return result.ToList();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in GetSeveritiesAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<List<FindingStatus>> GetFindingStatusesAsync()
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();

                var query = @"
                    SELECT id AS Id, name AS Name, description AS Description,
                           color AS Color, is_closed AS IsClosed, sort_order AS SortOrder, is_active AS IsActive
                    FROM ra_finding_status
                    WHERE is_active = true
                    ORDER BY sort_order";

                var result = await db.QueryAsync<FindingStatus>(query);
                return result.ToList();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in GetFindingStatusesAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<List<RecommendationStatus>> GetRecommendationStatusesAsync()
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();

                var query = @"
                    SELECT id AS Id, name AS Name, description AS Description,
                           color AS Color, sort_order AS SortOrder, is_active AS IsActive
                    FROM ra_recommendation_status
                    WHERE is_active = true
                    ORDER BY sort_order";

                var result = await db.QueryAsync<RecommendationStatus>(query);
                return result.ToList();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in GetRecommendationStatusesAsync: {ex.Message}");
                throw;
            }
        }

        #endregion

        #region Analytics

        public async Task<FindingsAgingResponse> GetFindingsAgingAsync(int? referenceId, int? auditUniverseId)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();

                var whereClause = "WHERE st.is_closed = false";
                var parameters = new DynamicParameters();

                if (referenceId.HasValue)
                {
                    whereClause += " AND f.reference_id = @ReferenceId";
                    parameters.Add("ReferenceId", referenceId.Value);
                }
                if (auditUniverseId.HasValue)
                {
                    whereClause += " AND f.audit_universe_id = @AuditUniverseId";
                    parameters.Add("AuditUniverseId", auditUniverseId.Value);
                }

                var query = $@"
                    SELECT
                        s.name AS Severity,
                        s.color AS SeverityColor,
                        COUNT(*) FILTER (WHERE CURRENT_DATE - f.identified_date <= 30) AS Days0To30,
                        COUNT(*) FILTER (WHERE CURRENT_DATE - f.identified_date BETWEEN 31 AND 60) AS Days31To60,
                        COUNT(*) FILTER (WHERE CURRENT_DATE - f.identified_date BETWEEN 61 AND 90) AS Days61To90,
                        COUNT(*) FILTER (WHERE CURRENT_DATE - f.identified_date > 90) AS Days90Plus,
                        COUNT(*) AS TotalOpen
                    FROM audit_findings f
                    INNER JOIN ra_finding_severity s ON f.severity_id = s.id
                    INNER JOIN ra_finding_status st ON f.status_id = st.id
                    {whereClause}
                    GROUP BY s.name, s.color, s.sort_order
                    ORDER BY s.sort_order";

                var buckets = await db.QueryAsync<FindingsAgingBucket>(query, parameters);

                // Get summary
                var summaryQuery = $@"
                    SELECT
                        COUNT(*) AS TotalOpen,
                        COUNT(*) FILTER (WHERE f.due_date < CURRENT_DATE) AS TotalOverdue,
                        COALESCE(AVG(EXTRACT(DAY FROM (CURRENT_DATE - f.identified_date))), 0)::numeric(10,1) AS AverageAgeInDays,
                        COALESCE(MAX(EXTRACT(DAY FROM (CURRENT_DATE - f.identified_date))), 0)::int AS OldestOpenDays
                    FROM audit_findings f
                    INNER JOIN ra_finding_status st ON f.status_id = st.id
                    {whereClause}";

                var summary = await db.QueryFirstOrDefaultAsync<FindingsAgingSummary>(summaryQuery, parameters) ?? new FindingsAgingSummary();

                return new FindingsAgingResponse
                {
                    ReferenceId = referenceId ?? 0,
                    AuditUniverseId = auditUniverseId,
                    AgingBuckets = buckets.ToList(),
                    Summary = summary
                };
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in GetFindingsAgingAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<RecommendationSummary> GetRecommendationSummaryAsync(int? referenceId, int? auditUniverseId)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();

                var whereClause = "WHERE 1=1";
                var parameters = new DynamicParameters();

                if (referenceId.HasValue)
                {
                    whereClause += " AND f.reference_id = @ReferenceId";
                    parameters.Add("ReferenceId", referenceId.Value);
                }
                if (auditUniverseId.HasValue)
                {
                    whereClause += " AND f.audit_universe_id = @AuditUniverseId";
                    parameters.Add("AuditUniverseId", auditUniverseId.Value);
                }

                var query = $@"
                    SELECT
                        COUNT(*) AS TotalCount,
                        COUNT(*) FILTER (WHERE s.name = 'Pending') AS PendingCount,
                        COUNT(*) FILTER (WHERE s.name = 'Agreed') AS AgreedCount,
                        COUNT(*) FILTER (WHERE s.name = 'In Progress') AS InProgressCount,
                        COUNT(*) FILTER (WHERE s.name = 'Implemented') AS ImplementedCount,
                        COUNT(*) FILTER (WHERE s.name = 'Rejected') AS RejectedCount,
                        COUNT(*) FILTER (WHERE s.name = 'Deferred') AS DeferredCount,
                        COUNT(*) FILTER (WHERE r.target_date < CURRENT_DATE AND s.name NOT IN ('Implemented', 'Rejected')) AS OverdueCount,
                        CASE WHEN COUNT(*) > 0
                             THEN ROUND(COUNT(*) FILTER (WHERE s.name = 'Implemented')::numeric / COUNT(*) * 100, 1)
                             ELSE 0 END AS ImplementationRate
                    FROM audit_recommendations r
                    INNER JOIN audit_findings f ON r.finding_id = f.id
                    LEFT JOIN ra_recommendation_status s ON r.status_id = s.id
                    {whereClause}";

                return await db.QueryFirstOrDefaultAsync<RecommendationSummary>(query, parameters) ?? new RecommendationSummary();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in GetRecommendationSummaryAsync: {ex.Message}");
                throw;
            }
        }

        #endregion

        #region Audit Coverage

        public async Task<List<AuditCoverage>> GetAuditCoverageAsync(int auditUniverseId, int? year)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();

                var whereClause = "WHERE c.audit_universe_id = @AuditUniverseId";
                var parameters = new DynamicParameters();
                parameters.Add("AuditUniverseId", auditUniverseId);

                if (year.HasValue)
                {
                    whereClause += " AND c.period_year = @Year";
                    parameters.Add("Year", year.Value);
                }

                var query = $@"
                    SELECT
                        c.id AS Id,
                        c.audit_universe_id AS AuditUniverseId,
                        c.period_year AS PeriodYear,
                        c.period_quarter AS PeriodQuarter,
                        c.planned_audits AS PlannedAudits,
                        c.completed_audits AS CompletedAudits,
                        c.coverage_percentage AS CoveragePercentage,
                        c.total_findings AS TotalFindings,
                        c.critical_findings AS CriticalFindings,
                        c.high_findings AS HighFindings,
                        c.notes AS Notes,
                        au.name AS AuditUniverseName,
                        au.code AS AuditUniverseCode
                    FROM audit_coverage c
                    INNER JOIN audit_universe au ON c.audit_universe_id = au.id
                    {whereClause}
                    ORDER BY c.period_year DESC, c.period_quarter DESC NULLS FIRST";

                var result = await db.QueryAsync<AuditCoverage>(query, parameters);
                return result.ToList();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in GetAuditCoverageAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<AuditCoverageMapResponse> GetAuditCoverageMapAsync(int year, int? quarter)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();

                var quarterClause = quarter.HasValue ? "AND c.period_quarter = @Quarter" : "AND c.period_quarter IS NULL";

                var query = $@"
                    SELECT
                        au.id AS Id,
                        au.name AS Name,
                        au.code AS Code,
                        au.parent_id AS ParentId,
                        au.level AS Level,
                        au.risk_rating AS RiskRating,
                        COALESCE(c.planned_audits, 0) AS PlannedAudits,
                        COALESCE(c.completed_audits, 0) AS CompletedAudits,
                        COALESCE(c.coverage_percentage, 0) AS CoveragePercentage,
                        COALESCE(c.total_findings, 0) AS TotalFindings,
                        (SELECT COUNT(*) FROM audit_findings f
                         INNER JOIN ra_finding_status s ON f.status_id = s.id
                         WHERE f.audit_universe_id = au.id AND s.is_closed = false) AS OpenFindings,
                        COALESCE(c.critical_findings, 0) AS CriticalFindings,
                        COALESCE(c.high_findings, 0) AS HighFindings,
                        CASE
                            WHEN COALESCE(c.coverage_percentage, 0) < 50 THEN '#EF4444'
                            WHEN COALESCE(c.coverage_percentage, 0) < 80 THEN '#F59E0B'
                            ELSE '#10B981'
                        END AS CoverageColor,
                        CASE au.risk_rating WHEN 'High' THEN 3 WHEN 'Medium' THEN 2 ELSE 1 END * 10 AS Size
                    FROM audit_universe au
                    LEFT JOIN audit_coverage c ON au.id = c.audit_universe_id
                        AND c.period_year = @Year {quarterClause}
                    WHERE au.is_active = true
                    ORDER BY au.level, au.name";

                var parameters = new DynamicParameters();
                parameters.Add("Year", year);
                if (quarter.HasValue) parameters.Add("Quarter", quarter.Value);

                var allNodes = (await db.QueryAsync<AuditCoverageMapNode>(query, parameters)).ToList();

                // Build hierarchy
                var nodeDict = allNodes.ToDictionary(n => n.Id);
                var rootNodes = new List<AuditCoverageMapNode>();

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

                // Calculate summary
                var summary = new AuditCoverageMapSummary
                {
                    TotalNodes = allNodes.Count,
                    NodesAudited = allNodes.Count(n => n.CompletedAudits > 0),
                    OverallCoverage = allNodes.Any() ? allNodes.Average(n => n.CoveragePercentage) : 0,
                    TotalPlannedAudits = allNodes.Sum(n => n.PlannedAudits),
                    TotalCompletedAudits = allNodes.Sum(n => n.CompletedAudits),
                    NodesBelowTarget = allNodes.Count(n => n.CoveragePercentage < 80),
                    NodesAtRisk = allNodes.Count(n => n.CoveragePercentage < 50)
                };

                return new AuditCoverageMapResponse
                {
                    Year = year,
                    Quarter = quarter,
                    Nodes = rootNodes,
                    Summary = summary
                };
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in GetAuditCoverageMapAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<bool> UpdateAuditCoverageAsync(UpdateAuditCoverageRequest request)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();

                var query = @"
                    INSERT INTO audit_coverage
                        (audit_universe_id, period_year, period_quarter, planned_audits, completed_audits,
                         total_findings, critical_findings, high_findings, notes)
                    VALUES
                        (@AuditUniverseId, @PeriodYear, @PeriodQuarter, @PlannedAudits, @CompletedAudits,
                         @TotalFindings, @CriticalFindings, @HighFindings, @Notes)
                    ON CONFLICT (audit_universe_id, period_year, period_quarter)
                    DO UPDATE SET
                        planned_audits = EXCLUDED.planned_audits,
                        completed_audits = EXCLUDED.completed_audits,
                        total_findings = EXCLUDED.total_findings,
                        critical_findings = EXCLUDED.critical_findings,
                        high_findings = EXCLUDED.high_findings,
                        notes = EXCLUDED.notes,
                        updated_at = CURRENT_TIMESTAMP";

                await db.ExecuteAsync(query, request);
                return true;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in UpdateAuditCoverageAsync: {ex.Message}");
                throw;
            }
        }

        #endregion

        #region Risk Trends

        public async Task<RiskTrendResponse> GetRiskTrendAsync(int? referenceId, int? auditUniverseId, int months)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();

                var whereClause = "WHERE snapshot_date >= CURRENT_DATE - INTERVAL '" + months + " months'";
                var parameters = new DynamicParameters();

                if (referenceId.HasValue)
                {
                    whereClause += " AND reference_id = @ReferenceId";
                    parameters.Add("ReferenceId", referenceId.Value);
                }
                if (auditUniverseId.HasValue)
                {
                    whereClause += " AND audit_universe_id = @AuditUniverseId";
                    parameters.Add("AuditUniverseId", auditUniverseId.Value);
                }

                var query = $@"
                    SELECT
                        snapshot_date AS Date,
                        TO_CHAR(snapshot_date, 'Mon YYYY') AS PeriodLabel,
                        critical_count AS CriticalCount,
                        high_count AS HighCount,
                        medium_count AS MediumCount,
                        low_count AS LowCount,
                        (critical_count + high_count + medium_count + low_count + very_low_count) AS TotalCount,
                        CASE WHEN assessment_count > 0
                             THEN ROUND(total_residual_score / assessment_count, 2)
                             ELSE 0 END AS AverageResidualScore
                    FROM risk_trend_history
                    {whereClause}
                    ORDER BY snapshot_date";

                var dataPoints = await db.QueryAsync<RiskTrendDataPoint>(query, parameters);
                var pointsList = dataPoints.ToList();

                // Calculate summary
                var summary = new RiskTrendSummary();
                if (pointsList.Count >= 2)
                {
                    var current = pointsList.Last();
                    var previous = pointsList[pointsList.Count - 2];

                    summary.CurrentTotal = current.TotalCount;
                    summary.PreviousTotal = previous.TotalCount;
                    summary.ChangeCount = current.TotalCount - previous.TotalCount;
                    summary.ChangePercentage = previous.TotalCount > 0
                        ? Math.Round((decimal)(current.TotalCount - previous.TotalCount) / previous.TotalCount * 100, 1)
                        : 0;
                    summary.TrendDirection = summary.ChangeCount < 0 ? "improving" : summary.ChangeCount > 0 ? "worsening" : "stable";
                    summary.CriticalChange = current.CriticalCount - previous.CriticalCount;
                    summary.HighChange = current.HighCount - previous.HighCount;
                }

                return new RiskTrendResponse
                {
                    ReferenceId = referenceId,
                    AuditUniverseId = auditUniverseId,
                    PeriodType = "monthly",
                    DataPoints = pointsList,
                    Summary = summary
                };
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in GetRiskTrendAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<RiskVelocityResponse> GetRiskVelocityAsync(int? referenceId, int? auditUniverseId)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();

                // Get current and previous period data
                var trend = await GetRiskTrendAsync(referenceId, auditUniverseId, 2);

                var response = new RiskVelocityResponse
                {
                    ReferenceId = referenceId,
                    AuditUniverseId = auditUniverseId,
                    PeriodStart = DateTime.Today.AddMonths(-1),
                    PeriodEnd = DateTime.Today,
                    NetChange = trend.Summary.ChangeCount,
                    PreviousPeriodNetChange = 0,
                    VelocityScore = Math.Min(100, Math.Max(-100, trend.Summary.ChangeCount * 10)),
                    TrendIndicator = trend.Summary.TrendDirection,
                    VelocityDirection = "stable"
                };

                if (trend.Summary.ChangeCount > 0)
                {
                    response.ComparisonText = $"Risk increased by {trend.Summary.ChangeCount} this period";
                    response.VelocityDirection = "accelerating";
                }
                else if (trend.Summary.ChangeCount < 0)
                {
                    response.ComparisonText = $"Risk decreased by {Math.Abs(trend.Summary.ChangeCount)} this period";
                    response.VelocityDirection = "decelerating";
                }
                else
                {
                    response.ComparisonText = "Risk level unchanged this period";
                }

                return response;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in GetRiskVelocityAsync: {ex.Message}");
                throw;
            }
        }

        public async Task<bool> CreateRiskTrendSnapshotAsync(int? referenceId, int? auditUniverseId)
        {
            try
            {
                using IDbConnection db = new NpgsqlConnection(_connectionString);
                db.Open();

                // This would typically be called by a scheduled job
                var query = @"
                    INSERT INTO risk_trend_history
                        (reference_id, audit_universe_id, snapshot_date, period_type,
                         critical_count, high_count, medium_count, low_count, very_low_count,
                         total_inherent_score, total_residual_score, assessment_count)
                    SELECT
                        @ReferenceId,
                        @AuditUniverseId,
                        CURRENT_DATE,
                        'monthly',
                        COUNT(*) FILTER (WHERE residual_score >= 20),
                        COUNT(*) FILTER (WHERE residual_score >= 12 AND residual_score < 20),
                        COUNT(*) FILTER (WHERE residual_score >= 8 AND residual_score < 12),
                        COUNT(*) FILTER (WHERE residual_score >= 4 AND residual_score < 8),
                        COUNT(*) FILTER (WHERE residual_score < 4),
                        COALESCE(SUM(inherent_score), 0),
                        COALESCE(SUM(residual_score), 0),
                        COUNT(*)
                    FROM (
                        SELECT
                            (risklikelihood_id * riskimpact_id) AS inherent_score,
                            (outcomelikelihood_id * COALESCE(outcome_riskimpact_id, 1)) AS residual_score
                        FROM riskassessment
                        WHERE reference_id = COALESCE(@ReferenceId, reference_id)
                    ) scores
                    ON CONFLICT (reference_id, snapshot_date, period_type) DO UPDATE SET
                        critical_count = EXCLUDED.critical_count,
                        high_count = EXCLUDED.high_count,
                        medium_count = EXCLUDED.medium_count,
                        low_count = EXCLUDED.low_count,
                        very_low_count = EXCLUDED.very_low_count,
                        total_inherent_score = EXCLUDED.total_inherent_score,
                        total_residual_score = EXCLUDED.total_residual_score,
                        assessment_count = EXCLUDED.assessment_count";

                await db.ExecuteAsync(query, new { ReferenceId = referenceId, AuditUniverseId = auditUniverseId });
                return true;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in CreateRiskTrendSnapshotAsync: {ex.Message}");
                throw;
            }
        }

        #endregion
    }
}
