interface ConfirmModalProps {
  scheduleName: string;
  userName: string;
  start: string;
  end: string;
  onConfirm: () => void;
  onCancel: () => void;
  loading: boolean;
}

function fmt(iso: string): string {
  return new Date(iso).toLocaleString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

export function ConfirmModal({
  scheduleName,
  userName,
  start,
  end,
  onConfirm,
  onCancel,
  loading,
}: ConfirmModalProps) {
  return (
    <div className="modal-overlay" role="dialog" aria-modal="true">
      <div className="modal">
        <div className="modal-header">
          <h3>Confirm Override</h3>
        </div>
        <div className="modal-body">
          <table className="confirm-table">
            <tbody>
              <tr>
                <td className="confirm-label">Schedule</td>
                <td className="confirm-value">{scheduleName}</td>
              </tr>
              <tr>
                <td className="confirm-label">Assignee</td>
                <td className="confirm-value">{userName}</td>
              </tr>
              <tr>
                <td className="confirm-label">From</td>
                <td className="confirm-value">{fmt(start)}</td>
              </tr>
              <tr>
                <td className="confirm-label">To</td>
                <td className="confirm-value">{fmt(end)}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div className="modal-footer">
          <button className="btn btn-secondary" onClick={onCancel} disabled={loading}>
            Cancel
          </button>
          <button className="btn btn-primary" onClick={onConfirm} disabled={loading}>
            {loading ? "Creating..." : "Create Override ✓"}
          </button>
        </div>
      </div>
    </div>
  );
}
