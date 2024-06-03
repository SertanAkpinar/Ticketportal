from datetime import datetime

import qrcode
from io import BytesIO
from django.core.files import File
from PIL import Image, ImageDraw
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.db import models
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.utils import timezone


class User(AbstractUser):
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.username


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_pic = models.ImageField(null=True, blank=True, upload_to='profile/')
    bio = models.TextField(max_length=500, blank=True)

    @admin.display(ordering='user__username')
    def username(self):
        return self.user.username

    def email(self):
        return self.user.email

    def password(self):
        return self.user.password

    def __str__(self):
        return self.user.username


def create_profile(sender, instance, created, **kwargs):
    if created:
        user_profile = Profile.objects.create(user=instance)
        user_profile.save()


post_save.connect(create_profile, sender=User)


class Venue(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    capacity = models.IntegerField()
    extraDetails = models.CharField(max_length=255)
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE, editable=False, default=1)
    google_maps_address = models.CharField(max_length=255, default="no google maps")
    venue_image = models.ImageField(null=True, blank=True, upload_to='Venue_images/')

    def __str__(self):
        return self.name


class Event(models.Model):
    CATEGORY_CHOICES = [('Sport', 'Sport'), ('Music', 'Music'), ('Theater', 'Theater'),
                        ('Art', 'Art'), ('Workshop', 'Workshop'), ('Gaming', 'Gaming'),
                        ('Health', 'Health'), ('Culinary', 'Culinary'), ('Party', 'Party'),
                        ('Movie', 'Movie'), ('Fashion', 'Fashion'), ('Lecture', 'Lecture')]
    CURRENCY = [('USD', 'USD'), ('EUR', 'EUR')]
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE, editable=False)
    eventName = models.CharField(max_length=255)
    image = models.ImageField(null=True, blank=True, upload_to='events/')
    video = models.FileField(null=True, blank=True, upload_to='events/')
    video_url = models.URLField(max_length=255)
    start_date = models.DateField(editable=True)
    start_time = models.TimeField(editable=True)
    end_date = models.DateField(editable=True, null=True)
    end_time = models.TimeField(editable=True)
    category = models.CharField(max_length=255, choices=CATEGORY_CHOICES, default='Art')
    tickets = models.IntegerField()
    ticket_price = models.DecimalField(null=True, max_digits=7, decimal_places=2)
    currency = models.CharField(max_length=3, choices=CURRENCY, default='EUR')
    artistName = models.CharField(max_length=255)
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE)
    description = models.TextField()
    active = models.BooleanField(default=True)

    def is_expired(self):
        now = timezone.localtime(timezone.now())
        event_end_datetime = timezone.make_aware(datetime.combine(self.end_date, self.end_time))
        return now > event_end_datetime

    def update_active_status(self):
        self.active = not self.is_expired()
        self.save()

    def clean(self):
        if self.tickets > self.venue.capacity:
            raise ValidationError(
                f'You can not sell more tickets than capacity in the venue.'
                f'The maximum number of tickets is {self.venue.capacity}')

    def __str__(self):
        return "{} - {} - {} - {} - {}".format(
            self.eventName, self.image, self.category, self.start_date, self.start_time
        )


class EventTicket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='items')
    quantity = models.IntegerField(default=1)
    qr_code = models.ImageField(null=True, blank=True, upload_to='qr_codes/')

    def __str__(self):
        return self.event.eventName

    def save(self, *args, **kwargs):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(self.event.eventName)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="#7393D8", back_color="white")
        canvas = Image.new('RGB', (310, 310), 'white')
        canvas.paste(qr_img)
        file_name = f'{self.event.eventName}.png'
        buffer = BytesIO()
        canvas.save(buffer, 'PNG')
        self.qr_code.save(file_name, File(buffer), save=False)
        canvas.close()
        super().save(*args, **kwargs)
