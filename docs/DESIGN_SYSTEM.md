# SISUiQ Design System
## Complete Visual Identity & Component Architecture

> **Cosmic Minimalism** – A futuristic, premium design system inspired by Sana AI and V7's executive-friendly aesthetics, optimized for strategy, analytics, and regulatory intelligence.

---

## 🎨 1. COLOR PALETTE

### 1.1 Core Theme (Cosmic Minimalism)

#### Backgrounds
```css
--bg-deep-space:     #020617;  /* Main background - deep space navy */
--surface-primary:   #0F172A;  /* Panel background - slate dark */
--surface-secondary: #1E293B;  /* Cards, chat bubbles */
--surface-elevated:  #334155;  /* Elevated elements */
```

#### Accent Colors
```css
--neon-cyan:         #22D3EE;  /* Primary neon - electric cyan (Sana glow) */
--neon-violet:       #A855F7;  /* Secondary neon - V7 violet energy */
--accent-orange:     #F97316;  /* Subtle warm accent (sparingly) */
--success-green:     #10B981;  /* Success states */
--warning-amber:     #F59E0B;  /* Warning states */
--error-red:         #EF4444;  /* Error states */
```

#### Text Colors
```css
--text-primary:      #E2E8F0;  /* Soft silver-white */
--text-secondary:    #94A3B8;  /* Muted blue-grey */
--text-tertiary:     #64748B;  /* Dim text */
--text-inverse:      #020617;  /* Dark text on light backgrounds */
```

#### Borders & Effects
```css
--border-subtle:     #1E293B;  /* Soft low-contrast outlines */
--border-medium:     #334155;  /* Medium contrast borders */
--border-strong:     #475569;  /* Strong borders */
```

### 1.2 Tailwind CSS Configuration

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        'deep-space': '#020617',
        'slate': {
          850: '#0F172A',
          900: '#1E293B',
        },
        'neon-cyan': '#22D3EE',
        'neon-violet': '#A855F7',
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'cosmic-grid': 'linear-gradient(to right, #1E293B 1px, transparent 1px), linear-gradient(to bottom, #1E293B 1px, transparent 1px)',
      },
      backdropBlur: {
        'glass': '12px',
      },
      boxShadow: {
        'neon-cyan': '0 0 20px rgba(34, 211, 238, 0.35)',
        'neon-violet': '0 0 20px rgba(168, 85, 247, 0.35)',
        'cosmic': '0 4px 20px rgba(0, 0, 0, 0.3)',
      },
    },
  },
}
```

### 1.3 CSS Custom Properties

```css
:root {
  /* Backgrounds */
  --bg-deep-space: #020617;
  --surface-primary: #0F172A;
  --surface-secondary: #1E293B;

  /* Neon Accents */
  --neon-cyan: #22D3EE;
  --neon-violet: #A855F7;

  /* Effects */
  --glow-cyan: rgba(34, 211, 238, 0.35);
  --glow-violet: rgba(168, 85, 247, 0.35);
  --glass-bg: rgba(15, 23, 42, 0.4);

  /* Gradients */
  --gradient-primary: linear-gradient(135deg, #0EA5E9 0%, #0284C7 100%);
  --gradient-accent: linear-gradient(135deg, #A855F7 0%, #7C3AED 100%);
  --gradient-surface: linear-gradient(180deg, #0F172A 0%, #1E293B 100%);
}
```

---

## 📝 2. TYPOGRAPHY

### 2.1 Font Stack

```css
/* Primary Font - Interface */
--font-primary: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;

/* Display Font - Headers & Branding */
--font-display: 'Space Grotesk', 'Sora', sans-serif;

/* Monospace - Code & Data */
--font-mono: 'JetBrains Mono', 'Fira Code', monospace;
```

### 2.2 Type Scale

| Element | Size | Weight | Line Height | Letter Spacing |
|---------|------|--------|-------------|----------------|
| **H1** | 36px (2.25rem) | 700 | 1.2 | -0.02em |
| **H2** | 30px (1.875rem) | 700 | 1.3 | -0.01em |
| **H3** | 24px (1.5rem) | 600 | 1.4 | 0 |
| **H4** | 20px (1.25rem) | 600 | 1.4 | 0 |
| **Body Large** | 18px (1.125rem) | 400 | 1.6 | 0 |
| **Body** | 16px (1rem) | 400 | 1.6 | 0 |
| **Body Small** | 14px (0.875rem) | 400 | 1.5 | 0 |
| **Caption** | 12px (0.75rem) | 500 | 1.4 | 0.02em |
| **Label** | 12px (0.75rem) | 600 | 1.2 | 0.05em |

### 2.3 Tailwind Typography Classes

```css
.text-display-1 { @apply text-4xl font-bold tracking-tight font-display; }
.text-display-2 { @apply text-3xl font-bold tracking-tight font-display; }
.text-heading-1 { @apply text-2xl font-semibold; }
.text-heading-2 { @apply text-xl font-semibold; }
.text-body-lg   { @apply text-lg font-normal; }
.text-body      { @apply text-base font-normal; }
.text-body-sm   { @apply text-sm font-normal; }
.text-caption   { @apply text-xs font-medium tracking-wide; }
```

---

## 🧩 3. COMPONENT STYLING

### 3.1 Chat Bubbles

#### User Message
```tsx
<div className="flex justify-end">
  <div className="max-w-[70%] rounded-2xl bg-gradient-to-br from-cyan-500 to-cyan-600 p-4 text-black shadow-lg">
    <p className="text-sm">User message here</p>
  </div>
</div>
```

**Styling:**
- Right-aligned
- Gradient: `#0EA5E9` → `#0284C7`
- `rounded-2xl`
- Text color: black for contrast
- Drop shadow

#### Assistant Message
```tsx
<div className="flex justify-start">
  <div className="max-w-[70%] rounded-2xl border border-slate-700 bg-slate-800 p-4 shadow-cosmic">
    <p className="text-sm text-slate-200">Assistant response here</p>
  </div>
</div>
```

**Styling:**
- Left-aligned
- Background: `#1E293B`
- Subtle 1px border: `#334155`
- Soft shadow

### 3.2 Cards

```tsx
<div className="group rounded-2xl border border-slate-700/50 bg-slate-900/40 p-6 backdrop-blur-glass transition-all hover:border-neon-cyan/50 hover:shadow-neon-cyan">
  <h3 className="mb-2 text-lg font-semibold text-slate-100">Card Title</h3>
  <p className="text-sm text-slate-400">Card content</p>
</div>
```

**Features:**
- `rounded-2xl`
- Glass effect with backdrop blur
- Glow on hover
- Smooth transitions

### 3.3 Panels (Glass Effect)

```tsx
<div className="rounded-2xl border border-slate-700/30 bg-slate-900/40 p-8 backdrop-blur-md">
  {/* Panel content */}
</div>
```

**Properties:**
- Semi-transparent background
- `backdrop-blur-md`
- Subtle border
- Large padding

### 3.4 Buttons

#### Primary Button
```tsx
<button className="rounded-xl bg-cyan-500 px-6 py-3 font-medium text-black transition-all hover:bg-cyan-400 hover:shadow-neon-cyan">
  Primary Action
</button>
```

#### Secondary Button
```tsx
<button className="rounded-xl border border-slate-700 bg-slate-800 px-6 py-3 font-medium text-slate-200 transition-all hover:bg-slate-700">
  Secondary Action
</button>
```

#### Ghost Button
```tsx
<button className="rounded-xl px-6 py-3 font-medium text-slate-300 transition-all hover:bg-slate-800/50">
  Ghost Action
</button>
```

### 3.5 Input Fields

```tsx
<input
  type="text"
  className="w-full rounded-xl border border-slate-700 bg-slate-900/60 px-4 py-3 text-slate-200 placeholder-slate-500 backdrop-blur-sm transition-all focus:border-neon-cyan focus:outline-none focus:ring-2 focus:ring-neon-cyan/50"
  placeholder="Enter text..."
/>
```

### 3.6 Tables

```tsx
<table className="w-full">
  <thead>
    <tr className="border-b border-slate-700">
      <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-neon-cyan">
        Column Header
      </th>
    </tr>
  </thead>
  <tbody>
    <tr className="border-b border-slate-800 transition-colors hover:bg-slate-800/50">
      <td className="px-4 py-3 text-sm text-slate-300">Cell Data</td>
    </tr>
  </tbody>
</table>
```

---

## 🎭 4. SPECIAL EFFECTS

### 4.1 Neon Glow

```css
/* Cyan Glow */
.glow-cyan {
  box-shadow: 0 0 20px rgba(34, 211, 238, 0.35);
}

/* Violet Glow */
.glow-violet {
  box-shadow: 0 0 20px rgba(168, 85, 247, 0.35);
}

/* Animated Pulse Glow */
@keyframes pulse-glow {
  0%, 100% { box-shadow: 0 0 20px rgba(34, 211, 238, 0.35); }
  50% { box-shadow: 0 0 30px rgba(34, 211, 238, 0.5); }
}

.pulse-glow {
  animation: pulse-glow 2s ease-in-out infinite;
}
```

### 4.2 Grid Background

```tsx
<div className="relative min-h-screen bg-deep-space">
  {/* Diagonal Grid Overlay */}
  <div
    className="absolute inset-0 opacity-[0.06]"
    style={{
      backgroundImage: `
        linear-gradient(45deg, #1E293B 1px, transparent 1px),
        linear-gradient(-45deg, #1E293B 1px, transparent 1px)
      `,
      backgroundSize: '40px 40px'
    }}
  />

  {/* Content */}
  <div className="relative z-10">
    {/* Your content here */}
  </div>
</div>
```

### 4.3 Glass Morphism

```css
.glass-panel {
  background: rgba(15, 23, 42, 0.4);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(30, 41, 59, 0.3);
}
```

---

## 🖼️ 5. LAYOUT ARCHITECTURE

### 5.1 Main Chat Interface

```tsx
<div className="flex h-screen bg-deep-space">
  {/* Left Sidebar - Navigation */}
  <aside className="w-64 border-r border-slate-800 bg-slate-900/40 backdrop-blur-md">
    {/* Logo */}
    {/* Mode Selector */}
    {/* Navigation Links */}
  </aside>

  {/* Main Chat Area */}
  <main className="flex-1 flex flex-col">
    {/* Header */}
    <header className="border-b border-slate-800 bg-slate-900/40 p-4 backdrop-blur-md">
      {/* Mode indicator, user info */}
    </header>

    {/* Messages Area */}
    <div className="flex-1 overflow-y-auto p-6">
      {/* Chat messages */}
    </div>

    {/* Input Area */}
    <div className="border-t border-slate-800 bg-slate-900/40 p-4 backdrop-blur-md">
      {/* Message input */}
    </div>
  </main>

  {/* Right Insights Panel */}
  <aside className="w-96 border-l border-slate-800 bg-slate-900/40 backdrop-blur-md p-6">
    {/* Retrieved sources */}
    {/* Analytics */}
    {/* Suggestions */}
  </aside>
</div>
```

### 5.2 Admin Dashboard

```tsx
<div className="min-h-screen bg-deep-space p-8">
  {/* Header */}
  <header className="mb-8">
    <h1 className="text-display-1 text-slate-100">Admin Dashboard</h1>
  </header>

  {/* Stats Grid */}
  <div className="mb-8 grid grid-cols-4 gap-6">
    {/* Stat cards */}
  </div>

  {/* Data Tables */}
  <div className="grid grid-cols-2 gap-6">
    {/* Sessions table */}
    {/* Documents table */}
  </div>
</div>
```

---

## 🎨 6. ICONOGRAPHY

### 6.1 Icon Libraries
- **Primary**: Lucide React
- **Alternative**: Radix Icons

### 6.2 Icon Styling
```tsx
import { MessageSquare, FileText, BarChart3, Shield } from 'lucide-react';

<MessageSquare
  className="h-5 w-5 text-slate-400 transition-colors group-hover:text-neon-cyan"
  strokeWidth={1.5}
/>
```

**Guidelines:**
- Size: 16px (h-4 w-4) to 24px (h-6 w-6)
- Stroke width: 1.5 (thin, minimal)
- Color: slate-400 default, neon accent on hover

---

## 📐 7. SPACING SYSTEM

```css
/* Spacing Scale (Tailwind) */
--space-xs:   0.25rem;  /* 4px  - p-1 */
--space-sm:   0.5rem;   /* 8px  - p-2 */
--space-md:   1rem;     /* 16px - p-4 */
--space-lg:   1.5rem;   /* 24px - p-6 */
--space-xl:   2rem;     /* 32px - p-8 */
--space-2xl:  3rem;     /* 48px - p-12 */
```

**Component Spacing:**
- Card padding: `p-6` (24px)
- Button padding: `px-6 py-3` (24px × 12px)
- Section gaps: `gap-6` (24px)
- Page margins: `p-8` (32px)

---

## 🚀 8. SHADCN/UI CUSTOMIZATION

### 8.1 Theme Configuration

```typescript
// app/globals.css
@layer base {
  :root {
    --background: 222.2 84% 4.9%;
    --foreground: 210 40% 98%;
    --card: 222.2 84% 4.9%;
    --card-foreground: 210 40% 98%;
    --popover: 222.2 84% 4.9%;
    --popover-foreground: 210 40% 98%;
    --primary: 186 100% 53%;
    --primary-foreground: 222.2 84% 4.9%;
    --secondary: 217.2 32.6% 17.5%;
    --secondary-foreground: 210 40% 98%;
    --muted: 217.2 32.6% 17.5%;
    --muted-foreground: 215 20.2% 65.1%;
    --accent: 217.2 32.6% 17.5%;
    --accent-foreground: 210 40% 98%;
    --destructive: 0 62.8% 30.6%;
    --destructive-foreground: 210 40% 98%;
    --border: 217.2 32.6% 17.5%;
    --input: 217.2 32.6% 17.5%;
    --ring: 186 100% 53%;
    --radius: 0.75rem;
  }
}
```

---

## 📦 9. COMPONENT LIBRARY

### Essential shadcn/ui Components to Install

```bash
# Core components
npx shadcn-ui@latest add button
npx shadcn-ui@latest add card
npx shadcn-ui@latest add input
npx shadcn-ui@latest add textarea
npx shadcn-ui@latest add dropdown-menu
npx shadcn-ui@latest add dialog
npx shadcn-ui@latest add tabs
npx shadcn-ui@latest add table
npx shadcn-ui@latest add badge
npx shadcn-ui@latest add avatar
npx shadcn-ui@latest add tooltip
npx shadcn-ui@latest add select
npx shadcn-ui@latest add separator
npx shadcn-ui@latest add scroll-area
```

---

## 🎯 10. QUICK REFERENCE

### Copy-Paste Utility Classes

```css
/* Cosmic Background */
.cosmic-bg {
  @apply bg-deep-space;
}

/* Glass Panel */
.glass-panel {
  @apply rounded-2xl border border-slate-700/30 bg-slate-900/40 backdrop-blur-md;
}

/* Neon Text */
.text-neon-cyan {
  @apply text-neon-cyan drop-shadow-[0_0_8px_rgba(34,211,238,0.5)];
}

/* Hover Glow */
.hover-glow {
  @apply transition-all hover:shadow-neon-cyan;
}

/* Card Standard */
.card-cosmic {
  @apply glass-panel p-6 transition-all hover:border-neon-cyan/50 hover:shadow-neon-cyan;
}
```

---

## 📝 11. IMPLEMENTATION CHECKLIST

- [ ] Install fonts (Inter, Space Grotesk)
- [ ] Configure Tailwind with custom colors
- [ ] Install shadcn/ui components
- [ ] Create reusable component wrappers
- [ ] Implement glass morphism utilities
- [ ] Add neon glow animations
- [ ] Set up grid background pattern
- [ ] Configure typography scale
- [ ] Test responsive breakpoints
- [ ] Implement dark mode (already dark)

---

## 🔗 Resources

- **Tailwind CSS**: https://tailwindcss.com
- **shadcn/ui**: https://ui.shadcn.com
- **Lucide Icons**: https://lucide.dev
- **Space Grotesk Font**: https://fonts.google.com/specimen/Space+Grotesk
- **Inter Font**: https://fonts.google.com/specimen/Inter

---

**Ready to implement!** This design system provides everything needed to create a production-ready, visually stunning SISUiQ interface.
