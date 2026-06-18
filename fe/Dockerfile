FROM node:lts-alpine AS builder

WORKDIR /app

ARG PUBLIC_API_URL=http://localhost:3001/api
ARG PUBLIC_BE2_URL=http://localhost:8000
ARG BUILD_TARGET=node

ENV PUBLIC_API_URL=$PUBLIC_API_URL
ENV PUBLIC_BE2_URL=$PUBLIC_BE2_URL
ENV BUILD_TARGET=$BUILD_TARGET

COPY package.json yarn.lock ./
RUN yarn install --frozen-lockfile

COPY . .
RUN yarn build

FROM node:lts-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production

COPY --from=builder /app/build ./build
COPY --from=builder /app/package.json ./
COPY --from=builder /app/yarn.lock ./

RUN yarn install --production --frozen-lockfile

EXPOSE 3000

CMD ["node", "build/index.js"]
