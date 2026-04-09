"""Tests for the activity management system API using AAA pattern"""
import pytest


class TestRootEndpoint:
    """Tests for GET / endpoint"""

    def test_root_redirect(self, client):
        """Test that root path redirects to static HTML"""
        # Arrange - No special setup needed

        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_all_activities(self, client):
        """Test retrieving all activities returns success and data"""
        # Arrange - Activities are pre-loaded in the app

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0

    def test_activities_have_required_fields(self, client):
        """Test that each activity contains all required fields"""
        # Arrange - Get activities data

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        for activity_name, activity in activities.items():
            assert "description" in activity
            assert "schedule" in activity
            assert "max_participants" in activity
            assert "participants" in activity
            assert isinstance(activity["participants"], list)


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_success(self, client, existing_activity, sample_email):
        """Test successful signup for an existing activity"""
        # Arrange - Use existing activity and new email

        # Act
        response = client.post(
            f"/activities/{existing_activity}/signup",
            params={"email": sample_email}
        )

        # Assert
        assert response.status_code == 200
        response_data = response.json()
        assert "Signed up" in response_data["message"]
        assert sample_email in response_data["message"]

    def test_signup_adds_participant_to_activity(self, client, sample_email):
        """Test that signup actually adds the participant to the activity"""
        # Arrange
        activity_name = "Programming Class"
        initial_response = client.get("/activities")
        initial_participants = initial_response.json()[activity_name]["participants"]

        # Act
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": sample_email}
        )

        # Assert
        final_response = client.get("/activities")
        final_participants = final_response.json()[activity_name]["participants"]
        assert sample_email in final_participants
        assert len(final_participants) == len(initial_participants) + 1

    def test_signup_nonexistent_activity(self, client, nonexistent_activity, sample_email):
        """Test signup for activity that doesn't exist returns 404"""
        # Arrange - Use nonexistent activity name

        # Act
        response = client.post(
            f"/activities/{nonexistent_activity}/signup",
            params={"email": sample_email}
        )

        # Assert
        assert response.status_code == 404
        response_data = response.json()
        assert "Activity not found" in response_data["detail"]

    def test_signup_duplicate_email(self, client, existing_activity):
        """Test signing up with an email that's already registered"""
        # Arrange - Use an email that's already in the activity
        duplicate_email = "michael@mergington.edu"  # Pre-loaded in Chess Club

        # Act
        response = client.post(
            f"/activities/{existing_activity}/signup",
            params={"email": duplicate_email}
        )

        # Assert
        assert response.status_code == 400
        response_data = response.json()
        assert "already signed up" in response_data["detail"]


class TestUnregister:
    """Tests for DELETE /activities/{activity_name}/participants/{email} endpoint"""

    def test_unregister_success(self, client, sample_email):
        """Test successful unregistration from an activity"""
        # Arrange - First sign up for an activity
        activity_name = "Gym Class"
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": sample_email}
        )

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{sample_email}"
        )

        # Assert
        assert response.status_code == 200
        response_data = response.json()
        assert "Unregistered" in response_data["message"]
        assert sample_email in response_data["message"]

    def test_unregister_removes_participant_from_activity(self, client, sample_email):
        """Test that unregister actually removes the participant"""
        # Arrange
        activity_name = "Tennis Club"
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": sample_email}
        )
        initial_response = client.get("/activities")
        initial_participants = initial_response.json()[activity_name]["participants"]

        # Act
        client.delete(
            f"/activities/{activity_name}/participants/{sample_email}"
        )

        # Assert
        final_response = client.get("/activities")
        final_participants = final_response.json()[activity_name]["participants"]
        assert sample_email not in final_participants
        assert len(final_participants) == len(initial_participants) - 1

    def test_unregister_nonexistent_activity(self, client, nonexistent_activity, sample_email):
        """Test unregister from activity that doesn't exist returns 404"""
        # Arrange - Use nonexistent activity name

        # Act
        response = client.delete(
            f"/activities/{nonexistent_activity}/participants/{sample_email}"
        )

        # Assert
        assert response.status_code == 404
        response_data = response.json()
        assert "Activity not found" in response_data["detail"]

    def test_unregister_student_not_signed_up(self, client, existing_activity):
        """Test unregister for student not in the activity returns 404"""
        # Arrange - Use a unique email that's definitely not signed up
        unique_email = "never_signed_up@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{existing_activity}/participants/{unique_email}"
        )

        # Assert
        assert response.status_code == 404
        response_data = response.json()
        assert "Student not signed up" in response_data["detail"]


class TestEdgeCases:
    """Tests for edge cases and potential issues"""

    def test_signup_empty_email(self, client, existing_activity):
        """Test signup with empty email string"""
        # Arrange
        empty_email = ""

        # Act
        response = client.post(
            f"/activities/{existing_activity}/signup",
            params={"email": empty_email}
        )

        # Assert - Currently accepts empty email, but this might be a bug
        # This test documents current behavior; should be updated if validation is added
        assert response.status_code == 200

    def test_signup_special_characters_in_activity_name(self, client, sample_email):
        """Test signup with special characters in activity name"""
        # Arrange
        activity_with_spaces = "Art Studio"  # Has space

        # Act
        response = client.post(
            f"/activities/{activity_with_spaces}/signup",
            params={"email": sample_email}
        )

        # Assert
        assert response.status_code == 200

    def test_get_activities_returns_consistent_data(self, client):
        """Test that multiple calls to get activities return consistent data"""
        # Arrange - Get activities twice

        # Act
        response1 = client.get("/activities")
        response2 = client.get("/activities")

        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response1.json() == response2.json()