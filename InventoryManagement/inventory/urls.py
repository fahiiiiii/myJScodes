from django.urls import path
from . import views

urlpatterns = [
    path('property/add/', views.add_property, name='add_property'),
    path('property/update/<int:pk>/', views.update_property, name='update_property'),
]
