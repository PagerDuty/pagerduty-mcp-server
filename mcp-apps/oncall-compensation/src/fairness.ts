// src/fairness.ts

import type { UserCompensationRecord } from "./api";
import type { FairnessConfig } from "./config";

export interface TeamFairness {
  teamId: string;
  teamName: string;
  memberCount: number;
  avgHours: number;
  stdDev: number;
  outlierCount: number;
  equityScore: number; // 0–100
}

export interface FairnessData {
  globalAvgHours: number;
  globalStdDev: number;
  globalEquityScore: number;
  outliers: (UserCompensationRecord & { multiplierVsAvg: number })[];
  teams: TeamFairness[];
}

function stdDev(values: number[]): number {
  if (values.length === 0) return 0;
  const mean = values.reduce((s, v) => s + v, 0) / values.length;
  const variance = values.reduce((s, v) => s + (v - mean) ** 2, 0) / values.length;
  return Math.sqrt(variance);
}

function equityScore(mean: number, sd: number): number {
  if (mean === 0) return 100;
  return Math.max(0, Math.min(100, Math.round(100 - (sd / mean) * 100)));
}

export function computeFairnessData(
  records: UserCompensationRecord[],
  cfg: FairnessConfig,
): FairnessData {
  if (records.length === 0) {
    return { globalAvgHours: 0, globalStdDev: 0, globalEquityScore: 100, outliers: [], teams: [] };
  }

  const allHours = records.map((r) => r.scheduledHours);
  const globalAvg = allHours.reduce((s, v) => s + v, 0) / allHours.length;
  const globalSd = stdDev(allHours);

  const outliers = records
    .filter((r) => globalAvg > 0 && r.scheduledHours >= cfg.outlierMultiplier * globalAvg)
    .map((r) => ({
      ...r,
      multiplierVsAvg: globalAvg > 0 ? Math.round((r.scheduledHours / globalAvg) * 10) / 10 : 0,
    }))
    .sort((a, b) => b.scheduledHours - a.scheduledHours);

  // Group by primary teamId
  const teamMap = new Map<string, { name: string; members: UserCompensationRecord[] }>();
  for (const r of records) {
    const tid = r.teamId ?? "__none__";
    const tname = r.teamName ?? "No Team";
    if (!teamMap.has(tid)) teamMap.set(tid, { name: tname, members: [] });
    teamMap.get(tid)!.members.push(r);
  }

  const teams: TeamFairness[] = Array.from(teamMap.entries()).map(([teamId, { name, members }]) => {
    const hours = members.map((m) => m.scheduledHours);
    const avg = hours.reduce((s, v) => s + v, 0) / hours.length;
    const sd = stdDev(hours);
    const outlierCount = members.filter(
      (m) => avg > 0 && m.scheduledHours >= cfg.outlierMultiplier * avg,
    ).length;
    return {
      teamId,
      teamName: name,
      memberCount: members.length,
      avgHours: Math.round(avg * 10) / 10,
      stdDev: Math.round(sd * 10) / 10,
      outlierCount,
      equityScore: equityScore(avg, sd),
    };
  });

  teams.sort((a, b) => a.equityScore - b.equityScore);

  return {
    globalAvgHours: Math.round(globalAvg * 10) / 10,
    globalStdDev: Math.round(globalSd * 10) / 10,
    globalEquityScore: equityScore(globalAvg, globalSd),
    outliers,
    teams,
  };
}
