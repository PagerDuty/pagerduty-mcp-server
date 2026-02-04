/**
 * Workflow Modal - Start incident workflows
 */

import type { App } from "@modelcontextprotocol/ext-apps";
import { useState, useEffect } from "react";
import { fetchIncidentWorkflows, startIncidentWorkflow } from "../api";

interface WorkflowModalProps {
  app: App;
  incident: any;
  onClose: () => void;
  onStarted: () => void;
}

interface Workflow {
  id: string;
  name: string;
  description?: string;
}

export function WorkflowModal({ app, incident, onClose, onStarted }: WorkflowModalProps) {
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [selectedWorkflow, setSelectedWorkflow] = useState<string>("");
  const [isLoading, setIsLoading] = useState(true);
  const [isStarting, setIsStarting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch workflows
  useEffect(() => {
    const loadWorkflows = async () => {
      setIsLoading(true);
      try {
        const workflowsData = await fetchIncidentWorkflows(app);
        setWorkflows(workflowsData);
      } catch (err) {
        console.error("Failed to fetch workflows:", err);
        setError("Failed to load workflows");
      } finally {
        setIsLoading(false);
      }
    };

    loadWorkflows();
  }, [app]);

  const handleStart = async () => {
    if (!selectedWorkflow) {
      setError("Please select a workflow");
      return;
    }

    setIsStarting(true);
    setError(null);

    try {
      await startIncidentWorkflow(app, selectedWorkflow, incident.id);
      onStarted();
      onClose();
    } catch (err) {
      setError("Failed to start workflow. Please try again.");
      console.error(err);
    } finally {
      setIsStarting(false);
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
      <div className="modal-content workflow-modal-content">
        <div className="modal-header">
          <div className="modal-title">
            <h2>Run Workflow - Incident #{incident.incident_number}</h2>
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
            </div>
          </div>
          <div style={{ padding: "20px 24px" }}>
            <div className="workflow-panel">
              <h4>⚡ Run Workflow</h4>
              <div className="workflow-content">
                {/* Workflow selector */}
                <div className="workflow-selector">
                  <label htmlFor="workflow">Select Workflow:</label>
                  {isLoading ? (
                    <p>Loading workflows...</p>
                  ) : workflows.length === 0 ? (
                    <p className="empty-text">No workflows available</p>
                  ) : (
                    <select
                      id="workflow"
                      value={selectedWorkflow}
                      onChange={(e) => setSelectedWorkflow(e.target.value)}
                      disabled={isStarting}
                    >
                      <option value="">Select a Workflow</option>
                      {workflows.map((workflow) => (
                        <option key={workflow.id} value={workflow.id}>
                          {workflow.name}
                        </option>
                      ))}
                    </select>
                  )}
                </div>

                {/* Selected workflow details */}
                {selectedWorkflow && workflows.find((w) => w.id === selectedWorkflow) && (
                  <div className="workflow-details">
                    <strong>Description:</strong>
                    <p>
                      {workflows.find((w) => w.id === selectedWorkflow)?.description ||
                        "No description available"}
                    </p>
                  </div>
                )}

                {/* Start button */}
                <button
                  className="workflow-start-btn"
                  onClick={handleStart}
                  disabled={isStarting || !selectedWorkflow || isLoading}
                >
                  {isStarting ? "Starting..." : "Start Workflow"}
                </button>

                {error && <p className="error-text">{error}</p>}

                {/* Help text */}
                <p className="workflow-help">
                  Workflows automate incident response tasks like notifications, channel creation, and escalations.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
