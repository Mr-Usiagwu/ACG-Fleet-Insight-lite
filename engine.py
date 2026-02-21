import pandas as pd
import numpy as np

def generate_fleet_data():  # <--- Check this spelling
    tails = [f"N{i}0{i}AC" for i in range(1, 11)]
    models = ["Airbus A320", "Boeing 737-800"]
    
    data = []
    for tail in tails:
        model = np.random.choice(models)
        cycles = np.random.randint(50, 200) 
        hours = cycles * np.random.uniform(1.8, 2.5)
        faults = np.random.randint(0, 8)
        days_since_check = np.random.randint(10, 500)
        
        data.append({
            "Tail_Number": tail,
            "Model": model,
            "Flight_Hours": round(hours, 1),
            "Flight_Cycles": cycles,
            "Technical_Faults": faults,
            "Days_Since_Check": days_since_check
        })
    
    return pd.DataFrame(data)

def apply_risk_logic(df):  # <--- Check this spelling
    df['Risk_Score'] = (df['Technical_Faults'] * 12) + \
                       (df['Days_Since_Check'] * 0.05) + \
                       (df['Flight_Hours'] * 0.001)
    
    df['Risk_Score'] = df['Risk_Score'].clip(0, 100).round(1)
    df['Financial_Exposure'] = (df['Risk_Score'] * 150).round(0)
    
    return df