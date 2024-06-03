from django.urls import path
from . import viewsEvent

urlpatterns = [
    path('create/', viewsEvent.create_event, name='create_event'),
    path('update/<int:event_id>', viewsEvent.update_event, name='update_event'),
    path('<int:event_id>/', viewsEvent.event_detail, name='event_detail'),
    path('delete/<int:event_id>/', viewsEvent.delete_event, name='delete_event'),
    path('myEvents/', viewsEvent.my_events, name='my_events'),
    path("", viewsEvent.home, name="home_events"),
]
