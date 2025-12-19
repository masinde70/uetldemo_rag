# SISUiQ Figma Blueprint & Layout Specifications

**Complete Figma Design System Setup for SISUiQ UETCL Strategy Copilot**

*Ready-to-implement layouts with exact dimensions, spacing, and component architecture*

---

## 🎨 Figma File Structure

### Recommended Page Organization

```
📄 SISUiQ Design System (File)
├── 📄 Cover (Page)
├── 🎨 Design Tokens (Page)
│   ├── Colors
│   ├── Typography
│   ├── Spacing
│   ├── Shadows & Effects
│   └── Icons
├── 🧩 Components (Page)
│   ├── Buttons
│   ├── Inputs
│   ├── Cards
│   ├── Chat Bubbles
│   ├── Tables
│   └── Navigation
├── 📱 Layouts (Page)
│   ├── Copilot Home (Main Interface)
│   ├── Admin Dashboard
│   ├── Document Ingestion
│   └── Settings
└── 📐 Wireframes (Page)
    ├── User Flows
    └── Responsive Breakpoints
```

---

## 🎨 Setting Up Design Tokens in Figma

### Color Styles to Create

**Create these in Figma > Styles > Color:**

#### Backgrounds
1. **Background/Primary** - `#020617`
2. **Background/Surface 1** - `#0F172A`
3. **Background/Surface 2** - `#1E293B`
4. **Background/Surface 3** - `#334155`

#### Neon Accents
5. **Neon/Cyan** - `#22D3EE`
6. **Neon/Violet** - `#A855F7`
7. **Neon/Orange** - `#F97316`
8. **Neon/Green** - `#10B981`
9. **Neon/Yellow** - `#F59E0B`
10. **Neon/Red** - `#EF4444`

#### Text
11. **Text/Primary** - `#E2E8F0`
12. **Text/Secondary** - `#94A3B8`
13. **Text/Tertiary** - `#64748B`
14. **Text/Inverse** - `#020617`

#### Borders
15. **Border/Subtle** - `#1E293B`
16. **Border/Default** - `#334155`
17. **Border/Emphasis** - `#475569`
18. **Border/Neon** - `#22D3EE` at 20% opacity

### Text Styles to Create

**Create these in Figma > Styles > Text:**

#### Display & Headings
1. **Display/Bold** - Space Grotesk, 48px, Bold (700), -2% tracking
2. **H1/Bold** - Space Grotesk, 36px, Bold (700), -2% tracking
3. **H2/Semibold** - Inter, 24px, Semibold (600), 0% tracking
4. **H3/Semibold** - Inter, 20px, Semibold (600), 0% tracking
5. **H4/Medium** - Inter, 18px, Medium (500), 0% tracking

#### Body Text
6. **Body/Large** - Inter, 16px, Regular (400), 0% tracking
7. **Body/Default** - Inter, 14px, Regular (400), 0% tracking
8. **Body/Small** - Inter, 13px, Regular (400), 0% tracking

#### UI Text
9. **UI/Button** - Inter, 14px, Medium (500), 0% tracking
10. **UI/Label** - Inter, 12px, Medium (500), 5% tracking
11. **UI/Caption** - Inter, 11px, Regular (400), 0% tracking

### Effect Styles to Create

**Create these in Figma > Styles > Effect:**

#### Shadows
1. **Shadow/Small** - Drop Shadow, Y: 1px, Blur: 2px, `#000000` at 30%
2. **Shadow/Medium** - Drop Shadow, Y: 4px, Blur: 6px, `#000000` at 30%
3. **Shadow/Large** - Drop Shadow, Y: 10px, Blur: 15px, `#000000` at 40%
4. **Shadow/Extra Large** - Drop Shadow, Y: 20px, Blur: 25px, `#000000` at 50%

#### Glows
5. **Glow/Cyan** - Drop Shadow, Y: 0, Blur: 20px, `#22D3EE` at 35%
6. **Glow/Violet** - Drop Shadow, Y: 0, Blur: 20px, `#A855F7` at 35%

#### Blur
7. **Blur/Glass** - Layer Blur, 10px

---

## 📐 Page 1: Copilot Home (Main Interface)

### Overall Layout Dimensions

```
Canvas: 1440px × 900px (Desktop)

┌─────────────────────────────────────────────────────────────────┐
│  Top Bar (Height: 64px)                                         │
├─────────────┬───────────────────────────────┬───────────────────┤
│             │                               │                   │
│  Sidebar    │    Main Chat Area            │  Insights Panel   │
│  240px      │    flex (840px)              │  360px            │
│             │                               │                   │
│  Fixed      │    Scrollable                │  Scrollable       │
│             │                               │                   │
└─────────────┴───────────────────────────────┴───────────────────┘
```

### Top Bar

```
Height: 64px
Background: #0F172A (Background/Surface 1)
Border-bottom: 1px solid #334155
Padding: 0 24px

┌─────────────────────────────────────────────────────────────────┐
│  [Logo Icon]  SISUiQ                                    [Avatar]│
│  24px        H4 (18px)                          Search   User   │
└─────────────────────────────────────────────────────────────────┘

Elements:
- Logo Icon: 32px × 32px, Glow/Cyan effect
- App Name: H4/Medium, Text/Primary
- Search Icon: 20px, Text/Secondary
- User Avatar: 40px × 40px circle, border 2px Neon/Cyan
```

### Left Sidebar

```
Width: 240px (fixed)
Background: #0F172A (Background/Surface 1)
Padding: 24px 16px
Gap between items: 8px

┌──────────────────────────┐
│                          │
│  [Icon] Strategy Q&A     │  ← Navigation Item
│  [Icon] Action Planner   │
│  [Icon] Analytics        │
│  [Icon] Regulatory       │
│                          │
│  ─────────────────────   │  ← Divider
│                          │
│  [Icon] Admin            │
│  [Icon] Settings         │
│                          │
│  [Mode Selector Card]    │  ← Current Mode Display
│                          │
└──────────────────────────┘

Navigation Item (Default):
- Height: 40px
- Padding: 8px 12px
- Border-radius: 8px
- Background: Transparent
- Text: Body/Default, Text/Secondary
- Icon: 20px, Text/Secondary
- Gap: 12px

Navigation Item (Active):
- Background: rgba(34, 211, 238, 0.1)
- Text: Body/Default, Neon/Cyan
- Icon: 20px, Neon/Cyan
- Border-left: 2px solid Neon/Cyan
- Glow: Subtle cyan glow

Navigation Item (Hover):
- Background: rgba(255, 255, 255, 0.05)

Mode Selector Card:
- Width: 208px (full width - padding)
- Padding: 16px
- Border-radius: 12px
- Background: Background/Surface 2
- Border: 1px solid Border/Default
- Margin-top: auto (bottom of sidebar)
```

### Main Chat Area

```
Width: Flexible (840px in 1440px layout)
Background: #020617 (Background/Primary) with subtle grid
Padding: 24px

┌─────────────────────────────────────────────┐
│                                             │
│  ┌────────────────────────────────────────┐│
│  │  Header: "Strategy Q&A Mode"          ││
│  │  Subtitle: "Ask about UETCL strategy" ││
│  └────────────────────────────────────────┘│
│                                             │
│  ┌─ Chat Messages Container (Scrollable) ─┐│
│  │                                         ││
│  │  [User Bubble]           →              ││
│  │                                         ││
│  │  ← [Assistant Bubble]                  ││
│  │    [Citations]                         ││
│  │                                         ││
│  │  [User Bubble]           →              ││
│  │                                         ││
│  │  ← [Assistant Bubble]                  ││
│  │                                         ││
│  └─────────────────────────────────────────┘│
│                                             │
│  ┌────────── Input Area ──────────────────┐│
│  │  [Text Input Field - Pill Shape]       ││
│  │  [Send Button]                         ││
│  └────────────────────────────────────────┘│
│                                             │
└─────────────────────────────────────────────┘

Chat Messages Container:
- Max-width: 800px
- Margin: 0 auto (centered)
- Gap between messages: 16px
- Padding-bottom: 24px

User Bubble:
- Max-width: 75% (600px max)
- Align: Right (ml-auto)
- Padding: 12px 16px
- Border-radius: 24px
- Background: Linear gradient #0EA5E9 → #0284C7
- Text: Body/Default, White
- Margin-bottom: 16px

Assistant Bubble:
- Max-width: 85% (680px max)
- Align: Left
- Padding: 12px 16px
- Border-radius: 24px
- Background: Background/Surface 2
- Border: 1px solid Border/Default
- Text: Body/Default, Text/Primary
- Shadow: Shadow/Medium
- Margin-bottom: 4px (if citations follow)

Citations Component:
- Max-width: 85% (same as bubble)
- Padding: 8px 12px
- Border-radius: 8px
- Background: rgba(34, 211, 238, 0.05)
- Border-left: 2px solid Neon/Cyan
- Gap: 4px
- Text: UI/Caption, Text/Tertiary

Input Area:
- Position: Fixed at bottom of chat area
- Width: 100% - 48px padding
- Max-width: 800px
- Margin: 0 auto
- Height: 56px
- Border-radius: 28px (pill)
- Background: Background/Surface 2
- Border: 1px solid Border/Default
- Padding: 8px 8px 8px 20px
- Display: Flex, align-center

Input Field:
- Flex-grow: 1
- Background: Transparent
- Border: None
- Text: Body/Default, Text/Primary
- Placeholder: Text/Tertiary

Send Button:
- Width: 40px
- Height: 40px
- Border-radius: 20px (circle)
- Background: Neon/Cyan
- Icon: 20px, Text/Inverse
- Hover: Shadow/Glow Cyan
```

### Right Insights Panel

```
Width: 360px (fixed)
Background: #0F172A (Background/Surface 1)
Border-left: 1px solid Border/Default
Padding: 24px 16px
Gap: 16px

┌──────────────────────────┐
│  INSIGHTS                │  ← Section Header
│                          │
│  ┌────────────────────┐  │
│  │  Sources Card      │  │  ← Card
│  │                    │  │
│  │  • Doc 1           │  │
│  │  • Doc 2           │  │
│  └────────────────────┘  │
│                          │
│  ┌────────────────────┐  │
│  │  Analytics Card    │  │
│  │                    │  │
│  │  [Chart/Graph]     │  │
│  └────────────────────┘  │
│                          │
│  ┌────────────────────┐  │
│  │  Actions Card      │  │
│  │                    │  │
│  │  • Action 1        │  │
│  │  • Action 2        │  │
│  └────────────────────┘  │
│                          │
└──────────────────────────┘

Section Header:
- Text: UI/Label (12px), Text/Tertiary
- Letter-spacing: 5%
- Uppercase
- Margin-bottom: 12px

Insight Card:
- Width: 328px (full width - padding)
- Padding: 16px
- Border-radius: 12px
- Background: Background/Surface 2
- Border: 1px solid Border/Default
- Shadow: Shadow/Small
- Gap: 12px

Card Title:
- Text: H4/Medium (18px), Text/Primary
- Margin-bottom: 8px

Card Content:
- Text: Body/Small, Text/Secondary
- Line-height: 1.6

List Item:
- Padding: 8px 0
- Border-bottom: 1px solid Border/Subtle (except last)
- Text: Body/Default, Text/Primary

Hover State (Card):
- Border: Border/Neon
- Shadow: Shadow/Glow Cyan
- Transform: translateY(-2px)
- Transition: 250ms
```

---

## 📐 Page 2: Admin Dashboard

### Layout Dimensions

```
Canvas: 1600px × 900px (Wide Desktop)

┌─────────────────────────────────────────────────────────────────┐
│  Top Bar (Height: 64px)                                         │
├─────────────┬───────────────────────────────────────────────────┤
│             │                                                    │
│  Sidebar    │    Main Content Area                             │
│  200px      │    1376px (flexible)                             │
│             │                                                    │
│  Fixed      │    ┌──────────────────────────────────────┐       │
│             │    │  Stats Cards Row                     │       │
│  • Sessions │    └──────────────────────────────────────┘       │
│  • Docs     │                                                    │
│  • Analytics│    ┌──────────────────────────────────────┐       │
│  • Users    │    │  Data Table                          │       │
│  • Usage    │    │                                      │       │
│             │    └──────────────────────────────────────┘       │
│             │                                                    │
└─────────────┴────────────────────────────────────────────────────┘
```

### Top Bar (Same as Copilot)

Height: 64px, same design as main interface

### Admin Sidebar

```
Width: 200px
Background: #0F172A
Padding: 24px 16px
Gap: 8px

Navigation items same style as main sidebar,
but more compact.
```

### Main Content Area

```
Padding: 32px
Max-width: 1400px
Background: #020617

Stats Cards Row:
- Display: Grid, 4 columns
- Gap: 20px
- Margin-bottom: 32px

Stat Card:
- Width: ~320px (flex)
- Height: 120px
- Padding: 20px
- Border-radius: 12px
- Background: Background/Surface 2
- Border: 1px solid Border/Default

Card Layout:
┌────────────────────────┐
│  [Icon]  Label         │  ← 12px, Text/Tertiary
│  24px                  │
│                        │
│  Value                 │  ← H2/Semibold (24px), Text/Primary
│  +12.5%                │  ← Caption, Neon/Green (positive)
└────────────────────────┘
```

### Data Table

```
Width: 100%
Border-radius: 12px
Background: Background/Surface 2
Border: 1px solid Border/Default
Overflow: Hidden

Table Header:
- Background: Background/Surface 1
- Height: 48px
- Padding: 12px 16px
- Text: UI/Label (12px), Neon/Cyan, Uppercase
- Border-bottom: 2px solid Neon/Cyan

Table Row:
- Height: 64px
- Padding: 12px 16px
- Background: Background/Surface 2
- Border-bottom: 1px solid Border/Subtle
- Text: Body/Default, Text/Primary

Row (Hover):
- Background: Background/Surface 3
- Transition: 150ms

Row (Selected):
- Background: rgba(34, 211, 238, 0.05)
- Border-left: 3px solid Neon/Cyan

Cell Alignment:
- Text content: Left
- Numbers: Right
- Actions: Right
- Icons: Center

Action Buttons in Row:
- Size: 32px × 32px
- Border-radius: 8px
- Background: Transparent
- Icon: 16px, Text/Secondary
- Hover: Background rgba(255,255,255,0.05)
```

### Pagination

```
Position: Bottom of table
Height: 48px
Padding: 12px 16px
Display: Flex, justify-between, align-center
Background: Background/Surface 1
Border-top: 1px solid Border/Subtle

Left Side: "Showing 1-20 of 150"
- Text: Body/Small, Text/Tertiary

Right Side: Page Numbers
- Display: Flex, gap: 8px
- Button: 32px × 32px, rounded-lg
- Active: Background Neon/Cyan, Text Inverse
- Inactive: Text Text/Secondary
- Hover: Background rgba(34,211,238,0.1)
```

---

## 📐 Page 3: Document Ingestion

### Layout

```
Canvas: 1200px × 800px (Centered)

┌─────────────────────────────────────────────────┐
│                                                 │
│  ┌────────────────────────────────────────┐    │
│  │  Upload Area (Drag & Drop Zone)        │    │
│  │                                         │    │
│  │  [Cloud Upload Icon]                   │    │
│  │  Drag files here or click to browse    │    │
│  │  Supported: PDF, DOCX, TXT             │    │
│  │                                         │    │
│  └────────────────────────────────────────┘    │
│                                                 │
│  ┌────────────────────────────────────────┐    │
│  │  File List (After Upload)              │    │
│  │                                         │    │
│  │  ┌──────────────────────────────────┐  │    │
│  │  │ file1.pdf  [Progress Bar] 75%    │  │    │
│  │  └──────────────────────────────────┘  │    │
│  │  ┌──────────────────────────────────┐  │    │
│  │  │ file2.pdf  [Checkmark] Complete  │  │    │
│  │  └──────────────────────────────────┘  │    │
│  │                                         │    │
│  └────────────────────────────────────────┘    │
│                                                 │
│  [Process Documents Button]                    │
│                                                 │
└─────────────────────────────────────────────────┘
```

### Drag & Drop Zone

```
Width: 100%
Height: 300px
Border: 2px dashed Border/Default
Border-radius: 16px
Background: rgba(34, 211, 238, 0.02)
Display: Flex, direction: column, align: center, justify: center
Padding: 40px
Gap: 16px

Icon:
- Size: 64px
- Color: Neon/Cyan
- Opacity: 0.6

Main Text:
- H3/Semibold, Text/Primary

Subtitle:
- Body/Default, Text/Tertiary

Hover State:
- Border-color: Neon/Cyan
- Background: rgba(34, 211, 238, 0.05)
- Icon opacity: 1.0

Active (Dragging):
- Border-color: Neon/Cyan
- Border-style: solid
- Background: rgba(34, 211, 238, 0.1)
- Shadow: Glow/Cyan
```

### File List Item

```
Width: 100%
Height: 64px
Padding: 16px
Border-radius: 12px
Background: Background/Surface 2
Border: 1px solid Border/Default
Display: Flex, align-items: center
Gap: 16px
Margin-bottom: 12px

Layout:
[File Icon] [File Name] [Progress/Status] [Remove Button]
  32px      Flex-grow      160px              32px

File Icon:
- Size: 32px
- Background: Background/Surface 3
- Border-radius: 8px
- Icon: 20px, Neon/Cyan

File Name:
- Text: Body/Default, Text/Primary
- Truncate with ellipsis if too long

Progress Bar (Processing):
- Width: 160px
- Height: 4px
- Border-radius: 2px
- Background: Background/Surface 3
- Fill: Gradient Neon/Cyan → Neon/Violet
- Animated shimmer

Status (Complete):
- Icon: Checkmark, 20px, Neon/Green
- Text: Body/Small, Neon/Green

Remove Button:
- Size: 32px
- Border-radius: 8px
- Background: Transparent
- Icon: X, 16px, Text/Secondary
- Hover: Background rgba(239,68,68,0.1), Icon Neon/Red
```

---

## 🧩 Component Library Structure

### Auto Layout Components to Create

#### Button Component

**Variants:**
- Type: Primary, Secondary, Ghost, Danger
- Size: Small (32px), Medium (40px), Large (48px)
- State: Default, Hover, Active, Disabled

**Properties:**
- Icon: Boolean (show/hide leading icon)
- Label: Text
- Loading: Boolean (show spinner)

**Auto Layout:**
- Padding-horizontal: 16px (sm), 20px (md), 24px (lg)
- Padding-vertical: 8px (sm), 10px (md), 12px (lg)
- Gap: 8px
- Align: Center
- Justify: Center

#### Input Component

**Variants:**
- State: Default, Focus, Error, Disabled
- Size: Medium (40px), Large (48px)

**Properties:**
- Label: Text
- Placeholder: Text
- Helper Text: Text
- Icon: Boolean (leading/trailing)

**Auto Layout:**
- Padding: 12px 16px
- Gap: 8px
- Fill container horizontally

#### Card Component

**Variants:**
- Style: Default, Outlined, Glass
- Elevation: Flat, Low, Medium, High
- State: Default, Hover, Active

**Properties:**
- Title: Text
- Content: Text/Component
- Footer: Boolean

**Auto Layout:**
- Padding: 20px
- Gap: 16px
- Border-radius: 12px

---

## 📱 Responsive Breakpoints

### Desktop (>1024px)
```
3-column layout
Left sidebar: 240px
Main: Flexible
Right panel: 360px
```

### Tablet (640px - 1024px)
```
2-column layout
Collapsible left sidebar (overlay)
Main: Flexible
Right panel: 320px or hidden
```

### Mobile (<640px)
```
Single column, stacked
Sidebars become bottom sheets or drawer
Full width main content
```

---

## 🎬 Prototype Interactions

### Key Flows to Prototype:

1. **Message Send Flow**
   - Click input → Type → Click send
   - Animate new message (slide up + fade in)
   - Show typing indicator
   - Animate response (slide up + fade in)
   - Update insights panel (fade transition)

2. **Mode Switch**
   - Click mode selector
   - Show overlay transition
   - Animate sidebar active state change
   - Update main chat area context

3. **Card Hover**
   - Hover: Border glow + elevation
   - Click: Expand or navigate

4. **Table Row Select**
   - Click row → Highlight + check
   - Multi-select with shift/cmd

---

## 📋 Figma Plugin Recommendations

**Useful plugins for this design:**
1. **Iconify** - For Lucide/Radix icons
2. **Stark** - Contrast checker for accessibility
3. **Unsplash** - For placeholder images
4. **Content Reel** - Generate realistic content
5. **Auto Flow** - Create user flow diagrams
6. **Design Lint** - Check design consistency

---

## 🚀 Export Settings

### For Development:
- **Components**: Export as SVG @ 1x
- **Icons**: Export as SVG @ 1x
- **Screenshots**: Export as PNG @ 2x
- **Mockups**: Export as PNG @ 2x

### Naming Convention:
```
component-name-variant-state.svg
Example: button-primary-default.svg
```

---

**End of Figma Blueprint**

This complete blueprint provides all dimensions, specifications, and component structures needed to create a pixel-perfect Figma design for the SISUiQ project. Every measurement has been calculated for a professional, production-ready interface.
