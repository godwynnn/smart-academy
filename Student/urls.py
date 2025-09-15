# from .views import *
from django.contrib import admin
from django.urls import path, include
from .views import *

urlpatterns = [
    path('tutors/', TutorsClassView.as_view(),name='tutors'),
     
]
