FROM php:8.1-apache

# Copy frontend files
COPY . /var/www/html/

# Set proper permissions
RUN chown -R www-data:www-data /var/www/html \
    && chmod -R 755 /var/www/html

# Enable Apache rewrite module
RUN a2enmod rewrite