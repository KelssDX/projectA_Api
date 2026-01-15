-- Seed Operational Risk Assessment Data for Analytics Dashboard
-- Run this script against the Risk_Assess_Framework database

INSERT INTO "Risk_Assess_Framework"."OperationalRiskAssessment" 
("Id", "ReferenceId", "MainProcess", "SubProcess", "Source", "LossFrequency", "LossEventCount", "Probability", "LossAmount", "RiskMeasurement", "VaR", "SingleVaR", "CumulativeVaR", "CreatedAt") 
VALUES 
(1, 2, 'Unauthorized Trading', 'Trade Execution', 'People', 'Annually', 3, 0.15, 1200000, 'High', -750000, -250000, -750000, NOW()),
(2, 2, 'System Outage - Core Banking', 'IT Infrastructure', 'Systems', 'Quarterly', 5, 0.35, 2500000, 'Critical', -1500000, -500000, -2250000, NOW()),
(3, 2, 'Data Privacy Breach', 'Customer Data', 'External', 'Annually', 1, 0.08, 5000000, 'High', -3000000, -3000000, -5250000, NOW()),
(4, 2, 'Payment Processing Failure', 'Payments', 'Systems', 'Monthly', 12, 0.55, 800000, 'Medium', -400000, -66667, -5650000, NOW()),
(5, 2, 'Regulatory Non-Compliance', 'Compliance', 'Process', 'Annually', 2, 0.20, 3500000, 'High', -2100000, -1050000, -7750000, NOW()),
(6, 2, 'Fraud Detection Failure', 'Anti-Fraud', 'People', 'Quarterly', 8, 0.40, 1800000, 'High', -1080000, -135000, -8830000, NOW()),
(7, 2, 'Vendor Service Disruption', 'Vendor Management', 'External', 'Annually', 2, 0.12, 950000, 'Medium', -570000, -285000, -9400000, NOW()),
(8, 2, 'Model Risk - Credit Scoring', 'Model Governance', 'Process', 'Annually', 1, 0.18, 2200000, 'High', -1320000, -1320000, -10720000, NOW()),
(9, 2, 'Cyber Attack - Ransomware', 'Cybersecurity', 'External', 'Annually', 1, 0.05, 8000000, 'Critical', -4800000, -4800000, -15520000, NOW()),
(10, 2, 'Manual Processing Error', 'Operations', 'People', 'Monthly', 25, 0.65, 350000, 'Low', -175000, -7000, -15695000, NOW());
