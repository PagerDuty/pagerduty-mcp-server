// src/components/TabBar.tsx

export type TabId = "compensation" | "compliance" | "fairness" | "settings";

interface Tab {
  id: TabId;
  label: string;
}

const TABS: Tab[] = [
  { id: "compensation", label: "💰 Compensation" },
  { id: "compliance",   label: "🛡 Compliance" },
  { id: "fairness",     label: "⚖ Fairness" },
  { id: "settings",     label: "⚙ Settings" },
];

interface Props {
  activeTab: TabId;
  onTabChange: (tab: TabId) => void;
}

export function TabBar({ activeTab, onTabChange }: Props) {
  return (
    <div className="tab-bar">
      {TABS.map((t) => (
        <button
          key={t.id}
          className={["tab-btn", activeTab === t.id ? "tab-btn--active" : ""].filter(Boolean).join(" ")}
          onClick={() => onTabChange(t.id)}
        >
          {t.label}
        </button>
      ))}
    </div>
  );
}
