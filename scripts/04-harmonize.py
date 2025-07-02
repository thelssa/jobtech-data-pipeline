import pandas as pd
import numpy as np
import ast
import re

### === 1. Lecture du fichier CSV === ###
csv_filename = "datasets_clean/final_clean_ready.csv"
df = pd.read_csv(csv_filename, low_memory=False)

### === 2. Colonnes utiles (sélection) === ###
useful_cols = [
    "source", "title", "company", "industry", "sector", "location", "country",
    "salary_min_clean", "salary_max_clean", "language", "remote", "age",
    "employment", "remote_work", "years_code", "developer_type",
    "salary_yearly", "job_satisfaction", "skills_list", "skills_extracted_list"
]
df = df[[c for c in useful_cols if c in df.columns]]

### === 3. Harmonisation Industry & Sector === ###
industry_map = {
    '-1': np.nan, 'n/a': np.nan, 'unknown': np.nan, 'Unknown / Non-Applicable': np.nan,
    'Inna/ogólna': 'Other', 'Inżynieria': 'Engineering', 'IT': 'Tech', 'Technologie informatyczne': 'Tech'
}
sector_map = {
    'IT': 'Tech', 'Business Services': 'Business', 'Health Care': 'Healthcare',
    'Inżynieria': 'Engineering', 'Inna/ogólna': 'Other'
}
if 'industry' in df.columns:
    df['industry'] = df['industry'].replace(industry_map)
if 'sector' in df.columns:
    df['sector'] = df['sector'].replace(sector_map)

### === 4. Harmonisation Pays === ###
country_map = {
    'US': 'USA', 'GB': 'UK', 'PL': 'Poland', 'FR': 'France', 'DE': 'Germany',
    'UA': 'Ukraine', 'MX': 'Mexico', 'SE': 'Sweden', 'ZA': 'South Africa',
    'BE': 'Belgium', 'TH': 'Thailand', 'NL': 'Netherlands'
}
if 'country' in df.columns:
    df['country'] = df['country'].replace(country_map)

### === 5. Remote, Remote_work, Employment : harmonisation binaire/texte === ###
def clean_bool(val):
    if isinstance(val, bool): return val
    if pd.isnull(val): return np.nan
    val = str(val).strip().lower()
    if val in ['true', 'yes', 'remote', 'remoto', '1', 'fully remote']: return True
    if val in ['false', 'no', 'nan', 'none', '', 'in-person', 'non-remote', '0']: return False
    return np.nan

if 'remote' in df.columns:
    df['remote'] = df['remote'].apply(clean_bool)
if 'remote_work' in df.columns:
    df['remote_work'] = df['remote_work'].apply(lambda v: clean_bool(v) if pd.notnull(v) else np.nan)
if 'employment' in df.columns:
    df['employment'] = df['employment'].replace({'nan': np.nan, 'None': np.nan, '': np.nan})

### === 6. Age : formatage simple === ###
def clean_age(age):
    if pd.isnull(age): return np.nan
    age = str(age)
    # Ex: '25-34 years old' => '25-34'
    match = re.search(r'(\d{2})-(\d{2})', age)
    if match: return match.group(0)
    match = re.search(r'(\d{2,})\s*years?', age)
    if match: return match.group(1)
    return np.nan

if 'age' in df.columns:
    df['age'] = df['age'].apply(clean_age)

### === 7. Années d'expérience : cast numérique === ###
def clean_years_code(val):
    if pd.isnull(val): return np.nan
    val = str(val).strip()
    if val in ['nan', 'None', '']: return np.nan
    try:
        if '-' in val:  # ex: "5-7"
            val = val.split('-')[0]
        return float(val)
    except:
        return np.nan

if 'years_code' in df.columns:
    df['years_code'] = df['years_code'].apply(clean_years_code)

### === 8. Salaires : cast float, et harmonisation min/max === ###
for col in ['salary_min_clean', 'salary_max_clean', 'salary_yearly', 'job_satisfaction']:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

### === 9. Skills : nettoyage, listes => string séparées par virgule === ###
def safe_eval_list(val):
    if isinstance(val, list): return val
    if pd.isnull(val) or val in ['', '[]', 'nan', 'None']: return []
    try:
        res = ast.literal_eval(val)
        if isinstance(res, list): return [str(e).strip().lower() for e in res if e]
        return []
    except: return []

for col in ['skills_list', 'skills_extracted_list']:
    if col in df.columns:
        df[col] = df[col].apply(safe_eval_list)
        df[col] = df[col].apply(lambda x: ','.join(sorted(set(x))) if isinstance(x, list) else '')

### === 10. Nettoyage texte : strip + suppression des \r \n, unicité sur titre, company, location... === ###
text_cols = ['title', 'company', 'industry', 'sector', 'location', 'language', 'employment', 'developer_type']
for col in text_cols:
    if col in df.columns:
        df[col] = df[col].astype(str).str.replace(r'[\r\n]+', ' ', regex=True).str.strip()
        df[col] = df[col].replace({'nan': np.nan, 'None': np.nan, '': np.nan})

### === 11. Suppression des lignes "trop vides" (optionnel mais conseillé) === ###
min_non_null = 4  # seuil à adapter
df = df[df.notnull().sum(axis=1) >= min_non_null].reset_index(drop=True)

### === 12. Colonnes snake_case pour Postgres === ###
df.columns = [c.lower().replace(' ', '_') for c in df.columns]

### === 13. Export final === ###
df.to_csv("datasets_clean/final_ready_postgres.csv", index=False)
print("✅ Fichier prêt : final_ready_postgres.csv")
