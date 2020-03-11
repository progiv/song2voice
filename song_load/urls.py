from django.urls import path

from . import views

urlpatterns = [
    path('upload', views.upload, name='song_uploading'),
    path('download', views.download, name='get_song_vocal')
]
