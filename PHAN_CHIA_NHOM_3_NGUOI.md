# 👥 PHÂN CHIA NHÓM 3 NGƯỜI - NGẮN GỌN

## ⚡ MỖI NGƯỜI MỘT MODULE HOÀN CHỈNH

---

## 👤 **NGƯỜI 1: ACCOUNTS (Tài khoản & Bảo mật)**

### Database:
- TAIKHOAN, KHACHHANG, VAITRO, LOGIN_HISTORY, FAILED_LOGIN_ATTEMPTS, SECURITY_LOGS

### Backend:
- `apps/accounts/` - Login, Register, Logout, Profile, 2FA, Password Change

### Frontend:
- login.html, register.html, profile.html, setup_2fa.html, password_change.html

### Tính năng:
- Password hashing (SHA256 + Salt)
- 2FA (TOTP)
- Account lockout (5 lần sai)
- Rate limiting (5 login/phút)
- Session timeout (15 phút)

**Workload: 35% | Thời gian: 3 tuần**

---

## 👤 **NGƯỜI 2: ROOMS (Phòng trọ)**

### Database:
- NHATRO, PHONGTRO, HINHANH, TIENICH, PHONGTRO_TIENICH

### Backend:
- `apps/rooms/` - CRUD phòng, Search, Filter, Upload ảnh

### Frontend:
- home.html, room_detail.html, search_results.html, add_room.html, edit_room.html

### Tính năng:
- Danh sách phòng (pagination)
- Tìm kiếm & filter
- Upload ảnh (max 5MB, validate MIME)
- Responsive design

**Workload: 35% | Thời gian: 3 tuần**

---

## 👤 **NGƯỜI 3: BOOKINGS + ADMIN (Đặt lịch & Quản trị)**

### Database:
- HENXEMTRO, YCLAMCHUTRO, AUDIT_LOGS + Triggers + Backup scripts

### Backend:
- `apps/bookings/` - Booking, Admin dashboard, Landlord dashboard

### Frontend:
- admin_dashboard.html, landlord_dashboard.html, my_bookings.html, manage_customers.html

### Tính năng:
- Đặt lịch xem phòng
- Xác nhận/Từ chối lịch hẹn
- Admin dashboard (thống kê, duyệt phòng, quản lý user)
- Audit logs
- Database backup

**Workload: 30% | Thời gian: 2.5 tuần**

---

## 📅 TIMELINE (8 TUẦN)

| Tuần | Công việc |
|------|-----------|
| **1** | Setup chung: Django project, base template, database connection, Git |
| **2-4** | Mỗi người làm module của mình (100%) |
| **5-6** | Integration & Testing |
| **7** | Polish & Optimization |
| **8** | Documentation & Demo |

---

## 📝 PHÂN CHIA BÁO CÁO

| Người | Viết phần |
|-------|-----------|
| **Người 1** | Chương 2 (Lý thuyết bảo mật) + Module Accounts |
| **Người 2** | Chương 1 (Tổng quan) + Module Rooms |
| **Người 3** | Chương 5 (Kết quả) + Module Bookings + Admin |

---

## ✅ CHECKLIST

### Người 1:
- [ ] 6 bảng database
- [ ] Login/Register/2FA
- [ ] 5 templates
- [ ] Security features

### Người 2:
- [ ] 5 bảng database
- [ ] CRUD phòng + Search
- [ ] 5 templates
- [ ] Upload ảnh

### Người 3:
- [ ] 3 bảng + Triggers + Backup
- [ ] Booking system
- [ ] 3 dashboards
- [ ] Audit logs

---

## 🎯 ƯU ĐIỂM

✅ Mỗi người 1 module hoàn chỉnh (Database → Backend → Frontend)  
✅ Ít conflict code  
✅ Trách nhiệm rõ ràng  
✅ Dễ demo & bảo vệ  
✅ Workload cân bằng (35%-35%-30%)

---

## 🔄 GIT WORKFLOW

```
main
├── dev
    ├── feature/accounts (Người 1)
    ├── feature/rooms (Người 2)
    └── feature/bookings (Người 3)
```

**Daily standup:** 15 phút/ngày  
**Code review:** Mỗi pull request  
**Họp nhóm:** 2 lần/tuần

---

**🚀 Kết quả: Hệ thống hoàn chỉnh với 18 tính năng bảo mật, tuân thủ 100% OWASP Top 10!**

