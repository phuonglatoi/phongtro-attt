#!/usr/bin/env python
# ============================================
# apps/accounts/adapters.py
# Custom adapters for django-allauth
# ============================================

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings
from django.shortcuts import redirect


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Custom adapter for social account (Google OAuth)
    """

    def pre_social_login(self, request, sociallogin):
        """
        Invoked just after a user successfully authenticates via a
        social provider, but before the login is actually processed.
        """
        # If user is already logged in, just connect the account
        if request.user.is_authenticated:
            return

        # Check if user with this email already exists
        if sociallogin.is_existing:
            return

        # Get email from social account
        email = sociallogin.account.extra_data.get('email')
        if not email:
            return

        # Try to find existing user with this email
        from apps.accounts.models import Khachhang
        try:
            khachhang = Khachhang.objects.get(email=email)
            # Connect the social account to existing user
            sociallogin.connect(request, khachhang.matk.user if khachhang.matk else None)
        except Khachhang.DoesNotExist:
            pass

    def save_user(self, request, sociallogin, form=None):
        """
        Saves a newly signed up social login user.
        Customize user data from Google.
        """
        user = super().save_user(request, sociallogin, form)

        # Get extra data from Google
        if sociallogin.account.provider == 'google':
            extra_data = sociallogin.account.extra_data

            # Update user info from Google
            user.first_name = extra_data.get('given_name', '')
            user.last_name = extra_data.get('family_name', '')
            user.email = extra_data.get('email', '')
            user.save()

            # Create Khachhang profile if not exists
            from apps.accounts.models import Khachhang, Vaitro
            try:
                # Try to get existing Khachhang
                khachhang = Khachhang.objects.get(email=user.email)
            except Khachhang.DoesNotExist:
                # Create new Khachhang
                try:
                    vaitro_khachhang = Vaitro.objects.get(tenvt='Khách hàng')
                except Vaitro.DoesNotExist:
                    vaitro_khachhang = None

                khachhang = Khachhang.objects.create(
                    hoten=f"{extra_data.get('given_name', '')} {extra_data.get('family_name', '')}".strip(),
                    email=user.email,
                    sdt='',  # Will be updated later
                    mavt=vaitro_khachhang,
                )

                # Link to TaiKhoan if exists
                from apps.accounts.models import Taikhoan
                try:
                    taikhoan = Taikhoan.objects.get(user=user)
                    khachhang.matk = taikhoan
                    khachhang.save()
                except Taikhoan.DoesNotExist:
                    pass

        return user

    def populate_user(self, request, sociallogin, data):
        """
        Populate user information from social account data.
        """
        user = super().populate_user(request, sociallogin, data)

        # Set username from email if not provided
        if not user.username:
            email = data.get('email', '')
            if email:
                # Use email prefix as username
                username = email.split('@')[0]
                # Make sure username is unique
                from django.contrib.auth.models import User
                base_username = username
                counter = 1
                while User.objects.filter(username=username).exists():
                    username = f"{base_username}{counter}"
                    counter += 1
                user.username = username

        return user

    def is_auto_signup_allowed(self, request, sociallogin):
        """
        Return whether automatic signup is allowed.
        """
        # Allow auto signup for Google
        return True


class CustomAccountAdapter(DefaultAccountAdapter):
    """
    Custom adapter for account (regular signup/login)
    """

    def is_open_for_signup(self, request):
        """
        Whether to allow sign ups.
        """
        return True

    def get_login_redirect_url(self, request):
        """
        Returns the default URL to redirect to after logging in.
        """
        return settings.LOGIN_REDIRECT_URL

