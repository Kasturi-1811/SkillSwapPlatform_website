from django.contrib import admin
from .models import UserProfile, Skill, SwapRequest, PlatformMessage
import csv
from django.http import HttpResponse


# ========== Skill Admin ==========
@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_approved']
    list_filter = ['is_approved']
    search_fields = ['name']

    actions = ['approve_skills', 'reject_skills']

    @admin.action(description='Approve selected skills')
    def approve_skills(self, request, queryset):
        queryset.update(is_approved=True)

    @admin.action(description='Reject selected skills')
    def reject_skills(self, request, queryset):
        queryset.update(is_approved=False)


# ========== User Profile Admin ==========
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'location', 'phone_number', 'availability', 'is_banned', 'is_public']
    list_filter = ['is_banned', 'is_public', 'location', 'availability']
    search_fields = ['user__username', 'location', 'phone_number']
    actions = ['ban_users', 'unban_users']

    @admin.action(description="Ban selected users")
    def ban_users(self, request, queryset):
        queryset.update(is_banned=True)

    @admin.action(description="Unban selected users")
    def unban_users(self, request, queryset):
        queryset.update(is_banned=False)


# ========== Swap Request Admin ==========
@admin.action(description='Export selected swap requests as CSV')
def export_swaps_as_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="swap_requests.csv"'
    writer = csv.writer(response)
    writer.writerow(['From User', 'To User', 'Offered Skill', 'Requested Skill', 'Accepted', 'Rejected', 'Created At'])
    for swap in queryset:
        writer.writerow([
            swap.from_user.username,
            swap.to_user.username,
            swap.offered_skill.name if swap.offered_skill else '',
            swap.requested_skill.name,
            swap.is_accepted,
            swap.is_rejected,
            swap.created_at.strftime('%Y-%m-%d %H:%M'),
        ])
    return response


@admin.register(SwapRequest)
class SwapRequestAdmin(admin.ModelAdmin):
    list_display = ['from_user', 'to_user', 'offered_skill', 'requested_skill', 'is_accepted', 'is_rejected', 'created_at']
    list_filter = ['is_accepted', 'is_rejected', 'created_at']
    search_fields = ['from_user__username', 'to_user__username']
    actions = [export_swaps_as_csv]


# ========== Platform Message Admin ==========
@admin.register(PlatformMessage)
class PlatformMessageAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_at']
    search_fields = ['title', 'content']
    ordering = ['-created_at']
