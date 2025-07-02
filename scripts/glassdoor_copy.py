import shutil
import datetime
import os

os.makedirs("raw", exist_ok=True)

SRC = "datasets_public/glassdoor_jobs.csv"
date_str = datetime.datetime.now().strftime("%Y%m%d_%H%M")
dest = os.path.join("raw", f"glassdoor_{date_str}.csv")
shutil.copy(SRC, dest)
print(f"[Glassdoor] Dataset copié dans {dest}")
