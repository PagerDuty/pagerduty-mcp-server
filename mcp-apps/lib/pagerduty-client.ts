/**
 * PagerDuty API Client
 *
 * Wrapper for PagerDuty REST API calls with caching and error handling.
 * Uses the same environment variables as the Python MCP server.
 */

import { cache, TTL } from "./cache.js";
import {
  IncidentListSchema,
  ServiceListSchema,
  type Incident,
  type IncidentList,
  type ServiceList,
} from "./schemas.js";

const PAGERDUTY_API_BASE = "https://api.pagerduty.com";

/**
 * Get PagerDuty API credentials from environment
 */
function getCredentials(): { apiKey: string; userEmail: string } {
  const apiKey = process.env.PAGERDUTY_API_KEY;
  const userEmail = process.env.PAGERDUTY_USER_EMAIL;

  if (!apiKey || !userEmail) {
    throw new Error(
      "Missing PagerDuty credentials. Set PAGERDUTY_API_KEY and PAGERDUTY_USER_EMAIL environment variables."
    );
  }

  return { apiKey, userEmail };
}

/**
 * Make an authenticated request to PagerDuty API
 */
async function makeRequest<T>(
  endpoint: string,
  params: Record<string, any> = {}
): Promise<T> {
  const { apiKey, userEmail } = getCredentials();

  // Build query string
  const queryParams = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      queryParams.append(key, String(value));
    }
  });

  const url = `${PAGERDUTY_API_BASE}${endpoint}${queryParams.toString() ? `?${queryParams}` : ""}`;

  console.log(`[PagerDuty API] GET ${endpoint}`);

  const response = await fetch(url, {
    headers: {
      Accept: "application/vnd.pagerduty+json;version=2",
      Authorization: `Token token=${apiKey}`,
      From: userEmail,
    },
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(
      `PagerDuty API error (${response.status}): ${errorText}`
    );
  }

  return response.json() as Promise<T>;
}

/**
 * List incidents with optional filtering
 */
export async function listIncidents(params: {
  since?: string; // ISO 8601 datetime
  until?: string; // ISO 8601 datetime
  statuses?: string[]; // ["triggered", "acknowledged", "resolved"]
  urgencies?: string[]; // ["high", "low"]
  service_ids?: string[];
  team_ids?: string[];
  limit?: number;
  offset?: number;
}): Promise<IncidentList> {
  const cacheKey = `incidents:${JSON.stringify(params)}`;

  return cache.getOrFetch(
    cacheKey,
    async () => {
      const apiParams: Record<string, any> = {
        ...params,
        limit: params.limit || 100,
        offset: params.offset || 0,
      };

      // Convert arrays to comma-separated strings
      if (params.statuses) {
        apiParams["statuses[]"] = params.statuses;
        delete apiParams.statuses;
      }
      if (params.urgencies) {
        apiParams["urgencies[]"] = params.urgencies;
        delete apiParams.urgencies;
      }
      if (params.service_ids) {
        apiParams["service_ids[]"] = params.service_ids;
        delete apiParams.service_ids;
      }
      if (params.team_ids) {
        apiParams["team_ids[]"] = params.team_ids;
        delete apiParams.team_ids;
      }

      const response = await makeRequest<any>("/incidents", apiParams);

      // Validate response with Zod
      return IncidentListSchema.parse(response);
    },
    TTL.INCIDENTS
  );
}

/**
 * List services
 */
export async function listServices(params: {
  team_ids?: string[];
  limit?: number;
  offset?: number;
}): Promise<ServiceList> {
  const cacheKey = `services:${JSON.stringify(params)}`;

  return cache.getOrFetch(
    cacheKey,
    async () => {
      const apiParams: Record<string, any> = {
        ...params,
        limit: params.limit || 100,
        offset: params.offset || 0,
      };

      if (params.team_ids) {
        apiParams["team_ids[]"] = params.team_ids;
        delete apiParams.team_ids;
      }

      const response = await makeRequest<any>("/services", apiParams);

      // Validate response with Zod
      return ServiceListSchema.parse(response);
    },
    TTL.STATIC
  );
}

/**
 * Get recent incidents for a time range
 */
export async function getRecentIncidents(
  timeRange: "24h" | "7d" | "30d"
): Promise<Incident[]> {
  const now = new Date();
  const since = new Date(now);

  switch (timeRange) {
    case "24h":
      since.setHours(now.getHours() - 24);
      break;
    case "7d":
      since.setDate(now.getDate() - 7);
      break;
    case "30d":
      since.setDate(now.getDate() - 30);
      break;
  }

  const result = await listIncidents({
    since: since.toISOString(),
    until: now.toISOString(),
    limit: 1000, // Get all incidents in range
  });

  return result.incidents;
}

/**
 * Get active incidents (triggered or acknowledged)
 */
export async function getActiveIncidents(): Promise<Incident[]> {
  const result = await listIncidents({
    statuses: ["triggered", "acknowledged"],
    limit: 100,
  });

  return result.incidents;
}

/**
 * Clear all caches
 */
export function clearCache(): void {
  cache.clear();
}

/**
 * Invalidate incident caches
 */
export function invalidateIncidentCache(): void {
  cache.invalidatePattern(/^incidents:/);
}
