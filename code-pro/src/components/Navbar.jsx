import React from "react";
import { Code2, Play, Square, Trash2 } from "lucide-react";
import { setRemoteBotStatus, clearAllQuestions } from "../firebase";

export default function Navbar({ botActive, questionCount }) {
  const toggleBot = async () => {
    try {
      await setRemoteBotStatus(!botActive);
    } catch (e) {
      console.error("Failed to update bot status:", e);
    }
  };

  const handleClearAll = async () => {
    if (window.confirm("Are you sure you want to clear all questions from database?")) {
      await clearAllQuestions();
    }
  };

  return (
    <nav className="navbar">
      <div className="brand">
        <div className="brand-icon">
          <Code2 size={18} />
        </div>
        <div className="brand-text">
          Code<span className="brand-pro">-Pro</span>
        </div>
      </div>

      <div className="nav-actions">
        {/* Realtime Bot Status Indicator */}
        <div className={`status-pill ${botActive ? "status-active" : "status-inactive"}`}>
          <div className="status-indicator" />
          <span className="status-text">{botActive ? "Scanning Screen..." : "Bot Ready"}</span>
        </div>

        {/* Start / Stop Toggle Button */}
        <button
          onClick={toggleBot}
          className={`btn ${botActive ? "btn-danger" : "btn-success"} btn-sm`}
          title={botActive ? "Click to Cancel / Stop Bot" : "Click to Scan & Solve Problem"}
        >
          {botActive ? (
            <>
              <Square size={13} fill="currentColor" /> <span className="btn-label">Scanning (Stop)</span>
            </>
          ) : (
            <>
              <Play size={13} fill="currentColor" /> <span className="btn-label">Start Bot</span>
            </>
          )}
        </button>

        {questionCount > 0 && (
          <button
            onClick={handleClearAll}
            className="btn btn-secondary btn-sm"
            title="Clear all saved questions from Firebase"
          >
            <Trash2 size={13} /> <span className="btn-label-desktop">Clear</span>
          </button>
        )}
      </div>
    </nav>
  );
}
