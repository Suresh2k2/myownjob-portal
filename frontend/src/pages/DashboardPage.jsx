import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import Loader from "../components/Loader";

export default function DashboardPage() {
  const { user, loading } = useAuth();

  if (loading) return <Loader />;

  if (!user) return <Navigate to="/login" replace />;

  if (user.role === "candidate") return <Navigate to="/candidate-dashboard" replace />;
  if (user.role === "recruiter") return <Navigate to="/recruiter-dashboard" replace />;

  return <Navigate to="/jobs" replace />;
}
