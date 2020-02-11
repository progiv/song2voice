from django.urls import path

from . import views

urlpatterns = [
    path('check', views.check, name='check'),
    path('upload_file', views.upload_file, name='song uploading')
]
