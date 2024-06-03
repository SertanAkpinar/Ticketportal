from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from . import models
from .models import Profile


class ProfileInline(admin.StackedInline):
    model = Profile


class UserAdmin(BaseUserAdmin):
    inlines = [ProfileInline]


@admin.register(models.Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'profile_pic', 'bio']
    list_editable = ['profile_pic', 'bio']
    ordering = ['id']
    list_per_page = 10


@admin.register(models.Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['id', 'active', 'eventName', 'owner', 'venue', 'start_date', 'image',
                    'video', 'video_url', 'description']
    list_editable = ['eventName', 'image', 'video', 'video_url', 'description']
    ordering = ['start_date']
    list_per_page = 10


@admin.register(models.Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ['owner', 'name', 'location', 'capacity', 'extraDetails']
    list_editable = ['name', 'location', 'capacity', 'extraDetails']
    ordering = ['id']
    list_per_page = 10
