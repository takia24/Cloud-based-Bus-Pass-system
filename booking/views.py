from django.shortcuts import render, redirect, get_object_or_404
from .models import Bus, Ticket
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.http import HttpResponse
import qrcode, os
from django.conf import settings
from reportlab.pdfgen import canvas
from django.contrib.auth.decorators import login_required
from datetime import date


# 🔐 Register (UPDATED with email)
def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST.get('email')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return redirect('register')

        user = User.objects.create_user(
            username=username,
            password=password,
            email=email
        )

        login(request, user)
        return redirect('bus_list')

    return render(request, 'booking/register.html')


# 🔐 Login
def user_login(request):
    if request.method == 'POST':
        user = authenticate(
            request,
            username=request.POST['username'],
            password=request.POST['password']
        )

        if user:
            login(request, user)
            return redirect('bus_list')
        else:
            messages.error(request, "Invalid username or password!")

    return render(request, 'booking/login.html')


# 🔐 Logout
def user_logout(request):
    logout(request)
    return redirect('login')


# 🚌 Bus list
@login_required
def bus_list(request):
    buses = Bus.objects.all()
    return render(request, 'booking/bus_list.html', {'buses': buses})


# 🎫 Ticket list
@login_required
def ticket_list(request):
    tickets = Ticket.objects.filter(user=request.user)
    return render(request, 'booking/ticket_list.html', {'tickets': tickets})


# 🎫 Booking (FIXED)
@login_required
def book_ticket(request, bus_id):
    bus = get_object_or_404(Bus, id=bus_id)

    selected_date = request.POST.get('date') or date.today()

    booked_seats = list(
        Ticket.objects.filter(bus=bus, travel_date=selected_date)
        .values_list('seat_number', flat=True)
    )

    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        location = request.POST.get('location')
        seat = request.POST.get('seat')
        travel_date = request.POST.get('date')

        if not name or not seat or not travel_date:
            messages.error(request, "Please fill all required fields!")
            return redirect('book_ticket', bus_id=bus.id)

        if Ticket.objects.filter(bus=bus, seat_number=seat, travel_date=travel_date).exists():
            messages.error(request, "❌ This seat is already booked!")
            return redirect('book_ticket', bus_id=bus.id)

        ticket = Ticket.objects.create(
            user=request.user,
            bus=bus,
            passenger_name=name,
            phone=phone,
            location=location,
            seat_number=seat,
            travel_date=travel_date
        )

        # 🔥 QR FIXED
        qr = qrcode.make(str(ticket.ticket_id))

        qr_folder = os.path.join(settings.MEDIA_ROOT, 'qr_codes')
        os.makedirs(qr_folder, exist_ok=True)

        filename = f"{ticket.ticket_id}.png"
        path = os.path.join(qr_folder, filename)
        qr.save(path)

        ticket.qr_code = f"qr_codes/{filename}"
        ticket.save()

        # 🔥 Email FIXED
        send_mail(
            "🚌 Bus Ticket Confirmed",
            f"""
Ticket ID: {ticket.ticket_id}
Bus: {bus.name}
Seat: {seat}
Date: {travel_date}
Route: {bus.route}
""",
            settings.EMAIL_HOST_USER,
            [request.user.email],
            fail_silently=True,
        )

        messages.success(request, "✅ Booking Confirmed!")
        return redirect('ticket_list')

    return render(request, 'booking/book_ticket.html', {
        'bus': bus,
        'booked_seats': booked_seats
    })


# 📄 PDF DOWNLOAD (WITH QR)
@login_required
def download_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id, user=request.user)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="ticket.pdf"'

    p = canvas.Canvas(response)

    p.drawString(100, 800, f"Ticket ID: {ticket.ticket_id}")
    p.drawString(100, 770, f"Name: {ticket.passenger_name}")
    p.drawString(100, 740, f"Bus: {ticket.bus.name}")
    p.drawString(100, 710, f"Seat: {ticket.seat_number}")
    p.drawString(100, 680, f"Date: {ticket.travel_date}")
    p.drawString(100, 650, f"Route: {ticket.bus.route}")

    # 🔥 QR in PDF
    if ticket.qr_code:
        qr_path = os.path.join(settings.MEDIA_ROOT, str(ticket.qr_code))
        if os.path.exists(qr_path):
            p.drawImage(qr_path, 350, 650, width=150, height=150)

    p.save()
    return response