FROM node:20-alpine AS build

WORKDIR /app

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend/ .

ARG VITE_SENTRY_DSN=""
ENV VITE_SENTRY_DSN=$VITE_SENTRY_DSN

RUN npm run build

FROM alpine:3.19

COPY --from=build /app/dist /dist

CMD ["cp", "-r", "/dist/.", "/output/"]
