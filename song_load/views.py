# from django.shortcuts import render
from django.http import HttpResponse, HttpResponseServerError
# from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.views.decorators.csrf import csrf_exempt


# Create your views here.
def check(request):
    return HttpResponse("Gus is here!")


@csrf_exempt
def upload_file(request):
    if request.method == 'POST' and request.FILES['song']:
        myfile = request.FILES['song']
        if myfile.name.endswith('.wav'):
            fs = FileSystemStorage()
            filename = fs.save(myfile.name, myfile)
            uploaded_file_url = fs.url(filename)
            return HttpResponse(uploaded_file_url)
        return HttpResponseServerError('<h1>Incorrect file format</h1>')
    return HttpResponseServerError('<h1>Incorrect request</h1>')
