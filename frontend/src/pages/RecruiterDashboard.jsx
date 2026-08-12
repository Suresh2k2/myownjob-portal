import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { companyService } from "../services/companyService";
import { jobService } from "../services/jobService";
import { applicationService } from "../services/applicationService";
import Loader from "../components/Loader";
import ErrorState from "../components/ErrorState";
import EmptyState from "../components/EmptyState";
import StatusBadge from "../components/StatusBadge";

export default function RecruiterDashboard() {
  const [company, setCompany] = useState(null);
  const [jobs, setJobs] = useState([]);
  const [selectedJob, setSelectedJob] = useState(null);
  const [applicants, setApplicants] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showCreateJob, setShowCreateJob] = useState(false);
  const [jobForm, setJobForm] = useState({
    title: "", description: "", location: "", job_type: "full_time",
    salary_min: "", salary_max: "",
  });
  const [submitting, setSubmitting] = useState(false);
  const [jobError, setJobError] = useState("");

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const companyRes = await companyService.getMy();
      const myCompany = companyRes.data;
      setCompany(myCompany);

      const jobsRes = await jobService.list();
      const myJobs = jobsRes.data.filter((j) => j.company_id === myCompany.id);
      setJobs(myJobs);
    } catch (err) {
      if (err.response?.status === 404) {
        setCompany(null);
      } else {
        setError(err.response?.data?.detail || "Failed to load dashboard");
      }
    } finally {
      setLoading(false);
    }
  };

  const fetchApplicants = async (jobId) => {
    try {
      const res = await applicationService.listForJob(jobId);
      setApplicants(res.data);
      setSelectedJob(jobId);
    } catch (err) {
      console.error(err);
    }
  };

  const handleCreateJob = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setJobError("");
    try {
      const payload = {
        ...jobForm,
        company_id: company.id,
        salary_min: jobForm.salary_min ? parseFloat(jobForm.salary_min) : null,
        salary_max: jobForm.salary_max ? parseFloat(jobForm.salary_max) : null,
      };
      await jobService.create(payload);
      setShowCreateJob(false);
      setJobForm({ title: "", description: "", location: "", job_type: "full_time", salary_min: "", salary_max: "" });
      fetchData();
    } catch (err) {
      setJobError(err.response?.data?.detail || "Failed to create job");
    } finally {
      setSubmitting(false);
    }
  };

  const handleToggleActive = async (job) => {
    try {
      await jobService.update(job.id, { is_active: !job.is_active });
      fetchData();
    } catch (err) {
      alert(err.response?.data?.detail || "Failed to update job");
    }
  };

  const handleStatusUpdate = async (applicationId, status) => {
    try {
      await applicationService.updateStatus(applicationId, status);
      if (selectedJob) fetchApplicants(selectedJob);
    } catch (err) {
      alert(err.response?.data?.detail || "Failed to update status");
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  if (loading) return <Loader message="Loading dashboard..." />;
  if (error) return <ErrorState message={error} onRetry={fetchData} />;

  return (
    <div className="dashboard">
      <h1>Recruiter Dashboard</h1>

      <section className="dashboard-section">
        <h2>Company</h2>
        {company ? (
          <div className="card">
            <p style={{ fontWeight: 600, fontSize: 16, marginBottom: 4 }}>{company.name}</p>
            <p style={{ color: "var(--color-text-secondary)", marginBottom: 4 }}>{company.description || "No description"}</p>
            {company.website && <p><a href={company.website} target="_blank" rel="noreferrer">{company.website}</a></p>}
          </div>
        ) : (
          <EmptyState
            message="Create a company to start posting jobs."
            actionLabel="Create company"
            onAction={() => window.location.href = "/company"}
          />
        )}
      </section>

      {company && (
        <section className="dashboard-section">
          <div className="section-header">
            <h2>My Jobs ({jobs.length})</h2>
            <button onClick={() => { setShowCreateJob(!showCreateJob); setJobError(""); }} className="btn btn-primary">
              {showCreateJob ? "Cancel" : "Post new job"}
            </button>
          </div>

          {showCreateJob && (
            <form onSubmit={handleCreateJob} className="card job-form" style={{ marginBottom: 16 }}>
              {jobError && <div className="alert alert-error">{jobError}</div>}
              <div className="form-group">
                <label className="form-label">Title</label>
                <input className="form-input" value={jobForm.title} onChange={(e) => setJobForm({...jobForm, title: e.target.value})} required />
              </div>
              <div className="form-group">
                <label className="form-label">Description</label>
                <textarea className="form-textarea" value={jobForm.description} onChange={(e) => setJobForm({...jobForm, description: e.target.value})} required />
              </div>
              <div className="form-group">
                <label className="form-label">Location</label>
                <input className="form-input" value={jobForm.location} onChange={(e) => setJobForm({...jobForm, location: e.target.value})} />
              </div>
              <div className="form-group">
                <label className="form-label">Job Type</label>
                <select className="form-select" value={jobForm.job_type} onChange={(e) => setJobForm({...jobForm, job_type: e.target.value})}>
                  <option value="full_time">Full Time</option>
                  <option value="part_time">Part Time</option>
                  <option value="contract">Contract</option>
                  <option value="internship">Internship</option>
                </select>
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label className="form-label">Min Salary</label>
                  <input type="number" className="form-input" value={jobForm.salary_min} onChange={(e) => setJobForm({...jobForm, salary_min: e.target.value})} />
                </div>
                <div className="form-group">
                  <label className="form-label">Max Salary</label>
                  <input type="number" className="form-input" value={jobForm.salary_max} onChange={(e) => setJobForm({...jobForm, salary_max: e.target.value})} />
                </div>
              </div>
              <button type="submit" className="btn btn-primary" disabled={submitting}>
                {submitting ? "Creating..." : "Create job"}
              </button>
            </form>
          )}

          {jobs.length === 0 ? (
            <EmptyState message="No jobs posted yet." />
          ) : (
            <div className="table-wrapper">
              <table className="table">
                <thead>
                  <tr>
                    <th>Title</th>
                    <th>Location</th>
                    <th>Type</th>
                    <th>Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {jobs.map((job) => (
                    <tr key={job.id}>
                      <td><Link to={`/jobs/${job.id}`}>{job.title}</Link></td>
                      <td>{job.location || "-"}</td>
                      <td>{job.job_type?.replace("_", " ")}</td>
                      <td>{job.is_active ? "Active" : "Closed"}</td>
                      <td className="actions-cell">
                        <button onClick={() => fetchApplicants(job.id)} className="btn btn-sm">
                          Applicants
                        </button>
                        <button onClick={() => handleToggleActive(job)} className="btn btn-sm">
                          {job.is_active ? "Close" : "Reopen"}
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      )}

      {selectedJob && (
        <section className="dashboard-section">
          <div className="section-header">
            <h2>Applicants for Job #{selectedJob}</h2>
            <button onClick={() => setSelectedJob(null)} className="btn btn-sm">Close</button>
          </div>
          {applicants.length === 0 ? (
            <EmptyState message="No applications yet." />
          ) : (
            <div className="table-wrapper">
              <table className="table">
                <thead>
                  <tr>
                    <th>Candidate</th>
                    <th>Cover Letter</th>
                    <th>Status</th>
                    <th>Applied</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {applicants.map((app) => (
                    <tr key={app.id}>
                      <td>
                        <div style={{ fontWeight: 500 }}>{app.candidate?.full_name || `#${app.candidate_id}`}</div>
                        {app.candidate?.email && <div style={{ fontSize: 13, color: "var(--color-text-muted)" }}>{app.candidate.email}</div>}
                      </td>
                      <td>{app.cover_letter ? app.cover_letter.slice(0, 50) + "..." : "-"}</td>
                      <td><StatusBadge status={app.status} /></td>
                      <td>{new Date(app.applied_at).toLocaleDateString()}</td>
                      <td className="actions-cell">
                        {app.status === "pending" && (
                          <>
                            <button onClick={() => handleStatusUpdate(app.id, "accepted")} className="btn btn-sm btn-success">
                              Accept
                            </button>
                            <button onClick={() => handleStatusUpdate(app.id, "shortlisted")} className="btn btn-sm">
                              Shortlist
                            </button>
                            <button onClick={() => handleStatusUpdate(app.id, "rejected")} className="btn btn-sm btn-danger">
                              Reject
                            </button>
                          </>
                        )}
                        {app.status === "reviewed" && (
                          <>
                            <button onClick={() => handleStatusUpdate(app.id, "accepted")} className="btn btn-sm btn-success">
                              Accept
                            </button>
                            <button onClick={() => handleStatusUpdate(app.id, "shortlisted")} className="btn btn-sm">
                              Shortlist
                            </button>
                            <button onClick={() => handleStatusUpdate(app.id, "rejected")} className="btn btn-sm btn-danger">
                              Reject
                            </button>
                          </>
                        )}
                        {app.status === "shortlisted" && (
                          <>
                            <button onClick={() => handleStatusUpdate(app.id, "accepted")} className="btn btn-sm btn-success">
                              Accept
                            </button>
                            <button onClick={() => handleStatusUpdate(app.id, "rejected")} className="btn btn-sm btn-danger">
                              Reject
                            </button>
                          </>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      )}
    </div>
  );
}
