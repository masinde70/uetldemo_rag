/**
 * Visual Regression Tests
 *
 * Uses Playwright's screenshot comparison for UI regression testing.
 */

import { test, expect } from '@playwright/test';

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

test.describe('Visual Regression Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the app
    await page.goto('/');
    // Wait for initial load
    await page.waitForSelector('[data-testid="app-container"]');
  });

  test('homepage matches snapshot', async ({ page }) => {
    // Wait for animations to complete
    await page.waitForTimeout(1000);

    await expect(page).toHaveScreenshot('homepage.png', {
      fullPage: true,
      animations: 'disabled',
    });
  });

  test('sidebar modes match snapshot', async ({ page }) => {
    const sidebar = page.locator('[data-testid="sidebar"]').first();

    await expect(sidebar).toHaveScreenshot('sidebar-modes.png', {
      animations: 'disabled',
    });
  });

  test('chat area empty state matches snapshot', async ({ page }) => {
    const chatArea = page.locator('[data-testid="chat-area"]');

    await expect(chatArea).toHaveScreenshot('chat-empty-state.png', {
      animations: 'disabled',
    });
  });

  test('chat input matches snapshot', async ({ page }) => {
    const chatInput = page.locator('[data-testid="chat-input"]');

    await expect(chatInput).toHaveScreenshot('chat-input.png', {
      animations: 'disabled',
    });
  });

  test('insights panel matches snapshot', async ({ page }) => {
    const insights = page.locator('[data-testid="insights-panel"]');

    if (await insights.isVisible()) {
      await expect(insights).toHaveScreenshot('insights-panel.png', {
        animations: 'disabled',
      });
    }
  });

  test('mode selection changes UI', async ({ page }) => {
    // This test takes two screenshots so needs more time
    test.setTimeout(60000);

    // Click on Actions mode (label is 'Action Planner')
    await page.getByTestId('mode-actions').click();
    await page.waitForTimeout(500);

    await expect(page).toHaveScreenshot('mode-actions.png', {
      fullPage: true,
      animations: 'disabled',
      maxDiffPixelRatio: 0.02, // Allow 2% pixel difference for minor rendering variations
    });

    // Click on Analytics mode (label is 'Analytics + Strategy')
    await page.getByTestId('mode-analytics').click();
    await page.waitForTimeout(500);

    await expect(page).toHaveScreenshot('mode-analytics.png', {
      fullPage: true,
      animations: 'disabled',
      maxDiffPixelRatio: 0.02,
    });
  });

  test('loading state matches snapshot', async ({ page }) => {
    // Type a message - the data-testid is directly on the textarea element
    const input = page.getByTestId('chat-input');
    await input.fill('Test message');

    // Submit (this will show loading state)
    await input.press('Enter');

    // Capture loading state quickly
    await page.waitForTimeout(100);

    const messageList = page.locator('[data-testid="message-list"]');
    await expect(messageList).toHaveScreenshot('loading-state.png', {
      animations: 'disabled',
      maxDiffPixelRatio: 0.02, // Allow 2% pixel difference for minor rendering variations
    });
  });

  test('dark theme consistency', async ({ page }) => {
    // Verify dark theme elements
    const body = page.locator('body');
    const bgColor = await body.evaluate((el) =>
      window.getComputedStyle(el).backgroundColor
    );

    // Should be dark background
    expect(bgColor).toMatch(/rgb\(\d{1,2},\s*\d{1,2},\s*\d{1,2}\)/);
  });
});

test.describe('Responsive Visual Tests', () => {
  test('mobile viewport matches snapshot', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');
    await page.waitForSelector('[data-testid="app-container"]');
    await page.waitForTimeout(1000);

    await expect(page).toHaveScreenshot('mobile-viewport.png', {
      fullPage: true,
      animations: 'disabled',
    });
  });

  test('tablet viewport matches snapshot', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.goto('/');
    await page.waitForSelector('[data-testid="app-container"]');
    await page.waitForTimeout(1000);

    await expect(page).toHaveScreenshot('tablet-viewport.png', {
      fullPage: true,
      animations: 'disabled',
    });
  });
});
