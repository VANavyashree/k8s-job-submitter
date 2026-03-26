# Kubernetes Job Submitter

A web application to submit and monitor batch jobs on Kubernetes.

## Features
- Submit jobs with container image and command
- Track job status (Pending → Running → Completed)
- View execution logs
- Backend integrated with Kubernetes Python client
- SQLite database for job tracking

## Tech Stack
- Frontend: HTML, CSS, JavaScript
- Backend: FastAPI (Python)
- Database: SQLite
- Kubernetes: Python client

## How it works
User submits job → Backend processes request → Kubernetes Job is created → Status and logs are tracked → UI displays updates

## Note
Kubernetes execution is simulated locally due to environment constraints, but full integration logic is implemented.

## Architecture Diagram

![Architecture](images/architecture.png)

## UI Screenshot

![UI](images/ui.png)