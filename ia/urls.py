from django.urls import path
from . import views

app_name = 'ia'

urlpatterns = [
    path('assistant/', views.assistant, name='assistant'),
]