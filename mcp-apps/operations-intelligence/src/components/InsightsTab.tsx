import { useCallback, useEffect, useRef, useState } from "react";
import type { App } from "@modelcontextprotocol/ext-apps";
import { fetchInsight, type InsightMessage } from "../api";
import { InsightCard } from "./InsightCard";
import { InsightsChat } from "./InsightsChat";

interface InsightsTabProps {
  app: App;
  teamName: string;
  since: string;
  until: string;
  refreshKey: number;  // increment to trigger re-fetch
}

interface AutoInsight {
  title: string;
  query: string;
  content: string | null;
  error: string | null;
}

function buildQueries(team: string, since: string, until: string): [string, string, string] {
  return [
    `Summarize MTTA and MTTR trends for ${team} between ${since} and ${until}. Highlight any notable changes or anomalies.`,
    `Which services have the highest incident volume and worst resolution times for ${team} between ${since} and ${until}?`,
    `How is ${team} performing in terms of escalations, on-call interruptions, and responder load between ${since} and ${until}?`,
  ];
}

export function InsightsTab({ app, teamName, since, until, refreshKey }: InsightsTabProps) {
  const sessionId = useRef(crypto.randomUUID());
  const team = teamName || "all teams";

  const [insights, setInsights] = useState<AutoInsight[]>(() => {
    const [q0, q1, q2] = buildQueries(team, since, until);
    return [
      { title: "MTTA & MTTR Trends", query: q0, content: null, error: null },
      { title: "Noisiest Services", query: q1, content: null, error: null },
      { title: "Team & Responder Load", query: q2, content: null, error: null },
    ];
  });

  const [chatMessages, setChatMessages] = useState<InsightMessage[]>([]);
  const [chatLoading, setChatLoading] = useState(false);

  const loadInsight = useCallback(
    async (idx: number, query: string) => {
      setInsights((prev) =>
        prev.map((ins, i) => (i === idx ? { ...ins, content: null, error: null } : ins))
      );
      try {
        const content = await fetchInsight(app, query, sessionId.current);
        setInsights((prev) =>
          prev.map((ins, i) => (i === idx ? { ...ins, content } : ins))
        );
      } catch (err: any) {
        setInsights((prev) =>
          prev.map((ins, i) =>
            i === idx ? { ...ins, error: err?.message ?? "Failed to load insight" } : ins
          )
        );
      }
    },
    [app]
  );

  // Load all 3 auto-insights on mount and when refreshKey changes
  useEffect(() => {
    sessionId.current = crypto.randomUUID();
    setChatMessages([]);
    const queries = buildQueries(team, since, until);
    setInsights((prev) =>
      prev.map((ins, i) => ({ ...ins, query: queries[i]!, content: null, error: null }))
    );
    queries.forEach((q, i) => loadInsight(i, q));
  }, [refreshKey]); // eslint-disable-line react-hooks/exhaustive-deps

  async function handleSend(message: string) {
    setChatMessages((prev) => [...prev, { role: "user", content: message }]);
    setChatLoading(true);
    try {
      const reply = await fetchInsight(app, message, sessionId.current);
      setChatMessages((prev) => [...prev, { role: "assistant", content: reply }]);
    } catch (err: any) {
      setChatMessages((prev) => [
        ...prev,
        { role: "assistant", content: err?.message ?? "Sorry, I couldn't process that request. Please try again." },
      ]);
    } finally {
      setChatLoading(false);
    }
  }

  return (
    <div className="insights-tab">
      <div className="insight-cards">
        {insights.map((ins, i) => (
          <InsightCard
            key={ins.title}
            title={ins.title}
            content={ins.content}
            error={ins.error}
            onRetry={() => loadInsight(i, ins.query)}
          />
        ))}
      </div>
      <InsightsChat
        messages={chatMessages}
        loading={chatLoading}
        onSend={handleSend}
      />
    </div>
  );
}
