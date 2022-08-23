import os

db_dir = "data"
UPLOAD_FOLDER = 'uploads'
dblocation = os.path.join(db_dir,  "labels.sqlite")
os.makedirs(db_dir, exist_ok=True)
storage_location = "static/storage"