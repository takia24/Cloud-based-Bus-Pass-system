from django.contrib import admin
from .models import Bus, Ticket


# 🟢 Bus Admin
@admin.register(Bus)
class BusAdmin(admin.ModelAdmin):
    list_display = ('name', 'route', 'price')
    search_fields = ('name', 'route')
    list_filter = ('route',)
    ordering = ('name',)


# 🟢 Ticket Admin
@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = (
        'ticket_id',
        'passenger_name',
        'phone',
        'location',
        'seat_number',
        'travel_date',
        'bus'
    )

    search_fields = (
        'passenger_name',
        'phone',
        'ticket_id'
    )

    list_filter = (
        'bus',
        'travel_date'
    )

    ordering = ('-id',)

    readonly_fields = ('ticket_id',)

    # 🔥 field grouping (form UI clean)
    fieldsets = (
        ('Passenger Info', {
            'fields': ('passenger_name', 'phone', 'location')
        }),
        ('Booking Info', {
            'fields': ('bus', 'seat_number', 'travel_date')
        }),
        ('System Info', {
            'fields': ('ticket_id',)
        }),
    )