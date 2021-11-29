# Use the Nginx image
FROM nginx

# EXPOSE 8080

# Remove the default nginx.conf
RUN rm /etc/nginx/conf.d/default.conf

# attach logging volume
# VOLUME /var/log/nginx

# Replace with our own nginx.conf
COPY nginx.conf /etc/nginx/conf.d/
