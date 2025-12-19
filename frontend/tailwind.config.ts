import type { Config } from "tailwindcss";

export default {
  darkMode: ["class"],
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Core shadcn overrides
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
        success: {
          DEFAULT: "hsl(var(--success))",
          foreground: "hsl(var(--success-foreground))",
        },
        warning: {
          DEFAULT: "hsl(var(--warning))",
          foreground: "hsl(var(--warning-foreground))",
        },

        // SISUiQ Semantic Palette (theme-aware via CSS variables)
        'bg-primary': 'hsl(var(--bg-primary))',
        'bg-surface-1': 'hsl(var(--bg-surface-1))',
        'bg-surface-2': 'hsl(var(--bg-surface-2))',
        'bg-surface-3': 'hsl(var(--bg-surface-3))',

        'text-primary': 'hsl(var(--text-primary))',
        'text-secondary': 'hsl(var(--text-secondary))',
        'text-tertiary': 'hsl(var(--text-tertiary))',

        'border-subtle': 'hsl(var(--border-subtle))',
        'border-default': 'hsl(var(--border-default))',
        'border-emphasis': 'hsl(var(--border-emphasis))',

        // Accent colors (theme-aware)
        'accent-primary': 'hsl(var(--accent-primary))',
        'accent-secondary': 'hsl(var(--accent-secondary))',
        'accent-tertiary': 'hsl(var(--accent-tertiary))',

        // Neon colors (theme-aware - vibrant in dark, muted in light)
        'neon-cyan': 'hsl(var(--neon-cyan))',
        'neon-violet': 'hsl(var(--neon-violet))',
        'neon-orange': 'hsl(var(--neon-orange))',
        'neon-green': 'hsl(var(--neon-green))',
        'neon-yellow': 'hsl(var(--neon-yellow))',
        'neon-red': 'hsl(var(--neon-red))',
      },
      fontFamily: {
        sans: ['var(--font-geist)', 'system-ui', 'sans-serif'],
        display: ['var(--font-display)', 'system-ui', 'sans-serif'],
        mono: ['var(--font-geist-mono)', 'monospace'],
      },
      boxShadow: {
        'glow-cyan': '0 0 20px rgba(34, 211, 238, 0.35)',
        'glow-violet': '0 0 20px rgba(168, 85, 247, 0.35)',
        'glow-primary': '0 0 20px hsl(var(--primary) / 0.35)',
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
        xl: "16px",
        '2xl': "24px",
      },
      animation: {
        'glow-pulse': 'glow 2s ease-in-out infinite',
        'fade-in': 'fadeIn 250ms ease-out',
        'slide-up': 'slideUp 250ms ease-out',
      },
      keyframes: {
        glow: {
          '0%, 100%': { boxShadow: '0 0 20px rgba(34, 211, 238, 0.35)' },
          '50%': { boxShadow: '0 0 30px rgba(34, 211, 238, 0.5)' },
        },
        fadeIn: {
          from: { opacity: '0' },
          to: { opacity: '1' },
        },
        slideUp: {
          from: { transform: 'translateY(10px)' },
          to: { transform: 'translateY(0)' },
        },
      },
    },
  },
  plugins: [],
} satisfies Config;
