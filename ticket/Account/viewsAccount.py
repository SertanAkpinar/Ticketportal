from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib import messages
from .form import UserSignupForm, UserUpdateForm, UserPwChangeForm, ProfileEditForm
from ..models import Profile, Event, Venue


def signup_user(request):
    if request.method == 'POST':
        form = UserSignupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your account has been successfully created! You are now able to log in.')
            return redirect('login')
    else:
        form = UserSignupForm()
    context = {
        'title': 'Sign Up',
        'form': form,
    }
    return render(request, 'registration/signup.html', context)


@login_required
def edit_user(request):
    form_update_user = UserUpdateForm(request.POST, instance=request.user)
    form_change_password = UserPwChangeForm(request.user)
    profile = request.user.profile
    form_edit_profile = ProfileEditForm(request.POST, request.FILES, instance=profile)
    if request.method == 'POST':
        if 'edit_profile' in request.POST:
            form_edit_profile = ProfileEditForm(request.POST, request.FILES, instance=profile)
            if form_edit_profile.is_valid():
                form_edit_profile.save()
                messages.success(request, 'Your profile has been successfully updated!')
                return redirect('profile', pk=profile.id)
            else:
                messages.warning(request, 'Please correct the error below.')
                return redirect('edit_user')
        if 'update_user' in request.POST:
            form_update_user = UserUpdateForm(request.POST, instance=request.user)
            if form_update_user.is_valid():
                form_update_user.save()
                messages.success(request, 'Your account has been successfully updated!')
                return redirect('profile', pk=profile.id)
            else:
                messages.warning(request, 'Please correct the error below.')
                return redirect('edit_user')
        elif 'change_password' in request.POST:
            form_change_password = UserPwChangeForm(request.user, request.POST)
            if form_change_password.is_valid():
                user = form_change_password.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Your password has been successfully updated!')
                return redirect('profile', pk=profile.id)
            else:
                messages.warning(request, 'Please correct the error below.')
                return redirect('edit_user')
        elif 'delete_user' in request.POST:
            request.user.delete()
            return redirect('home')
    else:
        form_update_user = UserUpdateForm(instance=request.user)
        form_change_password = UserPwChangeForm(request.user)
        form_edit_profile = ProfileEditForm(instance=profile)
    context = {
        'title': 'Account Settings',
        'form_update_user': form_update_user,
        'form_change_password': form_change_password,
        'form_edit_profile': form_edit_profile,
    }
    return render(request, 'editAccount.html', context)


def login_user(request):
    if request.method == 'POST':
        if 'username' in request.POST and 'password' in request.POST:
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.warning(request, 'Invalid username or password.')
        else:
            return redirect('login')

    context = {
        'title': 'Login',
    }
    return render(request, 'registration/login.html', context)


def profiles_view(request):
    if request.user.is_authenticated:
        profiles = Profile.objects.exclude(user=request.user)
    else:
        messages.warning(request, 'You must be logged in to view this page.')
        return redirect('login')

    context = {
        'title': 'Profile List',
        'profiles': profiles,
    }
    return render(request, 'profileList.html', context)


def profile_view(request, pk):
    if request.user.is_authenticated:
        profile = get_object_or_404(Profile, id=pk)
        owned_events = Event.objects.filter(owner=profile)
        owned_venues = Venue.objects.filter(owner=profile)
    else:
        messages.warning(request, 'You must be logged in to view this page.')
        return redirect('login')

    context = {
        'title': 'Profile',
        'profile': profile,
        'owned_events': owned_events,
        'owned_venues': owned_venues,
    }
    return render(request, 'profile.html', context)
