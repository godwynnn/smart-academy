# from .views import *
from django.contrib import admin
from django.urls import path, include
from .apiviews import *

urlpatterns = [
    path('entry/',EntryView.as_view(),name='index'),
     path('questions/',QuestionsView.as_view(),name='questions'),
    path('export/form/<str:id>/',ExportToGoogleFormView.as_view(),name='export_to_form')

    # path('smart-academy/',SmartAcademyView,name='smart_academy'),
    # path('<str:entry>-entry/',LessonPlanEntryView,name='lesson_plan'),
    # path('<str:entry>-entry',QuestionEntryView,name='question_entry'),
    # path('c/question/<str:id>',QuestionChatView,name='question_chat'),
    # path('c/lesson/<str:id>',LessonChatView,name='lesson_chat'),
    #  path('export/form/<str:id>',ExportToGoogleForm,name='export_to_form')
]
