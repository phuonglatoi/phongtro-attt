#!/bin/bash
# ============================================
# PhongTro.vn Deployment Script
# ============================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting PhongTro.vn Deployment...${NC}"

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${RED}❌ Error: .env file not found!${NC}"
    echo "Please copy .env.example to .env and configure it."
    exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Error: Docker is not running!${NC}"
    exit 1
fi

echo -e "${YELLOW}📦 Building Docker images...${NC}"
docker-compose build --no-cache

echo -e "${YELLOW}🔄 Stopping existing containers...${NC}"
docker-compose down

echo -e "${YELLOW}🚀 Starting containers...${NC}"
docker-compose up -d

echo -e "${YELLOW}⏳ Waiting for database to be ready...${NC}"
sleep 30

echo -e "${YELLOW}📊 Running database migrations...${NC}"
docker-compose exec -T web python manage.py migrate --noinput

echo -e "${YELLOW}📁 Collecting static files...${NC}"
docker-compose exec -T web python manage.py collectstatic --noinput

echo -e "${YELLOW}🔍 Checking container status...${NC}"
docker-compose ps

echo -e "${GREEN}✅ Deployment complete!${NC}"
echo ""
echo "Your application is now running at:"
echo "  - HTTP:  http://localhost"
echo "  - HTTPS: https://localhost (if SSL configured)"
echo ""
echo "Useful commands:"
echo "  - View logs:     docker-compose logs -f"
echo "  - Stop:          docker-compose down"
echo "  - Restart:       docker-compose restart"
echo "  - Shell access:  docker-compose exec web bash"

