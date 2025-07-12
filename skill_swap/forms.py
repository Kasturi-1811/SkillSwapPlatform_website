from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, SwapRequest


class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            'location',
            'phone_number',
            'profile_photo',
            'skills_offered',
            'skills_wanted',
            'availability',
            'is_public',
        ]
        widgets = {
            'skills_offered': forms.CheckboxSelectMultiple(),
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
    email = forms.EmailField(required=True)
    location = forms.CharField(required=False)
    phone_number = forms.CharField(required=False)
    availability = forms.CharField(required=False)
    profile_photo = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']

        if commit:
            user.save()
            # Save the user profile
            profile = UserProfile.objects.create(
                user=user,
                location=self.cleaned_data.get('location'),
                phone_number=self.cleaned_data.get('phone_number'),
                availability=self.cleaned_data.get('availability'),
                profile_photo=self.cleaned_data.get('profile_photo'),
            )
        return user
