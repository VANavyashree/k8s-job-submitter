from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import time
import threading
import datetime

# Kubernetes imports
from kubernetes import client, config

app = FastAPI()

# ✅ CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Database setup
conn = sqlite3.connect("jobs.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_name TEXT,
    image TEXT,
    command TEXT,
    status TEXT,
    logs TEXT,
    start_time TEXT,
    completion_time TEXT
)
""")
conn.commit()

# -------- Kubernetes Function --------
def create_k8s_job(job_name, image, command):
    try:
        try:
            config.load_kube_config()
        except:
            return "Kubernetes not configured"

        batch_v1 = client.BatchV1Api()

        job = client.V1Job(
            metadata=client.V1ObjectMeta(name=job_name),
            spec=client.V1JobSpec(
                template=client.V1PodTemplateSpec(
                    spec=client.V1PodSpec(
                        containers=[
                            client.V1Container(
                                name="job",
                                image=image,
                                command=command.split()
                            )
                        ],
                        restart_policy="Never"
                    )
                )
            )
        )

        batch_v1.create_namespaced_job(namespace="default", body=job)

        return "Kubernetes Job Created"

    except Exception as e:
        print("K8s Error:", e)
        return "Kubernetes not available"


# -------- Simulated Execution --------
def run_job(job_id):
    print(f"Running job {job_id}")

    # Update status to Running
    cursor.execute("UPDATE jobs SET status=? WHERE id=?", ("Running", job_id))
    conn.commit()

    time.sleep(5)

    # Set completion time
    completion_time = str(datetime.datetime.now())

    cursor.execute(
        "UPDATE jobs SET status=?, logs=?, completion_time=? WHERE id=?",
        ("Completed", "Job executed successfully!", completion_time, job_id)
    )
    conn.commit()

    print(f"Completed job {job_id}")


# -------- API --------

@app.post("/jobs")
async def create_job(request: Request):
    params = dict(request.query_params)

    job_name = params.get("job_name", "default-job")
    image = params.get("image", "python:3.11")
    command = params.get("command", "echo Hello")

    print("Received:", job_name, image, command)

    # Set start time
    start_time = str(datetime.datetime.now())

    # Save to DB (UPDATED)
    cursor.execute(
        "INSERT INTO jobs (job_name, image, command, status, logs, start_time, completion_time) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (job_name, image, command, "Pending", "", start_time, "")
    )
    conn.commit()

    job_id = cursor.lastrowid

    # Try Kubernetes
    k8s_result = create_k8s_job(job_name, image, command)
    print("K8s:", k8s_result)

    # Simulate execution
    thread = threading.Thread(target=run_job, args=(job_id,))
    thread.start()

    return {"job_id": job_id, "k8s": k8s_result}


@app.get("/jobs/{job_id}")
def get_job(job_id: int):
    cursor.execute("SELECT * FROM jobs WHERE id=?", (job_id,))
    job = cursor.fetchone()

    if not job:
        return {"error": "Job not found"}

    return {
        "id": job[0],
        "job_name": job[1],
        "image": job[2],
        "command": job[3],
        "status": job[4],
        "logs": job[5],
        "start_time": job[6],
        "completion_time": job[7]
    }