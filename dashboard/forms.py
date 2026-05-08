from django import forms
from .models import PrinterProfile, SystemSettings


class PDFUploadForm(forms.Form):
    """Form for PDF upload and processing."""
    pdf_file = forms.FileField(
        label="Select PDF File",
        help_text="Upload a PDF file to process and correct page order",
        widget=forms.FileInput(attrs={
            'accept': '.pdf',
            'class': 'form-control',
            'required': True
        })
    )
    printer_profile = forms.ModelChoiceField(
        queryset=PrinterProfile.objects.all(),
        required=False,
        empty_label="Use Default Profile",
        help_text="Select a printer profile for processing",
        widget=forms.Select(attrs={'class': 'form-select'})
    )


class PrinterProfileForm(forms.ModelForm):
    """Form for creating/editing printer profiles."""
    class Meta:
        model = PrinterProfile
        fields = [
            'name', 'description', 'reverse_pages', 'duplex_mode',
            'auto_print', 'watch_folder', 'is_default'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Profile name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description'}),
            'watch_folder': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Leave empty for global watch folder'}),
            'reverse_pages': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'duplex_mode': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'auto_print': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class SystemSettingsForm(forms.ModelForm):
    """Form for system settings."""
    class Meta:
        model = SystemSettings
        fields = ['key', 'value', 'description']
        widgets = {
            'key': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Setting key'}),
            'value': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Setting value'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Description'}),
        }