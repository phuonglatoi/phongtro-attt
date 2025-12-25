#!/usr/bin/env python
# ============================================
# apps/accounts/management/commands/setup_google_oauth.py
# Setup Google OAuth automatically
# ============================================
import os
from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
from decouple import config


class Command(BaseCommand):
    help = 'Setup Google OAuth configuration automatically'

    def handle(self, *args, **options):
        self.stdout.write("=" * 60)
        self.stdout.write(self.style.SUCCESS("🔧 SETTING UP GOOGLE OAUTH"))
        self.stdout.write("=" * 60)

        # Step 1: Create or update Site
        self.stdout.write("\n📍 Step 1: Setting up Site...")
        
        site, created = Site.objects.get_or_create(id=1)
        site.domain = 'localhost:8000'
        site.name = 'PhongTroATTT'
        site.save()
        
        if created:
            self.stdout.write(self.style.SUCCESS(f"   ✅ Created new site: {site.name}"))
        else:
            self.stdout.write(self.style.SUCCESS(f"   ✅ Updated existing site: {site.name}"))
        
        # Step 2: Get Google OAuth credentials from .env
        self.stdout.write("\n🔑 Step 2: Loading Google OAuth credentials...")
        
        client_id = config('GOOGLE_OAUTH_CLIENT_ID', default='')
        client_secret = config('GOOGLE_OAUTH_CLIENT_SECRET', default='')
        
        if not client_id or not client_secret:
            self.stdout.write(self.style.ERROR("   ❌ ERROR: Google OAuth credentials not found in .env"))
            self.stdout.write(self.style.WARNING("   Please add GOOGLE_OAUTH_CLIENT_ID and GOOGLE_OAUTH_CLIENT_SECRET to .env"))
            return
        
        self.stdout.write(self.style.SUCCESS(f"   ✅ Client ID: {client_id[:20]}..."))
        self.stdout.write(self.style.SUCCESS(f"   ✅ Client Secret: {client_secret[:10]}..."))
        
        # Step 3: Create or update Google Social App
        self.stdout.write("\n🌐 Step 3: Setting up Google Social App...")
        
        try:
            # Try to get existing Google app
            social_app = SocialApp.objects.get(provider='google')
            social_app.name = 'Google OAuth'
            social_app.client_id = client_id
            social_app.secret = client_secret
            social_app.save()
            
            # Update sites
            social_app.sites.clear()
            social_app.sites.add(site)
            
            self.stdout.write(self.style.SUCCESS("   ✅ Updated existing Google Social App"))
        
        except SocialApp.DoesNotExist:
            # Create new Google app
            social_app = SocialApp.objects.create(
                provider='google',
                name='Google OAuth',
                client_id=client_id,
                secret=client_secret,
            )
            social_app.sites.add(site)
            
            self.stdout.write(self.style.SUCCESS("   ✅ Created new Google Social App"))
        
        # Step 4: Verify setup
        self.stdout.write("\n✅ Step 4: Verifying setup...")
        
        google_apps = SocialApp.objects.filter(provider='google')
        
        if google_apps.exists():
            app = google_apps.first()
            self.stdout.write(self.style.SUCCESS(f"   ✅ Provider: {app.provider}"))
            self.stdout.write(self.style.SUCCESS(f"   ✅ Name: {app.name}"))
            self.stdout.write(self.style.SUCCESS(f"   ✅ Client ID: {app.client_id[:20]}..."))
            self.stdout.write(self.style.SUCCESS(f"   ✅ Sites: {', '.join([s.domain for s in app.sites.all()])}"))
        
        # Final instructions
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("🎉 GOOGLE OAUTH SETUP COMPLETED!"))
        self.stdout.write("=" * 60)
        
        self.stdout.write("\n📝 Next steps:")
        self.stdout.write("   1. Make sure you added these URLs to Google Cloud Console:")
        self.stdout.write("      Authorized JavaScript origins:")
        self.stdout.write("         - http://localhost:8000")
        self.stdout.write("         - http://127.0.0.1:8000")
        self.stdout.write("")
        self.stdout.write("      Authorized redirect URIs:")
        self.stdout.write("         - http://localhost:8000/accounts/social/google/login/callback/")
        self.stdout.write("         - http://127.0.0.1:8000/accounts/social/google/login/callback/")
        self.stdout.write("")
        self.stdout.write("   2. Run the development server:")
        self.stdout.write("      python manage.py runserver")
        self.stdout.write("")
        self.stdout.write("   3. Visit http://localhost:8000/accounts/login/")
        self.stdout.write("   4. Click 'Đăng nhập với Google' button")
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("✨ Happy coding!"))
        self.stdout.write("")

