import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { jobService } from "../services/jobService";
import Loader from "../components/Loader";
import ErrorState from "../components/ErrorState";
import EmptyState from "../components/EmptyState";

export default function JobsPage() {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [search, setSearch] = useState("");
  const [location, setLocation] = useState("");
  const [jobType, setJobType] = useState("");

  const fetchJobs = async () => {
    setLoading(true);
    setError(null);
    try {
      const params = {};
      if (search) params.search = search;
      if (location) params.location = location;
      if (jobType) params.job_type = jobType;
      const res = await jobService.list(params);
      setJobs(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to load jobs");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchJobs();
  }, []);

  const handleSearch = (e) => {
    e.preventDefault();
    fetchJobs();
  };

  if (loading) return <Loader message="Loading jobs..." />;
  if (error) return <ErrorState message={error} onRetry={fetchJobs} />;

  return (
    <div className="page">
      <h1>Jobs</h1>

      <form onSubmit={handleSearch} className="search-bar">
        <div className="form-group">
          <input
            type="text"
            className="form-input"
            placeholder="Search by title or skill..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <div className="form-group">
          <input
            type="text"
            className="form-input"
            placeholder="Location"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
          />
        </div>
        <div className="form-group">
          <select
            className="form-select"
            value={jobType}
            onChange={(e) => setJobType(e.target.value)}
          >
            <option value="">All types</option>
            <option value="full_time">Full time</option>
            <option value="part_time">Part time</option>
            <option value="contract">Contract</option>
            <option value="internship">Internship</option>
          </select>
        </div>
        <button type="submit" className="btn btn-primary">Search</button>
      </form>

      {jobs.length === 0 ? (
        <EmptyState message="No jobs found matching your criteria." />
      ) : (
        <div className="job-grid">
          {jobs.map((job) => (
            <Link to={`/jobs/${job.id}`} key={job.id} className="job-card">
              <h3>{job.title}</h3>
              <p className="job-company">{job.company?.name || "Unknown Company"}</p>
              <p className="job-location">{job.location || "Remote"}</p>
              <div className="job-meta">
                <span className="job-type">{job.job_type?.replace("_", " ")}</span>
                {job.salary_min && (
                  <span className="job-salary">
                    ${Number(job.salary_min).toLocaleString()}
                    {job.salary_max ? ` \u2013 $${Number(job.salary_max).toLocaleString()}` : ""}
                  </span>
                )}
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
