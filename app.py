"""
Quiz App - CI/CD Pipeline Academic Demonstration Project
Course: Cloud Computing and DevOps (TYCSE)
Author: DevOps Student Team
Version: v2.0.0
"""

from flask import Flask, render_template, jsonify, request
import os
import time

app = Flask(__name__)

# Application Version Identifier (Updated during Run 2 to demonstrate CD)
APP_VERSION = os.getenv("APP_VERSION", "v2.0.0")
APP_ENV = os.getenv("APP_ENV", "Production")
START_TIME = time.time()

# In-memory question bank
QUESTIONS = [
    {
        "id": 1,
        "category": "Cloud & DevOps",
        "question": "What is the primary role of a Jenkinsfile in a CI/CD pipeline?",
        "options": [
            "To define declarative or scripted pipeline stages as code",
            "To configure the host operating system kernel",
            "To serve static HTML pages to end users",
            "To manage DNS routing between cloud regions"
        ],
        "answer_index": 0,
        "explanation": "A Jenkinsfile defines the entire pipeline workflow (Build, Test, Dockerize, Deploy) as version-controlled code."
    },
    {
        "id": 2,
        "category": "Cloud & DevOps",
        "question": "Which Kubernetes resource manages a set of identical Pods and handles rolling updates?",
        "options": [
            "ConfigMap",
            "Deployment",
            "IngressRoute",
            "PersistentVolume"
        ],
        "answer_index": 1,
        "explanation": "A Deployment provides declarative updates for Pods and ReplicaSets, enabling zero-downtime rolling releases."
    },
    {
        "id": 3,
        "category": "Cloud & DevOps",
        "question": "Why is Docker lightweight compared to a traditional Virtual Machine (VM)?",
        "options": [
            "Docker emulates hardware at the BIOS level",
            "Docker containers share the host OS kernel and isolate processes",
            "Docker requires a dedicated hypervisor like VMware ESXi",
            "Containers do not use memory or CPU limits"
        ],
        "answer_index": 1,
        "explanation": "Containers share the host operating system kernel rather than running a full guest OS, drastically reducing overhead."
    },
    {
        "id": 4,
        "category": "Cloud & DevOps",
        "question": "In Minikube, which command allows you to view the exposed URL of a NodePort service?",
        "options": [
            "minikube service <service-name> --url",
            "kubectl open-browser <service>",
            "minikube forward-all-ports",
            "docker service inspect <name>"
        ],
        "answer_index": 0,
        "explanation": "The 'minikube service <service-name> --url' command queries the cluster and outputs the accessible IP:NodePort URL."
    },
    {
        "id": 5,
        "category": "Cloud & DevOps",
        "question": "Which HTTP status code should a healthy Kubernetes liveness probe endpoint return?",
        "options": [
            "200 OK (any status between 200 and 399)",
            "404 Not Found",
            "500 Internal Server Error",
            "301 Moved Permanently"
        ],
        "answer_index": 0,
        "explanation": "Kubernetes considers any HTTP response code between 200 and 399 as a success."
    }
]


@app.route("/")
def home():
    """Renders the main interactive Quiz frontend UI."""
    return render_template(
        "index.html",
        version=APP_VERSION,
        environment=APP_ENV
    )


@app.route("/api/health", methods=["GET"])
def health():
    """
    Kubernetes Liveness / Readiness health check probe endpoint.
    Used by k8s livenessProbe & readinessProbe to verify container health.
    """
    uptime_seconds = int(time.time() - START_TIME)
    return jsonify({
        "status": "UP",
        "version": APP_VERSION,
        "environment": APP_ENV,
        "uptime_seconds": uptime_seconds,
        "total_questions": len(QUESTIONS)
    }), 200


@app.route("/api/questions", methods=["GET"])
def get_questions():
    """
    Returns the list of quiz questions without exposing the correct answer indices.
    """
    sanitized = [
        {
            "id": q["id"],
            "category": q["category"],
            "question": q["question"],
            "options": q["options"]
        }
        for q in QUESTIONS
    ]
    return jsonify({"version": APP_VERSION, "questions": sanitized}), 200


@app.route("/api/submit", methods=["POST"])
def submit_quiz():
    """
    Evaluates submitted user answers, calculates score, percentage, and feedback.
    Expected JSON payload: { "answers": { "1": 0, "2": 1, ... } }
    """
    payload = request.get_json(silent=True) or {}
    user_answers = payload.get("answers", {})

    score = 0
    total = len(QUESTIONS)
    results = []

    for q in QUESTIONS:
        qid_str = str(q["id"])
        user_choice = user_answers.get(qid_str)
        is_correct = (user_choice == q["answer_index"])

        if is_correct:
            score += 1

        results.append({
            "id": q["id"],
            "question": q["question"],
            "user_choice": user_choice,
            "correct_choice": q["answer_index"],
            "is_correct": is_correct,
            "explanation": q["explanation"]
        })

    percentage = round((score / total) * 100, 1) if total > 0 else 0

    badge = "Beginner"
    if percentage >= 90:
        badge = "DevOps Champion 🏆"
    elif percentage >= 60:
        badge = "Cloud Practitioner 🚀"
    elif percentage >= 40:
        badge = "Apprentice Engineer 🛠️"

    return jsonify({
        "score": score,
        "total": total,
        "percentage": percentage,
        "badge": badge,
        "version": APP_VERSION,
        "results": results
    }), 200


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
