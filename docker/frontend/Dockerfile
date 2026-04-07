FROM node:20-alpine AS build

WORKDIR /app

COPY frontend/package.json ./
RUN npm install

COPY frontend/ .
RUN npm run build

FROM alpine:3.19

COPY --from=build /app/dist /dist

CMD ["cp", "-r", "/dist/.", "/output/"]
