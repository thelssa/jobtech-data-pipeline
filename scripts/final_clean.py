import pandas as pd
import numpy as np
import ast
import json

INPUT = "datasets_clean/final_clean.csv"
OUTPUT = "datasets_clean/final_clean_ready.csv"

df = pd.read_csv(INPUT, low_memory=False)

def parse_skills(x):
    if pd.isnull(x) or x == "" or x == "[]":
        return []
    if isinstance(x, list):
        return x
    try:
        val = ast.literal_eval(x)
        if isinstance(val, list):
            return [str(s).strip() for s in val if s and str(s).strip()]
        else:
            return [str(val).strip()] if val and str(val).strip() else []
    except Exception:
        return [str(s).strip() for s in str(x).replace(";",",").split(",") if s.strip()]

df["skills"] = df["skills"].apply(parse_skills)
df["skills"] = df["skills"].apply(json.dumps)

for col in ["company", "sector", "title", "country"]:
    df[col] = df[col].replace({np.nan: None, "nan": None, "": None})

for col in ["salary_min", "salary_max"]:
    df[col] = df[col].apply(lambda x: float(x) if pd.notnull(x) and str(x).strip() != "" else None)

df.to_csv(OUTPUT, index=False)
print(f"✅ Fichier exporté prêt pour Django/Postgres : {OUTPUT}")
