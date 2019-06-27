from django.contrib import admin
from django.urls import path,include
from .views import *

urlpatterns = [
    path("",SpeechRecognition.as_view(),name="SpeechRecognition")
]
