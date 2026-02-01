# Income Smoothing Platform - Frontend

Production-ready React + TypeScript frontend for the Income Smoothing Platform.

## Features

- ✅ **Automatic Theme Detection** - Follows system dark/light mode
- ✅ **Responsive Design** - Works on all devices (mobile, tablet, desktop)
- ✅ **Smooth Animations** - Framer Motion & GSAP for fluid interactions
- ✅ **Real-time Charts** - Recharts for data visualization
- ✅ **Type Safety** - Full TypeScript coverage
- ✅ **Conservative Design** - Trust-first, calm UI following fintech best practices

## Tech Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Framer Motion** - Animations
- **Recharts** - Charts and graphs
- **Zustand** - State management
- **Axios** - API client
- **CSS Modules** - Scoped styling

## Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Start development server:
```bash
npm run dev
```

The app will be available at http://localhost:3000

## Build for Production

```bash
npm run build
```

The production build will be in the `dist` folder.

## Project Structure

```
frontend/
├── src/
│   ├── components/      # Reusable UI components
│   │   ├── Card.tsx
│   │   ├── StatCard.tsx
│   │   ├── Loading.tsx
│   │   └── Layout.tsx
│   ├── pages/          # Main application pages
│   │   ├── Login.tsx
│   │   ├── Register.tsx
│   │   ├── Dashboard.tsx
│   │   ├── IncomeBreakdown.tsx
│   │   ├── IncomeSmoothing.tsx
│   │   └── Insights.tsx
│   ├── services/       # API integration
│   │   └── api.ts
│   ├── store/          # State management
│   │   └── authStore.ts
│   ├── hooks/          # Custom React hooks
│   │   └── useTheme.ts
│   ├── styles/         # Global styles and theme
│   │   └── theme.ts
│   ├── App.tsx         # Main app component
│   ├── main.tsx        # Entry point
│   └── index.css       # Global CSS
├── index.html
├── package.json
├── tsconfig.json
└── vite.config.ts
```

## Design Philosophy

### Colors
- **Background**: Off-white / Light grey
- **Primary**: Charcoal / Deep navy
- **Positive**: Muted green
- **Warning**: Muted amber
- **Negative**: Soft red

### Typography
- Sans-serif fonts for clarity
- Tabular numbers for financial data
- Consistent spacing and hierarchy

### UX Principles
1. **Calm & Conservative** - No flashy animations or distracting elements
2. **Trust-first** - Clear explanations and transparent calculations
3. **Numbers > Visuals** - Data takes priority over decorative elements
4. **Responsive** - Works seamlessly on all devices
5. **Accessible** - Follows WCAG guidelines

## API Integration

The frontend connects to the backend API at `http://localhost:8000` through a proxy configured in `vite.config.ts`.

All API calls are made through the centralized `services/api.ts` file with:
- Automatic token injection
- Error handling
- Type-safe responses

## Theme System

The app automatically detects and follows the system's dark/light mode preference using the `useTheme` hook. The theme can be toggled manually if needed.

## Performance

- **Lazy Loading** - Components load on demand
- **Code Splitting** - Optimized bundle sizes
- **Memoization** - Prevents unnecessary re-renders
- **Optimized Charts** - Efficient data visualization

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Test Credentials

- Email: testuser1@example.com
- Password: TestPass123
