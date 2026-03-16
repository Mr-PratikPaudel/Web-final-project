from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Event, Booking, Category


def event_list(request):
    events = Event.objects.select_related('organizer', 'category').prefetch_related('bookings')
    categories = Category.objects.all()

    # Filters
    status_filter = request.GET.get('status', '')
    category_filter = request.GET.get('category', '')
    search = request.GET.get('q', '')

    if status_filter:
        events = events.filter(status=status_filter)
    if category_filter:
        events = events.filter(category_id=category_filter)
    if search:
        events = events.filter(title_icontains=search) | events.filter(city_icontains=search)

    context = {
        'events': events,
        'categories': categories,
        'status_filter': status_filter,
        'category_filter': category_filter,
        'search': search,
    }
    return render(request, 'events/event_list.html', context)


@login_required
def event_detail(request, pk):
    event = get_object_or_404(
        Event.objects.select_related('organizer', 'category').prefetch_related('bookings'),
        pk=pk
    )
    user_booking = None
    if request.user.is_authenticated:
        user_booking = event.bookings.filter(attendee=request.user).first()

    context = {'event': event, 'user_booking': user_booking}
    return render(request, 'events/event_detail.html', context)


@login_required
def event_create(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        try:
            event = Event.objects.create(
                title=request.POST['title'],
                description=request.POST['description'],
                venue=request.POST['venue'],
                city=request.POST['city'],
                start_date=request.POST['start_date'],
                end_date=request.POST['end_date'],
                capacity=request.POST.get('capacity', 100),
                price=request.POST.get('price', 0),
                status=request.POST.get('status', 'upcoming'),
                category_id=request.POST.get('category') or None,
                image_url=request.POST.get('image_url', ''),
                organizer=request.user,
            )
            messages.success(request, f'Event "{event.title}" created successfully!')
            return redirect('event_detail', pk=event.pk)
        except Exception as e:
            messages.error(request, f'Error creating event: {e}')

    return render(request, 'events/event_form.html', {'categories': categories, 'action': 'Create'})


@login_required
def event_edit(request, pk):
    event = get_object_or_404(Event, pk=pk, organizer=request.user)
    categories = Category.objects.all()

    if request.method == 'POST':
        try:
            event.title = request.POST['title']
            event.description = request.POST['description']
            event.venue = request.POST['venue']
            event.city = request.POST['city']
            event.start_date = request.POST['start_date']
            event.end_date = request.POST['end_date']
            event.capacity = request.POST.get('capacity', 100)
            event.price = request.POST.get('price', 0)
            event.status = request.POST.get('status', 'upcoming')
            event.category_id = request.POST.get('category') or None
            event.image_url = request.POST.get('image_url', '')
            event.save()
            messages.success(request, 'Event updated successfully!')
            return redirect('event_detail', pk=event.pk)
        except Exception as e:
            messages.error(request, f'Error updating event: {e}')

    return render(request, 'events/event_form.html', {
        'event': event, 'categories': categories, 'action': 'Edit'
    })


@login_required
def event_delete(request, pk):
    event = get_object_or_404(Event, pk=pk, organizer=request.user)
    if request.method == 'POST':
        title = event.title
        event.delete()
        messages.success(request, f'Event "{title}" deleted.')
        return redirect('event_list')
    return render(request, 'events/event_confirm_delete.html', {'event': event})


@login_required
def book_event(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == 'POST':
        seats = int(request.POST.get('seats', 1))
        notes = request.POST.get('notes', '')

        if event.available_seats < seats:
            messages.error(request, f'Only {event.available_seats} seat(s) available.')
        elif Booking.objects.filter(event=event, attendee=request.user, status='confirmed').exists():
            messages.error(request, 'You already have a booking for this event.')
        else:
            booking = Booking.objects.create(
                event=event, attendee=request.user, seats=seats, notes=notes
            )
            messages.success(request, f'Booking confirmed! Reference: {booking.booking_reference}')
            return redirect('my_bookings')

    return redirect('event_detail', pk=pk)


@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(
        attendee=request.user
    ).select_related('event', 'event__category')
    return render(request, 'events/my_bookings.html', {'bookings': bookings})


@login_required
def cancel_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk, attendee=request.user)
    if request.method == 'POST':
        booking.status = 'cancelled'
        booking.save()
        messages.success(request, 'Booking cancelled.')
    return redirect('my_bookings')


@login_required
def dashboard(request):
    user = request.user
    my_events = Event.objects.filter(organizer=user).prefetch_related('bookings')
    my_bookings = Booking.objects.filter(attendee=user, status='confirmed').select_related('event')
    upcoming_events = Event.objects.filter(status='upcoming').order_by('start_date')[:4]

    stats = {
        'total_events': my_events.count(),
        'total_bookings': my_bookings.count(),
        'upcoming': my_events.filter(status='upcoming').count(),
    }

    context = {
        'my_events': my_events,
        'my_bookings': my_bookings,
        'upcoming_events': upcoming_events,
        'stats': stats,
    }
    return render(request, 'events/dashboard.html', context)