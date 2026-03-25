/**
 * Business hours computation for the Oncall Compensation Report.
 *
 * Given raw on-call shift windows and a business hours configuration,
 * computes how many hours fell outside business hours (off-hours, weekends,
 * holidays) and derives metrics like max consecutive outside period and unique
 * outside periods. All time zone conversions use the Intl API — no library needed.
 */

export interface BusinessHoursConfig {
  startHour: number;     // 0–23, e.g. 9 = 09:00 (inclusive)
  endHour: number;       // 0–23, e.g. 18 = 18:00 (exclusive)
  workDays: Set<number>; // 0=Sun, 1=Mon, …, 6=Sat
  holidays: Set<string>; // "YYYY-MM-DD" in the configured timezone
  timezone: string;      // IANA timezone identifier
}

export interface OncallShift {
  userId: string;
  start: number; // UTC ms
  end: number;   // UTC ms
}

export interface OutsideHoursMetrics {
  totalOutsideHours: number;
  totalWeekendHours: number;
  totalHolidayHours: number;
  maxConsecutiveOutsideHours: number;
  uniquePeriodsOutside: number;
}

export function defaultBHConfig(): BusinessHoursConfig {
  return {
    startHour: 9,
    endHour: 18,
    workDays: new Set([1, 2, 3, 4, 5]),
    holidays: new Set(),
    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
  };
}

// ---------------------------------------------------------------------------
// Timezone helpers
// ---------------------------------------------------------------------------

interface DateParts {
  year: number;
  month: number;  // 1–12
  day: number;
  hour: number;   // 0–23
  minute: number;
  weekday: number; // 0=Sun … 6=Sat
  dateStr: string; // "YYYY-MM-DD"
}

const WEEKDAY_MAP: Record<string, number> = {
  Sun: 0, Mon: 1, Tue: 2, Wed: 3, Thu: 4, Fri: 5, Sat: 6,
};

function getPartsInTz(ms: number, tz: string): DateParts {
  const parts = new Intl.DateTimeFormat("en-US", {
    timeZone: tz,
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
    weekday: "short",
  }).formatToParts(new Date(ms));

  const get = (type: string): string =>
    parts.find((p) => p.type === type)?.value ?? "0";

  const year = parseInt(get("year"), 10);
  const month = parseInt(get("month"), 10);
  const day = parseInt(get("day"), 10);
  const hourRaw = parseInt(get("hour"), 10);
  const hour = hourRaw === 24 ? 0 : hourRaw; // some locales emit 24 for midnight
  const minute = parseInt(get("minute"), 10);

  return {
    year, month, day, hour, minute,
    weekday: WEEKDAY_MAP[get("weekday").slice(0, 3)] ?? 0,
    dateStr: `${year}-${String(month).padStart(2, "0")}-${String(day).padStart(2, "0")}`,
  };
}

/**
 * Approximate UTC ms for a given local date+time in a timezone.
 * Accurate to within seconds; handles DST via a two-pass correction.
 */
function localToUTC(
  y: number, mo: number, d: number,
  h: number, min: number,
  tz: string,
): number {
  const roughMs = Date.UTC(y, mo - 1, d, h, min);
  const p = getPartsInTz(roughMs, tz);
  const localMs = Date.UTC(p.year, p.month - 1, p.day, p.hour, p.minute);
  const corrected = roughMs + (roughMs - localMs);

  // Second pass to handle DST edge cases
  const p2 = getPartsInTz(corrected, tz);
  if (p2.year === y && p2.month === mo && p2.day === d && p2.hour === h) {
    return corrected;
  }
  const localMs2 = Date.UTC(p2.year, p2.month - 1, p2.day, p2.hour, p2.minute);
  return corrected + (corrected - localMs2);
}

function midnightUTC(dateStr: string, tz: string): number {
  const [y, m, d] = dateStr.split("-").map(Number);
  return localToUTC(y!, m!, d!, 0, 0, tz);
}

/**
 * Return all local calendar date strings "YYYY-MM-DD" that overlap [startMs, endMs).
 * Samples every 6 hours — safe because a calendar day is always ≥ 23 h.
 */
function getDaysInRange(startMs: number, endMs: number, tz: string): string[] {
  const seen = new Set<string>();
  const result: string[] = [];
  let t = startMs;
  while (t <= endMs) {
    const { dateStr } = getPartsInTz(t, tz);
    if (!seen.has(dateStr)) {
      seen.add(dateStr);
      result.push(dateStr);
    }
    t += 6 * 3_600_000;
  }
  // Ensure the last partial hour is captured
  const { dateStr: last } = getPartsInTz(endMs - 1, tz);
  if (!seen.has(last)) result.push(last);
  return result;
}

// ---------------------------------------------------------------------------
// Segment computation
// ---------------------------------------------------------------------------

interface Segment {
  start: number;
  end: number;
  category: "off-hours" | "weekend" | "holiday";
}

function shiftToOutsideSegments(
  shiftStart: number,
  shiftEnd: number,
  config: BusinessHoursConfig,
): Segment[] {
  const segments: Segment[] = [];

  for (const dateStr of getDaysInRange(shiftStart, shiftEnd, config.timezone)) {
    const [y, m, d] = dateStr.split("-").map(Number);

    // Compute this day's UTC boundaries in the target timezone
    const dayStartMs = midnightUTC(dateStr, config.timezone);
    // Next midnight: advance to noon, then compute next-day midnight
    const noonMs = localToUTC(y!, m!, d!, 12, 0, config.timezone);
    const nextDayStr = getPartsInTz(noonMs + 24 * 3_600_000, config.timezone).dateStr;
    const dayEndMs = midnightUTC(nextDayStr, config.timezone);

    // Clamp to shift boundaries
    const segStart = Math.max(dayStartMs, shiftStart);
    const segEnd = Math.min(dayEndMs, shiftEnd);
    if (segStart >= segEnd) continue;

    // Weekday is determined from noon (DST-safe)
    const { weekday } = getPartsInTz(noonMs, config.timezone);

    if (config.holidays.has(dateStr)) {
      segments.push({ start: segStart, end: segEnd, category: "holiday" });
    } else if (!config.workDays.has(weekday)) {
      segments.push({ start: segStart, end: segEnd, category: "weekend" });
    } else {
      // Workday: emit only the portions outside the business window
      const bizStart = localToUTC(y!, m!, d!, config.startHour, 0, config.timezone);
      const bizEnd = localToUTC(y!, m!, d!, config.endHour, 0, config.timezone);

      if (segStart < bizStart) {
        segments.push({
          start: segStart,
          end: Math.min(segEnd, bizStart),
          category: "off-hours",
        });
      }
      if (segEnd > bizEnd) {
        segments.push({
          start: Math.max(segStart, bizEnd),
          end: segEnd,
          category: "off-hours",
        });
      }
    }
  }

  return segments;
}

function mergeSegments(segs: Segment[]): Segment[] {
  if (segs.length === 0) return [];
  const sorted = [...segs].sort((a, b) => a.start - b.start);
  const merged: Segment[] = [{ ...sorted[0]! }];
  for (let i = 1; i < sorted.length; i++) {
    const last = merged[merged.length - 1]!;
    const curr = sorted[i]!;
    if (curr.start <= last.end) {
      last.end = Math.max(last.end, curr.end);
    } else {
      merged.push({ ...curr });
    }
  }
  return merged;
}

/** Merge overlapping shifts for one user to avoid double-counting. */
function mergeShifts(shifts: OncallShift[]): OncallShift[] {
  if (shifts.length === 0) return [];
  const sorted = [...shifts].sort((a, b) => a.start - b.start);
  const merged: OncallShift[] = [{ ...sorted[0]! }];
  for (let i = 1; i < sorted.length; i++) {
    const last = merged[merged.length - 1]!;
    const curr = sorted[i]!;
    if (curr.start <= last.end) {
      last.end = Math.max(last.end, curr.end);
    } else {
      merged.push({ ...curr });
    }
  }
  return merged;
}

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

export function computeOutsideHoursMetrics(
  rawShifts: OncallShift[],
  config: BusinessHoursConfig,
): OutsideHoursMetrics {
  if (rawShifts.length === 0) {
    return {
      totalOutsideHours: 0,
      totalWeekendHours: 0,
      totalHolidayHours: 0,
      maxConsecutiveOutsideHours: 0,
      uniquePeriodsOutside: 0,
    };
  }

  const shifts = mergeShifts(rawShifts);
  const allSegs: Segment[] = [];
  let weekendMs = 0;
  let holidayMs = 0;

  for (const shift of shifts) {
    for (const seg of shiftToOutsideSegments(shift.start, shift.end, config)) {
      allSegs.push(seg);
      if (seg.category === "weekend") weekendMs += seg.end - seg.start;
      else if (seg.category === "holiday") holidayMs += seg.end - seg.start;
    }
  }

  const merged = mergeSegments(allSegs);
  const totalMs = merged.reduce((s, seg) => s + seg.end - seg.start, 0);
  const maxMs = merged.reduce((m, seg) => Math.max(m, seg.end - seg.start), 0);
  const h = (ms: number) => Math.round((ms / 3_600_000) * 100) / 100;

  return {
    totalOutsideHours: h(totalMs),
    totalWeekendHours: h(weekendMs),
    totalHolidayHours: h(holidayMs),
    maxConsecutiveOutsideHours: h(maxMs),
    uniquePeriodsOutside: merged.length,
  };
}
