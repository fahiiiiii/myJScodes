from django.shortcuts import render, redirect
from .forms import AccommodationForm
from django.contrib.auth.decorators import login_required

@login_required
def add_property(request):
    if request.method == 'POST':
        form = AccommodationForm(request.POST)
        if form.is_valid():
            # Save the property with the logged-in user
            form.save()
            return redirect('property_list')  # Redirect to the property list view
    else:
        form = AccommodationForm()

    return render(request, 'add_property.html', {'form': form})

@login_required
def update_property(request, pk):
    property = Accommodation.objects.get(pk=pk)
    if property.user != request.user:
        return redirect('property_list')  # Redirect if the property doesn't belong to the user

    if request.method == 'POST':
        form = AccommodationForm(request.POST, instance=property)
        if form.is_valid():
            form.save()
            return redirect('property_list')
    else:
        form = AccommodationForm(instance=property)

    return render(request, 'update_property.html', {'form': form})
