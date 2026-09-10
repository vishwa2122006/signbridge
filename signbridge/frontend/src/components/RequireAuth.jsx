import React from "react";
import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../AuthContext.jsx";

/** A page for trainers and admins (`admin` for admins only). The public is sent to the login page and brought back after logging in. */
export default function RequireAuth({ admin = false, children }) {
  const { user, ready } = useAuth();
  const location = useLocation();
  if (!ready) {
    return (
      <div className="page-loading">
        <span className="spinner big" />
      </div>
    );
  }
  if (!user) return <Navigate to="/login" replace state={{ from: location.pathname + location.search }} />;
  if (admin && user.role !== "admin") return <Navigate to="/teach" replace />;
  return children;
}
