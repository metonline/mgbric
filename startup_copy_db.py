import os
import shutil

main_db = 'database.json'
temp_db = 'database_temp.json'

def is_empty_or_missing(path):
    if not os.path.exists(path):
        return True
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            return content == '' or content == '[]' or content == '{}'
    except Exception:
        return True

if is_empty_or_missing(main_db):
    if os.path.exists(temp_db):
        shutil.copyfile(temp_db, main_db)
        print(f"Copied '{temp_db}' to '{main_db}'.")
    else:
        print(f"Temp database '{temp_db}' not found. No action taken.")
else:
    print(f"'{main_db}' already exists and is not empty.")