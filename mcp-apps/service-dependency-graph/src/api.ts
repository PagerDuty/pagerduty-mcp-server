/**
 * API functions for Service Dependency Graph
 * Calls PagerDuty MCP tools to fetch services, business services, dependencies, and incidents.
 */

import type { App } from "@modelcontextprotocol/ext-apps";
import type { CallToolResult } from "@modelcontextprotocol/sdk/types.js";

export interface TechnicalService {
  id: string;
  name: string;
  summary: string;
  status: string;
  description?: string;
  team?: { id: string; summary: string };
}

export interface BusinessService {
  id: string;
  name: string;
  description?: string;
  point_of_contact?: string;
  team?: { id: string; summary: string };
}

export interface ServiceRelationship {
  supporting_service?: { id: string; type: string; summary?: string };
  dependent_service?: { id: string; type: string; summary?: string };
}

export interface ActiveIncident {
  id: string;
  incident_number: number;
  title: string;
  status: "triggered" | "acknowledged" | "resolved";
  urgency: "high" | "low";
  service?: { id: string; summary: string };
}

export interface GraphData {
  technicalServices: TechnicalService[];
  businessServices: BusinessService[];
  relationships: ServiceRelationship[];
  incidents: ActiveIncident[];
  errors: string[];
}

function extractData<T>(result: CallToolResult): T | null {
  const text = result.content?.find((c) => c.type === "text")?.text;
  if (!text) return null;
  try {
    return JSON.parse(text);
  } catch {
    return null;
  }
}

export async function fetchGraphData(app: App): Promise<GraphData> {
  const [servicesResult, bizServicesResult, incidentsResult] = await Promise.allSettled([
    app.callServerTool({
      name: "list_services",
      arguments: { query_model: { limit: 100 } },
    }),
    app.callServerTool({
      name: "list_business_services",
      arguments: { query_model: {} },
    }),
    app.callServerTool({
      name: "list_incidents",
      arguments: { query_model: { status: ["triggered", "acknowledged"], limit: 50 } },
    }),
  ]);

  const servicesData =
    servicesResult.status === "fulfilled"
      ? extractData<any>(servicesResult.value)
      : null;

  const bizServicesData =
    bizServicesResult.status === "fulfilled"
      ? extractData<any>(bizServicesResult.value)
      : null;

  const incidentsData =
    incidentsResult.status === "fulfilled"
      ? extractData<any>(incidentsResult.value)
      : null;

  const technicalServices: TechnicalService[] =
    (servicesData?.response ?? []).map((s: any) => ({
      id: s.id,
      name: s.name ?? s.summary,
      summary: s.summary ?? s.name,
      status: s.status ?? "active",
      description: s.description,
      team: s.teams?.[0] ?? s.team,
    }));

  const businessServices: BusinessService[] =
    (bizServicesData?.response ?? []).map((s: any) => ({
      id: s.id,
      name: s.name ?? s.summary,
      description: s.description,
      point_of_contact: s.point_of_contact,
      team: s.team,
    }));

  const incidents: ActiveIncident[] =
    (incidentsData?.response ?? []).map((i: any) => ({
      id: i.id,
      incident_number: i.incident_number,
      title: i.title,
      status: i.status,
      urgency: i.urgency,
      service: i.service,
    }));

  const relationships: ServiceRelationship[] = [];
  const errors: string[] = [];
  const seenRelIds = new Set<string>();

  function addRels(rels: ServiceRelationship[]) {
    for (const rel of rels) {
      const key = `${rel.dependent_service?.id}→${rel.supporting_service?.id}`;
      if (!seenRelIds.has(key)) {
        seenRelIds.add(key);
        relationships.push(rel);
      }
    }
  }

  // Step 1: fetch business service dependencies sequentially
  for (const bs of businessServices) {
    try {
      const res = await app.callServerTool({
        name: "get_business_service_dependencies",
        arguments: { business_service_id: bs.id },
      });
      if ((res as any).isError) {
        const errText = res.content?.find((c) => c.type === "text")?.text ?? "unknown error";
        errors.push(`biz-dep ${bs.name ?? bs.id}: ${errText}`);
        continue;
      }
      const data = extractData<any>(res);
      if (data?.relationships) addRels(data.relationships);
    } catch (e) {
      errors.push(`biz-dep ${bs.name ?? bs.id}: ${e}`);
    }
  }

  // Step 2: fetch tech service dependencies only for technical services
  // that appeared in the business-service relationships above.
  // Skip entirely if none were found — avoids flooding the server with
  // calls for a tool that may not be available.
  const techIdsInRelationships = new Set<string>();
  for (const rel of relationships) {
    for (const side of [rel.dependent_service, rel.supporting_service]) {
      if (side?.id && (side as any).type?.includes("technical")) {
        techIdsInRelationships.add(side.id);
      }
    }
  }
  const techToQuery = technicalServices.filter((ts) => techIdsInRelationships.has(ts.id));

  for (const ts of techToQuery) {
    try {
      const res = await app.callServerTool({
        name: "get_technical_service_dependencies",
        arguments: { service_id: ts.id },
      });
      const data = extractData<any>(res);
      if (data?.relationships) addRels(data.relationships);
    } catch {
      // Tool may not be available on this server; skip silently
    }
  }

  return { technicalServices, businessServices, relationships, incidents, errors };
}
