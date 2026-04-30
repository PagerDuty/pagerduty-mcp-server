// src/compliance.ts

import type { UserCompensationRecord } from "./api";
import type { ComplianceConfig } from "./config";

export type ComplianceStatus = "ok" | "near" | "over";

export interface ComplianceRecord extends UserCompensationRecord {
  estimatedPay: number;
  complianceStatus: ComplianceStatus;
  hoursCapPct: number;       // scheduledHours / periodHoursCap (0–∞)
  outsideCapPct: number;     // outsideHours / periodOutsideHoursCap (0–∞)
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

    // nearLimitThreshold is expected to be in (0, 1); values >= 1 would make "over" unreachable
    let complianceStatus: ComplianceStatus = "ok";
    if (hoursCapPct > 1 || outsideCapPct > 1) {
      complianceStatus = "over";
    } else if (hoursCapPct >= cfg.nearLimitThreshold || outsideCapPct >= cfg.nearLimitThreshold) {
      complianceStatus = "near";
    }

    return { ...r, complianceStatus, hoursCapPct, outsideCapPct };
  });
}
