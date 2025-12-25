# 👥 PHÂN CHIA NHIỆM VỤ NHÓM 3 NGƯỜI
## ⚡ PHƯƠNG ÁN: MỖI NGƯỜI MỘT MODULE HOÀN CHỈNH

---

## 👤 **NGƯỜI 1: MODULE QUẢN LÝ TÀI KHOẢN (ACCOUNTS)**

### 🎯 Chịu trách nhiệm toàn bộ:
**App:** `apps/accounts/` - Hệ thống tài khoản & bảo mật

### � Deliverables:

#### 1. Database (SQL Server)
```sql
✅ Bảng TAIKHOAN (username, password_hash, password_salt, 2FA...)
✅ Bảng KHACHHANG (thông tin cá nhân)
✅ Bảng VAITRO (Admin, Chủ trọ, Khách hàng)
✅ Bảng LOGIN_HISTORY (lịch sử đăng nhập)
✅ Bảng FAILED_LOGIN_ATTEMPTS (theo dõi đăng nhập sai)
✅ Bảng SECURITY_LOGS (logs bảo mật)
```

#### 2. Backend (Django)
```python
✅ apps/accounts/models.py - Models cho tài khoản
✅ apps/accounts/views.py - Login, Register, Logout, Profile, 2FA
✅ apps/accounts/forms.py - Forms validation
✅ apps/accounts/security.py - Password hashing, 2FA, rate limiting
✅ apps/accounts/decorators.py - @login_required, @admin_required
✅ apps/accounts/urls.py - URL routing
```

#### 3. Frontend (Templates)
```html
✅ templates/accounts/login.html
✅ templates/accounts/register.html
✅ templates/accounts/profile.html
✅ templates/accounts/password_change.html
✅ templates/accounts/setup_2fa.html
✅ templates/accounts/manage_devices.html
```

#### 4. Tính năng bảo mật
```
✅ Password hashing (SHA256 + Salt)
✅ 2FA (TOTP)
✅ Account lockout (5 lần sai)
✅ Rate limiting (5 login/phút)
✅ Session security (timeout 15 phút)
✅ Login history tracking
✅ Security logs
```

**📊 Workload:** 35% | **⏱️ Thời gian:** 3 tuần

---

## 👤 **NGƯỜI 2: MODULE QUẢN LÝ PHÒNG TRỌ (ROOMS)**

### 🎯 Chịu trách nhiệm toàn bộ:
**App:** `apps/rooms/` - Hệ thống phòng trọ & nhà trọ

### 📦 Deliverables:

#### 1. Database (SQL Server)
```sql
✅ Bảng NHATRO (thông tin nhà trọ)
✅ Bảng PHONGTRO (thông tin phòng)
✅ Bảng HINHANH (ảnh phòng)
✅ Bảng TIENICH (tiện ích)
✅ Bảng PHONGTRO_TIENICH (many-to-many)
✅ Stored Procedures (SP_SEARCH_ROOMS, SP_GET_ROOM_DETAILS...)
```

#### 2. Backend (Django)
```python
✅ apps/rooms/models.py - Models cho phòng trọ
✅ apps/rooms/views.py - Trang chủ, chi tiết phòng, search, filter
✅ apps/rooms/forms.py - Form thêm/sửa phòng
✅ apps/rooms/utils.py - Upload ảnh, resize, validation
✅ apps/rooms/urls.py - URL routing
```

#### 3. Frontend (Templates)
```html
✅ templates/rooms/home.html - Trang chủ (danh sách phòng)
✅ templates/rooms/room_detail.html - Chi tiết phòng
✅ templates/rooms/search_results.html - Kết quả tìm kiếm
✅ templates/rooms/add_room.html - Thêm phòng (Chủ trọ)
✅ templates/rooms/edit_room.html - Sửa phòng
✅ templates/rooms/my_rooms.html - Phòng của tôi
```

#### 4. Tính năng chính
```
✅ Hiển thị danh sách phòng (pagination)
✅ Tìm kiếm & filter (giá, diện tích, quận...)
✅ Upload ảnh phòng (max 5MB, validate MIME type)
✅ CRUD phòng trọ (Chủ trọ)
✅ Duyệt phòng (Admin)
✅ Responsive design (mobile-friendly)
```

**📊 Workload:** 35% | **⏱️ Thời gian:** 3 tuần

---

## 👤 **NGƯỜI 3: MODULE ĐẶT LỊCH & QUẢN TRỊ (BOOKINGS + ADMIN)**

### 🎯 Chịu trách nhiệm toàn bộ:
**App:** `apps/bookings/` - Hệ thống đặt lịch & admin dashboard

### � Deliverables:

#### 1. Database (SQL Server)
```sql
✅ Bảng HENXEMTRO (lịch hẹn xem phòng)
✅ Bảng YCLAMCHUTRO (yêu cầu làm chủ trọ)
✅ Bảng AUDIT_LOGS (audit trail)
✅ Triggers (TRG_AUDIT_TAIKHOAN, TRG_AUDIT_PHONGTRO...)
✅ Backup Scripts (full, differential, log backup)
```

#### 2. Backend (Django)
```python
✅ apps/bookings/models.py - Models cho booking
✅ apps/bookings/views.py - Booking, Admin dashboard, Landlord dashboard
✅ apps/bookings/forms.py - Form đặt lịch, duyệt yêu cầu
✅ apps/bookings/middleware.py - Audit middleware
✅ apps/bookings/urls.py - URL routing
```

#### 3. Frontend (Templates)
```html
✅ templates/bookings/admin_dashboard.html - Dashboard Admin
✅ templates/bookings/landlord_dashboard.html - Dashboard Chủ trọ
✅ templates/bookings/customer_dashboard.html - Dashboard Khách hàng
✅ templates/bookings/my_bookings.html - Lịch hẹn của tôi
✅ templates/bookings/manage_customers.html - Quản lý người dùng (Admin)
✅ templates/bookings/approve_rooms.html - Duyệt phòng (Admin)
```

#### 4. Tính năng chính
```
✅ Đặt lịch xem phòng
✅ Xác nhận/Từ chối lịch hẹn (Chủ trọ)
✅ Admin Dashboard (thống kê, duyệt phòng, quản lý user)
✅ Landlord Dashboard (quản lý nhà trọ, lịch hẹn)
✅ Customer Dashboard (lịch hẹn của tôi)
✅ Audit logs (theo dõi mọi thay đổi)
✅ Database backup automation
```

**📊 Workload:** 30% | **⏱️ Thời gian:** 2.5 tuần

---

## � PHỐI HỢP GIỮA CÁC MODULE

### Giao diện chung (Cả nhóm cùng làm):
```
✅ templates/base.html - Layout chung (navbar, footer)
✅ static/css/style.css - CSS chung
✅ static/js/main.js - JavaScript chung
✅ config/settings.py - Django settings
✅ config/urls.py - URL routing chính
```

### Dependencies:
- **Người 2 & 3** cần **Người 1** hoàn thành authentication trước
- **Người 3** cần **Người 2** hoàn thành models phòng trọ trước
- Tất cả cùng làm **base template** trong tuần 1

---

## � TIMELINE (8 TUẦN)

### **Tuần 1: Setup chung**
- **Cả nhóm:**
  - Setup project Django
  - Tạo base template, static files
  - Database connection
  - Git repository setup

### **Tuần 2-4: Development song song**
- **Người 1:** Hoàn thành module Accounts (100%)
- **Người 2:** Hoàn thành module Rooms (100%)
- **Người 3:** Hoàn thành module Bookings (100%)

### **Tuần 5-6: Integration & Testing**
- **Cả nhóm:**
  - Tích hợp 3 modules
  - Testing (unit tests, integration tests)
  - Bug fixing
  - Security testing

### **Tuần 7: Polish & Optimization**
- **Người 1:** Security hardening, performance tuning
- **Người 2:** UI/UX polish, responsive design
- **Người 3:** Admin features, backup testing

### **Tuần 8: Documentation & Deployment**
- **Cả nhóm:**
  - Viết báo cáo (mỗi người viết phần của mình)
  - Tài liệu hướng dẫn sử dụng
  - Chuẩn bị demo
  - Deployment (nếu cần)

---

## � PHỐI HỢP CÔNG VIỆC

### Git Workflow:
```bash
main (production)
├── dev (development)
    ├── feature/accounts (Người 1)
    ├── feature/rooms (Người 2)
    └── feature/bookings (Người 3)
```

### Daily Standup (15 phút/ngày):
- **Người 1:** Update accounts module progress
- **Người 2:** Update rooms module progress
- **Người 3:** Update bookings module progress
- **Blockers:** Ai cần gì từ ai?

### Code Review:
- Mỗi người review code của người khác
- Merge vào `dev` sau khi 2/3 approve
- Merge `dev` → `main` khi sprint hoàn thành

---

## 📊 BẢNG PHÂN CHIA CHI TIẾT

| Module | Người | Database | Backend | Frontend | Workload |
|--------|-------|----------|---------|----------|----------|
| **Accounts** | Người 1 | 6 bảng | 7 files | 6 templates | 35% |
| **Rooms** | Người 2 | 5 bảng | 5 files | 6 templates | 35% |
| **Bookings** | Người 3 | 4 bảng | 5 files | 6 templates | 30% |

---

## ✅ CHECKLIST HOÀN THÀNH

### 👤 Người 1 - Module ACCOUNTS:
- [ ] Database: 6 bảng (TAIKHOAN, KHACHHANG, VAITRO, LOGIN_HISTORY, FAILED_LOGIN_ATTEMPTS, SECURITY_LOGS)
- [ ] Backend: Login, Register, Logout, Profile, 2FA, Password Change
- [ ] Frontend: 6 templates (login, register, profile, 2fa, devices, password_change)
- [ ] Security: Password hashing, 2FA, Account lockout, Rate limiting, Session security
- [ ] Testing: Unit tests cho authentication
- [ ] Documentation: API docs cho accounts module

### 👤 Người 2 - Module ROOMS:
- [ ] Database: 5 bảng (NHATRO, PHONGTRO, HINHANH, TIENICH, PHONGTRO_TIENICH)
- [ ] Backend: CRUD phòng, Search, Filter, Upload ảnh
- [ ] Frontend: 6 templates (home, room_detail, search, add_room, edit_room, my_rooms)
- [ ] Features: Pagination, Image upload validation, Responsive design
- [ ] Testing: Unit tests cho rooms CRUD
- [ ] Documentation: User guide cho quản lý phòng

### 👤 Người 3 - Module BOOKINGS:
- [ ] Database: 4 bảng (HENXEMTRO, YCLAMCHUTRO, AUDIT_LOGS) + Triggers + Backup scripts
- [ ] Backend: Booking system, Admin dashboard, Landlord dashboard, Audit middleware
- [ ] Frontend: 6 templates (3 dashboards, my_bookings, manage_customers, approve_rooms)
- [ ] Features: Đặt lịch, Duyệt yêu cầu, Thống kê, Audit logs, Backup automation
- [ ] Testing: Integration tests cho booking flow
- [ ] Documentation: Admin guide

---

## 📝 PHÂN CHIA VIẾT BÁO CÁO

### Người 1 - Viết phần:
```
✅ Chương 2: Cơ sở lý thuyết
   - 2.1. Bảo mật web application
   - 2.2. Authentication & Authorization
   - 2.3. OWASP Top 10

✅ Chương 3: Phân tích & Thiết kế
   - 3.1. Database schema (6 bảng của mình)
   - 3.2. Authentication flow

✅ Chương 4: Triển khai
   - 4.1. Module Accounts (chi tiết)
   - 4.2. Security implementation (2FA, password hashing...)
```

### Người 2 - Viết phần:
```
✅ Chương 1: Tổng quan
   - 1.1. Giới thiệu đề tài
   - 1.2. Mục tiêu
   - 1.3. Phạm vi

✅ Chương 3: Phân tích & Thiết kế
   - 3.3. Database schema (5 bảng của mình)
   - 3.4. UI/UX design

✅ Chương 4: Triển khai
   - 4.3. Module Rooms (chi tiết)
   - 4.4. Frontend implementation
```

### Người 3 - Viết phần:
```
✅ Chương 3: Phân tích & Thiết kế
   - 3.5. Database schema (4 bảng của mình)
   - 3.6. System architecture

✅ Chương 4: Triển khai
   - 4.5. Module Bookings (chi tiết)
   - 4.6. Admin dashboard
   - 4.7. Backup & Recovery

✅ Chương 5: Kết quả & Đánh giá
   - 5.1. Kết quả đạt được
   - 5.2. Đánh giá bảo mật
   - 5.3. Hướng phát triển
```

---

## � LỢI ÍCH CỦA PHƯƠNG ÁN NÀY

### ✅ Ưu điểm:
1. **Độc lập cao:** Mỗi người làm module riêng, ít conflict
2. **Trách nhiệm rõ ràng:** Ai làm gì, ai chịu trách nhiệm gì
3. **Dễ quản lý:** Mỗi module có timeline riêng
4. **Dễ debug:** Lỗi ở module nào thì người đó fix
5. **Công bằng:** Workload cân bằng (35%-35%-30%)

### ⚠️ Lưu ý:
1. **Tuần 1 quan trọng:** Phải setup chung base template, database connection
2. **Communication:** Daily standup để sync progress
3. **Dependencies:** Người 2 & 3 cần Người 1 làm xong authentication trước
4. **Integration:** Tuần 5-6 cần test kỹ tích hợp giữa các module

---

## 🎓 KẾT QUẢ MONG ĐỢI

✅ **3 modules hoàn chỉnh, độc lập**
✅ **Mỗi người master 1 domain riêng**
✅ **Dễ demo:** Mỗi người demo phần của mình
✅ **Dễ bảo vệ:** Mỗi người trả lời câu hỏi về module của mình
✅ **Điểm cao:** Hệ thống hoàn chỉnh với 18 tính năng bảo mật! 🎉

---

## 📞 CONTACT & SUPPORT

**Khi gặp vấn đề:**
- **Người 1 (Accounts):** Hỏi về authentication, security, database users
- **Người 2 (Rooms):** Hỏi về UI/UX, phòng trọ, upload ảnh
- **Người 3 (Bookings):** Hỏi về booking, admin, backup

**Họp nhóm:** 2 lần/tuần (Thứ 3 & Thứ 6)
**Code review:** Mỗi pull request
**Testing:** Trước khi merge vào `dev`

---

**🚀 Chúc nhóm thành công!**
## Dự án: PhongTroATTT - Hệ thống Quản lý Phòng trọ với Bảo mật nâng cao

---

## 📋 TỔNG QUAN PHÂN CÔNG

### 🎯 Nguyên tắc phân chia:
1. **Cân bằng khối lượng công việc** (~33% mỗi người)
2. **Phân chia theo chuyên môn** (Frontend, Backend, Database/Security)
3. **Có sự phối hợp** giữa các thành viên
4. **Milestone rõ ràng** để theo dõi tiến độ

---

## 👤 THÀNH VIÊN 1: DATABASE & BACKEND CORE
**Vai trò:** Database Architect + Backend Developer  
**Khối lượng:** ~35% dự án  
**Thời gian:** 4-5 tuần

### 📦 Nhiệm vụ chính:

#### **1. Thiết kế & Triển khai Database (Tuần 1-2)**
- ✅ Thiết kế ERD (Entity Relationship Diagram)
- ✅ Tạo database schema (18 bảng)
- ✅ Viết stored procedures:
  - `SP_LOGIN` - Xác thực đăng nhập
  - `SP_REGISTER` - Đăng ký tài khoản
  - `SP_SEARCH_ROOMS` - Tìm kiếm phòng
  - `SP_CLEANUP_OLD_LOGS` - Dọn dẹp logs
- ✅ Tạo triggers cho audit logging:
  - `TRG_AUDIT_TAIKHOAN`
  - `TRG_AUDIT_PHONGTRO`
  - `TRG_AUDIT_KHACHHANG`
- ✅ Tạo indexes cho performance
- ✅ Setup constraints (FK, CHECK, UNIQUE)

**Files:**
```
scripts/
├── database_schema.sql
├── stored_procedures.sql
├── triggers.sql
├── indexes.sql
└── sample_data.sql
```

#### **2. Django Models & ORM (Tuần 2-3)**
- ✅ Tạo models cho tất cả bảng:
  - `apps/accounts/models.py` (Taikhoan, Khachhang, Vaitro)
  - `apps/rooms/models.py` (Phongtro, Nhatro, Hinhanh)
  - `apps/bookings/models.py` (Henxemtro, Yclamchutro)
  - `apps/security/models.py` (SecurityLog, AuditLog)
- ✅ Viết migrations
- ✅ Test database connections
- ✅ Seed data (tạo dữ liệu mẫu)

#### **3. Backend Core APIs (Tuần 3-4)**
- ✅ Authentication APIs:
  - Login/Logout
  - Register
  - Password reset
- ✅ Room Management APIs:
  - CRUD phòng trọ
  - Search & Filter
  - Upload images
- ✅ Booking APIs:
  - Tạo lịch hẹn
  - Xác nhận/Từ chối

**Files:**
```
apps/accounts/views.py
apps/rooms/views.py
apps/bookings/views.py
```

#### **4. Testing & Documentation (Tuần 4-5)**
- ✅ Viết unit tests cho models
- ✅ Test stored procedures
- ✅ Viết API documentation
- ✅ Database documentation

**Deliverables:**
- ✅ Database hoàn chỉnh với 18 bảng
- ✅ 15+ stored procedures
- ✅ 10+ triggers
- ✅ Django models đầy đủ
- ✅ Core APIs hoạt động

---

## 👤 THÀNH VIÊN 2: SECURITY & AUTHENTICATION
**Vai trò:** Security Engineer + Backend Developer  
**Khối lượng:** ~35% dự án  
**Thời gian:** 4-5 tuần

### 🔐 Nhiệm vụ chính:

#### **1. Authentication & Authorization (Tuần 1-2)**
- ✅ Implement password hashing (SHA256 + Salt)
- ✅ Session management
- ✅ 2FA (Two-Factor Authentication) với TOTP:
  - Setup QR code generation
  - Verify OTP
  - Backup codes
- ✅ OAuth 2.0 (Google Login)
- ✅ RBAC (Role-Based Access Control):
  - Admin decorator
  - Landlord decorator
  - Customer decorator

**Files:**
```
apps/accounts/
├── security.py          # Password hashing, 2FA
├── decorators.py        # RBAC decorators
├── forms.py             # Login, Register forms
└── views.py             # Auth views
```

#### **2. Security Features (Tuần 2-3)**
- ✅ Rate Limiting (django-ratelimit):
  - Login: 5 attempts/minute
  - Register: 3 attempts/minute
  - API: 100 requests/hour
- ✅ Account Lockout:
  - Lock sau 5 lần đăng nhập sai
  - Auto unlock sau 15 phút
- ✅ IP Filtering & Blocking:
  - Whitelist/Blacklist
  - Auto-block suspicious IPs
- ✅ WAF (Web Application Firewall):
  - Detect SQL Injection
  - Detect XSS
  - Detect Path Traversal

**Files:**
```
apps/security/
├── middleware/
│   ├── ip_filter.py
│   ├── waf.py
│   └── rate_limit.py
├── models.py            # SecurityLog, BlockedIP
└── utils.py
```

#### **3. Security Logging & Monitoring (Tuần 3-4)**
- ✅ Security Event Logging:
  - Login success/failure
  - Password changes
  - 2FA events
  - WAF blocks
  - IP blocks
- ✅ Audit Logging:
  - Database triggers
  - Middleware audit
  - Track all changes
- ✅ Login History:
  - IP address
  - User agent parsing
  - Device tracking
  - Browser/OS detection

**Files:**
```
apps/security/models.py
apps/accounts/models.py (LoginHistory, FailedLoginAttempts)
scripts/audit_triggers.sql
```

#### **4. Security Testing & Hardening (Tuần 4-5)**
- ✅ Penetration testing:
  - SQL Injection tests
  - XSS tests
  - CSRF tests
  - Session hijacking tests
- ✅ Security headers:
  - HSTS
  - CSP
  - X-Frame-Options
  - X-Content-Type-Options
- ✅ HTTPS/TLS configuration
- ✅ Security documentation

**Deliverables:**
- ✅ 2FA hoàn chỉnh
- ✅ WAF chặn được SQL Injection, XSS
- ✅ Rate limiting hoạt động
- ✅ Security logs đầy đủ
- ✅ Penetration test report

---

## 👤 THÀNH VIÊN 3: FRONTEND & UI/UX
**Vai trò:** Frontend Developer + UI/UX Designer  
**Khối lượng:** ~30% dự án  
**Thời gian:** 4-5 tuần

### 🎨 Nhiệm vụ chính:

#### **1. UI/UX Design & Base Templates (Tuần 1-2)**
- ✅ Thiết kế wireframes/mockups
- ✅ Chọn color scheme & typography
- ✅ Tạo base templates:
  - `base.html` - Template chính
  - `base_admin.html` - Template admin
  - Navigation bar
  - Footer
  - Sidebar
- ✅ Setup CSS framework (Bootstrap 5)
- ✅ Custom CSS cho branding

**Files:**
```
templates/
├── base.html
├── base_admin.html
└── includes/
    ├── navbar.html
    ├── footer.html
    └── sidebar.html

static/
├── css/
│   ├── style.css
│   └── admin.css
└── js/
    └── main.js
```

#### **2. User-facing Pages (Tuần 2-3)**
- ✅ **Homepage:**
  - Hero section
  - Search bar
  - Featured rooms
  - Statistics
- ✅ **Authentication Pages:**
  - Login (với 2FA)
  - Register
  - Password reset
  - 2FA setup
- ✅ **Room Pages:**
  - Room listing (grid/list view)
  - Room detail
  - Search & filters
  - Map integration
- ✅ **User Profile:**
  - Profile view
  - Edit profile
  - Change password
  - Manage devices
  - Login history

**Files:**
```
templates/
├── home.html
├── accounts/
│   ├── login.html
│   ├── register.html
│   ├── profile.html
│   └── setup_2fa.html
└── rooms/
    ├── room_list.html
    ├── room_detail.html
    └── search.html
```


