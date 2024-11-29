from django import forms
from .models import Accommodation

class AccommodationForm(forms.ModelForm):
    class Meta:
        model = Accommodation
        fields = ['title', 'country_code', 'bedroom_count', 'review_score', 'usd_rate', 'center', 'images', 'location', 'amenities']

    def save(self, commit=True):
        accommodation = super().save(commit=False)
        if commit:
            accommodation.user = self.request.user  # Set the user to the currently logged-in user
            accommodation.save()
        return accommodation
