from django.core.management.base import BaseCommand
import json
from dashboard.models import SystemSettings


class Command(BaseCommand):
    help = 'Populate comprehensive system settings with categories and options'

    def handle(self, *args, **options):
        settings_data = [
            # FILE HANDLING
            {
                'key': 'max_file_size_mb',
                'value': '500',
                'category': 'file_handling',
                'setting_type': 'number',
                'description': 'Maximum file size for PDF uploads',
                'help_text': 'Files larger than this will be rejected during upload',
                'default_value': '500',
                'is_system': True,
            },
            {
                'key': 'allowed_file_formats',
                'value': 'pdf',
                'category': 'file_handling',
                'setting_type': 'list',
                'description': 'Allowed file formats for upload',
                'help_text': 'Comma-separated list of file extensions (e.g., pdf,txt)',
                'default_value': 'pdf',
                'is_system': True,
            },
            {
                'key': 'auto_delete_processed',
                'value': 'false',
                'category': 'file_handling',
                'setting_type': 'boolean',
                'description': 'Automatically delete processed files',
                'help_text': 'When enabled, processed files are automatically removed after the specified number of days',
                'default_value': 'false',
                'is_system': True,
            },
            {
                'key': 'auto_delete_days',
                'value': '30',
                'category': 'file_handling',
                'setting_type': 'number',
                'description': 'Days to keep processed files',
                'help_text': 'Number of days before automatically deleting processed files (only if auto_delete_processed is enabled)',
                'default_value': '30',
                'is_system': True,
            },
            
            # PDF PROCESSING
            {
                'key': 'processing_timeout_seconds',
                'value': '300',
                'category': 'processing',
                'setting_type': 'number',
                'description': 'PDF processing timeout',
                'help_text': 'Maximum time in seconds for processing a single PDF before timeout',
                'default_value': '300',
                'is_system': True,
            },
            {
                'key': 'max_concurrent_jobs',
                'value': '3',
                'category': 'processing',
                'setting_type': 'choice',
                'description': 'Maximum concurrent processing jobs',
                'help_text': 'Number of PDFs that can be processed simultaneously',
                'choices_json': json.dumps(['1', '2', '3', '5', '10']),
                'default_value': '3',
                'is_system': True,
            },
            {
                'key': 'default_page_reversal',
                'value': 'true',
                'category': 'processing',
                'setting_type': 'boolean',
                'description': 'Reverse page order by default',
                'help_text': 'When enabled, pages are reversed by default for proper stacking',
                'default_value': 'true',
                'is_system': True,
            },
            {
                'key': 'compression_enabled',
                'value': 'false',
                'category': 'processing',
                'setting_type': 'boolean',
                'description': 'Enable PDF compression',
                'help_text': 'Compress PDFs during processing to reduce file size',
                'default_value': 'false',
                'is_system': True,
            },
            {
                'key': 'compression_quality',
                'value': 'medium',
                'category': 'processing',
                'setting_type': 'choice',
                'description': 'Compression quality level',
                'help_text': 'Quality level when compression is enabled',
                'choices_json': json.dumps(['low', 'medium', 'high']),
                'default_value': 'medium',
                'is_system': True,
            },
            
            # OUTPUT & PRINTING
            {
                'key': 'default_printer',
                'value': 'Microsoft Print to PDF',
                'category': 'output',
                'setting_type': 'text',
                'description': 'Default printer for output',
                'help_text': 'Default printer when no specific profile is selected',
                'default_value': 'Microsoft Print to PDF',
                'is_system': True,
            },
            {
                'key': 'auto_print_enabled',
                'value': 'false',
                'category': 'output',
                'setting_type': 'boolean',
                'description': 'Automatically launch print dialog',
                'help_text': 'Automatically open the print dialog after processing completes',
                'default_value': 'false',
                'is_system': True,
            },
            {
                'key': 'open_after_processing',
                'value': 'false',
                'category': 'output',
                'setting_type': 'boolean',
                'description': 'Open file after processing',
                'help_text': 'Automatically open processed PDF in default viewer after completion',
                'default_value': 'false',
                'is_system': True,
            },
            {
                'key': 'output_format_preference',
                'value': 'pdf',
                'category': 'output',
                'setting_type': 'choice',
                'description': 'Preferred output format',
                'help_text': 'Format for processed files',
                'choices_json': json.dumps(['pdf', 'pdf/a']),
                'default_value': 'pdf',
                'is_system': True,
            },
            
            # MONITORING & LOGGING
            {
                'key': 'watch_folder_enabled',
                'value': 'true',
                'category': 'monitoring',
                'setting_type': 'boolean',
                'description': 'Enable watch folder monitoring',
                'help_text': 'Monitor the watch folder for new PDF files to automatically process',
                'default_value': 'true',
                'is_system': True,
            },
            {
                'key': 'notification_email',
                'value': '',
                'category': 'monitoring',
                'setting_type': 'text',
                'description': 'Email for processing notifications',
                'help_text': 'Leave empty to disable. Email notifications are sent on completion or errors',
                'default_value': '',
                'is_system': True,
            },
            {
                'key': 'log_level',
                'value': 'info',
                'category': 'monitoring',
                'setting_type': 'choice',
                'description': 'Application logging level',
                'help_text': 'Verbosity of application logs',
                'choices_json': json.dumps(['debug', 'info', 'warning', 'error']),
                'default_value': 'info',
                'is_system': True,
            },
            {
                'key': 'keep_logs_days',
                'value': '30',
                'category': 'monitoring',
                'setting_type': 'number',
                'description': 'Keep logs for this many days',
                'help_text': 'Old log files are automatically deleted after this period',
                'default_value': '30',
                'is_system': True,
            },
            
            # PERFORMANCE
            {
                'key': 'cache_timeout_seconds',
                'value': '300',
                'category': 'performance',
                'setting_type': 'number',
                'description': 'Settings cache timeout',
                'help_text': 'How long to cache settings before refreshing from database',
                'default_value': '300',
                'is_system': True,
            },
            {
                'key': 'database_optimization',
                'value': 'true',
                'category': 'performance',
                'setting_type': 'boolean',
                'description': 'Enable database query optimization',
                'help_text': 'Enable query result caching and optimization',
                'default_value': 'true',
                'is_system': True,
            },
            {
                'key': 'thread_pool_size',
                'value': '4',
                'category': 'performance',
                'setting_type': 'choice',
                'description': 'Thread pool size for background tasks',
                'help_text': 'Number of worker threads for concurrent processing',
                'choices_json': json.dumps(['2', '4', '8', '16']),
                'default_value': '4',
                'is_system': True,
            },
            
            # ADVANCED
            {
                'key': 'debug_mode',
                'value': 'false',
                'category': 'advanced',
                'setting_type': 'boolean',
                'description': 'Enable debug mode',
                'help_text': 'Enable debug mode for troubleshooting (not recommended for production)',
                'default_value': 'false',
                'is_system': True,
            },
            {
                'key': 'backup_enabled',
                'value': 'false',
                'category': 'advanced',
                'setting_type': 'boolean',
                'description': 'Enable automatic backups',
                'help_text': 'Automatically backup database and settings',
                'default_value': 'false',
                'is_system': True,
            },
            {
                'key': 'backup_frequency_hours',
                'value': '24',
                'category': 'advanced',
                'setting_type': 'number',
                'description': 'Backup frequency in hours',
                'help_text': 'How often to create backups (only if backup_enabled is true)',
                'default_value': '24',
                'is_system': True,
            },
        ]

        for setting_data in settings_data:
            setting, created = SystemSettings.objects.update_or_create(
                key=setting_data['key'],
                defaults={
                    'value': setting_data['value'],
                    'category': setting_data['category'],
                    'setting_type': setting_data['setting_type'],
                    'description': setting_data['description'],
                    'help_text': setting_data['help_text'],
                    'choices_json': setting_data.get('choices_json', ''),
                    'default_value': setting_data['default_value'],
                    'is_system': setting_data['is_system'],
                }
            )
            status = 'Created' if created else 'Updated'
            self.stdout.write(
                self.style.SUCCESS(f'{status}: {setting.key}')
            )
