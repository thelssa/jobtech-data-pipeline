import pandas as pd
import numpy as np
import re

# Load the unified raw dataset
df = pd.read_csv("datasets_clean/unified_raw.csv")

final_dfs = []

# --- GLASSDOOR ---
def parse_glassdoor_salary(s):
    """
    Parse Glassdoor salary estimate to extract min/max annual salary in USD.
    Supports formats like "$63K-$112K (Glassdoor est.)" or "$53K-$91K".
    Returns (salary_min, salary_max)
    """
    if isinstance(s, str):
        nums = re.findall(r"\$?(\d+)[Kk]", s)
        if len(nums) == 2:
            return int(nums[0]) * 1000, int(nums[1]) * 1000
        elif len(nums) == 1:
            return int(nums[0]) * 1000, int(nums[0]) * 1000
    return np.nan, np.nan

if "glassdoor" in df["source"].unique():
    gd_cols = {
        "Job Title": "title",
        "Company Name": "company",
        "Salary Estimate": "salary_estimate",
        "Industry": "industry",
        "Sector": "sector",
        "Location": "location",
        "Revenue": "revenue",
        # add other useful columns if needed
    }
    glassdoor = df[df["source"] == "glassdoor"]
    present = [k for k in gd_cols.keys() if k in glassdoor.columns]
    glassdoor_clean = glassdoor[present].rename(columns={k: gd_cols[k] for k in present})
    glassdoor_clean["source"] = "glassdoor"
    # Parse salary
    glassdoor_clean[["salary_min", "salary_max"]] = glassdoor_clean["salary_estimate"].apply(
        lambda x: pd.Series(parse_glassdoor_salary(x))
    )
    final_dfs.append(glassdoor_clean)

# --- STACKOVERFLOW ---
if "stackoverflow" in df["source"].unique():
    so_cols = {
        "MainBranch": "main_branch",
        "Age": "age",
        "Employment": "employment",
        "RemoteWork": "remote_work",
        "Country": "country",
        "YearsCode": "years_code",
        "DevType": "developer_type",
        "ConvertedCompYearly": "salary_yearly",
        "Industry": "industry",
        "JobSat": "job_satisfaction",
        # add more columns if needed
    }
    stackoverflow = df[df["source"] == "stackoverflow"]
    present = [k for k in so_cols.keys() if k in stackoverflow.columns]
    stackoverflow_clean = stackoverflow[present].rename(columns={k: so_cols[k] for k in present})
    stackoverflow_clean["source"] = "stackoverflow"
    # If available, copy salary_yearly into salary_min/salary_max
    if "salary_yearly" in stackoverflow_clean.columns:
        stackoverflow_clean["salary_min"] = stackoverflow_clean["salary_yearly"]
        stackoverflow_clean["salary_max"] = stackoverflow_clean["salary_yearly"]
    final_dfs.append(stackoverflow_clean)

# --- ADZUNA ---
if "adzuna" in df["source"].unique():
    adzuna_cols = {
        "titre": "title",
        "company": "company",
        "secteur": "sector",
        "pays": "country",
        "salaire_min": "salary_min",
        "salaire_max": "salary_max",
        "techno_recherche": "skills_extracted",
        "url": "url",
        "is_remote": "remote",
        # add more if needed
    }
    adzuna = df[df["source"] == "adzuna"]
    present = [k for k in adzuna_cols.keys() if k in adzuna.columns]
    adzuna_clean = adzuna[present].rename(columns={k: adzuna_cols[k] for k in present})
    adzuna_clean["source"] = "adzuna"
    final_dfs.append(adzuna_clean)

# --- GITHUB ---
if "github" in df["source"].unique():
    github_cols = {
        "name": "repo_name",
        "full_name": "full_repo_name",
        "language": "language",
        "stars": "stars",
        "forks": "forks",
        "topics": "topics",
        "created_at": "created_at",
        "updated_at": "updated_at",
        # add more if needed
    }
    github = df[df["source"] == "github"]
    present = [k for k in github_cols.keys() if k in github.columns]
    github_clean = github[present].rename(columns={k: github_cols[k] for k in present})
    github_clean["source"] = "github"
    final_dfs.append(github_clean)

# --- REMOTEOK ---
if "remoteok" in df["source"].unique():
    remoteok_cols = {
        "title": "title",
        "company": "company",
        "location": "location",
        "skills_extracted": "skills",
        "sector_extracted": "sector",
        "url": "url",
        # add more if needed
    }
    remoteok = df[df["source"] == "remoteok"]
    present = [k for k in remoteok_cols.keys() if k in remoteok.columns]
    remoteok_clean = remoteok[present].rename(columns={k: remoteok_cols[k] for k in present})
    remoteok_clean["source"] = "remoteok"
    final_dfs.append(remoteok_clean)

# --------- CONCAT & SAVE ---------
if not final_dfs:
    print("No data to clean!")
    exit(1)

# Standard column order for output (adapt as needed)
main_cols = [
    "source", "title", "company", "industry", "sector", "location", "country",
    "salary_estimate", "salary_min", "salary_max", "skills_extracted", "repo_name",
    "full_repo_name", "language", "stars", "forks", "topics", "created_at", "updated_at",
    "remote", "url"
]

ordered_cols = [c for c in main_cols if c in pd.concat(final_dfs, axis=0).columns] + [
    c for c in pd.concat(final_dfs, axis=0).columns if c not in main_cols
]

df_final = pd.concat(final_dfs, ignore_index=True, sort=False)
df_final = df_final[ordered_cols]

# Replace NaN with empty strings
df_final.replace({np.nan: ""}, inplace=True)

# Save cleaned file
df_final.to_csv("datasets_clean/final_clean.csv", index=False)
print("[CLEAN] Cleaned file saved as datasets_clean/final_clean.csv")
