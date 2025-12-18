#!/bin/bash
# ============================================
# SSL Certificate Setup with Let's Encrypt
# ============================================

set -e

# Configuration
DOMAIN=${1:-"yourdomain.com"}
EMAIL=${2:-"admin@yourdomain.com"}

echo "🔐 Setting up SSL for: $DOMAIN"
echo "📧 Email: $EMAIL"

# Create directories
mkdir -p certbot/conf certbot/www

# Stop nginx if running
docker-compose stop nginx 2>/dev/null || true

# Get certificate
docker run -it --rm \
    -v "$(pwd)/certbot/conf:/etc/letsencrypt" \
    -v "$(pwd)/certbot/www:/var/www/certbot" \
    -p 80:80 \
    certbot/certbot certonly \
    --standalone \
    --email $EMAIL \
    --agree-tos \
    --no-eff-email \
    -d $DOMAIN \
    -d www.$DOMAIN

echo "✅ SSL certificate obtained!"
echo ""
echo "Next steps:"
echo "1. Update docker/nginx/conf.d/phongtro.conf with your domain"
echo "2. Run: docker-compose up -d"
echo ""
echo "Certificate will auto-renew via certbot container."

