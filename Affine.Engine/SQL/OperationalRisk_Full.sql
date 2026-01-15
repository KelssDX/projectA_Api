-- Operational Risk Schema
CREATE TABLE IF NOT EXISTS "Risk_Assess_Framework"."OperationalRiskAssessment" (
    "Id" SERIAL PRIMARY KEY,
    "ReferenceId" INT NOT NULL,
    "MainProcess" VARCHAR(200),
    "SubProcess" VARCHAR(200),
    "Source" VARCHAR(100),
    "LossFrequency" VARCHAR(50),
    "LossEventCount" INT,
    "Probability" DECIMAL(10, 4),
    "LossAmount" DECIMAL(18, 2),
    "RiskMeasurement" VARCHAR(50),
    "VaR" DECIMAL(18, 2),
    "SingleVaR" DECIMAL(18, 2),
    "CumulativeVaR" DECIMAL(18, 2),
    "CreatedAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Seed Data (Based on user image)
-- Ideally this runs only if table is empty or via migration tool
-- For demo purposed, we insert if count is 0

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM "Risk_Assess_Framework"."OperationalRiskAssessment") THEN
        INSERT INTO "Risk_Assess_Framework"."OperationalRiskAssessment" 
        ("ReferenceId", "MainProcess", "Source", "LossFrequency", "LossEventCount", "Probability", "LossAmount", "RiskMeasurement", "VaR", "SingleVaR", "CumulativeVaR")
        VALUES 
        (1, 'Internal Fraud', 'People', 'Annually', 1, 0.3679, 900000.00, 'Operational VAR', -544597.05, -544597.05, -1089194.10),
        (1, 'Employment practices', 'People', 'Annually', 4, 0.0153, 250000.00, 'Operational VAR', -6303.21, -6303.21, -409708.43),
        (1, 'Clients, products and business practices', 'External Events', 'Quarterly', 2, 0.0758, 500000.00, 'Operational VAR', -62353.38, -62353.38, -810594.00),
        (1, 'Clients, products and business practices', 'External Events', 'Annually', 2, 0.1839, 500000.00, 'Operational VAR', -151276.96, -151276.96, -756384.79);
    END IF;
END $$;
