import type { CreatedResource } from "./types.js";

export const MOCK_TEAMS = [
  { id: "T001", name: "Platform Engineering", summary: "Platform Engineering" },
  { id: "T002", name: "SRE", summary: "SRE" },
];

export const MOCK_USERS = [
  { id: "U001", name: "Alice Johnson", email: "alice@example.com", role: "user" },
  { id: "U002", name: "Bob Smith", email: "bob@example.com", role: "admin" },
];

export const MOCK_SCHEDULES = [
  { id: "S001", name: "Primary On-Call" },
  { id: "S002", name: "Secondary On-Call" },
];

export const MOCK_ESCALATION_POLICIES = [
  { id: "EP001", name: "Default Escalation Policy" },
];

export const MOCK_SERVICES = [
  { id: "SVC001", name: "Payment Service" },
  { id: "SVC002", name: "Auth Service" },
];

export const MOCK_CREATE_TEAM: CreatedResource = {
  type: "Team",
  name: "Mock Team",
  id: "T999",
  status: "success",
};

export const MOCK_CREATE_USER: CreatedResource = {
  type: "User",
  name: "Mock User",
  id: "U999",
  status: "success",
};

export const MOCK_CREATE_SCHEDULE: CreatedResource = {
  type: "Schedule",
  name: "Mock Schedule",
  id: "S999",
  status: "success",
};

export const MOCK_CREATE_EP: CreatedResource = {
  type: "Escalation Policy",
  name: "Mock EP",
  id: "EP999",
  status: "success",
};

export const MOCK_CREATE_SERVICE: CreatedResource = {
  type: "Service",
  name: "Mock Service",
  id: "SVC999",
  status: "success",
};
