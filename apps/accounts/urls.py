# ============================================
# apps/accounts/urls.py
# ============================================

from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication
    path('login/', views.login_view, name='login'),
    path('login/2fa/', views.login_2fa_view, name='login_2fa'),
    path('logout/', views.logout_view, name='logout'),
    path('logout/all/', views.logout_all_devices_view, name='logout_all_devices'),
    path('register/', views.register_view, name='register'),

    # Password
    path('password/change/', views.password_change_view, name='password_change'),
    path('password/reset/', views.password_reset_view, name='password_reset'),
    path('password/reset/done/', views.password_reset_done_view, name='password_reset_done'),
    path('password/reset/confirm/<uidb64>/<token>/', views.password_reset_confirm_view, name='password_reset_confirm'),
    path('password/reset/complete/', views.password_reset_complete_view, name='password_reset_complete'),

    # 2FA
    path('2fa/setup/', views.setup_2fa_view, name='setup_2fa'),
    path('2fa/disable/', views.disable_2fa_view, name='disable_2fa'),

    # Security Questions
    path('security-question/', views.setup_security_question_view, name='setup_security_question'),

    # Profile
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),

    # Devices
    path('devices/', views.manage_devices_view, name='manage_devices'),
    path('devices/<int:device_id>/revoke/', views.revoke_device_view, name='revoke_device'),
]
