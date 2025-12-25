# 💾 HƯỚNG DẪN BACKUP & RESTORE DATABASE

## 📋 TỔNG QUAN

Hệ thống backup database tự động với 3 phương pháp:
1. **Azure SQL Automatic Backups** - Tự động bởi Azure (ĐÃ CÓ SẴN)
2. **Manual Backup Scripts** - Script Python backup thủ công
3. **Celery Scheduled Backups** - Backup tự động hàng ngày

---

## 🎯 PHƯƠNG PHÁP 1: AZURE SQL AUTOMATIC BACKUPS

### Tính năng có sẵn:
- ✅ **Point-in-Time Restore**: 35 ngày
- ✅ **Long-term Retention**: 10 năm
- ✅ **Geo-redundant**: Có thể bật
- ✅ **RPO**: < 5 phút

### Khôi phục từ Azure Portal:

1. Vào **Azure Portal** → **SQL Database**
2. Chọn database → Click **Restore**
3. Chọn thời điểm cần restore
4. Nhập tên database mới
5. Click **Create**

### Khôi phục bằng Azure CLI:

```bash
az sql db restore \
  --resource-group phongtro-rg \
  --server phongtro-server \
  --name PhongTroATTT \
  --dest-name PhongTroATTT_Restored \
  --time "2025-12-24T10:00:00Z"
```

---

## 🎯 PHƯƠNG PHÁP 2: MANUAL BACKUP SCRIPTS

### A. Backup SQL Server (Local/VM)

```bash
# Chạy script backup
python scripts/backup_database.py

# Kết quả:
# - File backup: backups/PhongTroATTT_backup_20251224_140530.bak
# - Tự động cleanup backup > 30 ngày
```

### B. Backup Azure SQL Database

```bash
# Chạy script backup Azure SQL
python scripts/backup_azure_sql.py

# Kết quả:
# - Tạo database copy: PhongTroATTT_backup_20251224_140530
# - Tự động cleanup, giữ 7 bản mới nhất
```

### Cấu hình trong `.env`:

```bash
DB_HOST=phongtro-server.database.windows.net
DB_NAME=PhongTroATTT
DB_USER=phontroadmin
DB_PASSWORD=YourStrongPassword
```

---

## 🎯 PHƯƠNG PHÁP 3: CELERY SCHEDULED BACKUPS

### Tự động backup hàng ngày:

Celery task đã được cấu hình chạy tự động:

```python
# File: config/celery.py

'backup-database-daily': {
    'task': 'backup_database_task',
    'schedule': crontab(hour=2, minute=0),  # 2:00 AM mỗi ngày
}
```

### Khởi động Celery Worker:

```bash
# Terminal 1: Celery Worker
celery -A config worker -l info

# Terminal 2: Celery Beat (Scheduler)
celery -A config beat -l info
```

### Kiểm tra task đã chạy:

```python
from apps.core.tasks import backup_database_task

# Chạy thủ công ngay lập tức
result = backup_database_task.delay()

# Kiểm tra kết quả
print(result.get())
# {'status': 'success', 'backup': '...', 'message': '...'}
```

---

## 🔄 RESTORE DATABASE

### A. Restore SQL Server (Local/VM)

```bash
# Liệt kê các backup có sẵn
python scripts/restore_database.py

# Output:
# Available backups:
# 1. PhongTroATTT_backup_20251224_140530.bak
#    Created: 2025-12-24 14:05:30
#    Size: 125.45 MB

# Restore backup mới nhất (interactive)
python scripts/restore_database.py

# Hoặc chỉ định file cụ thể
python scripts/restore_database.py backups/PhongTroATTT_backup_20251224_140530.bak
```

### B. Restore Azure SQL Database

**Cách 1: Từ Azure Portal** (Khuyến nghị)
- Sử dụng Point-in-Time Restore (xem Phương pháp 1)

**Cách 2: Từ Database Copy**
```sql
-- Rename backup database thành production
-- (Cần stop application trước)

-- 1. Drop database hiện tại (NGUY HIỂM!)
DROP DATABASE [PhongTroATTT];

-- 2. Rename backup database
ALTER DATABASE [PhongTroATTT_backup_20251224_140530]
MODIFY NAME = [PhongTroATTT];
```

---

## 📅 LỊCH BACKUP TỰ ĐỘNG

| Task | Thời gian | Mô tả |
|------|-----------|-------|
| **Database Backup** | 2:00 AM hàng ngày | Backup toàn bộ database |
| **Cleanup Old Logs** | 3:00 AM hàng ngày | Xóa log > 180 ngày |
| **Database Health Check** | Mỗi giờ | Kiểm tra kết nối & kích thước DB |
| **IP Reputation Check** | Mỗi 30 phút | Kiểm tra IP đáng ngờ |

---

## 📊 MONITORING BACKUP

### Kiểm tra backup logs:

```bash
# Xem log backup
tail -f logs/backup.log

# Hoặc trong Python
import logging
logger = logging.getLogger('backup')
```

### Kiểm tra kích thước backup:

```bash
# Linux/Mac
du -sh backups/

# Windows PowerShell
Get-ChildItem backups/ | Measure-Object -Property Length -Sum
```

### Kiểm tra backup databases (Azure SQL):

```sql
SELECT name, create_date, 
       CAST(DATABASEPROPERTYEX(name, 'Status') AS VARCHAR(20)) as status
FROM sys.databases
WHERE name LIKE '%_backup_%'
ORDER BY create_date DESC;
```

---

## ⚙️ CẤU HÌNH NÂNG CAO

### Thay đổi lịch backup:

Edit `config/celery.py`:

```python
'backup-database-daily': {
    'task': 'backup_database_task',
    'schedule': crontab(hour=2, minute=0, day_of_week='0,3,6'),  # Chủ nhật, Thứ 4, Thứ 7
}
```

### Thay đổi số lượng backup giữ lại:

Edit `scripts/backup_database.py`:

```python
# Giữ backup trong 60 ngày thay vì 30
backup_manager.cleanup_old_backups(keep_days=60)
```

Edit `scripts/backup_azure_sql.py`:

```python
# Giữ 14 bản backup thay vì 7
backup_manager.delete_old_backups(keep_count=14)
```

---

## 🚨 DISASTER RECOVERY PLAN

### Kịch bản 1: Database bị lỗi (< 35 ngày)

1. Sử dụng Azure Point-in-Time Restore
2. Restore về thời điểm trước khi lỗi
3. Kiểm tra dữ liệu
4. Chuyển application sang database mới

### Kịch bản 2: Cần restore backup thủ công

1. Chạy `python scripts/restore_database.py`
2. Chọn backup cần restore
3. Xác nhận restore
4. Restart application

### Kịch bản 3: Mất toàn bộ dữ liệu

1. Restore từ Long-term Retention (Azure)
2. Hoặc restore từ Geo-redundant backup
3. Hoặc restore từ backup copy database

---

## ✅ BEST PRACTICES

1. **Test restore định kỳ** - Ít nhất 1 tháng/lần
2. **Giữ nhiều bản backup** - Tối thiểu 7 bản
3. **Backup trước khi update** - Luôn backup trước khi deploy
4. **Monitor backup logs** - Kiểm tra log hàng ngày
5. **Geo-redundant** - Bật cho production
6. **Encrypt backups** - Azure tự động encrypt

---

## 🔧 TROUBLESHOOTING

### Lỗi: "Permission denied"
```bash
# Cấp quyền execute cho script
chmod +x scripts/backup_database.py
chmod +x scripts/restore_database.py
```

### Lỗi: "Backup failed - disk full"
```bash
# Cleanup old backups
python scripts/backup_database.py
# Hoặc xóa thủ công
rm backups/*_backup_202412*.bak
```

### Lỗi: "Cannot restore - database in use"
```bash
# Stop application trước
sudo systemctl stop phongtro

# Restore
python scripts/restore_database.py

# Start application
sudo systemctl start phongtro
```

---

**Ngày cập nhật:** 24/12/2025  
**Phiên bản:** 1.0

