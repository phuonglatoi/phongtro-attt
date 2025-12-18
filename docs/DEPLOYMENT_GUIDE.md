# 🚀 Hướng dẫn Triển khai PhongTro.vn

## 📋 Tổng quan

Tài liệu này hướng dẫn triển khai PhongTro.vn lên server với bảo mật tối đa.

## 🏗️ Kiến trúc đề xuất

```
┌─────────────────────────────────────────────────────────────┐
│                     INTERNET                                │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  CLOUDFLARE (WAF + DDoS)                    │
│                  - SSL/TLS Termination                      │
│                  - Rate Limiting                            │
│                  - Bot Protection                           │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    NGINX (Reverse Proxy)                    │
│                    Port 443 (HTTPS only)                    │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    GUNICORN (WSGI)                          │
│                    Port 8000 (internal)                     │
└─────────────────────────────────────────────────────────────┘
                            │
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
┌──────────────────┐ ┌──────────────┐ ┌──────────────────┐
│   SQL Server     │ │    Redis     │ │   File Storage   │
│   (Database)     │ │   (Cache)    │ │    (Media)       │
└──────────────────┘ └──────────────┘ └──────────────────┘
```

## 🖥️ Lựa chọn Server

### Option 1: VPS (Khuyến nghị cho team nhỏ)
- **DigitalOcean**: $12-24/tháng
- **Vultr**: $10-20/tháng
- **Linode**: $12-24/tháng
- **Azure VM**: ~$20-40/tháng

### Option 2: Cloud Platform
- **Azure App Service** (tích hợp tốt với SQL Server)
- **AWS Elastic Beanstalk**
- **Google Cloud Run**

### Cấu hình tối thiểu:
- **CPU**: 2 vCPU
- **RAM**: 4GB
- **Storage**: 40GB SSD
- **OS**: Ubuntu 22.04 LTS

---

## 📝 Bước 1: Chuẩn bị Server

### 1.1. Cập nhật hệ thống
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3.11 python3.11-venv python3-pip nginx redis-server
sudo apt install -y git curl wget ufw fail2ban
```

### 1.2. Tạo user riêng cho ứng dụng
```bash
# Tạo user không có shell access
sudo adduser --system --group --no-create-home phongtro
sudo mkdir -p /var/www/phongtro
sudo chown phongtro:phongtro /var/www/phongtro
```

### 1.3. Cấu hình Firewall (UFW)
```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

### 1.4. Cấu hình Fail2Ban (Chống brute force SSH)
```bash
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
sudo nano /etc/fail2ban/jail.local
```

Thêm:
```ini
[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
bantime = 3600
```

```bash
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

---

## 📝 Bước 2: Triển khai ứng dụng

### 2.1. Clone source code
```bash
cd /var/www/phongtro
sudo -u phongtro git clone https://github.com/YOUR_REPO/PhongTroATTT.git app
cd app
```

### 2.2. Tạo Virtual Environment
```bash
sudo -u phongtro python3.11 -m venv venv
sudo -u phongtro ./venv/bin/pip install --upgrade pip
sudo -u phongtro ./venv/bin/pip install -r requirements.txt
sudo -u phongtro ./venv/bin/pip install gunicorn
```

### 2.3. Tạo file .env (QUAN TRỌNG!)
```bash
sudo -u phongtro nano /var/www/phongtro/app/.env
```

```ini
# ============================================
# DJANGO SETTINGS
# ============================================
SECRET_KEY=your-very-long-random-secret-key-here-min-50-chars
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# ============================================
# DATABASE (SQL Server)
# ============================================
DB_NAME=PhongTroATTT
DB_USER=your_db_user
DB_PASSWORD=YourSecurePassword123!
DB_HOST=your-sql-server.database.windows.net
DB_PORT=1433

# ============================================
# REDIS (Cache & Session)
# ============================================
REDIS_URL=redis://127.0.0.1:6379/0

# ============================================
# SECURITY KEYS
# ============================================
RECAPTCHA_PUBLIC_KEY=your_recaptcha_public_key
RECAPTCHA_PRIVATE_KEY=your_recaptcha_private_key
GOOGLE_OAUTH_CLIENT_ID=your_google_oauth_client_id
GOOGLE_OAUTH_CLIENT_SECRET=your_google_oauth_client_secret

# ============================================
# EMAIL (SMTP)
# ============================================
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# ============================================
# SENTRY (Error Monitoring)
# ============================================
SENTRY_DSN=https://xxx@xxx.ingest.sentry.io/xxx
```

### 2.4. Collect Static Files
```bash
cd /var/www/phongtro/app
sudo -u phongtro ./venv/bin/python manage.py collectstatic --noinput --settings=config.settings.production
```

---

## 📝 Bước 3: Cấu hình Gunicorn

### 3.1. Tạo Gunicorn systemd service
```bash
sudo nano /etc/systemd/system/phongtro.service
```

```ini
[Unit]
Description=PhongTro.vn Gunicorn Daemon
After=network.target

[Service]
User=phongtro
Group=phongtro
WorkingDirectory=/var/www/phongtro/app
Environment="DJANGO_SETTINGS_MODULE=config.settings.production"
EnvironmentFile=/var/www/phongtro/app/.env
ExecStart=/var/www/phongtro/app/venv/bin/gunicorn \
    --workers 3 \
    --bind unix:/var/www/phongtro/app/phongtro.sock \
    --access-logfile /var/log/phongtro/access.log \
    --error-logfile /var/log/phongtro/error.log \
    --capture-output \
    config.wsgi:application
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

### 3.2. Tạo thư mục log
```bash
sudo mkdir -p /var/log/phongtro
sudo chown phongtro:phongtro /var/log/phongtro
```

### 3.3. Khởi động service
```bash
sudo systemctl daemon-reload
sudo systemctl enable phongtro
sudo systemctl start phongtro
sudo systemctl status phongtro
```

---

## 📝 Bước 4: Cấu hình Nginx (HTTPS)

### 4.1. Cài đặt SSL Certificate (Let's Encrypt)
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

### 4.2. Cấu hình Nginx
```bash
sudo nano /etc/nginx/sites-available/phongtro
```

```nginx
# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

# Main HTTPS server
server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:50m;
    ssl_stapling on;
    ssl_stapling_verify on;

    # Security Headers
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' https://www.google.com https://www.gstatic.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com; img-src 'self' data: https:; frame-src https://www.google.com;" always;

    # Rate Limiting
    limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;
    limit_req_zone $binary_remote_addr zone=general:10m rate=30r/s;

    # Logging
    access_log /var/log/nginx/phongtro_access.log;
    error_log /var/log/nginx/phongtro_error.log;

    # Max upload size
    client_max_body_size 10M;

    # Static files
    location /static/ {
        alias /var/www/phongtro/app/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Media files
    location /media/ {
        alias /var/www/phongtro/app/media/;
        expires 7d;
        add_header Cache-Control "public";

        # Prevent execution of uploaded files
        location ~* \.(php|py|pl|sh|bash)$ {
            deny all;
        }
    }

    # Rate limit login
    location /accounts/login/ {
        limit_req zone=login burst=3 nodelay;
        proxy_pass http://unix:/var/www/phongtro/app/phongtro.sock;
        include proxy_params;
    }

    # Django application
    location / {
        limit_req zone=general burst=50 nodelay;
        proxy_pass http://unix:/var/www/phongtro/app/phongtro.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 300s;
        proxy_read_timeout 300s;
    }

    # Block sensitive files
    location ~ /\. {
        deny all;
    }
    location ~ \.env$ {
        deny all;
    }
}
```

### 4.3. Kích hoạt site
```bash
sudo ln -s /etc/nginx/sites-available/phongtro /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 📝 Bước 5: Cấu hình Database Security

### 5.1. SQL Server trên Azure
```sql
-- Tạo user riêng cho ứng dụng (không dùng sa/admin)
CREATE LOGIN phongtro_app WITH PASSWORD = 'SecurePassword123!';
CREATE USER phongtro_app FOR LOGIN phongtro_app;

-- Chỉ cấp quyền cần thiết (Principle of Least Privilege)
GRANT SELECT, INSERT, UPDATE, DELETE ON SCHEMA::dbo TO phongtro_app;

-- Bật Transparent Data Encryption
ALTER DATABASE PhongTroATTT SET ENCRYPTION ON;

-- Bật auditing
ALTER DATABASE PhongTroATTT SET QUERY_STORE = ON;
```

### 5.2. Firewall Rules
- Chỉ cho phép IP của server truy cập database
- Sử dụng Private Endpoint nếu dùng Azure

---

## 📝 Bước 6: Monitoring & Logging

### 6.1. Sentry (Error Tracking)
Đã tích hợp trong requirements.txt. Cấu hình DSN trong .env

### 6.2. Log Rotation
```bash
sudo nano /etc/logrotate.d/phongtro
```

```
/var/log/phongtro/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 phongtro phongtro
    sharedscripts
    postrotate
        systemctl reload phongtro >/dev/null 2>&1 || true
    endscript
}
```

---

## 🔐 Bước 7: Security Checklist

### ✅ Server Security
- [ ] UFW firewall enabled (only 80, 443, SSH)
- [ ] Fail2Ban configured for SSH
- [ ] SSH key-only authentication (disable password)
- [ ] Non-root user for deployment
- [ ] Regular security updates (unattended-upgrades)

### ✅ Application Security
- [ ] DEBUG=False in production
- [ ] Strong SECRET_KEY (50+ characters)
- [ ] HTTPS only (SECURE_SSL_REDIRECT=True)
- [ ] HSTS enabled
- [ ] CSRF protection enabled
- [ ] Content Security Policy headers
- [ ] Rate limiting configured

### ✅ Database Security
- [ ] Strong database password
- [ ] Separate database user (not admin)
- [ ] Firewall rules (IP whitelist)
- [ ] Encrypted connections (TLS)
- [ ] Regular backups

### ✅ Monitoring
- [ ] Sentry for error tracking
- [ ] Log rotation configured
- [ ] Health check endpoint
- [ ] Uptime monitoring (UptimeRobot, etc.)

---

## 🚀 Quick Deploy Script

Tạo script tự động deploy:

```bash
#!/bin/bash
# deploy.sh

set -e

echo "🚀 Starting deployment..."

cd /var/www/phongtro/app

# Pull latest code
sudo -u phongtro git pull origin main

# Install dependencies
sudo -u phongtro ./venv/bin/pip install -r requirements.txt

# Collect static
sudo -u phongtro ./venv/bin/python manage.py collectstatic --noinput --settings=config.settings.production

# Restart services
sudo systemctl restart phongtro
sudo systemctl restart nginx

echo "✅ Deployment complete!"
```

---

## 📞 Hỗ trợ

Nếu gặp vấn đề, kiểm tra:
1. `sudo systemctl status phongtro`
2. `sudo tail -f /var/log/phongtro/error.log`
3. `sudo tail -f /var/log/nginx/phongtro_error.log`

