FROM node:24-slim
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
ENV CI=1
EXPOSE 8090
CMD ["npx", "expo", "start", "--web", "--port", "8090", "--host", "lan"]
