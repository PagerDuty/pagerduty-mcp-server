// src/fairness.ts

import type { UserCompensationRecord } from "./api";
import type { FairnessConfig } from "./config";

export type FairnessStatus = "ok" | "near" | "over";

export interface FairnessRecord extends UserCompensationRecord {
  estimatedPay: number;
  weekendCapPct: number;
  holidayCapPct: number;
  oohPeriodsCapPct: number;
  fairnessStatus: FairnessStatus;
}

export function deriveFairnessRecords(
  records: (UserCompensationRecord & { estimatedPay: number })[],
  cfg: FairnessConfig,
): FairnessRecord[] {
  return records.map((r) => {
    const weekendCapPct = cfg.maxWeekendsPerPeriod > 0
      ? r.weekendPeriodCount / cfg.maxWeekendsPerPeriod
      : 0;
    const holidayCapPct = cfg.maxHolidaysPerPeriod > 0
      ? r.holidayCount / cfg.maxHolidaysPerPeriod
      : 0;
    const oohPeriodsCapPct = cfg.maxOohPeriodsPerPeriod > 0
      ? r.uniquePeriodsOutside / cfg.maxOohPeriodsPerPeriod
      : 0;

    let fairnessStatus: FairnessStatus = "ok";
    if (weekendCapPct > 1 || holidayCapPct > 1 || oohPeriodsCapPct > 1) {
      fairnessStatus = "over";
    } else if (
      weekendCapPct >= cfg.nearLimitThreshold ||
      holidayCapPct >= cfg.nearLimitThreshold ||
      oohPeriodsCapPct >= cfg.nearLimitThreshold
    ) {
      fairnessStatus = "near";
    }

    return { ...r, weekendCapPct, holidayCapPct, oohPeriodsCapPct, fairnessStatus };
  });
}
