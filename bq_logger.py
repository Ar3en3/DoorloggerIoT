import os
from google.cloud import bigquery
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

project_id = os.getenv("BIGQUERY_PROJECT_ID")
dataset = os.getenv("BIGQUERY_DATASET")
table = os.getenv("BIGQUERY_TABLE")

table_id = f"{project_id}.{dataset}.{table}"

bq_client = bigquery.Client(project=project_id)

def log_face_entry(filename, name):
    row = {
        "image_name": filename,
        "person_name": name,
        "timestamp": datetime.utcnow().isoformat()
    }

    errors = bq_client.insert_rows_json(table_id, [row])
    if errors:
        print(f"[BQ ERROR] {errors}")
    else:
        print("[BQ] Logged face event.")
