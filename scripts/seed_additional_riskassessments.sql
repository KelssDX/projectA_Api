-- Seed Additional Risk Assessment Data for Analytics Dashboard
-- Run this script against the Risk_Assess_Framework database

-- First, let's add more risk assessments linked to reference_id = 2
-- to make the analytical charts more meaningful

INSERT INTO "Risk_Assess_Framework".riskassessment 
(riskassessment_refid, businessobjectives, mainprocess, subprocess, keyriskandfactors, mitigatingcontrols, responsibility, authoriser, auditorsrecommendedactionplan, responsibleperson, agreeddate, risklikelihoodid, riskimpactid, keysecondaryid, riskcategoryid, datafrequencyid, frequencyid, evidenceid, outcomelikelihoodid, impactid, reference_id, department_id, project_id, auditor_id, status_id, created_at, updated_at)
VALUES 
(6, 'Improve Customer Service', 'Customer Support', 'Call Center Operations', 'Service Level Breaches', 'Call monitoring, Staff training', 'Customer Service Dept', 'COO', 'Implement AI chatbot', 'Jane Smith', NOW(), 3, 3, 1, 1, 1, 1, 1, 3, 2, 2, NULL, NULL, NULL, 1, NOW(), NOW()),
(7, 'Reduce Operational Costs', 'Supply Chain', 'Vendor Management', 'Supply Chain Disruption', 'Multi-vendor strategy, Safety stock', 'Procurement', 'CFO', 'Diversify supplier base', 'Mike Johnson', NOW(), 4, 4, 2, 2, 2, 2, 2, 4, 3, 2, NULL, NULL, NULL, 1, NOW(), NOW()),
(8, 'Ensure Data Integrity', 'IT Operations', 'Database Management', 'Data Corruption Risk', 'Regular backups, RAID systems', 'IT Department', 'CTO', 'Implement real-time replication', 'Sarah Lee', NOW(), 2, 5, 1, 1, 1, 1, 1, 2, 1, 2, NULL, NULL, NULL, 1, NOW(), NOW()),
(9, 'Meet Regulatory Requirements', 'Compliance', 'Regulatory Reporting', 'Reporting Deadline Miss', 'Automated reporting, Reminders', 'Compliance Team', 'Chief Compliance Officer', 'Early submission policy', 'Tom Brown', NOW(), 3, 4, 2, 3, 1, 1, 1, 2, 2, 2, NULL, NULL, NULL, 1, NOW(), NOW()),
(10, 'Protect Brand Reputation', 'Marketing', 'Social Media Management', 'Negative PR Incident', 'Social media monitoring, Crisis plan', 'Marketing Dept', 'CMO', 'Establish response protocol', 'Emily Davis', NOW(), 2, 3, 1, 2, 1, 1, 1, 1, 1, 2, NULL, NULL, NULL, 1, NOW(), NOW()),
(11, 'Secure Financial Transactions', 'Treasury', 'Payment Processing', 'Fraud Loss', 'Transaction limits, 2FA', 'Treasury Dept', 'CFO', 'Deploy fraud detection AI', 'David Wilson', NOW(), 4, 5, 2, 1, 2, 2, 2, 3, 3, 2, NULL, NULL, NULL, 1, NOW(), NOW()),
(12, 'Maintain System Availability', 'IT Operations', 'Infrastructure', 'System Downtime', 'Redundancy, Failover systems', 'IT Ops', 'CTO', 'Move to cloud HA', 'Chris Martin', NOW(), 5, 5, 1, 1, 1, 1, 1, 4, 3, 2, NULL, NULL, NULL, 1, NOW(), NOW()),
(13, 'Ensure Employee Safety', 'HR', 'Workplace Safety', 'Workplace Injury', 'Safety training, PPE', 'HR Department', 'CHRO', 'Safety audits quarterly', 'Lisa Anderson', NOW(), 2, 4, 2, 2, 1, 1, 1, 1, 1, 2, NULL, NULL, NULL, 1, NOW(), NOW());
