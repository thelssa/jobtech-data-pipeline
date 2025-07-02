import pandas as pd

# Chemin d’entrée
infile = "D:/EFREI/jobtech/datasets_clean/final_ready_postgres.csv"
# Chemin de sortie
outfile = "D:/EFREI/jobtech/datasets_clean/final_ready_postgres_filtered.csv"

# Colonnes utiles, à garder
final_cols = [
    'title', 'company', 'industry', 'sector', 'country',
    'salary_min_clean', 'salary_max_clean',
    'skills_extracted_list'
]

# Charge le fichier
df = pd.read_csv(infile, low_memory=False)

# Filtre STRICT : toutes les colonnes clés doivent être non-nulles
mandatory = ['title', 'company', 'industry', 'salary_min_clean']
strict_df = df.dropna(subset=mandatory)

# Sélectionne seulement les colonnes d’intérêt
strict_df = strict_df[[col for col in final_cols if col in strict_df.columns]]

# Renomme les colonnes de salaire
strict_df = strict_df.rename(columns={
    'salary_min_clean': 'salary_min',
    'salary_max_clean': 'salary_max'
})

# Réordonne pour avoir la bonne structure
ordered_cols = [
    'title', 'company', 'industry', 'sector', 'country',
    'salary_min', 'salary_max', 'skills_extracted_list'
]
strict_df = strict_df[[c for c in ordered_cols if c in strict_df.columns]]

# (Optionnel) Drop les doublons exacts sur tout
strict_df = strict_df.drop_duplicates()

# Export
strict_df.to_csv(outfile, index=False)
print(f"✅ Exporté : {outfile}  |  {len(strict_df)} lignes.")
