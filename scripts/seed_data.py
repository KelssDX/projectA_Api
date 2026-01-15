import psycopg2

conn = psycopg2.connect(
    dbname='Risk_Assess_Framework', 
    user='postgres', 
    password='Monday@123', 
    host='localhost', 
    port='5432'
)
cur = conn.cursor()

# Seed additional risk assessments
sql = """
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
(13, 'Ensure Employee Safety', 'HR', 'Workplace Safety', 'Workplace Injury', 'Safety training, PPE', 'HR Department', 'CHRO', 'Safety audits quarterly', 'Lisa Anderson', NOW(), 2, 4, 2, 2, 1, 1, 1, 1, 1, 2, NULL, NULL, NULL, 1, NOW(), NOW())
"""

cur.execute(sql)
conn.commit()
print('Inserted 8 risk assessments successfully!')

# Also seed operational risk data
sql2 = """
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
(10, 2, 'Manual Processing Error', 'Operations', 'People', 'Monthly', 25, 0.65, 350000, 'Low', -175000, -7000, -15695000, NOW())
ON CONFLICT DO NOTHING
"""

try:
    cur.execute(sql2)
    conn.commit()
    print('Inserted 10 operational risk records successfully!')
except Exception as e:
    print(f'Operational risk insert note: {e}')
    conn.rollback()

cur.close()
conn.close()
print('Done!')
