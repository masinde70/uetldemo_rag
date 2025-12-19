#!/usr/bin/env bash
set -e

echo "🚀 Installing MCPs for Codex/Claude + VS Code…"

# --- Serena ---
echo "➕ Adding Serena MCP"
claude mcp add serena -- uvx \
  --from git+https://github.com/oraios/serena \
  serena start-mcp-server --context ide-assistant --project $(pwd)

# --- Sequential Thinking ---
echo "➕ Adding Sequential-Thinking MCP"
claude mcp add sequential-thinking -- uvx \
  --from git+https://github.com/oraios/sequential-thinking \
  sequential-thinking start-mcp-server --context ide-assistant --project $(pwd)

# --- Context7 ---
echo "➕ Adding Context7 MCP"
claude mcp add context7 -- uvx \
  --from git+https://github.com/oraios/context7 \
  context7 start-mcp-server --context ide-assistant --project $(pwd)

# --- Playwright MCP setup ---
echo "📦 Installing Playwright (Node project)"
npm install -D @playwright/test
npx playwright install

echo "➕ Adding Playwright MCP"
claude mcp add playwright -- uvx \
  --from git+https://github.com/oraios/playwright-mcp \
  playwright_mcp start-mcp-server --context ide-assistant --project $(pwd)

echo ""
echo "🎉 All MCPs installed:"
echo "   - Serena"
echo "   - Sequential Thinking"
echo "   - Context7"
echo "   - Playwright"
echo ""
echo "You may now restart VS Code for MCP activation."
