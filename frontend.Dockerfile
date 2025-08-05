# Dockerfile serving the Nuxt frontend in development mode
FROM node:22-alpine

WORKDIR /frontend
CMD ["yarn", "dev"]

COPY package.json yarn.lock ./

RUN yarn install --frozen-lockfile --production=false

COPY . .
