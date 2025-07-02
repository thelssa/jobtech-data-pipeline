import os
import sys
import shutil
import datetime
import subprocess

# === Liste des scripts à lancer ===
SCRAPERS = [
    "adzuna_scraper.py",
    "github_scraper.py",
    "remoteok_scraper.py",
    "stackoverflow_copy.py",
    "glassdoor_copy.py"
]

# === Création d'un sous-dossier horodaté dans raw/ ===
RAW_ROOT = "raw"
now_str = datetime.datetime.now().strftime("%Y%m%d_%H%M")
TARGET_DIR = os.path.join(RAW_ROOT, now_str)
os.makedirs(TARGET_DIR, exist_ok=True)

print(f"\n[RUN] Les fichiers seront enregistrés dans : {TARGET_DIR}\n")

# === Préparation des variables d'environnement pour chaque script ===
env = os.environ.copy()
env["RAW_SUBDIR"] = TARGET_DIR

for script in SCRAPERS:
    print(f"Lancement : {script}")
    try:
        # Selon Windows/Linux, python ou python3
        result = subprocess.run(
            [sys.executable, script],
            cwd="scripts",   # tous tes scripts doivent être dans scripts/
            env=env,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if result.stderr:
            print("[WARN] Erreur dans", script)
            print(result.stderr)
    except Exception as e:
        print(f"[ERREUR] {script} a échoué : {e}")

# === Déplacer les fichiers générés dans le sous-dossier horodaté ===
def move_to_target(raw_root, target_dir):
    for filename in os.listdir(raw_root):
        fpath = os.path.join(raw_root, filename)
        if os.path.isfile(fpath) and not filename.endswith(".txt"):
            # On ne bouge pas les logs, seulement les données
            shutil.move(fpath, os.path.join(target_dir, filename))

move_to_target(RAW_ROOT, TARGET_DIR)

print(f"\n✅ Tous les scrapers ont tourné ! Les fichiers sont dans {TARGET_DIR}")
