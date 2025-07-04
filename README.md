# JobTech – Pipeline Data & API Django

Projet: collecte, nettoyage, stockage et exposition d’offres d’emploi tech, multi-sources, exploitable dans Django/Postgres avec API REST sécurisée.

## 1. Pipeline & Stack

- **Collecte multi-source** : Adzuna, Glassdoor, StackOverflow, GitHub
- **Nettoyage/harmonisation** : scripts Python pour unifier formats, secteurs, salaires, pays, skills, etc.
- **Stockage** : PostgreSQL (modèle `JobOffer`)
- **Exposition** : API REST Django sécurisée (token)

## 2. Structure de la donnée clean (CSV final)

| company | country | sector | title | salary_min | salary_max | skills |
|---------|---------|--------|-------|------------|------------|--------|
| ...     | ...     | ...    | ...   | ...        | ...        | ...    |

- **skills** : stocké comme JSON (exemple : `["python", "django"]`)
- **salary_min/max** : float (ou vide)
- **country/sector/title/company** : string

## 3. Mise en place

```bash
python -m venv venv
pip install -r requirements.txt


## 4. Migration & lancement serveur

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

## 5. Importer les données cleans

Place ton fichier `final_clean_ready.csv` dans `datasets_clean/` puis :

```bash
python jobapi/import_csv.py
```

## 6. Tester l’API

### Authentification (obtenir un token)

```bash
curl -X POST -d "username=TONUSERNAME&password=TONMOTDEPASSE" http://localhost:8000/api-token-auth/
```

*Récupère le token dans la réponse, puis utilise-le dans l’API.*

### Exemple de requête API filtrée

```bash
curl.exe -H "Authorization: Token VOTRE_TOKEN" "http://localhost:8000/api/v1/salary-daily/?country=Belgium&skill=python"
```

**Réponse attendue :**

```json
{"date":"2025-07-04","count":10,"median":51000.0,"distribution":[5,2,1,0,1,0,0,0,0,1]}
```

## 7. Interface d’admin

Accès à `/admin/` pour inspection directe des offres.

````
