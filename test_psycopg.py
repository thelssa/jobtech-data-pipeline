import pandas as pd
import numpy as np
import ast
import re

df = pd.read_csv("datasets_clean/unified_raw.csv", low_memory=False)

# 1. Trouve la 1ère colonne remplie pour chaque info clé

def choose_first_filled(row, candidates):
    for col in candidates:
        if col in row and pd.notnull(row[col]) and str(row[col]).strip():
            return str(row[col]).strip()
    return np.nan

df["company"] = df.apply(lambda row: choose_first_filled(row, ["company", "entreprise", "companie"]), axis=1)
df["title"]   = df.apply(lambda row: choose_first_filled(row, ["title", "titre", "job_title", "role"]), axis=1)
df["sector_raw"] = df.apply(lambda row: choose_first_filled(row, [
    "sector", "secteur", "industry", "job_category", "categoria", "branche", "fonction", "category",
    "emplois catégorie", "profession", "emploi", "berufsfeld", "branche", "functie", "vakgebied", "bereik"
]), axis=1)

# 2. Mapping sector large
sector_map = {
    # Null/unknown
    "-1": np.nan, "n/a": np.nan, "unknown": np.nan, "Unknown / Non-Applicable": np.nan,
    "n.a.": np.nan, "none": np.nan, "not specified": np.nan, "nan": np.nan, "": np.nan, None: np.nan,
    # IT / Tech
    "it": "IT", "informatique": "IT", "ict": "IT", "tech": "IT", "technology": "IT", "web": "IT",
    "digital": "IT", "software": "IT", "developer": "IT", "data": "IT", "development": "IT",
    "information technology": "IT", "computer science": "IT", "informatik": "IT",
    "it ict vacatures": "IT", "web development": "IT", "webdeveloper": "IT",
    # Engineering
    "engineering": "Engineering", "ingenierie": "Engineering", "ingénierie": "Engineering",
    "ingeniería": "Engineering", "mechanical": "Engineering", "construction": "Engineering",
    "bouwkunde vacatures": "Engineering", "bauwesen": "Engineering",
    # Finance
    "finance": "Finance", "banque": "Finance", "bank": "Finance", "accounting": "Finance",
    "assurance": "Finance", "insurance": "Finance", "financial": "Finance", "contabilità": "Finance",
    # Marketing / Sales
    "marketing": "Marketing", "pr reclame en marketing vacatures": "Marketing",
    "sales": "Sales", "vente": "Sales", "commercial": "Sales", "publicité": "Marketing",
    "communication": "Marketing", "media": "Marketing", "advertising": "Marketing",
    # Health
    "santé": "Health", "health": "Health", "healthcare": "Health", "medical": "Health",
    "médecine": "Health", "medizin": "Health", "pharma": "Health",
    # HR / Admin
    "hr": "HR", "human resources": "HR", "ressources humaines": "HR",
    "administration": "Admin", "admin": "Admin", "administratif": "Admin",
    # Legal / Law
    "legal": "Legal", "juridique": "Legal", "recht": "Legal", "law": "Legal",
    # Education
    "education": "Education", "enseignement": "Education", "teaching": "Education",
    # Science / R&D
    "science": "Science", "r&d": "Science", "research": "Science", "recherche": "Science",
    # Construction / Logistics
    "logistics": "Logistics", "logistique": "Logistics", "supply chain": "Logistics",
    "transport": "Logistics", "shipping": "Logistics",
    # Customer Service
    "customer service": "Customer Service", "support client": "Customer Service",
    # General / Other
    "autre": "Other", "andere": "Other", "other": "Other",
    "vacatures ander of algemeen": "Other", "divers": "Other", "miscellaneous": "Other",
    "algemeen": "Other", "general": "Other", "altro": "Other", "sonstiges": "Other",
}

def normalize_sector(val):
    if pd.isnull(val) or not str(val).strip(): return np.nan
    s = str(val).strip().lower()
    s = re.sub(r'[àáâäãå]', 'a', s)
    s = re.sub(r'[èéêë]', 'e', s)
    s = re.sub(r'[ìíîï]', 'i', s)
    s = re.sub(r'[òóôöõ]', 'o', s)
    s = re.sub(r'[ùúûü]', 'u', s)
    s = re.sub(r'[^a-z0-9&/ \-]', '', s)
    s = s.replace("/", " ").replace("&", "and").replace("  ", " ")
    s = s.strip()
    # Fallback : match partiel sur les mots clés si pas dans le mapping
    for k, v in sector_map.items():
        if k and isinstance(k, str) and k in s:
            return v
    return sector_map.get(s, "Other")

df["sector"] = df["sector_raw"].apply(normalize_sector)

# 3. Salary min/max
def clean_salary(x):
    try:
        if pd.isnull(x) or x == '': return np.nan
        x = str(x).replace(" ", "").replace(",", ".")
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

# 4. Skills (toujours liste)
def clean_skills(val):
    try:
        if pd.isnull(val) or val == '': return []
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

# 5. Export clean
final_cols = ["company", "sector", "title", "salary_min", "salary_max", "skills"]
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

# Rapport : taux de remplissage et secteurs non mappés
print(f"✅ Fichier exporté : datasets_clean/final_clean.csv ({len(df_final)} lignes)")
print("Taux de remplissage :")
for col in final_cols:
    nonnull = df_final[col].notnull().sum()
    print(f"- {col}: {nonnull} non vides sur {len(df_final)}")

# Affiche les sectors non mappés (uniques bruts)
print("\nExemples de secteurs restants après mapping :")
print(sorted(df['sector_raw'].dropna().unique())[:30])
