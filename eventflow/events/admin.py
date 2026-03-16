from django.contrib import admin
from .models import Event, Booking, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'color']


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'organizer', 'category', 'start_date', 'status', 'capacity']
    list_filter = ['status', 'category']
    search_fields = ['title', 'venue', 'city']


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['booking_reference', 'attendee', 'event', 'seats', 'status', 'booked_at']
    list_filter = ['status']
    search_fields = ['booking_reference', 'attendee__username']