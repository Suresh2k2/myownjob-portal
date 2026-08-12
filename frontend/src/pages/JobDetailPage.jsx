import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { jobService } from "../services/jobService";
import { applicationService } from "../services/applicationService";
import Loader from "../components/Loader";
import ErrorState from "../components/ErrorState";

export default function JobDetailPage() {
  const { id } = useParams();
  const { user } = useAuth();
  const [job, setJob] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [applying, setApplying] = useState(false);
  const [coverLetter, setCoverLetter] = useState("");
  const [applySuccess, setApplySuccess] = useState(false);
  const [applyError, setApplyError] = useState("");

  const fetchJob = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await jobService.get(id);
      setJob(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to load job");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchJob();
  }, [id]);

  const handleApply = async (e) => {
    e.preventDefault();
    setApplying(true);
    setApplyError("");
    try {
      await applicationService.create({ job_id: parseInt(id), cover_letter: coverLetter || null });
      setApplySuccess(true);
    } catch (err) {
      const detail = err.response?.data?.detail;
      setApplyError(typeof detail === "string" ? detail : "Failed to apply");
    } finally {
      setApplying(false);
    }
  };

  if (loading) return <Loader message="Loading job..." />;
  if (error) return <ErrorState message={error} onRetry={fetchJob} />;
  if (!job) return null;

  return (
    <div className="page">
      <Link to="/jobs" className="back-link">&larr; Back to jobs</Link>

      <div className="job-detail">
        <h1>{job.title}</h1>
        <p className="job-detail-company">
          {job.company?.name || "Unknown Company"}
        </p>

        <div className="job-detail-meta">
          <span>{job.location || "Remote"}</span>
          <span className="job-type">{job.job_type?.replace("_", " ")}</span>
          {job.salary_min && (
            <span className="job-salary">
              ${Number(job.salary_min).toLocaleString()}
              {job.salary_max ? ` \u2013 $${Number(job.salary_max).toLocaleString()}` : ""}
            </span>
          )}
        </div>

        <div className="job-detail-description">
          <h3>Description</h3>
          <p>{job.description}</p>
        </div>

        {user?.role === "candidate" && !applySuccess && (
          <form onSubmit={handleApply} className="apply-form card">
            <h3>Apply for this job</h3>
            {applyError && <div className="alert alert-error">{applyError}</div>}
            <div className="form-group">
              <label className="form-label" htmlFor="cover-letter">Cover letter (optional)</label>
              <textarea
                id="cover-letter"
                className="form-textarea"
                value={coverLetter}
                onChange={(e) => setCoverLetter(e.target.value)}
                rows={4}
                placeholder="Tell us why you're a great fit..."
              />
            </div>
            <button type="submit" className="btn btn-primary" disabled={applying}>
              {applying ? "Submitting..." : "Apply now"}
            </button>
          </form>
        )}

        {applySuccess && (
          <div className="alert alert-success">
            Application submitted successfully. <Link to="/my-applications">View your applications</Link>
          </div>
        )}

        {user?.role === "candidate" && (
          <Link to="/my-applications" className="btn" style={{ marginTop: 16 }}>My applications</Link>
        )}
      </div>
    </div>
  );
}
