from django.db import models
from django.contrib.auth.models import User

# List of availability options
AVAILABILITY_CHOICES = [
    ('weekends', 'Weekends'),
    ('evenings', 'Evenings'),
    ('weekdays', 'Weekdays'),
    ('anytime', 'Anytime'),
]

class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    location = models.CharField(max_length=100, blank=True, null=True)
    profile_photo = models.ImageField(upload_to='profiles/', blank=True, null=True)
    skills_offered = models.ManyToManyField(Skill, related_name='offered_by', blank=True)
    skills_wanted = models.ManyToManyField(Skill, related_name='wanted_by', blank=True)
    availability = models.CharField(max_length=20, choices=AVAILABILITY_CHOICES, blank=True)
    is_public = models.BooleanField(default=True)

    def __str__(self):
        return self.user.username


class SwapRequest(models.Model):
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_requests')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_requests')
    offered_skill = models.ForeignKey(Skill, on_delete=models.SET_NULL, null=True, related_name='offered_swaps')
    requested_skill = models.ForeignKey(Skill, on_delete=models.SET_NULL, null=True, related_name='requested_swaps')
    message = models.TextField(blank=True)
    is_accepted = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.from_user} → {self.to_user} | {self.offered_skill} for {self.requested_skill}"


class Feedback(models.Model):
    swap = models.OneToOneField(SwapRequest, on_delete=models.CASCADE, related_name='feedback')
    rating = models.PositiveIntegerField(default=5)  # rating out of 5
    comment = models.TextField(blank=True)

    def __str__(self):
        return f"Feedback for {self.swap} - {self.rating}★"
