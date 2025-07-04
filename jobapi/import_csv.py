import csv
import os
import django
import sys
import json

sys.path.append(os.path.dirname(os.path.abspath(os.path.join(__file__, '..'))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jobtech_api.settings')
django.setup()

from jobapi.models import JobOffer

csv_path = "datasets_clean/final_clean_ready.csv"

with open(csv_path, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    count = 0
    for row in reader:
        skills = json.loads(row.get('skills') or "[]")
        obj = JobOffer(
            title=row.get('title') or None,
            company=row.get('company') or None,
            country=row.get('country') or None,
            sector=row.get('sector') or None,
            salary_min=float(row['salary_min']) if row.get('salary_min') else None,
            salary_max=float(row['salary_max']) if row.get('salary_max') else None,
            skills=skills,
        )
        obj.save()
        count += 1
    print(f"Import terminé : {count} offres ajoutées.")
