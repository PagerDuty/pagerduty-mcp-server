/**
 * GraphCanvas — PagerDuty-style service dependency graph
 * Tree/DAG layout: dependent services above, supporting services below.
 */

import { useCallback, useEffect, useRef, useState } from "react";
import type { ActiveIncident, BusinessService, ServiceRelationship, TechnicalService } from "../api";

interface Props {
  businessServices: BusinessService[];
  technicalServices: TechnicalService[];
  relationships: ServiceRelationship[];
  incidents: ActiveIncident[];
  errors?: string[];
}

interface GraphNode {
  id: string;
  x: number;
  y: number;
  label: string;
  fullName: string;
  team: string;
  type: "business" | "technical";
  incidentCount: number;
  urgency: "high" | "low" | "none";
}

interface Tooltip { x: number; y: number; node: GraphNode; }
interface Transform { x: number; y: number; scale: number; }

const BIZ_W = 148;
const BIZ_H = 50;
const TECH_W = 130;
const TECH_H = 44;
const H_SPACING = 175;  // horizontal gap between nodes at the same level
const V_SPACING = 130;  // vertical gap between levels
const PAD_X = 80;
const PAD_Y = 60;

function trunc(s: string, n: number) { return s.length > n ? s.slice(0, n - 1) + "…" : s; }

/**
 * Tree/DAG layout using longest-path level assignment.
 * Edge direction: dependent_service → supporting_service (top → bottom).
 * Roots (nodes nothing depends on) are placed at the top.
 */
function treeLayout(
  nodeIds: string[],
  relationships: ServiceRelationship[],
): Map<string, { x: number; y: number }> {
  if (nodeIds.length === 0) return new Map();
  const idSet = new Set(nodeIds);

  // Build adjacency (deduplicated)
  const childrenOf = new Map<string, string[]>(); // dep → [sup, ...]
  const parentsOf = new Map<string, string[]>();   // sup → [dep, ...]
  for (const id of nodeIds) { childrenOf.set(id, []); parentsOf.set(id, []); }

  const seenEdges = new Set<string>();
  for (const rel of relationships) {
    const dep = rel.dependent_service?.id;
    const sup = rel.supporting_service?.id;
    if (!dep || !sup || dep === sup) continue;
    if (!idSet.has(dep) || !idSet.has(sup)) continue;
    const key = `${dep}|${sup}`;
    if (seenEdges.has(key)) continue;
    seenEdges.add(key);
    childrenOf.get(dep)!.push(sup);
    parentsOf.get(sup)!.push(dep);
  }

  // Kahn's topological sort — detects cycles (cycle nodes go to end)
  const tempIndeg = new Map(nodeIds.map(id => [id, parentsOf.get(id)!.length]));
  const topoQueue: string[] = nodeIds.filter(id => tempIndeg.get(id) === 0);
  const topoOrder: string[] = [];
  let qi = 0;
  while (qi < topoQueue.length) {
    const v = topoQueue[qi++];
    topoOrder.push(v);
    for (const child of childrenOf.get(v)!) {
      const ni = (tempIndeg.get(child) ?? 1) - 1;
      tempIndeg.set(child, ni);
      if (ni === 0) topoQueue.push(child);
    }
  }
  // Cycle members not in topoOrder — append at end
  for (const id of nodeIds) {
    if (!topoOrder.includes(id)) topoOrder.push(id);
  }

  // Longest-path depth assignment (process in topological order)
  const depth = new Map(nodeIds.map(id => [id, 0]));
  for (const v of topoOrder) {
    const d = depth.get(v) ?? 0;
    for (const child of childrenOf.get(v)!) {
      if (d + 1 > (depth.get(child) ?? 0)) depth.set(child, d + 1);
    }
  }

  // Group by level
  const byLevel = new Map<number, string[]>();
  for (const [id, d] of depth) {
    if (!byLevel.has(d)) byLevel.set(d, []);
    byLevel.get(d)!.push(id);
  }
  const levels = [...byLevel.keys()].sort((a, b) => a - b);

  // Position: center each row horizontally
  const positions = new Map<string, { x: number; y: number }>();
  for (const l of levels) {
    const ids = byLevel.get(l)!;
    const rowW = (ids.length - 1) * H_SPACING;
    ids.forEach((id, i) => {
      positions.set(id, {
        x: PAD_X + rowW / 2 + i * H_SPACING - rowW / 2 + PAD_X,
        y: PAD_Y + l * V_SPACING,
      });
    });
  }

  // Compute the content offset so the widest row is centered
  const maxRowW = Math.max(...levels.map(l => {
    const ids = byLevel.get(l)!;
    return (ids.length - 1) * H_SPACING;
  }));
  // Re-center all rows around the widest
  for (const l of levels) {
    const ids = byLevel.get(l)!;
    const rowW = (ids.length - 1) * H_SPACING;
    const offset = (maxRowW - rowW) / 2;
    for (const id of ids) {
      const p = positions.get(id)!;
      positions.set(id, { x: p.x + offset, y: p.y });
    }
  }

  return positions;
}

/** Compute bounding box of a set of nodes. */
function boundingBox(nodes: GraphNode[]) {
  if (nodes.length === 0) return { x1: 0, y1: 0, x2: 400, y2: 300 };
  return {
    x1: Math.min(...nodes.map(n => n.x - (n.type === "business" ? BIZ_W : TECH_W) / 2)),
    y1: Math.min(...nodes.map(n => n.y - (n.type === "business" ? BIZ_H : TECH_H) / 2)),
    x2: Math.max(...nodes.map(n => n.x + (n.type === "business" ? BIZ_W : TECH_W) / 2)),
    y2: Math.max(...nodes.map(n => n.y + (n.type === "business" ? BIZ_H : TECH_H) / 2)),
  };
}

function fitTransform(nodes: GraphNode[], cw: number, ch: number, maxScale = 1.0): Transform {
  if (nodes.length === 0) return { x: 0, y: 0, scale: 1 };
  const PAD = 56;
  const bb = boundingBox(nodes);
  const bw = bb.x2 - bb.x1 + PAD * 2;
  const bh = bb.y2 - bb.y1 + PAD * 2;
  const scale = Math.min(maxScale, (cw - PAD) / bw, (ch - PAD) / bh);
  const cx = (bb.x1 + bb.x2) / 2;
  const cy = (bb.y1 + bb.y2) / 2;
  return { x: cw / 2 - cx * scale, y: ch / 2 - cy * scale, scale };
}

function StatusIcon({ urgency, cx, cy, r }: { urgency: "high" | "low" | "none"; cx: number; cy: number; r: number }) {
  const fill = urgency === "high" ? "#f38ba8" : urgency === "low" ? "#fab387" : "#a6e3a1";
  const dark = urgency === "high" ? "#3d1520" : urgency === "low" ? "#3d2f1e" : "#1a2e1e";
  if (urgency === "none") {
    const s = r * 0.42;
    return (
      <g>
        <circle cx={cx} cy={cy} r={r} fill={fill} />
        <path d={`M ${cx - s} ${cy} L ${cx - s * 0.3} ${cy + s * 0.7} L ${cx + s} ${cy - s * 0.7}`}
          stroke={dark} strokeWidth={r * 0.28} fill="none" strokeLinecap="round" strokeLinejoin="round" />
      </g>
    );
  }
  return (
    <g>
      <circle cx={cx} cy={cy} r={r} fill={fill} />
      <text x={cx} y={cy + 0.5} textAnchor="middle" dominantBaseline="middle"
        fontSize={r * 1.1} fontWeight="800" fill={dark} fontFamily="-apple-system, sans-serif">!</text>
    </g>
  );
}

function NodeCard({ n, selected, dimmed, onClick, onMouseMove, onMouseLeave }: {
  n: GraphNode; selected: boolean; dimmed: boolean;
  onClick: () => void; onMouseMove: (e: React.MouseEvent) => void; onMouseLeave: () => void;
}) {
  const W = n.type === "business" ? BIZ_W : TECH_W;
  const H = n.type === "business" ? BIZ_H : TECH_H;
  const rx = n.type === "business" ? 6 : H / 2;
  const IR = H * 0.22, ICX = n.type === "business" ? 14 : H / 2, ICY = H / 2;
  const accentColor = n.urgency === "high" ? "#f38ba8" : n.urgency === "low" ? "#fab387" : "#a6e3a1";
  const borderColor = selected ? "#89b4fa" : n.urgency !== "none" ? accentColor : "#3d4166";
  const borderWidth = selected ? 2.5 : 1.5;

  return (
    <g transform={`translate(${n.x - W / 2}, ${n.y - H / 2})`}
      onClick={onClick} onMouseMove={onMouseMove} onMouseLeave={onMouseLeave}
      style={{ cursor: "pointer", opacity: dimmed ? 0.18 : 1, transition: "opacity 0.2s" }}>
      <rect width={W} height={H} rx={rx} ry={rx} fill="rgba(0,0,0,0.5)" transform="translate(1,3)" />
      <clipPath id={`c-${n.id}`}><rect width={W} height={H} rx={rx} ry={rx} /></clipPath>
      <g clipPath={`url(#c-${n.id})`}>
        <rect width={W} height={H} fill="#1e1e2e" />
        <rect width={W} height={4} fill={accentColor} opacity={n.type === "business" ? 1 : 0.6} />
      </g>
      <rect width={W} height={H} rx={rx} ry={rx} fill="none" stroke={borderColor} strokeWidth={borderWidth}
        style={selected ? { filter: "drop-shadow(0 0 6px rgba(137,180,250,0.6))" } : undefined} />
      <StatusIcon urgency={n.urgency} cx={ICX} cy={ICY} r={IR} />
      <text x={ICX + IR + 7} y={n.team ? H / 2 - 7 : H / 2 + 1} fill="#cdd6f4" fontSize={11}
        fontWeight={n.type === "business" ? 700 : 600} dominantBaseline="middle"
        fontFamily="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
        style={{ userSelect: "none" }}>{n.label}</text>
      {n.team && (
        <text x={ICX + IR + 7} y={H / 2 + 8} fill="#6c7086" fontSize={9} dominantBaseline="middle"
          fontFamily="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
          style={{ userSelect: "none" }}>{n.team}</text>
      )}
      {n.incidentCount > 0 && (
        <g transform={`translate(${W - 10}, -8)`}>
          <circle r={9} fill={n.urgency === "high" ? "#f38ba8" : "#fab387"} stroke="#13131f" strokeWidth={1.5} />
          <text textAnchor="middle" dominantBaseline="middle" fill="#1e1e2e" fontSize={8} fontWeight={700}>
            {n.incidentCount > 99 ? "99" : n.incidentCount}
          </text>
        </g>
      )}
    </g>
  );
}

export function GraphCanvas({ businessServices, technicalServices, relationships, incidents, errors }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const svgRef = useRef<SVGSVGElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const [containerSize, setContainerSize] = useState({ w: 800, h: 500 });
  const [tooltip, setTooltip] = useState<Tooltip | null>(null);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [transform, setTransform] = useState<Transform>({ x: 0, y: 0, scale: 1 });
  const [search, setSearch] = useState("");
  const [searchTab, setSearchTab] = useState<"all" | "business" | "technical">("all");
  const [showDropdown, setShowDropdown] = useState(false);
  const [animateTransform, setAnimateTransform] = useState(false);

  const isPanning = useRef(false);
  const panStart = useRef({ mx: 0, my: 0, px: 0, py: 0 });
  const didPan = useRef(false);
  const hasFitted = useRef(false);

  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    const obs = new ResizeObserver((e) => {
      const { width, height } = e[0].contentRect;
      setContainerSize({ w: Math.max(width, 400), h: Math.max(height, 300) });
    });
    obs.observe(el);
    return () => obs.disconnect();
  }, []);

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (inputRef.current?.contains(e.target as Node)) return;
      if (dropdownRef.current?.contains(e.target as Node)) return;
      setShowDropdown(false);
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  // Only show services that appear in at least one relationship
  const connectedIds = new Set<string>();
  for (const rel of relationships) {
    if (rel.dependent_service?.id) connectedIds.add(rel.dependent_service.id);
    if (rel.supporting_service?.id) connectedIds.add(rel.supporting_service.id);
  }
  const visibleBiz = businessServices.filter(s => connectedIds.has(s.id));
  const visibleTech = technicalServices.filter(s => connectedIds.has(s.id));

  // Build nodes: biz + tech in a single merged list
  const incByService = new Map<string, ActiveIncident[]>();
  for (const inc of incidents) {
    if (inc.service?.id) {
      const arr = incByService.get(inc.service.id) ?? [];
      arr.push(inc);
      incByService.set(inc.service.id, arr);
    }
  }

  const allServiceIds = [
    ...visibleBiz.map(s => s.id),
    ...visibleTech.map(s => s.id),
  ];

  const positions = treeLayout(allServiceIds, relationships);

  const nodes: GraphNode[] = [
    ...visibleBiz.map(s => {
      const pos = positions.get(s.id) ?? { x: 0, y: 0 };
      const incs = incByService.get(s.id) ?? [];
      return {
        id: s.id, x: pos.x, y: pos.y,
        label: trunc(s.name, 16), fullName: s.name,
        team: s.team?.summary ? trunc(s.team.summary, 20) : (s.description ? trunc(s.description, 20) : ""),
        type: "business" as const,
        incidentCount: incs.length,
        urgency: incs.length === 0 ? "none" as const : incs.some(i => i.urgency === "high") ? "high" as const : "low" as const,
      };
    }),
    ...visibleTech.map(s => {
      const pos = positions.get(s.id) ?? { x: 0, y: 0 };
      const incs = incByService.get(s.id) ?? [];
      return {
        id: s.id, x: pos.x, y: pos.y,
        label: trunc(s.name, 15), fullName: s.name,
        team: (s.team as any)?.summary ? trunc((s.team as any).summary, 18) : "",
        type: "technical" as const,
        incidentCount: incs.length,
        urgency: incs.length === 0 ? "none" as const : incs.some(i => i.urgency === "high") ? "high" as const : "low" as const,
      };
    }),
  ];

  const nodeById = new Map(nodes.map(n => [n.id, n]));

  // Auto-fit once when nodes first load
  useEffect(() => {
    if (hasFitted.current) return;
    if (nodes.length === 0) return;
    if (containerSize.w <= 400 && containerSize.h <= 300) return;
    hasFitted.current = true;
    const impacted = nodes.filter(n => n.urgency !== "none");
    const targets = impacted.length > 0 ? impacted : nodes;
    setTransform(fitTransform(targets, containerSize.w, containerSize.h));
  }, [nodes, containerSize]);

  const prevCount = useRef(allServiceIds.length);
  useEffect(() => {
    if (allServiceIds.length !== prevCount.current) {
      hasFitted.current = false;
      prevCount.current = allServiceIds.length;
    }
  }, [allServiceIds.length]);

  const fitImpacted = useCallback(() => {
    setAnimateTransform(true);
    const impacted = nodes.filter(n => n.urgency !== "none");
    const targets = impacted.length > 0 ? impacted : nodes;
    setTransform(fitTransform(targets, containerSize.w, containerSize.h));
  }, [nodes, containerSize]);

  const fitAll = useCallback(() => {
    setAnimateTransform(true);
    setTransform(fitTransform(nodes, containerSize.w, containerSize.h));
  }, [nodes, containerSize]);

  // Search filtering
  const q = search.trim().toLowerCase();
  const matchedIds = new Set<string>();
  if (q) {
    for (const n of nodes) {
      if ((searchTab === "all" || n.type === searchTab) &&
        (n.fullName.toLowerCase().includes(q) || n.team.toLowerCase().includes(q))) {
        matchedIds.add(n.id);
      }
    }
  }
  const hasSearch = q.length > 0;
  const dropdownMatches = hasSearch ? nodes.filter(n =>
    (searchTab === "all" || n.type === searchTab) &&
    (n.fullName.toLowerCase().includes(q) || n.team.toLowerCase().includes(q))
  ).slice(0, 12) : [];

  // Build edge list from relationships
  type Edge = { from: GraphNode; to: GraphNode; impacted: boolean };
  const allEdges: Edge[] = [];
  const seenEdgeKeys = new Set<string>();
  for (const rel of relationships) {
    const dep = nodeById.get(rel.dependent_service?.id ?? "");
    const sup = nodeById.get(rel.supporting_service?.id ?? "");
    if (!dep || !sup || dep.id === sup.id) continue;
    const key = `${dep.id}|${sup.id}`;
    if (seenEdgeKeys.has(key)) continue;
    seenEdgeKeys.add(key);
    allEdges.push({ from: dep, to: sup, impacted: dep.urgency !== "none" || sup.urgency !== "none" });
  }

  const selectedEdgeIds = new Set<number>();
  if (selectedId) allEdges.forEach((e, i) => {
    if (e.from.id === selectedId || e.to.id === selectedId) selectedEdgeIds.add(i);
  });

  // Neighbors of the selected node (selected + directly connected)
  const neighborIds = new Set<string>();
  if (selectedId) {
    neighborIds.add(selectedId);
    allEdges.forEach(e => {
      if (e.from.id === selectedId) neighborIds.add(e.to.id);
      if (e.to.id === selectedId) neighborIds.add(e.from.id);
    });
  }

  // Node click — select + fit node + its direct relations into view
  const handleNodeClick = useCallback((nodeId: string) => {
    if (didPan.current) return;
    const isDeselecting = selectedId === nodeId;
    setSelectedId(isDeselecting ? null : nodeId);
    if (!isDeselecting) {
      setAnimateTransform(true);
      const node = nodeById.get(nodeId);
      if (node) {
        // Collect selected node + all direct neighbors
        const neighborNodes: GraphNode[] = [node];
        for (const edge of allEdges) {
          if (edge.from.id === nodeId) { const n = nodeById.get(edge.to.id); if (n) neighborNodes.push(n); }
          if (edge.to.id === nodeId) { const n = nodeById.get(edge.from.id); if (n) neighborNodes.push(n); }
        }
        setTransform(fitTransform(neighborNodes, containerSize.w, containerSize.h, 2.0));
      }
    }
  }, [selectedId, nodeById, containerSize, allEdges]);

  // Pan to node (from dropdown)
  const panToNode = useCallback((node: GraphNode) => {
    setTransform(prev => ({
      ...prev,
      x: containerSize.w / 2 - node.x * prev.scale,
      y: containerSize.h / 2 - node.y * prev.scale,
    }));
  }, [containerSize]);

  const selectFromDropdown = useCallback((node: GraphNode) => {
    setSelectedId(node.id);
    setAnimateTransform(true);
    panToNode(node);
    setSearch("");
    setShowDropdown(false);
  }, [panToNode]);

  // Pan handlers
  const handleSvgMouseDown = useCallback((e: React.MouseEvent<SVGSVGElement>) => {
    setAnimateTransform(false);
    didPan.current = false;
    if ((e.target as Element).closest?.("[data-node]")) return;
    if (e.button !== 0) return;
    isPanning.current = true;
    panStart.current = { mx: e.clientX, my: e.clientY, px: transform.x, py: transform.y };
    e.preventDefault();
  }, [transform.x, transform.y]);

  const handleSvgMouseMove = useCallback((e: React.MouseEvent<SVGSVGElement>) => {
    if (!isPanning.current) return;
    const dx = e.clientX - panStart.current.mx;
    const dy = e.clientY - panStart.current.my;
    if (Math.abs(dx) > 2 || Math.abs(dy) > 2) didPan.current = true;
    setTransform(prev => ({ ...prev, x: panStart.current.px + dx, y: panStart.current.py + dy }));
  }, []);

  const handleSvgMouseUp = useCallback(() => { isPanning.current = false; }, []);

  // Scroll to zoom
  useEffect(() => {
    const svg = svgRef.current;
    if (!svg) return;
    const handler = (e: WheelEvent) => {
      e.preventDefault();
      const rect = svg.getBoundingClientRect();
      const mx = e.clientX - rect.left;
      const my = e.clientY - rect.top;
      const factor = e.deltaY < 0 ? 1.1 : 0.9;
      setTransform(prev => {
        const newScale = Math.max(0.08, Math.min(4, prev.scale * factor));
        const ratio = newScale / prev.scale;
        return { x: mx - (mx - prev.x) * ratio, y: my - (my - prev.y) * ratio, scale: newScale };
      });
    };
    svg.addEventListener("wheel", handler, { passive: false });
    return () => svg.removeEventListener("wheel", handler);
  }, []);

  const handleMouseMove = useCallback((e: React.MouseEvent, node: GraphNode) => {
    if (isPanning.current) return;
    const rect = svgRef.current?.getBoundingClientRect();
    if (!rect) return;
    setTooltip({ x: e.clientX - rect.left + 14, y: e.clientY - rect.top - 12, node });
  }, []);

  const hasImpacted = nodes.some(n => n.urgency !== "none");

  if (relationships.length === 0) {
    return (
      <div ref={containerRef} style={{ position: "relative", width: "100%", height: "100%", display: "flex", alignItems: "center", justifyContent: "center" }}>
        <div style={{ textAlign: "center", color: "#45475a", maxWidth: 380 }}>
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#3d4166" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" style={{ marginBottom: 16 }}>
            <circle cx="12" cy="5" r="2" /><circle cx="5" cy="19" r="2" /><circle cx="19" cy="19" r="2" />
            <line x1="12" y1="7" x2="5" y2="17" /><line x1="12" y1="7" x2="19" y2="17" />
          </svg>
          {errors && errors.length > 0 ? (
            <>
              <div style={{ fontSize: 14, fontWeight: 600, color: "#f38ba8", marginBottom: 6 }}>Failed to load dependencies</div>
              <div style={{ fontSize: 11, color: "#6c7086", maxWidth: 360, wordBreak: "break-all" }}>
                {errors.slice(0, 3).map((e, i) => <div key={i} style={{ marginBottom: 4 }}>{e}</div>)}
                {errors.length > 3 && <div>…and {errors.length - 3} more</div>}
              </div>
            </>
          ) : (
            <>
              <div style={{ fontSize: 14, fontWeight: 600, color: "#6c7086", marginBottom: 6 }}>No service dependencies found</div>
              <div style={{ fontSize: 12, color: "#45475a" }}>
                Configure service dependencies in PagerDuty to see the graph.
              </div>
            </>
          )}
        </div>
      </div>
    );
  }

  return (
    <div ref={containerRef} style={{ position: "relative", width: "100%", height: "100%" }}>

      {/* Search bar */}
      <div style={{ position: "absolute", top: 10, left: "50%", transform: "translateX(-50%)", zIndex: 30, minWidth: 340 }}>
        <div style={{
          display: "flex", alignItems: "center", gap: 6,
          background: "#1e1e2e", border: "1px solid #3d4166",
          borderRadius: showDropdown && dropdownMatches.length > 0 ? "8px 8px 0 0" : 8,
          padding: "5px 8px", boxShadow: "0 4px 16px rgba(0,0,0,0.5)",
        }}>
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#6c7086" strokeWidth="2"
            strokeLinecap="round" strokeLinejoin="round" style={{ flexShrink: 0 }}>
            <circle cx="11" cy="11" r="8" /><line x1="21" y1="21" x2="16.65" y2="16.65" />
          </svg>
          <input ref={inputRef} type="text" placeholder="Search services…" value={search}
            onChange={e => { setSearch(e.target.value); setShowDropdown(true); }}
            onFocus={() => { if (search.trim()) setShowDropdown(true); }}
            style={{ background: "transparent", border: "none", outline: "none", color: "#cdd6f4", fontSize: 12, flex: 1, minWidth: 120 }}
          />
          {(["all", "business", "technical"] as const).map(tab => (
            <button key={tab} onClick={() => { setSearchTab(tab); inputRef.current?.focus(); }}
              style={{
                background: searchTab === tab ? "#313244" : "transparent",
                border: "1px solid " + (searchTab === tab ? "#585b70" : "transparent"),
                borderRadius: 5, padding: "2px 7px", fontSize: 10, fontWeight: 600,
                color: searchTab === tab ? "#cdd6f4" : "#6c7086", cursor: "pointer", textTransform: "capitalize",
              }}>{tab}</button>
          ))}
          {hasSearch && (
            <button onClick={() => { setSearch(""); setShowDropdown(false); }}
              style={{ background: "none", border: "none", color: "#6c7086", cursor: "pointer", fontSize: 15, lineHeight: 1, padding: 0 }}>×</button>
          )}
        </div>

        {showDropdown && dropdownMatches.length > 0 && (
          <div ref={dropdownRef} style={{
            background: "#1e1e2e", border: "1px solid #3d4166", borderTop: "1px solid #2a2a3e",
            borderRadius: "0 0 8px 8px", boxShadow: "0 8px 24px rgba(0,0,0,0.6)",
            maxHeight: 260, overflowY: "auto",
          }}>
            {dropdownMatches.map(n => {
              const dotColor = n.urgency === "high" ? "#f38ba8" : n.urgency === "low" ? "#fab387"
                : n.type === "business" ? "#89b4fa" : "#a6e3a1";
              return (
                <div key={n.id}
                  onMouseDown={e => { e.preventDefault(); selectFromDropdown(n); }}
                  style={{ display: "flex", alignItems: "center", gap: 9, padding: "7px 12px", cursor: "pointer", borderBottom: "1px solid #1a1a28", transition: "background 0.1s" }}
                  onMouseEnter={e => (e.currentTarget.style.background = "#262637")}
                  onMouseLeave={e => (e.currentTarget.style.background = "transparent")}
                >
                  <div style={{ width: 8, height: 8, borderRadius: "50%", background: dotColor, flexShrink: 0 }} />
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ fontSize: 12, color: "#cdd6f4", fontWeight: 500, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{n.fullName}</div>
                    {n.team && <div style={{ fontSize: 10, color: "#6c7086", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{n.team}</div>}
                  </div>
                  <span style={{ fontSize: 9, fontWeight: 700, padding: "2px 6px", borderRadius: 4, background: n.type === "business" ? "rgba(137,180,250,0.12)" : "rgba(166,227,161,0.12)", color: n.type === "business" ? "#89b4fa" : "#a6e3a1", textTransform: "uppercase", letterSpacing: "0.05em", flexShrink: 0 }}>{n.type === "business" ? "Biz" : "Tech"}</span>
                  {n.incidentCount > 0 && (
                    <span style={{ fontSize: 9, fontWeight: 700, padding: "2px 5px", borderRadius: 4, background: "rgba(243,139,168,0.15)", color: "#f38ba8", flexShrink: 0 }}>{n.incidentCount} inc</span>
                  )}
                </div>
              );
            })}
            {dropdownMatches.length === 12 && hasSearch && (
              <div style={{ padding: "6px 12px", fontSize: 10, color: "#6c7086", textAlign: "center" }}>Showing top 12 — refine your search</div>
            )}
          </div>
        )}
        {showDropdown && hasSearch && dropdownMatches.length === 0 && (
          <div ref={dropdownRef} style={{ background: "#1e1e2e", border: "1px solid #3d4166", borderTop: "1px solid #2a2a3e", borderRadius: "0 0 8px 8px", padding: "10px 12px", fontSize: 11, color: "#6c7086", textAlign: "center", boxShadow: "0 8px 24px rgba(0,0,0,0.6)" }}>
            No matches for "{search}"
          </div>
        )}
      </div>

      {/* Fit buttons */}
      <div style={{ position: "absolute", bottom: 12, left: 12, zIndex: 20, display: "flex", gap: 6 }}>
        {hasImpacted && (
          <button onClick={fitImpacted} title="Fit impacted services"
            style={{ background: "rgba(243,139,168,0.12)", border: "1px solid rgba(243,139,168,0.3)", borderRadius: 6, padding: "4px 10px", fontSize: 10, fontWeight: 600, color: "#f38ba8", cursor: "pointer", backdropFilter: "blur(4px)" }}>
            ⚠ Fit Impacted
          </button>
        )}
        <button onClick={fitAll} title="Fit all services"
          style={{ background: "rgba(30,30,46,0.85)", border: "1px solid #3d4166", borderRadius: 6, padding: "4px 10px", fontSize: 10, fontWeight: 600, color: "#6c7086", cursor: "pointer", backdropFilter: "blur(4px)" }}>
          ⊞ Fit All
        </button>
      </div>

      {/* SVG canvas */}
      <svg ref={svgRef} width={containerSize.w} height={containerSize.h}
        style={{ display: "block", cursor: "grab" }}
        onMouseDown={handleSvgMouseDown}
        onMouseMove={handleSvgMouseMove}
        onMouseUp={handleSvgMouseUp}
        onMouseLeave={handleSvgMouseUp}
        onClick={e => { if (didPan.current) return; if (e.target === svgRef.current) setSelectedId(null); }}
      >
        <defs>
          <style>{`@keyframes dashFlow { to { stroke-dashoffset: -24; } }`}</style>
          <marker id="arr" markerWidth="7" markerHeight="7" refX="5" refY="3.5" orient="auto">
            <path d="M1,1 L1,6 L7,3.5 z" fill="#4a5080" />
          </marker>
          <marker id="arr-sel" markerWidth="7" markerHeight="7" refX="5" refY="3.5" orient="auto">
            <path d="M1,1 L1,6 L7,3.5 z" fill="#89b4fa" />
          </marker>
          <marker id="arr-imp" markerWidth="7" markerHeight="7" refX="5" refY="3.5" orient="auto">
            <path d="M1,1 L1,6 L7,3.5 z" fill="#f38ba8" />
          </marker>
          <pattern id="grid" x="0" y="0" width="30" height="30" patternUnits="userSpaceOnUse">
            <circle cx="1" cy="1" r="0.9" fill="var(--grid-dot)" />
          </pattern>
        </defs>
        <rect width={containerSize.w} height={containerSize.h} fill="url(#grid)" />

        <g transform={`translate(${transform.x}, ${transform.y}) scale(${transform.scale})`}
          style={{ transition: animateTransform ? "transform 0.45s cubic-bezier(0.4,0,0.2,1)" : "none" }}>
          {/* Edges */}
          {allEdges.map((edge, i) => {
            const Hf = edge.from.type === "business" ? BIZ_H : TECH_H;
            const Ht = edge.to.type === "business" ? BIZ_H : TECH_H;
            // Connect bottom of "from" to top of "to" when from is above to; otherwise sides
            const fromAbove = edge.from.y < edge.to.y;
            const x1 = edge.from.x;
            const y1 = fromAbove ? edge.from.y + Hf / 2 : edge.from.y;
            const x2 = edge.to.x;
            const y2 = fromAbove ? edge.to.y - Ht / 2 : edge.to.y;
            const cy1 = (y1 + y2) / 2;
            const isSel = selectedEdgeIds.has(i);
            const isDimmed = hasSearch
              ? !matchedIds.has(edge.from.id) && !matchedIds.has(edge.to.id)
              : !!selectedId && !isSel;
            const stroke = isSel ? "#89b4fa" : edge.impacted ? "#f38ba8" : "#4a5080";
            const marker = isSel ? "url(#arr-sel)" : edge.impacted ? "url(#arr-imp)" : "url(#arr)";
            return (
              <path key={i}
                d={`M ${x1} ${y1} C ${x1} ${cy1}, ${x2} ${cy1}, ${x2} ${y2}`}
                stroke={stroke} fill="none"
                strokeWidth={isSel ? 2 : 1.4}
                strokeOpacity={isDimmed ? 0.06 : isSel ? 1 : edge.impacted ? 0.85 : 0.75}
                markerEnd={marker}
                strokeDasharray={isSel ? "8 4" : undefined}
                style={isSel ? { animation: "dashFlow 0.5s linear infinite" } : undefined}
              />
            );
          })}

          {/* Nodes */}
          {nodes.map(n => (
            <g key={n.id} data-node="1">
              <NodeCard
                n={n}
                selected={n.id === selectedId}
                dimmed={(hasSearch && !matchedIds.has(n.id)) || (!!selectedId && !neighborIds.has(n.id))}
                onClick={() => handleNodeClick(n.id)}
                onMouseMove={e => handleMouseMove(e, n)}
                onMouseLeave={() => setTooltip(null)}
              />
            </g>
          ))}
        </g>
      </svg>

      {/* Tooltip */}
      {tooltip && !isPanning.current && (
        <div className="tooltip" style={{ left: tooltip.x, top: tooltip.y }}>
          <div className="tooltip-title">{tooltip.node.fullName}</div>
          <div className="tooltip-type">{tooltip.node.type === "business" ? "Business Service" : "Technical Service"}</div>
          {tooltip.node.team && <div className="tooltip-team">{tooltip.node.team}</div>}
          {tooltip.node.incidentCount > 0 && (
            <div className="tooltip-incidents">
              {tooltip.node.incidentCount} active incident{tooltip.node.incidentCount !== 1 ? "s" : ""}
            </div>
          )}
        </div>
      )}

      {/* Hint */}
      <div style={{ position: "absolute", bottom: 12, right: 12, fontSize: 10, color: "#45475a", pointerEvents: "none" }}>
        Scroll to zoom · Drag to pan · Click node to see relations
      </div>
    </div>
  );
}
