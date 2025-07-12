from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from skill_swap.views import register  # optional if you want direct register view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('skill_swap.urls')),
    path('login/', auth_views.LoginView.as_view(template_name='skill_swap/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('accounts/password_reset/', PasswordResetView.as_view(), name='password_reset'),
    path('password-reset/',
         auth_views.PasswordResetView.as_view(template_name='skill_swap/password_reset.html'),
         name='password_reset'),

    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(template_name='skill_swap/password_reset_done.html'),
         name='password_reset_done'),

    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='skill_swap/password_reset_confirm.html'),
         name='password_reset_confirm'),

    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(template_name='skill_swap/password_reset_complete.html'),
         name='password_reset_complete'),

   
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
