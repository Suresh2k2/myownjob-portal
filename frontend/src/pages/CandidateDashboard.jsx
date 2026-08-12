import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { candidateService } from "../services/candidateService";
import { applicationService } from "../services/applicationService";
import { Link } from "react-router-dom";
import Loader from "../components/Loader";
import ErrorState from "../components/ErrorState";
import EmptyState from "../components/EmptyState";
import StatusBadge from "../components/StatusBadge";

export default function CandidateDashboard() {
  const { user } = useAuth();
  const [profile, setProfile] = useState(null);
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [profileRes, appsRes] = await Promise.all([
        candidateService.getProfile().catch(() => null),
        applicationService.listMy(),
      ]);
      if (profileRes) setProfile(profileRes.data);
      setApplications(appsRes.data);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to load dashboard");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  if (loading) return <Loader message="Loading dashboard..." />;
  if (error) return <ErrorState message={error} onRetry={fetchData} />;

  return (
    <div className="dashboard">
      <h1>Candidate Dashboard</h1>

      <section className="dashboard-section">
        <h2>Profile</h2>
        {profile ? (
          <div className="card">
            <p><strong>Name:</strong> {profile.full_name}</p>
            <p><strong>Phone:</strong> {profile.phone || "Not provided"}</p>
            <p><strong>Skills:</strong> {profile.skills || "Not provided"}</p>
            <p><strong>Resume:</strong> {profile.resume_url ? <a href={profile.resume_url} target="_blank" rel="noreferrer">View</a> : "Not uploaded"}</p>
            <div style={{ marginTop: 12 }}>
              <Link to="/profile" className="btn btn-sm">Edit profile</Link>
            </div>
          </div>
        ) : (
          <EmptyState
            message="No profile yet. Create one to start applying."
            actionLabel="Create profile"
            onAction={() => window.location.href = "/profile"}
          />
        )}
      </section>

      <section className="dashboard-section">
        <h2>My Applications ({applications.length})</h2>
        {applications.length === 0 ? (
          <EmptyState
            message="You haven't applied to any jobs yet."
            actionLabel="Browse jobs"
            onAction={() => window.location.href = "/jobs"}
          />
        ) : (
          <div className="table-wrapper">
            <table className="table">
              <thead>
                <tr>
                  <th>Job</th>
                  <th>Company</th>
                  <th>Location</th>
                  <th>Status</th>
                  <th>Applied</th>
                </tr>
              </thead>
              <tbody>
                {applications.map((app) => (
                  <tr key={app.id}>
                    <td>
                      <Link to={`/jobs/${app.job_id}`}>
                        {app.job?.title || `Job #${app.job_id}`}
                      </Link>
                    </td>
                    <td>{app.job?.company?.name || "-"}</td>
                    <td>{app.job?.location || "-"}</td>
                    <td><StatusBadge status={app.status} /></td>
                    <td>{new Date(app.applied_at).toLocaleDateString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}
