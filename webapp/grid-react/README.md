# Grid Game - Next.js App

This is a [Next.js](https://nextjs.org/) project bootstrapped with TypeScript.

## Getting Started

### Prerequisites

- Node.js 18+ 
- pnpm (install with `npm install -g pnpm`)

### Installation

1. Install dependencies:
```bash
pnpm install
```

2. Run the development server:
```bash
pnpm dev
```

3. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Available Scripts

- `pnpm dev` - Start development server
- `pnpm build` - Build for production
- `pnpm start` - Start production server
- `pnpm lint` - Run ESLint
- `pnpm format` - Format code with Prettier
- `pnpm format:check` - Check code formatting

## Project Structure

```
grid-react/
├── app/              # Next.js App Router
│   ├── layout.tsx   # Root layout
│   └── page.tsx      # Home page
├── src/
│   ├── components/  # React components
│   ├── utils/       # Utility functions
│   └── *.css       # Global styles
└── public/          # Static assets
```

## Tech Stack

- **Next.js 15** - React framework
- **React 19** - UI library
- **TypeScript** - Type safety
- **SCSS** - Styling
- **pnpm** - Package manager
