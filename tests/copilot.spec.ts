import { test, expect } from "@playwright/test";

/**
 * SISUiQ E2E Tests
 *
 * Testing Strategy: Full stack integration with mocked backend responses.
 *
 * These tests validate the main user flows:
 * 1. Home page loads correctly with all UI elements
 * 2. User can send a message and receive a response
 * 3. Admin dashboard shows sessions
 *
 * Requirements:
 * - Frontend running at localhost:3000 (started automatically by Playwright)
 * - Backend running at localhost:8000 (start manually or mock responses)
 *
 * For CI: Either spin up full stack with docker-compose or mock the /api/chat route.
 * This implementation uses route interception to mock responses for reliability.
 */

// Global beforeEach to mock the documents API that InsightsPanel calls on mount
test.beforeEach(async ({ page }) => {
  // Mock /api/admin/documents to prevent ECONNREFUSED errors
  await page.route("**/api/admin/documents", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        data: [
          { id: "1", name: "UETCL Strategic Plan", type: "pdf", source: "UETCL", chunk_count: 45 },
          { id: "2", name: "ERA Guidelines 2024", type: "pdf", source: "ERA", chunk_count: 32 },
        ],
      }),
    });
  });
});


test.describe("Home Page", () => {
  test("should display main UI elements", async ({ page }) => {
    await page.goto("/");

    // Verify sidebar is visible
    await expect(page.getByTestId("sidebar")).toBeVisible();

    // Verify all mode buttons exist
    await expect(page.getByTestId("mode-strategy_qa")).toBeVisible();
    await expect(page.getByTestId("mode-actions")).toBeVisible();
    await expect(page.getByTestId("mode-analytics")).toBeVisible();
    await expect(page.getByTestId("mode-regulatory")).toBeVisible();

    // Verify chat area
    await expect(page.getByTestId("chat-area")).toBeVisible();
    await expect(page.getByTestId("chat-input")).toBeVisible();
    await expect(page.getByTestId("send-button")).toBeVisible();

    // Verify insights panel
    await expect(page.getByTestId("insights-panel")).toBeVisible();
  });

  test("should show welcome message when no messages", async ({ page }) => {
    await page.goto("/");

    // Check for welcome text
    await expect(page.getByText("Welcome to SISUiQ")).toBeVisible();
  });

  test("should allow mode switching", async ({ page }) => {
    await page.goto("/");

    // Click on Regulatory mode
    await page.getByTestId("mode-regulatory").click();

    // Verify the button is now selected (has primary styling - bg-primary/15)
    await expect(page.getByTestId("mode-regulatory")).toHaveClass(/bg-primary/);

    // Click on Analytics mode
    await page.getByTestId("mode-analytics").click();

    // Verify Analytics is now selected
    await expect(page.getByTestId("mode-analytics")).toHaveClass(/bg-primary/);
  });
});

test.describe("Chat Flow", () => {
  test("should send message and receive response", async ({ page }) => {
    // Mock the chat API response
    await page.route("**/api/chat", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          answer:
            "Based on the UETCL Strategic Plan, the key objectives include improving transmission efficiency and reducing outages. [UETCL Strategic Plan p.12]",
          session_id: "test-session-123",
          sources: ["[UETCL Strategic Plan p.12]", "[UETCL Strategic Plan p.15]"],
          analytics: null,
        }),
      });
    });

    await page.goto("/");

    // Disable streaming mode to use the mocked /api/chat endpoint
    await page.evaluate(() => {
      localStorage.setItem("sisuiq_streaming", "false");
    });

    // Reload to apply the localStorage change
    await page.reload();

    // Type a message
    const chatInput = page.getByTestId("chat-input");
    await chatInput.fill("What are the strategic objectives?");

    // Click send
    await page.getByTestId("send-button").click();

    // Wait for user message to appear
    await expect(page.getByTestId("message-user")).toBeVisible();

    // Wait for assistant message to appear
    await expect(page.getByTestId("message-assistant")).toBeVisible({
      timeout: 10000,
    });

    // Verify the response content
    await expect(
      page.getByText(/Based on the UETCL Strategic Plan/)
    ).toBeVisible();
  });

  test("should show loading state while waiting for response", async ({
    page,
  }) => {
    // Mock the chat API with a delay
    await page.route("**/api/chat", async (route) => {
      await new Promise((resolve) => setTimeout(resolve, 1000));
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          answer: "Test response",
          session_id: "test-session-123",
          sources: [],
          analytics: null,
        }),
      });
    });

    await page.goto("/");

    // Disable streaming mode to use the mocked /api/chat endpoint
    await page.evaluate(() => {
      localStorage.setItem("sisuiq_streaming", "false");
    });
    await page.reload();

    // Send a message
    await page.getByTestId("chat-input").fill("Test question");
    await page.getByTestId("send-button").click();

    // Verify send button is disabled during loading
    await expect(page.getByTestId("send-button")).toBeDisabled();
  });

  test("should update sources in insights panel", async ({ page }) => {
    // Mock the chat API with sources
    await page.route("**/api/chat", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          answer: "Test response with sources",
          session_id: "test-session-123",
          sources: ["[UETCL Strategic Plan p.12]", "[ERA Regulation 2024]"],
          analytics: null,
        }),
      });
    });

    await page.goto("/");

    // Disable streaming mode to use the mocked /api/chat endpoint
    await page.evaluate(() => {
      localStorage.setItem("sisuiq_streaming", "false");
    });
    await page.reload();

    // Send a message
    await page.getByTestId("chat-input").fill("Test question");
    await page.getByTestId("send-button").click();

    // Wait for response
    await expect(page.getByTestId("message-assistant")).toBeVisible({
      timeout: 10000,
    });

    // Verify sources appear in insights panel
    await expect(
      page.getByText("[UETCL Strategic Plan p.12]")
    ).toBeVisible();
    await expect(page.getByText("[ERA Regulation 2024]")).toBeVisible();
  });
});

test.describe("Admin Dashboard", () => {
  test("should display admin overview", async ({ page }) => {
    // Mock the auth API to simulate authenticated admin user
    await page.route("**/api/auth/me", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          id: "test-user-1",
          email: "admin@sisuiq.local",
          name: "Test Admin",
          role: "admin",
          is_active: true,
          created_at: new Date().toISOString(),
          last_login_at: new Date().toISOString(),
        }),
      });
    });

    // Mock the stats API
    await page.route("**/api/admin/stats*", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          users: 5,
          sessions: 10,
          messages: 50,
          documents: 3,
          chunks: 100,
          analytics_snapshots: 2,
        }),
      });
    });

    await page.goto("/admin/dashboard");

    // Verify admin page loads
    await expect(page.getByRole("heading", { name: "Admin Overview" })).toBeVisible();

    // Verify stats cards exist (using a more specific container if possible or unique text)
    // "Users" appears in sidebar, so let's look for the one in the main content
    const mainContent = page.locator("main");
    await expect(mainContent.getByText("Users")).toBeVisible();
    await expect(mainContent.getByText("Sessions")).toBeVisible();
    await expect(mainContent.getByText("Documents").first()).toBeVisible();
  });

  test("should display sessions list", async ({ page }) => {
    // Mock the auth API to simulate authenticated admin user
    await page.route("**/api/auth/me", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          id: "test-user-1",
          email: "admin@sisuiq.local",
          name: "Test Admin",
          role: "admin",
          is_active: true,
          created_at: new Date().toISOString(),
          last_login_at: new Date().toISOString(),
        }),
      });
    });

    // Mock the sessions API
    await page.route("**/api/admin/sessions*", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          data: [
            {
              id: "session-1",
              user_email: "demo@uetcl.go.ug",
              user_name: "Demo User",
              mode: "strategy_qa",
              title: "Strategic Planning",
              message_count: 5,
              created_at: new Date().toISOString(),
            },
            {
              id: "session-2",
              user_email: "admin@uetcl.go.ug",
              user_name: "Admin User",
              mode: "regulatory",
              title: "ERA Compliance",
              message_count: 3,
              created_at: new Date().toISOString(),
            },
          ],
          count: 2,
        }),
      });
    });

    await page.goto("/admin/sessions");

    // Verify sessions page loads
    await expect(page.getByText("Chat Sessions")).toBeVisible();

    // Verify session rows appear
    await expect(page.getByTestId("admin-session-row").first()).toBeVisible({
      timeout: 5000,
    });

    // Verify user info appears
    await expect(page.getByText("Demo User")).toBeVisible();
  });
});

test.describe("Theme Toggle", () => {
  test("should toggle between light, dark, and system themes", async ({ page }) => {
    await page.goto("/");

    // Find theme toggle buttons by aria-label
    const lightButton = page.getByRole("button", { name: "Switch to Light theme" });
    const darkButton = page.getByRole("button", { name: "Switch to Dark theme" });
    const systemButton = page.getByRole("button", { name: "Switch to System theme" });

    // Wait for theme toggle to be mounted
    await expect(lightButton).toBeVisible({ timeout: 5000 });
    await expect(darkButton).toBeVisible();
    await expect(systemButton).toBeVisible();

    // Click dark theme button
    await darkButton.click();

    // Verify dark class is applied to html element
    await expect(page.locator("html")).toHaveClass(/dark/);

    // Click light theme button
    await lightButton.click();

    // Verify dark class is removed (light mode)
    await expect(page.locator("html")).not.toHaveClass(/dark/);

    // Click system theme button
    await systemButton.click();

    // Verify system theme is selected (theme depends on OS preference)
    // Just verify the click works without error
  });

  test("should persist theme preference across page reloads", async ({ page }) => {
    await page.goto("/");

    // Wait for theme toggle to mount
    const darkButton = page.getByRole("button", { name: "Switch to Dark theme" });
    await expect(darkButton).toBeVisible({ timeout: 5000 });

    // Set dark theme
    await darkButton.click();
    await expect(page.locator("html")).toHaveClass(/dark/);

    // Reload the page
    await page.reload();

    // Verify dark theme persists
    await expect(page.locator("html")).toHaveClass(/dark/);
  });
});
