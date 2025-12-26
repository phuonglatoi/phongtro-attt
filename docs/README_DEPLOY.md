# 📚 TÀI LIỆU DEPLOY AN TOÀN

## 🎯 **MỤC ĐÍCH:**
Hướng dẫn deploy ứng dụng Django với **Database ở máy local** và **Code ở máy ảo** một cách **AN TOÀN**.

---

## 📖 **CÁC TÀI LIỆU:**

### **1. 📝 TOM_TAT_DEPLOY_AN_TOAN.md** ⭐ **BẮT ĐẦU TỪ ĐÂY**
**Nội dung:** Tóm tắt ngắn gọn, dễ hiểu
- Vấn đề cần giải quyết
- Giải pháp 3 bước
- Checklist nhanh
- So sánh các phương án
- FAQ

**Đọc khi:**
- Bạn muốn hiểu tổng quan
- Cần checklist nhanh
- Chưa biết bắt đầu từ đâu

---

### **2. 🔐 HUONG_DAN_DEPLOY_AN_TOAN.md** (Part 1)
**Nội dung:** Bảo mật Database
- Cấu hình `.env` file
- Setup SQL Server cho remote access
- Cấu hình Firewall
- SSH Tunnel setup (KHUYẾN NGHỊ)
- VPN alternatives (Tailscale, WireGuard)
- 5 lớp bảo mật
- So sánh các phương án

**Đọc khi:**
- Cần setup kết nối database
- Muốn hiểu chi tiết về bảo mật
- Cần cấu hình SQL Server

---

### **3. 🚀 HUONG_DAN_DEPLOY_AN_TOAN_PART2.md** (Part 2)
**Nội dung:** Deploy Code
- Clone code từ GitHub
- Tạo `.env` trên máy ảo
- Cài đặt dependencies
- Test kết nối database
- Production deployment (Gunicorn + Nginx)
- Systemd service setup
- Quy trình cập nhật code
- Security checklist

**Đọc khi:**
- Đã setup xong database
- Cần deploy code lên máy ảo
- Muốn setup production server

---

## 🛠️ **SCRIPTS HỖ TRỢ:**

### **1. 🔧 scripts/setup_ssh_tunnel.sh**
**Chức năng:** Tự động setup SSH Tunnel
- Tạo SSH keys
- Copy keys đến máy local
- Tạo encrypted tunnel
- Tạo systemd service (auto-start)

**Cách dùng:**
```bash
bash scripts/setup_ssh_tunnel.sh
# Nhập IP máy local và SSH username
```

---

### **2. 🔍 scripts/test_db_connection.py**
**Chức năng:** Test kết nối database
- Kiểm tra pyodbc
- Kiểm tra ODBC driver
- Test connection
- Kiểm tra Django tables
- Troubleshooting tips

**Cách dùng:**
```bash
python scripts/test_db_connection.py
```

---

## 🗺️ **LỘ TRÌNH HỌC:**

```
1. Đọc TOM_TAT_DEPLOY_AN_TOAN.md
   ↓
2. Đọc HUONG_DAN_DEPLOY_AN_TOAN.md (Part 1)
   ↓
3. Chạy scripts/setup_ssh_tunnel.sh (Optional)
   ↓
4. Đọc HUONG_DAN_DEPLOY_AN_TOAN_PART2.md (Part 2)
   ↓
5. Chạy scripts/test_db_connection.py
   ↓
6. Deploy thành công! 🎉
```

---

## ⚡ **QUICK START (5 PHÚT):**

### **Trên máy local (Database):**
```powershell
# 1. Mở SQL Server Configuration Manager
#    Enable TCP/IP

# 2. Mở Firewall
New-NetFirewallRule -DisplayName "SQL Server" `
  -Direction Inbound -Protocol TCP -LocalPort 1433 -Action Allow

# 3. Tạo SQL Login
# Chạy trong SSMS:
CREATE LOGIN phongtro_app_user WITH PASSWORD = 'StrongP@ssw0rd!2024';
```

### **Trên máy ảo (Code):**
```bash
# 1. Clone code
git clone https://github.com/phuonglatoi/phongtro-attt.git
cd phongtro-attt

# 2. Tạo .env
cp .env.example .env
nano .env  # Điền thông tin
chmod 600 .env

# 3. Setup SSH Tunnel (Optional)
bash scripts/setup_ssh_tunnel.sh

# 4. Test connection
python scripts/test_db_connection.py

# 5. Deploy
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

---

## 🔐 **NGUYÊN TẮC VÀNG:**

### **✅ LUÔN LUÔN:**
- Dùng `.env` file cho thông tin nhạy cảm
- Thêm `.env` vào `.gitignore`
- Mã hóa kết nối (SSH Tunnel/VPN)
- Phân quyền file `.env` (chmod 600)
- Dùng password mạnh (12+ ký tự)

### **❌ KHÔNG BAO GIỜ:**
- Commit `.env` lên Git
- Hardcode password trong code
- Dùng `DEBUG=True` trong production
- Dùng `sa` account cho ứng dụng
- Mở port 1433 ra Internet công khai

---

## 📊 **KIẾN TRÚC:**

```
🌐 Internet
   ↓
☁️ Máy ảo (VM)
   ├── Nginx (Port 80/443)
   ├── Gunicorn (Django)
   ├── .env (KHÔNG commit Git)
   └── Code (Clone từ GitHub)
   ↓
🔐 SSH Tunnel / VPN (Mã hóa)
   ↓
🏠 Máy local
   ├── SQL Server (Port 1433)
   └── Firewall (Chỉ cho phép IP VM)
```

---

## 🆘 **TROUBLESHOOTING:**

### **Lỗi: Cannot connect to database**
```bash
# Kiểm tra:
1. SQL Server đã chạy chưa?
2. Firewall có mở port 1433 không?
3. Thông tin trong .env đúng chưa?
4. SSH tunnel đã chạy chưa? (ps aux | grep ssh)
```

### **Lỗi: No module named 'pyodbc'**
```bash
pip install pyodbc
```

### **Lỗi: ODBC Driver not found**
```bash
# Ubuntu/Debian:
curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
sudo ACCEPT_EULA=Y apt-get install -y msodbcsql18
```

---

## 📞 **HỖ TRỢ:**

### **Tài liệu tham khảo:**
- Django Security: https://docs.djangoproject.com/en/stable/topics/security/
- SQL Server Security: https://learn.microsoft.com/en-us/sql/relational-databases/security/
- SSH Tunneling: https://www.ssh.com/academy/ssh/tunneling

### **Tools:**
- Tailscale VPN: https://tailscale.com/
- WireGuard VPN: https://www.wireguard.com/
- Let's Encrypt SSL: https://letsencrypt.org/

---

## ✅ **CHECKLIST HOÀN THÀNH:**

- [ ] Đã đọc TOM_TAT_DEPLOY_AN_TOAN.md
- [ ] Đã setup SQL Server cho remote access
- [ ] Đã tạo `.env` file (KHÔNG commit)
- [ ] Đã setup SSH Tunnel hoặc VPN
- [ ] Đã test kết nối database thành công
- [ ] Đã deploy code lên máy ảo
- [ ] Đã chạy migrations
- [ ] Đã test website hoạt động
- [ ] `DEBUG=False` trong production
- [ ] Đã setup SSL/TLS (HTTPS)

---

**🎉 Chúc bạn deploy thành công!**

Nếu có vấn đề, hãy đọc lại tài liệu hoặc chạy `scripts/test_db_connection.py` để troubleshoot.

