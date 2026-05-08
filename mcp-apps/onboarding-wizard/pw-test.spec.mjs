import { expect, test } from "@playwright/test";
import { mkdir } from "fs/promises";
import os from "os";
import path from "path";

const PORT = process.env.PORT ?? "5175";
const BASE_URL = `http://localhost:${PORT}/mcp-app.html`;
const APP_NAME = process.env.APP_NAME ?? "onboarding-wizard";
const SCREENSHOT_DIR =
  process.env.SCREENSHOT_DIR ?? path.join(os.homedir(), "tmp-screenshots");

async function screenshot(page, name) {
  await mkdir(SCREENSHOT_DIR, { recursive: true });
  const file = path.join(SCREENSHOT_DIR, `${APP_NAME}-${name}.png`);
  await page.screenshot({ path: file, fullPage: true });
  console.log(`  screenshot: ${file}`);
}

// ── 1. Initial load ────────────────────────────────────────────────────────
test("initial load — stepper and Teams phase visible, no JS errors", async ({ page }) => {
  const errors = [];
  page.on("pageerror", (err) => errors.push(err.message));

  await page.goto(BASE_URL);
  await page.waitForSelector(".stepper", { timeout: 8000 });

  await screenshot(page, "01-initial");

  expect(errors).toHaveLength(0);
  await expect(page.locator(".stepper")).toBeVisible();
  // All 8 steps rendered
  await expect(page.locator(".step")).toHaveCount(8);
  // Phase heading
  await expect(page.locator("h2")).toContainText("Teams");
  // Form fields
  await expect(page.locator("input[placeholder='e.g. Platform Engineering']")).toBeVisible();
});

// ── 2. Add a team and advance ──────────────────────────────────────────────
test("can add a team and navigate to Users phase", async ({ page }) => {
  await page.goto(BASE_URL);
  await page.waitForSelector(".stepper", { timeout: 8000 });

  await page.fill("input[placeholder='e.g. Platform Engineering']", "SRE Team");
  await page.fill("input[placeholder='Optional team description']", "Site reliability");

  const addBtn = page.locator("button", { hasText: "Add Team" });
  await addBtn.click();
  await screenshot(page, "02-team-added");

  // Item row appears
  await expect(page.locator(".item-row-name", { hasText: "SRE Team" })).toBeVisible();

  // Next is now enabled — click it
  await page.locator("button", { hasText: "Next →" }).click();
  await expect(page.locator("h2")).toContainText("Users");
  await screenshot(page, "03-users-phase");
});

// ── 3. CSV upload section toggles ─────────────────────────────────────────
test("CSV upload panel toggles open on Users phase", async ({ page }) => {
  await page.goto(BASE_URL);
  await page.waitForSelector(".stepper", { timeout: 8000 });

  // Skip to Users
  await page.locator("button", { hasText: "Skip this phase" }).click();
  await expect(page.locator("h2")).toContainText("Users");

  // CSV toggle
  await page.locator(".csv-toggle").click();
  await expect(page.locator(".csv-panel")).toBeVisible();
  await expect(page.locator(".csv-schema")).toBeVisible();

  await screenshot(page, "04-csv-panel");
});

// ── 4. Skip all phases reaches Review ─────────────────────────────────────
test("skipping all phases reaches Review & Create", async ({ page }) => {
  await page.goto(BASE_URL);
  await page.waitForSelector(".stepper", { timeout: 8000 });

  const phases = ["Teams", "Users", "Schedules", "Escalation Policies", "Services", "AIOps", "Incident Workflows"];
  for (const _phase of phases) {
    await page.locator("button", { hasText: "Skip this phase" }).click();
  }

  await expect(page.locator("h2")).toContainText("Review");
  await expect(page.locator(".empty-state")).toBeVisible();

  await screenshot(page, "05-review-empty");
});

// ── 5. Dark mode ──────────────────────────────────────────────────────────
test("dark mode renders without blank screen", async ({ page }) => {
  await page.emulateMedia({ colorScheme: "dark" });
  await page.goto(BASE_URL);
  await page.waitForSelector(".stepper", { timeout: 8000 });

  await screenshot(page, "06-dark-mode");
  await expect(page.locator(".stepper")).toBeVisible();
  await expect(page.locator("h2")).toContainText("Teams");
});
