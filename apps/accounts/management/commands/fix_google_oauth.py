#!/usr/bin/env python
# ============================================
# apps/accounts/management/commands/fix_google_oauth.py
# Fix MultipleObjectsReturned error for Google OAuth
# ============================================
from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
from decouple import config


class Command(BaseCommand):
    help = 'Fix MultipleObjectsReturned error by cleaning up duplicate Google Social Apps'

    def handle(self, *args, **options):
        self.stdout.write("=" * 60)
        self.stdout.write(self.style.WARNING("🔧 FIXING GOOGLE OAUTH"))
        self.stdout.write("=" * 60)

        # Step 1: Check current Google apps
        self.stdout.write("\n📊 Step 1: Checking current Google Social Apps...")
        
        google_apps = SocialApp.objects.filter(provider='google')
        count = google_apps.count()
        
        self.stdout.write(self.style.WARNING(f"   Found {count} Google Social App(s)"))
        
        for i, app in enumerate(google_apps, 1):
            self.stdout.write(f"   {i}. ID={app.id}, Name={app.name}, Client ID={app.client_id[:20]}...")
        
        # Step 2: Delete all Google apps
        if count > 0:
            self.stdout.write("\n🗑️  Step 2: Deleting all existing Google Social Apps...")
            deleted_count = google_apps.delete()[0]
            self.stdout.write(self.style.SUCCESS(f"   ✅ Deleted {deleted_count} app(s)"))
        else:
            self.stdout.write("\n✅ Step 2: No apps to delete")
        
        # Step 3: Get credentials
        self.stdout.write("\n🔑 Step 3: Loading Google OAuth credentials...")
        
        client_id = config('GOOGLE_OAUTH_CLIENT_ID', default='')
        client_secret = config('GOOGLE_OAUTH_CLIENT_SECRET', default='')
        
        if not client_id or not client_secret:
            self.stdout.write(self.style.ERROR("   ❌ ERROR: Credentials not found in .env"))
            return
        
        self.stdout.write(self.style.SUCCESS(f"   ✅ Client ID: {client_id[:20]}..."))
        
        # Step 4: Get or create Site
        self.stdout.write("\n📍 Step 4: Setting up Site...")
        
        site, created = Site.objects.get_or_create(id=1)
        site.domain = 'localhost:8000'
        site.name = 'PhongTroATTT'
        site.save()
        
        self.stdout.write(self.style.SUCCESS(f"   ✅ Site: {site.domain}"))
        
        # Step 5: Create ONE new Google Social App
        self.stdout.write("\n🌐 Step 5: Creating new Google Social App...")
        
        social_app = SocialApp.objects.create(
            provider='google',
            name='Google OAuth',
            client_id=client_id,
            secret=client_secret,
        )
        social_app.sites.add(site)
        
        self.stdout.write(self.style.SUCCESS(f"   ✅ Created app ID={social_app.id}"))
        
        # Step 6: Verify
        self.stdout.write("\n✅ Step 6: Verifying...")
        
        google_apps = SocialApp.objects.filter(provider='google')
        
        if google_apps.count() == 1:
            app = google_apps.first()
            self.stdout.write(self.style.SUCCESS(f"   ✅ Provider: {app.provider}"))
            self.stdout.write(self.style.SUCCESS(f"   ✅ Name: {app.name}"))
            self.stdout.write(self.style.SUCCESS(f"   ✅ Client ID: {app.client_id[:20]}..."))
            self.stdout.write(self.style.SUCCESS(f"   ✅ Sites: {', '.join([s.domain for s in app.sites.all()])}"))
        else:
            self.stdout.write(self.style.ERROR(f"   ❌ ERROR: Found {google_apps.count()} apps (should be 1)"))
            return
        
        # Final
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("🎉 GOOGLE OAUTH FIXED!"))
        self.stdout.write("=" * 60)
        
        self.stdout.write("\n📝 Next steps:")
        self.stdout.write("   1. Restart the development server")
        self.stdout.write("   2. Visit http://localhost:8000/accounts/login/")
        self.stdout.write("   3. Click 'Đăng nhập với Google'")
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("✨ Should work now!"))
        self.stdout.write("")

