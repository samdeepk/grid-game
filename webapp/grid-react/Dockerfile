
FROM node:20-alpine AS deps
ARG NEXT_PUBLIC_API_PROXY_TARGET

WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN corepack enable && pnpm install --frozen-lockfile

# Note: NEXT_PUBLIC_* vars are baked into the build at build time
# This is only for runtime override if needed
ENV NEXT_PUBLIC_API_BASE_URL=${NEXT_PUBLIC_API_PROXY_TARGET}

RUN echo "*******  NEXT_PUBLIC_API_BASE_URL $NEXT_PUBLIC_API_PROXY_TARGET"


FROM node:20-alpine AS builder

WORKDIR /app
ARG NEXT_PUBLIC_API_PROXY_TARGET

COPY --from=deps /app/node_modules ./node_modules
COPY . .
# Override the repository .env so Next.js picks up the desired base URL at build time
RUN if [ -n "${NEXT_PUBLIC_API_PROXY_TARGET}" ]; then \
      printf "NEXT_PUBLIC_API_BASE_URL=%s\n" "${NEXT_PUBLIC_API_PROXY_TARGET}" > .env; \
    else \
      printf "NEXT_PUBLIC_API_BASE_URL=/api/\n" > .env; \
    fi
ENV NEXT_PUBLIC_API_BASE_URL=${NEXT_PUBLIC_API_PROXY_TARGET}
RUN corepack enable && pnpm build

FROM node:20-alpine AS runner

WORKDIR /app
ENV NODE_ENV=production \
    PORT=8080


# Create non-root user
RUN addgroup -S nodejs && adduser -S nextjs -G nodejs

# Copy standalone output
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

# Copy entrypoint script and make it executable
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh && \
    chown -R nextjs:nodejs /app

USER nextjs
EXPOSE 8080

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["node", "server.js", "--hostname", "0.0.0.0", "--port", "8080"]

