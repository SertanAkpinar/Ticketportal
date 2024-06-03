from django import forms

from ticket.models import Venue


class VenueForm(forms.ModelForm):
    class Meta:
        model = Venue
        fields = (
            'name',
            'location',
            'capacity',
            'extraDetails',
            'google_maps_address',
            'venue_image',
        )
