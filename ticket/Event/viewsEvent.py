from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from datetime import datetime
from ..models import Event, Profile
from .forms import EventForm


def home(request):
    context = {}
    categories = set()
    now = timezone.localtime(timezone.now())
    for event in Event.objects.all():
        event.update_active_status()
        categories.add(event.category.upper())
    category_choices = [(category, category) for category in categories]

    category = request.GET.get('category')
    if category:
        context['events'] = Event.objects.filter(
            Q(category=category) & (
                    Q(end_date__gt=now.date()) |
                    (Q(end_date=now.date()) & Q(end_time__gt=now.time()))
            )
        ).order_by('start_date')
    else:
        context['events'] = Event.objects.filter(
            Q(end_date__gt=now.date()) |
            (Q(end_date=now.date()) & Q(end_time__gt=now.time()))
        ).order_by('start_date')
    context['category_choices'] = category_choices
    context['selected_category'] = category
    return render(request, 'events.html', context)


def my_events(request):
    context = {}
    categories = set()
    now = timezone.localtime(timezone.now())
    current_user = request.user
    profile = Profile.objects.get(user=current_user)
    for event in Event.objects.filter(owner=profile):
        categories.add(event.category.upper())
    category_choices = [(category, category) for category in categories]

    category = request.GET.get('category')
    if category:
        context['events'] = Event.objects.filter(
            Q(category=category) & (
                    Q(end_date__gt=now.date()) |
                    (Q(end_date=now.date()) & Q(end_time__gt=now.time()))
            )
        ).order_by('start_date')
    else:
        context['events'] = Event.objects.filter(
            Q(end_date__gt=now.date()) |
            (Q(end_date=now.date()) & Q(end_time__gt=now.time()))
        ).order_by('start_date')
    context['category_choices'] = category_choices
    context['selected_category'] = category
    return render(request, 'events.html', context)


def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    remaining_tickets = event.tickets
    context = {'event': event, 'remaining_tickets': remaining_tickets}
    return render(request, 'eventDetails.html', context)


@login_required
def create_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            new_form = form.save(commit=False)
            profile = get_object_or_404(Profile, user=request.user)
            new_form.owner = profile
            new_form.save()
            messages.success(request, 'Your Event is created successfully')
            return redirect('home_events')
    else:
        form = EventForm()
    context = {'form': form, 'title': "Create Event"}
    return render(request, 'createEvent.html', context)


@login_required
def update_event(request, event_id):
    event = Event.objects.get(id=event_id)
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your Event is updated successfully')
            return redirect('event_detail', event_id=event_id)
    else:
        form = EventForm(instance=event)
    context = {'form': form, 'title': "Update Event"}
    return render(request, 'createEvent.html', context)


@login_required
def delete_event(request, event_id):
    event = Event.objects.get(id=event_id)
    if request.method == "POST":
        event.delete()
        messages.success(request, 'Your Event is deleted successfully')
        return redirect('home_events')
    else:
        return render(request, 'eventDetails.html', {'event': event})
