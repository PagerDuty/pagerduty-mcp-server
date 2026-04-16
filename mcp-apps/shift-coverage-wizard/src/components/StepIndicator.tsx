interface StepIndicatorProps {
  steps: string[];
  current: number; // 0-based
}

export function StepIndicator({ steps, current }: StepIndicatorProps) {
  return (
    <div className="step-indicator">
      {steps.map((label, i) => (
        <div key={label} className="step-item">
          <div
            className={`step-circle ${
              i < current ? "done" : i === current ? "active" : "pending"
            }`}
          >
            {i < current ? "✓" : i + 1}
          </div>
          <span className={`step-label ${i === current ? "active" : ""}`}>{label}</span>
          {i < steps.length - 1 && <div className={`step-line ${i < current ? "done" : ""}`} />}
        </div>
      ))}
    </div>
  );
}
