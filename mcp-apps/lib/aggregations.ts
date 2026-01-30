/**
 * Data Aggregation Functions
 *
 * Server-side calculations for dashboard metrics:
 * - Time-series bucketing
 * - Service health aggregation
 * - MTTR calculations
 * - Urgency distribution
 */

import type {
  Incident,
  Service,
  TimeSeriesDataPoint,
  ServiceHealth,
  UrgencyDistribution,
  IncidentDashboardData,
  IncidentStats,
} from "./schemas.js";

/**
 * Aggregate incidents into time-series buckets
 */
export function aggregateIncidentTimeline(
  incidents: Incident[],
  bucketSize: "hour" | "day" = "hour"
): TimeSeriesDataPoint[] {
  const buckets = new Map<string, TimeSeriesDataPoint>();

  // Initialize buckets
  incidents.forEach((incident) => {
    const timestamp = new Date(incident.created_at);
    const bucketKey = getBucketKey(timestamp, bucketSize);

    if (!buckets.has(bucketKey)) {
      buckets.set(bucketKey, {
        timestamp: bucketKey,
        triggered: 0,
        acknowledged: 0,
        resolved: 0,
        total: 0,
      });
    }

    const bucket = buckets.get(bucketKey)!;
    bucket.total++;

    // Count by status
    switch (incident.status) {
      case "triggered":
        bucket.triggered++;
        break;
      case "acknowledged":
        bucket.acknowledged++;
        break;
      case "resolved":
        bucket.resolved++;
        break;
    }
  });

  // Sort by timestamp
  return Array.from(buckets.values()).sort(
    (a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
  );
}

/**
 * Get bucket key for time-series grouping
 */
function getBucketKey(date: Date, bucketSize: "hour" | "day"): string {
  if (bucketSize === "hour") {
    // Round to hour: "2024-01-30T14:00:00Z"
    const rounded = new Date(date);
    rounded.setMinutes(0, 0, 0);
    return rounded.toISOString();
  } else {
    // Round to day: "2024-01-30T00:00:00Z"
    const rounded = new Date(date);
    rounded.setHours(0, 0, 0, 0);
    return rounded.toISOString();
  }
}

/**
 * Aggregate incidents by service
 */
export function aggregateByService(
  incidents: Incident[],
  services: Service[]
): ServiceHealth[] {
  const serviceMap = new Map<string, ServiceHealth>();

  // Initialize service health for all services
  services.forEach((service) => {
    serviceMap.set(service.id, {
      service_id: service.id,
      service_name: service.name,
      incident_count: 0,
      high_urgency_count: 0,
      low_urgency_count: 0,
      avg_resolution_time_minutes: null,
      status: "healthy",
    });
  });

  // Aggregate incidents per service
  const resolutionTimes = new Map<string, number[]>();

  incidents.forEach((incident) => {
    const serviceId = incident.service.id;

    if (!serviceMap.has(serviceId)) {
      // Service not in our list, create entry
      serviceMap.set(serviceId, {
        service_id: serviceId,
        service_name: incident.service.summary,
        incident_count: 0,
        high_urgency_count: 0,
        low_urgency_count: 0,
        avg_resolution_time_minutes: null,
        status: "healthy",
      });
    }

    const serviceHealth = serviceMap.get(serviceId)!;
    serviceHealth.incident_count++;

    if (incident.urgency === "high") {
      serviceHealth.high_urgency_count++;
    } else {
      serviceHealth.low_urgency_count++;
    }

    // Calculate resolution time
    if (incident.status === "resolved" && incident.resolved_at) {
      const createdAt = new Date(incident.created_at).getTime();
      const resolvedAt = new Date(incident.resolved_at).getTime();
      const resolutionMinutes = (resolvedAt - createdAt) / (1000 * 60);

      if (!resolutionTimes.has(serviceId)) {
        resolutionTimes.set(serviceId, []);
      }
      resolutionTimes.get(serviceId)!.push(resolutionMinutes);
    }
  });

  // Calculate average resolution times and determine status
  serviceMap.forEach((serviceHealth, serviceId) => {
    const times = resolutionTimes.get(serviceId);
    if (times && times.length > 0) {
      serviceHealth.avg_resolution_time_minutes =
        times.reduce((sum, time) => sum + time, 0) / times.length;
    }

    // Determine status based on incident count
    if (serviceHealth.incident_count === 0) {
      serviceHealth.status = "healthy";
    } else if (serviceHealth.incident_count <= 2) {
      serviceHealth.status = "healthy";
    } else if (serviceHealth.incident_count <= 5) {
      serviceHealth.status = "warning";
    } else {
      serviceHealth.status = "critical";
    }
  });

  return Array.from(serviceMap.values()).sort(
    (a, b) => b.incident_count - a.incident_count
  );
}

/**
 * Calculate urgency distribution
 */
export function calculateUrgencyDistribution(
  incidents: Incident[]
): UrgencyDistribution {
  const high = incidents.filter((i) => i.urgency === "high").length;
  const low = incidents.filter((i) => i.urgency === "low").length;
  const total = incidents.length;

  return {
    high,
    low,
    total,
    high_percent: total > 0 ? Math.round((high / total) * 100) : 0,
    low_percent: total > 0 ? Math.round((low / total) * 100) : 0,
  };
}

/**
 * Calculate average resolution time for incidents
 */
export function calculateAvgResolutionTime(
  incidents: Incident[]
): number | null {
  const resolvedIncidents = incidents.filter(
    (i) => i.status === "resolved" && i.resolved_at
  );

  if (resolvedIncidents.length === 0) {
    return null;
  }

  const totalMinutes = resolvedIncidents.reduce((sum, incident) => {
    const createdAt = new Date(incident.created_at).getTime();
    const resolvedAt = new Date(incident.resolved_at!).getTime();
    const resolutionMinutes = (resolvedAt - createdAt) / (1000 * 60);
    return sum + resolutionMinutes;
  }, 0);

  return totalMinutes / resolvedIncidents.length;
}

/**
 * Generate complete dashboard data
 */
export function generateDashboardData(
  incidents: Incident[],
  services: Service[],
  timeRange: "24h" | "7d" | "30d"
): IncidentDashboardData {
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

  const activeIncidents = incidents.filter(
    (i) => i.status === "triggered" || i.status === "acknowledged"
  );

  const resolvedToday = incidents.filter((i) => {
    if (i.status !== "resolved" || !i.resolved_at) return false;
    const resolvedDate = new Date(i.resolved_at);
    const today = new Date();
    return resolvedDate.toDateString() === today.toDateString();
  });

  return {
    summary: {
      total_incidents: incidents.length,
      active_incidents: activeIncidents.length,
      resolved_today: resolvedToday.length,
      avg_resolution_time_minutes: calculateAvgResolutionTime(incidents),
    },
    timeline: aggregateIncidentTimeline(
      incidents,
      timeRange === "24h" ? "hour" : "day"
    ),
    service_health: aggregateByService(incidents, services),
    urgency_distribution: calculateUrgencyDistribution(incidents),
    time_range: {
      start: since.toISOString(),
      end: now.toISOString(),
      label: timeRange,
    },
    generated_at: now.toISOString(),
  };
}

/**
 * Generate real-time stats for polling
 */
export function generateIncidentStats(incidents: Incident[]): IncidentStats {
  const activeIncidents = incidents.filter(
    (i) => i.status === "triggered" || i.status === "acknowledged"
  );

  const triggered = incidents.filter((i) => i.status === "triggered");
  const acknowledged = incidents.filter((i) => i.status === "acknowledged");

  const high = incidents.filter((i) => i.urgency === "high");
  const low = incidents.filter((i) => i.urgency === "low");

  // Get most recent 5 incidents
  const recent = activeIncidents
    .sort(
      (a, b) =>
        new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    )
    .slice(0, 5)
    .map((i) => ({
      id: i.id,
      incident_number: i.incident_number,
      title: i.title,
      status: i.status,
      urgency: i.urgency,
      service_name: i.service.summary,
      created_at: i.created_at,
    }));

  return {
    timestamp: new Date().toISOString(),
    active_incidents: activeIncidents.length,
    triggered_count: triggered.length,
    acknowledged_count: acknowledged.length,
    high_urgency_count: high.length,
    low_urgency_count: low.length,
    recent_incidents: recent,
  };
}
