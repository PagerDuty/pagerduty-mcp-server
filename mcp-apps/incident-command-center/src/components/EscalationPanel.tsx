/**
 * EscalationPanel - Escalation controls for incidents
 */

import type { App } from "@modelcontextprotocol/ext-apps";
import { useState, useEffect } from "react";
import { escalateIncident, fetchEscalationPolicies } from "../api";

interface EscalationPolicy {
  id: string;
  name: string;
  summary: string;
}

interface EscalationPanelProps {
  app: App;
  incident: any;
  onEscalated: () => void;
}

export function EscalationPanel({ app, incident, onEscalated }: EscalationPanelProps) {
  const [policies, setPolicies] = useState<EscalationPolicy[]>([]);
  const [selectedPolicy, setSelectedPolicy] = useState<string>("");
  const [isLoading, setIsLoading] = useState(false);
  const [isEscalating, setIsEscalating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch escalation policies
  useEffect(() => {
    const loadPolicies = async () => {
      setIsLoading(true);
      try {
        const policiesData = await fetchEscalationPolicies(app);
        setPolicies(policiesData);
      } catch (err) {
        console.error("Failed to fetch escalation policies:", err);
        setError("Failed to load escalation policies");
      } finally {
        setIsLoading(false);
      }
    };

    loadPolicies();
  }, [app]);

  const handleEscalate = async () => {
    if (!selectedPolicy) {
      setError("Please select an escalation policy");
      return;
    }

    setIsEscalating(true);
    setError(null);

    try {
      await escalateIncident(app, incident.id, selectedPolicy);
      onEscalated(); // Refresh incident data
    } catch (err) {
      setError("Failed to escalate incident. Please try again.");
      console.error(err);
    } finally {
      setIsEscalating(false);
    }
  };

  return (
    <div className="escalation-panel">
      <h4>🚀 Escalation</h4>

      <div className="escalation-content">
        {/* Current escalation info */}
        {incident.escalation_policy && (
          <div className="current-escalation">
            <strong>Current Policy:</strong>
            <p>{incident.escalation_policy.summary}</p>
          </div>
        )}

        {/* Escalation policy selector */}
        <div className="escalation-selector">
          <label htmlFor="escalation-policy">Escalate to:</label>
          {isLoading ? (
            <p>Loading policies...</p>
          ) : (
            <select
              id="escalation-policy"
              value={selectedPolicy}
              onChange={(e) => setSelectedPolicy(e.target.value)}
              disabled={isEscalating}
            >
              <option value="">Select Escalation Policy</option>
              {policies.map((policy) => (
                <option key={policy.id} value={policy.id}>
                  {policy.name}
                </option>
              ))}
            </select>
          )}
        </div>

        {/* Escalate button */}
        <button
          className="escalate-btn"
          onClick={handleEscalate}
          disabled={isEscalating || !selectedPolicy || isLoading}
        >
          {isEscalating ? "Escalating..." : "Escalate Incident"}
        </button>

        {error && <p className="error-text">{error}</p>}

        {/* Help text */}
        <p className="escalation-help">
          Escalating will notify the selected on-call team and reassign the incident.
        </p>
      </div>
    </div>
  );
}
