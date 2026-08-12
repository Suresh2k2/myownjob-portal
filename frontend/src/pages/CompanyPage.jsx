import { useEffect, useState } from "react";
import { companyService } from "../services/companyService";
import { useAuth } from "../context/AuthContext";
import Loader from "../components/Loader";

export default function CompanyPage() {
  const { user } = useAuth();
  const [company, setCompany] = useState(null);
  const [loading, setLoading] = useState(true);
  const [form, setForm] = useState({ name: "", description: "", website: "" });
  const [creating, setCreating] = useState(false);
  const [message, setMessage] = useState("");

  useEffect(() => {
    companyService
      .list()
      .then((res) => {
        const myCompany = res.data.find((c) => c.owner_id === user?.id);
        if (myCompany) {
          setCompany(myCompany);
          setForm({ name: myCompany.name, description: myCompany.description || "", website: myCompany.website || "" });
        }
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [user]);

  const handleCreate = async (e) => {
    e.preventDefault();
    setCreating(true);
    setMessage("");
    try {
      const res = await companyService.create(form);
      setCompany(res.data);
      setMessage("Company created.");
    } catch (err) {
      const detail = err.response?.data?.detail;
      setMessage(typeof detail === "string" ? detail : "Failed to create company");
    } finally {
      setCreating(false);
    }
  };

  if (loading) return <Loader />;

  const isSaved = message === "Company created.";

  return (
    <div className="page">
      <h1>{company ? "My Company" : "Create Company"}</h1>
      <form onSubmit={handleCreate} className="card profile-form">
        {message && <div className={isSaved ? "alert alert-success" : "alert alert-error"}>{message}</div>}
        <div className="form-group">
          <label className="form-label" htmlFor="name">Company name</label>
          <input id="name" className="form-input" value={form.name} onChange={(e) => setForm({...form, name: e.target.value})} required disabled={!!company} />
        </div>
        <div className="form-group">
          <label className="form-label" htmlFor="description">Description</label>
          <textarea id="description" className="form-textarea" value={form.description} onChange={(e) => setForm({...form, description: e.target.value})} disabled={!!company} />
        </div>
        <div className="form-group">
          <label className="form-label" htmlFor="website">Website</label>
          <input id="website" className="form-input" value={form.website} onChange={(e) => setForm({...form, website: e.target.value})} disabled={!!company} />
        </div>
        {!company && (
          <button type="submit" className="btn btn-primary" disabled={creating}>
            {creating ? "Creating..." : "Create company"}
          </button>
        )}
      </form>
    </div>
  );
}
