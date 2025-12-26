#!/bin/bash
# ============================================
# SSH Tunnel Setup Script
# Tạo kết nối an toàn từ máy ảo đến SQL Server trên máy local
# ============================================

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  SSH Tunnel Setup for SQL Server${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# ============================================
# CẤU HÌNH
# ============================================
echo -e "${YELLOW}Nhập thông tin kết nối:${NC}"
read -p "IP máy local (SQL Server): " LOCAL_IP
read -p "SSH username trên máy local: " SSH_USER
read -p "SQL Server port (default 1433): " SQL_PORT
SQL_PORT=${SQL_PORT:-1433}

# ============================================
# KIỂM TRA SSH KEY
# ============================================
echo ""
echo -e "${YELLOW}Kiểm tra SSH key...${NC}"

if [ ! -f ~/.ssh/id_rsa ]; then
    echo -e "${YELLOW}Chưa có SSH key. Tạo mới...${NC}"
    ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N ""
    echo -e "${GREEN}✅ SSH key đã tạo!${NC}"
fi

# ============================================
# COPY SSH KEY ĐẾN MÁY LOCAL
# ============================================
echo ""
echo -e "${YELLOW}Copy SSH key đến máy local...${NC}"
echo -e "${YELLOW}Bạn sẽ cần nhập password của user ${SSH_USER}@${LOCAL_IP}${NC}"

ssh-copy-id ${SSH_USER}@${LOCAL_IP}

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ SSH key đã copy thành công!${NC}"
else
    echo -e "${RED}❌ Lỗi khi copy SSH key. Vui lòng kiểm tra lại.${NC}"
    exit 1
fi

# ============================================
# TEST KẾT NỐI SSH
# ============================================
echo ""
echo -e "${YELLOW}Test kết nối SSH...${NC}"

ssh -o BatchMode=yes -o ConnectTimeout=5 ${SSH_USER}@${LOCAL_IP} "echo 'SSH OK'" 2>/dev/null

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Kết nối SSH thành công!${NC}"
else
    echo -e "${RED}❌ Không thể kết nối SSH. Vui lòng kiểm tra:${NC}"
    echo "  - SSH service đã chạy trên máy local chưa?"
    echo "  - Firewall có cho phép port 22 không?"
    exit 1
fi

# ============================================
# TẠO SSH TUNNEL
# ============================================
echo ""
echo -e "${YELLOW}Tạo SSH tunnel...${NC}"

# Kill existing tunnel nếu có
pkill -f "ssh.*${LOCAL_IP}.*${SQL_PORT}" 2>/dev/null || true

# Tạo tunnel mới
ssh -f -N -L ${SQL_PORT}:localhost:${SQL_PORT} ${SSH_USER}@${LOCAL_IP}

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ SSH tunnel đã tạo thành công!${NC}"
    echo ""
    echo -e "${GREEN}Thông tin kết nối:${NC}"
    echo "  Local Port: ${SQL_PORT}"
    echo "  Remote: ${LOCAL_IP}:${SQL_PORT}"
    echo ""
    echo -e "${YELLOW}Trong file .env, dùng:${NC}"
    echo "  DB_HOST=localhost"
    echo "  DB_PORT=${SQL_PORT}"
else
    echo -e "${RED}❌ Lỗi khi tạo SSH tunnel${NC}"
    exit 1
fi

# ============================================
# TẠO SYSTEMD SERVICE (AUTO-START)
# ============================================
echo ""
read -p "Bạn có muốn tạo systemd service để auto-start tunnel không? (y/n): " CREATE_SERVICE

if [ "$CREATE_SERVICE" = "y" ]; then
    SERVICE_FILE="/etc/systemd/system/sql-tunnel.service"
    
    echo -e "${YELLOW}Tạo systemd service...${NC}"
    
    sudo tee $SERVICE_FILE > /dev/null <<EOF
[Unit]
Description=SSH Tunnel to SQL Server
After=network.target

[Service]
Type=simple
User=$USER
ExecStart=/usr/bin/ssh -N -L ${SQL_PORT}:localhost:${SQL_PORT} ${SSH_USER}@${LOCAL_IP}
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    sudo systemctl enable sql-tunnel
    sudo systemctl start sql-tunnel
    
    echo -e "${GREEN}✅ Systemd service đã tạo và khởi động!${NC}"
    echo ""
    echo "Các lệnh quản lý:"
    echo "  sudo systemctl status sql-tunnel   # Kiểm tra trạng thái"
    echo "  sudo systemctl restart sql-tunnel  # Khởi động lại"
    echo "  sudo systemctl stop sql-tunnel     # Dừng"
fi

# ============================================
# HOÀN TẤT
# ============================================
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  ✅ HOÀN TẤT!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Bây giờ bạn có thể kết nối đến SQL Server qua:"
echo "  Host: localhost"
echo "  Port: ${SQL_PORT}"
echo ""
echo "Tất cả traffic đã được mã hóa qua SSH tunnel!"

