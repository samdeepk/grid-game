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
│   ├── context/     # React Contexts (User, Toast)
│   ├── hooks/       # Custom React Hooks
│   ├── types/       # Shared TypeScript types
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

## Architecture Highlights

- **Context API**: User authentication and Toast notifications are managed via React Context (`UserContext`, `ToastContext`).
- **Custom Hooks**: Logic is encapsulated in hooks like `useGameSession`, `useTicTacToe` for better separation of concerns.
- **Providers**: The app is wrapped in a global `Providers` component in the root layout.

## Backend API Proxy

During local development the frontend proxies API calls to the FastAPI backend so you can call `/api/...` from the browser without dealing with CORS. In production, point the frontend directly at the deployed FastAPI base URL via `NEXT_PUBLIC_API_BASE_URL`.

- By default, requests to `/api/:path*` are forwarded to `http://127.0.0.1:8000/:path*`.
- You can override the target by setting `NEXT_PUBLIC_API_PROXY_TARGET` (or `API_PROXY_TARGET`) in `.env.local`.
- Set `NEXT_PUBLIC_API_BASE_URL` to `/api` (or a full URL) during local development so requests continue to use the proxy. For production builds, set it to the publicly reachable FastAPI URL (e.g., `https://api.example.com`).

Example `.env.local`:
```
NEXT_PUBLIC_API_PROXY_TARGET=http://localhost:8000
NEXT_PUBLIC_API_BASE_URL=/api
```

Start the frontend with `pnpm dev` and the backend with `uvicorn main:app --reload`. All API calls from the browser will be proxied to the backend port.

## Production Deployment (Next.js + FastAPI on Cloud Run)

The app now uses `output: 'standalone'`, so `pnpm build` emits a self-contained Node server under `.next/standalone`. Deploy the frontend and the FastAPI backend as separate Cloud Run services:

1. **Build the frontend**
   ```bash
   cd webapp/grid-react
   pnpm install
   pnpm build
   ```
   Copy the following into your deployment artifact/image:
   - `.next/standalone/**`
   - `.next/static/**`
   - `public/**`
   - `next.config.js`
   - `package.json`, `pnpm-lock.yaml`

2. **Containerize the frontend**
   ```Dockerfile
   FROM node:20-alpine
   WORKDIR /app
   COPY package.json pnpm-lock.yaml ./
   RUN corepack enable && pnpm fetch
   COPY .next/standalone .next/standalone
   COPY .next/static .next/static
   COPY public public
   COPY next.config.js .
   ENV PORT=8080
   EXPOSE 8080
   CMD ["node", ".next/standalone/server.js", "--hostname", "0.0.0.0", "--port", "8080"]
   ```

3. **Configure environment**
   - Set `NEXT_PUBLIC_API_BASE_URL` to the FastAPI Cloud Run URL (e.g., `https://api-your-service.run.app`).
   - Optionally disable the `/api` rewrite in production if you prefer absolute URLs everywhere.

4. **Deploy FastAPI separately**
   Deploy the FastAPI service independently on Cloud Run. Enable CORS for the frontend origin if the services run on different domains.

5. **Routing options**
   - Browser calls can hit the FastAPI URL directly using `NEXT_PUBLIC_API_BASE_URL`.
   - Alternatively use Google Cloud Load Balancing or API Gateway to route `/api/*` to FastAPI and all other paths to the Next.js service, giving you one public entry point.

This separation keeps the dynamic routes (`/game/[sessionId]`, `/waiting/[sessionId]`, etc.) fully functional while letting each service scale independently.
