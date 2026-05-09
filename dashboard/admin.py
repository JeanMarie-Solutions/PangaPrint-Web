from django.contrib import admin
from .models import PrinterProfile, ProcessingHistory, SystemSettings, PrintJobLog


@admin.register(PrinterProfile)
class PrinterProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'reverse_pages', 'auto_print', 'is_default', 'created_at')
    list_filter = ('is_default', 'reverse_pages', 'auto_print')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(ProcessingHistory)
class ProcessingHistoryAdmin(admin.ModelAdmin):
    list_display = ('original_filename', 'status', 'page_count', 'created_at', 'completed_at')
    list_filter = ('status', 'created_at')
    search_fields = ('original_filename', 'processed_filename')
    readonly_fields = ('created_at', 'completed_at')


@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    list_display = ('key', 'value', 'updated_at')
    list_filter = ('updated_at',)
    search_fields = ('key',)
    readonly_fields = ('updated_at',)


@admin.register(PrintJobLog)
class PrintJobLogAdmin(admin.ModelAdmin):
    list_display = ('printer_name', 'job_status', 'pages_printed', 'created_at')
    list_filter = ('job_status', 'created_at')
    search_fields = ('printer_name',)
    readonly_fields = ('created_at',)
