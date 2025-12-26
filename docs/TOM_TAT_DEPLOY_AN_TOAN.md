# 📝 TÓM TẮT: DEPLOY AN TOÀN

## ❓ **VẤN ĐỀ:**
> "Database ở máy local, code clone từ GitHub về máy ảo. Làm sao bảo mật thông tin kết nối?"

---

## ✅ **GIẢI PHÁP 3 BƯỚC:**

### **1️⃣ TÁCH THÔNG TIN NHẠY CẢM RA KHỎI CODE**

```
❌ SAI:
├── settings.py  (chứa password hardcode)
└── git push     (lộ password lên GitHub!)

✅ ĐÚNG:
├── settings.py  (đọc từ .env)
├── .env         (KHÔNG commit)
├── .env.example (template, commit được)
└── .gitignore   (chặn .env)
```

**File `.env` (CHỈ trên máy ảo):**
```ini
DB_HOST=192.168.1.100
DB_PASSWORD=StrongP@ssw0rd!2024
SECRET_KEY=random-50-chars
```

**File `.gitignore`:**
```
.env
*.log
media/
```

---

### **2️⃣ BẢO MẬT KẾT NỐI DATABASE**

#### **Option A: SSH Tunnel (KHUYẾN NGHỊ - Miễn phí)**
```bash
# Trên máy ảo
ssh -L 1433:localhost:1433 user@192.168.1.100 -N -f

# Trong .env
DB_HOST=localhost  # ← Kết nối qua tunnel
```

**Lợi ích:**
- ✅ Mã hóa AES-256
- ✅ Không cần VPN
- ✅ Miễn phí
- ✅ Dễ setup

#### **Option B: Tailscale VPN (DỄ NHẤT)**
```bash
# Cài trên cả 2 máy
curl -fsSL https://tailscale.com/install.sh | sh
tailscale up

# Dùng IP Tailscale trong .env
DB_HOST=100.x.x.x  # IP Tailscale
```

#### **Option C: Firewall + Strong Password (TỐI THIỂU)**
```powershell
# Trên máy local
New-NetFirewallRule -DisplayName "SQL Server" `
  -Direction Inbound -Protocol TCP -LocalPort 1433 `
  -RemoteAddress 203.x.x.x -Action Allow  # ← Chỉ IP máy ảo
```

---

### **3️⃣ PHÂN QUYỀN FILE `.env`**

```bash
# Trên máy ảo
chmod 600 .env
chown your-user:your-user .env

# Kiểm tra
ls -la .env
# -rw------- 1 user user 1234 Dec 26 .env
#  ↑ Chỉ owner đọc được
```

---

## 🔐 **5 LỚP BẢO MẬT:**

| Lớp | Công nghệ | Chức năng |
|-----|-----------|-----------|
| **1. Network** | Firewall, VPN | Chặn IP lạ |
| **2. Transport** | SSH Tunnel, TLS | Mã hóa dữ liệu |
| **3. Authentication** | SQL Login + Password | Xác thực |
| **4. Application** | `.env` file | Tách code/config |
| **5. File System** | `chmod 600` | Phân quyền |

---

## 📋 **CHECKLIST TRƯỚC KHI DEPLOY:**

### **Trên GitHub:**
- [ ] `.env` KHÔNG có trong repo
- [ ] `.gitignore` đã có `.env`
- [ ] Không hardcode password
- [ ] Chỉ commit `.env.example`

### **Trên máy ảo:**
- [ ] Tạo `.env` từ `.env.example`
- [ ] `chmod 600 .env`
- [ ] Test kết nối database
- [ ] `DEBUG=False` trong production

### **Trên máy local:**
- [ ] SQL Server enable TCP/IP
- [ ] Firewall mở port 1433
- [ ] Tạo SQL Login (không dùng `sa`)
- [ ] Firewall chỉ cho phép IP máy ảo

---

## 🚀 **HƯỚNG DẪN NHANH:**

### **Bước 1: Clone code**
```bash
git clone https://github.com/phuonglatoi/phongtro-attt.git
cd phongtro-attt
```

### **Bước 2: Tạo `.env`**
```bash
cp .env.example .env
nano .env  # Điền thông tin thật
chmod 600 .env
```

### **Bước 3: Setup SSH Tunnel (Optional)**
```bash
bash scripts/setup_ssh_tunnel.sh
# Nhập IP máy local và SSH user
```

### **Bước 4: Cài đặt và chạy**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

---

## 📊 **SO SÁNH CÁC PHƯƠNG ÁN:**

| Phương án | An toàn | Dễ dùng | Chi phí | Khuyến nghị |
|-----------|---------|---------|---------|-------------|
| **SSH Tunnel** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | Miễn phí | ✅ Tốt nhất |
| **Tailscale VPN** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Miễn phí | ✅ Dễ nhất |
| **Firewall Only** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Miễn phí | ⚠️ Tối thiểu |
| **Azure SQL** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Tốn phí | 💰 Production |

---

## 🎯 **KẾT LUẬN:**

### **Nguyên tắc vàng:**
1. **KHÔNG BAO GIỜ** commit `.env` lên Git
2. **LUÔN LUÔN** dùng `.env.example` làm template
3. **BẮT BUỘC** mã hóa kết nối (SSH/VPN)
4. **NÊN** giới hạn IP bằng Firewall
5. **PHẢI** phân quyền file `.env` (chmod 600)

### **Lợi ích:**
✅ Thông tin nhạy cảm KHÔNG lộ trên GitHub  
✅ Mỗi môi trường có config riêng  
✅ Dễ dàng thay đổi password  
✅ Tuân thủ best practices  
✅ An toàn cho đồ án và production  

---

## 📚 **TÀI LIỆU CHI TIẾT:**

- **Part 1:** `docs/HUONG_DAN_DEPLOY_AN_TOAN.md` - Bảo mật Database
- **Part 2:** `docs/HUONG_DAN_DEPLOY_AN_TOAN_PART2.md` - Deploy Code
- **Script:** `scripts/setup_ssh_tunnel.sh` - Tự động setup SSH Tunnel

---

## 💡 **CÂU HỎI THƯỜNG GẶP:**

### **Q: Nếu tôi đổi password DB thì sao?**
A: Chỉ cần sửa file `.env` trên máy ảo, không cần commit gì cả!

### **Q: Làm sao đồng đội biết config gì?**
A: Xem file `.env.example` - có tất cả các biến cần thiết (nhưng không có giá trị thật)

### **Q: Production thực tế dùng gì?**
A: AWS Secrets Manager, Azure Key Vault, hoặc HashiCorp Vault

### **Q: SSH Tunnel có chậm không?**
A: Không đáng kể. Overhead < 5% so với kết nối trực tiếp.

---

**🔒 Bây giờ bạn có thể deploy an toàn mà không lo lộ thông tin!**

