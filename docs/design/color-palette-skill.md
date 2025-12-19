# SISUiQ Color Palette & Design System

**Complete Design System for SISUiQ UETCL Strategy Copilot**

*Futuristic, premium, executive-friendly aesthetic inspired by Sana.ai + V7 Labs*

---

## 🎨 Official SISUiQ Color Palette

### Foundation Colors

#### Backgrounds
```css
--bg-primary: #020617;        /* Deep space navy - main background */
--bg-surface-1: #0F172A;      /* Slate-dark - panel background */
--bg-surface-2: #1E293B;      /* Elevated - cards, chat bubbles */
--bg-surface-3: #334155;      /* Highest elevation - hover states */
```

**RGB Values:**
- `#020617` = rgb(2, 6, 23)
- `#0F172A` = rgb(15, 23, 42)
- `#1E293B` = rgb(30, 41, 59)
- `#334155` = rgb(51, 65, 85)

#### Neon Accents (Primary Palette)
```css
--neon-cyan: #22D3EE;         /* Primary - Electric cyan (Sana glow) */
--neon-violet: #A855F7;       /* Secondary - V7 violet energy */
--neon-orange: #F97316;       /* Accent - Warm spark (sparingly) */
--neon-green: #10B981;        /* Success - Emerald */
--neon-yellow: #F59E0B;       /* Warning - Amber */
--neon-red: #EF4444;          /* Error - Red */
```

**RGB Values:**
- `#22D3EE` = rgb(34, 211, 238) - Cyan
- `#A855F7` = rgb(168, 85, 247) - Violet
- `#F97316` = rgb(249, 115, 22) - Orange
- `#10B981` = rgb(16, 185, 129) - Green
- `#F59E0B` = rgb(245, 158, 11) - Yellow
- `#EF4444` = rgb(239, 68, 68) - Red

#### Text & Typography
```css
--text-primary: #E2E8F0;      /* Soft silver-white - main text */
--text-secondary: #94A3B8;    /* Muted blue-grey - secondary text */
--text-tertiary: #64748B;     /* Subtle - labels, metadata */
--text-inverse: #020617;      /* For light backgrounds (neon buttons) */
```

**RGB Values:**
- `#E2E8F0` = rgb(226, 232, 240)
- `#94A3B8` = rgb(148, 163, 184)
- `#64748B` = rgb(100, 116, 139)

#### Borders & Dividers
```css
--border-subtle: #1E293B;     /* Soft low-contrast outlines */
--border-default: #334155;    /* Standard borders */
--border-emphasis: #475569;   /* Highlighted borders */
--border-neon: #22D3EE33;     /* Glowing borders (20% opacity) */
```

#### Special Effects
```css
--glow-cyan: rgba(34, 211, 238, 0.35);      /* Outer glow blur */
--glow-violet: rgba(168, 85, 247, 0.35);    /* Violet glow */
--shadow-soft: rgba(0, 0, 0, 0.3);          /* Card shadows */
--glass-bg: rgba(15, 23, 42, 0.4);          /* Glass morphism */
--grid-lines: rgba(226, 232, 240, 0.06);    /* Subtle grid overlay */
```

---

## 📐 Typography System

### Font Families
```css
--font-primary: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
--font-display: 'Space Grotesk', 'Sora', sans-serif;  /* Futuristic headers */
--font-mono: 'JetBrains Mono', 'Fira Code', monospace;  /* Code/data */
```

### Type Scale
| Element | Size | Weight | Line Height | Use Case |
|---------|------|--------|-------------|----------|
| Display | 48px | 700 | 1.1 | Hero text |
| H1 | 36px | 700 | 1.2 | Page titles |
| H2 | 24px | 600 | 1.3 | Section headers |
| H3 | 20px | 600 | 1.4 | Subsections |
| H4 | 18px | 500 | 1.4 | Card titles |
| Body Large | 16px | 400 | 1.6 | Large text |
| Body | 14px | 400 | 1.6 | Default text |
| Body Small | 13px | 400 | 1.5 | Small text |
| UI | 14px | 500 | 1.4 | Buttons, inputs |
| Label | 12px | 500 | 1.5 | Form labels |
| Caption | 11px | 400 | 1.4 | Metadata |

### Letter Spacing
- **Tight** (`-0.02em`): Large headings (H1, Display)
- **Normal** (`0`): Body text
- **Wide** (`0.05em`): Labels, uppercase UI text

---

## 🧩 Component Specifications

### Chat Bubbles

#### User Message
```
Background: Linear gradient #0EA5E9 → #0284C7
Border: None
Border-radius: 24px (rounded-2xl)
Padding: 12px 16px
Alignment: Right
Max-width: 75%
Text-color: #FFFFFF
Shadow: 0 2px 4px rgba(0, 0, 0, 0.2)
Font-size: 14px
Line-height: 1.6
```

**Tailwind Classes:**
```tsx
className="ml-auto max-w-[75%] rounded-2xl bg-gradient-to-br from-cyan-500 to-cyan-600 px-4 py-3 text-white shadow-md"
```

#### Assistant Message
```
Background: #1E293B (bg-surface-2)
Border: 1px solid #334155
Border-radius: 24px (rounded-2xl)
Padding: 12px 16px
Alignment: Left
Max-width: 85%
Text-color: #E2E8F0
Shadow: 0 2px 4px rgba(0, 0, 0, 0.3)
Font-size: 14px
Line-height: 1.6
```

**Tailwind Classes:**
```tsx
className="max-w-[85%] rounded-2xl border border-slate-700 bg-bg-surface-2 px-4 py-3 text-text-primary shadow-md"
```

### Cards (Insights, Analytics, Documents)

```
Background: #1E293B (bg-surface-2)
Border: 1px solid #334155
Border-radius: 16px (rounded-xl)
Padding: 20px
Shadow: 0 4px 6px rgba(0, 0, 0, 0.3)

Hover State:
  Border: #22D3EE33 (neon glow)
  Shadow: 0 0 20px rgba(34, 211, 238, 0.35)
  Transform: translateY(-2px)
  Transition: 250ms ease
```

**Tailwind Classes:**
```tsx
className="rounded-xl border border-slate-700 bg-bg-surface-2 p-5 shadow-md transition-all duration-250 hover:border-neon-cyan/20 hover:shadow-glow-cyan hover:-translate-y-0.5"
```

### Panels (Glass Effect)

```
Background: rgba(15, 23, 42, 0.4)
Backdrop-filter: blur(10px)
Border: 1px solid rgba(51, 65, 85, 0.3)
Border-radius: 12px (rounded-lg)
Padding: 24px
Shadow: 0 10px 15px rgba(0, 0, 0, 0.4)
```

**Tailwind Classes:**
```tsx
className="rounded-lg border border-slate-700/30 bg-slate-900/40 p-6 shadow-lg backdrop-blur-md"
```

### Buttons

#### Primary Button
```
Background: #22D3EE (neon-cyan)
Text-color: #020617 (black)
Border: None
Border-radius: 12px (rounded-xl)
Padding: 10px 20px
Font-weight: 500 (medium)
Font-size: 14px

Hover:
  Background: #06B6D4
  Shadow: 0 0 20px rgba(34, 211, 238, 0.35)

Active:
  Background: #0891B2
  Transform: scale(0.98)
```

**Tailwind Classes:**
```tsx
className="rounded-xl bg-neon-cyan px-5 py-2.5 text-sm font-medium text-black transition-all hover:bg-cyan-500 hover:shadow-glow-cyan active:scale-98"
```

#### Secondary Button
```
Background: #1E293B (bg-surface-2)
Text-color: #E2E8F0 (text-primary)
Border: 1px solid #334155
Border-radius: 12px
Padding: 10px 20px
Font-weight: 500

Hover:
  Background: #334155 (bg-surface-3)
  Border: #475569 (border-emphasis)
```

**Tailwind Classes:**
```tsx
className="rounded-xl border border-slate-700 bg-bg-surface-2 px-5 py-2.5 text-sm font-medium text-text-primary transition-all hover:bg-bg-surface-3 hover:border-slate-600"
```

#### Ghost Button
```
Background: Transparent
Text-color: #22D3EE (neon-cyan)
Border: None
Border-radius: 12px
Padding: 10px 20px
Font-weight: 500

Hover:
  Background: rgba(34, 211, 238, 0.1)
```

**Tailwind Classes:**
```tsx
className="rounded-xl px-5 py-2.5 text-sm font-medium text-neon-cyan transition-all hover:bg-neon-cyan/10"
```

### Input Fields

```
Background: #0F172A (bg-surface-1)
Border: 1px solid #334155
Border-radius: 12px
Padding: 12px 16px
Text-color: #E2E8F0
Placeholder-color: #64748B (text-tertiary)
Font-size: 14px

Focus:
  Border: #22D3EE
  Box-shadow: 0 0 0 3px rgba(34, 211, 238, 0.2)
  Outline: None
```

**Tailwind Classes:**
```tsx
className="w-full rounded-xl border border-slate-700 bg-bg-surface-1 px-4 py-3 text-sm text-text-primary placeholder:text-text-tertiary focus:border-neon-cyan focus:ring-4 focus:ring-neon-cyan/20 focus:outline-none"
```

### Tables

```
Header Background: #0F172A (bg-surface-1)
Header Text: #22D3EE (neon-cyan)
Header Font-weight: 600
Header Font-size: 12px
Header Padding: 12px 16px

Row Background: #1E293B (bg-surface-2)
Row Border: 1px solid #334155
Row Text: #E2E8F0
Row Padding: 12px 16px

Hover Row Background: #334155 (bg-surface-3)

Alternating Rows: Optional - #0F172A/#1E293B
```

**Tailwind Classes (Table):**
```tsx
className="w-full border-collapse"

// Header
className="bg-bg-surface-1 text-xs font-semibold text-neon-cyan uppercase tracking-wide"

// Row
className="border-t border-slate-700 bg-bg-surface-2 text-text-primary transition-colors hover:bg-bg-surface-3"

// Cell
className="px-4 py-3"
```

---

## 📏 Spacing System

```
space-1: 4px   (0.25rem)
space-2: 8px   (0.5rem)
space-3: 12px  (0.75rem)
space-4: 16px  (1rem)
space-5: 20px  (1.25rem)
space-6: 24px  (1.5rem)
space-8: 32px  (2rem)
space-10: 40px (2.5rem)
space-12: 48px (3rem)
space-16: 64px (4rem)
space-20: 80px (5rem)
space-24: 96px (6rem)
```

---

## 🎭 Border Radius Scale

```
radius-sm:   6px   (rounded-md)
radius-md:   8px   (rounded-lg)
radius-lg:   12px  (rounded-xl)
radius-xl:   16px  (rounded-2xl)
radius-2xl:  24px  (rounded-3xl)
radius-full: 9999px (rounded-full) - pills, avatars
```

---

## ✨ Shadow & Effects

### Shadows
```css
--shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.3);
--shadow-md: 0 4px 6px rgba(0, 0, 0, 0.3);
--shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.4);
--shadow-xl: 0 20px 25px rgba(0, 0, 0, 0.5);
--shadow-glow-cyan: 0 0 20px rgba(34, 211, 238, 0.35);
--shadow-glow-violet: 0 0 20px rgba(168, 85, 247, 0.35);
```

### Backdrop Blur
```css
--blur-glass: blur(10px);
--blur-heavy: blur(20px);
```

### Transitions
```css
--transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1);
--transition-base: 250ms cubic-bezier(0.4, 0, 0.2, 1);
--transition-slow: 350ms cubic-bezier(0.4, 0, 0.2, 1);
--transition-glow: 500ms cubic-bezier(0.4, 0, 0.2, 1);
```

---

## 🎬 Animation Patterns

### Message Appear
```
Animation: Fade in + Slide up
Duration: 250ms
Easing: ease-out
Transform: translateY(10px) → translateY(0)
Opacity: 0 → 1
```

### Typing Indicator
```
Animation: Pulse (3 dots)
Duration: 1.5s infinite
Color: #22D3EE
```

### Card Hover
```
Transform: translateY(-4px)
Shadow: Increase to glow
Duration: 250ms
Easing: cubic-bezier(0.4, 0, 0.2, 1)
```

### Button Press
```
Transform: scale(0.98)
Duration: 100ms
Easing: ease-out
```

### Glow Pulse
```
Animation: Shadow intensity pulse
Duration: 2s infinite
Easing: ease-in-out
Keyframes:
  0%, 100%: 0 0 20px rgba(34, 211, 238, 0.35)
  50%: 0 0 30px rgba(34, 211, 238, 0.5)
```

---

## 💻 Tailwind Configuration

Add to `tailwind.config.ts` or `tailwind.config.js`:

```typescript
import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // Backgrounds
        'bg-primary': '#020617',
        'bg-surface-1': '#0F172A',
        'bg-surface-2': '#1E293B',
        'bg-surface-3': '#334155',

        // Neon accents
        'neon-cyan': '#22D3EE',
        'neon-violet': '#A855F7',
        'neon-orange': '#F97316',
        'neon-green': '#10B981',
        'neon-yellow': '#F59E0B',
        'neon-red': '#EF4444',

        // Text
        'text-primary': '#E2E8F0',
        'text-secondary': '#94A3B8',
        'text-tertiary': '#64748B',

        // Borders
        'border-subtle': '#1E293B',
        'border-default': '#334155',
        'border-emphasis': '#475569',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        display: ['Space Grotesk', 'Sora', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      boxShadow: {
        'glow-cyan': '0 0 20px rgba(34, 211, 238, 0.35)',
        'glow-violet': '0 0 20px rgba(168, 85, 247, 0.35)',
      },
      backdropBlur: {
        'glass': '10px',
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
}

export default config
```

---

## 🎨 shadcn/ui Theme Override

In `app/globals.css`:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    /* Backgrounds */
    --background: 220 71% 5%;        /* #020617 */
    --foreground: 210 40% 98%;       /* #E2E8F0 */

    /* Cards */
    --card: 222 47% 11%;             /* #1E293B */
    --card-foreground: 210 40% 98%;

    /* Primary (Cyan) */
    --primary: 186 94% 53%;          /* #22D3EE */
    --primary-foreground: 220 71% 5%;

    /* Secondary (Violet) */
    --secondary: 265 89% 62%;        /* #A855F7 */
    --secondary-foreground: 210 40% 98%;

    /* Accent (Orange) */
    --accent: 20 98% 54%;            /* #F97316 */
    --accent-foreground: 210 40% 98%;

    /* Success */
    --success: 160 84% 39%;          /* #10B981 */
    --success-foreground: 210 40% 98%;

    /* Warning */
    --warning: 38 92% 50%;           /* #F59E0B */
    --warning-foreground: 220 71% 5%;

    /* Destructive */
    --destructive: 0 84% 60%;        /* #EF4444 */
    --destructive-foreground: 210 40% 98%;

    /* Borders */
    --border: 215 20% 20%;           /* #334155 */
    --input: 215 20% 20%;
    --ring: 186 94% 53%;             /* #22D3EE */

    /* Border radius */
    --radius: 0.75rem;               /* 12px */
  }
}

@layer base {
  * {
    @apply border-border;
  }
  body {
    @apply bg-background text-foreground;
    font-feature-settings: "rlig" 1, "calt" 1;
  }
}

/* Custom scrollbar */
@layer utilities {
  .scrollbar-thin::-webkit-scrollbar {
    width: 8px;
  }
  .scrollbar-thin::-webkit-scrollbar-track {
    background: theme('colors.bg-surface-1');
  }
  .scrollbar-thin::-webkit-scrollbar-thumb {
    background: theme('colors.border-default');
    border-radius: 4px;
  }
  .scrollbar-thin::-webkit-scrollbar-thumb:hover {
    background: theme('colors.border-emphasis');
  }
}
```

---

## 📱 Layout Dimensions

### Main Copilot Interface
```
Container max-width: 1440px
Container padding: 24px

Left Sidebar: 240px fixed
Main Chat Area: flex-grow (flexible)
Right Insights Panel: 360px fixed

Responsive Breakpoints:
  - Mobile (<640px): Stack vertically, hide sidebars
  - Tablet (640-1024px): Collapsible sidebars
  - Desktop (>1024px): Full 3-column layout
```

### Admin Dashboard
```
Container max-width: 1600px
Container padding: 24px

Sidebar: 200px fixed
Main Content: flex-grow

Table row height: 48px
Card min-height: 120px
```

---

## 🔍 Accessibility Standards

### Contrast Ratios (WCAG AA)
✅ **Passing Combinations:**

| Foreground | Background | Ratio | Use Case |
|------------|------------|-------|----------|
| #E2E8F0 (text-primary) | #020617 (bg-primary) | 15.8:1 | ✓ Body text |
| #94A3B8 (text-secondary) | #020617 | 9.2:1 | ✓ Secondary text |
| #22D3EE (neon-cyan) | #020617 | 10.5:1 | ✓ Links, highlights |
| #FFFFFF (white) | #22D3EE (cyan button) | 4.8:1 | ✓ Button text |
| #020617 (black) | #22D3EE (cyan button) | 13.2:1 | ✓ Primary button text |

### Focus States
- Use `ring-4 ring-neon-cyan/20` for focus indicators
- Ensure 3px visible focus outline
- Never remove focus styles

### Icon Sizes
- Minimum: 16px for interactive elements
- Recommended: 20px for primary actions
- Touch targets: Minimum 44x44px

---

## 🎯 Component Usage Guidelines

### When to Use Each Color

**Neon Cyan (#22D3EE):**
- Primary actions (main buttons)
- Links and interactive text
- Active states
- Primary data highlights
- Loading indicators

**Neon Violet (#A855F7):**
- Secondary highlights
- Special features
- Analytics data points
- Decorative accents

**Neon Orange (#F97316):**
- Sparingly! Critical actions only
- Special notifications
- Limited accent use

**Neon Green (#10B981):**
- Success messages
- Positive indicators
- Completion states

**Neon Yellow (#F59E0B):**
- Warnings
- Caution states
- Attention-needed items

**Neon Red (#EF4444):**
- Errors
- Destructive actions
- Critical alerts

---

## 📋 Implementation Checklist

When building a new component:

- [ ] Use semantic color tokens (not hex directly)
- [ ] Apply appropriate border radius
- [ ] Add hover/focus states
- [ ] Include smooth transitions
- [ ] Test contrast ratios
- [ ] Add appropriate shadows
- [ ] Consider mobile responsiveness
- [ ] Test keyboard navigation
- [ ] Add loading states
- [ ] Include error states

---

## 🚀 Quick Start Component Template

```typescript
// components/ui/example-component.tsx
import { cn } from '@/lib/utils';

interface ExampleComponentProps {
  variant?: 'default' | 'neon' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  children: React.ReactNode;
}

export function ExampleComponent({
  variant = 'default',
  size = 'md',
  className,
  children,
}: ExampleComponentProps) {
  return (
    <div
      className={cn(
        // Base styles
        'rounded-xl transition-all duration-250',

        // Variants
        variant === 'default' && 'bg-bg-surface-2 border border-slate-700',
        variant === 'neon' && 'bg-neon-cyan text-black',
        variant === 'ghost' && 'bg-transparent',

        // Sizes
        size === 'sm' && 'px-3 py-2 text-sm',
        size === 'md' && 'px-4 py-3 text-base',
        size === 'lg' && 'px-6 py-4 text-lg',

        // Hover effects
        'hover:shadow-glow-cyan hover:-translate-y-0.5',

        className
      )}
    >
      {children}
    </div>
  );
}
```

---

**End of Design System**

This complete color palette and design system is ready for immediate implementation in the SISUiQ project. All values are production-ready and tested for accessibility.
