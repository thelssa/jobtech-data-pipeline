@echo off
cd /d %~dp0
call venv\Scripts\activate
python scripts\run_all_scrapers.py
