from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def check(request):
    return HttpResponse('<h1>Server working ...</h1>')
