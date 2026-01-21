"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
    from app import activities
    # Store original state
    original = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Join the team and compete in local tournaments",
            "schedule": "Tuesdays and Thursdays, 4:30 PM - 6:00 PM",
            "max_participants": 15,
            "participants": []
        },
        "Soccer Club": {
            "description": "Practice soccer skills and play matches",
            "schedule": "Mondays and Wednesdays, 3:00 PM - 5:00 PM",
            "max_participants": 20,
            "participants": []
        },
        "Art Club": {
            "description": "Explore various art techniques and create projects",
            "schedule": "Fridays, 3:00 PM - 5:00 PM",
            "max_participants": 15,
            "participants": []
        },
        "Drama Club": {
            "description": "Participate in theater productions and improve acting skills",
            "schedule": "Tuesdays, 5:00 PM - 7:00 PM",
            "max_participants": 20,
            "participants": []
        },
        "Debate Team": {
            "description": "Engage in debates and improve public speaking skills",
            "schedule": "Wednesdays, 4:00 PM - 6:00 PM",
            "max_participants": 12,
            "participants": []
        },
        "Math Club": {
            "description": "Solve challenging math problems and compete in contests",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 10,
            "participants": []
        }
    }
    
    # Clear current activities
    activities.clear()
    # Restore original
    activities.update(original)
    yield
    # Reset after test
    activities.clear()
    activities.update(original)


# Tests for GET /activities
class TestGetActivities:
    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data

    def test_get_activities_contains_required_fields(self, client, reset_activities):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data


# Tests for POST /activities/{activity_name}/signup
class TestSignup:
    def test_signup_new_student(self, client, reset_activities):
        """Test signing up a new student for an activity"""
        response = client.post(
            "/activities/Basketball Team/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "newstudent@mergington.edu" in data["message"]
        
        # Verify student was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "newstudent@mergington.edu" in activities_data["Basketball Team"]["participants"]

    def test_signup_nonexistent_activity(self, client, reset_activities):
        """Test signing up for a non-existent activity"""
        response = client.post(
            "/activities/Fake Activity/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_duplicate_student(self, client, reset_activities):
        """Test that a student cannot sign up twice"""
        response = client.post(
            "/activities/Chess Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_multiple_activities(self, client, reset_activities):
        """Test that a student can sign up for multiple activities"""
        email = "versatile@mergington.edu"
        
        # Sign up for first activity
        response1 = client.post(
            f"/activities/Chess Club/signup?email={email}"
        )
        assert response1.status_code == 200
        
        # Sign up for second activity
        response2 = client.post(
            f"/activities/Soccer Club/signup?email={email}"
        )
        assert response2.status_code == 200
        
        # Verify in both activities
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data["Chess Club"]["participants"]
        assert email in activities_data["Soccer Club"]["participants"]


# Tests for DELETE /activities/{activity_name}/unregister
class TestUnregister:
    def test_unregister_student(self, client, reset_activities):
        """Test unregistering a student from an activity"""
        response = client.delete(
            "/activities/Chess Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "michael@mergington.edu" in data["message"]
        
        # Verify student was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "michael@mergington.edu" not in activities_data["Chess Club"]["participants"]

    def test_unregister_nonexistent_activity(self, client, reset_activities):
        """Test unregistering from a non-existent activity"""
        response = client.delete(
            "/activities/Fake Activity/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_unregister_not_registered_student(self, client, reset_activities):
        """Test unregistering a student who isn't registered"""
        response = client.delete(
            "/activities/Basketball Team/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"]

    def test_unregister_all_participants(self, client, reset_activities):
        """Test unregistering all participants from an activity"""
        # Get current participants
        activities_response = client.get("/activities")
        chess_participants = activities_response.json()["Chess Club"]["participants"].copy()
        
        # Unregister each participant
        for email in chess_participants:
            response = client.delete(
                f"/activities/Chess Club/unregister?email={email}"
            )
            assert response.status_code == 200
        
        # Verify all were removed
        activities_response = client.get("/activities")
        assert len(activities_response.json()["Chess Club"]["participants"]) == 0


# Integration tests
class TestIntegration:
    def test_signup_then_unregister(self, client, reset_activities):
        """Test signing up and then unregistering"""
        email = "test@mergington.edu"
        
        # Sign up
        signup_response = client.post(
            f"/activities/Soccer Club/signup?email={email}"
        )
        assert signup_response.status_code == 200
        
        # Verify signup
        activities_response = client.get("/activities")
        assert email in activities_response.json()["Soccer Club"]["participants"]
        
        # Unregister
        unregister_response = client.delete(
            f"/activities/Soccer Club/unregister?email={email}"
        )
        assert unregister_response.status_code == 200
        
        # Verify unregister
        activities_response = client.get("/activities")
        assert email not in activities_response.json()["Soccer Club"]["participants"]
