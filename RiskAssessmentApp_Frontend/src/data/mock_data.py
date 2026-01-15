MOCK_ANALYTICAL_REPORT = {
    "summary": "Sample analytical summary for demonstration.",
    "riskReduction": [
        {"level": "Critical", "inherentCount": 5, "residualCount": 2},
        {"level": "High", "inherentCount": 12, "residualCount": 4},
        {"level": "Medium", "inherentCount": 20, "residualCount": 8},
        {"level": "Low", "inherentCount": 15, "residualCount": 5},
        {"level": "Very Low", "inherentCount": 8, "residualCount": 3}
    ],
    "categoryDistribution": [
        {"categoryName": "Financial", "count": 15},
        {"categoryName": "Operational", "count": 25},
        {"categoryName": "Strategic", "count": 10},
        {"categoryName": "Compliance", "count": 12},
        {"categoryName": "reputational", "count": 8}
    ],
    "controlStats": [
        {
            "statType": "Coverage",
            "value": "82%",
            "description": "82% of key risks have at least one effective control mapped."
        }
    ]
}

MOCK_MARKET_DATA = [
    {"date": f"2023-01-{i:02d}", "closePrice": 140 + (i * 0.5), "logReturn": 0.001 * i} for i in range(1, 101)
]

MOCK_MARKET_METRICS = {
    "vaR95": -0.025,
    "cVaR95": -0.042,
    "volatility": 0.015
}

MOCK_TOP_RISKS = [
    {
        "Id": 101,
        "MainProcess": "Unauthorized Trading",
        "Source": "People",
        "LossFrequency": "Annually",
        "LossAmount": 1200000,
        "VaR": -750000
    },
    {
        "Id": 102,
        "MainProcess": "System Outage - Core Banking",
        "Source": "Systems",
        "LossFrequency": "Quarterly",
        "LossAmount": 2500000,
        "VaR": -1500000
    },
    {
        "Id": 103,
        "MainProcess": "Data Privacy Breach",
        "Source": "External",
        "LossFrequency": "Annually",
        "LossAmount": 5000000,
        "VaR": -3000000
    }
]
