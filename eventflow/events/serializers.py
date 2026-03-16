from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Event, Booking, Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'icon', 'color']


class OrganizerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']


class EventSerializer(serializers.ModelSerializer):
    organizer = OrganizerSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True, required=False
    )
    available_seats = serializers.ReadOnlyField()
    is_sold_out = serializers.ReadOnlyField()
    booking_count = serializers.SerializerMethodField()
    is_booked_by_user = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'category', 'category_id',
            'organizer', 'venue', 'city', 'start_date', 'end_date',
            'capacity', 'price', 'status', 'image_url', 'is_public',
            'available_seats', 'is_sold_out', 'booking_count',
            'is_booked_by_user', 'created_at', 'updated_at'
        ]
        read_only_fields = ['organizer', 'created_at', 'updated_at']

    def get_booking_count(self, obj):
        return obj.bookings.filter(status='confirmed').count()

    def get_is_booked_by_user(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.bookings.filter(attendee=request.user, status='confirmed').exists()
        return False

    def create(self, validated_data):
        validated_data['organizer'] = self.context['request'].user
        return super().create(validated_data)


class BookingSerializer(serializers.ModelSerializer):
    event = EventSerializer(read_only=True)
    event_id = serializers.PrimaryKeyRelatedField(
        queryset=Event.objects.all(), source='event', write_only=True
    )
    attendee = OrganizerSerializer(read_only=True)
    total_price = serializers.ReadOnlyField()

    class Meta:
        model = Booking
        fields = [
            'id', 'event', 'event_id', 'attendee', 'seats',
            'status', 'booking_reference', 'notes',
            'total_price', 'booked_at', 'updated_at'
        ]
        read_only_fields = ['attendee', 'booking_reference', 'booked_at', 'updated_at']

    def validate(self, attrs):
        event = attrs['event']
        seats = attrs.get('seats', 1)
        request = self.context['request']

        if event.available_seats < seats:
            raise serializers.ValidationError(
                f'Only {event.available_seats} seat(s) available.'
            )
        if event.status != 'upcoming':
            raise serializers.ValidationError('This event is no longer accepting bookings.')
        if Booking.objects.filter(event=event, attendee=request.user, status='confirmed').exists():
            raise serializers.ValidationError('You already have a booking for this event.')
        return attrs

    def create(self, validated_data):
        validated_data['attendee'] = self.context['request'].user
        return super().create(validated_data)