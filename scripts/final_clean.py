import pandas as pd
import numpy as np
import pycountry
import re
import ast

def country_to_iso(country_name):
    if pd.isnull(country_name):
        return np.nan
    country_name = str(country_name).strip()
    if len(country_name) == 2:
        return country_name.upper()
    try:
        return pycountry.countries.lookup(country_name).alpha_2
    except LookupError:
        return np.nan

def harmonize_country(df):
    # Harmonise les pays, crée colonne country si besoin
    if "country" in df.columns:
        df["country"] = df["country"].apply(country_to_iso)
    elif "pays" in df.columns:
        df["country"] = df["pays"].apply(country_to_iso)
    if "pays" in df.columns:
        df.drop(columns=["pays"], inplace=True)
    return df

def harmonize_industry_sector(df):
    # Harmonisation industry/sector
    industry_replace = {
        '-1': np.nan, 'n/a': np.nan, 'n.a.': np.nan, 'none': np.nan, 'unknown': np.nan, 'Unknown': np.nan,
        'Unknown / Non-Applicable': np.nan, 'not specified': np.nan, '': np.nan, 'nan': np.nan, None: np.nan,
        "Biotech & Pharmaceuticals": "Biotechnology",
        "Biotech and Pharmaceuticals": "Biotechnology",
        "Consumer Products Manufacturing": "Consumer Products",
        "Consumer Packaged Goods": "Consumer Products",
        "Banks & Credit Unions": "Finance", "Investment Banking & Asset Management": "Finance",
        "Financial Analytics & Research": "Finance", "Insurance Agencies & Brokerages": "Insurance",
        "Insurance Carriers": "Insurance", "IT Services": "Information Technology",
        "Enterprise Software & Network Solutions": "Information Technology", "Internet": "Information Technology",
        "Computer Hardware & Software": "Information Technology",
        "Telecommunications Services": "Telecommunications",
        "Motion Picture Production & Distribution": "Media", "TV Broadcast & Cable Networks": "Media", "Video Games": "Media",
        "Research & Development": "Business Services", "Advertising & Marketing": "Business Services", "Consulting": "Business Services",
        "Wholesale": "Business Services", "Staffing & Outsourcing": "Business Services",
        "Aerospace & Defense": "Aerospace & Defense",
        "Logistics & Supply Chain": "Transportation & Logistics", "Transportation Management": "Transportation & Logistics",
        "Oil, Gas, Energy & Utilities": "Energy", "Industrial Manufacturing": "Manufacturing",
        "Food & Beverage Manufacturing": "Manufacturing", "Transportation Equipment Manufacturing": "Manufacturing",
        "Mining": "Mining & Metals", "Metals Brokers": "Mining & Metals", "Education Training Services": "Education",
        "Colleges & Universities": "Education", "Preschool & Child Care": "Education", "Religious Organizations": "Non-Profit",
        "Social Assistance": "Non-Profit", "Architectural & Engineering Services": "Business Services",
        'Inna/ogólna': 'Other', 'Inżynieria': 'Engineering', 'IT': 'Tech', 'Technologie informatyczne': 'Tech'
    }
    sector_replace = {
        'IT': 'Tech', 'Business Services': 'Business', 'Health Care': 'Healthcare',
        'Inżynieria': 'Engineering', 'Inna/ogólna': 'Other'
    }
    if "industry" in df.columns:
        df["industry"] = df["industry"].replace(industry_replace)
    if "sector" in df.columns:
        df["sector"] = df["sector"].replace(sector_replace)
    return df

def parse_salary(sal):
    if pd.isnull(sal):
        return (np.nan, np.nan)
    sal = str(sal)
    if any(x in sal.lower() for x in ["unknown", "-1", "nan", "n/a", "non-applicable"]):
        return (np.nan, np.nan)
    if "per hour" in sal.lower():
        matches = re.findall(r'\$?([\d,.]+)[kK]?-\$?([\d,.]+)[kK]?', sal.replace(',', ''))
        if matches:
            low, high = matches[0]
            low, high = float(low), float(high)
            return (low * 40 * 52, high * 40 * 52)
    matches = re.findall(r'\$?([\d,.]+)[kK]?-\$?([\d,.]+)[kK]?', sal.replace(',', ''))
    if matches:
        low, high = matches[0]
        if "K" in sal.upper() or float(low) < 5000:
            low = float(low) * 1000 if float(low) < 5000 else float(low)
            high = float(high) * 1000 if float(high) < 5000 else float(high)
        else:
            low, high = float(low), float(high)
        return (low, high)
    matches = re.findall(r'\$?([\d,.]+)[kK]?', sal.replace(',', ''))
    if len(matches) == 1:
        value = float(matches[0])
        if "K" in sal.upper() or value < 5000:
            value *= 1000
        return (value, value)
    return (np.nan, np.nan)

def harmonize_salary(df):
    if "salary_estimate" in df.columns:
        df[["salary_min_clean", "salary_max_clean"]] = df["salary_estimate"].apply(lambda x: pd.Series(parse_salary(x)))
    for c in ["salary_min_clean", "salary_max_clean", "salary_min", "salary_max", "salary_yearly", "job_satisfaction"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors='coerce')
    return df

def clean_skills(skills):
    if pd.isnull(skills) or str(skills).strip() in ['', 'nan', '-1', 'None']:
        return []
    if isinstance(skills, list):
        return [str(s).strip().lower() for s in skills if s and s != 'nan']
    try:
        arr = ast.literal_eval(str(skills))
        if isinstance(arr, list):
            return [str(s).strip().lower() for s in arr if s and s != 'nan']
    except:
        pass
    splitters = [';', ',', '|', '/', '\\']
    val = str(skills)
    for sep in splitters:
        if sep in val:
            parts = [s.strip().lower() for s in val.split(sep)]
            return sorted(set([s for s in parts if s]))
    return [val.strip().lower()] if val.strip() else []

def harmonize_skills(df):
    for col in ["skills", "skills_extracted"]:
        if col in df.columns:
            df[col + "_list"] = df[col].apply(clean_skills)
            # Pour PostgreSQL : listes en strings séparés par virgules, sans doublons
            df[col + "_list"] = df[col + "_list"].apply(lambda l: ','.join(sorted(set(l))) if isinstance(l, list) else '')
    return df

def clean_missing(df):
    df.replace(['', ' ', '-1', 'nan', 'NaN', 'None'], np.nan, inplace=True)
    return df

def clean_text_fields(df):
    text_cols = ["title", "company", "industry", "sector", "location", "language", "employment", "developer_type"]
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(r'[\r\n]+', ' ', regex=True).str.strip()
            df[col] = df[col].replace({'nan': np.nan, 'None': np.nan, '': np.nan})
    return df

def deduplicate(df):
    # titre+company+location+salary_min_clean+language
    subset = [c for c in ["title", "company", "location", "salary_min_clean", "language"] if c in df.columns]
    before = len(df)
    df = df.drop_duplicates(subset=subset)
    after = len(df)
    print(f"✔ Dédoublonnage : {before - after} doublons supprimés ({before} → {after})")
    return df

def keep_relevant_columns(df):
    useful_cols = [
        "source","title","company","industry","sector","location","country",
        "salary_min_clean","salary_max_clean","language","remote","age","employment",
        "remote_work","years_code","developer_type","salary_yearly","job_satisfaction",
        "skills_list","skills_extracted_list"
    ]
    keep_cols = [c for c in useful_cols if c in df.columns]
    return df[keep_cols]

def filter_empty_rows(df, min_notnull=4):
    return df[df.notnull().sum(axis=1) >= min_notnull].reset_index(drop=True)

def columns_to_snake_case(df):
    df.columns = [c.lower().replace(' ', '_') for c in df.columns]
    return df

def clean_all_pipeline(input_path, output_path):
    print("=== Pipeline nettoyage & harmonisation avancé ===")
    df = pd.read_csv(input_path, low_memory=False)
    df = harmonize_country(df)
    df = harmonize_industry_sector(df)
    df = harmonize_salary(df)
    df = harmonize_skills(df)
    df = clean_text_fields(df)
    df = clean_missing(df)
    df = deduplicate(df)
    df = keep_relevant_columns(df)
    df = filter_empty_rows(df, min_notnull=4)
    df = columns_to_snake_case(df)
    # Pour ingestion PostgreSQL : tout string ou float, pas d'objet ni liste
    df = df.convert_dtypes()
    for col in df.select_dtypes(include='string').columns:
        df[col] = df[col].astype(str)
    for col in df.select_dtypes(include='Int64').columns:
        df[col] = df[col].astype(float)
    df.to_csv(output_path, index=False)
    print(f"\n✅ Données prêtes et exportées sous : {output_path}")

if __name__ == "__main__":
    clean_all_pipeline(
        input_path="datasets_clean/final_clean_ready.csv",
        output_path="final_ready_postgres.csv"
    )
