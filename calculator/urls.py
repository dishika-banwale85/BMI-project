from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('calculator/', views.calculator_view, name='calculator'),
    path('specialists/', views.specialists, name='specialists'),  
]