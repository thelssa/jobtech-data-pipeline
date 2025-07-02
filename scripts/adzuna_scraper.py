import requests
import datetime
import os
import json
import time
import logging
import re

APP_ID = "03d8c83f"
APP_KEY = "05f999f779382b6770f4916e6e91a48e"

COUNTRIES = {
    "fr": "France",
    "de": "Germany",
    "gb": "United Kingdom",
    "es": "Spain",
    "it": "Italy",
    "be": "Belgium",
    "nl": "Netherlands",
    "pl": "Poland",
    "ch": "Switzerland",
    "pt": "Portugal"
}

TECHNOS = ["python", "java", "react"]
SALARY_MIN = 40000
REMOTE_KEYWORDS = ["remote", "work from home", "teletravail", "homeoffice"]
SKILLS_LIST = [
    "python", "java", "react", "sql", "aws", "docker", "node", "typescript", "c#", "c++", "angular", "azure", "kubernetes",
    "data scientist", "ml", "nlp", "tensorflow", "pytorch", "flask", "django"
]
PAGES = 2
PAUSE_BETWEEN_CALLS = 1
RAW_DIR = "raw"
os.makedirs(RAW_DIR, exist_ok=True)

date_str = datetime.datetime.now().strftime("%Y%m%d_%H%M")
logging.basicConfig(filename=os.path.join(RAW_DIR, "adzuna_log.txt"), level=logging.INFO)

def extract_skills(text):
    text = text.lower()
    skills_found = [skill for skill in SKILLS_LIST if re.search(r"\b" + re.escape(skill) + r"\b", text)]
    return skills_found

for country_code, country_name in COUNTRIES.items():
    for techno in TECHNOS:
        all_enriched = []
        print(f"\n[Adzuna] {country_name} ({country_code}), Techno: {techno}, MinSalaire: {SALARY_MIN}")
        for page in range(1, PAGES + 1):
            url = (
                f"https://api.adzuna.com/v1/api/jobs/{country_code}/search/{page}"
                f"?app_id={APP_ID}&app_key={APP_KEY}"
                f"&results_per_page=50"
                f"&what={techno}"
                f"&sort_by=date"
            )
            if SALARY_MIN:
                url += f"&salary_min={SALARY_MIN}"

            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                for job in data.get("results", []):
                    title = job.get("title", "")
                    description = job.get("description", "")
                    sector = job.get("category", {}).get("label", "")
                    text = title + " " + description
                    skills_found = extract_skills(text)
                    is_remote = any(rk in text.lower() for rk in REMOTE_KEYWORDS)
                    enriched = {
                        "pays": country_name,
                        "code_pays": country_code,
                        "titre": title,
                        "description": description,
                        "secteur": sector,
                        "skills": skills_found,
                        "techno_recherche": techno,
                        "is_remote": is_remote,
                        "salaire_min": job.get("salary_min"),
                        "salaire_max": job.get("salary_max"),
                        "salaire_predicted": job.get("salary_is_predicted", "0"),
                        "url": job.get("redirect_url"),
                        "date_collected": date_str
                    }
                    all_enriched.append(enriched)
            else:
                print(f"  ! Erreur API : {response.status_code} - {response.text}")
            time.sleep(PAUSE_BETWEEN_CALLS)

        output_file = os.path.join(
            RAW_DIR,
            f"adzuna_{country_code}_{techno}_{SALARY_MIN}min_{date_str}.json"
        )
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(all_enriched, f, ensure_ascii=False, indent=2)
        print(f"  -> {len(all_enriched)} offres enrichies '{techno}' ({country_code}) sauvegardées dans {output_file}")

print("\n[Adzuna] Collecte enrichie terminée.")
