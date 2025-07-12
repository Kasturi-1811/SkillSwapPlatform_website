from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.models import User

from .models import UserProfile, Skill, SwapRequest
from .forms import ProfileForm, SwapRequestForm, CustomUserCreationForm

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            login(request, user)
            messages.success(request, f"Welcome, {user.username}!")
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'skill_swap/register.html', {'form': form})

def home(request):
    # Start with all public profiles, excluding the logged in user
    if request.user.is_authenticated:
        profiles = UserProfile.objects.filter(is_public=True).exclude(user=request.user)
    else:
        profiles = UserProfile.objects.filter(is_public=True)

    query = request.GET.get('q')
    availability = request.GET.get('availability')

    if query:
        # Filter profiles who offer skills with name containing the query (case-insensitive)
        profiles = profiles.filter(skills_offered__name__icontains=query).distinct()

    if availability:
        profiles = profiles.filter(availability__icontains=availability)

    return render(request, 'skill_swap/home.html', {'profiles': profiles})


@login_required
def profile(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('profile')
    else:
        form = ProfileForm(instance=user_profile)

    return render(request, 'skill_swap/profile.html', {'form': form})

@login_required
def user_profile(request, user_id):
    # View another user's profile page
    other_user = get_object_or_404(User, pk=user_id)
    profile = get_object_or_404(UserProfile, user=other_user)
    return render(request, 'skill_swap/user_profile.html', {'profile': profile})

@login_required
def send_swap_request(request, user_id):
    to_user = get_object_or_404(User, pk=user_id)
    to_profile = get_object_or_404(UserProfile, user=to_user)
    from_profile = get_object_or_404(UserProfile, user=request.user)

    # Only allow skills that user offers and skills that the to_user wants
    offered_skills = from_profile.skills_offered.all()
    requested_skills = to_profile.skills_wanted.all()

    if request.method == 'POST':
        form = SwapRequestForm(request.POST)
        form.fields['offered_skill'].queryset = offered_skills
        form.fields['requested_skill'].queryset = requested_skills

        if form.is_valid():
            swap = form.save(commit=False)
            swap.from_user = request.user
            swap.to_user = to_user
            swap.save()
            messages.success(request, "Swap request sent!")
            return redirect('user_profile', user_id=to_user.id)
    else:
        form = SwapRequestForm()
        form.fields['offered_skill'].queryset = offered_skills
        form.fields['requested_skill'].queryset = requested_skills

    return render(request, 'skill_swap/swap_request.html', {'form': form, 'to_user': to_user})

@login_required
def swap_list(request):
    received = SwapRequest.objects.filter(to_user=request.user)
    sent = SwapRequest.objects.filter(from_user=request.user)
    return render(request, 'skill_swap/swap_list.html', {'received': received, 'sent': sent})
