// @ts-check
import { themes as prismThemes } from 'prism-react-renderer';

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'PagerDuty MCP Server',
  tagline: 'Connect AI assistants to your PagerDuty account via the Model Context Protocol',
  favicon: 'img/favicon.ico',
  future: {
    v4: true,
  },
  url: 'https://pagerduty.github.io',
  baseUrl: '/pagerduty-mcp-server/',
  organizationName: 'PagerDuty',
  projectName: 'pagerduty-mcp-server',
  trailingSlash: false,
  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',
  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },
  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: './sidebars.js',
          editUrl: 'https://github.com/PagerDuty/pagerduty-mcp-server/tree/main/website/',
          routeBasePath: 'docs',
          breadcrumbs: true,
        },
        blog: false,
        theme: {
          customCss: './src/css/custom.css',
        },
      }),
    ],
  ],
  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      image: 'img/pagerduty-social-card.png',
      colorMode: {
        defaultMode: 'light',
        disableSwitch: false,
        respectPrefersColorScheme: true,
      },
      docs: {
        sidebar: {
          hideable: true,
          autoCollapseCategories: false,
        },
      },

      // ── Algolia DocSearch ─────────────────────────────────────────────
      // Apply for free DocSearch at: https://docsearch.algolia.com/apply/
      // Replace the placeholder values below with your real credentials.
      algolia: {
        appId: 'YOUR_ALGOLIA_APP_ID',
        apiKey: 'YOUR_ALGOLIA_SEARCH_API_KEY', // public search-only key
        indexName: 'pagerduty-mcp-server',
        contextualSearch: true,
        searchPagePath: 'search',
        insights: false,
      },

      // ── Navbar ────────────────────────────────────────────────────────
      navbar: {
        title: 'PagerDuty MCP Server',
        hideOnScroll: false,
        logo: {
          alt: 'PagerDuty Logo',
          src: 'img/logo.png',
          srcDark: 'img/logo.png',
          width: 28,
          height: 28,
        },
        items: [
          {
            type: 'docSidebar',
            sidebarId: 'docsSidebar',
            position: 'left',
            label: 'Docs',
          },
          {
            to: '/docs/tools/overview',
            label: 'Tools',
            position: 'left',
          },
          {
            to: '/docs/configuration/tool-filtering',
            label: 'Tool Filtering',
            position: 'left',
          },
          {
            to: '/docs/use-cases/overview',
            label: 'Use Cases',
            position: 'left',
          },
          {
            to: '/docs/community/streams',
            label: 'Streams',
            position: 'left',
          },
          {
            to: '/docs/experimental/overview',
            label: '🧪 Experimental',
            position: 'left',
          },
          {
            type: 'search',
            position: 'right',
          },
          {
            href: 'https://github.com/PagerDuty/pagerduty-mcp-server',
            label: 'GitHub',
            position: 'right',
          },
        ],
      },

      // ── Footer ────────────────────────────────────────────────────────
      footer: {
        style: 'dark',
        links: [
          {
            title: 'Docs',
            items: [
              { label: 'Quick Start', to: '/docs/getting-started/quick-start' },
              { label: 'Tools Reference', to: '/docs/tools/overview' },
              { label: 'Tool Filtering', to: '/docs/configuration/tool-filtering' },
              { label: 'Remote Server', to: '/docs/remote-server/setup' },
            ],
          },
          {
            title: 'Install',
            items: [
              { label: 'Cursor', to: '/docs/installation/cursor' },
              { label: 'VS Code', to: '/docs/installation/vscode' },
              { label: 'Claude Desktop', to: '/docs/installation/claude-desktop' },
              { label: 'Docker', to: '/docs/installation/docker' },
            ],
          },
          {
            title: 'Community',
            items: [
              { label: 'GitHub', href: 'https://github.com/PagerDuty/pagerduty-mcp-server' },
              { label: 'Issues', href: 'https://github.com/PagerDuty/pagerduty-mcp-server/issues' },
              { label: 'Contributing', to: '/docs/contributing/guidelines' },
            ],
          },
          {
            title: 'PagerDuty',
            items: [
              { label: 'Developer Docs', href: 'https://developer.pagerduty.com' },
              { label: 'API Reference', href: 'https://developer.pagerduty.com/api-reference' },
              { label: 'PagerDuty.com', href: 'https://www.pagerduty.com' },
            ],
          },
        ],
        copyright: `Copyright © ${new Date().getFullYear()} PagerDuty, Inc. Built with Docusaurus.`,
      },

      // ── Prism syntax highlighting ─────────────────────────────────────
      prism: {
        theme: prismThemes.nightOwlLight,
        darkTheme: prismThemes.dracula,
        additionalLanguages: ['bash', 'json', 'python', 'yaml', 'docker'],
        defaultLanguage: 'bash',
      },

      // ── Announcement bar (optional — remove if not needed) ─────────────
      // announcementBar: {
      //   id: 'v015',
      //   content: 'PagerDuty MCP Server v0.15.1 is out — <a href="/docs/getting-started/quick-start">Get started</a>',
      //   backgroundColor: '#e6f3ea',
      //   textColor: '#005a24',
      //   isCloseable: true,
      // },
    }),
};

export default config;
