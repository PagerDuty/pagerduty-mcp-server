interface InsightCardProps {
  title: string;
  content: string | null;  // null = loading
  error?: string | null;
  onRetry?: () => void;
}

export function InsightCard({ title, content, error, onRetry }: InsightCardProps) {
  return (
    <div className="insight-card">
      <div className="insight-card-title">{title}</div>
      {error ? (
        <div className="insight-error">
          Could not load insight.
          {onRetry && (
            <button type="button" className="btn btn-sm" onClick={onRetry} style={{ marginLeft: 8 }}>
              Retry
            </button>
          )}
        </div>
      ) : content === null ? (
        <>
          <div className="insight-skeleton" style={{ width: "90%" }} />
          <div className="insight-skeleton" style={{ width: "75%" }} />
          <div className="insight-skeleton" style={{ width: "80%" }} />
          <div className="insight-skeleton" />
        </>
      ) : (
        <div className="insight-card-body">{content}</div>
      )}
    </div>
  );
}
