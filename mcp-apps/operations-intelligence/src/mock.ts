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
  aggregated: {
    p50AckSeconds: 240,
    p75AckSeconds: 480,
    p90AckSeconds: 900,
    p95AckSeconds: 1800,
    p50ResolveSeconds: 3600,
    p75ResolveSeconds: 5400,
    p90ResolveSeconds: 9000,
    p95ResolveSeconds: 14400,
  },
  trendsData: {
    points: [
      { weekStart: "2026-03-23", totalIncidents: 9,  mttaMinutes: 11, mttrMinutes: 105, totalInterruptions: 6 },
      { weekStart: "2026-03-30", totalIncidents: 14, mttaMinutes: 9,  mttrMinutes: 98,  totalInterruptions: 9 },
      { weekStart: "2026-04-06", totalIncidents: 12, mttaMinutes: 7,  mttrMinutes: 88,  totalInterruptions: 7 },
      { weekStart: "2026-04-13", totalIncidents: 12, mttaMinutes: 6,  mttrMinutes: 82,  totalInterruptions: 4 },
    ],
  },
  serviceMetrics: [
    { id: "S1", name: "api-gateway",         teamName: "Platform", totalIncidents: 12, mttaMinutes: 6,  mttrMinutes: 72,  escalationCount: 2, uptimePct: 99.5 },
    { id: "S2", name: "auth-service",        teamName: "Backend",  totalIncidents: 9,  mttaMinutes: 11, mttrMinutes: 140, escalationCount: 3, uptimePct: 98.9 },
    { id: "S3", name: "payment-processor",   teamName: "Backend",  totalIncidents: 15, mttaMinutes: 5,  mttrMinutes: 55,  escalationCount: 1, uptimePct: 99.8 },
    { id: "S4", name: "user-dashboard",      teamName: "Frontend", totalIncidents: 6,  mttaMinutes: 14, mttrMinutes: 180, escalationCount: 2, uptimePct: 97.3 },
    { id: "S5", name: "notification-worker", teamName: "Platform", totalIncidents: 5,  mttaMinutes: 9,  mttrMinutes: 60,  escalationCount: 0, uptimePct: 99.1 },
  ],
  teamMetrics: [
    { id: "T1", name: "Platform", totalIncidents: 17, mttaMinutes: 7,  mttrMinutes: 66,  escalationCount: 2, totalInterruptions: 8,  uptimePct: 99.3, businessHourInterruptions: 5, offHourInterruptions: 2, sleepHourInterruptions: 1, meanEngagedMinutes: 45 },
    { id: "T2", name: "Backend",  totalIncidents: 24, mttaMinutes: 9,  mttrMinutes: 107, escalationCount: 4, totalInterruptions: 15, uptimePct: 99.1, businessHourInterruptions: 7, offHourInterruptions: 4, sleepHourInterruptions: 4, meanEngagedMinutes: 82 },
    { id: "T3", name: "Frontend", totalIncidents: 6,  mttaMinutes: 14, mttrMinutes: 180, escalationCount: 0, totalInterruptions: 3,  uptimePct: 97.3, businessHourInterruptions: 2, offHourInterruptions: 1, sleepHourInterruptions: 0, meanEngagedMinutes: 38 },
  ],
  responderMetrics: [
    { id: "R1", name: "Alice Chen",   teamName: "Platform", teamIds: ["T1"], onCallHours: 168, onCallHoursL1: 120, onCallHoursL2Plus: 48,  totalIncidents: 11, totalAcks: 10, sleepInterruptions: 2, engagedMinutes: 240, totalInterruptions: 5,  businessHourInterruptions: 2, offHourInterruptions: 1, meanEngagedMinutes: 22, riskLevel: "medium", oncallShifts: [{ userId: "R1", start: Date.now() - 7*86400000, end: Date.now() - 6*86400000 }, { userId: "R1", start: Date.now() - 3*86400000, end: Date.now() - 1*86400000 }] },
    { id: "R2", name: "Bob Martinez", teamName: "Backend",  teamIds: ["T2"], onCallHours: 120, onCallHoursL1: 120, onCallHoursL2Plus: 0,   totalIncidents: 14, totalAcks: 13, sleepInterruptions: 6, engagedMinutes: 510, totalInterruptions: 12, businessHourInterruptions: 4, offHourInterruptions: 2, meanEngagedMinutes: 36, riskLevel: "high",   oncallShifts: [{ userId: "R2", start: Date.now() - 5*86400000, end: Date.now() - 4*86400000 }] },
    { id: "R3", name: "Carol Park",   teamName: "Backend",  teamIds: ["T2"], onCallHours: 96,  onCallHoursL1: 72,  onCallHoursL2Plus: 24,  totalIncidents: 10, totalAcks: 9,  sleepInterruptions: 1, engagedMinutes: 210, totalInterruptions: 4,  businessHourInterruptions: 2, offHourInterruptions: 1, meanEngagedMinutes: 21, riskLevel: "low",    oncallShifts: [{ userId: "R3", start: Date.now() - 9*86400000, end: Date.now() - 8*86400000 }] },
    { id: "R4", name: "Dave Kim",     teamName: "Frontend", teamIds: ["T3"], onCallHours: 72,  onCallHoursL1: 72,  onCallHoursL2Plus: 0,   totalIncidents: 6,  totalAcks: 6,  sleepInterruptions: 0, engagedMinutes: 150, totalInterruptions: 2,  businessHourInterruptions: 2, offHourInterruptions: 0, meanEngagedMinutes: 25, riskLevel: "low",    oncallShifts: [{ userId: "R4", start: Date.now() - 2*86400000, end: Date.now() - 1*86400000 + 3600000 }] },
    { id: "R5", name: "Eve Johnson",  teamName: "Platform", teamIds: ["T1"], onCallHours: 144, onCallHoursL1: 96,  onCallHoursL2Plus: 48,  totalIncidents: 6,  totalAcks: 5,  sleepInterruptions: 3, engagedMinutes: 490, totalInterruptions: 6,  businessHourInterruptions: 2, offHourInterruptions: 1, meanEngagedMinutes: 82, riskLevel: "high",   oncallShifts: [{ userId: "R5", start: Date.now() - 6*86400000, end: Date.now() - 5*86400000 }, { userId: "R5", start: Date.now() - 1*86400000, end: Date.now() }] },
  ],
};
