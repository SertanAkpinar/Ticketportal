from ..models import Event
import django.forms as forms
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models import Q
from datetime import datetime


class DateInput(forms.DateInput):
    input_type = 'date'


class TimeInput(forms.TimeInput):
    input_type = 'time'


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = (
            'eventName',
            'image',
            'video_url',
            'video',
            'start_date',
            'start_time',
            'end_date',
            'end_time',
            'category',
            'venue',
            'tickets',
            'ticket_price',
            'currency',
            'artistName',
            'description',
        )

    start_time = forms.TimeField(widget=TimeInput(format='%H:%M', attrs={'step': 300}))
    end_time = forms.TimeField(widget=TimeInput(format='%H:%M', attrs={'step': 300}))
    start_date = forms.DateField(widget=DateInput())
    end_date = forms.DateField(widget=DateInput(), required=False)
    image = forms.ImageField(required=False)
    ticket_price = forms.DecimalField(required=False)
    video_url = forms.URLField(required=False)

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        ticket_price = cleaned_data.get('ticket_price')
        tickets = cleaned_data.get('tickets')
        video_url = cleaned_data.get('video_url')
        video = cleaned_data.get('video')
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        venue = cleaned_data.get('venue')

        if not video_url and not video:
            raise ValidationError('Either video or video_url must be provided.')

        if start_date and start_date < timezone.now().date():
            raise ValidationError('The start date can not be in the past.')

        if end_date and end_date < start_date:
            raise ValidationError('The end date has to be after the start date.')

        if start_time and timezone.make_aware(datetime.combine(start_date, start_time)) < timezone.now():
            raise ValidationError('The start time can not be in the past.')

        if end_time and end_time < start_time:
            raise ValidationError('The end time has to be after the start time.')

        if ticket_price is not None and ticket_price < 0:
            raise ValidationError('The Ticket price must be 0 or greater.')

        if tickets < 1:
            raise ValidationError('The Ticket must be more the 1.')

        if not end_date:
            cleaned_data['end_date'] = start_date

        if venue and start_date and start_time:
            overlapping_events = Event.objects.filter(
                venue=venue,
                start_date=start_date,
            ).exclude(id=self.instance.id)
            overlapping_events = overlapping_events.filter(
                (
                        (Q(start_time__lt=start_time) & Q(end_time__gt=end_time)) |
                        (Q(start_time__lt=end_time) & Q(end_time__gt=end_time)) |
                        (Q(start_time__gte=start_time) & Q(end_time__lte=end_time)) |
                        (Q(start_time__lte=start_time) & Q(end_time__gte=end_time)) |
                        (Q(start_time__gte=start_time) & Q(start_time__lt=end_time)) |
                        (Q(end_time__gt=start_time) & Q(end_time__lte=end_time))
                )
            )
            # existing_event_end_time = overlapping_events.aggregate(Max('end_time'))['end_time__max']

            if overlapping_events.exists():  # or (existing_event_end_time and start_time < existing_event_end_time):
                raise ValidationError(
                    'Es gibt bereits ein Event in diesem Veranstaltungsort während des angegebenen Zeitraums.')
        return cleaned_data
