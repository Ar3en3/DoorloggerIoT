import os
from flask import Flask, render_template, jsonify
from google.cloud import bigquery
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

project_id = os.getenv("BIGQUERY_PROJECT_ID")
dataset = os.getenv("BIGQUERY_DATASET")
table = os.getenv("BIGQUERY_TABLE")
bucket_name = os.getenv("BUCKET_NAME")

table_id = f"{project_id}.{dataset}.{table}"

client = bigquery.Client(project=project_id)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/logs')
def get_logs():
    try:
        query = f"""
            SELECT image_name, person_name, timestamp
            FROM `{table_id}`
            ORDER BY timestamp DESC
            LIMIT 20
        """
        query_job = client.query(query)
        results = query_job.result()

        logs = []
        for row in results:
            logs.append({
                "image_name": row.image_name,
                "person_name": row.person_name,
                "timestamp": row.timestamp.strftime("%d/%m/%Y, %H:%M:%S"),
                "image_url": f"https://storage.googleapis.com/{bucket_name}/captures/{row.image_name}"
            })

        return jsonify(logs)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
