FROM oven/bun:1-slim AS build

WORKDIR /app

COPY front-end/package.json ./package.json
COPY front-end/bun.lock ./bun.lock
RUN bun install --frozen-lockfile

COPY front-end/ ./

ARG VITE_API_BASE_URL=http://localhost:8000
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}

RUN bun run build

FROM nginx:1.28-alpine

COPY front-end/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80
