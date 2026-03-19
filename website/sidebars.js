// @ts-check

/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
  docsSidebar: [
    'intro',
    {
      type: 'category',
      label: 'Getting Started',
      collapsed: false,
      items: [
        'getting-started/prerequisites',
        'getting-started/quick-start',
        'getting-started/authentication',
      ],
    },
    {
      type: 'category',
      label: 'Installation',
      items: [
        'installation/cursor',
        'installation/vscode',
        'installation/claude-desktop',
        'installation/docker',
      ],
    },
    {
      type: 'category',
      label: 'Remote Server',
      items: [
        'remote-server/setup',
      ],
    },
    {
      type: 'category',
      label: 'Configuration',
      items: [
        'configuration/environment-variables',
        'configuration/write-tools',
        'configuration/tool-filtering',
      ],
    },
    {
      type: 'category',
      label: 'Tools Reference',
      items: [
        'tools/overview',
        'tools/alert-grouping',
        'tools/alerts',
        'tools/change-events',
        'tools/incidents',
        'tools/incident-workflows',
        'tools/services',
        'tools/teams',
        'tools/users',
        'tools/schedules',
        'tools/oncalls',
        'tools/log-entries',
        'tools/escalation-policies',
        'tools/event-orchestrations',
        'tools/status-pages',
      ],
    },
    {
      type: 'category',
      label: 'Use Cases',
      items: [
        'use-cases/overview',
        'use-cases/incident-investigation',
        'use-cases/on-call-handoff',
        'use-cases/service-health-check',
        'use-cases/incident-response-automation',
      ],
    },
    {
      type: 'category',
      label: 'Community',
      items: [
        'community/streams',
      ],
    },
    {
      type: 'category',
      label: 'Experimental',
      items: [
        'experimental/overview',
        'experimental/incident-command-center',
      ],
    },
    {
      type: 'category',
      label: 'Contributing',
      items: [
        'contributing/development',
        'contributing/guidelines',
      ],
    },
  ],
};

export default sidebars;
