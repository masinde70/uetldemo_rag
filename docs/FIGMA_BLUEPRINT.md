# SISUiQ Figma Design Blueprint
## Complete UI/UX Specifications for Implementation

> **Design Philosophy**: Cosmic Minimalism with Executive Polish – Inspired by Sana AI's glowing minimalism and V7's clean data visualization aesthetics.

---

## 🎨 FIGMA SETUP

### 1. Artboard Specifications

| Screen | Dimensions | Purpose |
|--------|-----------|---------|
| Desktop | 1920×1080 | Primary interface |
| Laptop | 1440×900 | Laptop optimization |
| Tablet | 1024×768 | Admin dashboard (iPad) |
| Mobile | 375×812 | Future mobile view |

### 2. Frame Structure

```
SISUiQ Design System
├── 🎨 Colors & Styles
│   ├── Color Palette
│   ├── Gradients
│   └── Effects (Glows, Shadows)
├── 📝 Typography
│   ├── Font Scales
│   └── Text Styles
├── 🧩 Components
│   ├── Buttons
│   ├── Cards
│   ├── Inputs
│   ├── Chat Bubbles
│   ├── Tables
│   └── Panels
├── 📐 Layouts
│   ├── Chat Interface (1920×1080)
│   ├── Admin Dashboard (1920×1080)
│   ├── Document Ingestion (1920×1080)
│   └── Analytics View (1920×1080)
└── 🎭 Prototypes
    └── Interactive Flows
```

---

## 🎨 COLOR STYLES (Figma Setup)

### Create These Color Styles:

```
Background/Deep Space         #020617
Background/Surface Primary    #0F172A
Background/Surface Secondary  #1E293B
Background/Surface Elevated   #334155

Neon/Cyan                    #22D3EE
Neon/Violet                  #A855F7
Accent/Orange                #F97316
Success/Green                #10B981
Warning/Amber                #F59E0B
Error/Red                    #EF4444

Text/Primary                 #E2E8F0
Text/Secondary               #94A3B8
Text/Tertiary                #64748B
Text/Inverse                 #020617

Border/Subtle                #1E293B
Border/Medium                #334155
Border/Strong                #475569
```

### Gradient Styles:

```
Gradient/Primary
  Type: Linear
  Angle: 135°
  Stops: #0EA5E9 (0%) → #0284C7 (100%)

Gradient/Accent
  Type: Linear
  Angle: 135°
  Stops: #A855F7 (0%) → #7C3AED (100%)

Gradient/Surface
  Type: Linear
  Angle: 180°
  Stops: #0F172A (0%) → #1E293B (100%)
```

### Effect Styles:

```
Effect/Neon Glow Cyan
  Type: Drop Shadow
  Blur: 20px
  Color: rgba(34, 211, 238, 0.35)
  X: 0, Y: 0

Effect/Neon Glow Violet
  Type: Drop Shadow
  Blur: 20px
  Color: rgba(168, 85, 247, 0.35)
  X: 0, Y: 0

Effect/Cosmic Shadow
  Type: Drop Shadow
  Blur: 20px
  Color: rgba(0, 0, 0, 0.3)
  X: 0, Y: 4

Effect/Glass Blur
  Type: Background Blur
  Blur: 12px
```

---

## 📝 TEXT STYLES (Figma Setup)

### Font Import:
1. Go to Text → Font → Import
2. Add **Inter** (Google Fonts)
3. Add **Space Grotesk** (Google Fonts)

### Text Style Definitions:

```
Display/1
  Font: Space Grotesk
  Size: 36px
  Weight: Bold (700)
  Line Height: 120%
  Letter Spacing: -0.72px

Display/2
  Font: Space Grotesk
  Size: 30px
  Weight: Bold (700)
  Line Height: 130%
  Letter Spacing: -0.3px

Heading/1
  Font: Inter
  Size: 24px
  Weight: Semibold (600)
  Line Height: 140%

Heading/2
  Font: Inter
  Size: 20px
  Weight: Semibold (600)
  Line Height: 140%

Body/Large
  Font: Inter
  Size: 18px
  Weight: Regular (400)
  Line Height: 160%

Body/Regular
  Font: Inter
  Size: 16px
  Weight: Regular (400)
  Line Height: 160%

Body/Small
  Font: Inter
  Size: 14px
  Weight: Regular (400)
  Line Height: 150%

Caption
  Font: Inter
  Size: 12px
  Weight: Medium (500)
  Line Height: 140%
  Letter Spacing: 0.24px

Label/Uppercase
  Font: Inter
  Size: 12px
  Weight: Semibold (600)
  Line Height: 120%
  Letter Spacing: 0.6px
  Transform: Uppercase
```

---

## 🧩 COMPONENT LIBRARY

### 1. BUTTON COMPONENTS

#### Primary Button
```
Frame: Auto Layout
Padding: 12px 24px
Corner Radius: 12px
Fill: Neon/Cyan (#22D3EE)
Text: Body/Small, Text/Inverse
Effects: None

Hover State:
  Fill: #0DCAF0
  Effects: Neon Glow Cyan

Pressed State:
  Fill: #0BA5D6
```

#### Secondary Button
```
Frame: Auto Layout
Padding: 12px 24px
Corner Radius: 12px
Fill: Background/Surface Elevated (#334155)
Stroke: 1px Border/Medium
Text: Body/Small, Text/Primary
Effects: None

Hover State:
  Fill: #475569
```

#### Ghost Button
```
Frame: Auto Layout
Padding: 12px 24px
Corner Radius: 12px
Fill: None
Text: Body/Small, Text/Secondary
Effects: None

Hover State:
  Fill: rgba(15, 23, 42, 0.5)
```

### 2. CHAT BUBBLE COMPONENTS

#### User Message Bubble
```
Frame: Auto Layout
Max Width: 70% of container
Padding: 16px
Corner Radius: 16px
Fill: Gradient/Primary
Text: Body/Small, Text/Inverse
Align: Right
Effects: Cosmic Shadow
```

#### Assistant Message Bubble
```
Frame: Auto Layout
Max Width: 70% of container
Padding: 16px
Corner Radius: 16px
Fill: Background/Surface Secondary
Stroke: 1px Border/Subtle
Text: Body/Small, Text/Primary
Align: Left
Effects: Cosmic Shadow
```

### 3. CARD COMPONENT

```
Frame: Auto Layout (Vertical)
Padding: 24px
Gap: 16px
Corner Radius: 16px
Fill: rgba(15, 23, 42, 0.4)
Stroke: 1px rgba(30, 41, 59, 0.5)
Effects: Glass Blur, Cosmic Shadow

Hover State:
  Stroke: 1px Neon/Cyan at 50% opacity
  Effects: Glass Blur, Neon Glow Cyan
```

### 4. INPUT FIELD

```
Frame: Auto Layout
Width: Fill container
Padding: 12px 16px
Corner Radius: 12px
Fill: rgba(2, 6, 23, 0.6)
Stroke: 1px Border/Medium
Text: Body/Regular, Text/Primary
Placeholder Text: Text/Tertiary
Effects: Glass Blur (subtle)

Focus State:
  Stroke: 2px Neon/Cyan
  Effects: Neon Glow Cyan (subtle)
```

### 5. TABLE ROW

#### Header Row
```
Frame: Auto Layout
Padding: 12px 16px
Fill: None
Stroke Bottom: 1px Border/Strong
Text: Label/Uppercase, Neon/Cyan
Gap: 16px
```

#### Data Row
```
Frame: Auto Layout
Padding: 12px 16px
Fill: None
Stroke Bottom: 1px Border/Subtle
Text: Body/Small, Text/Secondary
Gap: 16px

Hover State:
  Fill: rgba(30, 41, 59, 0.5)
```

---

## 📐 LAYOUT #1: CHAT INTERFACE

### Overall Structure
```
Canvas: 1920×1080
Background: Deep Space (#020617) with diagonal grid overlay
Layout: 3-column grid
```

### Layout Breakdown:

```
┌─────────────────────────────────────────────────────────────┐
│  HEADER (1920 × 64px)                                       │
│  Logo | Mode Selector | Search | User Avatar               │
└─────────────────────────────────────────────────────────────┘
┌───────────┬──────────────────────────────┬──────────────────┐
│           │                              │                  │
│  LEFT     │   MAIN CHAT AREA             │  RIGHT INSIGHTS  │
│  SIDEBAR  │                              │  PANEL           │
│  256px    │   1280px                     │  384px           │
│           │                              │                  │
│  • Logo   │  ┌────────────────────────┐  │  • Citations    │
│  • Modes  │  │                        │  │  • Analytics    │
│    ○ Q&A  │  │  Chat Messages         │  │  • Suggestions  │
│    ○ Plan │  │  (Scrollable)          │  │  • Metadata     │
│    ○ Data │  │                        │  │                  │
│    ○ Reg  │  │                        │  │                  │
│           │  └────────────────────────┘  │                  │
│  • History│                              │                  │
│  • Admin  │  ┌────────────────────────┐  │                  │
│           │  │ Message Input          │  │                  │
│           │  │ [Type message...]  [>] │  │                  │
│           │  └────────────────────────┘  │                  │
│   1016px  │          952px               │     1016px       │
└───────────┴──────────────────────────────┴──────────────────┘
```

### Detailed Specifications:

#### Left Sidebar (256px)
```
Component: Frame (Auto Layout Vertical)
Width: 256px
Height: Fill (1016px)
Fill: rgba(15, 23, 42, 0.4)
Stroke Right: 1px Border/Subtle
Effects: Glass Blur
Padding: 24px
Gap: 24px

Elements:
1. Logo (60px height)
2. Mode Selector (Card component)
3. Recent Sessions List
4. Admin Link (bottom)
```

#### Main Chat Area (1280px)
```
Component: Frame (Auto Layout Vertical)
Width: 1280px
Height: Fill
Fill: None
Padding: 24px
Gap: 16px

Sub-components:
1. Messages Container
   - Scrollable
   - Gap: 16px between messages
   - Padding: 24px

2. Input Bar (Fixed bottom)
   - Height: 120px
   - Fill: rgba(15, 23, 42, 0.4)
   - Stroke Top: 1px Border/Subtle
   - Effects: Glass Blur
```

#### Right Insights Panel (384px)
```
Component: Frame (Auto Layout Vertical)
Width: 384px
Height: Fill (1016px)
Fill: rgba(15, 23, 42, 0.4)
Stroke Left: 1px Border/Subtle
Effects: Glass Blur
Padding: 24px
Gap: 20px

Cards (stacked):
1. Retrieved Sources
2. Analytics Snapshot
3. Regulatory Alignment
4. Suggested Actions
```

---

## 📐 LAYOUT #2: ADMIN DASHBOARD

### Overall Structure
```
Canvas: 1920×1080
Background: Deep Space with subtle grid
Layout: Sidebar + Main Grid
```

### Layout Breakdown:

```
┌─────────────────────────────────────────────────────────────┐
│  HEADER (1920 × 80px)                                       │
│  Admin Dashboard | Stats Summary | Date Range | User        │
└─────────────────────────────────────────────────────────────┘
┌───────────┬─────────────────────────────────────────────────┐
│  SIDEBAR  │  MAIN CONTENT AREA (1640px)                     │
│  256px    │                                                  │
│           │  ┌──────────────────────────────────────────┐   │
│  • Dashboard │  STATS CARDS (4-column grid)              │   │
│  • Sessions  │  ├─────┬─────┬─────┬─────┐              │   │
│  • Users     │  │Total│Active│Docs│Tokens│             │   │
│  • Documents │  │Sess │Users │    │Used  │             │   │
│  • Analytics │  └─────┴─────┴─────┴─────┘              │   │
│  • Settings  │                                           │   │
│           │  ┌──────────────────────────────────────────┐   │
│           │  │  DATA TABLES (2-column grid)             │   │
│           │  │  ┌─────────────┬────────────────┐        │   │
│           │  │  │ Sessions    │ Documents      │        │   │
│           │  │  │ Table       │ Table          │        │   │
│           │  │  └─────────────┴────────────────┘        │   │
│           │  └──────────────────────────────────────────┘   │
└───────────┴─────────────────────────────────────────────────┘
```

### Stat Cards (4 cards, 350px each)
```
Component: Card
Width: 350px
Height: 140px
Padding: 24px
Layout: Auto Layout Vertical
Gap: 8px

Elements:
- Label (Caption, Text/Secondary)
- Value (Display/1, Text/Primary)
- Trend Indicator (+12% ↑, Success/Green)
```

### Data Tables
```
Component: Frame
Width: 790px each (2 tables side-by-side)
Height: Auto
Fill: Card background
Padding: 20px

Header: Sticky
Rows: 10 visible, scrollable
Row Height: 48px
```

---

## 📐 LAYOUT #3: DOCUMENT INGESTION

### Layout Breakdown:

```
┌─────────────────────────────────────────────────────────────┐
│  Centered Modal (800 × 600px)                               │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Upload Documents                                     │  │
│  │                                                        │  │
│  │  ┌────────────────────────────────────────────────┐  │  │
│  │  │  📄                                             │  │  │
│  │  │                                                 │  │  │
│  │  │  Drag & drop files here                        │  │  │
│  │  │  or click to browse                            │  │  │
│  │  │                                                 │  │  │
│  │  │  Supported: PDF, DOCX, TXT                     │  │  │
│  │  └────────────────────────────────────────────────┘  │  │
│  │                                                        │  │
│  │  Files to Upload (2):                                 │  │
│  │  • strategy_plan.pdf (2.4 MB) [Remove]               │  │
│  │  • regulatory_guide.pdf (1.8 MB) [Remove]            │  │
│  │                                                        │  │
│  │  [Cancel]                        [Upload Documents]   │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Upload Area (Drag & Drop)
```
Component: Frame
Width: 760px
Height: 280px
Fill: rgba(30, 41, 59, 0.3)
Stroke: 2px dashed Border/Medium
Corner Radius: 16px
Padding: 40px
Align: Center (vertical & horizontal)

Hover State (with file):
  Stroke: 2px dashed Neon/Cyan
  Effects: Neon Glow Cyan

Active State (drop):
  Fill: rgba(34, 211, 238, 0.1)
```

### Progress Bar (During Upload)
```
Component: Frame (Auto Layout)
Width: 760px
Height: 8px
Fill: Background/Surface Secondary
Corner Radius: 4px

Progress Fill:
  Fill: Gradient/Primary
  Effects: Neon Glow Cyan
  Animation: 0% → 100% width
```

---

## 🎭 INTERACTIVE PROTOTYPING

### Key Interactions to Prototype:

1. **Mode Switching**
   - Trigger: Click mode button
   - Action: Fade out → Change content → Fade in
   - Duration: 300ms

2. **Message Send**
   - Trigger: Click send button
   - Action: Add message → Scroll → Show typing indicator → Add response
   - Duration: 200ms per step

3. **Card Hover Effects**
   - Trigger: Mouse enter
   - Action: Border color change + Glow appear
   - Duration: 200ms ease-out

4. **Table Row Expand**
   - Trigger: Click row
   - Action: Slide panel from right
   - Duration: 300ms ease-in-out

5. **File Upload**
   - Trigger: File drop
   - Action: Progress bar animate
   - Duration: Based on file size (simulated)

---

## 📱 RESPONSIVE BREAKPOINTS

### Tablet (1024px)
- Collapse right panel to drawer
- Reduce sidebar to icons only
- Stack stat cards 2×2

### Mobile (375px)
- Full-screen chat
- Bottom navigation
- Swipe for panels
- Stack all elements vertically

---

## 🎨 DESIGN TOKENS EXPORT

### For Developers:
1. Select all color styles → Export as CSS variables
2. Select all text styles → Export as Tailwind config
3. Export components as React/shadcn templates
4. Export spacing as Tailwind spacing scale

---

## ✅ FIGMA DELIVERABLES CHECKLIST

- [ ] Color palette (all 20+ colors defined)
- [ ] Gradient styles (3 gradients)
- [ ] Effect styles (4 effects: glows + blur)
- [ ] Text styles (10 styles)
- [ ] Button components (3 variants × 3 states)
- [ ] Chat bubble components (2 types)
- [ ] Card component (with hover)
- [ ] Input component (with focus)
- [ ] Table components (header + row)
- [ ] Chat interface layout (1920×1080)
- [ ] Admin dashboard layout (1920×1080)
- [ ] Document upload modal
- [ ] Interactive prototype flows
- [ ] Responsive variants (tablet, mobile)
- [ ] Design tokens export

---

## 🚀 HANDOFF TO DEVELOPERS

### Export Settings:
- Format: SVG for icons
- Format: PNG 2x for raster assets
- Code: CSS for styles
- Code: React for components

### Documentation to Include:
1. Component specs (this document)
2. Color system
3. Typography scale
4. Spacing guidelines
5. Animation timings
6. Accessibility notes

---

**Ready for Figma!** This blueprint provides pixel-perfect specifications for creating the complete SISUiQ design in Figma, ready for developer handoff.
