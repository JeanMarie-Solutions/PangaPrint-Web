import os
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.views.decorators.http import require_POST
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .models import PrinterProfile, ProcessingHistory, SystemSettings, PrintJobLog
from .forms import PDFUploadForm, PrinterProfileForm
from .settings_manager import SettingsManager
from pdf_engine.reverse import reverse_pdf_pages
from print_automation.pdf_launcher import launch_pdf_print, print_pdf_silently
from print_automation.printer_manager import get_default_printer

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
    profiles = PrinterProfile.objects.all()

    if request.method == 'POST':
        form = PDFUploadForm(request.POST)
        form.fields['printer_profile'].queryset = PrinterProfile.objects.all()
        pdf_files = request.FILES.getlist('pdf_files')
        if form.is_valid() and pdf_files:
            profile = form.cleaned_data.get('printer_profile')
            processed_count = 0
            failed_count = 0

            max_file_size_mb = SettingsManager.get_int('max_file_size_mb', 500)
            allowed_formats = [fmt.strip().lstrip('.').lower() for fmt in SettingsManager.get_list('allowed_file_formats', ['pdf']) if fmt]
            default_page_reversal = SettingsManager.get_bool('default_page_reversal')
            open_after_processing = SettingsManager.get_bool('open_after_processing')

            # Ensure temp folder exists
            os.makedirs(settings.TEMP_FOLDER, exist_ok=True)

            for pdf_file in pdf_files:
                try:
                    # Sanitize filename
                    pdf_filename = os.path.basename(pdf_file.name)
                    lower_name = pdf_filename.lower()
                    if not any(lower_name.endswith(f'.{fmt}') for fmt in allowed_formats):
                        raise ValueError(f"File must be one of: {', '.join(allowed_formats)}")

                    if pdf_file.size > max_file_size_mb * 1024 * 1024:
                        raise ValueError(f"File exceeds the maximum size of {max_file_size_mb} MB")

                    # Save original file temporarily
                    temp_path = os.path.join(settings.TEMP_FOLDER, pdf_filename)

                    with open(temp_path, 'wb+') as destination:
                        for chunk in pdf_file.chunks():
                            destination.write(chunk)

                    # Process the PDF
                    processed_path, page_count = reverse_pdf_pages(
                        temp_path,
                        profile,
                        default_reverse=default_page_reversal
                    )

                    # Create processing history record
                    history = ProcessingHistory.objects.create(
                        original_filename=pdf_filename,
                        processed_filename=os.path.basename(processed_path),
                        file_size=pdf_file.size,
                        page_count=page_count,
                        status='completed',
                        printer_profile=profile,
                    )

                    if open_after_processing:
                        try:
                            if hasattr(os, 'startfile'):
                                os.startfile(processed_path)
                            else:
                                logger.warning("Skipping open_after_processing on non-Windows platform.")
                        except Exception as open_ex:
                            logger.warning(f"Failed to open processed PDF {processed_path}: {open_ex}")

                    processed_count += 1

                except Exception as e:
                    logger.error(f"PDF processing failed for {pdf_file.name}: {str(e)}")
                    try:
                        ProcessingHistory.objects.create(
                            original_filename=pdf_file.name,
                            file_size=pdf_file.size,
                            status='failed',
                            error_message=str(e),
                            printer_profile=profile,
                        )
                    except Exception as db_error:
                        logger.error(f"Failed to save error to database: {str(db_error)}")
                    failed_count += 1

            if processed_count > 0:
                messages.success(request, f"Successfully processed {processed_count} PDF(s).")
            if failed_count > 0:
                messages.error(request, f"Failed to process {failed_count} PDF(s). Check logs for details.")

            return redirect('upload_pdf')
        elif not pdf_files:
            messages.error(request, "Please select at least one PDF file.")
    else:
        form = PDFUploadForm()
        form.fields['printer_profile'].queryset = PrinterProfile.objects.all()

    return render(request, 'dashboard/upload.html', {'form': form, 'profiles': profiles})


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
    if request.method == 'POST':
        bulk_action = request.POST.get('bulk_action')
        selected_jobs = request.POST.getlist('selected_jobs')

        if not selected_jobs:
            messages.error(request, "No jobs selected.")
            return redirect('processing_history')

        if bulk_action == 'bulk_delete':
            deleted_count = ProcessingHistory.objects.filter(id__in=selected_jobs).delete()[0]
            messages.success(request, f"Deleted {deleted_count} job(s) successfully.")
        elif bulk_action == 'bulk_print':
            printer_name = get_default_printer()
            if not printer_name:
                messages.error(request, "No default printer configured.")
                return redirect('processing_history')
            printed_count = 0
            failed_count = 0
            for job_id in selected_jobs:
                job = get_object_or_404(ProcessingHistory, pk=job_id)
                if job.status == 'completed' and job.processed_filename:
                    file_path = os.path.join(settings.OUTPUT_FOLDER, job.processed_filename)
                    if os.path.exists(file_path):
                        printed = launch_pdf_print(file_path, printer_name)
                        if not printed:
                            printed = print_pdf_silently(file_path, printer_name)
                        if printed:
                            printed_count += 1
                        else:
                            failed_count += 1
                    else:
                        failed_count += 1
                else:
                    failed_count += 1
            if printed_count and failed_count:
                messages.success(request, f"Sent {printed_count} job(s) to print.")
                messages.warning(request, f"{failed_count} job(s) failed to print.")
            elif printed_count:
                messages.success(request, f"Sent {printed_count} job(s) to print.")
            else:
                messages.error(request, "No selected jobs could be printed.")
        else:
            messages.error(request, "Invalid bulk action.")

        return redirect('processing_history')

    jobs = ProcessingHistory.objects.all().order_by('-created_at')
    return render(request, 'dashboard/history.html', {'jobs': jobs})


def api_profiles(request):
    """Return current printer profiles in JSON."""
    profiles = PrinterProfile.objects.all().values('id', 'name', 'description', 'is_default')
    return JsonResponse(list(profiles), safe=False)


def print_processed(request, pk):
    """Serve the processed PDF inline for printing."""
    job = get_object_or_404(ProcessingHistory, pk=pk)

    if not job.processed_filename:
        messages.error(request, "No processed file available to print.")
        return redirect('processing_history')

    file_path = os.path.join(settings.OUTPUT_FOLDER, job.processed_filename)

    if not os.path.exists(file_path):
        messages.error(request, "Processed file not found.")
        return redirect('processing_history')

    with open(file_path, 'rb') as f:
        response = HttpResponse(f.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{job.processed_filename}"'
        return response


@require_POST
def delete_processing_history(request, pk):
    """Delete a processing history record."""
    job = get_object_or_404(ProcessingHistory, pk=pk)
    job.delete()
    messages.success(request, "Processing history record deleted successfully.")
    return redirect('processing_history')


def about(request):
    """About page for the application."""
    return render(request, 'dashboard/about.html')


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
