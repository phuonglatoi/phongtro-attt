# 🚀 HƯỚNG DẪN DEPLOY CODE (PART 2)

## 📋 **BƯỚC DEPLOY TRÊN MÁY ẢO:**

---

### **BƯỚC 1: Clone code từ GitHub**

```bash
# SSH vào máy ảo
ssh user@your-vm-ip

# Clone repository (KHÔNG chứa .env)
git clone https://github.com/phuonglatoi/phongtro-attt.git
cd phongtro-attt

# Kiểm tra .env KHÔNG có trong repo
ls -la | grep .env
# Chỉ thấy .env.example ← OK!
```

---

### **BƯỚC 2: Tạo file `.env` trên máy ảo**

```bash
# Copy từ template
cp .env.example .env

# Chỉnh sửa với thông tin thật
nano .env
```

**Điền thông tin:**
```ini
SECRET_KEY=<generate-random-50-chars>
DEBUG=False
ALLOWED_HOSTS=your-domain.com,192.168.x.x

# Database - Kết nối đến máy local
DB_HOST=192.168.1.100  # ← IP máy local của bạn
DB_USER=phongtro_app_user
DB_PASSWORD=StrongP@ssw0rd!2024#Secure

# Email
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

**Tạo SECRET_KEY ngẫu nhiên:**
```python
# Trên máy ảo
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

### **BƯỚC 3: Cài đặt dependencies**

```bash
# Tạo virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux
# hoặc: venv\Scripts\activate  # Windows

# Cài packages
pip install -r requirements.txt

# Cài ODBC Driver (nếu chưa có)
# Ubuntu/Debian:
curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list | sudo tee /etc/apt/sources.list.d/mssql-release.list
sudo apt-get update
sudo ACCEPT_EULA=Y apt-get install -y msodbcsql18
```

---

### **BƯỚC 4: Test kết nối database**

```bash
# Test connection
python manage.py check

# Nếu thành công, chạy migrations (nếu cần)
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput
```

---

### **BƯỚC 5: Chạy server (Development)**

```bash
# Chạy development server để test
python manage.py runserver 0.0.0.0:8000

# Truy cập từ browser:
# http://192.168.x.x:8000
```

---

### **BƯỚC 6: Deploy Production với Gunicorn + Nginx**

#### **6.1. Cài Gunicorn:**
```bash
pip install gunicorn
```

#### **6.2. Tạo file `gunicorn_config.py`:**
```python
# gunicorn_config.py
bind = "127.0.0.1:8000"
workers = 4
worker_class = "sync"
timeout = 120
accesslog = "/var/log/gunicorn/access.log"
errorlog = "/var/log/gunicorn/error.log"
loglevel = "info"
```

#### **6.3. Chạy Gunicorn:**
```bash
# Tạo thư mục logs
sudo mkdir -p /var/log/gunicorn
sudo chown $USER:$USER /var/log/gunicorn

# Chạy Gunicorn
gunicorn config.wsgi:application -c gunicorn_config.py
```

#### **6.4. Cấu hình Nginx:**
```nginx
# /etc/nginx/sites-available/phongtro
server {
    listen 80;
    server_name your-domain.com;

    location /static/ {
        alias /path/to/phongtro-attt/staticfiles/;
    }

    location /media/ {
        alias /path/to/phongtro-attt/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/phongtro /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

### **BƯỚC 7: Tạo systemd service (Auto-start)**

```bash
# /etc/systemd/system/phongtro.service
[Unit]
Description=PhongTro Django Application
After=network.target

[Service]
User=your-user
Group=www-data
WorkingDirectory=/path/to/phongtro-attt
Environment="PATH=/path/to/phongtro-attt/venv/bin"
ExecStart=/path/to/phongtro-attt/venv/bin/gunicorn config.wsgi:application -c gunicorn_config.py

[Install]
WantedBy=multi-user.target
```

```bash
# Enable và start service
sudo systemctl daemon-reload
sudo systemctl enable phongtro
sudo systemctl start phongtro
sudo systemctl status phongtro
```

---

## 🔐 **BẢO MẬT FILE `.env` TRÊN MÁY ẢO:**

### **1. Phân quyền file:**
```bash
# Chỉ owner mới đọc được
chmod 600 .env
chown your-user:your-user .env

# Kiểm tra
ls -la .env
# -rw------- 1 your-user your-user 1234 Dec 26 .env
```

### **2. Mã hóa `.env` (Optional - Nâng cao):**
```bash
# Cài ansible-vault
pip install ansible

# Mã hóa .env
ansible-vault encrypt .env
# Nhập password

# Khi cần dùng, giải mã:
ansible-vault decrypt .env
```

### **3. Dùng Secret Manager (Production thực tế):**
- **AWS Secrets Manager**
- **Azure Key Vault**
- **HashiCorp Vault**

---

## 🔄 **QUY TRÌNH CÂP NHẬT CODE:**

```bash
# 1. Pull code mới từ GitHub
cd /path/to/phongtro-attt
git pull origin main

# 2. Cài dependencies mới (nếu có)
source venv/bin/activate
pip install -r requirements.txt

# 3. Chạy migrations (nếu có)
python manage.py migrate

# 4. Collect static files
python manage.py collectstatic --noinput

# 5. Restart service
sudo systemctl restart phongtro
```

**LƯU Ý:** File `.env` KHÔNG bị ghi đè vì không có trong Git!

---

## 🛡️ **CHECKLIST BẢO MẬT:**

### **Trên GitHub:**
- [ ] `.env` KHÔNG có trong repository
- [ ] `.gitignore` đã có `.env`
- [ ] Không có password hardcode trong code
- [ ] Không có API keys trong code

### **Trên máy ảo:**
- [ ] File `.env` có permission 600
- [ ] Firewall chỉ mở port 80, 443, 22
- [ ] SSH dùng key thay vì password
- [ ] `DEBUG=False` trong production
- [ ] Gunicorn chạy dưới user thường (không phải root)
- [ ] Nginx đã cấu hình SSL/TLS (HTTPS)

### **Trên máy local (Database):**
- [ ] SQL Server firewall chỉ cho phép IP máy ảo
- [ ] SQL Login có password mạnh (12+ ký tự)
- [ ] Không dùng `sa` account
- [ ] Enable SQL Server Audit
- [ ] Backup database định kỳ

---

## 📊 **KIẾN TRÚC TRIỂN KHAI:**

```
┌─────────────────────────────────────────────┐
│           INTERNET (Users)                  │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
         ┌─────────────────┐
         │  Nginx (Port 80) │
         │  + SSL/TLS       │
         └────────┬─────────┘
                  │
                  ▼
         ┌─────────────────┐
         │  Gunicorn        │
         │  (Django App)    │
         └────────┬─────────┘
                  │
                  │ .env file
                  │ (DB_HOST=192.168.1.100)
                  │
                  ▼
    ┌─────────────────────────────┐
    │  SSH Tunnel / VPN           │
    │  (Encrypted Connection)     │
    └──────────────┬──────────────┘
                   │
                   ▼
         ┌─────────────────┐
         │  SQL Server      │
         │  (Máy Local)     │
         │  192.168.1.100   │
         └──────────────────┘
```

---

## 🎯 **TÓM TẮT:**

✅ **Code trên GitHub:** KHÔNG chứa `.env`, password, secrets  
✅ **File `.env` trên máy ảo:** Chứa thông tin kết nối thật, permission 600  
✅ **Kết nối DB:** Qua SSH Tunnel hoặc VPN (mã hóa)  
✅ **Firewall:** Chỉ cho phép IP cụ thể  
✅ **Production:** Dùng Gunicorn + Nginx + systemd  

---

**Bây giờ bạn có thể deploy an toàn mà không lo lộ thông tin!** 🔒✨

