import pandas as pd
import numpy as np
import pycountry
import re

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
    if "country" in df.columns:
        df["country"] = df["country"].apply(country_to_iso)
    elif "pays" in df.columns:
        df["country"] = df["pays"].apply(country_to_iso)
    if "pays" in df.columns:
        df.drop(columns=["pays"], inplace=True)
    print("✔ Harmonisation des pays")
    return df

def harmonize_industry_sector(df):
    industry_replace = {
        '-1': np.nan,
        'n/a': np.nan,
        'n.a.': np.nan,
        'none': np.nan,
        'unknown': np.nan,
        'Unknown': np.nan,
        'Unknown / Non-Applicable': np.nan,
        'not specified': np.nan,
        '': np.nan,
        'nan': np.nan,
        None: np.nan,
        "Biotech & Pharmaceuticals": "Biotechnology",
        "Biotech and Pharmaceuticals": "Biotechnology",
        "Consumer Products Manufacturing": "Consumer Products",
        "Consumer Packaged Goods": "Consumer Products",
        "Banks & Credit Unions": "Finance",
        "Investment Banking & Asset Management": "Finance",
        "Financial Analytics & Research": "Finance",
        "Insurance Agencies & Brokerages": "Insurance",
        "Insurance Carriers": "Insurance",
        "IT Services": "Information Technology",
        "Enterprise Software & Network Solutions": "Information Technology",
        "Internet": "Information Technology",
        "Computer Hardware & Software": "Information Technology",
        "Telecommunications Services": "Telecommunications",
        "Motion Picture Production & Distribution": "Media",
        "TV Broadcast & Cable Networks": "Media",
        "Video Games": "Media",
        "Research & Development": "Business Services",
        "Advertising & Marketing": "Business Services",
        "Consulting": "Business Services",
        "Wholesale": "Business Services",
        "Staffing & Outsourcing": "Business Services",
        "Aerospace & Defense": "Aerospace & Defense",
        "Logistics & Supply Chain": "Transportation & Logistics",
        "Transportation Management": "Transportation & Logistics",
        "Oil, Gas, Energy & Utilities": "Energy",
        "Industrial Manufacturing": "Manufacturing",
        "Food & Beverage Manufacturing": "Manufacturing",
        "Transportation Equipment Manufacturing": "Manufacturing",
        "Mining": "Mining & Metals",
        "Metals Brokers": "Mining & Metals",
        "Education Training Services": "Education",
        "Colleges & Universities": "Education",
        "Preschool & Child Care": "Education",
        "Religious Organizations": "Non-Profit",
        "Social Assistance": "Non-Profit",
        "Architectural & Engineering Services": "Business Services",
    }
    for col in ["industry", "sector"]:
        if col in df.columns:
            df[col] = df[col].replace(industry_replace)
    print("✔ Harmonisation des industries et secteurs")
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
    print("✔ Parsing et normalisation des salaires")
    return df

def clean_skills(skills):
    if pd.isnull(skills) or str(skills).strip() in ['', 'nan', '-1', 'None']:
        return []
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
    print("✔ Parsing et normalisation des skills")
    return df

def clean_missing(df):
    df.replace(['', ' ', '-1', 'nan', 'NaN', 'None'], np.nan, inplace=True)
    print("✔ Nettoyage des valeurs manquantes")
    return df

def keep_relevant_columns(df):
    useful_cols = [
        "source","title","company","industry","sector","location","country",
        "salary_estimate","salary_min","salary_max","skills_extracted",
        "language","remote","age","employment","remote_work","years_code",
        "developer_type","salary_yearly","job_satisfaction","skills",
        "salary_min_clean","salary_max_clean","skills_list","skills_extracted_list"
    ]
    keep_cols = [c for c in useful_cols if c in df.columns]
    return df[keep_cols]

def clean_all_pipeline(input_path, output_path):
    print("=== Lancement du pipeline de nettoyage & harmonisation ===")
    df = pd.read_csv(input_path)
    df = harmonize_country(df)
    df = harmonize_industry_sector(df)
    df = harmonize_salary(df)
    df = harmonize_skills(df)
    df = clean_missing(df)
    df = keep_relevant_columns(df)
    df.to_csv(output_path, index=False)
    print(f"\n✔ Données nettoyées sauvegardées sous : {output_path}")
    print("=== Pipeline terminé ===")

if __name__ == "__main__":
    clean_all_pipeline(
        input_path="datasets_clean/final_clean.csv",
        output_path="datasets_clean/final_clean_ready.csv"
    )
