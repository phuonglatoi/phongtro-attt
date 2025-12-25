#!/usr/bin/env python
# ============================================
# apps/accounts/management/commands/check_social_apps.py
# Check all Social Apps in database
# ============================================
from django.core.management.base import BaseCommand
from allauth.socialaccount.models import SocialApp


class Command(BaseCommand):
    help = 'Check all Social Apps in database'

    def handle(self, *args, **options):
        self.stdout.write("=" * 60)
        self.stdout.write(self.style.WARNING("📊 CHECKING ALL SOCIAL APPS"))
        self.stdout.write("=" * 60)

        # Get all social apps
        all_apps = SocialApp.objects.all()
        
        self.stdout.write(f"\n🔍 Total Social Apps: {all_apps.count()}")
        
        if all_apps.count() == 0:
            self.stdout.write(self.style.WARNING("   ⚠️  No Social Apps found!"))
            return
        
        self.stdout.write("\n📋 Details:")
        for i, app in enumerate(all_apps, 1):
            self.stdout.write(f"\n   App #{i}:")
            self.stdout.write(f"      ID: {app.id}")
            self.stdout.write(f"      Provider: {app.provider}")
            self.stdout.write(f"      Name: {app.name}")
            self.stdout.write(f"      Client ID: {app.client_id[:30]}...")
            self.stdout.write(f"      Sites: {', '.join([s.domain for s in app.sites.all()])}")
        
        # Check Google apps specifically
        google_apps = SocialApp.objects.filter(provider='google')
        
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(f"🔍 Google Apps: {google_apps.count()}")
        
        if google_apps.count() > 1:
            self.stdout.write(self.style.ERROR(f"   ❌ ERROR: Found {google_apps.count()} Google apps (should be 1)"))
            self.stdout.write("\n   Run: python manage.py fix_google_oauth")
        elif google_apps.count() == 1:
            self.stdout.write(self.style.SUCCESS("   ✅ OK: Exactly 1 Google app"))
        else:
            self.stdout.write(self.style.WARNING("   ⚠️  No Google app found"))
        
        self.stdout.write("=" * 60)

