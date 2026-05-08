import os
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .models import PrinterProfile, ProcessingHistory, SystemSettings, PrintJobLog
from .forms import PDFUploadForm, PrinterProfileForm, SystemSettingsForm
from pdf_engine.reverse import reverse_pdf_pages
from print_automation.pdf_launcher import launch_pdf_print

logger = logging.getLogger(__name__)


def dashboard_home(request):
    """Main dashboard view."""
    # Get recent processing history
    recent_jobs = ProcessingHistory.objects.all()[:10]

    # Get system stats
    total_jobs = ProcessingHistory.objects.count()
    successful_jobs = ProcessingHistory.objects.filter(status='completed').count()
    failed_jobs = ProcessingHistory.objects.filter(status='failed').count()

    # Calculate success rate
    if total_jobs > 0:
        success_rate = round((successful_jobs / total_jobs) * 100, 1)
    else:
        success_rate = 0

    context = {
        'recent_jobs': recent_jobs,
        'total_jobs': total_jobs,
        'successful_jobs': successful_jobs,
        'failed_jobs': failed_jobs,
        'success_rate': success_rate,
    }
    return render(request, 'dashboard/home.html', context)


def upload_pdf(request):
    """Handle PDF upload and processing."""
    if request.method == 'POST':
        form = PDFUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                pdf_file = request.FILES['pdf_file']
                profile = form.cleaned_data.get('printer_profile')

                # Ensure temp folder exists
                os.makedirs(settings.TEMP_FOLDER, exist_ok=True)

                # Sanitize filename
                pdf_filename = os.path.basename(pdf_file.name)
                if not pdf_filename.lower().endswith('.pdf'):
                    raise ValueError("File must be a PDF")

                # Save original file temporarily
                temp_path = os.path.join(settings.TEMP_FOLDER, pdf_filename)

                with open(temp_path, 'wb+') as destination:
                    for chunk in pdf_file.chunks():
                        destination.write(chunk)

                # Process the PDF
                processed_path, page_count = reverse_pdf_pages(temp_path, profile)

                # Create processing history record
                history = ProcessingHistory.objects.create(
                    original_filename=pdf_filename,
                    processed_filename=os.path.basename(processed_path),
                    file_size=pdf_file.size,
                    page_count=page_count,
                    status='completed',
                    printer_profile=profile,
                )

                # Launch print if auto_print is enabled
                if profile and profile.auto_print:
                    launch_pdf_print(processed_path)

                messages.success(request, f"PDF processed successfully: {pdf_filename}")
                return redirect('dashboard_home')

            except Exception as e:
                logger.error(f"PDF processing failed: {str(e)}")
                try:
                    ProcessingHistory.objects.create(
                        original_filename=pdf_file.name if 'pdf_file' in locals() else 'unknown',
                        file_size=pdf_file.size if 'pdf_file' in locals() else 0,
                        status='failed',
                        error_message=str(e),
                        printer_profile=profile if 'profile' in locals() else None,
                    )
                except Exception as db_error:
                    logger.error(f"Failed to save error to database: {str(db_error)}")

                messages.error(request, f"Processing failed: {str(e)}")
                return redirect('upload_pdf')
    else:
        form = PDFUploadForm()

    return render(request, 'dashboard/upload.html', {'form': form})


def printer_profiles(request):
    """Manage printer profiles."""
    profiles = PrinterProfile.objects.all()

    if request.method == 'POST':
        form = PrinterProfileForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Printer profile created successfully.")
            return redirect('printer_profiles')
    else:
        form = PrinterProfileForm()

    return render(request, 'dashboard/profiles.html', {
        'profiles': profiles,
        'form': form
    })


def edit_printer_profile(request, pk):
    """Edit a printer profile."""
    profile = get_object_or_404(PrinterProfile, pk=pk)

    if request.method == 'POST':
        form = PrinterProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Printer profile updated successfully.")
            return redirect('printer_profiles')
    else:
        form = PrinterProfileForm(instance=profile)

    return render(request, 'dashboard/edit_profile.html', {
        'form': form,
        'profile': profile
    })


def delete_printer_profile(request, pk):
    """Delete a printer profile."""
    profile = get_object_or_404(PrinterProfile, pk=pk)
    if request.method == 'POST':
        profile.delete()
        messages.success(request, "Printer profile deleted successfully.")
        return redirect('printer_profiles')

    return render(request, 'dashboard/delete_profile.html', {'profile': profile})


def processing_history(request):
    """View processing history."""
    jobs = ProcessingHistory.objects.all().order_by('-created_at')
    return render(request, 'dashboard/history.html', {'jobs': jobs})


@require_POST
def delete_processing_history(request, pk):
    """Delete a processing history record."""
    job = get_object_or_404(ProcessingHistory, pk=pk)
    job.delete()
    messages.success(request, "Processing history record deleted successfully.")
    return redirect('processing_history')


def system_settings(request):
    """Manage system settings."""
    settings_list = SystemSettings.objects.all()

    if request.method == 'POST':
        form = SystemSettingsForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Setting saved successfully.")
            return redirect('system_settings')
    else:
        form = SystemSettingsForm()

    return render(request, 'dashboard/settings.html', {
        'settings': settings_list,
        'form': form
    })


# API Views
@csrf_exempt
@require_POST
def api_status(request):
    """API endpoint for assistant status."""
    # This would be called by the desktop assistant
    data = {
        'status': 'running',
        'watch_folder': settings.WATCH_FOLDER,
        'total_jobs': ProcessingHistory.objects.count(),
    }
    return JsonResponse(data)


def download_processed(request, pk):
    """Download processed PDF file."""
    try:
        job = get_object_or_404(ProcessingHistory, pk=pk)

        if not job.processed_filename:
            messages.error(request, "No processed file available for download.")
            return redirect('processing_history')

        # Construct file path
        file_path = os.path.join(settings.OUTPUT_FOLDER, job.processed_filename)

        if not os.path.exists(file_path):
            messages.error(request, "Processed file not found.")
            return redirect('processing_history')

        # Open and serve the file
        with open(file_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{job.processed_filename}"'
            logger.info(f"Downloaded processed PDF: {job.processed_filename}")
            return response

    except Exception as e:
        logger.error(f"PDF download failed: {str(e)}")
        messages.error(request, f"Download failed: {str(e)}")
        return redirect('processing_history')


@csrf_exempt
@require_POST
def api_process_job(request):
    """API endpoint for processing a detected PDF."""
    try:
        filename = request.POST.get('filename')
        filepath = request.POST.get('filepath')

        if not filename or not filepath:
            return JsonResponse({'error': 'Missing filename or filepath'}, status=400)

        # Process the PDF
        processed_path, page_count = reverse_pdf_pages(filepath)

        # Create history record
        history = ProcessingHistory.objects.create(
            original_filename=filename,
            processed_filename=os.path.basename(processed_path),
            file_size=os.path.getsize(filepath),
            page_count=page_count,
            status='completed',
        )

        # Launch print
        launch_pdf_print(processed_path)

        return JsonResponse({'status': 'success', 'history_id': history.id})

    except Exception as e:
        logger.error(f"API processing failed: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)
