
FROM node:20-alpine AS deps
ARG NEXT_PUBLIC_API_BASE_URL

WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN corepack enable && pnpm install --frozen-lockfile

FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN corepack enable && pnpm build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production \
    PORT=8080


ENV NEXT_PUBLIC_API_BASE_URL=${NEXT_PUBLIC_API_BASE_URL}
RUN echo "NEXT_PUBLIC_API_BASE_URL $NEXT_PUBLIC_API_BASE_URL"

RUN echo "NEXT_PUBLIC_API_BASE_URL:${NEXT_PUBLIC_API_BASE_URL}" > .env


# Create non-root user
RUN addgroup -S nodejs && adduser -S nextjs -G nodejs

# Copy standalone output
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

USER nextjs
EXPOSE 8080

CMD ["node", "server.js", "--hostname", "0.0.0.0", "--port", "8080"]

