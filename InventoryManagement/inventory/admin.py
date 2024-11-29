# from django.contrib import admin
# from .models import Location, Accommodation, LocalizeAccommodation

# admin.site.register(Location)
# admin.site.register(Accommodation)
# admin.site.register(LocalizeAccommodation)
from django.contrib import admin
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

