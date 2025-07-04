import shutil
import datetime
import os

os.makedirs("raw", exist_ok=True)

SRC = "datasets_public/survey_results_public.csv"
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
file_path = os.path.join(parent_dir, SRC)
date_str = datetime.datetime.now().strftime("%Y%m%d_%H%M")
dest = os.path.join("raw", f"stackoverflow_{date_str}.csv")
shutil.copy(file_path, dest)
print(f"[StackOverflow] Dataset survey copié dans {dest}")