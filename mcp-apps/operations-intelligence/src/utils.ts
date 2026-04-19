/** Format a minute value as "Xm" (<60), "Xh" (exact hours), or "Xh Ym". Returns "—" for null. */
export function fmtMin(minutes: number | null): string {
  if (minutes === null) return "—";
  if (minutes < 60) return `${minutes}m`;
  const h = Math.floor(minutes / 60);
  const m = minutes % 60;
  return m === 0 ? `${h}h` : `${h}h ${m}m`;
}
