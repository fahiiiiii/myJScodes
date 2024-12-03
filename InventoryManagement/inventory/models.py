from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone 
from django.contrib.gis.db import models
import uuid
# from .models import Accommodation  # or the correct path if it's in another file

from django.contrib.gis.db import models as gis_models
from django.contrib.postgres.fields import ArrayField, JSONField
from django.contrib.gis.db import models as gis_models
# class Location(models.Model):
#     id = models.CharField(max_length=20, primary_key=True)
#     title = models.CharField(max_length=100)
#     center = models.PointField()  # Placeholder for PostGIS point
#     parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='children')
#     location_type = models.CharField(max_length=20)
#     country_code = models.CharField(max_length=2)
#     state_abbr = models.CharField(max_length=3, blank=True)
#     city = models.CharField(max_length=30, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)






class Accommodation(models.Model):
    # id = models.AutoField(primary_key=True)
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # id = models.CharField(max_length=20, primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=100)
    country_code = models.CharField(max_length=2)
    bedroom_count = models.PositiveIntegerField()
    review_score = models.DecimalField(max_digits=4, decimal_places=1, default=0)
    usd_rate = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    center = models.CharField(max_length=255)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    amenities = models.JSONField(default=list)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# class Accommodation(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     title = models.CharField(max_length=100)
#     country_code = models.CharField(max_length=2)
#     bedroom_count = models.PositiveIntegerField(null=True, blank=True)  # Allow empty
#     review_score = models.DecimalField(max_digits=4, decimal_places=1, default=0)
#     usd_rate = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
#     center = models.CharField(max_length=255)
#     images = models.ImageField(upload_to='property_images/', blank=True, null=True)  # This will store images in 'property_images/' folder
#     # images = models.JSONField(default=list)
#     location = models.ForeignKey(Location, on_delete=models.CASCADE)
#     amenities = models.JSONField(default=list)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     published = models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

# class Accommodation(models.Model):
#     id = models.CharField(max_length=20, primary_key=True)
#     feed = models.PositiveSmallIntegerField(default=0)
#     title = models.CharField(max_length=100)
#     country_code = models.CharField(max_length=2)
#     bedroom_count = models.PositiveIntegerField()
#     review_score = models.DecimalField(max_digits=4, decimal_places=1, default=0)
#     usd_rate = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
#     center = models.CharField(max_length=255)  # Placeholder for PostGIS point
#     images = models.JSONField(default=list)
#     location = models.ForeignKey(Location, on_delete=models.CASCADE)
#     amenities = models.JSONField(default=list)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     published = models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.id:  # Ensure the ID is assigned if it's not set
            self.id = str(uuid.uuid4())[:20]  # You can use UUID or any unique generation method
        if not self.created_at:
            self.created_at = timezone.now()
        super().save(*args, **kwargs)

# class Accommodation(models.Model):
#     # id = models.AutoField(max_length=20,primary_key=True)
#     id = models.CharField(max_length=20, primary_key=True)
#     feed = models.PositiveSmallIntegerField(default=0)
#     title = models.CharField(max_length=100)
#     country_code = models.CharField(max_length=2)
#     bedroom_count = models.PositiveIntegerField()
#     review_score = models.DecimalField(max_digits=4, decimal_places=1, default=0)
#     usd_rate = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
#     center = models.CharField(max_length=255)  # Placeholder for PostGIS point
#     images = models.JSONField(default=list)
#     location = models.ForeignKey(Location, on_delete=models.CASCADE)
#     amenities = models.JSONField(default=list)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     published = models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
    
    # def save(self, *args, **kwargs):
    #     if not self.created_at:
    #         self.created_at = timezone.now()  # Set the current time if created_at is not set
    #     super().save(*args, **kwargs)  # Call the original save method


# class Accommodation(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     title = models.CharField(max_length=100)
#     country_code = models.CharField(max_length=2)
#     bedroom_count = models.PositiveIntegerField(null=True, blank=True)
#     review_score = models.DecimalField(max_digits=4, decimal_places=1, default=0)
#     usd_rate = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
#     center = models.CharField(max_length=255)
#     images = models.ImageField(upload_to='property_images/', blank=True, null=True)  # Store images in 'property_images/' folder
#     location = models.ForeignKey('Location', on_delete=models.CASCADE)
#     amenities = models.JSONField(default=list)
#     user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
#     published = models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def save(self, *args, **kwargs):
#         if not self.created_at:
#             self.created_at = timezone.now()  # Set the current time if created_at is not set
#         super().save(*args, **kwargs)  # Call the original save method
# class Accommodation(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     title = models.CharField(max_length=100)
#     country_code = models.CharField(max_length=2)
#     bedroom_count = models.PositiveIntegerField(null=True, blank=True)
#     review_score = models.DecimalField(max_digits=4, decimal_places=1, default=0)
#     usd_rate = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
#     center = models.CharField(max_length=255)
#     images = models.ImageField(upload_to='property_images/', blank=True, null=True)  # Allow blank images
#     location = models.ForeignKey(Location, on_delete=models.CASCADE)
#     amenities = models.JSONField(default=list, blank=True)  # Default to an empty list
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     published = models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def save(self, *args, **kwargs):
#         if not self.created_at:
#             self.created_at = timezone.now()  # Set the current time if created_at is not set
#         super().save(*args, **kwargs)  # Call the original save method



# class Accommodation(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     title = models.CharField(max_length=200)
#     country_code = models.CharField(max_length=10)
#     country = models.CharField(max_length=100, default='Unknown')  # Add default here
#     bedroom_count = models.IntegerField()
#     review_score = models.FloatField()
#     usd_rate = models.DecimalField(max_digits=10, decimal_places=2)
#     center = gis_models.PointField(null=True, blank=True)
#     published = models.BooleanField(default=False)
#     amenities = models.CharField(max_length=200, blank=True, null=True)
    
#     property_images = models.JSONField(null=True, blank=True)
    
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
    
#     def __str__(self):
#         return self.title


# Location model (if it doesn't exist already)
from django.db import models
from django.contrib.gis.db import models as gis_models

class Location(models.Model):
    # Primary key: id
    id = models.CharField(max_length=20, primary_key=True)
    
    # Title: Name of the location
    title = models.CharField(max_length=100)
    
    # Geolocation: PostGIS Point (for latitude and longitude)
    center = gis_models.PointField()
    
    # Parent location: Foreign key to another Location for hierarchical nesting
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='children')
    
    # Location Type: Type of location (continent, country, state, city, etc.)
    location_type = models.CharField(max_length=20)
    
    # Country Code: ISO 3166-1 alpha-2 country code
    country_code = models.CharField(max_length=2)
    
    # State Abbreviation: e.g., 'CA' for California (optional)
    state_abbr = models.CharField(max_length=3, null=True, blank=True)
    
    # City: Name of the city (optional)
    city = models.CharField(max_length=30, null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Property(models.Model):
    id = models.CharField(max_length=20, primary_key=True)
    feed = models.PositiveSmallIntegerField(default=0)
    title = models.CharField(max_length=100)
    country_code = models.CharField(max_length=2)
    bedroom_count = models.PositiveIntegerField(null=True, blank=True)
    review_score = models.DecimalField(max_digits=3, decimal_places=1, default=0)
    usd_rate = models.DecimalField(max_digits=10, decimal_places=2)
    center = gis_models.PointField()
    images = ArrayField(models.ImageField(upload_to='property_images/'), blank=True, default=list)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    amenities = JSONField(blank=True, default=list)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    pass
# Define the regular function for default value
# def default_value():
#     return "default value"



# class Accommodation(models.Model):
#     # my_field = models.CharField(max_length=100, default=default_value)
#     my_field = models.CharField(max_length=100) 

#     # Primary key
#     id = models.CharField(
#         primary_key=True,
#         max_length=20,
#         unique=True,
#         editable=False,
#         default=lambda: str(uuid.uuid4())[:20],  # Generates a unique string
#     )
    
#     # Feed number
#     feed = models.PositiveSmallIntegerField(default=0)

#     # Title
#     title = models.CharField(max_length=100, null=False, blank=False)

#     # Country-related fields
#     country_code = models.CharField(max_length=2, null=False, blank=False)
#     country = models.CharField(max_length=100, default="Unknown")

#     # Bedroom count
#     bedroom_count = models.PositiveIntegerField(null=True, blank=True)

#     # Review score
#     review_score = models.DecimalField(
#         max_digits=4, decimal_places=1, default=0.0
#     )

#     # USD rate
#     usd_rate = models.DecimalField(
#         max_digits=10, decimal_places=2, blank=True, null=True
#     )

#     # Geolocation point
#     center = gis_models.PointField(null=True, blank=True)

#     # Images (stored as a JSON array of URLs)
#     images = models.JSONField(
#         null=True, blank=True, help_text="Array of image URLs"
#     )

#     # Foreign key to Location
#     location = models.ForeignKey(
#         "Location", on_delete=models.CASCADE, null=True, blank=True
#     )

#     # Amenities (stored as a JSON array)
#     amenities = models.JSONField(
#         default=list, blank=True, help_text="Array of amenities"
#     )

#     # Foreign key to User
#     user = models.ForeignKey(User, on_delete=models.CASCADE)

#     # Published status
#     published = models.BooleanField(default=False)

#     # Timestamps
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def save(self, *args, **kwargs):
#         # Automatically set created_at if not already set
#         if not self.created_at:
#             self.created_at = timezone.now()
#         super().save(*args, **kwargs)

#     def __str__(self):
#         return self.title



class LocalizeAccommodation(models.Model):
    id = models.AutoField(primary_key=True)
    # property = models.ForeignKey('Accommodation', on_delete=models.CASCADE)
    property = models.ForeignKey('Accommodation', on_delete=models.CASCADE)
    language = models.CharField(max_length=2)
    description = models.TextField(blank=True, null=True)
    policy = models.JSONField(default=dict)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['property', 'language'], name='unique_localization_per_language')
        ]



class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_approved_as_property_owner = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username








































































