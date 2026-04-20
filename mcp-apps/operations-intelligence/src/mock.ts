import type { OpsData } from "./api";

export const MOCK_OPS_DATA: OpsData = {
  teams: [
    { id: "T1", name: "Platform" },
    { id: "T2", name: "Backend" },
    { id: "T3", name: "Frontend" },
  ],
  selectedTeam: null,
  since: "2026-03-21T00:00:00.000Z",
  until: "2026-04-20T23:59:59.000Z",
  totalIncidents: 47,
  mttaMinutes: 8,
  mttrMinutes: 94,
  escalationRate: 12,
  uptimePct: 99.2,
  serviceMetrics: [
    { id: "S1", name: "api-gateway",         teamName: "Platform", totalIncidents: 12, mttaMinutes: 6,  mttrMinutes: 72,  escalationCount: 2, uptimePct: 99.5 },
    { id: "S2", name: "auth-service",        teamName: "Backend",  totalIncidents: 9,  mttaMinutes: 11, mttrMinutes: 140, escalationCount: 3, uptimePct: 98.9 },
    { id: "S3", name: "payment-processor",   teamName: "Backend",  totalIncidents: 15, mttaMinutes: 5,  mttrMinutes: 55,  escalationCount: 1, uptimePct: 99.8 },
    { id: "S4", name: "user-dashboard",      teamName: "Frontend", totalIncidents: 6,  mttaMinutes: 14, mttrMinutes: 180, escalationCount: 2, uptimePct: 97.3 },
    { id: "S5", name: "notification-worker", teamName: "Platform", totalIncidents: 5,  mttaMinutes: 9,  mttrMinutes: 60,  escalationCount: 0, uptimePct: 99.1 },
  ],
  teamMetrics: [
    { id: "T1", name: "Platform", totalIncidents: 17, mttaMinutes: 7,  mttrMinutes: 66,  escalationCount: 2, totalInterruptions: 8,  uptimePct: 99.3 },
    { id: "T2", name: "Backend",  totalIncidents: 24, mttaMinutes: 9,  mttrMinutes: 107, escalationCount: 4, totalInterruptions: 15, uptimePct: 99.1 },
    { id: "T3", name: "Frontend", totalIncidents: 6,  mttaMinutes: 14, mttrMinutes: 180, escalationCount: 0, totalInterruptions: 3,  uptimePct: 97.3 },
  ],
  responderMetrics: [
    { id: "R1", name: "Alice Chen",   teamName: "Platform", onCallHours: 168, totalIncidents: 11, totalAcks: 10, sleepInterruptions: 2, engagedMinutes: 240 },
    { id: "R2", name: "Bob Martinez", teamName: "Backend",  onCallHours: 120, totalIncidents: 14, totalAcks: 13, sleepInterruptions: 4, engagedMinutes: 380 },
    { id: "R3", name: "Carol Park",   teamName: "Backend",  onCallHours: 96,  totalIncidents: 10, totalAcks: 9,  sleepInterruptions: 1, engagedMinutes: 210 },
    { id: "R4", name: "Dave Kim",     teamName: "Frontend", onCallHours: 72,  totalIncidents: 6,  totalAcks: 6,  sleepInterruptions: 0, engagedMinutes: 150 },
    { id: "R5", name: "Eve Johnson",  teamName: "Platform", onCallHours: 144, totalIncidents: 6,  totalAcks: 5,  sleepInterruptions: 1, engagedMinutes: 90  },
  ],
};

export const MOCK_INSIGHT_RESPONSES: Record<string, string> = {
  "MTTA & MTTR Trends": "MTTA improved 18% this period, averaging 8 min across all teams. MTTR remains elevated at 94 min driven by Backend (107 min). auth-service is the outlier at 140 min — a DB migration in week 2 caused a spike that inflated the mean. Platform shows the most consistent response times.",
  "Noisiest Services": "payment-processor led with 15 incidents but resolved fastest (55 min MTTR, 99.8% uptime) — high volume, low impact. auth-service (9 incidents, 140 min MTTR) poses the biggest risk: 3 escalations and sub-99% uptime. user-dashboard has the worst uptime at 97.3% despite only 6 incidents.",
  "Team & Responder Load": "Backend carries the highest load: 24 incidents, 15 interruptions, Bob Martinez with 4 sleep-hour interruptions. Platform is well-distributed. Frontend's low volume (6 incidents) suggests either strong reliability or under-alerting — worth validating coverage. Consider redistributing Backend on-call to reduce Bob's sleep interruption count.",
};
