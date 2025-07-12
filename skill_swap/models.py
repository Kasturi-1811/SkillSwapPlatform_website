from django.contrib.auth.models import User
from django.db import models

class Skill(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_approved = models.BooleanField(default=True)  # Admin approval for description

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_banned = models.BooleanField(default=False)
    is_public = models.BooleanField(default=True)

    skills_offered = models.ManyToManyField(
        Skill, related_name='offered_by', blank=True
    )
    skills_wanted = models.ManyToManyField(
        Skill, related_name='wanted_by', blank=True
    )

    profile_photo = models.ImageField(
        upload_to='profiles/', blank=True, null=True
    )
    location = models.CharField(max_length=100, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    availability = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.user.username


class SwapRequest(models.Model):
    from_user = models.ForeignKey(
        User, related_name='sent_requests', on_delete=models.CASCADE
    )
    to_user = models.ForeignKey(
        User, related_name='received_requests', on_delete=models.CASCADE
    )
    offered_skill = models.ForeignKey(
        Skill, related_name='offered_in_swaps',
        on_delete=models.CASCADE, null=True, blank=True
    )
    requested_skill = models.ForeignKey(
        Skill, related_name='requested_in_swaps', on_delete=models.CASCADE
    )
    message = models.TextField(blank=True)
    is_accepted = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.from_user.username} → {self.to_user.username}"


class PlatformMessage(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
