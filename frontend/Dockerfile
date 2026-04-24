# frontend/Dockerfile
FROM nginx:alpine

# Remove default nginx config
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom configuration
COPY nginx.conf /etc/nginx/conf.d/

# Copy static assets
COPY css /usr/share/nginx/html/css
COPY js /usr/share/nginx/html/js
COPY index.html /usr/share/nginx/html/

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]