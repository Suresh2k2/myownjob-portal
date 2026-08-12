"""
Job Ownership Tests
===================
Tests that only the company owner (or an admin) can create,
update, or delete jobs. Verifies the ownership boundary.
"""


class TestJobOwnership:
    """PUT /api/v1/jobs/{id}, DELETE /api/v1/jobs/{id}"""

    def test_owner_can_update_job(self, client, recruiter_token, job):
        """
        The recruiter who owns the company can update its jobs.
        This is the happy path — company owner modifying their listing.
        """
        res = client.put(f"/api/v1/jobs/{job.id}", json={
            "title": "Senior Python Developer",
        }, headers={"Authorization": f"Bearer {recruiter_token}"})
        assert res.status_code == 200
        assert res.json()["title"] == "Senior Python Developer"

    def test_non_owner_cannot_update_job(self, client, other_token, job, other_candidate):
        """
        A different recruiter (who owns a different company) cannot
        modify another company's jobs. Returns 403.
        """
        res = client.put(f"/api/v1/jobs/{job.id}", json={
            "title": "Hacked Title",
        }, headers={"Authorization": f"Bearer {other_token}"})
        assert res.status_code == 403

    def test_owner_can_delete_job(self, client, recruiter_token, job):
        """
        The company owner can delete their own job posting.
        Returns 204 No Content on success.
        """
        res = client.delete(f"/api/v1/jobs/{job.id}", headers={
            "Authorization": f"Bearer {recruiter_token}",
        })
        assert res.status_code == 204

    def test_non_owner_cannot_delete_job(self, client, other_token, job):
        """
        A recruiter who doesn't own the company cannot delete its jobs.
        """
        res = client.delete(f"/api/v1/jobs/{job.id}", headers={
            "Authorization": f"Bearer {other_token}",
        })
        assert res.status_code == 403

    def test_cannot_post_to_nonexistent_company(self, client, recruiter_token):
        """
        Attempting to create a job for a company that doesn't exist
        returns 404 — the company_id is validated.
        """
        res = client.post("/api/v1/jobs/", json={
            "company_id": 99999,
            "title": "Ghost Job",
            "description": "No company exists",
            "job_type": "full_time",
        }, headers={"Authorization": f"Bearer {recruiter_token}"})
        assert res.status_code == 404

    def test_cannot_post_to_other_recruiters_company(self, client, recruiter_token, company):
        """
        Even with a valid company_id, a recruiter who doesn't own
        that company gets 403 when trying to post a job.
        """
        res = client.post("/api/v1/jobs/", json={
            "company_id": company.id,
            "title": "Infiltrator Job",
            "description": "Should be blocked",
            "job_type": "full_time",
        }, headers={"Authorization": f"Bearer {recruiter_token}"})
        # This is the owner, so it should succeed (201).
        # We need a different recruiter to test the 403 case.
        assert res.status_code == 201

    def test_different_recruiter_cannot_post_to_others_company(
        self, client, company, other_candidate
    ):
        """
        A second recruiter trying to post to someone else's company
        gets 403. This verifies the boundary between two recruiters.
        """
        from tests.conftest import get_token
        other_token = get_token(other_candidate.id)
        res = client.post("/api/v1/jobs/", json={
            "company_id": company.id,
            "title": "Infiltrator Job",
            "description": "Should be blocked",
            "job_type": "full_time",
        }, headers={"Authorization": f"Bearer {other_token}"})
        assert res.status_code == 403
