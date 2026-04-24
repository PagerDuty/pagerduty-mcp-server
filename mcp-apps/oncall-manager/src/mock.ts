import type {
  CurrentUser,
  EscalationPolicy,
  OnCallShift,
  OverrideDetail,
  Schedule,
  ScheduleDetail,
  ScheduleUser,
} from "./api";

const NOW = new Date();
const D = (offsetDays: number, hour = 9) => {
  const d = new Date(NOW);
  d.setDate(d.getDate() + offsetDays);
  d.setHours(hour, 0, 0, 0);
  return d.toISOString();
};

const ALICE: ScheduleUser = { id: "U001", name: "Alice Chen", email: "alice@example.com" };
const BOB: ScheduleUser = { id: "U002", name: "Bob Kim", email: "bob@example.com" };
const CARLOS: ScheduleUser = { id: "U003", name: "Carlos M.", email: "carlos@example.com" };
const DANA: ScheduleUser = { id: "U004", name: "Dana W.", email: "dana@example.com" };
const ERIC: ScheduleUser = { id: "U005", name: "Eric L.", email: "eric@example.com" };
const FIONA: ScheduleUser = { id: "U006", name: "Fiona R.", email: "fiona@example.com" };

export const MOCK_ONCALL_DATA: {
  currentUser: CurrentUser;
  schedules: Schedule[];
  myShifts: OnCallShift[];
  allShifts: OnCallShift[];
  overridesBySchedule: Record<string, Omit<OverrideDetail, "scheduleId" | "scheduleName">[]>;
  scheduleUsers: Record<string, ScheduleUser[]>;
  scheduleDetails: Record<string, ScheduleDetail>;
  allUsers: ScheduleUser[];
  escalationPolicies: EscalationPolicy[];
} = {
  currentUser: ALICE,

  schedules: [
    { id: "S001", name: "Infra Primary", timeZone: "America/New_York" },
    { id: "S002", name: "Platform On-Call", timeZone: "America/New_York" },
    { id: "S003", name: "Backend Primary", timeZone: "America/Los_Angeles" },
  ],

  myShifts: [
    { scheduleId: "S001", scheduleName: "Infra Primary", userId: "U001", userName: "Alice Chen", start: D(-1), end: D(1), escalationLevel: 1 },
    { scheduleId: "S002", scheduleName: "Platform On-Call", userId: "U001", userName: "Alice Chen", start: D(3), end: D(5), escalationLevel: 1 },
  ],

  allShifts: [
    { scheduleId: "S001", scheduleName: "Infra Primary", userId: "U001", userName: "Alice Chen", start: D(-1), end: D(1), escalationLevel: 1 },
    { scheduleId: "S001", scheduleName: "Infra Primary", userId: "U002", userName: "Bob Kim", start: D(1), end: D(3), escalationLevel: 1 },
    { scheduleId: "S002", scheduleName: "Platform On-Call", userId: "U004", userName: "Dana W.", start: D(0), end: D(2), escalationLevel: 1 },
    { scheduleId: "S002", scheduleName: "Platform On-Call", userId: "U001", userName: "Alice Chen", start: D(3), end: D(5), escalationLevel: 1 },
    { scheduleId: "S003", scheduleName: "Backend Primary", userId: "U003", userName: "Carlos M.", start: D(2), end: D(4), escalationLevel: 1 },
    { scheduleId: "S003", scheduleName: "Backend Primary", userId: "U006", userName: "Fiona R.", start: D(5), end: D(7), escalationLevel: 1 },
  ],

  overridesBySchedule: {
    S001: [
      { id: "OR001", start: D(2), end: D(3), user: { id: "U002", name: "Bob Kim" } },
    ],
    S002: [],
    S003: [
      { id: "OR002", start: D(5), end: D(6), user: { id: "U001", name: "Alice Chen" } },
    ],
  },

  scheduleUsers: {
    S001: [ALICE, BOB, CARLOS],
    S002: [ALICE, DANA, ERIC],
    S003: [CARLOS, BOB, FIONA],
  },

  scheduleDetails: {
    S001: {
      id: "S001",
      name: "Infra Primary",
      description: "Primary on-call rotation for infrastructure incidents",
      timeZone: "America/New_York",
      allUsers: [ALICE, BOB, CARLOS],
      layers: [
        {
          id: "L001",
          name: "Weekly Rotation",
          rotationSeconds: 604800,
          rotationVirtualStart: D(-7),
          start: D(-30),
          end: null,
          restrictions: null,
          users: [ALICE, BOB, CARLOS],
        },
      ],
    },
    S002: {
      id: "S002",
      name: "Platform On-Call",
      description: null,
      timeZone: "America/New_York",
      allUsers: [ALICE, DANA, ERIC],
      layers: [
        {
          id: "L002",
          name: "Weekly Rotation",
          rotationSeconds: 604800,
          rotationVirtualStart: D(-7),
          start: D(-30),
          end: null,
          restrictions: null,
          users: [ALICE, DANA, ERIC],
        },
      ],
    },
    S003: {
      id: "S003",
      name: "Backend Primary",
      description: "Backend team rotation",
      timeZone: "America/Los_Angeles",
      allUsers: [CARLOS, BOB, FIONA],
      layers: [
        {
          id: "L003",
          name: "Weekly Rotation",
          rotationSeconds: 604800,
          rotationVirtualStart: D(-7),
          start: D(-30),
          end: null,
          restrictions: null,
          users: [CARLOS, BOB, FIONA],
        },
      ],
    },
  },

  allUsers: [ALICE, BOB, CARLOS, DANA, ERIC, FIONA],

  escalationPolicies: [
    {
      id: "EP001",
      name: "Infra Escalation Policy",
      description: "Escalation for infrastructure incidents",
      num_loops: 2,
      escalation_rules: [
        {
          id: "ER001",
          escalation_delay_in_minutes: 30,
          targets: [
            { id: "U001", type: "user_reference", summary: "Alice Chen" },
            { id: "S001", type: "schedule_reference", summary: "Infra Primary" },
          ],
        },
        {
          id: "ER002",
          escalation_delay_in_minutes: 60,
          targets: [
            { id: "U004", type: "user_reference", summary: "Dana W." },
          ],
        },
      ],
      services: [{ id: "SVC001", summary: "Payment Service" }],
      teams: [{ id: "T001", summary: "Infrastructure" }],
    },
    {
      id: "EP002",
      name: "Platform Escalation",
      description: null,
      num_loops: 1,
      escalation_rules: [
        {
          id: "ER003",
          escalation_delay_in_minutes: 15,
          targets: [
            { id: "S002", type: "schedule_reference", summary: "Platform On-Call" },
          ],
        },
      ],
      services: [],
      teams: [{ id: "T002", summary: "Platform" }],
    },
  ],
};
