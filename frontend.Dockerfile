# Dockerfile serving the Nuxt frontend in development mode
FROM node:14-alpine

WORKDIR /frontend
CMD ["yarn", "dev"]

COPY package.json yarn.lock ./

RUN yarn install

COPY . .
