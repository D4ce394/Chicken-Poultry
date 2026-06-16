# FROM yarnpkg/node-yarn:node7
FROM node:lts

WORKDIR /app

COPY . /app

RUN yarn install

CMD ["sh", "-c", "yarn dev > /app/logs/app.log 2>&1"]
