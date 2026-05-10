from django.core.management.base import BaseCommand
from dashboard.models import PrinterProfile


class Command(BaseCommand):
    help = 'Create default printer profiles'

    def handle(self, *args, **options):
        # First, unset all defaults
        PrinterProfile.objects.all().update(is_default=False)

        profiles_data = [
            {
                'name': 'Normal Order',
                'description': 'Keep pages in normal order (no reversal)',
                'processing_mode': 'normal',
                'is_default': True,
            },
            {
                'name': 'Reverse for Stacking',
                'description': 'Reverse page order for correct printer stacking',
                'processing_mode': 'reverse',
                'is_default': False,
            },
        ]

        for profile_data in profiles_data:
            profile, created = PrinterProfile.objects.update_or_create(
                name=profile_data['name'],
                defaults={
                    'description': profile_data['description'],
                    'processing_mode': profile_data['processing_mode'],
                    'is_default': profile_data['is_default'],
                }
            )
            status = 'Created' if created else 'Updated'
            self.stdout.write(
                self.style.SUCCESS(f'{status}: {profile.name}')
            )