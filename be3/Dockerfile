FROM node:lts-alpine

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci --production

COPY . .

EXPOSE 3002

CMD ["node", "src/index.js"]
