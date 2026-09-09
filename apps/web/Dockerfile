FROM node:20-alpine
WORKDIR /app
COPY package.json tsconfig.json next-env.d.ts ./
RUN npm install
COPY app ./app
COPY components ./components
RUN npm run build
EXPOSE 3000
CMD ["npm","start"]
