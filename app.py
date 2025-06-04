import os
from flask import Flask, render_template, redirect, request, session, jsonify
from dotenv import load_dotenv
import datetime
import subprocess

load_dotenv()

print("DEBUG: Raw GOOGLE_APPLICATION_CREDENTIALS =", os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))

import firebase_admin
from firebase_admin import auth, credentials as fb_credentials

firebase_key_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
if not firebase_key_path or not os.path.exists(firebase_key_path):
    raise RuntimeError(f"Missing or invalid GOOGLE_APPLICATION_CREDENTIALS: {firebase_key_path}")

fb_cred = fb_credentials.Certificate(firebase_key_path)
print("DEBUG: Loaded Firebase Admin key for project:", fb_cred.project_id)
firebase_admin.initialize_app(fb_cred)

from google.cloud import bigquery

project_id = os.getenv("BIGQUERY_PROJECT_ID")
dataset_id = os.getenv("BIGQUERY_DATASET")
table_name = os.getenv("BIGQUERY_TABLE")
bucket_name = os.getenv("BUCKET_NAME")

if not project_id:
    raise RuntimeError("Missing BIGQUERY_PROJECT_ID in environment")
print("DEBUG: BigQuery will run against project:", project_id)

bq_client = bigquery.Client(project=project_id)
table_id = f"{project_id}.{dataset_id}.{table_name}"

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")


@app.route("/")
def index():
    return redirect("/login")


@app.route("/login")
def login():
    return render_template("index.html")


@app.route("/sessionLogin", methods=["POST"])
def session_login():
    id_token = request.json.get("idToken")
    print("DEBUG: Received ID token:", id_token[:10] + "...")
    decoded_token = auth.verify_id_token(id_token)
    print("DEBUG: Decoded token 'aud':", decoded_token.get("aud"))
    session["user"] = {"email": decoded_token["email"], "uid": decoded_token["uid"]}
    return jsonify({"status": "success"})


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")

    query = f"""
        SELECT person_name, image_name, timestamp
        FROM `{table_id}`
        ORDER BY timestamp DESC
        LIMIT 10
    """
    print("DEBUG: Running BigQuery query:", query.strip().split("\n")[0] + " ...")
    query_job = bq_client.query(query)
    rows = []
    for row in query_job:
        image_url = f"https://storage.googleapis.com/{bucket_name}/captures/{row['image_name']}"
        rows.append({
            "name": row["person_name"],
            "image_url": image_url,
            "timestamp": row["timestamp"]
        })
    return render_template("dashboard.html", user=session["user"], logs=rows)


@app.route("/start_capture", methods=["POST"])
def start_capture():
    if "user" not in session:
        return redirect("/login")

    script_path = "/home/amaz/doorlogger/face_capture.py"
    log_path = "/home/amaz/doorlogger/capture.log"

    print(f"DEBUG: Attempting to launch face_capture.py at {datetime.datetime.utcnow().isoformat()}")

    with open(log_path, "a") as log_file:
        try:
            proc = subprocess.Popen(
                ["python3", script_path],
                stdout=log_file,
                stderr=subprocess.STDOUT,
                start_new_session=True
            )
            print(f"DEBUG: Started face_capture.py (pid={proc.pid}), logging to {log_path}")
        except Exception as e:
            print("ERROR: Failed to start face_capture.py:", e)
            log_file.write(f"[{datetime.datetime.utcnow().isoformat()}] ERROR: {e}\n")

    return redirect("/dashboard")


@app.route("/stop_capture", methods=["POST"])
def stop_capture():
    if "user" not in session:
        return redirect("/login")

    print(f"DEBUG: Stopping face_capture.py processes at {datetime.datetime.utcnow().isoformat()}")
    subprocess.Popen(["pkill", "-f", "face_capture.py"])
    return redirect("/dashboard")


@app.route("/graph")
def graph():
    if "user" not in session:
        return redirect("/login")
    return render_template("graph.html")


@app.route("/api/data")
def api_data():
    if "user" not in session:
        return redirect("/login")

    now = datetime.datetime.utcnow()
    past = now - datetime.timedelta(hours=1)
    query = f"""
        SELECT person_name, timestamp
        FROM `{table_id}`
        WHERE timestamp BETWEEN TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 HOUR) AND CURRENT_TIMESTAMP()
        ORDER BY timestamp ASC
    """
    print("DEBUG: Running API data BigQuery query:", query.strip().split("\n")[0] + " ...")
    query_job = bq_client.query(query)
    data = [{"time": str(row["timestamp"]), "name": row["person_name"]} for row in query_job]
    return jsonify(data)


@app.route("/api/daily-data")
def api_daily_data():
    if "user" not in session:
        return redirect("/login")

    query = f"""
        SELECT
          DATE(timestamp) AS date,
          COUNT(*) AS count
        FROM `{table_id}`
        GROUP BY date
        ORDER BY date ASC
    """
    print("DEBUG: Running daily-data BigQuery query:", query.strip().split("\n")[0] + " ...")
    query_job = bq_client.query(query)
    daily = [{"date": str(row["date"]), "count": row["count"]} for row in query_job]
    return jsonify(daily)


@app.route("/capture_logs")
def capture_logs():
    if "user" not in session:
        return redirect("/login")

    log_path = "/home/amaz/doorlogger/capture.log"
    if not os.path.exists(log_path):
        logs = []
    else:
        with open(log_path, "r") as f:
            logs = f.readlines()
    return render_template("capture_logs.html", logs=logs)


if __name__ == "__main__":
    app.run(debug=True)
