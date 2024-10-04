FROM node:18 as build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY .docker/nginx.conf /etc/nginx/nginx.con
COPY --from=build /app/dist/my-angular-app/browser /usr/share/nginx/html

EXPOSE 80
