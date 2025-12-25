#!/usr/bin/env python
# ============================================
# apps/accounts/management/commands/check_sites.py
# Check all Sites in database
# ============================================
from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp


class Command(BaseCommand):
    help = 'Check all Sites and their Social Apps'

    def handle(self, *args, **options):
        self.stdout.write("=" * 60)
        self.stdout.write(self.style.WARNING("📊 CHECKING ALL SITES"))
        self.stdout.write("=" * 60)

        # Get all sites
        all_sites = Site.objects.all()
        
        self.stdout.write(f"\n🔍 Total Sites: {all_sites.count()}")
        
        for i, site in enumerate(all_sites, 1):
            self.stdout.write(f"\n   Site #{i}:")
            self.stdout.write(f"      ID: {site.id}")
            self.stdout.write(f"      Domain: {site.domain}")
            self.stdout.write(f"      Name: {site.name}")
            
            # Get social apps for this site
            apps = site.socialapp_set.all()
            self.stdout.write(f"      Social Apps: {apps.count()}")
            for app in apps:
                self.stdout.write(f"         - {app.provider}: {app.name} (ID={app.id})")
        
        # Check for duplicate Google apps across sites
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("🔍 Checking Google Apps across all sites...")
        
        google_apps = SocialApp.objects.filter(provider='google')
        self.stdout.write(f"\n   Total Google Apps in DB: {google_apps.count()}")
        
        for app in google_apps:
            sites = app.sites.all()
            self.stdout.write(f"\n   App ID={app.id}:")
            self.stdout.write(f"      Name: {app.name}")
            self.stdout.write(f"      Sites: {sites.count()} - {', '.join([f'{s.domain} (ID={s.id})' for s in sites])}")
        
        self.stdout.write("\n" + "=" * 60)

