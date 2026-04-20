import type { IncidentSummary, IncidentTimeline } from "./api";

export const MOCK_INCIDENTS: IncidentSummary[] = [
  {
    id: "INC001", number: 801,
    title: "API Gateway 5xx spike — elevated error rate",
    status: "resolved", urgency: "high",
    createdAt: "2026-04-18T02:14:33Z", resolvedAt: "2026-04-18T03:47:21Z",
    serviceName: "api-gateway", priority: "P1",
    assignees: ["Alice Chen"], alertCount: 3,
  },
  {
    id: "INC002", number: 798,
    title: "Auth service latency degradation",
    status: "resolved", urgency: "high",
    createdAt: "2026-04-15T14:22:07Z", resolvedAt: "2026-04-15T15:58:44Z",
    serviceName: "auth-service", priority: "P2",
    assignees: ["Bob Martinez", "Carol Park"], alertCount: 2,
  },
  {
    id: "INC003", number: 795,
    title: "Payment processor timeout errors",
    status: "resolved", urgency: "low",
    createdAt: "2026-04-12T09:05:12Z", resolvedAt: "2026-04-12T09:41:55Z",
    serviceName: "payment-processor", priority: null,
    assignees: ["Bob Martinez"], alertCount: 1,
  },
];

export const MOCK_TIMELINE: IncidentTimeline = {
  incident: MOCK_INCIDENTS[0]!,
  events: [
    { id: "E1", kind: "trigger",     timestamp: "2026-04-18T02:14:33Z", summary: "Triggered: API Gateway 5xx spike",     detail: null,                                                                                                                                   actor: "PagerDuty",  link: null },
    { id: "E2", kind: "alert",       timestamp: "2026-04-18T02:14:35Z", summary: "Alert: api-gateway-5xx-rate",          detail: "Severity: critical · Status: triggered\n{\"error_rate\": 0.42, \"threshold\": 0.05, \"window\": \"5m\"}",                              actor: "api-gateway", link: null },
    { id: "E3", kind: "acknowledge", timestamp: "2026-04-18T02:19:07Z", summary: "Acknowledged by Alice Chen",           detail: null,                                                                                                                                   actor: "Alice Chen", link: null },
    { id: "E4", kind: "note",        timestamp: "2026-04-18T02:24:51Z", summary: "Note added",                          detail: "Investigating elevated 5xx on api-gateway. Error rate at 42%. Checking recent deploys and DB connection pool.",                           actor: "Alice Chen", link: null },
    { id: "E5", kind: "change",      timestamp: "2026-04-18T02:31:00Z", summary: "Deploy: api-gateway v2.4.1",          detail: "{\"commit\": \"a3f9c12\", \"deployer\": \"ci-bot\", \"environment\": \"production\"}",                                                  actor: "ci-bot",     link: null },
    { id: "E6", kind: "escalation",  timestamp: "2026-04-18T02:45:00Z", summary: "Escalated to on-call lead",           detail: null,                                                                                                                                   actor: "Alice Chen", link: null },
    { id: "E7", kind: "note",        timestamp: "2026-04-18T03:10:18Z", summary: "Note added",                          detail: "Root cause identified: DB connection pool exhausted after traffic surge. Rolling back connection limit change from yesterday's config update.", actor: "Alice Chen", link: null },
    { id: "E8", kind: "resolve",     timestamp: "2026-04-18T03:47:21Z", summary: "Resolved by Alice Chen",              detail: null,                                                                                                                                   actor: "Alice Chen", link: null },
  ],
};
