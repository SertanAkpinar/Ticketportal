from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render, get_object_or_404
from ticket.Venue.forms import VenueForm
from ticket.models import Venue
from ticket.models import Profile
from ticket.models import Event
from django.contrib import messages


def create_venue(request):
    # request.user ist der aktuell eingeloggte user
    if request.method == 'POST':
        form = VenueForm(request.POST, request.FILES)
        if form.is_valid():
            new_form = form.save(
                commit=False)  # speichert die form nicht drekt in der DB -> einzelne felder kann man damit nochmal bearbeiten
            profile = get_object_or_404(Profile,
                                        user=request.user)  # gibt das Profile mit user = request.user wieder ODER eine 404 falls es das Profil nicht gibt
            new_form.owner = profile
            new_form.save()  # speichert die neue form in der DB
            messages.success(request, 'Venue created !')

            response = redirect('venues')  # redirect zu home
            return response

    else:
        form = VenueForm()
    context = {'form': form, 'title': 'Create Venue'}
    response = render(request, 'create_venue.html', context)
    return response


def all_venues(request):
    ## query erstellen die alle Venue Objekte enthalten tut
    query_all = Venue.objects.all()
    context = {"title": "Venues", 'venues': query_all}
    return render(request, 'venues.html', context)


# venues vom eingeloggten user
def specific_venues(request):
    current_user = request.user
    profile = Profile.objects.get(user=current_user)
    venues = Venue.objects.filter(owner=profile)
    context = {'title': 'My Venues', 'venues': venues, 'user': current_user}
    response = render(request, 'venues.html', context)
    return response


@login_required
def update_venue(request, venue_name):
    venue = get_object_or_404(Venue, name=venue_name)
    if request.method == 'POST':
        form = VenueForm(request.POST, request.FILES, instance=venue)
        if form.is_valid():
            form.save()
            messages.success(request, 'Venue has been updated !')

            return redirect('/venues', name=venue_name)
    else:
        form = VenueForm(instance=venue)
    context = {'form': form, 'title': 'Update'}
    return render(request, 'create_venue.html', context)


# DAS IST VERALTET UND WIRD NICHT MEHR BENUTZT, DAFÜR HABE ICH DIE is_legit_adress FUNCTION UNTEN
@login_required
def venue_detail(request, venue_name):
    venue = get_object_or_404(Venue, name=venue_name)
    events = Event.objects.filter(venue=venue)
    context = {'venue': venue, 'events': events}
    response = render(request, 'venue_detail.html', context)
    response.set_cookie('venue_name', venue_name)
    return response


@login_required
def venue_delete(request, venue_id):
    venue = Venue.objects.get(id=venue_id)
    if request.method == "POST":
        venue.delete()
        messages.success(request, 'Venue deleted !')

        return redirect('venues')
    else:
        context = {"venue": venue}
        return render(request, 'venue_detail.html', context)


def is_legit_address(request, venue_name):
    venue = get_object_or_404(Venue, name=venue_name)
    address = venue.google_maps_address

    if address.startswith("https://www.google.com/maps/"):
        events = Event.objects.filter(venue=venue)
        context = {'venue': venue, 'events': events}
        response = render(request, 'venue_detail.html', context)
        response.set_cookie("address", address)
    else:
        events = Event.objects.filter(venue=venue)
        context = {'venue': venue, 'events': events}
        response = render(request, 'noGoogleMapsVenue.html', context)
        response.set_cookie("address", address)

    return response
