// src/components/SettingsTab.tsx

import { useState, useEffect } from "react";
import type { AllSettings, ComplianceTemplateId } from "../config";
import { defaultAllSettings, COMPLIANCE_TEMPLATES } from "../config";
import { BusinessHoursConfig } from "./BusinessHoursConfig";
import { InfoIcon } from "./InfoIcon";

interface Props {
  settings: AllSettings;
  onSave: (s: AllSettings) => void;
}

const TEMPLATE_LABELS: Record<ComplianceTemplateId, string> = {
  emea: "EMEA",
  us: "US",
  custom: "Custom",
};

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
    includeDirectlyAdded: settings.includeDirectlyAdded,
  }));

  const setPay = (patch: Partial<AllSettings["pay"]>) =>
    setDraft((d) => ({ ...d, pay: { ...d.pay, ...patch } }));

  const setCompliance = (patch: Partial<AllSettings["compliance"]>) =>
    setDraft((d) => ({ ...d, compliance: { ...d.compliance, ...patch } }));

  const setFairness = (patch: Partial<AllSettings["fairness"]>) =>
    setDraft((d) => ({ ...d, fairness: { ...d.fairness, ...patch } }));

  useEffect(() => {
    setDraft({
      pay: { ...settings.pay },
      compliance: { ...settings.compliance },
      fairness: { ...settings.fairness },
      businessHours: {
        ...settings.businessHours,
        workDays: new Set(settings.businessHours.workDays),
        holidays: new Set(settings.businessHours.holidays),
      },
      includeDirectlyAdded: settings.includeDirectlyAdded,
    });
  }, [settings]);

  const applyTemplate = (id: ComplianceTemplateId) => {
    const tpl = COMPLIANCE_TEMPLATES[id];
    setDraft((d) => ({
      ...d,
      compliance: { ...d.compliance, templateId: id, ...tpl },
    }));
  };

  const handleReset = () => setDraft(defaultAllSettings());

  return (
    <div className="settings-tab">
      <div className="settings-columns">

        {/* Left column */}
        <div className="settings-col">

          {/* Data Source */}
          <section className="settings-section">
            <h3 className="settings-section-title">
              🔍 Data Source
            </h3>
            <label className="settings-toggle-row">
              <div className="settings-toggle-info">
                <span className="settings-toggle-label">Include directly-added users</span>
                <span className="settings-toggle-sub">
                  When off, only users on-call via a schedule rotation are counted.
                  Directly-added escalation policy layer entries are excluded.
                  <InfoIcon text="In PagerDuty, a user can be on-call through a schedule rotation or added directly to an escalation policy layer with no schedule. Directly-added entries have no start/end time and don't reflect actual rotation patterns." />
                </span>
              </div>
              <button
                role="switch"
                aria-checked={draft.includeDirectlyAdded}
                className={["settings-toggle", draft.includeDirectlyAdded ? "settings-toggle--on" : ""].filter(Boolean).join(" ")}
                onClick={() => {
                  const next = { ...draft, includeDirectlyAdded: !draft.includeDirectlyAdded };
                  setDraft(next);
                  onSave(next);
                }}
              >
                <span className="settings-toggle-thumb" />
              </button>
            </label>
          </section>

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
                    onChange={(e) => { const v = parseFloat(e.target.value); if (!isNaN(v)) setPay({ l1RatePerHour: v }); }}
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
                    onChange={(e) => { const v = parseFloat(e.target.value); if (!isNaN(v)) setPay({ l2PlusRatePerHour: v }); }}
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
                  onChange={(e) => { const v = parseFloat(e.target.value); if (!isNaN(v)) setPay({ offHoursMultiplier: v }); }}
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
                  onChange={(e) => { const v = parseFloat(e.target.value); if (!isNaN(v)) setPay({ weekendMultiplier: v }); }}
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
                  onChange={(e) => { const v = parseFloat(e.target.value); if (!isNaN(v)) setPay({ holidayMultiplier: v }); }}
                  className="settings-input"
                />
              </label>
            </div>
          </section>

          {/* Compliance Caps */}
          <section className="settings-section">
            <h3 className="settings-section-title">
              🛡 Compliance Rules
              <InfoIcon text="Users exceeding these caps are flagged ⚠ OVER CAP in the Compliance tab. Set a value to 0 to disable that rule. The near-limit threshold triggers a ⚡ NEAR warning before the cap is hit." />
            </h3>

            {/* Template selector */}
            <div className="settings-label" style={{ marginBottom: 8 }}>
              Rule template
              <InfoIcon text="EMEA: EU Working Time Directive (48h/wk avg, 11h rest). US: FLSA-aligned (40h/wk). Custom: set your own values." />
            </div>
            <div className="template-chip-group">
              {(["emea", "us", "custom"] as ComplianceTemplateId[]).map((id) => (
                <button
                  key={id}
                  className={["template-chip", draft.compliance.templateId === id ? "template-chip--active" : ""].filter(Boolean).join(" ")}
                  onClick={() => applyTemplate(id)}
                >
                  {TEMPLATE_LABELS[id]}
                </button>
              ))}
            </div>

            <div className="settings-grid-2" style={{ marginTop: 10 }}>
              <label className="settings-label">
                Period total cap (hrs)
                <InfoIcon text="Maximum total scheduled oncall hours in the selected period. 0 = disabled." />
                <input
                  type="number"
                  min={0}
                  step={1}
                  value={draft.compliance.periodHoursCap}
                  onChange={(e) => { const v = parseFloat(e.target.value); if (!isNaN(v)) setCompliance({ periodHoursCap: v, templateId: "custom" }); }}
                  className="settings-input"
                />
              </label>
              <label className="settings-label">
                Period outside-hours cap (hrs)
                <InfoIcon text="Maximum oncall hours outside business hours in the selected period. 0 = disabled." />
                <input
                  type="number"
                  min={0}
                  step={1}
                  value={draft.compliance.periodOutsideHoursCap}
                  onChange={(e) => { const v = parseFloat(e.target.value); if (!isNaN(v)) setCompliance({ periodOutsideHoursCap: v, templateId: "custom" }); }}
                  className="settings-input"
                />
              </label>
              <label className="settings-label">
                Max consecutive on-call days
                <InfoIcon text="Alert when a user has on-call coverage on this many consecutive calendar days. 0 = disabled." />
                <input
                  type="number"
                  min={0}
                  step={1}
                  value={draft.compliance.maxConsecutiveDays}
                  onChange={(e) => { const v = parseFloat(e.target.value); if (!isNaN(v)) setCompliance({ maxConsecutiveDays: v, templateId: "custom" }); }}
                  className="settings-input"
                />
              </label>
              <label className="settings-label">
                Max consecutive on-call hours
                <InfoIcon text="Alert when a user has an unbroken on-call shift this long. 0 = disabled." />
                <input
                  type="number"
                  min={0}
                  step={1}
                  value={draft.compliance.maxConsecutiveHours}
                  onChange={(e) => { const v = parseFloat(e.target.value); if (!isNaN(v)) setCompliance({ maxConsecutiveHours: v, templateId: "custom" }); }}
                  className="settings-input"
                />
              </label>
              <label className="settings-label">
                Mandatory rest between shifts (hrs)
                <InfoIcon text="Flag users whose gap between consecutive on-call shifts is shorter than this. 0 = disabled." />
                <input
                  type="number"
                  min={0}
                  step={1}
                  value={draft.compliance.mandatoryRestHours}
                  onChange={(e) => { const v = parseFloat(e.target.value); if (!isNaN(v)) setCompliance({ mandatoryRestHours: v, templateId: "custom" }); }}
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

          {/* Fairness Limits */}
          <section className="settings-section">
            <h3 className="settings-section-title">
              ⚖ Fairness Limits
              <InfoIcon text="Flag users who exceed these caps in the Fairness tab. Set to 0 to disable a limit." />
            </h3>
            <div className="settings-grid-2">
              <label className="settings-label">
                Max on-call weekends / period
                <InfoIcon text="Maximum number of distinct weekends (Sat or Sun) with any on-call coverage. 0 = disabled." />
                <input
                  type="number"
                  min={0}
                  step={1}
                  value={draft.fairness.maxWeekendsPerPeriod}
                  onChange={(e) => { const v = parseFloat(e.target.value); if (!isNaN(v)) setFairness({ maxWeekendsPerPeriod: v }); }}
                  className="settings-input"
                />
              </label>
              <label className="settings-label">
                Max on-call holidays / period
                <InfoIcon text="Maximum number of distinct holiday dates with any on-call coverage. 0 = disabled." />
                <input
                  type="number"
                  min={0}
                  step={1}
                  value={draft.fairness.maxHolidaysPerPeriod}
                  onChange={(e) => { const v = parseFloat(e.target.value); if (!isNaN(v)) setFairness({ maxHolidaysPerPeriod: v }); }}
                  className="settings-input"
                />
              </label>
              <label className="settings-label">
                Max outside-hours periods / period
                <InfoIcon text="Maximum number of distinct outside-business-hours on-call blocks. 0 = disabled." />
                <input
                  type="number"
                  min={0}
                  step={1}
                  value={draft.fairness.maxOohPeriodsPerPeriod}
                  onChange={(e) => { const v = parseFloat(e.target.value); if (!isNaN(v)) setFairness({ maxOohPeriodsPerPeriod: v }); }}
                  className="settings-input"
                />
              </label>
            </div>
            <label className="settings-label" style={{ marginTop: 10 }}>
              Near-limit warning threshold
              <InfoIcon text="When a user reaches this % of a fairness cap, they show ⚡ NEAR instead of ✓ OK." />
              <div className="settings-slider-row">
                <input
                  type="range"
                  min={50}
                  max={99}
                  step={1}
                  value={Math.round(draft.fairness.nearLimitThreshold * 100)}
                  onChange={(e) => setFairness({ nearLimitThreshold: Number(e.target.value) / 100 })}
                  className="settings-slider"
                />
                <span className="settings-slider-value">{Math.round(draft.fairness.nearLimitThreshold * 100)}%</span>
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
