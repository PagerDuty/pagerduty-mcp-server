// src/compensation.ts

import type { UserCompensationRecord } from "./api";
import type { PayConfig } from "./config";

export function computeEstimatedPay(
  r: UserCompensationRecord,
  cfg: PayConfig,
): number {
  // outsideHours = weekendHours + holidayHours + off-hours weekday time
  // insideHours = all scheduled time that is NOT outside
  const insideHours = Math.max(
    0,
    r.scheduledHours - r.outsideHours - r.weekendHours - r.holidayHours,
  );

  const pay =
    insideHours * cfg.l1RatePerHour +
    r.outsideHours * cfg.l1RatePerHour * cfg.offHoursMultiplier +
    r.weekendHours * cfg.l1RatePerHour * cfg.weekendMultiplier +
    r.holidayHours * cfg.l1RatePerHour * cfg.holidayMultiplier +
    r.scheduledHoursL2Plus * cfg.l2PlusRatePerHour;

  return Math.round(pay * 100) / 100;
}
