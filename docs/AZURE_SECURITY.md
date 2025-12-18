# 🔐 Azure Security Features - PhongTro.vn

## 📋 Tổng quan Bảo mật Azure

Tài liệu này mô tả các tính năng bảo mật tích hợp sẵn của Azure cho PhongTro.vn.

---

## 1. 🔒 Encryption at Rest (Mã hóa dữ liệu lưu trữ)

### Azure SQL Database - Transparent Data Encryption (TDE)

| Tính năng | Chi tiết |
|-----------|----------|
| **Thuật toán** | AES-256 |
| **Trạng thái** | ✅ Bật mặc định |
| **Key Management** | Microsoft-managed hoặc Customer-managed (BYOK) |
| **Phạm vi** | Toàn bộ database, backups, transaction logs |

**Cách kiểm tra TDE đang bật:**
```sql
SELECT db.name, 
       db.is_encrypted,
       dm.encryption_state
FROM sys.databases db
LEFT JOIN sys.dm_database_encryption_keys dm 
ON db.database_id = dm.database_id;
```

### Azure App Service - Storage Encryption

- ✅ **Tự động**: Tất cả files được mã hóa với AES-256
- ✅ **Không cần cấu hình**: Hoạt động ngay khi tạo App Service
- ✅ **Bao gồm**: Source code, logs, temp files

### Azure Blob Storage (Media Files)

- ✅ **Storage Service Encryption (SSE)**: Tự động mã hóa
- ✅ **Thuật toán**: AES-256
- ✅ **Options**: Microsoft-managed keys hoặc Customer-managed keys

---

## 2. 🔄 Encryption in Transit (Mã hóa dữ liệu truyền tải)

### HTTPS/TLS cho App Service

| Tính năng | Chi tiết |
|-----------|----------|
| **SSL Certificate** | ✅ Miễn phí (*.azurewebsites.net) |
| **Custom Domain SSL** | Miễn phí với App Service Managed Certificate |
| **TLS Version** | TLS 1.2+ (có thể enforce) |
| **HTTPS Only** | Bật trong cấu hình để redirect HTTP → HTTPS |

**Cách bật HTTPS Only:**
1. Azure Portal → App Service → **TLS/SSL settings**
2. Set **HTTPS Only** = **On**
3. Set **Minimum TLS Version** = **1.2**

### SQL Server Connection Encryption

- ✅ **TLS 1.2** được enforce mặc định
- ✅ **Encrypt=yes** trong connection string
- ✅ **Certificate validation** tự động

**Connection String mẫu:**
```
Server=your-server.database.windows.net;Database=PhongTroATTT;User Id=user;Password=pass;Encrypt=yes;TrustServerCertificate=no;
```

---

## 3. 💾 Automated Backups (Sao lưu tự động)

### Azure SQL Database Backups

| Tier | Point-in-Time | Long-term | Geo-redundant |
|------|---------------|-----------|---------------|
| Basic | 7 ngày | ❌ | ❌ |
| Standard | 35 ngày | ✅ (10 năm) | ✅ Optional |
| Premium | 35 ngày | ✅ (10 năm) | ✅ Optional |

**Tính năng:**
- ✅ **Automatic**: Không cần cấu hình
- ✅ **Point-in-Time Restore**: Khôi phục đến bất kỳ thời điểm nào
- ✅ **Geo-restore**: Khôi phục từ backup ở region khác
- ✅ **RPO**: < 5 phút (Recovery Point Objective)

**Khôi phục database:**
1. Azure Portal → SQL Database → **Restore**
2. Chọn thời điểm cần restore
3. Nhập tên database mới
4. Click **Create**

### Azure App Service Backups

| Tier | Automatic Backup | Manual Backup | Max Storage |
|------|-----------------|---------------|-------------|
| Free/Basic | ❌ | ✅ (limited) | N/A |
| Standard | ✅ Daily | ✅ | 10 GB |
| Premium | ✅ Hourly option | ✅ | 50 GB |

**Cấu hình Backup:**
1. Azure Portal → App Service → **Backups**
2. Click **Configure**
3. Chọn Storage Account
4. Set schedule (daily recommended)
5. Include database connection (optional)

---

## 4. 📊 Application Insights (Giám sát ứng dụng)

### Tính năng chính

| Tính năng | Mô tả |
|-----------|-------|
| **Live Metrics** | Xem real-time: requests, CPU, memory |
| **Request Tracking** | Log tất cả HTTP requests |
| **Exception Tracking** | Tự động capture errors |
| **Dependency Tracking** | Monitor SQL queries, HTTP calls |
| **Custom Events** | Log business events (login, booking) |
| **Smart Detection** | AI phát hiện anomalies |
| **Alerts** | Email/SMS khi có vấn đề |

### Đã tích hợp trong PhongTro.vn

Application Insights đã được cấu hình trong `config/settings/production.py`:

```python
# Thêm biến môi trường trong Azure:
APPLICATIONINSIGHTS_CONNECTION_STRING=InstrumentationKey=xxx;...
```

### Xem Insights trong Azure Portal

1. Azure Portal → Application Insights → Your App
2. **Overview**: Tổng quan health
3. **Live Metrics**: Real-time monitoring
4. **Failures**: Xem lỗi và exceptions
5. **Performance**: Response times, slow requests
6. **Users**: Analytics về người dùng

---

## 5. 🛡️ Security Center Recommendations

### Checklist Bảo mật Azure

- [ ] **Enable Azure Defender** for SQL
- [ ] **Enable TDE** (mặc định đã bật)
- [ ] **Configure firewall rules** - chỉ cho phép App Service IP
- [ ] **Enable Auditing** for SQL Database
- [ ] **Set up Alerts** for suspicious activities
- [ ] **Enable HTTPS Only** on App Service
- [ ] **Set Minimum TLS 1.2**
- [ ] **Enable Managed Identity** (không dùng password trong code)
- [ ] **Use Key Vault** cho secrets

---

## 6. 🔑 Recommended: Managed Identity

Thay vì lưu password trong environment variables, dùng Managed Identity:

```python
# Không cần password - Azure tự xác thực
DATABASES = {
    'default': {
        'ENGINE': 'mssql',
        'NAME': 'PhongTroATTT',
        'HOST': 'server.database.windows.net',
        'OPTIONS': {
            'driver': 'ODBC Driver 18 for SQL Server',
            'extra_params': 'Authentication=ActiveDirectoryMsi;',
        },
    }
}
```

---

## 📞 Hỗ trợ

- **Azure Support**: https://azure.microsoft.com/support/
- **Documentation**: https://docs.microsoft.com/azure/
- **Security Center**: Azure Portal → Security Center

