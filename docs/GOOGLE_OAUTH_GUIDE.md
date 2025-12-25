# 🔐 HƯỚNG DẪN GOOGLE OAUTH LOGIN

## ✅ **ĐÃ CẤU HÌNH XONG**

Google OAuth đã được cấu hình thành công cho dự án PhongTroATTT!

---

## 📋 **THÔNG TIN CẤU HÌNH**

### **Client ID:**
```
128669403514-pdco2ivui2s5g68cah9r44pbudftva0t.apps.googleusercontent.com
```

### **Client Secret:**
```
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
```

### **Authorized JavaScript Origins:**
- `http://localhost:8000`
- `http://127.0.0.1:8000`

### **Authorized Redirect URIs:**
- `http://localhost:8000/accounts/social/google/login/callback/`
- `http://127.0.0.1:8000/accounts/social/google/login/callback/`

---

## 🚀 **CÁCH SỬ DỤNG**

### **1. Chạy Server:**

```bash
python manage.py runserver
```

### **2. Truy cập trang đăng nhập:**

```
http://localhost:8000/accounts/login/
```

### **3. Click nút "Đăng nhập với Google"**

### **4. Chọn tài khoản Google và cho phép quyền truy cập**

### **5. Tự động đăng nhập và redirect về trang chủ**

---

## 🔧 **CÁCH HOẠT ĐỘNG**

### **Luồng OAuth:**

```
[User clicks "Đăng nhập với Google"]
         ↓
[Redirect to Google OAuth]
         ↓
[User chọn tài khoản Google]
         ↓
[Google redirect về /accounts/social/google/login/callback/]
         ↓
[Django Allauth xử lý callback]
         ↓
[Tạo/Update user trong database]
         ↓
[Đăng nhập user]
         ↓
[Redirect về trang chủ]
```

---

## 📁 **CÁC FILE ĐÃ THAY ĐỔI**

### **1. `.env`**
```bash
GOOGLE_OAUTH_CLIENT_ID=128669403514-pdco2ivui2s5g68cah9r44pbudftva0t.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=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
```

### **2. `config/settings/base.py`**
- Thêm `allauth` vào `INSTALLED_APPS`
- Thêm `AUTHENTICATION_BACKENDS`
- Thêm `SOCIALACCOUNT_PROVIDERS` config

### **3. `config/urls.py`**
- Đã có: `path('accounts/social/', include('allauth.urls'))`

### **4. `templates/accounts/login.html`**
- Thêm nút "Đăng nhập với Google"

### **5. `templates/accounts/register.html`**
- Thêm nút "Đăng ký với Google"

### **6. Database**
- Tạo `Site` object (id=1, domain=localhost:8000)
- Tạo `SocialApp` object (provider=google)

---

## 🎨 **CUSTOMIZE**

### **Thay đổi thông tin user sau khi đăng nhập:**

Tạo file `apps/accounts/adapters.py`:

```python
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        
        # Customize user data
        # VD: Lấy ảnh đại diện từ Google
        if sociallogin.account.provider == 'google':
            extra_data = sociallogin.account.extra_data
            user.first_name = extra_data.get('given_name', '')
            user.last_name = extra_data.get('family_name', '')
            # user.profile_picture = extra_data.get('picture', '')
            user.save()
        
        return user
```

Thêm vào `settings.py`:

```python
SOCIALACCOUNT_ADAPTER = 'apps.accounts.adapters.CustomSocialAccountAdapter'
```

---

## 🔒 **BẢO MẬT**

### **1. Không commit credentials vào Git:**

File `.env` đã được thêm vào `.gitignore`

### **2. Production:**

Khi deploy production, cần:
- Thay đổi `Site.domain` thành domain thật
- Thêm domain vào Google Cloud Console
- Update redirect URIs

```python
# Production settings
python manage.py shell

from django.contrib.sites.models import Site
site = Site.objects.get(id=1)
site.domain = 'phongtro.yourdomain.com'
site.name = 'PhongTro Production'
site.save()
```

### **3. Giới hạn OAuth Consent Screen:**

Trong Google Cloud Console:
- Thêm test users nếu app chưa publish
- Hoặc publish app để cho phép tất cả user

---

## 🧪 **TESTING**

### **Test login flow:**

```bash
# 1. Chạy server
python manage.py runserver

# 2. Mở browser
http://localhost:8000/accounts/login/

# 3. Click "Đăng nhập với Google"

# 4. Kiểm tra user đã được tạo
python manage.py shell

from django.contrib.auth.models import User
from allauth.socialaccount.models import SocialAccount

# Xem user vừa tạo
user = User.objects.last()
print(f"Username: {user.username}")
print(f"Email: {user.email}")

# Xem social account
social = SocialAccount.objects.filter(user=user).first()
print(f"Provider: {social.provider}")
print(f"UID: {social.uid}")
print(f"Extra data: {social.extra_data}")
```

---

## ⚠️ **TROUBLESHOOTING**

### **Lỗi: "redirect_uri_mismatch"**

**Nguyên nhân:** Redirect URI không khớp với Google Cloud Console

**Giải pháp:**
1. Vào Google Cloud Console
2. Kiểm tra **Authorized redirect URIs**
3. Đảm bảo có: `http://localhost:8000/accounts/social/google/login/callback/`
4. Lưu ý: **CÓ** dấu `/` ở cuối

---

### **Lỗi: "invalid_client"**

**Nguyên nhân:** Client ID hoặc Secret sai

**Giải pháp:**
1. Kiểm tra `.env` file
2. Chạy lại: `python manage.py setup_google_oauth`
3. Restart server

---

### **Lỗi: "Site matching query does not exist"**

**Nguyên nhân:** Chưa có Site object

**Giải pháp:**
```bash
python manage.py setup_google_oauth
```

---

### **Lỗi: "SocialApp matching query does not exist"**

**Nguyên nhân:** Chưa có Google Social App

**Giải pháp:**
```bash
python manage.py setup_google_oauth
```

---

## 📊 **MONITORING**

### **Xem log đăng nhập:**

```python
from apps.accounts.models import SecurityLogs

# Xem log đăng nhập Google
logs = SecurityLogs.objects.filter(
    action_type='login',
    details__icontains='google'
).order_by('-created_at')[:20]

for log in logs:
    print(f"{log.created_at} - {log.user.email} - {log.ip_address}")
```

---

## 🚀 **PRODUCTION DEPLOYMENT**

### **1. Update Google Cloud Console:**

Thêm production domain vào:
- **Authorized JavaScript origins:**
  ```
  https://phongtro.yourdomain.com
  ```

- **Authorized redirect URIs:**
  ```
  https://phongtro.yourdomain.com/accounts/social/google/login/callback/
  ```

### **2. Update Django Site:**

```bash
python manage.py shell

from django.contrib.sites.models import Site
site = Site.objects.get(id=1)
site.domain = 'phongtro.yourdomain.com'
site.name = 'PhongTro Production'
site.save()
```

### **3. Update settings:**

```python
# config/settings/production.py

CSRF_TRUSTED_ORIGINS = [
    'https://phongtro.yourdomain.com',
]

ALLOWED_HOSTS = [
    'phongtro.yourdomain.com',
]
```

---

**Ngày cập nhật:** 24/12/2025  
**Phiên bản:** 1.0  
**Trạng thái:** ✅ Hoạt động

