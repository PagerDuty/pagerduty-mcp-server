import { useState } from "react";

export interface BPTip {
  icon: string;
  text: string;
}

interface Props {
  phase: string;
  tips: BPTip[];
}

export function BestPracticesPanel({ phase, tips }: Props) {
  const [optedOut, setOptedOut] = useState(false);

  if (optedOut) {
    return (
      <div className="bp-opted-out">
        <label className="bp-optout-label">
          <input
            type="checkbox"
            checked={true}
            onChange={() => setOptedOut(false)}
          />
          Skipping PagerDuty best practices for {phase}
        </label>
      </div>
    );
  }

  return (
    <div className="bp-panel">
      <div className="bp-header">
        <span className="bp-icon">✦</span>
        <span className="bp-title">PagerDuty Best Practices for {phase}</span>
      </div>
      <ul className="bp-list">
        {tips.map((t, i) => (
          <li key={i} className="bp-item">
            <span className="bp-item-icon">{t.icon}</span>
            <span className="bp-item-text">{t.text}</span>
          </li>
        ))}
      </ul>
      <label className="bp-optout-label">
        <input
          type="checkbox"
          checked={false}
          onChange={() => setOptedOut(true)}
        />
        I don't want to follow PagerDuty best practices for {phase}
      </label>
    </div>
  );
}
