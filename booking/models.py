from django.db import models
from django.contrib.auth.models import User
import uuid
from datetime import date, time

class Bus(models.Model):
    name = models.CharField(max_length=100)
    route = models.CharField(max_length=200)
    price = models.IntegerField()

    departure_time = models.TimeField(default=time(8,0))
    arrival_time = models.TimeField(default=time(14,0))

    def __str__(self):
        return f"{self.name} ({self.route})"


class Ticket(models.Model):
    # 🔥 user with default
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)

    bus = models.ForeignKey(Bus, on_delete=models.CASCADE)
    passenger_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    location = models.CharField(max_length=100)

    seat_number = models.CharField(max_length=5)
    travel_date = models.DateField(default=date.today)

    ticket_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['bus', 'seat_number', 'travel_date']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.passenger_name} - {self.bus.name} ({self.seat_number})"