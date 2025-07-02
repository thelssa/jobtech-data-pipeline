import requests
import pandas as pd
import os
from datetime import datetime
import re
import json

SKILLS_LIST = [
    "python", "java", "c++", "c#", "javascript", "react", "vue", "docker", "aws", "sql",
    "node", "typescript", "angular", "go", "ruby", "php", "azure", "kubernetes", "django", "flask",
    "css", "html", "linux", "git", "machine learning", "ai", "nlp", "tensorflow", "pytorch",
    "data science", "data engineer", "devops", "cloud", "gcp", "rest", "graphql", "mobile", "ios", "android"
]
SECTORS_LIST = [
    "finance", "bank", "insurance", "health", "medical", "pharma", "biotech", "education", "e-learning",
    "e-commerce", "retail", "cloud", "blockchain", "crypto", "marketing", "communication", "media",
    "logistics", "supply chain", "automotive", "transport", "aerospace", "gaming", "video game", "cybersecurity",
    "security", "energy", "renewable", "consulting", "public", "government", "telecom", "travel", "hospitality",
    "food", "agriculture", "legal", "real estate", "HR", "startup", "SaaS", "AI", "robotics", "environment",
    "nonprofit", "manufacturing", "hardware", "semiconductor", "mobility", "sport", "music", "fashion", "luxury"
]

def extract_keywords(text, keywords):
    found = set()
    if not text:
        return []
    text = text.lower()
    for kw in keywords:
        if re.search(r'\b' + re.escape(kw.lower()) + r'\b', text):
            found.add(kw)
    return sorted(found)

def fetch_remoteok_jobs_json(raw_folder="raw"):
    url = "https://remoteok.com/api"
    headers = {'User-Agent': 'Mozilla/5.0'}
    date_str = datetime.now().strftime("%Y%m%d_%H%M")
    output_json = os.path.join(raw_folder, f"remoteok_{date_str}.json")

    try:
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, list) and len(data) > 1:
                jobs = data[1:]
                results = []
                for job in jobs:
                    txt = " ".join(str(x) for x in [
                        job.get('position',''), job.get('description',''),
                        job.get('tags',''), job.get('company','')
                    ])
                    skills = extract_keywords(txt, SKILLS_LIST)
                    sectors = extract_keywords(txt, SECTORS_LIST)
                    entry = {
                        "title": job.get("position", job.get("title", "")),
                        "company": job.get("company", ""),
                        "location": job.get("location", ""),
                        "url": job.get("url", ""),
                        "description": job.get("description", ""),
                        "tags": ", ".join(job.get("tags", [])) if isinstance(job.get("tags", []), list) else job.get("tags", ""),
                        "skills_extracted": skills,
                        "sector_extracted": sectors
                    }
                    results.append(entry)

                os.makedirs(raw_folder, exist_ok=True)
                with open(output_json, "w", encoding="utf-8") as f:
                    json.dump(results, f, ensure_ascii=False, indent=2)
                print(f"[RemoteOK] {len(results)} offres sauvegardées en JSON enrichi dans {output_json}")
                return True
            else:
                print("[RemoteOK] Pas d'offres à sauvegarder.")
                return False
        else:
            print(f"[RemoteOK] Erreur HTTP: {resp.status_code}")
            return False
    except Exception as e:
        print(f"[RemoteOK] Exception: {e}")
        return False

if __name__ == "__main__":
    fetch_remoteok_jobs_json()
