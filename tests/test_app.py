import os
import sys
import pytest

# Add parent directory to sys.path so 'app' can always be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app, QUESTIONS

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_health_endpoint(client):
    """Verify Kubernetes health probe returns HTTP 200 and status UP."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "UP"
    assert "version" in data
    assert "uptime_seconds" in data

def test_home_page_renders(client):
    """Verify main index UI responds with status 200 and HTML content."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"CloudOps Quiz Portal" in response.data or b"Quiz" in response.data

def test_get_questions_sanitized(client):
    """Verify question endpoint does not leak answer_index to client."""
    response = client.get("/api/questions")
    assert response.status_code == 200
    data = response.get_json()
    assert "questions" in data
    assert len(data["questions"]) == len(QUESTIONS)
    for q in data["questions"]:
        assert "answer_index" not in q
        assert "question" in q
        assert len(q["options"]) > 0

def test_quiz_submission_perfect_score(client):
    """Test full score evaluation when all correct choices are submitted."""
    answers = {str(q["id"]): q["answer_index"] for q in QUESTIONS}
    response = client.post("/api/submit", json={"answers": answers})
    assert response.status_code == 200
    data = response.get_json()
    assert data["score"] == len(QUESTIONS)
    assert data["percentage"] == 100.0
    assert "DevOps Champion" in data["badge"]

def test_quiz_submission_zero_score(client):
    """Test calculation when incorrect answers are submitted."""
    answers = {str(q["id"]): (q["answer_index"] + 1) % len(q["options"]) for q in QUESTIONS}
    response = client.post("/api/submit", json={"answers": answers})
    assert response.status_code == 200
    data = response.get_json()
    assert data["score"] == 0
    assert data["percentage"] == 0.0
