# ============================================
# apps/accounts/tests/test_login.py
# ============================================
import pytest
from django.test import Client
from django.urls import reverse
from apps.accounts.models import User

@pytest.mark.django_db
class TestLogin:
    
    def test_login_page_loads(self, client):
        """Test trang login load thành công"""
        response = client.get(reverse('accounts:login'))
        assert response.status_code == 200
    
    def test_login_with_valid_credentials(self, client):
        """Test đăng nhập với thông tin đúng"""
        User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='Test@123456',
            phone='0912345678'
        )
        
        response = client.post(reverse('accounts:login'), {
            'email': 'test@test.com',
            'password': 'Test@123456'
        })
        
        assert response.status_code == 302  # Redirect after login
    
    def test_login_with_invalid_credentials(self, client):
        """Test đăng nhập với thông tin sai"""
        response = client.post(reverse('accounts:login'), {
            'email': 'wrong@test.com',
            'password': 'WrongPassword'
        })
        
        assert response.status_code == 302
        # Should redirect back to login with error


@pytest.mark.django_db
class TestRateLimit:
    
    def test_login_rate_limit(self, client):
        """Test rate limiting sau nhiều lần đăng nhập sai"""
        for i in range(6):
            response = client.post(reverse('accounts:login'), {
                'email': 'test@test.com',
                'password': 'wrong'
            })
        
        # Lần thứ 6 phải bị rate limit
        assert 'rate' in response.content.decode().lower() or response.status_code == 429