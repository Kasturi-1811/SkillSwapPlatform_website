from django.urls import path
from . import views
from skill_swap import views
urlpatterns = [
    path('', views.home, name='home'),
    path('profile/', views.profile, name='profile'),
    path('user/<int:user_id>/', views.user_profile, name='user_profile'),
    path('send-swap-request/<int:user_id>/', views.send_swap_request, name='send_swap_request'),
    path('swap-request/<int:user_id>/', views.send_swap_request, name='swap_request'),
    
     path('swaps/', views.swap_list, name='swap_list'),
    path('register/', views.register, name='register'),
    path('accept-swap-request/<int:request_id>/', views.accept_swap_request, name='accept_swap_request'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/approve-skill/<int:skill_id>/', views.approve_skill, name='approve_skill'),
    path('admin/reject-skill/<int:skill_id>/', views.reject_skill, name='reject_skill'),
    path('accept-request/<int:request_id>/', views.accept_swap_request, name='accept_swap_request'),
    path('admin/ban-user/<int:user_id>/', views.ban_user, name='ban_user'),
    path('admin/unban-user/<int:user_id>/', views.unban_user, name='unban_user'),
    path('admin/send-message/', views.send_platform_message, name='send_platform_message'),
    path('admin/download-report/', views.download_report, name='download_report'),
]
