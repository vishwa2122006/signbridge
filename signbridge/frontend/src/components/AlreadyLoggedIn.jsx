import React from "react";
import { Link } from "react-router-dom";
import { T } from "./Bilingual.jsx";
import { useAuth } from "../AuthContext.jsx";

export default function AlreadyLoggedIn() {
  const { user, signOut } = useAuth();
  return (
    <div className="auth-page">
      <div className="card accent auth-card">
        <p>
          👋 <T k="alreadyLoggedIn" vars={{ name: user.name }} />
        </p>
        <div className="toolbar">
          <Link to={user.role === "admin" ? "/review" : "/teach"}>
            <button>
              <T k="continue" /> ➜
            </button>
          </Link>
          <button className="secondary" onClick={signOut}>
            🚪 <T k="logOut" />
          </button>
        </div>
      </div>
    </div>
  );
}
