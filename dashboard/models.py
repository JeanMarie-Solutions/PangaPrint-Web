from django.db import models
from django.utils import timezone


class PrinterProfile(models.Model):
    """Model for printer profiles with different configurations."""
    
    PROCESSING_CHOICES = [
        ('normal', 'Normal Order'),
        ('reverse', 'Reverse Pages'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    processing_mode = models.CharField(
        max_length=20, 
        choices=PROCESSING_CHOICES, 
        default='normal',
        help_text="How to process the PDF pages"
    )
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
    CATEGORY_CHOICES = [
        ('file_handling', 'File Handling'),
        ('processing', 'PDF Processing'),
        ('output', 'Output & Printing'),
        ('monitoring', 'Monitoring & Logging'),
        ('performance', 'Performance'),
        ('advanced', 'Advanced'),
    ]
    
    TYPE_CHOICES = [
        ('text', 'Text'),
        ('number', 'Number'),
        ('boolean', 'Boolean'),
        ('choice', 'Choice'),
        ('list', 'List'),
    ]

    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='advanced')
    setting_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='text')
    description = models.TextField(blank=True)
    help_text = models.TextField(blank=True)
    choices_json = models.TextField(blank=True, help_text='JSON array of choice options for choice type')
    default_value = models.TextField(blank=True)
    is_system = models.BooleanField(default=False, help_text='System settings cannot be deleted via UI')
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
