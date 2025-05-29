import os
from google.cloud import bigquery
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def log_face_entry(image_name):

    project_id = os.getenv("BQ_PROJECT_ID", "door-logger-pi")
    dataset_id = os.getenv("BQ_DATASET_ID", "doorlogger_logs")
    table_id = os.getenv("BQ_TABLE_ID", "face_events")

    full_table_id = f"{project_id}.{dataset_id}.{table_id}"

    client = bigquery.Client(project=project_id)

    row = {
        "image_name": image_name,
        "timestamp": datetime.utcnow().isoformat()
    }

    errors = client.insert_rows_json(full_table_id, [row])

    if errors:
        print("Errors:", errors)
    else:
        print("Row inserted.")
