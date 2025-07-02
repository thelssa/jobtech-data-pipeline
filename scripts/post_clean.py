import pandas as pd
import numpy as np

# Lecture du fichier propre
df = pd.read_csv("datasets_clean/final_ready_postgres.csv", low_memory=False)

### 1. Supprimer les lignes “trop vides”
cols_min = ["title", "industry", "country", "salary_yearly", "salary_min_clean", "salary_max_clean", "company"]
df['non_nulls'] = df[cols_min].notnull().sum(axis=1)
df = df[df['non_nulls'] >= 3].drop('non_nulls', axis=1)  

### 2. Dédoublonnage total puis sur colonnes clés
df = df.drop_duplicates()  # toutes colonnes
for subset in [["title", "company", "location"], ["title", "company"], ["title"]]:
    if all([c in df.columns for c in subset]):
        df = df.drop_duplicates(subset=subset)

### 3. Suppression des outliers salaires
if 'salary_yearly' in df.columns:
    df = df[(df['salary_yearly'] < 1_000_000) & (df['salary_yearly'] > 10_000)]

### 4. Suppression colonnes inutilisables
to_drop = [c for c in ["skills_list", "skills_extracted_list", "language", "location"] if df[c].isnull().mean() > 0.97]
df = df.drop(columns=to_drop)

### 5. Types/casts
if 'remote' in df.columns:
    df['remote'] = df['remote'].astype('boolean')
if 'job_satisfaction' in df.columns:
    df['job_satisfaction'] = pd.to_numeric(df['job_satisfaction'], errors='coerce')

# Colonnes lower-case + snake_case
df.columns = [c.lower().replace(' ', '_') for c in df.columns]

### 6. Sauvegarde finale
df.to_csv("datasets_clean/final_ready_postgres_curated.csv", index=False)
print("✅ Données filtrées, prêtes pour analyse & base de données.")
