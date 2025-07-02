import pandas as pd
import numpy as np

file = "datasets_clean/final_ready_postgres_filtered.csv"

df = pd.read_csv(file, low_memory=False)

print("\n🔍 Aperçu général :")
print(df.head(5))
print(f"\nColonnes: {df.columns.tolist()}")
print(f"Shape: {df.shape}")

print("\n--- Taux de complétion (%) ---")
print((df.notnull().mean() * 100).sort_values(ascending=False).round(2))

print("\n--- Types et nb valeurs uniques ---")
for col in df.columns:
    print(f"\nColonne: {col} ({df[col].dtype})")
    print(f" - Nb valeurs uniques: {df[col].nunique(dropna=True)}")
    print(" - Top 5:", df[col].value_counts(dropna=False).head(5).to_dict())

print("\n--- Stats numériques ---")
print(df.describe(percentiles=[.01, .05, .25, .5, .75, .95, .99]).T)

print("\n--- Doublons (title/company/industry/salaire) ---")
if all(x in df.columns for x in ['title', 'company', 'industry', 'salary_min_clean']):
    print(df.duplicated(['title','company','industry','salary_min_clean']).sum())
else:
    print("Pas assez de colonnes pour tester les doublons.")
