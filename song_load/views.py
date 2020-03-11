# from django.shortcuts import render
from django.http import HttpResponse, HttpResponseServerError
# from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.files.storage import default_storage
from django.views.decorators.csrf import csrf_exempt
import datetime
import hashlib
from spleeter_model.inference import Spleeter
from .models import ProcessedSong
import filetype
import tempfile
import pathlib
from django.http import JsonResponse
from http import HTTPStatus
from get_voice_server.settings import GS_BUCKET_NAME

from google.cloud import storage

global_model = None

def init_model():
    global global_model
    if global_model is None:
        global_model = Spleeter()

def process_file(input_file_url, processed_song_folder_url):
    init_model()
    global_model.predict(input_file_url, processed_song_folder_url)

def get_md5(file):
    hash_md5 = hashlib.md5()
    for chunk in file.chunks(4096):
        hash_md5.update(chunk)
    return hash_md5.hexdigest()

def is_wav_mp3_file(file):
    buf = filetype.get_bytes(file)
    kind = filetype.guess(buf)
    return (kind is not None) and (kind.extension in ['mp3', 'wav'])

def save_files(saver, names, files):
    assert len(names) == len(files)
    files_urls = []
    for i in range(len(names)):
        file_name = saver.save(names[i], files[i])
        files_urls.append(saver.url(file_name))
    return files_urls

def is_download_request(request):
    return request.method == 'GET' and 'hash' in request.GET

def is_upload_request(request):
    return request.method == 'POST' and 'song' in request.FILES

def is_used_hash(test_hash_code):
    return ProcessedSong.objects.filter(pk=test_hash_code).exists()

def download(request):
    if not is_download_request:
        return JsonResponse(status=HTTPStatus.BAD_REQUEST,
                            data={'message': 'Incorrect request format'})

    cur_hash = request.GET["hash"]
    if not is_used_hash(cur_hash):
        return JsonResponse(status=HTTPStatus.NOT_FOUND,
                            data={'message': 'Hash code not found'})
    return JsonResponse({'vocal_url': ProcessedSong.objects.get(pk=cur_hash).vocal_url})

def blob_exists(filename):  
    storage_client = storage.Client()
    bucket = storage_client.bucket(GS_BUCKET_NAME)
    exist = storage.Blob(bucket=bucket, name=filename).exists(storage_client)
    return exist

def is_in_google_storage(md5_of_song):
    file_names = [f'{md5_of_song}.wav', f'{md5_of_song}_vocal.wav', f'{md5_of_song}_accompaniment.wav']
    exist = True
    for fn in file_names:
        exist = exist and blob_exists(fn)
    return exist

@csrf_exempt
def upload(request):
    if not is_upload_request(request):
        return JsonResponse(status=HTTPStatus.BAD_REQUEST,
                            data={'message': 'Incorrect request format'})
    input_song = request.FILES['song']
    if not is_wav_mp3_file(input_song):
        return JsonResponse(status=HTTPStatus.BAD_REQUEST,
                            data={'message': 'Incorrect file format'})
    md5_of_song = get_md5(input_song)
    print("====================This hash: ", md5_of_song)
    used_hash = is_used_hash(md5_of_song)
    in_google_storage = is_in_google_storage(md5_of_song)
    print("====================Is used hash: ", used_hash)
    print("====================Is in google storage: ", in_google_storage)
    if used_hash and in_google_storage:
        return JsonResponse({'md5_of_song': md5_of_song})

    print("Processing ....")
    with tempfile.TemporaryDirectory() as directory_name:
        the_dir = pathlib.Path(directory_name)
        the_dir_url = f'{the_dir}/'
        dir_fs = FileSystemStorage(location=the_dir, base_url=the_dir_url)

        input_song_url = save_files(dir_fs, [f'{md5_of_song}.wav'], [input_song])[0]
        process_file(input_song_url, the_dir_url)
        local_vocal_url = f'{the_dir_url}{md5_of_song}/vocals.wav'
        local_accompaniment_url = f'{the_dir_url}{md5_of_song}/accompaniment.wav'
        default_song_url, default_vocal_url, default_accomp_url = save_files(default_storage,
                                                                             [f'{md5_of_song}.wav',
                                                                              f'{md5_of_song}_vocal.wav',
                                                                              f'{md5_of_song}_accompaniment.wav'],
                                                                             [dir_fs.open(input_song_url),
                                                                              dir_fs.open(local_vocal_url),
                                                                              dir_fs.open(local_accompaniment_url)])
        if not used_hash:
            ProcessedSong.objects.create(hash_code=md5_of_song,
                                         pub_date=datetime.datetime.now(),
                                         input_url=default_song_url,
                                         vocal_url=default_vocal_url,
                                         accompaniment_url=default_accomp_url)
    return JsonResponse({'md5_of_song': md5_of_song})
