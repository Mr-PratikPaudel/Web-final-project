from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Event, Booking, Category
from .serializers import EventSerializer, BookingSerializer, CategorySerializer


class IsOrganizerOrReadOnly(permissions.BasePermission):
    """Allow only event organizers to modify their events."""
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if hasattr(obj, 'organizer'):
            return obj.organizer == request.user
        if hasattr(obj, 'attendee'):
            return obj.attendee == request.user
        return False


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class EventViewSet(viewsets.ModelViewSet):
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizerOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'venue', 'city']
    ordering_fields = ['start_date', 'price', 'created_at']
    ordering = ['start_date']

    def get_queryset(self):
        queryset = Event.objects.select_related('organizer', 'category').prefetch_related('bookings')
        status_filter = self.request.query_params.get('status')
        category = self.request.query_params.get('category')
        city = self.request.query_params.get('city')
        my_events = self.request.query_params.get('my_events')

        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if category:
            queryset = queryset.filter(category_id=category)
        if city:
            queryset = queryset.filter(city__icontains=city)
        if my_events == 'true':
            queryset = queryset.filter(organizer=self.request.user)

        return queryset

    def perform_create(self, serializer):
        serializer.save(organizer=self.request.user)

    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel_event(self, request, pk=None):
        event = self.get_object()
        if event.organizer != request.user:
            return Response({'error': 'Only the organizer can cancel this event.'}, status=403)
        event.status = 'cancelled'
        event.save()
        event.bookings.filter(status='confirmed').update(status='cancelled')
        return Response({'message': 'Event cancelled and all bookings updated.'})


class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizerOrReadOnly]

    def get_queryset(self):
        return Booking.objects.filter(
            attendee=self.request.user
        ).select_related('event', 'event__category', 'attendee')

    def perform_create(self, serializer):
        serializer.save(attendee=self.request.user)

    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel_booking(self, request, pk=None):
        booking = self.get_object()
        if booking.attendee != request.user:
            return Response({'error': 'Not authorized.'}, status=403)
        booking.status = 'cancelled'
        booking.save()
        return Response({'message': 'Booking cancelled successfully.'})