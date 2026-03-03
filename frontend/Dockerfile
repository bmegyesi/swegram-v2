FROM node:24-alpine AS build

COPY . /app
WORKDIR /app
RUN npm install
RUN npm run build

FROM nginx:stable-alpine

# Remove default Nginx configuration
RUN rm -rf /etc/nginx/conf.d/*

# Remove default nginx static files
RUN rm -rf /usr/share/nginx/html/*

# Copy custom Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/

# Copy built files from build stage
COPY --from=build /app/dist /usr/share/nginx/html

# Expose the port that Nginx will run on
EXPOSE 80

# Command to start Nginx
CMD ["nginx", "-g", "daemon off;"]
