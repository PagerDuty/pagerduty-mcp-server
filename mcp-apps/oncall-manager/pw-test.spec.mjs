// @ts-check
import { test, expect } from "@playwright/test";
import { mkdir } from "node:fs/promises";
import { join } from "node:path";

const PORT = process.env.PORT ?? "5174";
const BASE_URL = `http://localhost:${PORT}/mcp-app.html`;
const APP_NAME = process.env.APP_NAME ?? "oncall-manager";
const SCREENSHOT_DIR = process.env.SCREENSHOT_DIR ?? `${process.env.HOME}/tmp-screenshots`;

test.beforeAll(async () => {
  await mkdir(SCREENSHOT_DIR, { recursive: true });
});

test("initial load — My On-Calls tab", async ({ page }) => {
  await page.goto(BASE_URL);
  await page.waitForSelector(".countdown-row", { timeout: 10000 });
  await page.screenshot({
    path: join(SCREENSHOT_DIR, `${APP_NAME}-myoncalls.png`),
    fullPage: true,
  });
  // Should show at least one countdown card
  const cards = await page.locator(".countdown-card").count();
  expect(cards).toBeGreaterThan(0);
});

test("7-day grid renders", async ({ page }) => {
  await page.goto(BASE_URL);
  await page.waitForSelector(".grid-table", { timeout: 10000 });
  // Table should have at least one data row
  const rows = await page.locator(".grid-table tbody tr").count();
  expect(rows).toBeGreaterThan(0);
});

test("overrides tab renders", async ({ page }) => {
  await page.goto(BASE_URL);
  await page.waitForSelector(".tabs", { timeout: 10000 });
  await page.click(".tab-btn:has-text('Overrides')");
  await page.waitForSelector(".override-list", { timeout: 5000 });
  await page.screenshot({
    path: join(SCREENSHOT_DIR, `${APP_NAME}-overrides.png`),
    fullPage: true,
  });
});

test("coverage wizard opens and advances steps", async ({ page }) => {
  await page.goto(BASE_URL);
  await page.waitForSelector(".countdown-card", { timeout: 10000 });
  // Click "Find coverage" on the active shift card (if present) or Overrides tab
  const findCovBtn = page.locator("button:has-text('Find coverage')").first();
  if (await findCovBtn.isVisible()) {
    await findCovBtn.click();
  } else {
    await page.click(".tab-btn:has-text('Overrides')");
    await page.click("button:has-text('Find Coverage')");
  }
  await page.waitForSelector(".wizard-dialog", { timeout: 5000 });
  await page.screenshot({
    path: join(SCREENSHOT_DIR, `${APP_NAME}-wizard-step1.png`),
    fullPage: true,
  });
  // Step indicator should show step 1 or 2 active (if preselected)
  const stepNum = await page.locator(".wizard-step.active .wizard-step-num").first().textContent();
  expect(["1", "2"].includes(stepNum ?? "")).toBeTruthy();
});
