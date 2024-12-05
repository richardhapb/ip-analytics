# Etapa 1: construir la aplicación React
FROM node:20

WORKDIR /app

COPY package*.json ./

RUN npm ci --only=prod

COPY . .

RUN npm run build

FROM nginx:alpine

COPY --from=build /app/build /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

