# from django.shortcuts import render
from django.http import HttpResponse, HttpResponseServerError
# from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.views.decorators.csrf import csrf_exempt
import time
import hashlib
from .models import ProcessedSong


# Real Deep Learning!
class StubModel:
    def predict(self, file):
        time.sleep(3)
        return file

global_model = None
fs = FileSystemStorage()

def init_model():
    global global_model
    if global_model is None:
        global_model = StubModel()


def process_file(file):
    init_model()
    # TODO: carefully pass file in real model
    result_file = global_model.predict(file)
    return result_file

def get_md5(file):
    hash_md5 = hashlib.md5()
    for chunk in file.chunks(4096):
        hash_md5.update(chunk)
    return hash_md5.hexdigest()

def is_wav_file(file):
    return file.name.endswith('.wav')

def save_file_in_media(file):
    filename = fs.save(file.name, file)
    uploaded_file_url = fs.url(filename)
    return uploaded_file_url

def is_good_request(request):
    return request.method == 'POST' and 'song' in request.FILES

def is_used_hash(test_hash_code):
    return ProcessedSong.objects.filter(pk=test_hash_code).exists()

@csrf_exempt
def upload(request):
    if not is_good_request(request):
        return HttpResponseServerError('<h1>Incorrect request format</h1>')
    input_song = request.FILES['song']
    if not is_wav_file(input_song):
        return HttpResponseServerError('<h1>Incorrect file format</h1>')
    md5_of_song = get_md5(input_song)
    if is_used_hash(md5_of_song):
        song_url =  ProcessedSong.objects.filter(pk=md5_of_song).first().procesed_song_url
        return HttpResponse(song_url)
    processed_song = process_file(input_song)
    uploaded_song_url = save_file_in_media(processed_song)
    _ = ProcessedSong.objects.create(hash_code=md5_of_song, procesed_song_url=uploaded_song_url)
    return HttpResponse(uploaded_song_url)
        
    