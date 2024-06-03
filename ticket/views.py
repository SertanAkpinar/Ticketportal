from datetime import datetime
from django.db.models import Sum, Q
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from ticket.models import Event, Venue, EventTicket, Profile
from django.db.models import Sum


@require_http_methods(["GET"])
def home(request):
    now = timezone.localtime(timezone.now())

    query_all_venues = Venue.objects.all()
    query_all_events = Event.objects.filter(Q(end_date__gt=now.date()) |
                                            (Q(end_date=now.date()) & Q(end_time__gt=now.time()))
                                            ).order_by('start_date')

    # session
    session_value = request.session.get('my_session', 'default session value')
    request.session['my_session'] = 'set session value'
    request.session.save()

    context = {
        "venues": query_all_venues,
        'events': query_all_events,
        'my_session': session_value,
        'title': 'Home'
    }

    response = render(request, 'home.html', context)

    # cookie
    response.set_cookie('last_visit', datetime.now().strftime("%Y-%m-%d %H:%M%S"))

    return response


'''
# Create your views here.
@require_http_methods(["GET"])
def home(request):
    # queries
    query_all_venues = Venue.objects.all()
    query_all_events = Event.objects.all()
    num_cart_items = request.session.get('num_cart_items', 0)

    if request.user.is_authenticated:
        user = request.user
        event_tickets = (
            EventTicket.objects.filter(user=user).aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
        )
        request.session['num_cart_items'] = event_tickets

    # session
    session_value = request.session.get('my_session', 'default session value')
    request.session['my_session'] = 'set session value'
    request.session.save()

    context = {
        "venues": query_all_venues,
        'events': query_all_events,
        'my_session': session_value,
        'num_cart_items': num_cart_items,
        'title': 'Home'
    }

    response = render(request, 'home.html', context)

    # cookie
    response.set_cookie('last_visit', datetime.now().strftime("%Y-%m-%d %H:%M%S"))

    return response
'''
