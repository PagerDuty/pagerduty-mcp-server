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

export function InsightsTab({ app, teamName, since, until, refreshKey }: InsightsTabProps) {
  const sessionId = useRef(crypto.randomUUID());
  const team = teamName || "all teams";

  const [insights, setInsights] = useState<AutoInsight[]>([
    {
      title: "MTTA & MTTR Trends",
      query: `Summarize MTTA and MTTR trends for ${team} between ${since} and ${until}. Highlight any notable changes or anomalies.`,
      content: null,
      error: null,
    },
    {
      title: "Noisiest Services",
      query: `Which services have the highest incident volume and worst resolution times for ${team} between ${since} and ${until}?`,
      content: null,
      error: null,
    },
    {
      title: "Team & Responder Load",
      query: `How is ${team} performing in terms of escalations, on-call interruptions, and responder load between ${since} and ${until}?`,
      content: null,
      error: null,
    },
  ]);

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
      } catch {
        setInsights((prev) =>
          prev.map((ins, i) =>
            i === idx ? { ...ins, error: "Failed to load insight" } : ins
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
    const queries: [string, string, string] = [
      `Summarize MTTA and MTTR trends for ${team} between ${since} and ${until}. Highlight any notable changes or anomalies.`,
      `Which services have the highest incident volume and worst resolution times for ${team} between ${since} and ${until}?`,
      `How is ${team} performing in terms of escalations, on-call interruptions, and responder load between ${since} and ${until}?`,
    ];
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
    } catch {
      setChatMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Sorry, I couldn't process that request. Please try again." },
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
            key={i}
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
