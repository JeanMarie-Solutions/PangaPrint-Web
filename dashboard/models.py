from django.db import models
from django.utils import timezone


class PrinterProfile(models.Model):
    """Model for printer profiles with different configurations."""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    reverse_pages = models.BooleanField(default=True, help_text="Reverse page order for correct stacking")
    auto_print = models.BooleanField(default=True, help_text="Automatically launch print dialog")
    watch_folder = models.CharField(max_length=500, blank=True, help_text="Specific watch folder for this profile")
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-is_default', 'name']


class ProcessingHistory(models.Model):
    """Model for tracking PDF processing history."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    original_filename = models.CharField(max_length=255)
    processed_filename = models.CharField(max_length=255, blank=True)
    file_size = models.PositiveIntegerField()
    page_count = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    printer_profile = models.ForeignKey(PrinterProfile, on_delete=models.SET_NULL, null=True, blank=True)
    error_message = models.TextField(blank=True)
    processing_time = models.DurationField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.original_filename} - {self.status}"

    class Meta:
        ordering = ['-created_at']


class SystemSettings(models.Model):
    """Model for system-wide settings."""
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    description = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.key

    class Meta:
        ordering = ['key']


class PrintJobLog(models.Model):
    """Model for logging print job operations."""
    processing_history = models.ForeignKey(ProcessingHistory, on_delete=models.CASCADE)
    printer_name = models.CharField(max_length=255)
    job_status = models.CharField(max_length=50)
    pages_printed = models.PositiveIntegerField(default=0)
    error_details = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Print job for {self.processing_history.original_filename}"

    class Meta:
        ordering = ['-created_at']
