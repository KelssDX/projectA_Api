using System;
using System.Threading.Tasks;
using DotNet.Testcontainers.Builders;
using Testcontainers.PostgreSql;

namespace Affine.Tests.Helpers
{
    public class PostgresTestDbHelper
    {
        private readonly PostgreSqlContainer _postgreSqlContainer;

        public PostgresTestDbHelper()
        {
            _postgreSqlContainer = new PostgreSqlBuilder()
                .WithImage("postgres:14")
                .WithPortBinding(5432, true)
                .WithDatabase("Risk_Assess_Framework_Test")
                .WithUsername("postgres")
                .WithPassword("testpassword")
                .WithCleanUp(true)
                .Build();
        }

        public async Task InitializeAsync()
        {
            await _postgreSqlContainer.StartAsync();

            // Initialize schema
            await _postgreSqlContainer.ExecScriptAsync(@"
                CREATE TABLE IF NOT EXISTS RiskAssessmentReference (
                    reference_id SERIAL PRIMARY KEY,
                    client VARCHAR(255),
                    assessment_start_date TIMESTAMP,
                    assessment_end_date TIMESTAMP,
                    assessor VARCHAR(255),
                    approved_by VARCHAR(255)
                );
                
                CREATE TABLE IF NOT EXISTS RA_RiskLikelihood (
                    id SERIAL PRIMARY KEY,
                    description VARCHAR(255),
                    position INTEGER
                );
                
                CREATE TABLE IF NOT EXISTS RA_RiskImpact (
                    id SERIAL PRIMARY KEY,
                    description VARCHAR(255),
                    position INTEGER
                );
                
                CREATE TABLE IF NOT EXISTS RA_KeySecondary (
                    id SERIAL PRIMARY KEY,
                    description VARCHAR(255),
                    position INTEGER
                );
                
                CREATE TABLE IF NOT EXISTS RA_RiskCategory (
                    id SERIAL PRIMARY KEY,
                    description VARCHAR(255),
                    position INTEGER
                );
                
                CREATE TABLE IF NOT EXISTS RA_DataFrequency (
                    id SERIAL PRIMARY KEY,
                    description VARCHAR(255),
                    position INTEGER
                );
                
                CREATE TABLE IF NOT EXISTS RA_Frequency (
                    id SERIAL PRIMARY KEY,
                    description VARCHAR(255),
                    position INTEGER
                );
                
                CREATE TABLE IF NOT EXISTS RA_Evidence (
                    id SERIAL PRIMARY KEY,
                    description VARCHAR(255),
                    position INTEGER
                );
                
                CREATE TABLE IF NOT EXISTS RA_OutcomeLikelihood (
                    id SERIAL PRIMARY KEY,
                    description VARCHAR(255),
                    position INTEGER
                );
                
                CREATE TABLE IF NOT EXISTS RA_Impact (
                    id SERIAL PRIMARY KEY,
                    description VARCHAR(255),
                    position INTEGER
                );
                
                CREATE TABLE IF NOT EXISTS RA_Nature (
                    id SERIAL PRIMARY KEY,
                    description VARCHAR(255),
                    position INTEGER
                );
                
                CREATE TABLE IF NOT EXISTS RiskAssessment (
                    id SERIAL PRIMARY KEY,
                    RiskAssessment_RefID INTEGER,
                    reference_id INTEGER REFERENCES RiskAssessmentReference(reference_id),
                    BusinessObjectives VARCHAR(255),
                    MainProcess VARCHAR(255),
                    SubProcess VARCHAR(255),
                    KeyRiskAndFactors VARCHAR(255),
                    MitigatingControls VARCHAR(255),
                    Responsibility VARCHAR(255),
                    Authoriser VARCHAR(255),
                    AuditorsRecommendedActionPlan VARCHAR(255),
                    ResponsiblePerson VARCHAR(255),
                    AgreedDate TIMESTAMP,
                    RiskLikelihoodId INTEGER REFERENCES RA_RiskLikelihood(id),
                    RiskImpactId INTEGER REFERENCES RA_RiskImpact(id),
                    KeySecondaryId INTEGER REFERENCES RA_KeySecondary(id),
                    RiskCategoryId INTEGER REFERENCES RA_RiskCategory(id),
                    DataFrequencyId INTEGER REFERENCES RA_DataFrequency(id),
                    FrequencyId INTEGER REFERENCES RA_Frequency(id),
                    EvidenceId INTEGER REFERENCES RA_Evidence(id),
                    OutcomeLikelihoodId INTEGER REFERENCES RA_OutcomeLikelihood(id),
                    ImpactId INTEGER REFERENCES RA_Impact(id)
                );
                
                -- Insert some test data
                INSERT INTO RA_RiskLikelihood (description, position) VALUES ('Low', 1), ('Medium', 2), ('High', 3);
                INSERT INTO RA_RiskImpact (description, position) VALUES ('Low', 1), ('Medium', 2), ('High', 3);
                INSERT INTO RA_KeySecondary (description, position) VALUES ('Key', 1), ('Secondary', 2);
                INSERT INTO RA_RiskCategory (description, position) VALUES ('Operational', 1), ('Financial', 2), ('Compliance', 3);
                INSERT INTO RA_DataFrequency (description, position) VALUES ('Daily', 1), ('Weekly', 2), ('Monthly', 3);
                INSERT INTO RA_Frequency (description, position) VALUES ('Low', 1), ('Medium', 2), ('High', 3);
                INSERT INTO RA_Evidence (description, position) VALUES ('Documentation', 1), ('Interview', 2), ('Observation', 3);
                INSERT INTO RA_OutcomeLikelihood (description, position) VALUES ('Low', 1), ('Medium', 2), ('High', 3);
                INSERT INTO RA_Impact (description, position) VALUES ('Low', 1), ('Medium', 2), ('High', 3);
                INSERT INTO RA_Nature (description, position) VALUES ('Preventive', 1), ('Detective', 2), ('Corrective', 3);
                
                -- Insert test reference
                INSERT INTO RiskAssessmentReference (client, assessment_start_date, assessment_end_date, assessor, approved_by)
                VALUES ('Test Client', '2025-01-01', '2025-02-01', 'Test Assessor', 'Test Approver');
                
                -- Insert test risk assessment
                INSERT INTO RiskAssessment (
                    RiskAssessment_RefID, reference_id, BusinessObjectives, MainProcess, SubProcess,
                    KeyRiskAndFactors, MitigatingControls, Responsibility, Authoriser,
                    AuditorsRecommendedActionPlan, ResponsiblePerson, AgreedDate,
                    RiskLikelihoodId, RiskImpactId, KeySecondaryId, RiskCategoryId,
                    DataFrequencyId, FrequencyId, EvidenceId, OutcomeLikelihoodId, ImpactId
                )
                VALUES (
                    1, 1, 'Test Objectives', 'Test Main Process', 'Test Sub Process',
                    'Test Risk Factors', 'Test Controls', 'Test Responsibility', 'Test Authoriser',
                    'Test Action Plan', 'Test Person', '2025-02-15',
                    1, 1, 1, 1, 1, 1, 1, 1, 1
                );
            ");
        }

        public async Task DisposeAsync()
        {
            await _postgreSqlContainer.StopAsync();
            await _postgreSqlContainer.DisposeAsync();
        }

        public string GetConnectionString()
        {
            return _postgreSqlContainer.GetConnectionString();
        }
    }
} 