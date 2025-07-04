import pandas as pd
import numpy as np
import ast
import re

df = pd.read_csv("datasets_clean/unified_raw.csv", low_memory=False)

# -------- 1. Company : always present, strip, lower if needed -----------
if "company" not in df.columns:
    df["company"] = ""
else:
    df["company"] = df["company"].fillna("").astype(str).str.strip()

# -------- 2. Sector: harmonization avancée --------
sector_map = {
    # Null/unknown
    "-1": np.nan, "n/a": np.nan, "unknown": np.nan, "Unknown / Non-Applicable": np.nan,
    "n.a.": np.nan, "none": np.nan, "not specified": np.nan, "nan": np.nan, "": np.nan, None: np.nan,
    "autre": "Other", "andere": "Other", "other": "Other",
    # IT / Tech
    "it": "IT", "it ict vacatures": "IT", "ict": "IT", "ict it": "IT",
    "informatique": "IT", "tech": "IT", "technologie": "IT", "technology": "IT", "software": "IT",
    "data": "IT", "big data": "IT", "informatik": "IT", "development": "IT",
    "information technology": "IT", "information-technology": "IT", "information systems": "IT",
    "computer science": "IT", "it & telecom": "IT", "telecom": "IT",
    "web": "IT", "web development": "IT", "webdevelopment": "IT", "digital": "IT",
    # Engineering
    "engineering": "Engineering", "bouwkunde vacatures": "Engineering",
    "ingenierie": "Engineering", "ingénierie": "Engineering", "ingeniería": "Engineering",
    "ingenieurwesen": "Engineering", "mécanique": "Engineering", "mechanical": "Engineering",
    # Finance
    "finance": "Finance", "banque": "Finance", "bank": "Finance", "accounting": "Finance",
    "assurance": "Finance", "insurance": "Finance", "financial": "Finance",
    # Marketing / Sales
    "pr reclame en marketing vacatures": "Marketing",
    "marketing": "Marketing", "sales": "Sales", "vente": "Sales", "commercial": "Sales",
    "publicité": "Marketing", "communication": "Marketing", "media": "Marketing",
    # Health
    "santé": "Health", "health": "Health", "healthcare": "Health", "medical": "Health",
    "médecine": "Health", "medizin": "Health", "pharma": "Health",
    # HR / Admin
    "hr": "HR", "human resources": "HR", "ressources humaines": "HR",
    "administration": "Admin", "admin": "Admin", "administratif": "Admin",
    # Legal / Law
    "legal": "Legal", "juridique": "Legal", "recht": "Legal", "law": "Legal",
    # Education / Teaching
    "education": "Education", "enseignement": "Education", "teaching": "Education",
    "enseignement / education": "Education",
    # Science / R&D
    "science": "Science", "r&d": "Science", "research": "Science", "recherche": "Science",
    # Construction
    "construction": "Construction", "bouw": "Construction", "bâtiment": "Construction",
    # Transport / Logistics
    "logistics": "Logistics", "logistique": "Logistics", "supply chain": "Logistics",
    "transport": "Logistics", "transports": "Logistics", "shipping": "Logistics",
    # Customer Service
    "customer service": "Customer Service", "support client": "Customer Service",
    # Other / General
    "vacatures ander of algemeen": "Other", "divers": "Other", "miscellaneous": "Other",
    "allgemein": "Other", "algemeen": "Other", "diverso": "Other",
}

def normalize_sector(val):
    if pd.isnull(val): return np.nan
    # Harmonise : retire accents, lower, retire symboles inutiles
    s = str(val).strip().lower()
    s = re.sub(r'[àáâäãå]', 'a', s)
    s = re.sub(r'[èéêë]', 'e', s)
    s = re.sub(r'[ìíîï]', 'i', s)
    s = re.sub(r'[òóôöõ]', 'o', s)
    s = re.sub(r'[ùúûü]', 'u', s)
    s = re.sub(r'[^a-z0-9&/ \-]', '', s)
    s = s.replace("/", " ").replace("&", "and").replace("  ", " ")
    s = s.strip()
    return sector_map.get(s, val.strip().title())  # Garde valeur lisible si inconnue

def find_sector(row):
    for key in ["sector", "secteur", "industry"]:
        if key in row and pd.notnull(row[key]) and str(row[key]).strip():
            return str(row[key]).strip()
    return np.nan

if "sector" not in df.columns:
    df["sector"] = df.apply(find_sector, axis=1)
df["sector"] = df["sector"].apply(normalize_sector).replace("nan", np.nan).replace("", np.nan)

# -------- 3. Title --------
if "title" not in df.columns and "titre" in df.columns:
    df["title"] = df["titre"]
elif "title" not in df.columns:
    df["title"] = ""
df["title"] = df["title"].fillna("").astype(str).str.strip()

# -------- 4. Salary min/max --------
def clean_salary(x):
    try:
        if pd.isnull(x) or x == '': return np.nan
        x = str(x).replace(" ", "").replace(",", ".")
        # gère les valeurs style "¥1M", "1.2k", "500K", etc.
        mult = 1
        if x.lower().endswith('k'): mult = 1_000; x = x[:-1]
        if x.lower().endswith('m'): mult = 1_000_000; x = x[:-1]
        return float(x) * mult
    except:
        return np.nan

for orig, target in [("salaire_min", "salary_min"), ("salary_min", "salary_min"),
                     ("salaire_max", "salary_max"), ("salary_max", "salary_max")]:
    if orig in df.columns:
        df[target] = df[orig].apply(clean_salary)

# -------- 5. Skills --------
def clean_skills(val):
    try:
        if pd.isnull(val) or val == '': return []
        if isinstance(val, list): return [str(x).strip() for x in val if x]
        s = str(val).strip()
        if s.startswith("[") and s.endswith("]"):
            # liste python
            return [x.strip("'\" ") for x in ast.literal_eval(s) if x]
        return [x.strip() for x in s.replace(";", ",").split(",") if x.strip()]
    except:
        return []
if "skills" not in df.columns:
    df["skills"] = [[] for _ in range(len(df))]
else:
    df["skills"] = df["skills"].apply(clean_skills)

final_cols = ["company", "sector", "title", "salary_min", "salary_max", "skills"]
df_final = df[final_cols].copy()

# Garde si au moins une info pertinente
df_final = df_final[
    (df_final["title"].str.len() > 0) |
    (df_final["company"].str.len() > 0) |
    (df_final["sector"].notnull()) |
    (df_final["skills"].apply(lambda x: len(x) > 0))
]

# Drop doublons robuste
df_final["skills"] = df_final["skills"].apply(lambda x: ",".join(x) if isinstance(x, list) else str(x))
df_final = df_final.drop_duplicates()
df_final["skills"] = df_final["skills"].apply(lambda x: [s.strip() for s in x.split(",") if s.strip()] if isinstance(x, str) and x else [])

df_final.columns = [c.lower() for c in df_final.columns]
df_final.to_csv("datasets_clean/final_clean.csv", index=False)
print(f"✅ Fichier exporté : datasets_clean/final_clean.csv ({len(df_final)} lignes)")
