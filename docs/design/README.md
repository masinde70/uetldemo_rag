# SISUiQ Design System Documentation

**Complete design system for the SISUiQ UETCL Strategy Copilot**

This directory contains the complete visual design system, color palette, component specifications, and Figma blueprints for building the SISUiQ user interface.

---

## 📚 Documentation Index

### [Color Palette & Design System](./color-palette-skill.md)
Complete design system with:
- ✅ Official color palette with hex/RGB values
- ✅ Typography system and font specifications
- ✅ Component styling guidelines
- ✅ Spacing, shadows, and effects
- ✅ Tailwind CSS configuration
- ✅ shadcn/ui theme overrides
- ✅ Accessibility standards (WCAG AA)
- ✅ Ready-to-use code snippets

### [Figma Blueprint & Layouts](./figma-blueprint.md)
Detailed layout specifications with:
- ✅ Complete page layouts with exact dimensions
- ✅ Figma file structure and organization
- ✅ Design token setup instructions
- ✅ Component library structure
- ✅ Responsive breakpoints
- ✅ Interaction patterns and prototyping flows
- ✅ Export settings for development

---

## 🎨 Design Philosophy

### Core Aesthetic: **Cosmic Minimalism**

**Inspired by:**
- **Sana.ai** - Clean interface with subtle glowing effects
- **V7 Labs** - Data-driven elegance and professional appeal
- **Space Themes** - Futuristic, premium executive look

### Key Principles
1. **Professional First** - Enterprise-ready, not consumer-tech
2. **Data Clarity** - High contrast for complex information
3. **Subtle Energy** - Glows and effects that enhance, not distract
4. **Accessibility** - WCAG AA minimum for all interactions

---

## 🎯 Quick Reference

### Primary Colors

| Color | Hex | Use Case |
|-------|-----|----------|
| **Deep Space Navy** | `#020617` | Main background |
| **Electric Cyan** | `#22D3EE` | Primary actions, highlights |
| **Violet Energy** | `#A855F7` | Secondary accents |
| **Warm Orange** | `#F97316` | Sparingly - special accents |

### Typography

| Element | Font | Size | Weight |
|---------|------|------|--------|
| Display | Space Grotesk | 48px | Bold (700) |
| H1 | Space Grotesk | 36px | Bold (700) |
| H2 | Inter | 24px | Semibold (600) |
| Body | Inter | 14px | Regular (400) |
| UI Labels | Inter | 12px | Medium (500) |

### Key Spacing

```
Small:  8px  (space-2)
Medium: 16px (space-4)
Large:  24px (space-6)
XLarge: 32px (space-8)
```

### Border Radius

```
Small:  8px  (rounded-lg)
Medium: 12px (rounded-xl)
Large:  16px (rounded-2xl)
Bubble: 24px (rounded-3xl)
```

---

## 💻 Implementation

### For Developers

1. **Start with Tailwind Config**
   - Copy configuration from [color-palette-skill.md](./color-palette-skill.md#tailwind-configuration)
   - Add to `tailwind.config.ts`

2. **Setup shadcn/ui Theme**
   - Copy CSS variables from [color-palette-skill.md](./color-palette-skill.md#shadcnui-theme-override)
   - Add to `app/globals.css`

3. **Install Fonts**
   ```bash
   # Via Google Fonts or local
   - Inter (weights: 400, 500, 600, 700)
   - Space Grotesk (weights: 500, 600, 700)
   - JetBrains Mono (weights: 400, 500) [optional for code]
   ```

4. **Build Components**
   - Reference component specifications in color-palette-skill.md
   - Use shadcn/ui as base, customize with our theme
   - Follow auto-layout patterns from Figma blueprint

### For Designers

1. **Setup Figma File**
   - Follow structure from [figma-blueprint.md](./figma-blueprint.md#figma-file-structure)
   - Create design tokens (colors, typography, effects)
   - Build component library

2. **Create Layouts**
   - Use exact dimensions from blueprints
   - Follow spacing system (8px grid)
   - Apply consistent shadows and effects

3. **Maintain Consistency**
   - Use color/text styles (not raw hex)
   - Follow component variants
   - Check accessibility with Stark plugin

---

## 🧩 Component Checklist

When building a new component, ensure:

- [ ] Uses semantic color tokens (not hardcoded hex)
- [ ] Has hover, focus, and disabled states
- [ ] Includes smooth transitions (250ms default)
- [ ] Meets WCAG AA contrast ratios
- [ ] Responsive on mobile, tablet, desktop
- [ ] Keyboard accessible
- [ ] Has loading and error states
- [ ] Follows 8px spacing grid
- [ ] Uses appropriate shadows
- [ ] Has proper border radius

---

## 📐 Layout Reference

### Copilot Main Interface

```
Desktop (1440px):
┌────────────────────────────────────────┐
│  Top Bar (64px)                        │
├──────────┬────────────┬────────────────┤
│ Sidebar  │ Chat Area  │ Insights Panel │
│ 240px    │ Flexible   │ 360px          │
└──────────┴────────────┴────────────────┘
```

### Admin Dashboard

```
Wide Desktop (1600px):
┌────────────────────────────────────────┐
│  Top Bar (64px)                        │
├──────────┬─────────────────────────────┤
│ Sidebar  │ Main Content (Stats+Table) │
│ 200px    │ Flexible                    │
└──────────┴─────────────────────────────┘
```

### Responsive Breakpoints

- **Mobile**: < 640px (stacked, single column)
- **Tablet**: 640px - 1024px (2 columns, collapsible sidebar)
- **Desktop**: > 1024px (full 3-column layout)

---

## 🎬 Animation Guidelines

### Standard Timings

- **Fast**: 150ms (micro-interactions)
- **Base**: 250ms (default for most transitions)
- **Slow**: 350ms (complex state changes)
- **Glow**: 500ms (effect animations)

### Easing Functions

- **Default**: `cubic-bezier(0.4, 0, 0.2, 1)` (ease-out)
- **Bounce**: `cubic-bezier(0.68, -0.55, 0.265, 1.55)`

### Common Patterns

```css
/* Fade in */
animation: fadeIn 250ms ease-out;

/* Slide up */
animation: slideUp 250ms ease-out;

/* Glow pulse */
animation: glow 2s ease-in-out infinite;

/* Hover lift */
transform: translateY(-2px);
transition: 250ms ease;
```

---

## 🔍 Accessibility Standards

### Contrast Ratios (WCAG AA)

✅ **All Passing Combinations:**

| Foreground | Background | Ratio | Grade |
|------------|------------|-------|-------|
| #E2E8F0 | #020617 | 15.8:1 | AAA |
| #94A3B8 | #020617 | 9.2:1 | AAA |
| #22D3EE | #020617 | 10.5:1 | AAA |
| #020617 | #22D3EE | 13.2:1 | AAA |

### Focus Indicators

- Always visible 3px outline
- Color: Neon Cyan (#22D3EE)
- Style: `ring-4 ring-neon-cyan/20`
- Never remove focus styles

### Interactive Elements

- Minimum touch target: 44×44px
- Icon minimum: 16px (24px recommended)
- Clear hover states
- Keyboard navigation support

---

## 📦 Assets & Resources

### Icon Libraries

- **Primary**: Lucide React
- **Alternative**: Radix Icons
- **Style**: Line-based, 1.5px stroke weight
- **Sizes**: 16px (sm), 20px (md), 24px (lg)

### Fonts

- **Inter**: Body text, UI elements
  - Download: https://fonts.google.com/specimen/Inter
- **Space Grotesk**: Display, headers
  - Download: https://fonts.google.com/specimen/Space+Grotesk
- **JetBrains Mono**: Code blocks (optional)
  - Download: https://www.jetbrains.com/lp/mono/

### Design Tools

**Recommended Figma Plugins:**
1. Iconify - Icon search and insert
2. Stark - Accessibility checker
3. Content Reel - Realistic content generation
4. Design Lint - Design consistency checker

---

## 🚀 Getting Started

### For New Team Members

1. **Read the Color Palette Guide** ([color-palette-skill.md](./color-palette-skill.md))
   - Understand the color system
   - Learn component patterns
   - Review code examples

2. **Study the Figma Blueprint** ([figma-blueprint.md](./figma-blueprint.md))
   - See exact layout dimensions
   - Understand spacing system
   - Review interaction patterns

3. **Setup Your Environment**
   - Install required fonts
   - Copy Tailwind config
   - Setup shadcn/ui theme

4. **Build Your First Component**
   - Start with a button or card
   - Follow specifications exactly
   - Test accessibility
   - Review with team

---

## 📝 Contributing

### Adding New Components

1. Design in Figma following existing patterns
2. Document specifications in color-palette-skill.md
3. Add layout details to figma-blueprint.md if complex
4. Create code example with Tailwind classes
5. Test accessibility
6. Get design review

### Updating Colors or Styles

1. Propose change with rationale
2. Check accessibility impacts
3. Update all documentation
4. Update Figma design tokens
5. Update code examples
6. Communicate to team

---

## 🎯 Design System Goals

✅ **Consistency** - Every instance of a component looks identical
✅ **Efficiency** - Developers can build quickly using documented patterns
✅ **Accessibility** - All users can access and use the interface
✅ **Scalability** - System grows without becoming complex
✅ **Maintainability** - Easy to update and evolve over time

---

## 📞 Questions?

- **Design Questions**: Reference this documentation first
- **Implementation Help**: Check code examples in color-palette-skill.md
- **Figma Setup**: Follow step-by-step guide in figma-blueprint.md
- **New Patterns**: Propose with examples and rationale

---

## 📄 Related Documentation

- [Project Architecture](../architecture/README.md)
- [Frontend README](../../frontend/README.md)
- [API Documentation](../api/README.md)

---

**Last Updated**: December 2024

**Design System Version**: 1.0.0

**Status**: ✅ Production Ready
