import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { candidateService } from "../services/candidateService";
import Loader from "../components/Loader";

export default function ProfilePage() {
  const { user } = useAuth();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({ full_name: "", phone: "", resume_url: "", skills: "" });
  const [message, setMessage] = useState("");

  useEffect(() => {
    candidateService
      .getProfile()
      .then((res) => {
        setProfile(res.data);
        setForm({
          full_name: res.data.full_name,
          phone: res.data.phone || "",
          resume_url: res.data.resume_url || "",
          skills: res.data.skills || "",
        });
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setMessage("");
    try {
      if (profile) {
        const res = await candidateService.updateProfile(form);
        setProfile(res.data);
      } else {
        const res = await candidateService.createProfile(form);
        setProfile(res.data);
      }
      setMessage("Profile saved.");
    } catch (err) {
      const detail = err.response?.data?.detail;
      setMessage(typeof detail === "string" ? detail : "Failed to save profile");
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <Loader />;

  const isSaved = message === "Profile saved.";

  return (
    <div className="page">
      <h1>My Profile</h1>
      <form onSubmit={handleSubmit} className="card profile-form">
        {message && <div className={isSaved ? "alert alert-success" : "alert alert-error"}>{message}</div>}
        <div className="form-group">
          <label className="form-label" htmlFor="full_name">Full name</label>
          <input id="full_name" className="form-input" value={form.full_name} onChange={(e) => setForm({...form, full_name: e.target.value})} required />
        </div>
        <div className="form-group">
          <label className="form-label" htmlFor="phone">Phone</label>
          <input id="phone" className="form-input" value={form.phone} onChange={(e) => setForm({...form, phone: e.target.value})} />
        </div>
        <div className="form-group">
          <label className="form-label" htmlFor="resume_url">Resume URL</label>
          <input id="resume_url" className="form-input" value={form.resume_url} onChange={(e) => setForm({...form, resume_url: e.target.value})} />
        </div>
        <div className="form-group">
          <label className="form-label" htmlFor="skills">Skills</label>
          <textarea id="skills" className="form-textarea" value={form.skills} onChange={(e) => setForm({...form, skills: e.target.value})} rows={3} placeholder="e.g. Python, FastAPI, React" />
        </div>
        <button type="submit" className="btn btn-primary" disabled={saving}>
          {saving ? "Saving..." : "Save profile"}
        </button>
      </form>
    </div>
  );
}
