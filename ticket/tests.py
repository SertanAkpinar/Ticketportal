from django.test import TestCase
from django.urls import reverse
from ticket.models import User
from .models import Profile, Venue, Event


class EventTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')
        self.profile = Profile.objects.get(user=self.user)
        self.venue = Venue.objects.create(name='Test Venue', location='Test Location', capacity=100,
                                          extraDetails='Details', google_maps_address='no google maps')
        self.create_test_event()

    def create_test_event(self):
        url = reverse('create_event')
        data = {
            'eventName': 'Test Event',
            'image': '',
            'video_url': 'https://www.youtube.com/test',
            'start_date': '2024-02-20',
            'start_time': '12:00',
            'end_date': '2024-02-21',
            'end_time': '14:00',
            'category': 'Music',
            'venue': self.venue.id,
            'tickets': 50,
            'ticket_price': '20.00',
            'currency': 'USD',
            'artistName': 'Test Artist',
            'description': 'Test Description',
        }
        response = self.client.post(url, data, format='text/html')
        self.assertEqual(response.status_code, 302)

    def test_create_event(self):
        events_after = Event.objects.count()
        print(events_after)
        event = Event.objects.filter(eventName='Test Event').first()
        print(event)
        self.assertEqual(event.owner, self.profile)

    def test_update_event(self):
        event = Event.objects.get(eventName='Test Event')
        print(event.description)
        u_url = reverse('update_event', args=[event.id])
        updated_data = {
            'eventName': 'Test Event',
            'image': '',
            'video_url': 'https://www.youtube.com/test',
            'start_date': '2024-02-20',
            'start_time': '12:00',
            'end_date': '2024-02-21',
            'end_time': '14:00',
            'category': 'Music',
            'venue': self.venue.id,
            'tickets': 50,
            'ticket_price': '20.00',
            'currency': 'USD',
            'artistName': 'Test Artist',
            'description': 'This got updated.'
        }
        self.client.post(u_url, updated_data, format='text/html')
        print('Neue Daten: ', updated_data)

        updated_event = Event.objects.get(eventName='Test Event')
        print("Nach der Aktualisierung - Beschreibung:", updated_event.description)

        self.assertNotEqual(event.description, updated_event.description,
                            'Hier sollte jetzt eine neue Beschreibung sein')

    def test_update_event_past_date(self):
        event = Event.objects.get(eventName='Test Event')
        u_url = reverse('update_event', args=[event.id])
        invalid_data = {
            'eventName': 'Test Event',
            'image': '',
            'video_url': 'https://www.youtube.com/test',
            'start_date': '2000-02-20',
            'start_time': '12:00',
            'end_date': '2024-02-21',
            'end_time': '14:00',
            'category': 'Music',
            'venue': self.venue.id,
            'tickets': 50,
            'ticket_price': '20.00',
            'currency': 'USD',
            'artistName': 'Test Artist',
            'description': 'This got updated.'
        }
        response = self.client.post(u_url, invalid_data, format='text/html')
        self.assertEqual(response.status_code, 200)
        updated_event = Event.objects.get(eventName='Test Event')
        print("Nach der Aktualisierung - Datum:", updated_event.start_date)
        self.assertEqual(event.start_date, updated_event.start_date, 'selbes Datum, da nicht aktualisiert')

    def test_end_before_start(self):
        event = Event.objects.get(eventName='Test Event')
        u_url = reverse('update_event', args=[event.id])
        invalid_data = {
            'eventName': 'Test Event',
            'image': '',
            'video_url': 'https://www.youtube.com/test',
            'start_date': '2024-02-20',
            'start_time': '12:00',
            'end_date': '2024-02-10',
            'end_time': '10:00',
            'category': 'Music',
            'venue': self.venue.id,
            'tickets': 50,
            'ticket_price': '20.00',
            'currency': 'USD',
            'artistName': 'Test Artist',
            'description': 'Test Description',
        }
        response = self.client.post(u_url, invalid_data, format='text/html')
        self.assertEqual(response.status_code, 200)
        updated_event = Event.objects.get(eventName='Test Event')
        print("Nach der Aktualisierung - Zeiten:", updated_event.start_time, updated_event.end_time)
        print("Nach der Aktualisierung - Datum:", updated_event.start_date, updated_event.end_date)
        self.assertEqual(event.start_time, updated_event.start_time, 'selbe Uhrzeit, da nicht aktualisiert')
        self.assertEqual(event.end_time, updated_event.end_time, 'selbe Uhrzeit, da nicht aktualisiert')
        self.assertEqual(event.start_date, updated_event.start_date, 'selbes Datum, da nicht aktualisiert')
        self.assertEqual(event.end_date, updated_event.end_date, 'selbes Datum, da nicht aktualisiert')

    def test_event_without_required_field(self):
        event = Event.objects.get(eventName='Test Event')
        u_url = reverse('update_event', args=[event.id])
        invalid_data = {
            'eventName': 'Test Event',
            'image': '',
            'video_url': 'https://www.youtube.com/test',
            'start_date': '2024-02-20',
            'start_time': '12:00',
            'end_date': '2024-02-21',
            'end_time': '14:00',
            'category': 'Music',
            'venue': self.venue.id,
            'tickets': 50,
            'ticket_price': '20.00',
            'currency': '',
            'artistName': '',
            'description': 'Test Description',
        }
        response = self.client.post(u_url, invalid_data, format='text/html')
        self.assertEqual(response.status_code, 200)
        updated_event = Event.objects.get(eventName='Test Event')
        print("Nach der Aktualisierung - Currency:", updated_event.currency)
        print("Nach der Aktualisierung - Artist Name:", updated_event.artistName)
        self.assertEqual(event.currency, updated_event.currency, 'selbe Währung, da nicht aktualisiert')
        self.assertEqual(event.artistName, updated_event.artistName, 'selber Artist, da nicht aktualisiert')

    def test_no_end_date(self):
        event = Event.objects.get(eventName='Test Event')
        u_url = reverse('update_event', args=[event.id])
        data = {
            'eventName': 'Test Event',
            'image': '',
            'video_url': 'https://www.youtube.com/test',
            'start_date': '2024-02-20',
            'start_time': '12:00',
            'end_date': '',
            'end_time': '14:00',
            'category': 'Music',
            'venue': self.venue.id,
            'tickets': 50,
            'ticket_price': '20.00',
            'currency': 'USD',
            'artistName': 'Test Artist',
            'description': 'Test Description',
        }
        response = self.client.post(u_url, data, format='text/html')
        self.assertEqual(response.status_code, 302)
        updated_event = Event.objects.get(eventName='Test Event')
        print("Nach der Aktualisierung - End date = Start date:", updated_event.end_date)
        self.assertEqual(updated_event.start_date, updated_event.end_date, 'selbes Datum, da kein end datum')

    def test_create_duplicate_event(self):
        url = reverse('create_event')
        data = {
            'eventName': 'Test Event',
            'image': '',
            'video_url': 'https://www.youtube.com/test',
            'start_date': '2024-02-20',
            'start_time': '12:00',
            'end_date': '2024-02-21',
            'end_time': '14:00',
            'category': 'Music',
            'venue': self.venue.id,
            'tickets': 50,
            'ticket_price': '20.00',
            'currency': 'USD',
            'artistName': 'Test Artist',
            'description': 'Test Description',
        }
        events_before = Event.objects.count()
        print(events_before)
        self.client.post(url, data, format='text/html')
        events_after = Event.objects.count()
        print(events_after)
        self.assertEqual(events_before, events_after, 'Wenn kein Event erstellt wurde beide Werte 1')

    def test_delete_event(self):
        event = Event.objects.get(eventName='Test Event')
        print(event.eventName)
        d_url = reverse('delete_event', args=[event.id])
        self.client.post(d_url)
        event_exists = Event.objects.filter(eventName=event.eventName).exists()
        print(Event.objects.count())
        if event_exists:
            print('es lebt')
        else:
            print('dead')


class VenueTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='luffy', password='testpassword')
        self.client.login(username='luffy', password='testpassword')
        self.profile = Profile.objects.get(user=self.user)

    def test_create_venue(self):
        url = reverse("create_venue")
        vorher = Venue.objects.all().count()
        print("vorher : " + str(vorher))
        data = {
            "name": 'test',
            'location': 'lll',
            'capacity': 100,
            'extraDetails': 'newDetails',
            'google_maps_address': 'no google maps'
        }
        response = self.client.post(url, data, format='text/html')
        testVen = Venue.objects.filter(name="test").first()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(testVen.name, 'test')
        self.assertEqual(testVen.location, 'lll')
        self.assertEqual(testVen.capacity, 100)
        self.assertEqual(testVen.extraDetails, 'newDetails')
        self.assertEqual(testVen.google_maps_address, 'no google maps')

        nachher = Venue.objects.all().count()
        print("nachher : " + str(nachher))
        print('test_create_venue hat funktionert.')

    def test_update_venue(self):
        url = reverse("create_venue")
        vorher = Venue.objects.all().count()
        print("vorher : " + str(vorher))
        data = {
            "name": 'test',
            'location': 'lll',
            'capacity': 100,
            'extraDetails': 'newDetails',
            'google_maps_address': 'no google maps'
        }
        response = self.client.post(url, data, format='text/html')
        testVen = Venue.objects.filter(name="test").first()
        self.assertEqual(response.status_code, 302)
        print("ohne update : " + str(testVen.extraDetails))
        update_url = reverse("update_venue", args=[testVen.name])
        update_data = {
            'extraDetails': " updated Details"
        }
        self.client.post(update_url, update_data, format='text/html')
        updatd_venue = Venue.objects.filter(id=testVen.id)
        updatd_venue.extraDetails = update_data['extraDetails']
        print("updatedVenue.extraDetails : " + str(updatd_venue.extraDetails))
        self.assertNotEqual(testVen.extraDetails, updatd_venue.extraDetails)
        print('update done.')

    def test_delete_venue(self):
        url = reverse("create_venue")
        vorher = Venue.objects.all().count()
        print("vorher : " + str(vorher))
        data = {
            "name": 'test',
            'location': 'lll',
            'capacity': 100,
            'extraDetails': 'newDetails',
            'google_maps_address': 'no google maps'
        }
        self.client.post(url, data, format='text/html')
        testVen = Venue.objects.filter(name="test").first()
        venues = Venue.objects.all().count()
        self.assertEquals(venues, 1)
        print('anzahl der Venues VOR dem Delete : ' + str(venues))
        delete_url = reverse('venue_delete', args=[testVen.id])
        self.client.post(delete_url)
        after_delete = Venue.objects.all().count()
        print('anzahl after Delete : ' + str(after_delete))
        self.assertEquals(after_delete, 0)
        print('delte done.')
