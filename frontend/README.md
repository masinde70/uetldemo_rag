# SISUiQ Frontend

Next.js 15 frontend application with App Router, shadcn/ui, and Tailwind CSS.

## 📁 Structure

```
frontend/
├── app/                    # Next.js App Router
│   ├── layout.tsx         # Root layout
│   ├── page.tsx           # Home page
│   ├── chat/              # Chat interface
│   └── admin/             # Admin dashboard
├── components/
│   ├── ui/                # shadcn/ui components
│   ├── chat/              # Chat-specific components
│   ├── admin/             # Admin components
│   └── analytics/         # Analytics visualizations
├── lib/
│   ├── api.ts             # API client
│   ├── utils.ts           # Utilities
│   └── constants.ts       # Constants
└── public/
    └── assets/            # Images, icons, fonts
```

## 🎨 Design System

### Theme
- Space-themed, futuristic design
- Dark mode optimized
- Professional enterprise look

### Colors
- Primary: Deep blue (#0A1628)
- Accent: Electric blue (#00D9FF)
- Success: Green (#00FF88)
- Warning: Amber (#FFB800)

### Components
All UI components use shadcn/ui for consistency and accessibility.

## 🚀 Development

**Requirements**: Node.js 20+ LTS (or latest 22+)

```bash
npm install
npm run dev          # Development server
npm run build        # Production build
npm run lint         # Lint code
```

## 🔧 Environment Variables

Create `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=SISUiQ
```

## 📱 Features

### Chat Interface
- Multi-mode agent selection
- Real-time streaming responses
- Citation display
- Message history

### Analytics Panel
- Outage visualizations
- KPI tracking
- Strategy alignment metrics

### Admin Dashboard
- Session management
- Document viewer
- Usage analytics
- Model monitoring
