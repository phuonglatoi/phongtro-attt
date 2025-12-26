/**
 * Form Input Limits - Giới hạn ký tự cho tất cả các form
 * Tự động thêm maxlength và hiển thị số ký tự còn lại (trừ form đăng nhập/đăng ký)
 */

document.addEventListener('DOMContentLoaded', function() {

    // Kiểm tra xem có phải trang đăng nhập/đăng ký không
    const isAuthPage = window.location.pathname.includes('/accounts/login') ||
                       window.location.pathname.includes('/accounts/register') ||
                       window.location.pathname.includes('/accounts/signup');

    // Cấu hình giới hạn ký tự cho các loại input
    const INPUT_LIMITS = {
        // Text inputs
        'input[name="tenpt"]': { max: 200, label: 'Tên phòng', showCounter: true },
        'input[name="tennt"]': { max: 200, label: 'Tên nhà trọ', showCounter: true },
        'input[name="username"]': { max: 200, label: 'Họ tên', showCounter: !isAuthPage },
        'input[name="hoten"]': { max: 200, label: 'Họ tên', showCounter: true },
        'input[name="diachi"]': { max: 500, label: 'Địa chỉ', showCounter: true },
        'input[name="email"]': { max: 254, label: 'Email', showCounter: !isAuthPage },
        'input[name="phone"]': { max: 15, label: 'Số điện thoại', showCounter: !isAuthPage },
        'input[name="sdt"]': { max: 15, label: 'Số điện thoại', showCounter: true },

        // Textareas
        'textarea[name="mota"]': { max: 2000, label: 'Mô tả', showCounter: true },
        'textarea[name="binhluan"]': { max: 1000, label: 'Bình luận', showCounter: true },
        'textarea[name="ghichu"]': { max: 500, label: 'Ghi chú', showCounter: true },
        'textarea[name="noidung"]': { max: 2000, label: 'Nội dung', showCounter: true },
        'textarea[name="message"]': { max: 1000, label: 'Tin nhắn', showCounter: true },
    };

    // Áp dụng giới hạn cho từng field
    Object.keys(INPUT_LIMITS).forEach(selector => {
        const elements = document.querySelectorAll(selector);
        const config = INPUT_LIMITS[selector];

        elements.forEach(element => {
            applyCharacterLimit(element, config.max, config.label, config.showCounter);
        });
    });
    
    /**
     * Áp dụng giới hạn ký tự cho một element
     */
    function applyCharacterLimit(element, maxLength, label, showCounter = true) {
        // Set maxlength attribute (luôn luôn set)
        element.setAttribute('maxlength', maxLength);

        // Chỉ hiển thị counter nếu showCounter = true
        if (!showCounter) {
            return;
        }

        // Tạo counter element
        const counter = document.createElement('div');
        counter.className = 'char-counter text-muted small mt-1';
        counter.style.textAlign = 'right';

        // Insert counter sau element
        element.parentNode.insertBefore(counter, element.nextSibling);

        // Update counter function
        function updateCounter() {
            const currentLength = element.value.length;
            const remaining = maxLength - currentLength;

            counter.textContent = `${currentLength}/${maxLength} ký tự`;

            // Đổi màu khi gần hết
            if (remaining < 50) {
                counter.classList.add('text-warning');
                counter.classList.remove('text-muted');
            } else if (remaining < 10) {
                counter.classList.add('text-danger');
                counter.classList.remove('text-warning', 'text-muted');
            } else {
                counter.classList.add('text-muted');
                counter.classList.remove('text-warning', 'text-danger');
            }
        }

        // Update on input
        element.addEventListener('input', updateCounter);
        element.addEventListener('keyup', updateCounter);
        element.addEventListener('paste', function() {
            setTimeout(updateCounter, 10);
        });

        // Initial update
        updateCounter();
    }
    
    // Validate số điện thoại Việt Nam
    const phoneInputs = document.querySelectorAll('input[name="phone"], input[name="sdt"]');
    phoneInputs.forEach(input => {
        input.addEventListener('input', function(e) {
            // Chỉ cho phép số và dấu +
            this.value = this.value.replace(/[^0-9+]/g, '');
            
            // Giới hạn độ dài
            if (this.value.length > 15) {
                this.value = this.value.substring(0, 15);
            }
        });
        
        input.addEventListener('blur', function(e) {
            const value = this.value.trim();
            
            // Validate format: 0xxxxxxxxx hoặc +84xxxxxxxxx
            const vnPhoneRegex = /^(\+84|0)[0-9]{9}$/;
            
            if (value && !vnPhoneRegex.test(value)) {
                this.setCustomValidity('Số điện thoại không hợp lệ (VD: 0912345678 hoặc +84912345678)');
                this.classList.add('is-invalid');
            } else {
                this.setCustomValidity('');
                this.classList.remove('is-invalid');
            }
        });
    });
    
    // Validate email
    const emailInputs = document.querySelectorAll('input[type="email"], input[name="email"]');
    emailInputs.forEach(input => {
        input.addEventListener('blur', function(e) {
            const value = this.value.trim();
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            
            if (value && !emailRegex.test(value)) {
                this.setCustomValidity('Email không hợp lệ');
                this.classList.add('is-invalid');
            } else {
                this.setCustomValidity('');
                this.classList.remove('is-invalid');
            }
        });
    });
    
    // Prevent XSS - sanitize inputs
    const textInputs = document.querySelectorAll('input[type="text"], textarea');
    textInputs.forEach(input => {
        input.addEventListener('blur', function(e) {
            // Remove HTML tags
            const cleaned = this.value.replace(/<[^>]*>/g, '');
            if (cleaned !== this.value) {
                this.value = cleaned;
                showWarning('HTML tags không được phép!');
            }
        });
    });
    
    function showWarning(message) {
        // Tạo toast notification
        const toast = document.createElement('div');
        toast.className = 'alert alert-warning alert-dismissible fade show position-fixed';
        toast.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        toast.innerHTML = `
            <i class="fas fa-exclamation-triangle me-2"></i>${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.remove();
        }, 3000);
    }
});

