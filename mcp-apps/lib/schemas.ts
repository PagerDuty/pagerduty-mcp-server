import { z } from "zod";

/**
 * PagerDuty Data Schemas
 *
 * Zod schemas matching PagerDuty API response structures.
 * Based on pagerduty-mcp-server Python models.
 */

// Reference schemas for related entities
export const ServiceReferenceSchema = z.object({
  id: z.string(),
  type: z.literal("service_reference"),
  summary: z.string(),
  self: z.string().url().optional(),
  html_url: z.string().url().optional(),
});

export const UserReferenceSchema = z.object({
  id: z.string(),
  type: z.literal("user_reference"),
  summary: z.string(),
  self: z.string().url().optional(),
  html_url: z.string().url().optional(),
});

export const TeamReferenceSchema = z.object({
  id: z.string(),
  type: z.literal("team_reference"),
  summary: z.string(),
  self: z.string().url().optional(),
  html_url: z.string().url().optional(),
});

// Core incident schema
export const IncidentSchema = z.object({
  id: z.string(),
  type: z.literal("incident"),
  incident_number: z.number(),
  status: z.enum(["triggered", "acknowledged", "resolved"]),
  title: z.string(),
  summary: z.string().optional(),
  created_at: z.string(), // ISO 8601 datetime
  updated_at: z.string().optional(),
  resolved_at: z.string().nullable().optional(),
  urgency: z.enum(["high", "low"]),
  priority: z
    .object({
      id: z.string(),
      summary: z.string(),
    })
    .nullish(), // Allow null or undefined (incidents may not have priorities)
  service: ServiceReferenceSchema,
  assignments: z
    .array(
      z.object({
        at: z.string(), // assignment timestamp
        assignee: UserReferenceSchema,
      })
    )
    .optional(),
  acknowledgements: z
    .array(
      z.object({
        at: z.string(),
        acknowledger: UserReferenceSchema,
      })
    )
    .optional(),
  teams: z.array(TeamReferenceSchema).optional(),
  html_url: z.string().url().optional(),
  self: z.string().url().optional(),
});

export const IncidentListSchema = z.object({
  incidents: z.array(IncidentSchema),
  limit: z.number(),
  offset: z.number(),
  total: z.number().nullable().optional(),
  more: z.boolean().nullable().optional(),
});

// Service schema
export const ServiceSchema = z.object({
  id: z.string(),
  type: z.literal("service"),
  name: z.string(),
  description: z.string().optional(),
  status: z.enum(["active", "disabled", "maintenance", "critical", "warning"]),
  teams: z.array(TeamReferenceSchema).optional(),
  html_url: z.string().url().optional(),
  self: z.string().url().optional(),
});

export const ServiceListSchema = z.object({
  services: z.array(ServiceSchema),
  limit: z.number(),
  offset: z.number(),
  total: z.number().nullable().optional(),
  more: z.boolean().nullable().optional(),
});

// Input schemas for tools
export const DashboardInputSchema = z.object({
  timeRange: z.enum(["24h", "7d", "30d"]).optional().default("24h"),
});

// Aggregated data schemas for visualizations
export const TimeSeriesDataPointSchema = z.object({
  timestamp: z.string(), // ISO 8601
  triggered: z.number(),
  acknowledged: z.number(),
  resolved: z.number(),
  total: z.number(),
});

export const ServiceHealthSchema = z.object({
  service_id: z.string(),
  service_name: z.string(),
  incident_count: z.number(),
  high_urgency_count: z.number(),
  low_urgency_count: z.number(),
  avg_resolution_time_minutes: z.number().nullable(),
  status: z.enum(["healthy", "warning", "critical"]),
});

export const UrgencyDistributionSchema = z.object({
  high: z.number(),
  low: z.number(),
  total: z.number(),
  high_percent: z.number(),
  low_percent: z.number(),
});

// Dashboard data schema (returned by get-incident-dashboard)
export const IncidentDashboardDataSchema = z.object({
  summary: z.object({
    total_incidents: z.number(),
    active_incidents: z.number(),
    resolved_today: z.number(),
    avg_resolution_time_minutes: z.number().nullable(),
  }),
  timeline: z.array(TimeSeriesDataPointSchema),
  service_health: z.array(ServiceHealthSchema),
  urgency_distribution: UrgencyDistributionSchema,
  time_range: z.object({
    start: z.string(),
    end: z.string(),
    label: z.string(), // "24h", "7d", "30d"
  }),
  generated_at: z.string(),
});

// Polling data schema (returned by poll-incident-stats)
export const IncidentStatsSchema = z.object({
  timestamp: z.string(),
  active_incidents: z.number(),
  triggered_count: z.number(),
  acknowledged_count: z.number(),
  high_urgency_count: z.number(),
  low_urgency_count: z.number(),
  recent_incidents: z.array(
    z.object({
      id: z.string(),
      incident_number: z.number(),
      title: z.string(),
      status: z.enum(["triggered", "acknowledged", "resolved"]),
      urgency: z.enum(["high", "low"]),
      service_name: z.string(),
      created_at: z.string(),
    })
  ),
});

// Type exports
export type DashboardInput = z.infer<typeof DashboardInputSchema>;
export type Incident = z.infer<typeof IncidentSchema>;
export type IncidentList = z.infer<typeof IncidentListSchema>;
export type Service = z.infer<typeof ServiceSchema>;
export type ServiceList = z.infer<typeof ServiceListSchema>;
export type TimeSeriesDataPoint = z.infer<typeof TimeSeriesDataPointSchema>;
export type ServiceHealth = z.infer<typeof ServiceHealthSchema>;
export type UrgencyDistribution = z.infer<typeof UrgencyDistributionSchema>;
export type IncidentDashboardData = z.infer<
  typeof IncidentDashboardDataSchema
>;
export type IncidentStats = z.infer<typeof IncidentStatsSchema>;
