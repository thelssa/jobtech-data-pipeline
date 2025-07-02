# scripts/01_unify_raw.py

import os
import pandas as pd
import glob

RAW_DIR = "raw"
CLEAN_DIR = "datasets_clean"

os.makedirs(CLEAN_DIR, exist_ok=True)

def get_latest_run_folder(raw_dir):
    subdirs = [d for d in os.listdir(raw_dir) if os.path.isdir(os.path.join(raw_dir, d))]
    subdirs = sorted(subdirs, reverse=True)
    return os.path.join(raw_dir, subdirs[0]) if subdirs else None

def guess_source(filename):
    fn = filename.lower()
    if "adzuna" in fn: return "adzuna"
    if "github" in fn: return "github"
    if "remoteok" in fn: return "remoteok"
    if "glassdoor" in fn: return "glassdoor"
    if "stackoverflow" in fn: return "stackoverflow"
    return "unknown"

def load_file(filepath):
    ext = os.path.splitext(filepath)[-1].lower()
    if ext == ".json":
        try:
            df = pd.read_json(filepath)
        except Exception as e:
            print(f"Erreur JSON {filepath}: {e}")
            return None
    elif ext == ".csv":
        try:
            df = pd.read_csv(filepath)
        except Exception as e:
            print(f"Erreur CSV {filepath}: {e}")
            return None
    else:
        print(f"Format non supporté: {filepath}")
        return None
    df["source"] = guess_source(os.path.basename(filepath))
    df["filename"] = os.path.basename(filepath)
    return df

if __name__ == "__main__":
    run_folder = get_latest_run_folder(RAW_DIR)
    if not run_folder:
        print("Aucun dossier de run trouvé dans 'raw/'.")
        exit(1)
    print(f"[UNIFY] Chargement des fichiers depuis : {run_folder}")

    files = glob.glob(os.path.join(run_folder, "*"))
    all_dfs = []
    for file in files:
        print(f"  - Chargement: {os.path.basename(file)}")
        df = load_file(file)
        if df is not None:
            all_dfs.append(df)

    if not all_dfs:
        print("Aucun fichier exploitable n'a été trouvé.")
        exit(1)

    df_all = pd.concat(all_dfs, ignore_index=True, sort=False)
    print(f"\n[UNIFY] Un DataFrame de {len(df_all)} lignes au total.")
    print(df_all.head(5))

    # Sauvegarde le résultat
    df_all.to_csv(os.path.join(CLEAN_DIR, "unified_raw.csv"), index=False)
    df_all.to_parquet(os.path.join(CLEAN_DIR, "unified_raw.parquet"), index=False)
    print(f"[UNIFY] Sauvegardé dans {CLEAN_DIR}/unified_raw.csv et .parquet")
