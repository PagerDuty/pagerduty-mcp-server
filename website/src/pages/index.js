import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import styles from './index.module.css';

const features = [
  {
    icon: '⚡',
    title: 'Local MCP Server',
    description:
      'Run locally via uvx or Docker. Zero config — just add your API token and point any MCP-compatible client at it.',
    link: '/docs/installation/cursor',
    linkLabel: 'Installation guides →',
  },
  {
    icon: '☁️',
    title: 'Remote MCP Server',
    description:
      'PagerDuty-hosted, OAuth-based. Connect in seconds from Cursor or VS Code — no local installation required.',
    link: '/docs/remote-server/setup',
    linkLabel: 'Remote setup →',
  },
  {
    icon: '🔧',
    title: '55 Tools Across 14 Domains',
    description:
      'Incidents, on-call schedules, services, teams, event orchestrations, status pages, and more — all from your AI assistant.',
    link: '/docs/tools/overview',
    linkLabel: 'Browse tools →',
  },
  {
    icon: '🔒',
    title: 'Safe by Default',
    description:
      'Read-only mode out of the box. Opt into write tools explicitly with --enable-write-tools when you need them.',
    link: '/docs/configuration/write-tools',
    linkLabel: 'Learn more →',
  },
  {
    icon: '🎛️',
    title: 'Tool Filtering',
    description:
      'Too many tools hurts AI performance. Use mcp-proxy to expose only the subset your workflow needs.',
    link: '/docs/configuration/tool-filtering',
    linkLabel: 'Filtering guide →',
  },
  {
    icon: '🌍',
    title: 'EU Region Support',
    description:
      'Point the server at api.eu.pagerduty.com with a single environment variable. Works with both local and remote modes.',
    link: '/docs/configuration/environment-variables',
    linkLabel: 'Configuration →',
  },
];

const quickLinks = [
  { label: 'Cursor', to: '/docs/installation/cursor' },
  { label: 'VS Code', to: '/docs/installation/vscode' },
  { label: 'Claude Desktop', to: '/docs/installation/claude-desktop' },
  { label: 'Docker', to: '/docs/installation/docker' },
];

function HomepageHero() {
  const { siteConfig } = useDocusaurusContext();
  return (
    <header className={clsx('hero', styles.heroBanner)}>
      <div className={clsx('container', styles.heroInner)}>
        <div className={styles.heroBadge}>Model Context Protocol</div>
        <h1 className={clsx('hero__title', styles.heroTitle)}>
          {siteConfig.title}
        </h1>
        <p className={clsx('hero__subtitle', styles.heroSubtitle)}>
          {siteConfig.tagline}
        </p>
        <div className={styles.heroButtons}>
          <Link
            className={clsx('button button--secondary button--lg', styles.btnPrimary)}
            to="/docs/getting-started/quick-start"
          >
            Get Started
          </Link>
          <Link
            className={clsx('button button--outline button--secondary button--lg', styles.btnSecondary)}
            href="https://github.com/PagerDuty/pagerduty-mcp-server"
          >
            View on GitHub
          </Link>
        </div>
        <div className={styles.quickInstall}>
          <span className={styles.quickInstallLabel}>Quick install:</span>
          <code className={styles.quickInstallCode}>uvx pagerduty-mcp</code>
        </div>
      </div>
    </header>
  );
}

function ClientLinks() {
  return (
    <div className={styles.clientBar}>
      <div className="container">
        <div className={styles.clientBarInner}>
          <span className={styles.clientBarLabel}>Works with</span>
          {quickLinks.map(({ label, to }) => (
            <Link key={label} to={to} className={styles.clientChip}>
              {label}
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}

function FeaturesGrid() {
  return (
    <section className={styles.featuresSection}>
      <div className="container">
        <div className={styles.featuresGrid}>
          {features.map(({ icon, title, description, link, linkLabel }) => (
            <div key={title} className={styles.featureCard}>
              <div className={styles.featureIcon}>{icon}</div>
              <h3 className={styles.featureTitle}>{title}</h3>
              <p className={styles.featureDesc}>{description}</p>
              <Link to={link} className={styles.featureLink}>{linkLabel}</Link>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function Spotlight() {
  return (
    <section className={styles.spotlight}>
      <div className="container">
        <div className={styles.spotlightInner}>
          <div className={styles.spotlightMedia}>
            <img
              src={require('@site/static/img/icc-vscode-full.png').default}
              alt="Incident Command Center running inside VS Code"
              className={styles.spotlightImg}
              loading="lazy"
            />
          </div>
          <div className={styles.spotlightContent}>
            <span className={styles.spotlightBadge}>Experimental</span>
            <h2 className={styles.spotlightTitle}>Incident Command Center</h2>
            <p className={styles.spotlightDesc}>
              A live incident dashboard that renders directly inside your editor.
              View, triage, and resolve PagerDuty incidents without leaving your chat session.
            </p>
            <Link
              to="/docs/experimental/incident-command-center"
              className={styles.spotlightLink}
            >
              Explore the experiment →
            </Link>
          </div>
        </div>
      </div>
    </section>
  );
}

function CtaBanner() {
  return (
    <section className={styles.ctaBanner}>
      <div className="container">
        <div className={styles.ctaBannerInner}>
          <div>
            <h2 className={styles.ctaTitle}>Ready to connect your AI to PagerDuty?</h2>
            <p className={styles.ctaDesc}>
              Follow the quick-start guide and have your first tool call running in under 5 minutes.
            </p>
          </div>
          <div className={styles.ctaActions}>
            <Link className={clsx('button button--primary button--lg')} to="/docs/getting-started/quick-start">
              Read the Docs
            </Link>
          </div>
        </div>
      </div>
    </section>
  );
}

export default function Home() {
  return (
    <Layout
      title="Home"
      description="Official documentation for the PagerDuty MCP Server — connect AI assistants to PagerDuty via the Model Context Protocol."
    >
      <HomepageHero />
      <ClientLinks />
      <FeaturesGrid />
      <Spotlight />
      <CtaBanner />
    </Layout>
  );
}
