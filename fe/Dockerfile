FROM node:lts-alpine AS builder

WORKDIR /app

COPY package.json yarn.lock ./
RUN yarn install --frozen-lockfile

COPY . .
RUN yarn build

FROM node:lts-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production

COPY --from=builder /app/build ./build
COPY --from=builder /app/package.json ./

RUN yarn install --production --frozen-lockfile

EXPOSE 3000

CMD ["node", "build/index.js"]
