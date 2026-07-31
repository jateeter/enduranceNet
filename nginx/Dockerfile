FROM nginx:1.27-alpine

ENV NGINX_ENVSUBST_OUTPUT_DIR=/etc/nginx

COPY nginx.conf /etc/nginx/templates/nginx.conf.template

# Directory for Let's Encrypt ACME challenge
RUN mkdir -p /var/www/certbot

EXPOSE 80 443

CMD ["nginx", "-g", "daemon off;"]
