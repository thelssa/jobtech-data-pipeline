import requests
import datetime
import os
import json
import time

# --- Configuration du token GitHub ---
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
RAW_DIR = os.path.join(parent_dir, 'raw')
os.makedirs(RAW_DIR, exist_ok=True)

TECHNOS = [
    "python",          # language
    "java",            # language
    "typescript",      # language
    "react",           # topic
    "data-science",    # topic
    "machine-learning", # topic
    "django",           # topic
    "nlp"               # topic
]
PER_PAGE = 50
PAGES = 2

date_str = datetime.datetime.now().strftime("%Y%m%d_%H%M")

def build_query(techno):
    """Retourne le query adapté selon techno est un language ou un topic"""
    language_based = {"python", "java", "typescript"}
    if techno.lower() in language_based:
        return f"language:{techno}"
    else:
        return f"topic:{techno}"

def safe_github_get(url, headers, max_retries=2):
    """Tente de récupérer l'URL, gère la limite d'API en attendant si besoin"""
    for attempt in range(max_retries):
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response
        elif response.status_code == 403 and "rate limit" in response.text.lower():
            reset_time = 60  # Attendre 1 minute (peut être ajusté)
            print(f"  ! Erreur API GitHub : {response.status_code} - {response.text[:80]}...")
            print(f"    > Limite atteinte, pause de {reset_time} secondes puis nouvel essai...")
            time.sleep(reset_time)
        else:
            print(f"  ! Erreur API GitHub : {response.status_code} - {response.text[:80]}...")
            break
    return response  # retour même s'il y a erreur après plusieurs essais

for techno in TECHNOS:
    all_repos = []
    for page in range(1, PAGES+1):
        query = build_query(techno)
        url = (
            f"https://api.github.com/search/repositories"
            f"?q={query}&sort=stars&order=desc&per_page={PER_PAGE}&page={page}"
        )
        print(f"[GitHub] {techno} page {page} : {url}")
        response = safe_github_get(url, HEADERS)
        if response.status_code == 200:
            data = response.json()
            all_repos.extend(data.get("items", []))
        else:
            print(f"  ! Erreur API GitHub : {response.status_code} - {response.text[:80]}...")
        time.sleep(2)

    output_data = [
        {
            "name": repo["name"],
            "full_name": repo["full_name"],
            "url": repo["html_url"],
            "description": repo.get("description"),
            "stars": repo.get("stargazers_count"),
            "forks": repo.get("forks_count"),
            "language": repo.get("language"),
            "created_at": repo.get("created_at"),
            "updated_at": repo.get("updated_at"),
            "topics": repo.get("topics", []),
            "owner": repo["owner"]["login"]
        }
        for repo in all_repos
    ]

    output_file = os.path.join("raw", f"github_{techno}_{date_str}.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"[GitHub] {len(output_data)} dépôts '{techno}' sauvegardés dans {output_file}")

print("\n[GitHub] Collecte terminée.")
