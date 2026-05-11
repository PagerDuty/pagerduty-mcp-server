// src/compliance.ts

import type { UserCompensationRecord } from "./api";
import type { ComplianceConfig } from "./config";

export type ComplianceStatus = "ok" | "near" | "over";

export interface ComplianceRecord extends UserCompensationRecord {
  estimatedPay: number;
  complianceStatus: ComplianceStatus;
  hoursCapPct: number;         // scheduledHours / periodHoursCap (0–∞)
  outsideCapPct: number;       // outsideHours / periodOutsideHoursCap (0–∞)
  consecutiveDaysPct: number;  // maxConsecutiveOnCallDays / maxConsecutiveDays (0 if disabled)
  consecutiveHoursPct: number; // maxConsecutiveOnCallHours / maxConsecutiveHours (0 if disabled)
  restViolation: boolean;      // minRestHours < mandatoryRestHours (false if disabled)
}

export function deriveComplianceRecords(
  records: (UserCompensationRecord & { estimatedPay: number })[],
  cfg: ComplianceConfig,
): ComplianceRecord[] {
  return records.map((r) => {
    // A cap of 0 is treated as "disabled" — no limit enforced for that dimension
    const hoursCapPct = cfg.periodHoursCap > 0
      ? r.scheduledHours / cfg.periodHoursCap
      : 0;
    const outsideCapPct = cfg.periodOutsideHoursCap > 0
      ? r.outsideHours / cfg.periodOutsideHoursCap
      : 0;
    const consecutiveDaysPct = cfg.maxConsecutiveDays > 0
      ? r.maxConsecutiveOnCallDays / cfg.maxConsecutiveDays
      : 0;
    const consecutiveHoursPct = cfg.maxConsecutiveHours > 0
      ? r.maxConsecutiveOnCallHours / cfg.maxConsecutiveHours
      : 0;
    const restViolation = cfg.mandatoryRestHours > 0
      ? r.minRestHours < cfg.mandatoryRestHours
      : false;

    let complianceStatus: ComplianceStatus = "ok";
    if (
      hoursCapPct > 1 ||
      outsideCapPct > 1 ||
      consecutiveDaysPct > 1 ||
      consecutiveHoursPct > 1 ||
      restViolation
    ) {
      complianceStatus = "over";
    } else if (
      hoursCapPct >= cfg.nearLimitThreshold ||
      outsideCapPct >= cfg.nearLimitThreshold ||
      consecutiveDaysPct >= cfg.nearLimitThreshold ||
      consecutiveHoursPct >= cfg.nearLimitThreshold
    ) {
      complianceStatus = "near";
    }

    return {
      ...r,
      complianceStatus,
      hoursCapPct,
      outsideCapPct,
      consecutiveDaysPct,
      consecutiveHoursPct,
      restViolation,
    };
  });
}
