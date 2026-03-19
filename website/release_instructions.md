# Release Instructions

How to publish the PagerDuty MCP Server documentation site to GitHub Pages.

## Prerequisites

- `gh` CLI installed and authenticated (`gh auth status`)
- `node` 20+ and `npm` installed
- Write access to the PagerDuty GitHub organization

---

## One-Time Setup

### 1. Create the GitHub repository

```bash
gh repo create PagerDuty/pagerduty-mcp-server-docs --public
```

### 2. Initialize and push the local repo

```bash
git init
git add .
git commit -m "init: initial docs site"
git remote add origin https://github.com/PagerDuty/pagerduty-mcp-server-docs
git push -u origin main
```

### 3. Enable GitHub Pages

In the GitHub UI:

1. Go to the repo → **Settings** → **Pages**
2. Under **Build and deployment**, set **Source** to **GitHub Actions**
3. Save

> Do **not** select the legacy "Deploy from a branch" option — the workflow uses the modern `actions/deploy-pages` method.

### 4. Configure Algolia Search (optional)

The site ships with Algolia DocSearch pre-configured but with placeholder credentials.

1. Apply for free DocSearch at **https://docsearch.algolia.com/apply/**
   (free for open-source projects with public docs)
2. Once approved, replace the three placeholder values in `docusaurus.config.js`:

```js
algolia: {
  appId: 'YOUR_ALGOLIA_APP_ID',        // ← replace
  apiKey: 'YOUR_ALGOLIA_SEARCH_API_KEY', // ← replace (search-only public key)
  indexName: 'pagerduty-mcp-server',   // ← replace if different
  ...
}
```

3. Commit and push — search will be live on the next deploy.

### 5. Custom domain (optional)

To serve the site from a custom domain (e.g. `docs.pagerduty.com`):

1. Create `static/CNAME` containing only the custom domain:

```
docs.pagerduty.com
```

2. Update `docusaurus.config.js`:

```js
url: 'https://docs.pagerduty.com',
baseUrl: '/',
```

3. Point a DNS `CNAME` record for `docs.pagerduty.com` → `pagerduty.github.io`
4. In GitHub Pages settings, set the custom domain and enable **Enforce HTTPS**

### 6. How to setup the Custom domain

⏺ Two places to configure — DNS at your registrar, and GitHub:

  1. DNS — add a CNAME record at your registrar

  ┌───────┬──────────────────────┬──────────────────────────┬──────┐
  │ Type  │         Host         │          Value           │ TTL  │
  ├───────┼──────────────────────┼──────────────────────────┼──────┤
  │ CNAME │ docs (or @ for root) │ imjaroiswebdev.github.io │ 3600 │
  └───────┴──────────────────────┴──────────────────────────┴──────┘

  For a subdomain like docs.yourdomain.com:
  - Host: docs
  - Points to: imjaroiswebdev.github.io

  For a root domain yourdomain.com, use 4 A records instead (GitHub's IPs):
  185.199.108.153
  185.199.109.153
  185.199.110.153
  185.199.111.153

  ---
  2. Repo — add a CNAME file

  echo "docs.yourdomain.com" > static/CNAME
  git add static/CNAME
  git commit -m "feat: add custom domain"
  git push

  Placing it in static/ ensures Docusaurus copies it to the build root on every deploy, so GitHub never loses it.

  ---
  3. GitHub Pages settings

  Go back to Settings → Pages → Custom domain, type docs.yourdomain.com, click Save, then tick Enforce HTTPS (available ~10 min after
  DNS propagates).

  ---
  4. Update docusaurus.config.js

  url: 'https://docs.yourdomain.com',
  baseUrl: '/',  // ← change from '/pagerduty-mcp-server-docs/' to '/'

  DNS propagation takes anywhere from a few minutes to 48 hours depending on the registrar.


---

## Deploying Changes

Every push to `main` triggers an automatic build and deploy via the workflow at
`.github/workflows/deploy.yml`. No manual steps required.

**Workflow summary:**
1. Checks out the repo
2. Installs dependencies with `npm ci`
3. Builds the static site with `npm run build`
4. Uploads the `build/` directory as a Pages artifact
5. Deploys to `https://pagerduty.github.io/pagerduty-mcp-server-docs/`

Monitor deployments at:
**https://github.com/PagerDuty/pagerduty-mcp-server-docs/actions**

---

## Manual Deploy (if needed)

To trigger a deployment without a code change, use the GitHub UI:

1. Go to **Actions** → **Deploy to GitHub Pages**
2. Click **Run workflow** → **Run workflow**

Or via CLI:

```bash
gh workflow run deploy.yml --repo PagerDuty/pagerduty-mcp-server-docs
```

---

## Verifying a Deploy

After the Actions workflow completes (~2 minutes), verify the site is live:

```bash
curl -s -o /dev/null -w "%{http_code}" https://pagerduty.github.io/pagerduty-mcp-server-docs/
# Expected: 200
```

---

## Local Preview Before Releasing

Always verify the production build locally before pushing:

```bash
npm run build   # catches broken links, MDX errors
npm run serve   # serves build/ at http://localhost:3000/pagerduty-mcp-server-docs/
```
