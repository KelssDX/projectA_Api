import pandas as pd
import sys

try:
    file_path = r'c:\Users\keletso\Source\Repos\projectA_Api\AuditRiskAutomation_Docs\RiskFramework1.xlsx'
    xl = pd.ExcelFile(file_path)
    
    print("SHEETS FOUND:")
    for s in xl.sheet_names:
        print(f"- {s}")
        
    targets = [s for s in xl.sheet_names if "market" in s.lower() or "risk" in s.lower() or "control" in s.lower()]
    
    for t in targets:
        print(f"\n\n=== SHEET: {t} ===")
        df = pd.read_excel(xl, t)
        print(df.head().to_string())
        print("\nCOLUMNS:", list(df.columns))

except Exception as e:
    print(f"ERROR: {e}")
