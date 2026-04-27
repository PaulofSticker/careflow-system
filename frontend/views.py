from urllib import request
from urllib.parse import quote_plus
from datetime import time, datetime, timedelta
from decimal import Decimal

from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.core.exceptions import ValidationError

from clients.models import Client
from packages.models import Package
from sessions_app.models import Session
from payments.models import Installment


def dashboard(request):
    today = timezone.now().date()

    selected_date = request.GET.get('date')
    if selected_date:
        try:
            base_date = datetime.strptime(selected_date, "%Y-%m-%d").date()
        except ValueError:
            base_date = today
            selected_date = ""
    else:
        base_date = None

    next_session = (
        Session.objects
        .filter(
            status='scheduled',
            scheduled_date__gte=today,
            client__street__isnull=False
        )
        .exclude(client__street='')
        .select_related('client', 'package')
        .order_by('scheduled_date', 'scheduled_time')
        .first()
    )

    today_sessions = Session.objects.none()
    available_slots = []

    if base_date:
        today_sessions = (
            Session.objects
            .filter(
                status__in=['scheduled', 'completed'],
                scheduled_date=base_date,
                client__street__isnull=False
            )
            .exclude(client__street='')
            .select_related('client', 'package')
            .order_by('scheduled_time')
        )

        scheduled_sessions = (
            Session.objects
            .filter(status='scheduled', scheduled_date=base_date)
            .select_related('client', 'package')
        )

        now = timezone.now()
        current_date = now.date()
        current_time = now.time().replace(second=0, microsecond=0)

        for hour in range(5, 24):
            for minute in [0, 15, 30, 45]:
                slot_time = time(hour, minute)

                if base_date == current_date and slot_time < current_time:
                    continue

                slot_start = datetime.combine(base_date, slot_time)
                slot_end = slot_start + timedelta(minutes=60)

                has_conflict = False

                for session in scheduled_sessions:
                    existing_start = datetime.combine(session.scheduled_date, session.scheduled_time)
                    existing_end = existing_start + timedelta(minutes=session.duration_minutes)

                    if slot_start < existing_end and slot_end > existing_start:
                        has_conflict = True
                        break

                if not has_conflict:
                    available_slots.append(slot_time)

    google_maps_url = None
    waze_url = None

    if next_session:
        client = next_session.client
        full_address = f"{client.street}, {client.city}, {client.state}, {client.zip_code}"
        encoded_address = quote_plus(full_address)

        google_maps_url = f"https://www.google.com/maps/search/?api=1&query={encoded_address}"
        waze_url = f"https://waze.com/ul?q={encoded_address}"

    context = {
        'total_clients': Client.objects.count(),
        'total_packages': Package.objects.count(),
        'total_sessions': Session.objects.count(),
        'total_installments': Installment.objects.count(),
        'active_packages': Package.objects.filter(status='active').count(),
        'completed_packages': Package.objects.filter(status='completed').count(),
        'completed_sessions': Session.objects.filter(status='completed').count(),
        'overdue_installments': Installment.objects.filter(status='overdue').count(),
        'next_session': next_session,
        'today_sessions': today_sessions,
        'available_slots': available_slots,
        'base_date': base_date,
        'selected_date': selected_date,
        'google_maps_url': google_maps_url,
        'waze_url': waze_url,
    }

    return render(request, 'dashboard.html', context)


def create_session(request):
    error_message = None

    clients = Client.objects.all().order_by('full_name')

    selected_client = request.GET.get('client') or request.POST.get('client')

    if selected_client:
        packages = Package.objects.filter(
            client_id=selected_client,
            status='active'
        ).select_related('client')
    else:
        packages = Package.objects.none()

    selected_date = request.GET.get('date', '')
    selected_time = request.GET.get('time', '')
    selected_client = request.GET.get('client') or request.POST.get('client')
    selected_package = request.POST.get('package', '')
    notes = request.POST.get('notes', '')

    if request.method == 'POST':
        selected_client = request.POST.get('client', '')
        selected_package = request.POST.get('package', '')
        selected_date = request.POST.get('scheduled_date', '')
        selected_time = request.POST.get('scheduled_time', '')
        notes = request.POST.get('notes', '')

        if not selected_client or not selected_package or not selected_date or not selected_time:
            error_message = "Please fill in Client, Package, Date, and Time."
        else:
            try:
                session = Session(
                    client_id=selected_client,
                    package_id=selected_package,
                    scheduled_date=selected_date,
                    scheduled_time=selected_time,
                    status='scheduled',
                    notes=notes,
                    duration_minutes=60,
                )
                session.full_clean()
                session.save()
                return redirect('dashboard')

            except ValidationError as e:
                if hasattr(e, "messages") and e.messages:
                    error_message = " ".join(e.messages)
                else:
                    error_message = str(e)

            except Exception as e:
                error_message = str(e)

    context = {
        'selected_date': selected_date,
        'selected_time': selected_time,
        'clients': clients,
        'packages': packages,
        'selected_client': selected_client,
        'selected_package': selected_package,
        'notes': notes,
        'error_message': error_message,
    }

    return render(request, 'create_session.html', context)


def clients_list(request):
    clients = Client.objects.all().order_by('full_name')

    context = {
        'clients': clients,
    }

    return render(request, 'clients_list.html', context)


def client_detail(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    packages = Package.objects.filter(client=client).order_by('-created_at')
    sessions = Session.objects.filter(client=client).order_by('-scheduled_date', '-scheduled_time')
    now = timezone.now()
    min_date = now.date().isoformat()
    min_time = now.strftime("%H:%M")

    context = {
        'client': client,
        'packages': packages,
        'sessions': sessions,
        'min_date': min_date,
        'min_time': min_time,
    }

    return render(request, 'client_detail.html', context)

def packages_list(request):
    packages = Package.objects.select_related('client').order_by('-created_at')

    context = {
        'packages': packages,
    }

    return render(request, 'packages_list.html', context)


def sessions_list(request):
    sessions = Session.objects.select_related('client', 'package').order_by('scheduled_date', 'scheduled_time')

    context = {
        'sessions': sessions,
    }

    return render(request, 'sessions_list.html', context)


def installments_list(request):
    installments = Installment.objects.select_related('package', 'package__client').order_by('due_date', 'installment_number')

    context = {
        'installments': installments,
    }

    return render(request, 'installments_list.html', context)    

def client_create(request):
    error_message = None

    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        street = request.POST.get('street', '').strip()
        city = request.POST.get('city', '').strip()
        state = request.POST.get('state', '').strip()
        zip_code = request.POST.get('zip_code', '').strip()
        notes = request.POST.get('notes', '').strip()

        if not full_name or not phone:
            error_message = "Please fill in Full Name and Phone."
        else:
            client = Client.objects.create(
                full_name=full_name,
                email=email,
                phone=phone,
                street=street,
                city=city,
                state=state,
                zip_code=zip_code,
                notes=notes,
                status='active',
            )
            return redirect('client_detail', client_id=client.id)

    return render(request, 'client_form.html', {'error_message': error_message})

def package_create(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    error_message = None

    if request.method == 'POST':
        package_type = request.POST.get('package_type')
        total_sessions = int(request.POST.get('total_sessions') or 0)
        total_price = float(request.POST.get('total_price') or 0)
        billing_type = request.POST.get('billing_type')
        payment_method = request.POST.get('payment_method')
        installment_count = int(request.POST.get('installment_count') or 1)
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        try:
            package = Package.objects.create(
                client=client,
                package_type=package_type,
                total_sessions=int(total_sessions),
                total_price=Decimal(total_price),
                billing_type=billing_type,
                payment_method=payment_method,
                installment_count=int(installment_count or 1),
                start_date=start_date,
                end_date=end_date,
                status='active'
            )

            installment_total = package.installment_count
            installment_amount = package.total_price / installment_total

            for number in range(1, installment_total + 1):
                due_date = datetime.strptime(start_date, "%Y-%m-%d").date() + timedelta(days=30 * (number - 1))

                Installment.objects.create(
                    package=package,
                    installment_number=number,
                    amount=installment_amount,
                    due_date=due_date,
                    payment_method=payment_method,
                )

            return redirect('client_detail', client_id=client.id)
            
        except Exception as e:
            error_message = str(e)

    return render(request, 'package_form.html', {
        'client': client,
        'error_message': error_message
    })

