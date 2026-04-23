/**
 * Playwright visual test template for MCP apps.
 *
 * Copy this file to mcp-apps/<app-name>/pw-test.spec.mjs
 * and fill in the app-specific selectors and interaction flow.
 *
 * Usage:
 *   Terminal 1: npm run dev:mock
 *   Terminal 2: npm run test
 *
 * Env vars (set in package.json "test" script):
 *   PORT           — Vite dev server port (default: 5173)
 *   APP_NAME       — used as screenshot filename prefix (default: "app")
 *   SCREENSHOT_DIR — where to save PNGs (default: ~/tmp-screenshots)
 */

import { test, expect } from "@playwright/test";
import { mkdir } from "fs/promises";
import path from "path";
import os from "os";

const PORT = process.env.PORT ?? "5173";
const BASE_URL = `http://localhost:${PORT}/mcp-app.html`;
const APP_NAME = process.env.APP_NAME ?? "app";
const SCREENSHOT_DIR =
  process.env.SCREENSHOT_DIR ?? path.join(os.homedir(), "tmp-screenshots");

async function screenshot(page, name) {
  await mkdir(SCREENSHOT_DIR, { recursive: true });
  const file = path.join(SCREENSHOT_DIR, `${APP_NAME}-${name}.png`);
  await page.screenshot({ path: file, fullPage: true });
  console.log(`  screenshot: ${file}`);
}

// ── 1. Initial load ────────────────────────────────────────────────────────
test("initial load — no blank screen, no JS error", async ({ page }) => {
  const errors = [];
  page.on("pageerror", (err) => errors.push(err.message));

  await page.goto(BASE_URL);
  await page.waitForSelector(".app", { timeout: 8000 });
  await screenshot(page, "01-initial");

  expect(errors).toHaveLength(0);
});

// ── 2. Mock data visible — tables / cards populated ─────────────────────
test("mock data renders — not empty", async ({ page }) => {
  await page.goto(BASE_URL);
  await page.waitForSelector(".app", { timeout: 8000 });

  // TODO: replace with the first meaningful data element in your app
  // Examples:
  //   await expect(page.locator(".incident-list .incident-row").first()).toBeVisible();
  //   await expect(page.locator("table tbody tr").first()).toBeVisible();
  await expect(page.locator(".app")).toBeVisible();

  await screenshot(page, "02-data");
});

// ── 3. Dark theme ──────────────────────────────────────────────────────────
test("dark theme — readable text contrast", async ({ page }) => {
  await page.goto(BASE_URL + "?theme=dark");
  await page.waitForSelector(".app", { timeout: 8000 });
  await screenshot(page, "03-dark");

  // Verify the dark theme attribute is applied
  const html = page.locator("html");
  await expect(html).toHaveAttribute("data-theme", "dark");
});

// ── 4. Primary interaction (app-specific) ──────────────────────────────
test("primary interaction — TODO fill in", async ({ page }) => {
  await page.goto(BASE_URL);
  await page.waitForSelector(".app", { timeout: 8000 });

  // TODO: implement the main multi-step flow for your app.
  // Example (post-mortem builder):
  //   await page.click(".incident-row");
  //   await page.waitForSelector(".timeline-events", { timeout: 5000 });
  //   await screenshot(page, "04-timeline");
  //   await expect(page.locator(".timeline-card").first()).toBeVisible();

  // Example (operations-intelligence):
  //   await page.click('button:has-text("Insights")');
  //   await page.waitForTimeout(2500);
  //   await screenshot(page, "04-insights");
  //   await expect(page.locator(".insight-card").first()).toBeVisible();

  await screenshot(page, "04-interaction");
});
