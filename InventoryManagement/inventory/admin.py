from django.contrib import admin
from django.contrib.auth.models import Group
from django.shortcuts import render, get_object_or_404
from django.urls import path
from django.utils.html import format_html

# from django.contrib import admin
from .models import Location, Accommodation, LocalizeAccommodation

# Custom admin for Location
@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'country_code', 'location_type', 'parent', 'created_at', 'updated_at')
    search_fields = ('title', 'country_code', 'city')
    list_filter = ('location_type', 'country_code')

# Custom admin for Accommodation
@admin.register(Accommodation)
class AccommodationAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'country_code', 'bedroom_count', 'review_score', 'usd_rate', 'published', 'created_at', 'updated_at')
    search_fields = ('title', 'country_code')
    list_filter = ('country_code', 'published', 'bedroom_count')
    fieldsets = (
        (None, {
            'fields': ('id', 'feed', 'title', 'country_code', 'bedroom_count', 'review_score', 'usd_rate', 'center', 'published')
        }),
        ('Images and Amenities', {
            'fields': ('images', 'amenities'),
            'classes': ('collapse',),
        }),
        ('Location and User', {
            'fields': ('location', 'user'),
        }),
    )
    def get_queryset(self, request):
        # Only return accommodations for the logged-in user
        queryset = super().get_queryset(request)
        if request.user.groups.filter(name='Property Owners').exists():
            return queryset.filter(user=request.user)
        return queryset

# Custom admin for LocalizeAccommodation
@admin.register(LocalizeAccommodation)
class LocalizeAccommodationAdmin(admin.ModelAdmin):
    list_display = ('property', 'language', 'description')
    search_fields = ('property__title', 'language')
    list_filter = ('language',)


class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'show_users')

    def show_users(self, obj):
        url = f"/admin/auth/group/{obj.id}/users/"
        return format_html('<a href="{}">View Users</a>', url)
    show_users.short_description = 'Users'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:group_id>/users/', self.admin_site.admin_view(self.view_group_users), name='group_users'),
        ]
        return custom_urls + urls

    def view_group_users(self, request, group_id):
        group = get_object_or_404(Group, pk=group_id)
        users = group.user_set.all()
        context = {
            'group': group,
            'users': users,
        }
        return render(request, 'admin/group_users.html', context)

# Unregister and re-register Group with the custom GroupAdmin
admin.site.unregister(Group)
admin.site.register(Group, GroupAdmin)


