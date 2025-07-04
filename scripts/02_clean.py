import pandas as pd
import numpy as np
import ast
import re

df = pd.read_csv("datasets_clean/unified_raw.csv", low_memory=False)

def choose_first_filled(row, candidates):
    for col in candidates:
        if col in row and pd.notnull(row[col]) and str(row[col]).strip():
            return str(row[col]).strip()
    return None

# Harmonise le pays
def clean_country(row):
    # Prend "country" sinon "pays" sinon "code_pays"
    return choose_first_filled(row, ["country", "pays", "code_pays"])

df["company"] = df.apply(lambda row: choose_first_filled(row, ["company", "entreprise", "companie"]), axis=1)
df["title"] = df.apply(lambda row: choose_first_filled(row, ["title", "titre", "job_title", "role"]), axis=1)
df["country"] = df.apply(clean_country, axis=1)
df["sector_raw"] = df.apply(lambda row: choose_first_filled(row, [
    "sector", "secteur", "industry", "job_category", "categoria", "branche", "fonction", "category",
    "emplois catégorie", "profession", "emploi", "berufsfeld", "branche", "functie", "vakgebied", "bereik"
]), axis=1)

# Harmonisation sector fuzzy
def normalize_sector(val):
    if pd.isnull(val) or not str(val).strip(): return "Unknown"
    s = str(val).strip().lower()
    s = re.sub(r'[àáâäãå]', 'a', s)
    s = re.sub(r'[èéêë]', 'e', s)
    s = re.sub(r'[ìíîï]', 'i', s)
    s = re.sub(r'[òóôöõ]', 'o', s)
    s = re.sub(r'[ùúûü]', 'u', s)
    s = re.sub(r'[^a-z0-9&/ \-]', '', s)
    s = s.replace("/", " ").replace("&", "and").replace("  ", " ")
    s = s.strip()
    keywords = {
        "it": "IT",
        "informatique": "IT",
        "ict": "IT",
        "engineering": "Engineering",
        "ingenierie": "Engineering",
        "consult": "Consulting",
        "finance": "Finance",
        "comptabilite": "Finance",
        "account": "Finance",
        "retail": "Retail",
        "vente": "Sales",
        "sales": "Sales",
        "marketing": "Marketing",
        "admin": "Admin",
        "administration": "Admin",
        "scientifique": "Science",
        "science": "Science",
        "health": "Health",
        "sante": "Health",
        "medical": "Health",
        "education": "Education",
        "teaching": "Education",
        "logist": "Logistics",
        "transport": "Logistics",
        "customer": "Customer Service",
        "creative": "Design",
        "design": "Design",
        "industrie": "Industry",
        "distribution": "Logistics",
        "autre": "Other",
        "altro": "Other",
        "general": "Other",
        "other": "Other"
    }
    for k, v in keywords.items():
        if k in s:
            return v
    return "Unknown"

df["sector"] = df["sector_raw"].apply(normalize_sector)

# Salary
def clean_salary(x):
    try:
        if pd.isnull(x) or x == '': return None
        x = str(x).replace(" ", "").replace(",", ".")
        mult = 1
        if x.lower().endswith('k'): mult = 1_000; x = x[:-1]
        if x.lower().endswith('m'): mult = 1_000_000; x = x[:-1]
        return float(x) * mult
    except:
        return None

for orig, target in [("salaire_min", "salary_min"), ("salary_min", "salary_min"),
                     ("salaire_max", "salary_max"), ("salary_max", "salary_max")]:
    if orig in df.columns:
        df[target] = df[orig].apply(clean_salary)

def clean_skills(val):
    try:
        if pd.isnull(val) or val == '' or val == "[]": return []
        if isinstance(val, list): return [str(x).strip() for x in val if x]
        s = str(val).strip()
        if s.startswith("[") and s.endswith("]"):
            return [x.strip("'\" ") for x in ast.literal_eval(s) if x]
        return [x.strip() for x in s.replace(";", ",").split(",") if x.strip()]
    except:
        return []
if "skills" not in df.columns:
    df["skills"] = [[] for _ in range(len(df))]
else:
    df["skills"] = df["skills"].apply(clean_skills)

final_cols = ["company", "country", "sector", "title", "salary_min", "salary_max", "skills"]
df_final = df[final_cols].copy()
df_final = df_final[
    (df_final["title"].notnull() & (df_final["title"].str.len() > 0)) |
    (df_final["company"].notnull() & (df_final["company"].str.len() > 0)) |
    (df_final["sector"].notnull()) |
    (df_final["skills"].apply(lambda x: len(x) > 0))
]
df_final["skills"] = df_final["skills"].apply(lambda x: ",".join(x) if isinstance(x, list) else str(x))
df_final = df_final.drop_duplicates()
df_final["skills"] = df_final["skills"].apply(lambda x: [s.strip() for s in x.split(",") if s.strip()] if isinstance(x, str) and x else [])

df_final.columns = [c.lower() for c in df_final.columns]
df_final.to_csv("datasets_clean/final_clean.csv", index=False)
print(f"✅ Fichier exporté : datasets_clean/final_clean.csv ({len(df_final)} lignes)")
