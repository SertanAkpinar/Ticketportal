from django.urls import path
from .viewsVenue import all_venues, create_venue, venue_delete, update_venue, specific_venues, \
    is_legit_address

urlpatterns = [
    path("", all_venues, name='venues'),
    path('create', create_venue, name='create_venue'),

    path('update/<str:venue_name>', update_venue, name='update_venue'),

    # path('<str:venue_name>', venue_detail, name='venue_detail'),

    path('<str:venue_name>', is_legit_address, name='venue_detail'),

    path('<str:venue_id>/delete', venue_delete, name='venue_delete'),

    path('myvenues/', specific_venues, name="specific_venues")
]
