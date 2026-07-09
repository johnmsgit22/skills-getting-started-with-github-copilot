from fastapi.testclient import TestClient

from src import app as app_module


def test_root_redirects_to_static_index():
    # Arrange
    client = TestClient(app_module.app)

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_seed_data():
    # Arrange
    client = TestClient(app_module.app)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert "Chess Club" in payload
    assert payload["Chess Club"]["max_participants"] == 12
    assert "michael@mergington.edu" in payload["Chess Club"]["participants"]


def test_signup_for_activity_adds_participant():
    # Arrange
    client = TestClient(app_module.app)
    activity_name = "Chess Club"
    original_participants = list(app_module.activities[activity_name]["participants"])

    try:
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": "newstudent@mergington.edu"},
        )

        # Assert
        assert response.status_code == 200
        assert response.json() == {
            "message": f"Signed up newstudent@mergington.edu for {activity_name}"
        }
        assert "newstudent@mergington.edu" in app_module.activities[activity_name]["participants"]
    finally:
        app_module.activities[activity_name]["participants"] = original_participants


def test_signup_for_unknown_activity_returns_not_found():
    # Arrange
    client = TestClient(app_module.app)

    # Act
    response = client.post(
        "/activities/Nonexistent/signup",
        params={"email": "student@mergington.edu"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}
