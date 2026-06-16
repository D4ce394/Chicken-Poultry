FROM node:lts

WORKDIR /app

COPY . /app

RUN npm install

CMD ["sh", "-c", "npm run dev > /app/logs/app.log 2>&1"]



