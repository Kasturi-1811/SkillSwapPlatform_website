from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from .models import UserProfile, Skill, SwapRequest, PlatformMessage
from .forms import ProfileForm, SwapRequestForm, CustomUserCreationForm
from django.contrib.admin.views.decorators import staff_member_required
import csv


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            # Create UserProfile with is_public=True
            profile, created = UserProfile.objects.get_or_create(user=user)
            if created:
                profile.is_public = True
                # Also set initial data from form if relevant:
                profile.location = form.cleaned_data.get('location', '')
                profile.phone_number = form.cleaned_data.get('phone_number', '')
                profile.availability = form.cleaned_data.get('availability', '')
                if request.FILES.get('profile_photo'):
                    profile.profile_photo = request.FILES['profile_photo']
                profile.save()

            login(request, user)
            messages.success(request, f"Welcome, {user.username}!")
            return redirect('home')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CustomUserCreationForm()
    return render(request, 'skill_swap/register.html', {'form': form})

from django.db.models import Q

@login_required
def home(request):
    if request.user.is_authenticated:
        # Show profiles that are public OR belong to the logged-in user
        profiles = UserProfile.objects.filter(
            Q(is_public=True) | Q(user=request.user)
        )
        
        # Filter by search query and availability if given
        query = request.GET.get('q')
        availability = request.GET.get('availability')

        if query:
            profiles = profiles.filter(skills_offered__name__icontains=query).distinct()

        if availability:
            profiles = profiles.filter(availability__icontains=availability)

        incoming_requests = SwapRequest.objects.filter(
            to_user=request.user,
            is_accepted=False,
            is_rejected=False,
        ).select_related('from_user', 'offered_skill', 'requested_skill')
    else:
        # For anonymous users, show only public profiles
        profiles = UserProfile.objects.filter(is_public=True)
        incoming_requests = None

    context = {
        'profiles': profiles,
        'incoming_requests': incoming_requests,
    }
    return render(request, 'skill_swap/home.html', context)

@login_required
def accept_swap_request(request, request_id):
    swap_request = get_object_or_404(SwapRequest, id=request_id, to_user=request.user)
    if request.method == 'POST':
        swap_request.is_accepted = True
        swap_request.save()
        messages.success(request, f"Swap request from {swap_request.from_user.username} accepted!")
        return HttpResponseRedirect(reverse('home'))
    return HttpResponseRedirect(reverse('home'))


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
    other_user = get_object_or_404(User, pk=user_id)
    profile = get_object_or_404(UserProfile, user=other_user)
    return render(request, 'skill_swap/user_profile.html', {'profile': profile})


@login_required
def send_swap_request(request, user_id):
    to_user = get_object_or_404(User, pk=user_id)
    to_profile = get_object_or_404(UserProfile, user=to_user)
    from_profile = get_object_or_404(UserProfile, user=request.user)

    offered_skills = from_profile.skills_offered.all()
    requested_skills = to_profile.skills_wanted.all()

    if request.method == 'POST':
        form = SwapRequestForm(request.POST)
        # **Set the queryset here on POST as well**
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
        # **Set the queryset here on GET**
        form.fields['offered_skill'].queryset = offered_skills
        form.fields['requested_skill'].queryset = requested_skills

    return render(request, 'skill_swap/swap_request.html', {'form': form, 'to_user': to_user})

@login_required
def swap_list(request):
    received = SwapRequest.objects.filter(to_user=request.user)
    sent = SwapRequest.objects.filter(from_user=request.user)
    return render(request, 'skill_swap/swap_list.html', {'received': received, 'sent': sent})


@staff_member_required
def admin_dashboard(request):
    pending_skills = Skill.objects.filter(is_approved=False)
    banned_users = UserProfile.objects.filter(is_banned=True)
    swaps_pending = SwapRequest.objects.filter(is_accepted=False, is_rejected=False)
    swaps_accepted = SwapRequest.objects.filter(is_accepted=True)
    swaps_rejected = SwapRequest.objects.filter(is_rejected=True)

    context = {
        'pending_skills': pending_skills,
        'banned_users': banned_users,
        'swaps_pending': swaps_pending,
        'swaps_accepted': swaps_accepted,
        'swaps_rejected': swaps_rejected,
    }
    return render(request, 'skill_swap/admin_dashboard.html', context)


@staff_member_required
def approve_skill(request, skill_id):
    skill = get_object_or_404(Skill, id=skill_id)
    skill.is_approved = True
    skill.save()
    messages.success(request, f"Skill '{skill.name}' approved.")
    return redirect('admin_dashboard')


@staff_member_required
def reject_skill(request, skill_id):
    skill = get_object_or_404(Skill, id=skill_id)
    skill.delete()
    messages.success(request, f"Skill '{skill.name}' rejected and deleted.")
    return redirect('admin_dashboard')


@staff_member_required
def ban_user(request, user_id):
    profile = get_object_or_404(UserProfile, user__id=user_id)
    profile.is_banned = True
    profile.save()
    messages.success(request, f"User '{profile.user.username}' has been banned.")
    return redirect('admin_dashboard')


@staff_member_required
def unban_user(request, user_id):
    profile = get_object_or_404(UserProfile, user__id=user_id)
    profile.is_banned = False
    profile.save()
    messages.success(request, f"User '{profile.user.username}' has been unbanned.")
    return redirect('admin_dashboard')


@staff_member_required
def send_platform_message(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        PlatformMessage.objects.create(title=title, content=content)
        messages.success(request, "Platform-wide message sent.")
        return redirect('admin_dashboard')
    return render(request, 'skill_swap/send_platform_message.html')


@staff_member_required
def download_report(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="user_swap_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Username', 'Is Banned', 'Skills Offered', 'Skills Wanted', 'Swaps Sent', 'Swaps Received'])

    users = UserProfile.objects.all()
    for profile in users:
        swaps_sent = SwapRequest.objects.filter(from_user=profile.user).count()
        swaps_received = SwapRequest.objects.filter(to_user=profile.user).count()
        writer.writerow([
            profile.user.username,
            profile.is_banned,
            ", ".join(s.name for s in profile.skills_offered.all()),
            ", ".join(s.name for s in profile.skills_wanted.all()),
            swaps_sent,
            swaps_received,
        ])

    return response


