# from .views import *
from django.contrib import admin
from django.urls import path, include
from .views import *

urlpatterns = [
    path('students/', StudentsView.as_view(),name='students'),
    path('calendly/webhook/', CalendlyWebHookView.as_view(),name='calendly_webhook'),
    # path('schedule/class/', ScheduleClassView.as_view(),name='schedule_class'),
    path('schedule/class/', CreateEventView.as_view(),name='schedule_class'),
     
]
