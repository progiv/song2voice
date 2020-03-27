from .models import AccessLogsModel
from django.conf import settings
from django.utils import timezone
from http import HTTPStatus
from django.http import JsonResponse
import logging

class AccessLogsMiddleware(object):

    def __init__(self, get_response=None):
        self.get_response = get_response
        self.logger = logging.getLogger('default')
        # One-time configuration and initialization.

    def __call__(self, request):
        # create session
        self.logger.info('=============================New request===============================')
        if not request.session.session_key:
            request.session.create()

        self.access_logs_data = dict()
        self.process_request(request)

        response = self.get_response(request)

        self.process_response(request, response)
        return response
    
    def process_request(self, request):
        # get the request path
        self.access_logs_data["request_path"] = request.path

        # get the client's IP address
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        self.access_logs_data["request_ip_address"] = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')
        self.access_logs_data["request_method"] = request.method
        self.access_logs_data["request_referrer"] = request.META.get('HTTP_REFERER',None)
        self.access_logs_data["session_key"] = request.session.session_key

        data = dict()
        data["get"] = dict(request.GET.copy())
        data['post'] = dict(request.POST.copy())

        # remove password form post data for security reasons
        keys_to_remove = ["password", "csrfmiddlewaretoken"]
        for key in keys_to_remove:
            data["post"].pop(key, None)

        self.access_logs_data["request_data"] = data
        self.access_logs_data["request_timestamp"] = timezone.now()

    def process_response(self, request, response):
        # save response
        self.access_logs_data["response_status"] = response.status_code
        self.access_logs_data["response_timestamp"] = timezone.now()
        self.access_logs_data["processed_time"] = str(self.access_logs_data["response_timestamp"] - self.access_logs_data["request_timestamp"])

        model = AccessLogsModel.objects.create(**self.access_logs_data)
        self.logger.info(model)
        self.logger.info('==================================================================')


    def process_exception(self, request, exception):
        self.logger.exception('xxxxxxxx get_response fails in middleware xxxxxxxx')
        return JsonResponse(status=HTTPStatus.INTERNAL_SERVER_ERROR,
                            data={'message': 'Fail response processing'})