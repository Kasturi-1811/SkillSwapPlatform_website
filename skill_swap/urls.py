from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Home page showing all users
    path('profile/', views.profile, name='profile'),  # Your own profile edit page
    path('user/<int:user_id>/', views.user_profile, name='user_profile'),  # View other user's profile
    path('swap-request/<int:user_id>/', views.send_swap_request, name='swap_request'),  # Send swap request form
    path('my-swaps/', views.swap_list, name='swap_list'),  # View your swaps
    path('register/', views.register, name='register'),  # Sign up
]
