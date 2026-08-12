"""
Application Tests
=================
Tests for duplicate applications, candidate privacy,
and recruiter status update enforcement.
"""
from tests.conftest import get_token, create_user
from app.models.application import Application, ApplicationStatus
from app.models.user import UserRole


class TestDuplicateApplication:
    """POST /api/v1/applications/"""

    def test_cannot_apply_twice_to_same_job(
        self, client, candidate_token, candidate_profile, job
    ):
        """
        A candidate cannot submit two applications for the same job.
        The UNIQUE constraint on (candidate_id, job_id) enforces this,
        and the endpoint returns 409 Conflict.
        """
        payload = {"job_id": job.id, "cover_letter": "I'm interested"}
        headers = {"Authorization": f"Bearer {candidate_token}"}

        res1 = client.post("/api/v1/applications/", json=payload, headers=headers)
        assert res1.status_code == 201

        res2 = client.post("/api/v1/applications/", json=payload, headers=headers)
        assert res2.status_code == 409
        assert res2.json()["detail"] == "You have already applied to this job"

    def test_cannot_apply_to_closed_job(
        self, client, candidate_token, candidate_profile, closed_job
    ):
        """
        Applications to inactive (closed) jobs are rejected with 404.
        The query filters on `is_active == True`.
        """
        res = client.post("/api/v1/applications/", json={
            "job_id": closed_job.id,
        }, headers={"Authorization": f"Bearer {candidate_token}"})
        assert res.status_code == 404

    def test_apply_without_profile_fails(self, client, candidate_token, job):
        """
        A candidate who hasn't created a profile cannot apply.
        The endpoint requires a candidate_profile row first.
        """
        res = client.post("/api/v1/applications/", json={
            "job_id": job.id,
        }, headers={"Authorization": f"Bearer {candidate_token}"})
        assert res.status_code == 400
        assert "profile" in res.json()["detail"].lower()


class TestCandidatePrivacy:
    """
    Candidates cannot see other candidates' data.
    Recruiters can only see applicants for their own company's jobs.
    """

    def test_cannot_view_other_candidates_profile(
        self, client, candidate_token, candidate_profile, other_profile
    ):
        """
        GET /candidates/me/profile only returns the authenticated
        user's own profile, never someone else's.
        """
        res = client.get("/api/v1/candidates/me/profile", headers={
            "Authorization": f"Bearer {candidate_token}",
        })
        assert res.status_code == 200
        data = res.json()
        # Should be the candidate's own profile (from fixture), not "John Smith"
        assert data["full_name"] == "Jane Doe"

    def test_recruiter_cannot_see_other_companys_applicants(
        self, client, recruiter_token, company, job, candidate_profile, db
    ):
        """
        A recruiter can only view applicants for their own company's jobs.
        When a second company's job has applicants, the first recruiter
        can't see them.
        """
        from app.models.company import Company
        from app.models.job import Job, JobType

        # Create a second recruiter with their own company
        recruiter2 = create_user(db, email="r2@test.com", role="recruiter")
        co2 = Company(owner_id=recruiter2.id, name="Other Corp")
        db.add(co2)
        db.commit()
        db.refresh(co2)

        # Create a job in the second company
        job2 = Job(company_id=co2.id, title="Other Job", description="X", job_type=JobType.full_time)
        db.add(job2)
        db.commit()
        db.refresh(job2)

        # Create an application for the second company's job
        app = Application(candidate_id=candidate_profile.id, job_id=job2.id)
        db.add(app)
        db.commit()

        # The first recruiter (owner of 'company') cannot see applicants
        # for job2 (which belongs to co2).
        res = client.get(f"/api/v1/applications/job/{job2.id}", headers={
            "Authorization": f"Bearer {recruiter_token}",
        })
        assert res.status_code == 403


class TestRecruiterStatusUpdates:
    """PUT /api/v1/applications/{id}/status"""

    def test_can_shortlist_pending_application(
        self, client, recruiter_token, candidate_profile, job
    ):
        """
        A recruiter can move a 'pending' application to 'shortlisted'.
        This is a valid forward transition.
        """
        # Create application
        app_res = client.post("/api/v1/applications/", json={
            "job_id": job.id,
        }, headers={"Authorization": f"Bearer {get_token(candidate_profile.user_id)}"})
        assert app_res.status_code == 201
        app_id = app_res.json()["id"]

        # Shortlist it
        res = client.put(f"/api/v1/applications/{app_id}/status", json={
            "status": "shortlisted",
        }, headers={"Authorization": f"Bearer {recruiter_token}"})
        assert res.status_code == 200
        assert res.json()["status"] == "shortlisted"

    def test_can_reject_pending_application(
        self, client, recruiter_token, candidate_profile, job
    ):
        """
        A recruiter can reject a pending application directly.
        'pending -> rejected' is a valid transition.
        """
        app_res = client.post("/api/v1/applications/", json={
            "job_id": job.id,
        }, headers={"Authorization": f"Bearer {get_token(candidate_profile.user_id)}"})
        app_id = app_res.json()["id"]

        res = client.put(f"/api/v1/applications/{app_id}/status", json={
            "status": "rejected",
        }, headers={"Authorization": f"Bearer {recruiter_token}"})
        assert res.status_code == 200
        assert res.json()["status"] == "rejected"

    def test_cannot_move_rejected_back_to_pending(
        self, client, recruiter_token, candidate_profile, job, db
    ):
        """
        Once an application is 'rejected', it cannot be moved back
        to 'pending'. The state machine prevents backward transitions.
        """
        # Create and reject an application directly via DB
        application = Application(
            candidate_id=candidate_profile.id,
            job_id=job.id,
            status=ApplicationStatus.rejected,
        )
        db.add(application)
        db.commit()
        db.refresh(application)

        # Try to move it back to pending
        res = client.put(f"/api/v1/applications/{application.id}/status", json={
            "status": "pending",
        }, headers={"Authorization": f"Bearer {recruiter_token}"})
        assert res.status_code == 400
        assert "Cannot transition" in res.json()["detail"]

    def test_cannot_move_accepted_back_to_shortlisted(
        self, client, recruiter_token, candidate_profile, job, db
    ):
        """
        An 'accepted' application is terminal — no further transitions.
        """
        application = Application(
            candidate_id=candidate_profile.id,
            job_id=job.id,
            status=ApplicationStatus.accepted,
        )
        db.add(application)
        db.commit()
        db.refresh(application)

        res = client.put(f"/api/v1/applications/{application.id}/status", json={
            "status": "shortlisted",
        }, headers={"Authorization": f"Bearer {recruiter_token}"})
        assert res.status_code == 400

    def test_cannot_skip_to_accepted_from_pending(
        self, client, recruiter_token, candidate_profile, job
    ):
        """
        You cannot jump from 'pending' straight to 'accepted'.
        Must go through 'reviewed' or 'shortlisted' first.
        """
        app_res = client.post("/api/v1/applications/", json={
            "job_id": job.id,
        }, headers={"Authorization": f"Bearer {get_token(candidate_profile.user_id)}"})
        app_id = app_res.json()["id"]

        res = client.put(f"/api/v1/applications/{app_id}/status", json={
            "status": "accepted",
        }, headers={"Authorization": f"Bearer {recruiter_token}"})
        assert res.status_code == 400
        assert "Cannot transition" in res.json()["detail"]

    def test_recruiter_cannot_update_other_companys_application(
        self, client, candidate_profile, job, db
    ):
        """
        A recruiter who doesn't own the job's company cannot
        update application status. Returns 403.
        """
        other_recruiter = create_user(db, email="other-recruiter@test.com", role=UserRole.recruiter)
        other_recruiter_token = get_token(other_recruiter.id)

        # Create application
        app_res = client.post("/api/v1/applications/", json={
            "job_id": job.id,
        }, headers={"Authorization": f"Bearer {get_token(candidate_profile.user_id)}"})
        app_id = app_res.json()["id"]

        # Try to update from a recruiter who doesn't own the company
        res = client.put(f"/api/v1/applications/{app_id}/status", json={
            "status": "reviewed",
        }, headers={"Authorization": f"Bearer {other_recruiter_token}"})
        assert res.status_code == 403
