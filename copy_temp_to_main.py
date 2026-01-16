import shutil
import os

src = 'database_temp.json'
dst = 'database.json'

if not os.path.exists(src):
    print(f"Source file '{src}' does not exist.")
else:
    shutil.copyfile(src, dst)
    print(f"Copied '{src}' to '{dst}'.")
