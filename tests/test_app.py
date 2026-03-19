import copy

import pytest
from fastapi.testclient import TestClient

from src import app

client = TestClient(app.app)

ORIGINAL_ACTIVITIES = copy.deepcopy(app.activities)

@pytest.fixture(autouse=True)
def reset_activities():
    app.activities.clear()
    app.activities.update(copy.deepcopy(ORIGINAL_ACTIVITIES))
    yield


def test_root_redirect():
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data


def test_signup_for_activity():
    response = client.post("/activities/Chess Club/signup", params={"email": "new@student.com"})
    assert response.status_code == 200
    assert "Signed up new@student.com for Chess Club" in response.json()["message"]
    assert "new@student.com" in app.activities["Chess Club"]["participants"]


def test_signup_duplicate_raises_400():
    student_email = "michael@mergington.edu"
    response = client.post("/activities/Chess Club/signup", params={"email": student_email})
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_invalid_activity_raises_404():
    response = client.post("/activities/Unknown/signup", params={"email": "x@x.com"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_from_activity():
    response = client.delete("/activities/Chess Club/signup", params={"email": "michael@mergington.edu"})
    assert response.status_code == 200
    assert "Unregistered michael@mergington.edu from Chess Club" in response.json()["message"]
    assert "michael@mergington.edu" not in app.activities["Chess Club"]["participants"]


def test_unregister_missing_participant_raises_404():
    response = client.delete("/activities/Chess Club/signup", params={"email": "notfound@mergington.edu"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"


def test_unregister_invalid_activity_raises_404():
    response = client.delete("/activities/Unknown/signup", params={"email": "x@x.com"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
