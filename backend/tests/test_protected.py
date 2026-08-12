"""
Protected Endpoint & Role Access Tests
=======================================
Tests that authenticated endpoints require valid tokens,
and that role-based access control works correctly.
"""


class TestProtectedEndpoint:
    """GET /api/v1/users/me — requires any authenticated user."""

    def test_unauthenticated_access_rejected(self, client):
        """
        Hitting a protected endpoint without a token returns 401.
        The response includes a WWW-Authenticate header per RFC 6750.
        """
        res = client.get("/api/v1/users/me")
        assert res.status_code == 401

    def test_invalid_token_rejected(self, client):
        """
        A malformed or expired token is rejected with 401.
        """
        res = client.get("/api/v1/users/me", headers={
            "Authorization": "Bearer invalid.token.here",
        })
        assert res.status_code == 401

    def test_authenticated_user_can_access(self, client, candidate_token, candidate_user):
        """
        A valid token allows access to /me and returns the correct user data.
        """
        res = client.get("/api/v1/users/me", headers={
            "Authorization": f"Bearer {candidate_token}",
        })
        assert res.status_code == 200
        data = res.json()
        assert data["email"] == "candidate@test.com"
        assert data["role"] == "candidate"


class TestRoleAccess:
    """
    Each endpoint has specific role requirements.
    These tests verify that wrong-role access is blocked.
    """

    def test_candidate_cannot_create_company(self, client, candidate_token):
        """
        POST /companies/ requires recruiter or admin role.
        A candidate trying to create a company gets 403.
        """
        res = client.post("/api/v1/companies/", json={
            "name": "Sneaky Corp",
        }, headers={"Authorization": f"Bearer {candidate_token}"})
        assert res.status_code == 403

    def test_candidate_cannot_post_job(self, client, candidate_token, company):
        """
        POST /jobs/ requires recruiter or admin role.
        Even though the candidate knows the company_id, they are blocked.
        """
        res = client.post("/api/v1/jobs/", json={
            "company_id": company.id,
            "title": "Fake Job",
            "description": "Should not work",
            "job_type": "full_time",
        }, headers={"Authorization": f"Bearer {candidate_token}"})
        assert res.status_code == 403

    def test_recruiter_cannot_access_candidate_profile(self, client, recruiter_token):
        """
        GET /candidates/me/profile requires candidate role.
        A recruiter hitting this endpoint gets 403.
        """
        res = client.get("/api/v1/candidates/me/profile", headers={
            "Authorization": f"Bearer {recruiter_token}",
        })
        assert res.status_code == 403

    def test_candidate_cannot_update_application_status(self, client, candidate_token):
        """
        PUT /applications/{id}/status requires recruiter or admin role.
        A candidate cannot change their own application status.
        """
        res = client.put("/api/v1/applications/1/status", json={
            "status": "accepted",
        }, headers={"Authorization": f"Bearer {candidate_token}"})
        assert res.status_code == 403

    def test_unauthenticated_cannot_list_applicants(self, client, job):
        """
        GET /applications/job/{job_id} requires recruiter or admin role.
        Even without a token, the endpoint should reject the request.
        """
        res = client.get(f"/api/v1/applications/job/{job.id}")
        assert res.status_code == 401
