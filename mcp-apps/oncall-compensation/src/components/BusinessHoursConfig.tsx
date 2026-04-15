import { useState } from "react";
import type { BusinessHoursConfig } from "../businessHours";

interface Props {
  config: BusinessHoursConfig;
  onChange: (config: BusinessHoursConfig) => void;
  disabled?: boolean;
  /** When false, render only the panel content (no toggle button). Used when hosted inside a modal. */
  showToggle?: boolean;
}

const DAY_LABELS: { idx: number; short: string }[] = [
  { idx: 1, short: "Mon" },
  { idx: 2, short: "Tue" },
  { idx: 3, short: "Wed" },
  { idx: 4, short: "Thu" },
  { idx: 5, short: "Fri" },
  { idx: 6, short: "Sat" },
  { idx: 0, short: "Sun" },
];

function formatHour(h: number): string {
  return `${String(h).padStart(2, "0")}:00`;
}

const HOURS = Array.from({ length: 24 }, (_, i) => i);

// Curated timezone list grouped by region
const TIMEZONES = [
  "UTC",
  "America/New_York",
  "America/Chicago",
  "America/Denver",
  "America/Los_Angeles",
  "America/Sao_Paulo",
  "America/Argentina/Buenos_Aires",
  "America/Mexico_City",
  "America/Toronto",
  "America/Vancouver",
  "Europe/London",
  "Europe/Paris",
  "Europe/Berlin",
  "Europe/Madrid",
  "Europe/Rome",
  "Europe/Amsterdam",
  "Europe/Stockholm",
  "Europe/Warsaw",
  "Europe/Lisbon",
  "Europe/Moscow",
  "Europe/Istanbul",
  "Africa/Cairo",
  "Africa/Johannesburg",
  "Africa/Lagos",
  "Asia/Dubai",
  "Asia/Kolkata",
  "Asia/Colombo",
  "Asia/Dhaka",
  "Asia/Bangkok",
  "Asia/Singapore",
  "Asia/Shanghai",
  "Asia/Tokyo",
  "Asia/Seoul",
  "Asia/Jakarta",
  "Asia/Karachi",
  "Asia/Riyadh",
  "Australia/Sydney",
  "Australia/Melbourne",
  "Australia/Perth",
  "Pacific/Auckland",
  "Pacific/Honolulu",
];

export function BusinessHoursConfig({ config, onChange, disabled, showToggle = true }: Props) {
  const [open, setOpen] = useState(false);
  const [holidayInput, setHolidayInput] = useState("");

  const update = (patch: Partial<BusinessHoursConfig>) =>
    onChange({ ...config, ...patch });

  const toggleDay = (idx: number) => {
    const next = new Set(config.workDays);
    if (next.has(idx)) next.delete(idx);
    else next.add(idx);
    update({ workDays: next });
  };

  const addHoliday = () => {
    const val = holidayInput.trim();
    if (!val || !/^\d{4}-\d{2}-\d{2}$/.test(val)) return;
    const next = new Set(config.holidays);
    next.add(val);
    update({ holidays: next });
    setHolidayInput("");
  };

  const removeHoliday = (date: string) => {
    const next = new Set(config.holidays);
    next.delete(date);
    update({ holidays: next });
  };

  const sortedHolidays = Array.from(config.holidays).sort();

  // Get browser TZ to show as default hint
  const browserTz = Intl.DateTimeFormat().resolvedOptions().timeZone;
  const tzOptions = Array.from(new Set([browserTz, ...TIMEZONES])).sort();

  const panel = (
    <div className="bh-panel">
      {/* Row 1: Hours + Timezone */}
      <div className="bh-row">
        <label className="bh-label">Business Hours</label>
        <div className="bh-hours-wrap">
          <select
            className="bh-select"
            value={config.startHour}
            onChange={(e) => update({ startHour: parseInt(e.target.value, 10) })}
          >
            {HOURS.map((h) => (
              <option key={h} value={h}>{formatHour(h)}</option>
            ))}
          </select>
          <span className="bh-to">to</span>
          <select
            className="bh-select"
            value={config.endHour}
            onChange={(e) => update({ endHour: parseInt(e.target.value, 10) })}
          >
            {HOURS.map((h) => (
              <option key={h} value={h}>{formatHour(h)}</option>
            ))}
          </select>
        </div>

        <label className="bh-label" style={{ marginLeft: 20 }}>Timezone</label>
        <select
          className="bh-select bh-select--tz"
          value={config.timezone}
          onChange={(e) => update({ timezone: e.target.value })}
        >
          {tzOptions.map((tz) => (
            <option key={tz} value={tz}>{tz}</option>
          ))}
        </select>
      </div>

      {/* Row 2: Work days */}
      <div className="bh-row">
        <label className="bh-label">Work Days</label>
        <div className="bh-days">
          {DAY_LABELS.map(({ idx, short }) => (
            <button
              key={idx}
              className={["bh-day-btn", config.workDays.has(idx) ? "bh-day-btn--on" : ""].filter(Boolean).join(" ")}
              onClick={() => toggleDay(idx)}
            >
              {short}
            </button>
          ))}
        </div>
      </div>

      {/* Row 3: Holidays */}
      <div className="bh-row bh-row--holidays">
        <label className="bh-label">Holidays</label>
        <div className="bh-holiday-input-wrap">
          <input
            type="date"
            className="bh-date-input"
            value={holidayInput}
            onChange={(e) => setHolidayInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && addHoliday()}
          />
          <button className="bh-add-btn" onClick={addHoliday} disabled={!holidayInput}>
            Add
          </button>
        </div>
        {sortedHolidays.length > 0 && (
          <div className="bh-holiday-chips">
            {sortedHolidays.map((date) => (
              <span key={date} className="bh-holiday-chip">
                {date}
                <button
                  className="bh-chip-remove"
                  onClick={() => removeHoliday(date)}
                  aria-label={`Remove ${date}`}
                >
                  ×
                </button>
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );

  if (!showToggle) return panel;

  return (
    <div className="bh-config-root">
      <button
        className={["bh-toggle", open ? "bh-toggle--open" : ""].filter(Boolean).join(" ")}
        onClick={() => setOpen((o) => !o)}
        disabled={disabled}
        title="Configure business hours for compensation calculation"
      >
        <span className="bh-toggle-icon">{open ? "▾" : "▸"}</span>
        Business Hours Config
        {config.holidays.size > 0 && (
          <span className="bh-badge">{config.holidays.size} holiday{config.holidays.size > 1 ? "s" : ""}</span>
        )}
        <span className="bh-summary">
          {formatHour(config.startHour)}–{formatHour(config.endHour)} · {config.timezone}
        </span>
      </button>
      {open && panel}
    </div>
  );
}
