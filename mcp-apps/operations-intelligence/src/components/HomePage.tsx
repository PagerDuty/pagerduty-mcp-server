import type { Page } from "../mcp-app";

interface MenuCardProps {
  icon: string;
  title: string;
  description: string;
  pills: string[];
  page: Page;
  cardClass: string;
  onNavigate: (page: Page) => void;
}

function MenuCard({ icon, title, description, pills, page, cardClass, onNavigate }: MenuCardProps) {
  return (
    <div
      className={`menu-card ${cardClass}`}
      onClick={() => onNavigate(page)}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") onNavigate(page); }}
    >
      <div className="card-icon-wrap">{icon}</div>
      <h3>{title}</h3>
      <p>{description}</p>
      <div className="card-pills">
        {pills.map((p) => <span key={p} className="pill">{p}</span>)}
      </div>
    </div>
  );
}

interface HomePageProps {
  onNavigate: (page: Page) => void;
}

export function HomePage({ onNavigate }: HomePageProps) {
  return (
    <div className="home-body">
      <div className="home-intro">
        <h2>What would you like to explore?</h2>
        <p>Select a section to dive into your operational data for the selected period.</p>
      </div>
      <div className="menu-grid">
        <MenuCard
          icon="📊"
          title="Service Metrics"
          description="Incident volume, MTTA, MTTR and uptime per service."
          pills={["MTTA", "MTTR", "Uptime"]}
          page="service"
          cardClass="card-service"
          onNavigate={onNavigate}
        />
        <MenuCard
          icon="👥"
          title="Team Metrics"
          description="Incident volume, escalations and response times per team."
          pills={["Incidents", "Escalations"]}
          page="team"
          cardClass="card-team"
          onNavigate={onNavigate}
        />
        <MenuCard
          icon="🧑‍💻"
          title="Responder Metrics"
          description="On-call hours, ack rates and interruption load per responder."
          pills={["Load", "Risk", "Hours"]}
          page="responder"
          cardClass="card-responder"
          onNavigate={onNavigate}
        />
        <MenuCard
          icon="💙"
          title="Team Health"
          description="Fatigue signals, sleep-hour interruptions and burnout risk scoring."
          pills={["Fatigue", "Burnout"]}
          page="teamHealth"
          cardClass="card-health"
          onNavigate={onNavigate}
        />
        <MenuCard
          icon="📈"
          title="Trends"
          description="Weekly incident volume, MTTA and MTTR trend charts over time."
          pills={["Charts", "Weekly"]}
          page="trends"
          cardClass="card-trends"
          onNavigate={onNavigate}
        />
        <MenuCard
          icon="💰"
          title="Oncall Compensation"
          description="Per-responder on-call hours, interruptions and outside-hours breakdown."
          pills={["Hours", "Shifts", "Risk"]}
          page="compensation"
          cardClass="card-comp"
          onNavigate={onNavigate}
        />
      </div>
    </div>
  );
}
