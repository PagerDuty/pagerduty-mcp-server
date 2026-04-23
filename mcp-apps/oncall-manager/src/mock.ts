import type { CurrentUser, OnCallShift, Override, Schedule, ScheduleUser } from "./api";

const NOW = new Date();
const D = (offsetDays: number, hour = 9) => {
  const d = new Date(NOW);
  d.setDate(d.getDate() + offsetDays);
  d.setHours(hour, 0, 0, 0);
  return d.toISOString();
};

export const MOCK_ONCALL_DATA: {
  currentUser: CurrentUser;
  schedules: Schedule[];
  myShifts: OnCallShift[];
  allShifts: OnCallShift[];
  overrides: Override[];
  scheduleUsers: Record<string, ScheduleUser[]>;
} = {
  currentUser: { id: "U001", name: "Alice Chen", email: "alice@example.com" },

  schedules: [
    { id: "S001", name: "Infra Primary", timeZone: "America/New_York" },
    { id: "S002", name: "Platform On-Call", timeZone: "America/New_York" },
    { id: "S003", name: "Backend Primary", timeZone: "America/Los_Angeles" },
  ],

  myShifts: [
    // Active now
    { scheduleId: "S001", scheduleName: "Infra Primary", start: D(-1), end: D(1), escalationLevel: 1 },
    // Upcoming in 3 days
    { scheduleId: "S002", scheduleName: "Platform On-Call", start: D(3), end: D(5), escalationLevel: 1 },
  ],

  allShifts: [
    // Alice (current user) — shown in blue
    { scheduleId: "S001", scheduleName: "Infra Primary", start: D(-1), end: D(1), escalationLevel: 1 },
    { scheduleId: "S002", scheduleName: "Platform On-Call", start: D(3), end: D(5), escalationLevel: 1 },
    // Others — shown in grey
    { scheduleId: "S001", scheduleName: "Infra Primary", start: D(1), end: D(3), escalationLevel: 1 },
    { scheduleId: "S002", scheduleName: "Platform On-Call", start: D(0), end: D(2), escalationLevel: 1 },
    { scheduleId: "S003", scheduleName: "Backend Primary", start: D(2), end: D(4), escalationLevel: 1 },
    { scheduleId: "S003", scheduleName: "Backend Primary", start: D(5), end: D(7), escalationLevel: 1 },
  ],

  overrides: [
    {
      id: "OR001",
      scheduleId: "S001",
      scheduleName: "Infra Primary",
      userId: "U002",
      userName: "Bob Kim",
      start: D(2),
      end: D(3),
    },
    {
      id: "OR002",
      scheduleId: "S003",
      scheduleName: "Backend Primary",
      userId: "U001",
      userName: "Alice Chen",
      start: D(5),
      end: D(6),
    },
  ],

  scheduleUsers: {
    S001: [
      { id: "U001", name: "Alice Chen", email: "alice@example.com" },
      { id: "U002", name: "Bob Kim", email: "bob@example.com" },
      { id: "U003", name: "Carlos M.", email: "carlos@example.com" },
    ],
    S002: [
      { id: "U001", name: "Alice Chen", email: "alice@example.com" },
      { id: "U004", name: "Dana W.", email: "dana@example.com" },
      { id: "U005", name: "Eric L.", email: "eric@example.com" },
    ],
    S003: [
      { id: "U003", name: "Carlos M.", email: "carlos@example.com" },
      { id: "U002", name: "Bob Kim", email: "bob@example.com" },
      { id: "U006", name: "Fiona R.", email: "fiona@example.com" },
    ],
  },
};
