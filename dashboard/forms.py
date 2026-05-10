from django import forms
from .models import PrinterProfile, SystemSettings


class PDFUploadForm(forms.Form):
    """Form for PDF upload and processing."""
    printer_profile = forms.ModelChoiceField(
        queryset=PrinterProfile.objects.none(),
        required=False,
        empty_label="Use Default Profile",
        help_text="Select a printer profile for processing",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['printer_profile'].queryset = PrinterProfile.objects.all()


class PrinterProfileForm(forms.ModelForm):
    """Form for creating/editing printer profiles."""
    class Meta:
        model = PrinterProfile
        fields = [
            'name', 'description', 'processing_mode',
            'is_default'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Profile name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description'}),
            'processing_mode': forms.Select(attrs={'class': 'form-select'}),
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