# Website (retired)

> [!IMPORTANT]
> The published documentation site at `https://pagerduty.github.io/pagerduty-mcp-server/` has been
> retired. The documentation now lives in [`../docs/`](../docs/) and is read directly on GitHub —
> start from the [Contents table in the README](../README.md#contents).
>
> This Docusaurus scaffolding is kept for reference only. Its `docs/` directory was moved to the
> repository root, so the site no longer builds as-is, and the GitHub Pages deploy workflow has been
> removed. Edit the Markdown under `../docs/` instead.

This website is built using [Docusaurus](https://docusaurus.io/), a modern static website generator.

## Installation

```bash
yarn
```

## Local Development

```bash
yarn start
```

This command starts a local development server and opens up a browser window. Most changes are reflected live without having to restart the server.

## Build

```bash
yarn build
```

This command generates static content into the `build` directory and can be served using any static contents hosting service.

## Deployment

Using SSH:

```bash
USE_SSH=true yarn deploy
```

Not using SSH:

```bash
GIT_USER=<Your GitHub username> yarn deploy
```

If you are using GitHub pages for hosting, this command is a convenient way to build the website and push to the `gh-pages` branch.
