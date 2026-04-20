/**
 * Playwright visual tests — Operations Intelligence MCP App
 *
 * Usage:
 *   Terminal 1: npm run dev:mock
 *   Terminal 2: npm run test
 */

import { test, expect } from "@playwright/test";
import { mkdir } from "fs/promises";
import path from "path";
import os from "os";

const PORT = process.env.PORT ?? "5173";
const BASE_URL = `http://localhost:${PORT}/mcp-app.html`;
const APP_NAME = process.env.APP_NAME ?? "operations-intelligence";
const SCREENSHOT_DIR =
  process.env.SCREENSHOT_DIR ?? path.join(os.homedir(), "tmp-screenshots");

async function screenshot(page, name) {
  await mkdir(SCREENSHOT_DIR, { recursive: true });
  const file = path.join(SCREENSHOT_DIR, `${APP_NAME}-${name}.png`);
  await page.screenshot({ path: file, fullPage: true });
  console.log(`  screenshot: ${file}`);
}

// ── 1. Initial load — Operational tab ─────────────────────────────────────
test("initial load — Operational tab renders with KPI cards", async ({ page }) => {
  const errors = [];
  page.on("pageerror", (err) => errors.push(err.message));

  await page.goto(BASE_URL);
  await page.waitForSelector(".tabs", { timeout: 8000 });
  await screenshot(page, "01-operational");

  // KPI cards must be visible
  await expect(page.locator(".kpi-card").first()).toBeVisible();
  // At least one service row in the services table
  await expect(page.locator(".analytics-table tbody tr, .service-row").first()).toBeVisible();
  expect(errors).toHaveLength(0);
});

// ── 2. Dark theme ──────────────────────────────────────────────────────────
test("dark theme — readable on Operational tab", async ({ page }) => {
  await page.goto(BASE_URL + "?theme=dark");
  await page.waitForSelector(".tabs", { timeout: 8000 });
  await screenshot(page, "02-dark");

  const html = page.locator("html");
  await expect(html).toHaveAttribute("data-theme", "dark");
});

// ── 3. Trends tab — charts render ──────────────────────────────────────────────
test("Trends tab — charts render", async ({ page }) => {
  await page.goto(BASE_URL);
  await page.waitForSelector(".tabs", { timeout: 8000 });

  await page.click('button:has-text("Trends")');
  await page.waitForSelector(".trend-card", { timeout: 5000 });
  await screenshot(page, "03-trends");

  await expect(page.locator(".trend-card").first()).toBeVisible();
});
