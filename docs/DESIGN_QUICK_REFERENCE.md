# SISUiQ Design System - Quick Reference Card

> **One-page cheat sheet** for developers and designers implementing the SISUiQ interface.

---

## 🎨 COLOR PALETTE (Hex Codes)

```css
/* Copy-paste into your code */

/* Backgrounds */
--bg-deep-space:     #020617
--surface-primary:   #0F172A
--surface-secondary: #1E293B

/* Neons */
--neon-cyan:         #22D3EE
--neon-violet:       #A855F7
--accent-orange:     #F97316

/* Text */
--text-primary:      #E2E8F0
--text-secondary:    #94A3B8

/* Borders */
--border-subtle:     #1E293B
```

---

## 📝 TYPOGRAPHY

```css
/* Headers */
H1: 36px/700/Space Grotesk/-0.72px
H2: 30px/700/Space Grotesk/-0.3px
H3: 24px/600/Inter
H4: 20px/600/Inter

/* Body */
Body:    16px/400/Inter/1.6 line-height
Small:   14px/400/Inter/1.5 line-height
Caption: 12px/500/Inter/+0.24px
```

---

## 🧩 COMPONENT CODE SNIPPETS

### Primary Button
```tsx
<button className="rounded-xl bg-cyan-500 px-6 py-3 font-medium text-black transition-all hover:bg-cyan-400 hover:shadow-neon-cyan">
  Click Me
</button>
```

### Card with Glass Effect
```tsx
<div className="rounded-2xl border border-slate-700/30 bg-slate-900/40 p-6 backdrop-blur-md hover:border-neon-cyan/50 hover:shadow-neon-cyan">
  {children}
</div>
```

### User Message Bubble
```tsx
<div className="flex justify-end">
  <div className="max-w-[70%] rounded-2xl bg-gradient-to-br from-cyan-500 to-cyan-600 p-4 text-black shadow-lg">
    <p className="text-sm">{message}</p>
  </div>
</div>
```

### Input Field
```tsx
<input
  className="w-full rounded-xl border border-slate-700 bg-slate-900/60 px-4 py-3 text-slate-200 placeholder-slate-500 backdrop-blur-sm focus:border-neon-cyan focus:outline-none focus:ring-2 focus:ring-neon-cyan/50"
  placeholder="Type here..."
/>
```

---

## 🎭 EFFECTS

### Neon Glow (CSS)
```css
.glow-cyan {
  box-shadow: 0 0 20px rgba(34, 211, 238, 0.35);
}

.glow-violet {
  box-shadow: 0 0 20px rgba(168, 85, 247, 0.35);
}
```

### Glass Panel (Tailwind)
```html
<div class="bg-slate-900/40 backdrop-blur-md border border-slate-700/30">
```

### Cosmic Grid Background
```tsx
<div className="relative min-h-screen bg-deep-space">
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
  <div className="relative z-10">{children}</div>
</div>
```

---

## 📐 LAYOUT STRUCTURE

### 3-Column Chat Interface
```
┌────────────┬─────────────────┬─────────────┐
│  Sidebar   │  Main Chat      │  Insights   │
│  256px     │  1280px         │  384px      │
└────────────┴─────────────────┴─────────────┘
```

### Spacing
- Card padding: `p-6` (24px)
- Section gap: `gap-6` (24px)
- Page margin: `p-8` (32px)

---

## 🚀 TAILWIND CONFIG (Essential)

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        'deep-space': '#020617',
        'neon-cyan': '#22D3EE',
        'neon-violet': '#A855F7',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        display: ['Space Grotesk', 'sans-serif'],
      },
      boxShadow: {
        'neon-cyan': '0 0 20px rgba(34, 211, 238, 0.35)',
      },
    },
  },
}
```

---

## 📦 SHADCN/UI COMPONENTS TO INSTALL

```bash
npx shadcn-ui@latest add button
npx shadcn-ui@latest add card
npx shadcn-ui@latest add input
npx shadcn-ui@latest add dropdown-menu
npx shadcn-ui@latest add dialog
npx shadcn-ui@latest add table
```

---

## 🎯 DESIGN PRINCIPLES

1. **Cosmic Minimalism** - Dark space theme with neon accents
2. **Glass Morphism** - Semi-transparent panels with blur
3. **Subtle Glows** - Neon effects on hover/focus
4. **High Contrast Text** - Ensure readability
5. **Smooth Transitions** - 200-300ms animations
6. **Generous Spacing** - Never cramped
7. **Futuristic Feel** - Space-themed, executive-friendly

---

## 🔗 FULL DOCUMENTATION

- **Complete Design System**: `docs/DESIGN_SYSTEM.md`
- **Figma Blueprint**: `docs/FIGMA_BLUEPRINT.md`
- **Component Examples**: `docs/DESIGN_SYSTEM.md#component-styling`

---

## ✅ IMPLEMENTATION CHECKLIST

- [ ] Install Inter & Space Grotesk fonts
- [ ] Configure Tailwind with custom colors
- [ ] Add CSS custom properties
- [ ] Install shadcn/ui components
- [ ] Create utility classes for effects
- [ ] Test color contrast (WCAG AA)
- [ ] Implement responsive breakpoints
- [ ] Add smooth transitions

---

**Print this page** and keep it next to your desk while coding! 🚀
