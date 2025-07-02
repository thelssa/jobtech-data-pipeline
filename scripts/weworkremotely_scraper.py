import requests
import os
import re
import json
from datetime import datetime
from bs4 import BeautifulSoup
import time

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

def fetch_weworkremotely_jobs(raw_folder="raw"):
    url = "https://weworkremotely.com/categories/remote-programming-jobs"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/",
        "Connection": "keep-alive",
        "DNT": "1"
    }
    date_str = datetime.now().strftime("%Y%m%d_%H%M")
    output_json = os.path.join(raw_folder, f"weworkremotely_{date_str}.json")

    try:
        resp = requests.get(url, headers=headers, timeout=15)
        time.sleep(1)
        if resp.status_code != 200:
            print(f"[WeWorkRemotely] Erreur HTTP: {resp.status_code}")
            return False

        soup = BeautifulSoup(resp.text, "html.parser")
        jobs = soup.select("section.jobs article ul li:not(.view-all)")
        results = []

        for job in jobs:
            link = job.find("a", href=True)
            if not link:
                continue
            job_url = "https://weworkremotely.com" + link["href"]
            company = job.find("span", class_="company")
            title = job.find("span", class_="title")
            location = job.find("span", class_="region company")
            date = job.find("time")
            if not title or not company:
                continue

            # Requête pour la page détail de l'offre
            try:
                job_resp = requests.get(job_url, headers=headers, timeout=10)
                time.sleep(1)
                if job_resp.status_code == 200:
                    job_soup = BeautifulSoup(job_resp.text, "html.parser")
                    desc_div = job_soup.find("div", class_="listing-container")
                    description = desc_div.get_text(separator="\n").strip() if desc_div else ""
                else:
                    description = ""
            except Exception:
                description = ""

            txt = " ".join(str(x) for x in [title.text, company.text, description])
            skills = extract_keywords(txt, SKILLS_LIST)
            sectors = extract_keywords(txt, SECTORS_LIST)

            entry = {
                "title": title.text.strip(),
                "company": company.text.strip(),
                "location": location.text.strip() if location else "",
                "url": job_url,
                "date": date['datetime'] if date and date.has_attr('datetime') else "",
                "description": description[:8000],
                "skills_extracted": skills,
                "sector_extracted": sectors
            }
            results.append(entry)

        os.makedirs(raw_folder, exist_ok=True)
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"[WeWorkRemotely] {len(results)} offres sauvegardées dans {output_json}")
        return True

    except Exception as e:
        print(f"[WeWorkRemotely] Exception: {e}")
        return False

if __name__ == "__main__":
    RAW_SUBDIR = os.environ.get("RAW_SUBDIR", "raw")
    fetch_weworkremotely_jobs(RAW_SUBDIR)
