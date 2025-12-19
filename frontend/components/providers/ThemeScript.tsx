/**
 * Inline script to prevent flash of unstyled content (FOUC)
 * This runs before React hydrates to set the correct theme class
 */
export function ThemeScript() {
  const script = `
    (function() {
      try {
        var storageKey = 'sisuiq-theme';
        var theme = localStorage.getItem(storageKey);
        var systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
        var resolvedTheme = theme === 'system' || !theme ? systemTheme : theme;
        document.documentElement.classList.remove('light', 'dark');
        document.documentElement.classList.add(resolvedTheme);
      } catch (e) {}
    })();
  `;

  return (
    <script
      dangerouslySetInnerHTML={{ __html: script }}
      suppressHydrationWarning
    />
  );
}
