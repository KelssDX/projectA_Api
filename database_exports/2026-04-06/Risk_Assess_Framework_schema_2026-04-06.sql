--
-- PostgreSQL database dump
--

-- Dumped from database version 16.3
-- Dumped by pg_dump version 16.3

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

DROP DATABASE IF EXISTS "Risk_Assess_Framework";
--
-- Name: Risk_Assess_Framework; Type: DATABASE; Schema: -; Owner: -
--

CREATE DATABASE "Risk_Assess_Framework" WITH TEMPLATE = template0 ENCODING = 'UTF8';


\connect "Risk_Assess_Framework"

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: Elsa; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA "Elsa";


--
-- Name: Risk_Assess_Framework; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA "Risk_Assess_Framework";


--
-- Name: Risk_Workflow; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA "Risk_Workflow";


--
-- Name: generate_audit_procedure_code(); Type: FUNCTION; Schema: Risk_Assess_Framework; Owner: -
--

CREATE FUNCTION "Risk_Assess_Framework".generate_audit_procedure_code() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF NEW.procedure_code IS NULL THEN
        NEW.procedure_code := 'PROC-' || EXTRACT(YEAR FROM CURRENT_DATE)::TEXT || '-' ||
                              LPAD(nextval('audit_procedures_id_seq')::TEXT, 4, '0');
    END IF;
    RETURN NEW;
END;
$$;


--
-- Name: generate_document_code(); Type: FUNCTION; Schema: Risk_Assess_Framework; Owner: -
--

CREATE FUNCTION "Risk_Assess_Framework".generate_document_code() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF NEW.document_code IS NULL THEN
        NEW.document_code := 'DOC-' || EXTRACT(YEAR FROM CURRENT_DATE)::TEXT || '-' ||
                             LPAD(nextval('audit_documents_id_seq')::TEXT, 4, '0');
    END IF;
    RETURN NEW;
END;
$$;


--
-- Name: generate_evidence_request_number(); Type: FUNCTION; Schema: Risk_Assess_Framework; Owner: -
--

CREATE FUNCTION "Risk_Assess_Framework".generate_evidence_request_number() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF NEW.request_number IS NULL THEN
        NEW.request_number := 'EDR-' || EXTRACT(YEAR FROM CURRENT_DATE)::TEXT || '-' ||
                              LPAD(nextval('audit_evidence_requests_id_seq')::TEXT, 4, '0');
    END IF;
    RETURN NEW;
END;
$$;


--
-- Name: generate_finding_number(); Type: FUNCTION; Schema: Risk_Assess_Framework; Owner: -
--

CREATE FUNCTION "Risk_Assess_Framework".generate_finding_number() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF NEW.finding_number IS NULL THEN
        NEW.finding_number := 'FND-' || EXTRACT(YEAR FROM CURRENT_DATE)::TEXT || '-' ||
                             LPAD(nextval('audit_findings_id_seq')::TEXT, 4, '0');
    END IF;
    RETURN NEW;
END;
$$;


--
-- Name: generate_recommendation_number(); Type: FUNCTION; Schema: Risk_Assess_Framework; Owner: -
--

CREATE FUNCTION "Risk_Assess_Framework".generate_recommendation_number() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF NEW.recommendation_number IS NULL THEN
        NEW.recommendation_number := 'REC-' || EXTRACT(YEAR FROM CURRENT_DATE)::TEXT || '-' ||
                                    LPAD(nextval('audit_recommendations_id_seq')::TEXT, 4, '0');
    END IF;
    RETURN NEW;
END;
$$;


--
-- Name: generate_working_paper_code(); Type: FUNCTION; Schema: Risk_Assess_Framework; Owner: -
--

CREATE FUNCTION "Risk_Assess_Framework".generate_working_paper_code() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF NEW.working_paper_code IS NULL THEN
        NEW.working_paper_code := 'WP-' || EXTRACT(YEAR FROM CURRENT_DATE)::TEXT || '-' ||
                                  LPAD(nextval('audit_working_papers_id_seq')::TEXT, 4, '0');
    END IF;
    RETURN NEW;
END;
$$;


--
-- Name: set_audit_updated_at(); Type: FUNCTION; Schema: Risk_Assess_Framework; Owner: -
--

CREATE FUNCTION "Risk_Assess_Framework".set_audit_updated_at() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;


--
-- Name: update_audit_collaborator_updated_at(); Type: FUNCTION; Schema: Risk_Assess_Framework; Owner: -
--

CREATE FUNCTION "Risk_Assess_Framework".update_audit_collaborator_updated_at() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;


--
-- Name: update_audit_domain_rule_packages_updated_at(); Type: FUNCTION; Schema: Risk_Assess_Framework; Owner: -
--

CREATE FUNCTION "Risk_Assess_Framework".update_audit_domain_rule_packages_updated_at() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;


--
-- Name: update_audit_engagement_plan_updated_at(); Type: FUNCTION; Schema: Risk_Assess_Framework; Owner: -
--

CREATE FUNCTION "Risk_Assess_Framework".update_audit_engagement_plan_updated_at() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;


--
-- Name: update_audit_finance_finalization_updated_at(); Type: FUNCTION; Schema: Risk_Assess_Framework; Owner: -
--

CREATE FUNCTION "Risk_Assess_Framework".update_audit_finance_finalization_updated_at() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;


--
-- Name: update_audit_fs_mappings_updated_at(); Type: FUNCTION; Schema: Risk_Assess_Framework; Owner: -
--

CREATE FUNCTION "Risk_Assess_Framework".update_audit_fs_mappings_updated_at() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;


--
-- Name: update_audit_fs_profile_rules_updated_at(); Type: FUNCTION; Schema: Risk_Assess_Framework; Owner: -
--

CREATE FUNCTION "Risk_Assess_Framework".update_audit_fs_profile_rules_updated_at() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;


--
-- Name: update_audit_fs_profiles_updated_at(); Type: FUNCTION; Schema: Risk_Assess_Framework; Owner: -
--

CREATE FUNCTION "Risk_Assess_Framework".update_audit_fs_profiles_updated_at() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;


--
-- Name: update_audit_management_action_updated_at(); Type: FUNCTION; Schema: Risk_Assess_Framework; Owner: -
--

CREATE FUNCTION "Risk_Assess_Framework".update_audit_management_action_updated_at() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;


--
-- Name: update_audit_materiality_benchmark_profiles_updated_at(); Type: FUNCTION; Schema: Risk_Assess_Framework; Owner: -
--

CREATE FUNCTION "Risk_Assess_Framework".update_audit_materiality_benchmark_profiles_updated_at() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;


--
-- Name: update_audit_materiality_calculations_updated_at(); Type: FUNCTION; Schema: Risk_Assess_Framework; Owner: -
--

CREATE FUNCTION "Risk_Assess_Framework".update_audit_materiality_calculations_updated_at() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;


--
-- Name: update_audit_misstatements_updated_at(); Type: FUNCTION; Schema: Risk_Assess_Framework; Owner: -
--

CREATE FUNCTION "Risk_Assess_Framework".update_audit_misstatements_updated_at() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;


--
-- Name: update_audit_procedure_updated_at(); Type: FUNCTION; Schema: Risk_Assess_Framework; Owner: -
--

CREATE FUNCTION "Risk_Assess_Framework".update_audit_procedure_updated_at() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;


--
-- Name: update_audit_rcm_updated_at(); Type: FUNCTION; Schema: Risk_Assess_Framework; Owner: -
--

CREATE FUNCTION "Risk_Assess_Framework".update_audit_rcm_updated_at() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;


--
-- Name: update_audit_support_requests_updated_at(); Type: FUNCTION; Schema: Risk_Assess_Framework; Owner: -
--

CREATE FUNCTION "Risk_Assess_Framework".update_audit_support_requests_updated_at() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;


--
-- Name: update_audit_walkthrough_updated_at(); Type: FUNCTION; Schema: Risk_Assess_Framework; Owner: -
--

CREATE FUNCTION "Risk_Assess_Framework".update_audit_walkthrough_updated_at() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;


--
-- Name: update_evidence_request_updated_at(); Type: FUNCTION; Schema: Risk_Assess_Framework; Owner: -
--

CREATE FUNCTION "Risk_Assess_Framework".update_evidence_request_updated_at() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;


--
-- Name: update_updated_at_column(); Type: FUNCTION; Schema: Risk_Assess_Framework; Owner: -
--

CREATE FUNCTION "Risk_Assess_Framework".update_updated_at_column() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;


--
-- Name: update_working_paper_updated_at(); Type: FUNCTION; Schema: Risk_Assess_Framework; Owner: -
--

CREATE FUNCTION "Risk_Assess_Framework".update_working_paper_updated_at() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: ActivityExecutionRecords; Type: TABLE; Schema: Elsa; Owner: -
--

CREATE TABLE "Elsa"."ActivityExecutionRecords" (
    "Id" text NOT NULL,
    "WorkflowInstanceId" text NOT NULL,
    "ActivityId" text NOT NULL,
    "ActivityNodeId" text NOT NULL,
    "ActivityType" text NOT NULL,
    "ActivityTypeVersion" integer NOT NULL,
    "ActivityName" text,
    "StartedAt" timestamp with time zone NOT NULL,
    "HasBookmarks" boolean NOT NULL,
    "Status" text NOT NULL,
    "CompletedAt" timestamp with time zone,
    "SerializedActivityState" text,
    "SerializedException" text,
    "SerializedOutputs" text,
    "SerializedPayload" text,
    "SerializedActivityStateCompressionAlgorithm" text,
    "SerializedProperties" text,
    "TenantId" text
);


--
-- Name: BookmarkQueueItems; Type: TABLE; Schema: Elsa; Owner: -
--

CREATE TABLE "Elsa"."BookmarkQueueItems" (
    "Id" text NOT NULL,
    "WorkflowInstanceId" text,
    "CorrelationId" text,
    "BookmarkId" text,
    "StimulusHash" text,
    "ActivityInstanceId" text,
    "ActivityTypeName" text,
    "CreatedAt" timestamp with time zone NOT NULL,
    "SerializedOptions" text,
    "TenantId" text
);


--
-- Name: Bookmarks; Type: TABLE; Schema: Elsa; Owner: -
--

CREATE TABLE "Elsa"."Bookmarks" (
    "Id" text NOT NULL,
    "ActivityTypeName" text NOT NULL,
    "Hash" text NOT NULL,
    "WorkflowInstanceId" text NOT NULL,
    "ActivityInstanceId" text,
    "CorrelationId" text,
    "CreatedAt" timestamp with time zone NOT NULL,
    "SerializedMetadata" text,
    "SerializedPayload" text,
    "TenantId" text
);


--
-- Name: KeyValuePairs; Type: TABLE; Schema: Elsa; Owner: -
--

CREATE TABLE "Elsa"."KeyValuePairs" (
    "Id" text NOT NULL,
    "SerializedValue" text NOT NULL,
    "TenantId" text
);


--
-- Name: Triggers; Type: TABLE; Schema: Elsa; Owner: -
--

CREATE TABLE "Elsa"."Triggers" (
    "Id" text NOT NULL,
    "WorkflowDefinitionId" text NOT NULL,
    "WorkflowDefinitionVersionId" text NOT NULL,
    "Name" text NOT NULL,
    "ActivityId" text NOT NULL,
    "Hash" text,
    "SerializedPayload" text,
    "TenantId" text
);


--
-- Name: WorkflowDefinitions; Type: TABLE; Schema: Elsa; Owner: -
--

CREATE TABLE "Elsa"."WorkflowDefinitions" (
    "Id" text NOT NULL,
    "DefinitionId" text NOT NULL,
    "Name" text,
    "Description" text,
    "ToolVersion" text,
    "ProviderName" text,
    "MaterializerName" text NOT NULL,
    "MaterializerContext" text,
    "StringData" text,
    "BinaryData" bytea,
    "IsReadonly" boolean NOT NULL,
    "Data" text,
    "UsableAsActivity" boolean,
    "CreatedAt" timestamp with time zone NOT NULL,
    "Version" integer NOT NULL,
    "IsLatest" boolean NOT NULL,
    "IsPublished" boolean NOT NULL,
    "IsSystem" boolean DEFAULT false NOT NULL,
    "TenantId" text
);


--
-- Name: WorkflowExecutionLogRecords; Type: TABLE; Schema: Elsa; Owner: -
--

CREATE TABLE "Elsa"."WorkflowExecutionLogRecords" (
    "Id" text NOT NULL,
    "WorkflowDefinitionId" text NOT NULL,
    "WorkflowDefinitionVersionId" text NOT NULL,
    "WorkflowInstanceId" text NOT NULL,
    "WorkflowVersion" integer NOT NULL,
    "ActivityInstanceId" text NOT NULL,
    "ParentActivityInstanceId" text,
    "ActivityId" text NOT NULL,
    "ActivityType" text NOT NULL,
    "ActivityTypeVersion" integer NOT NULL,
    "ActivityName" text,
    "ActivityNodeId" text NOT NULL,
    "Timestamp" timestamp with time zone NOT NULL,
    "Sequence" bigint NOT NULL,
    "EventName" text,
    "Message" text,
    "Source" text,
    "SerializedActivityState" text,
    "SerializedPayload" text,
    "TenantId" text
);


--
-- Name: WorkflowInboxMessages; Type: TABLE; Schema: Elsa; Owner: -
--

CREATE TABLE "Elsa"."WorkflowInboxMessages" (
    "Id" text NOT NULL,
    "ActivityTypeName" text NOT NULL,
    "Hash" text NOT NULL,
    "WorkflowInstanceId" text,
    "CorrelationId" text,
    "ActivityInstanceId" text,
    "CreatedAt" timestamp with time zone NOT NULL,
    "ExpiresAt" timestamp with time zone NOT NULL,
    "SerializedBookmarkPayload" text,
    "SerializedInput" text,
    "TenantId" text
);


--
-- Name: WorkflowInstances; Type: TABLE; Schema: Elsa; Owner: -
--

CREATE TABLE "Elsa"."WorkflowInstances" (
    "Id" text NOT NULL,
    "DefinitionId" text NOT NULL,
    "DefinitionVersionId" text NOT NULL,
    "Version" integer NOT NULL,
    "Status" text NOT NULL,
    "SubStatus" text NOT NULL,
    "CorrelationId" text,
    "Name" text,
    "IncidentCount" integer NOT NULL,
    "CreatedAt" timestamp with time zone NOT NULL,
    "UpdatedAt" timestamp with time zone NOT NULL,
    "FinishedAt" timestamp with time zone,
    "Data" text,
    "DataCompressionAlgorithm" text,
    "IsSystem" boolean DEFAULT false NOT NULL,
    "ParentWorkflowInstanceId" text,
    "TenantId" text,
    "IsExecuting" boolean DEFAULT false NOT NULL
);


--
-- Name: __EFMigrationsHistory; Type: TABLE; Schema: Elsa; Owner: -
--

CREATE TABLE "Elsa"."__EFMigrationsHistory" (
    "MigrationId" character varying(150) NOT NULL,
    "ProductVersion" character varying(32) NOT NULL
);


--
-- Name: OperationalRiskAssessment; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework"."OperationalRiskAssessment" (
    "Id" integer NOT NULL,
    "ReferenceId" integer NOT NULL,
    "MainProcess" character varying(200),
    "SubProcess" character varying(200),
    "Source" character varying(100),
    "LossFrequency" character varying(50),
    "LossEventCount" integer,
    "Probability" numeric(10,4),
    "LossAmount" numeric(18,2),
    "RiskMeasurement" character varying(50),
    "VaR" numeric(18,2),
    "SingleVaR" numeric(18,2),
    "CumulativeVaR" numeric(18,2),
    "CreatedAt" timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: OperationalRiskAssessment_Id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework"."OperationalRiskAssessment_Id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: OperationalRiskAssessment_Id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Assess_Framework; Owner: -
--

ALTER SEQUENCE "Risk_Assess_Framework"."OperationalRiskAssessment_Id_seq" OWNED BY "Risk_Assess_Framework"."OperationalRiskAssessment"."Id";


--
-- Name: accounts_user_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".accounts_user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: accounts; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".accounts (
    user_id integer DEFAULT nextval('"Risk_Assess_Framework".accounts_user_id_seq'::regclass) NOT NULL,
    password character varying(50) NOT NULL,
    firstname character varying(50),
    email character varying(255) NOT NULL,
    username character varying(100) NOT NULL,
    lastname character varying(255),
    role_id integer DEFAULT 3,
    department_id integer,
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: COLUMN accounts.username; Type: COMMENT; Schema: Risk_Assess_Framework; Owner: -
--

COMMENT ON COLUMN "Risk_Assess_Framework".accounts.username IS 'Unique username for login (separate from email)';


--
-- Name: COLUMN accounts.lastname; Type: COMMENT; Schema: Risk_Assess_Framework; Owner: -
--

COMMENT ON COLUMN "Risk_Assess_Framework".accounts.lastname IS 'User last name (combined with firstname for full name)';


--
-- Name: COLUMN accounts.role_id; Type: COMMENT; Schema: Risk_Assess_Framework; Owner: -
--

COMMENT ON COLUMN "Risk_Assess_Framework".accounts.role_id IS 'Foreign key to ra_userroles table';


--
-- Name: COLUMN accounts.department_id; Type: COMMENT; Schema: Risk_Assess_Framework; Owner: -
--

COMMENT ON COLUMN "Risk_Assess_Framework".accounts.department_id IS 'Foreign key to departments table';


--
-- Name: activity_log; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".activity_log (
    id integer NOT NULL,
    user_id integer,
    action character varying(100) NOT NULL,
    entity_type character varying(50) NOT NULL,
    entity_id integer NOT NULL,
    details jsonb,
    ip_address inet,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: TABLE activity_log; Type: COMMENT; Schema: Risk_Assess_Framework; Owner: -
--

COMMENT ON TABLE "Risk_Assess_Framework".activity_log IS 'Comprehensive audit log for all system activities';


--
-- Name: COLUMN activity_log.details; Type: COMMENT; Schema: Risk_Assess_Framework; Owner: -
--

COMMENT ON COLUMN "Risk_Assess_Framework".activity_log.details IS 'JSON details of what changed in the action';


--
-- Name: activity_log_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".activity_log_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: activity_log_id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Assess_Framework; Owner: -
--

ALTER SEQUENCE "Risk_Assess_Framework".activity_log_id_seq OWNED BY "Risk_Assess_Framework".activity_log.id;


--
-- Name: assessment_statistics; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".assessment_statistics (
    id integer NOT NULL,
    department_id integer,
    total_assessments integer DEFAULT 0,
    completed_assessments integer DEFAULT 0,
    high_risk_assessments integer DEFAULT 0,
    medium_risk_assessments integer DEFAULT 0,
    low_risk_assessments integer DEFAULT 0,
    last_updated timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: TABLE assessment_statistics; Type: COMMENT; Schema: Risk_Assess_Framework; Owner: -
--

COMMENT ON TABLE "Risk_Assess_Framework".assessment_statistics IS 'Pre-calculated statistics for dashboard performance';


--
-- Name: COLUMN assessment_statistics.last_updated; Type: COMMENT; Schema: Risk_Assess_Framework; Owner: -
--

COMMENT ON COLUMN "Risk_Assess_Framework".assessment_statistics.last_updated IS 'Timestamp when statistics were last recalculated';


--
-- Name: assessment_statistics_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".assessment_statistics_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: assessment_statistics_id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Assess_Framework; Owner: -
--

ALTER SEQUENCE "Risk_Assess_Framework".assessment_statistics_id_seq OWNED BY "Risk_Assess_Framework".assessment_statistics.id;


--
-- Name: audit_analytics_import_batches; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".audit_analytics_import_batches (
    id integer NOT NULL,
    reference_id integer,
    dataset_type character varying(50) NOT NULL,
    batch_name character varying(255),
    source_system character varying(100),
    source_file_name character varying(255),
    row_count integer DEFAULT 0 NOT NULL,
    imported_by_user_id integer,
    imported_by_name character varying(255),
    imported_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    notes text
);


--
-- Name: audit_analytics_import_batches_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".audit_analytics_import_batches_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: audit_analytics_import_batches_id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Assess_Framework; Owner: -
--

ALTER SEQUENCE "Risk_Assess_Framework".audit_analytics_import_batches_id_seq OWNED BY "Risk_Assess_Framework".audit_analytics_import_batches.id;


--
-- Name: audit_archival_events; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".audit_archival_events (
    id integer NOT NULL,
    reference_id integer,
    entity_type character varying(100) NOT NULL,
    entity_id character varying(100) NOT NULL,
    archive_action character varying(100) NOT NULL,
    reason text,
    retention_policy_id integer,
    archived_by_user_id integer,
    archived_by_name character varying(255),
    archived_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    details_json text
);


--
-- Name: audit_archival_events_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".audit_archival_events_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: audit_archival_events_id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Assess_Framework; Owner: -
--

ALTER SEQUENCE "Risk_Assess_Framework".audit_archival_events_id_seq OWNED BY "Risk_Assess_Framework".audit_archival_events.id;


--
-- Name: audit_control_test_results; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".audit_control_test_results (
    id integer NOT NULL,
    control_test_id integer NOT NULL,
    sample_reference character varying(100),
    attribute_tested character varying(255),
    expected_result text,
    actual_result text,
    is_exception boolean DEFAULT false,
    exception_description text,
    evidence_document_id integer,
    evidence_working_paper_id integer,
    result_status character varying(100) DEFAULT 'Pass'::character varying NOT NULL,
    tested_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    tested_by_user_id integer
);


--
-- Name: TABLE audit_control_test_results; Type: COMMENT; Schema: Risk_Assess_Framework; Owner: -
--

COMMENT ON TABLE "Risk_Assess_Framework".audit_control_test_results IS 'Sample-level or attribute-level results captured under a control test.';


--
-- Name: audit_control_test_results_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".audit_control_test_results_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: audit_control_test_results_id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Assess_Framework; Owner: -
--

ALTER SEQUENCE "Risk_Assess_Framework".audit_control_test_results_id_seq OWNED BY "Risk_Assess_Framework".audit_control_test_results.id;


--
-- Name: audit_control_tests; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".audit_control_tests (
    id integer NOT NULL,
    reference_id integer NOT NULL,
    scope_item_id integer,
    risk_control_matrix_id integer,
    procedure_id integer,
    working_paper_id integer,
    control_name character varying(500) NOT NULL,
    control_description text,
    test_objective text,
    test_method character varying(100),
    population_description text,
    sample_size integer,
    sample_basis text,
    test_frequency character varying(100),
    tester_user_id integer,
    reviewer_user_id integer,
    planned_test_date date,
    performed_test_date date,
    status character varying(100) DEFAULT 'Planned'::character varying NOT NULL,
    conclusion character varying(100),
    notes text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: TABLE audit_control_tests; Type: COMMENT; Schema: Risk_Assess_Framework; Owner: -
--

COMMENT ON TABLE "Risk_Assess_Framework".audit_control_tests IS 'Engagement-level control test records linked to procedures, RCM items, and working papers.';


--
-- Name: audit_control_tests_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".audit_control_tests_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: audit_control_tests_id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Assess_Framework; Owner: -
--

ALTER SEQUENCE "Risk_Assess_Framework".audit_control_tests_id_seq OWNED BY "Risk_Assess_Framework".audit_control_tests.id;


--
-- Name: audit_coverage; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".audit_coverage (
    id integer NOT NULL,
    audit_universe_id integer NOT NULL,
    period_year integer NOT NULL,
    period_quarter integer,
    planned_audits integer DEFAULT 0,
    completed_audits integer DEFAULT 0,
    coverage_percentage numeric(5,2) GENERATED ALWAYS AS (
CASE
    WHEN (planned_audits > 0) THEN round((((completed_audits)::numeric / (planned_audits)::numeric) * (100)::numeric), 2)
    ELSE (0)::numeric
END) STORED,
    total_findings integer DEFAULT 0,
    critical_findings integer DEFAULT 0,
    high_findings integer DEFAULT 0,
    notes text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: TABLE audit_coverage; Type: COMMENT; Schema: Risk_Assess_Framework; Owner: -
--

COMMENT ON TABLE "Risk_Assess_Framework".audit_coverage IS 'Tracks audit coverage by universe node and time period';


--
-- Name: COLUMN audit_coverage.coverage_percentage; Type: COMMENT; Schema: Risk_Assess_Framework; Owner: -
--

COMMENT ON COLUMN "Risk_Assess_Framework".audit_coverage.coverage_percentage IS 'Auto-calculated coverage percentage';


--
-- Name: audit_coverage_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".audit_coverage_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: audit_coverage_id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Assess_Framework; Owner: -
--

ALTER SEQUENCE "Risk_Assess_Framework".audit_coverage_id_seq OWNED BY "Risk_Assess_Framework".audit_coverage.id;


--
-- Name: audit_document_access_logs; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".audit_document_access_logs (
    id bigint NOT NULL,
    document_id integer NOT NULL,
    reference_id integer,
    action_type character varying(50) NOT NULL,
    accessed_by_user_id integer,
    accessed_by_name character varying(255),
    ip_address character varying(100),
    client_context character varying(100),
    correlation_id character varying(255),
    success boolean DEFAULT true NOT NULL,
    details_json jsonb,
    accessed_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: TABLE audit_document_access_logs; Type: COMMENT; Schema: Risk_Assess_Framework; Owner: -
--

COMMENT ON TABLE "Risk_Assess_Framework".audit_document_access_logs IS 'Immutable log of document opens, downloads, previews, shares, deletes, and uploads.';


--
-- Name: audit_document_access_logs_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".audit_document_access_logs_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: audit_document_access_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Assess_Framework; Owner: -
--

ALTER SEQUENCE "Risk_Assess_Framework".audit_document_access_logs_id_seq OWNED BY "Risk_Assess_Framework".audit_document_access_logs.id;


--
-- Name: audit_document_permission_grants; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".audit_document_permission_grants (
    id integer NOT NULL,
    document_id integer NOT NULL,
    grantee_user_id integer,
    grantee_role_name character varying(100),
    permission_level character varying(50) DEFAULT 'View'::character varying NOT NULL,
    can_download boolean DEFAULT true NOT NULL,
    granted_by_user_id integer,
    granted_by_name character varying(255),
    notes text,
    granted_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    expires_at timestamp without time zone,
    CONSTRAINT chk_audit_document_permission_grant_target CHECK (((grantee_user_id IS NOT NULL) OR (NULLIF(btrim((COALESCE(grantee_role_name, ''::character varying))::text), ''::text) IS NOT NULL)))
);


--
-- Name: TABLE audit_document_permission_grants; Type: COMMENT; Schema: Risk_Assess_Framework; Owner: -
--

COMMENT ON TABLE "Risk_Assess_Framework".audit_document_permission_grants IS 'Explicit user- or role-based visibility grants for confidential audit documents.';


--
-- Name: COLUMN audit_document_permission_grants.permission_level; Type: COMMENT; Schema: Risk_Assess_Framework; Owner: -
--

COMMENT ON COLUMN "Risk_Assess_Framework".audit_document_permission_grants.permission_level IS 'Current values include View and Manage.';


--
-- Name: audit_document_permission_grants_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".audit_document_permission_grants_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: audit_document_permission_grants_id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Assess_Framework; Owner: -
--

ALTER SEQUENCE "Risk_Assess_Framework".audit_document_permission_grants_id_seq OWNED BY "Risk_Assess_Framework".audit_document_permission_grants.id;


--
-- Name: audit_documents; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".audit_documents (
    id integer NOT NULL,
    reference_id integer,
    audit_universe_id integer,
    procedure_id integer,
    working_paper_id integer,
    finding_id integer,
    recommendation_id integer,
    document_code character varying(50),
    title character varying(500) NOT NULL,
    original_file_name character varying(500) NOT NULL,
    stored_file_name character varying(500) NOT NULL,
    stored_relative_path character varying(1000) NOT NULL,
    content_type character varying(255),
    file_extension character varying(50),
    file_size bigint,
    category_id integer,
    source_type character varying(100) DEFAULT 'Audit Team'::character varying,
    tags text,
    notes text,
    uploaded_by_name character varying(255),
    uploaded_by_user_id integer,
    uploaded_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    is_active boolean DEFAULT true,
    visibility_level_id integer,
    confidentiality_label character varying(150),
    confidentiality_reason text,
    security_review_required boolean DEFAULT false,
    security_review_status character varying(50) DEFAULT 'Not Required'::character varying,
    security_review_requested_at timestamp without time zone,
    security_review_requested_by_user_id integer,
    security_review_requested_by_name character varying(255),
    security_reviewed_at timestamp without time zone,
    security_reviewed_by_user_id integer,
    security_reviewed_by_name character varying(255),
    security_review_notes text
);


--
-- Name: TABLE audit_documents; Type: COMMENT; Schema: Risk_Assess_Framework; Owner: -
--

COMMENT ON TABLE "Risk_Assess_Framework".audit_documents IS 'Central engagement document and evidence library';


--
-- Name: COLUMN audit_documents.source_type; Type: COMMENT; Schema: Risk_Assess_Framework; Owner: -
--

COMMENT ON COLUMN "Risk_Assess_Framework".audit_documents.source_type IS 'Typical values: Audit Team, Client, Management, System, Third Party';


--
-- Name: audit_documents_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".audit_documents_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: audit_documents_id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Assess_Framework; Owner: -
--

ALTER SEQUENCE "Risk_Assess_Framework".audit_documents_id_seq OWNED BY "Risk_Assess_Framework".audit_documents.id;


--
-- Name: audit_domain_rule_packages; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".audit_domain_rule_packages (
    id integer NOT NULL,
    package_code character varying(100) NOT NULL,
    package_name character varying(255) NOT NULL,
    domain_code character varying(100) NOT NULL,
    description text,
    is_default boolean DEFAULT false NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


--
-- Name: audit_domain_rule_packages_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".audit_domain_rule_packages_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: audit_domain_rule_packages_id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Assess_Framework; Owner: -
--

ALTER SEQUENCE "Risk_Assess_Framework".audit_domain_rule_packages_id_seq OWNED BY "Risk_Assess_Framework".audit_domain_rule_packages.id;


--
-- Name: audit_engagement_plans; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".audit_engagement_plans (
    id integer NOT NULL,
    reference_id integer NOT NULL,
    engagement_title character varying(500) NOT NULL,
    engagement_type_id integer,
    plan_year integer,
    annual_plan_name character varying(255),
    business_unit character varying(255),
    process_area character varying(255),
    subprocess_area character varying(255),
    fsli character varying(255),
    scope_summary text,
    materiality text,
    risk_strategy text,
    planning_status_id integer DEFAULT 1,
    scope_letter_document_id integer,
    is_signed_off boolean DEFAULT false,
    signed_off_by_name character varying(255),
    signed_off_by_user_id integer,
    signed_off_at timestamp without time zone,
    notes text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    materiality_basis character varying(255),
    overall_materiality numeric(18,2),
    performance_materiality numeric(18,2),
    clearly_trivial_threshold numeric(18,2),
    materiality_source character varying(50) DEFAULT 'Manual'::character varying NOT NULL,
    active_materiality_calculation_id bigint,
    materiality_last_calculated_at timestamp without time zone,
    materiality_override_reason text,
    selected_materiality_benchmark character varying(255),
    selected_materiality_benchmark_amount numeric(18,2),
    selected_materiality_benchmark_percentage numeric(9,4),
    materiality_benchmark_profile_id integer,
    materiality_entity_type character varying(150),
    materiality_industry_name character varying(255),
    materiality_benchmark_selection_rationale text
);


--
-- Name: audit_engagement_plans_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".audit_engagement_plans_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: audit_engagement_plans_id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Assess_Framework; Owner: -
--

ALTER SEQUENCE "Risk_Assess_Framework".audit_engagement_plans_id_seq OWNED BY "Risk_Assess_Framework".audit_engagement_plans.id;


--
-- Name: audit_evidence_request_items; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".audit_evidence_request_items (
    id integer NOT NULL,
    request_id integer NOT NULL,
    item_description text NOT NULL,
    expected_document_type character varying(255),
    is_required boolean DEFAULT true,
    fulfilled_document_id integer,
    submitted_at timestamp without time zone,
    reviewer_notes text,
    reviewed_by_user_id integer,
    reviewed_at timestamp without time zone,
    is_accepted boolean,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: TABLE audit_evidence_request_items; Type: COMMENT; Schema: Risk_Assess_Framework; Owner: -
--

COMMENT ON TABLE "Risk_Assess_Framework".audit_evidence_request_items IS 'Individual evidence items requested under a single request';


--
-- Name: COLUMN audit_evidence_request_items.fulfilled_document_id; Type: COMMENT; Schema: Risk_Assess_Framework; Owner: -
--

COMMENT ON COLUMN "Risk_Assess_Framework".audit_evidence_request_items.fulfilled_document_id IS 'Document uploaded to fulfill this request item';


--
-- Name: audit_evidence_request_items_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".audit_evidence_request_items_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: audit_evidence_request_items_id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Assess_Framework; Owner: -
--

ALTER SEQUENCE "Risk_Assess_Framework".audit_evidence_request_items_id_seq OWNED BY "Risk_Assess_Framework".audit_evidence_request_items.id;


--
-- Name: audit_evidence_requests; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".audit_evidence_requests (
    id integer NOT NULL,
    reference_id integer,
    audit_universe_id integer,
    request_number character varying(50),
    title character varying(500) NOT NULL,
    request_description text,
    requested_from character varying(255),
    requested_to_email character varying(255),
    priority integer DEFAULT 2,
    due_date date,
    status_id integer DEFAULT 2,
    requested_by_user_id integer,
    requested_by_name character varying(255),
    workflow_instance_id character varying(255),
    notes text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: TABLE audit_evidence_requests; Type: COMMENT; Schema: Risk_Assess_Framework; Owner: -
--

COMMENT ON TABLE "Risk_Assess_Framework".audit_evidence_requests IS 'Evidence or document requests issued during audit execution';


--
-- Name: COLUMN audit_evidence_requests.priority; Type: COMMENT; Schema: Risk_Assess_Framework; Owner: -
--

COMMENT ON COLUMN "Risk_Assess_Framework".audit_evidence_requests.priority IS '1=High, 2=Medium, 3=Low';


--
-- Name: audit_evidence_requests_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".audit_evidence_requests_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: audit_evidence_requests_id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Assess_Framework; Owner: -
--

ALTER SEQUENCE "Risk_Assess_Framework".audit_evidence_requests_id_seq OWNED BY "Risk_Assess_Framework".audit_evidence_requests.id;


--
-- Name: audit_finance_finalization; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".audit_finance_finalization (
    id bigint NOT NULL,
    reference_id integer NOT NULL,
    active_mapping_profile_id integer,
    active_rule_package_id integer,
    overall_conclusion text,
    recommendation_summary text,
    release_readiness_status character varying(100) DEFAULT 'In Preparation'::character varying NOT NULL,
    draft_statement_status character varying(100) DEFAULT 'Not Generated'::character varying NOT NULL,
    outstanding_items text,
    reviewer_notes text,
    ready_for_release boolean DEFAULT false NOT NULL,
    last_generated_statement_year integer,
    last_generated_at timestamp without time zone,
    updated_by_user_id integer,
    updated_by_name character varying(255),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


--
-- Name: audit_finance_finalization_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".audit_finance_finalization_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: audit_finance_finalization_id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Assess_Framework; Owner: -
--

ALTER SEQUENCE "Risk_Assess_Framework".audit_finance_finalization_id_seq OWNED BY "Risk_Assess_Framework".audit_finance_finalization.id;


--
-- Name: audit_financial_statement_mapping_profiles; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".audit_financial_statement_mapping_profiles (
    id integer NOT NULL,
    reference_id integer,
    engagement_type_id integer,
    rule_package_id integer,
    profile_code character varying(150) NOT NULL,
    profile_name character varying(255) NOT NULL,
    entity_type character varying(150),
    industry_name character varying(255),
    notes text,
    is_reusable boolean DEFAULT false NOT NULL,
    is_default boolean DEFAULT false NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    created_by_user_id integer,
    created_by_name character varying(255),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


--
-- Name: audit_financial_statement_mapping_profiles_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".audit_financial_statement_mapping_profiles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: audit_financial_statement_mapping_profiles_id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Assess_Framework; Owner: -
--

ALTER SEQUENCE "Risk_Assess_Framework".audit_financial_statement_mapping_profiles_id_seq OWNED BY "Risk_Assess_Framework".audit_financial_statement_mapping_profiles.id;


--
-- Name: audit_financial_statement_mappings; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".audit_financial_statement_mappings (
    id bigint NOT NULL,
    reference_id integer NOT NULL,
    fiscal_year integer NOT NULL,
    mapping_profile_id integer,
    account_number character varying(100) NOT NULL,
    account_name character varying(255),
    fsli character varying(255),
    business_unit character varying(255),
    current_balance numeric(18,2) DEFAULT 0 NOT NULL,
    statement_type character varying(100),
    section_name character varying(255),
    line_name character varying(255),
    classification character varying(100),
    display_order integer DEFAULT 100 NOT NULL,
    notes text,
    is_auto_mapped boolean DEFAULT true NOT NULL,
    is_reviewed boolean DEFAULT false NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


--
-- Name: audit_financial_statement_mappings_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".audit_financial_statement_mappings_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: audit_financial_statement_mappings_id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Assess_Framework; Owner: -
--

ALTER SEQUENCE "Risk_Assess_Framework".audit_financial_statement_mappings_id_seq OWNED BY "Risk_Assess_Framework".audit_financial_statement_mappings.id;


--
-- Name: audit_financial_statement_profile_rules; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".audit_financial_statement_profile_rules (
    id bigint NOT NULL,
    mapping_profile_id integer NOT NULL,
    account_number character varying(100) NOT NULL,
    account_name character varying(255),
    fsli character varying(255),
    statement_type character varying(100) NOT NULL,
    section_name character varying(255) NOT NULL,
    line_name character varying(255) NOT NULL,
    classification character varying(100),
    display_order integer DEFAULT 100 NOT NULL,
    notes text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


--
-- Name: audit_financial_statement_profile_rules_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".audit_financial_statement_profile_rules_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: audit_financial_statement_profile_rules_id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Assess_Framework; Owner: -
--

ALTER SEQUENCE "Risk_Assess_Framework".audit_financial_statement_profile_rules_id_seq OWNED BY "Risk_Assess_Framework".audit_financial_statement_profile_rules.id;


--
-- Name: audit_findings; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".audit_findings (
    id integer NOT NULL,
    reference_id integer,
    audit_universe_id integer,
    finding_number character varying(50),
    finding_title character varying(500) NOT NULL,
    finding_description text,
    severity_id integer DEFAULT 3,
    status_id integer DEFAULT 1,
    identified_date date DEFAULT CURRENT_DATE NOT NULL,
    due_date date,
    closed_date date,
    assigned_to character varying(255),
    assigned_to_user_id integer,
    root_cause text,
    business_impact text,
    created_by_user_id integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: TABLE audit_findings; Type: COMMENT; Schema: Risk_Assess_Framework; Owner: -
--

COMMENT ON TABLE "Risk_Assess_Framework".audit_findings IS 'Audit findings identified during risk assessments';


--
-- Name: COLUMN audit_findings.finding_number; Type: COMMENT; Schema: Risk_Assess_Framework; Owner: -
--

COMMENT ON COLUMN "Risk_Assess_Framework".audit_findings.finding_number IS 'Auto-generated unique finding identifier';


--
-- Name: COLUMN audit_findings.root_cause; Type: COMMENT; Schema: Risk_Assess_Framework; Owner: -
--

COMMENT ON COLUMN "Risk_Assess_Framework".audit_findings.root_cause IS 'Root cause analysis of the finding';


--
-- Name: COLUMN audit_findings.business_impact; Type: COMMENT; Schema: Risk_Assess_Framework; Owner: -
--

COMMENT ON COLUMN "Risk_Assess_Framework".audit_findings.business_impact IS 'Description of the business impact if unaddressed';


--
-- Name: audit_findings_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".audit_findings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: audit_findings_id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Assess_Framework; Owner: -
--

ALTER SEQUENCE "Risk_Assess_Framework".audit_findings_id_seq OWNED BY "Risk_Assess_Framework".audit_findings.id;


--
-- Name: audit_gl_journal_entries; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".audit_gl_journal_entries (
    id bigint NOT NULL,
    import_batch_id integer,
    reference_id integer,
    company_code character varying(50),
    fiscal_year integer NOT NULL,
    fiscal_period integer,
    posting_date date NOT NULL,
    document_date date,
    journal_number character varying(100) NOT NULL,
    line_number integer DEFAULT 1 NOT NULL,
    account_number character varying(100),
    account_name character varying(255),
    fsli character varying(255),
    business_unit character varying(255),
    cost_center character varying(100),
    user_id character varying(100),
    user_name character varying(255),
    description text,
    amount numeric(18,2) DEFAULT 0 NOT NULL,
    debit_amount numeric(18,2),
    credit_amount numeric(18,2),
    currency_code character varying(10),
    source_system character varying(100),
    source_document_number character varying(100),
    is_manual boolean DEFAULT false NOT NULL,
    is_period_end boolean DEFAULT false NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


--
-- Name: audit_gl_journal_entries_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".audit_gl_journal_entries_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: audit_gl_journal_entries_id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Assess_Framework; Owner: -
--

ALTER SEQUENCE "Risk_Assess_Framework".audit_gl_journal_entries_id_seq OWNED BY "Risk_Assess_Framework".audit_gl_journal_entries.id;


--
-- Name: audit_holiday_calendar; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".audit_holiday_calendar (
    id integer NOT NULL,
    holiday_date date NOT NULL,
    holiday_name character varying(255) NOT NULL,
    country_code character varying(10),
    region_code character varying(50),
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


--
-- Name: audit_holiday_calendar_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".audit_holiday_calendar_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: audit_holiday_calendar_id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Assess_Framework; Owner: -
--

ALTER SEQUENCE "Risk_Assess_Framework".audit_holiday_calendar_id_seq OWNED BY "Risk_Assess_Framework".audit_holiday_calendar.id;


--
-- Name: audit_industry_benchmarks; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".audit_industry_benchmarks (
    id bigint NOT NULL,
    import_batch_id integer,
    reference_id integer,
    fiscal_year integer NOT NULL,
    industry_code character varying(100),
    industry_name character varying(255),
    metric_name character varying(255) NOT NULL,
    unit_of_measure character varying(50),
    company_value numeric(18,4) DEFAULT 0 NOT NULL,
    benchmark_median numeric(18,4) DEFAULT 0 NOT NULL,
    benchmark_lower_quartile numeric(18,4),
    benchmark_upper_quartile numeric(18,4),
    benchmark_source character varying(255),
    notes text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


--
-- Name: audit_industry_benchmarks_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".audit_industry_benchmarks_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: audit_industry_benchmarks_id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Assess_Framework; Owner: -
--

ALTER SEQUENCE "Risk_Assess_Framework".audit_industry_benchmarks_id_seq OWNED BY "Risk_Assess_Framework".audit_industry_benchmarks.id;


--
-- Name: audit_login_events; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".audit_login_events (
    id bigint NOT NULL,
    user_id integer,
    username character varying(255),
    display_name character varying(255),
    event_type character varying(50) DEFAULT 'Login'::character varying NOT NULL,
    status character varying(50) DEFAULT 'Success'::character varying NOT NULL,
    ip_address character varying(100),
    user_agent text,
    client_context character varying(100),
    failure_reason text,
    correlation_id character varying(255),
    occurred_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: TABLE audit_login_events; Type: COMMENT; Schema: Risk_Assess_Framework; Owner: -
--

COMMENT ON TABLE "Risk_Assess_Framework".audit_login_events IS 'Authentication and session lifecycle log for auditability of platform access.';


--
-- Name: audit_login_events_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".audit_login_events_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: audit_login_events_id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Assess_Framework; Owner: -
--

ALTER SEQUENCE "Risk_Assess_Framework".audit_login_events_id_seq OWNED BY "Risk_Assess_Framework".audit_login_events.id;


--
-- Name: audit_management_actions; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".audit_management_actions (
    id integer NOT NULL,
    reference_id integer NOT NULL,
    finding_id integer,
    recommendation_id integer,
    action_title character varying(500) NOT NULL,
    action_description text,
    owner_name character varying(255),
    owner_user_id integer,
    due_date date,
    status character varying(100) DEFAULT 'Open'::character varying,
    progress_percent integer DEFAULT 0,
    management_response text,
    closure_notes text,
    validated_by_name character varying(255),
    validated_by_user_id integer,
    validated_at date,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: audit_management_actions_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".audit_management_actions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: audit_management_actions_id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Assess_Framework; Owner: -
--

ALTER SEQUENCE "Risk_Assess_Framework".audit_management_actions_id_seq OWNED BY "Risk_Assess_Framework".audit_management_actions.id;


--
-- Name: audit_materiality_approval_history; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".audit_materiality_approval_history (
    id bigint NOT NULL,
    reference_id integer NOT NULL,
    previous_calculation_id bigint,
    calculation_id bigint NOT NULL,
    benchmark_profile_id integer,
    action_type character varying(100) DEFAULT 'activated'::character varying NOT NULL,
    action_label character varying(255),
    benchmark_code character varying(100),
    benchmark_name character varying(255),
    percentage_applied numeric(9,4) DEFAULT 0 NOT NULL,
    performance_percentage_applied numeric(9,4) DEFAULT 0 NOT NULL,
    clearly_trivial_percentage_applied numeric(9,4) DEFAULT 0 NOT NULL,
    overall_materiality numeric(18,2) DEFAULT 0 NOT NULL,
    performance_materiality numeric(18,2) DEFAULT 0 NOT NULL,
    clearly_trivial_threshold numeric(18,2) DEFAULT 0 NOT NULL,
    entity_type character varying(150),
    industry_name character varying(255),
    benchmark_selection_rationale text,
    override_reason text,
    approved_by_user_id integer,
    approved_by_name character varying(255),
    approved_at timestamp without time zone,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


--
-- Name: audit_materiality_approval_history_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".audit_materiality_approval_history_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: audit_materiality_approval_history_id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Assess_Framework; Owner: -
--

ALTER SEQUENCE "Risk_Assess_Framework".audit_materiality_approval_history_id_seq OWNED BY "Risk_Assess_Framework".audit_materiality_approval_history.id;


--
-- Name: audit_materiality_benchmark_profiles; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".audit_materiality_benchmark_profiles (
    id integer NOT NULL,
    profile_code character varying(100) NOT NULL,
    profile_name character varying(255) NOT NULL,
    engagement_type_id integer,
    entity_type character varying(150),
    industry_name character varying(255),
    profit_before_tax_percentage numeric(9,4) DEFAULT 5 NOT NULL,
    revenue_percentage numeric(9,4) DEFAULT 1 NOT NULL,
    total_assets_percentage numeric(9,4) DEFAULT 1 NOT NULL,
    expenses_percentage numeric(9,4) DEFAULT 1 NOT NULL,
    performance_percentage numeric(9,4) DEFAULT 75 NOT NULL,
    clearly_trivial_percentage numeric(9,4) DEFAULT 5 NOT NULL,
    benchmark_rationale text,
    validation_status character varying(100) DEFAULT 'Pending auditor confirmation'::character varying NOT NULL,
    validation_notes text,
    approved_by_user_id integer,
    approved_by_name character varying(255),
    approved_at timestamp without time zone,
    is_default boolean DEFAULT false NOT NULL,
    sort_order integer DEFAULT 100 NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


--
-- Name: audit_materiality_benchmark_profiles_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".audit_materiality_benchmark_profiles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: audit_materiality_benchmark_profiles_id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Assess_Framework; Owner: -
--

ALTER SEQUENCE "Risk_Assess_Framework".audit_materiality_benchmark_profiles_id_seq OWNED BY "Risk_Assess_Framework".audit_materiality_benchmark_profiles.id;


--
-- Name: audit_materiality_calculations; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".audit_materiality_calculations (
    id bigint NOT NULL,
    reference_id integer NOT NULL,
    fiscal_year integer,
    candidate_id bigint,
    benchmark_code character varying(100) NOT NULL,
    benchmark_name character varying(255) NOT NULL,
    benchmark_source character varying(100) DEFAULT 'trial_balance'::character varying NOT NULL,
    source_table character varying(100),
    benchmark_amount numeric(18,2) DEFAULT 0 NOT NULL,
    percentage_applied numeric(9,4) DEFAULT 0 NOT NULL,
    overall_materiality numeric(18,2) DEFAULT 0 NOT NULL,
    performance_percentage_applied numeric(9,4) DEFAULT 75 NOT NULL,
    performance_materiality numeric(18,2) DEFAULT 0 NOT NULL,
    clearly_trivial_percentage_applied numeric(9,4) DEFAULT 5 NOT NULL,
    clearly_trivial_threshold numeric(18,2) DEFAULT 0 NOT NULL,
    calculation_summary character varying(500),
    rationale text,
    is_active boolean DEFAULT false NOT NULL,
    is_manual_override boolean DEFAULT false NOT NULL,
    approved_by_user_id integer,
    approved_by_name character varying(255),
    approved_at timestamp without time zone,
    created_by_user_id integer,
    created_by_name character varying(255),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    benchmark_profile_id integer,
    entity_type character varying(150),
    industry_name character varying(255),
    benchmark_selection_rationale text
);


--
-- Name: audit_materiality_calculations_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".audit_materiality_calculations_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: audit_materiality_calculations_id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Assess_Framework; Owner: -
--

ALTER SEQUENCE "Risk_Assess_Framework".audit_materiality_calculations_id_seq OWNED BY "Risk_Assess_Framework".audit_materiality_calculations.id;


--
-- Name: audit_materiality_candidates; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".audit_materiality_candidates (
    id bigint NOT NULL,
    reference_id integer NOT NULL,
    fiscal_year integer,
    candidate_code character varying(100) NOT NULL,
    candidate_name character varying(255) NOT NULL,
    benchmark_source character varying(100) DEFAULT 'trial_balance'::character varying NOT NULL,
    source_table character varying(100),
    source_metric_label character varying(255),
    benchmark_amount numeric(18,2) DEFAULT 0 NOT NULL,
    recommended_percentage numeric(9,4) DEFAULT 0 NOT NULL,
    recommended_overall_materiality numeric(18,2) DEFAULT 0 NOT NULL,
    recommended_performance_percentage numeric(9,4) DEFAULT 75 NOT NULL,
    recommended_performance_materiality numeric(18,2) DEFAULT 0 NOT NULL,
    recommended_clearly_trivial_percentage numeric(9,4) DEFAULT 5 NOT NULL,
    recommended_clearly_trivial_threshold numeric(18,2) DEFAULT 0 NOT NULL,
    notes text,
    is_selected boolean DEFAULT false NOT NULL,
    selected_calculation_id bigint,
    generated_by_user_id integer,
    generated_by_name character varying(255),
    generated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    benchmark_profile_id integer,
    entity_type character varying(150),
    industry_name character varying(255)
);


--
-- Name: audit_materiality_candidates_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".audit_materiality_candidates_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: audit_materiality_candidates_id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Assess_Framework; Owner: -
--

ALTER SEQUENCE "Risk_Assess_Framework".audit_materiality_candidates_id_seq OWNED BY "Risk_Assess_Framework".audit_materiality_candidates.id;


--
-- Name: audit_materiality_scope_links; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".audit_materiality_scope_links (
    id bigint NOT NULL,
    reference_id integer NOT NULL,
    materiality_calculation_id bigint NOT NULL,
    scope_item_id integer,
    fsli character varying(255),
    benchmark_relevance character varying(255),
    inclusion_reason text,
    is_above_threshold boolean DEFAULT false NOT NULL,
    coverage_percent numeric(9,2),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


--
-- Name: audit_materiality_scope_links_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".audit_materiality_scope_links_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: audit_materiality_scope_links_id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Assess_Framework; Owner: -
--

ALTER SEQUENCE "Risk_Assess_Framework".audit_materiality_scope_links_id_seq OWNED BY "Risk_Assess_Framework".audit_materiality_scope_links.id;


--
-- Name: audit_misstatements; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".audit_misstatements (
    id bigint NOT NULL,
    reference_id integer NOT NULL,
    finding_id integer,
    materiality_calculation_id bigint,
    fsli character varying(255),
    account_number character varying(100),
    transaction_identifier character varying(255),
    description text NOT NULL,
    actual_amount numeric(18,2) DEFAULT 0 NOT NULL,
    projected_amount numeric(18,2),
    evaluation_basis character varying(100),
    exceeds_clearly_trivial boolean DEFAULT false NOT NULL,
    exceeds_performance_materiality boolean DEFAULT false NOT NULL,
    exceeds_overall_materiality boolean DEFAULT false NOT NULL,
    status character varying(100) DEFAULT 'Open'::character varying NOT NULL,
    created_by_user_id integer,
    created_by_name character varying(255),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


--
-- Name: audit_misstatements_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".audit_misstatements_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: audit_misstatements_id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Assess_Framework; Owner: -
--

ALTER SEQUENCE "Risk_Assess_Framework".audit_misstatements_id_seq OWNED BY "Risk_Assess_Framework".audit_misstatements.id;


--
-- Name: audit_notifications; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".audit_notifications (
    id integer NOT NULL,
    reference_id integer,
    entity_type character varying(100) NOT NULL,
    entity_id integer,
    workflow_instance_id character varying(255),
    notification_type character varying(100) DEFAULT 'Workflow'::character varying,
    severity character varying(50) DEFAULT 'Info'::character varying,
    title character varying(255) NOT NULL,
    message text,
    recipient_user_id integer,
    recipient_name character varying(255),
    is_read boolean DEFAULT false,
    read_at timestamp without time zone,
    action_url character varying(500),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: audit_notifications_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".audit_notifications_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: audit_notifications_id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Assess_Framework; Owner: -
--

ALTER SEQUENCE "Risk_Assess_Framework".audit_notifications_id_seq OWNED BY "Risk_Assess_Framework".audit_notifications.id;


--
-- Name: audit_procedure_assignments; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".audit_procedure_assignments (
    id integer NOT NULL,
    procedure_id integer NOT NULL,
    procedure_step_id integer,
    reference_id integer,
    scope_item_id integer,
    risk_control_matrix_id integer,
    walkthrough_id integer,
    working_paper_id integer,
    assignment_type character varying(100) DEFAULT 'Primary'::character varying NOT NULL,
    status character varying(100) DEFAULT 'Assigned'::character varying NOT NULL,
    assigned_to_user_id integer,
    assigned_to_name character varying(255),
    assigned_by_user_id integer,
    assigned_by_name character varying(255),
    due_date timestamp without time zone,
    notes text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: TABLE audit_procedure_assignments; Type: COMMENT; Schema: Risk_Assess_Framework; Owner: -
--

COMMENT ON TABLE "Risk_Assess_Framework".audit_procedure_assignments IS 'Links procedures or specific procedure steps to scope, RCM, walkthrough, or working-paper execution context.';


--
-- Name: audit_procedure_assignments_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".audit_procedure_assignments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: audit_procedure_assignments_id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Assess_Framework; Owner: -
--

ALTER SEQUENCE "Risk_Assess_Framework".audit_procedure_assignments_id_seq OWNED BY "Risk_Assess_Framework".audit_procedure_assignments.id;


--
-- Name: audit_procedure_steps; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".audit_procedure_steps (
    id integer NOT NULL,
    procedure_id integer NOT NULL,
    step_number integer NOT NULL,
    step_title character varying(255) NOT NULL,
    instruction_text text,
    expected_result text,
    sample_guidance text,
    is_mandatory boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: TABLE audit_procedure_steps; Type: COMMENT; Schema: Risk_Assess_Framework; Owner: -
--

COMMENT ON TABLE "Risk_Assess_Framework".audit_procedure_steps IS 'Ordered steps that define how a procedure should be executed.';


--
-- Name: audit_procedure_steps_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".audit_procedure_steps_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: audit_procedure_steps_id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Assess_Framework; Owner: -
--

ALTER SEQUENCE "Risk_Assess_Framework".audit_procedure_steps_id_seq OWNED BY "Risk_Assess_Framework".audit_procedure_steps.id;


--
-- Name: audit_procedures; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".audit_procedures (
    id integer NOT NULL,
    reference_id integer,
    audit_universe_id integer,
    procedure_code character varying(50),
    procedure_title character varying(500) NOT NULL,
    objective text,
    procedure_description text,
    procedure_type_id integer DEFAULT 1,
    status_id integer DEFAULT 1,
    sample_size integer,
    expected_evidence text,
    working_paper_ref character varying(100),
    owner character varying(255),
    performer_user_id integer,
    reviewer_user_id integer,
    planned_date date,
    performed_date date,
    reviewed_date date,
    conclusion text,
    notes text,
    is_template boolean DEFAULT false,
    source_template_id integer,
    created_by_user_id integer,
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    applicable_engagement_type_id integer,
    template_pack character varying(150),
    template_tags text
);


--
-- Name: TABLE audit_procedures; Type: COMMENT; Schema: Risk_Assess_Framework; Owner: -
--

COMMENT ON TABLE "Risk_Assess_Framework".audit_procedures IS 'Reusable audit procedure library templates and engagement-linked procedures';


--
-- Name: COLUMN audit_procedures.is_template; Type: COMMENT; Schema: Risk_Assess_Framework; Owner: -
--

COMMENT ON COLUMN "Risk_Assess_Framework".audit_procedures.is_template IS 'True when the record is a reusable library procedure';


--
-- Name: COLUMN audit_procedures.source_template_id; Type: COMMENT; Schema: Risk_Assess_Framework; Owner: -
--

COMMENT ON COLUMN "Risk_Assess_Framework".audit_procedures.source_template_id IS 'Original library template used to create this procedure';


--
-- Name: audit_procedures_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".audit_procedures_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: audit_procedures_id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Assess_Framework; Owner: -
--

ALTER SEQUENCE "Risk_Assess_Framework".audit_procedures_id_seq OWNED BY "Risk_Assess_Framework".audit_procedures.id;


--
-- Name: audit_project_collaborators; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".audit_project_collaborators (
    id integer NOT NULL,
    project_id integer NOT NULL,
    user_id integer NOT NULL,
    collaborator_role_id integer,
    can_edit boolean DEFAULT true NOT NULL,
    can_review boolean DEFAULT false NOT NULL,
    can_upload_evidence boolean DEFAULT true NOT NULL,
    can_manage_access boolean DEFAULT false NOT NULL,
    notes text,
    assigned_by_user_id integer,
    assigned_by_name character varying(255),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: audit_project_collaborators_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".audit_project_collaborators_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: audit_project_collaborators_id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Assess_Framework; Owner: -
--

ALTER SEQUENCE "Risk_Assess_Framework".audit_project_collaborators_id_seq OWNED BY "Risk_Assess_Framework".audit_project_collaborators.id;


--
-- Name: audit_reasonability_forecasts; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".audit_reasonability_forecasts (
    id bigint NOT NULL,
    import_batch_id integer,
    reference_id integer,
    fiscal_year integer NOT NULL,
    fiscal_period integer,
    metric_name character varying(255) NOT NULL,
    metric_category character varying(100),
    forecast_basis character varying(100),
    actual_value numeric(18,2) DEFAULT 0 NOT NULL,
    expected_value numeric(18,2) DEFAULT 0 NOT NULL,
    budget_value numeric(18,2),
    prior_year_value numeric(18,2),
    threshold_amount numeric(18,2),
    threshold_percent numeric(9,2),
    explanation text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


--
-- Name: audit_reasonability_forecasts_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".audit_reasonability_forecasts_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: audit_reasonability_forecasts_id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Assess_Framework; Owner: -
--

ALTER SEQUENCE "Risk_Assess_Framework".audit_reasonability_forecasts_id_seq OWNED BY "Risk_Assess_Framework".audit_reasonability_forecasts.id;


--
-- Name: audit_recommendations; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".audit_recommendations (
    id integer NOT NULL,
    finding_id integer NOT NULL,
    recommendation_number character varying(50),
    recommendation text NOT NULL,
    priority integer DEFAULT 2,
    management_response text,
    agreed_date date,
    target_date date,
    implementation_date date,
    responsible_person character varying(255),
    responsible_user_id integer,
    status_id integer DEFAULT 1,
    verification_notes text,
    verified_by_user_id integer,
    verified_date date,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: TABLE audit_recommendations; Type: COMMENT; Schema: Risk_Assess_Framework; Owner: -
--

COMMENT ON TABLE "Risk_Assess_Framework".audit_recommendations IS 'Recommendations/action plans for audit findings';


--
-- Name: COLUMN audit_recommendations.priority; Type: COMMENT; Schema: Risk_Assess_Framework; Owner: -
--

COMMENT ON COLUMN "Risk_Assess_Framework".audit_recommendations.priority IS '1=High, 2=Medium, 3=Low priority';


--
-- Name: audit_recommendations_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".audit_recommendations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: audit_recommendations_id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Assess_Framework; Owner: -
--

ALTER SEQUENCE "Risk_Assess_Framework".audit_recommendations_id_seq OWNED BY "Risk_Assess_Framework".audit_recommendations.id;


--
-- Name: audit_reference_collaborators; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".audit_reference_collaborators (
    id integer NOT NULL,
    reference_id integer NOT NULL,
    user_id integer NOT NULL,
    collaborator_role_id integer,
    can_edit boolean DEFAULT true NOT NULL,
    can_review boolean DEFAULT false NOT NULL,
    can_upload_evidence boolean DEFAULT true NOT NULL,
    can_manage_access boolean DEFAULT false NOT NULL,
    notes text,
    assigned_by_user_id integer,
    assigned_by_name character varying(255),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: audit_reference_collaborators_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".audit_reference_collaborators_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: audit_reference_collaborators_id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Assess_Framework; Owner: -
--

ALTER SEQUENCE "Risk_Assess_Framework".audit_reference_collaborators_id_seq OWNED BY "Risk_Assess_Framework".audit_reference_collaborators.id;


--
-- Name: audit_retention_policies; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".audit_retention_policies (
    id integer NOT NULL,
    policy_name character varying(255) NOT NULL,
    entity_type character varying(100) NOT NULL,
    retention_days integer NOT NULL,
    archive_action character varying(100) DEFAULT 'Archive'::character varying NOT NULL,
    is_enabled boolean DEFAULT true NOT NULL,
    notes text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


--
-- Name: audit_retention_policies_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".audit_retention_policies_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: audit_retention_policies_id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Assess_Framework; Owner: -
--

ALTER SEQUENCE "Risk_Assess_Framework".audit_retention_policies_id_seq OWNED BY "Risk_Assess_Framework".audit_retention_policies.id;


--
-- Name: audit_review_notes; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".audit_review_notes (
    id integer NOT NULL,
    review_id integer NOT NULL,
    working_paper_section_id integer,
    note_type character varying(100) DEFAULT 'Review Note'::character varying NOT NULL,
    severity character varying(50) DEFAULT 'Medium'::character varying NOT NULL,
    status character varying(100) DEFAULT 'Open'::character varying NOT NULL,
    note_text text NOT NULL,
    response_text text,
    raised_by_user_id integer,
    raised_by_name character varying(255),
    raised_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    cleared_by_user_id integer,
    cleared_by_name character varying(255),
    cleared_at timestamp without time zone
);


--
-- Name: TABLE audit_review_notes; Type: COMMENT; Schema: Risk_Assess_Framework; Owner: -
--

COMMENT ON TABLE "Risk_Assess_Framework".audit_review_notes IS 'Notes, exceptions, and rework comments raised during reviews.';


--
-- Name: audit_review_notes_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".audit_review_notes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: audit_review_notes_id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Assess_Framework; Owner: -
--

ALTER SEQUENCE "Risk_Assess_Framework".audit_review_notes_id_seq OWNED BY "Risk_Assess_Framework".audit_review_notes.id;


--
-- Name: audit_reviews; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".audit_reviews (
    id integer NOT NULL,
    reference_id integer,
    entity_type character varying(100) NOT NULL,
    entity_id integer NOT NULL,
    review_type character varying(100) DEFAULT 'Manager Review'::character varying NOT NULL,
    status character varying(100) DEFAULT 'Open'::character varying NOT NULL,
    task_id integer,
    workflow_instance_id character varying(255),
    assigned_reviewer_user_id integer,
    assigned_reviewer_name character varying(255),
    requested_by_user_id integer,
    requested_by_name character varying(255),
    requested_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    due_date timestamp without time zone,
    completed_at timestamp without time zone,
    completed_by_user_id integer,
    summary text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: TABLE audit_reviews; Type: COMMENT; Schema: Risk_Assess_Framework; Owner: -
--

COMMENT ON TABLE "Risk_Assess_Framework".audit_reviews IS 'Generic review records for working papers, findings, procedures, planning packs, and report packs.';


--
-- Name: audit_reviews_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".audit_reviews_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: audit_reviews_id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Assess_Framework; Owner: -
--

ALTER SEQUENCE "Risk_Assess_Framework".audit_reviews_id_seq OWNED BY "Risk_Assess_Framework".audit_reviews.id;


--
-- Name: audit_risk_control_matrix; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".audit_risk_control_matrix (
    id integer NOT NULL,
    reference_id integer NOT NULL,
    scope_item_id integer,
    procedure_id integer,
    risk_title character varying(500) NOT NULL,
    risk_description text,
    control_name character varying(500) NOT NULL,
    control_description text,
    control_adequacy character varying(100),
    control_effectiveness character varying(100),
    control_classification_id integer,
    control_type_id integer,
    control_frequency_id integer,
    control_owner character varying(255),
    notes text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: audit_risk_control_matrix_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".audit_risk_control_matrix_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: audit_risk_control_matrix_id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Assess_Framework; Owner: -
--

ALTER SEQUENCE "Risk_Assess_Framework".audit_risk_control_matrix_id_seq OWNED BY "Risk_Assess_Framework".audit_risk_control_matrix.id;


--
-- Name: audit_scope_items; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".audit_scope_items (
    id integer NOT NULL,
    plan_id integer NOT NULL,
    reference_id integer NOT NULL,
    business_unit character varying(255),
    process_name character varying(255),
    subprocess_name character varying(255),
    fsli character varying(255),
    scope_status character varying(100) DEFAULT 'Planned'::character varying,
    include_in_scope boolean DEFAULT true,
    risk_reference text,
    control_reference text,
    procedure_id integer,
    owner character varying(255),
    notes text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    assertions text,
    scoping_rationale text,
    materiality_relevance character varying(100),
    materiality_notes text
);


--
-- Name: audit_scope_items_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".audit_scope_items_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: audit_scope_items_id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Assess_Framework; Owner: -
--

ALTER SEQUENCE "Risk_Assess_Framework".audit_scope_items_id_seq OWNED BY "Risk_Assess_Framework".audit_scope_items.id;


--
-- Name: audit_signoffs; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".audit_signoffs (
    id integer NOT NULL,
    reference_id integer,
    entity_type character varying(100) NOT NULL,
    entity_id integer NOT NULL,
    review_id integer,
    workflow_instance_id character varying(255),
    signoff_type character varying(100) NOT NULL,
    signoff_level character varying(100),
    status character varying(100) DEFAULT 'Signed'::character varying NOT NULL,
    signed_by_user_id integer,
    signed_by_name character varying(255),
    signed_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    comment text
);


--
-- Name: TABLE audit_signoffs; Type: COMMENT; Schema: Risk_Assess_Framework; Owner: -
--

COMMENT ON TABLE "Risk_Assess_Framework".audit_signoffs IS 'Generic sign-off records across planning, execution, review, and reporting stages.';


--
-- Name: audit_signoffs_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".audit_signoffs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: audit_signoffs_id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Assess_Framework; Owner: -
--

ALTER SEQUENCE "Risk_Assess_Framework".audit_signoffs_id_seq OWNED BY "Risk_Assess_Framework".audit_signoffs.id;


--
-- Name: audit_substantive_support_requests; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".audit_substantive_support_requests (
    id bigint NOT NULL,
    reference_id integer NOT NULL,
    fiscal_year integer NOT NULL,
    source_type character varying(50) NOT NULL,
    source_record_id bigint,
    source_key character varying(255) NOT NULL,
    transaction_identifier character varying(255) NOT NULL,
    journal_number character varying(100),
    posting_date date,
    account_number character varying(100),
    account_name character varying(255),
    fsli character varying(255),
    amount numeric(18,2) DEFAULT 0 NOT NULL,
    description text,
    triage_reason character varying(255) NOT NULL,
    risk_flags text,
    support_status character varying(100) DEFAULT 'Requested'::character varying NOT NULL,
    support_summary text,
    linked_procedure_id integer,
    linked_walkthrough_id integer,
    linked_control_id integer,
    linked_finding_id integer,
    notes text,
    requested_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


--
-- Name: audit_substantive_support_requests_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".audit_substantive_support_requests_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: audit_substantive_support_requests_id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Assess_Framework; Owner: -
--

ALTER SEQUENCE "Risk_Assess_Framework".audit_substantive_support_requests_id_seq OWNED BY "Risk_Assess_Framework".audit_substantive_support_requests.id;


--
-- Name: audit_tasks; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".audit_tasks (
    id integer NOT NULL,
    reference_id integer,
    entity_type character varying(100) NOT NULL,
    entity_id integer,
    workflow_instance_id character varying(255),
    task_type character varying(100) DEFAULT 'Action'::character varying NOT NULL,
    title character varying(255) NOT NULL,
    description text,
    assigned_to_user_id integer,
    assigned_to_name character varying(255),
    assigned_by_user_id integer,
    assigned_by_name character varying(255),
    status character varying(100) DEFAULT 'Open'::character varying NOT NULL,
    priority character varying(50) DEFAULT 'Medium'::character varying NOT NULL,
    due_date timestamp without time zone,
    completed_at timestamp without time zone,
    completed_by_user_id integer,
    completion_notes text,
    source character varying(50) DEFAULT 'Manual'::character varying NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: TABLE audit_tasks; Type: COMMENT; Schema: Risk_Assess_Framework; Owner: -
--

COMMENT ON TABLE "Risk_Assess_Framework".audit_tasks IS 'Generic audit work items for manual or application-managed actions outside the Elsa task list.';


--
-- Name: audit_tasks_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".audit_tasks_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: audit_tasks_id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Assess_Framework; Owner: -
--

ALTER SEQUENCE "Risk_Assess_Framework".audit_tasks_id_seq OWNED BY "Risk_Assess_Framework".audit_tasks.id;


--
-- Name: audit_trail_entity_changes; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".audit_trail_entity_changes (
    id bigint NOT NULL,
    audit_trail_event_id bigint NOT NULL,
    field_name character varying(255) NOT NULL,
    old_value text,
    new_value text
);


--
-- Name: audit_trail_entity_changes_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".audit_trail_entity_changes_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: audit_trail_entity_changes_id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Assess_Framework; Owner: -
--

ALTER SEQUENCE "Risk_Assess_Framework".audit_trail_entity_changes_id_seq OWNED BY "Risk_Assess_Framework".audit_trail_entity_changes.id;


--
-- Name: audit_trail_events; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".audit_trail_events (
    id bigint NOT NULL,
    reference_id integer,
    entity_type character varying(100) NOT NULL,
    entity_id character varying(255),
    category character varying(50) DEFAULT 'Business'::character varying NOT NULL,
    action character varying(255) NOT NULL,
    summary text NOT NULL,
    performed_by_user_id integer,
    performed_by_name character varying(255),
    icon character varying(50),
    color character varying(20),
    workflow_instance_id character varying(255),
    correlation_id character varying(255),
    source character varying(50) DEFAULT 'Application'::character varying NOT NULL,
    details_json jsonb,
    event_time timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


--
-- Name: audit_trail_events_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".audit_trail_events_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: audit_trail_events_id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Assess_Framework; Owner: -
--

ALTER SEQUENCE "Risk_Assess_Framework".audit_trail_events_id_seq OWNED BY "Risk_Assess_Framework".audit_trail_events.id;


--
-- Name: audit_trial_balance_snapshots; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".audit_trial_balance_snapshots (
    id bigint NOT NULL,
    import_batch_id integer,
    reference_id integer,
    fiscal_year integer NOT NULL,
    period_label character varying(50),
    as_of_date date,
    account_number character varying(100) NOT NULL,
    account_name character varying(255),
    fsli character varying(255),
    business_unit character varying(255),
    current_balance numeric(18,2) DEFAULT 0 NOT NULL,
    currency_code character varying(10),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


--
-- Name: audit_trial_balance_snapshots_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".audit_trial_balance_snapshots_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: audit_trial_balance_snapshots_id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Assess_Framework; Owner: -
--

ALTER SEQUENCE "Risk_Assess_Framework".audit_trial_balance_snapshots_id_seq OWNED BY "Risk_Assess_Framework".audit_trial_balance_snapshots.id;


--
-- Name: audit_universe; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".audit_universe (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    code character varying(50) NOT NULL,
    parent_id integer,
    level integer DEFAULT 1 NOT NULL,
    level_name character varying(100),
    description text,
    risk_rating character varying(20) DEFAULT 'Medium'::character varying,
    last_audit_date date,
    next_audit_date date,
    audit_frequency_months integer DEFAULT 12,
    owner character varying(255),
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: TABLE audit_universe; Type: COMMENT; Schema: Risk_Assess_Framework; Owner: -
--

COMMENT ON TABLE "Risk_Assess_Framework".audit_universe IS 'Hierarchical structure of all auditable entities in the organization';


--
-- Name: COLUMN audit_universe.level; Type: COMMENT; Schema: Risk_Assess_Framework; Owner: -
--

COMMENT ON COLUMN "Risk_Assess_Framework".audit_universe.level IS '1=Entity, 2=Division, 3=Process, 4=Sub-Process';


--
-- Name: COLUMN audit_universe.level_name; Type: COMMENT; Schema: Risk_Assess_Framework; Owner: -
--

COMMENT ON COLUMN "Risk_Assess_Framework".audit_universe.level_name IS 'Human-readable name for this level in the hierarchy';


--
-- Name: COLUMN audit_universe.audit_frequency_months; Type: COMMENT; Schema: Risk_Assess_Framework; Owner: -
--

COMMENT ON COLUMN "Risk_Assess_Framework".audit_universe.audit_frequency_months IS 'How often this entity should be audited';


--
-- Name: audit_universe_department_link; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".audit_universe_department_link (
    id integer NOT NULL,
    audit_universe_id integer NOT NULL,
    department_id integer NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: TABLE audit_universe_department_link; Type: COMMENT; Schema: Risk_Assess_Framework; Owner: -
--

COMMENT ON TABLE "Risk_Assess_Framework".audit_universe_department_link IS 'Links audit universe nodes to departments for integrated risk tracking';


--
-- Name: audit_universe_department_link_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".audit_universe_department_link_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: audit_universe_department_link_id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Assess_Framework; Owner: -
--

ALTER SEQUENCE "Risk_Assess_Framework".audit_universe_department_link_id_seq OWNED BY "Risk_Assess_Framework".audit_universe_department_link.id;


--
-- Name: audit_universe_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".audit_universe_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: audit_universe_id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Assess_Framework; Owner: -
--

ALTER SEQUENCE "Risk_Assess_Framework".audit_universe_id_seq OWNED BY "Risk_Assess_Framework".audit_universe.id;


--
-- Name: audit_usage_events; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".audit_usage_events (
    id integer NOT NULL,
    module_name character varying(100) NOT NULL,
    feature_name character varying(100) NOT NULL,
    event_name character varying(100) NOT NULL,
    reference_id integer,
    performed_by_user_id integer,
    performed_by_name character varying(255),
    role_name character varying(100),
    session_id character varying(100),
    source character varying(100),
    metadata_json text,
    event_time timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


--
-- Name: audit_usage_events_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".audit_usage_events_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: audit_usage_events_id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Assess_Framework; Owner: -
--

ALTER SEQUENCE "Risk_Assess_Framework".audit_usage_events_id_seq OWNED BY "Risk_Assess_Framework".audit_usage_events.id;


--
-- Name: audit_walkthrough_exceptions; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".audit_walkthrough_exceptions (
    id integer NOT NULL,
    walkthrough_id integer NOT NULL,
    exception_title character varying(500) NOT NULL,
    exception_description text,
    severity character varying(100) DEFAULT 'Medium'::character varying,
    linked_finding_id integer,
    is_resolved boolean DEFAULT false,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: audit_walkthrough_exceptions_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".audit_walkthrough_exceptions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: audit_walkthrough_exceptions_id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Assess_Framework; Owner: -
--

ALTER SEQUENCE "Risk_Assess_Framework".audit_walkthrough_exceptions_id_seq OWNED BY "Risk_Assess_Framework".audit_walkthrough_exceptions.id;


--
-- Name: audit_walkthroughs; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".audit_walkthroughs (
    id integer NOT NULL,
    reference_id integer NOT NULL,
    scope_item_id integer,
    procedure_id integer,
    risk_control_matrix_id integer,
    process_name character varying(255) NOT NULL,
    walkthrough_date date,
    participants text,
    process_narrative text,
    evidence_summary text,
    control_design_conclusion text,
    notes text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: audit_walkthroughs_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".audit_walkthroughs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: audit_walkthroughs_id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Assess_Framework; Owner: -
--

ALTER SEQUENCE "Risk_Assess_Framework".audit_walkthroughs_id_seq OWNED BY "Risk_Assess_Framework".audit_walkthroughs.id;


--
-- Name: audit_workflow_events; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".audit_workflow_events (
    id integer NOT NULL,
    workflow_instance_id character varying(255) NOT NULL,
    reference_id integer,
    entity_type character varying(100) NOT NULL,
    entity_id integer,
    event_type character varying(100) NOT NULL,
    title character varying(255) NOT NULL,
    description text,
    actor_user_id integer,
    actor_name character varying(255),
    event_time timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    metadata_json text
);


--
-- Name: audit_workflow_events_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".audit_workflow_events_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: audit_workflow_events_id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Assess_Framework; Owner: -
--

ALTER SEQUENCE "Risk_Assess_Framework".audit_workflow_events_id_seq OWNED BY "Risk_Assess_Framework".audit_workflow_events.id;


--
-- Name: audit_workflow_instances; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".audit_workflow_instances (
    id integer NOT NULL,
    reference_id integer,
    entity_type character varying(100) NOT NULL,
    entity_id integer,
    workflow_definition_id character varying(255) NOT NULL,
    workflow_display_name character varying(255),
    workflow_instance_id character varying(255) NOT NULL,
    status character varying(100) DEFAULT 'Running'::character varying NOT NULL,
    current_activity_id character varying(255),
    current_activity_name character varying(255),
    started_by_user_id integer,
    started_by_name character varying(255),
    started_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    last_synced_at timestamp without time zone,
    completed_at timestamp without time zone,
    is_active boolean DEFAULT true,
    metadata_json text
);


--
-- Name: audit_workflow_instances_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".audit_workflow_instances_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: audit_workflow_instances_id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Assess_Framework; Owner: -
--

ALTER SEQUENCE "Risk_Assess_Framework".audit_workflow_instances_id_seq OWNED BY "Risk_Assess_Framework".audit_workflow_instances.id;


--
-- Name: audit_workflow_tasks; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".audit_workflow_tasks (
    id integer NOT NULL,
    workflow_instance_id character varying(255) NOT NULL,
    reference_id integer,
    entity_type character varying(100) NOT NULL,
    entity_id integer,
    task_title character varying(255) NOT NULL,
    task_description text,
    assignee_user_id integer,
    assignee_name character varying(255),
    status character varying(100) DEFAULT 'Pending'::character varying NOT NULL,
    priority character varying(50) DEFAULT 'Medium'::character varying,
    due_date timestamp without time zone,
    action_url character varying(500),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    completed_at timestamp without time zone,
    completed_by_user_id integer,
    completion_notes text,
    external_task_id character varying(255),
    external_task_source character varying(100)
);


--
-- Name: audit_workflow_tasks_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".audit_workflow_tasks_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: audit_workflow_tasks_id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Assess_Framework; Owner: -
--

ALTER SEQUENCE "Risk_Assess_Framework".audit_workflow_tasks_id_seq OWNED BY "Risk_Assess_Framework".audit_workflow_tasks.id;


--
-- Name: audit_working_paper_references; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".audit_working_paper_references (
    id integer NOT NULL,
    from_working_paper_id integer NOT NULL,
    to_working_paper_id integer NOT NULL,
    reference_type character varying(100) DEFAULT 'Supporting'::character varying,
    notes text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: audit_working_paper_references_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".audit_working_paper_references_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: audit_working_paper_references_id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Assess_Framework; Owner: -
--

ALTER SEQUENCE "Risk_Assess_Framework".audit_working_paper_references_id_seq OWNED BY "Risk_Assess_Framework".audit_working_paper_references.id;


--
-- Name: audit_working_paper_sections; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".audit_working_paper_sections (
    id integer NOT NULL,
    working_paper_id integer NOT NULL,
    section_order integer DEFAULT 1 NOT NULL,
    section_code character varying(50),
    section_title character varying(255) NOT NULL,
    section_type character varying(100) DEFAULT 'Narrative'::character varying NOT NULL,
    content_text text,
    is_required boolean DEFAULT true,
    prepared_by_user_id integer,
    review_status character varying(100) DEFAULT 'Draft'::character varying NOT NULL,
    last_reviewed_at timestamp without time zone,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: TABLE audit_working_paper_sections; Type: COMMENT; Schema: Risk_Assess_Framework; Owner: -
--

COMMENT ON TABLE "Risk_Assess_Framework".audit_working_paper_sections IS 'Structured sections within a working paper to support preparation, review, and sign-off at subsection level.';


--
-- Name: audit_working_paper_sections_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".audit_working_paper_sections_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: audit_working_paper_sections_id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Assess_Framework; Owner: -
--

ALTER SEQUENCE "Risk_Assess_Framework".audit_working_paper_sections_id_seq OWNED BY "Risk_Assess_Framework".audit_working_paper_sections.id;


--
-- Name: audit_working_paper_signoffs; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".audit_working_paper_signoffs (
    id integer NOT NULL,
    working_paper_id integer NOT NULL,
    action_type character varying(100) NOT NULL,
    signed_by_user_id integer,
    signed_by_name character varying(255),
    comment text,
    signed_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: audit_working_paper_signoffs_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".audit_working_paper_signoffs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: audit_working_paper_signoffs_id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Assess_Framework; Owner: -
--

ALTER SEQUENCE "Risk_Assess_Framework".audit_working_paper_signoffs_id_seq OWNED BY "Risk_Assess_Framework".audit_working_paper_signoffs.id;


--
-- Name: audit_working_papers; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".audit_working_papers (
    id integer NOT NULL,
    reference_id integer,
    audit_universe_id integer,
    procedure_id integer,
    working_paper_code character varying(50),
    title character varying(500) NOT NULL,
    objective text,
    description text,
    status_id integer DEFAULT 1,
    prepared_by character varying(255),
    prepared_by_user_id integer,
    reviewer_name character varying(255),
    reviewer_user_id integer,
    conclusion text,
    notes text,
    prepared_date date,
    reviewed_date date,
    is_template boolean DEFAULT false,
    source_template_id integer,
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    applicable_engagement_type_id integer,
    template_pack character varying(150),
    template_tags text
);


--
-- Name: TABLE audit_working_papers; Type: COMMENT; Schema: Risk_Assess_Framework; Owner: -
--

COMMENT ON TABLE "Risk_Assess_Framework".audit_working_papers IS 'Audit working papers and reusable working paper templates';


--
-- Name: COLUMN audit_working_papers.is_template; Type: COMMENT; Schema: Risk_Assess_Framework; Owner: -
--

COMMENT ON COLUMN "Risk_Assess_Framework".audit_working_papers.is_template IS 'True when the record is a reusable working paper template';


--
-- Name: COLUMN audit_working_papers.source_template_id; Type: COMMENT; Schema: Risk_Assess_Framework; Owner: -
--

COMMENT ON COLUMN "Risk_Assess_Framework".audit_working_papers.source_template_id IS 'Original template used to create this working paper';


--
-- Name: audit_working_papers_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".audit_working_papers_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: audit_working_papers_id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Assess_Framework; Owner: -
--

ALTER SEQUENCE "Risk_Assess_Framework".audit_working_papers_id_seq OWNED BY "Risk_Assess_Framework".audit_working_papers.id;


--
-- Name: auditlog_log_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".auditlog_log_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: auditlog; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".auditlog (
    log_id integer DEFAULT nextval('"Risk_Assess_Framework".auditlog_log_id_seq'::regclass) NOT NULL,
    user_id integer,
    activity_type character varying(255),
    audit_time timestamp without time zone,
    description character varying(255)
);


--
-- Name: authentication_user_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".authentication_user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: authentication; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".authentication (
    user_id integer DEFAULT nextval('"Risk_Assess_Framework".authentication_user_id_seq'::regclass) NOT NULL,
    method character varying(30),
    verification_code integer,
    expiry_date timestamp without time zone
);


--
-- Name: departments; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".departments (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    head character varying(255),
    risk_level_id integer DEFAULT 2,
    assessments integer DEFAULT 0,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: TABLE departments; Type: COMMENT; Schema: Risk_Assess_Framework; Owner: -
--

COMMENT ON TABLE "Risk_Assess_Framework".departments IS 'Organizational departments with risk assessment tracking';


--
-- Name: COLUMN departments.risk_level_id; Type: COMMENT; Schema: Risk_Assess_Framework; Owner: -
--

COMMENT ON COLUMN "Risk_Assess_Framework".departments.risk_level_id IS 'Foreign key to ra_risklevels table';


--
-- Name: COLUMN departments.assessments; Type: COMMENT; Schema: Risk_Assess_Framework; Owner: -
--

COMMENT ON COLUMN "Risk_Assess_Framework".departments.assessments IS 'Count of risk assessments associated with this department';


--
-- Name: departments_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".departments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: departments_id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Assess_Framework; Owner: -
--

ALTER SEQUENCE "Risk_Assess_Framework".departments_id_seq OWNED BY "Risk_Assess_Framework".departments.id;


--
-- Name: market_data; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".market_data (
    id integer NOT NULL,
    symbol character varying(50) NOT NULL,
    date_time timestamp without time zone NOT NULL,
    close_price numeric(18,6) NOT NULL,
    log_return double precision NOT NULL
);


--
-- Name: market_data_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".market_data_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: market_data_id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Assess_Framework; Owner: -
--

ALTER SEQUENCE "Risk_Assess_Framework".market_data_id_seq OWNED BY "Risk_Assess_Framework".market_data.id;


--
-- Name: permissions_permission_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".permissions_permission_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: permissions; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".permissions (
    permission_id integer DEFAULT nextval('"Risk_Assess_Framework".permissions_permission_id_seq'::regclass) NOT NULL,
    permission_name character varying(50) NOT NULL,
    permission_description character varying(255)
);


--
-- Name: projects; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".projects (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    description text,
    status_id integer DEFAULT 1,
    department_id integer,
    start_date date,
    end_date date,
    budget numeric(15,2),
    risk_level_id integer DEFAULT 2,
    manager character varying(255),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: TABLE projects; Type: COMMENT; Schema: Risk_Assess_Framework; Owner: -
--

COMMENT ON TABLE "Risk_Assess_Framework".projects IS 'Project portfolio with department assignment and risk tracking';


--
-- Name: COLUMN projects.status_id; Type: COMMENT; Schema: Risk_Assess_Framework; Owner: -
--

COMMENT ON COLUMN "Risk_Assess_Framework".projects.status_id IS 'Foreign key to ra_projectstatus table';


--
-- Name: COLUMN projects.department_id; Type: COMMENT; Schema: Risk_Assess_Framework; Owner: -
--

COMMENT ON COLUMN "Risk_Assess_Framework".projects.department_id IS 'Foreign key reference to departments table';


--
-- Name: COLUMN projects.risk_level_id; Type: COMMENT; Schema: Risk_Assess_Framework; Owner: -
--

COMMENT ON COLUMN "Risk_Assess_Framework".projects.risk_level_id IS 'Foreign key to ra_risklevels table';


--
-- Name: projects_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".projects_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: projects_id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Assess_Framework; Owner: -
--

ALTER SEQUENCE "Risk_Assess_Framework".projects_id_seq OWNED BY "Risk_Assess_Framework".projects.id;


--
-- Name: ra_assessmentstatus; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".ra_assessmentstatus (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    description text,
    sort_order integer,
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: ra_assessmentstatus_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".ra_assessmentstatus_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: ra_assessmentstatus_id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Assess_Framework; Owner: -
--

ALTER SEQUENCE "Risk_Assess_Framework".ra_assessmentstatus_id_seq OWNED BY "Risk_Assess_Framework".ra_assessmentstatus.id;


--
-- Name: ra_audit_collaborator_role; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".ra_audit_collaborator_role (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    description text,
    color character varying(20),
    is_client_role boolean DEFAULT false,
    sort_order integer,
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: ra_audit_collaborator_role_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".ra_audit_collaborator_role_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: ra_audit_collaborator_role_id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Assess_Framework; Owner: -
--

ALTER SEQUENCE "Risk_Assess_Framework".ra_audit_collaborator_role_id_seq OWNED BY "Risk_Assess_Framework".ra_audit_collaborator_role.id;


--
-- Name: ra_audit_universe_levels; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".ra_audit_universe_levels (
    id integer NOT NULL,
    level integer NOT NULL,
    name character varying(100) NOT NULL,
    description text,
    icon character varying(50),
    sort_order integer,
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: ra_audit_universe_levels_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".ra_audit_universe_levels_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: ra_audit_universe_levels_id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Assess_Framework; Owner: -
--

ALTER SEQUENCE "Risk_Assess_Framework".ra_audit_universe_levels_id_seq OWNED BY "Risk_Assess_Framework".ra_audit_universe_levels.id;


--
-- Name: ra_control_classification; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".ra_control_classification (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    description text,
    sort_order integer,
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: ra_control_classification_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".ra_control_classification_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: ra_control_classification_id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Assess_Framework; Owner: -
--

ALTER SEQUENCE "Risk_Assess_Framework".ra_control_classification_id_seq OWNED BY "Risk_Assess_Framework".ra_control_classification.id;


--
-- Name: ra_control_frequency; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".ra_control_frequency (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    description text,
    sort_order integer,
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: ra_control_frequency_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".ra_control_frequency_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: ra_control_frequency_id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Assess_Framework; Owner: -
--

ALTER SEQUENCE "Risk_Assess_Framework".ra_control_frequency_id_seq OWNED BY "Risk_Assess_Framework".ra_control_frequency.id;


--
-- Name: ra_control_type; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".ra_control_type (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    description text,
    sort_order integer,
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: ra_control_type_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".ra_control_type_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: ra_control_type_id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Assess_Framework; Owner: -
--

ALTER SEQUENCE "Risk_Assess_Framework".ra_control_type_id_seq OWNED BY "Risk_Assess_Framework".ra_control_type.id;


--
-- Name: ra_datafrequency_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".ra_datafrequency_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: ra_datafrequency; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".ra_datafrequency (
    id integer DEFAULT nextval('"Risk_Assess_Framework".ra_datafrequency_id_seq'::regclass) NOT NULL,
    description text NOT NULL,
    "position" integer
);


--
-- Name: ra_document_category; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".ra_document_category (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    description text,
    color character varying(20),
    sort_order integer,
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    is_sensitive boolean DEFAULT false,
    default_visibility_level_id integer,
    requires_security_approval boolean DEFAULT false,
    default_confidentiality_label character varying(150)
);


--
-- Name: ra_document_category_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".ra_document_category_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: ra_document_category_id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Assess_Framework; Owner: -
--

ALTER SEQUENCE "Risk_Assess_Framework".ra_document_category_id_seq OWNED BY "Risk_Assess_Framework".ra_document_category.id;


--
-- Name: ra_document_visibility_level; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".ra_document_visibility_level (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    description text,
    color character varying(20),
    is_restricted boolean DEFAULT false,
    sort_order integer,
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: ra_document_visibility_level_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".ra_document_visibility_level_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: ra_document_visibility_level_id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Assess_Framework; Owner: -
--

ALTER SEQUENCE "Risk_Assess_Framework".ra_document_visibility_level_id_seq OWNED BY "Risk_Assess_Framework".ra_document_visibility_level.id;


--
-- Name: ra_engagement_type; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".ra_engagement_type (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    description text,
    sort_order integer,
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: ra_engagement_type_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".ra_engagement_type_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: ra_engagement_type_id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Assess_Framework; Owner: -
--

ALTER SEQUENCE "Risk_Assess_Framework".ra_engagement_type_id_seq OWNED BY "Risk_Assess_Framework".ra_engagement_type.id;


--
-- Name: ra_evidence_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".ra_evidence_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: ra_evidence; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".ra_evidence (
    id integer DEFAULT nextval('"Risk_Assess_Framework".ra_evidence_id_seq'::regclass) NOT NULL,
    description text NOT NULL,
    "position" integer
);


--
-- Name: ra_evidence_request_status; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".ra_evidence_request_status (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    description text,
    color character varying(20),
    is_closed boolean DEFAULT false,
    sort_order integer,
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: ra_evidence_request_status_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".ra_evidence_request_status_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: ra_evidence_request_status_id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Assess_Framework; Owner: -
--

ALTER SEQUENCE "Risk_Assess_Framework".ra_evidence_request_status_id_seq OWNED BY "Risk_Assess_Framework".ra_evidence_request_status.id;


--
-- Name: ra_finding_severity; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".ra_finding_severity (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    description text,
    color character varying(20),
    sort_order integer,
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: ra_finding_severity_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".ra_finding_severity_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: ra_finding_severity_id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Assess_Framework; Owner: -
--

ALTER SEQUENCE "Risk_Assess_Framework".ra_finding_severity_id_seq OWNED BY "Risk_Assess_Framework".ra_finding_severity.id;


--
-- Name: ra_finding_status; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".ra_finding_status (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    description text,
    color character varying(20),
    is_closed boolean DEFAULT false,
    sort_order integer,
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: ra_finding_status_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".ra_finding_status_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: ra_finding_status_id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Assess_Framework; Owner: -
--

ALTER SEQUENCE "Risk_Assess_Framework".ra_finding_status_id_seq OWNED BY "Risk_Assess_Framework".ra_finding_status.id;


--
-- Name: ra_frequency_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".ra_frequency_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: ra_frequency; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".ra_frequency (
    id integer DEFAULT nextval('"Risk_Assess_Framework".ra_frequency_id_seq'::regclass) NOT NULL,
    description text NOT NULL,
    "position" integer
);


--
-- Name: ra_impact_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".ra_impact_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: ra_impact; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".ra_impact (
    id integer DEFAULT nextval('"Risk_Assess_Framework".ra_impact_id_seq'::regclass) NOT NULL,
    description text NOT NULL,
    "position" integer
);


--
-- Name: ra_keyriskfactors_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".ra_keyriskfactors_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: ra_keyriskfactors; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".ra_keyriskfactors (
    id integer DEFAULT nextval('"Risk_Assess_Framework".ra_keyriskfactors_id_seq'::regclass) NOT NULL,
    riskassessmentid integer,
    objectiveprocessesid integer,
    description character varying(250)
);


--
-- Name: ra_keysecondary_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".ra_keysecondary_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: ra_keysecondary; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".ra_keysecondary (
    id integer DEFAULT nextval('"Risk_Assess_Framework".ra_keysecondary_id_seq'::regclass) NOT NULL,
    description text NOT NULL,
    "position" integer
);


--
-- Name: ra_nature_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".ra_nature_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: ra_nature; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".ra_nature (
    id integer DEFAULT nextval('"Risk_Assess_Framework".ra_nature_id_seq'::regclass) NOT NULL,
    description text NOT NULL,
    "position" integer
);


--
-- Name: ra_objectiveprocesses_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".ra_objectiveprocesses_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: ra_objectiveprocesses; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".ra_objectiveprocesses (
    id integer DEFAULT nextval('"Risk_Assess_Framework".ra_objectiveprocesses_id_seq'::regclass) NOT NULL,
    riskassessmentid integer,
    description character varying(250)
);


--
-- Name: ra_outcomelikelihood_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".ra_outcomelikelihood_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: ra_outcomelikelihood; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".ra_outcomelikelihood (
    id integer DEFAULT nextval('"Risk_Assess_Framework".ra_outcomelikelihood_id_seq'::regclass) NOT NULL,
    description text NOT NULL,
    "position" integer
);


--
-- Name: ra_planning_status; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".ra_planning_status (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    description text,
    color character varying(20),
    is_closed boolean DEFAULT false,
    sort_order integer,
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: ra_planning_status_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".ra_planning_status_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: ra_planning_status_id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Assess_Framework; Owner: -
--

ALTER SEQUENCE "Risk_Assess_Framework".ra_planning_status_id_seq OWNED BY "Risk_Assess_Framework".ra_planning_status.id;


--
-- Name: ra_procedure_status; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".ra_procedure_status (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    description text,
    color character varying(20),
    is_closed boolean DEFAULT false,
    sort_order integer,
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: ra_procedure_status_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".ra_procedure_status_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: ra_procedure_status_id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Assess_Framework; Owner: -
--

ALTER SEQUENCE "Risk_Assess_Framework".ra_procedure_status_id_seq OWNED BY "Risk_Assess_Framework".ra_procedure_status.id;


--
-- Name: ra_procedure_type; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".ra_procedure_type (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    description text,
    color character varying(20),
    sort_order integer,
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: ra_procedure_type_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".ra_procedure_type_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: ra_procedure_type_id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Assess_Framework; Owner: -
--

ALTER SEQUENCE "Risk_Assess_Framework".ra_procedure_type_id_seq OWNED BY "Risk_Assess_Framework".ra_procedure_type.id;


--
-- Name: ra_projectstatus; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".ra_projectstatus (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    description text,
    sort_order integer,
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: ra_projectstatus_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".ra_projectstatus_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: ra_projectstatus_id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Assess_Framework; Owner: -
--

ALTER SEQUENCE "Risk_Assess_Framework".ra_projectstatus_id_seq OWNED BY "Risk_Assess_Framework".ra_projectstatus.id;


--
-- Name: ra_recommendation_status; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".ra_recommendation_status (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    description text,
    color character varying(20),
    sort_order integer,
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: ra_recommendation_status_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".ra_recommendation_status_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: ra_recommendation_status_id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Assess_Framework; Owner: -
--

ALTER SEQUENCE "Risk_Assess_Framework".ra_recommendation_status_id_seq OWNED BY "Risk_Assess_Framework".ra_recommendation_status.id;


--
-- Name: ra_referencestatus; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".ra_referencestatus (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    description text,
    sort_order integer,
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: ra_referencestatus_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".ra_referencestatus_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: ra_referencestatus_id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Assess_Framework; Owner: -
--

ALTER SEQUENCE "Risk_Assess_Framework".ra_referencestatus_id_seq OWNED BY "Risk_Assess_Framework".ra_referencestatus.id;


--
-- Name: ra_riskcategory_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".ra_riskcategory_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: ra_riskcategory; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".ra_riskcategory (
    id integer DEFAULT nextval('"Risk_Assess_Framework".ra_riskcategory_id_seq'::regclass) NOT NULL,
    description text NOT NULL,
    "position" integer
);


--
-- Name: ra_riskimpact_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".ra_riskimpact_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: ra_riskimpact; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".ra_riskimpact (
    id integer DEFAULT nextval('"Risk_Assess_Framework".ra_riskimpact_id_seq'::regclass) NOT NULL,
    description text NOT NULL,
    "position" integer
);


--
-- Name: ra_risklevels; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".ra_risklevels (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    description text,
    sort_order integer,
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: ra_risklevels_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".ra_risklevels_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: ra_risklevels_id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Assess_Framework; Owner: -
--

ALTER SEQUENCE "Risk_Assess_Framework".ra_risklevels_id_seq OWNED BY "Risk_Assess_Framework".ra_risklevels.id;


--
-- Name: ra_risklikelihood_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".ra_risklikelihood_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: ra_userroles; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".ra_userroles (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    description text,
    permissions jsonb,
    sort_order integer,
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: ra_userroles_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".ra_userroles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: ra_userroles_id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Assess_Framework; Owner: -
--

ALTER SEQUENCE "Risk_Assess_Framework".ra_userroles_id_seq OWNED BY "Risk_Assess_Framework".ra_userroles.id;


--
-- Name: ra_working_paper_status; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".ra_working_paper_status (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    description text,
    color character varying(20),
    is_closed boolean DEFAULT false,
    sort_order integer,
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: ra_working_paper_status_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".ra_working_paper_status_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: ra_working_paper_status_id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Assess_Framework; Owner: -
--

ALTER SEQUENCE "Risk_Assess_Framework".ra_working_paper_status_id_seq OWNED BY "Risk_Assess_Framework".ra_working_paper_status.id;


--
-- Name: risk_trend_history; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".risk_trend_history (
    id integer NOT NULL,
    reference_id integer,
    audit_universe_id integer,
    snapshot_date date DEFAULT CURRENT_DATE NOT NULL,
    period_type character varying(20) DEFAULT 'monthly'::character varying,
    critical_count integer DEFAULT 0,
    high_count integer DEFAULT 0,
    medium_count integer DEFAULT 0,
    low_count integer DEFAULT 0,
    very_low_count integer DEFAULT 0,
    total_inherent_score numeric(10,2) DEFAULT 0,
    total_residual_score numeric(10,2) DEFAULT 0,
    assessment_count integer DEFAULT 0,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: TABLE risk_trend_history; Type: COMMENT; Schema: Risk_Assess_Framework; Owner: -
--

COMMENT ON TABLE "Risk_Assess_Framework".risk_trend_history IS 'Historical snapshots of risk levels for trend analysis';


--
-- Name: risk_trend_history_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".risk_trend_history_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: risk_trend_history_id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Assess_Framework; Owner: -
--

ALTER SEQUENCE "Risk_Assess_Framework".risk_trend_history_id_seq OWNED BY "Risk_Assess_Framework".risk_trend_history.id;


--
-- Name: riskassessment_riskassessment_refid_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".riskassessment_riskassessment_refid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: riskassessment; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".riskassessment (
    riskassessment_refid integer DEFAULT nextval('"Risk_Assess_Framework".riskassessment_riskassessment_refid_seq'::regclass) NOT NULL,
    businessobjectives character varying(50),
    mainprocess character varying(50),
    subprocess character varying(50),
    keyriskandfactors character varying(50),
    mitigatingcontrols character varying(50),
    responsibility character varying(50),
    authoriser character varying(50),
    auditorsrecommendedactionplan character varying(50),
    responsibleperson character varying(50),
    agreeddate timestamp without time zone,
    risklikelihoodid integer,
    riskimpactid integer,
    keysecondaryid integer,
    riskcategoryid integer,
    datafrequencyid integer,
    frequencyid integer,
    evidenceid integer,
    outcomelikelihoodid integer,
    impactid integer,
    reference_id integer,
    department_id integer,
    project_id integer,
    auditor_id integer,
    status_id integer DEFAULT 1,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    businessobjectivedescription text,
    riskdescription text,
    controldescription text,
    outcomedescription text
);


--
-- Name: COLUMN riskassessment.department_id; Type: COMMENT; Schema: Risk_Assess_Framework; Owner: -
--

COMMENT ON COLUMN "Risk_Assess_Framework".riskassessment.department_id IS 'Department this assessment belongs to';


--
-- Name: COLUMN riskassessment.project_id; Type: COMMENT; Schema: Risk_Assess_Framework; Owner: -
--

COMMENT ON COLUMN "Risk_Assess_Framework".riskassessment.project_id IS 'Project this assessment is associated with (optional)';


--
-- Name: COLUMN riskassessment.auditor_id; Type: COMMENT; Schema: Risk_Assess_Framework; Owner: -
--

COMMENT ON COLUMN "Risk_Assess_Framework".riskassessment.auditor_id IS 'User who is conducting/responsible for this assessment';


--
-- Name: COLUMN riskassessment.status_id; Type: COMMENT; Schema: Risk_Assess_Framework; Owner: -
--

COMMENT ON COLUMN "Risk_Assess_Framework".riskassessment.status_id IS 'Foreign key to ra_assessmentstatus table';


--
-- Name: riskassessmentreference; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".riskassessmentreference (
    reference_id integer NOT NULL,
    client character varying(100),
    assessor character varying(100),
    approved_by character varying(100),
    created_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    assessment_start_date date,
    assessment_end_date date,
    department_id integer,
    project_id integer,
    title character varying(255),
    description text,
    status_id integer DEFAULT 1,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    is_archived boolean DEFAULT false NOT NULL,
    archived_at timestamp without time zone,
    archived_by_user_id integer,
    archived_by_name character varying(255),
    archive_reason text
);


--
-- Name: COLUMN riskassessmentreference.title; Type: COMMENT; Schema: Risk_Assess_Framework; Owner: -
--

COMMENT ON COLUMN "Risk_Assess_Framework".riskassessmentreference.title IS 'Human-readable title for the assessment reference';


--
-- Name: COLUMN riskassessmentreference.description; Type: COMMENT; Schema: Risk_Assess_Framework; Owner: -
--

COMMENT ON COLUMN "Risk_Assess_Framework".riskassessmentreference.description IS 'Detailed description of the assessment scope';


--
-- Name: COLUMN riskassessmentreference.status_id; Type: COMMENT; Schema: Risk_Assess_Framework; Owner: -
--

COMMENT ON COLUMN "Risk_Assess_Framework".riskassessmentreference.status_id IS 'Foreign key to ra_referencestatus table';


--
-- Name: riskassessmentreference_reference_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".riskassessmentreference_reference_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: riskassessmentreference_reference_id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Assess_Framework; Owner: -
--

ALTER SEQUENCE "Risk_Assess_Framework".riskassessmentreference_reference_id_seq OWNED BY "Risk_Assess_Framework".riskassessmentreference.reference_id;


--
-- Name: riskmatrix_outcome_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".riskmatrix_outcome_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: riskmatrix_outcome; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".riskmatrix_outcome (
    id integer DEFAULT nextval('"Risk_Assess_Framework".riskmatrix_outcome_id_seq'::regclass) NOT NULL,
    riskassessmentid integer,
    keyriskfactorsid integer,
    resultoutcome text
);


--
-- Name: riskmatrix_setup_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".riskmatrix_setup_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: riskmatrix_setup; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".riskmatrix_setup (
    id integer DEFAULT nextval('"Risk_Assess_Framework".riskmatrix_setup_id_seq'::regclass) NOT NULL,
    riskimpact_id integer,
    risklikelihood_id integer,
    setupoutcome text
);


--
-- Name: roles_role_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".roles_role_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: roles; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".roles (
    role_id integer DEFAULT nextval('"Risk_Assess_Framework".roles_role_id_seq'::regclass) NOT NULL,
    rolename character varying(255) NOT NULL,
    role_description character varying(255)
);


--
-- Name: rolesjoin_user_role_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".rolesjoin_user_role_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: rolesjoin; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".rolesjoin (
    user_role_id integer DEFAULT nextval('"Risk_Assess_Framework".rolesjoin_user_role_id_seq'::regclass) NOT NULL,
    user_id integer,
    role_id integer
);


--
-- Name: token_token_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".token_token_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: token; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".token (
    token_id integer DEFAULT nextval('"Risk_Assess_Framework".token_token_id_seq'::regclass) NOT NULL,
    token_value character varying(50),
    expiry_date timestamp without time zone
);


--
-- Name: user_view; Type: VIEW; Schema: Risk_Assess_Framework; Owner: -
--

CREATE VIEW "Risk_Assess_Framework".user_view AS
 SELECT a.user_id AS id,
    a.username,
    concat(a.firstname, ' ', COALESCE(a.lastname, ''::character varying)) AS name,
    a.email,
    r.name AS role,
    d.name AS department,
    a.is_active,
    a.created_at,
    a.updated_at
   FROM (("Risk_Assess_Framework".accounts a
     LEFT JOIN "Risk_Assess_Framework".ra_userroles r ON ((a.role_id = r.id)))
     LEFT JOIN "Risk_Assess_Framework".departments d ON ((a.department_id = d.id)));


--
-- Name: VIEW user_view; Type: COMMENT; Schema: Risk_Assess_Framework; Owner: -
--

COMMENT ON VIEW "Risk_Assess_Framework".user_view IS 'View that presents user data in frontend-compatible format';


--
-- Name: users; Type: TABLE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TABLE "Risk_Assess_Framework".users (
    id integer NOT NULL,
    username character varying(100) NOT NULL,
    password_hash character varying(255) NOT NULL,
    name character varying(255) NOT NULL,
    email character varying(255) NOT NULL,
    role_id integer DEFAULT 3,
    department_id integer,
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: TABLE users; Type: COMMENT; Schema: Risk_Assess_Framework; Owner: -
--

COMMENT ON TABLE "Risk_Assess_Framework".users IS 'System users with role-based access and department assignment';


--
-- Name: COLUMN users.password_hash; Type: COMMENT; Schema: Risk_Assess_Framework; Owner: -
--

COMMENT ON COLUMN "Risk_Assess_Framework".users.password_hash IS 'Hashed password - never store plain text passwords';


--
-- Name: COLUMN users.role_id; Type: COMMENT; Schema: Risk_Assess_Framework; Owner: -
--

COMMENT ON COLUMN "Risk_Assess_Framework".users.role_id IS 'Foreign key to ra_userroles table';


--
-- Name: users_id_seq; Type: SEQUENCE; Schema: Risk_Assess_Framework; Owner: -
--

CREATE SEQUENCE "Risk_Assess_Framework".users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Assess_Framework; Owner: -
--

ALTER SEQUENCE "Risk_Assess_Framework".users_id_seq OWNED BY "Risk_Assess_Framework".users.id;


--
-- Name: vw_audit_reporting_analytics_summary; Type: VIEW; Schema: Risk_Assess_Framework; Owner: -
--

CREATE VIEW "Risk_Assess_Framework".vw_audit_reporting_analytics_summary AS
 WITH journal_summary AS (
         SELECT audit_gl_journal_entries.reference_id,
            count(*) AS journal_entry_rows
           FROM "Risk_Assess_Framework".audit_gl_journal_entries
          GROUP BY audit_gl_journal_entries.reference_id
        ), tb_summary AS (
         SELECT audit_trial_balance_snapshots.reference_id,
            count(*) AS trial_balance_accounts
           FROM "Risk_Assess_Framework".audit_trial_balance_snapshots
          GROUP BY audit_trial_balance_snapshots.reference_id
        ), benchmark_summary AS (
         SELECT audit_industry_benchmarks.reference_id,
            count(*) AS industry_benchmark_metrics
           FROM "Risk_Assess_Framework".audit_industry_benchmarks
          GROUP BY audit_industry_benchmarks.reference_id
        ), forecast_summary AS (
         SELECT audit_reasonability_forecasts.reference_id,
            count(*) AS reasonability_forecast_metrics
           FROM "Risk_Assess_Framework".audit_reasonability_forecasts
          GROUP BY audit_reasonability_forecasts.reference_id
        )
 SELECT COALESCE(j.reference_id, tb.reference_id, b.reference_id, f.reference_id) AS reference_id,
    COALESCE(j.journal_entry_rows, (0)::bigint) AS journal_entry_rows,
    COALESCE(tb.trial_balance_accounts, (0)::bigint) AS trial_balance_accounts,
    COALESCE(b.industry_benchmark_metrics, (0)::bigint) AS industry_benchmark_metrics,
    COALESCE(f.reasonability_forecast_metrics, (0)::bigint) AS reasonability_forecast_metrics
   FROM (((journal_summary j
     FULL JOIN tb_summary tb ON ((tb.reference_id = j.reference_id)))
     FULL JOIN benchmark_summary b ON ((b.reference_id = COALESCE(j.reference_id, tb.reference_id))))
     FULL JOIN forecast_summary f ON ((f.reference_id = COALESCE(j.reference_id, tb.reference_id, b.reference_id))));


--
-- Name: vw_audit_reporting_execution_summary; Type: VIEW; Schema: Risk_Assess_Framework; Owner: -
--

CREATE VIEW "Risk_Assess_Framework".vw_audit_reporting_execution_summary AS
 WITH working_paper_summary AS (
         SELECT wp_1.reference_id,
            count(*) FILTER (WHERE ((COALESCE(wp_1.is_template, false) = false) AND (COALESCE(wp_1.is_active, true) = true))) AS total_working_papers,
            count(DISTINCT
                CASE
                    WHEN (s.id IS NOT NULL) THEN wp_1.id
                    ELSE NULL::integer
                END) FILTER (WHERE ((COALESCE(wp_1.is_template, false) = false) AND (COALESCE(wp_1.is_active, true) = true))) AS signed_off_working_papers
           FROM ("Risk_Assess_Framework".audit_working_papers wp_1
             LEFT JOIN "Risk_Assess_Framework".audit_working_paper_signoffs s ON ((s.working_paper_id = wp_1.id)))
          GROUP BY wp_1.reference_id
        ), document_summary AS (
         SELECT d_1.reference_id,
            count(*) FILTER (WHERE (COALESCE(d_1.is_active, true) = true)) AS total_documents
           FROM "Risk_Assess_Framework".audit_documents d_1
          GROUP BY d_1.reference_id
        ), evidence_summary AS (
         SELECT er_1.reference_id,
            count(*) FILTER (WHERE (COALESCE(es.is_closed, false) = false)) AS open_evidence_requests
           FROM ("Risk_Assess_Framework".audit_evidence_requests er_1
             LEFT JOIN "Risk_Assess_Framework".ra_evidence_request_status es ON ((es.id = er_1.status_id)))
          GROUP BY er_1.reference_id
        ), workflow_summary AS (
         SELECT wi_1.reference_id,
            count(*) FILTER (WHERE (COALESCE(wi_1.is_active, false) = true)) AS active_workflows
           FROM "Risk_Assess_Framework".audit_workflow_instances wi_1
          GROUP BY wi_1.reference_id
        ), task_summary AS (
         SELECT wt_1.reference_id,
            count(*) FILTER (WHERE (lower((COALESCE(wt_1.status, 'pending'::character varying))::text) = 'pending'::text)) AS pending_workflow_tasks
           FROM "Risk_Assess_Framework".audit_workflow_tasks wt_1
          GROUP BY wt_1.reference_id
        )
 SELECT COALESCE(wp.reference_id, d.reference_id, er.reference_id, wi.reference_id, wt.reference_id) AS reference_id,
    COALESCE(wp.total_working_papers, (0)::bigint) AS total_working_papers,
    COALESCE(wp.signed_off_working_papers, (0)::bigint) AS signed_off_working_papers,
    COALESCE(d.total_documents, (0)::bigint) AS total_documents,
    COALESCE(er.open_evidence_requests, (0)::bigint) AS open_evidence_requests,
    COALESCE(wi.active_workflows, (0)::bigint) AS active_workflows,
    COALESCE(wt.pending_workflow_tasks, (0)::bigint) AS pending_workflow_tasks
   FROM ((((working_paper_summary wp
     FULL JOIN document_summary d ON ((d.reference_id = wp.reference_id)))
     FULL JOIN evidence_summary er ON ((er.reference_id = COALESCE(wp.reference_id, d.reference_id))))
     FULL JOIN workflow_summary wi ON ((wi.reference_id = COALESCE(wp.reference_id, d.reference_id, er.reference_id))))
     FULL JOIN task_summary wt ON ((wt.reference_id = COALESCE(wp.reference_id, d.reference_id, er.reference_id, wi.reference_id))));


--
-- Name: vw_audit_reporting_findings_summary; Type: VIEW; Schema: Risk_Assess_Framework; Owner: -
--

CREATE VIEW "Risk_Assess_Framework".vw_audit_reporting_findings_summary AS
 WITH finding_summary AS (
         SELECT f_1.reference_id,
            count(*) AS total_findings,
            count(*) FILTER (WHERE (COALESCE(fs.is_closed, false) = false)) AS open_findings
           FROM ("Risk_Assess_Framework".audit_findings f_1
             LEFT JOIN "Risk_Assess_Framework".ra_finding_status fs ON ((fs.id = f_1.status_id)))
          GROUP BY f_1.reference_id
        ), recommendation_summary AS (
         SELECT f_1.reference_id,
            count(*) AS total_recommendations,
            count(*) FILTER (WHERE ((COALESCE(rs.name, 'Pending'::character varying))::text <> ALL ((ARRAY['Implemented'::character varying, 'Rejected'::character varying, 'Deferred'::character varying])::text[]))) AS open_recommendations
           FROM (("Risk_Assess_Framework".audit_recommendations r_1
             JOIN "Risk_Assess_Framework".audit_findings f_1 ON ((f_1.id = r_1.finding_id)))
             LEFT JOIN "Risk_Assess_Framework".ra_recommendation_status rs ON ((rs.id = r_1.status_id)))
          GROUP BY f_1.reference_id
        ), management_action_summary AS (
         SELECT ma.reference_id,
            count(*) FILTER (WHERE ((ma.due_date < CURRENT_DATE) AND (lower((COALESCE(ma.status, 'open'::character varying))::text) <> ALL (ARRAY['closed'::text, 'completed'::text, 'validated'::text, 'cancelled'::text, 'canceled'::text])))) AS overdue_management_actions
           FROM "Risk_Assess_Framework".audit_management_actions ma
          GROUP BY ma.reference_id
        )
 SELECT COALESCE(f.reference_id, r.reference_id, m.reference_id) AS reference_id,
    COALESCE(f.total_findings, (0)::bigint) AS total_findings,
    COALESCE(f.open_findings, (0)::bigint) AS open_findings,
    COALESCE(r.total_recommendations, (0)::bigint) AS total_recommendations,
    COALESCE(r.open_recommendations, (0)::bigint) AS open_recommendations,
    COALESCE(m.overdue_management_actions, (0)::bigint) AS overdue_management_actions
   FROM ((finding_summary f
     FULL JOIN recommendation_summary r ON ((r.reference_id = f.reference_id)))
     FULL JOIN management_action_summary m ON ((m.reference_id = COALESCE(f.reference_id, r.reference_id))));


--
-- Name: ControlTest; Type: TABLE; Schema: Risk_Workflow; Owner: -
--

CREATE TABLE "Risk_Workflow"."ControlTest" (
    "Id" integer NOT NULL,
    "ControlId" character varying(255) NOT NULL,
    "RiskAssessmentId" character varying(255) NOT NULL,
    "WorkflowInstanceId" uuid NOT NULL,
    "TesterId" character varying(255) NOT NULL,
    "TestFrequency" character varying(50) NOT NULL,
    "TestPassed" boolean,
    "TestNotes" text,
    "TestDate" timestamp without time zone,
    "ScheduledDate" timestamp without time zone NOT NULL,
    "CompletedDate" timestamp without time zone,
    "RemediationRequired" boolean,
    "RemediationTaskId" character varying(255)
);


--
-- Name: ControlTest_Id_seq; Type: SEQUENCE; Schema: Risk_Workflow; Owner: -
--

CREATE SEQUENCE "Risk_Workflow"."ControlTest_Id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: ControlTest_Id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Workflow; Owner: -
--

ALTER SEQUENCE "Risk_Workflow"."ControlTest_Id_seq" OWNED BY "Risk_Workflow"."ControlTest"."Id";


--
-- Name: Elsa_ActivityExecutionRecords; Type: TABLE; Schema: Risk_Workflow; Owner: -
--

CREATE TABLE "Risk_Workflow"."Elsa_ActivityExecutionRecords" (
    "Id" character varying(255) NOT NULL,
    "WorkflowInstanceId" character varying(255) NOT NULL,
    "ActivityId" character varying(255) NOT NULL,
    "ActivityType" character varying(255) NOT NULL,
    "ActivityName" character varying(255),
    "ActivityNodeId" character varying(255) NOT NULL,
    "StartedAt" timestamp with time zone DEFAULT now() NOT NULL,
    "CompletedAt" timestamp with time zone,
    "Status" integer DEFAULT 0 NOT NULL,
    "Data" jsonb,
    "Exception" text,
    "Payload" jsonb,
    "Outcomes" jsonb,
    "ActivityState" jsonb
);


--
-- Name: Elsa_Bookmarks; Type: TABLE; Schema: Risk_Workflow; Owner: -
--

CREATE TABLE "Risk_Workflow"."Elsa_Bookmarks" (
    "Id" character varying(255) NOT NULL,
    "ActivityTypeName" character varying(255) NOT NULL,
    "Hash" character varying(255) NOT NULL,
    "WorkflowInstanceId" character varying(255) NOT NULL,
    "ActivityInstanceId" character varying(255) NOT NULL,
    "CorrelationId" character varying(255),
    "Data" jsonb,
    "CreatedAt" timestamp with time zone DEFAULT now() NOT NULL,
    "ActivityId" character varying(255),
    "Payload" jsonb,
    "CallbackMethodName" character varying(255)
);


--
-- Name: Elsa_KeyValuePairs; Type: TABLE; Schema: Risk_Workflow; Owner: -
--

CREATE TABLE "Risk_Workflow"."Elsa_KeyValuePairs" (
    "Key" character varying(255) NOT NULL,
    "SerializedValue" text NOT NULL
);


--
-- Name: Elsa_Triggers; Type: TABLE; Schema: Risk_Workflow; Owner: -
--

CREATE TABLE "Risk_Workflow"."Elsa_Triggers" (
    "Id" character varying(255) NOT NULL,
    "WorkflowDefinitionId" character varying(255) NOT NULL,
    "WorkflowDefinitionVersionId" character varying(255) NOT NULL,
    "ActivityId" character varying(255) NOT NULL,
    "Hash" character varying(255) NOT NULL,
    "Name" character varying(255),
    "Data" jsonb,
    "Payload" jsonb
);


--
-- Name: Elsa_WorkflowDefinitions; Type: TABLE; Schema: Risk_Workflow; Owner: -
--

CREATE TABLE "Risk_Workflow"."Elsa_WorkflowDefinitions" (
    "Id" character varying(255) NOT NULL,
    "DefinitionId" character varying(255) NOT NULL,
    "Name" character varying(255),
    "Description" text,
    "Version" integer DEFAULT 1 NOT NULL,
    "IsLatest" boolean DEFAULT true NOT NULL,
    "IsPublished" boolean DEFAULT false NOT NULL,
    "CreatedAt" timestamp with time zone DEFAULT now() NOT NULL,
    "UpdatedAt" timestamp with time zone DEFAULT now() NOT NULL,
    "Data" jsonb NOT NULL,
    "UsableAsActivity" boolean DEFAULT false NOT NULL,
    "MaterializerName" character varying(255),
    "MaterializerContext" jsonb
);


--
-- Name: Elsa_WorkflowExecutionLogRecords; Type: TABLE; Schema: Risk_Workflow; Owner: -
--

CREATE TABLE "Risk_Workflow"."Elsa_WorkflowExecutionLogRecords" (
    "Id" character varying(255) NOT NULL,
    "WorkflowDefinitionId" character varying(255) NOT NULL,
    "WorkflowDefinitionVersionId" character varying(255) NOT NULL,
    "WorkflowInstanceId" character varying(255) NOT NULL,
    "WorkflowVersion" integer NOT NULL,
    "ActivityInstanceId" character varying(255) NOT NULL,
    "ParentActivityInstanceId" character varying(255),
    "ActivityId" character varying(255) NOT NULL,
    "ActivityType" character varying(255) NOT NULL,
    "ActivityName" character varying(255),
    "NodeId" character varying(255) NOT NULL,
    "Timestamp" timestamp with time zone DEFAULT now() NOT NULL,
    "Sequence" bigint NOT NULL,
    "EventName" character varying(255),
    "Message" text,
    "Source" character varying(255),
    "Data" jsonb,
    "Payload" jsonb
);


--
-- Name: Elsa_WorkflowInboxMessages; Type: TABLE; Schema: Risk_Workflow; Owner: -
--

CREATE TABLE "Risk_Workflow"."Elsa_WorkflowInboxMessages" (
    "Id" character varying(255) NOT NULL,
    "ActivityTypeName" character varying(255) NOT NULL,
    "Hash" character varying(255) NOT NULL,
    "WorkflowInstanceId" character varying(255),
    "CorrelationId" character varying(255),
    "ActivityInstanceId" character varying(255),
    "CreatedAt" timestamp with time zone DEFAULT now() NOT NULL,
    "ExpiresAt" timestamp with time zone,
    "Data" jsonb,
    "ActivityId" character varying(255)
);


--
-- Name: Elsa_WorkflowInstances; Type: TABLE; Schema: Risk_Workflow; Owner: -
--

CREATE TABLE "Risk_Workflow"."Elsa_WorkflowInstances" (
    "Id" character varying(255) NOT NULL,
    "DefinitionId" character varying(255) NOT NULL,
    "DefinitionVersionId" character varying(255) NOT NULL,
    "Version" integer DEFAULT 1 NOT NULL,
    "WorkflowState" integer DEFAULT 0 NOT NULL,
    "Status" integer DEFAULT 0 NOT NULL,
    "SubStatus" integer DEFAULT 0 NOT NULL,
    "CorrelationId" character varying(255),
    "Name" character varying(255),
    "CreatedAt" timestamp with time zone DEFAULT now() NOT NULL,
    "UpdatedAt" timestamp with time zone DEFAULT now() NOT NULL,
    "FinishedAt" timestamp with time zone,
    "Data" jsonb,
    "IsSystem" boolean DEFAULT false NOT NULL,
    "ParentWorkflowInstanceId" character varying(255),
    "ScheduledAt" timestamp with time zone,
    "ExpiresAt" timestamp with time zone
);


--
-- Name: RemediationTask; Type: TABLE; Schema: Risk_Workflow; Owner: -
--

CREATE TABLE "Risk_Workflow"."RemediationTask" (
    "Id" integer NOT NULL,
    "ControlTestId" integer NOT NULL,
    "AssigneeId" character varying(255) NOT NULL,
    "Description" text NOT NULL,
    "Priority" character varying(50) NOT NULL,
    "Status" character varying(50) NOT NULL,
    "CreatedDate" timestamp without time zone NOT NULL,
    "DueDate" timestamp without time zone,
    "CompletedDate" timestamp without time zone
);


--
-- Name: RemediationTask_Id_seq; Type: SEQUENCE; Schema: Risk_Workflow; Owner: -
--

CREATE SEQUENCE "Risk_Workflow"."RemediationTask_Id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: RemediationTask_Id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Workflow; Owner: -
--

ALTER SEQUENCE "Risk_Workflow"."RemediationTask_Id_seq" OWNED BY "Risk_Workflow"."RemediationTask"."Id";


--
-- Name: RiskAssessmentApproval; Type: TABLE; Schema: Risk_Workflow; Owner: -
--

CREATE TABLE "Risk_Workflow"."RiskAssessmentApproval" (
    "Id" integer NOT NULL,
    "RiskAssessmentId" character varying(255) NOT NULL,
    "WorkflowInstanceId" uuid NOT NULL,
    "ApproverId" character varying(255) NOT NULL,
    "IsApproved" boolean,
    "Comments" text,
    "ApprovalDeadline" timestamp without time zone,
    "RequestedAt" timestamp without time zone NOT NULL,
    "RespondedAt" timestamp without time zone
);


--
-- Name: RiskAssessmentApproval_Id_seq; Type: SEQUENCE; Schema: Risk_Workflow; Owner: -
--

CREATE SEQUENCE "Risk_Workflow"."RiskAssessmentApproval_Id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: RiskAssessmentApproval_Id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Workflow; Owner: -
--

ALTER SEQUENCE "Risk_Workflow"."RiskAssessmentApproval_Id_seq" OWNED BY "Risk_Workflow"."RiskAssessmentApproval"."Id";


--
-- Name: WorkflowExecutionLog; Type: TABLE; Schema: Risk_Workflow; Owner: -
--

CREATE TABLE "Risk_Workflow"."WorkflowExecutionLog" (
    "Id" integer NOT NULL,
    "WorkflowInstanceId" uuid NOT NULL,
    "ActivityId" character varying(255) NOT NULL,
    "ActivityType" character varying(255) NOT NULL,
    "Timestamp" timestamp without time zone NOT NULL,
    "EventType" character varying(50) NOT NULL,
    "Message" text,
    "Data" jsonb
);


--
-- Name: WorkflowExecutionLog_Id_seq; Type: SEQUENCE; Schema: Risk_Workflow; Owner: -
--

CREATE SEQUENCE "Risk_Workflow"."WorkflowExecutionLog_Id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: WorkflowExecutionLog_Id_seq; Type: SEQUENCE OWNED BY; Schema: Risk_Workflow; Owner: -
--

ALTER SEQUENCE "Risk_Workflow"."WorkflowExecutionLog_Id_seq" OWNED BY "Risk_Workflow"."WorkflowExecutionLog"."Id";


--
-- Name: WorkflowInstance; Type: TABLE; Schema: Risk_Workflow; Owner: -
--

CREATE TABLE "Risk_Workflow"."WorkflowInstance" (
    "Id" uuid NOT NULL,
    "DefinitionId" character varying(255) NOT NULL,
    "DefinitionVersion" integer NOT NULL,
    "CorrelationId" character varying(255),
    "Status" character varying(50) NOT NULL,
    "CreatedAt" timestamp without time zone NOT NULL,
    "LastExecutedAt" timestamp without time zone,
    "FinishedAt" timestamp without time zone,
    "FaultedAt" timestamp without time zone,
    "Data" jsonb
);


--
-- Name: ra_risklikelihood; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.ra_risklikelihood (
    id integer DEFAULT nextval('"Risk_Assess_Framework".ra_risklikelihood_id_seq'::regclass) NOT NULL,
    description text NOT NULL,
    "position" integer
);


--
-- Name: OperationalRiskAssessment Id; Type: DEFAULT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework"."OperationalRiskAssessment" ALTER COLUMN "Id" SET DEFAULT nextval('"Risk_Assess_Framework"."OperationalRiskAssessment_Id_seq"'::regclass);


--
-- Name: activity_log id; Type: DEFAULT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".activity_log ALTER COLUMN id SET DEFAULT nextval('"Risk_Assess_Framework".activity_log_id_seq'::regclass);


--
-- Name: assessment_statistics id; Type: DEFAULT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".assessment_statistics ALTER COLUMN id SET DEFAULT nextval('"Risk_Assess_Framework".assessment_statistics_id_seq'::regclass);


--
-- Name: audit_analytics_import_batches id; Type: DEFAULT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_analytics_import_batches ALTER COLUMN id SET DEFAULT nextval('"Risk_Assess_Framework".audit_analytics_import_batches_id_seq'::regclass);


--
-- Name: audit_archival_events id; Type: DEFAULT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_archival_events ALTER COLUMN id SET DEFAULT nextval('"Risk_Assess_Framework".audit_archival_events_id_seq'::regclass);


--
-- Name: audit_control_test_results id; Type: DEFAULT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_control_test_results ALTER COLUMN id SET DEFAULT nextval('"Risk_Assess_Framework".audit_control_test_results_id_seq'::regclass);


--
-- Name: audit_control_tests id; Type: DEFAULT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_control_tests ALTER COLUMN id SET DEFAULT nextval('"Risk_Assess_Framework".audit_control_tests_id_seq'::regclass);


--
-- Name: audit_coverage id; Type: DEFAULT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_coverage ALTER COLUMN id SET DEFAULT nextval('"Risk_Assess_Framework".audit_coverage_id_seq'::regclass);


--
-- Name: audit_document_access_logs id; Type: DEFAULT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_document_access_logs ALTER COLUMN id SET DEFAULT nextval('"Risk_Assess_Framework".audit_document_access_logs_id_seq'::regclass);


--
-- Name: audit_document_permission_grants id; Type: DEFAULT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_document_permission_grants ALTER COLUMN id SET DEFAULT nextval('"Risk_Assess_Framework".audit_document_permission_grants_id_seq'::regclass);


--
-- Name: audit_documents id; Type: DEFAULT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_documents ALTER COLUMN id SET DEFAULT nextval('"Risk_Assess_Framework".audit_documents_id_seq'::regclass);


--
-- Name: audit_domain_rule_packages id; Type: DEFAULT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_domain_rule_packages ALTER COLUMN id SET DEFAULT nextval('"Risk_Assess_Framework".audit_domain_rule_packages_id_seq'::regclass);


--
-- Name: audit_engagement_plans id; Type: DEFAULT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_engagement_plans ALTER COLUMN id SET DEFAULT nextval('"Risk_Assess_Framework".audit_engagement_plans_id_seq'::regclass);


--
-- Name: audit_evidence_request_items id; Type: DEFAULT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_evidence_request_items ALTER COLUMN id SET DEFAULT nextval('"Risk_Assess_Framework".audit_evidence_request_items_id_seq'::regclass);


--
-- Name: audit_evidence_requests id; Type: DEFAULT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_evidence_requests ALTER COLUMN id SET DEFAULT nextval('"Risk_Assess_Framework".audit_evidence_requests_id_seq'::regclass);


--
-- Name: audit_finance_finalization id; Type: DEFAULT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_finance_finalization ALTER COLUMN id SET DEFAULT nextval('"Risk_Assess_Framework".audit_finance_finalization_id_seq'::regclass);


--
-- Name: audit_financial_statement_mapping_profiles id; Type: DEFAULT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_financial_statement_mapping_profiles ALTER COLUMN id SET DEFAULT nextval('"Risk_Assess_Framework".audit_financial_statement_mapping_profiles_id_seq'::regclass);


--
-- Name: audit_financial_statement_mappings id; Type: DEFAULT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_financial_statement_mappings ALTER COLUMN id SET DEFAULT nextval('"Risk_Assess_Framework".audit_financial_statement_mappings_id_seq'::regclass);


--
-- Name: audit_financial_statement_profile_rules id; Type: DEFAULT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_financial_statement_profile_rules ALTER COLUMN id SET DEFAULT nextval('"Risk_Assess_Framework".audit_financial_statement_profile_rules_id_seq'::regclass);


--
-- Name: audit_findings id; Type: DEFAULT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_findings ALTER COLUMN id SET DEFAULT nextval('"Risk_Assess_Framework".audit_findings_id_seq'::regclass);


--
-- Name: audit_gl_journal_entries id; Type: DEFAULT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_gl_journal_entries ALTER COLUMN id SET DEFAULT nextval('"Risk_Assess_Framework".audit_gl_journal_entries_id_seq'::regclass);


--
-- Name: audit_holiday_calendar id; Type: DEFAULT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_holiday_calendar ALTER COLUMN id SET DEFAULT nextval('"Risk_Assess_Framework".audit_holiday_calendar_id_seq'::regclass);


--
-- Name: audit_industry_benchmarks id; Type: DEFAULT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_industry_benchmarks ALTER COLUMN id SET DEFAULT nextval('"Risk_Assess_Framework".audit_industry_benchmarks_id_seq'::regclass);


--
-- Name: audit_login_events id; Type: DEFAULT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_login_events ALTER COLUMN id SET DEFAULT nextval('"Risk_Assess_Framework".audit_login_events_id_seq'::regclass);


--
-- Name: audit_management_actions id; Type: DEFAULT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_management_actions ALTER COLUMN id SET DEFAULT nextval('"Risk_Assess_Framework".audit_management_actions_id_seq'::regclass);


--
-- Name: audit_materiality_approval_history id; Type: DEFAULT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_materiality_approval_history ALTER COLUMN id SET DEFAULT nextval('"Risk_Assess_Framework".audit_materiality_approval_history_id_seq'::regclass);


--
-- Name: audit_materiality_benchmark_profiles id; Type: DEFAULT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_materiality_benchmark_profiles ALTER COLUMN id SET DEFAULT nextval('"Risk_Assess_Framework".audit_materiality_benchmark_profiles_id_seq'::regclass);


--
-- Name: audit_materiality_calculations id; Type: DEFAULT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_materiality_calculations ALTER COLUMN id SET DEFAULT nextval('"Risk_Assess_Framework".audit_materiality_calculations_id_seq'::regclass);


--
-- Name: audit_materiality_candidates id; Type: DEFAULT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_materiality_candidates ALTER COLUMN id SET DEFAULT nextval('"Risk_Assess_Framework".audit_materiality_candidates_id_seq'::regclass);


--
-- Name: audit_materiality_scope_links id; Type: DEFAULT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_materiality_scope_links ALTER COLUMN id SET DEFAULT nextval('"Risk_Assess_Framework".audit_materiality_scope_links_id_seq'::regclass);


--
-- Name: audit_misstatements id; Type: DEFAULT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_misstatements ALTER COLUMN id SET DEFAULT nextval('"Risk_Assess_Framework".audit_misstatements_id_seq'::regclass);


--
-- Name: audit_notifications id; Type: DEFAULT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_notifications ALTER COLUMN id SET DEFAULT nextval('"Risk_Assess_Framework".audit_notifications_id_seq'::regclass);


--
-- Name: audit_procedure_assignments id; Type: DEFAULT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_procedure_assignments ALTER COLUMN id SET DEFAULT nextval('"Risk_Assess_Framework".audit_procedure_assignments_id_seq'::regclass);


--
-- Name: audit_procedure_steps id; Type: DEFAULT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_procedure_steps ALTER COLUMN id SET DEFAULT nextval('"Risk_Assess_Framework".audit_procedure_steps_id_seq'::regclass);


--
-- Name: audit_procedures id; Type: DEFAULT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_procedures ALTER COLUMN id SET DEFAULT nextval('"Risk_Assess_Framework".audit_procedures_id_seq'::regclass);


--
-- Name: audit_project_collaborators id; Type: DEFAULT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_project_collaborators ALTER COLUMN id SET DEFAULT nextval('"Risk_Assess_Framework".audit_project_collaborators_id_seq'::regclass);


--
-- Name: audit_reasonability_forecasts id; Type: DEFAULT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_reasonability_forecasts ALTER COLUMN id SET DEFAULT nextval('"Risk_Assess_Framework".audit_reasonability_forecasts_id_seq'::regclass);


--
-- Name: audit_recommendations id; Type: DEFAULT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_recommendations ALTER COLUMN id SET DEFAULT nextval('"Risk_Assess_Framework".audit_recommendations_id_seq'::regclass);


--
-- Name: audit_reference_collaborators id; Type: DEFAULT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_reference_collaborators ALTER COLUMN id SET DEFAULT nextval('"Risk_Assess_Framework".audit_reference_collaborators_id_seq'::regclass);


--
-- Name: audit_retention_policies id; Type: DEFAULT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_retention_policies ALTER COLUMN id SET DEFAULT nextval('"Risk_Assess_Framework".audit_retention_policies_id_seq'::regclass);


--
-- Name: audit_review_notes id; Type: DEFAULT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_review_notes ALTER COLUMN id SET DEFAULT nextval('"Risk_Assess_Framework".audit_review_notes_id_seq'::regclass);


--
-- Name: audit_reviews id; Type: DEFAULT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_reviews ALTER COLUMN id SET DEFAULT nextval('"Risk_Assess_Framework".audit_reviews_id_seq'::regclass);


--
-- Name: audit_risk_control_matrix id; Type: DEFAULT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_risk_control_matrix ALTER COLUMN id SET DEFAULT nextval('"Risk_Assess_Framework".audit_risk_control_matrix_id_seq'::regclass);


--
-- Name: audit_scope_items id; Type: DEFAULT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_scope_items ALTER COLUMN id SET DEFAULT nextval('"Risk_Assess_Framework".audit_scope_items_id_seq'::regclass);


--
-- Name: audit_signoffs id; Type: DEFAULT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_signoffs ALTER COLUMN id SET DEFAULT nextval('"Risk_Assess_Framework".audit_signoffs_id_seq'::regclass);


--
-- Name: audit_substantive_support_requests id; Type: DEFAULT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_substantive_support_requests ALTER COLUMN id SET DEFAULT nextval('"Risk_Assess_Framework".audit_substantive_support_requests_id_seq'::regclass);


--
-- Name: audit_tasks id; Type: DEFAULT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_tasks ALTER COLUMN id SET DEFAULT nextval('"Risk_Assess_Framework".audit_tasks_id_seq'::regclass);


--
-- Name: audit_trail_entity_changes id; Type: DEFAULT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_trail_entity_changes ALTER COLUMN id SET DEFAULT nextval('"Risk_Assess_Framework".audit_trail_entity_changes_id_seq'::regclass);


--
-- Name: audit_trail_events id; Type: DEFAULT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_trail_events ALTER COLUMN id SET DEFAULT nextval('"Risk_Assess_Framework".audit_trail_events_id_seq'::regclass);


--
-- Name: audit_trial_balance_snapshots id; Type: DEFAULT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_trial_balance_snapshots ALTER COLUMN id SET DEFAULT nextval('"Risk_Assess_Framework".audit_trial_balance_snapshots_id_seq'::regclass);


--
-- Name: audit_universe id; Type: DEFAULT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_universe ALTER COLUMN id SET DEFAULT nextval('"Risk_Assess_Framework".audit_universe_id_seq'::regclass);


--
-- Name: audit_universe_department_link id; Type: DEFAULT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_universe_department_link ALTER COLUMN id SET DEFAULT nextval('"Risk_Assess_Framework".audit_universe_department_link_id_seq'::regclass);


--
-- Name: audit_usage_events id; Type: DEFAULT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_usage_events ALTER COLUMN id SET DEFAULT nextval('"Risk_Assess_Framework".audit_usage_events_id_seq'::regclass);


--
-- Name: audit_walkthrough_exceptions id; Type: DEFAULT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_walkthrough_exceptions ALTER COLUMN id SET DEFAULT nextval('"Risk_Assess_Framework".audit_walkthrough_exceptions_id_seq'::regclass);


--
-- Name: audit_walkthroughs id; Type: DEFAULT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_walkthroughs ALTER COLUMN id SET DEFAULT nextval('"Risk_Assess_Framework".audit_walkthroughs_id_seq'::regclass);


--
-- Name: audit_workflow_events id; Type: DEFAULT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_workflow_events ALTER COLUMN id SET DEFAULT nextval('"Risk_Assess_Framework".audit_workflow_events_id_seq'::regclass);


--
-- Name: audit_workflow_instances id; Type: DEFAULT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_workflow_instances ALTER COLUMN id SET DEFAULT nextval('"Risk_Assess_Framework".audit_workflow_instances_id_seq'::regclass);


--
-- Name: audit_workflow_tasks id; Type: DEFAULT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_workflow_tasks ALTER COLUMN id SET DEFAULT nextval('"Risk_Assess_Framework".audit_workflow_tasks_id_seq'::regclass);


--
-- Name: audit_working_paper_references id; Type: DEFAULT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_working_paper_references ALTER COLUMN id SET DEFAULT nextval('"Risk_Assess_Framework".audit_working_paper_references_id_seq'::regclass);


--
-- Name: audit_working_paper_sections id; Type: DEFAULT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_working_paper_sections ALTER COLUMN id SET DEFAULT nextval('"Risk_Assess_Framework".audit_working_paper_sections_id_seq'::regclass);


--
-- Name: audit_working_paper_signoffs id; Type: DEFAULT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_working_paper_signoffs ALTER COLUMN id SET DEFAULT nextval('"Risk_Assess_Framework".audit_working_paper_signoffs_id_seq'::regclass);


--
-- Name: audit_working_papers id; Type: DEFAULT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_working_papers ALTER COLUMN id SET DEFAULT nextval('"Risk_Assess_Framework".audit_working_papers_id_seq'::regclass);


--
-- Name: departments id; Type: DEFAULT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".departments ALTER COLUMN id SET DEFAULT nextval('"Risk_Assess_Framework".departments_id_seq'::regclass);


--
-- Name: market_data id; Type: DEFAULT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".market_data ALTER COLUMN id SET DEFAULT nextval('"Risk_Assess_Framework".market_data_id_seq'::regclass);


--
-- Name: projects id; Type: DEFAULT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".projects ALTER COLUMN id SET DEFAULT nextval('"Risk_Assess_Framework".projects_id_seq'::regclass);


--
-- Name: ra_assessmentstatus id; Type: DEFAULT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".ra_assessmentstatus ALTER COLUMN id SET DEFAULT nextval('"Risk_Assess_Framework".ra_assessmentstatus_id_seq'::regclass);


--
-- Name: ra_audit_collaborator_role id; Type: DEFAULT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".ra_audit_collaborator_role ALTER COLUMN id SET DEFAULT nextval('"Risk_Assess_Framework".ra_audit_collaborator_role_id_seq'::regclass);


--
-- Name: ra_audit_universe_levels id; Type: DEFAULT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".ra_audit_universe_levels ALTER COLUMN id SET DEFAULT nextval('"Risk_Assess_Framework".ra_audit_universe_levels_id_seq'::regclass);


--
-- Name: ra_control_classification id; Type: DEFAULT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".ra_control_classification ALTER COLUMN id SET DEFAULT nextval('"Risk_Assess_Framework".ra_control_classification_id_seq'::regclass);


--
-- Name: ra_control_frequency id; Type: DEFAULT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".ra_control_frequency ALTER COLUMN id SET DEFAULT nextval('"Risk_Assess_Framework".ra_control_frequency_id_seq'::regclass);


--
-- Name: ra_control_type id; Type: DEFAULT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".ra_control_type ALTER COLUMN id SET DEFAULT nextval('"Risk_Assess_Framework".ra_control_type_id_seq'::regclass);


--
-- Name: ra_document_category id; Type: DEFAULT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".ra_document_category ALTER COLUMN id SET DEFAULT nextval('"Risk_Assess_Framework".ra_document_category_id_seq'::regclass);


--
-- Name: ra_document_visibility_level id; Type: DEFAULT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".ra_document_visibility_level ALTER COLUMN id SET DEFAULT nextval('"Risk_Assess_Framework".ra_document_visibility_level_id_seq'::regclass);


--
-- Name: ra_engagement_type id; Type: DEFAULT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".ra_engagement_type ALTER COLUMN id SET DEFAULT nextval('"Risk_Assess_Framework".ra_engagement_type_id_seq'::regclass);


--
-- Name: ra_evidence_request_status id; Type: DEFAULT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".ra_evidence_request_status ALTER COLUMN id SET DEFAULT nextval('"Risk_Assess_Framework".ra_evidence_request_status_id_seq'::regclass);


--
-- Name: ra_finding_severity id; Type: DEFAULT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".ra_finding_severity ALTER COLUMN id SET DEFAULT nextval('"Risk_Assess_Framework".ra_finding_severity_id_seq'::regclass);


--
-- Name: ra_finding_status id; Type: DEFAULT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".ra_finding_status ALTER COLUMN id SET DEFAULT nextval('"Risk_Assess_Framework".ra_finding_status_id_seq'::regclass);


--
-- Name: ra_planning_status id; Type: DEFAULT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".ra_planning_status ALTER COLUMN id SET DEFAULT nextval('"Risk_Assess_Framework".ra_planning_status_id_seq'::regclass);


--
-- Name: ra_procedure_status id; Type: DEFAULT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".ra_procedure_status ALTER COLUMN id SET DEFAULT nextval('"Risk_Assess_Framework".ra_procedure_status_id_seq'::regclass);


--
-- Name: ra_procedure_type id; Type: DEFAULT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".ra_procedure_type ALTER COLUMN id SET DEFAULT nextval('"Risk_Assess_Framework".ra_procedure_type_id_seq'::regclass);


--
-- Name: ra_projectstatus id; Type: DEFAULT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".ra_projectstatus ALTER COLUMN id SET DEFAULT nextval('"Risk_Assess_Framework".ra_projectstatus_id_seq'::regclass);


--
-- Name: ra_recommendation_status id; Type: DEFAULT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".ra_recommendation_status ALTER COLUMN id SET DEFAULT nextval('"Risk_Assess_Framework".ra_recommendation_status_id_seq'::regclass);


--
-- Name: ra_referencestatus id; Type: DEFAULT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".ra_referencestatus ALTER COLUMN id SET DEFAULT nextval('"Risk_Assess_Framework".ra_referencestatus_id_seq'::regclass);


--
-- Name: ra_risklevels id; Type: DEFAULT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".ra_risklevels ALTER COLUMN id SET DEFAULT nextval('"Risk_Assess_Framework".ra_risklevels_id_seq'::regclass);


--
-- Name: ra_userroles id; Type: DEFAULT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".ra_userroles ALTER COLUMN id SET DEFAULT nextval('"Risk_Assess_Framework".ra_userroles_id_seq'::regclass);


--
-- Name: ra_working_paper_status id; Type: DEFAULT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".ra_working_paper_status ALTER COLUMN id SET DEFAULT nextval('"Risk_Assess_Framework".ra_working_paper_status_id_seq'::regclass);


--
-- Name: risk_trend_history id; Type: DEFAULT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".risk_trend_history ALTER COLUMN id SET DEFAULT nextval('"Risk_Assess_Framework".risk_trend_history_id_seq'::regclass);


--
-- Name: riskassessmentreference reference_id; Type: DEFAULT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".riskassessmentreference ALTER COLUMN reference_id SET DEFAULT nextval('"Risk_Assess_Framework".riskassessmentreference_reference_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".users ALTER COLUMN id SET DEFAULT nextval('"Risk_Assess_Framework".users_id_seq'::regclass);


--
-- Name: ControlTest Id; Type: DEFAULT; Schema: Risk_Workflow; Owner: -
--

ALTER TABLE ONLY "Risk_Workflow"."ControlTest" ALTER COLUMN "Id" SET DEFAULT nextval('"Risk_Workflow"."ControlTest_Id_seq"'::regclass);


--
-- Name: RemediationTask Id; Type: DEFAULT; Schema: Risk_Workflow; Owner: -
--

ALTER TABLE ONLY "Risk_Workflow"."RemediationTask" ALTER COLUMN "Id" SET DEFAULT nextval('"Risk_Workflow"."RemediationTask_Id_seq"'::regclass);


--
-- Name: RiskAssessmentApproval Id; Type: DEFAULT; Schema: Risk_Workflow; Owner: -
--

ALTER TABLE ONLY "Risk_Workflow"."RiskAssessmentApproval" ALTER COLUMN "Id" SET DEFAULT nextval('"Risk_Workflow"."RiskAssessmentApproval_Id_seq"'::regclass);


--
-- Name: WorkflowExecutionLog Id; Type: DEFAULT; Schema: Risk_Workflow; Owner: -
--

ALTER TABLE ONLY "Risk_Workflow"."WorkflowExecutionLog" ALTER COLUMN "Id" SET DEFAULT nextval('"Risk_Workflow"."WorkflowExecutionLog_Id_seq"'::regclass);


--
-- Name: ActivityExecutionRecords PK_ActivityExecutionRecords; Type: CONSTRAINT; Schema: Elsa; Owner: -
--

ALTER TABLE ONLY "Elsa"."ActivityExecutionRecords"
    ADD CONSTRAINT "PK_ActivityExecutionRecords" PRIMARY KEY ("Id");


--
-- Name: BookmarkQueueItems PK_BookmarkQueueItems; Type: CONSTRAINT; Schema: Elsa; Owner: -
--

ALTER TABLE ONLY "Elsa"."BookmarkQueueItems"
    ADD CONSTRAINT "PK_BookmarkQueueItems" PRIMARY KEY ("Id");


--
-- Name: Bookmarks PK_Bookmarks; Type: CONSTRAINT; Schema: Elsa; Owner: -
--

ALTER TABLE ONLY "Elsa"."Bookmarks"
    ADD CONSTRAINT "PK_Bookmarks" PRIMARY KEY ("Id");


--
-- Name: KeyValuePairs PK_KeyValuePairs; Type: CONSTRAINT; Schema: Elsa; Owner: -
--

ALTER TABLE ONLY "Elsa"."KeyValuePairs"
    ADD CONSTRAINT "PK_KeyValuePairs" PRIMARY KEY ("Id");


--
-- Name: Triggers PK_Triggers; Type: CONSTRAINT; Schema: Elsa; Owner: -
--

ALTER TABLE ONLY "Elsa"."Triggers"
    ADD CONSTRAINT "PK_Triggers" PRIMARY KEY ("Id");


--
-- Name: WorkflowDefinitions PK_WorkflowDefinitions; Type: CONSTRAINT; Schema: Elsa; Owner: -
--

ALTER TABLE ONLY "Elsa"."WorkflowDefinitions"
    ADD CONSTRAINT "PK_WorkflowDefinitions" PRIMARY KEY ("Id");


--
-- Name: WorkflowExecutionLogRecords PK_WorkflowExecutionLogRecords; Type: CONSTRAINT; Schema: Elsa; Owner: -
--

ALTER TABLE ONLY "Elsa"."WorkflowExecutionLogRecords"
    ADD CONSTRAINT "PK_WorkflowExecutionLogRecords" PRIMARY KEY ("Id");


--
-- Name: WorkflowInboxMessages PK_WorkflowInboxMessages; Type: CONSTRAINT; Schema: Elsa; Owner: -
--

ALTER TABLE ONLY "Elsa"."WorkflowInboxMessages"
    ADD CONSTRAINT "PK_WorkflowInboxMessages" PRIMARY KEY ("Id");


--
-- Name: WorkflowInstances PK_WorkflowInstances; Type: CONSTRAINT; Schema: Elsa; Owner: -
--

ALTER TABLE ONLY "Elsa"."WorkflowInstances"
    ADD CONSTRAINT "PK_WorkflowInstances" PRIMARY KEY ("Id");


--
-- Name: __EFMigrationsHistory PK___EFMigrationsHistory; Type: CONSTRAINT; Schema: Elsa; Owner: -
--

ALTER TABLE ONLY "Elsa"."__EFMigrationsHistory"
    ADD CONSTRAINT "PK___EFMigrationsHistory" PRIMARY KEY ("MigrationId");


--
-- Name: OperationalRiskAssessment OperationalRiskAssessment_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework"."OperationalRiskAssessment"
    ADD CONSTRAINT "OperationalRiskAssessment_pkey" PRIMARY KEY ("Id");


--
-- Name: accounts accounts_email_key; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".accounts
    ADD CONSTRAINT accounts_email_key UNIQUE (email);


--
-- Name: accounts accounts_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".accounts
    ADD CONSTRAINT accounts_pkey PRIMARY KEY (user_id);


--
-- Name: accounts accounts_username_key; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".accounts
    ADD CONSTRAINT accounts_username_key UNIQUE (username);


--
-- Name: activity_log activity_log_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".activity_log
    ADD CONSTRAINT activity_log_pkey PRIMARY KEY (id);


--
-- Name: assessment_statistics assessment_statistics_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".assessment_statistics
    ADD CONSTRAINT assessment_statistics_pkey PRIMARY KEY (id);


--
-- Name: audit_analytics_import_batches audit_analytics_import_batches_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_analytics_import_batches
    ADD CONSTRAINT audit_analytics_import_batches_pkey PRIMARY KEY (id);


--
-- Name: audit_archival_events audit_archival_events_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_archival_events
    ADD CONSTRAINT audit_archival_events_pkey PRIMARY KEY (id);


--
-- Name: audit_control_test_results audit_control_test_results_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_control_test_results
    ADD CONSTRAINT audit_control_test_results_pkey PRIMARY KEY (id);


--
-- Name: audit_control_tests audit_control_tests_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_control_tests
    ADD CONSTRAINT audit_control_tests_pkey PRIMARY KEY (id);


--
-- Name: audit_coverage audit_coverage_audit_universe_id_period_year_period_quarter_key; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_coverage
    ADD CONSTRAINT audit_coverage_audit_universe_id_period_year_period_quarter_key UNIQUE (audit_universe_id, period_year, period_quarter);


--
-- Name: audit_coverage audit_coverage_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_coverage
    ADD CONSTRAINT audit_coverage_pkey PRIMARY KEY (id);


--
-- Name: audit_document_access_logs audit_document_access_logs_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_document_access_logs
    ADD CONSTRAINT audit_document_access_logs_pkey PRIMARY KEY (id);


--
-- Name: audit_document_permission_grants audit_document_permission_grants_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_document_permission_grants
    ADD CONSTRAINT audit_document_permission_grants_pkey PRIMARY KEY (id);


--
-- Name: audit_documents audit_documents_document_code_key; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_documents
    ADD CONSTRAINT audit_documents_document_code_key UNIQUE (document_code);


--
-- Name: audit_documents audit_documents_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_documents
    ADD CONSTRAINT audit_documents_pkey PRIMARY KEY (id);


--
-- Name: audit_domain_rule_packages audit_domain_rule_packages_package_code_key; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_domain_rule_packages
    ADD CONSTRAINT audit_domain_rule_packages_package_code_key UNIQUE (package_code);


--
-- Name: audit_domain_rule_packages audit_domain_rule_packages_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_domain_rule_packages
    ADD CONSTRAINT audit_domain_rule_packages_pkey PRIMARY KEY (id);


--
-- Name: audit_engagement_plans audit_engagement_plans_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_engagement_plans
    ADD CONSTRAINT audit_engagement_plans_pkey PRIMARY KEY (id);


--
-- Name: audit_engagement_plans audit_engagement_plans_reference_id_key; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_engagement_plans
    ADD CONSTRAINT audit_engagement_plans_reference_id_key UNIQUE (reference_id);


--
-- Name: audit_evidence_request_items audit_evidence_request_items_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_evidence_request_items
    ADD CONSTRAINT audit_evidence_request_items_pkey PRIMARY KEY (id);


--
-- Name: audit_evidence_requests audit_evidence_requests_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_evidence_requests
    ADD CONSTRAINT audit_evidence_requests_pkey PRIMARY KEY (id);


--
-- Name: audit_evidence_requests audit_evidence_requests_request_number_key; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_evidence_requests
    ADD CONSTRAINT audit_evidence_requests_request_number_key UNIQUE (request_number);


--
-- Name: audit_finance_finalization audit_finance_finalization_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_finance_finalization
    ADD CONSTRAINT audit_finance_finalization_pkey PRIMARY KEY (id);


--
-- Name: audit_finance_finalization audit_finance_finalization_reference_id_key; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_finance_finalization
    ADD CONSTRAINT audit_finance_finalization_reference_id_key UNIQUE (reference_id);


--
-- Name: audit_financial_statement_mapping_profiles audit_financial_statement_mapping_profiles_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_financial_statement_mapping_profiles
    ADD CONSTRAINT audit_financial_statement_mapping_profiles_pkey PRIMARY KEY (id);


--
-- Name: audit_financial_statement_mapping_profiles audit_financial_statement_mapping_profiles_profile_code_key; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_financial_statement_mapping_profiles
    ADD CONSTRAINT audit_financial_statement_mapping_profiles_profile_code_key UNIQUE (profile_code);


--
-- Name: audit_financial_statement_mappings audit_financial_statement_mappings_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_financial_statement_mappings
    ADD CONSTRAINT audit_financial_statement_mappings_pkey PRIMARY KEY (id);


--
-- Name: audit_financial_statement_profile_rules audit_financial_statement_profile_rules_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_financial_statement_profile_rules
    ADD CONSTRAINT audit_financial_statement_profile_rules_pkey PRIMARY KEY (id);


--
-- Name: audit_findings audit_findings_finding_number_key; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_findings
    ADD CONSTRAINT audit_findings_finding_number_key UNIQUE (finding_number);


--
-- Name: audit_findings audit_findings_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_findings
    ADD CONSTRAINT audit_findings_pkey PRIMARY KEY (id);


--
-- Name: audit_gl_journal_entries audit_gl_journal_entries_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_gl_journal_entries
    ADD CONSTRAINT audit_gl_journal_entries_pkey PRIMARY KEY (id);


--
-- Name: audit_holiday_calendar audit_holiday_calendar_holiday_date_country_code_region_cod_key; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_holiday_calendar
    ADD CONSTRAINT audit_holiday_calendar_holiday_date_country_code_region_cod_key UNIQUE (holiday_date, country_code, region_code);


--
-- Name: audit_holiday_calendar audit_holiday_calendar_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_holiday_calendar
    ADD CONSTRAINT audit_holiday_calendar_pkey PRIMARY KEY (id);


--
-- Name: audit_industry_benchmarks audit_industry_benchmarks_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_industry_benchmarks
    ADD CONSTRAINT audit_industry_benchmarks_pkey PRIMARY KEY (id);


--
-- Name: audit_login_events audit_login_events_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_login_events
    ADD CONSTRAINT audit_login_events_pkey PRIMARY KEY (id);


--
-- Name: audit_management_actions audit_management_actions_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_management_actions
    ADD CONSTRAINT audit_management_actions_pkey PRIMARY KEY (id);


--
-- Name: audit_materiality_approval_history audit_materiality_approval_history_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_materiality_approval_history
    ADD CONSTRAINT audit_materiality_approval_history_pkey PRIMARY KEY (id);


--
-- Name: audit_materiality_benchmark_profiles audit_materiality_benchmark_profiles_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_materiality_benchmark_profiles
    ADD CONSTRAINT audit_materiality_benchmark_profiles_pkey PRIMARY KEY (id);


--
-- Name: audit_materiality_benchmark_profiles audit_materiality_benchmark_profiles_profile_code_key; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_materiality_benchmark_profiles
    ADD CONSTRAINT audit_materiality_benchmark_profiles_profile_code_key UNIQUE (profile_code);


--
-- Name: audit_materiality_calculations audit_materiality_calculations_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_materiality_calculations
    ADD CONSTRAINT audit_materiality_calculations_pkey PRIMARY KEY (id);


--
-- Name: audit_materiality_candidates audit_materiality_candidates_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_materiality_candidates
    ADD CONSTRAINT audit_materiality_candidates_pkey PRIMARY KEY (id);


--
-- Name: audit_materiality_scope_links audit_materiality_scope_links_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_materiality_scope_links
    ADD CONSTRAINT audit_materiality_scope_links_pkey PRIMARY KEY (id);


--
-- Name: audit_misstatements audit_misstatements_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_misstatements
    ADD CONSTRAINT audit_misstatements_pkey PRIMARY KEY (id);


--
-- Name: audit_notifications audit_notifications_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_notifications
    ADD CONSTRAINT audit_notifications_pkey PRIMARY KEY (id);


--
-- Name: audit_procedure_assignments audit_procedure_assignments_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_procedure_assignments
    ADD CONSTRAINT audit_procedure_assignments_pkey PRIMARY KEY (id);


--
-- Name: audit_procedure_steps audit_procedure_steps_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_procedure_steps
    ADD CONSTRAINT audit_procedure_steps_pkey PRIMARY KEY (id);


--
-- Name: audit_procedure_steps audit_procedure_steps_procedure_id_step_number_key; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_procedure_steps
    ADD CONSTRAINT audit_procedure_steps_procedure_id_step_number_key UNIQUE (procedure_id, step_number);


--
-- Name: audit_procedures audit_procedures_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_procedures
    ADD CONSTRAINT audit_procedures_pkey PRIMARY KEY (id);


--
-- Name: audit_procedures audit_procedures_procedure_code_key; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_procedures
    ADD CONSTRAINT audit_procedures_procedure_code_key UNIQUE (procedure_code);


--
-- Name: audit_project_collaborators audit_project_collaborators_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_project_collaborators
    ADD CONSTRAINT audit_project_collaborators_pkey PRIMARY KEY (id);


--
-- Name: audit_project_collaborators audit_project_collaborators_project_id_user_id_key; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_project_collaborators
    ADD CONSTRAINT audit_project_collaborators_project_id_user_id_key UNIQUE (project_id, user_id);


--
-- Name: audit_reasonability_forecasts audit_reasonability_forecasts_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_reasonability_forecasts
    ADD CONSTRAINT audit_reasonability_forecasts_pkey PRIMARY KEY (id);


--
-- Name: audit_recommendations audit_recommendations_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_recommendations
    ADD CONSTRAINT audit_recommendations_pkey PRIMARY KEY (id);


--
-- Name: audit_recommendations audit_recommendations_recommendation_number_key; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_recommendations
    ADD CONSTRAINT audit_recommendations_recommendation_number_key UNIQUE (recommendation_number);


--
-- Name: audit_reference_collaborators audit_reference_collaborators_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_reference_collaborators
    ADD CONSTRAINT audit_reference_collaborators_pkey PRIMARY KEY (id);


--
-- Name: audit_reference_collaborators audit_reference_collaborators_reference_id_user_id_key; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_reference_collaborators
    ADD CONSTRAINT audit_reference_collaborators_reference_id_user_id_key UNIQUE (reference_id, user_id);


--
-- Name: audit_retention_policies audit_retention_policies_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_retention_policies
    ADD CONSTRAINT audit_retention_policies_pkey PRIMARY KEY (id);


--
-- Name: audit_retention_policies audit_retention_policies_policy_name_key; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_retention_policies
    ADD CONSTRAINT audit_retention_policies_policy_name_key UNIQUE (policy_name);


--
-- Name: audit_review_notes audit_review_notes_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_review_notes
    ADD CONSTRAINT audit_review_notes_pkey PRIMARY KEY (id);


--
-- Name: audit_reviews audit_reviews_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_reviews
    ADD CONSTRAINT audit_reviews_pkey PRIMARY KEY (id);


--
-- Name: audit_risk_control_matrix audit_risk_control_matrix_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_risk_control_matrix
    ADD CONSTRAINT audit_risk_control_matrix_pkey PRIMARY KEY (id);


--
-- Name: audit_scope_items audit_scope_items_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_scope_items
    ADD CONSTRAINT audit_scope_items_pkey PRIMARY KEY (id);


--
-- Name: audit_signoffs audit_signoffs_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_signoffs
    ADD CONSTRAINT audit_signoffs_pkey PRIMARY KEY (id);


--
-- Name: audit_substantive_support_requests audit_substantive_support_requests_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_substantive_support_requests
    ADD CONSTRAINT audit_substantive_support_requests_pkey PRIMARY KEY (id);


--
-- Name: audit_tasks audit_tasks_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_tasks
    ADD CONSTRAINT audit_tasks_pkey PRIMARY KEY (id);


--
-- Name: audit_trail_entity_changes audit_trail_entity_changes_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_trail_entity_changes
    ADD CONSTRAINT audit_trail_entity_changes_pkey PRIMARY KEY (id);


--
-- Name: audit_trail_events audit_trail_events_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_trail_events
    ADD CONSTRAINT audit_trail_events_pkey PRIMARY KEY (id);


--
-- Name: audit_trial_balance_snapshots audit_trial_balance_snapshots_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_trial_balance_snapshots
    ADD CONSTRAINT audit_trial_balance_snapshots_pkey PRIMARY KEY (id);


--
-- Name: audit_universe audit_universe_code_key; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_universe
    ADD CONSTRAINT audit_universe_code_key UNIQUE (code);


--
-- Name: audit_universe_department_link audit_universe_department_lin_audit_universe_id_department__key; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_universe_department_link
    ADD CONSTRAINT audit_universe_department_lin_audit_universe_id_department__key UNIQUE (audit_universe_id, department_id);


--
-- Name: audit_universe_department_link audit_universe_department_link_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_universe_department_link
    ADD CONSTRAINT audit_universe_department_link_pkey PRIMARY KEY (id);


--
-- Name: audit_universe audit_universe_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_universe
    ADD CONSTRAINT audit_universe_pkey PRIMARY KEY (id);


--
-- Name: audit_usage_events audit_usage_events_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_usage_events
    ADD CONSTRAINT audit_usage_events_pkey PRIMARY KEY (id);


--
-- Name: audit_walkthrough_exceptions audit_walkthrough_exceptions_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_walkthrough_exceptions
    ADD CONSTRAINT audit_walkthrough_exceptions_pkey PRIMARY KEY (id);


--
-- Name: audit_walkthroughs audit_walkthroughs_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_walkthroughs
    ADD CONSTRAINT audit_walkthroughs_pkey PRIMARY KEY (id);


--
-- Name: audit_workflow_events audit_workflow_events_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_workflow_events
    ADD CONSTRAINT audit_workflow_events_pkey PRIMARY KEY (id);


--
-- Name: audit_workflow_instances audit_workflow_instances_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_workflow_instances
    ADD CONSTRAINT audit_workflow_instances_pkey PRIMARY KEY (id);


--
-- Name: audit_workflow_instances audit_workflow_instances_workflow_instance_id_key; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_workflow_instances
    ADD CONSTRAINT audit_workflow_instances_workflow_instance_id_key UNIQUE (workflow_instance_id);


--
-- Name: audit_workflow_tasks audit_workflow_tasks_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_workflow_tasks
    ADD CONSTRAINT audit_workflow_tasks_pkey PRIMARY KEY (id);


--
-- Name: audit_working_paper_references audit_working_paper_reference_from_working_paper_id_to_work_key; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_working_paper_references
    ADD CONSTRAINT audit_working_paper_reference_from_working_paper_id_to_work_key UNIQUE (from_working_paper_id, to_working_paper_id, reference_type);


--
-- Name: audit_working_paper_references audit_working_paper_references_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_working_paper_references
    ADD CONSTRAINT audit_working_paper_references_pkey PRIMARY KEY (id);


--
-- Name: audit_working_paper_sections audit_working_paper_sections_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_working_paper_sections
    ADD CONSTRAINT audit_working_paper_sections_pkey PRIMARY KEY (id);


--
-- Name: audit_working_paper_sections audit_working_paper_sections_working_paper_id_section_order_key; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_working_paper_sections
    ADD CONSTRAINT audit_working_paper_sections_working_paper_id_section_order_key UNIQUE (working_paper_id, section_order);


--
-- Name: audit_working_paper_signoffs audit_working_paper_signoffs_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_working_paper_signoffs
    ADD CONSTRAINT audit_working_paper_signoffs_pkey PRIMARY KEY (id);


--
-- Name: audit_working_papers audit_working_papers_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_working_papers
    ADD CONSTRAINT audit_working_papers_pkey PRIMARY KEY (id);


--
-- Name: audit_working_papers audit_working_papers_working_paper_code_key; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_working_papers
    ADD CONSTRAINT audit_working_papers_working_paper_code_key UNIQUE (working_paper_code);


--
-- Name: auditlog auditlog_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".auditlog
    ADD CONSTRAINT auditlog_pkey PRIMARY KEY (log_id);


--
-- Name: authentication authentication_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".authentication
    ADD CONSTRAINT authentication_pkey PRIMARY KEY (user_id);


--
-- Name: departments departments_name_key; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".departments
    ADD CONSTRAINT departments_name_key UNIQUE (name);


--
-- Name: departments departments_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".departments
    ADD CONSTRAINT departments_pkey PRIMARY KEY (id);


--
-- Name: market_data market_data_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".market_data
    ADD CONSTRAINT market_data_pkey PRIMARY KEY (id);


--
-- Name: permissions permissions_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".permissions
    ADD CONSTRAINT permissions_pkey PRIMARY KEY (permission_id);


--
-- Name: projects projects_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".projects
    ADD CONSTRAINT projects_pkey PRIMARY KEY (id);


--
-- Name: ra_assessmentstatus ra_assessmentstatus_name_key; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".ra_assessmentstatus
    ADD CONSTRAINT ra_assessmentstatus_name_key UNIQUE (name);


--
-- Name: ra_assessmentstatus ra_assessmentstatus_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".ra_assessmentstatus
    ADD CONSTRAINT ra_assessmentstatus_pkey PRIMARY KEY (id);


--
-- Name: ra_audit_collaborator_role ra_audit_collaborator_role_name_key; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".ra_audit_collaborator_role
    ADD CONSTRAINT ra_audit_collaborator_role_name_key UNIQUE (name);


--
-- Name: ra_audit_collaborator_role ra_audit_collaborator_role_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".ra_audit_collaborator_role
    ADD CONSTRAINT ra_audit_collaborator_role_pkey PRIMARY KEY (id);


--
-- Name: ra_audit_universe_levels ra_audit_universe_levels_level_key; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".ra_audit_universe_levels
    ADD CONSTRAINT ra_audit_universe_levels_level_key UNIQUE (level);


--
-- Name: ra_audit_universe_levels ra_audit_universe_levels_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".ra_audit_universe_levels
    ADD CONSTRAINT ra_audit_universe_levels_pkey PRIMARY KEY (id);


--
-- Name: ra_control_classification ra_control_classification_name_key; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".ra_control_classification
    ADD CONSTRAINT ra_control_classification_name_key UNIQUE (name);


--
-- Name: ra_control_classification ra_control_classification_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".ra_control_classification
    ADD CONSTRAINT ra_control_classification_pkey PRIMARY KEY (id);


--
-- Name: ra_control_frequency ra_control_frequency_name_key; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".ra_control_frequency
    ADD CONSTRAINT ra_control_frequency_name_key UNIQUE (name);


--
-- Name: ra_control_frequency ra_control_frequency_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".ra_control_frequency
    ADD CONSTRAINT ra_control_frequency_pkey PRIMARY KEY (id);


--
-- Name: ra_control_type ra_control_type_name_key; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".ra_control_type
    ADD CONSTRAINT ra_control_type_name_key UNIQUE (name);


--
-- Name: ra_control_type ra_control_type_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".ra_control_type
    ADD CONSTRAINT ra_control_type_pkey PRIMARY KEY (id);


--
-- Name: ra_datafrequency ra_datafrequency_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".ra_datafrequency
    ADD CONSTRAINT ra_datafrequency_pkey PRIMARY KEY (id);


--
-- Name: ra_document_category ra_document_category_name_key; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".ra_document_category
    ADD CONSTRAINT ra_document_category_name_key UNIQUE (name);


--
-- Name: ra_document_category ra_document_category_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".ra_document_category
    ADD CONSTRAINT ra_document_category_pkey PRIMARY KEY (id);


--
-- Name: ra_document_visibility_level ra_document_visibility_level_name_key; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".ra_document_visibility_level
    ADD CONSTRAINT ra_document_visibility_level_name_key UNIQUE (name);


--
-- Name: ra_document_visibility_level ra_document_visibility_level_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".ra_document_visibility_level
    ADD CONSTRAINT ra_document_visibility_level_pkey PRIMARY KEY (id);


--
-- Name: ra_engagement_type ra_engagement_type_name_key; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".ra_engagement_type
    ADD CONSTRAINT ra_engagement_type_name_key UNIQUE (name);


--
-- Name: ra_engagement_type ra_engagement_type_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".ra_engagement_type
    ADD CONSTRAINT ra_engagement_type_pkey PRIMARY KEY (id);


--
-- Name: ra_evidence ra_evidence_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".ra_evidence
    ADD CONSTRAINT ra_evidence_pkey PRIMARY KEY (id);


--
-- Name: ra_evidence_request_status ra_evidence_request_status_name_key; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".ra_evidence_request_status
    ADD CONSTRAINT ra_evidence_request_status_name_key UNIQUE (name);


--
-- Name: ra_evidence_request_status ra_evidence_request_status_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".ra_evidence_request_status
    ADD CONSTRAINT ra_evidence_request_status_pkey PRIMARY KEY (id);


--
-- Name: ra_finding_severity ra_finding_severity_name_key; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".ra_finding_severity
    ADD CONSTRAINT ra_finding_severity_name_key UNIQUE (name);


--
-- Name: ra_finding_severity ra_finding_severity_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".ra_finding_severity
    ADD CONSTRAINT ra_finding_severity_pkey PRIMARY KEY (id);


--
-- Name: ra_finding_status ra_finding_status_name_key; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".ra_finding_status
    ADD CONSTRAINT ra_finding_status_name_key UNIQUE (name);


--
-- Name: ra_finding_status ra_finding_status_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".ra_finding_status
    ADD CONSTRAINT ra_finding_status_pkey PRIMARY KEY (id);


--
-- Name: ra_frequency ra_frequency_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".ra_frequency
    ADD CONSTRAINT ra_frequency_pkey PRIMARY KEY (id);


--
-- Name: ra_impact ra_impact_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".ra_impact
    ADD CONSTRAINT ra_impact_pkey PRIMARY KEY (id);


--
-- Name: ra_keyriskfactors ra_keyriskfactors_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".ra_keyriskfactors
    ADD CONSTRAINT ra_keyriskfactors_pkey PRIMARY KEY (id);


--
-- Name: ra_keysecondary ra_keysecondary_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".ra_keysecondary
    ADD CONSTRAINT ra_keysecondary_pkey PRIMARY KEY (id);


--
-- Name: ra_nature ra_nature_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".ra_nature
    ADD CONSTRAINT ra_nature_pkey PRIMARY KEY (id);


--
-- Name: ra_objectiveprocesses ra_objectiveprocesses_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".ra_objectiveprocesses
    ADD CONSTRAINT ra_objectiveprocesses_pkey PRIMARY KEY (id);


--
-- Name: ra_outcomelikelihood ra_outcomelikelihood_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".ra_outcomelikelihood
    ADD CONSTRAINT ra_outcomelikelihood_pkey PRIMARY KEY (id);


--
-- Name: ra_planning_status ra_planning_status_name_key; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".ra_planning_status
    ADD CONSTRAINT ra_planning_status_name_key UNIQUE (name);


--
-- Name: ra_planning_status ra_planning_status_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".ra_planning_status
    ADD CONSTRAINT ra_planning_status_pkey PRIMARY KEY (id);


--
-- Name: ra_procedure_status ra_procedure_status_name_key; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".ra_procedure_status
    ADD CONSTRAINT ra_procedure_status_name_key UNIQUE (name);


--
-- Name: ra_procedure_status ra_procedure_status_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".ra_procedure_status
    ADD CONSTRAINT ra_procedure_status_pkey PRIMARY KEY (id);


--
-- Name: ra_procedure_type ra_procedure_type_name_key; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".ra_procedure_type
    ADD CONSTRAINT ra_procedure_type_name_key UNIQUE (name);


--
-- Name: ra_procedure_type ra_procedure_type_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".ra_procedure_type
    ADD CONSTRAINT ra_procedure_type_pkey PRIMARY KEY (id);


--
-- Name: ra_projectstatus ra_projectstatus_name_key; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".ra_projectstatus
    ADD CONSTRAINT ra_projectstatus_name_key UNIQUE (name);


--
-- Name: ra_projectstatus ra_projectstatus_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".ra_projectstatus
    ADD CONSTRAINT ra_projectstatus_pkey PRIMARY KEY (id);


--
-- Name: ra_recommendation_status ra_recommendation_status_name_key; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".ra_recommendation_status
    ADD CONSTRAINT ra_recommendation_status_name_key UNIQUE (name);


--
-- Name: ra_recommendation_status ra_recommendation_status_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".ra_recommendation_status
    ADD CONSTRAINT ra_recommendation_status_pkey PRIMARY KEY (id);


--
-- Name: ra_referencestatus ra_referencestatus_name_key; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".ra_referencestatus
    ADD CONSTRAINT ra_referencestatus_name_key UNIQUE (name);


--
-- Name: ra_referencestatus ra_referencestatus_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".ra_referencestatus
    ADD CONSTRAINT ra_referencestatus_pkey PRIMARY KEY (id);


--
-- Name: ra_riskcategory ra_riskcategory_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".ra_riskcategory
    ADD CONSTRAINT ra_riskcategory_pkey PRIMARY KEY (id);


--
-- Name: ra_riskimpact ra_riskimpact_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".ra_riskimpact
    ADD CONSTRAINT ra_riskimpact_pkey PRIMARY KEY (id);


--
-- Name: ra_risklevels ra_risklevels_name_key; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".ra_risklevels
    ADD CONSTRAINT ra_risklevels_name_key UNIQUE (name);


--
-- Name: ra_risklevels ra_risklevels_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".ra_risklevels
    ADD CONSTRAINT ra_risklevels_pkey PRIMARY KEY (id);


--
-- Name: ra_userroles ra_userroles_name_key; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".ra_userroles
    ADD CONSTRAINT ra_userroles_name_key UNIQUE (name);


--
-- Name: ra_userroles ra_userroles_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".ra_userroles
    ADD CONSTRAINT ra_userroles_pkey PRIMARY KEY (id);


--
-- Name: ra_working_paper_status ra_working_paper_status_name_key; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".ra_working_paper_status
    ADD CONSTRAINT ra_working_paper_status_name_key UNIQUE (name);


--
-- Name: ra_working_paper_status ra_working_paper_status_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".ra_working_paper_status
    ADD CONSTRAINT ra_working_paper_status_pkey PRIMARY KEY (id);


--
-- Name: risk_trend_history risk_trend_history_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".risk_trend_history
    ADD CONSTRAINT risk_trend_history_pkey PRIMARY KEY (id);


--
-- Name: risk_trend_history risk_trend_history_reference_id_snapshot_date_period_type_key; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".risk_trend_history
    ADD CONSTRAINT risk_trend_history_reference_id_snapshot_date_period_type_key UNIQUE (reference_id, snapshot_date, period_type);


--
-- Name: riskassessment riskassessment_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".riskassessment
    ADD CONSTRAINT riskassessment_pkey PRIMARY KEY (riskassessment_refid);


--
-- Name: riskassessmentreference riskassessmentreference_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".riskassessmentreference
    ADD CONSTRAINT riskassessmentreference_pkey PRIMARY KEY (reference_id);


--
-- Name: riskmatrix_outcome riskmatrix_outcome_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".riskmatrix_outcome
    ADD CONSTRAINT riskmatrix_outcome_pkey PRIMARY KEY (id);


--
-- Name: riskmatrix_setup riskmatrix_setup_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".riskmatrix_setup
    ADD CONSTRAINT riskmatrix_setup_pkey PRIMARY KEY (id);


--
-- Name: roles roles_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".roles
    ADD CONSTRAINT roles_pkey PRIMARY KEY (role_id);


--
-- Name: rolesjoin rolesjoin_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".rolesjoin
    ADD CONSTRAINT rolesjoin_pkey PRIMARY KEY (user_role_id);


--
-- Name: token token_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".token
    ADD CONSTRAINT token_pkey PRIMARY KEY (token_id);


--
-- Name: audit_financial_statement_mappings uq_audit_fs_mapping; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_financial_statement_mappings
    ADD CONSTRAINT uq_audit_fs_mapping UNIQUE (reference_id, fiscal_year, account_number);


--
-- Name: audit_financial_statement_profile_rules uq_audit_fs_profile_rule; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_financial_statement_profile_rules
    ADD CONSTRAINT uq_audit_fs_profile_rule UNIQUE (mapping_profile_id, account_number);


--
-- Name: audit_substantive_support_requests uq_audit_support_request; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_substantive_support_requests
    ADD CONSTRAINT uq_audit_support_request UNIQUE (reference_id, source_key, triage_reason);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: users users_username_key; Type: CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- Name: ControlTest ControlTest_pkey; Type: CONSTRAINT; Schema: Risk_Workflow; Owner: -
--

ALTER TABLE ONLY "Risk_Workflow"."ControlTest"
    ADD CONSTRAINT "ControlTest_pkey" PRIMARY KEY ("Id");


--
-- Name: Elsa_ActivityExecutionRecords Elsa_ActivityExecutionRecords_pkey; Type: CONSTRAINT; Schema: Risk_Workflow; Owner: -
--

ALTER TABLE ONLY "Risk_Workflow"."Elsa_ActivityExecutionRecords"
    ADD CONSTRAINT "Elsa_ActivityExecutionRecords_pkey" PRIMARY KEY ("Id");


--
-- Name: Elsa_Bookmarks Elsa_Bookmarks_pkey; Type: CONSTRAINT; Schema: Risk_Workflow; Owner: -
--

ALTER TABLE ONLY "Risk_Workflow"."Elsa_Bookmarks"
    ADD CONSTRAINT "Elsa_Bookmarks_pkey" PRIMARY KEY ("Id");


--
-- Name: Elsa_KeyValuePairs Elsa_KeyValuePairs_pkey; Type: CONSTRAINT; Schema: Risk_Workflow; Owner: -
--

ALTER TABLE ONLY "Risk_Workflow"."Elsa_KeyValuePairs"
    ADD CONSTRAINT "Elsa_KeyValuePairs_pkey" PRIMARY KEY ("Key");


--
-- Name: Elsa_Triggers Elsa_Triggers_pkey; Type: CONSTRAINT; Schema: Risk_Workflow; Owner: -
--

ALTER TABLE ONLY "Risk_Workflow"."Elsa_Triggers"
    ADD CONSTRAINT "Elsa_Triggers_pkey" PRIMARY KEY ("Id");


--
-- Name: Elsa_WorkflowDefinitions Elsa_WorkflowDefinitions_pkey; Type: CONSTRAINT; Schema: Risk_Workflow; Owner: -
--

ALTER TABLE ONLY "Risk_Workflow"."Elsa_WorkflowDefinitions"
    ADD CONSTRAINT "Elsa_WorkflowDefinitions_pkey" PRIMARY KEY ("Id");


--
-- Name: Elsa_WorkflowExecutionLogRecords Elsa_WorkflowExecutionLogRecords_pkey; Type: CONSTRAINT; Schema: Risk_Workflow; Owner: -
--

ALTER TABLE ONLY "Risk_Workflow"."Elsa_WorkflowExecutionLogRecords"
    ADD CONSTRAINT "Elsa_WorkflowExecutionLogRecords_pkey" PRIMARY KEY ("Id");


--
-- Name: Elsa_WorkflowInboxMessages Elsa_WorkflowInboxMessages_pkey; Type: CONSTRAINT; Schema: Risk_Workflow; Owner: -
--

ALTER TABLE ONLY "Risk_Workflow"."Elsa_WorkflowInboxMessages"
    ADD CONSTRAINT "Elsa_WorkflowInboxMessages_pkey" PRIMARY KEY ("Id");


--
-- Name: Elsa_WorkflowInstances Elsa_WorkflowInstances_pkey; Type: CONSTRAINT; Schema: Risk_Workflow; Owner: -
--

ALTER TABLE ONLY "Risk_Workflow"."Elsa_WorkflowInstances"
    ADD CONSTRAINT "Elsa_WorkflowInstances_pkey" PRIMARY KEY ("Id");


--
-- Name: RemediationTask RemediationTask_pkey; Type: CONSTRAINT; Schema: Risk_Workflow; Owner: -
--

ALTER TABLE ONLY "Risk_Workflow"."RemediationTask"
    ADD CONSTRAINT "RemediationTask_pkey" PRIMARY KEY ("Id");


--
-- Name: RiskAssessmentApproval RiskAssessmentApproval_pkey; Type: CONSTRAINT; Schema: Risk_Workflow; Owner: -
--

ALTER TABLE ONLY "Risk_Workflow"."RiskAssessmentApproval"
    ADD CONSTRAINT "RiskAssessmentApproval_pkey" PRIMARY KEY ("Id");


--
-- Name: WorkflowExecutionLog WorkflowExecutionLog_pkey; Type: CONSTRAINT; Schema: Risk_Workflow; Owner: -
--

ALTER TABLE ONLY "Risk_Workflow"."WorkflowExecutionLog"
    ADD CONSTRAINT "WorkflowExecutionLog_pkey" PRIMARY KEY ("Id");


--
-- Name: WorkflowInstance WorkflowInstance_pkey; Type: CONSTRAINT; Schema: Risk_Workflow; Owner: -
--

ALTER TABLE ONLY "Risk_Workflow"."WorkflowInstance"
    ADD CONSTRAINT "WorkflowInstance_pkey" PRIMARY KEY ("Id");


--
-- Name: ra_risklikelihood ra_risklikelihood_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ra_risklikelihood
    ADD CONSTRAINT ra_risklikelihood_pkey PRIMARY KEY (id);


--
-- Name: IX_ActivityExecutionRecord_ActivityId; Type: INDEX; Schema: Elsa; Owner: -
--

CREATE INDEX "IX_ActivityExecutionRecord_ActivityId" ON "Elsa"."ActivityExecutionRecords" USING btree ("ActivityId");


--
-- Name: IX_ActivityExecutionRecord_ActivityName; Type: INDEX; Schema: Elsa; Owner: -
--

CREATE INDEX "IX_ActivityExecutionRecord_ActivityName" ON "Elsa"."ActivityExecutionRecords" USING btree ("ActivityName");


--
-- Name: IX_ActivityExecutionRecord_ActivityNodeId; Type: INDEX; Schema: Elsa; Owner: -
--

CREATE INDEX "IX_ActivityExecutionRecord_ActivityNodeId" ON "Elsa"."ActivityExecutionRecords" USING btree ("ActivityNodeId");


--
-- Name: IX_ActivityExecutionRecord_ActivityType; Type: INDEX; Schema: Elsa; Owner: -
--

CREATE INDEX "IX_ActivityExecutionRecord_ActivityType" ON "Elsa"."ActivityExecutionRecords" USING btree ("ActivityType");


--
-- Name: IX_ActivityExecutionRecord_ActivityTypeVersion; Type: INDEX; Schema: Elsa; Owner: -
--

CREATE INDEX "IX_ActivityExecutionRecord_ActivityTypeVersion" ON "Elsa"."ActivityExecutionRecords" USING btree ("ActivityTypeVersion");


--
-- Name: IX_ActivityExecutionRecord_ActivityType_ActivityTypeVersion; Type: INDEX; Schema: Elsa; Owner: -
--

CREATE INDEX "IX_ActivityExecutionRecord_ActivityType_ActivityTypeVersion" ON "Elsa"."ActivityExecutionRecords" USING btree ("ActivityType", "ActivityTypeVersion");


--
-- Name: IX_ActivityExecutionRecord_CompletedAt; Type: INDEX; Schema: Elsa; Owner: -
--

CREATE INDEX "IX_ActivityExecutionRecord_CompletedAt" ON "Elsa"."ActivityExecutionRecords" USING btree ("CompletedAt");


--
-- Name: IX_ActivityExecutionRecord_HasBookmarks; Type: INDEX; Schema: Elsa; Owner: -
--

CREATE INDEX "IX_ActivityExecutionRecord_HasBookmarks" ON "Elsa"."ActivityExecutionRecords" USING btree ("HasBookmarks");


--
-- Name: IX_ActivityExecutionRecord_StartedAt; Type: INDEX; Schema: Elsa; Owner: -
--

CREATE INDEX "IX_ActivityExecutionRecord_StartedAt" ON "Elsa"."ActivityExecutionRecords" USING btree ("StartedAt");


--
-- Name: IX_ActivityExecutionRecord_Status; Type: INDEX; Schema: Elsa; Owner: -
--

CREATE INDEX "IX_ActivityExecutionRecord_Status" ON "Elsa"."ActivityExecutionRecords" USING btree ("Status");


--
-- Name: IX_ActivityExecutionRecord_TenantId; Type: INDEX; Schema: Elsa; Owner: -
--

CREATE INDEX "IX_ActivityExecutionRecord_TenantId" ON "Elsa"."ActivityExecutionRecords" USING btree ("TenantId");


--
-- Name: IX_ActivityExecutionRecord_WorkflowInstanceId; Type: INDEX; Schema: Elsa; Owner: -
--

CREATE INDEX "IX_ActivityExecutionRecord_WorkflowInstanceId" ON "Elsa"."ActivityExecutionRecords" USING btree ("WorkflowInstanceId");


--
-- Name: IX_BookmarkQueueItem_ActivityInstanceId; Type: INDEX; Schema: Elsa; Owner: -
--

CREATE INDEX "IX_BookmarkQueueItem_ActivityInstanceId" ON "Elsa"."BookmarkQueueItems" USING btree ("ActivityInstanceId");


--
-- Name: IX_BookmarkQueueItem_ActivityTypeName; Type: INDEX; Schema: Elsa; Owner: -
--

CREATE INDEX "IX_BookmarkQueueItem_ActivityTypeName" ON "Elsa"."BookmarkQueueItems" USING btree ("ActivityTypeName");


--
-- Name: IX_BookmarkQueueItem_BookmarkId; Type: INDEX; Schema: Elsa; Owner: -
--

CREATE INDEX "IX_BookmarkQueueItem_BookmarkId" ON "Elsa"."BookmarkQueueItems" USING btree ("BookmarkId");


--
-- Name: IX_BookmarkQueueItem_CorrelationId; Type: INDEX; Schema: Elsa; Owner: -
--

CREATE INDEX "IX_BookmarkQueueItem_CorrelationId" ON "Elsa"."BookmarkQueueItems" USING btree ("CorrelationId");


--
-- Name: IX_BookmarkQueueItem_CreatedAt; Type: INDEX; Schema: Elsa; Owner: -
--

CREATE INDEX "IX_BookmarkQueueItem_CreatedAt" ON "Elsa"."BookmarkQueueItems" USING btree ("CreatedAt");


--
-- Name: IX_BookmarkQueueItem_StimulusHash; Type: INDEX; Schema: Elsa; Owner: -
--

CREATE INDEX "IX_BookmarkQueueItem_StimulusHash" ON "Elsa"."BookmarkQueueItems" USING btree ("StimulusHash");


--
-- Name: IX_BookmarkQueueItem_TenantId; Type: INDEX; Schema: Elsa; Owner: -
--

CREATE INDEX "IX_BookmarkQueueItem_TenantId" ON "Elsa"."BookmarkQueueItems" USING btree ("TenantId");


--
-- Name: IX_BookmarkQueueItem_WorkflowInstanceId; Type: INDEX; Schema: Elsa; Owner: -
--

CREATE INDEX "IX_BookmarkQueueItem_WorkflowInstanceId" ON "Elsa"."BookmarkQueueItems" USING btree ("WorkflowInstanceId");


--
-- Name: IX_SerializedKeyValuePair_TenantId; Type: INDEX; Schema: Elsa; Owner: -
--

CREATE INDEX "IX_SerializedKeyValuePair_TenantId" ON "Elsa"."KeyValuePairs" USING btree ("TenantId");


--
-- Name: IX_StoredBookmark_ActivityInstanceId; Type: INDEX; Schema: Elsa; Owner: -
--

CREATE INDEX "IX_StoredBookmark_ActivityInstanceId" ON "Elsa"."Bookmarks" USING btree ("ActivityInstanceId");


--
-- Name: IX_StoredBookmark_ActivityTypeName; Type: INDEX; Schema: Elsa; Owner: -
--

CREATE INDEX "IX_StoredBookmark_ActivityTypeName" ON "Elsa"."Bookmarks" USING btree ("ActivityTypeName");


--
-- Name: IX_StoredBookmark_ActivityTypeName_Hash; Type: INDEX; Schema: Elsa; Owner: -
--

CREATE INDEX "IX_StoredBookmark_ActivityTypeName_Hash" ON "Elsa"."Bookmarks" USING btree ("ActivityTypeName", "Hash");


--
-- Name: IX_StoredBookmark_ActivityTypeName_Hash_WorkflowInstanceId; Type: INDEX; Schema: Elsa; Owner: -
--

CREATE INDEX "IX_StoredBookmark_ActivityTypeName_Hash_WorkflowInstanceId" ON "Elsa"."Bookmarks" USING btree ("ActivityTypeName", "Hash", "WorkflowInstanceId");


--
-- Name: IX_StoredBookmark_CreatedAt; Type: INDEX; Schema: Elsa; Owner: -
--

CREATE INDEX "IX_StoredBookmark_CreatedAt" ON "Elsa"."Bookmarks" USING btree ("CreatedAt");


--
-- Name: IX_StoredBookmark_Hash; Type: INDEX; Schema: Elsa; Owner: -
--

CREATE INDEX "IX_StoredBookmark_Hash" ON "Elsa"."Bookmarks" USING btree ("Hash");


--
-- Name: IX_StoredBookmark_TenantId; Type: INDEX; Schema: Elsa; Owner: -
--

CREATE INDEX "IX_StoredBookmark_TenantId" ON "Elsa"."Bookmarks" USING btree ("TenantId");


--
-- Name: IX_StoredBookmark_WorkflowInstanceId; Type: INDEX; Schema: Elsa; Owner: -
--

CREATE INDEX "IX_StoredBookmark_WorkflowInstanceId" ON "Elsa"."Bookmarks" USING btree ("WorkflowInstanceId");


--
-- Name: IX_StoredTrigger_Hash; Type: INDEX; Schema: Elsa; Owner: -
--

CREATE INDEX "IX_StoredTrigger_Hash" ON "Elsa"."Triggers" USING btree ("Hash");


--
-- Name: IX_StoredTrigger_Name; Type: INDEX; Schema: Elsa; Owner: -
--

CREATE INDEX "IX_StoredTrigger_Name" ON "Elsa"."Triggers" USING btree ("Name");


--
-- Name: IX_StoredTrigger_TenantId; Type: INDEX; Schema: Elsa; Owner: -
--

CREATE INDEX "IX_StoredTrigger_TenantId" ON "Elsa"."Triggers" USING btree ("TenantId");


--
-- Name: IX_StoredTrigger_WorkflowDefinitionId; Type: INDEX; Schema: Elsa; Owner: -
--

CREATE INDEX "IX_StoredTrigger_WorkflowDefinitionId" ON "Elsa"."Triggers" USING btree ("WorkflowDefinitionId");


--
-- Name: IX_StoredTrigger_WorkflowDefinitionVersionId; Type: INDEX; Schema: Elsa; Owner: -
--

CREATE INDEX "IX_StoredTrigger_WorkflowDefinitionVersionId" ON "Elsa"."Triggers" USING btree ("WorkflowDefinitionVersionId");


--
-- Name: IX_WorkflowDefinition_DefinitionId_Version; Type: INDEX; Schema: Elsa; Owner: -
--

CREATE UNIQUE INDEX "IX_WorkflowDefinition_DefinitionId_Version" ON "Elsa"."WorkflowDefinitions" USING btree ("DefinitionId", "Version");


--
-- Name: IX_WorkflowDefinition_IsLatest; Type: INDEX; Schema: Elsa; Owner: -
--

CREATE INDEX "IX_WorkflowDefinition_IsLatest" ON "Elsa"."WorkflowDefinitions" USING btree ("IsLatest");


--
-- Name: IX_WorkflowDefinition_IsPublished; Type: INDEX; Schema: Elsa; Owner: -
--

CREATE INDEX "IX_WorkflowDefinition_IsPublished" ON "Elsa"."WorkflowDefinitions" USING btree ("IsPublished");


--
-- Name: IX_WorkflowDefinition_IsSystem; Type: INDEX; Schema: Elsa; Owner: -
--

CREATE INDEX "IX_WorkflowDefinition_IsSystem" ON "Elsa"."WorkflowDefinitions" USING btree ("IsSystem");


--
-- Name: IX_WorkflowDefinition_Name; Type: INDEX; Schema: Elsa; Owner: -
--

CREATE INDEX "IX_WorkflowDefinition_Name" ON "Elsa"."WorkflowDefinitions" USING btree ("Name");


--
-- Name: IX_WorkflowDefinition_TenantId; Type: INDEX; Schema: Elsa; Owner: -
--

CREATE INDEX "IX_WorkflowDefinition_TenantId" ON "Elsa"."WorkflowDefinitions" USING btree ("TenantId");


--
-- Name: IX_WorkflowDefinition_UsableAsActivity; Type: INDEX; Schema: Elsa; Owner: -
--

CREATE INDEX "IX_WorkflowDefinition_UsableAsActivity" ON "Elsa"."WorkflowDefinitions" USING btree ("UsableAsActivity");


--
-- Name: IX_WorkflowDefinition_Version; Type: INDEX; Schema: Elsa; Owner: -
--

CREATE INDEX "IX_WorkflowDefinition_Version" ON "Elsa"."WorkflowDefinitions" USING btree ("Version");


--
-- Name: IX_WorkflowExecutionLogRecord_ActivityId; Type: INDEX; Schema: Elsa; Owner: -
--

CREATE INDEX "IX_WorkflowExecutionLogRecord_ActivityId" ON "Elsa"."WorkflowExecutionLogRecords" USING btree ("ActivityId");


--
-- Name: IX_WorkflowExecutionLogRecord_ActivityInstanceId; Type: INDEX; Schema: Elsa; Owner: -
--

CREATE INDEX "IX_WorkflowExecutionLogRecord_ActivityInstanceId" ON "Elsa"."WorkflowExecutionLogRecords" USING btree ("ActivityInstanceId");


--
-- Name: IX_WorkflowExecutionLogRecord_ActivityName; Type: INDEX; Schema: Elsa; Owner: -
--

CREATE INDEX "IX_WorkflowExecutionLogRecord_ActivityName" ON "Elsa"."WorkflowExecutionLogRecords" USING btree ("ActivityName");


--
-- Name: IX_WorkflowExecutionLogRecord_ActivityNodeId; Type: INDEX; Schema: Elsa; Owner: -
--

CREATE INDEX "IX_WorkflowExecutionLogRecord_ActivityNodeId" ON "Elsa"."WorkflowExecutionLogRecords" USING btree ("ActivityNodeId");


--
-- Name: IX_WorkflowExecutionLogRecord_ActivityType; Type: INDEX; Schema: Elsa; Owner: -
--

CREATE INDEX "IX_WorkflowExecutionLogRecord_ActivityType" ON "Elsa"."WorkflowExecutionLogRecords" USING btree ("ActivityType");


--
-- Name: IX_WorkflowExecutionLogRecord_ActivityTypeVersion; Type: INDEX; Schema: Elsa; Owner: -
--

CREATE INDEX "IX_WorkflowExecutionLogRecord_ActivityTypeVersion" ON "Elsa"."WorkflowExecutionLogRecords" USING btree ("ActivityTypeVersion");


--
-- Name: IX_WorkflowExecutionLogRecord_ActivityType_ActivityTypeVersion; Type: INDEX; Schema: Elsa; Owner: -
--

CREATE INDEX "IX_WorkflowExecutionLogRecord_ActivityType_ActivityTypeVersion" ON "Elsa"."WorkflowExecutionLogRecords" USING btree ("ActivityType", "ActivityTypeVersion");


--
-- Name: IX_WorkflowExecutionLogRecord_EventName; Type: INDEX; Schema: Elsa; Owner: -
--

CREATE INDEX "IX_WorkflowExecutionLogRecord_EventName" ON "Elsa"."WorkflowExecutionLogRecords" USING btree ("EventName");


--
-- Name: IX_WorkflowExecutionLogRecord_ParentActivityInstanceId; Type: INDEX; Schema: Elsa; Owner: -
--

CREATE INDEX "IX_WorkflowExecutionLogRecord_ParentActivityInstanceId" ON "Elsa"."WorkflowExecutionLogRecords" USING btree ("ParentActivityInstanceId");


--
-- Name: IX_WorkflowExecutionLogRecord_Sequence; Type: INDEX; Schema: Elsa; Owner: -
--

CREATE INDEX "IX_WorkflowExecutionLogRecord_Sequence" ON "Elsa"."WorkflowExecutionLogRecords" USING btree ("Sequence");


--
-- Name: IX_WorkflowExecutionLogRecord_TenantId; Type: INDEX; Schema: Elsa; Owner: -
--

CREATE INDEX "IX_WorkflowExecutionLogRecord_TenantId" ON "Elsa"."WorkflowExecutionLogRecords" USING btree ("TenantId");


--
-- Name: IX_WorkflowExecutionLogRecord_Timestamp; Type: INDEX; Schema: Elsa; Owner: -
--

CREATE INDEX "IX_WorkflowExecutionLogRecord_Timestamp" ON "Elsa"."WorkflowExecutionLogRecords" USING btree ("Timestamp");


--
-- Name: IX_WorkflowExecutionLogRecord_Timestamp_Sequence; Type: INDEX; Schema: Elsa; Owner: -
--

CREATE INDEX "IX_WorkflowExecutionLogRecord_Timestamp_Sequence" ON "Elsa"."WorkflowExecutionLogRecords" USING btree ("Timestamp", "Sequence");


--
-- Name: IX_WorkflowExecutionLogRecord_WorkflowDefinitionId; Type: INDEX; Schema: Elsa; Owner: -
--

CREATE INDEX "IX_WorkflowExecutionLogRecord_WorkflowDefinitionId" ON "Elsa"."WorkflowExecutionLogRecords" USING btree ("WorkflowDefinitionId");


--
-- Name: IX_WorkflowExecutionLogRecord_WorkflowDefinitionVersionId; Type: INDEX; Schema: Elsa; Owner: -
--

CREATE INDEX "IX_WorkflowExecutionLogRecord_WorkflowDefinitionVersionId" ON "Elsa"."WorkflowExecutionLogRecords" USING btree ("WorkflowDefinitionVersionId");


--
-- Name: IX_WorkflowExecutionLogRecord_WorkflowInstanceId; Type: INDEX; Schema: Elsa; Owner: -
--

CREATE INDEX "IX_WorkflowExecutionLogRecord_WorkflowInstanceId" ON "Elsa"."WorkflowExecutionLogRecords" USING btree ("WorkflowInstanceId");


--
-- Name: IX_WorkflowExecutionLogRecord_WorkflowVersion; Type: INDEX; Schema: Elsa; Owner: -
--

CREATE INDEX "IX_WorkflowExecutionLogRecord_WorkflowVersion" ON "Elsa"."WorkflowExecutionLogRecords" USING btree ("WorkflowVersion");


--
-- Name: IX_WorkflowInboxMessage_ActivityInstanceId; Type: INDEX; Schema: Elsa; Owner: -
--

CREATE INDEX "IX_WorkflowInboxMessage_ActivityInstanceId" ON "Elsa"."WorkflowInboxMessages" USING btree ("ActivityInstanceId");


--
-- Name: IX_WorkflowInboxMessage_ActivityTypeName; Type: INDEX; Schema: Elsa; Owner: -
--

CREATE INDEX "IX_WorkflowInboxMessage_ActivityTypeName" ON "Elsa"."WorkflowInboxMessages" USING btree ("ActivityTypeName");


--
-- Name: IX_WorkflowInboxMessage_CorrelationId; Type: INDEX; Schema: Elsa; Owner: -
--

CREATE INDEX "IX_WorkflowInboxMessage_CorrelationId" ON "Elsa"."WorkflowInboxMessages" USING btree ("CorrelationId");


--
-- Name: IX_WorkflowInboxMessage_CreatedAt; Type: INDEX; Schema: Elsa; Owner: -
--

CREATE INDEX "IX_WorkflowInboxMessage_CreatedAt" ON "Elsa"."WorkflowInboxMessages" USING btree ("CreatedAt");


--
-- Name: IX_WorkflowInboxMessage_ExpiresAt; Type: INDEX; Schema: Elsa; Owner: -
--

CREATE INDEX "IX_WorkflowInboxMessage_ExpiresAt" ON "Elsa"."WorkflowInboxMessages" USING btree ("ExpiresAt");


--
-- Name: IX_WorkflowInboxMessage_Hash; Type: INDEX; Schema: Elsa; Owner: -
--

CREATE INDEX "IX_WorkflowInboxMessage_Hash" ON "Elsa"."WorkflowInboxMessages" USING btree ("Hash");


--
-- Name: IX_WorkflowInboxMessage_WorkflowInstanceId; Type: INDEX; Schema: Elsa; Owner: -
--

CREATE INDEX "IX_WorkflowInboxMessage_WorkflowInstanceId" ON "Elsa"."WorkflowInboxMessages" USING btree ("WorkflowInstanceId");


--
-- Name: IX_WorkflowInstance_CorrelationId; Type: INDEX; Schema: Elsa; Owner: -
--

CREATE INDEX "IX_WorkflowInstance_CorrelationId" ON "Elsa"."WorkflowInstances" USING btree ("CorrelationId");


--
-- Name: IX_WorkflowInstance_CreatedAt; Type: INDEX; Schema: Elsa; Owner: -
--

CREATE INDEX "IX_WorkflowInstance_CreatedAt" ON "Elsa"."WorkflowInstances" USING btree ("CreatedAt");


--
-- Name: IX_WorkflowInstance_DefinitionId; Type: INDEX; Schema: Elsa; Owner: -
--

CREATE INDEX "IX_WorkflowInstance_DefinitionId" ON "Elsa"."WorkflowInstances" USING btree ("DefinitionId");


--
-- Name: IX_WorkflowInstance_FinishedAt; Type: INDEX; Schema: Elsa; Owner: -
--

CREATE INDEX "IX_WorkflowInstance_FinishedAt" ON "Elsa"."WorkflowInstances" USING btree ("FinishedAt");


--
-- Name: IX_WorkflowInstance_IsExecuting; Type: INDEX; Schema: Elsa; Owner: -
--

CREATE INDEX "IX_WorkflowInstance_IsExecuting" ON "Elsa"."WorkflowInstances" USING btree ("IsExecuting");


--
-- Name: IX_WorkflowInstance_IsSystem; Type: INDEX; Schema: Elsa; Owner: -
--

CREATE INDEX "IX_WorkflowInstance_IsSystem" ON "Elsa"."WorkflowInstances" USING btree ("IsSystem");


--
-- Name: IX_WorkflowInstance_Name; Type: INDEX; Schema: Elsa; Owner: -
--

CREATE INDEX "IX_WorkflowInstance_Name" ON "Elsa"."WorkflowInstances" USING btree ("Name");


--
-- Name: IX_WorkflowInstance_Status; Type: INDEX; Schema: Elsa; Owner: -
--

CREATE INDEX "IX_WorkflowInstance_Status" ON "Elsa"."WorkflowInstances" USING btree ("Status");


--
-- Name: IX_WorkflowInstance_Status_DefinitionId; Type: INDEX; Schema: Elsa; Owner: -
--

CREATE INDEX "IX_WorkflowInstance_Status_DefinitionId" ON "Elsa"."WorkflowInstances" USING btree ("Status", "DefinitionId");


--
-- Name: IX_WorkflowInstance_Status_SubStatus; Type: INDEX; Schema: Elsa; Owner: -
--

CREATE INDEX "IX_WorkflowInstance_Status_SubStatus" ON "Elsa"."WorkflowInstances" USING btree ("Status", "SubStatus");


--
-- Name: IX_WorkflowInstance_Status_SubStatus_DefinitionId_Version; Type: INDEX; Schema: Elsa; Owner: -
--

CREATE INDEX "IX_WorkflowInstance_Status_SubStatus_DefinitionId_Version" ON "Elsa"."WorkflowInstances" USING btree ("Status", "SubStatus", "DefinitionId", "Version");


--
-- Name: IX_WorkflowInstance_SubStatus; Type: INDEX; Schema: Elsa; Owner: -
--

CREATE INDEX "IX_WorkflowInstance_SubStatus" ON "Elsa"."WorkflowInstances" USING btree ("SubStatus");


--
-- Name: IX_WorkflowInstance_SubStatus_DefinitionId; Type: INDEX; Schema: Elsa; Owner: -
--

CREATE INDEX "IX_WorkflowInstance_SubStatus_DefinitionId" ON "Elsa"."WorkflowInstances" USING btree ("SubStatus", "DefinitionId");


--
-- Name: IX_WorkflowInstance_TenantId; Type: INDEX; Schema: Elsa; Owner: -
--

CREATE INDEX "IX_WorkflowInstance_TenantId" ON "Elsa"."WorkflowInstances" USING btree ("TenantId");


--
-- Name: IX_WorkflowInstance_UpdatedAt; Type: INDEX; Schema: Elsa; Owner: -
--

CREATE INDEX "IX_WorkflowInstance_UpdatedAt" ON "Elsa"."WorkflowInstances" USING btree ("UpdatedAt");


--
-- Name: idx_accounts_created_at; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_accounts_created_at ON "Risk_Assess_Framework".accounts USING btree (created_at);


--
-- Name: idx_accounts_department_id; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_accounts_department_id ON "Risk_Assess_Framework".accounts USING btree (department_id);


--
-- Name: idx_accounts_email; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_accounts_email ON "Risk_Assess_Framework".accounts USING btree (email);


--
-- Name: idx_accounts_is_active; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_accounts_is_active ON "Risk_Assess_Framework".accounts USING btree (is_active);


--
-- Name: idx_accounts_role_id; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_accounts_role_id ON "Risk_Assess_Framework".accounts USING btree (role_id);


--
-- Name: idx_accounts_username; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_accounts_username ON "Risk_Assess_Framework".accounts USING btree (username);


--
-- Name: idx_activity_log_action; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_activity_log_action ON "Risk_Assess_Framework".activity_log USING btree (action);


--
-- Name: idx_activity_log_created_at; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_activity_log_created_at ON "Risk_Assess_Framework".activity_log USING btree (created_at);


--
-- Name: idx_activity_log_entity; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_activity_log_entity ON "Risk_Assess_Framework".activity_log USING btree (entity_type, entity_id);


--
-- Name: idx_activity_log_user_id; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_activity_log_user_id ON "Risk_Assess_Framework".activity_log USING btree (user_id);


--
-- Name: idx_assessment_statistics_department_id; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_assessment_statistics_department_id ON "Risk_Assess_Framework".assessment_statistics USING btree (department_id);


--
-- Name: idx_assessment_statistics_last_updated; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_assessment_statistics_last_updated ON "Risk_Assess_Framework".assessment_statistics USING btree (last_updated);


--
-- Name: idx_audit_analytics_import_batches_reference; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_analytics_import_batches_reference ON "Risk_Assess_Framework".audit_analytics_import_batches USING btree (reference_id, dataset_type, imported_at DESC);


--
-- Name: idx_audit_archival_events_archived_at; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_archival_events_archived_at ON "Risk_Assess_Framework".audit_archival_events USING btree (archived_at DESC);


--
-- Name: idx_audit_archival_events_reference_id; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_archival_events_reference_id ON "Risk_Assess_Framework".audit_archival_events USING btree (reference_id);


--
-- Name: idx_audit_control_test_results_control_test_id; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_control_test_results_control_test_id ON "Risk_Assess_Framework".audit_control_test_results USING btree (control_test_id);


--
-- Name: idx_audit_control_test_results_exception; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_control_test_results_exception ON "Risk_Assess_Framework".audit_control_test_results USING btree (is_exception, result_status);


--
-- Name: idx_audit_control_tests_rcm_id; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_control_tests_rcm_id ON "Risk_Assess_Framework".audit_control_tests USING btree (risk_control_matrix_id);


--
-- Name: idx_audit_control_tests_reference_id; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_control_tests_reference_id ON "Risk_Assess_Framework".audit_control_tests USING btree (reference_id);


--
-- Name: idx_audit_control_tests_status; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_control_tests_status ON "Risk_Assess_Framework".audit_control_tests USING btree (status);


--
-- Name: idx_audit_control_tests_working_paper_id; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_control_tests_working_paper_id ON "Risk_Assess_Framework".audit_control_tests USING btree (working_paper_id);


--
-- Name: idx_audit_coverage_period; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_coverage_period ON "Risk_Assess_Framework".audit_coverage USING btree (period_year, period_quarter);


--
-- Name: idx_audit_coverage_universe; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_coverage_universe ON "Risk_Assess_Framework".audit_coverage USING btree (audit_universe_id);


--
-- Name: idx_audit_document_access_logs_document_id; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_document_access_logs_document_id ON "Risk_Assess_Framework".audit_document_access_logs USING btree (document_id, accessed_at DESC);


--
-- Name: idx_audit_document_access_logs_reference_id; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_document_access_logs_reference_id ON "Risk_Assess_Framework".audit_document_access_logs USING btree (reference_id, accessed_at DESC);


--
-- Name: idx_audit_document_permission_grants_document_id; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_document_permission_grants_document_id ON "Risk_Assess_Framework".audit_document_permission_grants USING btree (document_id);


--
-- Name: idx_audit_document_permission_grants_grantee_user_id; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_document_permission_grants_grantee_user_id ON "Risk_Assess_Framework".audit_document_permission_grants USING btree (grantee_user_id);


--
-- Name: idx_audit_documents_category_id; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_documents_category_id ON "Risk_Assess_Framework".audit_documents USING btree (category_id);


--
-- Name: idx_audit_documents_finding_id; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_documents_finding_id ON "Risk_Assess_Framework".audit_documents USING btree (finding_id);


--
-- Name: idx_audit_documents_procedure_id; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_documents_procedure_id ON "Risk_Assess_Framework".audit_documents USING btree (procedure_id);


--
-- Name: idx_audit_documents_recommendation_id; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_documents_recommendation_id ON "Risk_Assess_Framework".audit_documents USING btree (recommendation_id);


--
-- Name: idx_audit_documents_reference_id; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_documents_reference_id ON "Risk_Assess_Framework".audit_documents USING btree (reference_id);


--
-- Name: idx_audit_documents_visibility_level_id; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_documents_visibility_level_id ON "Risk_Assess_Framework".audit_documents USING btree (visibility_level_id);


--
-- Name: idx_audit_documents_working_paper_id; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_documents_working_paper_id ON "Risk_Assess_Framework".audit_documents USING btree (working_paper_id);


--
-- Name: idx_audit_evidence_request_items_fulfilled_document_id; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_evidence_request_items_fulfilled_document_id ON "Risk_Assess_Framework".audit_evidence_request_items USING btree (fulfilled_document_id);


--
-- Name: idx_audit_evidence_request_items_request_id; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_evidence_request_items_request_id ON "Risk_Assess_Framework".audit_evidence_request_items USING btree (request_id);


--
-- Name: idx_audit_evidence_requests_due_date; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_evidence_requests_due_date ON "Risk_Assess_Framework".audit_evidence_requests USING btree (due_date);


--
-- Name: idx_audit_evidence_requests_reference_id; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_evidence_requests_reference_id ON "Risk_Assess_Framework".audit_evidence_requests USING btree (reference_id);


--
-- Name: idx_audit_evidence_requests_status_id; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_evidence_requests_status_id ON "Risk_Assess_Framework".audit_evidence_requests USING btree (status_id);


--
-- Name: idx_audit_findings_assigned_to; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_findings_assigned_to ON "Risk_Assess_Framework".audit_findings USING btree (assigned_to_user_id);


--
-- Name: idx_audit_findings_due_date; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_findings_due_date ON "Risk_Assess_Framework".audit_findings USING btree (due_date);


--
-- Name: idx_audit_findings_identified_date; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_findings_identified_date ON "Risk_Assess_Framework".audit_findings USING btree (identified_date);


--
-- Name: idx_audit_findings_reference; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_findings_reference ON "Risk_Assess_Framework".audit_findings USING btree (reference_id);


--
-- Name: idx_audit_findings_severity; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_findings_severity ON "Risk_Assess_Framework".audit_findings USING btree (severity_id);


--
-- Name: idx_audit_findings_status; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_findings_status ON "Risk_Assess_Framework".audit_findings USING btree (status_id);


--
-- Name: idx_audit_findings_universe; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_findings_universe ON "Risk_Assess_Framework".audit_findings USING btree (audit_universe_id);


--
-- Name: idx_audit_fs_mappings_reference; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_fs_mappings_reference ON "Risk_Assess_Framework".audit_financial_statement_mappings USING btree (reference_id, fiscal_year, statement_type, section_name, display_order);


--
-- Name: idx_audit_fs_profiles_reference; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_fs_profiles_reference ON "Risk_Assess_Framework".audit_financial_statement_mapping_profiles USING btree (reference_id, is_active, is_default);


--
-- Name: idx_audit_gl_journal_entries_posting_date; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_gl_journal_entries_posting_date ON "Risk_Assess_Framework".audit_gl_journal_entries USING btree (posting_date);


--
-- Name: idx_audit_gl_journal_entries_reference_year; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_gl_journal_entries_reference_year ON "Risk_Assess_Framework".audit_gl_journal_entries USING btree (reference_id, fiscal_year, fiscal_period);


--
-- Name: idx_audit_gl_journal_entries_user; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_gl_journal_entries_user ON "Risk_Assess_Framework".audit_gl_journal_entries USING btree (user_name, user_id);


--
-- Name: idx_audit_holiday_calendar_date; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_holiday_calendar_date ON "Risk_Assess_Framework".audit_holiday_calendar USING btree (holiday_date);


--
-- Name: idx_audit_industry_benchmarks_metric; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_industry_benchmarks_metric ON "Risk_Assess_Framework".audit_industry_benchmarks USING btree (metric_name, fiscal_year);


--
-- Name: idx_audit_industry_benchmarks_reference_year; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_industry_benchmarks_reference_year ON "Risk_Assess_Framework".audit_industry_benchmarks USING btree (reference_id, fiscal_year);


--
-- Name: idx_audit_login_events_status; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_login_events_status ON "Risk_Assess_Framework".audit_login_events USING btree (status, occurred_at DESC);


--
-- Name: idx_audit_login_events_user_id; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_login_events_user_id ON "Risk_Assess_Framework".audit_login_events USING btree (user_id, occurred_at DESC);


--
-- Name: idx_audit_management_actions_due_date; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_management_actions_due_date ON "Risk_Assess_Framework".audit_management_actions USING btree (due_date);


--
-- Name: idx_audit_management_actions_recommendation_id; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_management_actions_recommendation_id ON "Risk_Assess_Framework".audit_management_actions USING btree (recommendation_id);


--
-- Name: idx_audit_management_actions_reference_id; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_management_actions_reference_id ON "Risk_Assess_Framework".audit_management_actions USING btree (reference_id);


--
-- Name: idx_audit_management_actions_status; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_management_actions_status ON "Risk_Assess_Framework".audit_management_actions USING btree (status);


--
-- Name: idx_audit_materiality_approval_history_reference; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_materiality_approval_history_reference ON "Risk_Assess_Framework".audit_materiality_approval_history USING btree (reference_id, created_at DESC);


--
-- Name: idx_audit_materiality_benchmark_profiles_active; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_materiality_benchmark_profiles_active ON "Risk_Assess_Framework".audit_materiality_benchmark_profiles USING btree (is_active, sort_order, profile_name);


--
-- Name: idx_audit_materiality_calculations_active_reference; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE UNIQUE INDEX idx_audit_materiality_calculations_active_reference ON "Risk_Assess_Framework".audit_materiality_calculations USING btree (reference_id) WHERE (is_active = true);


--
-- Name: idx_audit_materiality_calculations_reference_id; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_materiality_calculations_reference_id ON "Risk_Assess_Framework".audit_materiality_calculations USING btree (reference_id, created_at DESC);


--
-- Name: idx_audit_materiality_candidates_reference_id; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_materiality_candidates_reference_id ON "Risk_Assess_Framework".audit_materiality_candidates USING btree (reference_id, generated_at DESC);


--
-- Name: idx_audit_materiality_scope_links_reference_id; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_materiality_scope_links_reference_id ON "Risk_Assess_Framework".audit_materiality_scope_links USING btree (reference_id, materiality_calculation_id);


--
-- Name: idx_audit_misstatements_reference_id; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_misstatements_reference_id ON "Risk_Assess_Framework".audit_misstatements USING btree (reference_id, created_at DESC);


--
-- Name: idx_audit_notifications_recipient; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_notifications_recipient ON "Risk_Assess_Framework".audit_notifications USING btree (recipient_user_id, is_read);


--
-- Name: idx_audit_notifications_reference_id; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_notifications_reference_id ON "Risk_Assess_Framework".audit_notifications USING btree (reference_id);


--
-- Name: idx_audit_procedure_assignments_assignee; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_procedure_assignments_assignee ON "Risk_Assess_Framework".audit_procedure_assignments USING btree (assigned_to_user_id, status);


--
-- Name: idx_audit_procedure_assignments_procedure_id; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_procedure_assignments_procedure_id ON "Risk_Assess_Framework".audit_procedure_assignments USING btree (procedure_id);


--
-- Name: idx_audit_procedure_assignments_reference_id; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_procedure_assignments_reference_id ON "Risk_Assess_Framework".audit_procedure_assignments USING btree (reference_id);


--
-- Name: idx_audit_procedure_assignments_scope_item_id; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_procedure_assignments_scope_item_id ON "Risk_Assess_Framework".audit_procedure_assignments USING btree (scope_item_id);


--
-- Name: idx_audit_procedure_assignments_working_paper_id; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_procedure_assignments_working_paper_id ON "Risk_Assess_Framework".audit_procedure_assignments USING btree (working_paper_id);


--
-- Name: idx_audit_procedure_steps_procedure_id; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_procedure_steps_procedure_id ON "Risk_Assess_Framework".audit_procedure_steps USING btree (procedure_id, step_number);


--
-- Name: idx_audit_procedures_applicable_engagement_type_id; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_procedures_applicable_engagement_type_id ON "Risk_Assess_Framework".audit_procedures USING btree (applicable_engagement_type_id);


--
-- Name: idx_audit_procedures_audit_universe_id; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_procedures_audit_universe_id ON "Risk_Assess_Framework".audit_procedures USING btree (audit_universe_id);


--
-- Name: idx_audit_procedures_is_template; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_procedures_is_template ON "Risk_Assess_Framework".audit_procedures USING btree (is_template);


--
-- Name: idx_audit_procedures_reference_id; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_procedures_reference_id ON "Risk_Assess_Framework".audit_procedures USING btree (reference_id);


--
-- Name: idx_audit_procedures_status_id; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_procedures_status_id ON "Risk_Assess_Framework".audit_procedures USING btree (status_id);


--
-- Name: idx_audit_procedures_type_id; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_procedures_type_id ON "Risk_Assess_Framework".audit_procedures USING btree (procedure_type_id);


--
-- Name: idx_audit_project_collaborators_project_id; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_project_collaborators_project_id ON "Risk_Assess_Framework".audit_project_collaborators USING btree (project_id);


--
-- Name: idx_audit_project_collaborators_user_id; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_project_collaborators_user_id ON "Risk_Assess_Framework".audit_project_collaborators USING btree (user_id);


--
-- Name: idx_audit_reasonability_forecasts_metric; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_reasonability_forecasts_metric ON "Risk_Assess_Framework".audit_reasonability_forecasts USING btree (metric_name, fiscal_year);


--
-- Name: idx_audit_reasonability_forecasts_reference_year; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_reasonability_forecasts_reference_year ON "Risk_Assess_Framework".audit_reasonability_forecasts USING btree (reference_id, fiscal_year, fiscal_period);


--
-- Name: idx_audit_recommendations_finding; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_recommendations_finding ON "Risk_Assess_Framework".audit_recommendations USING btree (finding_id);


--
-- Name: idx_audit_recommendations_responsible; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_recommendations_responsible ON "Risk_Assess_Framework".audit_recommendations USING btree (responsible_user_id);


--
-- Name: idx_audit_recommendations_status; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_recommendations_status ON "Risk_Assess_Framework".audit_recommendations USING btree (status_id);


--
-- Name: idx_audit_recommendations_target_date; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_recommendations_target_date ON "Risk_Assess_Framework".audit_recommendations USING btree (target_date);


--
-- Name: idx_audit_reference_collaborators_reference_id; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_reference_collaborators_reference_id ON "Risk_Assess_Framework".audit_reference_collaborators USING btree (reference_id);


--
-- Name: idx_audit_reference_collaborators_user_id; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_reference_collaborators_user_id ON "Risk_Assess_Framework".audit_reference_collaborators USING btree (user_id);


--
-- Name: idx_audit_review_notes_review_id; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_review_notes_review_id ON "Risk_Assess_Framework".audit_review_notes USING btree (review_id, status);


--
-- Name: idx_audit_review_notes_section_id; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_review_notes_section_id ON "Risk_Assess_Framework".audit_review_notes USING btree (working_paper_section_id);


--
-- Name: idx_audit_reviews_entity; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_reviews_entity ON "Risk_Assess_Framework".audit_reviews USING btree (entity_type, entity_id, status);


--
-- Name: idx_audit_reviews_reference_id; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_reviews_reference_id ON "Risk_Assess_Framework".audit_reviews USING btree (reference_id);


--
-- Name: idx_audit_reviews_reviewer; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_reviews_reviewer ON "Risk_Assess_Framework".audit_reviews USING btree (assigned_reviewer_user_id, status);


--
-- Name: idx_audit_risk_control_matrix_procedure_id; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_risk_control_matrix_procedure_id ON "Risk_Assess_Framework".audit_risk_control_matrix USING btree (procedure_id);


--
-- Name: idx_audit_risk_control_matrix_reference_id; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_risk_control_matrix_reference_id ON "Risk_Assess_Framework".audit_risk_control_matrix USING btree (reference_id);


--
-- Name: idx_audit_risk_control_matrix_scope_item_id; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_risk_control_matrix_scope_item_id ON "Risk_Assess_Framework".audit_risk_control_matrix USING btree (scope_item_id);


--
-- Name: idx_audit_scope_items_plan_id; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_scope_items_plan_id ON "Risk_Assess_Framework".audit_scope_items USING btree (plan_id);


--
-- Name: idx_audit_scope_items_procedure_id; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_scope_items_procedure_id ON "Risk_Assess_Framework".audit_scope_items USING btree (procedure_id);


--
-- Name: idx_audit_scope_items_reference_id; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_scope_items_reference_id ON "Risk_Assess_Framework".audit_scope_items USING btree (reference_id);


--
-- Name: idx_audit_signoffs_entity; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_signoffs_entity ON "Risk_Assess_Framework".audit_signoffs USING btree (entity_type, entity_id, signoff_type);


--
-- Name: idx_audit_signoffs_reference_id; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_signoffs_reference_id ON "Risk_Assess_Framework".audit_signoffs USING btree (reference_id, signed_at DESC);


--
-- Name: idx_audit_support_requests_reference; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_support_requests_reference ON "Risk_Assess_Framework".audit_substantive_support_requests USING btree (reference_id, fiscal_year, support_status, requested_at DESC);


--
-- Name: idx_audit_tasks_assignee; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_tasks_assignee ON "Risk_Assess_Framework".audit_tasks USING btree (assigned_to_user_id, status);


--
-- Name: idx_audit_tasks_reference_id; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_tasks_reference_id ON "Risk_Assess_Framework".audit_tasks USING btree (reference_id);


--
-- Name: idx_audit_tasks_workflow_instance_id; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_tasks_workflow_instance_id ON "Risk_Assess_Framework".audit_tasks USING btree (workflow_instance_id);


--
-- Name: idx_audit_trail_entity_changes_event; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_trail_entity_changes_event ON "Risk_Assess_Framework".audit_trail_entity_changes USING btree (audit_trail_event_id);


--
-- Name: idx_audit_trail_events_entity; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_trail_events_entity ON "Risk_Assess_Framework".audit_trail_events USING btree (entity_type, entity_id, event_time DESC);


--
-- Name: idx_audit_trail_events_reference_time; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_trail_events_reference_time ON "Risk_Assess_Framework".audit_trail_events USING btree (reference_id, event_time DESC);


--
-- Name: idx_audit_trail_events_workflow; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_trail_events_workflow ON "Risk_Assess_Framework".audit_trail_events USING btree (workflow_instance_id, event_time DESC);


--
-- Name: idx_audit_trial_balance_account; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_trial_balance_account ON "Risk_Assess_Framework".audit_trial_balance_snapshots USING btree (account_number, fiscal_year);


--
-- Name: idx_audit_trial_balance_reference_year; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_trial_balance_reference_year ON "Risk_Assess_Framework".audit_trial_balance_snapshots USING btree (reference_id, fiscal_year);


--
-- Name: idx_audit_universe_code; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_universe_code ON "Risk_Assess_Framework".audit_universe USING btree (code);


--
-- Name: idx_audit_universe_dept_link_dept; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_universe_dept_link_dept ON "Risk_Assess_Framework".audit_universe_department_link USING btree (department_id);


--
-- Name: idx_audit_universe_dept_link_universe; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_universe_dept_link_universe ON "Risk_Assess_Framework".audit_universe_department_link USING btree (audit_universe_id);


--
-- Name: idx_audit_universe_is_active; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_universe_is_active ON "Risk_Assess_Framework".audit_universe USING btree (is_active);


--
-- Name: idx_audit_universe_level; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_universe_level ON "Risk_Assess_Framework".audit_universe USING btree (level);


--
-- Name: idx_audit_universe_next_audit; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_universe_next_audit ON "Risk_Assess_Framework".audit_universe USING btree (next_audit_date);


--
-- Name: idx_audit_universe_parent_id; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_universe_parent_id ON "Risk_Assess_Framework".audit_universe USING btree (parent_id);


--
-- Name: idx_audit_universe_risk_rating; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_universe_risk_rating ON "Risk_Assess_Framework".audit_universe USING btree (risk_rating);


--
-- Name: idx_audit_usage_events_module_time; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_usage_events_module_time ON "Risk_Assess_Framework".audit_usage_events USING btree (module_name, event_time DESC);


--
-- Name: idx_audit_usage_events_reference_id; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_usage_events_reference_id ON "Risk_Assess_Framework".audit_usage_events USING btree (reference_id);


--
-- Name: idx_audit_walkthrough_exceptions_walkthrough_id; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_walkthrough_exceptions_walkthrough_id ON "Risk_Assess_Framework".audit_walkthrough_exceptions USING btree (walkthrough_id);


--
-- Name: idx_audit_walkthroughs_procedure_id; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_walkthroughs_procedure_id ON "Risk_Assess_Framework".audit_walkthroughs USING btree (procedure_id);


--
-- Name: idx_audit_walkthroughs_reference_id; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_walkthroughs_reference_id ON "Risk_Assess_Framework".audit_walkthroughs USING btree (reference_id);


--
-- Name: idx_audit_walkthroughs_scope_item_id; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_walkthroughs_scope_item_id ON "Risk_Assess_Framework".audit_walkthroughs USING btree (scope_item_id);


--
-- Name: idx_audit_workflow_events_reference_id; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_workflow_events_reference_id ON "Risk_Assess_Framework".audit_workflow_events USING btree (reference_id, event_time DESC);


--
-- Name: idx_audit_workflow_events_workflow_instance_id; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_workflow_events_workflow_instance_id ON "Risk_Assess_Framework".audit_workflow_events USING btree (workflow_instance_id, event_time DESC);


--
-- Name: idx_audit_workflow_instances_entity; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_workflow_instances_entity ON "Risk_Assess_Framework".audit_workflow_instances USING btree (entity_type, entity_id);


--
-- Name: idx_audit_workflow_instances_reference_id; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_workflow_instances_reference_id ON "Risk_Assess_Framework".audit_workflow_instances USING btree (reference_id);


--
-- Name: idx_audit_workflow_instances_status; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_workflow_instances_status ON "Risk_Assess_Framework".audit_workflow_instances USING btree (status, is_active);


--
-- Name: idx_audit_workflow_tasks_assignee; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_workflow_tasks_assignee ON "Risk_Assess_Framework".audit_workflow_tasks USING btree (assignee_user_id, status);


--
-- Name: idx_audit_workflow_tasks_external_task_id; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_workflow_tasks_external_task_id ON "Risk_Assess_Framework".audit_workflow_tasks USING btree (external_task_id);


--
-- Name: idx_audit_workflow_tasks_reference_id; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_workflow_tasks_reference_id ON "Risk_Assess_Framework".audit_workflow_tasks USING btree (reference_id);


--
-- Name: idx_audit_working_paper_sections_working_paper_id; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_working_paper_sections_working_paper_id ON "Risk_Assess_Framework".audit_working_paper_sections USING btree (working_paper_id, section_order);


--
-- Name: idx_audit_working_papers_applicable_engagement_type_id; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_working_papers_applicable_engagement_type_id ON "Risk_Assess_Framework".audit_working_papers USING btree (applicable_engagement_type_id);


--
-- Name: idx_audit_working_papers_is_template; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_working_papers_is_template ON "Risk_Assess_Framework".audit_working_papers USING btree (is_template);


--
-- Name: idx_audit_working_papers_procedure_id; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_working_papers_procedure_id ON "Risk_Assess_Framework".audit_working_papers USING btree (procedure_id);


--
-- Name: idx_audit_working_papers_reference_id; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_working_papers_reference_id ON "Risk_Assess_Framework".audit_working_papers USING btree (reference_id);


--
-- Name: idx_audit_working_papers_status_id; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_audit_working_papers_status_id ON "Risk_Assess_Framework".audit_working_papers USING btree (status_id);


--
-- Name: idx_departments_created_at; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_departments_created_at ON "Risk_Assess_Framework".departments USING btree (created_at);


--
-- Name: idx_departments_name; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_departments_name ON "Risk_Assess_Framework".departments USING btree (name);


--
-- Name: idx_departments_risk_level_id; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_departments_risk_level_id ON "Risk_Assess_Framework".departments USING btree (risk_level_id);


--
-- Name: idx_market_data_symbol_date; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_market_data_symbol_date ON "Risk_Assess_Framework".market_data USING btree (symbol, date_time);


--
-- Name: idx_projects_created_at; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_projects_created_at ON "Risk_Assess_Framework".projects USING btree (created_at);


--
-- Name: idx_projects_dates; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_projects_dates ON "Risk_Assess_Framework".projects USING btree (start_date, end_date);


--
-- Name: idx_projects_department_id; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_projects_department_id ON "Risk_Assess_Framework".projects USING btree (department_id);


--
-- Name: idx_projects_manager; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_projects_manager ON "Risk_Assess_Framework".projects USING btree (manager);


--
-- Name: idx_projects_risk_level_id; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_projects_risk_level_id ON "Risk_Assess_Framework".projects USING btree (risk_level_id);


--
-- Name: idx_projects_status_id; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_projects_status_id ON "Risk_Assess_Framework".projects USING btree (status_id);


--
-- Name: idx_ra_assessmentstatus_name; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_ra_assessmentstatus_name ON "Risk_Assess_Framework".ra_assessmentstatus USING btree (name);


--
-- Name: idx_ra_assessmentstatus_sort_order; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_ra_assessmentstatus_sort_order ON "Risk_Assess_Framework".ra_assessmentstatus USING btree (sort_order);


--
-- Name: idx_ra_projectstatus_name; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_ra_projectstatus_name ON "Risk_Assess_Framework".ra_projectstatus USING btree (name);


--
-- Name: idx_ra_projectstatus_sort_order; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_ra_projectstatus_sort_order ON "Risk_Assess_Framework".ra_projectstatus USING btree (sort_order);


--
-- Name: idx_ra_referencestatus_name; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_ra_referencestatus_name ON "Risk_Assess_Framework".ra_referencestatus USING btree (name);


--
-- Name: idx_ra_referencestatus_sort_order; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_ra_referencestatus_sort_order ON "Risk_Assess_Framework".ra_referencestatus USING btree (sort_order);


--
-- Name: idx_ra_risklevels_name; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_ra_risklevels_name ON "Risk_Assess_Framework".ra_risklevels USING btree (name);


--
-- Name: idx_ra_risklevels_sort_order; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_ra_risklevels_sort_order ON "Risk_Assess_Framework".ra_risklevels USING btree (sort_order);


--
-- Name: idx_ra_userroles_name; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_ra_userroles_name ON "Risk_Assess_Framework".ra_userroles USING btree (name);


--
-- Name: idx_ra_userroles_sort_order; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_ra_userroles_sort_order ON "Risk_Assess_Framework".ra_userroles USING btree (sort_order);


--
-- Name: idx_risk_trend_date; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_risk_trend_date ON "Risk_Assess_Framework".risk_trend_history USING btree (snapshot_date);


--
-- Name: idx_risk_trend_reference; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_risk_trend_reference ON "Risk_Assess_Framework".risk_trend_history USING btree (reference_id);


--
-- Name: idx_risk_trend_universe; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_risk_trend_universe ON "Risk_Assess_Framework".risk_trend_history USING btree (audit_universe_id);


--
-- Name: idx_riskassessment_auditor_id; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_riskassessment_auditor_id ON "Risk_Assess_Framework".riskassessment USING btree (auditor_id);


--
-- Name: idx_riskassessment_created_at; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_riskassessment_created_at ON "Risk_Assess_Framework".riskassessment USING btree (created_at);


--
-- Name: idx_riskassessment_department_id; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_riskassessment_department_id ON "Risk_Assess_Framework".riskassessment USING btree (department_id);


--
-- Name: idx_riskassessment_project_id; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_riskassessment_project_id ON "Risk_Assess_Framework".riskassessment USING btree (project_id);


--
-- Name: idx_riskassessment_status_id; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_riskassessment_status_id ON "Risk_Assess_Framework".riskassessment USING btree (status_id);


--
-- Name: idx_riskassessmentreference_department_id; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_riskassessmentreference_department_id ON "Risk_Assess_Framework".riskassessmentreference USING btree (department_id);


--
-- Name: idx_riskassessmentreference_is_archived; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_riskassessmentreference_is_archived ON "Risk_Assess_Framework".riskassessmentreference USING btree (is_archived);


--
-- Name: idx_riskassessmentreference_project_id; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_riskassessmentreference_project_id ON "Risk_Assess_Framework".riskassessmentreference USING btree (project_id);


--
-- Name: idx_riskassessmentreference_status_id; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_riskassessmentreference_status_id ON "Risk_Assess_Framework".riskassessmentreference USING btree (status_id);


--
-- Name: idx_riskassessmentreference_title; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_riskassessmentreference_title ON "Risk_Assess_Framework".riskassessmentreference USING btree (title);


--
-- Name: idx_users_created_at; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_users_created_at ON "Risk_Assess_Framework".users USING btree (created_at);


--
-- Name: idx_users_department_id; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_users_department_id ON "Risk_Assess_Framework".users USING btree (department_id);


--
-- Name: idx_users_email; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_users_email ON "Risk_Assess_Framework".users USING btree (email);


--
-- Name: idx_users_is_active; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_users_is_active ON "Risk_Assess_Framework".users USING btree (is_active);


--
-- Name: idx_users_role_id; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_users_role_id ON "Risk_Assess_Framework".users USING btree (role_id);


--
-- Name: idx_users_username; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_users_username ON "Risk_Assess_Framework".users USING btree (username);


--
-- Name: idx_wp_references_from_id; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_wp_references_from_id ON "Risk_Assess_Framework".audit_working_paper_references USING btree (from_working_paper_id);


--
-- Name: idx_wp_references_to_id; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_wp_references_to_id ON "Risk_Assess_Framework".audit_working_paper_references USING btree (to_working_paper_id);


--
-- Name: idx_wp_signoffs_working_paper_id; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE INDEX idx_wp_signoffs_working_paper_id ON "Risk_Assess_Framework".audit_working_paper_signoffs USING btree (working_paper_id);


--
-- Name: uq_audit_document_permission_grants_role; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE UNIQUE INDEX uq_audit_document_permission_grants_role ON "Risk_Assess_Framework".audit_document_permission_grants USING btree (document_id, grantee_role_name, permission_level) WHERE (grantee_role_name IS NOT NULL);


--
-- Name: uq_audit_document_permission_grants_user; Type: INDEX; Schema: Risk_Assess_Framework; Owner: -
--

CREATE UNIQUE INDEX uq_audit_document_permission_grants_user ON "Risk_Assess_Framework".audit_document_permission_grants USING btree (document_id, grantee_user_id, permission_level) WHERE (grantee_user_id IS NOT NULL);


--
-- Name: IX_ControlTest_ControlId; Type: INDEX; Schema: Risk_Workflow; Owner: -
--

CREATE INDEX "IX_ControlTest_ControlId" ON "Risk_Workflow"."ControlTest" USING btree ("ControlId");


--
-- Name: IX_ControlTest_RiskAssessmentId; Type: INDEX; Schema: Risk_Workflow; Owner: -
--

CREATE INDEX "IX_ControlTest_RiskAssessmentId" ON "Risk_Workflow"."ControlTest" USING btree ("RiskAssessmentId");


--
-- Name: IX_ControlTest_TesterId; Type: INDEX; Schema: Risk_Workflow; Owner: -
--

CREATE INDEX "IX_ControlTest_TesterId" ON "Risk_Workflow"."ControlTest" USING btree ("TesterId");


--
-- Name: IX_Elsa_ActivityExecutionRecords_ActivityId; Type: INDEX; Schema: Risk_Workflow; Owner: -
--

CREATE INDEX "IX_Elsa_ActivityExecutionRecords_ActivityId" ON "Risk_Workflow"."Elsa_ActivityExecutionRecords" USING btree ("ActivityId");


--
-- Name: IX_Elsa_ActivityExecutionRecords_ActivityType; Type: INDEX; Schema: Risk_Workflow; Owner: -
--

CREATE INDEX "IX_Elsa_ActivityExecutionRecords_ActivityType" ON "Risk_Workflow"."Elsa_ActivityExecutionRecords" USING btree ("ActivityType");


--
-- Name: IX_Elsa_ActivityExecutionRecords_CompletedAt; Type: INDEX; Schema: Risk_Workflow; Owner: -
--

CREATE INDEX "IX_Elsa_ActivityExecutionRecords_CompletedAt" ON "Risk_Workflow"."Elsa_ActivityExecutionRecords" USING btree ("CompletedAt");


--
-- Name: IX_Elsa_ActivityExecutionRecords_StartedAt; Type: INDEX; Schema: Risk_Workflow; Owner: -
--

CREATE INDEX "IX_Elsa_ActivityExecutionRecords_StartedAt" ON "Risk_Workflow"."Elsa_ActivityExecutionRecords" USING btree ("StartedAt");


--
-- Name: IX_Elsa_ActivityExecutionRecords_WorkflowInstanceId; Type: INDEX; Schema: Risk_Workflow; Owner: -
--

CREATE INDEX "IX_Elsa_ActivityExecutionRecords_WorkflowInstanceId" ON "Risk_Workflow"."Elsa_ActivityExecutionRecords" USING btree ("WorkflowInstanceId");


--
-- Name: IX_Elsa_Bookmarks_ActivityTypeName; Type: INDEX; Schema: Risk_Workflow; Owner: -
--

CREATE INDEX "IX_Elsa_Bookmarks_ActivityTypeName" ON "Risk_Workflow"."Elsa_Bookmarks" USING btree ("ActivityTypeName");


--
-- Name: IX_Elsa_Bookmarks_CorrelationId; Type: INDEX; Schema: Risk_Workflow; Owner: -
--

CREATE INDEX "IX_Elsa_Bookmarks_CorrelationId" ON "Risk_Workflow"."Elsa_Bookmarks" USING btree ("CorrelationId");


--
-- Name: IX_Elsa_Bookmarks_Hash; Type: INDEX; Schema: Risk_Workflow; Owner: -
--

CREATE INDEX "IX_Elsa_Bookmarks_Hash" ON "Risk_Workflow"."Elsa_Bookmarks" USING btree ("Hash");


--
-- Name: IX_Elsa_Bookmarks_WorkflowInstanceId; Type: INDEX; Schema: Risk_Workflow; Owner: -
--

CREATE INDEX "IX_Elsa_Bookmarks_WorkflowInstanceId" ON "Risk_Workflow"."Elsa_Bookmarks" USING btree ("WorkflowInstanceId");


--
-- Name: IX_Elsa_Triggers_Hash; Type: INDEX; Schema: Risk_Workflow; Owner: -
--

CREATE INDEX "IX_Elsa_Triggers_Hash" ON "Risk_Workflow"."Elsa_Triggers" USING btree ("Hash");


--
-- Name: IX_Elsa_Triggers_Name; Type: INDEX; Schema: Risk_Workflow; Owner: -
--

CREATE INDEX "IX_Elsa_Triggers_Name" ON "Risk_Workflow"."Elsa_Triggers" USING btree ("Name");


--
-- Name: IX_Elsa_Triggers_WorkflowDefinitionId; Type: INDEX; Schema: Risk_Workflow; Owner: -
--

CREATE INDEX "IX_Elsa_Triggers_WorkflowDefinitionId" ON "Risk_Workflow"."Elsa_Triggers" USING btree ("WorkflowDefinitionId");


--
-- Name: IX_Elsa_WorkflowDefinitions_DefinitionId; Type: INDEX; Schema: Risk_Workflow; Owner: -
--

CREATE INDEX "IX_Elsa_WorkflowDefinitions_DefinitionId" ON "Risk_Workflow"."Elsa_WorkflowDefinitions" USING btree ("DefinitionId");


--
-- Name: IX_Elsa_WorkflowDefinitions_IsLatest; Type: INDEX; Schema: Risk_Workflow; Owner: -
--

CREATE INDEX "IX_Elsa_WorkflowDefinitions_IsLatest" ON "Risk_Workflow"."Elsa_WorkflowDefinitions" USING btree ("IsLatest");


--
-- Name: IX_Elsa_WorkflowDefinitions_IsPublished; Type: INDEX; Schema: Risk_Workflow; Owner: -
--

CREATE INDEX "IX_Elsa_WorkflowDefinitions_IsPublished" ON "Risk_Workflow"."Elsa_WorkflowDefinitions" USING btree ("IsPublished");


--
-- Name: IX_Elsa_WorkflowDefinitions_Name; Type: INDEX; Schema: Risk_Workflow; Owner: -
--

CREATE INDEX "IX_Elsa_WorkflowDefinitions_Name" ON "Risk_Workflow"."Elsa_WorkflowDefinitions" USING btree ("Name");


--
-- Name: IX_Elsa_WorkflowDefinitions_UsableAsActivity; Type: INDEX; Schema: Risk_Workflow; Owner: -
--

CREATE INDEX "IX_Elsa_WorkflowDefinitions_UsableAsActivity" ON "Risk_Workflow"."Elsa_WorkflowDefinitions" USING btree ("UsableAsActivity");


--
-- Name: IX_Elsa_WorkflowExecutionLogRecords_ActivityInstanceId; Type: INDEX; Schema: Risk_Workflow; Owner: -
--

CREATE INDEX "IX_Elsa_WorkflowExecutionLogRecords_ActivityInstanceId" ON "Risk_Workflow"."Elsa_WorkflowExecutionLogRecords" USING btree ("ActivityInstanceId");


--
-- Name: IX_Elsa_WorkflowExecutionLogRecords_Sequence; Type: INDEX; Schema: Risk_Workflow; Owner: -
--

CREATE INDEX "IX_Elsa_WorkflowExecutionLogRecords_Sequence" ON "Risk_Workflow"."Elsa_WorkflowExecutionLogRecords" USING btree ("Sequence");


--
-- Name: IX_Elsa_WorkflowExecutionLogRecords_Timestamp; Type: INDEX; Schema: Risk_Workflow; Owner: -
--

CREATE INDEX "IX_Elsa_WorkflowExecutionLogRecords_Timestamp" ON "Risk_Workflow"."Elsa_WorkflowExecutionLogRecords" USING btree ("Timestamp");


--
-- Name: IX_Elsa_WorkflowExecutionLogRecords_WorkflowInstanceId; Type: INDEX; Schema: Risk_Workflow; Owner: -
--

CREATE INDEX "IX_Elsa_WorkflowExecutionLogRecords_WorkflowInstanceId" ON "Risk_Workflow"."Elsa_WorkflowExecutionLogRecords" USING btree ("WorkflowInstanceId");


--
-- Name: IX_Elsa_WorkflowInboxMessages_ActivityTypeName; Type: INDEX; Schema: Risk_Workflow; Owner: -
--

CREATE INDEX "IX_Elsa_WorkflowInboxMessages_ActivityTypeName" ON "Risk_Workflow"."Elsa_WorkflowInboxMessages" USING btree ("ActivityTypeName");


--
-- Name: IX_Elsa_WorkflowInboxMessages_CorrelationId; Type: INDEX; Schema: Risk_Workflow; Owner: -
--

CREATE INDEX "IX_Elsa_WorkflowInboxMessages_CorrelationId" ON "Risk_Workflow"."Elsa_WorkflowInboxMessages" USING btree ("CorrelationId");


--
-- Name: IX_Elsa_WorkflowInboxMessages_CreatedAt; Type: INDEX; Schema: Risk_Workflow; Owner: -
--

CREATE INDEX "IX_Elsa_WorkflowInboxMessages_CreatedAt" ON "Risk_Workflow"."Elsa_WorkflowInboxMessages" USING btree ("CreatedAt");


--
-- Name: IX_Elsa_WorkflowInboxMessages_ExpiresAt; Type: INDEX; Schema: Risk_Workflow; Owner: -
--

CREATE INDEX "IX_Elsa_WorkflowInboxMessages_ExpiresAt" ON "Risk_Workflow"."Elsa_WorkflowInboxMessages" USING btree ("ExpiresAt");


--
-- Name: IX_Elsa_WorkflowInboxMessages_Hash; Type: INDEX; Schema: Risk_Workflow; Owner: -
--

CREATE INDEX "IX_Elsa_WorkflowInboxMessages_Hash" ON "Risk_Workflow"."Elsa_WorkflowInboxMessages" USING btree ("Hash");


--
-- Name: IX_Elsa_WorkflowInboxMessages_WorkflowInstanceId; Type: INDEX; Schema: Risk_Workflow; Owner: -
--

CREATE INDEX "IX_Elsa_WorkflowInboxMessages_WorkflowInstanceId" ON "Risk_Workflow"."Elsa_WorkflowInboxMessages" USING btree ("WorkflowInstanceId");


--
-- Name: IX_Elsa_WorkflowInstances_CorrelationId; Type: INDEX; Schema: Risk_Workflow; Owner: -
--

CREATE INDEX "IX_Elsa_WorkflowInstances_CorrelationId" ON "Risk_Workflow"."Elsa_WorkflowInstances" USING btree ("CorrelationId");


--
-- Name: IX_Elsa_WorkflowInstances_CreatedAt; Type: INDEX; Schema: Risk_Workflow; Owner: -
--

CREATE INDEX "IX_Elsa_WorkflowInstances_CreatedAt" ON "Risk_Workflow"."Elsa_WorkflowInstances" USING btree ("CreatedAt");


--
-- Name: IX_Elsa_WorkflowInstances_DefinitionId; Type: INDEX; Schema: Risk_Workflow; Owner: -
--

CREATE INDEX "IX_Elsa_WorkflowInstances_DefinitionId" ON "Risk_Workflow"."Elsa_WorkflowInstances" USING btree ("DefinitionId");


--
-- Name: IX_Elsa_WorkflowInstances_FinishedAt; Type: INDEX; Schema: Risk_Workflow; Owner: -
--

CREATE INDEX "IX_Elsa_WorkflowInstances_FinishedAt" ON "Risk_Workflow"."Elsa_WorkflowInstances" USING btree ("FinishedAt");


--
-- Name: IX_Elsa_WorkflowInstances_Status; Type: INDEX; Schema: Risk_Workflow; Owner: -
--

CREATE INDEX "IX_Elsa_WorkflowInstances_Status" ON "Risk_Workflow"."Elsa_WorkflowInstances" USING btree ("Status");


--
-- Name: IX_Elsa_WorkflowInstances_SubStatus; Type: INDEX; Schema: Risk_Workflow; Owner: -
--

CREATE INDEX "IX_Elsa_WorkflowInstances_SubStatus" ON "Risk_Workflow"."Elsa_WorkflowInstances" USING btree ("SubStatus");


--
-- Name: IX_Elsa_WorkflowInstances_UpdatedAt; Type: INDEX; Schema: Risk_Workflow; Owner: -
--

CREATE INDEX "IX_Elsa_WorkflowInstances_UpdatedAt" ON "Risk_Workflow"."Elsa_WorkflowInstances" USING btree ("UpdatedAt");


--
-- Name: IX_ExecutionLog_WorkflowInstanceId; Type: INDEX; Schema: Risk_Workflow; Owner: -
--

CREATE INDEX "IX_ExecutionLog_WorkflowInstanceId" ON "Risk_Workflow"."WorkflowExecutionLog" USING btree ("WorkflowInstanceId");


--
-- Name: IX_RemediationTask_AssigneeId; Type: INDEX; Schema: Risk_Workflow; Owner: -
--

CREATE INDEX "IX_RemediationTask_AssigneeId" ON "Risk_Workflow"."RemediationTask" USING btree ("AssigneeId");


--
-- Name: IX_RemediationTask_Status; Type: INDEX; Schema: Risk_Workflow; Owner: -
--

CREATE INDEX "IX_RemediationTask_Status" ON "Risk_Workflow"."RemediationTask" USING btree ("Status");


--
-- Name: IX_RiskAssessmentApproval_ApproverId; Type: INDEX; Schema: Risk_Workflow; Owner: -
--

CREATE INDEX "IX_RiskAssessmentApproval_ApproverId" ON "Risk_Workflow"."RiskAssessmentApproval" USING btree ("ApproverId");


--
-- Name: IX_RiskAssessmentApproval_RiskAssessmentId; Type: INDEX; Schema: Risk_Workflow; Owner: -
--

CREATE INDEX "IX_RiskAssessmentApproval_RiskAssessmentId" ON "Risk_Workflow"."RiskAssessmentApproval" USING btree ("RiskAssessmentId");


--
-- Name: IX_WorkflowInstance_CorrelationId; Type: INDEX; Schema: Risk_Workflow; Owner: -
--

CREATE INDEX "IX_WorkflowInstance_CorrelationId" ON "Risk_Workflow"."WorkflowInstance" USING btree ("CorrelationId");


--
-- Name: IX_WorkflowInstance_Status; Type: INDEX; Schema: Risk_Workflow; Owner: -
--

CREATE INDEX "IX_WorkflowInstance_Status" ON "Risk_Workflow"."WorkflowInstance" USING btree ("Status");


--
-- Name: audit_procedures trigger_generate_audit_procedure_code; Type: TRIGGER; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TRIGGER trigger_generate_audit_procedure_code BEFORE INSERT ON "Risk_Assess_Framework".audit_procedures FOR EACH ROW EXECUTE FUNCTION "Risk_Assess_Framework".generate_audit_procedure_code();


--
-- Name: audit_documents trigger_generate_document_code; Type: TRIGGER; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TRIGGER trigger_generate_document_code BEFORE INSERT ON "Risk_Assess_Framework".audit_documents FOR EACH ROW EXECUTE FUNCTION "Risk_Assess_Framework".generate_document_code();


--
-- Name: audit_evidence_requests trigger_generate_evidence_request_number; Type: TRIGGER; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TRIGGER trigger_generate_evidence_request_number BEFORE INSERT ON "Risk_Assess_Framework".audit_evidence_requests FOR EACH ROW EXECUTE FUNCTION "Risk_Assess_Framework".generate_evidence_request_number();


--
-- Name: audit_findings trigger_generate_finding_number; Type: TRIGGER; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TRIGGER trigger_generate_finding_number BEFORE INSERT ON "Risk_Assess_Framework".audit_findings FOR EACH ROW EXECUTE FUNCTION "Risk_Assess_Framework".generate_finding_number();


--
-- Name: audit_recommendations trigger_generate_recommendation_number; Type: TRIGGER; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TRIGGER trigger_generate_recommendation_number BEFORE INSERT ON "Risk_Assess_Framework".audit_recommendations FOR EACH ROW EXECUTE FUNCTION "Risk_Assess_Framework".generate_recommendation_number();


--
-- Name: audit_working_papers trigger_generate_working_paper_code; Type: TRIGGER; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TRIGGER trigger_generate_working_paper_code BEFORE INSERT ON "Risk_Assess_Framework".audit_working_papers FOR EACH ROW EXECUTE FUNCTION "Risk_Assess_Framework".generate_working_paper_code();


--
-- Name: audit_control_tests trigger_update_audit_control_tests_updated_at; Type: TRIGGER; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TRIGGER trigger_update_audit_control_tests_updated_at BEFORE UPDATE ON "Risk_Assess_Framework".audit_control_tests FOR EACH ROW EXECUTE FUNCTION "Risk_Assess_Framework".set_audit_updated_at();


--
-- Name: audit_domain_rule_packages trigger_update_audit_domain_rule_packages_updated_at; Type: TRIGGER; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TRIGGER trigger_update_audit_domain_rule_packages_updated_at BEFORE UPDATE ON "Risk_Assess_Framework".audit_domain_rule_packages FOR EACH ROW EXECUTE FUNCTION "Risk_Assess_Framework".update_audit_domain_rule_packages_updated_at();


--
-- Name: audit_engagement_plans trigger_update_audit_engagement_plan_updated_at; Type: TRIGGER; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TRIGGER trigger_update_audit_engagement_plan_updated_at BEFORE UPDATE ON "Risk_Assess_Framework".audit_engagement_plans FOR EACH ROW EXECUTE FUNCTION "Risk_Assess_Framework".update_audit_engagement_plan_updated_at();


--
-- Name: audit_finance_finalization trigger_update_audit_finance_finalization_updated_at; Type: TRIGGER; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TRIGGER trigger_update_audit_finance_finalization_updated_at BEFORE UPDATE ON "Risk_Assess_Framework".audit_finance_finalization FOR EACH ROW EXECUTE FUNCTION "Risk_Assess_Framework".update_audit_finance_finalization_updated_at();


--
-- Name: audit_financial_statement_mappings trigger_update_audit_fs_mappings_updated_at; Type: TRIGGER; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TRIGGER trigger_update_audit_fs_mappings_updated_at BEFORE UPDATE ON "Risk_Assess_Framework".audit_financial_statement_mappings FOR EACH ROW EXECUTE FUNCTION "Risk_Assess_Framework".update_audit_fs_mappings_updated_at();


--
-- Name: audit_financial_statement_profile_rules trigger_update_audit_fs_profile_rules_updated_at; Type: TRIGGER; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TRIGGER trigger_update_audit_fs_profile_rules_updated_at BEFORE UPDATE ON "Risk_Assess_Framework".audit_financial_statement_profile_rules FOR EACH ROW EXECUTE FUNCTION "Risk_Assess_Framework".update_audit_fs_profile_rules_updated_at();


--
-- Name: audit_financial_statement_mapping_profiles trigger_update_audit_fs_profiles_updated_at; Type: TRIGGER; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TRIGGER trigger_update_audit_fs_profiles_updated_at BEFORE UPDATE ON "Risk_Assess_Framework".audit_financial_statement_mapping_profiles FOR EACH ROW EXECUTE FUNCTION "Risk_Assess_Framework".update_audit_fs_profiles_updated_at();


--
-- Name: audit_management_actions trigger_update_audit_management_action_updated_at; Type: TRIGGER; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TRIGGER trigger_update_audit_management_action_updated_at BEFORE UPDATE ON "Risk_Assess_Framework".audit_management_actions FOR EACH ROW EXECUTE FUNCTION "Risk_Assess_Framework".update_audit_management_action_updated_at();


--
-- Name: audit_materiality_benchmark_profiles trigger_update_audit_materiality_benchmark_profiles_updated_at; Type: TRIGGER; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TRIGGER trigger_update_audit_materiality_benchmark_profiles_updated_at BEFORE UPDATE ON "Risk_Assess_Framework".audit_materiality_benchmark_profiles FOR EACH ROW EXECUTE FUNCTION "Risk_Assess_Framework".update_audit_materiality_benchmark_profiles_updated_at();


--
-- Name: audit_materiality_calculations trigger_update_audit_materiality_calculations_updated_at; Type: TRIGGER; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TRIGGER trigger_update_audit_materiality_calculations_updated_at BEFORE UPDATE ON "Risk_Assess_Framework".audit_materiality_calculations FOR EACH ROW EXECUTE FUNCTION "Risk_Assess_Framework".update_audit_materiality_calculations_updated_at();


--
-- Name: audit_misstatements trigger_update_audit_misstatements_updated_at; Type: TRIGGER; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TRIGGER trigger_update_audit_misstatements_updated_at BEFORE UPDATE ON "Risk_Assess_Framework".audit_misstatements FOR EACH ROW EXECUTE FUNCTION "Risk_Assess_Framework".update_audit_misstatements_updated_at();


--
-- Name: audit_procedure_assignments trigger_update_audit_procedure_assignments_updated_at; Type: TRIGGER; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TRIGGER trigger_update_audit_procedure_assignments_updated_at BEFORE UPDATE ON "Risk_Assess_Framework".audit_procedure_assignments FOR EACH ROW EXECUTE FUNCTION "Risk_Assess_Framework".set_audit_updated_at();


--
-- Name: audit_procedure_steps trigger_update_audit_procedure_steps_updated_at; Type: TRIGGER; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TRIGGER trigger_update_audit_procedure_steps_updated_at BEFORE UPDATE ON "Risk_Assess_Framework".audit_procedure_steps FOR EACH ROW EXECUTE FUNCTION "Risk_Assess_Framework".set_audit_updated_at();


--
-- Name: audit_procedures trigger_update_audit_procedure_updated_at; Type: TRIGGER; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TRIGGER trigger_update_audit_procedure_updated_at BEFORE UPDATE ON "Risk_Assess_Framework".audit_procedures FOR EACH ROW EXECUTE FUNCTION "Risk_Assess_Framework".update_audit_procedure_updated_at();


--
-- Name: audit_project_collaborators trigger_update_audit_project_collaborators_updated_at; Type: TRIGGER; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TRIGGER trigger_update_audit_project_collaborators_updated_at BEFORE UPDATE ON "Risk_Assess_Framework".audit_project_collaborators FOR EACH ROW EXECUTE FUNCTION "Risk_Assess_Framework".update_audit_collaborator_updated_at();


--
-- Name: audit_risk_control_matrix trigger_update_audit_rcm_updated_at; Type: TRIGGER; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TRIGGER trigger_update_audit_rcm_updated_at BEFORE UPDATE ON "Risk_Assess_Framework".audit_risk_control_matrix FOR EACH ROW EXECUTE FUNCTION "Risk_Assess_Framework".update_audit_rcm_updated_at();


--
-- Name: audit_reference_collaborators trigger_update_audit_reference_collaborators_updated_at; Type: TRIGGER; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TRIGGER trigger_update_audit_reference_collaborators_updated_at BEFORE UPDATE ON "Risk_Assess_Framework".audit_reference_collaborators FOR EACH ROW EXECUTE FUNCTION "Risk_Assess_Framework".update_audit_collaborator_updated_at();


--
-- Name: audit_reviews trigger_update_audit_reviews_updated_at; Type: TRIGGER; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TRIGGER trigger_update_audit_reviews_updated_at BEFORE UPDATE ON "Risk_Assess_Framework".audit_reviews FOR EACH ROW EXECUTE FUNCTION "Risk_Assess_Framework".set_audit_updated_at();


--
-- Name: audit_substantive_support_requests trigger_update_audit_support_requests_updated_at; Type: TRIGGER; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TRIGGER trigger_update_audit_support_requests_updated_at BEFORE UPDATE ON "Risk_Assess_Framework".audit_substantive_support_requests FOR EACH ROW EXECUTE FUNCTION "Risk_Assess_Framework".update_audit_support_requests_updated_at();


--
-- Name: audit_tasks trigger_update_audit_tasks_updated_at; Type: TRIGGER; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TRIGGER trigger_update_audit_tasks_updated_at BEFORE UPDATE ON "Risk_Assess_Framework".audit_tasks FOR EACH ROW EXECUTE FUNCTION "Risk_Assess_Framework".set_audit_updated_at();


--
-- Name: audit_walkthroughs trigger_update_audit_walkthrough_updated_at; Type: TRIGGER; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TRIGGER trigger_update_audit_walkthrough_updated_at BEFORE UPDATE ON "Risk_Assess_Framework".audit_walkthroughs FOR EACH ROW EXECUTE FUNCTION "Risk_Assess_Framework".update_audit_walkthrough_updated_at();


--
-- Name: audit_working_paper_sections trigger_update_audit_working_paper_sections_updated_at; Type: TRIGGER; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TRIGGER trigger_update_audit_working_paper_sections_updated_at BEFORE UPDATE ON "Risk_Assess_Framework".audit_working_paper_sections FOR EACH ROW EXECUTE FUNCTION "Risk_Assess_Framework".set_audit_updated_at();


--
-- Name: audit_evidence_requests trigger_update_evidence_request_updated_at; Type: TRIGGER; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TRIGGER trigger_update_evidence_request_updated_at BEFORE UPDATE ON "Risk_Assess_Framework".audit_evidence_requests FOR EACH ROW EXECUTE FUNCTION "Risk_Assess_Framework".update_evidence_request_updated_at();


--
-- Name: audit_working_papers trigger_update_working_paper_updated_at; Type: TRIGGER; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TRIGGER trigger_update_working_paper_updated_at BEFORE UPDATE ON "Risk_Assess_Framework".audit_working_papers FOR EACH ROW EXECUTE FUNCTION "Risk_Assess_Framework".update_working_paper_updated_at();


--
-- Name: accounts update_accounts_updated_at; Type: TRIGGER; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TRIGGER update_accounts_updated_at BEFORE UPDATE ON "Risk_Assess_Framework".accounts FOR EACH ROW EXECUTE FUNCTION "Risk_Assess_Framework".update_updated_at_column();


--
-- Name: departments update_departments_updated_at; Type: TRIGGER; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TRIGGER update_departments_updated_at BEFORE UPDATE ON "Risk_Assess_Framework".departments FOR EACH ROW EXECUTE FUNCTION "Risk_Assess_Framework".update_updated_at_column();


--
-- Name: projects update_projects_updated_at; Type: TRIGGER; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON "Risk_Assess_Framework".projects FOR EACH ROW EXECUTE FUNCTION "Risk_Assess_Framework".update_updated_at_column();


--
-- Name: riskassessment update_riskassessment_updated_at; Type: TRIGGER; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TRIGGER update_riskassessment_updated_at BEFORE UPDATE ON "Risk_Assess_Framework".riskassessment FOR EACH ROW EXECUTE FUNCTION "Risk_Assess_Framework".update_updated_at_column();


--
-- Name: riskassessmentreference update_riskassessmentreference_updated_at; Type: TRIGGER; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TRIGGER update_riskassessmentreference_updated_at BEFORE UPDATE ON "Risk_Assess_Framework".riskassessmentreference FOR EACH ROW EXECUTE FUNCTION "Risk_Assess_Framework".update_updated_at_column();


--
-- Name: users update_users_updated_at; Type: TRIGGER; Schema: Risk_Assess_Framework; Owner: -
--

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON "Risk_Assess_Framework".users FOR EACH ROW EXECUTE FUNCTION "Risk_Assess_Framework".update_updated_at_column();


--
-- Name: accounts accounts_department_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".accounts
    ADD CONSTRAINT accounts_department_id_fkey FOREIGN KEY (department_id) REFERENCES "Risk_Assess_Framework".departments(id) ON DELETE SET NULL;


--
-- Name: accounts accounts_role_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".accounts
    ADD CONSTRAINT accounts_role_id_fkey FOREIGN KEY (role_id) REFERENCES "Risk_Assess_Framework".ra_userroles(id);


--
-- Name: activity_log activity_log_user_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".activity_log
    ADD CONSTRAINT activity_log_user_id_fkey FOREIGN KEY (user_id) REFERENCES "Risk_Assess_Framework".users(id) ON DELETE SET NULL;


--
-- Name: assessment_statistics assessment_statistics_department_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".assessment_statistics
    ADD CONSTRAINT assessment_statistics_department_id_fkey FOREIGN KEY (department_id) REFERENCES "Risk_Assess_Framework".departments(id) ON DELETE CASCADE;


--
-- Name: audit_archival_events audit_archival_events_archived_by_user_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_archival_events
    ADD CONSTRAINT audit_archival_events_archived_by_user_id_fkey FOREIGN KEY (archived_by_user_id) REFERENCES "Risk_Assess_Framework".users(id) ON DELETE SET NULL;


--
-- Name: audit_archival_events audit_archival_events_reference_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_archival_events
    ADD CONSTRAINT audit_archival_events_reference_id_fkey FOREIGN KEY (reference_id) REFERENCES "Risk_Assess_Framework".riskassessmentreference(reference_id) ON DELETE SET NULL;


--
-- Name: audit_archival_events audit_archival_events_retention_policy_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_archival_events
    ADD CONSTRAINT audit_archival_events_retention_policy_id_fkey FOREIGN KEY (retention_policy_id) REFERENCES "Risk_Assess_Framework".audit_retention_policies(id) ON DELETE SET NULL;


--
-- Name: audit_control_test_results audit_control_test_results_control_test_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_control_test_results
    ADD CONSTRAINT audit_control_test_results_control_test_id_fkey FOREIGN KEY (control_test_id) REFERENCES "Risk_Assess_Framework".audit_control_tests(id) ON DELETE CASCADE;


--
-- Name: audit_control_test_results audit_control_test_results_evidence_document_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_control_test_results
    ADD CONSTRAINT audit_control_test_results_evidence_document_id_fkey FOREIGN KEY (evidence_document_id) REFERENCES "Risk_Assess_Framework".audit_documents(id) ON DELETE SET NULL;


--
-- Name: audit_control_test_results audit_control_test_results_evidence_working_paper_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_control_test_results
    ADD CONSTRAINT audit_control_test_results_evidence_working_paper_id_fkey FOREIGN KEY (evidence_working_paper_id) REFERENCES "Risk_Assess_Framework".audit_working_papers(id) ON DELETE SET NULL;


--
-- Name: audit_control_test_results audit_control_test_results_tested_by_user_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_control_test_results
    ADD CONSTRAINT audit_control_test_results_tested_by_user_id_fkey FOREIGN KEY (tested_by_user_id) REFERENCES "Risk_Assess_Framework".users(id) ON DELETE SET NULL;


--
-- Name: audit_control_tests audit_control_tests_procedure_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_control_tests
    ADD CONSTRAINT audit_control_tests_procedure_id_fkey FOREIGN KEY (procedure_id) REFERENCES "Risk_Assess_Framework".audit_procedures(id) ON DELETE SET NULL;


--
-- Name: audit_control_tests audit_control_tests_reference_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_control_tests
    ADD CONSTRAINT audit_control_tests_reference_id_fkey FOREIGN KEY (reference_id) REFERENCES "Risk_Assess_Framework".riskassessmentreference(reference_id) ON DELETE CASCADE;


--
-- Name: audit_control_tests audit_control_tests_reviewer_user_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_control_tests
    ADD CONSTRAINT audit_control_tests_reviewer_user_id_fkey FOREIGN KEY (reviewer_user_id) REFERENCES "Risk_Assess_Framework".users(id) ON DELETE SET NULL;


--
-- Name: audit_control_tests audit_control_tests_risk_control_matrix_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_control_tests
    ADD CONSTRAINT audit_control_tests_risk_control_matrix_id_fkey FOREIGN KEY (risk_control_matrix_id) REFERENCES "Risk_Assess_Framework".audit_risk_control_matrix(id) ON DELETE SET NULL;


--
-- Name: audit_control_tests audit_control_tests_scope_item_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_control_tests
    ADD CONSTRAINT audit_control_tests_scope_item_id_fkey FOREIGN KEY (scope_item_id) REFERENCES "Risk_Assess_Framework".audit_scope_items(id) ON DELETE SET NULL;


--
-- Name: audit_control_tests audit_control_tests_tester_user_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_control_tests
    ADD CONSTRAINT audit_control_tests_tester_user_id_fkey FOREIGN KEY (tester_user_id) REFERENCES "Risk_Assess_Framework".users(id) ON DELETE SET NULL;


--
-- Name: audit_control_tests audit_control_tests_working_paper_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_control_tests
    ADD CONSTRAINT audit_control_tests_working_paper_id_fkey FOREIGN KEY (working_paper_id) REFERENCES "Risk_Assess_Framework".audit_working_papers(id) ON DELETE SET NULL;


--
-- Name: audit_coverage audit_coverage_audit_universe_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_coverage
    ADD CONSTRAINT audit_coverage_audit_universe_id_fkey FOREIGN KEY (audit_universe_id) REFERENCES "Risk_Assess_Framework".audit_universe(id) ON DELETE CASCADE;


--
-- Name: audit_document_access_logs audit_document_access_logs_accessed_by_user_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_document_access_logs
    ADD CONSTRAINT audit_document_access_logs_accessed_by_user_id_fkey FOREIGN KEY (accessed_by_user_id) REFERENCES "Risk_Assess_Framework".users(id) ON DELETE SET NULL;


--
-- Name: audit_document_access_logs audit_document_access_logs_document_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_document_access_logs
    ADD CONSTRAINT audit_document_access_logs_document_id_fkey FOREIGN KEY (document_id) REFERENCES "Risk_Assess_Framework".audit_documents(id) ON DELETE CASCADE;


--
-- Name: audit_document_access_logs audit_document_access_logs_reference_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_document_access_logs
    ADD CONSTRAINT audit_document_access_logs_reference_id_fkey FOREIGN KEY (reference_id) REFERENCES "Risk_Assess_Framework".riskassessmentreference(reference_id) ON DELETE SET NULL;


--
-- Name: audit_document_permission_grants audit_document_permission_grants_document_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_document_permission_grants
    ADD CONSTRAINT audit_document_permission_grants_document_id_fkey FOREIGN KEY (document_id) REFERENCES "Risk_Assess_Framework".audit_documents(id) ON DELETE CASCADE;


--
-- Name: audit_document_permission_grants audit_document_permission_grants_granted_by_user_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_document_permission_grants
    ADD CONSTRAINT audit_document_permission_grants_granted_by_user_id_fkey FOREIGN KEY (granted_by_user_id) REFERENCES "Risk_Assess_Framework".users(id) ON DELETE SET NULL;


--
-- Name: audit_document_permission_grants audit_document_permission_grants_grantee_user_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_document_permission_grants
    ADD CONSTRAINT audit_document_permission_grants_grantee_user_id_fkey FOREIGN KEY (grantee_user_id) REFERENCES "Risk_Assess_Framework".users(id) ON DELETE CASCADE;


--
-- Name: audit_documents audit_documents_audit_universe_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_documents
    ADD CONSTRAINT audit_documents_audit_universe_id_fkey FOREIGN KEY (audit_universe_id) REFERENCES "Risk_Assess_Framework".audit_universe(id) ON DELETE SET NULL;


--
-- Name: audit_documents audit_documents_category_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_documents
    ADD CONSTRAINT audit_documents_category_id_fkey FOREIGN KEY (category_id) REFERENCES "Risk_Assess_Framework".ra_document_category(id) ON DELETE SET NULL;


--
-- Name: audit_documents audit_documents_finding_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_documents
    ADD CONSTRAINT audit_documents_finding_id_fkey FOREIGN KEY (finding_id) REFERENCES "Risk_Assess_Framework".audit_findings(id) ON DELETE SET NULL;


--
-- Name: audit_documents audit_documents_procedure_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_documents
    ADD CONSTRAINT audit_documents_procedure_id_fkey FOREIGN KEY (procedure_id) REFERENCES "Risk_Assess_Framework".audit_procedures(id) ON DELETE SET NULL;


--
-- Name: audit_documents audit_documents_recommendation_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_documents
    ADD CONSTRAINT audit_documents_recommendation_id_fkey FOREIGN KEY (recommendation_id) REFERENCES "Risk_Assess_Framework".audit_recommendations(id) ON DELETE SET NULL;


--
-- Name: audit_documents audit_documents_reference_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_documents
    ADD CONSTRAINT audit_documents_reference_id_fkey FOREIGN KEY (reference_id) REFERENCES "Risk_Assess_Framework".riskassessmentreference(reference_id) ON DELETE SET NULL;


--
-- Name: audit_documents audit_documents_security_review_requested_by_user_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_documents
    ADD CONSTRAINT audit_documents_security_review_requested_by_user_id_fkey FOREIGN KEY (security_review_requested_by_user_id) REFERENCES "Risk_Assess_Framework".users(id) ON DELETE SET NULL;


--
-- Name: audit_documents audit_documents_security_reviewed_by_user_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_documents
    ADD CONSTRAINT audit_documents_security_reviewed_by_user_id_fkey FOREIGN KEY (security_reviewed_by_user_id) REFERENCES "Risk_Assess_Framework".users(id) ON DELETE SET NULL;


--
-- Name: audit_documents audit_documents_uploaded_by_user_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_documents
    ADD CONSTRAINT audit_documents_uploaded_by_user_id_fkey FOREIGN KEY (uploaded_by_user_id) REFERENCES "Risk_Assess_Framework".users(id) ON DELETE SET NULL;


--
-- Name: audit_documents audit_documents_visibility_level_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_documents
    ADD CONSTRAINT audit_documents_visibility_level_id_fkey FOREIGN KEY (visibility_level_id) REFERENCES "Risk_Assess_Framework".ra_document_visibility_level(id) ON DELETE SET NULL;


--
-- Name: audit_documents audit_documents_working_paper_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_documents
    ADD CONSTRAINT audit_documents_working_paper_id_fkey FOREIGN KEY (working_paper_id) REFERENCES "Risk_Assess_Framework".audit_working_papers(id) ON DELETE SET NULL;


--
-- Name: audit_engagement_plans audit_engagement_plans_active_materiality_calculation_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_engagement_plans
    ADD CONSTRAINT audit_engagement_plans_active_materiality_calculation_id_fkey FOREIGN KEY (active_materiality_calculation_id) REFERENCES "Risk_Assess_Framework".audit_materiality_calculations(id) ON DELETE SET NULL;


--
-- Name: audit_engagement_plans audit_engagement_plans_engagement_type_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_engagement_plans
    ADD CONSTRAINT audit_engagement_plans_engagement_type_id_fkey FOREIGN KEY (engagement_type_id) REFERENCES "Risk_Assess_Framework".ra_engagement_type(id) ON DELETE SET NULL;


--
-- Name: audit_engagement_plans audit_engagement_plans_materiality_benchmark_profile_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_engagement_plans
    ADD CONSTRAINT audit_engagement_plans_materiality_benchmark_profile_id_fkey FOREIGN KEY (materiality_benchmark_profile_id) REFERENCES "Risk_Assess_Framework".audit_materiality_benchmark_profiles(id) ON DELETE SET NULL;


--
-- Name: audit_engagement_plans audit_engagement_plans_planning_status_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_engagement_plans
    ADD CONSTRAINT audit_engagement_plans_planning_status_id_fkey FOREIGN KEY (planning_status_id) REFERENCES "Risk_Assess_Framework".ra_planning_status(id);


--
-- Name: audit_engagement_plans audit_engagement_plans_reference_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_engagement_plans
    ADD CONSTRAINT audit_engagement_plans_reference_id_fkey FOREIGN KEY (reference_id) REFERENCES "Risk_Assess_Framework".riskassessmentreference(reference_id) ON DELETE CASCADE;


--
-- Name: audit_engagement_plans audit_engagement_plans_scope_letter_document_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_engagement_plans
    ADD CONSTRAINT audit_engagement_plans_scope_letter_document_id_fkey FOREIGN KEY (scope_letter_document_id) REFERENCES "Risk_Assess_Framework".audit_documents(id) ON DELETE SET NULL;


--
-- Name: audit_engagement_plans audit_engagement_plans_signed_off_by_user_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_engagement_plans
    ADD CONSTRAINT audit_engagement_plans_signed_off_by_user_id_fkey FOREIGN KEY (signed_off_by_user_id) REFERENCES "Risk_Assess_Framework".users(id) ON DELETE SET NULL;


--
-- Name: audit_evidence_request_items audit_evidence_request_items_fulfilled_document_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_evidence_request_items
    ADD CONSTRAINT audit_evidence_request_items_fulfilled_document_id_fkey FOREIGN KEY (fulfilled_document_id) REFERENCES "Risk_Assess_Framework".audit_documents(id) ON DELETE SET NULL;


--
-- Name: audit_evidence_request_items audit_evidence_request_items_request_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_evidence_request_items
    ADD CONSTRAINT audit_evidence_request_items_request_id_fkey FOREIGN KEY (request_id) REFERENCES "Risk_Assess_Framework".audit_evidence_requests(id) ON DELETE CASCADE;


--
-- Name: audit_evidence_request_items audit_evidence_request_items_reviewed_by_user_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_evidence_request_items
    ADD CONSTRAINT audit_evidence_request_items_reviewed_by_user_id_fkey FOREIGN KEY (reviewed_by_user_id) REFERENCES "Risk_Assess_Framework".users(id) ON DELETE SET NULL;


--
-- Name: audit_evidence_requests audit_evidence_requests_audit_universe_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_evidence_requests
    ADD CONSTRAINT audit_evidence_requests_audit_universe_id_fkey FOREIGN KEY (audit_universe_id) REFERENCES "Risk_Assess_Framework".audit_universe(id) ON DELETE SET NULL;


--
-- Name: audit_evidence_requests audit_evidence_requests_reference_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_evidence_requests
    ADD CONSTRAINT audit_evidence_requests_reference_id_fkey FOREIGN KEY (reference_id) REFERENCES "Risk_Assess_Framework".riskassessmentreference(reference_id) ON DELETE SET NULL;


--
-- Name: audit_evidence_requests audit_evidence_requests_requested_by_user_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_evidence_requests
    ADD CONSTRAINT audit_evidence_requests_requested_by_user_id_fkey FOREIGN KEY (requested_by_user_id) REFERENCES "Risk_Assess_Framework".users(id) ON DELETE SET NULL;


--
-- Name: audit_evidence_requests audit_evidence_requests_status_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_evidence_requests
    ADD CONSTRAINT audit_evidence_requests_status_id_fkey FOREIGN KEY (status_id) REFERENCES "Risk_Assess_Framework".ra_evidence_request_status(id);


--
-- Name: audit_finance_finalization audit_finance_finalization_active_mapping_profile_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_finance_finalization
    ADD CONSTRAINT audit_finance_finalization_active_mapping_profile_id_fkey FOREIGN KEY (active_mapping_profile_id) REFERENCES "Risk_Assess_Framework".audit_financial_statement_mapping_profiles(id) ON DELETE SET NULL;


--
-- Name: audit_finance_finalization audit_finance_finalization_active_rule_package_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_finance_finalization
    ADD CONSTRAINT audit_finance_finalization_active_rule_package_id_fkey FOREIGN KEY (active_rule_package_id) REFERENCES "Risk_Assess_Framework".audit_domain_rule_packages(id) ON DELETE SET NULL;


--
-- Name: audit_finance_finalization audit_finance_finalization_reference_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_finance_finalization
    ADD CONSTRAINT audit_finance_finalization_reference_id_fkey FOREIGN KEY (reference_id) REFERENCES "Risk_Assess_Framework".riskassessmentreference(reference_id) ON DELETE CASCADE;


--
-- Name: audit_finance_finalization audit_finance_finalization_updated_by_user_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_finance_finalization
    ADD CONSTRAINT audit_finance_finalization_updated_by_user_id_fkey FOREIGN KEY (updated_by_user_id) REFERENCES "Risk_Assess_Framework".users(id) ON DELETE SET NULL;


--
-- Name: audit_financial_statement_mapping_profiles audit_financial_statement_mapping_profi_created_by_user_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_financial_statement_mapping_profiles
    ADD CONSTRAINT audit_financial_statement_mapping_profi_created_by_user_id_fkey FOREIGN KEY (created_by_user_id) REFERENCES "Risk_Assess_Framework".users(id) ON DELETE SET NULL;


--
-- Name: audit_financial_statement_mapping_profiles audit_financial_statement_mapping_profi_engagement_type_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_financial_statement_mapping_profiles
    ADD CONSTRAINT audit_financial_statement_mapping_profi_engagement_type_id_fkey FOREIGN KEY (engagement_type_id) REFERENCES "Risk_Assess_Framework".ra_engagement_type(id) ON DELETE SET NULL;


--
-- Name: audit_financial_statement_mapping_profiles audit_financial_statement_mapping_profiles_reference_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_financial_statement_mapping_profiles
    ADD CONSTRAINT audit_financial_statement_mapping_profiles_reference_id_fkey FOREIGN KEY (reference_id) REFERENCES "Risk_Assess_Framework".riskassessmentreference(reference_id) ON DELETE SET NULL;


--
-- Name: audit_financial_statement_mapping_profiles audit_financial_statement_mapping_profiles_rule_package_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_financial_statement_mapping_profiles
    ADD CONSTRAINT audit_financial_statement_mapping_profiles_rule_package_id_fkey FOREIGN KEY (rule_package_id) REFERENCES "Risk_Assess_Framework".audit_domain_rule_packages(id) ON DELETE SET NULL;


--
-- Name: audit_financial_statement_mappings audit_financial_statement_mappings_mapping_profile_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_financial_statement_mappings
    ADD CONSTRAINT audit_financial_statement_mappings_mapping_profile_id_fkey FOREIGN KEY (mapping_profile_id) REFERENCES "Risk_Assess_Framework".audit_financial_statement_mapping_profiles(id) ON DELETE SET NULL;


--
-- Name: audit_financial_statement_mappings audit_financial_statement_mappings_reference_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_financial_statement_mappings
    ADD CONSTRAINT audit_financial_statement_mappings_reference_id_fkey FOREIGN KEY (reference_id) REFERENCES "Risk_Assess_Framework".riskassessmentreference(reference_id) ON DELETE CASCADE;


--
-- Name: audit_financial_statement_profile_rules audit_financial_statement_profile_rules_mapping_profile_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_financial_statement_profile_rules
    ADD CONSTRAINT audit_financial_statement_profile_rules_mapping_profile_id_fkey FOREIGN KEY (mapping_profile_id) REFERENCES "Risk_Assess_Framework".audit_financial_statement_mapping_profiles(id) ON DELETE CASCADE;


--
-- Name: audit_findings audit_findings_assigned_to_user_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_findings
    ADD CONSTRAINT audit_findings_assigned_to_user_id_fkey FOREIGN KEY (assigned_to_user_id) REFERENCES "Risk_Assess_Framework".users(id) ON DELETE SET NULL;


--
-- Name: audit_findings audit_findings_audit_universe_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_findings
    ADD CONSTRAINT audit_findings_audit_universe_id_fkey FOREIGN KEY (audit_universe_id) REFERENCES "Risk_Assess_Framework".audit_universe(id) ON DELETE SET NULL;


--
-- Name: audit_findings audit_findings_created_by_user_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_findings
    ADD CONSTRAINT audit_findings_created_by_user_id_fkey FOREIGN KEY (created_by_user_id) REFERENCES "Risk_Assess_Framework".users(id) ON DELETE SET NULL;


--
-- Name: audit_findings audit_findings_reference_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_findings
    ADD CONSTRAINT audit_findings_reference_id_fkey FOREIGN KEY (reference_id) REFERENCES "Risk_Assess_Framework".riskassessmentreference(reference_id) ON DELETE SET NULL;


--
-- Name: audit_findings audit_findings_severity_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_findings
    ADD CONSTRAINT audit_findings_severity_id_fkey FOREIGN KEY (severity_id) REFERENCES "Risk_Assess_Framework".ra_finding_severity(id);


--
-- Name: audit_findings audit_findings_status_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_findings
    ADD CONSTRAINT audit_findings_status_id_fkey FOREIGN KEY (status_id) REFERENCES "Risk_Assess_Framework".ra_finding_status(id);


--
-- Name: audit_gl_journal_entries audit_gl_journal_entries_import_batch_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_gl_journal_entries
    ADD CONSTRAINT audit_gl_journal_entries_import_batch_id_fkey FOREIGN KEY (import_batch_id) REFERENCES "Risk_Assess_Framework".audit_analytics_import_batches(id) ON DELETE SET NULL;


--
-- Name: audit_industry_benchmarks audit_industry_benchmarks_import_batch_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_industry_benchmarks
    ADD CONSTRAINT audit_industry_benchmarks_import_batch_id_fkey FOREIGN KEY (import_batch_id) REFERENCES "Risk_Assess_Framework".audit_analytics_import_batches(id) ON DELETE SET NULL;


--
-- Name: audit_login_events audit_login_events_user_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_login_events
    ADD CONSTRAINT audit_login_events_user_id_fkey FOREIGN KEY (user_id) REFERENCES "Risk_Assess_Framework".users(id) ON DELETE SET NULL;


--
-- Name: audit_management_actions audit_management_actions_finding_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_management_actions
    ADD CONSTRAINT audit_management_actions_finding_id_fkey FOREIGN KEY (finding_id) REFERENCES "Risk_Assess_Framework".audit_findings(id) ON DELETE SET NULL;


--
-- Name: audit_management_actions audit_management_actions_owner_user_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_management_actions
    ADD CONSTRAINT audit_management_actions_owner_user_id_fkey FOREIGN KEY (owner_user_id) REFERENCES "Risk_Assess_Framework".users(id) ON DELETE SET NULL;


--
-- Name: audit_management_actions audit_management_actions_recommendation_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_management_actions
    ADD CONSTRAINT audit_management_actions_recommendation_id_fkey FOREIGN KEY (recommendation_id) REFERENCES "Risk_Assess_Framework".audit_recommendations(id) ON DELETE SET NULL;


--
-- Name: audit_management_actions audit_management_actions_reference_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_management_actions
    ADD CONSTRAINT audit_management_actions_reference_id_fkey FOREIGN KEY (reference_id) REFERENCES "Risk_Assess_Framework".riskassessmentreference(reference_id) ON DELETE CASCADE;


--
-- Name: audit_management_actions audit_management_actions_validated_by_user_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_management_actions
    ADD CONSTRAINT audit_management_actions_validated_by_user_id_fkey FOREIGN KEY (validated_by_user_id) REFERENCES "Risk_Assess_Framework".users(id) ON DELETE SET NULL;


--
-- Name: audit_materiality_approval_history audit_materiality_approval_history_approved_by_user_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_materiality_approval_history
    ADD CONSTRAINT audit_materiality_approval_history_approved_by_user_id_fkey FOREIGN KEY (approved_by_user_id) REFERENCES "Risk_Assess_Framework".users(id) ON DELETE SET NULL;


--
-- Name: audit_materiality_approval_history audit_materiality_approval_history_benchmark_profile_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_materiality_approval_history
    ADD CONSTRAINT audit_materiality_approval_history_benchmark_profile_id_fkey FOREIGN KEY (benchmark_profile_id) REFERENCES "Risk_Assess_Framework".audit_materiality_benchmark_profiles(id) ON DELETE SET NULL;


--
-- Name: audit_materiality_approval_history audit_materiality_approval_history_calculation_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_materiality_approval_history
    ADD CONSTRAINT audit_materiality_approval_history_calculation_id_fkey FOREIGN KEY (calculation_id) REFERENCES "Risk_Assess_Framework".audit_materiality_calculations(id) ON DELETE CASCADE;


--
-- Name: audit_materiality_approval_history audit_materiality_approval_history_previous_calculation_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_materiality_approval_history
    ADD CONSTRAINT audit_materiality_approval_history_previous_calculation_id_fkey FOREIGN KEY (previous_calculation_id) REFERENCES "Risk_Assess_Framework".audit_materiality_calculations(id) ON DELETE SET NULL;


--
-- Name: audit_materiality_approval_history audit_materiality_approval_history_reference_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_materiality_approval_history
    ADD CONSTRAINT audit_materiality_approval_history_reference_id_fkey FOREIGN KEY (reference_id) REFERENCES "Risk_Assess_Framework".riskassessmentreference(reference_id) ON DELETE CASCADE;


--
-- Name: audit_materiality_benchmark_profiles audit_materiality_benchmark_profiles_approved_by_user_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_materiality_benchmark_profiles
    ADD CONSTRAINT audit_materiality_benchmark_profiles_approved_by_user_id_fkey FOREIGN KEY (approved_by_user_id) REFERENCES "Risk_Assess_Framework".users(id) ON DELETE SET NULL;


--
-- Name: audit_materiality_benchmark_profiles audit_materiality_benchmark_profiles_engagement_type_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_materiality_benchmark_profiles
    ADD CONSTRAINT audit_materiality_benchmark_profiles_engagement_type_id_fkey FOREIGN KEY (engagement_type_id) REFERENCES "Risk_Assess_Framework".ra_engagement_type(id) ON DELETE SET NULL;


--
-- Name: audit_materiality_calculations audit_materiality_calculations_approved_by_user_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_materiality_calculations
    ADD CONSTRAINT audit_materiality_calculations_approved_by_user_id_fkey FOREIGN KEY (approved_by_user_id) REFERENCES "Risk_Assess_Framework".users(id) ON DELETE SET NULL;


--
-- Name: audit_materiality_calculations audit_materiality_calculations_benchmark_profile_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_materiality_calculations
    ADD CONSTRAINT audit_materiality_calculations_benchmark_profile_id_fkey FOREIGN KEY (benchmark_profile_id) REFERENCES "Risk_Assess_Framework".audit_materiality_benchmark_profiles(id) ON DELETE SET NULL;


--
-- Name: audit_materiality_calculations audit_materiality_calculations_created_by_user_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_materiality_calculations
    ADD CONSTRAINT audit_materiality_calculations_created_by_user_id_fkey FOREIGN KEY (created_by_user_id) REFERENCES "Risk_Assess_Framework".users(id) ON DELETE SET NULL;


--
-- Name: audit_materiality_calculations audit_materiality_calculations_reference_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_materiality_calculations
    ADD CONSTRAINT audit_materiality_calculations_reference_id_fkey FOREIGN KEY (reference_id) REFERENCES "Risk_Assess_Framework".riskassessmentreference(reference_id) ON DELETE CASCADE;


--
-- Name: audit_materiality_candidates audit_materiality_candidates_benchmark_profile_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_materiality_candidates
    ADD CONSTRAINT audit_materiality_candidates_benchmark_profile_id_fkey FOREIGN KEY (benchmark_profile_id) REFERENCES "Risk_Assess_Framework".audit_materiality_benchmark_profiles(id) ON DELETE SET NULL;


--
-- Name: audit_materiality_candidates audit_materiality_candidates_generated_by_user_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_materiality_candidates
    ADD CONSTRAINT audit_materiality_candidates_generated_by_user_id_fkey FOREIGN KEY (generated_by_user_id) REFERENCES "Risk_Assess_Framework".users(id) ON DELETE SET NULL;


--
-- Name: audit_materiality_candidates audit_materiality_candidates_reference_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_materiality_candidates
    ADD CONSTRAINT audit_materiality_candidates_reference_id_fkey FOREIGN KEY (reference_id) REFERENCES "Risk_Assess_Framework".riskassessmentreference(reference_id) ON DELETE CASCADE;


--
-- Name: audit_materiality_scope_links audit_materiality_scope_links_materiality_calculation_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_materiality_scope_links
    ADD CONSTRAINT audit_materiality_scope_links_materiality_calculation_id_fkey FOREIGN KEY (materiality_calculation_id) REFERENCES "Risk_Assess_Framework".audit_materiality_calculations(id) ON DELETE CASCADE;


--
-- Name: audit_materiality_scope_links audit_materiality_scope_links_reference_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_materiality_scope_links
    ADD CONSTRAINT audit_materiality_scope_links_reference_id_fkey FOREIGN KEY (reference_id) REFERENCES "Risk_Assess_Framework".riskassessmentreference(reference_id) ON DELETE CASCADE;


--
-- Name: audit_materiality_scope_links audit_materiality_scope_links_scope_item_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_materiality_scope_links
    ADD CONSTRAINT audit_materiality_scope_links_scope_item_id_fkey FOREIGN KEY (scope_item_id) REFERENCES "Risk_Assess_Framework".audit_scope_items(id) ON DELETE CASCADE;


--
-- Name: audit_misstatements audit_misstatements_created_by_user_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_misstatements
    ADD CONSTRAINT audit_misstatements_created_by_user_id_fkey FOREIGN KEY (created_by_user_id) REFERENCES "Risk_Assess_Framework".users(id) ON DELETE SET NULL;


--
-- Name: audit_misstatements audit_misstatements_finding_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_misstatements
    ADD CONSTRAINT audit_misstatements_finding_id_fkey FOREIGN KEY (finding_id) REFERENCES "Risk_Assess_Framework".audit_findings(id) ON DELETE SET NULL;


--
-- Name: audit_misstatements audit_misstatements_materiality_calculation_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_misstatements
    ADD CONSTRAINT audit_misstatements_materiality_calculation_id_fkey FOREIGN KEY (materiality_calculation_id) REFERENCES "Risk_Assess_Framework".audit_materiality_calculations(id) ON DELETE SET NULL;


--
-- Name: audit_misstatements audit_misstatements_reference_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_misstatements
    ADD CONSTRAINT audit_misstatements_reference_id_fkey FOREIGN KEY (reference_id) REFERENCES "Risk_Assess_Framework".riskassessmentreference(reference_id) ON DELETE CASCADE;


--
-- Name: audit_notifications audit_notifications_reference_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_notifications
    ADD CONSTRAINT audit_notifications_reference_id_fkey FOREIGN KEY (reference_id) REFERENCES "Risk_Assess_Framework".riskassessmentreference(reference_id) ON DELETE CASCADE;


--
-- Name: audit_notifications audit_notifications_workflow_instance_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_notifications
    ADD CONSTRAINT audit_notifications_workflow_instance_id_fkey FOREIGN KEY (workflow_instance_id) REFERENCES "Risk_Assess_Framework".audit_workflow_instances(workflow_instance_id) ON DELETE SET NULL;


--
-- Name: audit_procedure_assignments audit_procedure_assignments_assigned_by_user_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_procedure_assignments
    ADD CONSTRAINT audit_procedure_assignments_assigned_by_user_id_fkey FOREIGN KEY (assigned_by_user_id) REFERENCES "Risk_Assess_Framework".users(id) ON DELETE SET NULL;


--
-- Name: audit_procedure_assignments audit_procedure_assignments_assigned_to_user_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_procedure_assignments
    ADD CONSTRAINT audit_procedure_assignments_assigned_to_user_id_fkey FOREIGN KEY (assigned_to_user_id) REFERENCES "Risk_Assess_Framework".users(id) ON DELETE SET NULL;


--
-- Name: audit_procedure_assignments audit_procedure_assignments_procedure_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_procedure_assignments
    ADD CONSTRAINT audit_procedure_assignments_procedure_id_fkey FOREIGN KEY (procedure_id) REFERENCES "Risk_Assess_Framework".audit_procedures(id) ON DELETE CASCADE;


--
-- Name: audit_procedure_assignments audit_procedure_assignments_procedure_step_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_procedure_assignments
    ADD CONSTRAINT audit_procedure_assignments_procedure_step_id_fkey FOREIGN KEY (procedure_step_id) REFERENCES "Risk_Assess_Framework".audit_procedure_steps(id) ON DELETE SET NULL;


--
-- Name: audit_procedure_assignments audit_procedure_assignments_reference_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_procedure_assignments
    ADD CONSTRAINT audit_procedure_assignments_reference_id_fkey FOREIGN KEY (reference_id) REFERENCES "Risk_Assess_Framework".riskassessmentreference(reference_id) ON DELETE CASCADE;


--
-- Name: audit_procedure_assignments audit_procedure_assignments_risk_control_matrix_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_procedure_assignments
    ADD CONSTRAINT audit_procedure_assignments_risk_control_matrix_id_fkey FOREIGN KEY (risk_control_matrix_id) REFERENCES "Risk_Assess_Framework".audit_risk_control_matrix(id) ON DELETE SET NULL;


--
-- Name: audit_procedure_assignments audit_procedure_assignments_scope_item_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_procedure_assignments
    ADD CONSTRAINT audit_procedure_assignments_scope_item_id_fkey FOREIGN KEY (scope_item_id) REFERENCES "Risk_Assess_Framework".audit_scope_items(id) ON DELETE SET NULL;


--
-- Name: audit_procedure_assignments audit_procedure_assignments_walkthrough_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_procedure_assignments
    ADD CONSTRAINT audit_procedure_assignments_walkthrough_id_fkey FOREIGN KEY (walkthrough_id) REFERENCES "Risk_Assess_Framework".audit_walkthroughs(id) ON DELETE SET NULL;


--
-- Name: audit_procedure_assignments audit_procedure_assignments_working_paper_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_procedure_assignments
    ADD CONSTRAINT audit_procedure_assignments_working_paper_id_fkey FOREIGN KEY (working_paper_id) REFERENCES "Risk_Assess_Framework".audit_working_papers(id) ON DELETE SET NULL;


--
-- Name: audit_procedure_steps audit_procedure_steps_procedure_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_procedure_steps
    ADD CONSTRAINT audit_procedure_steps_procedure_id_fkey FOREIGN KEY (procedure_id) REFERENCES "Risk_Assess_Framework".audit_procedures(id) ON DELETE CASCADE;


--
-- Name: audit_procedures audit_procedures_applicable_engagement_type_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_procedures
    ADD CONSTRAINT audit_procedures_applicable_engagement_type_id_fkey FOREIGN KEY (applicable_engagement_type_id) REFERENCES "Risk_Assess_Framework".ra_engagement_type(id) ON DELETE SET NULL;


--
-- Name: audit_procedures audit_procedures_audit_universe_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_procedures
    ADD CONSTRAINT audit_procedures_audit_universe_id_fkey FOREIGN KEY (audit_universe_id) REFERENCES "Risk_Assess_Framework".audit_universe(id) ON DELETE SET NULL;


--
-- Name: audit_procedures audit_procedures_created_by_user_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_procedures
    ADD CONSTRAINT audit_procedures_created_by_user_id_fkey FOREIGN KEY (created_by_user_id) REFERENCES "Risk_Assess_Framework".users(id) ON DELETE SET NULL;


--
-- Name: audit_procedures audit_procedures_performer_user_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_procedures
    ADD CONSTRAINT audit_procedures_performer_user_id_fkey FOREIGN KEY (performer_user_id) REFERENCES "Risk_Assess_Framework".users(id) ON DELETE SET NULL;


--
-- Name: audit_procedures audit_procedures_procedure_type_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_procedures
    ADD CONSTRAINT audit_procedures_procedure_type_id_fkey FOREIGN KEY (procedure_type_id) REFERENCES "Risk_Assess_Framework".ra_procedure_type(id);


--
-- Name: audit_procedures audit_procedures_reference_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_procedures
    ADD CONSTRAINT audit_procedures_reference_id_fkey FOREIGN KEY (reference_id) REFERENCES "Risk_Assess_Framework".riskassessmentreference(reference_id) ON DELETE SET NULL;


--
-- Name: audit_procedures audit_procedures_reviewer_user_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_procedures
    ADD CONSTRAINT audit_procedures_reviewer_user_id_fkey FOREIGN KEY (reviewer_user_id) REFERENCES "Risk_Assess_Framework".users(id) ON DELETE SET NULL;


--
-- Name: audit_procedures audit_procedures_source_template_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_procedures
    ADD CONSTRAINT audit_procedures_source_template_id_fkey FOREIGN KEY (source_template_id) REFERENCES "Risk_Assess_Framework".audit_procedures(id) ON DELETE SET NULL;


--
-- Name: audit_procedures audit_procedures_status_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_procedures
    ADD CONSTRAINT audit_procedures_status_id_fkey FOREIGN KEY (status_id) REFERENCES "Risk_Assess_Framework".ra_procedure_status(id);


--
-- Name: audit_project_collaborators audit_project_collaborators_assigned_by_user_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_project_collaborators
    ADD CONSTRAINT audit_project_collaborators_assigned_by_user_id_fkey FOREIGN KEY (assigned_by_user_id) REFERENCES "Risk_Assess_Framework".users(id) ON DELETE SET NULL;


--
-- Name: audit_project_collaborators audit_project_collaborators_collaborator_role_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_project_collaborators
    ADD CONSTRAINT audit_project_collaborators_collaborator_role_id_fkey FOREIGN KEY (collaborator_role_id) REFERENCES "Risk_Assess_Framework".ra_audit_collaborator_role(id) ON DELETE SET NULL;


--
-- Name: audit_project_collaborators audit_project_collaborators_project_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_project_collaborators
    ADD CONSTRAINT audit_project_collaborators_project_id_fkey FOREIGN KEY (project_id) REFERENCES "Risk_Assess_Framework".projects(id) ON DELETE CASCADE;


--
-- Name: audit_project_collaborators audit_project_collaborators_user_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_project_collaborators
    ADD CONSTRAINT audit_project_collaborators_user_id_fkey FOREIGN KEY (user_id) REFERENCES "Risk_Assess_Framework".users(id) ON DELETE CASCADE;


--
-- Name: audit_reasonability_forecasts audit_reasonability_forecasts_import_batch_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_reasonability_forecasts
    ADD CONSTRAINT audit_reasonability_forecasts_import_batch_id_fkey FOREIGN KEY (import_batch_id) REFERENCES "Risk_Assess_Framework".audit_analytics_import_batches(id) ON DELETE SET NULL;


--
-- Name: audit_recommendations audit_recommendations_finding_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_recommendations
    ADD CONSTRAINT audit_recommendations_finding_id_fkey FOREIGN KEY (finding_id) REFERENCES "Risk_Assess_Framework".audit_findings(id) ON DELETE CASCADE;


--
-- Name: audit_recommendations audit_recommendations_responsible_user_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_recommendations
    ADD CONSTRAINT audit_recommendations_responsible_user_id_fkey FOREIGN KEY (responsible_user_id) REFERENCES "Risk_Assess_Framework".users(id) ON DELETE SET NULL;


--
-- Name: audit_recommendations audit_recommendations_status_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_recommendations
    ADD CONSTRAINT audit_recommendations_status_id_fkey FOREIGN KEY (status_id) REFERENCES "Risk_Assess_Framework".ra_recommendation_status(id);


--
-- Name: audit_recommendations audit_recommendations_verified_by_user_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_recommendations
    ADD CONSTRAINT audit_recommendations_verified_by_user_id_fkey FOREIGN KEY (verified_by_user_id) REFERENCES "Risk_Assess_Framework".users(id) ON DELETE SET NULL;


--
-- Name: audit_reference_collaborators audit_reference_collaborators_assigned_by_user_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_reference_collaborators
    ADD CONSTRAINT audit_reference_collaborators_assigned_by_user_id_fkey FOREIGN KEY (assigned_by_user_id) REFERENCES "Risk_Assess_Framework".users(id) ON DELETE SET NULL;


--
-- Name: audit_reference_collaborators audit_reference_collaborators_collaborator_role_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_reference_collaborators
    ADD CONSTRAINT audit_reference_collaborators_collaborator_role_id_fkey FOREIGN KEY (collaborator_role_id) REFERENCES "Risk_Assess_Framework".ra_audit_collaborator_role(id) ON DELETE SET NULL;


--
-- Name: audit_reference_collaborators audit_reference_collaborators_reference_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_reference_collaborators
    ADD CONSTRAINT audit_reference_collaborators_reference_id_fkey FOREIGN KEY (reference_id) REFERENCES "Risk_Assess_Framework".riskassessmentreference(reference_id) ON DELETE CASCADE;


--
-- Name: audit_reference_collaborators audit_reference_collaborators_user_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_reference_collaborators
    ADD CONSTRAINT audit_reference_collaborators_user_id_fkey FOREIGN KEY (user_id) REFERENCES "Risk_Assess_Framework".users(id) ON DELETE CASCADE;


--
-- Name: audit_review_notes audit_review_notes_cleared_by_user_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_review_notes
    ADD CONSTRAINT audit_review_notes_cleared_by_user_id_fkey FOREIGN KEY (cleared_by_user_id) REFERENCES "Risk_Assess_Framework".users(id) ON DELETE SET NULL;


--
-- Name: audit_review_notes audit_review_notes_raised_by_user_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_review_notes
    ADD CONSTRAINT audit_review_notes_raised_by_user_id_fkey FOREIGN KEY (raised_by_user_id) REFERENCES "Risk_Assess_Framework".users(id) ON DELETE SET NULL;


--
-- Name: audit_review_notes audit_review_notes_review_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_review_notes
    ADD CONSTRAINT audit_review_notes_review_id_fkey FOREIGN KEY (review_id) REFERENCES "Risk_Assess_Framework".audit_reviews(id) ON DELETE CASCADE;


--
-- Name: audit_review_notes audit_review_notes_working_paper_section_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_review_notes
    ADD CONSTRAINT audit_review_notes_working_paper_section_id_fkey FOREIGN KEY (working_paper_section_id) REFERENCES "Risk_Assess_Framework".audit_working_paper_sections(id) ON DELETE SET NULL;


--
-- Name: audit_reviews audit_reviews_assigned_reviewer_user_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_reviews
    ADD CONSTRAINT audit_reviews_assigned_reviewer_user_id_fkey FOREIGN KEY (assigned_reviewer_user_id) REFERENCES "Risk_Assess_Framework".users(id) ON DELETE SET NULL;


--
-- Name: audit_reviews audit_reviews_completed_by_user_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_reviews
    ADD CONSTRAINT audit_reviews_completed_by_user_id_fkey FOREIGN KEY (completed_by_user_id) REFERENCES "Risk_Assess_Framework".users(id) ON DELETE SET NULL;


--
-- Name: audit_reviews audit_reviews_reference_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_reviews
    ADD CONSTRAINT audit_reviews_reference_id_fkey FOREIGN KEY (reference_id) REFERENCES "Risk_Assess_Framework".riskassessmentreference(reference_id) ON DELETE CASCADE;


--
-- Name: audit_reviews audit_reviews_requested_by_user_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_reviews
    ADD CONSTRAINT audit_reviews_requested_by_user_id_fkey FOREIGN KEY (requested_by_user_id) REFERENCES "Risk_Assess_Framework".users(id) ON DELETE SET NULL;


--
-- Name: audit_reviews audit_reviews_task_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_reviews
    ADD CONSTRAINT audit_reviews_task_id_fkey FOREIGN KEY (task_id) REFERENCES "Risk_Assess_Framework".audit_tasks(id) ON DELETE SET NULL;


--
-- Name: audit_reviews audit_reviews_workflow_instance_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_reviews
    ADD CONSTRAINT audit_reviews_workflow_instance_id_fkey FOREIGN KEY (workflow_instance_id) REFERENCES "Risk_Assess_Framework".audit_workflow_instances(workflow_instance_id) ON DELETE SET NULL;


--
-- Name: audit_risk_control_matrix audit_risk_control_matrix_control_classification_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_risk_control_matrix
    ADD CONSTRAINT audit_risk_control_matrix_control_classification_id_fkey FOREIGN KEY (control_classification_id) REFERENCES "Risk_Assess_Framework".ra_control_classification(id) ON DELETE SET NULL;


--
-- Name: audit_risk_control_matrix audit_risk_control_matrix_control_frequency_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_risk_control_matrix
    ADD CONSTRAINT audit_risk_control_matrix_control_frequency_id_fkey FOREIGN KEY (control_frequency_id) REFERENCES "Risk_Assess_Framework".ra_control_frequency(id) ON DELETE SET NULL;


--
-- Name: audit_risk_control_matrix audit_risk_control_matrix_control_type_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_risk_control_matrix
    ADD CONSTRAINT audit_risk_control_matrix_control_type_id_fkey FOREIGN KEY (control_type_id) REFERENCES "Risk_Assess_Framework".ra_control_type(id) ON DELETE SET NULL;


--
-- Name: audit_risk_control_matrix audit_risk_control_matrix_procedure_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_risk_control_matrix
    ADD CONSTRAINT audit_risk_control_matrix_procedure_id_fkey FOREIGN KEY (procedure_id) REFERENCES "Risk_Assess_Framework".audit_procedures(id) ON DELETE SET NULL;


--
-- Name: audit_risk_control_matrix audit_risk_control_matrix_reference_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_risk_control_matrix
    ADD CONSTRAINT audit_risk_control_matrix_reference_id_fkey FOREIGN KEY (reference_id) REFERENCES "Risk_Assess_Framework".riskassessmentreference(reference_id) ON DELETE CASCADE;


--
-- Name: audit_risk_control_matrix audit_risk_control_matrix_scope_item_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_risk_control_matrix
    ADD CONSTRAINT audit_risk_control_matrix_scope_item_id_fkey FOREIGN KEY (scope_item_id) REFERENCES "Risk_Assess_Framework".audit_scope_items(id) ON DELETE SET NULL;


--
-- Name: audit_scope_items audit_scope_items_plan_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_scope_items
    ADD CONSTRAINT audit_scope_items_plan_id_fkey FOREIGN KEY (plan_id) REFERENCES "Risk_Assess_Framework".audit_engagement_plans(id) ON DELETE CASCADE;


--
-- Name: audit_scope_items audit_scope_items_procedure_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_scope_items
    ADD CONSTRAINT audit_scope_items_procedure_id_fkey FOREIGN KEY (procedure_id) REFERENCES "Risk_Assess_Framework".audit_procedures(id) ON DELETE SET NULL;


--
-- Name: audit_scope_items audit_scope_items_reference_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_scope_items
    ADD CONSTRAINT audit_scope_items_reference_id_fkey FOREIGN KEY (reference_id) REFERENCES "Risk_Assess_Framework".riskassessmentreference(reference_id) ON DELETE CASCADE;


--
-- Name: audit_signoffs audit_signoffs_reference_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_signoffs
    ADD CONSTRAINT audit_signoffs_reference_id_fkey FOREIGN KEY (reference_id) REFERENCES "Risk_Assess_Framework".riskassessmentreference(reference_id) ON DELETE CASCADE;


--
-- Name: audit_signoffs audit_signoffs_review_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_signoffs
    ADD CONSTRAINT audit_signoffs_review_id_fkey FOREIGN KEY (review_id) REFERENCES "Risk_Assess_Framework".audit_reviews(id) ON DELETE SET NULL;


--
-- Name: audit_signoffs audit_signoffs_signed_by_user_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_signoffs
    ADD CONSTRAINT audit_signoffs_signed_by_user_id_fkey FOREIGN KEY (signed_by_user_id) REFERENCES "Risk_Assess_Framework".users(id) ON DELETE SET NULL;


--
-- Name: audit_signoffs audit_signoffs_workflow_instance_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_signoffs
    ADD CONSTRAINT audit_signoffs_workflow_instance_id_fkey FOREIGN KEY (workflow_instance_id) REFERENCES "Risk_Assess_Framework".audit_workflow_instances(workflow_instance_id) ON DELETE SET NULL;


--
-- Name: audit_substantive_support_requests audit_substantive_support_requests_linked_control_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_substantive_support_requests
    ADD CONSTRAINT audit_substantive_support_requests_linked_control_id_fkey FOREIGN KEY (linked_control_id) REFERENCES "Risk_Assess_Framework".audit_risk_control_matrix(id) ON DELETE SET NULL;


--
-- Name: audit_substantive_support_requests audit_substantive_support_requests_linked_finding_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_substantive_support_requests
    ADD CONSTRAINT audit_substantive_support_requests_linked_finding_id_fkey FOREIGN KEY (linked_finding_id) REFERENCES "Risk_Assess_Framework".audit_findings(id) ON DELETE SET NULL;


--
-- Name: audit_substantive_support_requests audit_substantive_support_requests_linked_procedure_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_substantive_support_requests
    ADD CONSTRAINT audit_substantive_support_requests_linked_procedure_id_fkey FOREIGN KEY (linked_procedure_id) REFERENCES "Risk_Assess_Framework".audit_procedures(id) ON DELETE SET NULL;


--
-- Name: audit_substantive_support_requests audit_substantive_support_requests_linked_walkthrough_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_substantive_support_requests
    ADD CONSTRAINT audit_substantive_support_requests_linked_walkthrough_id_fkey FOREIGN KEY (linked_walkthrough_id) REFERENCES "Risk_Assess_Framework".audit_walkthroughs(id) ON DELETE SET NULL;


--
-- Name: audit_substantive_support_requests audit_substantive_support_requests_reference_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_substantive_support_requests
    ADD CONSTRAINT audit_substantive_support_requests_reference_id_fkey FOREIGN KEY (reference_id) REFERENCES "Risk_Assess_Framework".riskassessmentreference(reference_id) ON DELETE CASCADE;


--
-- Name: audit_tasks audit_tasks_assigned_by_user_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_tasks
    ADD CONSTRAINT audit_tasks_assigned_by_user_id_fkey FOREIGN KEY (assigned_by_user_id) REFERENCES "Risk_Assess_Framework".users(id) ON DELETE SET NULL;


--
-- Name: audit_tasks audit_tasks_assigned_to_user_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_tasks
    ADD CONSTRAINT audit_tasks_assigned_to_user_id_fkey FOREIGN KEY (assigned_to_user_id) REFERENCES "Risk_Assess_Framework".users(id) ON DELETE SET NULL;


--
-- Name: audit_tasks audit_tasks_completed_by_user_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_tasks
    ADD CONSTRAINT audit_tasks_completed_by_user_id_fkey FOREIGN KEY (completed_by_user_id) REFERENCES "Risk_Assess_Framework".users(id) ON DELETE SET NULL;


--
-- Name: audit_tasks audit_tasks_reference_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_tasks
    ADD CONSTRAINT audit_tasks_reference_id_fkey FOREIGN KEY (reference_id) REFERENCES "Risk_Assess_Framework".riskassessmentreference(reference_id) ON DELETE CASCADE;


--
-- Name: audit_tasks audit_tasks_workflow_instance_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_tasks
    ADD CONSTRAINT audit_tasks_workflow_instance_id_fkey FOREIGN KEY (workflow_instance_id) REFERENCES "Risk_Assess_Framework".audit_workflow_instances(workflow_instance_id) ON DELETE SET NULL;


--
-- Name: audit_trail_entity_changes audit_trail_entity_changes_audit_trail_event_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_trail_entity_changes
    ADD CONSTRAINT audit_trail_entity_changes_audit_trail_event_id_fkey FOREIGN KEY (audit_trail_event_id) REFERENCES "Risk_Assess_Framework".audit_trail_events(id) ON DELETE CASCADE;


--
-- Name: audit_trial_balance_snapshots audit_trial_balance_snapshots_import_batch_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_trial_balance_snapshots
    ADD CONSTRAINT audit_trial_balance_snapshots_import_batch_id_fkey FOREIGN KEY (import_batch_id) REFERENCES "Risk_Assess_Framework".audit_analytics_import_batches(id) ON DELETE SET NULL;


--
-- Name: audit_universe_department_link audit_universe_department_link_audit_universe_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_universe_department_link
    ADD CONSTRAINT audit_universe_department_link_audit_universe_id_fkey FOREIGN KEY (audit_universe_id) REFERENCES "Risk_Assess_Framework".audit_universe(id) ON DELETE CASCADE;


--
-- Name: audit_universe_department_link audit_universe_department_link_department_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_universe_department_link
    ADD CONSTRAINT audit_universe_department_link_department_id_fkey FOREIGN KEY (department_id) REFERENCES "Risk_Assess_Framework".departments(id) ON DELETE CASCADE;


--
-- Name: audit_universe audit_universe_parent_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_universe
    ADD CONSTRAINT audit_universe_parent_id_fkey FOREIGN KEY (parent_id) REFERENCES "Risk_Assess_Framework".audit_universe(id) ON DELETE SET NULL;


--
-- Name: audit_usage_events audit_usage_events_performed_by_user_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_usage_events
    ADD CONSTRAINT audit_usage_events_performed_by_user_id_fkey FOREIGN KEY (performed_by_user_id) REFERENCES "Risk_Assess_Framework".users(id) ON DELETE SET NULL;


--
-- Name: audit_usage_events audit_usage_events_reference_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_usage_events
    ADD CONSTRAINT audit_usage_events_reference_id_fkey FOREIGN KEY (reference_id) REFERENCES "Risk_Assess_Framework".riskassessmentreference(reference_id) ON DELETE SET NULL;


--
-- Name: audit_walkthrough_exceptions audit_walkthrough_exceptions_linked_finding_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_walkthrough_exceptions
    ADD CONSTRAINT audit_walkthrough_exceptions_linked_finding_id_fkey FOREIGN KEY (linked_finding_id) REFERENCES "Risk_Assess_Framework".audit_findings(id) ON DELETE SET NULL;


--
-- Name: audit_walkthrough_exceptions audit_walkthrough_exceptions_walkthrough_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_walkthrough_exceptions
    ADD CONSTRAINT audit_walkthrough_exceptions_walkthrough_id_fkey FOREIGN KEY (walkthrough_id) REFERENCES "Risk_Assess_Framework".audit_walkthroughs(id) ON DELETE CASCADE;


--
-- Name: audit_walkthroughs audit_walkthroughs_procedure_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_walkthroughs
    ADD CONSTRAINT audit_walkthroughs_procedure_id_fkey FOREIGN KEY (procedure_id) REFERENCES "Risk_Assess_Framework".audit_procedures(id) ON DELETE SET NULL;


--
-- Name: audit_walkthroughs audit_walkthroughs_reference_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_walkthroughs
    ADD CONSTRAINT audit_walkthroughs_reference_id_fkey FOREIGN KEY (reference_id) REFERENCES "Risk_Assess_Framework".riskassessmentreference(reference_id) ON DELETE CASCADE;


--
-- Name: audit_walkthroughs audit_walkthroughs_risk_control_matrix_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_walkthroughs
    ADD CONSTRAINT audit_walkthroughs_risk_control_matrix_id_fkey FOREIGN KEY (risk_control_matrix_id) REFERENCES "Risk_Assess_Framework".audit_risk_control_matrix(id) ON DELETE SET NULL;


--
-- Name: audit_walkthroughs audit_walkthroughs_scope_item_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_walkthroughs
    ADD CONSTRAINT audit_walkthroughs_scope_item_id_fkey FOREIGN KEY (scope_item_id) REFERENCES "Risk_Assess_Framework".audit_scope_items(id) ON DELETE SET NULL;


--
-- Name: audit_workflow_events audit_workflow_events_reference_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_workflow_events
    ADD CONSTRAINT audit_workflow_events_reference_id_fkey FOREIGN KEY (reference_id) REFERENCES "Risk_Assess_Framework".riskassessmentreference(reference_id) ON DELETE CASCADE;


--
-- Name: audit_workflow_events audit_workflow_events_workflow_instance_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_workflow_events
    ADD CONSTRAINT audit_workflow_events_workflow_instance_id_fkey FOREIGN KEY (workflow_instance_id) REFERENCES "Risk_Assess_Framework".audit_workflow_instances(workflow_instance_id) ON DELETE CASCADE;


--
-- Name: audit_workflow_instances audit_workflow_instances_reference_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_workflow_instances
    ADD CONSTRAINT audit_workflow_instances_reference_id_fkey FOREIGN KEY (reference_id) REFERENCES "Risk_Assess_Framework".riskassessmentreference(reference_id) ON DELETE CASCADE;


--
-- Name: audit_workflow_tasks audit_workflow_tasks_reference_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_workflow_tasks
    ADD CONSTRAINT audit_workflow_tasks_reference_id_fkey FOREIGN KEY (reference_id) REFERENCES "Risk_Assess_Framework".riskassessmentreference(reference_id) ON DELETE CASCADE;


--
-- Name: audit_workflow_tasks audit_workflow_tasks_workflow_instance_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_workflow_tasks
    ADD CONSTRAINT audit_workflow_tasks_workflow_instance_id_fkey FOREIGN KEY (workflow_instance_id) REFERENCES "Risk_Assess_Framework".audit_workflow_instances(workflow_instance_id) ON DELETE CASCADE;


--
-- Name: audit_working_paper_references audit_working_paper_references_from_working_paper_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_working_paper_references
    ADD CONSTRAINT audit_working_paper_references_from_working_paper_id_fkey FOREIGN KEY (from_working_paper_id) REFERENCES "Risk_Assess_Framework".audit_working_papers(id) ON DELETE CASCADE;


--
-- Name: audit_working_paper_references audit_working_paper_references_to_working_paper_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_working_paper_references
    ADD CONSTRAINT audit_working_paper_references_to_working_paper_id_fkey FOREIGN KEY (to_working_paper_id) REFERENCES "Risk_Assess_Framework".audit_working_papers(id) ON DELETE CASCADE;


--
-- Name: audit_working_paper_sections audit_working_paper_sections_prepared_by_user_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_working_paper_sections
    ADD CONSTRAINT audit_working_paper_sections_prepared_by_user_id_fkey FOREIGN KEY (prepared_by_user_id) REFERENCES "Risk_Assess_Framework".users(id) ON DELETE SET NULL;


--
-- Name: audit_working_paper_sections audit_working_paper_sections_working_paper_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_working_paper_sections
    ADD CONSTRAINT audit_working_paper_sections_working_paper_id_fkey FOREIGN KEY (working_paper_id) REFERENCES "Risk_Assess_Framework".audit_working_papers(id) ON DELETE CASCADE;


--
-- Name: audit_working_paper_signoffs audit_working_paper_signoffs_signed_by_user_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_working_paper_signoffs
    ADD CONSTRAINT audit_working_paper_signoffs_signed_by_user_id_fkey FOREIGN KEY (signed_by_user_id) REFERENCES "Risk_Assess_Framework".users(id) ON DELETE SET NULL;


--
-- Name: audit_working_paper_signoffs audit_working_paper_signoffs_working_paper_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_working_paper_signoffs
    ADD CONSTRAINT audit_working_paper_signoffs_working_paper_id_fkey FOREIGN KEY (working_paper_id) REFERENCES "Risk_Assess_Framework".audit_working_papers(id) ON DELETE CASCADE;


--
-- Name: audit_working_papers audit_working_papers_applicable_engagement_type_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_working_papers
    ADD CONSTRAINT audit_working_papers_applicable_engagement_type_id_fkey FOREIGN KEY (applicable_engagement_type_id) REFERENCES "Risk_Assess_Framework".ra_engagement_type(id) ON DELETE SET NULL;


--
-- Name: audit_working_papers audit_working_papers_audit_universe_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_working_papers
    ADD CONSTRAINT audit_working_papers_audit_universe_id_fkey FOREIGN KEY (audit_universe_id) REFERENCES "Risk_Assess_Framework".audit_universe(id) ON DELETE SET NULL;


--
-- Name: audit_working_papers audit_working_papers_prepared_by_user_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_working_papers
    ADD CONSTRAINT audit_working_papers_prepared_by_user_id_fkey FOREIGN KEY (prepared_by_user_id) REFERENCES "Risk_Assess_Framework".users(id) ON DELETE SET NULL;


--
-- Name: audit_working_papers audit_working_papers_procedure_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_working_papers
    ADD CONSTRAINT audit_working_papers_procedure_id_fkey FOREIGN KEY (procedure_id) REFERENCES "Risk_Assess_Framework".audit_procedures(id) ON DELETE SET NULL;


--
-- Name: audit_working_papers audit_working_papers_reference_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_working_papers
    ADD CONSTRAINT audit_working_papers_reference_id_fkey FOREIGN KEY (reference_id) REFERENCES "Risk_Assess_Framework".riskassessmentreference(reference_id) ON DELETE SET NULL;


--
-- Name: audit_working_papers audit_working_papers_reviewer_user_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_working_papers
    ADD CONSTRAINT audit_working_papers_reviewer_user_id_fkey FOREIGN KEY (reviewer_user_id) REFERENCES "Risk_Assess_Framework".users(id) ON DELETE SET NULL;


--
-- Name: audit_working_papers audit_working_papers_source_template_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_working_papers
    ADD CONSTRAINT audit_working_papers_source_template_id_fkey FOREIGN KEY (source_template_id) REFERENCES "Risk_Assess_Framework".audit_working_papers(id) ON DELETE SET NULL;


--
-- Name: audit_working_papers audit_working_papers_status_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".audit_working_papers
    ADD CONSTRAINT audit_working_papers_status_id_fkey FOREIGN KEY (status_id) REFERENCES "Risk_Assess_Framework".ra_working_paper_status(id);


--
-- Name: departments departments_risk_level_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".departments
    ADD CONSTRAINT departments_risk_level_id_fkey FOREIGN KEY (risk_level_id) REFERENCES "Risk_Assess_Framework".ra_risklevels(id);


--
-- Name: riskassessment fk_riskassessment_reference; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".riskassessment
    ADD CONSTRAINT fk_riskassessment_reference FOREIGN KEY (reference_id) REFERENCES "Risk_Assess_Framework".riskassessmentreference(reference_id);


--
-- Name: projects projects_department_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".projects
    ADD CONSTRAINT projects_department_id_fkey FOREIGN KEY (department_id) REFERENCES "Risk_Assess_Framework".departments(id) ON DELETE SET NULL;


--
-- Name: projects projects_risk_level_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".projects
    ADD CONSTRAINT projects_risk_level_id_fkey FOREIGN KEY (risk_level_id) REFERENCES "Risk_Assess_Framework".ra_risklevels(id);


--
-- Name: projects projects_status_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".projects
    ADD CONSTRAINT projects_status_id_fkey FOREIGN KEY (status_id) REFERENCES "Risk_Assess_Framework".ra_projectstatus(id);


--
-- Name: ra_document_category ra_document_category_default_visibility_level_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".ra_document_category
    ADD CONSTRAINT ra_document_category_default_visibility_level_id_fkey FOREIGN KEY (default_visibility_level_id) REFERENCES "Risk_Assess_Framework".ra_document_visibility_level(id) ON DELETE SET NULL;


--
-- Name: ra_keyriskfactors ra_keyriskfactors_objectiveprocessesid_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".ra_keyriskfactors
    ADD CONSTRAINT ra_keyriskfactors_objectiveprocessesid_fkey FOREIGN KEY (objectiveprocessesid) REFERENCES "Risk_Assess_Framework".ra_objectiveprocesses(id);


--
-- Name: ra_keyriskfactors ra_keyriskfactors_riskassessmentid_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".ra_keyriskfactors
    ADD CONSTRAINT ra_keyriskfactors_riskassessmentid_fkey FOREIGN KEY (riskassessmentid) REFERENCES "Risk_Assess_Framework".riskassessment(riskassessment_refid);


--
-- Name: ra_objectiveprocesses ra_objectiveprocesses_riskassessmentid_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".ra_objectiveprocesses
    ADD CONSTRAINT ra_objectiveprocesses_riskassessmentid_fkey FOREIGN KEY (riskassessmentid) REFERENCES "Risk_Assess_Framework".riskassessment(riskassessment_refid);


--
-- Name: risk_trend_history risk_trend_history_audit_universe_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".risk_trend_history
    ADD CONSTRAINT risk_trend_history_audit_universe_id_fkey FOREIGN KEY (audit_universe_id) REFERENCES "Risk_Assess_Framework".audit_universe(id) ON DELETE SET NULL;


--
-- Name: risk_trend_history risk_trend_history_reference_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".risk_trend_history
    ADD CONSTRAINT risk_trend_history_reference_id_fkey FOREIGN KEY (reference_id) REFERENCES "Risk_Assess_Framework".riskassessmentreference(reference_id) ON DELETE CASCADE;


--
-- Name: riskassessment riskassessment_auditor_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".riskassessment
    ADD CONSTRAINT riskassessment_auditor_id_fkey FOREIGN KEY (auditor_id) REFERENCES "Risk_Assess_Framework".users(id) ON DELETE SET NULL;


--
-- Name: riskassessment riskassessment_department_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".riskassessment
    ADD CONSTRAINT riskassessment_department_id_fkey FOREIGN KEY (department_id) REFERENCES "Risk_Assess_Framework".departments(id) ON DELETE SET NULL;


--
-- Name: riskassessment riskassessment_project_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".riskassessment
    ADD CONSTRAINT riskassessment_project_id_fkey FOREIGN KEY (project_id) REFERENCES "Risk_Assess_Framework".projects(id) ON DELETE SET NULL;


--
-- Name: riskassessment riskassessment_status_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".riskassessment
    ADD CONSTRAINT riskassessment_status_id_fkey FOREIGN KEY (status_id) REFERENCES "Risk_Assess_Framework".ra_assessmentstatus(id);


--
-- Name: riskassessmentreference riskassessmentreference_archived_by_user_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".riskassessmentreference
    ADD CONSTRAINT riskassessmentreference_archived_by_user_id_fkey FOREIGN KEY (archived_by_user_id) REFERENCES "Risk_Assess_Framework".users(id) ON DELETE SET NULL;


--
-- Name: riskassessmentreference riskassessmentreference_department_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".riskassessmentreference
    ADD CONSTRAINT riskassessmentreference_department_id_fkey FOREIGN KEY (department_id) REFERENCES "Risk_Assess_Framework".departments(id) ON DELETE SET NULL;


--
-- Name: riskassessmentreference riskassessmentreference_project_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".riskassessmentreference
    ADD CONSTRAINT riskassessmentreference_project_id_fkey FOREIGN KEY (project_id) REFERENCES "Risk_Assess_Framework".projects(id) ON DELETE SET NULL;


--
-- Name: riskassessmentreference riskassessmentreference_status_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".riskassessmentreference
    ADD CONSTRAINT riskassessmentreference_status_id_fkey FOREIGN KEY (status_id) REFERENCES "Risk_Assess_Framework".ra_referencestatus(id);


--
-- Name: riskmatrix_outcome riskmatrix_outcome_keyriskfactorsid_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".riskmatrix_outcome
    ADD CONSTRAINT riskmatrix_outcome_keyriskfactorsid_fkey FOREIGN KEY (keyriskfactorsid) REFERENCES "Risk_Assess_Framework".ra_keyriskfactors(id);


--
-- Name: riskmatrix_outcome riskmatrix_outcome_riskassessmentid_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".riskmatrix_outcome
    ADD CONSTRAINT riskmatrix_outcome_riskassessmentid_fkey FOREIGN KEY (riskassessmentid) REFERENCES "Risk_Assess_Framework".riskassessment(riskassessment_refid);


--
-- Name: riskmatrix_setup riskmatrix_setup_riskimpact_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".riskmatrix_setup
    ADD CONSTRAINT riskmatrix_setup_riskimpact_id_fkey FOREIGN KEY (riskimpact_id) REFERENCES "Risk_Assess_Framework".ra_riskimpact(id);


--
-- Name: riskmatrix_setup riskmatrix_setup_risklikelihood_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".riskmatrix_setup
    ADD CONSTRAINT riskmatrix_setup_risklikelihood_id_fkey FOREIGN KEY (risklikelihood_id) REFERENCES public.ra_risklikelihood(id);


--
-- Name: users users_department_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".users
    ADD CONSTRAINT users_department_id_fkey FOREIGN KEY (department_id) REFERENCES "Risk_Assess_Framework".departments(id) ON DELETE SET NULL;


--
-- Name: users users_role_id_fkey; Type: FK CONSTRAINT; Schema: Risk_Assess_Framework; Owner: -
--

ALTER TABLE ONLY "Risk_Assess_Framework".users
    ADD CONSTRAINT users_role_id_fkey FOREIGN KEY (role_id) REFERENCES "Risk_Assess_Framework".ra_userroles(id);


--
-- Name: ControlTest FK_ControlTest_WorkflowInstance; Type: FK CONSTRAINT; Schema: Risk_Workflow; Owner: -
--

ALTER TABLE ONLY "Risk_Workflow"."ControlTest"
    ADD CONSTRAINT "FK_ControlTest_WorkflowInstance" FOREIGN KEY ("WorkflowInstanceId") REFERENCES "Risk_Workflow"."WorkflowInstance"("Id") ON DELETE CASCADE;


--
-- Name: WorkflowExecutionLog FK_ExecutionLog_WorkflowInstance; Type: FK CONSTRAINT; Schema: Risk_Workflow; Owner: -
--

ALTER TABLE ONLY "Risk_Workflow"."WorkflowExecutionLog"
    ADD CONSTRAINT "FK_ExecutionLog_WorkflowInstance" FOREIGN KEY ("WorkflowInstanceId") REFERENCES "Risk_Workflow"."WorkflowInstance"("Id") ON DELETE CASCADE;


--
-- Name: RemediationTask FK_RemediationTask_ControlTest; Type: FK CONSTRAINT; Schema: Risk_Workflow; Owner: -
--

ALTER TABLE ONLY "Risk_Workflow"."RemediationTask"
    ADD CONSTRAINT "FK_RemediationTask_ControlTest" FOREIGN KEY ("ControlTestId") REFERENCES "Risk_Workflow"."ControlTest"("Id") ON DELETE CASCADE;


--
-- Name: RiskAssessmentApproval FK_RiskApproval_WorkflowInstance; Type: FK CONSTRAINT; Schema: Risk_Workflow; Owner: -
--

ALTER TABLE ONLY "Risk_Workflow"."RiskAssessmentApproval"
    ADD CONSTRAINT "FK_RiskApproval_WorkflowInstance" FOREIGN KEY ("WorkflowInstanceId") REFERENCES "Risk_Workflow"."WorkflowInstance"("Id") ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--
