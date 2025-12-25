#!/usr/bin/env python
# ============================================
# apps/accounts/management/commands/check_redirect_uri.py
# Check redirect URI configuration
# ============================================
from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp


class Command(BaseCommand):
    help = 'Check redirect URI configuration for Google OAuth'

    def handle(self, *args, **options):
        self.stdout.write("=" * 60)
        self.stdout.write(self.style.WARNING("🔍 CHECKING REDIRECT URI CONFIGURATION"))
        self.stdout.write("=" * 60)

        # Get current site
        try:
            site = Site.objects.get(id=1)
            self.stdout.write(f"\n📍 Current Site:")
            self.stdout.write(f"   Domain: {site.domain}")
            self.stdout.write(f"   Name: {site.name}")
        except Site.DoesNotExist:
            self.stdout.write(self.style.ERROR("\n❌ No site found!"))
            return

        # Get Google app
        try:
            google_app = SocialApp.objects.get(provider='google')
            self.stdout.write(f"\n🔑 Google OAuth App:")
            self.stdout.write(f"   Name: {google_app.name}")
            self.stdout.write(f"   Client ID: {google_app.client_id[:30]}...")
            self.stdout.write(f"   Sites: {', '.join([s.domain for s in google_app.sites.all()])}")
        except SocialApp.DoesNotExist:
            self.stdout.write(self.style.ERROR("\n❌ No Google OAuth app found!"))
            return

        # Show expected redirect URIs
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("📝 EXPECTED REDIRECT URIs IN GOOGLE CLOUD CONSOLE:")
        self.stdout.write("=" * 60)
        
        protocols = ['http', 'https']
        domains = [site.domain, '127.0.0.1:8000']
        
        self.stdout.write("\nAdd these URIs to Google Cloud Console:")
        self.stdout.write("(Credentials → OAuth 2.0 Client IDs → Authorized redirect URIs)\n")
        
        for protocol in protocols:
            for domain in domains:
                uri = f"{protocol}://{domain}/accounts/social/google/login/callback/"
                self.stdout.write(f"   {uri}")
        
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("✅ CURRENT CALLBACK URL:")
        self.stdout.write("=" * 60)
        self.stdout.write(f"\n   http://{site.domain}/accounts/social/google/login/callback/")
        self.stdout.write("\n" + "=" * 60)

