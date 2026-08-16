from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('calculator/', views.calculator_view, name='calculator'),
    path('specialists/', views.specialists, name='specialists'),  
    path('chat/', views.chat_view, name='chat_view'),       # Main chat UI page
    path('chat/ask/', views.chat_ask, name='chat_ask'),    # API endpoint for messages


]
          