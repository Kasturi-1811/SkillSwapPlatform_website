from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, SwapRequest


class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            'location',
            'profile_photo',
            'skills_offered',
            'skills_wanted',
            'availability',
            'is_public',
        ]
        widgets = {
            'skills_offered': forms.CheckboxSelectMultiple(),  # Add parentheses to instantiate widget
            'skills_wanted': forms.CheckboxSelectMultiple(),
        }


class SwapRequestForm(forms.ModelForm):
    class Meta:
        model = SwapRequest
        fields = [
            'offered_skill',
            'requested_skill',
            'message',
        ]
        widgets = {
            'message': forms.Textarea(attrs={'rows': 3}),
        }


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        help_text="Enter a valid email address."
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        # Override save to save the email field properly
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user
