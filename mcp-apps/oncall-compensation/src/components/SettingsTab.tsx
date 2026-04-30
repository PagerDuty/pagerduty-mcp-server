// src/components/SettingsTab.tsx

import { useState } from "react";
import type { AllSettings } from "../config";
import { defaultAllSettings } from "../config";
import { BusinessHoursConfig } from "./BusinessHoursConfig";
import { InfoIcon } from "./InfoIcon";

interface Props {
  settings: AllSettings;
  onSave: (s: AllSettings) => void;
}

export function SettingsTab({ settings, onSave }: Props) {
  const [draft, setDraft] = useState<AllSettings>(() => ({
    pay: { ...settings.pay },
    compliance: { ...settings.compliance },
    fairness: { ...settings.fairness },
    businessHours: {
      ...settings.businessHours,
      workDays: new Set(settings.businessHours.workDays),
      holidays: new Set(settings.businessHours.holidays),
    },
  }));

  const setPay = (patch: Partial<AllSettings["pay"]>) =>
    setDraft((d) => ({ ...d, pay: { ...d.pay, ...patch } }));

  const setCompliance = (patch: Partial<AllSettings["compliance"]>) =>
    setDraft((d) => ({ ...d, compliance: { ...d.compliance, ...patch } }));

  const setFairness = (patch: Partial<AllSettings["fairness"]>) =>
    setDraft((d) => ({ ...d, fairness: { ...d.fairness, ...patch } }));

  const handleReset = () => setDraft(defaultAllSettings());

  return (
    <div className="settings-tab">
      <div className="settings-columns">

        {/* Left column */}
        <div className="settings-col">

          {/* Pay Rates */}
          <section className="settings-section">
            <h3 className="settings-section-title">
              💰 Pay Rates
              <InfoIcon text="Estimated pay = (inside-hours × L1 rate) + (outside-hours × L1 rate × off-hours multiplier) + (weekend hrs × L1 rate × weekend multiplier) + (holiday hrs × L1 rate × holiday multiplier) + (L2+ hrs × L2+ rate). This is an estimate only." />
            </h3>
            <div className="settings-grid-2">
              <label className="settings-label">
                L1 (Primary) base rate / hr
                <div className="settings-currency-input">
                  <span className="settings-currency-symbol">$</span>
                  <input
                    type="number"
                    min={0}
                    step={1}
                    value={draft.pay.l1RatePerHour}
                    onChange={(e) => setPay({ l1RatePerHour: Number(e.target.value) })}
                    className="settings-input"
                  />
                </div>
              </label>
              <label className="settings-label">
                L2+ (Secondary) base rate / hr
                <div className="settings-currency-input">
                  <span className="settings-currency-symbol">$</span>
                  <input
                    type="number"
                    min={0}
                    step={1}
                    value={draft.pay.l2PlusRatePerHour}
                    onChange={(e) => setPay({ l2PlusRatePerHour: Number(e.target.value) })}
                    className="settings-input"
                  />
                </div>
              </label>
            </div>
            <div className="settings-label" style={{ marginTop: 10 }}>
              Multipliers
              <InfoIcon text="Applied on top of the L1 base rate. Off-hours = weekday hours outside the business window. Weekend = Sat/Sun. Holiday = dates listed in Business Hours config." />
            </div>
            <div className="settings-grid-3" style={{ marginTop: 6 }}>
              <label className="settings-label">
                Off-Hours ×
                <input
                  type="number"
                  min={1}
                  step={0.1}
                  value={draft.pay.offHoursMultiplier}
                  onChange={(e) => setPay({ offHoursMultiplier: Number(e.target.value) })}
                  className="settings-input"
                />
              </label>
              <label className="settings-label">
                Weekend ×
                <input
                  type="number"
                  min={1}
                  step={0.1}
                  value={draft.pay.weekendMultiplier}
                  onChange={(e) => setPay({ weekendMultiplier: Number(e.target.value) })}
                  className="settings-input"
                />
              </label>
              <label className="settings-label">
                Holiday ×
                <input
                  type="number"
                  min={1}
                  step={0.1}
                  value={draft.pay.holidayMultiplier}
                  onChange={(e) => setPay({ holidayMultiplier: Number(e.target.value) })}
                  className="settings-input"
                />
              </label>
            </div>
          </section>

          {/* Compliance Caps */}
          <section className="settings-section">
            <h3 className="settings-section-title">
              🛡 Compliance Caps
              <InfoIcon text="Users exceeding these caps are flagged ⚠ OVER CAP in the Compliance tab. The near-limit threshold triggers a ⚡ NEAR warning before the cap is hit. Caps apply to the selected date range." />
            </h3>
            <div className="settings-grid-2">
              <label className="settings-label">
                Period total cap (hrs)
                <InfoIcon text="Maximum total scheduled oncall hours allowed in the selected period." />
                <input
                  type="number"
                  min={1}
                  step={1}
                  value={draft.compliance.periodHoursCap}
                  onChange={(e) => setCompliance({ periodHoursCap: Number(e.target.value) })}
                  className="settings-input"
                />
              </label>
              <label className="settings-label">
                Period outside-hours cap (hrs)
                <InfoIcon text="Maximum oncall hours outside business hours allowed in the selected period." />
                <input
                  type="number"
                  min={1}
                  step={1}
                  value={draft.compliance.periodOutsideHoursCap}
                  onChange={(e) => setCompliance({ periodOutsideHoursCap: Number(e.target.value) })}
                  className="settings-input"
                />
              </label>
            </div>
            <label className="settings-label" style={{ marginTop: 10 }}>
              Near-limit warning threshold
              <InfoIcon text="When a user reaches this % of their cap, they show ⚡ NEAR instead of ✓ OK." />
              <div className="settings-slider-row">
                <input
                  type="range"
                  min={50}
                  max={99}
                  step={1}
                  value={Math.round(draft.compliance.nearLimitThreshold * 100)}
                  onChange={(e) => setCompliance({ nearLimitThreshold: Number(e.target.value) / 100 })}
                  className="settings-slider"
                />
                <span className="settings-slider-value">
                  {Math.round(draft.compliance.nearLimitThreshold * 100)}%
                </span>
              </div>
            </label>
          </section>

        </div>

        {/* Right column */}
        <div className="settings-col">

          {/* Business Hours */}
          <section className="settings-section">
            <h3 className="settings-section-title">
              🕐 Business Hours
              <InfoIcon text="Defines what counts as 'business hours' for outside-hours calculations. Oncall time outside this window on work days is counted as off-hours. Weekends and holidays are always outside hours." />
            </h3>
            <BusinessHoursConfig
              config={draft.businessHours}
              onChange={(bh) => setDraft((d) => ({ ...d, businessHours: bh }))}
              showToggle={false}
            />
          </section>

          {/* Fairness Thresholds */}
          <section className="settings-section">
            <h3 className="settings-section-title">
              ⚖ Fairness Thresholds
              <InfoIcon text="Equity Score = 100 − (std deviation ÷ mean × 100), capped 0–100. A perfectly equal team scores 100. Outliers are users whose scheduled hours exceed the threshold multiple of the team average." />
            </h3>
            <label className="settings-label">
              Outlier threshold (× team average)
              <InfoIcon text="A user is flagged as an outlier when their scheduled hours ≥ this multiple of the team average." />
              <div className="settings-slider-row">
                <input
                  type="range"
                  min={1.5}
                  max={5}
                  step={0.5}
                  value={draft.fairness.outlierMultiplier}
                  onChange={(e) => setFairness({ outlierMultiplier: Number(e.target.value) })}
                  className="settings-slider"
                />
                <span className="settings-slider-value">{draft.fairness.outlierMultiplier}×</span>
              </div>
            </label>
          </section>

          {/* Actions */}
          <div className="settings-actions">
            <button className="btn-settings-reset" onClick={handleReset}>
              Reset to defaults
            </button>
            <button className="btn-settings-save" onClick={() => onSave(draft)}>
              Save Settings
            </button>
          </div>

        </div>
      </div>
    </div>
  );
}
