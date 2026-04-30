// src/config.ts

import { defaultBHConfig } from "./businessHours";
import type { BusinessHoursConfig } from "./businessHours";

export interface PayConfig {
  l1RatePerHour: number;
  l2PlusRatePerHour: number;
  offHoursMultiplier: number;
  weekendMultiplier: number;
  holidayMultiplier: number;
}

export interface ComplianceConfig {
  periodHoursCap: number;
  periodOutsideHoursCap: number;
  nearLimitThreshold: number; // 0–1, e.g. 0.9 = 90%
}

export interface FairnessConfig {
  outlierMultiplier: number;
}

export interface AllSettings {
  pay: PayConfig;
  compliance: ComplianceConfig;
  fairness: FairnessConfig;
  businessHours: BusinessHoursConfig;
}

export function defaultPayConfig(): PayConfig {
  return {
    l1RatePerHour: 20,
    l2PlusRatePerHour: 15,
    offHoursMultiplier: 1.5,
    weekendMultiplier: 2.0,
    holidayMultiplier: 2.5,
  };
}

export function defaultComplianceConfig(): ComplianceConfig {
  return {
    periodHoursCap: 160,
    periodOutsideHoursCap: 60,
    nearLimitThreshold: 0.9,
  };
}

export function defaultFairnessConfig(): FairnessConfig {
  return { outlierMultiplier: 2.0 };
}

export function defaultAllSettings(): AllSettings {
  return {
    pay: defaultPayConfig(),
    compliance: defaultComplianceConfig(),
    fairness: defaultFairnessConfig(),
    businessHours: defaultBHConfig(),
  };
}

const STORAGE_KEY = "oncall-compliance-settings";

function serializeBH(bh: BusinessHoursConfig): object {
  return {
    startHour: bh.startHour,
    endHour: bh.endHour,
    timezone: bh.timezone,
    workDays: Array.from(bh.workDays),
    holidays: Array.from(bh.holidays).sort(),
  };
}

function deserializeBH(raw: any): BusinessHoursConfig {
  const toHour = (v: unknown, fallback: number): number => {
    const n = Number(v);
    return Number.isFinite(n) ? n : fallback;
  };
  return {
    startHour: toHour(raw.startHour, 9),
    endHour: toHour(raw.endHour, 18),
    timezone: String(raw.timezone ?? Intl.DateTimeFormat().resolvedOptions().timeZone),
    workDays: new Set<number>(
      Array.isArray(raw.workDays)
        ? raw.workDays.map(Number).filter(Number.isFinite)
        : [1, 2, 3, 4, 5],
    ),
    holidays: new Set<string>(Array.isArray(raw.holidays) ? raw.holidays.map(String) : []),
  };
}

export function loadSettings(): AllSettings {
  const defaults = defaultAllSettings();
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return defaults;
    const parsed = JSON.parse(raw);
    return {
      pay: { ...defaults.pay, ...parsed.pay },
      compliance: { ...defaults.compliance, ...parsed.compliance },
      fairness: { ...defaults.fairness, ...parsed.fairness },
      businessHours: parsed.businessHours
        ? deserializeBH(parsed.businessHours)
        : defaults.businessHours,
    };
  } catch (e) {
    console.warn("[config] Failed to load settings from localStorage, using defaults:", e);
    return defaults;
  }
}

export function saveSettings(s: AllSettings): void {
  localStorage.setItem(
    STORAGE_KEY,
    JSON.stringify({
      pay: s.pay,
      compliance: s.compliance,
      fairness: s.fairness,
      businessHours: serializeBH(s.businessHours),
    }),
  );
}
