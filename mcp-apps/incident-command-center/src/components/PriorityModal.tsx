/**
 * Priority Change Modal - Change incident urgency/priority
 */

import type { App } from "@modelcontextprotocol/ext-apps";
import { useState, useEffect } from "react";
import { fetchPriorities, changeIncidentPriority } from "../api";

interface Priority {
  id: string;
  name: string;
  summary: string;
  description?: string;
}

interface PriorityModalProps {
  app: App;
  incident: any;
  onClose: () => void;
  onChanged: () => void;
}

export function PriorityModal({ app, incident, onClose, onChanged }: PriorityModalProps) {
  const [priorities, setPriorities] = useState<Priority[]>([]);
  const [selectedPriority, setSelectedPriority] = useState<string>(incident.priority?.id || "");
  const [isLoading, setIsLoading] = useState(true);
  const [isChanging, setIsChanging] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch priorities
  useEffect(() => {
    const loadPriorities = async () => {
      setIsLoading(true);
      try {
        const prioritiesData = await fetchPriorities(app);
        setPriorities(prioritiesData);
      } catch (err) {
        console.error("Failed to fetch priorities:", err);
        setError("Failed to load priorities");
      } finally {
        setIsLoading(false);
      }
    };

    loadPriorities();
  }, [app]);

  const handleChange = async () => {
    if (!selectedPriority) {
      setError("Please select a priority");
      return;
    }

    if (selectedPriority === incident.priority?.id) {
      setError("Please select a different priority");
      return;
    }

    setIsChanging(true);
    setError(null);

    try {
      await changeIncidentPriority(app, incident.id, selectedPriority);
      onChanged();
      onClose();
    } catch (err) {
      setError("Failed to change priority. Please try again.");
      console.error(err);
    } finally {
      setIsChanging(false);
    }
  };

  return (
    <div
      className="modal-overlay"
      onClick={(e) => {
        if (e.target === e.currentTarget) {
          onClose();
        }
      }}
    >
      <div className="modal-content priority-modal-content">
        <div className="modal-header">
          <div className="modal-title">
            <h2>Change Priority - Incident #{incident.incident_number}</h2>
          </div>
          <button className="modal-close" onClick={onClose}>
            ×
          </button>
        </div>
        <div className="modal-body">
          <div className="modal-summary">
            <h3>{incident.title}</h3>
            <div className="summary-meta">
              <span>Service: {incident.service.summary}</span>
              <span className={`status-badge status-${incident.status}`}>
                {incident.status}
              </span>
              <span className={`urgency-badge urgency-${incident.urgency}`}>
                {incident.urgency}
              </span>
              {incident.priority && (
                <span className="priority-badge-display">
                  Priority: {incident.priority.summary}
                </span>
              )}
            </div>
          </div>
          <div style={{ padding: "20px 24px" }}>
            <div className="priority-panel">
              <h4>🎯 Change Priority</h4>
              <div className="priority-content">
                {incident.priority && (
                  <div className="current-priority">
                    <strong>Current Priority:</strong>
                    <p>{incident.priority.summary}</p>
                  </div>
                )}

                <div className="priority-selector">
                  <label htmlFor="priority-select">Select new priority:</label>
                  {isLoading ? (
                    <p>Loading priorities...</p>
                  ) : priorities.length === 0 ? (
                    <p className="empty-text">No priorities configured in your account</p>
                  ) : (
                    <select
                      id="priority-select"
                      value={selectedPriority}
                      onChange={(e) => setSelectedPriority(e.target.value)}
                      disabled={isChanging}
                    >
                      <option value="">Select Priority Level</option>
                      {priorities.map((priority) => (
                        <option key={priority.id} value={priority.id}>
                          {priority.name} - {priority.summary}
                        </option>
                      ))}
                    </select>
                  )}
                </div>

                <button
                  className="priority-change-btn"
                  onClick={handleChange}
                  disabled={isChanging || !selectedPriority || isLoading}
                >
                  {isChanging ? "Changing..." : "Change Priority"}
                </button>

                {error && <p className="error-text">{error}</p>}

                <p className="priority-help">
                  Priority levels (P1-P5) help organize and route incidents based on business impact.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
