import shutil
import datetime
import os

os.makedirs("raw", exist_ok=True)

SRC = "datasets_public/survey_results_public.csv"
date_str = datetime.datetime.now().strftime("%Y%m%d_%H%M")
dest = os.path.join("raw", f"stackoverflow_{date_str}.csv")
shutil.copy(SRC, dest)
print(f"[StackOverflow] Dataset survey copié dans {dest}")
